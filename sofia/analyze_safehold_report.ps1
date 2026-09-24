<#
.SYNOPSIS
    Ставит диагноз по safehold_report.json, собранному diagnose_host_safe_hold.ps1.

.DESCRIPTION
    Реализует дерево решений из RUNBOOK_host_safe_hold.md: взвешивает улики,
    ранжирует гипотезы root cause и выдаёт одну минимальную обратимую команду.
    Ничего не изменяет: читает только указанный JSON.

    Гипотезы, которые различает анализатор:
      gpu_transient  - пики RTX 5090 роняют линию 12V (события 41 в окнах рендера)
      thermal        - перегрев (температура/throttle reasons)
      driver_bsod    - крах драйвера (есть BugCheck 1001 и минидампы)
      mains_psu      - питание сети или блок питания (события вне окон рендера)
      not_power      - событий 41 нет, hold выставлен по другой причине

.PARAMETER ReportPath
    Путь к safehold_report.json. По умолчанию берётся самый свежий отчёт
    из %TEMP%\sofia_safehold_*.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\analyze_safehold_report.ps1

.EXAMPLE
    .\analyze_safehold_report.ps1 -ReportPath C:\temp\safehold_report.json
#>

[CmdletBinding()]
param(
    [string] $ReportPath
)

$ErrorActionPreference = 'Stop'

function Write-Head {
    param([string]$Text)
    Write-Host ''
    Write-Host ('=' * 78) -ForegroundColor DarkCyan
    Write-Host "  $Text" -ForegroundColor Cyan
    Write-Host ('=' * 78) -ForegroundColor DarkCyan
}

if (-not $ReportPath) {
    $candidates = Get-ChildItem (Join-Path ([System.IO.Path]::GetTempPath()) 'sofia_safehold_*') -Directory -ErrorAction SilentlyContinue |
                  Sort-Object LastWriteTime -Descending
    foreach ($c in $candidates) {
        $p = Join-Path $c.FullName 'safehold_report.json'
        if (Test-Path $p) { $ReportPath = $p; break }
    }
}

if (-not $ReportPath -or -not (Test-Path $ReportPath)) {
    Write-Host 'Отчёт не найден. Сначала запустите diagnose_host_safe_hold.ps1,' -ForegroundColor Red
    Write-Host 'либо укажите путь: -ReportPath <...>\safehold_report.json' -ForegroundColor Red
    exit 2
}

$r = Get-Content $ReportPath -Raw | ConvertFrom-Json
$s = $r.sections

Write-Host ''
Write-Host 'Sofia AI Studio — анализ host_unstable_safe_hold' -ForegroundColor White
Write-Host ("Отчёт   : {0}" -f $ReportPath)
Write-Host ("Собран  : {0}  (хост {1}, окно {2} дн.)" -f $r.generated_at, $r.host, $r.window_days)

# ---------------------------------------------------------------------------
# Улики
# ---------------------------------------------------------------------------
$blocked41 = ($s.kernel_power -is [string] -and $s.kernel_power -eq 'ACCESS_DENIED')

$stats = $s.kernel_power_stats
$count41 = if ($stats) { [int]$stats.count_41 } else { 0 }
$bugchecks = if ($stats) { [int]$stats.bugcheck_count } else { 0 }
$gaps = if ($stats -and $stats.gaps_hours) { @($stats.gaps_hours) } else { @() }

$dumps = if ($s.minidumps) { @($s.minidumps).Count } else { 0 }

$corr = if ($s.correlation_41_vs_render) { @($s.correlation_41_vs_render) } else { @() }
$corrHits = @($corr | Where-Object { [int]$_.artifacts_20min -gt 0 }).Count

# Коды остановки прямо из текста сохранённых событий 1001 — точная улика без доп. запусков
$lib = Join-Path $PSScriptRoot 'lib_bugcheck.ps1'
$haveLib = Test-Path $lib
if ($haveLib) { . $lib }

