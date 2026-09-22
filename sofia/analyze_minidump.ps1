<#
.SYNOPSIS
    Достаёт bug check код и виновника из минидампов Windows без установки
    отладчика; если cdb/windbg есть — дополнительно прогоняет !analyze -v.

.DESCRIPTION
    Три независимых источника, от самого надёжного к запасному:
      1. События System / BugCheck 1001 — текст события содержит код остановки;
      2. Заголовок файла дампа — код читается напрямую из байтов;
      3. cdb.exe / kd.exe, если Debugging Tools for Windows установлены.

    Скрипт только читает. Дампы не удаляет и не перемещает.

.PARAMETER DumpPath
    Каталог с дампами или конкретный .dmp. По умолчанию C:\Windows\Minidump.

.PARAMETER Days
    Насколько глубоко смотреть события и дампы. По умолчанию 14.

.PARAMETER Top
    Сколько последних дампов разбирать. По умолчанию 5.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\analyze_minidump.ps1
#>

[CmdletBinding()]
param(
    [string] $DumpPath = (Join-Path $env:SystemRoot 'Minidump'),
    [int]    $Days = 14,
    [int]    $Top = 5
)

$ErrorActionPreference = 'Continue'

$lib = Join-Path $PSScriptRoot 'lib_bugcheck.ps1'
if (Test-Path $lib) { . $lib } else {
    Write-Host 'Не найден lib_bugcheck.ps1 рядом со скриптом — скачайте его из того же каталога репозитория.' -ForegroundColor Red
    exit 2
}

function Write-Head { param([string]$T)
    Write-Host ''; Write-Host ('=' * 78) -ForegroundColor DarkCyan
    Write-Host "  $T" -ForegroundColor Cyan; Write-Host ('=' * 78) -ForegroundColor DarkCyan
}

$since = (Get-Date).AddDays(-$Days)
$found = @()

# ---------------------------------------------------------------------------
# 1. События BugCheck 1001 — самый надёжный источник, ничего не нужно ставить
# ---------------------------------------------------------------------------
Write-Head '1/3  События BugCheck 1001'
try {
    $ev = Get-WinEvent -FilterHashtable @{ LogName='System'; Id=1001; StartTime=$since } -ErrorAction Stop |
          Where-Object { $_.ProviderName -match 'BugCheck' -or $_.Message -match 'bugcheck' }
    if (-not $ev) {
        Write-Host '  Записей нет.' -ForegroundColor DarkGray
    }
    foreach ($e in $ev) {
        $m = ($e.Message -replace '\s+', ' ')
        $code = $null
        if ($m -match '0x([0-9a-fA-F]{8})') { $code = [uint32]::Parse($Matches[1], 'HexNumber') }
        $params = @()
        foreach ($mm in [regex]::Matches($m, '0x([0-9a-fA-F]{16})')) { $params += ('0x' + $mm.Groups[1].Value) }
        $dumpRef = $null
        if ($m -match '([A-Za-z]:\\[^ ]+\.(?:dmp|DMP))') { $dumpRef = $Matches[1] }

        if ($code) {
            $info = Get-BugCheckInfo -Code $code
            $found += [pscustomobject]@{
                Source = 'event1001'; Time = $e.TimeCreated; Code = $code
                Hex = $info.Hex; Name = $info.Name; Class = $info.Class; Hint = $info.Hint
                Params = $params; Dump = $dumpRef
            }
            Write-Host ("  {0}  {1}  {2}" -f $e.TimeCreated, $info.Hex, $info.Name) -ForegroundColor Yellow
            if ($params.Count -gt 0) { Write-Host ("      параметры: {0}" -f ($params -join '  ')) -ForegroundColor DarkGray }
            if ($dumpRef) { Write-Host ("      дамп: {0}" -f $dumpRef) -ForegroundColor DarkGray }
        } else {
            Write-Host ("  {0}  код не распознан в тексте события" -f $e.TimeCreated) -ForegroundColor DarkGray
        }
    }
} catch {
    if ($_.Exception.Message -match 'No events were found') {
        Write-Host '  Записей нет.' -ForegroundColor DarkGray
    } else {
        Write-Host ("  Журнал недоступен: {0}" -f $_.Exception.Message) -ForegroundColor Magenta
        Write-Host '  Запустите PowerShell от имени администратора.' -ForegroundColor Magenta
    }
}

# ---------------------------------------------------------------------------
# 2. Заголовки файлов дампов
# ---------------------------------------------------------------------------
Write-Head '2/3  Заголовки файлов дампов'
$dumps = @()
if (Test-Path $DumpPath) {
    $item = Get-Item $DumpPath
    $dumps = if ($item.PSIsContainer) {
        Get-ChildItem $DumpPath -Filter *.dmp -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Descending | Select-Object -First $Top
    } else { @($item) }
}
if (-not $dumps) {
    Write-Host ("  Дампов не найдено в {0}" -f $DumpPath) -ForegroundColor DarkGray
}

