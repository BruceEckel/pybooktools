# indented_prints.py
for i in range(10):
    print(f"{i = }")
## i = 0
## i = 1
## i = 2
## i = 3
## i = 4
## i = 5
## i = 6
## i = 7
## i = 8
## i = 9


def will_throw(yes: bool = False) -> str:
    if yes:
        raise ValueError("Yes")
    else:
        return "will_throw didn't throw"


try:
    print(will_throw())
except ValueError as e:
    print(f"{e = }")
## will_throw didn't throw

if True:
    if True:
        print("True")
## True
