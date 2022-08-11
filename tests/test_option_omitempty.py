from dataclasses import dataclass, field
from typing import Optional

from dataclass_jsonable import J, json_options


@dataclass
class Book(J):
    name: str = field(default="", metadata={"j": json_options(omitempty=True)})
    data: int = 2


def test_option_omitempty():
    b = Book(name="")
    x = {"data": 2}
    assert b.json() == x
    assert Book.from_json(x) == b


@dataclass
class S(J):
    a: Optional[int] = field(
        default=None,
        metadata={
            "j": json_options(omitempty=True, omitempty_tester=lambda x: x is None)
        },
    )
    b: Optional[int] = field(
        default=None,
        metadata={
            "j": json_options(omitempty=True, omitempty_tester=lambda x: x is None)
        },
    )


def test_option_omitempty_tester():
    s = S(a=None, b=0)
    x = {"b": 0}
    assert s.json() == x
    assert S.from_json(x) == s
