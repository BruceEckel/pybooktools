# Python Book Creation tools

Tools I use for writing Python books.

##### [Repository](https://github.com/BruceEckel/pybooktools)

<hr style="height:3px;border-width:0;color:gray;background-color:gray; margin-top:50px;">

## Installation

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
  can make changes to the code, but these will not be reflected in the running installation.

<hr style="height:3px;border-width:0;color:gray;background-color:gray; margin-top:50px;">

## Command Reminder

> Shortcut: **cr**

Displays a quick reminder of these commands.

<hr style="height:3px;border-width:0;color:gray;background-color:gray; margin-top:50px;">

## Update Console Output

> Shortcut: **px**

Updates embedded console output in **P**ython e**X**amples.

For top-level statements (no indentation), including compound statements clears and then updates `##` output lines.

When updating, produces the actual output from the example and inserts it, 
so the output is correct and the example runs successfully.

Run `px -h` for details on how to use it.

**Note**: This works only on the Python example files, and not
the examples embedded in Markdown documents. To update those after
you've run this program, use `bookup`.

<hr style="height:3px;border-width:0;color:gray;background-color:gray; margin-top:50px;">

## Update Markdown Code Listings

> Shortcut: **bookup**

Looks in Markdown files for listings with sluglines (listings without sluglines are ignored),
and updates those listings from the source code repository.
You must use the `#[code_location]` tag to provide the path to at least one source code repository,
as a Markdown comment in this format:

```text
<!-- #[code_location] ./src/validate -->
```
- The above is a relative path; You can also use absolute paths:
```text
<!-- #[code_location] /git/pybooktools/src -->
```
- These can appear anywhere in the file.
- The program searches across all the specified directories for the file name
  in the slugline.
- If you provide more than one source code repository, the program ensures
  there are no duplicate file names across those directories.

Run `bookup -h` for details on how to use it.

<hr style="height:3px;border-width:0;color:gray;background-color:gray; margin-top:50px;">


## Slug Line

> Shortcut: **slug**

The "Slug Line" (a term from journalism) not only tells the reader which file
this is, it also enables `bookup` to update the code listing in the book from the source file.

It automatically adds the commented file name at the top of each Python file, in the form:

```text
# file_name.py
```

1. If the slug line does not exist, it is added.
2. If it exists and is incorrect, it is corrected.
3. If it exists and is correct, no changes are made.

Changes are reported by the program.

Run `slug -h` for details on how to use it.

<hr style="height:3px;border-width:0;color:gray;background-color:gray; margin-top:50px;">

## Renumber Chapters and Chapter Names

> Shortcut: **chapnum**

Only works with Markdown (`.md`) files with names beginning with a chapter number, which is digits, possibly followed by a letter.
This is followed by a space and the name of the file followed by `.md`.
If you run the `chapnum` command inside the directory containing such markdown files, it will:

1. Renumber the chapters, choosing the appropriate number of leading zeroes so that all chapter numbers have the same width.
    If a chapter number includes a trailing letter, that letter will be used to establish the resulting numerical order.
    (The letters will be removed from the chapter number in the process).

2. For each file, ensure the file names and the Markdown chapter name on the first line agree:

    A. If there is no chapter name (beginning with a single `#`), the file name without the number will be adapted and inserted as the chapter name.

    B. If there is a chapter name, and it uses title capitalization, the program makes the file name match the chapter name, including correct title capitalization.

    C. If the chapter name doesn't use title capitalization, it is changed to use title capitalization and step B. is applied.

3. To recursively run on all subdirectories, use the `-r` flag.

Run `chapnum -h` for details on how to use it.
