from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal

from dataclass_jsonable import J


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
    }
    assert s.json() == x
    assert S1.from_json(x) == s
