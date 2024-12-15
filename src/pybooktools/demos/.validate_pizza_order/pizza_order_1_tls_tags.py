# pizza_order.py
from dataclasses import dataclass
print("__$1$_tls__")
from enum import Enum, auto
print("__$2$_tls__")


class Size(Enum):
    SMALL = auto()
    LARGE = auto()
print("__$3$_tls__")


class Add(Enum):
    PEPPERONI = auto()
    MUSHROOMS = auto()
    OLIVES = auto()
    PEPPERS = auto()
print("__$4$_tls__")


@dataclass
class Pizza:
    size: Size
    toppings: list[Add]
print("__$5$_tls__")


class Status(Enum):
    ORDERED = auto()
    IN_OVEN = auto()
    READY = auto()
print("__$6$_tls__")


@dataclass
class Order:
    pizza: Pizza
    __status: Status = Status.ORDERED

    def __repr__(self) -> str:
        return self.__status.name.replace("_", " ").title()

    def update(self, new_status: Status) -> "Order":
        self.__status = new_status
        return self
print("__$7$_tls__")


pizza = Pizza(Size.LARGE, [Add.PEPPERONI, Add.OLIVES])
print("__$8$_tls__")
print(pizza)
print("__$9$_tls__")
print(order := Order(pizza))
print("__$10$_tls__")
print(order.update(Status.IN_OVEN))
print("__$11$_tls__")
print(order.update(Status.READY))
print("__$12$_tls__")
