<#
    Контракт watch_host_stability.ps1.

    Окно наблюдения — единственное доказательство, по которому владелец снимает
    HOST_SAFE_HOLD. Поэтому цена ложного PASS здесь максимальная: он возвращает
    производство на хост, который продолжает падать. Тесты защищают именно это.
#>

$watcher = Join-Path (Split-Path $PSScriptRoot -Parent) 'watch_host_stability.ps1'

function Invoke-Watcher {
    param(
        [hashtable] $Arguments = @{},
        [string] $OutDir
    )
    $p = @{ Hours = 0.0006; IntervalSeconds = 1; OutDir = $OutDir }
    foreach ($k in $Arguments.Keys) { $p[$k] = $Arguments[$k] }
    & $watcher @p | Out-Null
    $summary = Join-Path $OutDir 'stability_summary.json'
    if (-not (Test-Path $summary)) { throw 'итоговый JSON не создан' }
    Get-Content $summary -Raw | ConvertFrom-Json
}

# --------------------------------------------------------------------------

Test 'недоступный журнал System даёт NOT_MEASURED, а не PASS' {
    $sb = New-Sandbox 'watch_denied'
    try {
        Set-WinEventStub -Mode denied
        $r = Invoke-Watcher -OutDir (Join-Path $sb.Dir 'out')
        Assert-Equal 'NOT_MEASURED' $r.verdict 'вердикт при недоступном журнале'
        Assert-True ([bool]$r.event_log_blocked) 'флаг event_log_blocked должен быть выставлен'
        Assert-True (-not $r.hold_exit_ready) 'выход из hold не может быть разрешён без измерения'
    } finally { Remove-Sandbox $sb }
}

Test 'чистое, но короткое окно не разрешает выход из hold' {
    $sb = New-Sandbox 'watch_short'
    try {
        Set-WinEventStub -Mode ok -Events @()
        $r = Invoke-Watcher -OutDir (Join-Path $sb.Dir 'out')
        Assert-Equal 'PASS' $r.verdict 'событий нет — вердикт по стабильности PASS'
        Assert-True (-not $r.hold_exit_ready) 'окна в секунды недостаточно для выхода из hold'
        Assert-Match 'window_short' ($r.hold_exit_blockers -join ';') 'причина отказа должна быть названа'
        Assert-Equal 48 $r.required_hours 'порог по умолчанию — 48 ч из runbook'
    } finally { Remove-Sandbox $sb }
}

Test 'событие Kernel-Power 41 внутри окна даёт FAIL' {
    $sb = New-Sandbox 'watch_kp41'
    try {
        Set-WinEventStub -Mode ok -Events @(
            New-TestEvent -Id 41 -Provider 'Microsoft-Windows-Kernel-Power' -Time (Get-Date).AddSeconds(30)
        )
        $r = Invoke-Watcher -OutDir (Join-Path $sb.Dir 'out')
        Assert-Equal 'FAIL' $r.verdict 'краш внутри окна'
        Assert-True (-not $r.hold_exit_ready) 'при FAIL выход из hold запрещён'
    } finally { Remove-Sandbox $sb }
}

Test 'новая ошибка WHEA без краха тоже даёт FAIL' {
    $sb = New-Sandbox 'watch_whea'
    try {
        Set-WinEventStub -Mode ok -Events @(
            New-TestEvent -Id 47 -Provider 'Microsoft-Windows-WHEA-Logger' -Time (Get-Date).AddSeconds(30) -PhysicalAddress '0x3f8a21000'
        )
        $r = Invoke-Watcher -OutDir (Join-Path $sb.Dir 'out')
        Assert-Equal 'FAIL' $r.verdict 'корректируемая ошибка — тоже грязное окно'
        Assert-Equal 1 @($r.whea_detected).Count 'ошибка WHEA должна попасть в отчёт'
    } finally { Remove-Sandbox $sb }
}

