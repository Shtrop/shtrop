<#
.SYNOPSIS
    Автопилот: находит граф, прогоняет фотосессии Sofia и собирает контактный лист.

.DESCRIPTION
    Одна команда на весь цикл. Сам ищет фото-workflow в API-формате, ставит настройки
    против пластика и за сходство, прогоняет сессии, продолжает с места обрыва
    и в конце собирает HTML-лист со всеми кадрами.
    Ничего не публикует, существующие файлы не перезаписывает.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File tools\autopilot.ps1

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File tools\autopilot.ps1 -Grid -Sessions corset_cellar
#>
param(
    [string]   $Workflow,
    [string]   $OutRoot  = (Join-Path ([Environment]::GetFolderPath('Desktop')) 'Фотосессия'),
    [string]   $Server   = '127.0.0.1:8188',
    [int]      $Variants = 1,
    [double]   $Guidance = 2.2,
    [int]      $Steps    = 40,
    [double]   $Identity = 0.9,
    [double]   $Lora     = 0.8,
    [switch]   $KeepDetailer,
    [switch]   $Grid,
    [switch]   $Redo,
    [switch]   $NoOpen,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $Sessions
)

$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [Text.Encoding]::UTF8 } catch {}
$env:PYTHONIOENCODING = 'utf-8'

if ($Sessions) {
    $Sessions = @(
        $Sessions |
            ForEach-Object { $_ -split '[,;]' } |
            ForEach-Object { $_.Trim() } |
            Where-Object { $_ -ne '' }
    )
}
if ($Server -notmatch '^[\w\.\-]+:\d+$') {
    throw "Адрес ComfyUI выглядит неверно: '$Server'. Ожидается вид 127.0.0.1:8188."
}

$Pack   = Split-Path -Parent $PSScriptRoot
$Python = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $Python) { $Python = (Get-Command py -ErrorAction SilentlyContinue).Source }
if (-not $Python) { throw 'Python не найден в PATH.' }

function Step([string]$Text) { Write-Host "`n=== $Text ===" -ForegroundColor Cyan }

# --- 1. ComfyUI --------------------------------------------------------
Step "Проверяю ComfyUI на http://$Server"
try {
    Invoke-RestMethod -Uri "http://$Server/system_stats" -TimeoutSec 8 | Out-Null
    Write-Host '  отвечает' -ForegroundColor Green
} catch {
    throw "ComfyUI не отвечает на http://$Server. Запустите ComfyUI и повторите."
}

# --- 2. Граф -----------------------------------------------------------
Step 'Ищу фото-workflow'
if (-not $Workflow) {
    $dirs = @('D:\AI_CONTENT\Sofia\workflows', (Join-Path $Pack 'workflows')) |
            Where-Object { Test-Path $_ }
    if (-not $dirs) { throw 'Каталог с workflow не найден. Укажите -Workflow <путь>.' }
    $Workflow = & $Python (Join-Path $PSScriptRoot 'inspect_workflows.py') @dirs --pick 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $Workflow) {
        throw ('Фото-workflow не найден. В ComfyUI: Workflow -> Export (API), ' +
               'затем autopilot.ps1 -Workflow <путь>.')
    }
    $Workflow = $Workflow.Trim()
}
Write-Host "  $Workflow" -ForegroundColor Green

# --- 3. Сетка подбора (по желанию) -------------------------------------
if ($Grid) {
    Step 'Сетка подбора параметров'
    $first = if ($Sessions) { $Sessions[0] } else { 'corset_cellar' }
    $batch = Join-Path $Pack "build\$first\batch.json"
    if (-not (Test-Path $batch)) { throw "Нет сессии '$first' в build." }
    $gridOut = Join-Path $OutRoot '_grid'
    $gridArgs = @('--batch', $batch, '--workflow', $Workflow, '--out', $gridOut,
                  '--server', $Server, '--guidance', '1.8', '2.2', '3.5',
                  '--identity', '0.75', '0.9', '--steps', $Steps)
    if (-not $KeepDetailer) { $gridArgs += '--no-detailer' }
    & $Python (Join-Path $PSScriptRoot 'ab_grid.py') @gridArgs
    & $Python (Join-Path $PSScriptRoot 'contact_sheet.py') $gridOut
    Write-Host "`nСетка готова: $gridOut" -ForegroundColor Green
    Write-Host 'Выберите сочетание и запустите автопилот с -Guidance и -Identity из имени папки.'
    if (-not $NoOpen) { Start-Process (Join-Path $gridOut 'index.html') }
    return
}

# --- 4. Прогон ---------------------------------------------------------
Step 'Прогон сессий'
$runArgs = @('-Workflow', $Workflow, '-OutRoot', $OutRoot, '-Server', $Server,
             '-Variants', $Variants, '-Guidance', $Guidance, '-Steps', $Steps,
             '-Identity', $Identity, '-Lora', $Lora)
if (-not $KeepDetailer) { $runArgs += '-NoDetailer' }
if ($Redo)              { $runArgs += '-Redo' }
if ($Sessions)          { $runArgs += @('-Sessions') + $Sessions }

& powershell -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'run_all.ps1') @runArgs

# --- 5. Контактный лист ------------------------------------------------
Step 'Собираю контактный лист'
& $Python (Join-Path $PSScriptRoot 'contact_sheet.py') $OutRoot

$png = @(Get-ChildItem -Path $OutRoot -Filter *.png -Recurse -ErrorAction SilentlyContinue)
$fails = 0
Get-ChildItem -Path $OutRoot -Filter run_manifest.json -Recurse -ErrorAction SilentlyContinue |
    ForEach-Object {
        try { $fails += (Get-Content -Raw $_.FullName | ConvertFrom-Json).failed.Count } catch {}
    }

Step 'Итог'
Write-Host "  кадров на диске: $($png.Count)"
Write-Host "  сбоев по манифестам: $fails"
Write-Host "  каталог: $OutRoot"
Write-Host '  публикация не выполнялась'
if (-not $NoOpen) { Start-Process (Join-Path $OutRoot 'index.html') }
