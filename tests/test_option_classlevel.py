from dataclasses import dataclass, field
from typing import Optional

from dataclass_jsonable import J, json_options


@dataclass
class Obj(J):
    __default_json_options__ = json_options(omitempty=True)

    a: Optional[int] = None
    b: Optional[str] = None
    # We could still override the default json_options at field level.
    c: Optional[str] = field(
        default=None, metadata={"j": json_options(omitempty=False)}
    )


def test_option_classlevel_omitempty():
    o = Obj(b="b")
    x = {"b": "b", "c": None}
    assert o.json() == x
    assert Obj.from_json(x) == o
