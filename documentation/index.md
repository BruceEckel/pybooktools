# Python Book Creation tools

**NOTE:** This repository is under development so
everything might not be working as described here.

Tools I use for writing Python books.

## Installation

If you are only using `validate_output.py` you do not need
to `pip` install this package, but just include it in your project.

If you install the package using `pip install git+https://github.com/BruceEckel/pybooktools.git
`, you will get the command-line shortcuts shown in the subsections below:

## Slugline

> Shortcut: **slugline**

The "Slug Line" (a term from journalism) not only tells the reader which file
this is, it also enables `update_markdown_code_listings.py` to update the
code listing in the book from the source file.

Automatically adds the commented file name at the top of each Python file,
in the form:
```text
#: file_name.py
```
1. If the slug line does not exist it is added.
2. If it exists and is incorrect it is corrected.
3. If it exists and is correct, no changes are made.

Changes are reported by the program.

Run `python slug_line.py -h` for details on how to use it.

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

## Update Console Output

> Shortcut: **upcon**

Updates or clears 'console ==' output sections in Python examples that use
`validate_output`. When updating, produces the actual output from the example since
the last `console ==` and inserts it, so that the output is correct and the example
will run successfully without reporting any errors in the `console ==` output.

Run `python update_console_output.py -h` for details on how to use it.

## Update Markdown Code Listings

> Shortcut: **uplist**

Looks in Markdown files for listings with sluglines (those without are ignored),
and updates those listings from the source code repository.
You must provide the path to at least one source code repository,
as a Markdown comment in the form:
<!-- #[code_location] ./src/functional_error_handling -->
These can appear anywhere in the file.
If you provide more than one source code repository, you must ensure
there are no duplicate file names across those directories, as the program
searches across all of them for the file name in the slugline and
chooses the first one it encounters.

Run `python update_markdown_code_listings.py -h` for details on how to use it.

{{ Possible addition: report duplicate names }}

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
python  .\update_output.py *
rye test
cd ..\..
python .\update_markdown_code_listings.py ".\Slides2.md"
python .\update_markdown_code_listings.py ".\Slides.md"
python .\update_markdown_code_listings.py ".\Functional Error Handling.md"
```
