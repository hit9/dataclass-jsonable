# dataclass-jsonable

Simple, practical and overridable conversions between dataclasses
and jsonable dictionaries.

## Quick Example

```python
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

# Encode to jsonable dictionary.
d = box.json()
# {'pens': [{'color': 1, 'price': '20.1', 'produced_at': 1660023062}]}

# Construct dataclass from jsonable dictionary.
box1: Box = Box.from_json(d)
```

## License

BSD.
