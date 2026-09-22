<#
.SYNOPSIS
    GROWTH READINESS: какие звенья ростового контура Sofia реально замкнуты.

.DESCRIPTION
    Матрица агентов отвечает, кто существует. Этот скрипт отвечает на другой
    вопрос: замкнут ли контур

      TREND -> AUDIENCE -> IDEA -> HOOK -> STORY -> MEDIA -> QA -> PUBLISH
            -> RETENTION/SHARES/SAVES/FOLLOWS -> LEARNING -> NEXT CONTENT

    и можно ли по данным студии доказать, что обучение действительно меняет
    следующее решение, а не просто пишет отчёты.

    Проверяется по артефактам, а не по намерениям. Для каждой способности:
      - есть ли артефакт (файл данных, а не код и не спецификация);
      - свежий ли он в окне -FreshHours;
      - есть ли в нём обязательные поля.

    Отдельно считаются вещи, которые нельзя подменить наличием файла:
      - портфель за сегодня: фото / Reels / Stories против цели 3 / 4 / N;
      - data lineage: сквозная цепочка id от тренда до аналитики;
      - learning contract: сколько раз аналитика реально изменила решение
        (нужно не меньше -LearningCases, по умолчанию 10);
      - follow conversion: измеряется ли FOLLOW_PER_1000_VIEWS;
      - состояние производства и публикации по control_flags.

    Нечего измерить — статус NOT_MEASURED. Это не FAIL и не PASS:
    отсутствие сигнала честнее выдуманного вывода.

    Скрипт ТОЛЬКО ЧИТАЕТ: не трогает control_flags, publishing state, сервисы,
    планировщик, ничего не удаляет и не пишет в дерево студии.

.PARAMETER SofiaRoot
    Корень дерева студии. По умолчанию определяется автоматически.

.PARAMETER MatrixReport
    Путь к agent_matrix.json от audit_agent_matrix.ps1. Если указан, итоговый
    отчёт включает и состояние агентов.

.PARAMETER FreshHours
    Окно свежести артефактов. По умолчанию 48.

.PARAMETER LearningCases
    Сколько доказанных случаев «аналитика изменила решение» требуется для PASS.
    По умолчанию 10.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\audit_growth_readiness.ps1

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\audit_growth_readiness.ps1 -MatrixReport C:\Temp\sofia_agent_matrix_20260922_120000\agent_matrix.json
#>

[CmdletBinding()]
param(
    [string] $SofiaRoot      = '',
    [string] $MatrixReport   = '',
    [double] $FreshHours     = 48,
    [int]    $LearningCases  = 10,
    [int]    $PhotoTarget    = 3,
    [int]    $ReelTarget     = 4,
    [string] $OutDir         = (Join-Path ([System.IO.Path]::GetTempPath()) ("sofia_growth_{0}" -f (Get-Date -Format 'yyyyMMdd_HHmmss')))
)

$ErrorActionPreference = 'Continue'
$ProgressPreference    = 'SilentlyContinue'

. (Join-Path $PSScriptRoot 'lib_sofia_tree.ps1')

# ==========================================================================
#  Таблица способностей ростового контура
# ==========================================================================
#  section — пункт задания; files — где искать артефакт данных;
#  fields  — что обязано быть внутри, иначе способность объявлена, но пуста.

