$ErrorActionPreference = "Stop"
$Script:RepoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "../.."))

function Get-LocalRagPython {
    $venvPython = Join-Path $Script:RepoRoot ".venv/Scripts/python.exe"
    if (Test-Path -LiteralPath $venvPython -PathType Leaf) {
        return $venvPython
    }
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($null -eq $python) {
        throw "Python was not found. Install Python 3.11 or 3.12 and run 01-check-environment.ps1 again."
    }
    return $python.Source
}

function Resolve-RepoPath([string]$Path) {
    $full = [System.IO.Path]::GetFullPath((Join-Path $Script:RepoRoot $Path))
    if (-not $full.StartsWith($Script:RepoRoot + [System.IO.Path]::DirectorySeparatorChar)) {
        throw "Path must stay inside the repository: $Path"
    }
    return $full
}

function Invoke-LocalRagPython {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments)
    $python = Get-LocalRagPython
    Push-Location -LiteralPath $Script:RepoRoot
    try {
        & $python @Arguments
        if ($LASTEXITCODE -ne 0) {
            throw "Python exited with code $LASTEXITCODE"
        }
    }
    finally {
        Pop-Location
    }
}

function Import-UserEnvironmentVariable([string]$Name) {
    if (-not [Environment]::GetEnvironmentVariable($Name, "Process")) {
        $value = [Environment]::GetEnvironmentVariable($Name, "User")
        if ($value) {
            [Environment]::SetEnvironmentVariable($Name, $value, "Process")
        }
    }
}

function Get-RuntimeSecretNames([string]$RuntimeConfigPath) {
    $config = Get-Content -LiteralPath $RuntimeConfigPath -Raw | ConvertFrom-Json
    $names = [System.Collections.Generic.HashSet[string]]::new()
    foreach ($role in @("planner", "rag", "summary")) {
        [void]$names.Add([string]$config.roles.$role.cloud.api_key_env)
        [void]$names.Add([string]$config.roles.$role.local.api_token_env)
    }
    if ($config.embedding.api_key_env) {
        [void]$names.Add([string]$config.embedding.api_key_env)
    }
    return @($names | Where-Object { $_ })
}

function Get-LlamaFactoryCli {
    $venvCli = Join-Path $Script:RepoRoot ".venv/Scripts/llamafactory-cli.exe"
    if (Test-Path -LiteralPath $venvCli -PathType Leaf) {
        return $venvCli
    }
    $command = Get-Command llamafactory-cli -ErrorAction SilentlyContinue
    if ($null -eq $command) {
        throw "LLaMA-Factory is not installed. Run 04-train-qlora.ps1 -InstallLlamaFactory -CheckOnly first."
    }
    return $command.Source
}
