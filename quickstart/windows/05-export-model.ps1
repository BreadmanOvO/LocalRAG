[CmdletBinding()]
param(
    [switch]$CheckOnly,
    [switch]$UseEvaluatedAdapter
)

. (Join-Path $PSScriptRoot "_common.ps1")
$cli = Get-LlamaFactoryCli
$config = Resolve-RepoPath "finetune/llamafactory_configs/localrag_sft_full_export.yaml"
$adapter = if ($UseEvaluatedAdapter) {
    Resolve-RepoPath "saves/Qwen3-4B-Thinking/lora/localrag_sft_e6_1_qlora_webui"
}
else {
    Resolve-RepoPath "saves/Qwen3-4B-Thinking/lora/localrag_sft_full_qlora"
}
$merged = Resolve-RepoPath "artifacts/models/localrag-sft-full-merged"

$adapterReady = (Test-Path -LiteralPath (Join-Path $adapter "adapter_model.safetensors")) -and
    (Test-Path -LiteralPath (Join-Path $adapter "adapter_config.json"))
Write-Output "adapter=$adapter"
Write-Output "adapter_ready=$adapterReady"
Write-Output "merged_output=$merged"
Write-Output "merged_present=$([bool](Test-Path -LiteralPath $merged))"
if (-not $adapterReady) { throw "The trained adapter is incomplete" }
if ($CheckOnly) { return }
if ($UseEvaluatedAdapter) {
    throw "-UseEvaluatedAdapter is a preflight option only. Use the fixed E6.1 deployment scripts for that adapter."
}
if (Test-Path -LiteralPath $merged) {
    throw "Merged output already exists. Move it aside before exporting again."
}
Write-Warning "Merging the adapter is slower than the preflight check and temporarily uses substantial CPU RAM."
Push-Location -LiteralPath $Script:RepoRoot
try {
    & $cli export $config
    if ($LASTEXITCODE -ne 0) { throw "Model export failed with code $LASTEXITCODE" }
}
finally {
    Pop-Location
}
Write-Output "For GGUF conversion, install llama.cpp and run convert_hf_to_gguf.py on $merged, then quantize with llama-quantize.exe Q4_K_M."
