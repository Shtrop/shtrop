<#
    Контракт check_memory_storage.ps1.

    Это ветка расследования под коды класса memory (0x154 и соседние) —
    та самая, на которой стоит текущий инцидент. Главное, что здесь
    проверяется: нечитаемый журнал не должен выглядеть как отсутствие ошибок.
#>

$tool = Join-Path (Split-Path $PSScriptRoot -Parent) 'check_memory_storage.ps1'

function Invoke-MemCheck {
    param([int] $Days = 7)
    & $tool -Days $Days *>&1 | Out-String
}

function New-WheaEvent {
    param([int] $Id = 47, [string] $Address = '', [int] $HoursAgo = 3)
    New-TestEvent -Id $Id -Provider 'Microsoft-Windows-WHEA-Logger' `
                  -Time (Get-Date).AddHours(-$HoursAgo) -PhysicalAddress $Address `
                  -Message 'A corrected hardware error has occurred.'
}

# --------------------------------------------------------------------------

Test 'ошибка WHEA даёт FAIL с числом и идентификаторами событий' {
    Set-WinEventStub -Mode ok -Events @(
        (New-WheaEvent -Id 47 -Address '0x3f8a21000' -HoursAgo 3),
        (New-WheaEvent -Id 47 -Address '0x3f8a21000' -HoursAgo 2),
        (New-WheaEvent -Id 19 -HoursAgo 1)
    )
    $out = Invoke-MemCheck
    Assert-Match 'FAIL\s*\]\s*WHEA' $out 'WHEA должен быть FAIL'
    Assert-Match '3 аппаратных ошибок' $out 'число ошибок должно быть названо'
    Assert-Match '47x2' $out 'разбивка по идентификаторам должна быть в доказательстве'
}

Test 'физический адрес из события попадает в вывод' {
    Set-WinEventStub -Mode ok -Events @(New-WheaEvent -Id 47 -Address '0x3f8a21000' -HoursAgo 1)
    $out = Invoke-MemCheck
    Assert-Match 'PhysicalAddress=0x3f8a21000' $out 'адрес — это улика, он должен быть показан'
}

Test 'отсутствие ошибок WHEA даёт PASS' {
    Set-WinEventStub -Mode ok -Events @()
    $out = Invoke-MemCheck
    Assert-Match 'PASS\s*\]\s*WHEA' $out 'чистый журнал — PASS по WHEA'
}

Test 'недоступный журнал даёт NOT_MEASURED, а не PASS' {
    # Тот же класс дефекта, что был в окне наблюдения: отказ в доступе нельзя
    # засчитывать как отсутствие аппаратных ошибок.
    Set-WinEventStub -Mode denied
    $out = Invoke-MemCheck
    Assert-Match 'NOT_MEASURED\s*\]\s*WHEA' $out 'нечитаемый журнал — это не измерение'
    Assert-NotMatch 'PASS\s*\]\s*WHEA' $out 'PASS по WHEA при закрытом журнале недопустим'
}

Test 'итоговый вердикт следует из находок' {
    Set-WinEventStub -Mode ok -Events @(New-WheaEvent -Id 47 -Address '0x1b7fac8000' -HoursAgo 5)
    $out = Invoke-MemCheck
    Assert-Match 'ВЕРДИКТ:\s*FAIL' $out 'при FAIL-находке вердикт обязан быть FAIL'
}

Test 'проверка ничего не меняет и советует самое дешёвое действие первым' {
    Set-WinEventStub -Mode ok -Events @()
    $out = Invoke-MemCheck
    Assert-Match 'Отключить XMP/EXPO' $out 'первым шагом должен идти бесплатный обратимый тест'
}

Test 'чистый прогон проверки памяти не объявляется отказом' {
    # Сообщение об УСПЕХЕ само содержит слово об ошибках: «detected no errors»,
    # «не обнаружило ошибок». Прежнее условие ловило это по тексту и отправляло
    # владельца искать несуществующий дефект RAM.
    Set-WinEventStub -Mode ok -Events @(
        (New-TestEvent -Id 1201 -Provider 'Microsoft-Windows-MemoryDiagnostics-Results' `
                       -Time (Get-Date).AddDays(-2) `
                       -Message 'The Windows Memory Diagnostic tested the computer memory and detected no errors.')
    )
    $out = Invoke-MemCheck
    Assert-Match 'PASS\s*\]\s*Проверка памяти Windows' $out 'чистый прогон — это PASS'
    Assert-NotMatch 'FAIL\s*\]\s*Проверка памяти Windows' $out 'и точно не FAIL'
}

Test 'прогон с ошибками объявляется отказом' {
    Set-WinEventStub -Mode ok -Events @(
        (New-TestEvent -Id 1202 -Provider 'Microsoft-Windows-MemoryDiagnostics-Results' `
                       -Time (Get-Date).AddDays(-2) `
                       -Message 'Hardware problems were detected.')
    )
    $out = Invoke-MemCheck
    Assert-Match 'FAIL\s*\]\s*Проверка памяти Windows' $out 'событие 1202 — настоящие ошибки'
}

Test 'событие без вердикта не выдаётся ни за PASS, ни за FAIL' {
    Set-WinEventStub -Mode ok -Events @(
        (New-TestEvent -Id 1101 -Provider 'Microsoft-Windows-MemoryDiagnostics-Results' `
                       -Time (Get-Date).AddDays(-2) -Message 'Some other record.')
    )
    $out = Invoke-MemCheck
    Assert-Match 'NOT_MEASURED\s*\]\s*Проверка памяти Windows' $out 'вердикта нет — значит не измерено'
}

Test 'свежий чистый прогон перевешивает старый прогон с ошибками' {
    # Планку заменили и перепроверили. Старое 1202 не должно вечно держать
    # машину в статусе сбойной.
    Set-WinEventStub -Mode ok -Events @(
        (New-TestEvent -Id 1202 -Provider 'Microsoft-Windows-MemoryDiagnostics-Results' `
                       -Time (Get-Date).AddDays(-20) -Message 'Hardware problems were detected.'),
        (New-TestEvent -Id 1201 -Provider 'Microsoft-Windows-MemoryDiagnostics-Results' `
                       -Time (Get-Date).AddDays(-1) -Message 'detected no errors.')
    )
    $out = Invoke-MemCheck -Days 60
    Assert-Match 'PASS\s*\]\s*Проверка памяти Windows' $out 'вердикт берётся по самому свежему прогону'
}

Test 'свежий прогон с ошибками перевешивает старый чистый' {
    Set-WinEventStub -Mode ok -Events @(
        (New-TestEvent -Id 1201 -Provider 'Microsoft-Windows-MemoryDiagnostics-Results' `
                       -Time (Get-Date).AddDays(-20) -Message 'detected no errors.'),
        (New-TestEvent -Id 1202 -Provider 'Microsoft-Windows-MemoryDiagnostics-Results' `
                       -Time (Get-Date).AddDays(-1) -Message 'Hardware problems were detected.')
    )
    $out = Invoke-MemCheck -Days 60
    Assert-Match 'FAIL\s*\]\s*Проверка памяти Windows' $out 'и в обратную сторону тоже'
}
