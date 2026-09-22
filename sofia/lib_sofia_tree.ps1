<#
    Общая библиотека обнаружения для аудитов Sofia AI Studio.
    Подключается точкой из audit_agent_matrix.ps1 и audit_growth_readiness.ps1.

    Принцип: ничего не предполагать про дерево студии. Всё, что утверждает аудит,
    должно опираться на найденный файл, найденный процесс, найденную запись
    планировщика или найденную строку в логе. Не нашли — NOT_MEASURED,
    а не FAIL и не выдуманный PASS.

    Библиотека только читает. Ни одна функция здесь не пишет в дерево студии.
#>

# --------------------------------------------------------------------------
#  Корень дерева
# --------------------------------------------------------------------------

function Resolve-SofiaRoot {
    <#
        Возвращает путь к дереву студии или $null. Порядок: явный параметр,
        переменная окружения, типовые расположения. Каталог считается корнем,
        только если внутри есть хотя бы один опознаваемый маркер студии.
    #>
    param([string] $Hint)

    $markers = @('control_flags','agents','config','state','logs','pipelines','memory')

    $candidates = New-Object System.Collections.Generic.List[string]
    if ($Hint)            { $candidates.Add($Hint) }
    if ($env:SOFIA_ROOT)  { $candidates.Add($env:SOFIA_ROOT) }
    foreach ($c in @('D:\AI_CONTENT\Sofia','C:\AI_CONTENT\Sofia','E:\AI_CONTENT\Sofia','D:\Sofia','C:\Sofia')) {
        $candidates.Add($c)
    }

    foreach ($c in $candidates) {
        if (-not $c) { continue }
        if (-not (Test-Path -LiteralPath $c)) { continue }
        $hits = 0
        foreach ($m in $markers) {
            if (Test-Path -LiteralPath (Join-Path $c $m)) { $hits++ }
        }
        # один маркер может оказаться совпадением имени, два — уже дерево студии
        if ($hits -ge 2) { return (Resolve-Path -LiteralPath $c).Path }
    }

    # корень указали явно, но маркеров нет: вернуть как есть, аудит отметит это отдельно
    if ($Hint -and (Test-Path -LiteralPath $Hint)) { return (Resolve-Path -LiteralPath $Hint).Path }
    return $null
}

# --------------------------------------------------------------------------
#  Индекс файлов
# --------------------------------------------------------------------------

$script:SofiaSkipDirs = @(
    '\.git\', '\node_modules\', '\__pycache__\', '\site-packages\', '\.venv\', '\venv\',
    '\.cache\', '\.mypy_cache\', '\.pytest_cache\', '\dist-info\',
    '\models\', '\checkpoints\', '\loras\', '\vae\', '\clip\', '\unet\', '\embeddings\',
    '\python_embeded\', '\torch\', '\cuda\'
)

$script:SofiaCodeExt   = @('.py','.ps1','.psm1','.js','.mjs','.ts','.sh','.bat','.cmd')
$script:SofiaConfExt   = @('.json','.yaml','.yml','.toml','.ini','.jsonl','.csv')
$script:SofiaMediaExt  = @('.mp4','.mov','.mkv','.webm','.png','.jpg','.jpeg','.webp','.gif','.wav','.mp3','.m4a','.flac')