$script:Caps = @(
    @{ key='AUDIENCE_INTELLIGENCE'; section=2; title='Audience Intelligence';
       files=@('audience','segment');
       fields=@('segments','topics','retention','saves','shares','profile_visits','follows') }

    @{ key='HOOK_LAB'; section=3; title='Hook & Retention Lab';
       files=@('hook');
       fields=@('candidates','hook_type','selected','hold_rate','completion','rewatch') }

    @{ key='PATTERN_MEMORY'; section=4; title='Viral Format / Pattern Memory';
       files=@('pattern','winner','viral');
       fields=@('topic','hook','format','duration','shot_count','pacing','edit_style','voice_style','caption_style','cta','posting_time','music','cover') }

    @{ key='CONTENT_PURPOSE'; section=5; title='Content Strategist / PURPOSE';
       files=@('content_plan','plan','idea');
       fields=@('purpose','why_watch') }

    @{ key='TREND_RADAR'; section=6; title='Trend Radar (fresh data)';
       files=@('trend');
       fields=@('source','url','timestamp','freshness','velocity','saturation','platform','format','audience_fit','sofia_fit','confidence','expiry') }

    @{ key='COMPETITOR_INTEL'; section=7; title='Competitor Intelligence';
       files=@('competitor','benchmark');
       fields=@('hook','shot_structure','duration','pace','story_structure','editing','cta','cadence','cover','voice','trend_adoption') }

    @{ key='IDEA_SCORING'; section=8; title='Idea Scoring';
       files=@('idea','score','plan');
       fields=@('trend_strength','audience_fit','sofia_fit','novelty','hook_potential','share_potential','save_potential','follow_potential','production_risk','saturation') }

    @{ key='STORY_ENGINE'; section=10; title='Story Engine';
       files=@('reel','story','script','shot');
       fields=@('hook','setup','tension','development','payoff') }

    @{ key='RETENTION_ENGINE'; section=11; title='Retention Engine';
       files=@('retention','analytic','insight');
       fields=@('retention_failure_reason','drop_off','watch_time','completion') }

    @{ key='PACKAGING'; section=12; title='Packaging';
       files=@('packag','cover','caption','thumbnail');
       fields=@('cover','first_frame','caption','cta','subtitles','metadata','music','thumbnail') }

    @{ key='CADENCE'; section=13; title='Distribution / Cadence Optimizer';
       files=@('cadence','posting','schedule','distribut');
       fields=@('content_type','day','hour','reach','retention','shares','follows') }

    @{ key='COMMUNITY_FEEDBACK'; section=14; title='Community Feedback Loop';
       files=@('comment','feedback','community','dm');
       fields=@('questions','objections','themes','requests') }

    @{ key='FOLLOW_CONVERSION'; section=15; title='Follow Conversion Engine';
       files=@('follow','conversion','analytic','funnel');
       fields=@('views','profile_visits','follows','follow_per_1000') }

    @{ key='EXPERIMENT_ENGINE'; section=16; title='Experiment Engine';
       files=@('experiment','ab_test');
       fields=@('hypothesis','primary_kpi','control','challenger','sample','result','confidence','decision') }

    @{ key='META_CRITIC'; section=17; title='Causal / Meta-Critic';
       files=@('critic','meta','verdict','causal');
       fields=@('sample_size','confounder','unknown','conclusion') }

    @{ key='NOVELTY_WATCH'; section=18; title='Creative Novelty Watch';
       files=@('novelty','diversity','fatigue','repetit');
       fields=@('location','outfit','camera_angle','pose','hook_type','topic','music','caption') }

    @{ key='CHARACTER_CONTINUITY'; section=19; title='Character Continuity';
       files=@('continuity','character','persona','arc');
       fields=@('where','did','said','promised','outfits','interests','arcs') }

    @{ key='WINNER_SCALING'; section=27; title='Winner Scaling / Loser Decay';
       files=@('weight','policy','pattern');
       fields=@('weight','saturation') }

    @{ key='RANDOM_ACCEPTANCE'; section=29; title='Random Media Acceptance';
       files=@('acceptance','random','review','qa');
       fields=@('identity','realism','story','hook','motion','voice','lip_sync','editing','ai_tells','publishable') }
)

$script:Report = [ordered]@{
    generated_at   = (Get-Date).ToString('o')
    host           = $env:COMPUTERNAME
    tool           = 'audit_growth_readiness'
    sofia_root     = $null
    fresh_hours    = $FreshHours
    reachable      = $false
    capabilities   = @()
    portfolio      = [ordered]@{}
    production     = [ordered]@{}
    lineage        = [ordered]@{}
    learning       = [ordered]@{}
    acceptance     = [ordered]@{}
    gaps           = @()
    agents         = $null
    verdict        = 'NOT_MEASURED'
    notes          = @()
}

function Add-Note {
    param([string] $Text)
    $script:Report.notes += $Text
    Write-Host ("  ! {0}" -f $Text) -ForegroundColor DarkYellow
}

# ==========================================================================
#  0. Дерево
# ==========================================================================

Write-SofiaHead 'GROWTH READINESS — 0. дерево студии'

