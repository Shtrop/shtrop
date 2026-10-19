<#
.SYNOPSIS
    Growth Engine Sofia — весь недельный цикл одной командой.

.DESCRIPTION
    Проверяет наличие реальных публикаций, собирает Insights, считает KPI,
    обновляет growth memory, пересобирает бэклог и готовит контент-план.

    Подлинность выгрузок определяется сверкой media_id с журналом публикатора,
    а не именем каталога. Ничего не публикует и не снимает HOLD.

.EXAMPLE
    .\sofia_growth\run_growth.ps1
    .\sofia_growth\run_growth.ps1 -Studio "D:\AI_CONTENT\Sofia" -Account sofia
#>
[CmdletBinding()]
param(
    [string]$Studio = "D:\AI_CONTENT\Sofia",
    [string]$Account = "",
    [int]$Days = 30,
    [int]$PlanDays = 14
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

$python = (Get-Command python -ErrorAction SilentlyContinue)
if (-not $python) { throw "Python не найден в PATH. Нужен Python 3.11+." }

$version = & python -c "import sys;print('%d.%d' % sys.version_info[:2])"
Write-Host "Python $version | студия: $Studio" -ForegroundColor Cyan
if ([version]$version -lt [version]"3.11") { throw "Нужен Python 3.11+, найден $version." }

if (-not (Test-Path $Studio)) {
    Write-Warning "Каталог студии не найден: $Studio. Цикл отработает по уже собранным данным."
    & python "$root\sofia_growth\tools\growth_cycle.py" --days $Days --plan-days $PlanDays
    exit $LASTEXITCODE
}

& python "$root\sofia_growth\tools\growth_cycle.py" `
    --studio $Studio --account $Account --days $Days --plan-days $PlanDays

if ($LASTEXITCODE -ne 0) {
    Write-Warning "Часть стадий помечена BLOCKED — смотрите вывод выше. Метрики не подменяются нулями."
}
exit $LASTEXITCODE
