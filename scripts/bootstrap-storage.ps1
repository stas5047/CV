$ErrorActionPreference = "Stop"

$root = Join-Path (Split-Path -Parent $PSScriptRoot) "storage"
$folders = @("uploads", "results", "reports", "models", "temp", "datasets")

foreach ($folder in $folders) {
    $path = Join-Path $root $folder
    New-Item -ItemType Directory -Force -Path $path | Out-Null
}

Write-Output "Storage folders ready under $root"

