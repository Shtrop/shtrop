<#
.SYNOPSIS
    Подделка schtasks для тестов: хранит задачи в tasks.json рядом со скриптом.

.DESCRIPTION
    Поддержаны вызовы, которые делает apply_safehold_fix.ps1:
      /Create /TN <имя> /TR <команда> /SC ONSTART /RU SYSTEM /RL HIGHEST /F
      /Query  /TN <имя>
      /Delete /TN <имя> /F

    Файл deny.flag рядом со скриптом заставляет /Create и /Delete отказать:
    так проверяется ветка «нет прав администратора».
#>

$tasksFile = Join-Path $PSScriptRoot 'tasks.json'
$tasks = if (Test-Path $tasksFile) { @(Get-Content $tasksFile -Raw | ConvertFrom-Json) } else { @() }
$tasks = @($tasks | Where-Object { $_ })

function Save-Tasks { param($T) ,@($T) | ConvertTo-Json -Depth 5 | Out-File -FilePath $tasksFile -Encoding UTF8 }

$name = ''
$run  = ''
for ($i = 0; $i -lt $args.Count; $i++) {
    if ("$($args[$i])" -ieq '/TN' -and $i + 1 -lt $args.Count) { $name = "$($args[$i + 1])" }
    if ("$($args[$i])" -ieq '/TR' -and $i + 1 -lt $args.Count) { $run  = "$($args[$i + 1])" }
}
$verb = if ($args.Count -gt 0) { "$($args[0])" } else { '' }
$denied = Test-Path (Join-Path $PSScriptRoot 'deny.flag')

switch -Regex ($verb) {
    '(?i)^/Create$' {
        if ($denied) { 'ERROR: Access is denied.'; exit 1 }
        $tasks = @($tasks | Where-Object { $_.name -ne $name })
        $tasks += [pscustomobject]@{ name = $name; run = $run }
        Save-Tasks $tasks
        ('SUCCESS: The scheduled task "{0}" has successfully been created.' -f $name)
        exit 0
    }
    '(?i)^/Query$' {
        $t = @($tasks | Where-Object { $_.name -eq $name })
        if ($t.Count -eq 0) {
            ('ERROR: The system cannot find the file specified.')
            exit 1
        }
        'TaskName                                 Next Run Time          Status'
        ('{0}    N/A                    Ready' -f $t[0].name)
        exit 0
    }
    '(?i)^/Delete$' {
        if ($denied) { 'ERROR: Access is denied.'; exit 1 }
        $before = $tasks.Count
        $tasks = @($tasks | Where-Object { $_.name -ne $name })
        Save-Tasks $tasks
        if ($tasks.Count -eq $before) { ('ERROR: The system cannot find the file specified.'); exit 1 }
        ('SUCCESS: The scheduled task "{0}" was successfully deleted.' -f $name)
        exit 0
    }
    default { ('fake schtasks: неизвестный вызов: {0}' -f ($args -join ' ')); exit 1 }
}
