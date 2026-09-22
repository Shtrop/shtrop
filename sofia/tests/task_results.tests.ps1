<#
    Контракт lib_task_results.ps1.

    «Ненулевой код» — не синоним отказа. Планировщик возвращает и свои коды
    состояния: выполняется, ни разу не запускалась, в очереди. Если считать их
    провалами, на машине с сотнями задач получаются десятки несуществующих
    отказов, и настоящие в них тонут.
#>

. (Join-Path (Split-Path $PSScriptRoot -Parent) 'lib_task_results.ps1')

Test 'каждый код из таблицы находится по ключу' {
    # Числовые литералы дают Int32 для малых кодов и Int64 для 0x8xxxxxxx,
    # поэтому поиск по числовому ключу не совпадал ни по одному типу и вся
    # таблица была недостижима. Ключи строковые — проверяем, что это держится.
    foreach ($hex in $script:TaskResultTable.Keys) {
        $code = [Convert]::ToUInt32($hex.Substring(2), 16)
        $info = Get-TaskResultInfo -Code $code
        Assert-True ([bool]$info.Known) ("код {0} не найден в собственной таблице" -f $hex)
        Assert-Equal $hex $info.Hex ("hex для {0}" -f $hex)
    }
}

Test 'состояния планировщика не считаются отказом' {
    foreach ($c in @(0x41300, 0x41301, 0x41302, 0x41303, 0x41304, 0x41325)) {
        $i = Get-TaskResultInfo -Code $c
        Assert-Equal 'info' $i.Class ("код 0x{0:X} — состояние, а не отказ" -f $c)
    }
}

Test 'настоящие отказы помечаются как fail' {
    foreach ($c in @(0x1, 0x2, 0x41306, 0x41307, 0x8004131F, 0x80070002, 0x80070005)) {
        $i = Get-TaskResultInfo -Code $c
        Assert-Equal 'fail' $i.Class ("код 0x{0:X} — отказ" -f $c)
    }
}

Test 'ноль — это успех' {
    Assert-Equal 'ok' (Get-TaskResultInfo -Code 0).Class 'нулевой код'
}

Test 'отрицательный Int32 из LastTaskResult приводится к беззнаковому виду' {
    # Get-ScheduledTaskInfo отдаёт Int32, поэтому 0x80070005 приходит как -2147024891.
    $i = Get-TaskResultInfo -Code ([int]-2147024891)
    Assert-Equal '0x80070005' $i.Hex 'код должен нормализоваться'
    Assert-Equal 'fail' $i.Class 'и остаться отказом'
}

Test 'неизвестные коды классифицируются по диапазону, а не наугад' {
    Assert-Equal 'info' (Get-TaskResultInfo -Code 0x41399).Class 'SCHED_S_* — коды успеха по соглашению HRESULT'
    Assert-Equal 'fail' (Get-TaskResultInfo -Code 0x80998877).Class 'старший бит — ошибка HRESULT'
    Assert-Equal 'fail' (Get-TaskResultInfo -Code 0x99).Class 'обычный код выхода процесса'
}

Test 'сводка отделяет отказы от состояний и группирует по коду' {
    $tasks = @(
        [pscustomobject]@{ name = 'sofia_photo';   last_code = 0 },
        [pscustomobject]@{ name = 'sofia_reel';    last_code = 0x41301 },
        [pscustomobject]@{ name = 'sofia_trends';  last_code = 0x41303 },
        [pscustomobject]@{ name = 'sofia_pub_a';   last_code = 1 },
        [pscustomobject]@{ name = 'sofia_pub_b';   last_code = 1 },
        [pscustomobject]@{ name = 'sofia_pub_c';   last_code = 1 },
        [pscustomobject]@{ name = 'sofia_watch';   last_code = ([int]-2147024891) }
    )
    $s = Get-TaskFailureSummary -Tasks $tasks

    Assert-Equal 7 $s.Total 'все задачи учтены'
    Assert-Equal 1 $s.OkCount 'успешных'
    Assert-Equal 2 $s.InfoCount 'выполняется и ни разу не запускалась — не отказы'
    Assert-Equal 4 $s.FailedCount 'настоящих отказов'

    Assert-Equal '0x00000001' $s.Groups[0].Hex 'самая частая причина идёт первой'
    Assert-Equal 3 $s.Groups[0].Count 'три задачи с этим кодом'
    Assert-True ($s.Groups[0].Examples -contains 'sofia_pub_a') 'примеры должны называть задачи'
    Assert-Equal 2 $s.Groups.Count 'две различные причины отказа'
}

Test 'задачи без результата пропускаются, а не считаются отказом' {
    $s = Get-TaskFailureSummary -Tasks @(
        [pscustomobject]@{ name = 'sofia_new'; last_code = $null },
        [pscustomobject]@{ name = 'sofia_ok';  last_code = 0 }
    )
    Assert-Equal 1 $s.Total 'задача без результата не учитывается'
    Assert-Equal 0 $s.FailedCount 'и точно не как отказ'
}

Test 'пустой список не ломает сводку' {
    $s = Get-TaskFailureSummary -Tasks @()
    Assert-Equal 0 $s.Total 'ноль задач'
    Assert-Equal 0 $s.FailedCount 'ноль отказов'
}
