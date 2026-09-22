<#
    Контракт apply_safehold_fix.ps1.

    Скрипт меняет состояние машины, поэтому проверяется главное: без -Confirm
    не меняется ничего, с -Confirm изменение обратимо, а смягчение, которое не
    переживает перезагрузку, честно помечается как непережившее.
#>

$tool = Join-Path (Split-Path $PSScriptRoot -Parent) 'apply_safehold_fix.ps1'

function Invoke-Tool {
    param([hashtable] $Arguments, [string] $StateDir)
    $p = @{ StateDir = $StateDir }
    foreach ($k in $Arguments.Keys) { $p[$k] = $Arguments[$k] }
    $out = & $tool @p *>&1 | Out-String
    [pscustomobject]@{ Out = $out; ExitCode = $LASTEXITCODE }
}

# --------------------------------------------------------------------------

Test 'Status ничего не меняет и не трогает hold' {
    $sb = New-Sandbox 'fix_status'
    try {
        $gs = Install-FakeNvidiaSmi -Dir $sb.Dir
        $r = Invoke-Tool -Arguments @{ Action = 'Status' } -StateDir (Join-Path $sb.Dir 'state')
        Assert-Equal 600 (Get-FakeGpuState -StatePath $gs).power_limit 'лимит не должен меняться'
        Assert-Match 'HOST_SAFE_HOLD' $r.Out 'напоминание про hold должно остаться'
    } finally { Remove-Sandbox $sb }
}

Test 'PowerLimit без -Confirm не меняет лимит' {
    $sb = New-Sandbox 'fix_pl_dry'
    try {
        $gs = Install-FakeNvidiaSmi -Dir $sb.Dir
        $r = Invoke-Tool -Arguments @{ Action = 'PowerLimit'; Percent = 75 } -StateDir (Join-Path $sb.Dir 'state')
        Assert-Match 'DRY-RUN' $r.Out 'должен сообщить про dry-run'
        Assert-Equal 600 (Get-FakeGpuState -StatePath $gs).power_limit 'лимит обязан остаться прежним'
    } finally { Remove-Sandbox $sb }
}

Test 'PowerLimit с -Confirm ставит лимит и сохраняет откат' {
    $sb = New-Sandbox 'fix_pl_apply'
    try {
        $gs = Install-FakeNvidiaSmi -Dir $sb.Dir
        $stateDir = Join-Path $sb.Dir 'state'
        $r = Invoke-Tool -Arguments @{ Action = 'PowerLimit'; Percent = 75; Confirm = $true } -StateDir $stateDir
        Assert-Match 'PASS' $r.Out 'лимит должен примениться'
        Assert-Equal 450 (Get-FakeGpuState -StatePath $gs).power_limit '75% от 600 W'
        $rb = Get-Content (Join-Path $stateDir 'gpu0_powerlimit_rollback.json') -Raw | ConvertFrom-Json
        Assert-Equal 600 $rb.original_limit_w 'исходный лимит должен быть сохранён'
    } finally { Remove-Sandbox $sb }
}

Test 'PowerLimit предупреждает, что лимит не переживёт перезагрузку' {
    $sb = New-Sandbox 'fix_pl_warn'
    try {
        Install-FakeNvidiaSmi -Dir $sb.Dir | Out-Null
        Install-FakeSchtasks -Dir $sb.Dir | Out-Null
        $r = Invoke-Tool -Arguments @{ Action = 'PowerLimit'; Percent = 75; Confirm = $true } -StateDir (Join-Path $sb.Dir 'state')
        Assert-Match 'PowerLimitPersist' $r.Out 'после применения обязан быть показан способ закрепления'
    } finally { Remove-Sandbox $sb }
}

Test 'PowerLimit без прав администратора даёт FAIL и ненулевой код' {
    $sb = New-Sandbox 'fix_pl_denied'
    try {
        $gs = Install-FakeNvidiaSmi -Dir $sb.Dir
        Set-FakeGpuDenyPowerLimit -StatePath $gs
        $r = Invoke-Tool -Arguments @{ Action = 'PowerLimit'; Percent = 75; Confirm = $true } -StateDir (Join-Path $sb.Dir 'state')
        Assert-Match 'FAIL' $r.Out 'отказ должен быть виден'
        Assert-True ($r.ExitCode -ne 0) 'код возврата обязан быть ненулевым'
        Assert-Equal 600 (Get-FakeGpuState -StatePath $gs).power_limit 'лимит не изменился'
    } finally { Remove-Sandbox $sb }
}

Test 'PowerLimitPersist без -Confirm не создаёт задачу' {
    $sb = New-Sandbox 'fix_persist_dry'
    try {
        Install-FakeNvidiaSmi -Dir $sb.Dir -State @{ power_limit = 450 } | Out-Null
        $tasks = Install-FakeSchtasks -Dir $sb.Dir
        $r = Invoke-Tool -Arguments @{ Action = 'PowerLimitPersist' } -StateDir (Join-Path $sb.Dir 'state')
        Assert-Match 'DRY-RUN' $r.Out 'должен сообщить про dry-run'
        Assert-Equal 0 (Get-FakeTasks -TasksPath $tasks).Count 'задача не должна создаваться без -Confirm'
    } finally { Remove-Sandbox $sb }
}

