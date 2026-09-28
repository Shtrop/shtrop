<#
.SYNOPSIS
    Sofia AI Studio - read-only сборщик доказательств по инцидентам HOST_REBOOTED и JOB_STUCK.

.DESCRIPTION
    Скрипт НИЧЕГО не изменяет на хосте: не перезапускает сервисы, не снимает флаги,
    не удаляет файлы и локи, не трогает Task Scheduler и не инициирует reboot.
    Он только читает состояние и складывает артефакты в отдельную папку отчёта.

    Собирает:
      1. Снимок хоста и аптайм (был ли ребут и когда).
      2. Kernel-Power 41, BugCheck 1001, 6008, WHEA-Logger, ошибки диска - root cause падений.
      3. Список минидампов (без удаления и без перемещения).
      4. Живой стек зависшего процесса через py-spy (главное доказательство JOB_STUCK).
      5. Состояние процесса dashboard, его потоки, сокеты и ответ API.
      6. Канонические state-файлы студии, флаги и ПРОВЕРКУ STALE-ЛОКОВ после жёсткого ребута.
      7. Свежесть heartbeat/liveness файлов, на которые смотрит supervisor.
      8. Хвосты свежих логов и корреляцию времени падений с GPU-рендером.
      9. SUMMARY.md с вердиктами PASS/WARN/FAIL/BLOCKED/NOT_MEASURED.

.PARAMETER StuckPid
    PID зависшего процесса из алерта JOB_STUCK. Если не задан - определяется автоматически
    по командной строке (dashboard) и по владельцу слушающего порта.

.PARAMETER SofiaRoot
    Корень студии. По умолчанию D:\AI_CONTENT\Sofia.

.PARAMETER OutDir
    Куда писать отчёт. По умолчанию <SofiaRoot>\reports\incident_<timestamp>.

.PARAMETER CrashDays
    Глубина разбора журнала событий в днях. По умолчанию 7 (как crashes_7d в алерте).

.PARAMETER DashboardPort
    Порт dashboard для проверки API. По умолчанию 5681.

.PARAMETER AllowPySpyInstall
    Разрешить `pip install py-spy`, если py-spy не найден. По умолчанию выключено:
    без этого ключа скрипт остаётся строго read-only и просто сообщит, что py-spy нет.

.EXAMPLE
    # Запускать в PowerShell ОТ АДМИНИСТРАТОРА, пока зависший процесс ещё жив:
    powershell -ExecutionPolicy Bypass -File .\Collect-SofiaIncident.ps1 -StuckPid 26520

.NOTES
    Запускать ДО перезапуска dashboard: рестарт уничтожает стек и делает root cause недоказуемым.
#>
[CmdletBinding()]
param(
    [int]$StuckPid = 0,
    [string]$SofiaRoot = 'D:\AI_CONTENT\Sofia',
    [string]$OutDir = '',
    [int]$CrashDays = 7,
    [int]$DashboardPort = 5681,
    [switch]$AllowPySpyInstall
)

$ErrorActionPreference = 'Continue'
$ProgressPreference = 'SilentlyContinue'

# ---------------------------------------------------------------- инфраструктура отчёта

$script:Findings = New-Object System.Collections.ArrayList
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'

if (-not $OutDir -or $OutDir.Trim() -eq '') {
    if (Test-Path -LiteralPath $SofiaRoot) {
        $OutDir = Join-Path $SofiaRoot ("reports\incident_" + $stamp)
    } else {
        $OutDir = Join-Path $env:USERPROFILE ("sofia_incident_" + $stamp)
    }
}
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

function Write-Step {
    param([string]$Text)
    Write-Host ("[*] " + $Text) -ForegroundColor Cyan
}

function Add-Finding {
    param(
        [Parameter(Mandatory = $true)][string]$Check,
        [Parameter(Mandatory = $true)]
        [ValidateSet('PASS', 'WARN', 'FAIL', 'BLOCKED', 'NOT_MEASURED')]
        [string]$Status,
        [string]$Detail = '',
        [string]$Evidence = ''
    )
    $null = $script:Findings.Add([pscustomobject]@{
        Check    = $Check
        Status   = $Status
        Detail   = $Detail
        Evidence = $Evidence
    })
    $color = switch ($Status) {
        'PASS'    { 'Green' }
        'WARN'    { 'Yellow' }
        'FAIL'    { 'Red' }
        'BLOCKED' { 'Magenta' }
        default   { 'DarkGray' }
    }
    Write-Host ("    " + $Status.PadRight(14) + $Check + " - " + $Detail) -ForegroundColor $color
}

function Save-Artifact {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)]$Content
    )
    $path = Join-Path $OutDir $Name
    $dir = Split-Path -Parent $path
    if (-not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    if ($null -eq $Content) { $Content = '(нет данных)' }
    $text = ($Content | Out-String)
    Set-Content -LiteralPath $path -Value $text -Encoding UTF8
    return $Name
}

function Get-EventsSafe {
    param([hashtable]$Filter, [int]$Max = 50)
    try {
        $ev = Get-WinEvent -FilterHashtable $Filter -MaxEvents $Max -ErrorAction Stop
        return @{ Ok = $true; Events = @($ev); Error = $null }
    } catch {
        $msg = $_.Exception.Message
        if ($msg -match 'No events were found') {
            return @{ Ok = $true; Events = @(); Error = $null }
        }
        return @{ Ok = $false; Events = @(); Error = $msg }
    }
}