function New-SofiaIndex {
    <#
        Один обход дерева, дальше все проверки работают по этому индексу.
        Тяжёлые каталоги (веса моделей, venv, кэш) пропускаются: там нет агентов,
        а обход стоит минуты.
    #>
    param(
        [Parameter(Mandatory)][string] $Root,
        [int] $MaxFiles = 300000
    )

    $sw    = [System.Diagnostics.Stopwatch]::StartNew()
    $files = New-Object System.Collections.Generic.List[object]
    $truncated = $false
    $rootLen   = $Root.Length

    $raw = @()
    try {
        $raw = Get-ChildItem -LiteralPath $Root -Recurse -File -Force -ErrorAction SilentlyContinue
    } catch {
        $raw = @()
    }

    foreach ($f in $raw) {
        if ($files.Count -ge $MaxFiles) { $truncated = $true; break }

        $full = $f.FullName
        $rel  = if ($full.Length -gt $rootLen) { $full.Substring($rootLen).TrimStart('\','/') } else { $f.Name }
        $relLower = '\' + $rel.ToLowerInvariant().Replace('/','\')

        $skip = $false
        foreach ($s in $script:SofiaSkipDirs) {
            if ($relLower.Contains($s)) { $skip = $true; break }
        }
        if ($skip) { continue }

        $ext = $f.Extension.ToLowerInvariant()
        $files.Add([pscustomobject]@{
            Full     = $full
            Rel      = $rel
            RelLower = $relLower
            Name     = $f.Name
            NameLower= $f.Name.ToLowerInvariant()
            Ext      = $ext
            Length   = $f.Length
            Modified = $f.LastWriteTime
            IsCode   = ($script:SofiaCodeExt  -contains $ext)
            IsConf   = ($script:SofiaConfExt  -contains $ext)
            IsMedia  = ($script:SofiaMediaExt -contains $ext)
            IsLog    = ($ext -eq '.log' -or $relLower.Contains('\logs\') -or $relLower.Contains('\log\'))
        })
    }

    $sw.Stop()
    [pscustomobject]@{
        Root       = $Root
        Files      = $files
        Count      = $files.Count
        Truncated  = $truncated
        ScanMs     = [int]$sw.Elapsed.TotalMilliseconds
        ScannedAt  = Get-Date
    }
}

function Select-SofiaPath {
    <#
        Файлы, чей относительный путь совпал с любым из регулярных выражений.
        Совпадение по пути — слабая улика: имя файла ещё не агент.
    #>
    param(
        [Parameter(Mandatory)] $Index,
        [Parameter(Mandatory)][string[]] $Patterns,
        [ValidateSet('any','code','conf','log','media')][string] $Kind = 'any',
        [int] $Limit = 400
    )

    $out = New-Object System.Collections.Generic.List[object]
    foreach ($f in $Index.Files) {
        if ($out.Count -ge $Limit) { break }

        # continue внутри switch в PowerShell относится к самому switch,
        # а не к объемлющему foreach, поэтому фильтр — обычным условием
        $kindOk = $true
        if     ($Kind -eq 'code')  { $kindOk = $f.IsCode  }
        elseif ($Kind -eq 'conf')  { $kindOk = $f.IsConf  }
        elseif ($Kind -eq 'log')   { $kindOk = $f.IsLog   }
        elseif ($Kind -eq 'media') { $kindOk = $f.IsMedia }
        if (-not $kindOk) { continue }

        foreach ($p in $Patterns) {
            if ($f.RelLower -match $p) { $out.Add($f); break }
        }
    }
    # Возврат перечислением, без unary comma: на пустом наборе `,$arr` отдаёт
    # массив из одного пустого массива, и вызывающий считает фантом уликой.
    # Все вызывающие оборачивают результат в @(), поэтому единственный элемент
    # не схлопнется в скаляр.
    $out.ToArray()
}

function Search-SofiaContent {
    <#
        Поиск по содержимому с ограничениями: только текстовые файлы разумного
        размера и не больше $MaxScan штук, иначе аудит превращается в grep по
        всему диску. Возвращает совпадения с файлом и номером строки.
    #>
    param(
        [Parameter(Mandatory)] $Index,
        [Parameter(Mandatory)][string] $Pattern,
        [ValidateSet('code','conf','codeconf','log','any')][string] $Kind = 'codeconf',
        [int] $MaxScan  = 4000,
        [int] $MaxBytes = 1048576,
        [int] $MaxHits  = 60
    )

    $targets = New-Object System.Collections.Generic.List[string]
    foreach ($f in $Index.Files) {
        if ($targets.Count -ge $MaxScan) { break }
        if ($f.Length -gt $MaxBytes -or $f.Length -eq 0) { continue }
        $ok = switch ($Kind) {
            'code'     { $f.IsCode }
            'conf'     { $f.IsConf }
            'codeconf' { $f.IsCode -or $f.IsConf }
            'log'      { $f.IsLog }
            default    { -not $f.IsMedia }
        }
        if ($ok) { $targets.Add($f.Full) }
    }

    if ($targets.Count -eq 0) { return }

    $hits = @()
    try {
        $hits = @(Select-String -LiteralPath $targets.ToArray() -Pattern $Pattern -List:$false `
                                -ErrorAction SilentlyContinue | Select-Object -First $MaxHits)
    } catch {
        $hits = @()
    }

    $res = foreach ($h in $hits) {
        [pscustomobject]@{
            Path = $h.Path
            Rel  = if ($h.Path.StartsWith($Index.Root)) { $h.Path.Substring($Index.Root.Length).TrimStart('\','/') } else { $h.Path }
            Line = $h.LineNumber
            Text = $h.Line.Trim()
        }
    }
    $res
}

function Get-SofiaFresh {
    <#
        Из набора файлов — те, что изменялись за последние $Hours часов.
        Свежесть здесь единственное доказательство «оно работает», поэтому
        порог всегда явный, а не «недавно».
    #>
    param(
        [Parameter(Mandatory)] $Files,
        [double] $Hours = 48
    )
    $since = (Get-Date).AddHours(-1 * $Hours)
    $Files | Where-Object { $_.Modified -ge $since }
}

function Get-SofiaNewest {
    param([Parameter(Mandatory)] $Files)
    if (-not $Files -or @($Files).Count -eq 0) { return $null }
    @($Files) | Sort-Object Modified -Descending | Select-Object -First 1
}

function Format-SofiaAge {
    param($Time)
    if (-not $Time) { return 'никогда' }
    $span = (Get-Date) - $Time
    if ($span.TotalMinutes -lt 90) { return ('{0:N0} мин назад' -f $span.TotalMinutes) }
    if ($span.TotalHours   -lt 48) { return ('{0:N1} ч назад'   -f $span.TotalHours)   }
    return ('{0:N1} сут назад' -f $span.TotalDays)
}

# --------------------------------------------------------------------------
#  JSON
# --------------------------------------------------------------------------

function Read-SofiaJson {
    param([Parameter(Mandatory)][string] $Path, [int] $MaxBytes = 8388608)
    try {
        $fi = Get-Item -LiteralPath $Path -ErrorAction Stop
        if ($fi.Length -gt $MaxBytes -or $fi.Length -eq 0) { return $null }
        $raw = Get-Content -LiteralPath $Path -Raw -Encoding UTF8 -ErrorAction Stop
        if (-not $raw) { return $null }
        return ($raw | ConvertFrom-Json -ErrorAction Stop)
    } catch {
        return $null
    }
}

function Test-SofiaJsonKey {
    <#
        Есть ли где-нибудь в объекте ключ с таким именем. Глубина и ширина
        ограничены: смысл в наличии поля, а не в полном обходе большого файла.

        -Like смягчает сравнение до вхождения подстроки: имена полей в разных
        частях студии пишутся по-разному (hook_type / hookType / type_of_hook),
        и точное совпадение дало бы ложное «поля нет». Что именно совпало,
        вызывающий печатает в отчёте, поэтому смягчение остаётся проверяемым.
    #>
    param($Node, [Parameter(Mandatory)][string] $Key, [int] $Depth = 6, [int] $MaxItems = 40, [switch] $Like)

    if ($null -eq $Node -or $Depth -le 0) { return $false }

    $norm = $Key.ToLowerInvariant().Replace('_','')

    if ($Node -is [System.Management.Automation.PSCustomObject]) {
        foreach ($p in $Node.PSObject.Properties) {
            if ($p.Name -ieq $Key) { return $true }
            if ($Like -and $p.Name.ToLowerInvariant().Replace('_','').Contains($norm)) { return $true }
            if (Test-SofiaJsonKey -Node $p.Value -Key $Key -Depth ($Depth - 1) -MaxItems $MaxItems -Like:$Like) { return $true }
        }
        return $false
    }

    if ($Node -is [System.Collections.IDictionary]) {
        foreach ($k in $Node.Keys) {
            if ("$k" -ieq $Key) { return $true }
            if ($Like -and "$k".ToLowerInvariant().Replace('_','').Contains($norm)) { return $true }
            if (Test-SofiaJsonKey -Node $Node[$k] -Key $Key -Depth ($Depth - 1) -MaxItems $MaxItems -Like:$Like) { return $true }
        }
        return $false
    }

    if ($Node -is [System.Collections.IEnumerable] -and $Node -isnot [string]) {
        $i = 0
        foreach ($item in $Node) {
            if ($i -ge $MaxItems) { break }
            $i++
            if (Test-SofiaJsonKey -Node $item -Key $Key -Depth ($Depth - 1) -MaxItems $MaxItems -Like:$Like) { return $true }
        }
    }
    return $false
}

function Get-SofiaFieldCoverage {
    <#
        Какие из обязательных полей реально присутствуют. Возвращает объект
        с present/missing и долей — по ней капабилити получает PASS/PARTIAL/FAIL.
    #>
    param($Node, [Parameter(Mandatory)][string[]] $Fields, [switch] $Like)

    $present = @(); $missing = @()
    foreach ($f in $Fields) {
        if (Test-SofiaJsonKey -Node $Node -Key $f -Like:$Like) { $present += $f } else { $missing += $f }
    }
    [pscustomobject]@{
        Present = $present
        Missing = $missing
        Ratio   = if ($Fields.Count -gt 0) { [math]::Round($present.Count / $Fields.Count, 3) } else { 0 }
    }
}

# --------------------------------------------------------------------------
#  Живость: процессы и планировщик
# --------------------------------------------------------------------------

function Get-SofiaProcesses {
    <#
        Процессы, чья командная строка указывает внутрь дерева студии.
        Без прав администратора CommandLine чужих процессов бывает пустой —
        тогда возвращается меньше, чем есть, и это отмечается вызывающим.
    #>
    param([Parameter(Mandatory)][string] $Root)
    try {
        $all = @(Get-CimInstance Win32_Process -ErrorAction Stop |
                 Select-Object ProcessId, Name, CommandLine, CreationDate)
    } catch {
        # «не смогли посмотреть» и «посмотрели, ничего нет» — разные вещи:
        # первое обязано стать NOT_MEASURED, а не отсутствием улики
        return [pscustomobject]@{ Available = $false; Items = @() }
    }
    $needle = $Root.ToLowerInvariant()
    $res = foreach ($p in $all) {
        if (-not $p.CommandLine) { continue }
        if ($p.CommandLine.ToLowerInvariant().Contains($needle)) {
            [pscustomobject]@{
                Pid       = $p.ProcessId
                Name      = $p.Name
                Started   = $p.CreationDate
                CmdLine   = $p.CommandLine
            }
        }
    }
    [pscustomobject]@{ Available = $true; Items = @($res) }
}

function Get-SofiaScheduledTasks {
    <#
        Задачи планировщика, которые запускают что-то из дерева студии.
        Это единственный способ отличить «агент по расписанию» от файла,
        который никто не вызывает.
    #>
    param([Parameter(Mandatory)][string] $Root)
    try {
        $tasks = @(Get-ScheduledTask -ErrorAction Stop)
    } catch {
        return [pscustomobject]@{ Available = $false; Items = @() }
    }
    $needle = $Root.ToLowerInvariant()
    $res = foreach ($t in $tasks) {
        $line = ''
        foreach ($a in @($t.Actions)) {
            $line += ' ' + [string]$a.Execute + ' ' + [string]$a.Arguments + ' ' + [string]$a.WorkingDirectory
        }
        if (-not $line.ToLowerInvariant().Contains($needle)) { continue }

        $info = $null
        try { $info = Get-ScheduledTaskInfo -TaskName $t.TaskName -TaskPath $t.TaskPath -ErrorAction Stop } catch { }
        [pscustomobject]@{
            Name      = $t.TaskName
            Path      = $t.TaskPath
            State     = [string]$t.State
            Command   = $line.Trim()
            LastRun   = if ($info) { $info.LastRunTime } else { $null }
            NextRun   = if ($info) { $info.NextRunTime } else { $null }
            LastResult= if ($info) { $info.LastTaskResult } else { $null }
        }
    }
    [pscustomobject]@{ Available = $true; Items = @($res) }
}

# --------------------------------------------------------------------------
#  Отчёт
# --------------------------------------------------------------------------

function Write-SofiaHead {
    param([string] $Text)
    Write-Host ''
    Write-Host ('=' * 78) -ForegroundColor DarkCyan
    Write-Host "  $Text" -ForegroundColor Cyan
    Write-Host ('=' * 78) -ForegroundColor DarkCyan
}

function Get-SofiaStatusColor {
    param([string] $Status)
    switch ($Status) {
        'PASS'        { 'Green' }
        'ACTIVE_REAL' { 'Green' }
        'PARTIAL'     { 'Yellow' }
        'WARN'        { 'Yellow' }
        'DUPLICATE'   { 'Yellow' }
        'FAIL'        { 'Red' }
        'BROKEN'      { 'Red' }
        'MISSING'     { 'Red' }
        'SPEC_ONLY'   { 'Magenta' }
        'BLOCKED'     { 'Magenta' }
        default       { 'DarkGray' }
    }
}

function Save-SofiaReport {
    <#
        Отчёт пишется только в -OutDir, по умолчанию вне дерева студии.
        В дерево студии аудит не пишет ничего и никогда.
    #>
    param(
        [Parameter(Mandatory)] $Report,
        [Parameter(Mandatory)][string] $OutDir,
        [string] $FileName = 'report.json'
    )
    New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
    $path = Join-Path $OutDir $FileName
    $Report | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $path -Encoding UTF8
    return $path
}
