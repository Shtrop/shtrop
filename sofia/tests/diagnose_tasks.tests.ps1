<#
    Интеграция: diagnose_host_safe_hold.ps1 должен отличать отказ задачи от
    состояния планировщика.

    На машине студии 310 задач Sofia. Прежняя версия объявляла отказом любой
    ненулевой код — включая «выполняется сейчас» и «ни разу не запускалась», —
    и давала WARN там, где отказов могло не быть вовсе.
#>

$tool = Join-Path (Split-Path $PSScriptRoot -Parent) 'diagnose_host_safe_hold.ps1'

function Invoke-Diagnose {
    param([string] $SofiaRoot, [string] $OutDir)
    & $tool -SofiaRoot $SofiaRoot -OutDir $OutDir -Days 1 *>&1 | Out-String | Out-Null
    Get-Content (Join-Path $OutDir 'safehold_report.json') -Raw | ConvertFrom-Json
}

function New-Root {
    param([string] $Dir)
    New-Item -ItemType Directory -Force -Path (Join-Path $Dir 'control_flags') | Out-Null
    $Dir
}

# --------------------------------------------------------------------------

Test 'выполняющиеся и ни разу не запускавшиеся задачи не считаются отказом' {
    $sb = New-Sandbox 'diag_tasks_ok'
    try {
        Install-FakeNvidiaSmi -Dir $sb.Dir | Out-Null
        Set-WinEventStub -Mode ok -Events @()
        Set-GpuCounterStub -PerPid @{}
        Set-ScheduledTaskStub -Tasks @(
            @{ name = 'sofia_photo';  code = 0 },
            @{ name = 'sofia_reel';   code = 0x41301 },
            @{ name = 'sofia_trends'; code = 0x41303 },
            @{ name = 'sofia_queue';  code = 0x41325 }
        )

        $r = Invoke-Diagnose -SofiaRoot (New-Root (Join-Path $sb.Dir 'studio')) -OutDir (Join-Path $sb.Dir 'out')
        $f = @($r.findings | Where-Object { $_.component -eq 'Task Scheduler' })

        Assert-Equal 'PASS' $f[0].status 'отказов нет — WARN здесь был бы ложным'
        Assert-Equal 3 $r.sections.scheduled_tasks_summary.info_count 'три состояния планировщика'
        Assert-Equal 0 $r.sections.scheduled_tasks_summary.failed_count 'ни одного отказа'
    } finally { Remove-Sandbox $sb }
}

Test 'настоящие отказы группируются по причине и называются в находке' {
    $sb = New-Sandbox 'diag_tasks_fail'
    try {
        Install-FakeNvidiaSmi -Dir $sb.Dir | Out-Null
        Set-WinEventStub -Mode ok -Events @()
        Set-GpuCounterStub -PerPid @{}
        Set-ScheduledTaskStub -Tasks @(
            @{ name = 'sofia_pub_a';  code = 1 },
            @{ name = 'sofia_pub_b';  code = 1 },
            @{ name = 'sofia_pub_c';  code = 1 },
            @{ name = 'sofia_render'; code = 0x41306 },
            @{ name = 'sofia_ok';     code = 0 },
            @{ name = 'sofia_run';    code = 0x41301 }
        )

        $r = Invoke-Diagnose -SofiaRoot (New-Root (Join-Path $sb.Dir 'studio')) -OutDir (Join-Path $sb.Dir 'out')
        $sum = $r.sections.scheduled_tasks_summary
        $f = @($r.findings | Where-Object { $_.component -eq 'Task Scheduler' })

        Assert-Equal 'WARN' $f[0].status 'отказы есть'
        Assert-Equal 4 $sum.failed_count 'четыре отказа'
        Assert-Equal 1 $sum.info_count 'выполняющаяся задача в отказы не попала'
        Assert-Equal '0x00000001' $sum.groups[0].hex 'самая частая причина первой'
        Assert-Equal 3 $sum.groups[0].count 'три задачи с этой причиной'
        Assert-Match '0x00000001' $f[0].evidence 'код самой частой причины должен быть в доказательстве'
        Assert-Match 'sofia_pub' ($sum.groups[0].examples -join ',') 'примеры задач должны сохраняться'
    } finally { Remove-Sandbox $sb }
}

Test 'недоступный планировщик даёт NOT_MEASURED, а не PASS' {
    $sb = New-Sandbox 'diag_tasks_denied'
    try {
        Install-FakeNvidiaSmi -Dir $sb.Dir | Out-Null
        Set-WinEventStub -Mode ok -Events @()
        Set-GpuCounterStub -PerPid @{}
        Set-ScheduledTaskStub -Tasks $null

        $r = Invoke-Diagnose -SofiaRoot (New-Root (Join-Path $sb.Dir 'studio')) -OutDir (Join-Path $sb.Dir 'out')
        $f = @($r.findings | Where-Object { $_.component -eq 'Task Scheduler' })
        Assert-Equal 'NOT_MEASURED' $f[0].status 'нет доступа — это не «отказов нет»'
    } finally { Remove-Sandbox $sb }
}
