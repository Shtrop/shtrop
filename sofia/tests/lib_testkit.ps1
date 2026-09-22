<#
.SYNOPSIS
    Мини-фреймворк для тестов инструментов sofia/: проверки, песочница GPU,
    подмена Get-WinEvent.

.DESCRIPTION
    Инструменты написаны под Windows, но почти вся их логика — разбор текста и
    принятие решений. Тесты запускаются где угодно, где есть PowerShell 7:
      - nvidia-smi и bcdedit подменяются исполняемыми заглушками в PATH;
      - Get-WinEvent подменяется глобальной функцией, которую наследует
        дочерняя область тестируемого скрипта.

    Ничего в дереве студии тесты не трогают: всё происходит во временном
    каталоге песочницы.
#>

$global:SofiaTestResults = @()

function Test {
    param(
        [Parameter(Mandatory)][string] $Name,
        [Parameter(Mandatory)][scriptblock] $Body
    )
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    try {
        & $Body
        $sw.Stop()
        $global:SofiaTestResults += [pscustomobject]@{ Name = $Name; Status = 'PASS'; Error = ''; Ms = $sw.ElapsedMilliseconds }
        Write-Host ("  PASS  {0}" -f $Name) -ForegroundColor Green
    } catch {
        $sw.Stop()
        $msg = $_.Exception.Message
        if ($msg -like 'SOFIA_TEST_SKIP:*') {
            $reason = $msg.Substring('SOFIA_TEST_SKIP:'.Length)
            $global:SofiaTestResults += [pscustomobject]@{ Name = $Name; Status = 'SKIP'; Error = $reason; Ms = $sw.ElapsedMilliseconds }
            Write-Host ("  SKIP  {0}" -f $Name) -ForegroundColor Yellow
            Write-Host ("        {0}" -f $reason) -ForegroundColor DarkYellow
            return
        }
        $global:SofiaTestResults += [pscustomobject]@{ Name = $Name; Status = 'FAIL'; Error = $msg; Ms = $sw.ElapsedMilliseconds }
        Write-Host ("  FAIL  {0}" -f $Name) -ForegroundColor Red
        Write-Host ("        {0}" -f $msg) -ForegroundColor DarkRed
    }
}

function Skip {
    <#
        Пропустить тест: среда не даёт выполнить его безопасно.
        Пропуск не равен успеху и печатается отдельно.
    #>
    param([string] $Reason = 'условия окружения')
    throw ("SOFIA_TEST_SKIP:{0}" -f $Reason)
}

function Assert-True {
    param($Condition, [string] $Message = 'условие ложно')
    if (-not $Condition) { throw $Message }
}

function Assert-Equal {
    param($Expected, $Actual, [string] $Message = 'значения не совпали')
    if ("$Expected" -ne "$Actual") { throw ("{0}: ожидалось '{1}', получено '{2}'" -f $Message, $Expected, $Actual) }
}

function Assert-Match {
    param([string] $Pattern, $Text, [string] $Message = 'текст не совпал с шаблоном')
    if (("$Text") -notmatch $Pattern) { throw ("{0}: '{1}' не соответствует /{2}/" -f $Message, ("$Text"), $Pattern) }
}

function Assert-NotMatch {
    param([string] $Pattern, $Text, [string] $Message = 'текст совпал с запрещённым шаблоном')
    if (("$Text") -match $Pattern) { throw ("{0}: '{1}' соответствует /{2}/" -f $Message, ("$Text"), $Pattern) }
}

# --------------------------------------------------------------------------
# Песочница
# --------------------------------------------------------------------------

function New-Sandbox {
    param([string] $Label = 'sofia_test')
    $dir = Join-Path ([System.IO.Path]::GetTempPath()) ("{0}_{1}" -f $Label, [guid]::NewGuid().ToString('N').Substring(0, 8))
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    [pscustomobject]@{ Dir = $dir }
}

