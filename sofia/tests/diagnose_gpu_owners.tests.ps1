<#
    Интеграция: diagnose_host_safe_hold.ps1 должен превращать список процессов
    GPU в вердикт по владельцам, а не в общий WARN «задачи есть».

    Запускается весь скрипт целиком: секции ловят свои ошибки сами, поэтому
    отсутствие Windows-источников не мешает проверить нужную секцию.
#>

$tool = Join-Path (Split-Path $PSScriptRoot -Parent) 'diagnose_host_safe_hold.ps1'

function Invoke-Diagnose {
    param([string] $SofiaRoot, [string] $OutDir)
    & $tool -SofiaRoot $SofiaRoot -OutDir $OutDir -Days 1 *>&1 | Out-String | Out-Null
    $report = Join-Path $OutDir 'safehold_report.json'
    if (-not (Test-Path $report)) { throw 'отчёт safehold_report.json не создан' }
    Get-Content $report -Raw | ConvertFrom-Json
}

function New-StudioRoot {
    param([string] $Dir, [bool] $HoldActive)
    $flags = Join-Path $Dir 'control_flags'
    New-Item -ItemType Directory -Force -Path $flags | Out-Null
    if ($HoldActive) {
        'host_unstable_safe_hold' | Out-File -FilePath (Join-Path $flags 'HOST_SAFE_HOLD.flag') -Encoding UTF8
    }
    $Dir
}

# --------------------------------------------------------------------------

Test 'два тяжёлых владельца попадают в отчёт как FAIL по ONE HEAVY GPU OWNER' {
    $sb = New-Sandbox 'diag_owners_fail'
    try {
        Install-FakeNvidiaSmi -Dir $sb.Dir -State @{
            memory_used  = 16500
            compute_apps = @(
                @{ pid = 100; process_name = 'C:\ComfyUI\python.exe';     used_memory = 9000 },
                @{ pid = 201; process_name = 'C:\ComfyUI_old\python.exe'; used_memory = 7000 }
            )
        } | Out-Null
        Set-WinEventStub -Mode ok -Events @()
        Set-LiveProcessStub -Pids @(100, 201, 10, 11, 55, 2056, 14464, 21384, 27900, 19692)

        $root = New-StudioRoot -Dir (Join-Path $sb.Dir 'studio') -HoldActive $true
        $r = Invoke-Diagnose -SofiaRoot $root -OutDir (Join-Path $sb.Dir 'out')

        $owners = $r.sections.gpu_owners
        Assert-True ($null -ne $owners) 'секция gpu_owners обязана появиться в отчёте'
        Assert-Equal 2 $owners.heavy_count 'оба владельца должны быть посчитаны'
        Assert-Equal 16000 $owners.heavy_used_mib 'суммарная занятая память'
        Assert-True ([bool]$owners.hold_active) 'активный hold должен быть виден в секции'

        $f = @($r.findings | Where-Object { $_.component -eq 'GPU owners' })
        Assert-Equal 1 $f.Count 'должен быть ровно один вывод по владельцам'
        Assert-Equal 'FAIL' $f[0].status 'конкурирующие рендеры — это FAIL'
        Assert-Match 'ONE HEAVY GPU OWNER' $f[0].evidence 'правило должно быть названо в доказательстве'
    } finally { Remove-Sandbox $sb }
}

Test 'занятая VRAM без единой задачи попадает в отчёт как след неотработавшей очистки' {
    $sb = New-Sandbox 'diag_owners_orphan'
    try {
        Install-FakeNvidiaSmi -Dir $sb.Dir -State @{ memory_used = 11000; compute_apps = @() } | Out-Null
        Set-WinEventStub -Mode ok -Events @()
        Set-LiveProcessStub -Pids @(100, 201, 10, 11, 55, 2056, 14464, 21384, 27900, 19692)

        $root = New-StudioRoot -Dir (Join-Path $sb.Dir 'studio') -HoldActive $true
        $r = Invoke-Diagnose -SofiaRoot $root -OutDir (Join-Path $sb.Dir 'out')

        $f = @($r.findings | Where-Object { $_.component -eq 'GPU owners' })
        Assert-Equal 'WARN' $f[0].status 'память держится без владельца'
        Assert-Equal 11000 $r.sections.gpu_owners.orphan_vram_mib 'объём осиротевшей памяти должен быть в отчёте'
    } finally { Remove-Sandbox $sb }
}

