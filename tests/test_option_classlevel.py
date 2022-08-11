from dataclasses import dataclass, field
from typing import Optional

from dataclass_jsonable import J, json_options


@dataclass
class Obj(J):
    __default_json_options__ = json_options(omitempty=True)

    a: Optional[int] = None
    b: Optional[str] = None


def test_option_classlevel_omitempty():
    o = Obj(b="b")
    x = {"b": "b"}
    assert o.json() == x
    assert Obj.from_json(x) == o
