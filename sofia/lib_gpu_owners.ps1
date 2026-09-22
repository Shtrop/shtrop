<#
.SYNOPSIS
    Разбор владельцев GPU и правило ONE HEAVY GPU OWNER.

.DESCRIPTION
    Подключается точкой: . .\lib_gpu_owners.ps1

    Строка nvidia-smi --query-compute-apps сама по себе ничего не доказывает:
    «на GPU есть задачи» одинаково выглядит и для штатного рендера, и для двух
    конкурирующих ComfyUI, оставшихся от прошлых прогонов. Здесь она
    превращается в вердикт.

    Два разных дефекта, которые ловит этот разбор:
      - несколько тяжёлых владельцев одновременно: они делят VRAM и питание,
        и именно это даёт просадки, OOM и срывы рендера;
      - VRAM занята, а тяжёлых задач нет: освобождение после рендера не
        отработало, память держит завершившийся или зависший процесс.

    Функции чистые: на вход текст и числа, на выход объект. Поэтому их можно
    проверять тестами где угодно, без GPU.
#>

# Процессы рабочего стола держат VRAM всегда и владельцами рендера не являются.
$script:GpuDesktopProcesses = @(
    'dwm.exe', 'explorer.exe', 'csrss.exe', 'winlogon.exe', 'taskhostw.exe',
    'chrome.exe', 'msedge.exe', 'firefox.exe', 'Code.exe', 'Discord.exe',
    'nvcontainer.exe', 'NVIDIA Share.exe', 'SearchHost.exe', 'StartMenuExperienceHost.exe'
)

# Имена, по которым процесс считается владельцем тяжёлого рендера независимо
# от того, сколько VRAM он занимает в момент снимка: между шагами пайплайна
# занятая память проседает, но владельцем он быть не перестаёт.
$script:GpuRenderProcessPatterns = @(
    'python', 'pythonw', 'comfy', 'ffmpeg', 'wan2', 'sdxl', 'sd_', 'diffus',
    'torch', 'ollama', 'llama', 'koboldcpp', 'automatic1111', 'invokeai'
)

function ConvertFrom-NvidiaComputeApps {
    <#
        Разбирает вывод:
            nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader
        Строки вида: "12345, C:\...\python.exe, 8192 MiB"
        Мусор и служебные строки ("No running processes found") пропускаются.
    #>
    param([string] $Text)

    $apps = @()
    if (-not $Text) { return @($apps) }

    foreach ($line in ($Text -split "`r?`n")) {
        $l = $line.Trim()
        if (-not $l) { continue }
        if ($l -match '(?i)no running processes') { continue }
        if ($l -match '(?i)^(failed|unable|error)') { continue }

        $parts = $l -split ','
        if ($parts.Count -lt 3) { continue }

        $pidText = $parts[0].Trim()
        if ($pidText -notmatch '^\d+$') { continue }

        # Путь может содержать запятые, поэтому имя — всё между pid и памятью.
        $memText = $parts[-1].Trim()
        $nameText = ($parts[1..($parts.Count - 2)] -join ',').Trim()

        # На Windows под WDDM nvidia-smi отдаёт used_memory как [N/A] почти
        # всегда: per-process VRAM там доступна только в TCC. Ноль и «не
        # измерено» — разные вещи, иначе занятая память молча спишется в ноль.
        $mem = 0
        $memKnown = $false
        if ($memText -notmatch '(?i)n/?a' -and $memText -match '([\d\.]+)') {
            $mem = [int][double]$Matches[1]
            $memKnown = $true
        }

        $apps += [pscustomobject]@{
            Pid      = [int]$pidText
            Path     = $nameText
            Name     = (Split-Path $nameText -Leaf)
            UsedMiB  = $mem
            MemKnown = $memKnown
        }
    }
    @($apps)
}

function Test-GpuRenderProcess {
    param([string] $Name, [string] $Path = '')
    $probe = ("{0} {1}" -f $Name, $Path).ToLower()
    foreach ($p in $script:GpuRenderProcessPatterns) {
        if ($probe -like ("*{0}*" -f $p.ToLower())) { return $true }
    }
    $false
}

