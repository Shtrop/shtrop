<#
.SYNOPSIS
    Протокол аренды GPU для тяжёлых задач Sofia AI Studio: владелец, свободная
    VRAM, освобождение без рестарта, проверка возврата к базовой линии.

.DESCRIPTION
    Закрывает шаг «CHECK OWNER -> CHECK FREE VRAM -> RELEASE/OFFLOAD -> VERIFY ->
    RUN -> POST-JOB RELEASE -> VERIFY BASELINE» и ловит зависание ComfyUI.

    Правила, заложенные в скрипт:

      * Один тяжёлый владелец GPU. Два процесса, держащих VRAM выше порога, —
        это конфликт, а не очередь: вердикт NO_GO.
      * Fail-closed. ERROR / MISSING / UNKNOWN / TIMEOUT никогда не становятся GO.
        Неизмеренное состояние — это NO_GO, а не «наверное, всё хорошо».
      * Перезапуск ComfyUI не является штатным механизмом освобождения VRAM,
        поэтому скрипт его не делает и не предлагает. Освобождение идёт через
        выгрузку моделей (Action Release), рестарт остаётся аварийной мерой
        владельца.
      * Состояние меняет только Action Release и только с -Confirm.
        Всё остальное — чтение.

.PARAMETER Action
    Preflight  — можно ли отдавать GPU тяжёлой задаче (по умолчанию).
    Baseline   — записать базовую линию простоя для последующего сравнения.
    Postflight — сравнить текущую VRAM с базовой линией, найти утечку.
    Watch      — следить за зависанием ComfyUI и неосвобождённой VRAM.
    Release    — выгрузить модели ComfyUI без перезапуска (нужен -Confirm).

.PARAMETER RequiredFreeMiB
    Сколько свободной VRAM требует тяжёлый маршрут. По умолчанию 16384.

.PARAMETER HeavyMiB
    С какого объёма занятой VRAM процесс считается тяжёлым владельцем.
    По умолчанию 2048.

.PARAMETER ToleranceMiB
    Допустимое расхождение с базовой линией в Postflight. По умолчанию 512.

.PARAMETER GpuIndex
    Индекс GPU. По умолчанию 0.

.PARAMETER ComfyUrl
    База ComfyUI. По умолчанию http://127.0.0.1:8188.

.PARAMETER ComfyPorts
    Порты, на которых искать экземпляры ComfyUI: -ComfyPorts 8188,8189.
    Пусто — искать самостоятельно: порт из -ComfyUrl плюс порты, которые
    слушают рендер-процессы. Принимает и список, и строку через запятую:
    при запуске через powershell -File аргумент приходит одной строкой, и
    [int[]] склеил бы «8188,8189» в одно число.

.PARAMETER RenderProcessPattern
    Образец пути процесса, по которому узнаётся рендер-воркер. Нужен там, где
    потребление по процессам недоступно и владельца приходится узнавать по
    имени. По умолчанию 'comfy|python|wan|infinitetalk'.

.PARAMETER BaselineFile
    Файл базовой линии. По умолчанию %TEMP%\sofia_gpu_baseline.json.

.PARAMETER Minutes
    Длительность Watch в минутах. По умолчанию 15.

.PARAMETER IntervalSeconds
    Период опроса в Watch. По умолчанию 30.

.PARAMETER StallSamples
    Сколько подряд «очередь работает, а GPU не считает» нужно для вердикта
    STALL. По умолчанию 4.

.PARAMETER OutFile
    Куда положить JSON с результатом. По умолчанию в %TEMP%.

.PARAMETER Confirm
    Разрешает единственное изменяющее действие — Release.

.EXAMPLE
    .\check_gpu_lease.ps1                                  # можно ли запускать тяжёлую задачу
.EXAMPLE
    .\check_gpu_lease.ps1 -Action Baseline                 # зафиксировать простой
.EXAMPLE
    .\check_gpu_lease.ps1 -Action Postflight               # вернулась ли VRAM после задачи
.EXAMPLE
    .\check_gpu_lease.ps1 -Action Watch -Minutes 30        # ловим stall и утечку
.EXAMPLE
    .\check_gpu_lease.ps1 -Action Release -Confirm         # выгрузить модели, без рестарта

.NOTES
    Коды возврата: 0 — GO/PASS, 1 — NO_GO/FAIL, 2 — NOT_MEASURED (тоже не GO).
    Скрипт ничего не удаляет, не трогает планировщик, не снимает hold-флаги и
    не перезапускает сервисы.
#>

[CmdletBinding()]
param(
    [ValidateSet('Preflight','Baseline','Postflight','Watch','Release')]
    [string] $Action = 'Preflight',
    [int]    $RequiredFreeMiB = 16384,
    [int]    $HeavyMiB = 2048,
    [int]    $ToleranceMiB = 512,
    [int]    $GpuIndex = 0,
    [string] $ComfyUrl = 'http://127.0.0.1:8188',
    [string] $RenderProcessPattern = 'comfy|python|wan|infinitetalk',
    [string[]] $ComfyPorts = @(),
    [string] $BaselineFile = (Join-Path ([System.IO.Path]::GetTempPath()) 'sofia_gpu_baseline.json'),
    [double] $Minutes = 15,
    [int]    $IntervalSeconds = 30,
    [int]    $StallSamples = 4,
    [string] $OutFile = (Join-Path ([System.IO.Path]::GetTempPath()) ("sofia_gpu_lease_{0}.json" -f (Get-Date -Format 'yyyyMMdd_HHmmss'))),
    [switch] $Confirm
)

$ErrorActionPreference = 'Continue'
$ProgressPreference    = 'SilentlyContinue'

$script:Findings = @()

function Add-Finding {
    param(
        [ValidateSet('PASS','WARN','FAIL','NOT_MEASURED')] [string] $Status,
        [string] $Component,
        [string] $Evidence,
        [string] $NextAction = ''
    )
    $script:Findings += [ordered]@{
        status = $Status; component = $Component; evidence = $Evidence; next_action = $NextAction
    }
    $color = switch ($Status) {
        'PASS'         { 'Green' }
        'WARN'         { 'Yellow' }
        'FAIL'         { 'Red' }
        'NOT_MEASURED' { 'Magenta' }
    }
    Write-Host ("  [{0,-12}] {1,-26} {2}" -f $Status, $Component, $Evidence) -ForegroundColor $color
    if ($NextAction) { Write-Host ("                 -> {0}" -f $NextAction) -ForegroundColor DarkGray }
}

function Write-Head {
    param([string] $Text)
    Write-Host ''
    Write-Host ('-' * 78) -ForegroundColor DarkCyan
    Write-Host ("  {0}" -f $Text) -ForegroundColor White
    Write-Host ('-' * 78) -ForegroundColor DarkCyan
}

# --- сбор фактов -----------------------------------------------------------

