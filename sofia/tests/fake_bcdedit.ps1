<#
.SYNOPSIS
    Подделка bcdedit для тестов: хранит badmemorylist в badmemory.json.

.DESCRIPTION
    Поддержаны вызовы apply_safehold_fix.ps1:
      /enum {badmemory}
      /set {badmemory} badmemorylist <pfn> [<pfn> ...]
      /deletevalue {badmemory} badmemorylist

    Вывод /enum повторяет формат настоящего bcdedit, включая перенос длинного
    списка на строки продолжения с отступом: именно на нём ломается наивный
    разбор.
#>

$stateFile = Join-Path $PSScriptRoot 'badmemory.json'
$state = if (Test-Path $stateFile) { Get-Content $stateFile -Raw | ConvertFrom-Json } else { [pscustomobject]@{ list = @() } }
$list = @($state.list | Where-Object { $_ })
$script:list = $list

$access = if ($state.PSObject.Properties.Name -contains 'access') { "$($state.access)" } else { '' }
$script:access = $access

function Save-State {
    param($L, [string] $A)
    @{ list = @($L); access = $A } | ConvertTo-Json | Out-File -FilePath $stateFile -Encoding UTF8
}
function Save-List   { param($L) Save-State -L $L -A $script:access }
function Save-Access { param([string] $A) Save-State -L $script:list -A $A }

$verb = if ($args.Count -gt 0) { "$($args[0])" } else { '' }

switch -Regex ($verb) {
    '(?i)^/enum$' {
        'Плохая память'
        '---------------'
        if ($list.Count -eq 0) {
            'identifier              {badmemory}'
            exit 0
        }
        # Настоящий bcdedit переносит длинный список, выравнивая по колонке значения.
        $perLine = 4
        for ($i = 0; $i -lt $list.Count; $i += $perLine) {
            $chunk = $list[$i..([math]::Min($i + $perLine - 1, $list.Count - 1))]
            if ($i -eq 0) { ('badmemorylist           {0}' -f ($chunk -join ' ')) }
            else          { ('                        {0}' -f ($chunk -join ' ')) }
        }
        exit 0
    }
    '(?i)^/set$' {
        # /set {badmemory} <имя параметра> <значения...>
        # Настоящий bcdedit различает badmemorylist и badmemoryaccess;
        # заглушка обязана различать тоже, иначе второй вызов затрёт список.
        if ($args.Count -lt 4) { 'Ошибка: недостаточно параметров.'; exit 1 }
        $setting = "$($args[2])"
        $values = @($args[3..($args.Count - 1)] | ForEach-Object { "$_" })
        switch -Regex ($setting) {
            '(?i)^badmemorylist$'   { Save-List $values }
            '(?i)^badmemoryaccess$' { Save-Access $values[0] }
            default { ('fake bcdedit: неизвестный параметр: {0}' -f $setting); exit 1 }
        }
        'Операция успешно завершена.'
        exit 0
    }
    '(?i)^/deletevalue$' {
        Save-State -L @() -A $access
        'Операция успешно завершена.'
        exit 0
    }
    default { ('fake bcdedit: неизвестный вызов: {0}' -f ($args -join ' ')); exit 1 }
}