$stopCodes = @()
if ($s.kernel_power -is [array]) {
    foreach ($e in $s.kernel_power) {
        if ([int]$e.id -ne 1001) { continue }
        $msg = [string]$e.message
        if ($msg -match '0x([0-9a-fA-F]{8})') {
            $code = [uint32]::Parse($Matches[1], 'HexNumber')
            $info = if ($haveLib) { Get-BugCheckInfo -Code $code }
                    else { [pscustomobject]@{ Hex = ('0x{0:X8}' -f $code); Name = 'UNKNOWN'; Class = 'driver'; Hint = '' } }
            $stopCodes += [pscustomobject]@{ Time = $e.time; Hex = $info.Hex; Name = $info.Name; Class = $info.Class; Hint = $info.Hint }
        }
    }
}

$findings = @($r.findings)
function Get-Finding { param([string]$Name) ($findings | Where-Object { $_.component -eq $Name } | Select-Object -First 1) }

$fTemp     = Get-Finding 'GPU температура'
$fLimit    = Get-Finding 'GPU power limit'
$fThrottle = Get-Finding 'GPU throttle reasons'
$fUps      = Get-Finding 'UPS/батарея'
$fHold     = Get-Finding 'HOST_SAFE_HOLD.flag'

$holdActive = ($fHold -and $fHold.status -eq 'FAIL')
$noUps      = ($fUps -and $fUps.status -eq 'WARN')
$thermalHit = (($fTemp -and $fTemp.status -in @('WARN','FAIL')) -or
               ($fThrottle -and $fThrottle.status -eq 'WARN'))
$limitAtMax = ($fLimit -and $fLimit.status -eq 'WARN')

Write-Head 'Улики'
if ($blocked41) {
    Write-Host '  Журнал System не прочитан (нет прав) — главная улика отсутствует.' -ForegroundColor Magenta
} else {
    Write-Host ("  Событий Kernel-Power 41 : {0}" -f $count41)
    if ($count41 -gt 0) {
        Write-Host ("  Первое / последнее      : {0}  ->  {1}" -f $stats.first, $stats.last)
        Write-Host ("  Частота                 : {0}/сут" -f $stats.per_day)
        if ($gaps.Count -ge 2) {
            Write-Host ("  Интервалы (ч)           : {0}" -f ($gaps -join ', '))
        }
    }
}
Write-Host ("  BugCheck 1001 / дампы   : {0} / {1}" -f $bugchecks, $dumps)
$covered = [math]::Max($bugchecks, $dumps)
if ($count41 -gt 0 -and $covered -gt 0 -and $covered -lt $count41) {
    Write-Host ("  ВНИМАНИЕ: дампы покрывают лишь {0} из {1} событий — остальные {2} прошли" -f $covered, $count41, ($count41 - $covered)) -ForegroundColor Yellow
    Write-Host '            без дампа, то есть как потеря питания. Причин, вероятно, две.' -ForegroundColor Yellow
}
foreach ($sc in $stopCodes) {
    Write-Host ("  Код остановки           : {0} {1}  ({2})" -f $sc.Hex, $sc.Name, $sc.Time) -ForegroundColor Yellow
    if ($sc.Hint) { Write-Host ("                            {0}" -f $sc.Hint) -ForegroundColor DarkGray }
}
if ($corr.Count -gt 0) {
    Write-Host ("  Совпало с рендером      : {0} из {1} событий" -f $corrHits, $corr.Count)
}
Write-Host ("  HOST_SAFE_HOLD.flag     : {0}" -f $(if ($holdActive) { 'активен' } else { 'не активен' }))

# ---------------------------------------------------------------------------
# Взвешивание гипотез
# ---------------------------------------------------------------------------
$h = [ordered]@{
    gpu_transient = 0
    thermal       = 0
    driver_bsod   = 0
    mains_psu     = 0
    not_power     = 0
}
$why = [ordered]@{
    gpu_transient = @()
    thermal       = @()
    driver_bsod   = @()
    mains_psu     = @()
    not_power     = @()
}