Test 'возобновление окна после ресета видит событие, случившееся до перезапуска' {
    $sb = New-Sandbox 'watch_resume'
    try {
        $out = Join-Path $sb.Dir 'out'
        New-Item -ItemType Directory -Force -Path $out | Out-Null

        # Первый прогон: окно стартовало 3 часа назад, потом хост ушёл в ресет.
        Set-WinEventStub -Mode ok -Events @()
        Invoke-Watcher -OutDir $out | Out-Null

        $statePath = Join-Path $out 'window_state.json'
        Assert-True (Test-Path $statePath) 'состояние окна должно сохраняться для возобновления'
        $st = Get-Content $statePath -Raw | ConvertFrom-Json
        $st.window_start = (Get-Date).AddHours(-3).ToString('o')
        $st | ConvertTo-Json -Depth 6 | Out-File -FilePath $statePath -Encoding UTF8

        # Ресет случился час назад: событие 41 уже в журнале, но до перезапуска скрипта.
        Set-WinEventStub -Mode ok -Events @(
            New-TestEvent -Id 41 -Provider 'Microsoft-Windows-Kernel-Power' -Time (Get-Date).AddHours(-1)
        )
        $r = Invoke-Watcher -OutDir $out -Arguments @{ Resume = $true }

        Assert-Equal 'FAIL' $r.verdict 'событие до перезапуска обязано обнулить окно'
        Assert-True ($r.window_span_hours -ge 2.5) ('окно должно считаться от исходного старта, получено ' + $r.window_span_hours)
    } finally { Remove-Sandbox $sb }
}

Test 'возобновление давно брошенного окна не засчитывается как выполненный порог' {
    $sb = New-Sandbox 'watch_stale_resume'
    try {
        $out = Join-Path $sb.Dir 'out'
        New-Item -ItemType Directory -Force -Path $out | Out-Null

        Set-WinEventStub -Mode ok -Events @()
        Invoke-Watcher -OutDir $out | Out-Null

        # Окно якобы открыто месяц назад, а наблюдали за ним секунды.
        $statePath = Join-Path $out 'window_state.json'
        $st = Get-Content $statePath -Raw | ConvertFrom-Json
        $st.window_start = (Get-Date).AddDays(-30).ToString('o')
        $st.observed_hours = 0.001
        $st | ConvertTo-Json -Depth 6 | Out-File -FilePath $statePath -Encoding UTF8

        $r = Invoke-Watcher -OutDir $out -Arguments @{ Resume = $true }

        Assert-Equal 'PASS' $r.verdict 'крахов не было'
        Assert-True ($r.window_span_hours -ge 700) 'календарный размах действительно большой'
        Assert-True (-not $r.hold_exit_ready) 'но наблюдения за это окно почти не было'
        Assert-Match 'window_short' ($r.hold_exit_blockers -join ';') 'порог считается по наблюдению'
        Assert-Match 'coverage_gap' ($r.hold_exit_blockers -join ';') 'пропуск окна должен быть назван'
    } finally { Remove-Sandbox $sb }
}

Test 'откат power limit посреди окна снимает право на выход из hold' {
    $sb = New-Sandbox 'watch_pl_drift'
    try {
        Install-FakeNvidiaSmi -Dir $sb.Dir -State @{
            power_limit          = 450
            power_limit_sequence = @(450, 450, 600, 600, 600)
        } | Out-Null
        Set-WinEventStub -Mode ok -Events @()
        # LimitSettleSeconds = 2: в тесте опрос раз в секунду, поэтому режимом
        # считается то, что продержалось два опроса. В production порог 600 с.
        $r = Invoke-Watcher -OutDir (Join-Path $sb.Dir 'out') `
                            -Arguments @{ Hours = 0.0025; LimitSettleSeconds = 2 }

        Assert-Equal 'PASS' $r.verdict 'крахов не было'
        Assert-True ([bool]$r.power_limit_changed) 'смена лимита обязана быть замечена'
        Assert-True (-not $r.hold_exit_ready) 'смягчение не держалось всё окно — окно не доказательство'
        Assert-Match 'power_limit_changed' ($r.hold_exit_blockers -join ';') 'причина отказа должна быть названа'
    } finally { Remove-Sandbox $sb }
}

Test 'стабильный power limit не мешает выходу из hold' {
    $sb = New-Sandbox 'watch_pl_stable'
    try {
        Install-FakeNvidiaSmi -Dir $sb.Dir -State @{ power_limit = 450 } | Out-Null
        Set-WinEventStub -Mode ok -Events @()
        $r = Invoke-Watcher -OutDir (Join-Path $sb.Dir 'out') `
                            -Arguments @{ RequiredHours = 0; Hours = 0.002; LimitSettleSeconds = 2 }

        Assert-Equal 'PASS' $r.verdict 'крахов не было'
        Assert-True (-not $r.power_limit_changed) 'лимит не менялся'
        Assert-True ([bool]$r.hold_exit_ready) 'при нулевом пороге и чистом окне выход разрешён'
    } finally { Remove-Sandbox $sb }
}

