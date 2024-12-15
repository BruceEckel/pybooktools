# indented_prints.py
for i in range(10):
    print(f"{i = }")
print("__$1$_tls__")


def will_throw(yes: bool = False) -> str:
    if yes:
        raise ValueError("Yes")
    else:
        return "will_throw didn't throw"
print("__$2$_tls__")


try:
    print(will_throw())
except ValueError as e:
    print(f"{e = }")
print("__$3$_tls__")

if True:
    if True:
        print("True")
print("__$4$_tls__")
