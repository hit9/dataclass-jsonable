from dataclasses import dataclass
from typing import Dict, List, Optional

from dataclass_jsonable import J


@dataclass
class A(J):
    a: int = 0


@dataclass
class B(J):
    a: A


@dataclass
class C(J):
    a_list: List[A]
    b_dict: Dict[str, B]
    children: List["C"]
    a1: A


def test_nested_j():
    c = C(a_list=[A(a=1), A(a=2)], b_dict={"b": B(a=A(a=3))}, children=[], a1=A(a=4))
    x = {
        "a_list": [{"a": 1}, {"a": 2}],
        "b_dict": {"b": {"a": {"a": 3}}},
        "children": [],
        "a1": {"a": 4},
    }
    assert c.json() == x
    assert C.from_json(x) == c


@dataclass
class Elem(J):
    k: str


@dataclass
class Obj(J):
    a: List[Elem]


def test_nested_j_simple():
    o = Obj([Elem("v")])
    x = {"a": [{"k": "v"}]}
    assert o.json() == x
    assert Obj.from_json(x) == o


@dataclass
class JsonLike:  # Not extend from J
    parts: List[str]

    @classmethod
    def from_json(cls, d: str) -> "JsonLike":
        return cls(parts=d.split(";"))

    def json(self) -> str:
        return ";".join(self.parts)


@dataclass
class Container(J):
    f: JsonLike


def test_nested_j_jsonlike():
    c = Container(f=JsonLike(parts=["a", "b", "c"]))
    x = {"f": "a;b;c"}
    assert c.json() == x
    assert Container.from_json(x) == c
