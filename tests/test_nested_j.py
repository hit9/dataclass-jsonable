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
