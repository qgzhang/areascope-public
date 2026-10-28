$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

# Activate AreaScope's Python environment.
& "$PSScriptRoot\.venv\Scripts\Activate.ps1"

# Windows/PostGIS installs a global PROJ path.
# That PROJ database is incompatible with Rasterio's
# bundled PROJ library, so AreaScope's Python process
# must not inherit it.
Remove-Item Env:PROJ_LIB `
    -ErrorAction SilentlyContinue

Remove-Item Env:PROJ_DATA `
    -ErrorAction SilentlyContinue


Write-Host ""
Write-Host "AreaScope backend environment"
Write-Host "-----------------------------"

Write-Host "Python:"
python --version

Write-Host ""

Write-Host "Rasterio PROJ data:"
rio env --proj-data

Write-Host ""

Write-Host "Starting FastAPI..."
Write-Host ""

fastapi dev main.py