<#
.SYNOPSIS
    Наблюдает за стабильностью хоста Sofia AI Studio: копит доказательства для
    выхода из HOST_SAFE_HOLD.

.DESCRIPTION
    Периодически снимает телеметрию GPU и проверяет журнал System на новые
    события Kernel-Power 41 / 6008 / BugCheck 1001 и новые ошибки WHEA.
    Пишет CSV, состояние окна и итоговый JSON. Ничего не изменяет.

    Окно наблюдения переживает перезагрузку, но только с -Resume: момент старта
    лежит в window_state.json рядом с CSV, и при возобновлении события ищутся
    от исходного старта, а не от момента перезапуска. Поэтому ресет посреди
    окна не прячет собственное событие 41 — оно попадает в следующий отчёт.
    Без -Resume каждый запуск начинает окно заново.

    Вердикт и право на выход из hold — разные вещи:
      verdict          — были ли за окно крахи и ошибки WHEA;
      hold_exit_ready  — можно ли по этому окну выходить из hold.
    Чистое окно длиной в час даёт verdict = PASS и hold_exit_ready = false.

    Порог RequiredHours применяется к фактически набранному наблюдению
    (observed_hours), а не к календарному размаху окна: иначе возобновление
    давно брошенного окна засчиталось бы как 48 ч за пять минут работы.
    Разница между размахом и наблюдением видна в coverage_gap_hours.

.PARAMETER Hours
    Длительность текущего сеанса наблюдения в часах. По умолчанию 24.

.PARAMETER RequiredHours
    Требуемая длина всего окна для выхода из hold. По умолчанию 48 (runbook).
    Значение 0 снимает требование — только для тестов и отладки.

.PARAMETER Resume
    Продолжить ранее начатое окно: взять момент старта из window_state.json.
    Без -OutDir берётся самый свежий каталог sofia_stability_* в %TEMP%.

.PARAMETER IntervalSeconds
    Период опроса. По умолчанию 60.

.PARAMETER OutDir
    Каталог вывода. По умолчанию %TEMP%\sofia_stability_<timestamp>.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\watch_host_stability.ps1 -Hours 48

.EXAMPLE
    # после неожиданного ресета — продолжить то же окно, не начиная заново
    .\watch_host_stability.ps1 -Hours 48 -Resume

.NOTES
    Критерий выхода из hold по runbook: 48 ч штатной нагрузки без новых
    событий 41, минимум с одним полным production-циклом.
#>

[CmdletBinding()]
param(
    [double] $Hours = 24,
    [double] $RequiredHours = 48,
    [switch] $Resume,
    [int]    $IntervalSeconds = 60,

    # Сколько секунд режим power limit должен продержаться, чтобы считаться
    # режимом, а не переходным показанием. Задача закрепления срабатывает на
    # старте системы с задержкой и повторами, поэтому сразу после перезагрузки
    # карта какое-то время честно стоит на максимуме платы. Засчитывать это как
    # смену режима нельзя: такое показание попадёт в состояние окна и запрёт
    # выход из hold навсегда.
    [int]    $LimitSettleSeconds = 600,
    [string] $OutDir = ''
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
    # Несуществующий провайдер или неподходящая комбинация фильтра дают
    # EventLogException, которую -ErrorAction SilentlyContinue не подавляет,
    # поэтому глушим через try/catch и возвращаем пустой результат.
    $p = @{ FilterHashtable = $Filter; ErrorAction = 'Stop' }
    if ($MaxEvents -gt 0) { $p['MaxEvents'] = $MaxEvents }
    try { @(Get-WinEvent @p) } catch { @() }
}

function Get-WheaAddress {
    param($Event)
    try {
        $wx = [xml]$Event.ToXml()
        foreach ($d in $wx.Event.EventData.Data) {
            if ("$($d.Name)" -eq 'PhysicalAddress') { return "$($d.'#text')" }
        }
    } catch { }
    ''
}

# --------------------------------------------------------------------------
# Каталог вывода и состояние окна
# --------------------------------------------------------------------------

function Find-LatestWindowDir {
    $root = [System.IO.Path]::GetTempPath()
    $cand = @(Get-ChildItem -Path $root -Directory -Filter 'sofia_stability_*' -ErrorAction SilentlyContinue |
              Where-Object { Test-Path (Join-Path $_.FullName 'window_state.json') } |
              Sort-Object LastWriteTime -Descending)
    if ($cand.Count -gt 0) { return $cand[0].FullName }
    $null
}

