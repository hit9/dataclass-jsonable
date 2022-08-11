from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import IntEnum
from typing import List

from dataclass_jsonable import J, json_options


class PhoneType(IntEnum):
    MOBILE = 0
    HOME = 1
    WORK = 2


@dataclass
class PhoneNumber(J):
    number: str
    type: PhoneType
    created_at: datetime = field(
        default_factory=datetime.now,
        metadata={
            "j": json_options(
                name="create_time",
                encoder=datetime.isoformat,
                decoder=datetime.fromisoformat,
            )
        },
    )


@dataclass
class Person(J):
    name: str
    id: int
    email: str
    phones: List[PhoneNumber] = field(default_factory=list)


@dataclass
class AddressBook(J):
    people: List[Person] = field(default_factory=list)
    price: Decimal = Decimal("0.0")
    produced_at: datetime = field(default_factory=datetime.now)


def test_simple():
    address = AddressBook(
        people=[
            Person(
                name="tom",
                id=1,
                email="tom@example.com",
                phones=[
                    PhoneNumber(
                        "18501111111",
                        PhoneType.MOBILE,
                        created_at=datetime(2022, 8, 9, 8, 0, 0),
                    )
                ],
            )
        ],
        produced_at=datetime(2022, 8, 7, 19, 30, 0),
    )

    # Encode
    data = address.json()

    assert data == {
        "people": [
            {
                "name": "tom",
                "id": 1,
                "email": "tom@example.com",
                "phones": [
                    {
                        "number": "18501111111",
                        "type": 0,
                        "create_time": "2022-08-09T08:00:00",
                    }
                ],
            }
        ],
        "price": "0.0",
        "produced_at": 1659871800,
    }

    # Decode
    address1 = AddressBook.from_json(data)
    assert address1 == address
