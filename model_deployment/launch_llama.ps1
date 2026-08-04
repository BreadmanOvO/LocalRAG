[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = "Medium")]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("ValidationF16", "ReleaseQ4")]
    [string]$Mode,

    [Parameter(Mandatory = $true)][string]$Model,
    [Parameter(Mandatory = $true)][string]$Manifest,
    [ValidateRange(1, 65535)][int]$InternalPort = 18002,
    [ValidateRange(1, 65535)][int]$Port = 8002,
    [string]$ToolRoot = "tools/llama.cpp"
)

$ErrorActionPreference = "Stop"
$RepoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$ModelFull = (Resolve-Path -LiteralPath (Join-Path $RepoRoot $Model)).Path
$ManifestFull = (Resolve-Path -LiteralPath (Join-Path $RepoRoot $Manifest)).Path
$ManifestPayload = Get-Content -LiteralPath $ManifestFull -Raw | ConvertFrom-Json
$ToolVersion = $ManifestPayload.metadata.tool.version
if ([string]::IsNullOrWhiteSpace($ToolVersion)) {
    throw "manifest does not contain a llama.cpp tool version"
}
$ExpectedKind = if ($Mode -eq "ValidationF16") { "model-gguf-f16" } else { "model-gguf-q4-k-m" }
if ($ManifestPayload.kind -ne $ExpectedKind) {
    throw "manifest kind does not match launch mode"
}
$ManifestModel = [System.IO.Path]::GetFullPath((Join-Path $RepoRoot $ManifestPayload.metadata.model_identity.artifact_path))
if ($ManifestModel -ne $ModelFull) {
    throw "model path does not match manifest"
}
$Server = (Resolve-Path -LiteralPath (Join-Path $RepoRoot "$ToolRoot/$ToolVersion/bin/llama-server.exe")).Path

Push-Location -LiteralPath $RepoRoot
try {
    python -m model_deployment.manifest --repo-root . --verify $Manifest
    if ($LASTEXITCODE -ne 0) {
        throw "model manifest verification exited with code $LASTEXITCODE"
    }
    & $Server --version
    if ($LASTEXITCODE -ne 0) {
        throw "llama-server --version exited with code $LASTEXITCODE"
    }
    $ServerArgs = @(
        "--model", $ModelFull,
        "--alias", "localrag-qwen3-4b-e6.1",
        "--host", "127.0.0.1",
        "--port", $InternalPort.ToString(),
        "--ctx-size", "40960",
        "--jinja",
        "--chat-template-kwargs", '{"enable_thinking":false}',
        "--parallel", "1",
        "--n-gpu-layers", "999",
        "--temp", "0"
    )
    if (-not $PSCmdlet.ShouldProcess($ModelFull, "Launch llama.cpp mode $Mode")) {
        Write-Output "what_if=true"
        Write-Output "mode=$Mode"
        Write-Output "internal_url=http://127.0.0.1:$InternalPort/v1"
        if ($Mode -eq "ReleaseQ4") {
            Write-Output "external_url=http://127.0.0.1:$Port/v1"
        }
        return
    }
    if ($Mode -eq "ValidationF16") {
        & $Server @ServerArgs
        if ($LASTEXITCODE -ne 0) {
            throw "llama-server exited with code $LASTEXITCODE"
        }
        return
    }

    $LogRoot = Join-Path $RepoRoot "results/model_serving/llama-cpp"
    New-Item -ItemType Directory -Force -Path $LogRoot | Out-Null
    $Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $Stdout = Join-Path $LogRoot "llama-$Stamp.stdout.log"
    $Stderr = Join-Path $LogRoot "llama-$Stamp.stderr.log"
    $Internal = Start-Process -FilePath $Server -ArgumentList $ServerArgs -PassThru -WindowStyle Hidden -RedirectStandardOutput $Stdout -RedirectStandardError $Stderr
    try {
        $Ready = $false
        for ($Attempt = 0; $Attempt -lt 180; $Attempt++) {
            Start-Sleep -Seconds 1
            if ($Internal.HasExited) {
                throw "llama-server exited before readiness"
            }
            try {
                $Models = Invoke-RestMethod -Uri "http://127.0.0.1:$InternalPort/v1/models" -TimeoutSec 2
                if ($Models.data.id -contains "localrag-qwen3-4b-e6.1") {
                    $Ready = $true
                    break
                }
            }
            catch {
            }
        }
        if (-not $Ready) {
            throw "llama-server did not become ready"
        }
        python -m model_serving.main --profiles config/model_serving_profiles.example.json --profile e6_1_q4_k_m --host 127.0.0.1 --port $Port --active-limit 1 --waiting-limit 4 --workers 1 --llama-base-url "http://127.0.0.1:$InternalPort/v1"
        if ($LASTEXITCODE -ne 0) {
            throw "LocalRAG Q4 service exited with code $LASTEXITCODE"
        }
    }
    finally {
        if (-not $Internal.HasExited) {
            Stop-Process -Id $Internal.Id -Force
            $Internal.WaitForExit()
        }
    }
}
finally {
    Pop-Location
}
