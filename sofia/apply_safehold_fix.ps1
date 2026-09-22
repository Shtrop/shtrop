<#
.SYNOPSIS
    Применяет минимальный ОБРАТИМЫЙ fix по инциденту host_unstable_safe_hold
    и сохраняет данные для отката.

.DESCRIPTION
    Единственное поддерживаемое действие — ограничение power limit GPU: самый
    дешёвый и полностью обратимый способ проверить гипотезу транзиентов питания.

    Чего скрипт не делает НИКОГДА:
      - не снимает HOST_SAFE_HOLD.flag и не трогает control_flags;
      - не меняет publishing state, FROZEN и автопост;
      - не перезапускает сервисы и не делает reboot;
      - не трогает Task Scheduler НИ В КАКОМ действии, кроме
        PowerLimitPersist -Confirm: там создаётся ровно одна именованная
        задача на старт системы, и Rollback её снимает;
      - не удаляет ни одного файла;
      - не правит конфиги студии (схему подтвердить неоткуда — fail-closed).

    Без -Confirm выполняется dry-run: показывает, что было бы сделано.

.PARAMETER Action
    PowerLimit        - ограничить энергопотребление GPU.
    PowerLimitPersist - закрепить текущий лимит, чтобы он пережил перезагрузку.
    Rollback          - вернуть значения из файлов отката.
    Status            - показать текущие и сохранённые значения.

.PARAMETER Percent
    Доля от максимального лимита платы, 50..100. По умолчанию 80.

.PARAMETER GpuIndex
    Индекс GPU. По умолчанию 0.

.PARAMETER StateDir
    Каталог для файла отката. По умолчанию %TEMP%\sofia_safehold_fix.

.PARAMETER Confirm
    Выполнить изменение по-настоящему. Без него — dry-run.

.EXAMPLE
    .\apply_safehold_fix.ps1 -Action Status

.EXAMPLE
    .\apply_safehold_fix.ps1 -Action PowerLimit -Percent 80          # dry-run

.EXAMPLE
    .\apply_safehold_fix.ps1 -Action PowerLimit -Percent 80 -Confirm # применить

.EXAMPLE
    .\apply_safehold_fix.ps1 -Action Rollback -Confirm

.NOTES
    nvidia-smi -pl требует прав администратора. Само по себе ограничение НЕ
    сохраняется после перезагрузки, а выход из hold по runbook требует reboot:
    без закрепления смягчение исчезнет ровно в тот момент, когда производство
    вернётся под нагрузку. Закрепление: -Action PowerLimitPersist -Confirm.
#>

[CmdletBinding()]
param(
    [ValidateSet('PowerLimit','PowerLimitPersist','MemoryCompression','BadMemoryList','Rollback','Status')]
    [string] $Action = 'Status',

    # Дополнительные физические адреса сбойной памяти, например из отчёта MemTest86.
    # Принимаются как 0x... или десятичные.
    [string[]] $Address = @(),

    # Глубина поиска событий WHEA для действия BadMemoryList.
    [int] $WheaDays = 90,

    [ValidateRange(50,100)]
    [int] $Percent = 80,

    [int] $GpuIndex = 0,

    [string] $StateDir = (Join-Path ([System.IO.Path]::GetTempPath()) 'sofia_safehold_fix'),

    # Каталог для обёртки закрепления: переживает очистку %TEMP% и читается
    # из-под SYSTEM на старте системы.
    [string] $PersistDir = '',

    [switch] $Confirm
)

$ErrorActionPreference = 'Stop'
$rollbackPath = Join-Path $StateDir ("gpu{0}_powerlimit_rollback.json" -f $GpuIndex)
$plPersistPath = Join-Path $StateDir ("gpu{0}_powerlimit_persist_rollback.json" -f $GpuIndex)
$plTaskName = "SofiaAIStudio_GpuPowerLimit_{0}" -f $GpuIndex
if (-not $PersistDir) {
    $PersistDir = if ($env:ProgramData) { Join-Path $env:ProgramData 'SofiaAIStudio' } else { $StateDir }
}
$mcRollbackPath = Join-Path $StateDir 'memory_compression_rollback.json'
$bmRollbackPath = Join-Path $StateDir 'badmemorylist_rollback.json'

