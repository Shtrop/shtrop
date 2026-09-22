<#
.SYNOPSIS
    Проверяет направление, на которое указывает код остановки 0x154
    UNEXPECTED_STORE_EXCEPTION: память и системный диск. Только чтение.

.DESCRIPTION
    Менеджер сжатой памяти (store manager) падает по трём типовым причинам:
    сбойная или нестабильно разогнанная RAM, отказывающий системный диск
    (там живут файл подкачки и store) и реже — драйвер. Скрипт собирает
    доказательства по каждой из них:

      1. Конфигурация RAM и признаки активного XMP/EXPO.
      2. События WHEA-Logger — аппаратные ошибки, которые видит сама платформа.
      3. Результаты средства проверки памяти Windows, если запускалось.
      4. Ошибки дисковой подсистемы в журнале (disk, Ntfs, volmgr).
      5. SMART/надёжность физических дисков, износ и температура.
      6. Файл подкачки и флаг грязного тома.

    Скрипт ничего не изменяет, не запускает chkdsk и не трогает дерево студии.

.PARAMETER Days
    Глубина анализа журналов. По умолчанию 30.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\check_memory_storage.ps1
#>

[CmdletBinding()]
param(
    [int] $Days = 30
)

$ErrorActionPreference = 'Continue'
$ProgressPreference    = 'SilentlyContinue'

# Текст ошибки «событий не найдено» локализован, поэтому полагаться на него нельзя:
# пустой результат и реальный отказ в доступе различаются пробой доступа, а не разбором строки.
function Test-SystemLogReadable {
    try { $null = Get-WinEvent -LogName System -MaxEvents 1 -ErrorAction Stop; return $true }
    catch { return $false }
}

function Get-SystemEvents {
    param([hashtable] $Filter, [int] $MaxEvents = 0)
    # Несуществующий провайдер или неподходящая комбинация фильтра дают
    # EventLogException, которую -ErrorAction SilentlyContinue не подавляет,
    # поэтому глушим через try/catch и возвращаем пустой результат.
    $p = @{ FilterHashtable = $Filter; ErrorAction = 'Stop' }
    if ($MaxEvents -gt 0) { $p['MaxEvents'] = $MaxEvents }
    try { @(Get-WinEvent @p) } catch { @() }
}

$since = (Get-Date).AddDays(-$Days)

$findings = @()
function Add-F {
    param(
        [ValidateSet('PASS','WARN','FAIL','NOT_MEASURED')][string]$Status,
        [string]$Component, [string]$Evidence, [string]$Next = ''
    )
    $script:findings += [pscustomobject]@{ Component=$Component; Status=$Status; Evidence=$Evidence; Next=$Next }
    $c = switch ($Status) { 'PASS'{'Green'} 'WARN'{'Yellow'} 'FAIL'{'Red'} default{'DarkGray'} }
    Write-Host ("  [{0,-12}] {1}: {2}" -f $Status, $Component, $Evidence) -ForegroundColor $c
}
function Write-Head { param([string]$T)
    Write-Host ''; Write-Host ('=' * 78) -ForegroundColor DarkCyan
    Write-Host "  $T" -ForegroundColor Cyan; Write-Host ('=' * 78) -ForegroundColor DarkCyan
}

Write-Host ''
Write-Host 'Sofia AI Studio — проверка памяти и дисковой подсистемы (READ-ONLY)' -ForegroundColor White
Write-Host ("Окно журналов: {0} дн." -f $Days)

