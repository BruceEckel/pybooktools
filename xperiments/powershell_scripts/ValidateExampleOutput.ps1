# ValidateExampleOutput.ps1
# Runs Python examples and compares actual output with ## comments (ignoring whitespace).
# Uses parallel threads and supports uv/venv Python activation.

param (
    [string]$TargetDir = ".",
    [int]$ThrottleLimit = 4
)

if ($PSVersionTable.PSVersion.Major -lt 7) {
    Write-Host "❌ This script requires PowerShell 7 or higher." -ForegroundColor Red
    exit 1
}

# Use currently activated Python interpreter
$pythonPath = & python -c "import sys; print(sys.executable)"
$pythonPath = $pythonPath.Trim()

if (-not (Test-Path $pythonPath)) {
    Write-Host "❌ Could not detect active Python interpreter: $pythonPath" -ForegroundColor Red
    exit 1
}

Write-Host "🐍 Using interpreter: $pythonPath" -ForegroundColor Green

$ErrorActionPreference = 'Stop'
$root = Resolve-Path $TargetDir
Write-Host "🔍 Validating Python examples in: $root" -ForegroundColor Yellow

$pythonFiles = Get-ChildItem -Path $root -Recurse -File -Filter *.py |
Where-Object {
    $_.FullName -notmatch '\\(venv|\.venv|__pycache__|\.git|python)\\' -and
    $_.Name -ne '__init__.py'
}

if (-not $pythonFiles) {
    Write-Host "❗ No Python files found." -ForegroundColor Red
    exit 1
}

Write-Host "🧪 Comparing output for $($pythonFiles.Count) examples (ThrottleLimit = $ThrottleLimit)" -ForegroundColor Green

$discrepancies = [System.Collections.Concurrent.ConcurrentBag[string]]::new()
$jobs = @()
$semaphore = [System.Threading.SemaphoreSlim]::new($ThrottleLimit, $ThrottleLimit)

foreach ($file in $pythonFiles) {
    $null = $semaphore.WaitAsync()

    $jobs += Start-ThreadJob -ScriptBlock {
        param($path, $sema, $interpreter)

        $timestamp = Get-Date -Format 'HH:mm:ss'
        Write-Host "$timestamp ▶️ Checking: $path" -ForegroundColor Cyan

        # Read expected output from ## comments
        $rawLines = Get-Content -Path $path -Encoding UTF8
        $expectedParts = @()
        foreach ($line in $rawLines) {
            if ($line -match '^## (.*)$') {
                $expectedParts += $matches[1]
            }
        }
        $expectedString = ($expectedParts -join "`n")

        # Run the script
        $psi = New-Object System.Diagnostics.ProcessStartInfo
        $psi.FileName = $interpreter
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
            return @{
                Path  = $path
                Error = "Script failed to run:`n$stderr"
            }
        }

        $actualStripped = ($stdout -replace '\s+', '')
        $expectedStripped = ($expectedString -replace '\s+', '')

        if (-not $expectedStripped.Contains($actualStripped)) {
            return @{
                Path  = $path
                Error = "Output mismatch.`n--- Expected (## comments) ---`n$expectedString`n--- Actual (stdout) ---`n$stdout"
            }
        }

        return @{ Success = $true }

    } -ArgumentList $file.FullName, $semaphore, $pythonPath
}

foreach ($job in $jobs) {
    $job | Wait-Job
    $results = Receive-Job $job
    $null = $semaphore.Release()

    foreach ($result in $results) {
        if ($result -is [hashtable] -and $result.ContainsKey('Error')) {
            $message = "❌ $($result.Path)`n$($result['Error'])"
            $discrepancies.Add($message)
        }
    }
}

$jobs | Remove-Job -Force

if ($discrepancies.Count -gt 0) {
    Write-Host "`n❗ Discrepancies found in output:" -ForegroundColor Red
    $discrepancies | ForEach-Object { Write-Host $_ -ForegroundColor Red }
    exit 1
}

Write-Host "`n✅ All outputs matched expectations." -ForegroundColor Green
