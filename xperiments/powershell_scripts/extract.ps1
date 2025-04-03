# extract.ps1
. C:\git\ThinkingInTypes_Examples\Confirm-Or-Exit.ps1
$directory = "C:\git\ThinkingInTypes_Examples"
$chaptersDir = "C:\git\ThinkingInTypes.github.io\Chapters"

mdvalid -d $chaptersDir
Write-Host "WARNING: You are about to delete the examples in: $directory"
$response = Read-Host "Are you sure? Type 'y' to continue"

if ($response -eq 'y') {
Remove the directory
if (Test-Path $directory) {
    repoclean -a $directory
}
else {
    Write-Host "Directory does not exist: $directory"
}

# Run mdextract
mdextract -d $chaptersDir $directory
}
else {
    Write-Host "Operation canceled."
}
