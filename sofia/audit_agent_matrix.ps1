<#
.SYNOPSIS
    REAL AGENT MATRIX: кто из агентов Sofia AI Studio существует на самом деле.

.DESCRIPTION
    Скрипт отвечает на вопрос, с которого начинается любое развитие студии:
    какие роли реально работают, а какие существуют только в виде файлов.

    Правило проверки (одно, жёсткое): файл или класс НЕ является доказательством
    агента. Агент считается настоящим, только если одновременно есть:

      1. RUNNER    — его действительно кто-то запускает (планировщик, процесс,
                     регистрация в оркестраторе, точка входа);
      2. EXECUTION — след недавнего запуска в пределах окна -FreshHours;
      3. OUTPUT    — свежий артефакт, который он произвёл;
      4. CONSUMER  — этот артефакт кто-то читает, кроме самого агента;
      5. METRIC    — есть метрика успеха, по которой видно, работает он или нет.

    Классы: ACTIVE_REAL / PARTIAL / SPEC_ONLY / BROKEN / DUPLICATE / MISSING.

    Отдельно собирается:
      - таблица оркестрации (AGENT/OWNER/TASK/STATUS/INPUT/OUTPUT/LAST_RUN/NEXT_RUN/ERROR);
      - список кандидатов на RETIRE: сущности с runner, но без потребителя и без запусков.

    Скрипт ТОЛЬКО ЧИТАЕТ. Он не трогает control_flags, HOST_SAFE_HOLD.flag,
    publishing state, сервисы и планировщик, ничего не удаляет и не пишет
    в дерево студии. Отчёт кладётся только в -OutDir.

.PARAMETER SofiaRoot
    Корень дерева студии. По умолчанию определяется автоматически
    (D:\AI_CONTENT\Sofia и другие типовые расположения, переменная SOFIA_ROOT).

.PARAMETER FreshHours
    Окно свежести для «недавнего запуска» и «свежего output». По умолчанию 48.

.PARAMETER OutDir
    Каталог отчёта. По умолчанию %TEMP%\sofia_agent_matrix_<timestamp>.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\audit_agent_matrix.ps1

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\audit_agent_matrix.ps1 -FreshHours 72

.NOTES
    Права администратора не обязательны. Без них не видно командных строк чужих
    процессов и части задач планировщика — такие улики помечаются как
    NOT_MEASURED, а не превращаются в FAIL.
#>

[CmdletBinding()]
param(
    [string] $SofiaRoot   = '',
    [double] $FreshHours  = 48,
    [string] $OutDir      = (Join-Path ([System.IO.Path]::GetTempPath()) ("sofia_agent_matrix_{0}" -f (Get-Date -Format 'yyyyMMdd_HHmmss'))),
    [int]    $MaxScanFiles = 6000
)

$ErrorActionPreference = 'Continue'
$ProgressPreference    = 'SilentlyContinue'

. (Join-Path $PSScriptRoot 'lib_sofia_tree.ps1')

# ==========================================================================
#  Таблица ролей
# ==========================================================================
#  path   — фрагменты пути, по которым ищем кандидатов в реализацию;
#  code   — что должно встречаться в коде/конфиге, чтобы это была именно эта роль;
#  output — где искать её свежие артефакты;
#  metric — имена метрик успеха;
#  group  — core: роли из текущей архитектуры; growth: роли ростового контура.