$isAdmin = $false
try {
    $id = [Security.Principal.WindowsIdentity]::GetCurrent()
    $isAdmin = (New-Object Security.Principal.WindowsPrincipal($id)).IsInRole(
        [Security.Principal.WindowsBuiltInRole]::Administrator)
} catch { }

Write-Host ""
Write-Host "Sofia AI Studio - read-only incident collector" -ForegroundColor White
Write-Host ("Отчёт: " + $OutDir) -ForegroundColor White
Write-Host ("Режим: READ-ONLY (ничего не перезапускается, не удаляется, не публикуется)") -ForegroundColor White
Write-Host ""

if (-not $isAdmin) {
    Add-Finding -Check 'Права запуска' -Status 'WARN' `
        -Detail 'Скрипт запущен БЕЗ прав администратора: часть журналов и стеков может быть недоступна. Перезапустите PowerShell от админа.'
} else {
    Add-Finding -Check 'Права запуска' -Status 'PASS' -Detail 'Администратор'
}

# ---------------------------------------------------------------- 1. хост и аптайм

Write-Step '1/9 Снимок хоста и аптайм'
$bootTime = $null
try {
    $os = Get-CimInstance Win32_OperatingSystem -ErrorAction Stop
    $cs = Get-CimInstance Win32_ComputerSystem -ErrorAction Stop
    $bootTime = $os.LastBootUpTime
    $uptime = (Get-Date) - $bootTime
    $hostInfo = [pscustomobject]@{
        ComputerName   = $env:COMPUTERNAME
        OS             = $os.Caption
        Version        = $os.Version
        LastBootUpTime = $bootTime
        UptimeHours    = [math]::Round($uptime.TotalHours, 2)
        Manufacturer   = $cs.Manufacturer
        Model          = $cs.Model
        TotalRAM_GB    = [math]::Round($cs.TotalPhysicalMemory / 1GB, 2)
        CollectedAtUtc = (Get-Date).ToUniversalTime().ToString('s') + 'Z'
    }
    $ev = Save-Artifact -Name '01_host.txt' -Content ($hostInfo | Format-List | Out-String)
    if ($uptime.TotalHours -lt 24) {
        Add-Finding -Check 'Аптайм хоста' -Status 'WARN' `
            -Detail ("Хост поднят " + [math]::Round($uptime.TotalHours, 1) + " ч назад (" + $bootTime + ") - недавний ребут подтверждён") -Evidence $ev
    } else {
        Add-Finding -Check 'Аптайм хоста' -Status 'PASS' `
            -Detail ("Аптайм " + [math]::Round($uptime.TotalHours, 1) + " ч, последняя загрузка " + $bootTime) -Evidence $ev
    }
} catch {
    Add-Finding -Check 'Аптайм хоста' -Status 'NOT_MEASURED' -Detail $_.Exception.Message
}

# Fast Startup: при включённом hybrid boot ребуты маскируются и диагностика врёт
try {
    $hiberKey = 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Power'
    $fastStartup = (Get-ItemProperty -LiteralPath $hiberKey -Name HiberbootEnabled -ErrorAction Stop).HiberbootEnabled
    if ($fastStartup -eq 1) {
        Add-Finding -Check 'Fast Startup' -Status 'WARN' `
            -Detail 'HiberbootEnabled=1. Быстрый запуск маскирует часть аварийных перезагрузок и мешает чистой диагностике железа.'
    } else {
        Add-Finding -Check 'Fast Startup' -Status 'PASS' -Detail 'HiberbootEnabled=0'
    }
} catch {
    Add-Finding -Check 'Fast Startup' -Status 'NOT_MEASURED' -Detail 'Ключ не прочитан'
}

# ---------------------------------------------------------------- 2. root cause падений

Write-Step '2/9 Журнал событий: Kernel-Power 41 / BugCheck / WHEA'
$since = (Get-Date).AddDays(-1 * $CrashDays)
$crashTimes = @()

