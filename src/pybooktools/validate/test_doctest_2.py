def f():
    print("one line\nanother line")


def g():
    print(
        """
        multiple lines
        of output
        using triple quotes
        """
    )


__doc__ = """
>>> f()
one line
another line
>>> g()
multiple lines
of output
using triple quotes
"""
