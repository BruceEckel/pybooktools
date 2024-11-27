#: test2.py


class Foo:
    def x(self):
        print("test1")

    def y(self):
        print("test2\ntest3")


if __name__ == "__main__":
    f = Foo()
    f.x()
    "1:test1"
    f.y()
    """2:"""
