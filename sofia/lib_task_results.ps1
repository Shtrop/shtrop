<#
.SYNOPSIS
    Разбор кодов завершения задач Task Scheduler.

.DESCRIPTION
    Подключается точкой: . .\lib_task_results.ps1

    «Ненулевой код» и «задача упала» — разные вещи. Планировщик возвращает
    в LastTaskResult не только код выхода процесса, но и свои коды состояния
    SCHED_S_*: «выполняется сейчас» (0x41301), «ни разу не запускалась»
    (0x41303), «в очереди» (0x41325). Считать их провалами — значит
    получить десятки несуществующих отказов и не увидеть за ними настоящие.

    class:
      ok   - успех;
      info - состояние планировщика, не отказ;
      fail - настоящий отказ, который стоит разбирать.
#>

$script:TaskResultTable = @{
    '0x00000000' = @{ name = 'SUCCESS';                     class = 'ok';   hint = 'успешно' }
    '0x00000001' = @{ name = 'EXIT_CODE_1';                 class = 'fail'; hint = 'задача вернула 1 — ошибка внутри самого скрипта или программы' }
    '0x00000002' = @{ name = 'ERROR_FILE_NOT_FOUND';        class = 'fail'; hint = 'не найден исполняемый файл или скрипт задачи' }
    '0x0000000A' = @{ name = 'ERROR_BAD_ENVIRONMENT';       class = 'fail'; hint = 'неверное окружение запуска' }
    '0x00041300' = @{ name = 'SCHED_S_TASK_READY';          class = 'info'; hint = 'готова к запуску' }
    '0x00041301' = @{ name = 'SCHED_S_TASK_RUNNING';        class = 'info'; hint = 'выполняется прямо сейчас' }
    '0x00041302' = @{ name = 'SCHED_S_TASK_DISABLED';       class = 'info'; hint = 'отключена' }
    '0x00041303' = @{ name = 'SCHED_S_TASK_HAS_NOT_RUN';    class = 'info'; hint = 'ни разу не запускалась' }
    '0x00041304' = @{ name = 'SCHED_S_TASK_NO_MORE_RUNS';   class = 'info'; hint = 'запусков больше не запланировано' }
    '0x00041305' = @{ name = 'SCHED_S_TASK_NOT_SCHEDULED';  class = 'info'; hint = 'расписание не задано' }
    '0x00041306' = @{ name = 'SCHED_S_TASK_TERMINATED';     class = 'fail'; hint = 'завершена принудительно: превышен лимит времени выполнения или остановлена вручную' }
    '0x00041307' = @{ name = 'SCHED_S_TASK_NO_VALID_TRIGGERS'; class = 'fail'; hint = 'нет действительных триггеров — задача не сработает никогда' }
    '0x00041325' = @{ name = 'SCHED_S_TASK_QUEUED';         class = 'info'; hint = 'в очереди: предыдущий экземпляр ещё выполняется' }
    '0x8004131F' = @{ name = 'SCHED_E_ALREADY_RUNNING';     class = 'fail'; hint = 'экземпляр уже выполняется — новый запуск отменён; задача не успевает отработать до следующего триггера' }
    '0x80041309' = @{ name = 'SCHED_E_TRIGGER_NOT_FOUND';   class = 'fail'; hint = 'триггер не найден' }
    '0x80070002' = @{ name = 'ERROR_FILE_NOT_FOUND';        class = 'fail'; hint = 'файл задачи не найден по указанному пути' }
    '0x80070005' = @{ name = 'ERROR_ACCESS_DENIED';         class = 'fail'; hint = 'доступ запрещён — не хватает прав учётной записи задачи' }
    '0x8007010B' = @{ name = 'ERROR_DIRECTORY';             class = 'fail'; hint = 'неверный рабочий каталог задачи (Start in)' }
    '0x800710E0' = @{ name = 'ERROR_OPERATOR_OR_ADMIN_HAS_REFUSED'; class = 'fail'; hint = 'запуск отклонён: часто «не запускать по требованию» или условия питания' }
    '0xC000013A' = @{ name = 'STATUS_CONTROL_C_EXIT';       class = 'fail'; hint = 'процесс завершён принудительно' }
    '0xC0000142' = @{ name = 'STATUS_DLL_INIT_FAILED';      class = 'fail'; hint = 'приложение не смогло инициализироваться' }
}

