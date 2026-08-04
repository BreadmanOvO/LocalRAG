[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = "Medium")]
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern("^b[0-9]+$")]
    [string]$Version,

    [Parameter(Mandatory = $true)]
    [ValidatePattern("^https://github\.com/ggml-org/llama\.cpp/")]
    [string]$BinaryAssetUrl,

    [Parameter(Mandatory = $true)]
    [ValidatePattern("^[0-9a-fA-F]{64}$")]
    [string]$BinarySha256,

    [Parameter(Mandatory = $true)]
    [ValidatePattern("^https://github\.com/ggml-org/llama\.cpp/")]
    [string]$CudaRuntimeAssetUrl,

    [Parameter(Mandatory = $true)]
    [ValidatePattern("^[0-9a-fA-F]{64}$")]
    [string]$CudaRuntimeSha256,

    [Parameter(Mandatory = $true)]
    [ValidatePattern("^https://(api|github|codeload)\.github\.com/")]
    [string]$SourceArchiveUrl,

    [Parameter(Mandatory = $true)]
    [ValidatePattern("^[0-9a-fA-F]{64}$")]
    [string]$SourceArchiveSha256,

    [ValidateRange(0, 2147483647)]
    [long]$BinarySize = 0,

    [ValidateRange(0, 2147483647)]
    [long]$CudaRuntimeSize = 0,

    [ValidateRange(0, 2147483647)]
    [long]$SourceArchiveSize = 0,

    [string]$DestinationRoot = "tools/llama.cpp"
)

$ErrorActionPreference = "Stop"
$RepoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$ExpectedRoot = [System.IO.Path]::GetFullPath((Join-Path $RepoRoot "tools/llama.cpp"))
$DestinationRootFull = [System.IO.Path]::GetFullPath((Join-Path $RepoRoot $DestinationRoot))
if ($DestinationRootFull -ne $ExpectedRoot) {
    throw "DestinationRoot must remain tools/llama.cpp"
}
$VersionRoot = [System.IO.Path]::GetFullPath((Join-Path $DestinationRootFull $Version))
if (-not $VersionRoot.StartsWith($DestinationRootFull + [System.IO.Path]::DirectorySeparatorChar)) {
    throw "Version destination escapes tools/llama.cpp"
}
if (Test-Path -LiteralPath $VersionRoot) {
    throw "llama.cpp version destination already exists: $VersionRoot"
}

function Assert-FileHash {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Expected
    )
    $Actual = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($Actual -ne $Expected.ToLowerInvariant()) {
        throw "SHA-256 mismatch for $(Split-Path -Leaf $Path): expected $Expected, got $Actual"
    }
}

