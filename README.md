# pybooktools

Tools I use for writing Python books.

- [Documentation](https://bruceeckel.github.io/pybooktools/)

- To deploy updated documentation: `uvx mkdocs gh-deploy`

TODO:
- Consistent UI, consider other UI systems
- Test `update_markdown_code_listings.py` to verify it works with new slugline format
- Add slugline-style output formatting to `update_example_output.py`
- Checker to see if all files in a chapter example directory are used in that chapter.
- Checker (combined with above) that checks sluglines in Markdown file to make sure they exist in the source code repo.
- Tool that extracts one example or all examples from a chapter back to its source code repo.
