[CmdletBinding()]
param(
    [ValidateSet("HuggingFace", "ModelScope")]
    [string]$Source = "HuggingFace",
    [string]$ModelId = "Qwen/Qwen3-4B",
    [string]$Output = "models/Qwen3-4B",
    [switch]$CheckOnly
)

. (Join-Path $PSScriptRoot "_common.ps1")
$outputPath = Resolve-RepoPath $Output
$python = Get-LocalRagPython

if ($CheckOnly) {
    $required = @("config.json", "tokenizer.json")
    $missing = @($required | Where-Object { -not (Test-Path -LiteralPath (Join-Path $outputPath $_)) })
    $weights = @(Get-ChildItem -LiteralPath $outputPath -Filter "*.safetensors" -File -ErrorAction SilentlyContinue)
    Write-Output "model_path=$outputPath"
    Write-Output "weight_files=$($weights.Count)"
    if ($missing.Count -gt 0 -or $weights.Count -eq 0) {
        throw "Model files are incomplete. Missing: $($missing -join ', ')"
    }
    Write-Output "model_ready=true"
    return
}

New-Item -ItemType Directory -Force -Path $outputPath | Out-Null
if ($Source -eq "HuggingFace") {
    & $python -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id=r'$ModelId', local_dir=r'$outputPath')"
}
else {
    & $python -c "from modelscope.hub.snapshot_download import snapshot_download; snapshot_download(r'$ModelId', local_dir=r'$outputPath')"
}
if ($LASTEXITCODE -ne 0) {
    throw "$Source download failed with code $LASTEXITCODE"
}

& $PSCommandPath -Source $Source -ModelId $ModelId -Output $Output -CheckOnly