$script:Roles = @(
    @{ key='MASTER_ORCHESTRATOR'; title='Master Orchestrator'; group='core';
       path=@('orchestrat','master'); code=@('master[_\-]?orchestrat','MasterOrchestrator','agent_registry','dispatch_agent');
       output=@('orchestrat','agent_state','agent_registry','cycle'); metric=@('cycle','dispatch','agents_active') }

    @{ key='CONTENT_DIRECTOR'; title='Content Director'; group='core';
       path=@('content[_\-]?director','content_plan','planner'); code=@('content[_\-]?director','ContentDirector','content_plan');
       output=@('content_plan','plan','idea'); metric=@('ideas_generated','plan_items','idea_score') }

    @{ key='PHOTO_AGENT'; title='Photo Agent'; group='core';
       path=@('photo','image[_\-]?gen','still'); code=@('photo[_\-]?agent','PhotoAgent','photo_pipeline','generate_photo');
       output=@('photo','image'); metric=@('photo_generated','photos_today','photo_accept') }

    @{ key='VIDEO_AGENT'; title='Video Agent'; group='core';
       path=@('video','render','wan','animate'); code=@('video[_\-]?agent','VideoAgent','video_pipeline','render_video');
       output=@('video','render'); metric=@('video_generated','videos_today','render_success') }

    @{ key='REEL_DIRECTOR'; title='Reel Director'; group='core';
       path=@('reel','edit','montage','story'); code=@('reel[_\-]?director','ReelDirector','reel_plan','shot_list');
       output=@('reel','edit','montage'); metric=@('reels_today','reel_accept','shot_count') }

    @{ key='VOICE_TALKING'; title='Voice / Talking'; group='core';
       path=@('voice','tts','audio','lip','talk'); code=@('voice[_\-]?agent','VoiceAgent','lip[_\-]?sync','tts_');
       output=@('voice','audio','tts'); metric=@('voice_generated','lip_sync_score','audio_accept') }

    @{ key='REALISM_CRITIC'; title='Realism Critic'; group='core';
       path=@('realism','critic','qa','quality'); code=@('realism[_\-]?critic','RealismCritic','ai_tell','realism_score');
       output=@('realism','qa','critic'); metric=@('realism_score','qa_pass','ai_tells') }

    @{ key='TREND_GROWTH'; title='Trend / Growth'; group='core';
       path=@('trend','growth','radar'); code=@('trend[_\-]?agent','TrendAgent','trend_radar','trend_signal');
       output=@('trend'); metric=@('trends_found','trends_used','trend_confidence') }

    @{ key='ANALYTICS_LEARNING'; title='Analytics / Learning'; group='core';
       path=@('analytic','insight','metric','learn'); code=@('analytics[_\-]?agent','AnalyticsAgent','collect_metrics','learning_loop');
       output=@('analytic','metric','insight'); metric=@('analytics_runs','metrics_collected','policy_updates') }

    @{ key='IMPROVEMENT_ENGINE'; title='Improvement Engine'; group='core';
       path=@('improve','backlog','upgrade'); code=@('improvement[_\-]?engine','ImprovementEngine','improvement_backlog');
       output=@('improve','backlog'); metric=@('improvements_applied','backlog_size') }

    @{ key='SRE'; title='SRE / Stability'; group='core';
       path=@('sre','stability','health','governor','watchdog'); code=@('governor','health_check','HOST_SAFE_HOLD','gpu_resource_scheduler');
       output=@('health','governor','sre','incident'); metric=@('uptime','incidents','health_status') }

    @{ key='INDEPENDENT_CRITIC'; title='Independent Critic'; group='core';
       path=@('independent','meta[_\-]?critic','review'); code=@('independent[_\-]?critic','IndependentCritic','meta[_\-]?critic');
       output=@('critic','review','verdict'); metric=@('critic_verdicts','rejected_ideas') }

    @{ key='AUDIENCE_INTELLIGENCE'; title='Audience Intelligence'; group='growth';
       path=@('audience','segment','viewer'); code=@('audience[_\-]?state','AudienceIntelligence','audience_segment','non_follower');
       output=@('audience'); metric=@('audience_segments','audience_updated') }

    @{ key='HOOK_LAB'; title='Hook & Retention Lab'; group='growth';
       path=@('hook'); code=@('hook[_\-]?candidate','HookLab','winning_hook','hook_type');
       output=@('hook'); metric=@('hook_candidates','hook_win_rate','hold_rate_3s') }

    @{ key='PATTERN_MEMORY'; title='Viral Format / Pattern Memory'; group='growth';
       path=@('pattern','winner','viral','memory'); code=@('pattern[_\-]?memory','winning_pattern','viral_pattern','format_weight');
       output=@('pattern','winner'); metric=@('patterns_stored','pattern_weight') }

    @{ key='COMPETITOR_INTEL'; title='Competitor Intelligence'; group='growth';
       path=@('competitor','benchmark'); code=@('competitor[_\-]?pattern','CompetitorIntel','competitor_memory');
       output=@('competitor'); metric=@('competitors_tracked','patterns_extracted') }

    @{ key='RETENTION_ENGINE'; title='Retention Engine'; group='growth';
       path=@('retention','dropoff','drop[_\-]?off'); code=@('retention_failure','RetentionEngine','drop_off_reason','watch_time');
       output=@('retention'); metric=@('retention_rate','completion_rate','drop_off_second') }

    @{ key='PACKAGING'; title='Packaging'; group='growth';
       path=@('packag','cover','thumbnail','caption'); code=@('PackagingAgent','cover_selection','first_frame','caption_opening');
       output=@('cover','thumbnail','caption'); metric=@('cover_ctr','packaging_score') }

    @{ key='CADENCE_OPTIMIZER'; title='Distribution / Cadence Optimizer'; group='growth';
       path=@('cadence','schedul','posting','distribut'); code=@('posting_window','CadenceOptimizer','best_hour','publish_schedule');
       output=@('cadence','schedule','posting'); metric=@('posting_window_score','publish_interval') }

    @{ key='COMMUNITY_FEEDBACK'; title='Community Feedback Loop'; group='growth';
       path=@('comment','community','dm','feedback'); code=@('community_feedback','CommunityFeedback','comment_insight');
       output=@('comment','community','feedback'); metric=@('comments_processed','feedback_signals') }

    @{ key='FOLLOW_CONVERSION'; title='Follow Conversion Engine'; group='growth';
       path=@('follow','conversion','funnel'); code=@('follow_per_1000','FollowConversion','profile_visit','follow_conversion');
       output=@('follow','conversion'); metric=@('follow_per_1000_views','profile_visits','follows') }

    @{ key='EXPERIMENT_ENGINE'; title='Experiment Engine'; group='growth';
       path=@('experiment','ab[_\-]?test','trial'); code=@('ExperimentEngine','hypothesis','challenger','primary_kpi');
       output=@('experiment'); metric=@('experiments_running','experiments_decided') }

    @{ key='NOVELTY_WATCH'; title='Creative Novelty Watch'; group='growth';
       path=@('novelty','fatigue','diversity','repetit'); code=@('novelty_score','NoveltyWatch','fatigue','repetition_count');
       output=@('novelty','diversity'); metric=@('novelty_score','repetition_rate') }

    @{ key='CHARACTER_CONTINUITY'; title='Character Continuity'; group='growth';
       path=@('continuity','character','persona','sofia_memory','arc'); code=@('character_continuity','story_arc','persona_state','outfit');
       output=@('continuity','character','persona'); metric=@('continuity_checks','arc_state') }
)

