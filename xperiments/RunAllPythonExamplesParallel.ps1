# RunAllPythonExamplesParallel.ps1
# Runs all Python files in a directory tree (or specific subdirectory) in parallel.
# Skips __init__.py files and anything inside venv/.venv directories.
# Colored output, timestamps, and stops all jobs on first failure.

param (
    [string]$TargetDir = ".",
    [int]$ThrottleLimit = [Environment]::ProcessorCount
)

if ($PSVersionTable.PSVersion.Major -lt 7) {
    Write-Host "❌ This script requires PowerShell 7 or higher." -ForegroundColor Red
    exit 1
}

$ErrorActionPreference = 'Stop'
$root = Resolve-Path $TargetDir
Write-Host "🔍 Searching for Python files in: $root" -ForegroundColor Yellow

$pythonFiles = Get-ChildItem -Path $root -Recurse -File -Filter *.py |
Where-Object {
    -not ($_.FullName -match '\\(\.venv|venv|__pycache__|\.git)\\') -and
    $_.Name -ne '__init__.py'
}

if (-not $pythonFiles) {
    Write-Host "❗ No Python files found." -ForegroundColor Red
    exit 1
}

Write-Host "🚀 Running $($pythonFiles.Count) scripts in parallel (ThrottleLimit = $ThrottleLimit)" -ForegroundColor Green

$failures = [System.Collections.Concurrent.ConcurrentBag[string]]::new()
$jobs = @()
$semaphore = [System.Threading.SemaphoreSlim]::new($ThrottleLimit, $ThrottleLimit)

foreach ($file in $pythonFiles) {
    $null = $semaphore.WaitAsync()

    $jobs += Start-ThreadJob -ScriptBlock {
        param($path, $sema)

        $timestamp = Get-Date -Format 'HH:mm:ss'
        Write-Host "$timestamp ▶️ Running: $path" -ForegroundColor Cyan

        $psi = New-Object System.Diagnostics.ProcessStartInfo
        $psi.FileName = "python"
        $psi.Arguments = "`"$path`""
        $psi.RedirectStandardOutput = $true
        $psi.RedirectStandardError = $true
        $psi.UseShellExecute = $false
        $psi.CreateNoWindow = $true

        $process = [System.Diagnostics.Process]::Start($psi)
        $stdout = $process.StandardOutput.ReadToEnd()
        $stderr = $process.StandardError.ReadToEnd()
        $process.WaitForExit()

        if ($process.ExitCode -ne 0) {
            return @{ Success = $false; Path = $path; Error = $stderr }
        }
        else {
            if ($stdout) {
                Write-Host $stdout -ForegroundColor Gray
            }
            return @{ Success = $true }
        }

    } -ArgumentList $file.FullName, $semaphore
}

# Monitor jobs
$failed = $false

foreach ($job in $jobs) {
    $job | Wait-Job

    $result = Receive-Job $job
    $null = $semaphore.Release()

    if (-not $result.Success) {
        $failed = $true
        Write-Host "`n❌ Failed: $($result.Path)`n$result.Error" -ForegroundColor Red

        foreach ($j in $jobs) {
            if ($j.State -eq 'Running') {
                Stop-Job $j | Out-Null
            }
        }
        break
    }
}

$jobs | Remove-Job -Force

if ($failed) {
    Write-Host "`n❌ One or more scripts failed." -ForegroundColor Red
    exit 1
}

Write-Host "`n✅ All scripts ran successfully." -ForegroundColor Green
