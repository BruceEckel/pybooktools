# BlankInitFiles.ps1
<#
.SYNOPSIS
    Replaces all __init__.py files in a directory tree with blank versions.

.DESCRIPTION
    Recursively searches from the current directory (or specified path)
    for all __init__.py files and overwrites them with empty files.

.PARAMETER Path
    The root directory to search in. Defaults to the current directory.
#>

param (
    [string]$Path = "."
)

Get-ChildItem -Path $Path -Recurse -Filter "__init__.py" | ForEach-Object {
    "" | Set-Content -Path $_.FullName -Encoding UTF8
    Write-Host "Cleared: $($_.FullName)"
}
