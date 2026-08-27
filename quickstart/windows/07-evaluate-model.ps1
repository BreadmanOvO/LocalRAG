[CmdletBinding()]
param(
    [ValidateSet("Smoke", "Quality")]
    [string]$Mode = "Smoke",
    [string]$Endpoint = "http://127.0.0.1:8001/v1",
    [string]$Profile = "adapter_bf16",
    [string]$Manifest = "model_deployment/manifests/e6_1_input_manifest.json",
    [switch]$CheckOnly
)

. (Join-Path $PSScriptRoot "_common.ps1")
$runtimePath = Resolve-RepoPath "config/runtime_models.json"
foreach ($name in Get-RuntimeSecretNames $runtimePath) {
    Import-UserEnvironmentVariable $name
}
$token = [Environment]::GetEnvironmentVariable("LOCALRAG_MODEL_API_TOKEN", "Process")
if (-not $token) { throw "LOCALRAG_MODEL_API_TOKEN is not set" }
$headers = @{ Authorization = "Bearer $token" }

if ($CheckOnly) {
    Write-Output "endpoint=$Endpoint"
    Write-Output "manifest=$([bool](Test-Path -LiteralPath (Resolve-RepoPath $Manifest)))"
    Write-Output "quality_dataset=$([bool](Test-Path -LiteralPath (Resolve-RepoPath 'data/evaluation/gold/generation_eval_set.json')))"
    return
}

$models = Invoke-RestMethod -Headers $headers -Uri "$Endpoint/models" -Method Get
$modelId = [string]$models.data[0].id
if (-not $modelId) { throw "The model service returned no model identity" }
Write-Output "model_id=$modelId"

if ($Mode -eq "Smoke") {
    $body = @{
        model = $modelId
        messages = @(
            @{ role = "system"; content = "只根据给定证据回答。证据：Apollo 感知模块会融合多种传感器输入。" },
            @{ role = "user"; content = "Apollo 感知模块会做什么？" }
        )
        temperature = 0
        max_tokens = 128
        stream = $false
        purpose = "rag_generation"
        metadata = @{ run_id = "quickstart-smoke" }
    } | ConvertTo-Json -Depth 8
    $timer = [Diagnostics.Stopwatch]::StartNew()
    $response = Invoke-RestMethod -Headers $headers -Uri "$Endpoint/chat/completions" -Method Post -ContentType "application/json" -Body $body
    $timer.Stop()
    Write-Output "elapsed_seconds=$([math]::Round($timer.Elapsed.TotalSeconds, 3))"
    Write-Output "answer=$($response.choices[0].message.content)"
    return
}

Push-Location -LiteralPath $Script:RepoRoot
try {
    $python = Get-LocalRagPython
    & $python eval/eval_model_quality.py `
        --profile $Profile `
        --model-id $modelId `
        --endpoint $Endpoint `
        --model-manifest $Manifest `
        --dataset data/evaluation/gold/generation_eval_set.json `
        --out-dir results/model_quality
    if ($LASTEXITCODE -ne 0) { throw "Model quality evaluation failed with code $LASTEXITCODE" }
}
finally {
    Pop-Location
}