$r41 = Get-EventsSafe -Filter @{ LogName = 'System'; Id = 41; StartTime = $since } -Max 50
if ($r41.Ok) {
    $crashTimes += @($r41.Events | ForEach-Object { $_.TimeCreated })
    $ev = Save-Artifact -Name '02_kernel_power_41.txt' -Content ($r41.Events | Select-Object TimeCreated, Id, ProviderName, Message | Format-List | Out-String)
    if ($r41.Events.Count -gt 0) {
        Add-Finding -Check 'Kernel-Power 41' -Status 'FAIL' `
            -Detail ("Найдено " + $r41.Events.Count + " аварийных завершений за " + $CrashDays + " дн. Последнее: " + $r41.Events[0].TimeCreated) -Evidence $ev
    } else {
        Add-Finding -Check 'Kernel-Power 41' -Status 'PASS' -Detail 'За окно событий не найдено' -Evidence $ev
    }
} else {
    Add-Finding -Check 'Kernel-Power 41' -Status 'BLOCKED' -Detail ('Журнал System недоступен: ' + $r41.Error)
}

$r1001 = Get-EventsSafe -Filter @{ LogName = 'System'; Id = 1001; StartTime = $since } -Max 50
if ($r1001.Ok) {
    $bugchecks = @($r1001.Events | Where-Object { $_.ProviderName -match 'Bugcheck' -or $_.Message -match 'bugcheck' })
    $ev = Save-Artifact -Name '03_bugcheck_1001.txt' -Content ($bugchecks | Select-Object TimeCreated, ProviderName, Message | Format-List | Out-String)
    if ($bugchecks.Count -gt 0) {
        Add-Finding -Check 'BugCheck 1001 (BSOD)' -Status 'FAIL' `
            -Detail ("Найдено " + $bugchecks.Count + " BSOD. Есть код останова и минидамп - причина, скорее всего, ДРАЙВЕР (часто GPU), а не питание.") -Evidence $ev
    } else {
        Add-Finding -Check 'BugCheck 1001 (BSOD)' -Status 'PASS' `
            -Detail 'BSOD не зафиксирован. В связке с Kernel-Power 41 это указывает на обрыв питания / PSU / зависание, а не на драйвер.' -Evidence $ev
    }
} else {
    Add-Finding -Check 'BugCheck 1001 (BSOD)' -Status 'BLOCKED' -Detail $r1001.Error
}

$rWhea = Get-EventsSafe -Filter @{ LogName = 'System'; ProviderName = 'Microsoft-Windows-WHEA-Logger'; StartTime = $since } -Max 50
if ($rWhea.Ok) {
    $ev = Save-Artifact -Name '04_whea.txt' -Content ($rWhea.Events | Select-Object TimeCreated, Id, LevelDisplayName, Message | Format-List | Out-String)
    if ($rWhea.Events.Count -gt 0) {
        Add-Finding -Check 'WHEA (аппаратные ошибки)' -Status 'FAIL' `
            -Detail ("Найдено " + $rWhea.Events.Count + " событий WHEA - ПРЯМОЕ доказательство отказа железа (RAM/CPU/PCIe/питание). Это root cause, а не следствие.") -Evidence $ev
    } else {
        Add-Finding -Check 'WHEA (аппаратные ошибки)' -Status 'PASS' -Detail 'Аппаратных ошибок в журнале нет' -Evidence $ev
    }
} else {
    Add-Finding -Check 'WHEA (аппаратные ошибки)' -Status 'BLOCKED' -Detail $rWhea.Error
}

$r6008 = Get-EventsSafe -Filter @{ LogName = 'System'; Id = 6008; StartTime = $since } -Max 50
if ($r6008.Ok) {
    $ev = Save-Artifact -Name '05_unexpected_shutdown_6008.txt' -Content ($r6008.Events | Select-Object TimeCreated, Message | Format-List | Out-String)
    Add-Finding -Check 'Неожиданные выключения (6008)' `
        -Status $(if ($r6008.Events.Count -gt 0) { 'WARN' } else { 'PASS' }) `
        -Detail ("Событий: " + $r6008.Events.Count) -Evidence $ev
}

