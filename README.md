# pybooktools

Tools I use for writing Python books.

- [Documentation](https://bruceeckel.github.io/pybooktools/)

- To deploy updated documentation: `uvx mkdocs gh-deploy`

TODO:
- Consistent UI, consider other UI systems:
  - Fill in `display` library 
  - https://rich.readthedocs.io/en/stable/protocol.html: Define __rich__ for classes
  - Add slugline-style output formatting to `update_example_output.py`
- Test `update_markdown_code_listings.py` to verify it works with new slugline format
- Tool that extracts one example or all examples from a chapter back to its source code repo.
  Will extract a new examples directory and stub files for a chapter.
  If a slugline exists in the Markdown file it will create it (if not already there) in the corresponding source-code repo.
  Also tells you if any files in a chapter example directory are not used in that chapter.
