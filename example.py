from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import IntEnum
from typing import List

from dataclass_jsonable import JSON, J, json_options


class Color(IntEnum):
    BLACK = 0
    BLUE = 1
    RED = 2
    GREEN = 3


@dataclass
class Person(J):
    name: str
    remark: str = field(default="", metadata={"j": json_options(skip=False)})
    extras: JSON = field(default_factory=dict)
    registered_at: datetime = field(default_factory=lambda: datetime.fromtimestamp(0))


@dataclass
class Pencil(J):
    name: str
    color: Color
    price: Decimal
    owner: Person
    created_at: datetime = field(
        metadata={
            "j": json_options(
                name="create_time",
                encoder=datetime.isoformat,
                decoder=datetime.fromisoformat,
            )
        }
    )
    is_typical: bool = field(
        default=False,
        metadata={
            "j": json_options(
                decoder=lambda x: x == "1", encoder=lambda x: "1" if x else "0"
            )
        },
    )
    creators: List[Person] = field(default_factory=list)


# Decode

pencil: Pencil = Pencil.from_json(
    {
        "name": "pencil",
        "color": 1,
        "create_time": "2022-08-08T18:54:24",
        "price": "10.5",
        "owner": {"name": "tom"},
        "creators": [{"name": "jerry"}, {"name": "kevin", "extras": {"note": "abc"}}],
    }
)

print(pencil)

# Encode
data = pencil.json()
print(data)

# Re-Decode
pencil2: Pencil = Pencil.from_json(data)
print(pencil2)
