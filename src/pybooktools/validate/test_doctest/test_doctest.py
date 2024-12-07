"""
>>> print("example output")
example output
"""


def f():
    """
    >>> f()
    one line
    another line
    """
    print("one line\nanother line")


def g():
    """
    >>> g()
    multiple lines
    of output
    using triple quotes
    """
    print(
        """
    multiple lines
    of output
    using triple quotes
    """
    )


def main():
    """
    >>> main()
    in main
    >>> f()
    one line
    another line
    >>> g()
    multiple lines
    of output
    using triple quotes
    """
    print("in main")


if __name__ == "__main__":
    main()
