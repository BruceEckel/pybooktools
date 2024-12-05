from pybooktools.validate.validate_output import show


def demo1():
    show("example output\nbo's yer uncle")
    #: example output
    #: bo's yer uncle


# def demo2():
#     show(
#     """
#     example
#     output
#     """
#     )


if __name__ == "__main__":
    show("step 1")
    demo1()
    show("step 2")
    # demo2()
    demo1()
    show("done")