if (-not $OutDir) {
    if ($Resume) {
        $found = Find-LatestWindowDir
        if ($found) {
            $OutDir = $found
        } else {
            Write-Host 'Возобновлять нечего: не найдено ни одного window_state.json. Начинаю новое окно.' -ForegroundColor Yellow
        }
    }
    if (-not $OutDir) {
        $OutDir = Join-Path ([System.IO.Path]::GetTempPath()) ("sofia_stability_{0}" -f (Get-Date -Format 'yyyyMMdd_HHmmss'))
    }
}

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$csv       = Join-Path $OutDir 'telemetry.csv'
$summary   = Join-Path $OutDir 'stability_summary.json'
$statePath = Join-Path $OutDir 'window_state.json'

$segmentStart   = Get-Date
$windowStart    = $segmentStart
$priorObserved  = 0.0   # часы наблюдения, набранные прошлыми сеансами
$segmentIndex   = 1
$limitFirst     = $null # power limit на начало всего окна, а не сеанса
$resumed        = $false
$script:ResumedRegimes = $null

if ($Resume -and (Test-Path $statePath)) {
    try {
        $prev = Get-Content $statePath -Raw | ConvertFrom-Json
        if ($prev.window_start) {
            $windowStart   = [datetime]::Parse($prev.window_start, [Globalization.CultureInfo]::InvariantCulture)
            $priorObserved = [double]$prev.observed_hours
            $segmentIndex  = [int]$prev.segments + 1
            if ($null -ne $prev.power_limit_w_first -and "$($prev.power_limit_w_first)") {
                $limitFirst = [double]$prev.power_limit_w_first
            }
            # Время, накопленное каждым режимом, переживает перезапуск: смена
            # лимита РОВНО на перезагрузке — штатный способ его потерять, и в
            # пределах одного сеанса её не видно.
            if ($prev.power_limit_regimes) {
                $script:ResumedRegimes = @($prev.power_limit_regimes | ForEach-Object {
                    [pscustomobject]@{ W = [double]$_.w; Seconds = [int]$_.seconds }
                })
            }
            $resumed = $true
        }
    } catch {
        Write-Host ("Не удалось прочитать {0}: {1}. Начинаю новое окно." -f $statePath, $_.Exception.Message) -ForegroundColor Yellow
    }
} elseif ($Resume) {
    Write-Host 'В каталоге нет window_state.json — начинаю новое окно.' -ForegroundColor Yellow
}

$end = $segmentStart.AddHours($Hours)

Write-Host ''
Write-Host 'Sofia AI Studio — наблюдение за стабильностью хоста (READ-ONLY)' -ForegroundColor White
if ($resumed) {
    Write-Host ("Окно    : продолжение, сеанс {0}, старт окна {1}" -f $segmentIndex, $windowStart) -ForegroundColor Cyan
    Write-Host ("          набрано ранее {0} ч наблюдения" -f [math]::Round($priorObserved, 2)) -ForegroundColor Cyan
}
Write-Host ("Старт   : {0}" -f $segmentStart)
Write-Host ("Финиш   : {0}  ({1} ч, опрос каждые {2} с)" -f $end, $Hours, $IntervalSeconds)
Write-Host ("Порог   : {0} ч непрерывного окна для выхода из hold" -f $RequiredHours)
Write-Host ("Вывод   : {0}" -f $OutDir)
Write-Host 'Прервать можно Ctrl+C — собранные данные останутся на месте.' -ForegroundColor DarkGray
Write-Host ''

if (-not (Test-Path $csv)) {
    'timestamp,temp_c,power_w,limit_w,util_pct,mem_used_mib,new_events_41,new_whea' | Out-File -FilePath $csv -Encoding UTF8
}

$hasNvidia = [bool](Get-Command nvidia-smi -ErrorAction SilentlyContinue)
if (-not $hasNvidia) {
    Write-Host 'nvidia-smi не найден — телеметрия GPU будет пустой, события всё равно отслеживаются.' -ForegroundColor Yellow
}

