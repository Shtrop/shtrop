<#
    Контракт lib_gpu_owners.ps1: правило ONE HEAVY GPU OWNER и осиротевшая VRAM.
#>

. (Join-Path (Split-Path $PSScriptRoot -Parent) 'lib_gpu_owners.ps1')

Test 'пустой вывод и "No running processes found" дают ноль владельцев' {
    Assert-Equal 0 @(ConvertFrom-NvidiaComputeApps -Text '').Count 'пустая строка'
    Assert-Equal 0 @(ConvertFrom-NvidiaComputeApps -Text 'No running processes found').Count 'служебная строка'
}

Test 'разбор строки compute-apps достаёт pid, имя и память' {
    $a = @(ConvertFrom-NvidiaComputeApps -Text '12345, C:\Tools\ComfyUI\python.exe, 8192 MiB')
    Assert-Equal 1 $a.Count 'одна запись'
    Assert-Equal 12345 $a[0].Pid 'pid'
    Assert-Equal 'python.exe' $a[0].Name 'имя процесса'
    Assert-Equal 8192 $a[0].UsedMiB 'занятая память'
}

Test 'запятая в пути не ломает разбор' {
    $a = @(ConvertFrom-NvidiaComputeApps -Text '77, D:\AI, models\comfy\python.exe, 4096 MiB')
    Assert-Equal 1 $a.Count 'одна запись'
    Assert-Equal 'python.exe' $a[0].Name 'имя берётся с конца пути'
    Assert-Equal 4096 $a[0].UsedMiB 'память берётся из последнего поля'
}

Test 'один тяжёлый владелец без hold — это норма' {
    $apps = ConvertFrom-NvidiaComputeApps -Text '100, C:\ComfyUI\python.exe, 9000 MiB'
    $r = Get-GpuOwnerReport -Apps $apps -MemoryUsedMiB 9200
    Assert-Equal 'PASS' $r.Status 'один владелец допустим'
    Assert-Equal 1 $r.HeavyCount 'ровно один тяжёлый'
}

Test 'тот же владелец при активном hold даёт WARN' {
    $apps = ConvertFrom-NvidiaComputeApps -Text '100, C:\ComfyUI\python.exe, 9000 MiB'
    $r = Get-GpuOwnerReport -Apps $apps -MemoryUsedMiB 9200 -HoldActive $true
    Assert-Equal 'WARN' $r.Status 'при hold рендеров быть не должно'
    Assert-Match 'hold' $r.Evidence 'причина должна быть названа'
}

Test 'два конкурирующих ComfyUI дают FAIL по ONE HEAVY GPU OWNER' {
    $apps = ConvertFrom-NvidiaComputeApps -Text @"
100, C:\ComfyUI\python.exe, 9000 MiB
201, C:\ComfyUI_old\python.exe, 7000 MiB
"@
    $r = Get-GpuOwnerReport -Apps $apps -MemoryUsedMiB 16500
    Assert-Equal 'FAIL' $r.Status 'два тяжёлых владельца недопустимы'
    Assert-Equal 2 $r.HeavyCount 'оба должны быть посчитаны'
    Assert-Equal 16000 $r.HeavyUsedMiB 'суммарная занятая память'
    Assert-Match 'ONE HEAVY GPU OWNER' $r.Evidence 'правило должно быть названо'
    Assert-Match 'несколько копий' $r.Evidence 'одинаковые имена — признак осиротевшей копии'
}

Test 'процессы рабочего стола не считаются владельцами рендера' {
    $apps = ConvertFrom-NvidiaComputeApps -Text @"
10, C:\Windows\System32\dwm.exe, 3000 MiB
11, C:\Program Files\Google\Chrome\chrome.exe, 2500 MiB
"@
    # Память занята, но она вся объяснена живыми процессами — это не дефект.
    # Подпись неотработавшей очистки — именно НЕ отнесённая память.
    $r = Get-GpuOwnerReport -Apps $apps -MemoryUsedMiB 5600
    Assert-Equal 0 $r.HeavyCount 'dwm и браузер — не рендер'
    Assert-Equal 'PASS' $r.Status 'вся занятая память объяснена процессами'
    Assert-Equal 'measured' $r.Attribution 'память известна по всем процессам'
    Assert-Equal 100 $r.UnattributedMiB 'остаток мал'
}

Test 'те же процессы, но с большим неучтённым остатком — WARN' {
    $apps = ConvertFrom-NvidiaComputeApps -Text @"
10, C:\Windows\System32\dwm.exe, 3000 MiB
11, C:\Program Files\Google\Chrome\chrome.exe, 2500 MiB
"@
    $r = Get-GpuOwnerReport -Apps $apps -MemoryUsedMiB 12000
    Assert-Equal 'WARN' $r.Status 'не отнесено 6500 MiB — так выглядит несработавшая очистка'
    Assert-Equal 6500 $r.UnattributedMiB 'размер разрыва'
    Assert-Match 'не отнесено' $r.Evidence 'разрыв должен быть назван'
}

Test 'безымянный процесс становится тяжёлым по объёму VRAM' {
    $apps = ConvertFrom-NvidiaComputeApps -Text '55, D:\some\unknown_worker.exe, 12000 MiB'
    $r = Get-GpuOwnerReport -Apps $apps -MemoryUsedMiB 12200
    Assert-Equal 1 $r.HeavyCount '12 ГиБ VRAM — это рендер, как бы он ни назывался'
}

