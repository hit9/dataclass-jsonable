from dataclasses import dataclass, field

from dataclass_jsonable import J, json_options


@dataclass
class Obj1(J):
    name: str = field(
        metadata={
            "j": json_options(
                name="Name",
            )
        }
    )


def test_option_name():
    o = Obj1(name="jack")
    d = {"Name": "jack"}
    t = {"Name": "jack"}
    assert o.json() == d
    assert Obj1.from_json(t) == o


@dataclass
class Obj2(J):
    name: str = field(
        metadata={
            "j": json_options(
                name_converter=lambda x: "nickname",
            )
        }
    )


def test_option_name_converter():
    o = Obj2(name="jack")
    d = {"nickname": "jack"}
    t = {"nickname": "jack"}
    assert o.json() == d
    assert Obj2.from_json(t) == o


@dataclass
class Obj3(J):
    name: str = field(
        metadata={
            "j": json_options(
                name_inverter=lambda x: x.upper(),
            )
        }
    )


def test_option_name_inverter():
    o = Obj3(name="jack")
    d = {"name": "jack"}
    t = {"NAME": "jack"}
    assert o.json() == d
    assert Obj3.from_json(t) == o


@dataclass
class Obj4(J):
    name: str = field(
        metadata={
            "j": json_options(
                name="Name",
                name_inverter=lambda x: x.upper(),
            )
        }
    )


def test_option_name_and_inverter():
    o = Obj4(name="jack")
    d = {"Name": "jack"}
    t = {"Name": "jack"}
    assert o.json() == d
    assert Obj4.from_json(t) == o


@dataclass
class Obj5(J):
    name: str = field(
        metadata={
            "j": json_options(
                name_converter=lambda x: "nickname",
                name_inverter=lambda x: x.upper(),
            )
        }
    )


def test_option_converter_and_inverter():
    o = Obj5(name="jack")
    d = {"nickname": "jack"}
    t = {"NAME": "jack"}
    assert o.json() == d
    assert Obj5.from_json(t) == o
