<#
    Контракт действия BadMemoryList в apply_safehold_fix.ps1.

    Это смягчение уже применено на машине владельца, поэтому цена ошибки
    здесь — испорченная загрузочная конфигурация. Тесты работают только с
    заглушкой bcdedit; если подменить настоящий bcdedit нельзя, тест
    пропускается, а не трогает реальную машину.
#>

$tool = Join-Path (Split-Path $PSScriptRoot -Parent) 'apply_safehold_fix.ps1'

function Initialize-BcdSandbox {
    param($Sandbox)
    $state = Install-FakeBcdedit -Dir $Sandbox.Dir
    if (-not $state) { Skip 'заглушку bcdedit не поставить — настоящий bcdedit остался бы первым в PATH' }
    Install-FakeNvidiaSmi -Dir $Sandbox.Dir | Out-Null
    $state
}

function Invoke-Tool {
    param([hashtable] $Arguments, [string] $StateDir)
    $p = @{ StateDir = $StateDir }
    foreach ($k in $Arguments.Keys) { $p[$k] = $Arguments[$k] }
    $out = & $tool @p *>&1 | Out-String
    [pscustomobject]@{ Out = $out; ExitCode = $LASTEXITCODE }
}

function New-WheaEvent {
    param([string] $Address, [int] $HoursAgo = 2)
    New-TestEvent -Id 47 -Provider 'Microsoft-Windows-WHEA-Logger' `
                  -Time (Get-Date).AddHours(-$HoursAgo) -PhysicalAddress $Address
}

# --------------------------------------------------------------------------

Test 'адрес из WHEA переводится в номер страницы и предлагается к исключению' {
    $sb = New-Sandbox 'bm_dryrun'
    try {
        $state = Initialize-BcdSandbox $sb
        Set-WinEventStub -Mode ok -Events @(New-WheaEvent -Address '0x3f8a21000')

        $r = Invoke-Tool -Arguments @{ Action = 'BadMemoryList' } -StateDir (Join-Path $sb.Dir 'state')

        # 0x3f8a21000 / 4096 = 0x3f8a21 = 4164129
        Assert-Match '4164129|0x3f8a21' $r.Out 'PFN должен быть посчитан и показан'
        Assert-Match 'DRY-RUN' $r.Out 'без -Confirm ничего не применяется'
        Assert-Equal 0 (Get-FakeBadMemoryList -StatePath $state).Count 'список не должен измениться'
    } finally { Remove-Sandbox $sb }
}

Test 'с -Confirm страница попадает в badmemorylist, прежний список сохраняется для отката' {
    $sb = New-Sandbox 'bm_apply'
    try {
        $state = Initialize-BcdSandbox $sb
        Set-WinEventStub -Mode ok -Events @(New-WheaEvent -Address '0x3f8a21000')
        $stateDir = Join-Path $sb.Dir 'state'

        $r = Invoke-Tool -Arguments @{ Action = 'BadMemoryList'; Confirm = $true } -StateDir $stateDir

        $list = @(Get-FakeBadMemoryList -StatePath $state)
        Assert-Equal 1 $list.Count 'страница должна быть добавлена'
        Assert-True (Test-Path (Join-Path $stateDir 'badmemorylist_rollback.json')) 'нужен файл отката'
        Assert-Match 'PASS' $r.Out 'применение должно отчитаться'

        # Без badmemoryaccess = no список исключений не применяется вовсе.
        Assert-Equal 'no' (Get-FakeBadMemoryAccess -StatePath $state) 'доступ к плохой памяти должен быть закрыт'
    } finally { Remove-Sandbox $sb }
}

Test 'уже исключённая страница не добавляется второй раз' {
    $sb = New-Sandbox 'bm_idempotent'
    try {
        $state = Initialize-BcdSandbox $sb
        Set-WinEventStub -Mode ok -Events @(New-WheaEvent -Address '0x3f8a21000')
        $stateDir = Join-Path $sb.Dir 'state'

        Invoke-Tool -Arguments @{ Action = 'BadMemoryList'; Confirm = $true } -StateDir $stateDir | Out-Null
        $after1 = Get-FakeBadMemoryList -StatePath $state
        Invoke-Tool -Arguments @{ Action = 'BadMemoryList'; Confirm = $true } -StateDir $stateDir | Out-Null
        $after2 = Get-FakeBadMemoryList -StatePath $state

        Assert-Equal $after1.Count $after2.Count 'повторный запуск не должен раздувать список'
    } finally { Remove-Sandbox $sb }
}

Test 'длинный список из строк продолжения разбирается целиком' {
    # bcdedit переносит длинный badmemorylist на строки с отступом. Наивный
    # разбор видит только первую строку и считает остальные страницы
    # неисключёнными — то есть молча добавляет их заново.
    $sb = New-Sandbox 'bm_continuation'
    try {
        $state = Initialize-BcdSandbox $sb
        $existing = @('0x1f93e5', '0x1b7fac', '0x2a0001', '0x2a0002', '0x3f8a21', '0x3f8a22')
        @{ list = $existing } | ConvertTo-Json | Out-File -FilePath $state -Encoding UTF8

        Set-WinEventStub -Mode ok -Events @(New-WheaEvent -Address '0x3f8a21000')
        $r = Invoke-Tool -Arguments @{ Action = 'BadMemoryList'; Confirm = $true } -StateDir (Join-Path $sb.Dir 'state')

        $after = Get-FakeBadMemoryList -StatePath $state
        Assert-Equal $existing.Count $after.Count 'страница со строки продолжения уже исключена — добавлять нечего'
    } finally { Remove-Sandbox $sb }
}

Test 'адрес из MemTest86 принимается параметром -Address' {
    $sb = New-Sandbox 'bm_manual'
    try {
        $state = Initialize-BcdSandbox $sb
        Set-WinEventStub -Mode ok -Events @()

        Invoke-Tool -Arguments @{ Action = 'BadMemoryList'; Address = @('0x1B7FAC8027'); Confirm = $true } `
                    -StateDir (Join-Path $sb.Dir 'state') | Out-Null

        Assert-Equal 1 (Get-FakeBadMemoryList -StatePath $state).Count 'ручной адрес должен быть исключён'
    } finally { Remove-Sandbox $sb }
}