# ==========================================================================
#  Отчёт
# ==========================================================================

$script:Report = [ordered]@{
    generated_at = (Get-Date).ToString('o')
    host         = $env:COMPUTERNAME
    tool         = 'audit_agent_matrix'
    sofia_root   = $null
    fresh_hours  = $FreshHours
    reachable    = $false
    index        = [ordered]@{}
    roles        = @()
    orchestration= @()
    retire       = @()
    duplicates   = @()
    totals       = [ordered]@{}
    verdict      = 'NOT_MEASURED'
    notes        = @()
}

function Add-Note {
    param([string] $Text)
    $script:Report.notes += $Text
    Write-Host ("  ! {0}" -f $Text) -ForegroundColor DarkYellow
}

# ==========================================================================
#  0. Корень и индекс
# ==========================================================================

Write-SofiaHead 'REAL AGENT MATRIX — 0. дерево студии'

$root = Resolve-SofiaRoot -Hint $SofiaRoot
if (-not $root) {
    Write-Host ''
    Write-Host '  Дерево Sofia AI Studio не найдено на этой машине.' -ForegroundColor Magenta
    Write-Host '  Аудит агентов возможен только там, где лежит студия.' -ForegroundColor Magenta
    Write-Host ''
    Write-Host '  Запустите на машине студии или укажите корень явно:' -ForegroundColor White
    Write-Host '    .\audit_agent_matrix.ps1 -SofiaRoot ''D:\AI_CONTENT\Sofia''' -ForegroundColor White
    Write-Host ''
    $script:Report.verdict = 'BLOCKED'
    $script:Report.notes  += 'sofia root not found: аудит не выполнялся'
    $p = Save-SofiaReport -Report $script:Report -OutDir $OutDir -FileName 'agent_matrix.json'
    Write-Host ("  Отчёт: {0}" -f $p) -ForegroundColor DarkGray
    exit 2
}

$script:Report.sofia_root = $root
$script:Report.reachable  = $true
Write-Host ("  Корень    : {0}" -f $root) -ForegroundColor White

