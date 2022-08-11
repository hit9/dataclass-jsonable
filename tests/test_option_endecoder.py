from dataclasses import dataclass, field
from datetime import datetime
from typing import List

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
