from dataclasses import dataclass, field
from typing import Optional

from dataclass_jsonable import J, json_options


@dataclass
class Obj(J):
    a: str
    b: int
    c: Optional[int] = field(default=None, metadata={"j": json_options(omitempty=True)})


def test_debug_origin_json():
    d = {"a": "a", "b": 1, "c": None}
    o = Obj.from_json(d)
    d1 = o._get_origin_json()
    assert d == d1
