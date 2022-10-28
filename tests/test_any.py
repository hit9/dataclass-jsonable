from dataclasses import dataclass
from typing import Any, Dict

from dataclass_jsonable import J

JSON = Dict[str, Any]


@dataclass
class A(J):
    B: JSON


def test_any():
    a = A(
        B={
            "abc": 2,
            "efg": [4, 5, 6],
            "dct": {"x": "y"},
            "set": {1, 2, 3},
            "empty_dict": {},
            "empty_list": [],
            "empty_set": set(),
            "n": None,
        }
    )
    d = a.json()
    assert d == {
        "B": {
            "abc": 2,
            "efg": [4, 5, 6],
            "dct": {"x": "y"},
            "set": {1, 2, 3},
            "empty_dict": {},
            "empty_list": [],
            "empty_set": set(),
            "n": None,
        }
    }
    a1 = A.from_json(
        {
            "B": {
                "abc": 2,
                "efg": [4, 5, 6],
                "dct": {"x": "y"},
                "set": {1, 2, 3},
                "empty_dict": {},
                "empty_list": [],
                "empty_set": set(),
                "n": None,
            }
        }
    )
    assert a1 == a
