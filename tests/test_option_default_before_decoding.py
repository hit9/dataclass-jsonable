from dataclasses import dataclass, field
from datetime import datetime

from dataclass_jsonable import J, json_options


@dataclass
class Obj(J):
    a: datetime = field(metadata={"j": json_options(default_before_decoding=0)})
    b: datetime = field(metadata={"j": json_options(default_on_missing=0)})


def test_option_default_before_decoding():
    o = Obj.from_json({})
    assert o.a == datetime.fromtimestamp(0)
    assert o.b == datetime.fromtimestamp(0)
