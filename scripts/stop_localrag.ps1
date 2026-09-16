[CmdletBinding()]
param()
$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
foreach ($name in @(".localrag-api.pid", ".localrag-web.pid")) {
  $path = Join-Path $root $name
  if (Test-Path $path) {
    $pidValue = [int](Get-Content -LiteralPath $path)
    $process = Get-Process -Id $pidValue -ErrorAction SilentlyContinue
    if ($process) { Stop-Process -Id $pidValue -Force }
    Remove-Item -LiteralPath $path -Force
  }
}
Write-Output "LocalRAG stopped"
