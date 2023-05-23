import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List

from dataclass_jsonable import J, json_options


@dataclass
class Obj(J):
    elems: List[str] = field(
        metadata={
            "j": json_options(
                encoder=lambda x: ",".join(x),
                decoder=lambda x: x.split(","),
            )
        }
    )


def test_option_endecoder_simple():
    o = Obj(elems=["a", "b", "c"])
    x = {"elems": "a,b,c"}
    assert o.json() == x
    assert Obj.from_json(x) == o


@dataclass
class Obj1(J):
    elems: List[str] = field(
        metadata={
            "j": json_options(
                to_json=lambda x: ",".join(x),
                from_json=lambda x: x.split(","),
            )
        }
    )


def test_option_endecoder_alias():
    o = Obj1(elems=["a", "b", "c"])
    x = {"elems": "a,b,c"}
    assert o.json() == x
    assert Obj1.from_json(x) == o


@dataclass
class Record(J):
    created_at: datetime = field(
        default_factory=datetime.now,
        metadata={
            "j": json_options(
                encoder=datetime.isoformat,
                decoder=datetime.fromisoformat,
            )
        },
    )


def test_option_endecoder_datetime():
    r = Record(created_at=datetime(2022, 1, 1, 1, 1, 1))
    x = {"created_at": "2022-01-01T01:01:01"}
    assert r.json() == x
    assert Record.from_json(x) == r


@dataclass
class Obj2(J):
    data: Dict[str, Any] = field(
        metadata={"j": json_options(before_decoder=json.loads)}
    )


def test_option_before_decoder():
    o = Obj2(data={"k": "v"})
    x = {"data": '{"k": "v"}'}
    assert Obj2.from_json(x) == o