function Remove-Sandbox {
    param($Sandbox)
    if ($Sandbox -and (Test-Path $Sandbox.Dir)) {
        Remove-Item -LiteralPath $Sandbox.Dir -Recurse -Force -ErrorAction SilentlyContinue
    }
}

function Get-PwshPath {
    $p = (Get-Process -Id $PID).Path
    if ($p) { return $p }
    return 'pwsh'
}

function New-ShimExecutable {
    <#
        Кладёт в $Dir исполняемый файл $Name, который зовёт $ScriptPath через
        текущий pwsh и передаёт все аргументы.
    #>
    param(
        [Parameter(Mandatory)][string] $Dir,
        [Parameter(Mandatory)][string] $Name,
        [Parameter(Mandatory)][string] $ScriptPath
    )
    $pwsh = Get-PwshPath
    if ($IsWindows) {
        $shim = Join-Path $Dir ("{0}.cmd" -f $Name)
        "@echo off`r`n`"$pwsh`" -NoLogo -NoProfile -File `"$ScriptPath`" %*`r`n" |
            Out-File -FilePath $shim -Encoding ASCII
    } else {
        $shim = Join-Path $Dir $Name
        "#!/bin/sh`nexec `"$pwsh`" -NoLogo -NoProfile -File `"$ScriptPath`" `"`$@`"`n" |
            Out-File -FilePath $shim -Encoding ASCII
        & chmod '+x' $shim
    }
    $shim
}

$script:DefaultGpuState = [ordered]@{
    name            = 'NVIDIA GeForce RTX 5090'
    temperature     = 46
    power_draw      = 62.5
    power_limit     = 600
    power_min_limit = 300
    power_max_limit = 600
    clocks_sm       = 2520
    utilization     = 0
    memory_used     = 512
    memory_total    = 32607
    compute_apps    = @()
    throttle_active = @()
    power_limit_sequence = @()
}

function Install-FakeNvidiaSmi {
    <#
        Ставит заглушку nvidia-smi в PATH текущего процесса.
        Возвращает путь к файлу состояния, чтобы тест мог его править и читать.
    #>
    param(
        [Parameter(Mandatory)][string] $Dir,
        [hashtable] $State = @{}
    )
    $binDir = Join-Path $Dir 'bin'
    New-Item -ItemType Directory -Force -Path $binDir | Out-Null

    $s = [ordered]@{}
    foreach ($k in $script:DefaultGpuState.Keys) { $s[$k] = $script:DefaultGpuState[$k] }
    foreach ($k in $State.Keys) { $s[$k] = $State[$k] }

    $statePath = Join-Path $binDir 'gpu_state.json'
    $s | ConvertTo-Json -Depth 6 | Out-File -FilePath $statePath -Encoding UTF8

    Copy-Item (Join-Path $PSScriptRoot 'fake_nvidia_smi.ps1') (Join-Path $binDir 'fake_nvidia_smi.ps1') -Force
    New-ShimExecutable -Dir $binDir -Name 'nvidia-smi' -ScriptPath (Join-Path $binDir 'fake_nvidia_smi.ps1') | Out-Null

    $env:PATH = $binDir + [System.IO.Path]::PathSeparator + $env:PATH
    $statePath
}

function Install-FakeSchtasks {
    <#
        Ставит заглушку schtasks в PATH текущего процесса.
        Возвращает путь к tasks.json, чтобы тест мог проверить содержимое.
    #>
    param([Parameter(Mandatory)][string] $Dir)
    $binDir = Join-Path $Dir 'bin'
    New-Item -ItemType Directory -Force -Path $binDir | Out-Null
    Copy-Item (Join-Path $PSScriptRoot 'fake_schtasks.ps1') (Join-Path $binDir 'fake_schtasks.ps1') -Force
    New-ShimExecutable -Dir $binDir -Name 'schtasks' -ScriptPath (Join-Path $binDir 'fake_schtasks.ps1') | Out-Null
    if (($env:PATH -split [System.IO.Path]::PathSeparator) -notcontains $binDir) {
        $env:PATH = $binDir + [System.IO.Path]::PathSeparator + $env:PATH
    }
    Join-Path $binDir 'tasks.json'
}

