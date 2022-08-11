from dataclasses import dataclass, field

from dataclass_jsonable import J, json_options


@dataclass
class Obj(J):
    attr: str = field(metadata={"j": json_options(skip=True)})
    x: str = "x"


def test_option_skip():
    o = Obj(attr="private")
    x = {"x": "x"}
    assert o.json() == x
