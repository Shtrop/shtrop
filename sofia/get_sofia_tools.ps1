<#
.SYNOPSIS
    Скачивает актуальные версии всех инструментов Sofia в обход кэша CDN.

.DESCRIPTION
    raw.githubusercontent отдаёт файлы через кэш, поэтому повторная загрузка
    сразу после обновления репозитория может вернуть старую версию. Скрипт
    добавляет к каждому URL уникальный параметр и проверяет, что файл
    действительно обновился, печатая размер и хэш.

.PARAMETER Dest
    Куда складывать. По умолчанию текущий каталог.

.PARAMETER Branch
    Ветка репозитория. По умолчанию master.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\get_sofia_tools.ps1
#>

[CmdletBinding()]
param(
    [string] $Dest = (Get-Location).Path,
    [string] $Branch = 'master'
)

$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$files = @(
    'lib_bugcheck.ps1',
    'diagnose_host_safe_hold.ps1',
    'analyze_safehold_report.ps1',
    'analyze_minidump.ps1',
    'check_memory_storage.ps1',
    'watch_host_stability.ps1',
    'apply_safehold_fix.ps1',
    'get_sofia_tools.ps1'
)

$base = "https://raw.githubusercontent.com/Shtrop/shtrop/$Branch/sofia"
$stamp = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()

New-Item -ItemType Directory -Force -Path $Dest | Out-Null
Write-Host ''
Write-Host ("Загрузка инструментов Sofia из ветки {0}" -f $Branch) -ForegroundColor White
Write-Host ("Каталог: {0}" -f $Dest)
Write-Host ''

foreach ($f in $files) {
    $target = Join-Path $Dest $f
    $before = if (Test-Path $target) { (Get-FileHash $target -Algorithm SHA256).Hash } else { $null }
    try {
        # уникальный параметр обходит кэш CDN
        Invoke-WebRequest "$base/$f`?nocache=$stamp" -OutFile $target -UseBasicParsing -Headers @{ 'Cache-Control' = 'no-cache' }
        $after = (Get-FileHash $target -Algorithm SHA256).Hash
        $size  = (Get-Item $target).Length
        $state = if (-not $before) { 'новый' } elseif ($before -ne $after) { 'ОБНОВЛЁН' } else { 'без изменений' }
        $color = if ($state -eq 'ОБНОВЛЁН') { 'Green' } elseif ($state -eq 'новый') { 'Cyan' } else { 'DarkGray' }
        Write-Host ("  {0,-32} {1,8} Б  {2,-14} {3}" -f $f, $size, $state, $after.Substring(0,12)) -ForegroundColor $color
    } catch {
        Write-Host ("  {0,-32} ОШИБКА: {1}" -f $f, $_.Exception.Message) -ForegroundColor Red
    }
}

Write-Host ''
Write-Host 'Порядок запуска:' -ForegroundColor White
Write-Host '  .\diagnose_host_safe_hold.ps1 -Days 14   собрать доказательства'
Write-Host '  .\analyze_safehold_report.ps1            диагноз и следующий шаг'
Write-Host '  .\analyze_minidump.ps1                   код остановки из событий и дампов'
Write-Host '  .\check_memory_storage.ps1               память, WHEA, SMART, диски'
Write-Host '  .\watch_host_stability.ps1 -Hours 48     окно наблюдения для выхода из hold'
Write-Host ''
