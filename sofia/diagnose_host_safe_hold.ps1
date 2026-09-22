<#
.SYNOPSIS
    Read-only диагностика инцидента GOVERNOR [CRITICAL] host_unstable_safe_hold
    (Kernel-Power 41 -> HOST_SAFE_HOLD.flag, конвейер остановлен).

.DESCRIPTION
    Скрипт НИЧЕГО не изменяет в боевом дереве Sofia AI Studio:
      - не удаляет и не трогает HOST_SAFE_HOLD.flag и другие control_flags;
      - не перезапускает сервисы, не трогает Task Scheduler, не делает reboot;
      - не меняет publishing state и не снимает FROZEN;
      - пишет отчёт ТОЛЬКО в -OutDir (по умолчанию вне дерева студии).

    Собирает доказательства по пяти осям:
      1. Частота и тайминг Kernel-Power 41 / 6008 / BugCheck 1001.
      2. Состояние governor, control_flags и канонических state-файлов.
      3. GPU: температура, питание, throttle reasons, активные процессы.
      4. Корреляция событий 41 с GPU-рендерами (по времени записи артефактов и логов).
      5. Живость сервисов студии (HTTP-проба с коротким timeout).

.PARAMETER SofiaRoot
    Корень боевого дерева. По умолчанию D:\AI_CONTENT\Sofia.

.PARAMETER Days
    Глубина анализа журнала событий в днях. По умолчанию 7.

.PARAMETER OutDir
    Каталог для отчёта. По умолчанию %TEMP%\sofia_safehold_<timestamp>.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\diagnose_host_safe_hold.ps1

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\diagnose_host_safe_hold.ps1 -Days 14

.NOTES
    Журнал System для Kernel-Power может требовать прав администратора или
    членства в группе "Event Log Readers". Если секция 1 вернёт ACCESS_DENIED,
    перезапустите PowerShell от имени администратора — это единственное,
    для чего нужны повышенные права.
#>

