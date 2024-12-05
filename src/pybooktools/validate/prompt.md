An "output comment line" (abbreviated as OCL) in a Python program has the following properties:

1. It follows a call to show(), a function with the same signature as print(). 
2. Each OCL is indented to the same level as its preceding show() and begins with `#: `
3. There is one OCL for each output line produced by show().
   If the call to show() produces multiple output lines, each line is represented with its own `#: ` output comment line.
4. Each correct OCL contains, after the `#: `, the corresponding output line from the preceding show()

For example, a correct OCL looks like this:  

```python
show("example output")
#: example output
```

There are two ways to correct an OCL

1. If there are no OCLs immediately after the call to show(), the appropriate lines
   are created and added to the Python source file after that particular call to show().

2. If OCLs do exist immediately after the call to show() but they are incorrect,
   then they are replaced by the corrected lines in the Python source file containing the call to show().


Define the `show()` function in show_ocl.py.

Create a program ensure_output.py that uses argparse for the command line. 
The program searches the current directory and recursively into subdirectories.
If you give it a file name on the command line, it will only look for that file.
It looks for Python files that contain calls to show().
For each python file containing show() calls:
1. It locates the first call to show() that isn't followed by correct OCLs.
2. It corrects those OCLs, saves the file, and then restarts the analysis by going back to #1.
3. It repeats this process until all OCLs are correct. 



----
My highest priority is a well-designed, elegant, easy-to-understand and easy-to-modify solution.

Update: Find the first show() that is followed by incorrect or nonexistent OCLs.
Fix the OCLs for only that version of show. 
Then re-run the file, which will be successful until the next incorrect or nonexistent OCLs.
Fix the new case, then repeat until there are no more show()s to correct.
