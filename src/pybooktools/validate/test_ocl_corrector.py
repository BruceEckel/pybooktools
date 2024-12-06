print("example output")


#: example output


def f():
    print("one line\nanother line")
    #: one line
    #: another line


def g():
    print(
        """
    multiple lines
    of output
    using triple quotes
    """
    )
    #: multiple lines
    #: of output
    #: using triple quotes


if __name__ == "__main__":
    print("in main")
    #: in main
    f()
    g()
