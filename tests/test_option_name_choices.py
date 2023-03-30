from dataclasses import dataclass, field

from dataclass_jsonable import J, json_options


@dataclass
class ChoiceData(J):
    value: str = field(metadata={"j": json_options(name_choice=["Value", "Data"])})


def test_option_name_choice():

    # choice 1
    x = {"Data": "value"}
    cd = ChoiceData.from_json(x)
    assert cd.json() == x

    # choice 2
    cd = ChoiceData(value="value")
    x = {"value": "value"}
    assert cd.json() == ChoiceData.from_json(x)


@dataclass
class Person(J):
    attr: str = field(metadata={"j": json_options(name="new_attr")})


def test_option_name():
    p = Person(attr="value")
    x = {"new_attr": "value"}
    assert p.json() == x
    assert Person.from_json(x) == p


@dataclass
class ChoiceData2(J):
    value: str = field(metadata={"j": json_options(name="value", name_choice=["Value", "Data"])})


def test_option_name_with_choice():
    cd2 = ChoiceData2(value="value")
    x = {"value": "value"}
    assert cd2.json() == x
    assert ChoiceData2.from_json(x) == cd2


def to_camel_case(snake_str: str):
    parts = snake_str.split("_")
    return parts[0] + "".join(x.title() for x in parts[1:])


@dataclass
class Obj(J):
    simple_value: int = field(
        metadata={"j": json_options(name_converter=to_camel_case)}
    )


def test_option_name_converter():
    p = Obj(simple_value=1)
    x = {"simpleValue": 1}
    assert p.json() == x
    assert Obj.from_json(x) == p
