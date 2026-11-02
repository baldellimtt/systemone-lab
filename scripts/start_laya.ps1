# Avvia Laya locale (API Jev-compatibile su http://127.0.0.1:8000)
# Uso: .\scripts\start_laya.ps1
# Opzionale: .\scripts\start_laya.ps1 -Device cpu

param(
    [ValidateSet("cuda", "cpu", "auto")]
    [string]$Device = "auto"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$VenvPython = Join-Path $Root ".venv-laya\Scripts\python.exe"
$VenvLayaServe = Join-Path $Root ".venv-laya\Scripts\laya-serve.exe"

if (-not (Test-Path $VenvPython)) {
    Write-Host "Creo .venv-laya e installo Laya (prima volta, puo' richiedere alcuni minuti)..."
    python -m venv .venv-laya
    & $VenvPython -m pip install -U pip

    # Prova CUDA; se fallisce, resta CPU.
    $useCuda = $false
    if ($Device -ne "cpu") {
        Write-Host "Installo PyTorch CUDA..."
        & $VenvPython -m pip install torch --index-url https://download.pytorch.org/whl/cu124
        $cudaOk = & $VenvPython -c "import torch; print(torch.cuda.is_available())"
        if ($cudaOk.Trim() -eq "True") {
            $useCuda = $true
            Write-Host "CUDA disponibile."
        } else {
            Write-Host "CUDA non disponibile in torch — passo a CPU."
            & $VenvPython -m pip install --force-reinstall torch --index-url https://download.pytorch.org/whl/cpu
        }
    } else {
        & $VenvPython -m pip install torch --index-url https://download.pytorch.org/whl/cpu
    }

    Write-Host "Installo laya[serve]..."
    & $VenvPython -m pip install "laya[serve]"
} else {
    $cudaOk = & $VenvPython -c "import torch; print(torch.cuda.is_available())" 2>$null
    $useCuda = ($Device -ne "cpu") -and ($cudaOk.Trim() -eq "True")
}

if ($Device -eq "cuda") { $resolved = "cuda" }
elseif ($Device -eq "cpu") { $resolved = "cpu" }
elseif ($useCuda) { $resolved = "cuda" }
else { $resolved = "cpu" }

# english + multilingual (~1.5GB total): IT/ES/FR/... via router
$env:LAYA_HOST = "127.0.0.1"
$env:LAYA_PORT = "8000"
$env:LAYA_DEVICE = $resolved
$env:LAYA_MODELS = "english,multilingual"
$env:LAYA_PRELOAD = "1"
$env:LAYA_DEFAULT_MODEL = "english"
$env:LAYA_MAX_LOADED = "2"
$env:NO_PROXY = "localhost,127.0.0.1"

Write-Host "Avvio laya-serve su http://127.0.0.1:8000 (device=$resolved, models=english+multilingual)"
Write-Host "Ctrl+C per fermare. UI: .\.venv-laya\Scripts\python.exe scripts\lab_ui.py"
& $VenvLayaServe
