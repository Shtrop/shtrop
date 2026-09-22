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
    'lib_gpu_owners.ps1',
    'lib_task_results.ps1',
    'diagnose_host_safe_hold.ps1',
    'analyze_safehold_report.ps1',
    'analyze_minidump.ps1',
    'check_memory_storage.ps1',
    'watch_host_stability.ps1',
    'apply_safehold_fix.ps1',
    'get_sofia_tools.ps1'
)

# Запрос по имени ветки уходит через кэш CDN и может вернуть копию до последнего
# коммита. Ссылка на конкретный SHA неизменяема, поэтому всегда отдаёт нужное
# содержимое. SHA берём из API, который кэшируется иначе.
$ref = $Branch
try {
    $head = Invoke-RestMethod "https://api.github.com/repos/Shtrop/shtrop/commits/$Branch" `
                              -Headers @{ 'User-Agent' = 'sofia-tools'; 'Accept' = 'application/vnd.github+json' }
    if ($head.sha) {
        $ref = $head.sha
        Write-Host ("Коммит {0}: {1}" -f $Branch, $ref.Substring(0,12)) -ForegroundColor DarkGray
        $when = $head.commit.committer.date
        if ($when) { Write-Host ("Дата коммита : {0}" -f $when) -ForegroundColor DarkGray }
    }
} catch {
    Write-Host ("Не удалось узнать SHA ветки ({0}) — качаю по имени ветки, возможен кэш." -f $_.Exception.Message) -ForegroundColor Yellow
}

$base = "https://raw.githubusercontent.com/Shtrop/shtrop/$ref/sofia"
$stamp = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()

New-Item -ItemType Directory -Force -Path $Dest | Out-Null
Write-Host ''
Write-Host ("Загрузка инструментов Sofia из ветки {0}" -f $Branch) -ForegroundColor White
Write-Host ("Каталог: {0}" -f $Dest)
Write-Host ''

function Get-ToolFile {
    param([string] $Name)
    $target = Join-Path $Dest $Name
    $before = if (Test-Path $target) { (Get-FileHash $target -Algorithm SHA256).Hash } else { $null }
    try {
        # уникальный параметр обходит кэш CDN
        Invoke-WebRequest "$base/$Name`?nocache=$stamp" -OutFile $target -UseBasicParsing -Headers @{ 'Cache-Control' = 'no-cache' }
        $after = (Get-FileHash $target -Algorithm SHA256).Hash
        $size  = (Get-Item $target).Length
        $state = if (-not $before) { 'новый' } elseif ($before -ne $after) { 'ОБНОВЛЁН' } else { 'без изменений' }
        $color = if ($state -eq 'ОБНОВЛЁН') { 'Green' } elseif ($state -eq 'новый') { 'Cyan' } else { 'DarkGray' }
        Write-Host ("  {0,-32} {1,8} Б  {2,-14} {3}" -f $Name, $size, $state, $after.Substring(0,12)) -ForegroundColor $color
    } catch {
        Write-Host ("  {0,-32} ОШИБКА: {1}" -f $Name, $_.Exception.Message) -ForegroundColor Red
    }
}

function Get-DeclaredFileList {
    <#
        Достаёт список файлов из текста загрузчика: блок $files = @( '...' ).
        Нужен, чтобы узнать состав набора из СВЕЖЕЙ копии, а не из своей.
    #>
    param([string] $Path)
    if (-not (Test-Path $Path)) { return @() }
    $text = Get-Content $Path -Raw
    $m = [regex]::Match($text, '(?s)\$files\s*=\s*@\((.*?)\)')
    if (-not $m.Success) { return @() }
    @([regex]::Matches($m.Groups[1].Value, "'([^']+\.ps1)'") | ForEach-Object { $_.Groups[1].Value })
}

foreach ($f in $files) { Get-ToolFile -Name $f }

# Список файлов зашит в сам загрузчик, поэтому старая копия не знает о файлах,
# добавленных в набор позже. Загрузчик обновляет сам себя, так что после этого
# его список можно перечитать и дочитать недостающее. Без этого новый файл
# доезжал бы только со второго запуска, а скрипт, который его подключает,
# отваливался бы на первом — во время инцидента.
$declared = Get-DeclaredFileList -Path (Join-Path $Dest 'get_sofia_tools.ps1')
$missing = @($declared | Where-Object { $files -notcontains $_ })
if ($missing.Count -gt 0) {
    Write-Host ''
    Write-Host ("В наборе появились новые файлы ({0}) — дочитываю:" -f $missing.Count) -ForegroundColor Cyan
    foreach ($f in $missing) { Get-ToolFile -Name $f }
}

Write-Host ''
Write-Host 'Порядок запуска:' -ForegroundColor White
Write-Host '  .\diagnose_host_safe_hold.ps1 -Days 14   собрать доказательства'
Write-Host '  .\analyze_safehold_report.ps1            диагноз и следующий шаг'
Write-Host '  .\analyze_minidump.ps1                   код остановки из событий и дампов'
Write-Host '  .\check_memory_storage.ps1               память, WHEA, SMART, диски'
Write-Host '  .\watch_host_stability.ps1 -Hours 48     окно наблюдения для выхода из hold'
Write-Host '      после ресета продолжать тем же окном: -Resume'
Write-Host '      решение принимать по hold_exit_ready, а не по verdict'
Write-Host ''
Write-Host 'Если применяется ограничение power limit:' -ForegroundColor White
Write-Host '  .\apply_safehold_fix.ps1 -Action PowerLimit -Percent 80 -Confirm'
Write-Host '  .\apply_safehold_fix.ps1 -Action PowerLimitPersist -Confirm   закрепить на reboot'
Write-Host '      без закрепления лимит исчезнет на первой же перезагрузке'
Write-Host ''
