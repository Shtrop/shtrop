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

---

## 4. Текущая последовательность по инциденту

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

## 5. Ручные проверки без скриптов

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
сервисы, Task Scheduler и не удаляют файлы. Перезагрузка, изменения BIOS,
MemTest86 и перестановка планок — руки и решение владельца.
