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
if (-not $Workflow) {
    Write-Host 'Ищу workflow в API-формате ...'
    $searchDirs = @(
        'D:\AI_CONTENT\Sofia\workflows',
        (Join-Path $PackRoot 'workflows'),
        $PSScriptRoot
    ) | Where-Object { Test-Path $_ }
    foreach ($dir in $searchDirs) {
        $found = Get-ChildItem -Path $dir -Filter *.json -Recurse -ErrorAction SilentlyContinue |
                 Sort-Object LastWriteTime -Descending |
                 Where-Object { Test-ApiWorkflow $_.FullName } |
                 Select-Object -First 1
        if ($found) { $Workflow = $found.FullName; break }
    }
}
if (-not $Workflow) {
    throw 'Не нашёл workflow в API-формате. В ComfyUI: Workflow -> Export (API), затем укажите -Workflow <путь>.'
}
if (-not (Test-ApiWorkflow $Workflow)) {
    throw "Файл $Workflow не в API-формате. В ComfyUI: Workflow -> Export (API)."
}
Write-Host "  Workflow: $Workflow" -ForegroundColor Green

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
    if ($Variants) { $params += @('--variants', $Variants) }
    if ($DryRun)   { $params += '--dry-run' }

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