$index = New-SofiaIndex -Root $root
$script:Report.index = [ordered]@{
    files      = $index.Count
    truncated  = $index.Truncated
    scan_ms    = $index.ScanMs
}
Write-Host ("  Файлов    : {0} (обход {1} мс)" -f $index.Count, $index.ScanMs) -ForegroundColor White
if ($index.Truncated) { Add-Note 'индекс усечён лимитом файлов: часть дерева не просмотрена' }
if ($index.Count -eq 0) {
    Add-Note 'в дереве не прочитано ни одного файла — проверьте права доступа'
}

# живость
$procProbe = Get-SofiaProcesses -Root $root
$taskProbe = Get-SofiaScheduledTasks -Root $root

if (-not $procProbe.Available) { Add-Note 'список процессов недоступен (нужны права) — улика RUNNER по процессам не собрана' }
if (-not $taskProbe.Available) { Add-Note 'планировщик недоступен (нужны права) — улика RUNNER по задачам не собрана' }

$procs = @($procProbe.Items)
$tasks = @($taskProbe.Items)
$script:Report.index.processes_available = $procProbe.Available
$script:Report.index.scheduler_available = $taskProbe.Available

Write-Host ("  Процессов : {0}" -f @($procs).Count) -ForegroundColor White
Write-Host ("  Задач     : {0}" -f @($tasks).Count) -ForegroundColor White

# ==========================================================================
#  1. Один проход по содержимому
# ==========================================================================
#  Отдельный поиск на каждую роль — это 24 обхода дерева. Вместо этого один
#  проход по объединённому выражению, потом попадания раскладываются по ролям.

Write-SofiaHead 'REAL AGENT MATRIX — 1. сбор улик по коду'

$allCodePatterns = @()
foreach ($r in $script:Roles) { $allCodePatterns += $r.code }
$combined = '(' + (($allCodePatterns | Sort-Object -Unique) -join '|') + ')'

$contentHits = Search-SofiaContent -Index $index -Pattern $combined -Kind 'codeconf' `
                                   -MaxScan $MaxScanFiles -MaxHits 8000
Write-Host ("  Совпадений в коде/конфигах: {0}" -f @($contentHits).Count) -ForegroundColor White

# точки входа: файл, который вообще можно запустить
$entryHits = Search-SofiaContent -Index $index -Pattern '__main__|^\s*param\s*\(|argparse|click\.command|def main\s*\(' `
                                 -Kind 'code' -MaxScan $MaxScanFiles -MaxHits 8000
$entryFiles = @{}
foreach ($h in $entryHits) { $entryFiles[$h.Path.ToLowerInvariant()] = $true }
Write-Host ("  Файлов с точкой входа     : {0}" -f $entryFiles.Count) -ForegroundColor White