$maxTemp     = 0.0
$maxDraw     = 0.0
$samples     = 0
$eventsSeen  = @()
$wheaSeen    = @()
$limitLast   = $null
# Сколько секунд держался каждый увиденный power limit, по всему окну.
# Порядок — по первому появлению, поэтому это список, а не хэш-таблица.
$limitRegimes = @()
if ($script:ResumedRegimes) { $limitRegimes = @($script:ResumedRegimes) }

# Доступ к журналу проверяется пробой на каждом опросе: если права пропали
# посреди окна, «событий не было» перестаёт быть доказательством. Потеря
# доступа в любой момент окна делает всё окно неизмеренным — fail-closed.
$everBlocked = -not (Test-SystemLogReadable)
if ($everBlocked) {
    Write-Host 'Журнал System недоступен — перезапустите PowerShell от имени администратора.' -ForegroundColor Magenta
    Write-Host 'Телеметрия GPU собираться будет, но события и WHEA — нет.' -ForegroundColor Magenta
}

function Save-WindowState {
    param([double] $ObservedHours)
    [ordered]@{
        window_start       = $windowStart.ToString('o')
        last_segment_start = $segmentStart.ToString('o')
        last_seen_at       = (Get-Date).ToString('o')
        observed_hours     = [math]::Round($ObservedHours, 4)
        segments           = $segmentIndex
        required_hours     = $RequiredHours
        power_limit_w_first = $limitFirst
        power_limit_regimes = @($limitRegimes | ForEach-Object { [ordered]@{ w = $_.W; seconds = $_.Seconds } })
        csv                = $csv
    } | ConvertTo-Json -Depth 5 | Out-File -FilePath $statePath -Encoding UTF8
}

Save-WindowState -ObservedHours $priorObserved

