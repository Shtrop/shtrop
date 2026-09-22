<#
.SYNOPSIS
    Подделка nvidia-smi для тестов: отвечает из файла состояния и меняет его на -pl.

.DESCRIPTION
    Состояние лежит в gpu_state.json рядом со скриптом. Поддержаны те вызовы,
    которые делают инструменты студии:
      --query-gpu=<поля> --format=csv,noheader
      --query-compute-apps=<поля> --format=csv,noheader
      -q -d PERFORMANCE
      -pl <ватты>            (меняет power.limit в состоянии)
      -i <индекс>            (принимается, состояние одно)

    Файл deny.flag рядом со скриптом заставляет -pl отказать: так проверяется
    ветка «нет прав администратора».
#>

$stateFile = Join-Path $PSScriptRoot 'gpu_state.json'
$state = Get-Content $stateFile -Raw | ConvertFrom-Json

function Format-Field {
    param([string] $Name)
    switch -Regex ($Name) {
        '^name$'            { return [string]$state.name }
        '^temperature\.'    { return ('{0}' -f [int]$state.temperature) }
        '^power\.draw$'     { return ('{0:N2} W' -f [double]$state.power_draw) }
        '^power\.limit$'    { return ('{0:N2} W' -f [double]$state.power_limit) }
        '^power\.min_limit$'{ return ('{0:N2} W' -f [double]$state.power_min_limit) }
        '^power\.max_limit$'{ return ('{0:N2} W' -f [double]$state.power_max_limit) }
        '^clocks\.'         { return ('{0} MHz' -f [int]$state.clocks_sm) }
        '^utilization\.'    { return ('{0} %' -f [int]$state.utilization) }
        '^memory\.used$'    { return ('{0} MiB' -f [int]$state.memory_used) }
        '^memory\.total$'   { return ('{0} MiB' -f [int]$state.memory_total) }
        default             { return '[N/A]' }
    }
}

$argline = ($args -join ' ')

# Сценарий дрейфа лимита: каждый опрос забирает следующее значение из очереди.
# Нужен, чтобы воспроизвести откат смягчения посреди окна наблюдения.
if ($argline -match '--query-gpu' -and @($state.power_limit_sequence).Count -gt 0) {
    $seq = @($state.power_limit_sequence)
    $state.power_limit = $seq[0]
    $state.power_limit_sequence = @($seq | Select-Object -Skip 1)
    $state | ConvertTo-Json -Depth 6 | Out-File -FilePath $stateFile -Encoding UTF8
}

# --query-gpu=a,b,c  либо  --query-gpu a,b,c
if ($argline -match '--query-gpu[= ]([^ ]+)') {
    $fields = $Matches[1].Trim('"',"'") -split ','
    ( ($fields | ForEach-Object { Format-Field -Name $_.Trim() }) -join ', ' )
    exit 0
}

if ($argline -match '--query-compute-apps[= ]([^ ]+)') {
    foreach ($p in @($state.compute_apps)) {
        if (-not $p) { continue }
        # Под WDDM настоящий nvidia-smi отдаёт [N/A] вместо объёма.
        $mem = if ("$($p.used_memory)" -match '(?i)^n/?a$') { '[N/A]' } else { ('{0} MiB' -f $p.used_memory) }
        ('{0}, {1}, {2}' -f $p.pid, $p.process_name, $mem)
    }
    exit 0
}

if ($argline -match '-q\b' -and $argline -match 'PERFORMANCE') {
    'Clocks Throttle Reasons'
    foreach ($r in @($state.throttle_active)) { if ($r) { ('        {0}                        : Active' -f $r) } }
    '        Idle                              : Not Active'
    exit 0
}

if ($argline -match '-pl\s+([0-9]+)') {
    $target = [int]$Matches[1]
    if (Test-Path (Join-Path $PSScriptRoot 'deny.flag')) {
        'Insufficient Permissions' | Write-Output
        exit 1
    }
    if ($target -lt [double]$state.power_min_limit -or $target -gt [double]$state.power_max_limit) {
        ('Provided power limit {0}.00 W is not a valid power limit' -f $target)
        exit 1
    }
    $state.power_limit = $target
    $state | ConvertTo-Json -Depth 6 | Out-File -FilePath $stateFile -Encoding UTF8
    ('Power limit for GPU 00000000:01:00.0 was set to {0}.00 W from {1}.00 W.' -f $target, $target)
    'All done.'
    exit 0
}

('fake nvidia-smi: неизвестный вызов: {0}' -f $argline)
exit 1