# ---------------------------------------------------------------------------
Write-Head '1/6  Конфигурация оперативной памяти'
try {
    $dimms = @(Get-CimInstance Win32_PhysicalMemory -ErrorAction Stop)
    $totalGb = [math]::Round((($dimms | Measure-Object Capacity -Sum).Sum / 1GB), 0)
    Write-Host ''
    $dimms | Select-Object @{n='Слот';e={$_.DeviceLocator}},
                           @{n='ГБ';e={[math]::Round($_.Capacity/1GB,0)}},
                           @{n='Speed МГц';e={$_.Speed}},
                           @{n='Факт МГц';e={$_.ConfiguredClockSpeed}},
                           @{n='Производитель';e={$_.Manufacturer}},
                           @{n='Партномер';e={$_.PartNumber}} |
        Format-Table -AutoSize | Out-String | Write-Host

    $cfg = @($dimms | ForEach-Object { [int]$_.ConfiguredClockSpeed } | Where-Object { $_ -gt 0 })
    $fact = if ($cfg) { ($cfg | Measure-Object -Maximum).Maximum } else { 0 }
    $isDdr5 = $fact -ge 4000
    $jedec  = if ($isDdr5) { 4800 } else { 3200 }

    Add-F -Status 'PASS' -Component 'Объём RAM' -Evidence ("{0} ГБ в {1} модулях" -f $totalGb, $dimms.Count)
    Write-Host '  Оба столбца частоты Windows берёт из текущей конфигурации, а не из паспорта модуля:' -ForegroundColor DarkGray
    Write-Host '  паспортную частоту смотреть по партномеру на сайте производителя.' -ForegroundColor DarkGray

    if ($fact -gt $jedec) {
        Add-F -Status 'WARN' -Component 'XMP/EXPO' `
              -Evidence ("память работает на {0} МГц при базовой JEDEC {1} МГц — профиль разгона активен" -f $fact, $jedec) `
              -Next 'самый дешёвый тест: отключить XMP/EXPO в BIOS и наблюдать 48 ч'
    } elseif ($fact -gt 0) {
        Add-F -Status 'PASS' -Component 'XMP/EXPO' -Evidence ("{0} МГц — в пределах JEDEC, разгон не активен" -f $fact)
    } else {
        Add-F -Status 'NOT_MEASURED' -Component 'XMP/EXPO' -Evidence 'фактическая частота не прочиталась'
    }

    if ($isDdr5 -and $dimms.Count -ge 4) {
        Add-F -Status 'WARN' -Component 'Режим заполнения слотов' `
              -Evidence ("{0} модуля DDR5 — по два на канал (2DPC)" -f $dimms.Count) `
              -Next 'для DDR5 это самый тяжёлый режим для контроллера памяти: при 0x154 проверить прогон на двух модулях'
    }

    $parts = @($dimms | Select-Object -ExpandProperty PartNumber -Unique | ForEach-Object { "$_".Trim() } | Where-Object { $_ })
    if ($parts.Count -gt 1) {
        Add-F -Status 'WARN' -Component 'Комплект памяти' `
              -Evidence ("модули разных партномеров: {0}" -f ($parts -join ' | ')) `
              -Next 'смешанные комплекты — частая причина нестабильности на высоких частотах'
    } elseif ($parts.Count -eq 1) {
        Add-F -Status 'PASS' -Component 'Комплект памяти' -Evidence ("единый партномер {0}" -f $parts[0])
    }
} catch {
    Add-F -Status 'NOT_MEASURED' -Component 'Конфигурация RAM' -Evidence $_.Exception.Message
}

# ---------------------------------------------------------------------------
Write-Head '2/6  События WHEA-Logger (аппаратные ошибки)'
if (-not (Test-SystemLogReadable)) {
    Add-F -Status 'NOT_MEASURED' -Component 'WHEA' -Evidence 'журнал System недоступен — нужны права администратора'
} else {
    $whea = Get-SystemEvents -Filter @{ LogName='System'; ProviderName='Microsoft-Windows-WHEA-Logger'; StartTime=$since }
    if ($whea.Count -eq 0) {
        Add-F -Status 'PASS' -Component 'WHEA' -Evidence 'аппаратных ошибок не зарегистрировано'
    } else {
        $whea | Group-Object Id | ForEach-Object {
            Write-Host ("  Event {0} x{1}" -f $_.Name, $_.Count) -ForegroundColor Yellow
        }
        $last = ($whea | Sort-Object TimeCreated -Descending)[0]
        Write-Host ("  Последнее: {0}" -f $last.TimeCreated) -ForegroundColor DarkGray

        # Текст WHEA часто не отрендерен (нет ресурсов провайдера), поэтому
        # берём поля напрямую из XML, а Message используем только если он есть.
        if ($last.Message) {
            $txt = ($last.Message -replace '\s+',' ')
            Write-Host ("  {0}" -f $txt.Substring(0, [math]::Min(300, $txt.Length))) -ForegroundColor DarkGray
        }
        try {
            $x = [xml]$last.ToXml()
            $pairs = @()
            foreach ($d in $x.Event.EventData.Data) {
                $n = "$($d.Name)"; $v = "$($d.'#text')"
                if ($n -and $v -and $v.Length -lt 60) { $pairs += ("{0}={1}" -f $n, $v) }
            }
            if ($pairs) { Write-Host ("  Поля: {0}" -f (($pairs | Select-Object -First 12) -join '  ')) -ForegroundColor DarkGray }
        } catch { }

        $ids = (($whea | Group-Object Id | ForEach-Object { "{0}x{1}" -f $_.Name, $_.Count }) -join ', ')
        Add-F -Status 'FAIL' -Component 'WHEA' `
              -Evidence ("{0} аппаратных ошибок за {1} дн. (ID: {2}), последняя {3}" -f $whea.Count, $Days, $ids, $last.TimeCreated) `
              -Next 'платформа сама зафиксировала аппаратную ошибку: питание, IMC/RAM, CPU — не драйвер'
    }
}

