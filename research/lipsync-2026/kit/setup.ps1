<#
.SYNOPSIS
    Prepare LongCat-Video-Avatar 1.5 for a test run on Windows.
.DESCRIPTION
    Clones the repo, applies the compatibility patch (lazy triton import,
    backend selection instead of hardcoded NCCL, --height/--width flags),
    and checks that the modules import. Weights are downloaded only with
    -Weights.

    NOTE: messages are intentionally ASCII-only. Windows PowerShell 5.1 reads
    .ps1 files as ANSI unless they carry a UTF-8 BOM, and mangled non-ASCII
    text breaks the parser.

    The recommended contour is still WSL2: -Wsl runs the bash version inside
    WSL, where flash-attn and NCCL work.
.EXAMPLE
    .\setup.ps1 -Dir D:\AI_CONTENT\_lipsync_test\LongCat-Video
.EXAMPLE
    .\setup.ps1 -Dir .\LongCat-Video -Weights
.EXAMPLE
    .\setup.ps1 -Wsl -Dir D:\AI_CONTENT\_lipsync_test\LongCat-Video
#>
[CmdletBinding()]
param(
    [string]$Dir = ".\LongCat-Video",
    [switch]$Weights,
    [switch]$InstallDeps,
    [switch]$Wsl
)

$ErrorActionPreference = "Stop"
# native command exit codes are checked manually via $LASTEXITCODE
$PSNativeCommandUseErrorActionPreference = $false
$kit = $PSScriptRoot
$patch = Join-Path $kit "longcat-compat.patch"

function Invoke-Native {
    # native stderr must not become a terminating error under -ErrorAction Stop
    param([string]$File, [string[]]$Arguments)
    $old = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        & $File @Arguments 2>&1 | ForEach-Object { $_.ToString() } | Out-Null
        return $LASTEXITCODE
    }
    finally { $ErrorActionPreference = $old }
}

function ConvertTo-WslPath([string]$p) {
    if ($p -match '^[A-Za-z]:\\' -or $p -like '*\*') {
        $converted = & wsl wslpath -a "$p" 2>$null
        if ($LASTEXITCODE -eq 0 -and $converted) { return $converted.Trim() }
    }
    return $p
}

if ($Wsl) {
    Write-Host "==> running through WSL2"
    $shPath = ConvertTo-WslPath (Join-Path $kit "setup.sh")
    $dirWsl = ConvertTo-WslPath $Dir
    $wslArgs = @("bash", $shPath, "--dir", $dirWsl)
    Write-Host "==> environment preflight"
& $pyExe @pyPre (Join-Path $kit "preflight.py") --repo $Dir
# informational only: weights may still be missing at this point

if ($InstallDeps) {
    Write-Host "==> installing requirements without flash-attn"
    # flash-attn 2.7.4.post1 builds from source and fails on Windows; after the
    # compatibility patch it is optional, the xformers/plain attention path works.
    foreach ($req in @("requirements.txt", "requirements_avatar.txt")) {
        $src = Join-Path $Dir $req
        if (-not (Test-Path $src)) { continue }
        $dst = Join-Path $Dir ($req -replace '\.txt$', '-nofa.txt')
        Get-Content $src | Where-Object { $_ -notmatch '^\s*flash[-_]attn' } | Set-Content $dst -Encoding ascii
        Write-Host "    pip install -r $dst"
        & $pyExe @pyPre -m pip install -r $dst
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "pip failed on $req; install the remaining packages manually"
        }
    }
}

if ($Weights) { $wslArgs += "--weights" }
    & wsl -- @wslArgs
    exit $LASTEXITCODE
}

function Get-Python {
    foreach ($c in @("python", "python3")) {
        if (Get-Command $c -ErrorAction SilentlyContinue) { return , @($c) }
    }
    if (Get-Command "py" -ErrorAction SilentlyContinue) { return , @("py", "-3") }
    throw "Python not found in PATH"
}

if (-not (Get-Command "git" -ErrorAction SilentlyContinue)) { throw "git not found in PATH" }

$py = Get-Python
$pyExe = $py[0]
$pyPre = @()
if ($py.Count -gt 1) { $pyPre = $py[1..($py.Count - 1)] }

