<#
.SYNOPSIS
    Готовит LongCat-Video-Avatar 1.5 к тестовому прогону на Windows.
.DESCRIPTION
    Клонирует репозиторий, накладывает патч совместимости (ленивый triton,
    выбор backend вместо жёсткого NCCL, флаги --height/--width) и проверяет,
    что модули импортируются. Веса не качает, пока не передан -Weights.

    Рекомендуемый контур всё равно WSL2: ключ -Wsl прогоняет bash-версию
    внутри WSL, где работают flash-attn и NCCL.
.EXAMPLE
    .\setup.ps1 -Dir D:\AI_CONTENT\_lipsync_test\LongCat-Video
.EXAMPLE
    .\setup.ps1 -Dir .\LongCat-Video -Weights
.EXAMPLE
    .\setup.ps1 -Wsl -Dir ./LongCat-Video
#>
[CmdletBinding()]
param(
    [string]$Dir = ".\LongCat-Video",
    [switch]$Weights,
    [switch]$Wsl
)

$ErrorActionPreference = "Stop"
# коды возврата нативных команд проверяем вручную по $LASTEXITCODE
$PSNativeCommandUseErrorActionPreference = $false
$kit = $PSScriptRoot
$patch = Join-Path $kit "longcat-compat.patch"

function ConvertTo-WslPath([string]$p) {
    if ($p -match '^[A-Za-z]:\\' -or $p -like '*\*') {
        $converted = (& wsl wslpath -a "$p") 2>$null
        if ($LASTEXITCODE -eq 0 -and $converted) { return $converted.Trim() }
    }
    return $p
}

if ($Wsl) {
    Write-Host "==> прогон через WSL2"
    $shPath = ConvertTo-WslPath (Join-Path $PSScriptRoot "setup.sh")
    $dirWsl = ConvertTo-WslPath $Dir
    $wslArgs = @("bash", $shPath, "--dir", $dirWsl)
    if ($Weights) { $wslArgs += "--weights" }
    & wsl -- @wslArgs
    exit $LASTEXITCODE
}

function Get-Python {
    foreach ($c in @("python", "python3")) {
        if (Get-Command $c -ErrorAction SilentlyContinue) { return @($c) }
    }
    if (Get-Command "py" -ErrorAction SilentlyContinue) { return @("py", "-3") }
    throw "Python не найден в PATH"
}

foreach ($tool in @("git")) {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) { throw "$tool не найден в PATH" }
}
$py = Get-Python
$pyExe = $py[0]
$pyPre = @(); if ($py.Count -gt 1) { $pyPre = $py[1..($py.Count - 1)] }

if (-not (Test-Path (Join-Path $Dir ".git"))) {
    Write-Host "==> клонирую LongCat-Video в $Dir"
    # core.autocrlf=false: патч сформирован с LF, CRLF в рабочем дереве его ломает
    & git -c core.autocrlf=false clone --single-branch --branch main `
        https://github.com/meituan-longcat/LongCat-Video $Dir
    if ($LASTEXITCODE -ne 0) { throw "git clone завершился с кодом $LASTEXITCODE" }
}

Write-Host "==> применяю патч совместимости"
Push-Location $Dir
try {
    & git apply --check $patch 2>$null
    if ($LASTEXITCODE -eq 0) {
        & git apply $patch
        if ($LASTEXITCODE -ne 0) { throw "git apply завершился с кодом $LASTEXITCODE" }
        Write-Host "    патч применён"
    }
    else {
        & git apply --reverse --check $patch 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "    патч уже применён, пропускаю"
        }
        else {
            & git apply --ignore-whitespace $patch 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "    патч применён (с --ignore-whitespace)"
            }
            else {
                throw "патч не накладывается — upstream изменился или в дереве CRLF; сверьте вручную"
            }
        }
    }
}
finally { Pop-Location }

Write-Host "==> проверяю импорт без triton/flash-attn"
$checker = Join-Path (Split-Path $kit -Parent) "checks\import_check.py"
& $pyExe @pyPre $checker $Dir
if ($LASTEXITCODE -ne 0) { throw "импорт не прошёл — смотрите вывод выше" }

if ($Weights) {
    Write-Host "==> качаю веса (долго, десятки ГБ)"
    $target = Join-Path $Dir "weights\LongCat-Video-Avatar-1.5"
    if (Get-Command "huggingface-cli" -ErrorAction SilentlyContinue) {
        & huggingface-cli download meituan-longcat/LongCat-Video-Avatar-1.5 --local-dir $target
    }
    else {
        & $pyExe @pyPre -m huggingface_hub.commands.huggingface_cli `
            download meituan-longcat/LongCat-Video-Avatar-1.5 --local-dir $target
    }
    if ($LASTEXITCODE -ne 0) { throw "скачивание весов завершилось с кодом $LASTEXITCODE" }
}

$bench = Join-Path $kit "bench_longcat.py"
Write-Host @"

Готово. Минимальный замер (1 сегмент = 3.72 c видео, 480p, INT8):

  python $bench --repo $Dir ``
    --checkpoint_dir $Dir\weights\LongCat-Video-Avatar-1.5 ``
    --segments 1 --resolution 480p --vram_budget_gb 24

Вертикаль 9:16 — добавить --vertical. Полный Reel ~32 c — --segments 10.
Если torchrun упадёт на инициализации process group или на flash-attn,
перезапустите тот же прогон в WSL2: .\setup.ps1 -Wsl
"@