while ((Get-Date) -lt $end) {
    $now = Get-Date
    $temp = ''; $draw = ''; $limit = ''; $util = ''; $mem = ''

    if ($hasNvidia) {
        try {
            # -i обязателен: без него многокарточная система даёт несколько
            # строк, Out-String склеивает их, и поля разных карт перемешиваются.
            $q = & nvidia-smi -i 0 --query-gpu="temperature.gpu,power.draw,power.limit,utilization.gpu,memory.used" --format=csv,noheader 2>&1
            $f = ($q | Out-String).Trim().Split(',') | ForEach-Object { $_.Trim() }
            if ($f.Count -ge 5) {
                $temp  = ($f[0] -replace '[^\d\.]','')
                $draw  = ($f[1] -replace '[^\d\.]','')
                $limit = ($f[2] -replace '[^\d\.]','')
                $util  = ($f[3] -replace '[^\d\.]','')
                $mem   = ($f[4] -replace '[^\d\.]','')
                if ($temp) { $maxTemp = [math]::Max($maxTemp, [double]$temp) }
                if ($draw) { $maxDraw = [math]::Max($maxDraw, [double]$draw) }
                if ($limit) {
                    $lv = [double]$limit
                    $limitLast = $lv
                    if ($null -eq $limitFirst) { $limitFirst = $lv }
                    # Копим ВРЕМЯ удержания, а не факт появления: переходное
                    # показание само обесценивается по мере роста окна, и
                    # запереть им выход из hold нельзя.
                    $hit = @($limitRegimes | Where-Object { [math]::Abs($_.W - $lv) -le 1 })
                    if ($hit.Count -gt 0) { $hit[0].Seconds += $IntervalSeconds }
                    else { $limitRegimes += [pscustomobject]@{ W = $lv; Seconds = $IntervalSeconds } }
                }
            }
        } catch { }
    }

    $newEvents = 0
    $newWhea = 0

    $blockedNow = -not (Test-SystemLogReadable)
    if ($blockedNow -and -not $everBlocked) {
        $everBlocked = $true
        Write-Host ("  !! {0}  доступ к журналу System потерян — окно больше не доказательство" -f $now) -ForegroundColor Magenta
    }

    if (-not $blockedNow) {
        # Поиск ведётся от старта ВСЕГО окна, а не сеанса: иначе собственный
        # ресет посреди окна спрятал бы своё же событие 41.
        $ev = Get-SystemEvents -Filter @{
            LogName   = 'System'
            Id        = 41, 6008, 1001
            StartTime = $windowStart
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
            StartTime    = $windowStart
        }
        foreach ($w in $wh) {
            $wkey = "{0}|{1}" -f $w.TimeCreated.ToString('o'), $w.Id
            if ($wheaSeen -notcontains $wkey) {
                $wheaSeen += $wkey
                $newWhea++
                $addr = Get-WheaAddress -Event $w
                $suffix = if ($addr -and $addr -ne '0') { " адрес $addr" } else { '' }
                Write-Host ("  !! {0}  WHEA Event {1}{2}" -f $w.TimeCreated, $w.Id, $suffix) -ForegroundColor Red
            }
        }
    }

    ("{0},{1},{2},{3},{4},{5},{6},{7}" -f $now.ToString('o'), $temp, $draw, $limit, $util, $mem, $newEvents, $newWhea) |
        Out-File -FilePath $csv -Append -Encoding UTF8
    $samples++

    $observedNow = $priorObserved + ((Get-Date) - $segmentStart).TotalHours
    Save-WindowState -ObservedHours $observedNow

    if ($samples % 10 -eq 1) {
        $left = [math]::Round(($end - $now).TotalHours, 1)
        Write-Host ("  {0}  temp={1}C  power={2}W  util={3}%  событий 41+: {4}  WHEA: {5}  осталось {6} ч" -f `
                    $now.ToString('HH:mm:ss'), $temp, $draw, $util, $eventsSeen.Count, $wheaSeen.Count, $left)
    }

    Start-Sleep -Seconds $IntervalSeconds
}

# --------------------------------------------------------------------------
# Итог
# --------------------------------------------------------------------------

$finishedAt  = Get-Date
$observed    = [math]::Round($priorObserved + ($finishedAt - $segmentStart).TotalHours, 2)
$windowSpan  = [math]::Round(($finishedAt - $windowStart).TotalHours, 2)
$coverageGap = [math]::Round([math]::Max($windowSpan - $observed, 0), 2)

# Новая ошибка WHEA означает, что дефект живой, даже если крахов за окно не было.
$clean   = ($eventsSeen.Count -eq 0 -and $wheaSeen.Count -eq 0)
$verdict = if ($everBlocked) { 'NOT_MEASURED' } elseif ($clean) { 'PASS' } else { 'FAIL' }

# Смягчение, которое не держалось всё окно, обесценивает окно: наблюдали
# один режим питания, а в production вернётся другой.
#
# Режимом считается только то, что продержалось дольше порога. Переходное
# показание сразу после перезагрузки режимом не становится и окно не запирает,
# а настоящая смена набирает часы и видна независимо от того, случилась она
# посреди работы или ровно на перезагрузке.
$settled = @($limitRegimes | Where-Object { $_.Seconds -ge $LimitSettleSeconds })
$limitChanged = ($settled.Count -gt 1)

$blockers = @()
if ($everBlocked)               { $blockers += 'event_log_blocked: журнал System не читался, крахи могли быть не видны' }
if (-not $clean)                { $blockers += ("crash_or_whea_in_window: событий {0}, WHEA {1}" -f $eventsSeen.Count, $wheaSeen.Count) }
# Считается именно наблюдение, а не календарный размах окна: иначе
# возобновление давно брошенного окна дало бы «48 ч» за пять минут работы.
if ($observed -lt $RequiredHours) { $blockers += ("window_short: наблюдения {0} ч из требуемых {1} ч" -f $observed, $RequiredHours) }
if ($coverageGap -gt 1) { $blockers += ("coverage_gap: {0} ч окна прошли без наблюдения — нагрузка за это время не подтверждена" -f $coverageGap) }
if ($limitChanged) {
    $shape = ($settled | ForEach-Object { "{0} W ({1} ч)" -f [int]$_.W, [math]::Round($_.Seconds / 3600, 1) }) -join ', '
    $blockers += ("power_limit_changed: за окно держались разные режимы — {0}" -f $shape)
}

$holdExitReady = ($blockers.Count -eq 0)

$result = [ordered]@{
    window_start        = $windowStart.ToString('o')
    started_at          = $segmentStart.ToString('o')
    finished_at         = $finishedAt.ToString('o')
    segments            = $segmentIndex
    resumed             = $resumed
    observed_hours      = $observed
    window_span_hours   = $windowSpan
    coverage_gap_hours  = $coverageGap
    required_hours      = $RequiredHours
    samples             = $samples
    max_temp_c          = $maxTemp
    max_power_w         = $maxDraw
    power_limit_w_first = $limitFirst
    power_limit_w_last  = $limitLast
    power_limit_changed = $limitChanged
    power_limit_settle_seconds = $LimitSettleSeconds
    power_limit_regimes = @($limitRegimes | ForEach-Object {
        [ordered]@{ w = $_.W; seconds = $_.Seconds; settled = ($_.Seconds -ge $LimitSettleSeconds) }
    })
    events_detected     = @($eventsSeen)
    whea_detected       = @($wheaSeen)
    event_log_blocked   = $everBlocked
    verdict             = $verdict
    hold_exit_ready     = $holdExitReady
    hold_exit_blockers  = @($blockers)
    csv                 = $csv
}
$result | ConvertTo-Json -Depth 5 | Out-File -FilePath $summary -Encoding UTF8
Save-WindowState -ObservedHours $observed

Write-Host ''
Write-Host ('=' * 78) -ForegroundColor DarkCyan
Write-Host ("  ВЕРДИКТ: {0}   окно {1} ч, событий 41/6008/1001: {2}, WHEA: {3}" -f `
            $verdict, $windowSpan, $eventsSeen.Count, $wheaSeen.Count) -ForegroundColor Cyan
Write-Host ("  ВЫХОД ИЗ HOLD: {0}" -f $(if ($holdExitReady) { 'условия наблюдения выполнены' } else { 'НЕТ' })) `
           -ForegroundColor $(if ($holdExitReady) { 'Green' } else { 'Yellow' })
Write-Host ('=' * 78) -ForegroundColor DarkCyan
Write-Host ("  Наблюдение / окно / пропуск: {0} ч / {1} ч / {2} ч  (порог {3} ч по наблюдению)" -f `
            $observed, $windowSpan, $coverageGap, $RequiredHours)
Write-Host ("  Пик температуры / потребления: {0} C / {1} W" -f $maxTemp, $maxDraw)
if ($null -ne $limitFirst) {
    Write-Host ("  Power limit: {0} W -> {1} W{2}" -f $limitFirst, $limitLast, $(if ($limitChanged) { '  (менялся за окно!)' } else { '' }))
}
Write-Host ("  CSV    : {0}" -f $csv)
Write-Host ("  Итог   : {0}" -f $summary)
Write-Host ''

foreach ($b in $blockers) { Write-Host ("  BLOCKER  {0}" -f $b) -ForegroundColor Yellow }

if ($holdExitReady) {
    Write-Host ''
    Write-Host '  Критерий выхода из hold по наблюдениям выполнен.' -ForegroundColor Green
    Write-Host '  Снятие HOST_SAFE_HOLD.flag остаётся решением владельца и выполняется' -ForegroundColor Yellow
    Write-Host '  штатной процедурой governor после REBOOT_PRECHECK/POSTCHECK.' -ForegroundColor Yellow
    Write-Host '  Перед reboot проверить, что смягчение переживёт перезагрузку:' -ForegroundColor Yellow
    Write-Host '    .\apply_safehold_fix.ps1 -Action Status' -ForegroundColor DarkGray
} elseif ($verdict -eq 'FAIL') {
    Write-Host ''
    Write-Host '  Хост всё ещё нестабилен: hold обязателен, fix не помог или причина другая.' -ForegroundColor Red
    if ($wheaSeen.Count -gt 0 -and $eventsSeen.Count -eq 0) {
        Write-Host '  Крахов не было, но появились новые ошибки WHEA: дефект памяти живой,' -ForegroundColor Red
        Write-Host '  просто ещё не дошёл до краха. Новые адреса добавить в список исключений:' -ForegroundColor Red
        Write-Host '    .\apply_safehold_fix.ps1 -Action BadMemoryList -Confirm' -ForegroundColor DarkGray
    }
} elseif ($verdict -eq 'PASS') {
    Write-Host ''
    Write-Host ("  Чисто, но окно не закрыто. Продолжить тем же окном:" ) -ForegroundColor Yellow
    Write-Host ("    .\watch_host_stability.ps1 -Hours {0} -Resume" -f $Hours) -ForegroundColor DarkGray
}