# Возвращает $null, если измерить не удалось. Нулями отсутствие данных не
# подменяем: ноль свободной VRAM и «не смогли спросить» — разные состояния.
function Get-GpuState {
    param([int] $Index)
    if (-not (Get-Command nvidia-smi -ErrorAction SilentlyContinue)) { return $null }
    $q = & nvidia-smi -i $Index --query-gpu='name,memory.total,memory.used,memory.free,utilization.gpu,temperature.gpu,power.draw,power.limit' --format=csv,noheader,nounits 2>&1
    $line = ($q | Out-String).Trim()
    if (-not $line -or $line -match 'Failed|Error|not found|No devices') { return $null }
    $f = $line.Split(',') | ForEach-Object { $_.Trim() }
    if ($f.Count -lt 8) { return $null }
    $num = {
        param($v)
        $clean = ($v -replace '[^\d\.]', '')
        if ($clean) { [double]$clean } else { $null }
    }
    [ordered]@{
        name          = $f[0]
        total_mib     = & $num $f[1]
        used_mib      = & $num $f[2]
        free_mib      = & $num $f[3]
        util_gpu_pct  = & $num $f[4]
        temp_c        = & $num $f[5]
        power_w       = & $num $f[6]
        power_limit_w = & $num $f[7]
    }
}

# На WDDM nvidia-smi ведёт себя двумя разными способами, и их нельзя путать:
# либо список compute-процессов не отдаётся вовсе ("Not Supported"), либо список
# приходит, но used_memory у каждой записи равен [N/A]. Во втором случае имена
# владельцев известны, а их потребление — нет, и считать «тяжёлых владельцев
# нет» по пустым значениям нельзя: это ровно то превращение UNKNOWN в PASS,
# от которого защищает весь остальной скрипт.
function Get-GpuOwners {
    param([int] $Index)
    if (-not (Get-Command nvidia-smi -ErrorAction SilentlyContinue)) {
        return @{ supported = $false; memory_known = $false; owners = @(); raw = 'nvidia-smi отсутствует' }
    }
    $q = & nvidia-smi -i $Index --query-compute-apps='pid,process_name,used_gpu_memory' --format=csv,noheader,nounits 2>&1
    $raw = ($q | Out-String).Trim()
    if ($raw -match 'Failed|Error') {
        return @{ supported = $false; memory_known = $false; owners = @(); raw = $raw }
    }
    $owners = @()
    foreach ($l in ($raw -split "`r?`n")) {
        $t = $l.Trim()
        if (-not $t) { continue }
        $p = $t.Split(',') | ForEach-Object { $_.Trim() }
        if ($p.Count -lt 3) { continue }
        # "[N/A]", "Not Supported" и пустое значение одинаково означают «неизвестно»
        $mem = ($p[2] -replace '[^\d\.]', '')
        $owners += [ordered]@{
            pid       = $p[0]
            process   = $p[1]
            used_mib  = if ($mem) { [double]$mem } else { $null }
        }
    }
    if ($owners.Count -eq 0) {
        return @{ supported = $false; memory_known = $false; owners = @(); raw = $(if ($raw) { $raw } else { 'пустой ответ' }) }
    }
    $known = @($owners | Where-Object { $null -ne $_.used_mib })
    return @{ supported = $true; memory_known = [bool]($known.Count -gt 0); owners = @($owners); raw = $raw }
}

# Список процессов на WDDM включает и графические задачи рабочего стола, поэтому
# в нём десятки строк. Печатаем ограниченно: сначала то, что реально занимает
# память, остальное — обрезанным списком имён.
# Когда nvidia-smi не отдаёт used_memory, потребление по процессам всё ещё
# доступно через счётчики производительности Windows — из них ту же картину
# рисует диспетчер задач. Имена счётчиков локализованы, а имена экземпляров
# ("pid_27900_luid_0x0_0xd8f1_phys_0") — нет, поэтому набор ищется по образцу
# экземпляра, а не по названию.
#
# Неоднозначностей две: какой из счётчиков набора означает выделенную память и
# какой адаптер наш (в системе может быть и встроенный GPU). Обе снимаются
# одним приёмом: суммы считаются по каждой паре (счётчик, адаптер), и берётся
# та, что ближе всего к занятости, измеренной nvidia-smi. Если ни одна пара не
# попадает в разумный коридор вокруг этого значения, владелец остаётся
# неизвестным — угадывать здесь нельзя.
function Select-GpuCounterOwners {
    param([array] $Samples, [double] $TargetUsedMiB)

    if (-not $Samples -or $Samples.Count -eq 0) { return @{ ok = $false; reason = 'счётчики не дали выборки' } }

    $rows = @()
    foreach ($smp in $Samples) {
        $path = [string]$smp.Path
        if ($path -notmatch '\(([^)]*pid_(\d+)_luid_([0-9a-fA-Fx_]+?)_phys_\d+)\)\\(.+)$') { continue }
        $rows += [pscustomobject]@{
            Pid     = $Matches[2]
            Luid    = $Matches[3]
            Counter = $Matches[4]
            Bytes   = [double]$smp.CookedValue
        }
    }
    if ($rows.Count -eq 0) { return @{ ok = $false; reason = 'среди счётчиков нет экземпляров вида pid_..._luid_..._phys_N' } }

    $best = $null
    foreach ($g in ($rows | Group-Object Counter, Luid)) {
        $sumMib = 0.0
        foreach ($r in $g.Group) { $sumMib += $r.Bytes / 1MB }
        $diff = [math]::Abs($sumMib - $TargetUsedMiB)
        if ($null -eq $best -or $diff -lt $best.Diff) {
            $best = [pscustomobject]@{ Diff = $diff; SumMib = $sumMib; Rows = $g.Group }
        }
    }
    if ($null -eq $best) { return @{ ok = $false; reason = 'не из чего выбирать' } }

    # Коридор вокруг измерения nvidia-smi: счётчики считают немного иначе, но
    # расхождение в разы означает, что выбрана не та величина или не тот
    # адаптер, и доверять ей нельзя.
    if ($TargetUsedMiB -gt 0) {
        $lo = $TargetUsedMiB * 0.5
        $hi = $TargetUsedMiB * 1.5
        if ($best.SumMib -lt $lo -or $best.SumMib -gt $hi) {
            # Расхождение в разы — счётчики видят не то, что nvidia-smi. Так
            # бывает, когда память выделена через CUDA: диспетчер видеопамяти
            # WDDM её процессам не приписывает. Возвращаем не просто «нет»,
            # а величину расхождения: она сама по себе улика.
            return @{ ok = $false; best_sum_mib = [math]::Round($best.SumMib); target_mib = [math]::Round($TargetUsedMiB) }
        }
    }

    $byPid = @{}
    foreach ($r in $best.Rows) {
        if (-not $byPid.ContainsKey($r.Pid)) { $byPid[$r.Pid] = 0.0 }
        $byPid[$r.Pid] += $r.Bytes / 1MB
    }
    $out = @()
    foreach ($k in $byPid.Keys) {
        $out += [ordered]@{ pid = $k; process = ''; used_mib = [math]::Round($byPid[$k]) }
    }
    return @{ ok = $true; owners = @($out); total_mib = [math]::Round($best.SumMib) }
}

