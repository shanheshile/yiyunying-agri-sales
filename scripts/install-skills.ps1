[CmdletBinding()]
param([string]$CodexHome)

$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($CodexHome)) {
    $CodexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }
}
$root = Split-Path -Parent $PSScriptRoot
$sourceRoot = Join-Path $root 'skills'
$destinationRoot = Join-Path ([System.IO.Path]::GetFullPath($CodexHome)) 'skills'
$backupRoot = Join-Path ([System.IO.Path]::GetFullPath($CodexHome)) ("skill-backups\yiyunying-agri-sales-" + (Get-Date -Format 'yyyyMMdd-HHmmss'))

New-Item -ItemType Directory -Force -Path $destinationRoot | Out-Null
foreach ($source in Get-ChildItem -LiteralPath $sourceRoot -Directory) {
    $destination = Join-Path $destinationRoot $source.Name
    if (Test-Path -LiteralPath $destination) {
        New-Item -ItemType Directory -Force -Path $backupRoot | Out-Null
        Copy-Item -LiteralPath $destination -Destination $backupRoot -Recurse
        Remove-Item -LiteralPath $destination -Recurse -Force
    }
    Copy-Item -LiteralPath $source.FullName -Destination $destination -Recurse
    Write-Host "Installed $($source.Name)"
}
if (Test-Path -LiteralPath $backupRoot) { Write-Host "Backups: $backupRoot" }

