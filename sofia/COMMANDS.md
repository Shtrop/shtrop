# Шпаргалка команд

Все команды запускаются в **PowerShell от имени администратора**.
Права нужны для чтения журнала System, `bcdedit`, `nvidia-smi -pl` и `MMAgent`.

Рабочий каталог везде: `%USERPROFILE%\sofia_tools`.

---

## 0. Установка и обновление инструментов

Первый раз:

```powershell
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$dst = "$env:USERPROFILE\sofia_tools"
New-Item -ItemType Directory -Force -Path $dst | Out-Null
Set-Location $dst
Invoke-WebRequest "https://raw.githubusercontent.com/Shtrop/shtrop/master/sofia/get_sofia_tools.ps1?v=$(Get-Random)" `
    -OutFile get_sofia_tools.ps1 -UseBasicParsing
.\get_sofia_tools.ps1
```

Дальше — всегда одной строкой. Загрузка идёт по SHA коммита, кэш CDN не мешает,
в выводе видно, какие файлы реально обновились:

```powershell
Set-Location "$env:USERPROFILE\sofia_tools"; .\get_sofia_tools.ps1
```

---

## 1. Диагностика (ничего не меняет)

```powershell
.\diagnose_host_safe_hold.ps1 -Days 14        # собрать доказательства
.\diagnose_host_safe_hold.ps1 -Days 30        # окно глубже
.\analyze_safehold_report.ps1                 # диагноз по свежему отчёту
.\analyze_minidump.ps1                        # код остановки из событий 1001 и дампов
.\analyze_minidump.ps1 -Days 90 -Top 10       # глубже и больше дампов
.\check_memory_storage.ps1                    # RAM, XMP, WHEA, SMART, диски, настройки дампа
```

Разобрать ранее собранный отчёт:

```powershell
.\analyze_safehold_report.ps1 -ReportPath C:\Temp\sofia_safehold_20260922_104727\safehold_report.json
```

---

## 2. Исправления (меняют состояние только с `-Confirm`)

Без `-Confirm` любая из них — dry-run: печатает, что было бы сделано.

```powershell
.\apply_safehold_fix.ps1 -Action Status                        # что применено сейчас

.\apply_safehold_fix.ps1 -Action BadMemoryList                 # какие страницы исключить
.\apply_safehold_fix.ps1 -Action BadMemoryList -Confirm        # исключить (нужна перезагрузка)

.\apply_safehold_fix.ps1 -Action MemoryCompression             # показать план
.\apply_safehold_fix.ps1 -Action MemoryCompression -Confirm    # отключить сжатие памяти