# свежие ошибки в логах
$errorHits = Search-SofiaContent -Index $index -Pattern 'Traceback|CRITICAL|\bERROR\b|Exception|FAILED' `
                                 -Kind 'log' -MaxScan 400 -MaxHits 2000
Write-Host ("  Строк с ошибками в логах  : {0}" -f @($errorHits).Count) -ForegroundColor White

$freshAll = Get-SofiaFresh -Files $index.Files -Hours $FreshHours
Write-Host ("  Файлов изменено за {0} ч   : {1}" -f $FreshHours, @($freshAll).Count) -ForegroundColor White

# ==========================================================================
#  2. Классификация ролей
# ==========================================================================

Write-SofiaHead 'REAL AGENT MATRIX — 2. классификация ролей'

function Test-AnyMatch {
    param([string] $Text, [string[]] $Patterns)
    if (-not $Text) { return $false }
    foreach ($p in $Patterns) { if ($Text -match $p) { return $true } }
    return $false
}

$roleRows = @()

foreach ($role in $script:Roles) {

    # --- кандидаты в реализацию: путь ИЛИ содержимое
    $byPath = @(Select-SofiaPath -Index $index -Patterns $role.path -Kind 'code' -Limit 200)

    $byCode = @()
    foreach ($h in $contentHits) {
        if (Test-AnyMatch -Text $h.Text -Patterns $role.code) { $byCode += $h }
    }

    $implPaths = @{}
    foreach ($f in $byPath) { $implPaths[$f.Full.ToLowerInvariant()] = $f }
    foreach ($h in $byCode) {
        $k = $h.Path.ToLowerInvariant()
        if ($implPaths.ContainsKey($k)) { continue }
        $fi = $index.Files | Where-Object { $_.Full -ieq $h.Path } | Select-Object -First 1
        if (-not $fi) { continue }
        # упоминание в metrics.json или в отчёте — это не реализация роли:
        # реализацией считается только код, иначе метрика сама себя назначит агентом
        if (-not $fi.IsCode) { continue }
        $implPaths[$k] = $fi
    }
    $impl = @($implPaths.Values)

    # --- 1. RUNNER
    $runnerEvidence = @()
    foreach ($t in $tasks) {
        if (Test-AnyMatch -Text $t.Command -Patterns ($role.path + $role.code)) {
            $runnerEvidence += ('scheduler:' + $t.Name)
        }
    }
    foreach ($p in $procs) {
        if (Test-AnyMatch -Text $p.CmdLine -Patterns ($role.path + $role.code)) {
            $runnerEvidence += ('process:' + $p.Pid + ':' + $p.Name)
        }
    }
    foreach ($f in $impl) {
        if ($entryFiles.ContainsKey($f.Full.ToLowerInvariant())) {
            $runnerEvidence += ('entrypoint:' + $f.Rel)
        }
    }
    # регистрация в оркестраторе: имя роли встречается в конфиге, а не только в своём же коде
    $registered = @()
    foreach ($h in $byCode) {
        $rl = $h.Rel.ToLowerInvariant()
        if ($rl -match '\\?(config|configs|registry|agents?\.(json|yaml|yml)|orchestrat)') {
            $registered += $h.Rel
        }
    }
    if ($registered.Count -gt 0) { $runnerEvidence += ('registered:' + (($registered | Select-Object -Unique -First 3) -join ',')) }

    $hasRunner = $runnerEvidence.Count -gt 0

    # --- 2. EXECUTION
    $execEvidence = @()
    $roleLogs = @(Select-SofiaPath -Index $index -Patterns ($role.path) -Kind 'log' -Limit 120)
    $freshLogs = @(Get-SofiaFresh -Files $roleLogs -Hours $FreshHours)
    if ($freshLogs.Count -gt 0) {
        $nl = Get-SofiaNewest -Files $freshLogs
        $execEvidence += ('log:' + $nl.Rel + ' (' + (Format-SofiaAge -Time $nl.Modified) + ')')
    }
    foreach ($t in $tasks) {
        if (-not (Test-AnyMatch -Text $t.Command -Patterns ($role.path + $role.code))) { continue }
        if ($t.LastRun -and $t.LastRun -ge (Get-Date).AddHours(-1 * $FreshHours)) {
            $execEvidence += ('scheduler_last_run:' + $t.Name + ' (' + (Format-SofiaAge -Time $t.LastRun) + ')')
        }
    }
    foreach ($p in $procs) {
        if (Test-AnyMatch -Text $p.CmdLine -Patterns ($role.path + $role.code)) {
            $execEvidence += ('running:' + $p.Pid)
        }
    }
    $freshImpl = @(Get-SofiaFresh -Files $impl -Hours $FreshHours)
    $hasExec = $execEvidence.Count -gt 0

    # --- 3. OUTPUT
    $outFiles   = @(Select-SofiaPath -Index $index -Patterns $role.output -Kind 'any' -Limit 600)
    $outFiles   = @($outFiles | Where-Object { -not $_.IsCode })
    $freshOut   = @(Get-SofiaFresh -Files $outFiles -Hours $FreshHours)
    $newestOut  = Get-SofiaNewest -Files $outFiles
    $hasOutput  = $freshOut.Count -gt 0

    # --- 4. CONSUMER: output читает кто-то, кроме самого агента
    $consumers = @()
    foreach ($h in $contentHits) {
        if (-not (Test-AnyMatch -Text $h.Text -Patterns $role.output)) { continue }
        if ($implPaths.ContainsKey($h.Path.ToLowerInvariant())) { continue }
        $consumers += $h.Rel
    }
    foreach ($h in $byCode) {
        $hk = $h.Path.ToLowerInvariant()
        if ($implPaths.ContainsKey($hk)) { continue }
        $rl = $h.Rel.ToLowerInvariant()
        if ($rl -match 'orchestrat|director|dashboard|registry|pipeline|planner') { $consumers += $h.Rel }
    }
    $consumers   = @($consumers | Select-Object -Unique)
    $hasConsumer = $consumers.Count -gt 0

    # --- 5. METRIC
    $metricHits = @()
    foreach ($m in $role.metric) {
        $mh = @(Search-SofiaContent -Index $index -Pattern ([regex]::Escape($m)) -Kind 'conf' -MaxScan 1500 -MaxHits 5)
        foreach ($x in $mh) { $metricHits += ($m + ' @ ' + $x.Rel) }
    }
    $hasMetric = $metricHits.Count -gt 0

    # --- ошибки
    $roleErrors = @()
    foreach ($e in $errorHits) {
        if (Test-AnyMatch -Text $e.Rel -Patterns $role.path) { $roleErrors += ($e.Rel + ':' + $e.Line) }
    }
    $roleErrors = @($roleErrors | Select-Object -Unique -First 5)

    # --- дубли: несколько независимых точек входа в разных каталогах
    $entryDirs = @{}
    foreach ($f in $impl) {
        if (-not $entryFiles.ContainsKey($f.Full.ToLowerInvariant())) { continue }
        $d = Split-Path $f.Rel -Parent
        if (-not $d) { $d = '.' }
        if (-not $entryDirs.ContainsKey($d)) { $entryDirs[$d] = @() }
        $entryDirs[$d] += $f.Rel
    }
    $duplicateRunners = @()
    if ($entryDirs.Count -ge 2) {
        foreach ($d in $entryDirs.Keys) { $duplicateRunners += $entryDirs[$d] }
    }

    # --- класс
    $score = 0
    if ($hasRunner)   { $score++ }
    if ($hasExec)     { $score++ }
    if ($hasOutput)   { $score++ }
    if ($hasConsumer) { $score++ }
    if ($hasMetric)   { $score++ }

    if ($impl.Count -eq 0 -and -not $hasRunner -and -not $hasOutput) {
        $class = 'MISSING'
    } elseif (-not $hasRunner -and -not $hasExec) {
        $class = 'SPEC_ONLY'
    } elseif ($hasRunner -and $hasExec -and $roleErrors.Count -gt 0 -and -not $hasOutput) {
        $class = 'BROKEN'
    } elseif ($hasRunner -and -not $hasExec -and -not $hasOutput) {
        $class = 'BROKEN'
    } elseif ($score -eq 5) {
        $class = 'ACTIVE_REAL'
    } else {
        $class = 'PARTIAL'
    }

    if ($class -in @('ACTIVE_REAL','PARTIAL') -and $duplicateRunners.Count -ge 2) {
        $class = 'DUPLICATE'
        $script:Report.duplicates += [ordered]@{
            role    = $role.key
            runners = @($duplicateRunners | Select-Object -Unique -First 8)
        }
    }

    # чего не хватает, чтобы дотянуть до ACTIVE_REAL
    $gaps = @()
    if (-not $hasRunner)   { $gaps += 'RUNNER: никто не запускает' }
    if (-not $hasExec)     { $gaps += ('EXECUTION: нет следов запуска за ' + $FreshHours + ' ч') }
    if (-not $hasOutput)   { $gaps += ('OUTPUT: нет свежих артефактов за ' + $FreshHours + ' ч') }
    if (-not $hasConsumer) { $gaps += 'CONSUMER: output никто не читает' }
    if (-not $hasMetric)   { $gaps += 'METRIC: нет метрики успеха' }

    $row = [ordered]@{
        role              = $role.key
        title             = $role.title
        group             = $role.group
        class             = $class
        score             = $score
        implementation    = @($impl | Select-Object -First 8 | ForEach-Object { $_.Rel })
        implementation_n  = $impl.Count
        runner            = @($runnerEvidence | Select-Object -Unique -First 6)
        execution         = @($execEvidence   | Select-Object -Unique -First 6)
        output_fresh_n    = $freshOut.Count
        output_newest     = if ($newestOut) { $newestOut.Rel } else { $null }
        output_newest_age = if ($newestOut) { Format-SofiaAge -Time $newestOut.Modified } else { 'никогда' }
        consumers         = @($consumers | Select-Object -First 6)
        metrics           = @($metricHits | Select-Object -First 6)
        errors            = $roleErrors
        gaps              = $gaps
    }
    $roleRows += $row

    $color = Get-SofiaStatusColor -Status $class
    Write-Host ("  [{0,-11}] {1,-32} {2}/5  {3}" -f $class, $role.title, $score, (($gaps | Select-Object -First 2) -join '; ')) -ForegroundColor $color
}

$script:Report.roles = $roleRows

# ==========================================================================
#  3. Таблица оркестрации
# ==========================================================================

Write-SofiaHead 'REAL AGENT MATRIX — 3. таблица оркестрации'

foreach ($r in $roleRows) {
    $status = switch ($r.class) {
        'ACTIVE_REAL' { if (@($r.execution) -join ' ' -match 'running:') { 'BUSY' } else { 'ACTIVE' } }
        'PARTIAL'     { 'DEGRADED' }
        'DUPLICATE'   { 'DEGRADED' }
        'BROKEN'      { 'BROKEN' }
        'SPEC_ONLY'   { 'DISABLED' }
        'MISSING'     { 'DISABLED' }
        default       { 'IDLE' }
    }

    $lastRun = 'NOT_MEASURED'
    foreach ($e in @($r.execution)) {
        if ($e -match '\(([^)]+)\)') { $lastRun = $Matches[1]; break }
        if ($e -match '^running:')   { $lastRun = 'сейчас'; break }
    }

    $nextRun = 'NOT_MEASURED'
    foreach ($t in $tasks) {
        if (Test-AnyMatch -Text $t.Command -Patterns @($r.role.ToLowerInvariant())) {
            if ($t.NextRun) { $nextRun = $t.NextRun.ToString('yyyy-MM-dd HH:mm') }
            break
        }
    }

    $script:Report.orchestration += [ordered]@{
        agent    = $r.role
        owner    = 'MASTER_ORCHESTRATOR'
        task     = $r.title
        status   = $status
        input    = if (@($r.runner).Count) { @($r.runner)[0] } else { 'NOT_MEASURED' }
        output   = if ($r.output_newest) { $r.output_newest } else { 'NOT_MEASURED' }
        last_run = $lastRun
        next_run = $nextRun
        error    = if (@($r.errors).Count) { @($r.errors)[0] } else { '' }
    }
}

$fmt = "  {0,-24} {1,-10} {2,-16} {3}"
Write-Host ($fmt -f 'AGENT','STATUS','LAST_RUN','ERROR') -ForegroundColor White
foreach ($o in $script:Report.orchestration) {
    $c = Get-SofiaStatusColor -Status $(if ($o.status -in @('ACTIVE','BUSY')) { 'PASS' } elseif ($o.status -eq 'DEGRADED') { 'WARN' } elseif ($o.status -eq 'BROKEN') { 'FAIL' } else { 'SPEC_ONLY' })
    Write-Host ($fmt -f $o.agent, $o.status, $o.last_run, $o.error) -ForegroundColor $c
}

# ==========================================================================
#  4. Кандидаты на RETIRE
# ==========================================================================
#  Сущность с точкой входа, но без недавних запусков и без потребителя —
#  это и есть «мёртвый агент». Скрипт только называет их; удаление и
#  отключение — отдельное решение, здесь ничего не трогается.

Write-SofiaHead 'REAL AGENT MATRIX — 4. кандидаты на RETIRE'

$agentLike = @(Select-SofiaPath -Index $index `
                -Patterns @('agent','critic','director','engine','orchestrat','worker','daemon') `
                -Kind 'code' -Limit 500)

$claimedByRole = @{}
foreach ($r in $roleRows) {
    foreach ($p in @($r.implementation)) { $claimedByRole[$p.ToLowerInvariant()] = $r.role }
}

$retire = @()
foreach ($f in $agentLike) {
    if (-not $entryFiles.ContainsKey($f.Full.ToLowerInvariant())) { continue }

    $stem = [System.IO.Path]::GetFileNameWithoutExtension($f.Name)
    if ($stem.Length -lt 4) { continue }

    $refs = @(Search-SofiaContent -Index $index -Pattern ([regex]::Escape($stem)) -Kind 'codeconf' -MaxScan 3000 -MaxHits 12)
    $external = @($refs | Where-Object { $_.Path -ine $f.Full })

    $isFresh = $f.Modified -ge (Get-Date).AddHours(-1 * $FreshHours)
    $scheduled = $false
    foreach ($t in $tasks) { if ($t.Command -match [regex]::Escape($stem)) { $scheduled = $true; break } }
    $runningNow = $false
    foreach ($p in $procs) { if ($p.CmdLine -match [regex]::Escape($stem)) { $runningNow = $true; break } }

    if ($external.Count -eq 0 -and -not $scheduled -and -not $runningNow -and -not $isFresh) {
        $retire += [ordered]@{
            file      = $f.Rel
            role      = if ($claimedByRole.ContainsKey($f.Full.ToLowerInvariant())) { $claimedByRole[$f.Full.ToLowerInvariant()] } else { 'UNCLAIMED' }
            modified  = $f.Modified.ToString('s')
            age       = Format-SofiaAge -Time $f.Modified
            reason    = 'есть точка входа, но нет внешних ссылок, задачи планировщика, процесса и изменений в окне свежести'
        }
    }
}
$script:Report.retire = @($retire | Select-Object -First 60)

if ($retire.Count -eq 0) {
    Write-Host '  Кандидатов нет: каждая найденная точка входа кем-то используется.' -ForegroundColor Green
} else {
    Write-Host ("  Кандидатов: {0} (ничего не удалено — только список)" -f $retire.Count) -ForegroundColor Yellow
    foreach ($x in ($retire | Select-Object -First 15)) {
        Write-Host ("    {0,-52} {1}" -f $x.file, $x.age) -ForegroundColor DarkYellow
    }
    if ($retire.Count -gt 15) { Write-Host ("    ... и ещё {0}" -f ($retire.Count - 15)) -ForegroundColor DarkGray }
}

# ==========================================================================
#  5. Итог
# ==========================================================================

Write-SofiaHead 'REAL AGENT MATRIX — итог'

$byClass = @{}
foreach ($c in @('ACTIVE_REAL','PARTIAL','SPEC_ONLY','BROKEN','DUPLICATE','MISSING')) {
    $byClass[$c] = @($roleRows | Where-Object { $_.class -eq $c }).Count
}
$script:Report.totals = [ordered]@{
    roles_total  = $roleRows.Count
    active_real  = $byClass['ACTIVE_REAL']
    partial      = $byClass['PARTIAL']
    spec_only    = $byClass['SPEC_ONLY']
    broken       = $byClass['BROKEN']
    duplicate    = $byClass['DUPLICATE']
    missing      = $byClass['MISSING']
    retire_count = $retire.Count
    core_active  = @($roleRows | Where-Object { $_.group -eq 'core'   -and $_.class -eq 'ACTIVE_REAL' }).Count
    core_total   = @($roleRows | Where-Object { $_.group -eq 'core'   }).Count
    growth_active= @($roleRows | Where-Object { $_.group -eq 'growth' -and $_.class -eq 'ACTIVE_REAL' }).Count
    growth_total = @($roleRows | Where-Object { $_.group -eq 'growth' }).Count
}

foreach ($c in @('ACTIVE_REAL','PARTIAL','DUPLICATE','BROKEN','SPEC_ONLY','MISSING')) {
    Write-Host ("  {0,-12} {1}" -f $c, $byClass[$c]) -ForegroundColor (Get-SofiaStatusColor -Status $c)
}
Write-Host ("  {0,-12} {1}" -f 'RETIRE', $retire.Count) -ForegroundColor DarkYellow

# Вердикт по матрице: он про достоверность картины, а не про здоровье студии.
if ($byClass['MISSING'] -eq $roleRows.Count) {
    $script:Report.verdict = 'FAIL'
} elseif ($byClass['BROKEN'] -gt 0 -or $byClass['DUPLICATE'] -gt 0) {
    $script:Report.verdict = 'PARTIAL'
} elseif ($byClass['ACTIVE_REAL'] -ge [math]::Ceiling($roleRows.Count * 0.6)) {
    $script:Report.verdict = 'PASS'
} else {
    $script:Report.verdict = 'PARTIAL'
}

Write-Host ''
Write-Host ("  ВЕРДИКТ МАТРИЦЫ: {0}" -f $script:Report.verdict) -ForegroundColor (Get-SofiaStatusColor -Status $script:Report.verdict)
Write-Host '  Вердикт описывает достоверность картины агентов, а не здоровье студии.' -ForegroundColor DarkGray

$reportPath = Save-SofiaReport -Report $script:Report -OutDir $OutDir -FileName 'agent_matrix.json'
Write-Host ''
Write-Host ("  Отчёт: {0}" -f $reportPath) -ForegroundColor White
Write-Host '  Следующий шаг: .\audit_growth_readiness.ps1 -MatrixReport "' -NoNewline -ForegroundColor White
Write-Host ("{0}`"" -f $reportPath) -ForegroundColor White
Write-Host ''
