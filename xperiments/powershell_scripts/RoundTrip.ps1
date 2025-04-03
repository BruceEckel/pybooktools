# RoundTrip.ps1
. C:\git\ThinkingInTypes_Examples\Confirm-Or-Exit.ps1

& ..\ThinkingInTypes.github.io\extract.ps1

Confirm-Or-Exit "Continue: Run all Python examples?" -DefaultChoice 0
& .\RunAllPythonExamplesParallel.ps1

Confirm-Or-Exit "Continue: Update embedded example outputs with px?" -DefaultChoice 0
Write-Host "Updating embedded example outputs"
& px -r .

Confirm-Or-Exit "Continue: Validate Example output?" -DefaultChoice 0
& .\ValidateExampleOutput.ps1

Confirm-Or-Exit "Continue: Inject Updated Examples Back Into Chapters?"
& ..\ThinkingInTypes.github.io\inject.ps1