if (-not $blocked41) {
    if ($count41 -eq 0) {
        $h.not_power += 5
        $why.not_power += 'событий Kernel-Power 41 за окно нет'
    } else {
        $covered = [math]::Max($bugchecks, $dumps)
        if ($covered -gt 0) {
            # дамп даёт точный ответ по своим событиям, поэтому разбор дампа всегда первый шаг
            $h.driver_bsod += 7
            $why.driver_bsod += ("есть BugCheck и минидампы ({0}/{1}) — по этим событиям root cause определяется точно" -f $bugchecks, $dumps)

            # ...но только по своим: события без дампа - это отдельная причина
            $uncovered = $count41 - $covered
            if ($uncovered -gt 0) {
                $h.gpu_transient += 2; $h.mains_psu += 2
                $note = ("{0} из {1} событий прошли без дампа — это потеря питания, а не BSOD" -f $uncovered, $count41)
                $why.gpu_transient += $note
                $why.mains_psu     += $note
            }

            foreach ($sc in $stopCodes) {
                switch ($sc.Class) {
                    'gpu'      { $h.gpu_transient += 2; $why.gpu_transient += ("код {0} {1} указывает на видеоподсистему" -f $sc.Hex, $sc.Name) }
                    'hardware' { $h.mains_psu += 3;     $why.mains_psu     += ("код {0} {1} — аппаратная причина, не драйвер" -f $sc.Hex, $sc.Name) }
                    'memory'   { $h.driver_bsod += 1;   $why.driver_bsod   += ("код {0} {1} указывает на память" -f $sc.Hex, $sc.Name) }
                    default    { }
                }
            }
        } else {
            $h.gpu_transient += 1; $h.mains_psu += 1
            $why.gpu_transient += 'ресет без BSOD-дампа — похоже на потерю питания, а не крах драйвера'
            $why.mains_psu     += 'ресет без BSOD-дампа — похоже на потерю питания, а не крах драйвера'
        }

        if ($corr.Count -gt 0) {
            if ($corrHits -eq $corr.Count) {
                $h.gpu_transient += 4
                $why.gpu_transient += ("все {0} событий пришлись на активную работу пайплайна" -f $corr.Count)
            } elseif ($corrHits -gt 0) {
                $h.gpu_transient += 2; $h.mains_psu += 1
                $why.gpu_transient += ("{0} из {1} событий совпали с работой пайплайна" -f $corrHits, $corr.Count)
                $why.mains_psu     += ("{0} событий произошли вне окон рендера" -f ($corr.Count - $corrHits))
            } else {
                $h.mains_psu += 4
                $why.mains_psu += 'ни одно событие не совпало с работой пайплайна'
            }
        }

        if ($thermalHit) {
            $h.thermal += 3
            $why.thermal += 'температура GPU или активные throttle reasons вне нормы'
        }
        if ($limitAtMax) {
            $h.gpu_transient += 1
            $why.gpu_transient += 'power limit равен максимуму платы — транзиентные пики ничем не ограничены'
        }
        if ($noUps) {
            $h.mains_psu += 1
            $why.mains_psu += 'ИБП системе не виден — просадки сети ничем не сглажены'
        }
        if ($gaps.Count -ge 2) {
            $mean = ($gaps | Measure-Object -Average).Average
            if ($mean -gt 0) {
                $dev = ($gaps | ForEach-Object { [math]::Abs($_ - $mean) } | Measure-Object -Maximum).Maximum
                if (($dev / $mean) -lt 0.2) {
                    $h.gpu_transient += 1
                    $why.gpu_transient += ("интервалы между событиями почти равны (~{0} ч) — триггер по расписанию" -f [math]::Round($mean,1))
                }
            }
        }
    }
}

$ranked = $h.GetEnumerator() | Where-Object { $_.Value -gt 0 } | Sort-Object Value -Descending
$top = $ranked | Select-Object -First 1