Test 'простаивающая карта при hold — PASS' {
    $sb = New-Sandbox 'diag_owners_idle'
    try {
        Install-FakeNvidiaSmi -Dir $sb.Dir -State @{ memory_used = 400; compute_apps = @() } | Out-Null
        Set-WinEventStub -Mode ok -Events @()
        Set-LiveProcessStub -Pids @(100, 201, 10, 11, 55, 2056, 14464, 21384, 27900, 19692)

        $root = New-StudioRoot -Dir (Join-Path $sb.Dir 'studio') -HoldActive $true
        $r = Invoke-Diagnose -SofiaRoot $root -OutDir (Join-Path $sb.Dir 'out')

        $f = @($r.findings | Where-Object { $_.component -eq 'GPU owners' })
        Assert-Equal 'PASS' $f[0].status 'при hold простой GPU — ожидаемое состояние'
        Assert-Equal 0 $r.sections.gpu_owners.heavy_count 'тяжёлых владельцев нет'
    } finally { Remove-Sandbox $sb }
}

Test 'диагностика не трогает флаг hold' {
    $sb = New-Sandbox 'diag_no_touch'
    try {
        Install-FakeNvidiaSmi -Dir $sb.Dir | Out-Null
        Set-WinEventStub -Mode ok -Events @()
        $root = New-StudioRoot -Dir (Join-Path $sb.Dir 'studio') -HoldActive $true
        $flag = Join-Path $root 'control_flags\HOST_SAFE_HOLD.flag'
        $before = (Get-Item $flag).LastWriteTime

        Invoke-Diagnose -SofiaRoot $root -OutDir (Join-Path $sb.Dir 'out') | Out-Null

        Assert-True (Test-Path $flag) 'флаг обязан остаться на месте'
        Assert-Equal $before.Ticks (Get-Item $flag).LastWriteTime.Ticks 'флаг не должен переписываться'
    } finally { Remove-Sandbox $sb }
}

Test 'WDDM: used_memory не отдаётся — диагностика говорит это прямо, а не молчит' {
    # Реальный случай с машины студии: nvidia-smi перечисляет процессы, но
    # used_memory по каждому [N/A], а карта занята почти целиком.
    $sb = New-Sandbox 'diag_wddm'
    try {
        Install-FakeNvidiaSmi -Dir $sb.Dir -State @{
            memory_used  = 30803
            memory_total = 32607
            compute_apps = @(
                @{ pid = 14464; process_name = 'C:\Windows\explorer.exe';       used_memory = 'N/A' },
                @{ pid = 21384; process_name = 'C:\NVIDIA\NVIDIA Overlay.exe';  used_memory = 'N/A' },
                @{ pid = 27900; process_name = 'C:\AI\ComfyUI\python.exe';      used_memory = 'N/A' }
            )
        } | Out-Null
        Set-WinEventStub -Mode ok -Events @()
        Set-LiveProcessStub -Pids @(100, 201, 10, 11, 55, 2056, 14464, 21384, 27900, 19692)
        Set-GpuCounterStub -PerPid $null   # счётчики тоже не дались

        $root = New-StudioRoot -Dir (Join-Path $sb.Dir 'studio') -HoldActive $true
        $r = Invoke-Diagnose -SofiaRoot $root -OutDir (Join-Path $sb.Dir 'out')

        $owners = $r.sections.gpu_owners
        Assert-Equal 'not_measured' $owners.attribution 'память не отдана ни по одному процессу'
        Assert-Equal 30803 $owners.unattributed_mib 'вся занятая память не отнесена'
        Assert-Equal 32607 $owners.memory_total_mib 'объём карты должен попасть в отчёт'

        $f = @($r.findings | Where-Object { $_.component -eq 'GPU owners' })
        Assert-Equal 'FAIL' $f[0].status 'карта занята, владелец неизвестен — это отказ'
        Assert-Match 'владельца установить нельзя' $f[0].evidence 'причина должна быть названа'
    } finally { Remove-Sandbox $sb }
}

