from enum import Enum


class EmptyToken(Enum):
    """A sentinel for empty/default token."""
    pass


def func(x: int | None | EmptyToken = EmptyToken) -> int:
    if x is EmptyToken:
        print(EmptyToken)
        return 0
    elif x is None:
        print(type(x))
        return 1
    else:  # here, x can only have type int
        print(type(x))
        return 42


if __name__ == "__main__":
    print(func(1))
    print(func(None))
    print(func())
