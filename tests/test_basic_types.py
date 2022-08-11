from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum, IntEnum

from dataclass_jsonable import J


class E1(IntEnum):
    A = 1
    B = 2


class E2(Enum):
    A = "A"
    B = "B"


@dataclass
class S1(J):
    a: int
    b: str
    c: bool
    d: None
    e: float
    f: Decimal
    g: datetime
    h: timedelta
    e1: E1
    e2: E2


def test_basic_types():
    s = S1(
        a=1,
        b="2",
        c=True,
        d=None,
        e=1.2,
        f=Decimal("1.2"),
        g=datetime(2022, 1, 1, 1, 1, 1),
        h=timedelta(days=1),
        e1=E1.A,
        e2=E2.B,
    )
    x = {
        "a": 1,
        "b": "2",
        "c": True,
        "d": None,
        "e": 1.2,
        "f": "1.2",
        "g": 1640970061,
        "h": 86400,
        "e1": 1,
        "e2": "B",
    }
    assert s.json() == x
    assert S1.from_json(x) == s