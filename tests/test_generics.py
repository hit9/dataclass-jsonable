import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

import pytest
from dataclass_jsonable import J


@dataclass
class S1(J):
    a: List[int]
    b: Set[str]
    c: Tuple[int, str]
    d: Tuple[int, ...]
    e: Optional[int] = None
    f: Dict[str, Any] = field(default_factory=dict)


def test_generics_simple():
    o = S1(
        a=[1, 2],
        b={"3"},
        c=(1, "a"),
        d=(5, 6, 7),
        e=9,
        f={"1": 2},
    )
    x = {
        "a": [1, 2],
        "b": ["3"],
        "c": [1, "a"],
        "d": [5, 6, 7],
        "e": 9,
        "f": {"1": 2},
    }
    assert o.json() == x
    assert S1.from_json(x) == o


@pytest.mark.skipif(
    sys.version_info < (3, 9), reason="list[int] etc supports since python 3.9"
)
def test_generics_simple_native() -> None:
    @dataclass
    class S2(J):
        g: list[int] = field(default_factory=list)
        h: set[str] = field(default_factory=set)
        i: dict[str, int] = field(default_factory=dict)

    o = S2(
        g=[1, 2],
        h={"a"},
        i={"a": 3},
    )
    x = {
        "g": [1, 2],
        "h": ["a"],
        "i": {"a": 3},
    }

    assert o.json() == x
    assert S2.from_json(x) == o
