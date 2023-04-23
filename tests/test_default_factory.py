from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Set, Tuple

from dataclass_jsonable import J, zero


@dataclass
class E(J):
    __default_factory__ = zero


@dataclass
class A(E):
    a: int


@dataclass
class B(E):
    a: A


@dataclass
class C(E):
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
class S1(E):
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


@dataclass
class Y(E):
    e: str
    k: str = "abc"


@dataclass
class X(E):
    a: int
    y: Y
    z: "M"
    b: int = 1
    c: List[str] = field(default_factory=list)


@dataclass
class M(E):
    z: List[Y]


def test_default_overload():
    x = X.from_json({})
    assert x.a == 0
    assert x.b == 1
    assert x.c == []
    assert x.y.e == ""
    assert x.y.k == "abc"
    assert x.z.z == []