function Receive-VerifiedArchive {
    param(
        [Parameter(Mandatory = $true)][string]$Uri,
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Sha256,
        [long]$ExpectedSize = 0
    )
    $Curl = Join-Path $env:SystemRoot "System32/curl.exe"
    if (-not (Test-Path -LiteralPath $Curl)) {
        $Curl = (Get-Command curl.exe -ErrorAction Stop).Source
    }
    $SegmentThresholdBytes = 64MB
    if ($ExpectedSize -le $SegmentThresholdBytes) {
        & $Curl --fail --location --silent --show-error --retry 3 --header "User-Agent: LocalRAG-v1.6-deployment" --output $Path $Uri
        if ($LASTEXITCODE -ne 0) {
            throw "archive download exited with code $LASTEXITCODE"
        }
        if ($ExpectedSize -gt 0 -and (Get-Item -LiteralPath $Path).Length -ne $ExpectedSize) {
            throw "archive size mismatch"
        }
    }
    else {
        $PartRoot = Join-Path (Split-Path -Parent $Path) ((Split-Path -Leaf $Path) + ".parts")
        New-Item -ItemType Directory -Force -Path $PartRoot | Out-Null
        $PartCount = 16
        $PartSize = [math]::Ceiling($ExpectedSize / $PartCount)
        $Processes = @()
        for ($Index = 0; $Index -lt $PartCount; $Index++) {
            $Start = [long]($Index * $PartSize)
            if ($Start -ge $ExpectedSize) { break }
            $End = [math]::Min($ExpectedSize - 1, $Start + $PartSize - 1)
            $PartPath = Join-Path $PartRoot ("part-{0:D2}" -f $Index)
            $Arguments = @(
                "--fail", "--location", "--silent", "--show-error", "--retry", "3",
                "--range", "$Start-$End", "--header", "User-Agent:LocalRAG-v1.6-deployment",
                "--output", $PartPath, $Uri
            )
            $Processes += Start-Process -FilePath $Curl -ArgumentList $Arguments -WindowStyle Hidden -PassThru
        }
        foreach ($Process in $Processes) {
            $Process.WaitForExit()
            if ($Process.ExitCode -ne 0) {
                throw "segmented archive download exited with code $($Process.ExitCode)"
            }
        }
        for ($Index = 0; $Index -lt $PartCount; $Index++) {
            $Start = [long]($Index * $PartSize)
            if ($Start -ge $ExpectedSize) { break }
            $ExpectedPartSize = [long][math]::Min($PartSize, $ExpectedSize - $Start)
            $PartPath = Join-Path $PartRoot ("part-{0:D2}" -f $Index)
            if (-not (Test-Path -LiteralPath $PartPath)) {
                throw "segmented archive part is missing: $Index"
            }
            if ((Get-Item -LiteralPath $PartPath).Length -ne $ExpectedPartSize) {
                throw "segmented archive part size mismatch: $Index"
            }
        }
        $Output = [System.IO.File]::Open($Path, [System.IO.FileMode]::Create, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
        try {
            for ($Index = 0; $Index -lt $PartCount; $Index++) {
                $PartPath = Join-Path $PartRoot ("part-{0:D2}" -f $Index)
                if (-not (Test-Path -LiteralPath $PartPath)) {
                    throw "segmented archive part is missing: $Index"
                }
                $Part = [System.IO.File]::OpenRead($PartPath)
                try { $Part.CopyTo($Output) }
                finally { $Part.Dispose() }
            }
        }
        finally { $Output.Dispose() }
        if ((Get-Item -LiteralPath $Path).Length -ne $ExpectedSize) {
            throw "segmented archive size mismatch"
        }
        Remove-Item -LiteralPath $PartRoot -Recurse -Force
    }
    Assert-FileHash -Path $Path -Expected $Sha256
}

if (-not $PSCmdlet.ShouldProcess($VersionRoot, "Install verified llama.cpp release $Version")) {
    Write-Output "what_if=true"
    Write-Output "install_path=$VersionRoot"
    return
}

New-Item -ItemType Directory -Path $VersionRoot | Out-Null
$VersionRoot = (Resolve-Path -LiteralPath $VersionRoot).Path
$DownloadRoot = Join-Path $VersionRoot "_downloads"
$SourceExtractRoot = Join-Path $VersionRoot "_source_extract"
$BinRoot = Join-Path $VersionRoot "bin"
$SourceRoot = Join-Path $VersionRoot "source"
New-Item -ItemType Directory -Path $DownloadRoot,$SourceExtractRoot,$BinRoot,$SourceRoot | Out-Null

$BinaryArchive = Join-Path $DownloadRoot "llama-bin.zip"
$CudaArchive = Join-Path $DownloadRoot "cudart.zip"
$SourceArchive = Join-Path $DownloadRoot "source.zip"
Receive-VerifiedArchive -Uri $BinaryAssetUrl -Path $BinaryArchive -Sha256 $BinarySha256 -ExpectedSize $BinarySize
Receive-VerifiedArchive -Uri $CudaRuntimeAssetUrl -Path $CudaArchive -Sha256 $CudaRuntimeSha256 -ExpectedSize $CudaRuntimeSize
Receive-VerifiedArchive -Uri $SourceArchiveUrl -Path $SourceArchive -Sha256 $SourceArchiveSha256 -ExpectedSize $SourceArchiveSize

Expand-Archive -LiteralPath $BinaryArchive -DestinationPath $BinRoot -Force
Expand-Archive -LiteralPath $CudaArchive -DestinationPath $BinRoot -Force
Expand-Archive -LiteralPath $SourceArchive -DestinationPath $SourceExtractRoot -Force
$Converter = Get-ChildItem -LiteralPath $SourceExtractRoot -Recurse -File -Filter "convert_hf_to_gguf.py" | Select-Object -First 1
if ($null -eq $Converter) {
    throw "source archive does not contain convert_hf_to_gguf.py"
}
$ArchiveSourceRoot = Split-Path -Parent $Converter.FullName
Get-ChildItem -LiteralPath $ArchiveSourceRoot -Force | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination $SourceRoot -Recurse -Force
}

$Server = Join-Path $BinRoot "llama-server.exe"
$Quantizer = Join-Path $BinRoot "llama-quantize.exe"
$InstalledConverter = Join-Path $SourceRoot "convert_hf_to_gguf.py"
foreach ($Required in @($Server, $Quantizer, $InstalledConverter)) {
    if (-not (Test-Path -LiteralPath $Required -PathType Leaf)) {
        throw "required llama.cpp tool is missing: $Required"
    }
}

& $Server --version
if ($LASTEXITCODE -ne 0) {
    throw "llama-server --version exited with code $LASTEXITCODE"
}

$InstallIdentity = [ordered]@{
    version = $Version
    installed_at = (Get-Date).ToString("o")
    binary = [ordered]@{ url = $BinaryAssetUrl; sha256 = $BinarySha256.ToLowerInvariant() }
    cuda_runtime = [ordered]@{ url = $CudaRuntimeAssetUrl; sha256 = $CudaRuntimeSha256.ToLowerInvariant() }
    source = [ordered]@{ url = $SourceArchiveUrl; sha256 = $SourceArchiveSha256.ToLowerInvariant() }
}
$InstallIdentity | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $VersionRoot "install.json") -Encoding UTF8

foreach ($Cleanup in @($DownloadRoot, $SourceExtractRoot)) {
    $ResolvedCleanup = [System.IO.Path]::GetFullPath($Cleanup)
    if (-not $ResolvedCleanup.StartsWith($VersionRoot + [System.IO.Path]::DirectorySeparatorChar)) {
        throw "cleanup path escapes version destination"
    }
    Remove-Item -LiteralPath $ResolvedCleanup -Recurse -Force
}

Write-Output "version=$Version"
Write-Output "install_path=$VersionRoot"
Write-Output "llama_server=$Server"
Write-Output "llama_quantize=$Quantizer"
Write-Output "converter=$InstalledConverter"
