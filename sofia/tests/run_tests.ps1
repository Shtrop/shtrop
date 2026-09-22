<#
.SYNOPSIS
    Запускает тесты инструментов sofia/.

.DESCRIPTION
    Каждый файл *.tests.ps1 выполняется в отдельном процессе PowerShell:
    тесты правят PATH и глобальные переменные, поэтому изоляция обязательна.

    Ничего в дереве студии не трогается — только временные каталоги.

.EXAMPLE
    pwsh -NoProfile -File .\run_tests.ps1

.EXAMPLE
    pwsh -NoProfile -File .\run_tests.ps1 -Filter watch
#>

[CmdletBinding()]
param(
    [string] $Filter = '',
    # Служебные параметры запуска одного файла в дочернем процессе.
    [switch] $Child,
    [string] $File = ''
)

$ErrorActionPreference = 'Stop'

if ($Child) {
    . (Join-Path $PSScriptRoot 'lib_testkit.ps1')
    Write-Host ("`n=== {0} ===" -f (Split-Path $File -Leaf)) -ForegroundColor Cyan
    . $File
    $failed = @($global:SofiaTestResults | Where-Object Status -eq 'FAIL')
    exit ([math]::Min($failed.Count, 250))
}

$files = @(Get-ChildItem -Path $PSScriptRoot -Filter '*.tests.ps1' -File | Sort-Object Name)
if ($Filter) { $files = @($files | Where-Object { $_.Name -like "*$Filter*" }) }

if ($files.Count -eq 0) {
    Write-Host 'Тестовых файлов не найдено.' -ForegroundColor Yellow
    exit 1
}

$pwshPath = (Get-Process -Id $PID).Path
if (-not $pwshPath) { $pwshPath = 'pwsh' }

$totalFailed = 0
foreach ($f in $files) {
    & $pwshPath -NoLogo -NoProfile -File $PSCommandPath -Child -File $f.FullName
    $totalFailed += $LASTEXITCODE
}

Write-Host ''
Write-Host ('=' * 70) -ForegroundColor DarkCyan
if ($totalFailed -eq 0) {
    Write-Host ("  ВСЕ ТЕСТЫ ПРОЙДЕНЫ  ({0} файлов)" -f $files.Count) -ForegroundColor Green
} else {
    Write-Host ("  ПРОВАЛЕНО ТЕСТОВ: {0}  ({1} файлов)" -f $totalFailed, $files.Count) -ForegroundColor Red
}
Write-Host ('=' * 70) -ForegroundColor DarkCyan
exit ([math]::Min($totalFailed, 250))
