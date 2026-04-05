param(
    [string]$EnvName = "spatialcode-repro",
    [string]$PythonVersion = "3.11"
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$RequirementsPath = Join-Path $ProjectRoot "requirements.txt"

Write-Host "Creating conda environment '$EnvName' with Python $PythonVersion"
conda --no-plugins create --solver classic -n $EnvName python=$PythonVersion pip -y

Write-Host "Installing PyTorch CUDA 12.8 wheels"
conda run -n $EnvName python -m pip install --upgrade pip
conda run -n $EnvName python -m pip install torch==2.10.0 torchvision==0.25.0 torchaudio==2.10.0 --index-url https://download.pytorch.org/whl/cu128

Write-Host "Installing project dependencies"
conda run -n $EnvName python -m pip install -r $RequirementsPath

Write-Host "Verifying torch CUDA visibility"
conda run -n $EnvName python -c "import torch; print('torch', torch.__version__); print('cuda', torch.version.cuda); print('cuda_available', torch.cuda.is_available()); print('device', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'cpu')"
