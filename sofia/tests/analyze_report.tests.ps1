<#
    Контракт analyze_safehold_report.ps1: вердикт строится из улик отчёта,
    и конкурирующие владельцы GPU должны попадать в этот вердикт, а не
    оставаться строчкой в JSON.
#>

$tool = Join-Path (Split-Path $PSScriptRoot -Parent) 'analyze_safehold_report.ps1'

function New-Report {
    param([hashtable] $Overrides = @{})
    $now = Get-Date
    $base = [ordered]@{
        generated_at = $now.ToString('o')
        host         = 'SOFIA-TEST'
        window_days  = 7
        verdict      = 'FAIL'
        sections     = [ordered]@{
            kernel_power = @(
                [ordered]@{ id = 41; time = $now.AddHours(-30).ToString('o') },
                [ordered]@{ id = 41; time = $now.AddHours(-20).ToString('o') },
                [ordered]@{ id = 41; time = $now.AddHours(-10).ToString('o') }
            )
            kernel_power_stats = [ordered]@{
                count_41       = 3
                first          = $now.AddHours(-30).ToString('o')
                last           = $now.AddHours(-10).ToString('o')
                span_hours     = 20
                per_day        = 3.6
                gaps_hours     = @(10, 10)
                bugcheck_count = 0
            }
            minidumps    = @()
            gpu_owners   = [ordered]@{
                heavy_count = 2; heavy_used_mib = 16000; orphan_vram_mib = 0; hold_active = $true
                apps = @()
            }
        }
        findings     = @(
            [ordered]@{ status = 'FAIL'; component = 'HOST_SAFE_HOLD.flag'; evidence = 'флаг активен' },
            [ordered]@{ status = 'WARN'; component = 'GPU power limit';     evidence = 'лимит = максимум платы' },
            [ordered]@{ status = 'FAIL'; component = 'GPU owners';          evidence = 'нарушено ONE HEAVY GPU OWNER: тяжёлых владельцев 2' }
        )
    }
    foreach ($k in $Overrides.Keys) { $base[$k] = $Overrides[$k] }
    $base
}

function Invoke-Analyzer {
    param($Report, [string] $Dir)
    New-Item -ItemType Directory -Force -Path $Dir | Out-Null
    $path = Join-Path $Dir 'safehold_report.json'
    $Report | ConvertTo-Json -Depth 8 | Out-File -FilePath $path -Encoding UTF8
    & $tool -ReportPath $path *>&1 | Out-String
}

# --------------------------------------------------------------------------

Test 'анализатор читает отчёт и не падает на новой секции gpu_owners' {
    $sb = New-Sandbox 'analyze_ok'
    try {
        $out = Invoke-Analyzer -Report (New-Report) -Dir $sb.Dir
        Assert-Match 'Улики' $out 'секция улик должна быть напечатана'
        Assert-NotMatch 'Exception|не найден' $out 'разбор не должен падать'
    } finally { Remove-Sandbox $sb }
}

Test 'конкурирующие владельцы GPU показаны в уликах и усиливают гипотезу транзиентов' {
    $sb = New-Sandbox 'analyze_owners'
    try {
        $out = Invoke-Analyzer -Report (New-Report) -Dir $sb.Dir
        Assert-Match 'Тяжёлых владельцев GPU\s*:\s*2' $out 'число владельцев должно быть в уликах'
        Assert-Match 'ONE HEAVY GPU OWNER' $out 'нарушение правила должно попасть в обоснование гипотезы'
    } finally { Remove-Sandbox $sb }
}

Test 'один владелец не добавляет обоснования про конкурирующие рендеры' {
    $sb = New-Sandbox 'analyze_single'
    try {
        $rep = New-Report
        $rep.sections.gpu_owners.heavy_count = 1
        $rep.sections.gpu_owners.heavy_used_mib = 9000
        $rep.findings = @($rep.findings | Where-Object { $_.component -ne 'GPU owners' }) + @(
            [ordered]@{ status = 'WARN'; component = 'GPU owners'; evidence = 'при активном hold на GPU работает python.exe' }
        )
        $out = Invoke-Analyzer -Report $rep -Dir $sb.Dir
        Assert-Match 'Тяжёлых владельцев GPU\s*:\s*1' $out 'счётчик должен остаться честным'
        Assert-NotMatch 'пики складываются' $out 'обоснование про конкуренцию не должно появляться'
    } finally { Remove-Sandbox $sb }
}

