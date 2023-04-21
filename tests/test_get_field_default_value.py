from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import datetime, timedelta
from decimal import Decimal

from dataclass_jsonable import J, get_field_default_value, json_options


@dataclass
class Base(J):
    __default_json_options__ = json_options(default_on_missing=get_field_default_value)


@dataclass
class A(Base):
    a: int


@dataclass
class B(Base):
    a: A


@dataclass
class C(Base):
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
    m: Optional[str] = ""


@dataclass
class S1(Base):
    a: List[int]
    b: Set[str]
    c: Tuple[int, str]
    d: Tuple[int, ...]
    e: Optional[int] = None
    f: Dict[str, Any] = field(default_factory=dict)


def test_default_basic():
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
        o=0,
        m="",
        t=(),
    )
    assert C.from_json(d) == c


def test_default_nested():
    d = {}
    assert B.from_json(d) == B(a=A(a=0))


def test_default_generics():
    d = {}
    assert S1.from_json(d) == S1(a=[], b=set(), c=(), d=(), e=None, f={})
