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


def to_camel_case(snake_str: str):
    parts = snake_str.split("_")
    return parts[0] + "".join(x.title() for x in parts[1:])


@dataclass
class Obj2(J):
    __default_json_options__ = json_options(name_converter=to_camel_case)
    status_code: int
    simple_value: str


def test_option_classlevel_name_converter():
    o = Obj2(status_code=1, simple_value="simple")
    x = {"statusCode": 1, "simpleValue": "simple"}
    assert o.json() == x
    assert Obj2.from_json(x) == o
