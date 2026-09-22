<#
.SYNOPSIS
    Наблюдает за стабильностью хоста Sofia AI Studio: копит доказательства для
    выхода из HOST_SAFE_HOLD.

.DESCRIPTION
    Периодически снимает телеметрию GPU и проверяет журнал System на новые
    события Kernel-Power 41 / 6008 / BugCheck 1001. Пишет CSV и итоговый JSON.
    Ничего не изменяет: чистое наблюдение.

    Окно наблюдения переживает перезагрузку: события ищутся по времени старта,
    записанному в CSV, поэтому после внезапного ресета достаточно запустить
    скрипт снова — уже случившееся событие 41 попадёт в следующий отчёт.

.PARAMETER Hours
    Длительность наблюдения в часах. По умолчанию 24.

.PARAMETER IntervalSeconds
    Период опроса. По умолчанию 60.

.PARAMETER OutDir
    Каталог вывода. По умолчанию %TEMP%\sofia_stability_<timestamp>.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\watch_host_stability.ps1 -Hours 48

.NOTES
    Критерий выхода из hold по runbook: 48 ч штатной нагрузки без новых
    событий 41, минимум с одним полным production-циклом.
#>

[CmdletBinding()]
param(
    [double] $Hours = 24,
    [int]    $IntervalSeconds = 60,
    [string] $OutDir = (Join-Path ([System.IO.Path]::GetTempPath()) ("sofia_stability_{0}" -f (Get-Date -Format 'yyyyMMdd_HHmmss')))
)

$ErrorActionPreference = 'Continue'
$ProgressPreference    = 'SilentlyContinue'

# Текст ошибки «событий не найдено» локализован, поэтому полагаться на него нельзя:
# пустой результат и реальный отказ в доступе различаются пробой доступа, а не разбором строки.
function Test-SystemLogReadable {
    try { $null = Get-WinEvent -LogName System -MaxEvents 1 -ErrorAction Stop; return $true }
    catch { return $false }
}

function Get-SystemEvents {
    param([hashtable] $Filter, [int] $MaxEvents = 0)
    $p = @{ FilterHashtable = $Filter; ErrorAction = 'SilentlyContinue' }
    if ($MaxEvents -gt 0) { $p['MaxEvents'] = $MaxEvents }
    @(Get-WinEvent @p)
}


New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$csv     = Join-Path $OutDir 'telemetry.csv'
$summary = Join-Path $OutDir 'stability_summary.json'

$start = Get-Date
$end   = $start.AddHours($Hours)

Write-Host ''
Write-Host 'Sofia AI Studio — наблюдение за стабильностью хоста (READ-ONLY)' -ForegroundColor White
Write-Host ("Старт   : {0}" -f $start)
Write-Host ("Финиш   : {0}  ({1} ч, опрос каждые {2} с)" -f $end, $Hours, $IntervalSeconds)
Write-Host ("Вывод   : {0}" -f $OutDir)
Write-Host 'Прервать можно Ctrl+C — собранные данные останутся на месте.' -ForegroundColor DarkGray
Write-Host ''

'timestamp,temp_c,power_w,limit_w,util_pct,mem_used_mib,new_events_41,new_whea' | Out-File -FilePath $csv -Encoding UTF8

$eventLogBlocked = -not (Test-SystemLogReadable)
if ($eventLogBlocked) {
    Write-Host 'Журнал System недоступен — перезапустите PowerShell от имени администратора.' -ForegroundColor Magenta
    Write-Host 'Телеметрия GPU собираться будет, но события и WHEA — нет.' -ForegroundColor Magenta
}

$hasNvidia = [bool](Get-Command nvidia-smi -ErrorAction SilentlyContinue)
if (-not $hasNvidia) {
    Write-Host 'nvidia-smi не найден — телеметрия GPU будет пустой, события всё равно отслеживаются.' -ForegroundColor Yellow
}

$maxTemp = 0.0
$maxDraw = 0.0
$samples = 0
$eventsSeen = @()
$wheaSeen = @()
$eventLogBlocked = $false

