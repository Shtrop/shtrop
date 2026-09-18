<#
.SYNOPSIS
    Прогон всех фотосессий Sofia через локальный ComfyUI на рабочий стол.

.DESCRIPTION
    Запускать НА МАШИНЕ СТУДИИ, где подняты ComfyUI и Sofia LoRA/PuLID.
    Скрипт сам находит workflow в API-формате, прогоняет сессии из build\*\batch.json
    и складывает PNG в <Рабочий стол>\Фотосессия\<сессия>.
    Ничего не публикует и не перезаписывает уже существующие файлы.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File tools\run_all.ps1

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File tools\run_all.ps1 -Sessions golden_gym -Variants 2
#>
param(
    [string]   $Workflow,
    [string]   $OutRoot = (Join-Path ([Environment]::GetFolderPath('Desktop')) 'Фотосессия'),
    [string]   $Server  = '127.0.0.1:8188',
    [string[]] $Sessions,
    [int]      $Variants,
    [string]   $Positive,
    [string]   $Negative,
    [string]   $SeedNode,
    [string]   $LatentNode,
    [double]   $Guidance,
    [int]      $Steps,
    [switch]   $DryRun
)

$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [Text.Encoding]::UTF8 } catch {}
$env:PYTHONIOENCODING = 'utf-8'

$PackRoot = Split-Path -Parent $PSScriptRoot
$Runner   = Join-Path $PSScriptRoot 'run_session.py'
if (-not (Test-Path $Runner)) { throw "Не найден $Runner" }

function Test-ApiWorkflow([string]$Path) {
    # В API-формате ключи графа — номера узлов, у каждого есть class_type.
    try {
        $json = Get-Content -Raw -Encoding UTF8 $Path | ConvertFrom-Json
    } catch { return $false }
    if ($json.PSObject.Properties.Name -contains 'nodes') { return $false }
    foreach ($prop in $json.PSObject.Properties) {
        if ($prop.Value.PSObject.Properties.Name -contains 'class_type') { return $true }
    }
    return $false
}

# --- python -------------------------------------------------------------
$Python = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $Python) { $Python = (Get-Command py -ErrorAction SilentlyContinue).Source }
if (-not $Python) { throw 'Python не найден в PATH. Установите Python 3.11+ и повторите.' }

# --- ComfyUI ------------------------------------------------------------
Write-Host "Проверяю ComfyUI на http://$Server ..."
try {
    Invoke-RestMethod -Uri "http://$Server/system_stats" -TimeoutSec 6 | Out-Null
    Write-Host '  ComfyUI отвечает.' -ForegroundColor Green
} catch {
    throw "ComfyUI не отвечает на http://$Server. Запустите ComfyUI и повторите."
}

# --- workflow -----------------------------------------------------------
$videoHints = @('i2v', 't2v', 'wan', 'video', 'reel', 'anim', 'latentsync', 'svd')
$photoHints = @('flux', 'photo', 'foto', 'image', 'portrait', 'sdxl', 'pulid')

function Get-WorkflowRank([string]$Path) {
    # Чем меньше, тем лучше: фото-графы вперёд, видео-графы в конец.
    $name = (Split-Path -Leaf $Path).ToLower()
    if ($videoHints | Where-Object { $name -like "*$_*" }) { return 2 }
    if ($photoHints | Where-Object { $name -like "*$_*" }) { return 0 }
    return 1
}

$candidates = @()
if (-not $Workflow) {
    Write-Host 'Ищу workflow в API-формате ...'
    $searchDirs = @(
        'D:\AI_CONTENT\Sofia\workflows',
        (Join-Path $PackRoot 'workflows'),
        $PSScriptRoot
    ) | Where-Object { Test-Path $_ }
    foreach ($dir in $searchDirs) {
        Get-ChildItem -Path $dir -Filter *.json -Recurse -ErrorAction SilentlyContinue |
            Where-Object { Test-ApiWorkflow $_.FullName } |
            ForEach-Object { $candidates += $_.FullName }
    }
    $candidates = $candidates | Sort-Object { Get-WorkflowRank $_ }, { (Get-Item $_).LastWriteTime } -Descending:$false
    $Workflow = $candidates | Select-Object -First 1
}

if (-not $Workflow) {
    Write-Host 'Не нашёл ни одного workflow в API-формате.' -ForegroundColor Red
    Write-Host 'В ComfyUI: Workflow -> Export (API). Затем осмотрите файлы:'
    Write-Host "  python `"$PSScriptRoot\inspect_workflows.py`" D:\AI_CONTENT\Sofia\workflows"
    throw 'Нет workflow для прогона.'
}
if (-not (Test-ApiWorkflow $Workflow)) {
    throw "Файл $Workflow не в API-формате. В ComfyUI: Workflow -> Export (API)."
}
Write-Host "  Workflow: $Workflow" -ForegroundColor Green
if ((Get-WorkflowRank $Workflow) -eq 2) {
    Write-Host '  ВНИМАНИЕ: имя файла похоже на видео-пайплайн (i2v/Wan), а не на фото-граф.' -ForegroundColor Yellow
    Write-Host '  Если кадры не получатся, осмотрите все графы:' -ForegroundColor Yellow
    Write-Host "    python `"$PSScriptRoot\inspect_workflows.py`" D:\AI_CONTENT\Sofia\workflows" -ForegroundColor Yellow
}
if ($candidates.Count -gt 1) {
    Write-Host "  (найдено кандидатов: $($candidates.Count); переопределить: -Workflow <путь>)"
}

# --- сессии -------------------------------------------------------------
$batches = Get-ChildItem -Path (Join-Path $PackRoot 'build') -Filter batch.json -Recurse |
           Sort-Object FullName
if ($Sessions) {
    $batches = $batches | Where-Object { $Sessions -contains $_.Directory.Name }
    if (-not $batches) { throw "Сессии не найдены: $($Sessions -join ', ')" }
}

New-Item -ItemType Directory -Force -Path $OutRoot | Out-Null
Write-Host "Каталог вывода: $OutRoot`n"

$failed = @()
foreach ($batch in $batches) {
    $slug = $batch.Directory.Name
    $out  = Join-Path $OutRoot $slug
    Write-Host "=== $slug ===" -ForegroundColor Cyan

    $params = @('--batch', $batch.FullName, '--workflow', $Workflow, '--out', $out, '--server', $Server)
    if ($Variants)   { $params += @('--variants', $Variants) }
    if ($Positive)   { $params += @('--positive', $Positive) }
    if ($Negative)   { $params += @('--negative', $Negative) }
    if ($SeedNode)   { $params += @('--seed-node', $SeedNode) }
    if ($LatentNode) { $params += @('--latent-node', $LatentNode) }
    if ($Guidance)   { $params += @('--guidance', $Guidance) }
    if ($Steps)      { $params += @('--steps', $Steps) }
    if ($DryRun)     { $params += '--dry-run' }

    & $Python $Runner @params
    if ($LASTEXITCODE -ne 0) { $failed += $slug }
    Write-Host ''
}

if ($failed) {
    Write-Host "Сессии с ошибками: $($failed -join ', ')" -ForegroundColor Yellow
    Write-Host 'Подробности — в run_manifest.json внутри каждой папки.'
} else {
    Write-Host 'Все сессии прогнаны без ошибок.' -ForegroundColor Green
}
Write-Host "Фото: $OutRoot"
if (-not $DryRun) { Start-Process explorer.exe $OutRoot }
