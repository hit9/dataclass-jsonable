from dataclasses import dataclass, field
from enum import IntEnum
from typing import List

from dataclass_jsonable import J


class PhoneType(IntEnum):
    MOBILE = 0
    HOME = 1
    WORK = 2


@dataclass
class PhoneNumber(J):
    number: str
    type: PhoneType


@dataclass
class Person(J):
    name: str
    id: int
    email: str
    phones: List[PhoneNumber] = field(default_factory=list)


@dataclass
class AddressBook(J):
    people: List[Person] = field(default_factory=list)


def test_simple():
    address = AddressBook(
        people=[
            Person(
                name="tom",
                id=1,
                email="tom@example.com",
                phones=[PhoneNumber("18501111111", PhoneType.MOBILE)],
            )
        ]
    )

    # Encode
    data = address.json()

    assert data == {
        "people": [
            {
                "name": "tom",
                "id": 1,
                "email": "tom@example.com",
                "phones": [{"number": "18501111111", "type": 0}],
            }
        ]
    }

    # Decode
    address1 = AddressBook.from_json(data)
    assert address1 == address