while ((Get-Date) -lt $end) {
    $now = Get-Date
    $temp = ''; $draw = ''; $limit = ''; $util = ''; $mem = ''

    if ($hasNvidia) {
        try {
            $q = & nvidia-smi --query-gpu="temperature.gpu,power.draw,power.limit,utilization.gpu,memory.used" --format=csv,noheader 2>&1
            $f = ($q | Out-String).Trim().Split(',') | ForEach-Object { $_.Trim() }
            if ($f.Count -ge 5) {
                $temp  = ($f[0] -replace '[^\d\.]','')
                $draw  = ($f[1] -replace '[^\d\.]','')
                $limit = ($f[2] -replace '[^\d\.]','')
                $util  = ($f[3] -replace '[^\d\.]','')
                $mem   = ($f[4] -replace '[^\d\.]','')
                if ($temp) { $maxTemp = [math]::Max($maxTemp, [double]$temp) }
                if ($draw) { $maxDraw = [math]::Max($maxDraw, [double]$draw) }
            }
        } catch { }
    }

    $newEvents = 0
    $newWhea = 0
    if (-not $eventLogBlocked) {
        $ev = Get-SystemEvents -Filter @{
            LogName   = 'System'
            Id        = 41, 6008, 1001
            StartTime = $start
        }
        foreach ($e in $ev) {
            $key = "{0}|{1}" -f $e.TimeCreated.ToString('o'), $e.Id
            if ($eventsSeen -notcontains $key) {
                $eventsSeen += $key
                $newEvents++
                Write-Host ("  !! {0}  Event {1} ({2})" -f $e.TimeCreated, $e.Id, $e.ProviderName) -ForegroundColor Red
            }
        }

        # Корректируемые аппаратные ошибки появляются раньше крахов, поэтому
        # они здесь не менее важны, чем сами ресеты.
        $wh = Get-SystemEvents -Filter @{
            LogName      = 'System'
            ProviderName = 'Microsoft-Windows-WHEA-Logger'
            StartTime    = $start
        }
        foreach ($w in $wh) {
            $wkey = "{0}|{1}" -f $w.TimeCreated.ToString('o'), $w.Id
            if ($wheaSeen -notcontains $wkey) {
                $wheaSeen += $wkey
                $newWhea++
                $addr = ''
                try {
                    $wx = [xml]$w.ToXml()
                    foreach ($d in $wx.Event.EventData.Data) {
                        if ("$($d.Name)" -eq 'PhysicalAddress') { $addr = "$($d.'#text')" }
                    }
                } catch { }
                $suffix = if ($addr -and $addr -ne '0') { " адрес $addr" } else { '' }
                Write-Host ("  !! {0}  WHEA Event {1}{2}" -f $w.TimeCreated, $w.Id, $suffix) -ForegroundColor Red
            }
        }
    }

    ("{0},{1},{2},{3},{4},{5},{6},{7}" -f $now.ToString('o'), $temp, $draw, $limit, $util, $mem, $newEvents, $newWhea) |
        Out-File -FilePath $csv -Append -Encoding UTF8
    $samples++

    if ($samples % 10 -eq 1) {
        $left = [math]::Round(($end - $now).TotalHours, 1)
        Write-Host ("  {0}  temp={1}C  power={2}W  util={3}%  событий 41+: {4}  WHEA: {5}  осталось {6} ч" -f `
                    $now.ToString('HH:mm:ss'), $temp, $draw, $util, $eventsSeen.Count, $wheaSeen.Count, $left)
    }

    Start-Sleep -Seconds $IntervalSeconds
}

# Новая ошибка WHEA означает, что дефект живой, даже если крахов за окно не было.
$clean = ($eventsSeen.Count -eq 0 -and $wheaSeen.Count -eq 0 -and -not $eventLogBlocked)
$observed = [math]::Round(((Get-Date) - $start).TotalHours, 2)

$verdict = if ($eventLogBlocked) { 'NOT_MEASURED' } elseif ($clean) { 'PASS' } else { 'FAIL' }

$result = [ordered]@{
    started_at       = $start.ToString('o')
    finished_at      = (Get-Date).ToString('o')
    observed_hours   = $observed
    samples          = $samples
    max_temp_c       = $maxTemp
    max_power_w      = $maxDraw
    events_detected  = @($eventsSeen)
    whea_detected    = @($wheaSeen)
    event_log_blocked = $eventLogBlocked
    verdict          = $verdict
    csv              = $csv
}
$result | ConvertTo-Json -Depth 5 | Out-File -FilePath $summary -Encoding UTF8

Write-Host ''
Write-Host ('=' * 78) -ForegroundColor DarkCyan
Write-Host ("  ВЕРДИКТ: {0}   окно {1} ч, событий 41/6008/1001: {2}, WHEA: {3}" -f `
            $verdict, $observed, $eventsSeen.Count, $wheaSeen.Count) -ForegroundColor Cyan
Write-Host ('=' * 78) -ForegroundColor DarkCyan
Write-Host ("  Пик температуры / потребления: {0} C / {1} W" -f $maxTemp, $maxDraw)
Write-Host ("  CSV    : {0}" -f $csv)
Write-Host ("  Итог   : {0}" -f $summary)
Write-Host ''
if ($verdict -eq 'PASS' -and $observed -ge 48) {
    Write-Host '  Критерий выхода из hold по наблюдениям выполнен.' -ForegroundColor Green
    Write-Host '  Снятие HOST_SAFE_HOLD.flag остаётся решением владельца и выполняется' -ForegroundColor Yellow
    Write-Host '  штатной процедурой governor после REBOOT_PRECHECK/POSTCHECK.' -ForegroundColor Yellow
} elseif ($verdict -eq 'PASS') {
    Write-Host ("  Чисто, но окна мало: нужно 48 ч, наблюдали {0} ч. Продолжить наблюдение." -f $observed) -ForegroundColor Yellow
} elseif ($verdict -eq 'FAIL') {
    Write-Host '  Хост всё ещё нестабилен: hold обязателен, fix не помог или причина другая.' -ForegroundColor Red
    if ($wheaSeen.Count -gt 0 -and $eventsSeen.Count -eq 0) {
        Write-Host '  Крахов не было, но появились новые ошибки WHEA: дефект памяти живой,' -ForegroundColor Red
        Write-Host '  просто ещё не дошёл до краха. Новые адреса добавить в список исключений:' -ForegroundColor Red
        Write-Host '    .\apply_safehold_fix.ps1 -Action BadMemoryList -Confirm' -ForegroundColor DarkGray
    }
}
