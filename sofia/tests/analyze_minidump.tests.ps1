<#
    Контракт analyze_minidump.ps1.

    Это источник точного кода остановки, из которого runbook выбирает ветку
    расследования. Проверяются оба пути: текст события 1001 и заголовок дампа
    (смещения BugCheckCode различаются между версиями структуры, поэтому
    выбор правильного кандидата — не мелочь).
#>

$tool = Join-Path (Split-Path $PSScriptRoot -Parent) 'analyze_minidump.ps1'

function New-FakeDump {
    <#
        Минимальный заголовок дампа: сигнатура и BugCheckCode по смещению.
        Остальное скрипту не нужно — он читает только первые 0x400 байт.
    #>
    param(
        [Parameter(Mandatory)][string] $Path,
        [Parameter(Mandatory)][string] $Signature,
        [Parameter(Mandatory)][int] $Offset,
        [Parameter(Mandatory)][uint32] $Code
    )
    $buf = New-Object byte[] 0x400
    $sig = [System.Text.Encoding]::ASCII.GetBytes($Signature)
    [Array]::Copy($sig, 0, $buf, 0, $sig.Length)
    [Array]::Copy([BitConverter]::GetBytes($Code), 0, $buf, $Offset, 4)
    [System.IO.File]::WriteAllBytes($Path, $buf)
    $Path
}

function Invoke-Minidump {
    param([string] $DumpPath, [int] $Days = 14)
    & $tool -DumpPath $DumpPath -Days $Days *>&1 | Out-String
}

function New-BugCheckEvent {
    param([uint32] $Code, [string] $Extra = '')
    New-TestEvent -Id 1001 -Provider 'Microsoft-Windows-WER-SystemErrorReporting' `
                  -Time (Get-Date).AddHours(-2) `
                  -Message ("The computer has rebooted from a bugcheck. The bugcheck was: 0x{0:x8} {1}" -f $Code, $Extra)
}

# --------------------------------------------------------------------------

Test 'код остановки достаётся из текста события 1001' {
    $sb = New-Sandbox 'dump_event'
    try {
        Set-WinEventStub -Mode ok -Events @(New-BugCheckEvent -Code 0x154)
        $out = Invoke-Minidump -DumpPath (Join-Path $sb.Dir 'nodumps')
        Assert-Match '0x00000154' $out 'код должен быть напечатан канонически'
        Assert-Match 'UNEXPECTED_STORE_EXCEPTION' $out 'имя кода должно быть распознано'
    } finally { Remove-Sandbox $sb }
}

Test 'параметры и путь к дампу вытаскиваются из текста события' {
    $sb = New-Sandbox 'dump_params'
    try {
        Set-WinEventStub -Mode ok -Events @(
            New-BugCheckEvent -Code 0x124 -Extra '(0x0000000000000000, 0xffffcf8a1b2c3d40). A dump was saved in: C:\Windows\MEMORY.DMP.'
        )
        $out = Invoke-Minidump -DumpPath (Join-Path $sb.Dir 'nodumps')
        Assert-Match '0xffffcf8a1b2c3d40' $out '64-битные параметры должны попасть в вывод'
        Assert-Match 'MEMORY\.DMP' $out 'путь к дампу должен быть показан'
    } finally { Remove-Sandbox $sb }
}

Test 'недоступный журнал не выдаётся за отсутствие крахов' {
    $sb = New-Sandbox 'dump_denied'
    try {
        Set-WinEventStub -Mode denied
        $out = Invoke-Minidump -DumpPath (Join-Path $sb.Dir 'nodumps')
        Assert-Match 'недоступен' $out 'отказ в доступе должен быть назван прямо'
        Assert-NotMatch 'Записей нет' $out 'нечитаемый журнал — не то же самое, что пустой'
    } finally { Remove-Sandbox $sb }
}

Test 'код читается из заголовка 64-битного дампа' {
    $sb = New-Sandbox 'dump_pagedu64'
    try {
        $dumps = Join-Path $sb.Dir 'Minidump'
        New-Item -ItemType Directory -Force -Path $dumps | Out-Null
        New-FakeDump -Path (Join-Path $dumps '092226-01.dmp') -Signature 'PAGEDU64' -Offset 0x38 -Code 0x154 | Out-Null

        Set-WinEventStub -Mode ok -Events @()
        $out = Invoke-Minidump -DumpPath $dumps
        Assert-Match '0x00000154' $out 'код из заголовка должен быть извлечён'
        Assert-Match 'UNEXPECTED_STORE_EXCEPTION' $out 'и классифицирован'
    } finally { Remove-Sandbox $sb }
}

Test 'выбирается то смещение, которое даёт известный код' {
    $sb = New-Sandbox 'dump_offset'
    try {
        $dumps = Join-Path $sb.Dir 'Minidump'
        New-Item -ItemType Directory -Force -Path $dumps | Out-Null
        # Код лежит по второму кандидату смещения; по первому — мусор,
        # которого нет в справочнике.
        $p = Join-Path $dumps '092226-02.dmp'
        New-FakeDump -Path $p -Signature 'PAGEDU64' -Offset 0x80 -Code 0x116 | Out-Null
        $buf = [System.IO.File]::ReadAllBytes($p)
        [Array]::Copy([BitConverter]::GetBytes([uint32]0x7777), 0, $buf, 0x38, 4)
        [System.IO.File]::WriteAllBytes($p, $buf)

        Set-WinEventStub -Mode ok -Events @()
        $out = Invoke-Minidump -DumpPath $dumps
        Assert-Match 'VIDEO_TDR_FAILURE' $out 'должен быть выбран кандидат с известным кодом'
        Assert-NotMatch '0x00007777' $out 'мусор по первому смещению не должен победить'
    } finally { Remove-Sandbox $sb }
}

Test 'отсутствие дампов не мешает работе' {
    $sb = New-Sandbox 'dump_none'
    try {
        Set-WinEventStub -Mode ok -Events @()
        $out = Invoke-Minidump -DumpPath (Join-Path $sb.Dir 'nodumps')
        Assert-Match 'Дампов не найдено' $out 'отсутствие дампов должно быть сказано прямо'
    } finally { Remove-Sandbox $sb }
}