foreach ($d in $dumps) {
    try {
        $fs = [System.IO.File]::OpenRead($d.FullName)
        try {
            $len = [int][math]::Min(0x400, $fs.Length)
            $buf = New-Object byte[] $len
            [void]$fs.Read($buf, 0, $len)
        } finally { $fs.Dispose() }

        $sig = [System.Text.Encoding]::ASCII.GetString($buf, 0, 8)
        # Кандидаты смещений BugCheckCode отличаются между версиями структуры,
        # поэтому проверяем оба и выбираем тот, что даёт известный код.
        $offsets = if ($sig -like 'PAGEDU64*') { @(0x38, 0x80) } else { @(0x38, 0x3C) }
        $picked = $null
        foreach ($off in $offsets) {
            if ($off + 4 -le $buf.Length) {
                $c = [BitConverter]::ToUInt32($buf, $off)
                if ($c -gt 0 -and $c -lt 0x10000) {
                    $i = Get-BugCheckInfo -Code $c
                    if ($i.Known) { $picked = $i; break }
                    if (-not $picked) { $picked = $i }
                }
            }
        }

        if ($picked) {
            $found += [pscustomobject]@{
                Source = 'dumpheader'; Time = $d.LastWriteTime; Code = $picked.Code
                Hex = $picked.Hex; Name = $picked.Name; Class = $picked.Class; Hint = $picked.Hint
                Params = @(); Dump = $d.FullName
            }
            Write-Host ("  {0}  {1}  {2}  ({3})" -f $d.LastWriteTime, $picked.Hex, $picked.Name, $d.Name) -ForegroundColor Yellow
        } else {
            Write-Host ("  {0}  код из заголовка не извлечён ({1}, sig={2})" -f $d.LastWriteTime, $d.Name, $sig.Trim()) -ForegroundColor DarkGray
        }
    } catch {
        Write-Host ("  {0}: не прочитан — {1}" -f $d.Name, $_.Exception.Message) -ForegroundColor DarkGray
    }
}

# ---------------------------------------------------------------------------
# 3. cdb/kd, если есть
# ---------------------------------------------------------------------------
Write-Head '3/3  Отладчик (!analyze -v), если установлен'
$dbg = $null
foreach ($cand in @(
    "$env:ProgramFiles (x86)\Windows Kits\10\Debuggers\x64\cdb.exe",
    "${env:ProgramFiles(x86)}\Windows Kits\10\Debuggers\x64\cdb.exe",
    "$env:ProgramFiles\Windows Kits\10\Debuggers\x64\cdb.exe",
    "$env:ProgramFiles\WindowsApps\Microsoft.WinDbg*\cdb.exe"
)) {
    $hit = Get-Item $cand -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($hit) { $dbg = $hit.FullName; break }
}
if (-not $dbg) { $dbg = (Get-Command cdb.exe -ErrorAction SilentlyContinue).Source }

if (-not $dbg) {
    Write-Host '  cdb.exe не найден — шаг пропущен (кода остановки из шагов 1-2 обычно достаточно).' -ForegroundColor DarkGray
    Write-Host '  Если нужен точный модуль-виновник: winget install Microsoft.WinDbg' -ForegroundColor DarkGray
} elseif ($dumps) {
    $target = $dumps[0].FullName
    Write-Host ("  Отладчик : {0}" -f $dbg) -ForegroundColor DarkGray
    Write-Host ("  Дамп     : {0}" -f $target) -ForegroundColor DarkGray
    $out = & $dbg -z $target -c '!analyze -v; q' -y 'srv*https://msdl.microsoft.com/download/symbols' 2>&1 | Out-String
    $keep = $out -split "`n" | Where-Object {
        $_ -match 'BUGCHECK_|MODULE_NAME|IMAGE_NAME|PROCESS_NAME|FAILURE_BUCKET|STACK_TEXT|Probably caused by'
    } | Select-Object -First 25
    if ($keep) { $keep | ForEach-Object { Write-Host ("  {0}" -f $_.Trim()) } }
    else { Write-Host '  Отладчик отработал, но ключевых строк не найдено.' -ForegroundColor DarkGray }
}

# ---------------------------------------------------------------------------
# Вердикт
# ---------------------------------------------------------------------------
Write-Head 'ВЕРДИКТ'
if (-not $found) {
    Write-Host '  NOT_MEASURED: код остановки получить не удалось.' -ForegroundColor DarkGray
    Write-Host '  Проверьте права администратора и наличие дампов в C:\Windows\Minidump.' -ForegroundColor DarkGray
    exit 0
}

$byClass = @($found | Group-Object Class | Sort-Object Count -Descending)
$dominant = $byClass[0].Name
$mixed = ($byClass.Count -gt 1)

Write-Host ("  Разобрано событий/дампов: {0}" -f $found.Count)
foreach ($g in $byClass) {
    $codes = ($g.Group | Select-Object -ExpandProperty Hex -Unique) -join ', '
    Write-Host ("    {0,-9} x{1}   {2}" -f $g.Name, $g.Count, $codes)
}
Write-Host ''
$uniq = $found | Sort-Object Hex -Unique
foreach ($u in $uniq) {
    Write-Host ("  {0} {1}" -f $u.Hex, $u.Name) -ForegroundColor Yellow
    Write-Host ("      {0}" -f $u.Hint)
}
Write-Host ''
Write-Host '  Что делать:' -ForegroundColor White
if ($mixed) {
    Write-Host '    Коды разных классов — причина не одна. Отработать оба направления,' -ForegroundColor Yellow
    Write-Host '    начиная с того, где событий больше:' -ForegroundColor Yellow
    foreach ($g in $byClass) {
        Write-Host ("    [{0} x{1}] {2}" -f $g.Name, $g.Count, (Get-BugCheckClassAdvice -Class $g.Name))
    }
} else {
    Write-Host ("    {0}" -f (Get-BugCheckClassAdvice -Class $dominant))
}
Write-Host ''
Write-Host '  HOST_SAFE_HOLD.flag не снимать: сначала fix, затем 48 ч чистого наблюдения' -ForegroundColor Yellow
Write-Host '  (.\watch_host_stability.ps1 -Hours 48).' -ForegroundColor Yellow
