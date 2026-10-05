<#
.SYNOPSIS
    Регистрирует автопилот Growth Engine в планировщике Windows.

.DESCRIPTION
    Создаёт задачу, которая раз в неделю запускает tools/autopilot.py:
    прогон цикла, отчёт, статус и журнал прогонов.

    Автопилот НИЧЕГО НЕ ПУБЛИКУЕТ. Он не снимает HOLD и FROZEN, не трогает
    canonical state студии и ничего не удаляет. Публикация остаётся решением
    владельца и проходит через Master Publish Gate отдельно.

    Скрипт только регистрирует задачу. Вся логика в Python и покрыта тестами;
    здесь лишь вызов планировщика.

.PARAMETER Studio
    Корень студии. По умолчанию D:\AI_CONTENT\Sofia

.PARAMETER MediaDir
    Каталог готового медиа для проверки формата.

.PARAMETER Day
    День недели запуска. По умолчанию Monday.

.PARAMETER Time
    Время запуска в формате HH:mm. По умолчанию 08:00.

.PARAMETER Push
    Отправлять безопасные артефакты в ветку после прогона.

.PARAMETER Uninstall
    Удалить задачу.

.EXAMPLE
    .\install_task.ps1
    .\install_task.ps1 -Time 09:30 -Push
    .\install_task.ps1 -Uninstall
#>
[CmdletBinding()]
param(
    [string]$Studio = "D:\AI_CONTENT\Sofia",
    [string]$MediaDir = "",
    [ValidateSet("Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday")]
    [string]$Day = "Monday",
    [string]$Time = "08:00",
    [switch]$Push,
    [switch]$Uninstall
)

$ErrorActionPreference = "Stop"
$TaskName = "SofiaGrowthAutopilot"

if ($Uninstall) {
    if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "Задача $TaskName удалена." -ForegroundColor Green
    } else {
        Write-Host "Задача $TaskName не найдена — удалять нечего."
    }
    exit 0
}

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$script = Join-Path $repoRoot "sofia_growth\tools\autopilot.py"
if (-not (Test-Path $script)) { throw "Не найден $script — запускать из клона репозитория." }

$python = (Get-Command python -ErrorAction SilentlyContinue)
if (-not $python) { throw "Python не найден в PATH. Нужен Python 3.11+." }
$version = & python -c "import sys;print('%d.%d' % sys.version_info[:2])"
if ([version]$version -lt [version]"3.11") { throw "Нужен Python 3.11+, найден $version." }

$arguments = @("`"$script`"", "--studio", "`"$Studio`"")
if ($MediaDir) { $arguments += @("--media-dir", "`"$MediaDir`"") }
if ($Push)     { $arguments += "--push" }

$action    = New-ScheduledTaskAction -Execute $python.Source `
                                     -Argument ($arguments -join " ") `
                                     -WorkingDirectory $repoRoot
$trigger   = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $Day -At $Time
$settings  = New-ScheduledTaskSettingsSet -StartWhenAvailable `
                                          -DontStopOnIdleEnd `
                                          -ExecutionTimeLimit (New-TimeSpan -Hours 1)

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger `
                       -Settings $settings -Description "Growth Engine Sofia: недельный цикл. Ничего не публикует." `
                       -Force | Out-Null

Write-Host "Задача $TaskName зарегистрирована: $Day в $Time." -ForegroundColor Green
Write-Host "Студия: $Studio"
if ($Push) { Write-Host "Push безопасных артефактов: включён" } else { Write-Host "Push: выключен (только локальные отчёты)" }
Write-Host ""
Write-Host "Проверить сейчас, не дожидаясь расписания:" -ForegroundColor Cyan
Write-Host "  Start-ScheduledTask -TaskName $TaskName"
Write-Host "  Get-ScheduledTaskInfo -TaskName $TaskName"
Write-Host ""
Write-Host "Автопилот не публикует и не снимает HOLD." -ForegroundColor Yellow
