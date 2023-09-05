from dataclasses import dataclass, field
from datetime import datetime

from dataclass_jsonable import J, json_options


@dataclass
class Obj(J):
    t: datetime = field(metadata={"j": json_options(keep=True)})
    t1: datetime = field(metadata={"j": json_options(keep=False)})


def test_option_skip():
    t = datetime.now()
    o = Obj(t=t, t1=t)
    d = o.json()
    assert isinstance(d["t"], datetime)
    assert isinstance(d["t1"], int)
