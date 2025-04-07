# go.ps1
. C:\git\ThinkingInTypes_Examples\Confirm-Or-Exit.ps1

& ..\ThinkingInTypes.github.io\extract.ps1

Confirm-Or-Exit "Continue?" -DefaultChoice 0
& .\RunAllPythonExamplesParallel.ps1

Confirm-Or-Exit "Continue?" -DefaultChoice 0
Write-Host "Updating embedded example outputs"
& px -r .

Confirm-Or-Exit "Continue?" -DefaultChoice 0
& .\ValidateExampleOutput.ps1