function Get-GpuProcessMemoryMiB {
    <#
        Сколько VRAM держит каждый процесс, по счётчикам производительности
        Windows. Нужен там, где nvidia-smi отдаёт used_memory как [N/A]:
        под WDDM это норма, а не сбой.

        Имя набора счётчиков локализовано, поэтому набор ищется по виду имён
        экземпляров (pid_<N>_luid_..._phys_<N>), а не по названию — тот же
        принцип, что и с локализованными текстами ошибок журнала.

        Возвращает хэш-таблицу @{ pid = MiB }. Пустая — значит счётчики не
        дались; это «не измерено», а не «памяти нет».
    #>
    $result = @{}
    if (-not (Get-Command Get-Counter -ErrorAction SilentlyContinue)) { return $result }
    try {
        $set = @(Get-Counter -ListSet * -ErrorAction Stop |
                 Where-Object { $_.PathsWithInstances -match 'pid_\d+_luid_.*_phys_\d' } |
                 Select-Object -First 1)
        if ($set.Count -eq 0) { return $result }

        $paths = @($set[0].PathsWithInstances | Where-Object { $_ -match '_phys_\d' })
        if ($paths.Count -eq 0) { return $result }

        foreach ($sample in (Get-Counter -Counter $paths -ErrorAction Stop).CounterSamples) {
            $m = [regex]::Match($sample.Path, 'pid_(\d+)')
            if (-not $m.Success) { continue }
            $procId = [int]$m.Groups[1].Value
            # У процесса бывает несколько экземпляров (phys_0, phys_1) — суммируем.
            $mib = [int]([double]$sample.CookedValue / 1MB)
            if ($result.ContainsKey($procId)) { $result[$procId] += $mib } else { $result[$procId] = $mib }
        }
    } catch { }
    $result
}

function Format-OwnerMemory {
    param($App)
    if ($App.MemKnown) { return ("{0} MiB" -f $App.UsedMiB) }
    'память не отдана'
}

