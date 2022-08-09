# dataclass-jsonable

Simple and flexible conversions between dataclasses and jsonable dictionaries.

## Requirements

Python >= 3.7

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

## Built-in Supported Types

* `bool`, `int`, `float`, `str`, `None` encoded as it is.
* `Decimal` encoded to `str`.
* `datetime` encoded to timestamp integer via `.timestamp()` method.
  `timedelta` encoded to integer via `.total_seconds()` method.
* `Enum` and `IntEnum` encoded to their values via `.value` attribute.
* `Any` is encoded according to its `type`.
* `Optional[X]` is supported, but `Union[X, Y, ...]` is not.
* `List[X]`, `Tuple[X]`, `Set[X]` are all encoded to `list`.
* `Dict[str, X]` encoded to `dict`
* Nested `JSONAble` or `J` dataclasses.

## Customization or Overriding

We can override the default conversion behaviors with `json_options`:

```python
from dataclasses import field
from dataclass_jsonable import json_options
```

Supported options:

1. Specific a custom dictionary key over the default field's name:

   ```python
   @dataclass
   class Person(J):
       name: str = field(metadata={"j": json_options(name="new_name")})
   ```

## License

BSD.
