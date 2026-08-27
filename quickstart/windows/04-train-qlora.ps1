[CmdletBinding()]
param(
    [switch]$InstallLlamaFactory,
    [switch]$CheckOnly
)

. (Join-Path $PSScriptRoot "_common.ps1")
$python = Get-LocalRagPython
$config = Resolve-RepoPath "finetune/llamafactory_configs/localrag_sft_full_qlora.yaml"
$trainData = Resolve-RepoPath "finetune/datasets/localrag_sft_full.jsonl"
$validationData = Resolve-RepoPath "finetune/datasets/localrag_sft_full_validation.jsonl"
$modelPath = Resolve-RepoPath "models/Qwen3-4B"
$adapterPath = Resolve-RepoPath "saves/Qwen3-4B-Thinking/lora/localrag_sft_full_qlora"

if ($InstallLlamaFactory) {
    & $python -m pip install "llamafactory==0.9.5"
    if ($LASTEXITCODE -ne 0) { throw "LLaMA-Factory installation failed" }
}

$cli = Get-LlamaFactoryCli
$trainCount = if (Test-Path -LiteralPath $trainData) { @(Get-Content -LiteralPath $trainData).Count } else { 0 }
$validationCount = if (Test-Path -LiteralPath $validationData) { @(Get-Content -LiteralPath $validationData).Count } else { 0 }
$weights = @(Get-ChildItem -LiteralPath $modelPath -Filter "*.safetensors" -File -ErrorAction SilentlyContinue)
$cuda = (& $python -c "import torch; print(torch.cuda.is_available())").Trim()

Write-Output "config=$config"
Write-Output "train_rows=$trainCount"
Write-Output "validation_rows=$validationCount"
Write-Output "base_weight_files=$($weights.Count)"
Write-Output "cuda_available=$cuda"
Write-Output "adapter_output=$adapterPath"
if ($trainCount -ne 183 -or $validationCount -ne 20) {
    throw "Prepared data must contain 183 training rows and 20 validation rows."
}
if ($weights.Count -eq 0) { throw "Qwen3-4B weights are missing" }
if ($cuda -ne "True") { throw "CUDA is not available to PyTorch" }

if ($CheckOnly) {
    Write-Output "training_preflight=passed"
    return
}
if (Test-Path -LiteralPath $adapterPath) {
    throw "Adapter output already exists. Move it aside or choose a new output_dir before training."
}
Write-Warning "This command runs the complete 4-bit QLoRA training job and can take a long time."
Push-Location -LiteralPath $Script:RepoRoot
try {
    & $cli train $config
    if ($LASTEXITCODE -ne 0) { throw "QLoRA training failed with code $LASTEXITCODE" }
}
finally {
    Pop-Location
}