function Get-GpuOwnersFromCounters {
    param([double] $TargetUsedMiB, [array] $KnownOwners = @())
    try {
        $set = Get-Counter -ListSet * -ErrorAction Stop |
               Where-Object { $_.PathsWithInstances -match 'pid_\d+_luid_.*_phys_\d' } |
               Select-Object -First 1
        if (-not $set) { return @{ ok = $false; reason = 'набор счётчиков GPU в системе не найден' } }
        $paths = @($set.PathsWithInstances | Where-Object { $_ -match '_phys_\d' })
        if ($paths.Count -eq 0) { return @{ ok = $false; reason = 'в наборе нет экземпляров _phys_' } }
        $samples = (Get-Counter -Counter $paths -ErrorAction Stop).CounterSamples
    } catch {
        # Текст исключения бывает многострочным и ломает таблицу находок.
        $msg = (($_.Exception.Message -split "`r?`n")[0]).Trim()
        return @{ ok = $false; reason = ("счётчики недоступны: {0}" -f $msg) }
    }

    $picked = Select-GpuCounterOwners -Samples $samples -TargetUsedMiB $TargetUsedMiB
    if (-not $picked -or -not $picked.ok) { return $picked }

    # Имена берём из уже собранного списка nvidia-smi, а чего там нет —
    # спрашиваем у системы.
    foreach ($o in $picked.owners) {
        $match = $KnownOwners | Where-Object { $_.pid -eq $o.pid } | Select-Object -First 1
        if ($match) {
            $o.process = $match.process
        } else {
            try { $o.process = (Get-Process -Id ([int]$o.pid) -ErrorAction Stop).ProcessName } catch { $o.process = ("pid {0}" -f $o.pid) }
        }
    }
    return $picked
}

# Два процесса одного дерева — это один экземпляр с подпроцессом, а не два
# владельца карты. Различать их обязательно: иначе каждый рендер, порождающий
# воркер, выглядел бы нарушением правила одного владельца и глушил бы
# production на ровном месте. Группы считаются по родству: процесс относится к
# той же группе, что и его родитель, если родитель тоже держит GPU.
function Select-OwnerGroups {
    param([array] $Procs)   # элементы: pid, parent

    $parentOf = @{}
    foreach ($p in $Procs) { $parentOf[[string]$p.pid] = [string]$p.parent }

    $rootOf = @{}
    foreach ($p in $Procs) {
        $cur = [string]$p.pid
        $seen = @{}
        while ($true) {
            if ($seen.ContainsKey($cur)) { break }   # защита от цикла в данных
            $seen[$cur] = $true
            $par = $parentOf[$cur]
            if (-not $par -or -not $parentOf.ContainsKey($par)) { break }
            $cur = $par
        }
        $rootOf[[string]$p.pid] = $cur
    }

    $groups = @{}
    foreach ($p in $Procs) {
        $r = $rootOf[[string]$p.pid]
        if (-not $groups.ContainsKey($r)) { $groups[$r] = @() }
        $groups[$r] += $p
    }
    return $groups
}

function Add-ParentPids {
    param([array] $Procs)
    try {
        $all = @{}
        foreach ($w in (Get-CimInstance Win32_Process -ErrorAction Stop | Select-Object ProcessId, ParentProcessId)) {
            $all[[string]$w.ProcessId] = [string]$w.ParentProcessId
        }
        foreach ($p in $Procs) {
            $p.parent = $all[[string]$p.pid]
        }
        return $true
    } catch {
        return $false
    }
}

function Write-OwnerList {
    param([array] $Owners, [bool] $MemoryKnown, [int] $Max = 12)
    if ($MemoryKnown) {
        $sorted = @($Owners | Sort-Object -Property @{ Expression = { if ($null -ne $_.used_mib) { $_.used_mib } else { -1 } } } -Descending)
    } else {
        $sorted = @($Owners)
    }
    $shown = @($sorted | Select-Object -First $Max)
    foreach ($o in $shown) {
        $mem = if ($null -ne $o.used_mib) { "{0} MiB" -f $o.used_mib } else { 'память неизвестна' }
        $name = Split-Path $o.process -Leaf
        Write-Host ("      pid {0,-8} {1,-44} {2}" -f $o.pid, $name, $mem) -ForegroundColor DarkGray
    }
    if ($sorted.Count -gt $shown.Count) {
        Write-Host ("      ... и ещё {0} из {1} процессов на GPU" -f ($sorted.Count - $shown.Count), $sorted.Count) -ForegroundColor DarkGray
    }
}

function Get-ComfyJson {
    param([string] $Url, [int] $TimeoutSec = 5)
    try { return @{ ok = $true; data = (Invoke-RestMethod -Uri $Url -TimeoutSec $TimeoutSec -Method Get) ; error = $null } }
    catch { return @{ ok = $false; data = $null; error = $_.Exception.Message } }
}

function Get-ComfyState {
    param([string] $Base, [int] $TimeoutSec = 5)
    $stats = Get-ComfyJson ("{0}/system_stats" -f $Base.TrimEnd('/')) $TimeoutSec
    $queue = Get-ComfyJson ("{0}/queue" -f $Base.TrimEnd('/')) $TimeoutSec
    $res = [ordered]@{
        reachable    = [bool]($stats.ok -or $queue.ok)
        error        = if ($stats.ok) { $null } else { $stats.error }
        vram_free    = $null
        vram_total   = $null
        torch_free   = $null
        torch_total  = $null
        torch_held   = $null
        running      = $null
        pending      = $null
    }
    if ($stats.ok -and $stats.data.devices) {
        $d = @($stats.data.devices)[0]
        if ($null -ne $d.vram_free)        { $res.vram_free   = [double]$d.vram_free / 1MB }
        if ($null -ne $d.vram_total)       { $res.vram_total  = [double]$d.vram_total / 1MB }
        if ($null -ne $d.torch_vram_free)  { $res.torch_free  = [double]$d.torch_vram_free / 1MB }
        if ($null -ne $d.torch_vram_total) { $res.torch_total = [double]$d.torch_vram_total / 1MB }
        # Выгружать имеет смысл только то, что torch реально держит. Свободное
        # место внутри его резервации к освобождению отношения не имеет.
        if ($null -ne $res.torch_total -and $null -ne $res.torch_free) {
            $res.torch_held = [math]::Max(0, $res.torch_total - $res.torch_free)
        }
    }
    if ($queue.ok -and $queue.data) {
        $res.running = @($queue.data.queue_running).Count
        $res.pending = @($queue.data.queue_pending).Count
    }
    return $res
}

