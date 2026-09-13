[CmdletBinding()]
param(
    [int]$Port = 8000,
    [string]$BindHost = "127.0.0.1"
)
$ErrorActionPreference = "Stop"
$root = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
Push-Location $root
try {
    $pythonCandidates = @()
    if ($env:LOCALRAG_PYTHON) { $pythonCandidates += $env:LOCALRAG_PYTHON }
    $pythonCandidates += (Join-Path $root ".venv\Scripts\python.exe")
    $pythonCandidates += (Join-Path $root ".venv\bin\python")
    if ($env:CONDA_PREFIX) { $pythonCandidates += (Join-Path $env:CONDA_PREFIX "python.exe") }
    if ($env:CONDA_EXE) {
        $condaRoot = Split-Path -Parent (Split-Path -Parent $env:CONDA_EXE)
        $pythonCandidates += (Join-Path $condaRoot "python.exe")
    }
    $pythonCandidates += "python"
    $runtimePython = $null
    foreach ($candidate in $pythonCandidates) {
        try {
            & $candidate -c "import fastapi" *> $null
            if ($LASTEXITCODE -eq 0) { $runtimePython = $candidate; break }
        } catch { }
    }
    if (-not $runtimePython) { throw "FastAPI is unavailable; activate the project environment or set LOCALRAG_PYTHON" }
    & $runtimePython -m uvicorn agent_platform.api.app:app --host $BindHost --port $Port
    if ($LASTEXITCODE -ne 0) { throw "agent platform exited with code $LASTEXITCODE" }
} finally { Pop-Location }
