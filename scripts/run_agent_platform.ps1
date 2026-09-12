[CmdletBinding()]
param(
    [int]$Port = 8010,
    [string]$Host = "127.0.0.1"
)
$ErrorActionPreference = "Stop"
$root = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
Push-Location $root
try {
    python -m uvicorn agent_platform.api.app:app --host $Host --port $Port
    if ($LASTEXITCODE -ne 0) { throw "agent platform exited with code $LASTEXITCODE" }
} finally { Pop-Location }