# Ошибки диска и контроллера - частая причина и падений, и подвисшего I/O в dashboard
$rDisk = Get-EventsSafe -Filter @{ LogName = 'System'; ProviderName = 'disk'; Level = 1, 2, 3; StartTime = $since } -Max 50
if ($rDisk.Ok) {
    $ev = Save-Artifact -Name '06_disk_errors.txt' -Content ($rDisk.Events | Select-Object TimeCreated, Id, LevelDisplayName, Message | Format-List | Out-String)
    if ($rDisk.Events.Count -gt 0) {
        Add-Finding -Check 'Ошибки диска' -Status 'WARN' `
            -Detail ("Событий disk: " + $rDisk.Events.Count + ". Подвисший I/O объясняет и JOB_STUCK, и часть зависаний хоста.") -Evidence $ev
    } else {
        Add-Finding -Check 'Ошибки диска' -Status 'PASS' -Detail 'Ошибок дисковой подсистемы нет' -Evidence $ev
    }
}

# S.M.A.R.T. предиктив
try {
    $smart = Get-CimInstance -Namespace root\wmi -ClassName MSStorageDriver_FailurePredictStatus -ErrorAction Stop
    $bad = @($smart | Where-Object { $_.PredictFailure })
    $ev = Save-Artifact -Name '07_smart.txt' -Content ($smart | Select-Object InstanceName, PredictFailure, Reason | Format-List | Out-String)
    if ($bad.Count -gt 0) {
        Add-Finding -Check 'S.M.A.R.T.' -Status 'FAIL' -Detail 'Диск предсказывает отказ' -Evidence $ev
    } else {
        Add-Finding -Check 'S.M.A.R.T.' -Status 'PASS' -Detail 'PredictFailure=False по всем дискам' -Evidence $ev
    }
} catch {
    Add-Finding -Check 'S.M.A.R.T.' -Status 'NOT_MEASURED' -Detail 'WMI-класс недоступен'
}

# ---------------------------------------------------------------- 3. минидампы (только чтение)

Write-Step '3/9 Минидампы'
$dumpPaths = @("$env:SystemRoot\Minidump", "$env:SystemRoot\MEMORY.DMP")
$dumps = @()
foreach ($p in $dumpPaths) {
    if (Test-Path -LiteralPath $p) {
        $dumps += Get-ChildItem -LiteralPath $p -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Descending | Select-Object -First 15
    }
}
$ev = Save-Artifact -Name '08_minidumps.txt' -Content ($dumps | Select-Object FullName, Length, LastWriteTime | Format-Table -AutoSize | Out-String)
if ($dumps.Count -gt 0) {
    Add-Finding -Check 'Минидампы' -Status 'WARN' `
        -Detail ("Найдено " + $dumps.Count + " дампов. Разобрать: WinDbg -> !analyze -v (файлы НЕ удалены и не перемещены).") -Evidence $ev
} else {
    Add-Finding -Check 'Минидампы' -Status 'PASS' `
        -Detail 'Дампов нет. При Kernel-Power 41 это типично для обрыва питания / зависания без BSOD.' -Evidence $ev
}

# ---------------------------------------------------------------- 4. зависший процесс: поиск

Write-Step '4/9 Поиск процесса dashboard'
$targetPid = 0
$procInfo = $null

if ($StuckPid -gt 0) {
    try { $procInfo = Get-CimInstance Win32_Process -Filter ("ProcessId = " + $StuckPid) -ErrorAction Stop } catch { $procInfo = $null }
    if (-not $procInfo) { $procInfo = Get-Process -Id $StuckPid -ErrorAction SilentlyContinue }
    if ($procInfo) {
        $targetPid = $StuckPid
        Add-Finding -Check 'Процесс из алерта' -Status 'WARN' `
            -Detail ("PID " + $StuckPid + " ЖИВ (" + $procInfo.Name + ") - стек снимаем, доказательство доступно")
    } else {
        Add-Finding -Check 'Процесс из алерта' -Status 'NOT_MEASURED' `
            -Detail ("PID " + $StuckPid + " уже не существует: процесс перезапущен или убит. Стек зависания потерян, ждём следующего JOB_STUCK.")
    }
}

if ($targetPid -eq 0) {
    $candidates = @()
    try {
        $candidates = @(Get-CimInstance Win32_Process -ErrorAction Stop | Where-Object {
            $_.CommandLine -and $_.CommandLine -match 'dashboard' -and $_.Name -match 'python|pythonw|py'
        })
    } catch {
        Add-Finding -Check 'WMI/CIM' -Status 'WARN' `
            -Detail ('Win32_Process недоступен (' + $_.Exception.Message + '). На деградировавшем хосте это само по себе симптом.')
    }
    if ($candidates.Count -gt 0) {
        $targetPid = [int]$candidates[0].ProcessId
        $procInfo = $candidates[0]
        Add-Finding -Check 'Автопоиск dashboard' -Status 'WARN' `
            -Detail ("Найден живой процесс dashboard PID " + $targetPid + " - работаем по нему")
    }
}

if ($targetPid -eq 0) {
    try {
        $conn = Get-NetTCPConnection -LocalPort $DashboardPort -State Listen -ErrorAction Stop | Select-Object -First 1
        if ($conn) {
            $targetPid = [int]$conn.OwningProcess
            try { $procInfo = Get-CimInstance Win32_Process -Filter ("ProcessId = " + $targetPid) -ErrorAction Stop } catch { $procInfo = $null }
            Add-Finding -Check 'Автопоиск по порту' -Status 'WARN' `
                -Detail ("Порт " + $DashboardPort + " слушает PID " + $targetPid)
        }
    } catch { }
}