# ---------------------------------------------------------------------------
Write-Head '3/6  Результаты средства проверки памяти Windows'
$md = Get-SystemEvents -Filter @{ LogName='System'; ProviderName='Microsoft-Windows-MemoryDiagnostics-Results' } -MaxEvents 5
foreach ($m in $md) {
    Write-Host ("  {0}  {1}" -f $m.TimeCreated, (($m.Message -replace '\s+',' '))) -ForegroundColor DarkGray
}
# Решать по тексту события нельзя дважды: он локализован, И сообщение об
# УСПЕХЕ само содержит слово об ошибках — «detected no errors», «не обнаружило
# ошибок». Прежнее условие превращало чистый прогон памяти в FAIL и отправляло
# владельца искать несуществующий дефект RAM.
# Решает идентификатор: 1201 — ошибок нет, 1202 — ошибки найдены.
# Берём САМЫЙ СВЕЖИЙ вердикт, а не любой из последних пяти: иначе старое 1202
# перевешивает новое 1201, и машина с уже заменённой планкой вечно числится
# сбойной. $md приходит от свежих к старым.
$verdicts = @($md | Where-Object { $_.Id -eq 1201 -or $_.Id -eq 1202 } | Sort-Object TimeCreated -Descending)
$bad  = @($verdicts | Select-Object -First 1 | Where-Object { $_.Id -eq 1202 })
$good = @($verdicts | Select-Object -First 1 | Where-Object { $_.Id -eq 1201 })
if ($md.Count -eq 0) {
    Add-F -Status 'NOT_MEASURED' -Component 'Проверка памяти Windows' -Evidence 'никогда не запускалась' `
          -Next 'встроенная проверка слабее MemTest86, но дешевле: mdsched.exe'
} elseif ($bad.Count -gt 0) {
    Add-F -Status 'FAIL' -Component 'Проверка памяти Windows' -Evidence 'прошлый прогон нашёл ошибки (событие 1202)'
} elseif ($good.Count -gt 0) {
    Add-F -Status 'PASS' -Component 'Проверка памяти Windows' -Evidence 'прошлый прогон ошибок не нашёл (событие 1201)'
} else {
    Add-F -Status 'NOT_MEASURED' -Component 'Проверка памяти Windows' `
          -Evidence ("события есть, но вердикта среди них нет (нет 1201/1202): {0}" -f (($md | ForEach-Object { $_.Id } | Sort-Object -Unique) -join ', ')) `
          -Next 'прогнать проверку заново: mdsched.exe, либо сразу MemTest86'
}

# ---------------------------------------------------------------------------
Write-Head '4/6  Ошибки дисковой подсистемы в журнале'
# Имена провайдеров регистронезависимы, поэтому 'disk' и 'Disk' — один и тот
# же провайдер: дубль в списке считал каждое событие диска дважды.
$diskProviders = @('disk','Ntfs','volmgr','storahci','stornvme','nvme') |
                 Sort-Object -Property { $_.ToLower() } -Unique
# Спрашиваем только про провайдеров, которые на этой системе зарегистрированы.
$known = @{}
try {
    foreach ($lp in (Get-WinEvent -ListProvider * -ErrorAction Stop)) { $known[$lp.Name.ToLower()] = $true }
} catch { }
$diskEvents = @()
foreach ($p in $diskProviders) {
    if ($known.Count -gt 0 -and -not $known.ContainsKey($p.ToLower())) { continue }
    $diskEvents += Get-SystemEvents -Filter @{ LogName='System'; ProviderName=$p; StartTime=$since; Level=1,2,3 }
}
if ($diskEvents.Count -eq 0) {
    Add-F -Status 'PASS' -Component 'Журнал дисков' -Evidence ("ошибок за {0} дн. нет" -f $Days)
} else {
    $diskEvents | Group-Object ProviderName, Id | Sort-Object Count -Descending | Select-Object -First 10 |
        ForEach-Object { Write-Host ("  {0}  x{1}" -f $_.Name, $_.Count) -ForegroundColor Yellow }
    $critical = @($diskEvents | Where-Object { $_.Id -in 7, 51, 55, 98, 129, 153 })
    $st = if ($critical.Count -gt 0) { 'FAIL' } else { 'WARN' }
    Add-F -Status $st -Component 'Журнал дисков' `
          -Evidence ("{0} записей, из них значимых (7/51/55/98/129/153): {1}" -f $diskEvents.Count, $critical.Count) `
          -Next 'события 7/51/129/153 на системном диске напрямую объясняют 0x154'

    # volmgr 161/162 — сбой записи аварийного дампа. Это переворачивает трактовку
    # ресетов без дампа: часть из них могла быть BSOD, дамп которого не сохранился.
    $dumpFail = @($diskEvents | Where-Object { $_.ProviderName -match 'volmgr' -and $_.Id -in 161, 162 })
    if ($dumpFail.Count -gt 0) {
        $lastDf = ($dumpFail | Sort-Object TimeCreated -Descending)[0]
        Add-F -Status 'WARN' -Component 'Запись аварийного дампа' `
              -Evidence ("volmgr {0} x{1}: системе не удалось сохранить дамп, последний раз {2}" -f `
                         ($dumpFail[0].Id), $dumpFail.Count, $lastDf.TimeCreated) `
              -Next 'ресет без дампа мог быть крахом, а не потерей питания — проверить размер и размещение pagefile на системном диске'
    }
}

