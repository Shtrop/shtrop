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