function Install-FakeBcdedit {
    <#
        Ставит заглушку bcdedit.exe в PATH и возвращает путь к файлу состояния.

        Возвращает $null, если подменить настоящий bcdedit нельзя (Windows:
        реальный bcdedit.exe останется первым в PATH). Тест в этом случае
        обязан пропустить себя, а не работать с загрузочной конфигурацией
        настоящей машины.
    #>
    param([Parameter(Mandatory)][string] $Dir)
    if ($IsWindows) { return $null }

    $binDir = Join-Path $Dir 'bin'
    New-Item -ItemType Directory -Force -Path $binDir | Out-Null
    Copy-Item (Join-Path $PSScriptRoot 'fake_bcdedit.ps1') (Join-Path $binDir 'fake_bcdedit.ps1') -Force
    New-ShimExecutable -Dir $binDir -Name 'bcdedit.exe' -ScriptPath (Join-Path $binDir 'fake_bcdedit.ps1') | Out-Null
    if (($env:PATH -split [System.IO.Path]::PathSeparator) -notcontains $binDir) {
        $env:PATH = $binDir + [System.IO.Path]::PathSeparator + $env:PATH
    }

    $statePath = Join-Path $binDir 'badmemory.json'
    @{ list = @() } | ConvertTo-Json | Out-File -FilePath $statePath -Encoding UTF8

    # Убедиться, что в PATH первым стоит именно заглушка.
    $resolved = (Get-Command bcdedit.exe -ErrorAction SilentlyContinue)
    if (-not $resolved -or $resolved.Source -notlike ("{0}*" -f $binDir)) { return $null }
    $statePath
}

function Get-FakeBadMemoryList {
    param([Parameter(Mandatory)][string] $StatePath)
    @((Get-Content $StatePath -Raw | ConvertFrom-Json).list | Where-Object { $_ })
}

function Get-FakeBadMemoryAccess {
    param([Parameter(Mandatory)][string] $StatePath)
    "$((Get-Content $StatePath -Raw | ConvertFrom-Json).access)"
}

function Get-FakeTasks {
    param([Parameter(Mandatory)][string] $TasksPath)
    if (-not (Test-Path $TasksPath)) { return @() }
    @(Get-Content $TasksPath -Raw | ConvertFrom-Json | Where-Object { $_ })
}

function Get-FakeGpuState {
    param([Parameter(Mandatory)][string] $StatePath)
    Get-Content $StatePath -Raw | ConvertFrom-Json
}

function Set-FakeGpuDenyPowerLimit {
    param([Parameter(Mandatory)][string] $StatePath, [bool] $Deny = $true)
    $flag = Join-Path (Split-Path $StatePath -Parent) 'deny.flag'
    if ($Deny) { 'deny' | Out-File -FilePath $flag -Encoding ASCII }
    elseif (Test-Path $flag) { Remove-Item $flag -Force }
}

# --------------------------------------------------------------------------
# Подмена журнала событий
# --------------------------------------------------------------------------

function New-TestEvent {
    param(
        [Parameter(Mandatory)][int] $Id,
        [string] $Provider = 'Microsoft-Windows-Kernel-Power',
        [datetime] $Time = (Get-Date),
        [string] $Message = 'test event',
        [string] $PhysicalAddress = ''
    )
    $e = [pscustomobject]@{
        Id              = $Id
        ProviderName    = $Provider
        TimeCreated     = $Time
        Message         = $Message
        PhysicalAddress = $PhysicalAddress
    }
    Add-Member -InputObject $e -MemberType ScriptMethod -Name ToXml -Value {
        $addr = $this.PhysicalAddress
        $data = if ($addr) { "<Data Name='PhysicalAddress'>$addr</Data>" } else { "<Data Name='Other'>0</Data>" }
        "<Event><System><EventID>$($this.Id)</EventID></System><EventData>$data</EventData></Event>"
    }
    $e
}