Test 'Rollback возвращает прежний список' {
    $sb = New-Sandbox 'bm_rollback'
    try {
        $state = Initialize-BcdSandbox $sb
        @{ list = @('0x1f93e5') } | ConvertTo-Json | Out-File -FilePath $state -Encoding UTF8
        Set-WinEventStub -Mode ok -Events @(New-WheaEvent -Address '0x3f8a21000')
        $stateDir = Join-Path $sb.Dir 'state'

        Invoke-Tool -Arguments @{ Action = 'BadMemoryList'; Confirm = $true } -StateDir $stateDir | Out-Null
        Assert-Equal 2 (Get-FakeBadMemoryList -StatePath $state).Count 'страница добавлена'

        Invoke-Tool -Arguments @{ Action = 'Rollback'; Confirm = $true } -StateDir $stateDir | Out-Null
        # Обернуть обязательно: PowerShell разворачивает список из одного
        # элемента в скаляр, и $after[0] дал бы первый символ строки.
        $after = @(Get-FakeBadMemoryList -StatePath $state)
        Assert-Equal 1 $after.Count 'откат обязан вернуть прежний список'
        Assert-Equal '0x1f93e5' $after[0] 'и именно прежнее значение'
    } finally { Remove-Sandbox $sb }
}

Test 'без событий WHEA и без -Address исключать нечего' {
    $sb = New-Sandbox 'bm_nothing'
    try {
        $state = Initialize-BcdSandbox $sb
        Set-WinEventStub -Mode ok -Events @()
        $r = Invoke-Tool -Arguments @{ Action = 'BadMemoryList'; Confirm = $true } -StateDir (Join-Path $sb.Dir 'state')
        Assert-Equal 0 (Get-FakeBadMemoryList -StatePath $state).Count 'список не должен меняться'
    } finally { Remove-Sandbox $sb }
}