.\apply_safehold_fix.ps1 -Action PowerLimit -Percent 80        # показать план по GPU
.\apply_safehold_fix.ps1 -Action PowerLimit -Percent 80 -Confirm
```

Адреса из отчёта MemTest86 добавляются вручную:

```powershell
.\apply_safehold_fix.ps1 -Action BadMemoryList -Address 0x1F93E53D27, 0x1B7FAC8027 -Confirm
```

Откат всего, что применялось (по файлам отката):

```powershell
.\apply_safehold_fix.ps1 -Action Rollback             # dry-run
.\apply_safehold_fix.ps1 -Action Rollback -Confirm    # откатить
```

---

## 3. Наблюдение

```powershell
.\watch_host_stability.ps1 -Hours 48                       # окно для выхода из hold
.\watch_host_stability.ps1 -Hours 24 -IntervalSeconds 30   # чаще опрос
```

Считает события 41/6008/1001 **и** новые ошибки WHEA. Любая новая ошибка WHEA
проваливает окно: дефект живой, даже если крахов не было.

Журнал System читается только с правами администратора. Если доступа нет —
вердикт `NOT_MEASURED`, и окно **не засчитывается**: пустой список событий в
этом случае означает «не измеряли», а не «крахов не было». Доступ
перепроверяется на каждом шаге, так что потеря прав посреди окна тоже даёт
`NOT_MEASURED`, а не `PASS`.

---

## 4. Аренда GPU и VRAM

Перед каждой тяжёлой задачей (WAN, InfiniteTalk, lip-sync, full-body):

```powershell
.\check_gpu_lease.ps1                                      # GO / NO_GO для тяжёлого маршрута
.\check_gpu_lease.ps1 -RequiredFreeMiB 20000               # маршрут требует больше VRAM
```

Коды возврата: `0` — GO, `1` — NO_GO, `2` — NOT_MEASURED (тоже не GO).
Годится как gate в runner'е: запускать рендер только при `exit 0`.

Полный цикл вокруг задачи:

```powershell
.\check_gpu_lease.ps1 -Action Baseline      # на простое, один раз до задачи
.\check_gpu_lease.ps1                       # preflight: владелец + свободная VRAM
#   ... тяжёлая задача ...
.\check_gpu_lease.ps1 -Action Postflight    # вернулась ли VRAM к базовой линии
```

Если VRAM не вернулась — выгрузка моделей **без перезапуска ComfyUI**:

```powershell
.\check_gpu_lease.ps1 -Action Release              # dry-run: что будет сделано
.\check_gpu_lease.ps1 -Action Release -Confirm     # POST /free, модели выгружаются
```

Ловля зависаний и неосвобождённой памяти:

```powershell
.\check_gpu_lease.ps1 -Action Watch -Minutes 60
```

`STALL` = задача числится выполняющейся, а GPU не считает. Это дефект маршрута,
а не повод перезапускать ComfyUI по расписанию: перезапуск штатным механизмом
освобождения VRAM не является.

Два процесса, держащих VRAM выше порога, — нарушение правила одного тяжёлого
владельца GPU: вердикт `NO_GO`, задачи разводятся по очереди, приоритет у
production.

На WDDM (обычный рабочий стол Windows) `nvidia-smi` отдаёт список процессов, но
без `used_memory` — у всех записей стоит `[N/A]`. Тогда потребление берётся из
счётчиков производительности Windows: те же цифры показывает диспетчер задач.
Набор счётчиков ищется по виду экземпляра (`pid_..._luid_..._phys_0`), а не по
названию, поэтому локализация Windows значения не имеет; нужный счётчик и нужный
адаптер выбираются по совпадению суммы с занятостью от `nvidia-smi`.

Счётчики видят не всё: память, выделенную через CUDA, диспетчер видеопамяти
WDDM процессам не приписывает, и сумма по счётчикам оказывается в разы меньше
занятости по `nvidia-smi`. Такое расхождение отбрасывается, а не выдаётся за
ответ, и печатается обеими величинами — само по себе оно улика.

Поэтому владелец ищется по трём источникам, от надёжного к последнему:

1. **имена рендер-процессов** — два независимых дерева процессов ComfyUI на
   карте нарушают правило одного владельца независимо от того, сколько
   мегабайт за каждым числится. Родитель и его подпроцесс за два владельца не
   считаются;
2. **очередь ComfyUI** — если он выполняет задачу, владелец он, и это знание
   не зависит ни от `nvidia-smi`, ни от счётчиков;
3. **счётчики Windows** — когда первые два молчат.

Если не помогло ничто, решение принимается по суммарной занятости GPU: занято
выше порога → `NO_GO` с пометкой, что владельца установить нельзя. Пустые
значения никогда не читаются как «никто ничего не держит».

Отдельная проверка — **нагрузка без очереди**: очередь ComfyUI пуста, а карта
занята и считает. Значит работает не этот экземпляр: либо второй, либо чужая
программа, либо прошлая задача не отпустила память. Для инцидента с питанием
это первоочередная улика, поэтому вердикт `FAIL`, а не примечание.

В списке процессов на WDDM видны и обычные приложения рабочего стола
(`dwm.exe`, `chrome.exe`, `explorer.exe`) — они тоже занимают VRAM. Если
свободной памяти не хватает, а `torch` держит единицы мегабайт, выгрузка
моделей не поможет: память занята не ComfyUI, и скрипт об этом прямо пишет.

---

## 5. Текущая последовательность по инциденту

```powershell
# 1. применить второе исправление, чтобы одна перезагрузка закрыла оба
.\apply_safehold_fix.ps1 -Action MemoryCompression -Confirm

# 2. перезагрузка штатно: REBOOT_PRECHECK -> reboot -> REBOOT_POSTCHECK  (руки владельца)

# 3. после перезагрузки — проверить, что всё на месте
Set-Location "$env:USERPROFILE\sofia_tools"; .\get_sofia_tools.ps1
.\apply_safehold_fix.ps1 -Action Status

# 4. MemTest86 с флешки, минимум 4 прохода                (руки владельца)
#    новые адреса из отчёта:
#    .\apply_safehold_fix.ps1 -Action BadMemoryList -Address 0x... -Confirm

# 5. окно наблюдения
.\watch_host_stability.ps1 -Hours 48

# 6. если окно чистое — снятие HOST_SAFE_HOLD.flag штатной процедурой governor
#    (решение владельца, скрипты флаг не трогают)
```

---

## 6. Ручные проверки без скриптов

```powershell
# события Kernel-Power 41 и BSOD за 14 дней
Get-WinEvent -FilterHashtable @{LogName='System'; Id=41,6008,1001; StartTime=(Get-Date).AddDays(-14)} |
    Select-Object TimeCreated, Id, ProviderName | Format-Table -AutoSize

# аппаратные ошибки WHEA
Get-WinEvent -FilterHashtable @{LogName='System'; ProviderName='Microsoft-Windows-WHEA-Logger'} -MaxEvents 20 |
    Select-Object TimeCreated, Id, Message | Format-List

# текущий список исключённых страниц памяти
bcdedit /enum '{badmemory}'

# состояние сжатия памяти
Get-MMAgent | Select-Object MemoryCompression, PageCombining

# дампы
Get-ChildItem C:\Windows\Minidump | Sort-Object LastWriteTime -Descending | Select-Object -First 10

# GPU
nvidia-smi -q -d TEMPERATURE,POWER,PERFORMANCE
```

---

## Границы

Скрипты **никогда** не трогают `HOST_SAFE_HOLD.flag`, publishing state, `FROZEN`,
Task Scheduler и не удаляют файлы. Ни один скрипт не перезапускает сервисы.
Перезагрузка, изменения BIOS, MemTest86 и перестановка планок — руки и решение
владельца.

Единственное обращение к живому сервису — `check_gpu_lease.ps1 -Action Release
-Confirm`: выгрузка моделей через собственный endpoint ComfyUI `/free`, и только
при пустой очереди. Это не перезапуск и не затрагивает выполняющиеся задачи.