function Set-WinEventStub {
    <#
        Режимы:
          ok     — журнал читается, события берутся из -Events;
          denied — любой вызов бросает исключение (нет прав администратора).
    #>
    param(
        [ValidateSet('ok', 'denied')][string] $Mode = 'ok',
        [object[]] $Events = @()
    )
    $global:SofiaTest_WinEventMode = $Mode
    $global:SofiaTest_WinEvents = @($Events)
}

function Set-GpuCounterStub {
    <#
        Задаёт, что вернут счётчики производительности Windows по VRAM.
        @{ pid = MiB }. $null означает «счётчиков нет вовсе».
    #>
    param([hashtable] $PerPid)
    $global:SofiaTest_GpuCounters = $PerPid
}

function Get-Counter {
    <#
        Заглушка cmdlet Get-Counter: отдаёт набор с именами экземпляров того
        же вида, что настоящий (pid_<N>_luid_..._phys_<N>).
    #>
    [CmdletBinding()]
    param(
        [switch] $ListSet,
        [string[]] $Counter
    )
    $per = $global:SofiaTest_GpuCounters
    if ($null -eq $per) { throw [System.Exception]::new('No counter sets') }

    $paths = @($per.Keys | ForEach-Object {
        '\GPU Process Memory(pid_{0}_luid_0x00000000_0x0000D5F2_phys_0)\Local Usage' -f $_
    })

    if ($ListSet) {
        return @([pscustomobject]@{ CounterSetName = 'GPU Process Memory'; PathsWithInstances = $paths })
    }

    $samples = @()
    foreach ($p in @($Counter)) {
        $m = [regex]::Match($p, 'pid_(\d+)')
        if (-not $m.Success) { continue }
        $procId = [int]$m.Groups[1].Value
        if (-not $per.ContainsKey($procId)) { continue }
        $samples += [pscustomobject]@{ Path = $p; CookedValue = ([double]$per[$procId] * 1MB) }
    }
    [pscustomobject]@{ CounterSamples = $samples }
}

function Get-WinEvent {
    <#
        Заглушка cmdlet Get-WinEvent. Определена глобально, поэтому её видит
        дочерняя область тестируемого скрипта.
    #>
    [CmdletBinding()]
    param(
        [hashtable] $FilterHashtable,
        [string] $LogName,
        [int] $MaxEvents
    )

    if ($global:SofiaTest_WinEventMode -eq 'denied') {
        throw [System.Exception]::new('Attempted to perform an unauthorized operation.')
    }

    # Проба доступности журнала: реальный System никогда не пуст.
    if (-not $FilterHashtable) {
        return @(New-TestEvent -Id 1 -Provider 'Microsoft-Windows-Kernel-General' -Time (Get-Date).AddMinutes(-1))
    }

    $res = @($global:SofiaTest_WinEvents)
    if ($FilterHashtable.ContainsKey('Id')) {
        $ids = @($FilterHashtable['Id'])
        $res = @($res | Where-Object { $ids -contains $_.Id })
    }
    if ($FilterHashtable.ContainsKey('ProviderName')) {
        $pn = @($FilterHashtable['ProviderName'])
        $res = @($res | Where-Object { $pn -contains $_.ProviderName })
    }
    if ($FilterHashtable.ContainsKey('StartTime')) {
        $st = [datetime]$FilterHashtable['StartTime']
        $res = @($res | Where-Object { $_.TimeCreated -ge $st })
    }
    if ($MaxEvents -gt 0) { $res = @($res | Select-Object -First $MaxEvents) }

    if ($res.Count -eq 0) {
        # Настоящий cmdlet в этом случае бросает исключение, а не возвращает пусто.
        throw [System.Exception]::new('No events were found that match the specified selection criteria.')
    }
    @($res)
}