Test 'PowerLimitPersist с -Confirm закрепляет текущий лимит на старт системы' {
    $sb = New-Sandbox 'fix_persist_apply'
    try {
        Install-FakeNvidiaSmi -Dir $sb.Dir -State @{ power_limit = 450 } | Out-Null
        $tasks = Install-FakeSchtasks -Dir $sb.Dir
        $stateDir = Join-Path $sb.Dir 'state'
        $r = Invoke-Tool -Arguments @{ Action = 'PowerLimitPersist'; Confirm = $true } -StateDir $stateDir

        Assert-Match 'PASS' $r.Out 'закрепление должно пройти'
        $t = Get-FakeTasks -TasksPath $tasks
        Assert-Equal 1 $t.Count 'должна появиться ровно одна задача'
        Assert-Match 'Sofia' $t[0].name 'имя задачи должно быть узнаваемым'

        $rbPath = Join-Path $stateDir 'gpu0_powerlimit_persist_rollback.json'
        Assert-True (Test-Path $rbPath) 'нужен файл отката закрепления'
        $rb = Get-Content $rbPath -Raw | ConvertFrom-Json
        Assert-Equal 450 $rb.watts 'закрепляется именно текущий лимит'
        Assert-Equal $rb.wrapper_cmd $t[0].run 'задача обязана запускать созданную обёртку'
        Assert-Match '-pl 450' (Get-Content $rb.wrapper_cmd -Raw) 'обёртка обязана восстанавливать этот лимит'
    } finally { Remove-Sandbox $sb }
}

Test 'PowerLimitPersist отказывается закреплять максимум платы' {
    $sb = New-Sandbox 'fix_persist_nothing'
    try {
        Install-FakeNvidiaSmi -Dir $sb.Dir -State @{ power_limit = 600 } | Out-Null
        $tasks = Install-FakeSchtasks -Dir $sb.Dir
        $r = Invoke-Tool -Arguments @{ Action = 'PowerLimitPersist'; Confirm = $true } -StateDir (Join-Path $sb.Dir 'state')
        Assert-Equal 0 (Get-FakeTasks -TasksPath $tasks).Count 'закреплять нечего — лимит не ограничен'
        Assert-Match 'максимум|нечего' $r.Out 'причина отказа должна быть названа'
    } finally { Remove-Sandbox $sb }
}

Test 'Rollback снимает и лимит, и закрепление' {
    $sb = New-Sandbox 'fix_rollback'
    try {
        $gs = Install-FakeNvidiaSmi -Dir $sb.Dir
        $tasks = Install-FakeSchtasks -Dir $sb.Dir
        $stateDir = Join-Path $sb.Dir 'state'

        Invoke-Tool -Arguments @{ Action = 'PowerLimit'; Percent = 75; Confirm = $true } -StateDir $stateDir | Out-Null
        Invoke-Tool -Arguments @{ Action = 'PowerLimitPersist'; Confirm = $true } -StateDir $stateDir | Out-Null
        Assert-Equal 1 (Get-FakeTasks -TasksPath $tasks).Count 'задача создана'

        $r = Invoke-Tool -Arguments @{ Action = 'Rollback'; Confirm = $true } -StateDir $stateDir
        Assert-Equal 0 (Get-FakeTasks -TasksPath $tasks).Count 'откат обязан снять закрепление'
        Assert-Equal 600 (Get-FakeGpuState -StatePath $gs).power_limit 'откат обязан вернуть исходный лимит'
        Assert-Match 'PASS' $r.Out 'откат должен отчитаться'
    } finally { Remove-Sandbox $sb }
}

Test 'Status показывает, закреплён лимит или нет' {
    $sb = New-Sandbox 'fix_status_persist'
    try {
        Install-FakeNvidiaSmi -Dir $sb.Dir -State @{ power_limit = 450 } | Out-Null
        Install-FakeSchtasks -Dir $sb.Dir | Out-Null
        $stateDir = Join-Path $sb.Dir 'state'

        $before = Invoke-Tool -Arguments @{ Action = 'Status' } -StateDir $stateDir
        Assert-Match 'не переживёт|не закреплён' $before.Out 'незакреплённый лимит должен быть отмечен'

        Invoke-Tool -Arguments @{ Action = 'PowerLimitPersist'; Confirm = $true } -StateDir $stateDir | Out-Null
        $after = Invoke-Tool -Arguments @{ Action = 'Status' } -StateDir $stateDir
        Assert-Match 'закреплён' $after.Out 'закрепление должно быть видно в Status'
    } finally { Remove-Sandbox $sb }
}
