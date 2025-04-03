# RunAllPythonExamples.ps1
# Recursively executes all Python files in the given directory 
# (or current directory if none specified).
# Stops immediately if any script fails.

param (
    [string]$TargetDir = "."
)

$ErrorActionPreference = 'Stop'

# Resolve full path
$root = Resolve-Path $TargetDir
Write-Host "🔍 Searching for Python files in: $root"

# Get all .py files recursively, excluding hidden or virtual env directories
$pythonFiles = Get-ChildItem -Path $root -Recurse -File -Filter *.py |
Where-Object { -not ($_.FullName -match '\\(\.venv|__pycache__|\.git)\\') }

if (-not $pythonFiles) {
    Write-Host "❗ No Python files found."
    exit 1
}

# Group files by directory
$groupedByDir = $pythonFiles | Group-Object DirectoryName

foreach ($group in $groupedByDir) {
    $dir = $group.Name
    Write-Host "`n📂 Entering directory: $dir"
    
    Push-Location $dir
    try {
        foreach ($file in $group.Group) {
            Write-Host "▶️ Running: $($file.Name)"
            python $file.Name
        }
    }
    catch {
        Write-Host "`n❌ Error running script: $($file.Name)"
        Write-Host "   $_"
        Pop-Location
        exit 1
    }
    Pop-Location
}

Write-Host "`n✅ All scripts ran successfully."