Test 'осиротевшая VRAM показана в уликах' {
    $sb = New-Sandbox 'analyze_orphan'
    try {
        $rep = New-Report
        $rep.sections.gpu_owners.heavy_count = 0
        $rep.sections.gpu_owners.heavy_used_mib = 0
        $rep.sections.gpu_owners.orphan_vram_mib = 11000
        $out = Invoke-Analyzer -Report $rep -Dir $sb.Dir
        Assert-Match 'осиротевшая VRAM 11000 MiB' $out 'объём должен быть назван'
    } finally { Remove-Sandbox $sb }
}

Test 'отчёт без секции gpu_owners разбирается по-старому' {
    $sb = New-Sandbox 'analyze_legacy'
    try {
        $rep = New-Report
        $rep.sections.Remove('gpu_owners')
        $rep.findings = @($rep.findings | Where-Object { $_.component -ne 'GPU owners' })
        $out = Invoke-Analyzer -Report $rep -Dir $sb.Dir
        Assert-Match 'Улики' $out 'старый отчёт должен разбираться'
        Assert-NotMatch 'Тяжёлых владельцев GPU' $out 'выдумывать данные нельзя'
    } finally { Remove-Sandbox $sb }
}

Test 'FAIL из-за неустановленного владельца не усиливает гипотезу транзиентов' {
    # У находки "GPU owners" статус FAIL бывает по двум разным причинам.
    # Конкуренция владельцев — про питание, неустановленный владелец — нет.
    $sb = New-Sandbox 'analyze_owner_unknown'
    try {
        $rep = New-Report
        $rep.sections.gpu_owners.heavy_count = 0
        $rep.sections.gpu_owners.heavy_used_mib = 0
        $rep.sections.gpu_owners.attribution = 'not_measured'
        $rep.sections.gpu_owners.unattributed_mib = 30803
        $rep.sections.gpu_owners.orphan_vram_mib = 30803
        $rep.sections.gpu_owners.memory_used_mib = 30803
        $out = Invoke-Analyzer -Report $rep -Dir $sb.Dir

        Assert-Match 'владелец не установлен' $out 'предупреждение должно быть показано'
        Assert-NotMatch 'пики складываются' $out 'это не довод в пользу транзиентов питания'
    } finally { Remove-Sandbox $sb }
}

# --------------------------------------------------------------------------
# План действий: гипотеза задаёт направление, но часть находок закрывается
# независимо от неё. Раньше они в план не попадали вовсе.
# --------------------------------------------------------------------------

Test 'известный код остановки не отправляет искать код остановки' {
    # В отчёте с машины анализатор печатал код 0x154 в уликах и тут же
    # советовал запустить analyze_minidump, чтобы его получить.
    $sb = New-Sandbox 'analyze_known_code'
    try {
        $rep = New-Report
        $now = Get-Date
        $rep.sections.kernel_power = @(
            [ordered]@{
                id = 1001; time = $now.AddHours(-20).ToString('o')
                message = 'The computer has rebooted from a bugcheck. The bugcheck was: 0x00000154'
            }
        )
        $rep.sections.minidumps = @([ordered]@{ name = '091826-01.dmp' }, [ordered]@{ name = '091726-01.dmp' })
        $rep.sections.kernel_power_stats.bugcheck_count = 2

        $out = Invoke-Analyzer -Report $rep -Dir $sb.Dir

        Assert-Match 'Код остановки уже известен' $out 'план должен опираться на уже добытый код'
        Assert-Match 'MemTest86' $out 'класс memory ведёт к проверке памяти'
        Assert-NotMatch 'Получить код остановки' $out 'второй раз за кодом гонять нельзя'
    } finally { Remove-Sandbox $sb }
}

