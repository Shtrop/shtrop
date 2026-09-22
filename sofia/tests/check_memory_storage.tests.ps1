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