if ($targetPid -eq 0) {
    Add-Finding -Check 'Процесс dashboard' -Status 'FAIL' `
        -Detail 'Живой процесс dashboard не найден ни по PID, ни по командной строке, ни по слушающему порту. Сервис лежит.'
}

# ---------------------------------------------------------------- 5. стек и состояние процесса

Write-Step '5/9 Стек зависшего процесса (py-spy) и состояние процесса'
if ($targetPid -gt 0) {
    $ev = Save-Artifact -Name '09_process_info.txt' -Content (
        ($procInfo | Select-Object ProcessId, Name, CreationDate, CommandLine, WorkingSetSize, HandleCount | Format-List | Out-String) +
        "`n--- Get-Process ---`n" +
        (Get-Process -Id $targetPid -ErrorAction SilentlyContinue |
            Select-Object Id, ProcessName, CPU, Handles, Threads, WS, StartTime, Responding | Format-List | Out-String)
    )
    Add-Finding -Check 'Состояние процесса' -Status 'WARN' -Detail ("Снимок PID " + $targetPid + " сохранён") -Evidence $ev

    try {
        $threads = (Get-Process -Id $targetPid -ErrorAction Stop).Threads |
            Select-Object Id, ThreadState, WaitReason, TotalProcessorTime, StartTime
        $ev = Save-Artifact -Name '10_threads.txt' -Content ($threads | Format-Table -AutoSize | Out-String)
        $waiting = @($threads | Where-Object { $_.ThreadState -eq 'Wait' })
        Add-Finding -Check 'Потоки процесса' -Status 'WARN' `
            -Detail ("Всего " + @($threads).Count + ", в состоянии Wait: " + $waiting.Count + ". WaitReason покажет, ждёт ли процесс I/O, лок или сеть.") -Evidence $ev
    } catch {
        Add-Finding -Check 'Потоки процесса' -Status 'NOT_MEASURED' -Detail $_.Exception.Message
    }

    # py-spy: главный артефакт для JOB_STUCK
    $pyspy = (Get-Command py-spy -ErrorAction SilentlyContinue)
    if (-not $pyspy -and $AllowPySpyInstall) {
        Write-Host "    Устанавливаю py-spy (разрешено ключом -AllowPySpyInstall)..." -ForegroundColor Yellow
        & pip install py-spy 2>&1 | Out-Null
        $pyspy = (Get-Command py-spy -ErrorAction SilentlyContinue)
    }
    if ($pyspy) {
        $dump = & py-spy dump --pid $targetPid 2>&1
        $ev = Save-Artifact -Name '11_pyspy_dump.txt' -Content $dump
        $dumpText = ($dump | Out-String)
        $verdict = 'Стек снят. Ищите нижний фрейм: sleep/recv/read = блокирующий вызов без timeout; acquire/wait = deadlock или лок; поток heartbeat отсутствует = watchdog-поток умер.'
        if ($dumpText -match 'Permission denied|Access is denied|Failed to') {
            Add-Finding -Check 'py-spy dump' -Status 'BLOCKED' `
                -Detail 'py-spy не смог прочитать процесс - нужен запуск от администратора.' -Evidence $ev
        } else {
            Add-Finding -Check 'py-spy dump' -Status 'PASS' -Detail $verdict -Evidence $ev
        }
        # Второй снимок через паузу: одинаковый стек = процесс реально стоит,
        # изменившийся = процесс работает, но не обновляет heartbeat.
        Start-Sleep -Seconds 5
        $dump2 = & py-spy dump --pid $targetPid 2>&1
        $ev2 = Save-Artifact -Name '12_pyspy_dump_plus5s.txt' -Content $dump2
        $frozen = (($dump2 | Out-String).Trim() -eq $dumpText.Trim())
        if ($frozen) {
            Add-Finding -Check 'Стек за 5 секунд' -Status 'FAIL' `
                -Detail 'Стек НЕ изменился за 5 с - процесс действительно заблокирован (deadlock/блокирующий вызов), а не просто молчит.' -Evidence $ev2
        } else {
            Add-Finding -Check 'Стек за 5 секунд' -Status 'WARN' `
                -Detail 'Стек меняется - процесс жив и что-то выполняет. Значит сломан heartbeat/liveness, а не сам воркер: искать причину в watchdog-потоке.' -Evidence $ev2
        }
    } else {
        Add-Finding -Check 'py-spy dump' -Status 'BLOCKED' `
            -Detail 'py-spy не установлен - стек зависания НЕ снят. Выполните `pip install py-spy` и перезапустите скрипт (или ключ -AllowPySpyInstall). Без этого причина JOB_STUCK останется недоказанной.'
    }

    try {
        $conns = Get-NetTCPConnection -OwningProcess $targetPid -ErrorAction Stop |
            Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort, State
        $ev = Save-Artifact -Name '13_process_sockets.txt' -Content ($conns | Format-Table -AutoSize | Out-String)
        Add-Finding -Check 'Сокеты процесса' -Status 'PASS' -Detail ("Соединений: " + @($conns).Count) -Evidence $ev
    } catch {
        Add-Finding -Check 'Сокеты процесса' -Status 'NOT_MEASURED' -Detail $_.Exception.Message
    }
}