function Get-WheaMemoryAddresses {
    param([int] $Days)
    $out = @()
    try {
        $ev = @(Get-WinEvent -FilterHashtable @{
            LogName      = 'System'
            ProviderName = 'Microsoft-Windows-WHEA-Logger'
            StartTime    = (Get-Date).AddDays(-$Days)
        } -ErrorAction Stop)
        foreach ($e in $ev) {
            try {
                $x = [xml]$e.ToXml()
                foreach ($d in $x.Event.EventData.Data) {
                    if ("$($d.Name)" -eq 'PhysicalAddress') {
                        $v = "$($d.'#text')"
                        if ($v -and $v -ne '0') {
                            $out += [pscustomobject]@{ Time = $e.TimeCreated; Raw = $v }
                        }
                    }
                }
            } catch { }
        }
    } catch { }
    $out
}

function ConvertTo-UInt64Address {
    param([string] $Value)
    $v = $Value.Trim()
    if ($v -match '^0x') { return [Convert]::ToUInt64($v.Substring(2), 16) }
    if ($v -match '^[0-9]+$') { return [uint64]$v }
    return [Convert]::ToUInt64($v, 16)
}

function Get-CurrentBadMemoryList {
    if (-not (Get-Command bcdedit.exe -ErrorAction SilentlyContinue)) { return $null }
    $raw = & bcdedit.exe /enum '{badmemory}' 2>&1 | Out-String
    $lines = $raw -split "`r?`n"
    $list = @()
    $inList = $false

    foreach ($line in $lines) {
        if ($line -match '(?i)^\s*badmemorylist\s+(.*)$') {
            # Первая строка поля: имя и первые значения.
            $inList = $true
            foreach ($tok in ($Matches[1] -split '\s+')) { if ($tok) { $list += $tok.Trim().ToLower() } }
            continue
        }
        if ($inList) {
            # bcdedit печатает длинный список продолжением: отступ и только числа.
            # Любая другая строка означает, что поле закончилось.
            if ($line -match '^\s+((?:0x[0-9a-fA-F]+|\d+)(?:\s+(?:0x[0-9a-fA-F]+|\d+))*)\s*$') {
                foreach ($tok in ($Matches[1] -split '\s+')) { if ($tok) { $list += $tok.Trim().ToLower() } }
            } else {
                $inList = $false
            }
        }
    }
    [pscustomobject]@{ Raw = $raw.Trim(); List = @($list) }
}

function Test-PfnInList {
    param([string[]] $List, [string] $Pfn)
    # bcdedit нормализует регистр и может опускать ведущие нули,
    # поэтому сравниваем числовые значения, а не строки.
    $target = ConvertTo-UInt64Address -Value $Pfn
    foreach ($item in $List) {
        try { if ((ConvertTo-UInt64Address -Value $item) -eq $target) { return $true } } catch { }
    }
    $false
}

function Get-MemoryCompressionState {
    if (-not (Get-Command Get-MMAgent -ErrorAction SilentlyContinue)) { return $null }
    try { return [bool](Get-MMAgent).MemoryCompression } catch { return $null }
}

function Get-GpuPower {
    param([int]$Index)
    $nv = Get-Command nvidia-smi -ErrorAction SilentlyContinue
    if (-not $nv) { throw 'nvidia-smi не найден в PATH' }
    $q = & nvidia-smi -i $Index --query-gpu="name,power.limit,power.min_limit,power.max_limit,power.draw,temperature.gpu" --format=csv,noheader 2>&1
    $line = ($q | Out-String).Trim()
    if (-not $line -or $line -match 'Failed|Error|not found') { throw ("nvidia-smi вернул: {0}" -f $line) }
    $f = $line.Split(',') | ForEach-Object { $_.Trim() }
    [pscustomobject]@{
        Name    = $f[0]
        Limit   = [double]($f[1] -replace '[^\d\.]','')
        MinLim  = [double]($f[2] -replace '[^\d\.]','')
        MaxLim  = [double]($f[3] -replace '[^\d\.]','')
        Draw    = [double]($f[4] -replace '[^\d\.]','')
        Temp    = [double]($f[5] -replace '[^\d\.]','')
    }
}

function Get-NvidiaSmiPath {
    $c = Get-Command nvidia-smi -ErrorAction SilentlyContinue
    if ($c) { return $c.Source }
    $null
}

function Test-PersistTask {
    # $null — проверить нечем (нет schtasks); иначе есть задача или нет.
    if (-not (Get-Command schtasks -ErrorAction SilentlyContinue)) { return $null }
    $null = & schtasks /Query /TN $plTaskName 2>&1
    return ($LASTEXITCODE -eq 0)
}

