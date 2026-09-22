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
    [ValidateSet('PowerLimit','Rollback','Status')]
    [string] $Action = 'Status',

    [ValidateRange(50,100)]
    [int] $Percent = 80,

    [int] $GpuIndex = 0,

    [string] $StateDir = (Join-Path ([System.IO.Path]::GetTempPath()) 'sofia_safehold_fix'),

    [switch] $Confirm
)

$ErrorActionPreference = 'Stop'
$rollbackPath = Join-Path $StateDir ("gpu{0}_powerlimit_rollback.json" -f $GpuIndex)

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

try {
    $gpu = Get-GpuPower -Index $GpuIndex
} catch {
    Write-Host ("Не удалось прочитать состояние GPU: {0}" -f $_.Exception.Message) -ForegroundColor Red
    Write-Host 'Проверьте, что драйвер NVIDIA установлен и nvidia-smi доступен в PATH.' -ForegroundColor Red
    exit 2
}

switch ($Action) {

    'Status' {
        Show-State -Gpu $gpu
        Write-Host ''
        Write-Host 'HOST_SAFE_HOLD.flag этот скрипт не трогает ни при каких параметрах.' -ForegroundColor Yellow
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
        if (-not (Test-Path $rollbackPath)) {
            Write-Host 'Файл отката не найден — откатывать нечего.' -ForegroundColor Yellow
            Show-State -Gpu $gpu
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
