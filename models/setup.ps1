# Create junctions from models/ to HuggingFace cache.
# Run from repo root: .\models\setup.ps1

$hfCache = "$env:USERPROFILE\.cache\huggingface\hub"
$modelsDir = "$PSScriptRoot"

$bgeM3Snap = Get-ChildItem "$hfCache\models--BAAI--bge-m3\snapshots" |
    Sort-Object LastWriteTime -Descending |
    Where-Object { Test-Path "$($_.FullName)\config.json" } |
    Select-Object -First 1

$bgeRerankerSnap = Get-ChildItem "$hfCache\models--BAAI--bge-reranker-base\snapshots" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

if (-not $bgeM3Snap) {
    Write-Error "BGE-M3 model not found in HuggingFace cache. Run: huggingface-cli download BAAI/bge-m3"
    exit 1
}
if (-not $bgeRerankerSnap) {
    Write-Error "BGE-Reranker model not found in HuggingFace cache. Run: huggingface-cli download BAAI/bge-reranker-base"
    exit 1
}

foreach ($link in @(
    @{ Name = "bge-m3"; Target = $bgeM3Snap.FullName },
    @{ Name = "bge-reranker-base"; Target = $bgeRerankerSnap.FullName }
)) {
    $path = Join-Path $modelsDir $link.Name
    if (Test-Path $path) {
        Write-Host "Skipping $($link.Name): already exists" -ForegroundColor Yellow
    } else {
        New-Item -ItemType Junction -Path $path -Target $link.Target | Out-Null
        Write-Host "Created junction: $($link.Name) -> $($link.Target)" -ForegroundColor Green
    }
}
