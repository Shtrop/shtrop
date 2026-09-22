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

        $mem = 0
        if ($memText -match '([\d\.]+)') { $mem = [int][double]$Matches[1] }
        if ($memText -match '(?i)\[N/A\]') { $mem = 0 }

        $apps += [pscustomobject]@{
            Pid      = [int]$pidText
            Path     = $nameText
            Name     = (Split-Path $nameText -Leaf)
            UsedMiB  = $mem
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

function Get-GpuOwnerReport {
    <#
        Возвращает вердикт по владельцам GPU.

        HeavyMiB     — с какого объёма VRAM процесс считается тяжёлым, даже
                       если его имя ни о чём не говорит.
        OrphanMiB    — с какого объёма занятой VRAM без тяжёлых владельцев
                       считаем, что освобождение не отработало.
        HoldActive   — активен ли HOST_SAFE_HOLD: при нём рендеров быть не должно.
        MemoryUsedMiB — общая занятая память карты из --query-gpu.
    #>
    param(
        [object[]] $Apps = @(),
        [int] $MemoryUsedMiB = 0,
        [bool] $HoldActive = $false,
        [int] $HeavyMiB = 2048,
        [int] $OrphanMiB = 2048
    )

    $apps = @($Apps | Where-Object { $_ })
    $classified = @()
    foreach ($a in $apps) {
        $isDesktop = $script:GpuDesktopProcesses -contains $a.Name
        $isRender  = Test-GpuRenderProcess -Name $a.Name -Path $a.Path
        $isHeavy   = (-not $isDesktop) -and ($isRender -or $a.UsedMiB -ge $HeavyMiB)
        $class = if ($isHeavy) { 'heavy' } elseif ($isDesktop) { 'desktop' } else { 'other' }
        $classified += [pscustomobject]@{
            Pid = $a.Pid; Path = $a.Path; Name = $a.Name; UsedMiB = $a.UsedMiB; Class = $class
        }
    }

    $heavy = @($classified | Where-Object Class -eq 'heavy')
    $heavyMib = 0
    foreach ($h in $heavy) { $heavyMib += $h.UsedMiB }

    # Несколько процессов с одним именем — почти всегда осиротевшие копии
    # прошлого прогона, а не осознанный параллелизм.
    $dupes = @($heavy | Group-Object Name | Where-Object { $_.Count -gt 1 })

    $status = 'PASS'
    $evidence = ''
    $next = ''
    $orphan = 0

    if ($heavy.Count -ge 2) {
        $status = 'FAIL'
        $evidence = ("нарушено ONE HEAVY GPU OWNER: тяжёлых владельцев {0} ({1}), суммарно {2} MiB" -f `
                     $heavy.Count, (($heavy | ForEach-Object { "{0}:{1}" -f $_.Name, $_.Pid }) -join ', '), $heavyMib)
        if ($dupes.Count -gt 0) {
            $evidence += ("; несколько копий одного процесса: {0}" -f (($dupes | ForEach-Object { $_.Name }) -join ', '))
        }
        $next = 'найти лишнего владельца и закрыть его штатно; конкурирующие рендеры делят VRAM и питание'
    } elseif ($heavy.Count -eq 1 -and $HoldActive) {
        $status = 'WARN'
        $evidence = ("при активном hold на GPU работает {0} (pid {1}, {2} MiB)" -f $heavy[0].Name, $heavy[0].Pid, $heavy[0].UsedMiB)
        $next = 'при hold рендеров быть не должно — проверить, кто и чем запустил задачу'
    } elseif ($heavy.Count -eq 1) {
        $status = 'PASS'
        $evidence = ("один тяжёлый владелец: {0} (pid {1}, {2} MiB)" -f $heavy[0].Name, $heavy[0].Pid, $heavy[0].UsedMiB)
    } else {
        $freeStanding = $MemoryUsedMiB
        foreach ($c in $classified) { $freeStanding -= $c.UsedMiB }
        if ($MemoryUsedMiB -ge $OrphanMiB) {
            $status = 'WARN'
            $orphan = [math]::Max($freeStanding, 0)
            $evidence = ("тяжёлых задач нет, но VRAM занята {0} MiB (не отнесено к процессам: {1} MiB)" -f $MemoryUsedMiB, $orphan)
            $next = 'похоже, освобождение VRAM после рендера не отработало: проверить зависшие процессы и post-render cleanup'
        } else {
            $status = 'PASS'
            $evidence = ("тяжёлых владельцев GPU нет, занято {0} MiB" -f $MemoryUsedMiB)
        }
    }

    [pscustomobject]@{
        Apps          = @($classified)
        HeavyOwners   = @($heavy)
        HeavyCount    = $heavy.Count
        HeavyUsedMiB  = $heavyMib
        OrphanVramMiB = $orphan
        Status        = $status
        Evidence      = $evidence
        NextAction    = $next
    }
}
