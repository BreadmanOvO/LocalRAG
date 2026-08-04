[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = "Medium")]
param(
    [Parameter(Mandatory = $true)][string]$InputF16,
    [Parameter(Mandatory = $true)][string]$OutputQ4,
    [Parameter(Mandatory = $true)][ValidatePattern("^b[0-9]+$")][string]$ToolVersion,
    [Parameter(Mandatory = $true)][string]$InputManifest,
    [string]$ToolRoot = "tools/llama.cpp",
    [string]$OutputManifest = "model_deployment/manifests/e6_1_q4_k_m_manifest.json"
)

$ErrorActionPreference = "Stop"
$RepoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$InputF16Full = [System.IO.Path]::GetFullPath((Join-Path $RepoRoot $InputF16))
$InputManifestFull = [System.IO.Path]::GetFullPath((Join-Path $RepoRoot $InputManifest))
$OutputQ4Full = [System.IO.Path]::GetFullPath((Join-Path $RepoRoot $OutputQ4))
$OutputManifestFull = [System.IO.Path]::GetFullPath((Join-Path $RepoRoot $OutputManifest))
$ArtifactsRoot = [System.IO.Path]::GetFullPath((Join-Path $RepoRoot "artifacts/models"))
$ManifestsRoot = [System.IO.Path]::GetFullPath((Join-Path $RepoRoot "model_deployment/manifests"))
if (-not $OutputQ4Full.StartsWith($ArtifactsRoot + [System.IO.Path]::DirectorySeparatorChar)) {
    throw "OutputQ4 must remain inside artifacts/models"
}
if (-not $OutputManifestFull.StartsWith($ManifestsRoot + [System.IO.Path]::DirectorySeparatorChar)) {
    throw "OutputManifest must remain inside model_deployment/manifests"
}
if ((Test-Path -LiteralPath $OutputQ4Full) -or (Test-Path -LiteralPath $OutputManifestFull)) {
    throw "Q4 output or manifest already exists"
}
$InputF16Resolved = Resolve-Path -LiteralPath $InputF16Full
$InputManifestResolved = Resolve-Path -LiteralPath $InputManifestFull
$Quantizer = Resolve-Path -LiteralPath (Join-Path $RepoRoot "$ToolRoot/$ToolVersion/bin/llama-quantize.exe")
$InputPayload = Get-Content -LiteralPath $InputManifestResolved.Path -Raw | ConvertFrom-Json
if ($InputPayload.kind -ne "model-gguf-f16") {
    throw "input manifest is not a GGUF F16 model"
}
$ManifestArtifact = [System.IO.Path]::GetFullPath((Join-Path $RepoRoot $InputPayload.metadata.model_identity.artifact_path))
if ($ManifestArtifact -ne $InputF16Resolved.Path -or $InputPayload.metadata.model_identity.dtype -ne "float16" -or $InputPayload.metadata.model_identity.quantization -ne "none") {
    throw "GGUF F16 path or identity does not match input manifest"
}

Push-Location -LiteralPath $RepoRoot
try {
    python -m model_deployment.manifest --repo-root . --verify $InputManifest
    if ($LASTEXITCODE -ne 0) {
        throw "input manifest verification exited with code $LASTEXITCODE"
    }
    if (-not $PSCmdlet.ShouldProcess($OutputQ4Full, "Quantize GGUF F16 to Q4_K_M")) {
        Write-Output "what_if=true"
        Write-Output "output=$OutputQ4Full"
        return
    }
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $OutputQ4Full) | Out-Null
    $Timer = [System.Diagnostics.Stopwatch]::StartNew()
    & $Quantizer.Path $InputF16Resolved.Path $OutputQ4Full Q4_K_M
    if ($LASTEXITCODE -ne 0) {
        throw "GGUF quantization exited with code $LASTEXITCODE"
    }
    $Timer.Stop()
    if (-not (Test-Path -LiteralPath $OutputQ4Full -PathType Leaf) -or (Get-Item -LiteralPath $OutputQ4Full).Length -lt 1MB) {
        throw "Q4_K_M output is missing or too small"
    }
    python -m model_deployment.manifest --repo-root . --out $OutputManifest --artifact $OutputQ4 --artifact-profile gguf_q4_k_m --input-manifest $InputManifest --tool-version $ToolVersion --elapsed-seconds $Timer.Elapsed.TotalSeconds
    if ($LASTEXITCODE -ne 0) {
        throw "Q4_K_M manifest creation exited with code $LASTEXITCODE"
    }
    Write-Output "tool_version=$ToolVersion"
    Write-Output "format=GGUF"
    Write-Output "quantization=Q4_K_M"
    Write-Output "elapsed_seconds=$([math]::Round($Timer.Elapsed.TotalSeconds, 3))"
    Write-Output "output=$OutputQ4Full"
    Write-Output "manifest=$OutputManifestFull"
}
finally {
    Pop-Location
}