function ConvertTo-TaskResultCode {
    <#
        LastTaskResult приходит как Int32, поэтому коды вида 0x8xxxxxxx
        оказываются отрицательными. Приводим к беззнаковому виду.
    #>
    param($Value)
    if ($null -eq $Value) { return $null }
    $i = [int64]$Value
    if ($i -lt 0) { $i = $i + 4294967296 }
    [uint32]$i
}

function Get-TaskResultInfo {
    <#
        Принимает код как есть, в том числе отрицательный Int32 из
        LastTaskResult: приведение к беззнаковому виду делается внутри.
    #>
    param([Parameter(Mandatory)] $Code)

    $c = ConvertTo-TaskResultCode -Value $Code
    if ($null -eq $c) { return $null }
    $hex = '0x{0:X8}' -f $c

    # Ключи таблицы — строки: числовые литералы дали бы Int32 для малых кодов
    # и Int64 для 0x8xxxxxxx, и поиск не совпал бы ни по одному типу.
    if ($script:TaskResultTable.ContainsKey($hex)) {
        $e = $script:TaskResultTable[$hex]
        return [pscustomobject]@{
            Code = $c; Hex = $hex
            Name = $e.name; Class = $e.class; Hint = $e.hint; Known = $true
        }
    }
    $Code = $c

    # SCHED_S_* лежат в диапазоне 0x00041300..0x000413FF и по соглашению
    # HRESULT являются кодами УСПЕХА: старший бит сброшен.
    if ($Code -ge 0x00041300 -and $Code -le 0x000413FF) {
        return [pscustomobject]@{
            Code = $Code; Hex = ('0x{0:X8}' -f $Code)
            Name = 'SCHED_S_UNKNOWN'; Class = 'info'
            Hint = 'состояние планировщика, не отказ'; Known = $false
        }
    }

    if (($Code -band 0x80000000) -ne 0) {
        return [pscustomobject]@{
            Code = $Code; Hex = ('0x{0:X8}' -f $Code)
            Name = 'HRESULT_ERROR'; Class = 'fail'
            Hint = 'ошибка HRESULT — искать код в документации Task Scheduler'; Known = $false
        }
    }

    [pscustomobject]@{
        Code = $Code; Hex = ('0x{0:X8}' -f $Code)
        Name = 'EXIT_CODE'; Class = 'fail'
        Hint = ('задача завершилась с кодом выхода {0}' -f $Code); Known = $false
    }
}

function Get-TaskFailureSummary {
    <#
        Группирует задачи по коду результата и отделяет настоящие отказы от
        состояний планировщика.

        Tasks — записи с полями name и last_code (как их пишет diagnose).
    #>
    param([object[]] $Tasks = @())

    $rows = @()
    foreach ($t in @($Tasks | Where-Object { $_ })) {
        $code = ConvertTo-TaskResultCode -Value $t.last_code
        if ($null -eq $code) { continue }
        $info = Get-TaskResultInfo -Code $code
        $rows += [pscustomobject]@{
            Name = $t.name; LastRun = $t.last_run
            Code = $code; Hex = $info.Hex; ResultName = $info.Name
            Class = $info.Class; Hint = $info.Hint
        }
    }

    $failed = @($rows | Where-Object Class -eq 'fail')
    $groups = @($failed | Group-Object Hex | Sort-Object Count -Descending | ForEach-Object {
        $first = $_.Group[0]
        [pscustomobject]@{
            Hex = $_.Name; Count = $_.Count
            ResultName = $first.ResultName; Hint = $first.Hint
            Examples = @($_.Group | Select-Object -First 3 | ForEach-Object { $_.Name })
        }
    })

    [pscustomobject]@{
        Total       = $rows.Count
        OkCount     = @($rows | Where-Object Class -eq 'ok').Count
        InfoCount   = @($rows | Where-Object Class -eq 'info').Count
        FailedCount = $failed.Count
        Failed      = $failed
        Groups      = $groups
    }
}