$pyVer = (& $pyExe @pyPre -c "import sys; print('%d.%d' % sys.version_info[:2])").Trim()
Write-Host "==> python $pyVer ($pyExe)"
if ($pyVer -notin @("3.10", "3.11", "3.12")) {
    Write-Warning "LongCat-Video pins torch==2.6.0, which has no wheels for python $pyVer."
    Write-Warning "Create a 3.10-3.12 environment before installing requirements, e.g.:"
    Write-Warning "    py -3.11 -m venv .venv ; .\.venv\Scripts\Activate.ps1"
    Write-Warning "Clone and patch below still work; only the actual run needs that env."
}

if (-not (Test-Path (Join-Path $Dir ".git"))) {
    Write-Host "==> cloning LongCat-Video into $Dir"
    # core.autocrlf=false: the patch is LF; CRLF in the worktree breaks git apply
    & git -c core.autocrlf=false clone --single-branch --branch main `
        https://github.com/meituan-longcat/LongCat-Video $Dir
    if ($LASTEXITCODE -ne 0) { throw "git clone failed with code $LASTEXITCODE" }
}
if (-not (Test-Path (Join-Path $Dir ".git"))) { throw "clone directory $Dir is missing" }

Write-Host "==> applying compatibility patch"
# Normalize to LF. Cloning this repo on Windows may rewrite the patch to CRLF,
# and then git apply cannot match the context of the LF sources.
$patchLf = Join-Path ([IO.Path]::GetTempPath()) "longcat-compat.lf.patch"
$text = [IO.File]::ReadAllText($patch)
[IO.File]::WriteAllText($patchLf, ($text -replace "`r`n", "`n"))

Push-Location $Dir
try {
    if ((Invoke-Native "git" @("apply", "--check", $patchLf)) -eq 0) {
        if ((Invoke-Native "git" @("apply", $patchLf)) -ne 0) { throw "git apply failed" }
        Write-Host "    patch applied"
    }
    elseif ((Invoke-Native "git" @("apply", "--reverse", "--check", $patchLf)) -eq 0) {
        Write-Host "    patch already applied, skipping"
    }
    elseif ((Invoke-Native "git" @("apply", "--ignore-whitespace", $patchLf)) -eq 0) {
        Write-Host "    patch applied (--ignore-whitespace)"
    }
    else {
        throw "patch does not apply: upstream changed, or the worktree was checked out with CRLF"
    }
}
finally {
    Pop-Location
    Remove-Item $patchLf -ErrorAction SilentlyContinue
}

Write-Host "==> checking imports without triton/flash-attn"
$checker = Join-Path (Split-Path $kit -Parent) "checks\import_check.py"
& $pyExe @pyPre $checker $Dir
if ($LASTEXITCODE -ne 0) { throw "import check failed, see output above" }

if ($Weights) {
    Write-Host "==> downloading weights (tens of GB, slow)"
    $target = Join-Path $Dir "weights\LongCat-Video-Avatar-1.5"
    if (Get-Command "huggingface-cli" -ErrorAction SilentlyContinue) {
        & huggingface-cli download meituan-longcat/LongCat-Video-Avatar-1.5 --local-dir $target
    }
    else {
        & $pyExe @pyPre -m huggingface_hub.commands.huggingface_cli `
            download meituan-longcat/LongCat-Video-Avatar-1.5 --local-dir $target
    }
    if ($LASTEXITCODE -ne 0) { throw "weight download failed with code $LASTEXITCODE" }
}

$bench = Join-Path $kit "bench_longcat.py"
$weightsDir = Join-Path $Dir "weights\LongCat-Video-Avatar-1.5"
Write-Host ""
Write-Host "Done. Minimal benchmark (1 segment = 3.72 s of video, 480p, INT8):"
Write-Host ""
Write-Host "  python `"$bench`" --repo `"$Dir`" --checkpoint_dir `"$weightsDir`" --segments 1 --resolution 480p --vram_budget_gb 24"
Write-Host ""
Write-Host "Vertical 9:16 -> add --vertical. Full ~32 s reel -> --segments 10."
Write-Host "If torchrun fails on process group init or flash-attn, rerun in WSL2: .\setup.ps1 -Wsl"
Write-Host "Dependencies (without flash-attn): .\setup.ps1 -Dir <dir> -InstallDeps"
Write-Host "bench_longcat.py runs preflight and adjusts the attention backend automatically."