[CmdletBinding()]
param(
    [string] $SofiaRoot = 'D:\AI_CONTENT\Sofia',
    [int]    $Days      = 7,
    [string] $OutDir    = (Join-Path ([System.IO.Path]::GetTempPath()) ("sofia_safehold_{0}" -f (Get-Date -Format 'yyyyMMdd_HHmmss')))
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


$script:Report = [ordered]@{
    generated_at   = (Get-Date).ToString('o')
    host           = $env:COMPUTERNAME
    sofia_root     = $SofiaRoot
    window_days    = $Days
    sections       = [ordered]@{}
    findings       = @()
    verdict        = 'NOT_MEASURED'
}

function Write-Head {
    param([string]$Text)
    Write-Host ''
    Write-Host ('=' * 78) -ForegroundColor DarkCyan
    Write-Host "  $Text" -ForegroundColor Cyan
    Write-Host ('=' * 78) -ForegroundColor DarkCyan
}

function Add-Finding {
    param(
        [ValidateSet('PASS','WARN','FAIL','BLOCKED','NOT_MEASURED')][string]$Status,
        [string]$Component,
        [string]$Evidence,
        [string]$NextAction = ''
    )
    $script:Report.findings += [ordered]@{
        component   = $Component
        status      = $Status
        evidence    = $Evidence
        next_action = $NextAction
    }
    $color = switch ($Status) {
        'PASS'    { 'Green' }
        'WARN'    { 'Yellow' }
        'FAIL'    { 'Red' }
        'BLOCKED' { 'Magenta' }
        default   { 'DarkGray' }
    }
    Write-Host ("  [{0,-12}] {1}: {2}" -f $Status, $Component, $Evidence) -ForegroundColor $color
}

function Invoke-Section {
    param([string]$Name, [scriptblock]$Body)
    try {
        & $Body
    } catch {
        Add-Finding -Status 'NOT_MEASURED' -Component $Name `
                    -Evidence ("сбор не выполнен: {0}" -f $_.Exception.Message) `
                    -NextAction 'проверить права/пути и перезапустить секцию вручную'
    }
}

function Invoke-Probe {
    # Секция состоит из независимых зондов, и один сбойный не должен уносить
    # остальные: отказ WMI иначе прячет и ИБП, и схему питания, и планировщик
    # под одной строкой NOT_MEASURED — ровно тогда, когда они нужнее всего.
    param([string]$Name, [scriptblock]$Body)
    try {
        & $Body
    } catch {
        Add-Finding -Status 'NOT_MEASURED' -Component $Name `
                    -Evidence ("зонд не выполнен: {0}" -f $_.Exception.Message) `
                    -NextAction 'остальные проверки секции не пострадали — разбирать только этот источник'
    }
}

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$transcript = Join-Path $OutDir 'console.log'
try { Start-Transcript -Path $transcript -Force | Out-Null } catch { }

Write-Host ''
Write-Host 'Sofia AI Studio — диагностика host_unstable_safe_hold (READ-ONLY)' -ForegroundColor White
Write-Host ("Корень студии : {0}" -f $SofiaRoot)
Write-Host ("Окно анализа  : {0} дн." -f $Days)
Write-Host ("Отчёт         : {0}" -f $OutDir)
Write-Host 'Скрипт не удаляет и не изменяет ни одного файла студии.' -ForegroundColor DarkGray

$since = (Get-Date).AddDays(-$Days)

# ---------------------------------------------------------------------------
# 1. Kernel-Power 41 и родственные события
# ---------------------------------------------------------------------------
Write-Head '1/6  Журнал Windows: Kernel-Power 41 / 6008 / BugCheck 1001'
$gpuLib = Join-Path $PSScriptRoot 'lib_gpu_owners.ps1'
$script:HasGpuLib = Test-Path $gpuLib
if ($script:HasGpuLib) { . $gpuLib }

$taskLib = Join-Path $PSScriptRoot 'lib_task_results.ps1'
$script:HasTaskLib = Test-Path $taskLib
if ($script:HasTaskLib) { . $taskLib }

Invoke-Section 'kernel_power' {
    if (-not (Test-SystemLogReadable)) {
        Add-Finding -Status 'BLOCKED' -Component 'Kernel-Power 41' `
                    -Evidence 'журнал System недоступен' `
                    -NextAction 'перезапустить PowerShell от имени администратора'
        $script:Report.sections['kernel_power'] = 'ACCESS_DENIED'
        return
    }

    $events = Get-SystemEvents -Filter @{
        LogName   = 'System'
        Id        = 41, 6008, 1001
        StartTime = $since
    }
    if ($events.Count -eq 0) {
        Add-Finding -Status 'PASS' -Component 'Kernel-Power 41' `
                    -Evidence ("за {0} дн. событий 41/6008/1001 нет" -f $Days) `
                    -NextAction 'причина safe hold вне журнала System — смотреть governor incidents'
        $script:Report.sections['kernel_power'] = @()
        return
    }

    $rows = $events | ForEach-Object {
        [ordered]@{
            time     = $_.TimeCreated.ToString('o')
            id       = $_.Id
            provider = $_.ProviderName
            level    = $_.LevelDisplayName
            message  = ($_.Message -replace '\s+', ' ').Trim()
        }
    }
    $script:Report.sections['kernel_power'] = @($rows)

    $e41 = @($events | Where-Object Id -eq 41 | Sort-Object TimeCreated)
    $e1001 = @($events | Where-Object Id -eq 1001)

    Write-Host ''
    $events | Sort-Object TimeCreated -Descending |
        Select-Object @{n='Время';e={$_.TimeCreated}}, Id,
                      @{n='Источник';e={$_.ProviderName}} |
        Format-Table -AutoSize | Out-String | Write-Host

    if ($e41.Count -eq 0) {
        Add-Finding -Status 'PASS' -Component 'Kernel-Power 41' `
                    -Evidence ("за {0} дн. событий 41 нет" -f $Days)
    } else {
        $first = $e41[0].TimeCreated
        $last  = $e41[-1].TimeCreated
        $spanH = [math]::Max(1, [int]((New-TimeSpan -Start $first -End $last).TotalHours))
        $perDay = [math]::Round($e41.Count / [math]::Max(1, $Days), 2)

        # межсобытийные интервалы — ищем регулярность (признак воспроизводимого триггера)
        $gaps = @()
        for ($i = 1; $i -lt $e41.Count; $i++) {
            $gaps += [math]::Round((New-TimeSpan -Start $e41[$i-1].TimeCreated -End $e41[$i].TimeCreated).TotalHours, 2)
        }
        $script:Report.sections['kernel_power_stats'] = [ordered]@{
            count_41        = $e41.Count
            first           = $first.ToString('o')
            last            = $last.ToString('o')
            span_hours      = $spanH
            per_day         = $perDay
            gaps_hours      = $gaps
            bugcheck_count  = $e1001.Count
        }

        $status = if ($e41.Count -ge 3) { 'FAIL' } elseif ($e41.Count -ge 1) { 'WARN' } else { 'PASS' }
        Add-Finding -Status $status -Component 'Kernel-Power 41' `
                    -Evidence ("{0} событий за {1} дн. ({2}/сут), последнее {3}" -f $e41.Count, $Days, $perDay, $last) `
                    -NextAction 'сопоставить время событий с GPU-рендерами (секция 4)'

        if ($gaps.Count -ge 2) {
            Write-Host ("  Интервалы между событиями 41 (ч): {0}" -f ($gaps -join ', ')) -ForegroundColor DarkGray
        }

        if ($e1001.Count -gt 0) {
            Add-Finding -Status 'FAIL' -Component 'BugCheck 1001' `
                        -Evidence ("{0} записей BSOD — есть код остановки, root cause определим точно" -f $e1001.Count) `
                        -NextAction 'разобрать минидамп (секция 2) — это сильнее любой гипотезы про питание'
        } else {
            Add-Finding -Status 'WARN' -Component 'BugCheck 1001' `
                        -Evidence 'записей BSOD нет — ресет без кода остановки' `
                        -NextAction 'типично для потери питания/железного ресета, а не для краха драйвера'
        }
    }
}

# ---------------------------------------------------------------------------
# 2. Минидампы
# ---------------------------------------------------------------------------
Write-Head '2/6  Минидампы BSOD'
Invoke-Section 'minidumps' {
    $dumpDirs = @("$env:SystemRoot\Minidump", "$env:SystemRoot\MEMORY.DMP")
    $dumps = @()
    foreach ($d in $dumpDirs) {
        if (Test-Path $d) {
            $dumps += Get-ChildItem $d -ErrorAction SilentlyContinue |
                      Where-Object { $_.LastWriteTime -ge $since }
        }
    }
    $script:Report.sections['minidumps'] = @($dumps | ForEach-Object {
        [ordered]@{ path = $_.FullName; modified = $_.LastWriteTime.ToString('o'); size = $_.Length }
    })

    if ($dumps.Count -eq 0) {
        Add-Finding -Status 'WARN' -Component 'Minidump' `
                    -Evidence ("свежих дампов за {0} дн. нет" -f $Days) `
                    -NextAction 'согласуется с внезапной потерей питания: ОС не успела записать дамп'
    } else {
        $dumps | Sort-Object LastWriteTime -Descending |
            Select-Object LastWriteTime, Length, FullName | Format-Table -AutoSize |
            Out-String | Write-Host
        Add-Finding -Status 'FAIL' -Component 'Minidump' `
                    -Evidence ("{0} дампов, последний {1}" -f $dumps.Count, ($dumps | Sort-Object LastWriteTime -Desc)[0].LastWriteTime) `
                    -NextAction 'открыть в WinDbg/BlueScreenView: !analyze -v даст виновный драйвер'
    }
}

# ---------------------------------------------------------------------------
# 3. Флаги, governor и канонические state-файлы
# ---------------------------------------------------------------------------
Write-Head '3/6  control_flags, governor, канонический state (чтение, без изменений)'
Invoke-Section 'studio_state' {
    if (-not (Test-Path $SofiaRoot)) {
        Add-Finding -Status 'BLOCKED' -Component 'Sofia root' `
                    -Evidence ("путь не найден: {0}" -f $SofiaRoot) `
                    -NextAction 'указать корректный -SofiaRoot'
        return
    }

    $flagDir = Join-Path $SofiaRoot 'control_flags'
    $flags = @()
    if (Test-Path $flagDir) {
        $flags = Get-ChildItem $flagDir -File -ErrorAction SilentlyContinue |
                 Sort-Object LastWriteTime -Descending
        $flags | Select-Object Name, LastWriteTime, Length | Format-Table -AutoSize |
            Out-String | Write-Host
    }
    $script:Report.sections['control_flags'] = @($flags | ForEach-Object {
        [ordered]@{ name = $_.Name; modified = $_.LastWriteTime.ToString('o'); size = $_.Length }
    })

    $hold = Join-Path $flagDir 'HOST_SAFE_HOLD.flag'
    if (Test-Path $hold) {
        $holdItem = Get-Item $hold
        $body = (Get-Content $hold -Raw -ErrorAction SilentlyContinue)
        $script:Report.sections['host_safe_hold'] = [ordered]@{
            path     = $hold
            modified = $holdItem.LastWriteTime.ToString('o')
            content  = $body
        }
        Add-Finding -Status 'FAIL' -Component 'HOST_SAFE_HOLD.flag' `
                    -Evidence ("флаг активен, выставлен {0}" -f $holdItem.LastWriteTime) `
                    -NextAction 'НЕ снимать до закрытия root cause — это штатная fail-closed защита'
        if ($body) {
            Write-Host '  --- содержимое флага ---' -ForegroundColor DarkGray
            Write-Host $body
        }
    } else {
        Add-Finding -Status 'PASS' -Component 'HOST_SAFE_HOLD.flag' `
                    -Evidence 'флаг отсутствует — hold снят или не выставлялся'
        $script:Report.sections['host_safe_hold'] = $null
    }

    # governor state / incidents — только чтение свежих файлов
    $govDir = Join-Path $SofiaRoot 'governor'
    if (Test-Path $govDir) {
        $gov = Get-ChildItem $govDir -Recurse -File -ErrorAction SilentlyContinue |
               Sort-Object LastWriteTime -Descending | Select-Object -First 15
        $gov | Select-Object LastWriteTime, @{n='Path';e={$_.FullName.Replace($SofiaRoot,'.')}} |
            Format-Table -AutoSize | Out-String | Write-Host
        $script:Report.sections['governor_recent'] = @($gov | ForEach-Object {
            [ordered]@{ path = $_.FullName; modified = $_.LastWriteTime.ToString('o') }
        })
        Add-Finding -Status 'PASS' -Component 'governor state' `
                    -Evidence ("{0} свежих файлов, последний {1}" -f $gov.Count, ($gov | Select-Object -First 1).LastWriteTime) `
                    -NextAction 'открыть последний incident-файл: в нём порог, который сработал'
    } else {
        Add-Finding -Status 'NOT_MEASURED' -Component 'governor state' `
                    -Evidence 'каталог governor не найден'
    }

    # канонические источники истины (только чтение)
    $canon = @(
        'control_flags\PUBLISHING_STATE.json',
        'CODEX_FINAL_KNOWN_GOOD_STATE.json',
        'agent_team_v2\state\SOFIA_AGENT_TEAM_RUNTIME_STATUS.json',
        'agent_team_v2\state\company_state.json'
    )
    $canonRows = @()
    foreach ($rel in $canon) {
        $p = Join-Path $SofiaRoot $rel
        if (Test-Path $p) {
            $it = Get-Item $p
            $age = [math]::Round((New-TimeSpan -Start $it.LastWriteTime -End (Get-Date)).TotalHours, 1)
            $canonRows += [ordered]@{ file = $rel; modified = $it.LastWriteTime.ToString('o'); age_hours = $age }
            $st = if ($age -gt 24) { 'WARN' } else { 'PASS' }
            Add-Finding -Status $st -Component $rel `
                        -Evidence ("обновлён {0} ({1} ч назад)" -f $it.LastWriteTime, $age) `
                        -NextAction $(if ($age -gt 24) { 'файл старше суток — считать историческим снимком' } else { '' })
        } else {
            $canonRows += [ordered]@{ file = $rel; modified = $null; age_hours = $null }
            Add-Finding -Status 'NOT_MEASURED' -Component $rel -Evidence 'файл не найден'
        }
    }
    $script:Report.sections['canonical_state'] = $canonRows

    # publishing state — показать, но не менять
    $ps = Join-Path $SofiaRoot 'control_flags\PUBLISHING_STATE.json'
    if (Test-Path $ps) {
        Write-Host '  --- PUBLISHING_STATE.json ---' -ForegroundColor DarkGray
        Get-Content $ps -Raw | Write-Host
    }

    # активные локи
    $lockDirs = @('state', 'locks', 'control_flags') | ForEach-Object { Join-Path $SofiaRoot $_ }
    $locks = @()
    foreach ($ld in $lockDirs) {
        if (Test-Path $ld) {
            $locks += Get-ChildItem $ld -Recurse -File -Filter '*.lock' -ErrorAction SilentlyContinue
        }
    }
    $script:Report.sections['locks'] = @($locks | ForEach-Object {
        [ordered]@{ path = $_.FullName; modified = $_.LastWriteTime.ToString('o') }
    })
    if ($locks.Count -gt 0) {
        $locks | Select-Object Name, LastWriteTime, FullName | Format-Table -AutoSize | Out-String | Write-Host
        Add-Finding -Status 'WARN' -Component 'locks' `
                    -Evidence ("{0} lock-файлов; после жёсткого ресета вероятны stale-локи" -f $locks.Count) `
                    -NextAction 'НЕ чистить вручную — использовать штатный stale-lock механизм'
    } else {
        Add-Finding -Status 'PASS' -Component 'locks' -Evidence 'активных lock-файлов не найдено'
    }

    # git status боевого дерева — чтобы не потерять правки владельца
    Push-Location $SofiaRoot
    try {
        $git = & git status --short --branch 2>&1
        $script:Report.sections['git_status'] = ($git | Out-String).Trim()
        Write-Host '  --- git status --short --branch ---' -ForegroundColor DarkGray
        $git | Write-Host
        $dirty = @($git | Where-Object { $_ -notmatch '^##' -and $_.Trim() })
        if ($dirty.Count -gt 0) {
            Add-Finding -Status 'WARN' -Component 'git worktree' `
                        -Evidence ("{0} изменённых путей в боевом дереве" -f $dirty.Count) `
                        -NextAction 'сохранить правки владельца до любого ремонта'
        } else {
            Add-Finding -Status 'PASS' -Component 'git worktree' -Evidence 'дерево чистое'
        }
    } catch {
        Add-Finding -Status 'NOT_MEASURED' -Component 'git worktree' -Evidence 'git недоступен'
    } finally {
        Pop-Location
    }
}

# ---------------------------------------------------------------------------
# 4. GPU и корреляция событий 41 с рендерами
# ---------------------------------------------------------------------------
Write-Head '4/6  GPU: питание, температура, throttle + корреляция с событиями 41'
Invoke-Section 'gpu' {
    $nvsmi = Get-Command nvidia-smi -ErrorAction SilentlyContinue
    if (-not $nvsmi) {
        Add-Finding -Status 'NOT_MEASURED' -Component 'GPU' -Evidence 'nvidia-smi не найден в PATH'
    } else {
        $memUsed = 0
        $memTotal = 0
        # Без -i вывод многокарточной системы — несколько строк, а Out-String
        # склеивает их в одну: Split(',') тогда смешивает поля разных карт, и
        # memory.total превращается в мусор вроде 326075090.
        $q = & nvidia-smi -i 0 --query-gpu='name,temperature.gpu,power.draw,power.limit,power.max_limit,clocks.sm,utilization.gpu,memory.used,memory.total' --format=csv,noheader 2>&1
        $script:Report.sections['gpu_query'] = ($q | Out-String).Trim()
        Write-Host ("  {0}" -f ($q | Out-String).Trim())

        $fields = ($q | Out-String).Split(',') | ForEach-Object { $_.Trim() }
        if ($fields.Count -ge 5) {
            $temp  = [double]($fields[1] -replace '[^\d\.]', '')
            $draw  = [double]($fields[2] -replace '[^\d\.]', '')
            $limit = [double]($fields[3] -replace '[^\d\.]', '')
            $maxL  = [double]($fields[4] -replace '[^\d\.]', '')
            if ($fields.Count -ge 8) { $memUsed = [int]([double]($fields[7] -replace '[^\d\.]', '')) }
            if ($fields.Count -ge 9) { $memTotal = [int]([double]($fields[8] -replace '[^\d\.]', '')) }
            $tSt = if ($temp -ge 83) { 'FAIL' } elseif ($temp -ge 75) { 'WARN' } else { 'PASS' }
            Add-Finding -Status $tSt -Component 'GPU температура' -Evidence ("{0} C" -f $temp)
            if ($limit -ge $maxL) {
                Add-Finding -Status 'WARN' -Component 'GPU power limit' `
                            -Evidence ("лимит {0} W = максимум платы {1} W; транзиентные пики ничем не ограничены" -f $limit, $maxL) `
                            -NextAction ("кандидат на минимальный обратимый fix: nvidia-smi -pl {0}" -f [int]($maxL * 0.8))
            } else {
                Add-Finding -Status 'PASS' -Component 'GPU power limit' -Evidence ("{0} W из {1} W" -f $limit, $maxL)
            }
        }

        $thr = & nvidia-smi -i 0 -q -d PERFORMANCE 2>&1
        $script:Report.sections['gpu_throttle'] = ($thr | Out-String).Trim()
        $active = @($thr | Select-String -Pattern ':\s*Active' )
        if ($active.Count -gt 0) {
            Add-Finding -Status 'WARN' -Component 'GPU throttle reasons' `
                        -Evidence ("активных причин throttle: {0}" -f $active.Count) `
                        -NextAction 'см. gpu_throttle в отчёте: HW Power Brake / Thermal указывают на питание или охлаждение'
        } else {
            Add-Finding -Status 'PASS' -Component 'GPU throttle reasons' -Evidence 'активных причин нет'
        }

        # «На GPU есть задачи» — не вывод. Важно, сколько тяжёлых владельцев и
        # не держится ли VRAM без владельца вовсе: это разные дефекты.
        # -i 0 обязателен и здесь: иначе рендеры со второй карты считаются
        # владельцами первой, а её занятая память их не объясняет.
        $procs = & nvidia-smi -i 0 --query-compute-apps='pid,process_name,used_memory' --format=csv,noheader 2>&1
        $procText = ($procs | Out-String).Trim()
        $script:Report.sections['gpu_processes'] = $procText

        if ($script:HasGpuLib) {
            $holdActive = [bool]$script:Report.sections['host_safe_hold']
            $apps = ConvertFrom-NvidiaComputeApps -Text $procText

            # Под WDDM nvidia-smi не отдаёт used_memory, поэтому память берём
            # из счётчиков Windows. Без этого занятая VRAM остаётся ничьей.
            $counterMem = Get-GpuProcessMemoryMiB
            $script:Report.sections['gpu_process_counters'] = @($counterMem.Keys | ForEach-Object {
                [ordered]@{ pid = $_; used_mib = $counterMem[$_] }
            })

            # Процессы, которых уже нет: nvidia-smi перечисляет их, пока
            # драйвер держит контекст. Это самая определённая причина занятой
            # памяти без живого владельца.
            $livePids = @()
            try { $livePids = @(Get-Process -ErrorAction Stop | ForEach-Object { [int]$_.Id }) } catch { }

            # Повторный опрос карты уже ПОСЛЕ снимка процессов: рендер, честно
            # завершившийся между двумя шагами, из этого списка уйдёт, и в
            # «мёртвые» не попадёт. Останется только тот, чей контекст висит.
            $stillListed = $null
            if ($livePids.Count -gt 0) {
                $procText2 = (& nvidia-smi -i 0 --query-compute-apps='pid,process_name,used_memory' --format=csv,noheader 2>&1 | Out-String).Trim()
                # Сверка засчитывается ТОЛЬКО при успешном втором опросе.
                # Иначе ошибка nvidia-smi дала бы пустой список, а пустой
                # список означал бы «карта никого не числит» — и настоящий
                # висящий контекст молча превратился бы в PASS.
                if ($LASTEXITCODE -eq 0) {
                    $stillListed = @((ConvertFrom-NvidiaComputeApps -Text $procText2) | ForEach-Object { [int]$_.Pid })
                } else {
                    Write-Host '  повторный опрос GPU не удался — сверка по завершившимся процессам пропущена' -ForegroundColor DarkGray
                }
            }

            $own = Get-GpuOwnerReport -Apps $apps -MemoryUsedMiB $memUsed -MemoryTotalMiB $memTotal `
                                      -HoldActive $holdActive -CounterMemory $counterMem `
                                      -LivePids $livePids -StillListedPids $stillListed

            $script:Report.sections['gpu_owners'] = [ordered]@{
                heavy_count      = $own.HeavyCount
                dead_count       = $own.DeadCount
                stale_dropped    = $own.StaleCount
                live_checked     = $own.LiveChecked
                heavy_used_mib   = $own.HeavyUsedMiB
                attributed_mib   = $own.AttributedMiB
                unattributed_mib = $own.UnattributedMiB
                attribution      = $own.Attribution
                orphan_vram_mib  = $own.OrphanVramMiB
                memory_used_mib  = $memUsed
                memory_total_mib = $memTotal
                hold_active      = $holdActive
                apps             = @($own.Apps | ForEach-Object {
                    [ordered]@{
                        pid = $_.Pid; name = $_.Name; used_mib = $_.UsedMiB
                        mem_known = $_.MemKnown; mem_source = $_.MemSource; class = $_.Class
                    }
                })
            }

            if ($own.Apps.Count -gt 0) {
                Write-Host '  --- владельцы GPU ---' -ForegroundColor DarkGray
                foreach ($a in $own.Apps) {
                    $mem = if ($a.MemKnown) { "{0,7} MiB" -f $a.UsedMiB } else { '  не отдана' }
                    $src = if ($a.MemSource -eq 'perf-counter') { ' (счётчик)' } else { '' }
                    Write-Host ("    {0,-24} pid {1,-8} {2}{3}  [{4}]" -f $a.Name, $a.Pid, $mem, $src, $a.Class)
                }
                Write-Host ("    отнесено {0} MiB из занятых {1} MiB (не отнесено {2} MiB)" -f `
                            $own.AttributedMiB, $memUsed, $own.UnattributedMiB) -ForegroundColor DarkGray
            }

            Add-Finding -Status $own.Status -Component 'GPU owners' `
                        -Evidence $own.Evidence -NextAction $own.NextAction
        } else {
            # Библиотеки рядом нет — не отказываемся собирать доказательства.
            if ($procText) {
                Write-Host '  --- активные GPU-процессы ---' -ForegroundColor DarkGray
                $procs | Write-Host
                Add-Finding -Status 'WARN' -Component 'GPU processes' `
                            -Evidence 'на GPU есть активные задачи, lib_gpu_owners.ps1 рядом не найден' `
                            -NextAction 'скачать lib_gpu_owners.ps1 из того же каталога репозитория и повторить'
            } else {
                Add-Finding -Status 'PASS' -Component 'GPU processes' -Evidence 'активных GPU-задач нет (ожидаемо при hold)'
            }
        }
    }

    # Корреляция: были ли рендеры/логи в пределах +-20 минут до событий 41
    $kp = $script:Report.sections['kernel_power']
    if ($kp -is [array] -and $kp.Count -gt 0) {
        $watchDirs = @(
            (Join-Path $SofiaRoot 'generated'),
            (Join-Path $SofiaRoot 'video_ready'),
            (Join-Path $SofiaRoot 'logs'),
            'D:\Sofia_Logs\runner'
        ) | Where-Object { Test-Path $_ }

        $recent = @()
        foreach ($wd in $watchDirs) {
            $recent += Get-ChildItem $wd -Recurse -File -ErrorAction SilentlyContinue |
                       Where-Object { $_.LastWriteTime -ge $since }
        }

        $corr = @()
        foreach ($ev in ($kp | Where-Object { $_.id -eq 41 })) {
            $t = [datetime]::Parse($ev.time, [Globalization.CultureInfo]::InvariantCulture)
            $near = @($recent | Where-Object {
                $d = [math]::Abs((New-TimeSpan -Start $_.LastWriteTime -End $t).TotalMinutes)
                $d -le 20
            })
            $corr += [ordered]@{
                event_time      = $ev.time
                artifacts_20min = $near.Count
                sample          = @($near | Sort-Object LastWriteTime -Descending |
                                    Select-Object -First 5 |
                                    ForEach-Object { "{0}  {1}" -f $_.LastWriteTime.ToString('HH:mm:ss'), $_.FullName })
            }
        }
        $script:Report.sections['correlation_41_vs_render'] = $corr

        $hits = @($corr | Where-Object { $_.artifacts_20min -gt 0 })
        if ($corr.Count -gt 0) {
            Write-Host ''
            foreach ($c in $corr) {
                Write-Host ("  {0} -> артефактов в окне +-20 мин: {1}" -f $c.event_time, $c.artifacts_20min)
                foreach ($s in $c.sample) { Write-Host ("      {0}" -f $s) -ForegroundColor DarkGray }
            }
            if ($hits.Count -eq $corr.Count -and $corr.Count -gt 0) {
                Add-Finding -Status 'FAIL' -Component 'Корреляция 41 <-> GPU-нагрузка' `
                            -Evidence ("все {0} событий 41 совпали с активной работой пайплайна" -f $corr.Count) `
                            -NextAction 'сильная гипотеза: транзиенты питания под GPU-нагрузкой -> ограничить power limit и параллелизм'
            } elseif ($hits.Count -gt 0) {
                Add-Finding -Status 'WARN' -Component 'Корреляция 41 <-> GPU-нагрузка' `
                            -Evidence ("{0} из {1} событий совпали с активной работой" -f $hits.Count, $corr.Count) `
                            -NextAction 'частичная корреляция — проверить также питание/UPS и температуру'
            } else {
                Add-Finding -Status 'WARN' -Component 'Корреляция 41 <-> GPU-нагрузка' `
                            -Evidence 'события 41 произошли вне окон рендера' `
                            -NextAction 'GPU-гипотеза слабая: смотреть питание сети/UPS, PSU, драйверы чипсета'
            }
        }
    }
}

# ---------------------------------------------------------------------------
# 5. Сервисы студии (проба, без рестартов)
# ---------------------------------------------------------------------------
Write-Head '5/6  Сервисы студии (HTTP-проба, без перезапусков)'
Invoke-Section 'services' {
    $svc = [ordered]@{
        'ComfyUI'          = 'http://127.0.0.1:8188'
        'Ollama'           = 'http://127.0.0.1:11434'
        'n8n'              = 'http://127.0.0.1:5678'
        'Command Center'   = 'http://127.0.0.1:5680'
        'Production API'   = 'http://127.0.0.1:5681/api/production-state'
        'Dashboard v2'     = 'http://127.0.0.1:5682'
        'Banana Local'     = 'http://127.0.0.1:8899'
        'Paywall/webhook'  = 'http://127.0.0.1:9099'
        'OpenClaw Gateway' = 'http://127.0.0.1:18789'
    }
    $rows = @()
    foreach ($name in $svc.Keys) {
        $url = $svc[$name]
        $code = $null; $err = $null; $bodyHead = $null
        try {
            $r = Invoke-WebRequest -Uri $url -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
            $code = $r.StatusCode
            $bodyHead = ($r.Content | Out-String)
            if ($bodyHead.Length -gt 400) { $bodyHead = $bodyHead.Substring(0, 400) }
        } catch {
            if ($_.Exception.Response) { $code = [int]$_.Exception.Response.StatusCode }
            $err = $_.Exception.Message
        }
        $rows += [ordered]@{ service = $name; url = $url; http = $code; error = $err }
        $st = if ($code -ge 200 -and $code -lt 400) { 'PASS' }
              elseif ($code) { 'WARN' } else { 'FAIL' }
        $note = if ($code -eq 404) { 'порт жив, контракт endpoint устарел — не перезапускать из-за 404' } else { '' }
        Add-Finding -Status $st -Component ("сервис {0}" -f $name) `
                    -Evidence $(if ($code) { "HTTP $code" } else { "нет ответа: $err" }) -NextAction $note
        if ($name -eq 'Production API' -and $bodyHead) {
            $script:Report.sections['production_state_body'] = $bodyHead
            Write-Host '  --- /api/production-state (первые 400 симв.) ---' -ForegroundColor DarkGray
            Write-Host $bodyHead
        }
    }
    $script:Report.sections['services'] = $rows
}

