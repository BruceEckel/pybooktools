# pizza_order.py
from dataclasses import dataclass
from enum import Enum, auto


class Size(Enum):
    SMALL = auto()
    LARGE = auto()


class Add(Enum):
    PEPPERONI = auto()
    MUSHROOMS = auto()
    OLIVES = auto()
    PEPPERS = auto()


@dataclass
class Pizza:
    size: Size
    toppings: list[Add]


class Status(Enum):
    ORDERED = auto()
    IN_OVEN = auto()
    READY = auto()


@dataclass
class Order:
    pizza: Pizza
    __status: Status = Status.ORDERED

    def __repr__(self) -> str:
        return self.__status.name.replace("_", " ").title()

    def update(self, new_status: Status) -> "Order":
        self.__status = new_status
        return self


print(pizza := Pizza(Size.LARGE, [Add.PEPPERONI, Add.OLIVES]))
print(order := Order(pizza))
print(order.update(Status.IN_OVEN))
print(order.update(Status.READY))
