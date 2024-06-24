# Python Book Creation tools

Tools I use for writing Python books.

##### [Repository](https://github.com/BruceEckel/pybooktools)

**NOTE:** This repository is under development so
everything might not be working as described here.


<hr style="height:3px;border-width:0;color:gray;background-color:gray; margin-top:50px;">

## Installation

- If you are only using `validate_output.py` you do not need
  to `pip` install this package, but just include it in your project.

- If you install the package using:  
      ```
      pip install git+https://github.com/BruceEckel/pybooktools.git
      ```    
  You will get the command-line shortcuts shown in the subsections below.

- If you clone the repository, you can install it by moving to the root
  directory of the repository and using:  
      ```
      pip install -e .
      ```    
  The `-e` is optional but it makes the installation editable. Without the `-e` you
  can make changes to the code but these will not be reflected in the running installation.

<hr style="height:3px;border-width:0;color:gray;background-color:gray; margin-top:50px;">

## Slug Line

> Shortcut: **slug**

The "Slug Line" (a term from journalism) not only tells the reader which file
this is, it also enables `update_markdown_code_listings.py` to update the
code listing in the book from the source file.

Automatically adds the commented file name at the top of each Python file,
in the form:

```text
#: file_name.py
```

1. If the slug line does not exist, it is added.
2. If it exists and is incorrect, it is corrected.
3. If it exists and is correct, no changes are made.

Changes are reported by the program.

Run `python slug_line.py -h` for details on how to use it.


<hr style="height:3px;border-width:0;color:gray;background-color:gray; margin-top:50px;">

## Validate Output

This tool allows you to include console output in your examples, and
to ensure the output is correct when the program runs. To use, include
this import in your example:

```python
from validate_output import console
```

Then, at any point in your example you can add this:

```python
console == """
output string
"""
```

The output string will be checked against the actual console output when
the program runs.

You may use multiple `console ==` expressions throughout your example.

You can also insert empty `console == """"""` expressions and use
`update_console_output.py` to initialize the outputs.


<hr style="height:3px;border-width:0;color:gray;background-color:gray; margin-top:50px;">

## Update Console Output

> Shortcut: **upcon**

Updates or clears 'console ==' output sections in Python examples that use
`validate_output`. When updating, produces the actual output from the example since
the last `console ==` and inserts it, so that the output is correct and the example
will run successfully without reporting any errors in the `console ==` output.

Run `python update_console_output.py -h` for details on how to use it.

**Note**: This works only on the Python files, and not
the examples embedded in Markdown documents. To update those after
you've run this program, use:
`update_markdown_code_listings.py`.

<hr style="height:3px;border-width:0;color:gray;background-color:gray; margin-top:50px;">

## Update Markdown Code Listings

> Shortcut: **uplist**

Looks in Markdown files for listings with sluglines (listings without sluglines are ignored),
and updates those listings from the source code repository.
You must provide the path to at least one source code repository,
as a Markdown comment in the form:  
```
<!-- #[code_location] ./src/functional_error_handling -->
```
- The above is a relative path; You can also use absolute paths
- These can appear anywhere in the file.
- The program searches across all the specified directories for the file name in the slugline.
- If you provide more than one source code repository, the program ensures
  there are no duplicate file names across those directories. 

Run `python update_markdown_code_listings.py -h` for details on how to use it.

<hr style="height:3px;border-width:0;color:gray;background-color:gray; margin-top:50px;">

## Recommended Usage

The easiest way to use these tools is to incorporate them in either
your automated build or in a script that you run whenever you need to
update. For example:

```bat
@REM refresh.bat
@REM From original https://github.com/BruceEckel/functional_error_handling
@REM Doesn't work here, only for reference.
cd .\src\functional_error_handling\
rye test
upcon *
rye test
cd ..\..
uplist ".\Slides2.md"
uplist ".\Slides.md"
uplist ".\Functional Error Handling.md"
```
