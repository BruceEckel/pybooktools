# install_g_function.ps1 - Script to define the 'g' function in the current session
# To install, use a leading '.':
# . .\install_g_function.ps1

function g {
    Clear-Host
    copy .\test_validate_output.py x_test.py
    python x_test.py
}

# Add the function to the global scope if needed, to persist in the current session.
Set-Item -Path Function:\g -Value $function:g
