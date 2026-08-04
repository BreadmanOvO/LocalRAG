[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = "Medium")]
param(
    [Parameter(Mandatory = $true)][string]$MergedModel,
    [Parameter(Mandatory = $true)][string]$OutputF16,
    [Parameter(Mandatory = $true)][ValidatePattern("^b[0-9]+$")][string]$ToolVersion,
    [Parameter(Mandatory = $true)][string]$InputManifest,
    [string]$ToolRoot = "tools/llama.cpp",
    [string]$OutputManifest = "model_deployment/manifests/e6_1_gguf_f16_manifest.json"
)

$ErrorActionPreference = "Stop"
$RepoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$MergedModelFull = [System.IO.Path]::GetFullPath((Join-Path $RepoRoot $MergedModel))
$InputManifestFull = [System.IO.Path]::GetFullPath((Join-Path $RepoRoot $InputManifest))
$OutputF16Full = [System.IO.Path]::GetFullPath((Join-Path $RepoRoot $OutputF16))
$OutputManifestFull = [System.IO.Path]::GetFullPath((Join-Path $RepoRoot $OutputManifest))
$ArtifactsRoot = [System.IO.Path]::GetFullPath((Join-Path $RepoRoot "artifacts/models"))
$ManifestsRoot = [System.IO.Path]::GetFullPath((Join-Path $RepoRoot "model_deployment/manifests"))
if (-not $OutputF16Full.StartsWith($ArtifactsRoot + [System.IO.Path]::DirectorySeparatorChar)) {
    throw "OutputF16 must remain inside artifacts/models"
}
if (-not $OutputManifestFull.StartsWith($ManifestsRoot + [System.IO.Path]::DirectorySeparatorChar)) {
    throw "OutputManifest must remain inside model_deployment/manifests"
}
if ((Test-Path -LiteralPath $OutputF16Full) -or (Test-Path -LiteralPath $OutputManifestFull)) {
    throw "GGUF F16 output or manifest already exists"
}
$MergedModelResolved = Resolve-Path -LiteralPath $MergedModelFull
$InputManifestResolved = Resolve-Path -LiteralPath $InputManifestFull
$Converter = Resolve-Path -LiteralPath (Join-Path $RepoRoot "$ToolRoot/$ToolVersion/source/convert_hf_to_gguf.py")
$InputPayload = Get-Content -LiteralPath $InputManifestResolved.Path -Raw | ConvertFrom-Json
if ($InputPayload.kind -ne "model-merged-bf16") {
    throw "input manifest is not a merged BF16 model"
}
$ManifestArtifact = [System.IO.Path]::GetFullPath((Join-Path $RepoRoot $InputPayload.metadata.model_identity.artifact_path))
if ($ManifestArtifact -ne $MergedModelResolved.Path -or $InputPayload.metadata.model_identity.dtype -ne "bfloat16" -or $InputPayload.metadata.model_identity.quantization -ne "none") {
    throw "merged model path or identity does not match input manifest"
}

Push-Location -LiteralPath $RepoRoot
try {
    python -m model_deployment.manifest --repo-root . --verify $InputManifest
    if ($LASTEXITCODE -ne 0) {
        throw "input manifest verification exited with code $LASTEXITCODE"
    }
    if (-not $PSCmdlet.ShouldProcess($OutputF16Full, "Convert merged BF16 model to GGUF F16")) {
        Write-Output "what_if=true"
        Write-Output "output=$OutputF16Full"
        return
    }
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $OutputF16Full) | Out-Null
    $Timer = [System.Diagnostics.Stopwatch]::StartNew()
    python $Converter.Path $MergedModelResolved.Path --outfile $OutputF16Full --outtype f16
    if ($LASTEXITCODE -ne 0) {
        throw "GGUF conversion exited with code $LASTEXITCODE"
    }
    $Timer.Stop()
    if (-not (Test-Path -LiteralPath $OutputF16Full -PathType Leaf) -or (Get-Item -LiteralPath $OutputF16Full).Length -lt 1MB) {
        throw "GGUF F16 output is missing or too small"
    }
    python -m model_deployment.manifest --repo-root . --out $OutputManifest --artifact $OutputF16 --artifact-profile gguf_f16 --input-manifest $InputManifest --tool-version $ToolVersion --elapsed-seconds $Timer.Elapsed.TotalSeconds
    if ($LASTEXITCODE -ne 0) {
        throw "GGUF F16 manifest creation exited with code $LASTEXITCODE"
    }
    Write-Output "tool_version=$ToolVersion"
    Write-Output "format=GGUF"
    Write-Output "quantization=F16"
    Write-Output "elapsed_seconds=$([math]::Round($Timer.Elapsed.TotalSeconds, 3))"
    Write-Output "output=$OutputF16Full"
    Write-Output "manifest=$OutputManifestFull"
}
finally {
    Pop-Location
}
