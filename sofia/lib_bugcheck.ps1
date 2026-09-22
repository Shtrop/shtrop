<#
    Справочник bug check кодов Windows с классификацией причины.
    Подключается точкой из analyze_minidump.ps1 и analyze_safehold_report.ps1.

    class:
      gpu       - видеоподсистема/драйвер GPU
      hardware  - железо: питание, CPU, RAM, разгон
      memory    - оперативная память или её повреждение
      storage   - диск/контроллер/таймауты DPC
      driver    - драйвер режима ядра (какой именно — скажет дамп)
#>

$script:BugCheckTable = @{
    0x0000000A = @{ name = 'IRQL_NOT_LESS_OR_EQUAL';            class = 'driver';   hint = 'драйвер обратился к памяти на неверном IRQL' }
    0x0000001A = @{ name = 'MEMORY_MANAGEMENT';                  class = 'memory';   hint = 'ошибка менеджера памяти: частая причина — сбойная планка или XMP' }
    0x0000001E = @{ name = 'KMODE_EXCEPTION_NOT_HANDLED';        class = 'driver';   hint = 'необработанное исключение в ядре' }
    0x0000003B = @{ name = 'SYSTEM_SERVICE_EXCEPTION';           class = 'driver';   hint = 'исключение при системном вызове' }
    0x00000050 = @{ name = 'PAGE_FAULT_IN_NONPAGED_AREA';        class = 'memory';   hint = 'обращение к несуществующей памяти: драйвер или RAM' }
    0x0000007E = @{ name = 'SYSTEM_THREAD_EXCEPTION_NOT_HANDLED';class = 'driver';   hint = 'исключение в системном потоке' }
    0x0000009F = @{ name = 'DRIVER_POWER_STATE_FAILURE';         class = 'hardware'; hint = 'драйвер завис при смене состояния питания' }
    0x000000C4 = @{ name = 'DRIVER_VERIFIER_DETECTED_VIOLATION'; class = 'driver';   hint = 'нарушение, пойманное Driver Verifier' }
    0x000000D1 = @{ name = 'DRIVER_IRQL_NOT_LESS_OR_EQUAL';      class = 'driver';   hint = 'драйвер обратился к выгруженной памяти' }
    0x000000EA = @{ name = 'THREAD_STUCK_IN_DEVICE_DRIVER';      class = 'gpu';      hint = 'поток завис в драйвере устройства — классика зависшего GPU' }
    0x000000F4 = @{ name = 'CRITICAL_OBJECT_TERMINATION';        class = 'storage';  hint = 'критический процесс завершился: часто диск или повреждение системы' }
    0x00000101 = @{ name = 'CLOCK_WATCHDOG_TIMEOUT';             class = 'hardware'; hint = 'ядро CPU не ответило: разгон, питание VRM, нестабильность' }
    0x00000109 = @{ name = 'CRITICAL_STRUCTURE_CORRUPTION';      class = 'memory';   hint = 'повреждение структур ядра: RAM, разгон или драйвер' }
    0x00000113 = @{ name = 'VIDEO_DXGKRNL_FATAL_ERROR';          class = 'gpu';      hint = 'фатальная ошибка графического ядра DirectX' }
    0x00000116 = @{ name = 'VIDEO_TDR_FAILURE';                  class = 'gpu';      hint = 'GPU не восстановился после таймаута: драйвер, перегрев или просадка питания' }
    0x00000117 = @{ name = 'VIDEO_TDR_TIMEOUT_DETECTED';         class = 'gpu';      hint = 'GPU не ответил вовремя' }
    0x00000119 = @{ name = 'VIDEO_SCHEDULER_INTERNAL_ERROR';     class = 'gpu';      hint = 'внутренняя ошибка планировщика видео' }
    0x00000124 = @{ name = 'WHEA_UNCORRECTABLE_ERROR';           class = 'hardware'; hint = 'аппаратная ошибка от WHEA: питание, CPU, RAM, разгон — не драйвер' }
    0x0000012B = @{ name = 'FAULTY_HARDWARE_CORRUPTED_PAGE';     class = 'memory';   hint = 'однобитовая ошибка памяти — почти всегда RAM' }
    0x00000133 = @{ name = 'DPC_WATCHDOG_VIOLATION';             class = 'storage';  hint = 'DPC выполнялся слишком долго: драйвер диска/NVMe или прошивка' }
    0x00000139 = @{ name = 'KERNEL_SECURITY_CHECK_FAILURE';      class = 'driver';   hint = 'повреждение структуры данных ядра' }
    0x00000141 = @{ name = 'VIDEO_ENGINE_TIMEOUT_DETECTED';      class = 'gpu';      hint = 'движок GPU не ответил вовремя' }
    0x0000014C = @{ name = 'FATAL_ABNORMAL_RESET_ERROR';         class = 'hardware'; hint = 'аварийный сброс платформы' }
    0x000001CA = @{ name = 'SYNTHETIC_WATCHDOG_TIMEOUT';         class = 'hardware'; hint = 'сторожевой таймер платформы' }
}

function Get-BugCheckInfo {
    param([Parameter(Mandatory)][uint32] $Code)

    if ($script:BugCheckTable.ContainsKey([int]$Code)) {
        $e = $script:BugCheckTable[[int]$Code]
        return [pscustomobject]@{
            Code    = $Code
            Hex     = ('0x{0:X8}' -f $Code)
            Name    = $e.name
            Class   = $e.class
            Hint    = $e.hint
            Known   = $true
        }
    }
    [pscustomobject]@{
        Code  = $Code
        Hex   = ('0x{0:X8}' -f $Code)
        Name  = 'UNKNOWN_BUGCHECK'
        Class = 'driver'
        Hint  = 'код не в справочнике — смотреть !analyze -v'
        Known = $false
    }
}

function Get-BugCheckClassAdvice {
    param([Parameter(Mandatory)][string] $Class)
    switch ($Class) {
        'gpu'      { 'Причина в видеоподсистеме: обновить/переустановить драйвер NVIDIA начисто (DDU), снять разгон, ограничить power limit, проверить температуру.' }
        'hardware' { 'Причина аппаратная: питание/PSU, разгон, VRM, CPU. Сбросить любой OC в стоковые значения, поставить ИБП, проверить запас мощности блока питания.' }
        'memory'   { 'Причина в памяти: отключить XMP/EXPO, прогнать MemTest86 минимум 4 прохода, проверить посадку планок.' }
        'storage'  { 'Причина в подсистеме хранения: обновить прошивку NVMe и драйвер контроллера, проверить SMART системного диска.' }
        default    { 'Драйвер режима ядра: точное имя даст !analyze -v; обновить или откатить именно его.' }
    }
}