Test 'нарушение ONE HEAVY GPU OWNER попадает в план, а не только в список FAIL' {
    $sb = New-Sandbox 'analyze_plan_owners'
    try {
        $rep = New-Report
        $rep.sections.gpu_owners.heavy_count = 2
        $rep.sections.gpu_owners.memory_used_mib = 31794
        $rep.sections.gpu_owners.orphan_vram_mib = 29879
        $rep.sections.gpu_owners.attribution = 'partial'
        $rep.sections.gpu_owners.apps = @(
            [ordered]@{ pid = 27900; name = 'python.exe'; class = 'heavy' },
            [ordered]@{ pid = 19692; name = 'python.exe'; class = 'heavy' }
        )
        $out = Invoke-Analyzer -Report $rep -Dir $sb.Dir

        Assert-Match 'Закрыть независимо от гипотезы' $out 'раздел должен появиться'
        Assert-Match 'python.exe:27900' $out 'владельцы должны быть названы поимённо'
        Assert-Match 'python.exe:19692' $out 'оба'
        Assert-Match '29879 MiB' $out 'не отнесённая память должна быть в плане'
    } finally { Remove-Sandbox $sb }
}

Test 'лимит на максимуме попадает в план, даже когда верхняя гипотеза другая' {
    $sb = New-Sandbox 'analyze_plan_limit'
    try {
        $rep = New-Report
        $now = Get-Date
        $rep.sections.kernel_power = @(
            [ordered]@{ id = 1001; time = $now.AddHours(-20).ToString('o')
                        message = 'bugcheck was: 0x00000154' }
        )
        $rep.sections.kernel_power_stats.bugcheck_count = 2
        $out = Invoke-Analyzer -Report $rep -Dir $sb.Dir

        Assert-Match 'power limit равен максимуму платы' $out 'дешёвая обратимая проверка не должна теряться'
        Assert-Match 'PowerLimitPersist' $out 'и закрепление вместе с ней'
    } finally { Remove-Sandbox $sb }
}

Test 'отказавшие задачи планировщика попадают в план с причиной' {
    $sb = New-Sandbox 'analyze_plan_tasks'
    try {
        $rep = New-Report
        $rep.sections.scheduled_tasks_summary = [ordered]@{
            total = 310; ok_count = 200; info_count = 65; failed_count = 45
            groups = @(
                [ordered]@{ hex = '0x00000001'; count = 40; name = 'EXIT_CODE_1'
                            hint = 'задача вернула 1 — ошибка внутри самого скрипта'
                            examples = @('sofia_publish', 'sofia_reel') }
            )
        }
        $out = Invoke-Analyzer -Report $rep -Dir $sb.Dir

        Assert-Match 'отказов 45 из 310' $out 'отказы и общее число должны быть названы'
        Assert-Match 'не отказов: 65' $out 'состояния планировщика считаются отдельно'
        Assert-Match 'sofia_publish' $out 'примеры задач должны дойти до плана'
    } finally { Remove-Sandbox $sb }
}

Test 'упавшие сервисы попадают в план и не предлагается их перезапускать' {
    $sb = New-Sandbox 'analyze_plan_services'
    try {
        $rep = New-Report
        $rep.findings = @($rep.findings) + @(
            [ordered]@{ status = 'FAIL'; component = 'сервис Command Center'; evidence = 'нет ответа' },
            [ordered]@{ status = 'FAIL'; component = 'сервис Dashboard v2';   evidence = 'нет ответа' }
        )
        $out = Invoke-Analyzer -Report $rep -Dir $sb.Dir

        Assert-Match 'Command Center' $out 'сервис должен быть назван'
        Assert-Match 'не перезапускать' $out 'перезапуск маскирует симптом — это должно быть сказано'
    } finally { Remove-Sandbox $sb }
}

Test 'чистый отчёт не порождает пустой раздел плана' {
    $sb = New-Sandbox 'analyze_plan_empty'
    try {
        $rep = New-Report
        $rep.sections.Remove('gpu_owners')
        $rep.findings = @($rep.findings | Where-Object { $_.component -notlike 'сервис *' -and $_.component -ne 'GPU power limit' })
        $out = Invoke-Analyzer -Report $rep -Dir $sb.Dir
        Assert-NotMatch 'Закрыть независимо от гипотезы' $out 'пустого раздела быть не должно'
    } finally { Remove-Sandbox $sb }
}