# ---------------------------------------------------------------------------
# 6. Аптайм, питание, планировщик (read-only)
# ---------------------------------------------------------------------------
Write-Head '6/6  Аптайм, профиль питания, задачи Sofia (read-only)'
Invoke-Section 'host' {
  Invoke-Probe 'Uptime' {
    $os = Get-CimInstance Win32_OperatingSystem
    $up = (Get-Date) - $os.LastBootUpTime
    $script:Report.sections['uptime'] = [ordered]@{
        last_boot    = $os.LastBootUpTime.ToString('o')
        uptime_hours = [math]::Round($up.TotalHours, 1)
    }
    Add-Finding -Status $(if ($up.TotalHours -lt 12) { 'WARN' } else { 'PASS' }) `
                -Component 'Uptime' `
                -Evidence ("последняя загрузка {0} ({1} ч назад)" -f $os.LastBootUpTime, [math]::Round($up.TotalHours,1))
  }

  Invoke-Probe 'UPS/батарея' {
    $bat = Get-CimInstance Win32_Battery -ErrorAction SilentlyContinue
    $script:Report.sections['ups_battery'] = if ($bat) {
        @($bat | ForEach-Object { [ordered]@{ name = $_.Name; status = $_.Status; charge = $_.EstimatedChargeRemaining } })
    } else { $null }
    if ($bat) {
        Add-Finding -Status 'PASS' -Component 'UPS/батарея' -Evidence 'ИБП/батарея видны системе'
    } else {
        Add-Finding -Status 'WARN' -Component 'UPS/батарея' `
                    -Evidence 'ИБП системе не виден' `
                    -NextAction 'при подтверждённых событиях 41 без BSOD — ИБП закрывает класс причин целиком'
    }
  }

  Invoke-Probe 'Схема питания' {
    $scheme = (& powercfg /getactivescheme 2>&1 | Out-String).Trim()
    $script:Report.sections['power_scheme'] = $scheme
    Write-Host ("  {0}" -f $scheme)
  }

  Invoke-Probe 'Task Scheduler' {
    try {
        $tasks = Get-ScheduledTask -ErrorAction Stop |
                 Where-Object { $_.TaskName -match 'sofia|comfy|reel|render|govern' -or $_.TaskPath -match 'Sofia' }
        $trows = @($tasks | ForEach-Object {
            $info = $_ | Get-ScheduledTaskInfo -ErrorAction SilentlyContinue
            [ordered]@{
                name      = $_.TaskName
                path      = $_.TaskPath
                state     = "$($_.State)"
                last_run  = if ($info) { "$($info.LastRunTime)" } else { $null }
                last_code = if ($info) { $info.LastTaskResult } else { $null }
                next_run  = if ($info) { "$($info.NextRunTime)" } else { $null }
            }
        })
        $script:Report.sections['scheduled_tasks'] = $trows
        if ($trows.Count -gt 0 -and $script:HasTaskLib) {
            # «Ненулевой код» — не синоним отказа: планировщик возвращает и свои
            # коды состояния (выполняется, ни разу не запускалась, в очереди).
            # Считать их провалами — получить десятки несуществующих отказов.
            $sum = Get-TaskFailureSummary -Tasks ($trows | ForEach-Object { [pscustomobject]$_ })

            $script:Report.sections['scheduled_tasks_summary'] = [ordered]@{
                total        = $sum.Total
                ok_count     = $sum.OkCount
                info_count   = $sum.InfoCount
                failed_count = $sum.FailedCount
                groups       = @($sum.Groups | ForEach-Object {
                    [ordered]@{ hex = $_.Hex; count = $_.Count; name = $_.ResultName; hint = $_.Hint; examples = @($_.Examples) }
                })
            }

            Write-Host ("  задач Sofia: {0}   успешно: {1}   состояние планировщика: {2}   отказов: {3}" -f `
                        $sum.Total, $sum.OkCount, $sum.InfoCount, $sum.FailedCount)

            if ($sum.FailedCount -gt 0) {
                Write-Host '  --- причины отказов ---' -ForegroundColor DarkGray
                foreach ($g in $sum.Groups) {
                    Write-Host ("    {0}  x{1,-4} {2}" -f $g.Hex, $g.Count, $g.ResultName) -ForegroundColor Yellow
                    Write-Host ("      {0}" -f $g.Hint) -ForegroundColor DarkGray
                    Write-Host ("      например: {0}" -f ($g.Examples -join ', ')) -ForegroundColor DarkGray
                }
            }

            if ($sum.FailedCount -gt 0) {
                $topG = $sum.Groups[0]
                Add-Finding -Status 'WARN' -Component 'Task Scheduler' `
                            -Evidence ("задач Sofia: {0}, отказов: {1} (чаще всего {2} {3} — {4} шт.); состояний планировщика, не отказов: {5}" -f `
                                       $sum.Total, $sum.FailedCount, $topG.Hex, $topG.ResultName, $topG.Count, $sum.InfoCount) `
                            -NextAction ("разбирать по самой частой причине: {0}; задачи не изменять — только чтение" -f $topG.Hint)
            } else {
                Add-Finding -Status 'PASS' -Component 'Task Scheduler' `
                            -Evidence ("задач Sofia: {0}, отказов нет ({1} в состоянии планировщика)" -f $sum.Total, $sum.InfoCount) `
                            -NextAction 'задачи не изменять — только чтение'
            }
        } elseif ($trows.Count -gt 0) {
            $trows | ForEach-Object { [pscustomobject]$_ } |
                Select-Object name, state, last_run, last_code, next_run |
                Format-Table -AutoSize | Out-String | Write-Host
            $bad = @($trows | Where-Object { $_.last_code -ne 0 -and $_.last_code -ne $null })
            Add-Finding -Status $(if ($bad.Count) { 'WARN' } else { 'PASS' }) -Component 'Task Scheduler' `
                        -Evidence ("задач Sofia: {0}, с ненулевым кодом: {1}; lib_task_results.ps1 рядом не найден" -f $trows.Count, $bad.Count) `
                        -NextAction 'скачать lib_task_results.ps1 из того же каталога репозитория и повторить'
        } else {
            Add-Finding -Status 'NOT_MEASURED' -Component 'Task Scheduler' -Evidence 'задачи Sofia не найдены по маске'
        }
    } catch {
        Add-Finding -Status 'NOT_MEASURED' -Component 'Task Scheduler' -Evidence 'нет доступа к планировщику'
    }
  }
}

# ---------------------------------------------------------------------------
# Вердикт и сохранение
# ---------------------------------------------------------------------------
$fails = @($script:Report.findings | Where-Object status -eq 'FAIL')
$warns = @($script:Report.findings | Where-Object status -eq 'WARN')
$blocked = @($script:Report.findings | Where-Object status -eq 'BLOCKED')

$script:Report.verdict =
    if ($blocked.Count -gt 0 -and $fails.Count -eq 0) { 'BLOCKED' }
    elseif ($fails.Count -gt 0) { 'FAIL' }
    elseif ($warns.Count -gt 0) { 'WARN' }
    else { 'PASS' }

Write-Head ("ВЕРДИКТ: {0}   (FAIL={1}  WARN={2}  BLOCKED={3})" -f $script:Report.verdict, $fails.Count, $warns.Count, $blocked.Count)

foreach ($f in $fails)   { Write-Host ("  FAIL    {0}: {1}" -f $f.component, $f.evidence) -ForegroundColor Red }
foreach ($f in $blocked) { Write-Host ("  BLOCKED {0}: {1}" -f $f.component, $f.evidence) -ForegroundColor Magenta }

Write-Host ''
Write-Host 'Напоминание о границах:' -ForegroundColor Yellow
Write-Host '  - HOST_SAFE_HOLD.flag не снимать до закрытия root cause;' -ForegroundColor Yellow
Write-Host '  - publishing state остаётся как есть (fail-closed);' -ForegroundColor Yellow
Write-Host '  - stale-локи не чистить вручную;' -ForegroundColor Yellow
Write-Host '  - reboot и изменения Task Scheduler — только решением владельца.' -ForegroundColor Yellow

$jsonPath = Join-Path $OutDir 'safehold_report.json'
$script:Report | ConvertTo-Json -Depth 8 | Out-File -FilePath $jsonPath -Encoding UTF8
try { Stop-Transcript | Out-Null } catch { }

Write-Host ''
Write-Host ("Отчёт JSON : {0}" -f $jsonPath) -ForegroundColor Green
Write-Host ("Лог консоли: {0}" -f $transcript) -ForegroundColor Green
Write-Host 'Пришлите safehold_report.json — по нему я поставлю точный диагноз.' -ForegroundColor Green