# ---------------------------------------------------------------------------
Write-Head '5/6  Состояние физических дисков'
try {
    $pds = @(Get-PhysicalDisk -ErrorAction Stop)
    foreach ($d in $pds) {
        $rc = $null
        try { $rc = $d | Get-StorageReliabilityCounter -ErrorAction Stop } catch { }
        Write-Host ("  {0}  {1}  {2} ГБ  health={3}  status={4}  прошивка={5}  шина={6}" -f `
            $d.DeviceId, $d.FriendlyName, [math]::Round($d.Size/1GB,0), $d.HealthStatus, $d.OperationalStatus,
            $d.FirmwareVersion, $d.BusType)
        if ($rc) {
            Write-Host ("      износ={0}%  темп={1}C  наработка={2} ч  ошибок чтения={3}  ошибок записи={4}" -f `
                $rc.Wear, $rc.Temperature, $rc.PowerOnHours, $rc.ReadErrorsTotal, $rc.WriteErrorsTotal) -ForegroundColor DarkGray
        }

        if ($d.HealthStatus -ne 'Healthy') {
            Add-F -Status 'FAIL' -Component ("Диск {0}" -f $d.FriendlyName) -Evidence ("health={0}" -f $d.HealthStatus) `
                  -Next 'диск заменить; при системном диске это прямая причина 0x154'
        } elseif ($rc -and $rc.Wear -ne $null -and [int]$rc.Wear -ge 80) {
            Add-F -Status 'WARN' -Component ("Диск {0}" -f $d.FriendlyName) -Evidence ("износ {0}%" -f $rc.Wear) `
                  -Next 'ресурс на исходе — планировать замену'
        } elseif ($rc -and (([int]$rc.ReadErrorsTotal -gt 0) -or ([int]$rc.WriteErrorsTotal -gt 0))) {
            Add-F -Status 'WARN' -Component ("Диск {0}" -f $d.FriendlyName) `
                  -Evidence ("ошибки чтения/записи: {0}/{1}" -f $rc.ReadErrorsTotal, $rc.WriteErrorsTotal)
        } else {
            Add-F -Status 'PASS' -Component ("Диск {0}" -f $d.FriendlyName) -Evidence 'Healthy, счётчики чистые'
        }
    }
} catch {
    Add-F -Status 'NOT_MEASURED' -Component 'Физические диски' -Evidence $_.Exception.Message
}

# ---------------------------------------------------------------------------
Write-Head '6/6  Файл подкачки и состояние тома'
try {
    $pf = @(Get-CimInstance Win32_PageFileUsage -ErrorAction SilentlyContinue)
    if ($pf) {
        foreach ($f in $pf) {
            Write-Host ("  {0}  выделено {1} МБ, пик {2} МБ" -f $f.Name, $f.AllocatedBaseSize, $f.PeakUsage)
        }
        Add-F -Status 'PASS' -Component 'Файл подкачки' -Evidence (($pf | ForEach-Object { $_.Name }) -join ', ')
    } else {
        Add-F -Status 'WARN' -Component 'Файл подкачки' -Evidence 'не найден или управляется системой автоматически'
    }
} catch {
    Add-F -Status 'NOT_MEASURED' -Component 'Файл подкачки' -Evidence $_.Exception.Message
}

try {
    $sysDrive = ($env:SystemDrive)
    $dirty = & fsutil dirty query $sysDrive 2>&1 | Out-String
    Write-Host ("  {0}" -f $dirty.Trim()) -ForegroundColor DarkGray
    if ($dirty -match 'не является|не помечен|is not dirty|NOT Dirty') {
        Add-F -Status 'PASS' -Component 'Флаг тома' -Evidence ("{0} не помечен как грязный" -f $sysDrive)
    } elseif ($dirty -match 'помечен|is dirty') {
        Add-F -Status 'FAIL' -Component 'Флаг тома' -Evidence ("{0} помечен грязным — файловая система повреждена" -f $sysDrive) `
              -Next 'запланировать chkdsk /f на перезагрузку — решение владельца'
    } else {
        Add-F -Status 'NOT_MEASURED' -Component 'Флаг тома' -Evidence 'ответ fsutil не распознан'
    }
} catch {
    Add-F -Status 'NOT_MEASURED' -Component 'Флаг тома' -Evidence 'fsutil недоступен'
}