$root = Resolve-SofiaRoot -Hint $SofiaRoot
if (-not $root) {
    Write-Host ''
    Write-Host '  Дерево Sofia AI Studio не найдено на этой машине.' -ForegroundColor Magenta
    Write-Host '  Ростовой контур можно проверить только там, где лежат данные студии.' -ForegroundColor Magenta
    Write-Host ''
    Write-Host '  Запустите на машине студии или укажите корень явно:' -ForegroundColor White
    Write-Host '    .\audit_growth_readiness.ps1 -SofiaRoot ''D:\AI_CONTENT\Sofia''' -ForegroundColor White
    Write-Host ''
    $script:Report.verdict = 'BLOCKED'
    $script:Report.notes  += 'sofia root not found: аудит не выполнялся'
    $p = Save-SofiaReport -Report $script:Report -OutDir $OutDir -FileName 'growth_readiness.json'
    Write-Host ("  Отчёт: {0}" -f $p) -ForegroundColor DarkGray
    exit 2
}

$script:Report.sofia_root = $root
$script:Report.reachable  = $true
Write-Host ("  Корень : {0}" -f $root) -ForegroundColor White

$index = New-SofiaIndex -Root $root
Write-Host ("  Файлов : {0} (обход {1} мс)" -f $index.Count, $index.ScanMs) -ForegroundColor White
if ($index.Truncated) { Add-Note 'индекс усечён лимитом файлов: часть дерева не просмотрена' }

if ($MatrixReport -and (Test-Path -LiteralPath $MatrixReport)) {
    $m = Read-SofiaJson -Path $MatrixReport
    if ($m) {
        $script:Report.agents = [ordered]@{
            verdict = $m.verdict
            totals  = $m.totals
            source  = $MatrixReport
        }
        Write-Host ("  Матрица агентов: {0} (ACTIVE_REAL {1}/{2})" -f $m.verdict, $m.totals.active_real, $m.totals.roles_total) -ForegroundColor White
    }
}

# ==========================================================================
#  1. Способности
# ==========================================================================

Write-SofiaHead 'GROWTH READINESS — 1. способности ростового контура'

function Read-CapSample {
    <#
        Одна запись из файла данных: объект целиком для .json, первая строка
        для .jsonl. Форматы, которые не разбираются, дают $null — и тогда
        способность честно получает NOT_MEASURED вместо выдуманного вывода.
    #>
    param($File)
    if ($File.Ext -eq '.json') { return (Read-SofiaJson -Path $File.Full) }
    if ($File.Ext -eq '.jsonl') {
        try {
            $l = Get-Content -LiteralPath $File.Full -TotalCount 1 -ErrorAction Stop
            if ($l) { return ($l | ConvertFrom-Json -ErrorAction SilentlyContinue) }
        } catch { return $null }
    }
    return $null
}

function Get-DataArtifacts {
    <#
        Артефакт способности — это файл ДАННЫХ. Код и markdown-спецификация
        артефактом не считаются: именно на этой подмене и вырастает «агент,
        которого нет».
    #>
    param($Index, [string[]] $Patterns)
    $f = @(Select-SofiaPath -Index $Index -Patterns $Patterns -Kind 'conf' -Limit 400)
    @($f | Where-Object { $_.Ext -in @('.json','.jsonl','.csv','.yaml','.yml') })
}

$capRows = @()