Test 'счётчики Windows закрывают пробел nvidia-smi и попадают в отчёт' {
    $sb = New-Sandbox 'diag_counters'
    try {
        Install-FakeNvidiaSmi -Dir $sb.Dir -State @{
            memory_used  = 30803
            memory_total = 32607
            compute_apps = @(
                @{ pid = 2056;  process_name = 'C:\Windows\System32\dwm.exe'; used_memory = 'N/A' },
                @{ pid = 27900; process_name = 'C:\AI\ComfyUI\python.exe';    used_memory = 'N/A' }
            )
        } | Out-Null
        Set-WinEventStub -Mode ok -Events @()
        Set-LiveProcessStub -Pids @(100, 201, 10, 11, 55, 2056, 14464, 21384, 27900, 19692)
        Set-GpuCounterStub -PerPid @{ 27900 = 27000; 2056 = 593 }

        $root = New-StudioRoot -Dir (Join-Path $sb.Dir 'studio') -HoldActive $true
        $r = Invoke-Diagnose -SofiaRoot $root -OutDir (Join-Path $sb.Dir 'out')

        $owners = $r.sections.gpu_owners
        Assert-Equal 'measured' $owners.attribution 'память нашлась по всем процессам'
        Assert-Equal 27593 $owners.attributed_mib 'сумма из счётчиков'
        Assert-Equal 3210 $owners.unattributed_mib 'остаток'

        $python = @($owners.apps | Where-Object { $_.pid -eq 27900 })
        Assert-Equal 'perf-counter' $python[0].mem_source 'источник памяти должен быть записан'
        Assert-True (@($r.sections.gpu_process_counters).Count -ge 2) 'сырые счётчики должны сохраниться в отчёте'
    } finally { Remove-Sandbox $sb }
}

Test 'мёртвый владелец GPU доезжает до отчёта как причина ничьей памяти' {
    # Прямой аналог картины с машины студии: nvidia-smi числит два python,
    # но одного из них в системе уже нет.
    $sb = New-Sandbox 'diag_dead_owner'
    try {
        Install-FakeNvidiaSmi -Dir $sb.Dir -State @{
            memory_used  = 31794
            memory_total = 32607
            compute_apps = @(
                @{ pid = 27900; process_name = 'C:\AI\ComfyUI\python.exe'; used_memory = 'N/A' },
                @{ pid = 19692; process_name = 'C:\AI\ComfyUI\python.exe'; used_memory = 'N/A' }
            )
        } | Out-Null
        Set-WinEventStub -Mode ok -Events @()
        Set-GpuCounterStub -PerPid @{ 27900 = 1915 }
        Set-LiveProcessStub -Pids @(27900)

        $root = New-StudioRoot -Dir (Join-Path $sb.Dir 'studio') -HoldActive $true
        $r = Invoke-Diagnose -SofiaRoot $root -OutDir (Join-Path $sb.Dir 'out')

        $owners = $r.sections.gpu_owners
        Assert-True ([bool]$owners.live_checked) 'проверка живых процессов должна была пройти'
        Assert-Equal 1 $owners.dead_count 'один владелец мёртв'
        Assert-Equal 1 $owners.heavy_count 'живой владелец один'

        $f = @($r.findings | Where-Object { $_.component -eq 'GPU owners' })
        Assert-Equal 'FAIL' $f[0].status 'незакрытый контекст — отказ'
        Assert-Match 'которых больше нет' $f[0].evidence 'причина должна быть названа'
        Assert-Match '19692' $f[0].evidence 'и виновник'
    } finally { Remove-Sandbox $sb }
}
