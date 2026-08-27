[CmdletBinding()]
param(
    [switch]$SkipIndex,
    [switch]$CheckOnly
)

. (Join-Path $PSScriptRoot "_common.ps1")

$sourceDataset = Resolve-RepoPath "data/evaluation/train/train_set.json"
$trainOutput = Resolve-RepoPath "finetune/datasets/localrag_sft_full.jsonl"
$validationOutput = Resolve-RepoPath "finetune/datasets/localrag_sft_full_validation.jsonl"
$registry = Resolve-RepoPath "data/evaluation/shared/source_registry.json"
$store = Resolve-RepoPath "results/local_corpus/doc_type_aware"

if ($CheckOnly) {
    $sourceCount = @((Get-Content -LiteralPath $sourceDataset -Raw | ConvertFrom-Json)).Count
    $trainCount = if (Test-Path -LiteralPath $trainOutput) { @(Get-Content -LiteralPath $trainOutput).Count } else { 0 }
    $validationCount = if (Test-Path -LiteralPath $validationOutput) { @(Get-Content -LiteralPath $validationOutput).Count } else { 0 }
    $registryCount = @((Get-Content -LiteralPath $registry -Raw | ConvertFrom-Json)).Count
    Write-Output "source_training_rows=$sourceCount"
    Write-Output "prepared_train_rows=$trainCount"
    Write-Output "prepared_validation_rows=$validationCount"
    Write-Output "corpus_sources=$registryCount"
    Write-Output "index_present=$([bool](Test-Path -LiteralPath $store))"
    if ($sourceCount -ne 203) { throw "Expected 203 source training rows" }
    return
}

Invoke-LocalRagPython scripts/prepare_sft_dataset.py `
    --input data/evaluation/train/train_set.json `
    --train-output finetune/datasets/localrag_sft_full.jsonl `
    --validation-output finetune/datasets/localrag_sft_full_validation.jsonl `
    --validation-count 20 `
    --format llamafactory `
    --dataset-version localrag-sft-full

if (-not $SkipIndex) {
    $runtimePath = Resolve-RepoPath "config/runtime_models.json"
    foreach ($name in Get-RuntimeSecretNames $runtimePath) {
        Import-UserEnvironmentVariable $name
        if (-not [Environment]::GetEnvironmentVariable($name, "Process")) {
            [Environment]::SetEnvironmentVariable($name, "data-preparation-only", "Process")
        }
    }
    Invoke-LocalRagPython scripts/build_active_corpus.py `
        --registry data/evaluation/shared/source_registry.json `
        --store results/local_corpus/doc_type_aware `
        --strategy doc_type_aware `
        --profile config/active_corpus.json `
        --release-version local
}

& $PSCommandPath -SkipIndex -CheckOnly
