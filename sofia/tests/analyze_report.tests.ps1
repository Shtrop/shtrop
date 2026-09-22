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