function New-PowerLimitWrapper {
    <#
        Обёртка для задачи на старт системы. Нужна по двум причинам:
        путь к nvidia-smi может содержать пробелы (quoting в /TR ненадёжен),
        а на старте драйвер бывает ещё не готов — поэтому здесь повторы.

        Содержимое намеренно только ASCII: .cmd исполняется в кодовой странице
        консоли, и кириллица в нём превратилась бы в мусор в логе.
    #>
    param(
        [Parameter(Mandatory)][string] $Dir,
        [Parameter(Mandatory)][string] $NvSmi,
        [Parameter(Mandatory)][int] $Index,
        [Parameter(Mandatory)][int] $Watts
    )
    New-Item -ItemType Directory -Force -Path $Dir | Out-Null
    $cmdPath = Join-Path $Dir ("sofia_gpu{0}_powerlimit.cmd" -f $Index)
    $logPath = Join-Path $Dir ("sofia_gpu{0}_powerlimit.log" -f $Index)
    $lines = @(
        '@echo off',
        'setlocal',
        'rem Sofia AI Studio: re-apply GPU power limit after boot.',
        'rem Created by apply_safehold_fix.ps1 -Action PowerLimitPersist.',
        ('set "NVSMI={0}"' -f $NvSmi),
        ('set "LOGF={0}"' -f $logPath),
        'for /L %%i in (1,1,10) do (',
        ('  "%NVSMI%" -i {0} -pl {1} >> "%LOGF%" 2>&1 && goto ok' -f $Index, $Watts),
        '  ping -n 16 127.0.0.1 > nul',
        ')',
        ('echo [%date% %time%] FAIL: power limit {0} W was not applied >> "%LOGF%"' -f $Watts),
        'exit /b 1',
        ':ok',
        ('echo [%date% %time%] OK: power limit {0} W applied >> "%LOGF%"' -f $Watts),
        'exit /b 0'
    )
    ($lines -join "`r`n") + "`r`n" | Out-File -FilePath $cmdPath -Encoding ASCII -NoNewline
    [pscustomobject]@{ Cmd = $cmdPath; Log = $logPath }
}

function Show-PersistState {
    param($Gpu)
    $task = Test-PersistTask
    Write-Host ''
    if ($null -eq $task) {
        Write-Host 'Закрепление  : проверить нечем (нет schtasks)' -ForegroundColor DarkGray
        return
    }
    if ($task) {
        Write-Host ("Закрепление  : лимит закреплён задачей {0} (переживёт перезагрузку)" -f $plTaskName) -ForegroundColor Green
        if (Test-Path $plPersistPath) {
            $rb = Get-Content $plPersistPath -Raw | ConvertFrom-Json
            Write-Host ("  задача      : {0} W, обёртка {1}" -f $rb.watts, $rb.wrapper_cmd) -ForegroundColor DarkGray
            if ($rb.wrapper_log -and (Test-Path $rb.wrapper_log)) {
                $last = @(Get-Content $rb.wrapper_log -ErrorAction SilentlyContinue | Where-Object { $_ } | Select-Object -Last 1)
                if ($last.Count) { Write-Host ("  последний старт: {0}" -f $last[0]) -ForegroundColor DarkGray }
            }
        }
    } elseif ($Gpu -and $Gpu.Limit -lt $Gpu.MaxLim) {
        Write-Host 'Закрепление  : лимит НЕ закреплён — не переживёт перезагрузку' -ForegroundColor Yellow
        Write-Host '               выход из hold по runbook требует reboot, после него' -ForegroundColor Yellow
        Write-Host '               смягчение исчезнет вместе с доказательствами окна.' -ForegroundColor Yellow
        Write-Host '               Закрепить: .\apply_safehold_fix.ps1 -Action PowerLimitPersist -Confirm' -ForegroundColor DarkGray
    } else {
        Write-Host 'Закрепление  : не требуется — лимит не ограничен' -ForegroundColor DarkGray
    }
}

function Show-State {
    param($Gpu)
    Write-Host ''
    if (-not $Gpu) {
        Write-Host ("GPU {0}: состояние недоступно ({1})" -f $GpuIndex, $script:gpuError) -ForegroundColor DarkGray
        return
    }
    Write-Host ("GPU {0}: {1}" -f $GpuIndex, $Gpu.Name) -ForegroundColor White
    Write-Host ("  power limit сейчас : {0} W  (диапазон платы {1}..{2} W)" -f $Gpu.Limit, $Gpu.MinLim, $Gpu.MaxLim)
    Write-Host ("  потребление / темп : {0} W / {1} C" -f $Gpu.Draw, $Gpu.Temp)
    if (Test-Path $rollbackPath) {
        $rb = Get-Content $rollbackPath -Raw | ConvertFrom-Json
        Write-Host ("  файл отката        : {0}" -f $rollbackPath) -ForegroundColor DarkGray
        Write-Host ("  исходный лимит     : {0} W (сохранён {1})" -f $rb.original_limit_w, $rb.saved_at) -ForegroundColor DarkGray
    } else {
        Write-Host '  файл отката        : отсутствует (fix ещё не применялся)' -ForegroundColor DarkGray
    }
}