# Проба одного порта показывает один экземпляр ComfyUI. Если на карте работает
# второй, он остаётся невидимым: очередь на известном порту пуста, а карта
# занята — и причина выглядит необъяснимой. Поэтому экземпляры ищутся по портам,
# которые слушают сами рендер-процессы, а не по списку угаданных номеров.
function Get-ComfyInstances {
    param(
        [string]   $PrimaryUrl,
        [array]    $Owners,
        [string]   $Pattern,
        [string[]] $Ports = @()
    )
    $primaryPort = 8188
    if ($PrimaryUrl -match ':(\d+)') { $primaryPort = [int]$Matches[1] }

    # Разбираем и список, и строку через запятую: через powershell -File
    # аргумент приходит одной строкой.
    $wanted = @()
    foreach ($item in $Ports) {
        foreach ($piece in ([string]$item -split '[,;\s]+')) {
            if ($piece -match '^\d+$') { $wanted += [int]$piece }
        }
    }

    $candidates = New-Object System.Collections.Generic.List[int]
    if ($wanted.Count -gt 0) {
        foreach ($p in $wanted) { if (-not $candidates.Contains([int]$p)) { $candidates.Add([int]$p) } }
    } else {
        $candidates.Add($primaryPort)
        $pids = @($Owners | Where-Object { $_.process -match $Pattern } | ForEach-Object { [string]$_.pid })
        if ($pids.Count -gt 0) {
            try {
                $listen = Get-NetTCPConnection -State Listen -ErrorAction Stop
                foreach ($c in $listen) {
                    if ($pids -contains [string]$c.OwningProcess) {
                        $port = [int]$c.LocalPort
                        if (-not $candidates.Contains($port)) { $candidates.Add($port) }
                    }
                }
            } catch { }
        }
    }

    # Под образец рендер-процесса попадает любой python, а он может слушать
    # десяток портов. Опрос каждого по общему таймауту растянул бы preflight на
    # минуту, а preflight — это gate перед запуском, он обязан быть быстрым.
    # Поэтому число кандидатов ограничено, а на разведку даётся короткий срок:
    # ComfyUI на localhost отвечает мгновенно либо не отвечает вовсе.
    $maxProbe = 12
    $probeList = @($candidates | Select-Object -First $maxProbe)
    $skipped = $candidates.Count - $probeList.Count

    $found = @()
    foreach ($port in $probeList) {
        $url = "http://127.0.0.1:{0}" -f $port
        # Основной порт опрашивается обычным таймаутом: по нему потом читается
        # очередь и VRAM, и ошибиться из-за спешки тут нельзя.
        $st = if ($port -eq $primaryPort) { Get-ComfyState -Base $url } else { Get-ComfyState -Base $url -TimeoutSec 2 }
        if ($st.reachable) {
            $found += [ordered]@{ port = $port; url = $url; primary = ($port -eq $primaryPort); state = $st }
        }
    }
    return @{ instances = @($found); probed = @($probeList); skipped_ports = $skipped }
}

function Write-Result {
    param([string] $Verdict, [hashtable] $Extra = @{})
    $payload = [ordered]@{
        action    = $Action
        checked_at = (Get-Date).ToString('o')
        gpu_index = $GpuIndex
        verdict   = $Verdict
        thresholds = [ordered]@{
            required_free_mib = $RequiredFreeMiB
            heavy_mib         = $HeavyMiB
            tolerance_mib     = $ToleranceMiB
        }
        findings  = @($script:Findings)
    }
    foreach ($k in $Extra.Keys) { $payload[$k] = $Extra[$k] }
    try { $payload | ConvertTo-Json -Depth 6 | Out-File -FilePath $OutFile -Encoding UTF8 } catch { }

    Write-Host ''
    Write-Host ('=' * 78) -ForegroundColor DarkCyan
    $c = switch ($Verdict) { 'GO' { 'Green' } 'PASS' { 'Green' } 'NO_GO' { 'Red' } 'FAIL' { 'Red' } default { 'Magenta' } }
    Write-Host ("  {0}: {1}" -f $Action.ToUpper(), $Verdict) -ForegroundColor $c
    Write-Host ('=' * 78) -ForegroundColor DarkCyan
    Write-Host ("  Отчёт: {0}" -f $OutFile) -ForegroundColor DarkGray
    Write-Host ''
}

function Get-ExitCode {
    param([string] $Verdict)
    switch ($Verdict) {
        'GO'   { 0 }
        'PASS' { 0 }
        'NOT_MEASURED' { 2 }
        default { 1 }
    }
}

# --- общий блок оценки владельца и свободной VRAM ---------------------------

