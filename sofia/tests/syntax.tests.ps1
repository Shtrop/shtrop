<#
    Синтаксис всех скриптов набора. Ошибка разбора на Windows означает, что
    владелец получит отказ в самый неподходящий момент — при инциденте.
#>

$sofiaDir = Split-Path $PSScriptRoot -Parent

foreach ($f in (Get-ChildItem -Path $sofiaDir -Filter '*.ps1' -File -Recurse | Sort-Object FullName)) {
    $rel = $f.FullName.Substring($sofiaDir.Length).TrimStart('\', '/')
    Test ("синтаксис: {0}" -f $rel) {
        $errors = $null
        $null = [System.Management.Automation.Language.Parser]::ParseFile($f.FullName, [ref]$null, [ref]$errors)
        if ($errors -and $errors.Count -gt 0) {
            throw ("ошибок разбора: {0}; первая: {1} (строка {2})" -f $errors.Count, $errors[0].Message, $errors[0].Extent.StartLineNumber)
        }
    }
}

# Инструменты обещают владельцу, что не удаляют файлы студии и не трогают hold.
# Проверяем обещание по тексту: Remove-Item допустим только во временных каталогах.
Test 'инструменты не снимают HOST_SAFE_HOLD.flag' {
    foreach ($f in (Get-ChildItem -Path $sofiaDir -Filter '*.ps1' -File)) {
        $text = Get-Content $f.FullName -Raw
        if ($text -match '(?i)(Remove-Item|del|Clear-Content)[^\r\n]*HOST_SAFE_HOLD') {
            throw ("{0} пытается снять hold" -f $f.Name)
        }
        if ($text -match '(?i)(Remove-Item|del)[^\r\n]*PUBLISHING_DISABLED') {
            throw ("{0} пытается снять запрет публикации" -f $f.Name)
        }
    }
}

# Инструменты запускаются штатным Windows PowerShell 5.1, а он читает файл без
# BOM как ANSI: весь русский текст превращается в мусор ровно в тот момент,
# когда владелец разбирает инцидент. Кодировка здесь — часть контракта.
foreach ($f in (Get-ChildItem -Path $sofiaDir -Filter '*.ps1' -File -Recurse | Sort-Object FullName)) {
    $rel = $f.FullName.Substring($sofiaDir.Length).TrimStart('\', '/')
    Test ("UTF-8 BOM: {0}" -f $rel) {
        $bytes = [System.IO.File]::ReadAllBytes($f.FullName)
        if ($bytes.Length -lt 3 -or $bytes[0] -ne 0xEF -or $bytes[1] -ne 0xBB -or $bytes[2] -ne 0xBF) {
            throw 'файл сохранён без UTF-8 BOM — PowerShell 5.1 покажет кириллицу как мусор'
        }
    }
}

# get_sofia_tools.ps1 скачивает набор по списку. Файл, которого нет в списке,
# не доедет до машины студии, и скрипт, который его подключает, отвалится
# ровно во время инцидента.
Test 'get_sofia_tools.ps1 перечисляет все скрипты набора' {
    $downloader = Join-Path $sofiaDir 'get_sofia_tools.ps1'
    $text = Get-Content $downloader -Raw
    foreach ($f in (Get-ChildItem -Path $sofiaDir -Filter '*.ps1' -File)) {
        if ($text -notmatch [regex]::Escape($f.Name)) {
            throw ("{0} не перечислен в get_sofia_tools.ps1" -f $f.Name)
        }
    }
}

# Загрузчик дочитывает новые файлы набора, разбирая собственный свежескачанный
# текст. Разбор и формат списка обязаны совпадать: иначе новый файл снова
# доедет только со второго запуска — во время инцидента этого никто не заметит.
Test 'загрузчик разбирает собственный список файлов' {
    $downloader = Join-Path $sofiaDir 'get_sofia_tools.ps1'
    $text = Get-Content $downloader -Raw

    # Шаблон продублирован из Get-DeclaredFileList: если он там изменится,
    # эта проверка обязана упасть.
    $pattern = '(?s)\$files\s*=\s*@\((.*?)\)'
    Assert-Match ([regex]::Escape($pattern)) $text 'шаблон разбора в скрипте разошёлся с тестом'

    $m = [regex]::Match($text, $pattern)
    Assert-True $m.Success 'блок $files не найден'
    $declared = @([regex]::Matches($m.Groups[1].Value, "'([^']+\.ps1)'") | ForEach-Object { $_.Groups[1].Value })

    $actual = @(Get-ChildItem -Path $sofiaDir -Filter '*.ps1' -File | ForEach-Object { $_.Name } | Sort-Object)
    Assert-Equal ($actual -join ',') (($declared | Sort-Object) -join ',') 'разобранный список не совпал с составом набора'
}