Test 'занятая VRAM без единой задачи — след неотработавшей очистки' {
    $r = Get-GpuOwnerReport -Apps @() -MemoryUsedMiB 11000
    Assert-Equal 'WARN' $r.Status 'память держится без владельца'
    Assert-Equal 11000 $r.OrphanVramMiB 'вся занятая память не отнесена к процессам'
    Assert-Match 'cleanup|освобожд' $r.NextAction 'следующий шаг должен указывать на очистку'
}

Test 'простаивающая карта — чистый PASS' {
    $r = Get-GpuOwnerReport -Apps @() -MemoryUsedMiB 400
    Assert-Equal 'PASS' $r.Status 'фоновая занятость картой — норма'
    Assert-Equal 0 $r.OrphanVramMiB 'осиротевшей памяти нет'
}

# --------------------------------------------------------------------------
# Случай с машины студии (2026-09-22): под WDDM nvidia-smi не отдаёт
# used_memory ни по одному процессу, а карта занята почти целиком.
# --------------------------------------------------------------------------

$wddmText = @"
14964, C:\Windows\System32\CrossDeviceResume.exe, [N/A]
14464, C:\Windows\explorer.exe, [N/A]
16092, C:\Windows\SystemApps\StartMenuExperienceHost.exe, [N/A]
16060, C:\Windows\SystemApps\SearchHost.exe, [N/A]
18780, C:\Program Files\msedgewebview2.exe, [N/A]
21384, C:\Program Files\NVIDIA Corporation\NVIDIA Overlay.exe, [N/A]
27900, C:\AI\ComfyUI\python.exe, [N/A]
"@

Test '[N/A] не превращается в ноль мегабайт' {
    $apps = @(ConvertFrom-NvidiaComputeApps -Text '14964, C:\Windows\System32\CrossDeviceResume.exe, [N/A]')
    Assert-Equal 1 $apps.Count 'процесс должен разобраться'
    Assert-True (-not $apps[0].MemKnown) 'память обязана считаться неизвестной, а не нулевой'
}

Test 'карта занята, а владельца установить нельзя — это FAIL, а не PASS' {
    $apps = ConvertFrom-NvidiaComputeApps -Text $wddmText
    $r = Get-GpuOwnerReport -Apps $apps -MemoryUsedMiB 30803 -MemoryTotalMiB 32607

    Assert-Equal 'not_measured' $r.Attribution 'ни по одному процессу памяти нет'
    Assert-Equal 30803 $r.UnattributedMiB 'не отнесена вся занятая память'
    Assert-Equal 'FAIL' $r.Status 'занята половина карты и больше, владелец неизвестен — тяжёлый маршрут не пройдёт'
    Assert-Match 'владельца установить нельзя' $r.Evidence 'причина должна быть названа прямо'
    Assert-Match 'WDDM|счётчик' $r.NextAction 'следующий шаг должен вести к счётчикам Windows'
}

Test 'разрыв виден даже тогда, когда тяжёлый владелец найден' {
    # Прежняя версия считала неотнесённую память только при нуле владельцев,
    # поэтому ровно этот случай — питон на карте плюс 27 ГиБ ничьих — проходил
    # молча.
    $apps = ConvertFrom-NvidiaComputeApps -Text @"
27900, C:\AI\ComfyUI\python.exe, 2917 MiB
2056, C:\Windows\System32\dwm.exe, 593 MiB
"@
    $r = Get-GpuOwnerReport -Apps $apps -MemoryUsedMiB 30803 -MemoryTotalMiB 32607

    Assert-Equal 1 $r.HeavyCount 'питон — тяжёлый владелец'
    Assert-Equal 3510 $r.AttributedMiB 'отнесено только то, что отдали'
    Assert-Equal 27293 $r.UnattributedMiB 'остальное ничьё'
    Assert-Equal 'FAIL' $r.Status 'разрыв больше половины карты'
    Assert-Match 'один тяжёлый владелец' $r.Evidence 'вывод по владельцам должен остаться'
    Assert-Match 'не отнесено' $r.Evidence 'и разрыв тоже'
}

Test 'счётчики Windows подставляются там, где nvidia-smi промолчал' {
    $apps = ConvertFrom-NvidiaComputeApps -Text $wddmText
    $counters = @{ 27900 = 27000; 14464 = 593 }
    $r = Get-GpuOwnerReport -Apps $apps -MemoryUsedMiB 30803 -MemoryTotalMiB 32607 -CounterMemory $counters

    Assert-Equal 'partial' $r.Attribution 'память нашлась не по всем процессам'
    Assert-Equal 27593 $r.AttributedMiB 'сумма из счётчиков'
    Assert-Equal 3210 $r.UnattributedMiB 'остаток стал объяснимым'
    Assert-Equal 'WARN' $r.Status 'разрыв меньше половины карты — уже не отказ'

    $python = @($r.Apps | Where-Object { $_.Pid -eq 27900 })
    Assert-Equal 'perf-counter' $python[0].MemSource 'источник памяти должен быть виден'
    Assert-Equal 27000 $python[0].UsedMiB 'значение из счётчика'
}

Test 'счётчик делает тяжёлым владельцем процесс с непонятным именем' {
    $apps = ConvertFrom-NvidiaComputeApps -Text '5555, D:\tools\unknown_worker.exe, [N/A]'
    $r = Get-GpuOwnerReport -Apps $apps -MemoryUsedMiB 9000 -CounterMemory @{ 5555 = 8800 }
    Assert-Equal 1 $r.HeavyCount '8,8 ГиБ — это рендер, как бы он ни назывался'
}