# API dashboard
try {
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $resp = Invoke-WebRequest -Uri ("http://127.0.0.1:" + $DashboardPort + "/api/production-state") -UseBasicParsing -TimeoutSec 10 -ErrorAction Stop
    $sw.Stop()
    $ev = Save-Artifact -Name '14_api_production_state.json' -Content $resp.Content
    Add-Finding -Check 'API /api/production-state' -Status 'PASS' `
        -Detail ("HTTP " + $resp.StatusCode + " за " + $sw.ElapsedMilliseconds + " мс - HTTP-поток жив, значит завис отдельный воркер, а не весь сервис") -Evidence $ev
} catch {
    $m = $_.Exception.Message
    if ($m -match '404') {
        Add-Finding -Check 'API /api/production-state' -Status 'WARN' `
            -Detail '404: контракт endpoint устарел. По политике студии НЕ перезапускать сервис из-за 404 - найти актуальный route в коде dashboard.'
    } else {
        Add-Finding -Check 'API /api/production-state' -Status 'FAIL' `
            -Detail ('Нет ответа: ' + $m + '. Сервис не отвечает на HTTP - зависание затронуло основной цикл.')
    }
}

# ---------------------------------------------------------------- 6. состояние студии и STALE-ЛОКИ

Write-Step '6/9 State-файлы, флаги и stale-локи'
if (Test-Path -LiteralPath $SofiaRoot) {
    $stateFiles = @(
        'control_flags\PUBLISHING_STATE.json',
        'CODEX_FINAL_KNOWN_GOOD_STATE.json',
        'CODEX_PRODUCTION_RELEASE_GATE.md',
        'agent_team_v2\state\SOFIA_AGENT_TEAM_RUNTIME_STATUS.json',
        'agent_team_v2\state\company_state.json'
    )
    $stateReport = New-Object System.Collections.ArrayList
    foreach ($rel in $stateFiles) {
        $full = Join-Path $SofiaRoot $rel
        if (Test-Path -LiteralPath $full) {
            $fi = Get-Item -LiteralPath $full
            $ageH = [math]::Round(((Get-Date) - $fi.LastWriteTime).TotalHours, 2)
            $null = $stateReport.Add([pscustomobject]@{ File = $rel; LastWrite = $fi.LastWriteTime; AgeHours = $ageH; Size = $fi.Length })
            $safeName = '15_state_' + ($rel -replace '[\\/:]', '_')
            Save-Artifact -Name $safeName -Content (Get-Content -LiteralPath $full -Raw -ErrorAction SilentlyContinue) | Out-Null
        } else {
            $null = $stateReport.Add([pscustomobject]@{ File = $rel; LastWrite = 'MISSING'; AgeHours = $null; Size = 0 })
        }
    }
    $ev = Save-Artifact -Name '15_state_index.txt' -Content ($stateReport | Format-Table -AutoSize | Out-String)
    $missing = @($stateReport | Where-Object { $_.LastWrite -eq 'MISSING' })
    if ($missing.Count -gt 0) {
        Add-Finding -Check 'Канонические state-файлы' -Status 'WARN' `
            -Detail ("Отсутствуют: " + (($missing | ForEach-Object { $_.File }) -join ', ')) -Evidence $ev
    } else {
        Add-Finding -Check 'Канонические state-файлы' -Status 'PASS' -Detail 'Все на месте, содержимое и timestamps сохранены' -Evidence $ev
    }

    # stale-локи: после жёсткого ребута лок от мёртвого PID вешает pipeline навсегда
    $lockDirs = @(
        (Join-Path $SofiaRoot 'control_flags'),
        (Join-Path $SofiaRoot 'locks'),
        (Join-Path $SofiaRoot 'runtime')
    )
    $lockReport = New-Object System.Collections.ArrayList
    $staleCount = 0
    foreach ($ld in $lockDirs) {
        if (-not (Test-Path -LiteralPath $ld)) { continue }
        $lockFiles = Get-ChildItem -LiteralPath $ld -Recurse -File -ErrorAction SilentlyContinue |
            Where-Object { $_.Extension -in @('.lock', '.flag', '.pid') -or $_.Name -match 'lock|LOCK' }
        foreach ($lf in $lockFiles) {
            $raw = ''
            try { $raw = (Get-Content -LiteralPath $lf.FullName -Raw -ErrorAction Stop) } catch { }
            if ($null -eq $raw) { $raw = '' }
            $pidMatch = [regex]::Match($raw, '(?<![\d.])(\d{2,7})(?![\d.])')
            $lockPid = $null
            $alive = $null
            $stale = $false
            if ($pidMatch.Success) {
                $lockPid = [int]$pidMatch.Groups[1].Value
                $alive = [bool](Get-Process -Id $lockPid -ErrorAction SilentlyContinue)
                if (-not $alive) { $stale = $true; $staleCount++ }
            }
            $beforeBoot = $false
            if ($bootTime -and $lf.LastWriteTime -lt $bootTime) { $beforeBoot = $true }
            $null = $lockReport.Add([pscustomobject]@{
                File          = $lf.FullName.Replace($SofiaRoot, '')
                LastWrite     = $lf.LastWriteTime
                WrittenBefore = $beforeBoot
                PidInFile     = $lockPid
                PidAlive      = $alive
                LikelyStale   = ($stale -or ($beforeBoot -and $lf.Extension -eq '.lock'))
                Preview       = ($raw -replace '\s+', ' ').Trim()
            })
        }
    }
    $ev = Save-Artifact -Name '16_locks_and_flags.txt' -Content ($lockReport | Format-List | Out-String)
    $likelyStale = @($lockReport | Where-Object { $_.LikelyStale })
    if ($likelyStale.Count -gt 0) {
        Add-Finding -Check 'Stale-локи после ребута' -Status 'FAIL' `
            -Detail ("Подозрительных локов: " + $likelyStale.Count + " (лок от мёртвого PID или созданный ДО текущей загрузки). Это правдоподобная ОБЩАЯ причина JOB_STUCK. Файлы НЕ удалены - решение за владельцем.") -Evidence $ev
    } else {
        Add-Finding -Check 'Stale-локи после ребута' -Status 'PASS' -Detail 'Зависших локов не обнаружено' -Evidence $ev
    }

    # git status - сохранить пользовательские изменения
    try {
        Push-Location -LiteralPath $SofiaRoot
        try { $git = & git status --short --branch 2>&1 } finally { Pop-Location }
        $ev = Save-Artifact -Name '17_git_status.txt' -Content $git
        Add-Finding -Check 'git status студии' -Status 'PASS' -Detail 'Сохранён (несохранённые изменения владельца не трогаем)' -Evidence $ev
    } catch {
        Add-Finding -Check 'git status студии' -Status 'NOT_MEASURED' -Detail $_.Exception.Message
    }
} else {
    Add-Finding -Check 'Корень студии' -Status 'BLOCKED' `
        -Detail ($SofiaRoot + ' не найден. Укажите верный путь параметром -SofiaRoot.')
}

# ---------------------------------------------------------------- 7. heartbeat / liveness