# ---------------------------------------------------------------------------
Write-Head '7/7  Настройки аварийного дампа'
try {
    $cc = Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\CrashControl' -ErrorAction Stop
    $kind = switch ([int]$cc.CrashDumpEnabled) {
        0 { 'отключён' } 1 { 'полный' } 2 { 'дамп ядра' } 3 { 'малый (минидамп)' } 7 { 'автоматический' }
        default { "код $($cc.CrashDumpEnabled)" }
    }
    Write-Host ("  Тип дампа      : {0}" -f $kind)
    Write-Host ("  Файл дампа     : {0}" -f $cc.DumpFile)
    Write-Host ("  Минидампы      : {0}" -f $cc.MinidumpDir)
    Write-Host ("  Автоперезагрузка: {0}" -f $cc.AutoReboot)
    if ([int]$cc.CrashDumpEnabled -eq 0) {
        Add-F -Status 'FAIL' -Component 'Аварийный дамп' -Evidence 'запись дампа отключена' `
              -Next 'без дампа причина краха не определяется — включить малый дамп'
    } else {
        Add-F -Status 'PASS' -Component 'Аварийный дамп' -Evidence ("включён: {0}" -f $kind)
    }
    if ([int]$cc.AutoReboot -eq 1) {
        Write-Host '  Автоперезагрузка включена: синий экран может не успеть показаться,' -ForegroundColor DarkGray
        Write-Host '  и внешне крах выглядит как внезапный ресет.' -ForegroundColor DarkGray
    }
} catch {
    Add-F -Status 'NOT_MEASURED' -Component 'Аварийный дамп' -Evidence 'ветка CrashControl недоступна'
}

# ---------------------------------------------------------------------------
$fails = @($findings | Where-Object Status -eq 'FAIL')
$warns = @($findings | Where-Object Status -eq 'WARN')
$passes = @($findings | Where-Object Status -eq 'PASS')
$verdict = if ($fails.Count) { 'FAIL' }
           elseif ($warns.Count) { 'WARN' }
           elseif ($passes.Count) { 'PASS' }
           else { 'NOT_MEASURED' }   # всё упало в NOT_MEASURED — это не «здоров»

Write-Head ("ВЕРДИКТ: {0}   (FAIL={1}  WARN={2})" -f $verdict, $fails.Count, $warns.Count)
foreach ($f in $fails + $warns) {
    Write-Host ("  {0,-5} {1}: {2}" -f $f.Status, $f.Component, $f.Evidence) -ForegroundColor $(if ($f.Status -eq 'FAIL') { 'Red' } else { 'Yellow' })
    if ($f.Next) { Write-Host ("        -> {0}" -f $f.Next) -ForegroundColor DarkGray }
}

Write-Host ''
Write-Host '  Порядок действий под 0x154 UNEXPECTED_STORE_EXCEPTION:' -ForegroundColor White
Write-Host '    1. Отключить XMP/EXPO в BIOS — бесплатно и обратимо, закрывает самую частую причину.'
Write-Host '    2. MemTest86 минимум 4 прохода (с флешки, не из Windows).'
Write-Host '    3. Проверить SMART системного диска и обновить прошивку NVMe.'
Write-Host '    4. Наблюдение: .\watch_host_stability.ps1 -Hours 48'
Write-Host ''
Write-Host '  Изменения BIOS, замена памяти или диска, chkdsk /f — решение и руки владельца.' -ForegroundColor Yellow
Write-Host '  HOST_SAFE_HOLD.flag не снимать до 48 ч без новых событий 41.' -ForegroundColor Yellow
