for i in range(10):
    print(f"{i = }")


def will_throw(yes: bool = False) -> str:
    if yes:
        raise ValueError("Yes")
    else:
        return "will_throw didn't throw"


try:
    print(will_throw())
except ValueError as e:
    print(f"{e = }")

if True:
    if True:
        print("True")
