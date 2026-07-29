[CmdletBinding()]
param(
    [ValidateRange(1, 65535)]
    [int]$Port = 8001,

    [ValidateSet("e6_1_adapter_bf16")]
    [string]$Profile = "e6_1_adapter_bf16"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")

Push-Location -LiteralPath $RepoRoot
try {
    python -m model_serving.main `
        --profiles config/model_serving_profiles.example.json `
        --profile $Profile `
        --host 127.0.0.1 `
        --port $Port `
        --active-limit 1 `
        --waiting-limit 4 `
        --workers 1
    if ($LASTEXITCODE -ne 0) {
        throw "Transformers model service exited with code $LASTEXITCODE"
    }
}
finally {
    Pop-Location
}
