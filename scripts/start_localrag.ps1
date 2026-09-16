[CmdletBinding()]
param([int]$ApiPort = 8000, [int]$WebPort = 5173)
$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$python = if ($env:LOCALRAG_PYTHON) { $env:LOCALRAG_PYTHON } else { "D:\Programs\Anaconda\python.exe" }
if (-not (Test-Path $python)) { $python = "python" }
$runtimeDirectory = Join-Path $root "results\runtime"
New-Item -ItemType Directory -Force -Path $runtimeDirectory | Out-Null
$databaseUrl = if ($env:LOCALRAG_DATABASE_URL) {
  $env:LOCALRAG_DATABASE_URL
} else {
  "sqlite:///" + ((Join-Path $runtimeDirectory "localrag.db") -replace "\\", "/")
}
$previousDatabaseUrl = $env:LOCALRAG_DATABASE_URL
$previousSyntheticDns = $env:LOCALRAG_ALLOW_SYNTHETIC_DNS
$env:LOCALRAG_DATABASE_URL = $databaseUrl
if ($env:LOCALRAG_ENV -notin @("prod", "production") -and -not $env:LOCALRAG_ALLOW_SYNTHETIC_DNS) {
  # Some local DNS/proxy setups map public provider domains to RFC 2544's
  # benchmark range. This opt-in only affects development discovery; the API
  # still rejects explicitly entered private/local addresses.
  $env:LOCALRAG_ALLOW_SYNTHETIC_DNS = "1"
}
try {
  $api = Start-Process -FilePath $python -ArgumentList "-m","uvicorn","agent_platform.api.app:app","--host","127.0.0.1","--port",$ApiPort -WorkingDirectory $root -PassThru -WindowStyle Hidden
} finally {
  $env:LOCALRAG_DATABASE_URL = $previousDatabaseUrl
  $env:LOCALRAG_ALLOW_SYNTHETIC_DNS = $previousSyntheticDns
}
$web = Start-Process -FilePath "npm.cmd" -ArgumentList "run","dev","--","--host","127.0.0.1","--port",$WebPort -WorkingDirectory (Join-Path $root "frontend") -PassThru -WindowStyle Hidden
Set-Content -LiteralPath (Join-Path $root ".localrag-api.pid") -Value $api.Id
Set-Content -LiteralPath (Join-Path $root ".localrag-web.pid") -Value $web.Id
Write-Output "LocalRAG started: http://127.0.0.1:$WebPort (API $ApiPort, durable database configured)"
