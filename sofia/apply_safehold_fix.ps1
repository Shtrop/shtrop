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
      - не перезапускает сервисы, не трогает Task Scheduler, не делает reboot;
      - не удаляет ни одного файла;
      - не правит конфиги студии (схему подтвердить неоткуда — fail-closed).

    Без -Confirm выполняется dry-run: показывает, что было бы сделано.

.PARAMETER Action
    PowerLimit - ограничить энергопотребление GPU.
    Rollback   - вернуть значение из файла отката.
    Status     - показать текущие и сохранённые значения.

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
    nvidia-smi -pl требует прав администратора. Ограничение не сохраняется
    после перезагрузки: после reboot применить заново или закрепить штатно.
#>

[CmdletBinding()]
param(
    [ValidateSet('PowerLimit','MemoryCompression','Rollback','Status')]
    [string] $Action = 'Status',

    [ValidateRange(50,100)]
    [int] $Percent = 80,

    [int] $GpuIndex = 0,

    [string] $StateDir = (Join-Path ([System.IO.Path]::GetTempPath()) 'sofia_safehold_fix'),

    [switch] $Confirm
)

$ErrorActionPreference = 'Stop'
$rollbackPath = Join-Path $StateDir ("gpu{0}_powerlimit_rollback.json" -f $GpuIndex)
$mcRollbackPath = Join-Path $StateDir 'memory_compression_rollback.json'

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

if (-not $gpu -and $Action -eq 'PowerLimit') {
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
            Write-Host 'Дальше: контрольный локальный прогон пайплайна в --no-publish и' -ForegroundColor White
            Write-Host '        наблюдение .\watch_host_stability.ps1 -Hours 24' -ForegroundColor White
            Write-Host ("Откат : .\apply_safehold_fix.ps1 -Action Rollback -Confirm") -ForegroundColor DarkGray
        } else {
            Write-Host ''
            Write-Host ("FAIL: лимит остался {0} W. Нужны права администратора или лимит заблокирован." -f $after.Limit) -ForegroundColor Red
            exit 1
        }
    }

    'Rollback' {
        $didSomething = $false

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
