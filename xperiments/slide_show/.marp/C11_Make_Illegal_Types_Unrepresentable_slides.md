---
marp: true
theme: uncover
paginate: true
style: |
  /* @auto-scaling false */
---
* Make Illegal Types Unrepresentable
  * "Stringly Typed"
---
```python
# string_phone_numbers.py
# Some problematic formats
phone_numbers: list[str] = [
    "5551234",  # No formatting – unclear area code
    "555-1234",  # US format, but without area code
    "(555) 123-4567",  # US format with punctuation
    "555.123.4567",  # Inconsistent punctuation
    "+1-555-123-4567",  # International format
    "+44 20 7946 0958",  # UK format – space-separated
    "5551234567",  # No formatting at all
    "555 1234",  # Ambiguous – local format?
    "555-12ab",  # Invalid characters
    "CallMeMaybe",  # Completely invalid
    "01234",  # Leading zero – looks like a zip code
    "",  # Empty string
    " 5551234 ",  # Whitespace issues
]
```
---
```python
# phone_number_functions.py
import re


def f1(phone: str):
    valid = re.compile(
        r"^\+?(\d{1,3})?[\s\-.()]*([\d\s\-.()]+)$"
    )
    if not valid.match(phone):
        print(f"Error {phone = }")
        return
    ...


def f2(phone_num: str):
    check = re.compile(
        r"^\+?(\d{1,3})?[\s\-.()]*([\d\s\-.()]+)$"
    )
    assert check.match(phone_num), f"Invalid {phone_num}"
    ...
```
---
```python


def f3(phonenumber: str):
    phone_number = re.compile(
        r"^\+?(\d{1,3})?[\s\-.()]*([\d\s\-.()]+)$"
    )
    if not phone_number.match(phonenumber):
        return f"Bad {phonenumber = }"
    ...
```
---
  * Design by Contract
---
```python
# require.py
from typing import Callable, NamedTuple
from functools import wraps


class Condition(NamedTuple):
    check: Callable[..., bool]
    message: str


def requires(*conditions: Condition):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for condition in conditions:
                if not condition.check(*args, **kwargs):
                    raise ValueError(condition.message)
            return func(*args, **kwargs)

        return wrapper
```
---
```python

    return decorator
```
---
```python
# basic_requires.py
from book_utils import Catch
from require import requires, Condition

positivity = Condition(
    check=lambda x: x > 0, message="x must be positive"
)


@requires(positivity)
def sqrt(x) -> float:
    return x**0.5


print(sqrt(4))
## 2.0
with Catch():
    sqrt(-2)
## Error: x must be positive
```
---
```python
# bank_account.py
from dataclasses import dataclass
from decimal import Decimal

from book_utils import Catch
from require import requires, Condition

positive_amount = Condition(
    check=lambda self, amount: amount >= Decimal("0"),
    message="Amount cannot be negative",
)

sufficient_balance = Condition(
    check=lambda self, amount: self.balance >= amount,
    message="Insufficient balance",
)


@dataclass
class BankAccount:
```
---
```python
    balance: Decimal

    @requires(positive_amount, sufficient_balance)
    def withdraw(self, amount: Decimal) -> str:
        self.balance -= amount
        return f"Withdrew {amount}, balance: {self.balance}"

    @requires(positive_amount)
    def deposit(self, amount: Decimal) -> str:
        self.balance += amount
        return (
            f"Deposited {amount}, balance: {self.balance}"
        )


account = BankAccount(Decimal(100))
print(account.deposit(Decimal(50)))
## Deposited 50, balance: 150
print(account.withdraw(Decimal(30)))
## Withdrew 30, balance: 120
```
---
```python
with Catch():
    account.withdraw(Decimal(200))
## Error: Insufficient balance
with Catch():
    account.deposit(Decimal(-10))
## Error: Amount cannot be negative
```
---
  * Centralizing Validation into Custom Types
