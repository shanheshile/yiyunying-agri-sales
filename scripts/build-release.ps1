[CmdletBinding()]
param([string]$OutputRoot)

$ErrorActionPreference = 'Stop'
$root = [System.IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
if ([string]::IsNullOrWhiteSpace($OutputRoot)) { $OutputRoot = Join-Path $root 'release' }
$output = [System.IO.Path]::GetFullPath($OutputRoot)
if (-not $output.StartsWith($root + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Release output must remain inside the project root: $output"
}

$python = if ($env:CODEX_PYTHON) { $env:CODEX_PYTHON } else { 'python' }
& $python (Join-Path $PSScriptRoot 'validate_suite.py') --root $root --public
if ($LASTEXITCODE -ne 0) { throw 'Suite validation failed.' }
& $python -m unittest discover -s (Join-Path $root 'tests') -p 'test_*.py'
if ($LASTEXITCODE -ne 0) { throw 'Tests failed.' }

if (Test-Path -LiteralPath $output) { Remove-Item -LiteralPath $output -Recurse -Force }
New-Item -ItemType Directory -Force -Path $output | Out-Null
$version = (Get-Content -Raw -Encoding UTF8 (Join-Path $root 'VERSION')).Trim()
$stage = Join-Path $output 'stage\yiyunying-agri-sales'
New-Item -ItemType Directory -Force -Path $stage | Out-Null

$exclude = @('.git', 'release', 'dist', 'runtime', '__pycache__')
Get-ChildItem -LiteralPath $root -Force | Where-Object { $_.Name -notin $exclude } | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination $stage -Recurse
}

$zip = Join-Path $output "yiyunying-agri-sales-$version.zip"
Compress-Archive -LiteralPath $stage -DestinationPath $zip -CompressionLevel Optimal
$hash = Get-FileHash -Algorithm SHA256 -LiteralPath $zip
"$($hash.Hash)  $([System.IO.Path]::GetFileName($zip))" | Set-Content -Encoding UTF8 (Join-Path $output 'SHA256SUMS.txt')
Write-Host "Built $zip"
