<#
    Контракт lib_bugcheck.ps1.

    Класс кода остановки — это развилка всего runbook: он отправляет владельца
    либо переустанавливать драйвер NVIDIA, либо гонять MemTest86, либо менять
    блок питания. Ошибка в классе стоит суток не в ту сторону.
#>

. (Join-Path (Split-Path $PSScriptRoot -Parent) 'lib_bugcheck.ps1')

Test 'известный код отдаёт имя, класс и подсказку' {
    $i = Get-BugCheckInfo -Code 0x154
    Assert-True ([bool]$i.Known) 'код должен быть в справочнике'
    Assert-Equal 'UNEXPECTED_STORE_EXCEPTION' $i.Name 'имя кода'
    Assert-Equal 'memory' $i.Class 'класс причины'
    Assert-Match 'сжат' $i.Hint 'подсказка должна объяснять природу кода'
}

Test 'hex печатается в каноническом виде 0xXXXXXXXX' {
    Assert-Equal '0x00000154' (Get-BugCheckInfo -Code 0x154).Hex 'короткий код дополняется нулями'
    Assert-Equal '0x0000000A' (Get-BugCheckInfo -Code 0xA).Hex 'однозначный код тоже'
}

Test 'неизвестный код не выдаёт себя за известный' {
    $i = Get-BugCheckInfo -Code 0xDEAD
    Assert-True (-not $i.Known) 'Known обязан быть false'
    Assert-Equal 'UNKNOWN_BUGCHECK' $i.Name 'имя не выдумывается'
    Assert-Match '!analyze' $i.Hint 'подсказка должна отправлять к отладчику'
}

Test 'видеокоды отнесены к gpu, а не к драйверу вообще' {
    foreach ($c in @(0x116, 0x117, 0x119, 0x113, 0x141, 0xEA)) {
        $i = Get-BugCheckInfo -Code $c
        Assert-Equal 'gpu' $i.Class ("код {0}" -f $i.Hex)
    }
}

Test 'WHEA и часы CPU — это железо, а не драйвер' {
    foreach ($c in @(0x124, 0x101, 0x9F, 0x14C)) {
        Assert-Equal 'hardware' (Get-BugCheckInfo -Code $c).Class ("код 0x{0:X}" -f $c)
    }
}

Test 'коды памяти отнесены к memory' {
    foreach ($c in @(0x154, 0x1A, 0x50, 0x12B, 0x109, 0x19, 0x4E, 0x13A)) {
        Assert-Equal 'memory' (Get-BugCheckInfo -Code $c).Class ("код 0x{0:X}" -f $c)
    }
}

Test 'каждый класс даёт непустой и осмысленный совет' {
    $expected = @{
        gpu      = 'DDU|драйвер NVIDIA'
        hardware = 'PSU|питани'
        memory   = 'MemTest86'
        storage  = 'NVMe|SMART'
        driver   = '!analyze'
    }
    foreach ($class in $expected.Keys) {
        $advice = Get-BugCheckClassAdvice -Class $class
        Assert-True ([bool]$advice) ("совет для класса {0} пуст" -f $class)
        Assert-Match $expected[$class] $advice ("совет для класса {0} не ведёт куда надо" -f $class)
    }
}

Test 'все классы справочника имеют совет' {
    # Класс без совета молча упал бы в ветку default и отправил владельца
    # разбираться с драйвером вместо настоящей причины.
    $classes = @($script:BugCheckTable.Values | ForEach-Object { $_.class } | Sort-Object -Unique)
    Assert-True ($classes.Count -ge 4) 'классов должно быть несколько'
    $driverAdvice = Get-BugCheckClassAdvice -Class 'driver'
    foreach ($c in $classes) {
        if ($c -eq 'driver') { continue }
        $a = Get-BugCheckClassAdvice -Class $c
        Assert-True ($a -ne $driverAdvice) ("класс {0} падает в ветку default" -f $c)
    }
}

Test 'у каждой записи справочника есть имя, класс и подсказка' {
    foreach ($k in $script:BugCheckTable.Keys) {
        $e = $script:BugCheckTable[$k]
        Assert-True ([bool]$e.name)  ("0x{0:X} без имени" -f $k)
        Assert-True ([bool]$e.class) ("0x{0:X} без класса" -f $k)
        Assert-True ([bool]$e.hint)  ("0x{0:X} без подсказки" -f $k)
    }
}

Test 'таблица кодов в runbook не разошлась со справочником' {
    # Runbook — то, что владелец читает глазами. Если он обещает класс,
    # которого код не имеет, решение будет принято по документу, а не по коду.
    $runbook = Join-Path (Split-Path $PSScriptRoot -Parent) 'RUNBOOK_host_safe_hold.md'
    $known = @('gpu', 'hardware', 'memory', 'storage')
    $checked = 0

    foreach ($line in (Get-Content $runbook)) {
        if ($line -notmatch '^\|\s*`(\w+)`\s*\|(.+?)\|') { continue }
        $class = $Matches[1]
        if ($known -notcontains $class) { continue }
        foreach ($m in [regex]::Matches($Matches[2], '0x([0-9A-Fa-f]+)')) {
            $code = [Convert]::ToUInt32($m.Groups[1].Value, 16)
            $info = Get-BugCheckInfo -Code $code
            Assert-True ([bool]$info.Known) ("runbook называет 0x{0:X}, справочник его не знает" -f $code)
            Assert-Equal $class $info.Class ("0x{0:X}: runbook и справочник расходятся в классе" -f $code)
            $checked++
        }
    }
    Assert-True ($checked -ge 15) ("сверено слишком мало кодов: {0} — разбор таблицы сломался" -f $checked)
}