---
```python
# amount.py
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Amount:
    value: Decimal

    def __init__(self, value: int | float | str | Decimal):
        d_value = Decimal(str(value))
        if d_value < Decimal("0"):
            raise ValueError(
                f"Amount({d_value}) cannot be negative"
            )
        object.__setattr__(self, "value", d_value)

    def __add__(self, other: "Amount") -> Amount:
        return Amount(self.value + other.value)
```
---
```python

    def __sub__(self, other: "Amount") -> Amount:
        return Amount(self.value - other.value)
```
---
```python
# bad_amount.py
from amount import Amount
from book_utils import Catch

print(Amount(123))
## Amount(value=Decimal('123'))
print(Amount("123"))
## Amount(value=Decimal('123'))
print(Amount(1.23))
## Amount(value=Decimal('1.23'))
with Catch():
    Amount("not-a-number")
## Error: [<class 'decimal.ConversionSyntax'>]
```
---
```python
# balance.py
from __future__ import annotations
from typing import NamedTuple
from amount import Amount


class Balance(NamedTuple):
    amount: Amount

    def deposit(self, amount: Amount) -> Balance:
        return Balance(self.amount + amount)

    def withdraw(self, amount: Amount) -> Balance:
        return Balance(self.amount - amount)
```
---
```python
# typed_bank_account.py
from dataclasses import dataclass
from amount import Amount
from balance import Balance
from book_utils import Catch


@dataclass
class BankAccount:
    balance: Balance

    def deposit(self, amount: Amount) -> str:
        self.balance = self.balance.deposit(amount)
        return f"Deposited {amount.value}, balance: {self.balance.amount.value}"

    def withdraw(self, amount: Amount) -> str:
        self.balance = self.balance.withdraw(amount)
        return f"Withdrew {amount.value}, balance: {self.balance.amount.value}"


```
---
```python
account = BankAccount(Balance(Amount(100)))
print(account.deposit(Amount(50)))
## Deposited 50, balance: 150
print(account.withdraw(Amount(30)))
## Withdrew 30, balance: 120
with Catch():
    account.withdraw(Amount(200))
## Error: Amount(-80) cannot be negative
with Catch():
    account.deposit(Amount(-10))
## Error: Amount(-10) cannot be negative
```
---
  * A `PhoneNumber` Type
---
```python
# phone_number.py
from dataclasses import dataclass
from typing import Self
import re


@dataclass(frozen=True)
class PhoneNumber:
    """
    A validated and normalized phone number.
    """

    country_code: str
    number: str  # Digits only, no formatting

    phone_number_re = re.compile(
        r"^\+?(\d{1,3})?[\s\-.()]*([\d\s\-.()]+)$"
    )

    @classmethod
```
---
```python
    def parse(cls, raw: str) -> Self:
        cleaned = raw.strip()
        match = cls.phone_number_re.match(cleaned)
        if not match:
            raise ValueError(
                f"Invalid phone number: {raw!r}"
            )

        cc, num = match.groups()
        digits = re.sub(r"\D", "", num)
        if not digits:
            raise ValueError(f"No digits found in: {raw!r}")

        country_code = cc if cc else "1"  # default to US
        return cls(country_code=country_code, number=digits)

    def format_number(self) -> str:
        if len(self.number) == 10:
            return f"({self.number[:3]}) {self.number[3:6]}-{self.number[6:]}"
        return self.number  # Fallback: just the digits
```
---
```python

    def __str__(self) -> str:
        formatted = self.format_number()
        return f"+{self.country_code} {formatted}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PhoneNumber):
            return NotImplemented
        return (
            self.country_code == other.country_code
            and self.number == other.number
        )
```
---
```python
# phone_numbers_as_types.py
from phone_number import PhoneNumber
from string_phone_numbers import phone_numbers
from book_utils import Catch

for raw in phone_numbers:
    with Catch():
        pn = PhoneNumber.parse(raw)
        print(f"{raw!r} -> {pn}")
## '5551234' -> +555 1234
## '555-1234' -> +555 1234
## '(555) 123-4567' -> +1 (555) 123-4567
## '555.123.4567' -> +555 1234567
## '+1-555-123-4567' -> +1 (555) 123-4567
## '+44 20 7946 0958' -> +44 (207) 946-0958
## '5551234567' -> +555 1234567
## '555 1234' -> +555 1234
## Error: Invalid phone number: '555-12ab'
## Error: Invalid phone number: 'CallMeMaybe'
## '01234' -> +012 34
```
---
```python
## Error: Invalid phone number: ''
## ' 5551234 ' -> +555 1234
```
---
  * The Programmable Meter
  * How Cyclopts uses Types
