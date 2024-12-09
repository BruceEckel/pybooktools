A top-level `print()` statement is one that is not inside a function or method; thus it is not indented.
The goal of this program is for each top-level `print()` statement in a Python example script to be followed by 
the output of that `print()`.
The output will be in the form of "Output Comment Lines" (OCLs) that each start with `#| `.

I'd like a program that takes the example Python script (as an argument on the command line using argparse)
and saves a modified version of that script.
When the modified version is executed, it generates a new version of the original script with OCLs.
