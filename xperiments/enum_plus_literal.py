from enum import Enum
from typing import Literal


class Status(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    PENDING = "pending"


# Now, for type hints, we define:
StatusLiteral = Literal["open", "closed", "pending"]


def update_status_flexible(new_status: Status | StatusLiteral) -> None:
    if isinstance(new_status, Status):
        new_status = new_status.value
    print(f"Updating status to: {new_status}")


update_status_flexible("pending")  # ✅ OK
update_status_flexible(Status.CLOSED)  # ✅ OK