Write-Step '7/9 Свежесть heartbeat/liveness файлов'
if (Test-Path -LiteralPath $SofiaRoot) {
    $hb = Get-ChildItem -LiteralPath $SofiaRoot -Recurse -File -Depth 4 -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match 'heartbeat|liveness|watchdog|supervisor' } |
        Sort-Object LastWriteTime -Descending | Select-Object -First 30
    $hbReport = $hb | Select-Object @{N = 'File'; E = { $_.FullName.Replace($SofiaRoot, '') } },
        LastWriteTime,
        @{N = 'AgeMinutes'; E = { [math]::Round(((Get-Date) - $_.LastWriteTime).TotalMinutes, 1) } }
    $ev = Save-Artifact -Name '18_heartbeat_files.txt' -Content ($hbReport | Format-Table -AutoSize | Out-String)
    $stale = @($hbReport | Where-Object { $_.AgeMinutes -gt 15 -and $_.File -match 'heartbeat|liveness' })
    if ($stale.Count -gt 0) {
        Add-Finding -Check 'Heartbeat/liveness' -Status 'FAIL' `
            -Detail ("Протухших heartbeat-файлов: " + $stale.Count + " (>15 мин без обновления) - это ровно то, на что сработал liveness contract") -Evidence $ev
    } elseif (@($hbReport).Count -eq 0) {
        Add-Finding -Check 'Heartbeat/liveness' -Status 'NOT_MEASURED' -Detail 'Файлы heartbeat не найдены - контракт живости, вероятно, в БД или в памяти supervisor' -Evidence $ev
    } else {
        Add-Finding -Check 'Heartbeat/liveness' -Status 'PASS' -Detail 'Все heartbeat свежие' -Evidence $ev
    }
}

# ---------------------------------------------------------------- 8. логи и корреляция с GPU

Write-Step '8/9 Логи, GPU и корреляция падений с рендером'
try {
    $nv = & nvidia-smi -q -d TEMPERATURE,POWER,CLOCK,PERFORMANCE 2>&1
    $ev = Save-Artifact -Name '19_nvidia_smi.txt' -Content $nv
    $nvProc = & nvidia-smi 2>&1
    Save-Artifact -Name '20_nvidia_smi_overview.txt' -Content $nvProc | Out-Null
    Add-Finding -Check 'GPU (nvidia-smi)' -Status 'PASS' -Detail 'Температуры, лимиты питания и активные процессы сохранены' -Evidence $ev
} catch {
    Add-Finding -Check 'GPU (nvidia-smi)' -Status 'NOT_MEASURED' -Detail 'nvidia-smi недоступен'
}

if (Test-Path -LiteralPath $SofiaRoot) {
    $logDirs = Get-ChildItem -LiteralPath $SofiaRoot -Recurse -Directory -Depth 3 -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match '^logs?$' }
    $recentLogs = @()
    foreach ($ld in $logDirs) {
        $recentLogs += Get-ChildItem -LiteralPath $ld.FullName -Recurse -File -ErrorAction SilentlyContinue |
            Where-Object { $_.Extension -in @('.log', '.txt', '.jsonl') -and $_.LastWriteTime -gt $since }
    }
    $recentLogs = $recentLogs | Sort-Object LastWriteTime -Descending | Select-Object -First 12
    $ev = Save-Artifact -Name '21_log_index.txt' -Content (
        $recentLogs | Select-Object @{N = 'File'; E = { $_.FullName.Replace($SofiaRoot, '') } }, LastWriteTime, Length |
        Format-Table -AutoSize | Out-String)
    Add-Finding -Check 'Свежие логи' -Status 'PASS' -Detail ("Собрано хвостов: " + @($recentLogs).Count) -Evidence $ev

    $i = 0
    foreach ($lg in $recentLogs) {
        $i++
        $tail = Get-Content -LiteralPath $lg.FullName -Tail 300 -ErrorAction SilentlyContinue
        $safe = ('22_tail_{0:d2}_{1}' -f $i, ($lg.Name -replace '[\\/:*?"<>|]', '_')) + '.txt'
        Save-Artifact -Name $safe -Content $tail | Out-Null
    }

    # корреляция: что писалось в логи в момент каждого падения хоста
    if ($crashTimes.Count -gt 0) {
        $corr = New-Object System.Collections.ArrayList
        foreach ($ct in $crashTimes) {
            $from = $ct.AddMinutes(-10)
            $to = $ct.AddMinutes(2)
            $touched = @()
            foreach ($ld in $logDirs) {
                $touched += Get-ChildItem -LiteralPath $ld.FullName -Recurse -File -ErrorAction SilentlyContinue |
                    Where-Object { $_.LastWriteTime -ge $from -and $_.LastWriteTime -le $to }
            }
            $gpuHit = @($touched | Where-Object { $_.Name -match 'gpu|render|reel|video' })
            $null = $corr.Add([pscustomobject]@{
                CrashTime       = $ct
                LogsTouched     = @($touched).Count
                GpuRenderActive = ($gpuHit.Count -gt 0)
                Files           = (($touched | Select-Object -First 8 | ForEach-Object { $_.Name }) -join '; ')
            })
        }
        $ev = Save-Artifact -Name '23_crash_gpu_correlation.txt' -Content ($corr | Format-List | Out-String)
        $gpuLinked = @($corr | Where-Object { $_.GpuRenderActive })
        if ($gpuLinked.Count -ge 2) {
            Add-Finding -Check 'Корреляция падений с GPU-рендером' -Status 'FAIL' `
                -Detail ("В " + $gpuLinked.Count + " из " + $corr.Count + " падений в момент сбоя шёл GPU-рендер. Классическая просадка PSU под нагрузкой - проверять питание, а не софт.") -Evidence $ev
        } else {
            Add-Finding -Check 'Корреляция падений с GPU-рендером' -Status 'PASS' `
                -Detail 'Устойчивой связи падений с рендером не видно - версию просадки PSU под GPU-нагрузкой это ослабляет' -Evidence $ev
        }
    }
}

# ---------------------------------------------------------------- 9. SUMMARY

Write-Step '9/9 Формирую SUMMARY.md'
$counts = $script:Findings | Group-Object Status | ForEach-Object { $_.Name + '=' + $_.Count }
$overall = 'PASS'
if ($script:Findings | Where-Object { $_.Status -eq 'FAIL' }) { $overall = 'FAIL' }
elseif ($script:Findings | Where-Object { $_.Status -eq 'BLOCKED' }) { $overall = 'BLOCKED' }
elseif ($script:Findings | Where-Object { $_.Status -eq 'WARN' }) { $overall = 'WARN' }

$sb = New-Object System.Text.StringBuilder
$null = $sb.AppendLine('# Sofia AI Studio - отчёт по инциденту')
$null = $sb.AppendLine('')
$null = $sb.AppendLine('- Собрано (UTC): ' + (Get-Date).ToUniversalTime().ToString('s') + 'Z')
$null = $sb.AppendLine('- Хост: ' + $env:COMPUTERNAME)
$null = $sb.AppendLine('- Корень студии: ' + $SofiaRoot)
$null = $sb.AppendLine('- PID из алерта JOB_STUCK: ' + $(if ($StuckPid -gt 0) { $StuckPid } else { 'не задан' }))
$null = $sb.AppendLine('- Разобранный PID: ' + $(if ($targetPid -gt 0) { $targetPid } else { 'не найден' }))
$null = $sb.AppendLine('- Режим: READ-ONLY, ничего не изменено, ничего не удалено')
$null = $sb.AppendLine('')
$null = $sb.AppendLine('## Итоговый вердикт: `' + $overall + '`')
$null = $sb.AppendLine('')
$null = $sb.AppendLine(($counts -join ', '))
$null = $sb.AppendLine('')
$null = $sb.AppendLine('## Проверки')
$null = $sb.AppendLine('')
$null = $sb.AppendLine('| Проверка | Статус | Детали | Артефакт |')
$null = $sb.AppendLine('|---|---|---|---|')
foreach ($f in $script:Findings) {
    # Многострочный текст ошибки ломает таблицу markdown - схлопываем в одну строку.
    $d = ((($f.Detail -replace '\r?\n', ' ') -replace '\s+', ' ') -replace '\|', '\|').Trim()
    $null = $sb.AppendLine('| ' + $f.Check + ' | `' + $f.Status + '` | ' + $d + ' | ' + $f.Evidence + ' |')
}
$null = $sb.AppendLine('')
$null = $sb.AppendLine('## Как читать результат')
$null = $sb.AppendLine('')
$null = $sb.AppendLine('**HOST_REBOOTED (root cause падений):**')
$null = $sb.AppendLine('- WHEA `FAIL` -> отказ железа (RAM/CPU/PCIe/питание). Дальше: MemTest86, проверка PSU.')
$null = $sb.AppendLine('- BugCheck 1001 `FAIL` + минидампы -> драйвер. Дальше: `!analyze -v` в WinDbg, чаще всего GPU-драйвер.')
$null = $sb.AppendLine('- Только Kernel-Power 41, без WHEA и без дампов -> обрыв питания, PSU или зависание. Дальше: PSU, розетка/UPS, температуры.')
$null = $sb.AppendLine('- Корреляция с GPU-рендером `FAIL` -> просадка PSU под нагрузкой.')
$null = $sb.AppendLine('')
$null = $sb.AppendLine('**JOB_STUCK (почему завис dashboard):**')
$null = $sb.AppendLine('- `11_pyspy_dump.txt` - нижний фрейм стека и есть причина:')
$null = $sb.AppendLine('  - `recv`/`read`/`connect` -> сетевой вызов без timeout;')
$null = $sb.AppendLine('  - `acquire`/`wait`/`join` -> deadlock или ожидание лока;')
$null = $sb.AppendLine('  - нет потока heartbeat -> watchdog-поток умер, сервис жив, но не отчитывается;')
$null = $sb.AppendLine('  - стек в файловых операциях + ошибки диска -> подвисший I/O.')
$null = $sb.AppendLine('- Stale-локи `FAIL` -> лок от мёртвого PID после жёсткого ребута держит pipeline. Это связывает оба алерта в одну причину.')
$null = $sb.AppendLine('')
$null = $sb.AppendLine('## Что требует отдельного решения владельца')
$null = $sb.AppendLine('')
$null = $sb.AppendLine('- Снятие любых локов и флагов (NO-DELETE: скрипт их только показал).')
$null = $sb.AppendLine('- Перезапуск dashboard (делать только ПОСЛЕ снятия стека).')
$null = $sb.AppendLine('- Тест памяти MemTest86 / mdsched, изменения автозапуска и Task Scheduler - влекут reboot.')
$null = $sb.AppendLine('- Публикация остаётся FROZEN, пока host_state = DEGRADED.')

Set-Content -LiteralPath (Join-Path $OutDir 'SUMMARY.md') -Value $sb.ToString() -Encoding UTF8
$script:Findings | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $OutDir 'findings.json') -Encoding UTF8

Write-Host ""
Write-Host ("Готово. Вердикт: " + $overall) -ForegroundColor White
Write-Host ("Отчёт: " + (Join-Path $OutDir 'SUMMARY.md')) -ForegroundColor White
Write-Host "Пришлите SUMMARY.md и 11_pyspy_dump.txt - по ним ставится точный диагноз." -ForegroundColor White
Write-Host ""
