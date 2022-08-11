from dataclasses import dataclass, field
from typing import List, Optional, Set, Tuple

from dataclass_jsonable import J, json_options


@dataclass
class Obj(J):
    a: List[int]
    b: Set[str]
    c: Tuple[int, str]
    d: Tuple[int, ...]
    e: Optional[int] = None


def test_generics_simple():
    o = Obj(a=[1, 2], b={"3", "4"}, c=(1, "a"), d=(5, 6, 7), e=9)
    x = {"a": [1, 2], "b": ["3", "4"], "c": [1, "a"], "d": [5, 6, 7], "e": 9}
    assert o.json() == x
    assert Obj.from_json(x) == o
