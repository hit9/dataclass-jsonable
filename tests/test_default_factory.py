from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Set, Tuple

from dataclass_jsonable import J


@dataclass
class A(J):
    a: int


@dataclass
class B(J):
    a: A


@dataclass
class C(J):
    a: int
    b: str
    c: bool
    d: None
    e: float
    f: Decimal
    g: datetime
    h: timedelta
    i: set
    k: dict
    o: Optional[int]
    t: Tuple[int, str]
    q: Any
    m: Optional[str] = ""


@dataclass
class S1(J):
    a: List[int]
    b: Set[str]
    c: Tuple[int, str]
    d: Tuple[int, ...]
    e: Optional[int] = None
    f: Dict[str, Any] = field(default_factory=dict)


def test_default_factory_basic():
    d = {}
    c = C(
        a=0,
        b="",
        c=False,
        d=None,
        e=0.0,
        f=Decimal("0.0"),
        g=datetime.fromtimestamp(0),
        h=timedelta(days=0),
        i=set(),
        k={},
        o=None,
        m="",
        t=(),  # type: ignore
        q=None,
    )
    assert C.from_json(d) == c


def test_default_factory_nested():
    d = {}
    assert B.from_json(d) == B(a=A(a=0))


def test_default_factory_generics():
    d = {}
    assert S1.from_json(d) == S1(a=[], b=set(), c=(), d=(), e=None, f={})
