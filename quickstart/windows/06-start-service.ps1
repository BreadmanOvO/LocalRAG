[CmdletBinding()]
param(
    [ValidateSet("e6_1_adapter_bf16", "full_sft_adapter_bf16")]
    [string]$Profile = "e6_1_adapter_bf16",
    [ValidateRange(1, 65535)]
    [int]$Port = 8001,
    [switch]$CheckOnly,
    [switch]$KeepRuntimeModel
)

. (Join-Path $PSScriptRoot "_common.ps1")
$python = Get-LocalRagPython
$runtimePath = Resolve-RepoPath "config/runtime_models.json"
foreach ($name in Get-RuntimeSecretNames $runtimePath) {
    Import-UserEnvironmentVariable $name
}

if ($Profile -eq "full_sft_adapter_bf16") {
    $profiles = Resolve-RepoPath "config/model_serving_profiles.quickstart.example.json"
    $manifest = Resolve-RepoPath "model_deployment/manifests/full_sft_input_manifest.json"
    $modelId = "localrag-qwen3-4b-full-sft"
    $plannerToolCallingVerified = $false
    $adapter = Resolve-RepoPath "saves/Qwen3-4B-Thinking/lora/localrag_sft_full_qlora"
    if (-not $CheckOnly -and -not (Test-Path -LiteralPath $manifest)) {
        Push-Location -LiteralPath $Script:RepoRoot
        try {
            & $python -m model_deployment.manifest `
                --repo-root . `
                --out model_deployment/manifests/full_sft_input_manifest.json `
                --base-model models/Qwen3-4B `
                --adapter saves/Qwen3-4B-Thinking/lora/localrag_sft_full_qlora `
                --model-id $modelId
            if ($LASTEXITCODE -ne 0) { throw "Model manifest creation failed" }
        }
        finally { Pop-Location }
    }
}
else {
    $profiles = Resolve-RepoPath "config/model_serving_profiles.example.json"
    $manifest = Resolve-RepoPath "model_deployment/manifests/e6_1_input_manifest.json"
    $modelId = "localrag-qwen3-4b-e6.1"
    $plannerToolCallingVerified = $true
    $adapter = Resolve-RepoPath "saves/Qwen3-4B-Thinking/lora/localrag_sft_e6_1_qlora_webui"
}

$adapterReady = (Test-Path -LiteralPath (Join-Path $adapter "adapter_model.safetensors")) -and
    (Test-Path -LiteralPath (Join-Path $adapter "chat_template.jinja"))
Write-Output "profile=$Profile"
Write-Output "model_id=$modelId"
Write-Output "planner_tool_calling_verified=$plannerToolCallingVerified"
Write-Output "adapter=$adapter"
Write-Output "adapter_ready=$adapterReady"
Write-Output "manifest=$manifest"
Write-Output "port=$Port"
if (-not $adapterReady) { throw "Adapter files are incomplete" }
if (-not (Test-Path -LiteralPath $manifest) -and $CheckOnly) {
    throw "Manifest is missing. Run this script once without -CheckOnly to create the full-SFT manifest."
}
if ($CheckOnly) { return }

if (-not $KeepRuntimeModel) {
    $runtime = Get-Content -LiteralPath $runtimePath -Raw | ConvertFrom-Json
    foreach ($role in @("planner", "rag", "summary")) {
        $runtime.roles.$role.local.model = $modelId
        $runtime.roles.$role.local.base_url = "http://127.0.0.1:$Port/v1"
        if ($role -eq "planner") {
            $runtime.roles.$role.local.tool_calling_verified = $plannerToolCallingVerified
        }
    }
    $json = $runtime | ConvertTo-Json -Depth 12
    [IO.File]::WriteAllText($runtimePath, $json + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))
}

Push-Location -LiteralPath $Script:RepoRoot
try {
    & $python -m model_serving.main `
        --profiles $profiles `
        --profile $Profile `
        --host 127.0.0.1 `
        --port $Port `
        --active-limit 1 `
        --waiting-limit 4 `
        --workers 1
    if ($LASTEXITCODE -ne 0) { throw "Model service exited with code $LASTEXITCODE" }
}
finally {
    Pop-Location
}
