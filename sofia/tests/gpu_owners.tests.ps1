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
    $r = Get-GpuOwnerReport -Apps $apps -MemoryUsedMiB 5600
    Assert-Equal 0 $r.HeavyCount 'dwm и браузер — не рендер'
    Assert-Equal 'WARN' $r.Status 'но занятая VRAM без рендера всё равно повод посмотреть'
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