function Get-GpuOwnerReport {
    <#
        Возвращает вердикт по владельцам GPU.

        HeavyMiB      — с какого объёма VRAM процесс считается тяжёлым, даже
                        если его имя ни о чём не говорит.
        OrphanMiB     — с какого объёма НЕ ОТНЕСЁННОЙ к процессам VRAM считаем,
                        что освобождение не отработало.
        HoldActive    — активен ли HOST_SAFE_HOLD: при нём рендеров быть не должно.
        MemoryUsedMiB — общая занятая память карты из --query-gpu.
        MemoryTotalMiB — объём карты; позволяет отличить «часть занята неизвестно
                        чем» от «карта занята неизвестно чем целиком».
        CounterMemory — @{ pid = MiB } от Get-GpuProcessMemoryMiB: подставляется
                        там, где nvidia-smi не отдал used_memory.
        LivePids      — идентификаторы существующих процессов. Если задан,
                        владельцы, которых уже нет в системе, помечаются
                        отдельно: это незакрытые контексты, и именно они
                        объясняют занятую память без живого владельца.
                        Пустой список означает «не проверяли».

        Проверяются два независимых дефекта:
          1. сколько тяжёлых владельцев на карте (правило ONE HEAVY GPU OWNER);
          2. сходится ли занятая память с суммой по процессам.
        Второй считается ВСЕГДА, а не только когда владельцев нет: именно так
        выглядит и неотработавшая очистка, и память, которую не за кем закрепить.
    #>
    param(
        [object[]] $Apps = @(),
        [int] $MemoryUsedMiB = 0,
        [int] $MemoryTotalMiB = 0,
        [bool] $HoldActive = $false,
        [int] $HeavyMiB = 2048,
        [int] $OrphanMiB = 2048,
        [hashtable] $CounterMemory = @{},
        [int[]] $LivePids = @()
    )

    $checkLive = (@($LivePids).Count -gt 0)

    $apps = @($Apps | Where-Object { $_ })
    $classified = @()
    foreach ($a in $apps) {
        $used = [int]$a.UsedMiB
        $known = [bool]$a.MemKnown
        $source = if ($known) { 'nvidia-smi' } else { '' }

        # nvidia-smi под WDDM молчит про used_memory — добираем счётчиками.
        if (-not $known -and $CounterMemory -and $CounterMemory.ContainsKey([int]$a.Pid)) {
            $used = [int]$CounterMemory[[int]$a.Pid]
            $known = $true
            $source = 'perf-counter'
        }

        # Процесс, которого уже нет, но который nvidia-smi всё ещё перечисляет —
        # незакрытый контекст: память за ним числится, а освобождать её некому.
        $isDead = $checkLive -and ($LivePids -notcontains [int]$a.Pid)

        $isDesktop = $script:GpuDesktopProcesses -contains $a.Name
        $isRender  = Test-GpuRenderProcess -Name $a.Name -Path $a.Path
        $isHeavy   = (-not $isDead) -and (-not $isDesktop) -and ($isRender -or ($known -and $used -ge $HeavyMiB))
        $class = if ($isDead) { 'dead' } elseif ($isHeavy) { 'heavy' } elseif ($isDesktop) { 'desktop' } else { 'other' }

        $classified += [pscustomobject]@{
            Pid = $a.Pid; Path = $a.Path; Name = $a.Name
            UsedMiB = $used; MemKnown = $known; MemSource = $source; Class = $class
        }
    }

    $heavy = @($classified | Where-Object Class -eq 'heavy')
    $heavyMib = 0
    foreach ($h in $heavy) { if ($h.MemKnown) { $heavyMib += $h.UsedMiB } }

    # Несколько процессов с одним именем — почти всегда осиротевшие копии
    # прошлого прогона, а не осознанный параллелизм.
    $dupes = @($heavy | Group-Object Name | Where-Object { $_.Count -gt 1 })

    # ---- 1. Владельцы -----------------------------------------------------
    $ownerStatus = 'PASS'
    $ownerEvidence = ''
    $ownerNext = ''

    if ($heavy.Count -ge 2) {
        $ownerStatus = 'FAIL'
        $ownerEvidence = ("нарушено ONE HEAVY GPU OWNER: тяжёлых владельцев {0} ({1})" -f `
                          $heavy.Count, (($heavy | ForEach-Object { "{0}:{1}" -f $_.Name, $_.Pid }) -join ', '))
        if ($heavyMib -gt 0) { $ownerEvidence += (", суммарно {0} MiB" -f $heavyMib) }
        if ($dupes.Count -gt 0) {
            $ownerEvidence += ("; несколько копий одного процесса: {0}" -f (($dupes | ForEach-Object { $_.Name }) -join ', '))
        }
        $ownerNext = 'найти лишнего владельца и закрыть его штатно; конкурирующие рендеры делят VRAM и питание'
    } elseif ($heavy.Count -eq 1 -and $HoldActive) {
        $ownerStatus = 'WARN'
        $ownerEvidence = ("при активном hold на GPU работает {0} (pid {1}, {2})" -f `
                          $heavy[0].Name, $heavy[0].Pid, (Format-OwnerMemory -App $heavy[0]))
        $ownerNext = 'при hold рендеров быть не должно — проверить, кто и чем запустил задачу'
    } elseif ($heavy.Count -eq 1) {
        $ownerEvidence = ("один тяжёлый владелец: {0} (pid {1}, {2})" -f `
                          $heavy[0].Name, $heavy[0].Pid, (Format-OwnerMemory -App $heavy[0]))
    } else {
        $ownerEvidence = ("тяжёлых владельцев GPU нет, занято {0} MiB" -f $MemoryUsedMiB)
    }

    $dead = @($classified | Where-Object Class -eq 'dead')

    # ---- 2. Сходится ли память -------------------------------------------
    $withMem = @($classified | Where-Object MemKnown)
    $attributed = 0
    foreach ($c in $withMem) { $attributed += $c.UsedMiB }
    $unattributed = [math]::Max($MemoryUsedMiB - $attributed, 0)

    $attribution = if ($classified.Count -eq 0) { 'measured' }
                   elseif ($withMem.Count -eq $classified.Count) { 'measured' }
                   elseif ($withMem.Count -gt 0) { 'partial' }
                   else { 'not_measured' }

    $attrStatus = 'PASS'
    $attrEvidence = ''
    $attrNext = ''
    $orphan = 0

    if ($unattributed -ge $OrphanMiB) {
        $orphan = $unattributed
        # Занята половина карты и больше, а владельца нет — тяжёлый маршрут
        # физически не пройдёт, это не предупреждение, а отказ.
        $attrStatus = if ($MemoryTotalMiB -gt 0 -and $unattributed -ge [int]($MemoryTotalMiB / 2)) { 'FAIL' } else { 'WARN' }

        if ($attribution -eq 'not_measured') {
            $attrEvidence = ("занято {0} MiB, но владельца установить нельзя: nvidia-smi не отдал used_memory ни по одному из {1} процессов" -f `
                             $MemoryUsedMiB, $classified.Count)
            $attrNext = 'per-process VRAM под WDDM nvidia-smi не отдаёт — снять счётчиками Windows (Get-GpuProcessMemoryMiB) и сверить сумму с занятой памятью; расхождение означает, что освобождение после рендера не отработало'
        } else {
            $attrEvidence = ("занято {0} MiB, по процессам отнесено {1} MiB, не отнесено {2} MiB" -f `
                             $MemoryUsedMiB, $attributed, $unattributed)
            $attrNext = 'освобождение VRAM после рендера не отработало: проверить зависшие процессы и post-render cleanup'
        }
        if ($attribution -eq 'partial') {
            $attrEvidence += ("; память известна только для {0} из {1} процессов" -f $withMem.Count, $classified.Count)
        }
    }

    # Мёртвые владельцы — отдельная и куда более определённая улика, чем просто
    # разрыв в цифрах: они объясняют, ПОЧЕМУ память ничья.
    if ($dead.Count -gt 0) {
        $attrStatus = 'FAIL'
        $deadNames = (($dead | Select-Object -First 5 | ForEach-Object { "{0}:{1}" -f $_.Name, $_.Pid }) -join ', ')
        # Формулировка без согласования по числу: «1 процессов» в отчёте,
        # который читают глазами при инциденте, выглядит как ошибка данных.
        $attrEvidence = (@($attrEvidence, ("в списке nvidia-smi есть процессы, которых больше нет в системе — {0} шт. ({1}): контексты GPU не закрыты" -f $dead.Count, $deadNames)) |
                         Where-Object { $_ }) -join '; '
        $attrNext = 'память за завершившимися процессами драйвер не отдаст сам: освободить штатным механизмом студии, иначе только перезагрузка'
    }

    # ---- Свести -----------------------------------------------------------
    $rank = @{ 'PASS' = 0; 'WARN' = 1; 'FAIL' = 2 }
    $status = if ($rank[$attrStatus] -gt $rank[$ownerStatus]) { $attrStatus } else { $ownerStatus }

    $evidence = (@($ownerEvidence, $attrEvidence) | Where-Object { $_ }) -join '; '
    $next     = (@($ownerNext, $attrNext) | Where-Object { $_ }) -join '; '

    [pscustomobject]@{
        Apps            = @($classified)
        HeavyOwners     = @($heavy)
        HeavyCount      = $heavy.Count
        DeadOwners      = @($dead)
        DeadCount       = $dead.Count
        LiveChecked     = $checkLive
        HeavyUsedMiB    = $heavyMib
        AttributedMiB   = $attributed
        UnattributedMiB = $unattributed
        Attribution     = $attribution
        OrphanVramMiB   = $orphan
        Status          = $status
        Evidence        = $evidence
        NextAction      = $next
    }
}
