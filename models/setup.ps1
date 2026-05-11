# Download local models into models/ directory.
# Run from repo root: .\models\setup.ps1

$modelsDir = "$PSScriptRoot"

$models = @(
    @{ Name = "bge-m3"; Repo = "BAAI/bge-m3" },
    @{ Name = "bge-reranker-base"; Repo = "BAAI/bge-reranker-base" }
)

foreach ($m in $models) {
    $path = Join-Path $modelsDir $m.Name
    if (Test-Path "$path\config.json") {
        Write-Host "Skipping $($m.Name): already exists" -ForegroundColor Yellow
    } else {
        Write-Host "Downloading $($m.Repo)..." -ForegroundColor Cyan
        huggingface-cli download $m.Repo --local-dir $path
    }
}
