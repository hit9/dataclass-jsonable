# dataclass-jsonable

Simple and flexible conversions between dataclasses and jsonable dictionaries.

## Requirements

Python >= 3.7

## Built-in Supported Type Annotations

* `bool`, `int`, `float`, `str`, `Decimal`, `datetime`, `timedelta`, `Enum`, `IntEnum`
* `Any`, `Optional[X]`
* `List[X]`, `Tuple[X]`, `Set[X]`, `Dict[str, X]`
* `JSONAble`

## Quick Example

```python
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import IntEnum
from typing import List
from dataclass_jsonable import J

class Color(IntEnum):
    BLACK = 0
    BLUE = 1
    RED = 2

@dataclass
class Pen(J):
    color: Color
    price: Decimal
    produced_at: datetime

@dataclass
class Box(J):
    pens: List[Pen]

box = Box(
    pens=[
        Pen(
            color=Color.BLUE,
            price=Decimal("20.1"),
            produced_at=datetime.now(),
        )
    ]
)

# Encode to a jsonable dictionary.
d = box.json()
print(d)  # {'pens': [{'color': 1, 'price': '20.1', 'produced_at': 1660023062}]}

# Construct dataclass from a jsonable dictionary.
print(Box.from_json(d))
```



## License

BSD.
