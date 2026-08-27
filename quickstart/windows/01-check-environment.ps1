[CmdletBinding()]
param(
    [switch]$InstallDependencies,
    [switch]$MigrateRuntimeConfig
)

. (Join-Path $PSScriptRoot "_common.ps1")

$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
if ($null -eq $pythonCommand) {
    throw "Python was not found. Install Python 3.11 or 3.12 first."
}
$pythonVersion = (& $pythonCommand.Source -c "import sys; print('.'.join(map(str, sys.version_info[:3])))").Trim()
$pythonSupported = & $pythonCommand.Source -c "import sys; print(int((3, 11) <= sys.version_info[:2] <= (3, 12)))"
if ($pythonSupported.Trim() -ne "1") {
    throw "Python $pythonVersion is not supported. Use Python 3.11 or 3.12."
}

$nvidia = Get-Command nvidia-smi -ErrorAction SilentlyContinue
if ($null -eq $nvidia) {
    throw "nvidia-smi was not found. The local training and Transformers serving path requires an NVIDIA GPU driver."
}
$gpuName = (& $nvidia.Source --query-gpu=name --format=csv,noheader | Select-Object -First 1).Trim()

$venvPython = Join-Path $Script:RepoRoot ".venv/Scripts/python.exe"
if ($InstallDependencies) {
    if (-not (Test-Path -LiteralPath $venvPython -PathType Leaf)) {
        & $pythonCommand.Source -m venv (Join-Path $Script:RepoRoot ".venv")
        if ($LASTEXITCODE -ne 0) { throw "Failed to create .venv" }
    }
    & $venvPython -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) { throw "Failed to upgrade pip" }
    & $venvPython -m pip install -r (Join-Path $Script:RepoRoot "requirements.txt")
    if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed" }
}

$runtimePath = Join-Path $Script:RepoRoot "config/runtime_models.json"
$runtimeExample = Join-Path $Script:RepoRoot "config/runtime_models.example.json"
if (-not (Test-Path -LiteralPath $runtimePath)) {
    Copy-Item -LiteralPath $runtimeExample -Destination $runtimePath
}

$runtime = Get-Content -LiteralPath $runtimePath -Raw | ConvertFrom-Json
if ($MigrateRuntimeConfig -and -not $runtime.contract_version) {
    $oldKey = [string]$runtime.api_key
    if (-not $oldKey) {
        throw "The old runtime config has no API key to migrate."
    }
    [Environment]::SetEnvironmentVariable("LOCALRAG_CLOUD_API_KEY", $oldKey, "User")
    $localToken = [Environment]::GetEnvironmentVariable("LOCALRAG_MODEL_API_TOKEN", "User")
    if (-not $localToken) {
        $bytes = [byte[]]::new(32)
        $generator = [Security.Cryptography.RandomNumberGenerator]::Create()
        try { $generator.GetBytes($bytes) } finally { $generator.Dispose() }
        $localToken = [Convert]::ToBase64String($bytes).TrimEnd("=").Replace("+", "-").Replace("/", "_")
        [Environment]::SetEnvironmentVariable("LOCALRAG_MODEL_API_TOKEN", $localToken, "User")
    }
    $example = Get-Content -LiteralPath $runtimeExample -Raw | ConvertFrom-Json
    foreach ($role in @("planner", "rag", "summary")) {
        $example.roles.$role.cloud.provider = [string]$runtime.provider
        $example.roles.$role.cloud.base_url = [string]$runtime.base_url
        $example.roles.$role.cloud.model = [string]$runtime.chat_model_name
    }
    $json = $example | ConvertTo-Json -Depth 12
    [IO.File]::WriteAllText($runtimePath, $json + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))
    $runtime = $example
}

if ($runtime.contract_version -ne "localrag-runtime-v2") {
    throw "config/runtime_models.json still uses the old schema. Run this script with -MigrateRuntimeConfig."
}

$missingSecrets = @()
foreach ($name in Get-RuntimeSecretNames $runtimePath) {
    Import-UserEnvironmentVariable $name
    if (-not [Environment]::GetEnvironmentVariable($name, "Process")) {
        $missingSecrets += $name
    }
}

$python = Get-LocalRagPython
$torch = & $python -c "import torch; print(torch.__version__); print(torch.cuda.is_available())" 2>$null
$torchInstalled = $LASTEXITCODE -eq 0

Write-Output "repository=$Script:RepoRoot"
Write-Output "python=$pythonVersion"
Write-Output "gpu=$gpuName"
Write-Output "venv=$([bool](Test-Path -LiteralPath $venvPython))"
Write-Output "torch_installed=$torchInstalled"
if ($torchInstalled) {
    Write-Output "torch_version=$($torch[0])"
    Write-Output "torch_cuda_available=$($torch[1])"
}
Write-Output "runtime_config=$runtimePath"
if ($missingSecrets.Count -gt 0) {
    Write-Warning ("Set these user environment variables before starting the application: " + ($missingSecrets -join ", "))
}
else {
    Write-Output "runtime_secrets=available"
}
