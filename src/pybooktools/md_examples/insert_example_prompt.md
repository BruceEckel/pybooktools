I'd like a function:

```python
def insert_example(example_path: Path, replace: bool = False):
    """
    Using example_path, figures out:
    1. What Markdown chapter this example came from
    2. Where in the Markdown chapter this example lives
    3. If the example at example_path is different than the one in the chapter.
       If so, show the diffs.
    4. If `replace` is True and the example is different, replace it in the chapter.
    """