foreach ($cap in $script:Caps) {

    $artifacts = @(Get-DataArtifacts -Index $index -Patterns $cap.files)
    $fresh     = @(Get-SofiaFresh -Files $artifacts -Hours $FreshHours)
    $newest    = Get-SofiaNewest -Files $artifacts

    # способность хотя бы объявлена в коде?
    $declared = @(Search-SofiaContent -Index $index -Pattern (($cap.fields | ForEach-Object { [regex]::Escape($_) }) -join '|') `
                                      -Kind 'code' -MaxScan 3000 -MaxHits 10)

    # Поля способности законно лежат в нескольких файлах: веса в одном,
    # насыщение в другом. Проверка только самого свежего файла объявила бы
    # недостающим то, что есть рядом, поэтому берётся объединение по
    # нескольким свежим артефактам, и в отчёт пишется, откуда оно собрано.
    $coverage    = $null
    $sampledFrom = @()
    $present     = @()

    foreach ($sf in @($artifacts | Sort-Object Modified -Descending | Select-Object -First 5)) {
        $obj = Read-CapSample -File $sf
        if (-not $obj) { continue }
        $sampledFrom += $sf.Rel
        $cv = Get-SofiaFieldCoverage -Node $obj -Fields $cap.fields -Like
        $present += $cv.Present
    }

    if ($sampledFrom.Count -gt 0) {
        $present  = @($present | Select-Object -Unique)
        $missing  = @($cap.fields | Where-Object { $present -notcontains $_ })
        $coverage = [pscustomobject]@{
            Present = $present
            Missing = $missing
            Ratio   = [math]::Round($present.Count / $cap.fields.Count, 3)
        }
    }

    # --- статус
    if ($artifacts.Count -eq 0 -and $declared.Count -eq 0) {
        $status = 'FAIL';   $why = 'ни артефакта данных, ни упоминания в коде'
    } elseif ($artifacts.Count -eq 0) {
        $status = 'PARTIAL'; $why = 'способность есть в коде, но данных она не производит'
    } elseif ($fresh.Count -eq 0) {
        $status = 'PARTIAL'; $why = ('артефакт есть, но не обновлялся: ' + (Format-SofiaAge -Time $newest.Modified))
    } elseif (-not $coverage) {
        $status = 'NOT_MEASURED'; $why = 'артефакт свежий, но его формат не разобран (не JSON/JSONL)'
    } elseif ($coverage.Ratio -ge 0.8) {
        $status = 'PASS';    $why = ('поля на месте: ' + $coverage.Present.Count + '/' + $cap.fields.Count)
    } elseif ($coverage.Ratio -ge 0.4) {
        $status = 'PARTIAL'; $why = ('нет полей: ' + (($coverage.Missing | Select-Object -First 5) -join ', '))
    } else {
        $status = 'FAIL';    $why = ('артефакт почти пустой, нет полей: ' + (($coverage.Missing | Select-Object -First 6) -join ', '))
    }

    $row = [ordered]@{
        key            = $cap.key
        section        = $cap.section
        title          = $cap.title
        status         = $status
        why            = $why
        artifacts_n    = $artifacts.Count
        fresh_n        = $fresh.Count
        newest         = if ($newest) { $newest.Rel } else { $null }
        newest_age     = if ($newest) { Format-SofiaAge -Time $newest.Modified } else { 'никогда' }
        fields_present = if ($coverage) { $coverage.Present } else { @() }
        fields_missing = if ($coverage) { $coverage.Missing } else { $cap.fields }
        sampled_from   = $sampledFrom
        declared_in_code = $declared.Count -gt 0
    }
    $capRows += $row

    Write-Host ("  [{0,-12}] §{1,-2} {2,-34} {3}" -f $status, $cap.section, $cap.title, $why) `
               -ForegroundColor (Get-SofiaStatusColor -Status $status)
}
$script:Report.capabilities = $capRows

# ==========================================================================
#  2. Портфель за сегодня
# ==========================================================================

Write-SofiaHead 'GROWTH READINESS — 2. портфель за сегодня'

$today = (Get-Date).Date

function Measure-TodayMedia {
    param($Index, [string[]] $Patterns, [string[]] $Ext)
    $n = 0
    foreach ($f in $Index.Files) {
        if (-not $f.IsMedia) { continue }
        if ($Ext -and ($Ext -notcontains $f.Ext)) { continue }
        if ($f.Modified.Date -ne $today) { continue }
        foreach ($p in $Patterns) {
            if ($f.RelLower -match $p) { $n++; break }
        }
    }
    $n
}

$photoToday = Measure-TodayMedia -Index $index -Patterns @('photo','image','still') -Ext @('.png','.jpg','.jpeg','.webp')
$reelToday  = Measure-TodayMedia -Index $index -Patterns @('reel','video','render','final') -Ext @('.mp4','.mov','.webm','.mkv')
$storyToday = Measure-TodayMedia -Index $index -Patterns @('story','stories') -Ext @('.mp4','.mov','.png','.jpg','.jpeg','.webp')

$script:Report.portfolio = [ordered]@{
    date          = $today.ToString('yyyy-MM-dd')
    photo         = $photoToday
    photo_target  = $PhotoTarget
    reels         = $reelToday
    reels_target  = $ReelTarget
    stories       = $storyToday
    note          = 'считаются медиафайлы с сегодняшней датой изменения; это произведено, а не обязательно опубликовано'
}

$pStatus = if ($photoToday -ge $PhotoTarget) { 'PASS' } elseif ($photoToday -gt 0) { 'PARTIAL' } else { 'FAIL' }
$rStatus = if ($reelToday  -ge $ReelTarget)  { 'PASS' } elseif ($reelToday  -gt 0) { 'PARTIAL' } else { 'FAIL' }

Write-Host ("  PHOTO   {0}/{1}" -f $photoToday, $PhotoTarget) -ForegroundColor (Get-SofiaStatusColor -Status $pStatus)
Write-Host ("  REELS   {0}/{1}" -f $reelToday,  $ReelTarget)  -ForegroundColor (Get-SofiaStatusColor -Status $rStatus)
Write-Host ("  STORIES {0}"     -f $storyToday) -ForegroundColor DarkGray
Write-Host '  Это счёт произведённого. Публикация проверяется отдельно ниже.' -ForegroundColor DarkGray

# ==========================================================================
#  3. Производство и публикация
# ==========================================================================

Write-SofiaHead 'GROWTH READINESS — 3. производство и публикация'

$flagDir = Join-Path $root 'control_flags'
$flags = @()
if (Test-Path -LiteralPath $flagDir) {
    $flags = @(Get-ChildItem -LiteralPath $flagDir -File -ErrorAction SilentlyContinue | ForEach-Object { $_.Name })
}

$holdFlags = @($flags | Where-Object { $_ -match 'HOLD|FROZEN|DISABLED|STOP|PAUSE' })

$pubRecords = @(Get-DataArtifacts -Index $index -Patterns @('publish','publication','posted','instagram','feed'))
$pubFresh   = @(Get-SofiaFresh -Files $pubRecords -Hours $FreshHours)
$pubNewest  = Get-SofiaNewest -Files $pubRecords

$prodStatus = if ($holdFlags.Count -gt 0) { 'BLOCKED' } elseif ($photoToday + $reelToday -gt 0) { 'RUNNING' } else { 'NOT_MEASURED' }
$pubStatus  = if ($holdFlags.Count -gt 0) { 'BLOCKED' } elseif ($pubFresh.Count -gt 0) { 'RUNNING' } elseif ($pubRecords.Count -gt 0) { 'STALLED' } else { 'NOT_MEASURED' }

$script:Report.production = [ordered]@{
    control_flags     = $flags
    blocking_flags    = $holdFlags
    production        = $prodStatus
    publication       = $pubStatus
    publications_seen = $pubRecords.Count
    publications_fresh= $pubFresh.Count
    newest_publication= if ($pubNewest) { $pubNewest.Rel + ' (' + (Format-SofiaAge -Time $pubNewest.Modified) + ')' } else { $null }
}

if ($holdFlags.Count -gt 0) {
    Write-Host ("  Блокирующие флаги: {0}" -f ($holdFlags -join ', ')) -ForegroundColor Magenta
    Write-Host '  Пока флаг стоит, производство и публикация остановлены штатно (fail-closed).' -ForegroundColor Magenta
    Write-Host '  Аудит флаг НЕ снимает: это решение владельца по своей процедуре.' -ForegroundColor Magenta
} else {
    Write-Host '  Блокирующих флагов нет.' -ForegroundColor Green
}
Write-Host ("  PRODUCTION  : {0}" -f $prodStatus) -ForegroundColor (Get-SofiaStatusColor -Status $(if ($prodStatus -eq 'RUNNING') {'PASS'} elseif ($prodStatus -eq 'BLOCKED') {'BLOCKED'} else {'NOT_MEASURED'}))
Write-Host ("  PUBLICATION : {0}" -f $pubStatus)  -ForegroundColor (Get-SofiaStatusColor -Status $(if ($pubStatus  -eq 'RUNNING') {'PASS'} elseif ($pubStatus  -eq 'BLOCKED') {'BLOCKED'} else {'NOT_MEASURED'}))

# ==========================================================================
#  4. Data lineage
# ==========================================================================
#  Без сквозной цепочки id обучение недостоверно: нельзя связать результат
#  с решением, которое к нему привело.

Write-SofiaHead 'GROWTH READINESS — 4. data lineage'

$lineageIds = @('trend_id','idea_id','script_id','asset_id','reel_id','publication_id','analytics_id','experiment_id')

$lineageFiles = @(Get-DataArtifacts -Index $index -Patterns @('publish','publication','analytic','reel','lineage','asset'))
$lineageFiles = @($lineageFiles | Sort-Object Modified -Descending | Select-Object -First 25)

$idSeen  = @{}
foreach ($i in $lineageIds) { $idSeen[$i] = 0 }
$chainComplete = 0
$inspected = 0

foreach ($f in $lineageFiles) {
    $obj = $null
    if ($f.Ext -eq '.json') {
        $obj = Read-SofiaJson -Path $f.Full
    } elseif ($f.Ext -eq '.jsonl') {
        try {
            $l = Get-Content -LiteralPath $f.Full -TotalCount 1 -ErrorAction Stop
            if ($l) { $obj = $l | ConvertFrom-Json -ErrorAction SilentlyContinue }
        } catch { $obj = $null }
    }
    if (-not $obj) { continue }
    $inspected++

    $hit = 0
    foreach ($i in $lineageIds) {
        if (Test-SofiaJsonKey -Node $obj -Key $i) { $idSeen[$i]++; $hit++ }
    }
    if ($hit -eq $lineageIds.Count) { $chainComplete++ }
}

$lineageStatus = if ($inspected -eq 0) { 'NOT_MEASURED' }
                 elseif ($chainComplete -gt 0) { 'PASS' }
                 elseif (($idSeen.Values | Measure-Object -Sum).Sum -gt 0) { 'PARTIAL' }
                 else { 'FAIL' }

$script:Report.lineage = [ordered]@{
    inspected_files = $inspected
    complete_chains = $chainComplete
    id_presence     = $idSeen
    status          = $lineageStatus
    required_ids    = $lineageIds
}

Write-Host ("  Разобрано записей : {0}" -f $inspected) -ForegroundColor White
Write-Host ("  Полных цепочек    : {0}" -f $chainComplete) -ForegroundColor White
foreach ($i in $lineageIds) {
    $c = $idSeen[$i]
    Write-Host ("    {0,-16} {1}" -f $i, $c) -ForegroundColor $(if ($c -gt 0) { 'Green' } else { 'DarkGray' })
}
Write-Host ("  LINEAGE: {0}" -f $lineageStatus) -ForegroundColor (Get-SofiaStatusColor -Status $lineageStatus)

# ==========================================================================
#  5. Learning contract
# ==========================================================================
#  Требуется доказательство: аналитика -> память -> изменение политики ->
#  изменённое решение. Запись засчитывается, только если в ней есть все три
#  звена. Отчёт без изменения политики обучением не является.

Write-SofiaHead 'GROWTH READINESS — 5. learning contract'

$policyFiles = @(Get-DataArtifacts -Index $index -Patterns @('policy','weight','learn','decision','memory','pattern'))
$policyFiles = @($policyFiles | Sort-Object Modified -Descending | Select-Object -First 40)

$evidenceKeysAnalytics = @('analytics_id','metric','evidence','observed','sample')
$evidenceKeysPolicy    = @('policy','weight','rule','threshold')
$evidenceKeysDecision  = @('decision','applied','next','changed_to','new_value')

$cases = @()
foreach ($f in $policyFiles) {
    $obj = $null
    if ($f.Ext -eq '.json') { $obj = Read-SofiaJson -Path $f.Full }
    elseif ($f.Ext -eq '.jsonl') {
        try { $obj = @(Get-Content -LiteralPath $f.Full -TotalCount 200 -ErrorAction Stop |
                       ForEach-Object { $_ | ConvertFrom-Json -ErrorAction SilentlyContinue }) } catch { $obj = $null }
    }
    if (-not $obj) { continue }

    # записи могут лежать и списком, и одним объектом
    $records = @()
    if ($obj -is [System.Collections.IEnumerable] -and $obj -isnot [string]) { $records = @($obj) } else { $records = @($obj) }

    foreach ($r in ($records | Select-Object -First 200)) {
        $hasA = $false; $hasP = $false; $hasD = $false
        foreach ($k in $evidenceKeysAnalytics) { if (Test-SofiaJsonKey -Node $r -Key $k -Like -Depth 4) { $hasA = $true; break } }
        foreach ($k in $evidenceKeysPolicy)    { if (Test-SofiaJsonKey -Node $r -Key $k -Like -Depth 4) { $hasP = $true; break } }
        foreach ($k in $evidenceKeysDecision)  { if (Test-SofiaJsonKey -Node $r -Key $k -Like -Depth 4) { $hasD = $true; break } }
        if ($hasA -and $hasP -and $hasD) {
            $cases += [ordered]@{ file = $f.Rel; age = (Format-SofiaAge -Time $f.Modified) }
        }
    }
}

$caseCount = $cases.Count
$learnStatus = if ($policyFiles.Count -eq 0) { 'NOT_MEASURED' }
               elseif ($caseCount -ge $LearningCases) { 'PASS' }
               elseif ($caseCount -gt 0) { 'PARTIAL' }
               else { 'FAIL' }

$script:Report.learning = [ordered]@{
    required_cases = $LearningCases
    proven_cases   = $caseCount
    status         = $learnStatus
    files_scanned  = $policyFiles.Count
    sample         = @($cases | Select-Object -First 10)
    definition     = 'запись засчитана, если в ней одновременно есть опора на аналитику, изменённая политика/вес и принятое решение'
}

Write-Host ("  Файлов политики/памяти : {0}" -f $policyFiles.Count) -ForegroundColor White
Write-Host ("  Доказанных случаев     : {0} из требуемых {1}" -f $caseCount, $LearningCases) `
           -ForegroundColor (Get-SofiaStatusColor -Status $learnStatus)
Write-Host ("  LEARNING: {0}" -f $learnStatus) -ForegroundColor (Get-SofiaStatusColor -Status $learnStatus)

# ==========================================================================
#  6. Acceptance
# ==========================================================================

Write-SofiaHead 'GROWTH READINESS — 6. acceptance'

function Get-CapStatus {
    param([string] $Key)
    $r = $capRows | Where-Object { $_.key -eq $Key } | Select-Object -First 1
    if ($r) { return $r.status }
    return 'NOT_MEASURED'
}

$acc = [ordered]@{
    'PRODUCTION'              = $prodStatus
    'PUBLICATION'             = $pubStatus
    'TREND -> CONTENT'        = Get-CapStatus 'TREND_RADAR'
    'AUDIENCE INTELLIGENCE'   = Get-CapStatus 'AUDIENCE_INTELLIGENCE'
    'HOOK / RETENTION LOOP'   = Get-CapStatus 'HOOK_LAB'
    'FOLLOW CONVERSION'       = $(if ((Get-CapStatus 'FOLLOW_CONVERSION') -eq 'PASS') { 'MEASURED' } else { 'NOT_MEASURED' })
    'ANALYTICS -> DECISION'   = $learnStatus
    'EXPERIMENT ENGINE'       = Get-CapStatus 'EXPERIMENT_ENGINE'
    'WINNER SCALING'          = Get-CapStatus 'WINNER_SCALING'
    'NOVELTY / FATIGUE'       = Get-CapStatus 'NOVELTY_WATCH'
    'CHARACTER CONTINUITY'    = Get-CapStatus 'CHARACTER_CONTINUITY'
    'DATA LINEAGE'            = $lineageStatus
    'MEDIA QUALITY'           = Get-CapStatus 'RANDOM_ACCEPTANCE'
}
if ($script:Report.agents) {
    $acc['AGENTS REAL']           = $script:Report.agents.verdict
    $acc['DEAD/DUPLICATE AGENTS'] = ([int]$script:Report.agents.totals.duplicate + [int]$script:Report.agents.totals.retire_count)
}
$script:Report.acceptance = $acc

foreach ($k in $acc.Keys) {
    Write-Host ("  {0,-24} {1}" -f $k, $acc[$k]) -ForegroundColor (Get-SofiaStatusColor -Status ([string]$acc[$k]))
}

# ==========================================================================
#  7. Топ разрывов и итог
# ==========================================================================

Write-SofiaHead 'GROWTH READINESS — 7. топ разрывов'

# приоритет по §26: follow conversion > shares/saves > retention > watch time > reach
$priority = @{
    'FOLLOW_CONVERSION'=1; 'HOOK_LAB'=2; 'RETENTION_ENGINE'=3; 'AUDIENCE_INTELLIGENCE'=4;
    'EXPERIMENT_ENGINE'=5; 'PATTERN_MEMORY'=6; 'TREND_RADAR'=7; 'IDEA_SCORING'=8;
    'CONTENT_PURPOSE'=9; 'STORY_ENGINE'=10; 'PACKAGING'=11; 'NOVELTY_WATCH'=12;
    'CHARACTER_CONTINUITY'=13; 'CADENCE'=14; 'COMMUNITY_FEEDBACK'=15; 'META_CRITIC'=16;
    'COMPETITOR_INTEL'=17; 'WINNER_SCALING'=18; 'RANDOM_ACCEPTANCE'=19
}

$gaps = @()
foreach ($r in $capRows) {
    if ($r.status -eq 'PASS') { continue }
    $gaps += [pscustomobject]@{
        key      = $r.key
        section  = $r.section
        title    = $r.title
        status   = $r.status
        why      = $r.why
        priority = $(if ($priority.ContainsKey($r.key)) { $priority[$r.key] } else { 99 })
    }
}
if ($lineageStatus -ne 'PASS') {
    $gaps += [pscustomobject]@{ key='DATA_LINEAGE'; section=24; title='Data lineage'; status=$lineageStatus;
                         why='без сквозной цепочки id выводы обучения недостоверны'; priority=0 }
}
if ($learnStatus -ne 'PASS') {
    $gaps += [pscustomobject]@{ key='LEARNING_CONTRACT'; section=25; title='Learning contract'; status=$learnStatus;
                         why=('доказанных случаев ' + $caseCount + ' из ' + $LearningCases); priority=0 }
}

# Sort-Object читает свойства объекта, а ключи [ordered]@{} свойствами не являются:
# на хэш-таблицах сортировка молча вырождается в исходный порядок, поэтому строки
# разрывов — [pscustomobject].
$gaps = @($gaps | Sort-Object priority, section)
$script:Report.gaps = $gaps

foreach ($g in ($gaps | Select-Object -First 5)) {
    Write-Host ("  §{0,-2} {1,-34} {2,-12} {3}" -f $g.section, $g.title, $g.status, $g.why) `
               -ForegroundColor (Get-SofiaStatusColor -Status $g.status)
}
if ($gaps.Count -gt 5) { Write-Host ("  ... всего разрывов: {0}" -f $gaps.Count) -ForegroundColor DarkGray }

