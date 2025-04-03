function Confirm-Or-Exit {
    param (
        [string]$Message = "Do you want to continue?",
        [string]$Title = "Confirmation Required",
        [ValidateSet(0, 1)]
        [int]$DefaultChoice = 1  # 0 = Yes, 1 = No
    )

    $choice = $Host.UI.PromptForChoice(
        $Title,
        $Message,
        @("&Yes", "&No"),
        $DefaultChoice
    )

    if ($choice -ne 0) {
        Write-Host "❌ Aborted." -ForegroundColor Red
        exit 1
    }
}
