# Python Book Creation tools

Tools I use for writing Python books.

## Installation

If you are only using `validate_output.py` you do not need
to `pip` install this package, but just include it in your project.

## Slugline

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

## Update Console Output

## Update Markdown Code Listings