Test 'смена power limit на перезагрузке замечается после -Resume' {
    # Лимит теряется именно на перезагрузке, а окно её переживает. Если
    # набор виденных значений сбрасывать посессионно, в новом сеансе значение
    # одно — и «лимит не менялся» выглядело бы правдой при смене 450 -> 600.
    $sb = New-Sandbox 'watch_pl_resume'
    try {
        $out = Join-Path $sb.Dir 'out'
        Install-FakeNvidiaSmi -Dir $sb.Dir -State @{ power_limit = 450 } | Out-Null
        Set-WinEventStub -Mode ok -Events @()

        Invoke-Watcher -OutDir $out -Arguments @{ Hours = 0.0025; LimitSettleSeconds = 2 } | Out-Null

        $statePath = Join-Path $out 'window_state.json'
        $st = Get-Content $statePath -Raw | ConvertFrom-Json
        Assert-True (@($st.power_limit_regimes).Count -ge 1) 'время удержания режимов должно сохраняться в состоянии окна'

        # После перезагрузки лимит вернулся к максимуму платы и там остался.
        $gs = Join-Path $sb.Dir 'bin/gpu_state.json'
        $g = Get-Content $gs -Raw | ConvertFrom-Json
        $g.power_limit = 600
        $g | ConvertTo-Json -Depth 6 | Out-File -FilePath $gs -Encoding UTF8

        $r = Invoke-Watcher -OutDir $out `
                            -Arguments @{ Resume = $true; RequiredHours = 0; Hours = 0.0025; LimitSettleSeconds = 2 }

        Assert-True ([bool]$r.power_limit_changed) 'смена лимита между сеансами обязана быть замечена'
        Assert-True (-not $r.hold_exit_ready) 'окно измеряло два разных режима питания'
        Assert-Match 'power_limit_changed' ($r.hold_exit_blockers -join ';') 'причина должна быть названа'
    } finally { Remove-Sandbox $sb }
}

Test 'одиночное показание на старте системы не блокирует выход навсегда' {
    # Задача закрепления срабатывает с задержкой, поэтому сразу после загрузки
    # один опрос видит максимум платы. Если засчитывать такие показания как
    # режим, они копятся в состоянии окна и блокируют выход из hold навсегда:
    # исправить это можно было бы только удалением файла состояния вместе с
    # набранными часами.
    $sb = New-Sandbox 'watch_pl_blip'
    try {
        $out = Join-Path $sb.Dir 'out'
        Install-FakeNvidiaSmi -Dir $sb.Dir -State @{ power_limit = 450 } | Out-Null
        Set-WinEventStub -Mode ok -Events @()

        Invoke-Watcher -OutDir $out -Arguments @{ Hours = 0.0025; LimitSettleSeconds = 2 } | Out-Null

        # Перезагрузка: первый опрос застаёт максимум платы, дальше лимит на
        # месте. Переходное показание не должно стать режимом.
        $gs = Join-Path $sb.Dir 'bin/gpu_state.json'
        $g = Get-Content $gs -Raw | ConvertFrom-Json
        $g.power_limit = 600
        $g.power_limit_sequence = @(600, 450, 450, 450, 450, 450)
        $g | ConvertTo-Json -Depth 6 | Out-File -FilePath $gs -Encoding UTF8

        $r = Invoke-Watcher -OutDir $out `
                            -Arguments @{ Resume = $true; RequiredHours = 0; Hours = 0.003; LimitSettleSeconds = 2 }

        Assert-Equal 450 ([int]$r.power_limit_w_last) 'на конце окна лимит на месте'
        Assert-True (-not $r.power_limit_changed) 'одиночное показание — не смена режима'
        Assert-True ([bool]$r.hold_exit_ready) 'и оно не должно запирать выход из hold'
    } finally { Remove-Sandbox $sb }
}
