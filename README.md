# dataclass-jsonable

[![dataclass-jsonable ci](https://github.com/hit9/dataclass-jsonable/actions/workflows/ci.yml/badge.svg)](https://github.com/hit9/dataclass-jsonable/actions/workflows/ci.yml)
![](https://img.shields.io/badge/license-BSD3-brightgreen)

Simple and flexible conversions between dataclasses and jsonable dictionaries.

It maps dataclasses to jsonable dictionaries but not json strings.


## Features

* Easy to use.
* Supports common type annotations.
* Supports recursive conversions.
* Supports field-level and dataclass-level overriding.

## Installation

Requirements: Python >= 3.7

Install via `pip`:

```
pip install dataclass-jsonable
```

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

box = Box(pens=[Pen(color=Color.BLUE, price=Decimal("20.1"), produced_at=datetime.now())])

# Encode to a jsonable dictionary.
d = box.json()
print(d)  # {'pens': [{'color': 1, 'price': '20.1', 'produced_at': 1660023062}]}

# Construct dataclass from a jsonable dictionary.
print(Box.from_json(d))
```

APIs are only the two: `.json()` and `.from_json()`.

## Built-in Supported Types

* `bool`, `int`, `float`, `str`, `None` encoded as it is.

  ```python
  @dataclass
  class Obj(J):
      a: int
      b: str
      c: bool
      d: None

  Obj(a=1, b="b", c=True, d=None).json()
  # => {'a': 1, 'b': 'b', 'c': True, 'd': None}
  ```

* `Decimal` encoded to `str`.

  ```python
  @dataclass
  class Obj(J):
      a: Decimal

  Obj(a=Decimal("3.1")).json()  # => {'a': '3.1'}
  ```

* `datetime` encoded to timestamp integer via `.timestamp()` method.
  `timedelta` encoded to integer via `.total_seconds()` method.

  ```python
  @dataclass
  class Obj(J):
      a: datetime
      b: timedelta

  Obj(a=datetime.now(), b=timedelta(minutes=1)).json()
  # => {'a': 1660062019, 'b': 60}
  ```

* `Enum` and `IntEnum` encoded to their values via `.value` attribute.

  ```python
  @dataclass
  class Obj(J):
      status: Status

  Obj(status=Status.DONE).json()  # => {'status': 1}
  ```

* `Any` is encoded according to its `type`.

  ```python
  @dataclass
  class Obj(J):
      a: Any

  Obj(1).json()  # {'a': 1}
  Obj("a").json()  # {'a': 'a'}
  Obj.from_json({"a": 1})  # Obj(a=1)
  ```

* `Optional[X]` is supported, but `Union[X, Y, ...]` is not.

  ```python
  @dataclass
  class Obj(J):
      a: Optional[int] = None

  Obj(a=1).json()  # => {'a': 1}
  ```

* `List[X]`, `Tuple[X]`, `Set[X]` are all encoded to `list`.

  ```python
  @dataclass
  class Obj(J):
      a: List[int]
      b: Set[int]
      c: Tuple[int, str]
      d: Tuple[int, ...]

  Obj(a=[1], b={2, 3}, c=(4, "5"), d=(7, 8, 9)).json())
  # => {'a': [1], 'b': [2, 3], 'c': [4, '5'], 'd': [7, 8, 9]}

  Obj.from_json({"a": [1], "b": [2, 3], "c": [4, "5"], "d": [7, 8, 9]}))
  # => Obj(a=[1], b={2, 3}, c=(4, '5'), d=(7, 8, 9))
  ```

* `Dict[str, X]` encoded to `dict`.

  ```python
  @dataclass
  class Obj(J):
      a: Dict[str, int]
  Obj(a={"x": 1}).json()  # => {'a': {'x': 1}}
  Obj.from_json({"a": {"x": 1}}) # => Obj(a={'x': 1})
  ```

* Nested or recursively `JSONAble` (or `J`) dataclasses.

  ```python
  @dataclass
  class Elem(J):
      k: str

  @dataclass
  class Obj(J):
      a: List[Elem]

  Obj([Elem("v")]).json()  # => {'a': [{'k': 'v'}]}
  Obj.from_json({"a": [{"k": "v"}]})  # Obj(a=[Elem(k='v')])
  ```

* Postponed annotations (the `ForwardRef` in [PEP 563](https://www.python.org/dev/peps/pep-0563/)).

  ```python
  @dataclass
  class Node(J):
      name: str
      left: Optional["Node"] = None
      right: Optional["Node"] = None

  root = Node("root", left=Node("left"), right=Node("right"))
  root.json()
  # {'name': 'root', 'left': {'name': 'left', 'left': None, 'right': None}, 'right': {'name': 'right', 'left': None, 'right': None}}
  ```

If these built-in default conversion behaviors do not meet your needs,
or your type is not on the list,
you can use [json_options](#customization--overriding-examples) introduced below to customize it.

## Customization / Overriding Examples

We can override the default conversion behaviors with `json_options`,
which uses the dataclass field's metadata for field-level customization purpose,
and the namespace is `j`.

The following pseudo code gives the pattern:

```python
from dataclasses import field
from dataclass_jsonable import json_options

@dataclass
class Struct(J):
    attr: T = field(metadata={"j": json_options(**kwds)})
```

An example list about `json_options`:

* Specific a custom dictionary key over the default field's name:

   ```python
   @dataclass
   class Person(J):
       attr: str = field(metadata={"j": json_options(name="new_attr")})
   Person(attr="value").json() # => {"new_attr": "value"}
   ```

  And more, we can use a function to specific a custom dictionary key.
  This may be convenient to work with class-level `__default_json_options__` attribute (check it below).

  ```python
  @dataclass
  class Obj(J):
      simple_value: int = field(metadata={"j": json_options(name_converter=to_camel_case)})
  Obj(simple_value=1).json()  # => {"simpleValue": 1}
  ```

  And we may specific a custom field name converter when converts dictionary to dataclass:

  ```python
  @dataclass
  def Person(J):
    name: str = field(
          metadata={
              "j": json_options(
                  name_converter=lambda x: x.capitalize(),
                  name_inverter=lambda x: "nickname",
            )
        }
    )
  ```

  As the `Person` defined above, it will convert to dictionary like `{"Name": "Jack"}` and can be loaded from `{"nickname": "Jack"}`.

* Omit a field if its value is empty:

   ```python
   @dataclass
   class Book(J):
       name: str = field(metadata={"j": json_options(omitempty=True)})
   Book(name="").json() # => {}
   ```

  Further, we can specify what is 'empty' via option `omitempty_tester`:

   ```python
   @dataclass
   class Book(J):
       attr: Optional[str] = field(
           default=None,
           metadata={
               # By default, we test `empty` using `not x`.
               "j": json_options(omitempty=True, omitempty_tester=lambda x: x is None)
           },
       )

   Book(attr="").json()  # => {'attr': ''}
   Book(attr=None).json()  # => {}
   ```

* Always skip a field. So we can stop some "private" fields from exporting:

   ```python
   @dataclass
   class Obj(J):
       attr: str = field(metadata={"j": json_options(skip=True)})

   Obj(attr="private").json() # => {}
   ```

* dataclasses's `field` allows us to pass a `default` or `default_factory` argument to
  set a default value:

  ```python
  @dataclass
  class Obj(J):
      attr: List[str] = field(default_factory=list, metadata={"j": json_options(**kwds)})
  ```

  There's also an option `default_on_missing` in dataclass-jsonable,
  which specifics a default value before decoding if the key is missing in the dictionary.
  Sometimes this way is more concise:

  ```python
  @dataclass
  class Obj(J):
      updated_at: datetime = field(metadata={"j": json_options(default_on_missing=0)})

  Obj.from_json({})  # => Obj(updated_at=datetime.datetime(1970, 1, 1, 8, 0))
  ```

* Override the default encoders and decoders.

  This way, you have complete control over how to encode and decode at field level.

  ```python
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

  Obj(elems=["a", "b", "c"]).json()  # => {'elems': 'a,b,c'}
  Obj.from_json({"elems": "a,b,c"})  # => Obj(elems=['a', 'b', 'c'])
  ```

  The following code snippet about `datetime` is a very common example,
  you might want ISO format datetime conversion over timestamp integers.

  ```python
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

  Record().json()  # => {'created_at': '2022-08-09T23:23:02.543007'}
  ```

* For some very narrow scenarios, we may need to execute a hook function before decoding,
  for example, the data to be decoded is a serialized json string,
  and but we still want to use the built-in decoder functions instead of making a new decoder.

  ```python
  import json

  @dataclass
  class Obj(J):
      data: Dict[str, Any] = field(metadata={"j": json_options(before_decoder=json.loads)})

  Obj.from_json({"data": '{"k": "v"}'})
  # => Obj(data={'k': 'v'})
  ```

* Customize default behaviors at the class level.

  If an option is not explicitly set at the field level,
  the `__default_json_options__` provided at the class level will be attempted.

  ````python
  @dataclass
  class Obj(J):
      __default_json_options__ = json_options(omitempty=True)

      a: Optional[int] = None
      b: Optional[str] = None

  Obj(b="b").json() # => {'b': 'b'}
  ````

  ```python
  @dataclass
  class Obj(J):
      __default_json_options__ = json_options(name_converter=to_camel_case)

      status_code: int
      simple_value: str

  Obj2(status_code=1, simple_value="simple").json()
  # => {"statusCode": 1, "simpleValue": "simple"}
  ```

## Debuging

It provides a method `obj._get_origin_json()`,
it returns the original json dictionary which constructs instance `obj` via `from_json()`.

```python
d = {"a": 1}
obj = Obj.from_json(d)
obj._get_origin_json()
# => {"a": 1}
```

## License

BSD.