function Test-LeaseReady {
    param([hashtable] $Gpu, [hashtable] $OwnerInfo, [hashtable] $Comfy, [array] $Instances = @())

    $blocking = $false

    if (-not $Gpu) {
        Add-Finding -Status 'NOT_MEASURED' -Component 'GPU' `
                    -Evidence 'nvidia-smi не ответил — состояние VRAM неизвестно' `
                    -NextAction 'без измерения тяжёлый маршрут не запускать: неизвестно != свободно'
        return 'NOT_MEASURED'
    }

    Add-Finding -Status 'PASS' -Component 'GPU' `
                -Evidence ("{0}: {1} MiB занято из {2} MiB, util {3}%, {4} W из {5} W" -f `
                           $Gpu.name, $Gpu.used_mib, $Gpu.total_mib, $Gpu.util_gpu_pct, $Gpu.power_w, $Gpu.power_limit_w)

    # 1. Владелец
    $heavyBlocking = $false

    # Решение о тяжёлых владельцах одно и то же, откуда бы ни пришли цифры —
    # от nvidia-smi или от счётчиков Windows. Отличается только подпись
    # источника, чтобы в отчёте было видно, чем мерили.
    function Test-HeavyOwners {
        param([array] $Owners, [string] $Source)
        $heavy = @($Owners | Where-Object { $null -ne $_.used_mib -and $_.used_mib -ge $HeavyMiB })
        if ($heavy.Count -eq 0) {
            Add-Finding -Status 'PASS' -Component 'владелец GPU' `
                        -Evidence ("тяжёлых владельцев нет, аренда свободна (по данным {0})" -f $Source)
            return $false
        }
        if ($heavy.Count -eq 1) {
            Add-Finding -Status 'WARN' -Component 'владелец GPU' `
                        -Evidence ("занято одним владельцем: pid {0} {1}, {2} MiB (по данным {3})" -f `
                                   $heavy[0].pid, (Split-Path $heavy[0].process -Leaf), $heavy[0].used_mib, $Source) `
                        -NextAction 'дождаться завершения текущей задачи — второй тяжёлый маршрут параллельно не запускать'
            return $true
        }
        $names = ($heavy | ForEach-Object { "{0}({1} MiB)" -f (Split-Path $_.process -Leaf), $_.used_mib }) -join ', '
        Add-Finding -Status 'FAIL' -Component 'владелец GPU' `
                    -Evidence ("тяжёлых владельцев {0}: {1} (по данным {2})" -f $heavy.Count, $names, $Source) `
                    -NextAction 'нарушено правило ONE HEAVY GPU OWNER — развести задачи по очереди, приоритет у production'
        return $true
    }

    if ($OwnerInfo.supported -and $OwnerInfo.memory_known) {
        Write-OwnerList -Owners $OwnerInfo.owners -MemoryKnown $true

        # Часть записей может прийти без used_memory. Если незакрытый остаток
        # занятой памяти сам дотягивает до порога, среди этих записей может
        # прятаться ещё один тяжёлый владелец, и молчать об этом нельзя.
        $unknownOwners = @($OwnerInfo.owners | Where-Object { $null -eq $_.used_mib })
        # Сумма считается перебором: элементы списка — hashtable, и
        # Measure-Object -Property по их ключам суммы не даёт (молча вернёт
        # пустоту, из-за чего всё занятое выглядело бы ничейным).
        $accounted = 0.0
        foreach ($o in $OwnerInfo.owners) {
            if ($null -ne $o.used_mib) { $accounted += [double]$o.used_mib }
        }
        $unaccounted = [double]$Gpu.used_mib - $accounted
        if ($unknownOwners.Count -gt 0 -and $unaccounted -ge $HeavyMiB) {
            Add-Finding -Status 'FAIL' -Component 'владелец GPU' `
                        -Evidence ("записей без used_memory: {0}; памяти ни за кем не числится: {1} MiB" -f $unknownOwners.Count, [math]::Round($unaccounted)) `
                        -NextAction 'среди них может быть ещё один тяжёлый владелец — тяжёлый маршрут не запускать'
            return 'NO_GO'
        }
        $heavyBlocking = Test-HeavyOwners -Owners $OwnerInfo.owners -Source 'nvidia-smi'
    } else {
        # Потребление по процессам от nvidia-smi неизвестно. Прежде чем
        # признать владельца неустановимым, пробуем три источника по
        # убыванию надёжности: имена рендер-процессов, очередь самого
        # ComfyUI и счётчики Windows.

        # 1) Правило одного тяжёлого владельца проверяется по именам, а не по
        #    памяти: два рендер-процесса на карте нарушают его независимо от
        #    того, сколько мегабайт за каждым числится.
        $renderish = @($OwnerInfo.owners | Where-Object { $_.process -match $RenderProcessPattern })
        if ($renderish.Count -ge 2) {
            foreach ($rp in $renderish) { if (-not $rp.Contains('parent')) { $rp['parent'] = $null } }
            $haveTree = Add-ParentPids -Procs $renderish
            $groups = if ($haveTree) { Select-OwnerGroups -Procs $renderish } else { $null }

            if ($haveTree -and $groups.Keys.Count -lt 2) {
                Write-Host ("      {0} рендер-процесса одного дерева — один экземпляр с подпроцессом" -f $renderish.Count) -ForegroundColor DarkGray
            } else {
                Write-OwnerList -Owners $renderish -MemoryKnown $false -Max 6
                $list = (@($renderish | ForEach-Object { "pid {0}" -f $_.pid }) -join ', ')
                $how = if ($haveTree) { ("{0} независимых дерева процессов" -f $groups.Keys.Count) } else { 'родство определить не удалось' }
                Add-Finding -Status 'FAIL' -Component 'владелец GPU' `
                            -Evidence ("на GPU {0} рендер-процесса ({1}), {2}; занято {3} MiB" -f $renderish.Count, $list, $how, $Gpu.used_mib) `
                            -NextAction 'похоже на два экземпляра ComfyUI — проверить: Get-CimInstance Win32_Process -Filter "Name=''python.exe''" | Select ProcessId,ParentProcessId,CommandLine'
                return 'NO_GO'
            }
        }

        # 2) Очередь ComfyUI — самый надёжный признак владельца на этом хосте:
        #    она отвечает на вопрос «кто занял карту» там, где ни nvidia-smi,
        #    ни счётчики не отвечают.
        $working = @($Instances | Where-Object { $_.state.running -gt 0 }) | Select-Object -First 1
        if (-not $working -and $Comfy.reachable -and $Comfy.running -gt 0) {
            $working = [ordered]@{ port = 'основной'; state = $Comfy }
        }
        if ($working -and $Gpu.used_mib -ge $HeavyMiB) {
            Add-Finding -Status 'WARN' -Component 'владелец GPU' `
                        -Evidence ("ComfyUI на порту {0} выполняет задачу, занято {1} MiB — владелец он (по очереди, не по nvidia-smi)" -f $working.port, $Gpu.used_mib) `
                        -NextAction 'дождаться завершения — второй тяжёлый маршрут параллельно не запускать'
            $heavyBlocking = $true
        } else {
            # 3) Счётчики Windows.
            Write-Host '      used_gpu_memory не отдаётся — опрашиваю счётчики Windows...' -ForegroundColor DarkGray
            $counters = Get-GpuOwnersFromCounters -TargetUsedMiB ([double]$Gpu.used_mib) -KnownOwners $OwnerInfo.owners

            if ($counters -and $counters.ok) {
                $sorted = @($counters.owners | Sort-Object { -[double]$_.used_mib })
                Write-OwnerList -Owners $sorted -MemoryKnown $true
                $heavyBlocking = Test-HeavyOwners -Owners $sorted -Source 'счётчики Windows'
            } else {
                if ($OwnerInfo.supported) {
                    Write-OwnerList -Owners $OwnerInfo.owners -MemoryKnown $false
                    $why = ("список процессов есть ({0} шт.), но used_gpu_memory не отдаётся" -f $OwnerInfo.owners.Count)
                } else {
                    $why = ("список процессов недоступен: {0}" -f $OwnerInfo.raw)
                }
                # Расхождение счётчиков с nvidia-smi — не шум, а улика: так
                # выглядит память, выделенная через CUDA, которую диспетчер
                # видеопамяти процессам не приписывает.
                $cnote = if ($counters -and $counters.best_sum_mib) {
                    ("; счётчики Windows насчитали всего {0} MiB против {1} MiB у nvidia-smi — память выделена мимо них (обычно CUDA)" -f $counters.best_sum_mib, $counters.target_mib)
                } elseif ($counters -and $counters.reason) {
                    ("; счётчики не помогли: {0}" -f $counters.reason)
                } else { '' }

                if ($Gpu.used_mib -ge $HeavyMiB) {
                    Add-Finding -Status 'FAIL' -Component 'владелец GPU' `
                                -Evidence ("{0}; занято {1} MiB{2}" -f $why, $Gpu.used_mib, $cnote) `
                                -NextAction 'владельца установить нельзя, а VRAM занята — тяжёлый маршрут не запускать'
                    $heavyBlocking = $true
                } else {
                    Add-Finding -Status 'WARN' -Component 'владелец GPU' `
                                -Evidence ("{0}; занято {1} MiB — ниже порога тяжёлой задачи{2}" -f $why, $Gpu.used_mib, $cnote) `
                                -NextAction 'владелец не определяется, но GPU фактически свободен'
                }
            }
        }
    }
    if ($heavyBlocking) { $blocking = $true }

    # 2. ComfyUI: занят ли он работой и сколько памяти реально держит
    if (-not $Comfy.reachable) {
        Add-Finding -Status 'NOT_MEASURED' -Component 'ComfyUI' `
                    -Evidence ("нет ответа: {0}" -f $Comfy.error) `
                    -NextAction 'состояние очереди неизвестно — запуск тяжёлой задачи вслепую запрещён'
        return 'NOT_MEASURED'
    }
    $qtext = "очередь: выполняется {0}, ожидает {1}" -f $Comfy.running, $Comfy.pending
    if ($Comfy.running -gt 0) {
        Add-Finding -Status 'WARN' -Component 'ComfyUI' -Evidence $qtext `
                    -NextAction 'ComfyUI уже занят — новый тяжёлый job встаёт в очередь, а не поверх текущего'
        $blocking = $true
    } else {
        Add-Finding -Status 'PASS' -Component 'ComfyUI' -Evidence $qtext
    }
    if ($null -ne $Comfy.torch_held -and $null -ne $Comfy.vram_free) {
        Add-Finding -Status 'PASS' -Component 'ComfyUI VRAM' `
                    -Evidence ("по данным ComfyUI свободно {0:N0} MiB, torch держит {1:N0} MiB" -f $Comfy.vram_free, $Comfy.torch_held)
    }

    # Очередь пуста, а карта занята и считает. Значит работу делает не этот
    # ComfyUI: либо второй экземпляр, либо чужая программа, либо прошлая задача
    # не отпустила память. Для инцидента с питанием это важнее всего
    # остального: карта под нагрузкой, а владельца в production-контуре нет.
    # Если работу делает другой найденный экземпляр, пустая очередь основного —
    # не аномалия, а объяснённая картина: аномалия это нагрузка, за которой не
    # стоит ни один известный ComfyUI.
    $anyWorking = @($Instances | Where-Object { $_.state.running -gt 0 }).Count -gt 0
    if ($Comfy.running -eq 0 -and -not $anyWorking) {
        $heldIdle = ($Gpu.used_mib -ge $HeavyMiB)
        $busyIdle = ($null -ne $Gpu.util_gpu_pct -and $Gpu.util_gpu_pct -ge 20)
        if ($heldIdle -or $busyIdle) {
            $ev = "очередь ComfyUI пуста, но GPU занят: {0} MiB, util {1}%, {2} W" -f $Gpu.used_mib, $Gpu.util_gpu_pct, $Gpu.power_w
            $na = if ($busyIdle) {
                'карту грузит не этот ComfyUI — искать второй экземпляр или стороннюю программу; для инцидента с питанием это первоочередная улика'
            } else {
                'память не освобождена после прошлой задачи либо её держит другой процесс: .\check_gpu_lease.ps1 -Action Watch'
            }
            Add-Finding -Status 'FAIL' -Component 'нагрузка без очереди' -Evidence $ev -NextAction $na
            $blocking = $true
        }
    }

    # 3. Свободная VRAM
    if ($null -eq $Gpu.free_mib) {
        Add-Finding -Status 'NOT_MEASURED' -Component 'свободная VRAM' -Evidence 'значение не прочитано'
        return 'NOT_MEASURED'
    }
    if ($Gpu.free_mib -ge $RequiredFreeMiB) {
        Add-Finding -Status 'PASS' -Component 'свободная VRAM' `
                    -Evidence ("{0} MiB свободно при требуемых {1} MiB" -f $Gpu.free_mib, $RequiredFreeMiB)
    } else {
        # Советовать выгрузку моделей имеет смысл, только если их есть что
        # выгружать. Когда torch почти ничего не держит, память занята другими
        # процессами, и Release не сдвинет ничего — совет увёл бы в сторону.
        $next = if ($null -eq $Comfy.torch_held) {
            'проверить, что именно держит память: .\check_gpu_lease.ps1 -Action Release (dry-run, ничего не меняет)'
        } elseif ($Comfy.torch_held -ge 1024) {
            ("ComfyUI держит {0:N0} MiB — освобождение: .\check_gpu_lease.ps1 -Action Release -Confirm (выгрузка моделей, не рестарт)" -f $Comfy.torch_held)
        } else {
            ("ComfyUI держит всего {0:N0} MiB — выгрузка моделей не поможет: память занята другими процессами на GPU" -f $Comfy.torch_held)
        }
        Add-Finding -Status 'FAIL' -Component 'свободная VRAM' `
                    -Evidence ("{0} MiB свободно, требуется {1} MiB" -f $Gpu.free_mib, $RequiredFreeMiB) `
                    -NextAction $next
        $blocking = $true
    }

    if ($blocking) { return 'NO_GO' }
    return 'GO'
}

# --- действия ---------------------------------------------------------------

Write-Host ''
Write-Host 'Sofia AI Studio — протокол аренды GPU' -ForegroundColor White
Write-Host ("Действие: {0}   GPU {1}   порог свободной VRAM: {2} MiB" -f $Action, $GpuIndex, $RequiredFreeMiB) -ForegroundColor DarkGray

switch ($Action) {

    'Preflight' {
        Write-Head 'PREFLIGHT: можно ли отдавать GPU тяжёлой задаче'
        $gpu    = Get-GpuState -Index $GpuIndex
        $owners = Get-GpuOwners -Index $GpuIndex

        $found = Get-ComfyInstances -PrimaryUrl $ComfyUrl -Owners $owners.owners `
                                    -Pattern $RenderProcessPattern -Ports $ComfyPorts
        $primary = @($found.instances | Where-Object { $_.primary }) | Select-Object -First 1
        $comfy = if ($primary) { $primary.state } else { Get-ComfyState -Base $ComfyUrl }

        # Несколько отвечающих экземпляров — это и есть нарушение правила одного
        # владельца, причём доказанное: не догадка по именам процессов, а два
        # живых ComfyUI, каждый со своей очередью.
        if ($found.instances.Count -ge 2) {
            $desc = (@($found.instances | ForEach-Object {
                "порт {0} (выполняется {1}, ожидает {2})" -f $_.port, $_.state.running, $_.state.pending
            }) -join '; ')
            Add-Finding -Status 'FAIL' -Component 'экземпляры ComfyUI' `
                        -Evidence ("отвечают {0} экземпляра: {1}" -f $found.instances.Count, $desc) `
                        -NextAction 'на карте два независимых ComfyUI — нарушено ONE HEAVY GPU OWNER, оставить один'
        }

        $verdict = Test-LeaseReady -Gpu $gpu -OwnerInfo $owners -Comfy $comfy -Instances $found.instances
        if ($found.instances.Count -ge 2 -and $verdict -eq 'GO') { $verdict = 'NO_GO' }
        Write-Result -Verdict $verdict -Extra @{
            gpu = $gpu; owners = $owners.owners; comfyui = $comfy
            comfy_instances = @($found.instances | ForEach-Object { [ordered]@{ port = $_.port; running = $_.state.running; pending = $_.state.pending } })
            comfy_ports_probed = @($found.probed)
            comfy_ports_skipped = $found.skipped_ports
        }
        if ($verdict -ne 'GO') {
            Write-Host '  Тяжёлый маршрут не запускать. CPU-работа (тренды, сценарии, аналитика) не блокируется.' -ForegroundColor Yellow
        }
        exit (Get-ExitCode $verdict)
    }

    'Baseline' {
        Write-Head 'BASELINE: фиксируем простой как точку отсчёта'
        $gpu   = Get-GpuState -Index $GpuIndex
        $comfy = Get-ComfyState -Base $ComfyUrl
        if (-not $gpu) {
            Add-Finding -Status 'NOT_MEASURED' -Component 'GPU' -Evidence 'nvidia-smi не ответил'
            Write-Result -Verdict 'NOT_MEASURED'
            exit 2
        }
        if ($comfy.running -gt 0 -or $comfy.pending -gt 0) {
            Add-Finding -Status 'WARN' -Component 'базовая линия' `
                        -Evidence ("ComfyUI не простаивает: выполняется {0}, ожидает {1}" -f $comfy.running, $comfy.pending) `
                        -NextAction 'база, снятая под нагрузкой, завысит «нормальную» занятость — снять повторно на простое'
        }
        $base = [ordered]@{
            recorded_at = (Get-Date).ToString('o')
            gpu_index   = $GpuIndex
            free_mib    = $gpu.free_mib
            used_mib    = $gpu.used_mib
            total_mib   = $gpu.total_mib
            comfy_running = $comfy.running
            comfy_pending = $comfy.pending
        }
        $base | ConvertTo-Json -Depth 4 | Out-File -FilePath $BaselineFile -Encoding UTF8
        Add-Finding -Status 'PASS' -Component 'базовая линия' `
                    -Evidence ("свободно {0} MiB, занято {1} MiB" -f $gpu.free_mib, $gpu.used_mib) `
                    -NextAction ("записано в {0}" -f $BaselineFile)
        Write-Result -Verdict 'PASS' -Extra @{ baseline = $base; baseline_file = $BaselineFile }
        exit 0
    }

    'Postflight' {
        Write-Head 'POSTFLIGHT: вернулась ли VRAM к базовой линии'
        if (-not (Test-Path $BaselineFile)) {
            Add-Finding -Status 'NOT_MEASURED' -Component 'базовая линия' `
                        -Evidence ("файл не найден: {0}" -f $BaselineFile) `
                        -NextAction 'снять базу на простое: .\check_gpu_lease.ps1 -Action Baseline'
            Write-Result -Verdict 'NOT_MEASURED'
            exit 2
        }
        $base = Get-Content $BaselineFile -Raw | ConvertFrom-Json
        $gpu  = Get-GpuState -Index $GpuIndex
        $comfy = Get-ComfyState -Base $ComfyUrl
        if (-not $gpu) {
            Add-Finding -Status 'NOT_MEASURED' -Component 'GPU' -Evidence 'nvidia-smi не ответил'
            Write-Result -Verdict 'NOT_MEASURED'
            exit 2
        }
        $delta = [double]$base.free_mib - [double]$gpu.free_mib
        Add-Finding -Status 'PASS' -Component 'база / сейчас' `
                    -Evidence ("свободно было {0} MiB, стало {1} MiB (разница {2} MiB)" -f $base.free_mib, $gpu.free_mib, [math]::Round($delta))
        $verdict = 'PASS'
        if ($comfy.reachable -and ($comfy.running -gt 0 -or $comfy.pending -gt 0)) {
            Add-Finding -Status 'WARN' -Component 'очередь' `
                        -Evidence ("ComfyUI ещё работает: выполняется {0}, ожидает {1}" -f $comfy.running, $comfy.pending) `
                        -NextAction 'сравнение с базой имеет смысл только после завершения очереди'
            $verdict = 'WARN'
        }
        if ($delta -gt $ToleranceMiB) {
            Add-Finding -Status 'FAIL' -Component 'возврат VRAM' `
                        -Evidence ("не возвращено {0} MiB сверх допуска {1} MiB" -f [math]::Round($delta), $ToleranceMiB) `
                        -NextAction 'выгрузить модели: .\check_gpu_lease.ps1 -Action Release -Confirm; рестарт ComfyUI — не штатный способ'
            $verdict = 'FAIL'
        } elseif ($verdict -ne 'WARN') {
            Add-Finding -Status 'PASS' -Component 'возврат VRAM' `
                        -Evidence ("в пределах допуска {0} MiB — утечки нет" -f $ToleranceMiB)
        }
        Write-Result -Verdict $verdict -Extra @{ gpu = $gpu; baseline = $base; delta_mib = [math]::Round($delta); comfyui = $comfy }
        exit (Get-ExitCode $verdict)
    }

    'Watch' {
        Write-Head ("WATCH: зависание ComfyUI и неосвобождённая VRAM ({0} мин)" -f $Minutes)
        $end = (Get-Date).AddMinutes($Minutes)
        $flat = 0          # подряд идущих «очередь работает, GPU простаивает»
        $idleHeld = 0      # подряд идущих «очередь пуста, VRAM держится»
        $stall = $false
        $leak  = $false
        $samples = 0
        $unreachable = 0
        while ((Get-Date) -lt $end) {
            $gpu   = Get-GpuState -Index $GpuIndex
            $comfy = Get-ComfyState -Base $ComfyUrl
            $samples++
            $ts = (Get-Date).ToString('HH:mm:ss')

            if (-not $gpu -or -not $comfy.reachable) {
                $unreachable++
                Write-Host ("  {0}  измерение недоступно (GPU: {1}, ComfyUI: {2})" -f `
                            $ts, [bool]$gpu, $comfy.reachable) -ForegroundColor Magenta
                Start-Sleep -Seconds $IntervalSeconds
                continue
            }

            $busy = ($comfy.running -gt 0)
            Write-Host ("  {0}  util {1,3}%  занято {2,6} MiB  очередь {3}/{4}" -f `
                        $ts, $gpu.util_gpu_pct, $gpu.used_mib, $comfy.running, $comfy.pending) -ForegroundColor DarkGray

            # Задача числится выполняющейся, но GPU не считает — это и есть stall.
            if ($busy -and $gpu.util_gpu_pct -lt 5) { $flat++ } elseif ($busy) { $flat = 0 }
            # Очередь пуста, а VRAM держится — модели не выгружены.
            if (-not $busy -and $gpu.used_mib -ge $HeavyMiB) { $idleHeld++ } else { $idleHeld = 0 }

            if ($flat -ge $StallSamples -and -not $stall) {
                $stall = $true
                Write-Host ("  !! {0}  STALL: очередь выполняется, GPU простаивает {1} проб подряд" -f $ts, $flat) -ForegroundColor Red
            }
            if ($idleHeld -ge $StallSamples -and -not $leak) {
                $leak = $true
                Write-Host ("  !! {0}  VRAM держится при пустой очереди {1} проб подряд" -f $ts, $idleHeld) -ForegroundColor Red
            }
            Start-Sleep -Seconds $IntervalSeconds
        }

        if ($unreachable -eq $samples -and $samples -gt 0) {
            Add-Finding -Status 'NOT_MEASURED' -Component 'окно наблюдения' `
                        -Evidence ("все {0} проб без данных" -f $samples) `
                        -NextAction 'проверить nvidia-smi в PATH и доступность ComfyUI'
            Write-Result -Verdict 'NOT_MEASURED' -Extra @{ samples = $samples }
            exit 2
        }
        if ($unreachable -gt 0) {
            Add-Finding -Status 'WARN' -Component 'пропуски измерений' `
                        -Evidence ("{0} проб из {1} без данных" -f $unreachable, $samples)
        }
        if ($stall) {
            Add-Finding -Status 'FAIL' -Component 'ComfyUI stall' `
                        -Evidence ("задача числилась активной при простаивающем GPU ≥{0} проб подряд" -f $StallSamples) `
                        -NextAction 'зафиксировать job id и логи ComfyUI; это дефект маршрута, а не повод для рестарта по расписанию'
        } else {
            Add-Finding -Status 'PASS' -Component 'ComfyUI stall' -Evidence 'зависаний не зафиксировано'
        }
        if ($leak) {
            Add-Finding -Status 'FAIL' -Component 'освобождение VRAM' `
                        -Evidence ("память удерживалась при пустой очереди ≥{0} проб подряд" -f $StallSamples) `
                        -NextAction 'после задачи вызывать .\check_gpu_lease.ps1 -Action Release -Confirm и затем Postflight'
        } else {
            Add-Finding -Status 'PASS' -Component 'освобождение VRAM' -Evidence 'после задач память возвращалась'
        }
        $verdict = if ($stall -or $leak) { 'FAIL' } else { 'PASS' }
        Write-Result -Verdict $verdict -Extra @{ samples = $samples; unreachable_samples = $unreachable; stall = $stall; vram_leak = $leak }
        exit (Get-ExitCode $verdict)
    }

    'Release' {
        Write-Head 'RELEASE: выгрузка моделей ComfyUI без перезапуска'
        $before = Get-GpuState -Index $GpuIndex
        $comfy  = Get-ComfyState -Base $ComfyUrl
        if (-not $comfy.reachable) {
            Add-Finding -Status 'FAIL' -Component 'ComfyUI' -Evidence ("нет ответа: {0}" -f $comfy.error) `
                        -NextAction 'освобождать нечем: сервис не отвечает. Рестарт — решение владельца, не этого скрипта'
            Write-Result -Verdict 'FAIL'
            exit 1
        }
        if ($comfy.running -gt 0) {
            Add-Finding -Status 'FAIL' -Component 'ComfyUI' `
                        -Evidence ("выполняется задач: {0} — выгрузка оборвёт работу" -f $comfy.running) `
                        -NextAction 'дождаться завершения очереди; приоритет у production-задачи'
            Write-Result -Verdict 'FAIL'
            exit 1
        }
        Write-Host ("  До  : свободно {0} MiB, занято {1} MiB" -f $before.free_mib, $before.used_mib)
        if (-not $Confirm) {
            Add-Finding -Status 'PASS' -Component 'dry-run' `
                        -Evidence 'без -Confirm ничего не выгружается' `
                        -NextAction ("POST {0}/free  {{unload_models:true, free_memory:true}}" -f $ComfyUrl.TrimEnd('/'))
            Write-Result -Verdict 'PASS' -Extra @{ dry_run = $true; gpu_before = $before }
            exit 0
        }
        $body = @{ unload_models = $true; free_memory = $true } | ConvertTo-Json -Compress
        try {
            Invoke-RestMethod -Uri ("{0}/free" -f $ComfyUrl.TrimEnd('/')) -Method Post -Body $body `
                              -ContentType 'application/json' -TimeoutSec 30 | Out-Null
        } catch {
            Add-Finding -Status 'FAIL' -Component 'выгрузка' -Evidence $_.Exception.Message `
                        -NextAction 'endpoint /free недоступен в этой сборке ComfyUI — освобождение выполняет владелец вручную'
            Write-Result -Verdict 'FAIL' -Extra @{ gpu_before = $before }
            exit 1
        }
        Start-Sleep -Seconds 5
        $after = Get-GpuState -Index $GpuIndex
        if (-not $after) {
            Add-Finding -Status 'NOT_MEASURED' -Component 'проверка после выгрузки' -Evidence 'nvidia-smi не ответил'
            Write-Result -Verdict 'NOT_MEASURED' -Extra @{ gpu_before = $before }
            exit 2
        }
        $freed = [double]$after.free_mib - [double]$before.free_mib
        Write-Host ("  После: свободно {0} MiB, занято {1} MiB" -f $after.free_mib, $after.used_mib)
        if ($freed -gt 0) {
            Add-Finding -Status 'PASS' -Component 'выгрузка' -Evidence ("освобождено {0} MiB" -f [math]::Round($freed))
        } else {
            Add-Finding -Status 'WARN' -Component 'выгрузка' `
                        -Evidence ("свободная VRAM не выросла (разница {0} MiB)" -f [math]::Round($freed)) `
                        -NextAction 'память держит не ComfyUI: искать владельца через Preflight'
        }
        $verdict = if ($after.free_mib -ge $RequiredFreeMiB) { 'PASS' } else { 'FAIL' }
        if ($verdict -eq 'FAIL') {
            Add-Finding -Status 'FAIL' -Component 'после выгрузки' `
                        -Evidence ("свободно {0} MiB, требуется {1} MiB" -f $after.free_mib, $RequiredFreeMiB) `
                        -NextAction 'тяжёлый маршрут остаётся заблокированным; рестарт ComfyUI штатным способом освобождения не считается'
        }
        Write-Result -Verdict $verdict -Extra @{ gpu_before = $before; gpu_after = $after; freed_mib = [math]::Round($freed) }
        exit (Get-ExitCode $verdict)
    }
}