Write-Head 'Гипотезы root cause (AI ANALYSIS, не факт)'
if (-not $ranked) {
    Write-Host '  Данных недостаточно для ранжирования — NOT_MEASURED.' -ForegroundColor DarkGray
} else {
    foreach ($k in $ranked) {
        $label = switch ($k.Key) {
            'gpu_transient' { 'Транзиенты GPU роняют питание' }
            'thermal'       { 'Перегрев / троттлинг' }
            'driver_bsod'   { 'Крах драйвера (BSOD)' }
            'mains_psu'     { 'Сеть или блок питания' }
            'not_power'     { 'Причина hold не в питании' }
        }
        $bar = '#' * [math]::Min(10, [int]$k.Value)
        Write-Host ("  [{0,-10}] {1,-38} {2}" -f $bar, $label, $k.Key) -ForegroundColor $(if ($k.Key -eq $top.Key) { 'Yellow' } else { 'DarkGray' })
        foreach ($w in $why[$k.Key]) { Write-Host ("               - {0}" -f $w) -ForegroundColor DarkGray }
    }
}

# ---------------------------------------------------------------------------
# Вердикт и единственный следующий шаг
# ---------------------------------------------------------------------------
$verdict = 'NOT_MEASURED'
$next = @()
$ownerDecision = @()

if ($blocked41) {
    $verdict = 'BLOCKED'
    $next += 'Перезапустить PowerShell от имени администратора и повторить diagnose_host_safe_hold.ps1:'
    $next += '  без журнала System диагноз поставить нельзя.'
} elseif ($count41 -eq 0) {
    $verdict = if ($holdActive) { 'WARN' } else { 'PASS' }
    $next += 'События 41 не подтвердились. Открыть последний incident-файл governor из секции'
    $next += 'governor_recent отчёта и посмотреть, какой порог сработал на самом деле.'
} else {
    $verdict = 'FAIL'
    switch ($top.Key) {
        'driver_bsod' {
            $next += 'Получить код остановки и виновника — без установки отладчика:'
            $next += '  .\analyze_minidump.ps1'
            $next += 'Скрипт читает событие 1001, заголовок дампа и, если есть, прогоняет !analyze -v.'
            $uncovered = $count41 - [math]::Max($bugchecks, $dumps)
            if ($uncovered -gt 0) {
                $next += ''
                $next += ("Затем отдельно закрыть {0} событий без дампа: это потеря питания," -f $uncovered)
                $next += 'а не крах драйвера — ИБП и проверка PSU, см. раздел mains_psu в runbook.'
            }
        }
        'thermal' {
            $next += 'Снять температурный профиль под нагрузкой и проверить охлаждение:'
            $next += '  nvidia-smi --query-gpu=timestamp,temperature.gpu,power.draw,clocks.sm --format=csv -l 5'
            $next += 'Параллельно проверить запылённость радиаторов и кривую вентиляторов.'
        }
        'gpu_transient' {
            $next += 'Применить минимальный обратимый fix — ограничить power limit GPU:'
            $next += '  .\apply_safehold_fix.ps1 -Action PowerLimit -Percent 80 -Confirm'
            $next += 'Скрипт сохранит исходное значение и создаст файл отката.'
        }
        'mains_psu' {
            $next += 'События вне окон рендера — питание вне GPU. Порядок проверки:'
            $next += '  1) поставить ИБП с линейно-интерактивным режимом;'
            $next += '  2) проверить возраст и запас мощности PSU под пиковую нагрузку RTX 5090;'
            $next += '  3) исключить общую линию с мощной бытовой нагрузкой.'
            $ownerDecision += 'замена/проверка PSU и установка ИБП — решение и руки владельца'
        }
        default {
            $next += 'Собрать ещё одно окно наблюдений: .\watch_host_stability.ps1 -Hours 24'
        }
    }
}

if ($holdActive) {
    $ownerDecision += 'HOST_SAFE_HOLD.flag не снимать до закрытия root cause и 48 ч без новых событий 41'
}

Write-Head ("ВЕРДИКТ: {0}" -f $verdict)
Write-Host '  Следующий шаг:' -ForegroundColor White
foreach ($n in $next) { Write-Host ("    {0}" -f $n) }
if ($ownerDecision.Count -gt 0) {
    Write-Host ''
    Write-Host '  Решение владельца:' -ForegroundColor Yellow
    foreach ($o in $ownerDecision) { Write-Host ("    - {0}" -f $o) -ForegroundColor Yellow }
}
Write-Host ''