$passN = @($capRows | Where-Object { $_.status -eq 'PASS' }).Count
if ($passN -eq $capRows.Count -and $lineageStatus -eq 'PASS' -and $learnStatus -eq 'PASS') {
    $script:Report.verdict = 'PASS'
} elseif ($passN -eq 0) {
    $script:Report.verdict = 'FAIL'
} else {
    $script:Report.verdict = 'PARTIAL'
}

Write-SofiaHead 'GROWTH READINESS — итог'
Write-Host ("  Способностей PASS : {0}/{1}" -f $passN, $capRows.Count) -ForegroundColor White
Write-Host ("  ВЕРДИКТ           : {0}" -f $script:Report.verdict) -ForegroundColor (Get-SofiaStatusColor -Status $script:Report.verdict)
Write-Host ''
Write-Host '  Вердикт описывает готовность контура, а не вероятность вирусности.' -ForegroundColor DarkGray
Write-Host '  Вирусность не гарантируется: контур повышает шансы, а не обещает результат.' -ForegroundColor DarkGray

$reportPath = Save-SofiaReport -Report $script:Report -OutDir $OutDir -FileName 'growth_readiness.json'
Write-Host ''
Write-Host ("  Отчёт: {0}" -f $reportPath) -ForegroundColor White
Write-Host ''
