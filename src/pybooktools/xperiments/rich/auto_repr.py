# auto_repr.py
from dataclasses import dataclass

from pybooktools.util import console


@dataclass
class Bird:
    name: str
    eats: list[str] = None
    fly: bool = True
    extinct: bool = False


BIRDS = {
    "gull": Bird("gull", eats=["fish", "chips", "ice cream", "sausage rolls"]),
    "penguin": Bird("penguin", eats=["fish"], fly=False),
    "dodo": Bird("dodo", eats=["fruit"], fly=False, extinct=True)
}

console.print(BIRDS)