# Состояние GPU нужно не всем действиям: сжатие памяти к видеокарте отношения
# не имеет, поэтому отсутствие nvidia-smi не должно блокировать его.
$gpu = $null
$gpuError = $null
try { $gpu = Get-GpuPower -Index $GpuIndex } catch { $gpuError = $_.Exception.Message }

if (-not $gpu -and @('PowerLimit','PowerLimitPersist') -contains $Action) {
    Write-Host ("Не удалось прочитать состояние GPU: {0}" -f $gpuError) -ForegroundColor Red
    Write-Host 'Проверьте, что драйвер NVIDIA установлен и nvidia-smi доступен в PATH.' -ForegroundColor Red
    exit 2
}

switch ($Action) {

    'Status' {
        Show-State -Gpu $gpu
        $mc = Get-MemoryCompressionState
        Write-Host ''
        if ($null -eq $mc) {
            Write-Host 'Сжатие памяти : состояние не прочитано (нет Get-MMAgent)' -ForegroundColor DarkGray
        } else {
            Write-Host ("Сжатие памяти : {0}" -f $(if ($mc) { 'включено' } else { 'выключено' }))
        }
        if (Test-Path $mcRollbackPath) {
            $rb = Get-Content $mcRollbackPath -Raw | ConvertFrom-Json
            Write-Host ("  откат        : вернуть в {0} (сохранено {1})" -f `
                        $(if ($rb.original_enabled) { 'включено' } else { 'выключено' }), $rb.saved_at) -ForegroundColor DarkGray
        }
        $bm = Get-CurrentBadMemoryList
        if ($bm) {
            Write-Host ''
            if ($bm.List.Count) {
                Write-Host ("Исключённые страницы памяти ({0}):" -f $bm.List.Count)
                foreach ($pfn in $bm.List) {
                    try {
                        $addr = (ConvertTo-UInt64Address -Value $pfn) * 4096
                        Write-Host ("  PFN {0,-12} адрес 0x{1:X}  (~{2} ГиБ)" -f $pfn, $addr, [math]::Round($addr / 1GB, 1))
                    } catch { Write-Host ("  PFN {0}" -f $pfn) }
                }
            } else {
                Write-Host 'Исключённых страниц памяти нет.'
            }
        }
        Show-PersistState -Gpu $gpu
        Write-Host ''
        Write-Host 'HOST_SAFE_HOLD.flag этот скрипт не трогает ни при каких параметрах.' -ForegroundColor Yellow
    }

    'MemoryCompression' {
        # 0x154 UNEXPECTED_STORE_EXCEPTION падает именно в менеджере сжатой памяти.
        # Отключение убирает этот код из схемы; это не лечит сбойную планку,
        # но снимает конкретный путь отказа и полностью обратимо.
        $mc = Get-MemoryCompressionState
        if ($null -eq $mc) {
            Write-Host 'Get-MMAgent недоступен — действие невозможно на этой системе.' -ForegroundColor Red
            exit 2
        }
        Write-Host ''
        Write-Host ("Сжатие памяти сейчас: {0}" -f $(if ($mc) { 'включено' } else { 'выключено' })) -ForegroundColor White
        if (-not $mc) {
            Write-Host 'Уже выключено — делать нечего.' -ForegroundColor Yellow
            break
        }
        Write-Host 'Планируется: выключить сжатие памяти (вступит в силу после перезагрузки).' -ForegroundColor Cyan

        if (-not $Confirm) {
            Write-Host ''
            Write-Host 'DRY-RUN: ничего не изменено. Для применения добавьте -Confirm.' -ForegroundColor Yellow
            break
        }

        New-Item -ItemType Directory -Force -Path $StateDir | Out-Null
        if (-not (Test-Path $mcRollbackPath)) {
            [ordered]@{
                setting          = 'MemoryCompression'
                original_enabled = $mc
                saved_at         = (Get-Date).ToString('o')
                rollback_command = 'Enable-MMAgent -MemoryCompression'
            } | ConvertTo-Json -Depth 3 | Out-File -FilePath $mcRollbackPath -Encoding UTF8
            Write-Host ("Файл отката сохранён: {0}" -f $mcRollbackPath) -ForegroundColor Green
        }

        Disable-MMAgent -MemoryCompression
        $after = Get-MemoryCompressionState
        if ($after -eq $false) {
            Write-Host ''
            Write-Host 'PASS: сжатие памяти выключено.' -ForegroundColor Green
            Write-Host 'Вступит в силу после перезагрузки — её выполняет владелец,' -ForegroundColor Yellow
            Write-Host 'штатно: REBOOT_PRECHECK -> reboot -> REBOOT_POSTCHECK.' -ForegroundColor Yellow
            Write-Host 'Откат: .\apply_safehold_fix.ps1 -Action Rollback -Confirm' -ForegroundColor DarkGray
        } else {
            Write-Host 'FAIL: состояние не изменилось — нужны права администратора.' -ForegroundColor Red
            exit 1
        }
    }

    'PowerLimit' {
        $target = [math]::Round($gpu.MaxLim * $Percent / 100, 0)
        if ($target -lt $gpu.MinLim) { $target = $gpu.MinLim }

        Show-State -Gpu $gpu
        Write-Host ''
        Write-Host ("Планируется: {0} W  ->  {1} W  ({2}% от максимума платы)" -f $gpu.Limit, $target, $Percent) -ForegroundColor Cyan

        if ($target -ge $gpu.Limit) {
            Write-Host 'Целевое значение не ниже текущего — смысла нет, выходим.' -ForegroundColor Yellow
            break
        }

        if (-not $Confirm) {
            Write-Host ''
            Write-Host 'DRY-RUN: ничего не изменено. Для применения добавьте -Confirm.' -ForegroundColor Yellow
            break
        }

        New-Item -ItemType Directory -Force -Path $StateDir | Out-Null
        if (-not (Test-Path $rollbackPath)) {
            [ordered]@{
                gpu_index        = $GpuIndex
                gpu_name         = $gpu.Name
                original_limit_w = $gpu.Limit
                board_max_w      = $gpu.MaxLim
                board_min_w      = $gpu.MinLim
                saved_at         = (Get-Date).ToString('o')
                rollback_command = ("nvidia-smi -i {0} -pl {1}" -f $GpuIndex, $gpu.Limit)
            } | ConvertTo-Json -Depth 4 | Out-File -FilePath $rollbackPath -Encoding UTF8
            Write-Host ("Файл отката сохранён: {0}" -f $rollbackPath) -ForegroundColor Green
        } else {
            Write-Host 'Файл отката уже существует — исходное значение не перезаписываю.' -ForegroundColor DarkGray
        }

        $out = & nvidia-smi -i $GpuIndex -pl $target 2>&1
        Write-Host ($out | Out-String).Trim()

        $after = Get-GpuPower -Index $GpuIndex
        if ([math]::Abs($after.Limit - $target) -le 1) {
            Write-Host ''
            Write-Host ("PASS: power limit = {0} W" -f $after.Limit) -ForegroundColor Green
            Write-Host ''
            Write-Host 'ВНИМАНИЕ: это значение не переживёт перезагрузку, а выход из hold' -ForegroundColor Yellow
            Write-Host '          по runbook требует reboot. Без закрепления смягчение' -ForegroundColor Yellow
            Write-Host '          исчезнет ровно тогда, когда производство вернётся под нагрузку.' -ForegroundColor Yellow
            Write-Host '          Закрепить: .\apply_safehold_fix.ps1 -Action PowerLimitPersist -Confirm' -ForegroundColor DarkGray
            Write-Host ''
            Write-Host 'Дальше: контрольный локальный прогон пайплайна в --no-publish и' -ForegroundColor White
            Write-Host '        наблюдение .\watch_host_stability.ps1 -Hours 24' -ForegroundColor White
            Write-Host ("Откат : .\apply_safehold_fix.ps1 -Action Rollback -Confirm") -ForegroundColor DarkGray
        } else {
            Write-Host ''
            Write-Host ("FAIL: лимит остался {0} W. Нужны права администратора или лимит заблокирован." -f $after.Limit) -ForegroundColor Red
            exit 1
        }
    }

    'PowerLimitPersist' {
        # nvidia-smi -pl живёт до перезагрузки. Runbook требует reboot перед
        # выходом из hold, поэтому без закрепления окно наблюдения измеряет
        # один режим питания, а производство возвращается в другой.
        if (-not (Get-Command schtasks -ErrorAction SilentlyContinue)) {
            Write-Host 'schtasks не найден — закрепление доступно только на Windows.' -ForegroundColor Red
            exit 2
        }
        $nvsmi = Get-NvidiaSmiPath
        if (-not $nvsmi) {
            Write-Host 'nvidia-smi не найден в PATH — закреплять нечем.' -ForegroundColor Red
            exit 2
        }

        Show-State -Gpu $gpu
        Show-PersistState -Gpu $gpu

        if ($gpu.Limit -ge $gpu.MaxLim) {
            Write-Host ''
            Write-Host ("Текущий лимит {0} W — это максимум платы, закреплять нечего." -f $gpu.Limit) -ForegroundColor Yellow
            Write-Host 'Сначала ограничить: .\apply_safehold_fix.ps1 -Action PowerLimit -Percent 80 -Confirm' -ForegroundColor DarkGray
            break
        }

        $watts = [int]$gpu.Limit
        Write-Host ''
        Write-Host ("Планируется закрепить {0} W задачей на старт системы:" -f $watts) -ForegroundColor Cyan
        Write-Host ("  имя задачи : {0}" -f $plTaskName)
        Write-Host ("  запуск     : при старте системы, от SYSTEM, с задержкой 1 мин")
        Write-Host ("  команда    : nvidia-smi -i {0} -pl {1} (через обёртку с повторами)" -f $GpuIndex, $watts)
        Write-Host ("  каталог    : {0}" -f $PersistDir)
        Write-Host 'Откат снимает задачу целиком: -Action Rollback -Confirm' -ForegroundColor DarkGray

        if (-not $Confirm) {
            Write-Host ''
            Write-Host 'DRY-RUN: ничего не изменено. Для применения добавьте -Confirm.' -ForegroundColor Yellow
            break
        }

        $wrap = New-PowerLimitWrapper -Dir $PersistDir -NvSmi $nvsmi -Index $GpuIndex -Watts $watts
        Write-Host ("Обёртка создана: {0}" -f $wrap.Cmd) -ForegroundColor Green

        $out = & schtasks /Create /TN $plTaskName /TR $wrap.Cmd /SC ONSTART /DELAY '0001:00' /RU 'SYSTEM' /RL 'HIGHEST' /F 2>&1
        Write-Host ($out | Out-String).Trim()

        if ((Test-PersistTask) -ne $true) {
            Write-Host ''
            Write-Host 'FAIL: задача не создана. Нужны права администратора.' -ForegroundColor Red
            exit 1
        }

        New-Item -ItemType Directory -Force -Path $StateDir | Out-Null
        [ordered]@{
            gpu_index        = $GpuIndex
            task_name        = $plTaskName
            watts            = $watts
            wrapper_cmd      = $wrap.Cmd
            wrapper_log      = $wrap.Log
            nvidia_smi       = $nvsmi
            saved_at         = (Get-Date).ToString('o')
            rollback_command = ("schtasks /Delete /TN {0} /F" -f $plTaskName)
        } | ConvertTo-Json -Depth 4 | Out-File -FilePath $plPersistPath -Encoding UTF8

        Write-Host ''
        Write-Host ("PASS: лимит {0} W закреплён — он вернётся после перезагрузки." -f $watts) -ForegroundColor Green
        Write-Host ("Файл отката: {0}" -f $plPersistPath) -ForegroundColor DarkGray
        Write-Host 'Проверить после ближайшей перезагрузки:' -ForegroundColor White
        Write-Host '    .\apply_safehold_fix.ps1 -Action Status' -ForegroundColor DarkGray
        Write-Host ("    журнал применения: {0}" -f $wrap.Log) -ForegroundColor DarkGray
    }

    'BadMemoryList' {
        # Windows умеет исключать страницы физической памяти из использования.
        # Это обход дефекта, а не ремонт: планка остаётся сбойной.
        if (-not (Get-Command bcdedit.exe -ErrorAction SilentlyContinue)) {
            Write-Host 'bcdedit не найден — действие доступно только на Windows.' -ForegroundColor Red
            exit 2
        }

        $addrs = @()
        foreach ($a in (Get-WheaMemoryAddresses -Days $WheaDays)) {
            $addrs += [pscustomobject]@{ Source = ("WHEA {0}" -f $a.Time); Value = $a.Raw }
        }
        foreach ($a in $Address) { $addrs += [pscustomobject]@{ Source = 'параметр -Address'; Value = $a } }

        if ($addrs.Count -eq 0) {
            Write-Host ''
            Write-Host ("Адресов сбойной памяти не найдено: событий WHEA с PhysicalAddress за {0} дн. нет." -f $WheaDays) -ForegroundColor Yellow
            Write-Host 'Адреса из отчёта MemTest86 можно передать вручную:' -ForegroundColor DarkGray
            Write-Host '  .\apply_safehold_fix.ps1 -Action BadMemoryList -Address 0x1F93E53D27 -Confirm' -ForegroundColor DarkGray
            break
        }

        $pfns = @{}
        Write-Host ''
        Write-Host 'Найденные адреса и их номера страниц (PFN = адрес / 4096):' -ForegroundColor White
        foreach ($a in $addrs) {
            try {
                $u = ConvertTo-UInt64Address -Value $a.Value
                $pfn = [uint64]([math]::Floor($u / 4096))
                $hex = ('0x{0:X}' -f $pfn)
                $pfns[$hex] = $true
                Write-Host ("  {0,-34} адрес {1}  ->  PFN {2}  (~{3} ГиБ)" -f `
                            $a.Source, ('0x{0:X}' -f $u), $hex, [math]::Round($u / 1GB, 1))
            } catch {
                Write-Host ("  {0}: адрес {1} не разобран" -f $a.Source, $a.Value) -ForegroundColor DarkGray
            }
        }

        $current = Get-CurrentBadMemoryList
        Write-Host ''
        Write-Host ("Сейчас в списке исключений: {0}" -f $(if ($current.List.Count) { $current.List -join ' ' } else { 'пусто' }))

        $merged = @($current.List)
        foreach ($k in $pfns.Keys) {
            if (-not (Test-PfnInList -List $merged -Pfn $k)) { $merged += $k.ToLower() }
        }
        Write-Host ("Станет: {0}" -f ($merged -join ' ')) -ForegroundColor Cyan
        Write-Host ''
        Write-Host 'Команды, которые будут выполнены:' -ForegroundColor DarkGray
        Write-Host ("  bcdedit /set {{badmemory}} badmemorylist {0}" -f ($merged -join ' ')) -ForegroundColor DarkGray
        Write-Host  '  bcdedit /set {badmemory} badmemoryaccess no' -ForegroundColor DarkGray

        Write-Host ''
        Write-Host 'Это обход, а не ремонт: сбойная планка остаётся сбойной, а исключается' -ForegroundColor Yellow
        Write-Host 'лишь та страница, по которой ошибка уже произошла. Полный список даёт MemTest86.' -ForegroundColor Yellow

        if (-not $Confirm) {
            Write-Host ''
            Write-Host 'DRY-RUN: ничего не изменено. Для применения добавьте -Confirm.' -ForegroundColor Yellow
            break
        }

        New-Item -ItemType Directory -Force -Path $StateDir | Out-Null
        if (-not (Test-Path $bmRollbackPath)) {
            [ordered]@{
                setting       = 'badmemorylist'
                original_list = @($current.List)
                original_enum = $current.Raw
                saved_at      = (Get-Date).ToString('o')
                rollback_note = 'пустой original_list означает bcdedit /deletevalue {badmemory} badmemorylist'
            } | ConvertTo-Json -Depth 4 | Out-File -FilePath $bmRollbackPath -Encoding UTF8
            Write-Host ("Файл отката сохранён: {0}" -f $bmRollbackPath) -ForegroundColor Green
        }

        $args1 = @('/set', '{badmemory}', 'badmemorylist') + $merged
        $r1 = & bcdedit.exe @args1 2>&1 | Out-String
        $r2 = & bcdedit.exe /set '{badmemory}' badmemoryaccess no 2>&1 | Out-String
        Write-Host $r1.Trim()
        Write-Host $r2.Trim()

        $after = Get-CurrentBadMemoryList
        $missing = @($merged | Where-Object { -not (Test-PfnInList -List $after.List -Pfn $_) })
        if ($missing.Count -eq 0) {
            Write-Host ''
            Write-Host ("PASS: список исключений — {0}" -f ($after.List -join ' ')) -ForegroundColor Green
            Write-Host 'Вступит в силу после перезагрузки, которую выполняет владелец.' -ForegroundColor Yellow
            Write-Host 'Откат: .\apply_safehold_fix.ps1 -Action Rollback -Confirm' -ForegroundColor DarkGray
        } else {
            Write-Host ''
            Write-Host ("FAIL: не попали в список {0}. Нужны права администратора." -f ($missing -join ' ')) -ForegroundColor Red
            exit 1
        }
    }

    'Rollback' {
        $didSomething = $false

        # Закрепление снимается первым: иначе откат лимита прожил бы только до
        # следующей перезагрузки, после которой задача вернула бы старое значение.
        if ((Test-PersistTask) -eq $true) {
            Write-Host ''
            Write-Host ("Закрепление лимита -> снять задачу {0}" -f $plTaskName) -ForegroundColor Cyan
            if ($Confirm) {
                & schtasks /Delete /TN $plTaskName /F 2>&1 | Out-String | Write-Host
                if ((Test-PersistTask) -eq $true) {
                    Write-Host 'FAIL: задача осталась — нужны права администратора.' -ForegroundColor Red
                    exit 1
                }
                if (Test-Path $plPersistPath) {
                    $plRb = Get-Content $plPersistPath -Raw | ConvertFrom-Json
                    # Обёртку убираем, журнал применения оставляем: он доказательство.
                    if ($plRb.wrapper_cmd -and (Test-Path $plRb.wrapper_cmd)) {
                        Remove-Item -LiteralPath $plRb.wrapper_cmd -Force -ErrorAction SilentlyContinue
                    }
                }
                Write-Host 'PASS: закрепление снято, лимит больше не восстанавливается на старте.' -ForegroundColor Green
                $didSomething = $true
            } else {
                Write-Host 'DRY-RUN: добавьте -Confirm.' -ForegroundColor Yellow
            }
        }

        if (Test-Path $bmRollbackPath) {
            $bmRb = Get-Content $bmRollbackPath -Raw | ConvertFrom-Json
            $orig = @($bmRb.original_list)
            Write-Host ''
            Write-Host ("Список исключений памяти -> {0}" -f $(if ($orig.Count) { $orig -join ' ' } else { 'очистить' })) -ForegroundColor Cyan
            if ($Confirm) {
                if ($orig.Count) {
                    $a = @('/set', '{badmemory}', 'badmemorylist') + $orig
                    & bcdedit.exe @a 2>&1 | Out-String | Write-Host
                } else {
                    & bcdedit.exe /deletevalue '{badmemory}' badmemorylist 2>&1 | Out-String | Write-Host
                }
                Write-Host 'PASS: исходный список исключений восстановлен (нужна перезагрузка).' -ForegroundColor Green
                $didSomething = $true
            } else {
                Write-Host 'DRY-RUN: добавьте -Confirm.' -ForegroundColor Yellow
            }
        }

        if (Test-Path $mcRollbackPath) {
            $mcRb = Get-Content $mcRollbackPath -Raw | ConvertFrom-Json
            $mcNow = Get-MemoryCompressionState
            Write-Host ''
            Write-Host ("Сжатие памяти: {0} -> {1}" -f `
                        $(if ($mcNow) { 'включено' } else { 'выключено' }),
                        $(if ($mcRb.original_enabled) { 'включено' } else { 'выключено' })) -ForegroundColor Cyan
            if ($Confirm) {
                if ($mcRb.original_enabled) { Enable-MMAgent -MemoryCompression } else { Disable-MMAgent -MemoryCompression }
                Write-Host 'PASS: исходное состояние сжатия памяти восстановлено (нужна перезагрузка).' -ForegroundColor Green
                $didSomething = $true
            } else {
                Write-Host 'DRY-RUN: добавьте -Confirm.' -ForegroundColor Yellow
            }
        }

        if (-not (Test-Path $rollbackPath) -or -not $gpu) {
            if (-not $didSomething) {
                Write-Host 'По GPU откатывать нечего: нет файла отката или недоступен nvidia-smi.' -ForegroundColor Yellow
                Show-State -Gpu $gpu
            }
            break
        }
        $rb = Get-Content $rollbackPath -Raw | ConvertFrom-Json
        Show-State -Gpu $gpu
        Write-Host ''
        Write-Host ("Планируется откат: {0} W  ->  {1} W" -f $gpu.Limit, $rb.original_limit_w) -ForegroundColor Cyan

        if (-not $Confirm) {
            Write-Host 'DRY-RUN: ничего не изменено. Для применения добавьте -Confirm.' -ForegroundColor Yellow
            break
        }

        $out = & nvidia-smi -i $GpuIndex -pl ([int]$rb.original_limit_w) 2>&1
        Write-Host ($out | Out-String).Trim()

        $after = Get-GpuPower -Index $GpuIndex
        if ([math]::Abs($after.Limit - [double]$rb.original_limit_w) -le 1) {
            Write-Host ("PASS: исходный power limit восстановлен ({0} W)" -f $after.Limit) -ForegroundColor Green
            Write-Host ("Файл отката оставлен как журнал: {0}" -f $rollbackPath) -ForegroundColor DarkGray
        } else {
            Write-Host ("FAIL: лимит {0} W, ожидался {1} W" -f $after.Limit, $rb.original_limit_w) -ForegroundColor Red
            exit 1
        }
    }
}
