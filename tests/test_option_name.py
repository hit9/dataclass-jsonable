from dataclasses import dataclass, field

from dataclass_jsonable import J, json_options


@dataclass
class Person(J):
    attr: str = field(metadata={"j": json_options(name="new_attr")})


def test_option_name():
    p = Person(attr="value")
    x = {"new_attr": "value"}
    assert p.json() == x
    assert Person.from_json(x) == p
