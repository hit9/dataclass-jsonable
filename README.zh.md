# dataclass-jsonable

[![dataclass-jsonable ci](https://github.com/hit9/dataclass-jsonable/actions/workflows/ci.yml/badge.svg)](https://github.com/hit9/dataclass-jsonable/actions/workflows/ci.yml)
![](https://img.shields.io/badge/license-BSD3-brightgreen)

dataclass-jsonable 是简单灵活的、在 dataclass 和 可 JSON 化字典转换的 Python 库。

它将 dataclasses 映射到可 JSON 编码的字典，而不是 JSON 字符串。

## 特点

* 好用
* 支持大部分常见类型标注
* 支持递归转换
* 支持字段级别和 dataclass 级别的行为重载

## 安装

要求 Python >= 3.7

通过 `pip` 安装:

```
pip install dataclass-jsonable
```

## 快速示例

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

# 编码到 json 字典
d = box.json()
print(d)  # {'pens': [{'color': 1, 'price': '20.1', 'produced_at': 1660023062}]}

# 从 json 字典构造一个 dataclass
print(Box.from_json(d))
```

API 只有两个: `.json()` and `.from_json()`.

## 内置支持的类型

* `bool`, `int`, `float`, `str`, `None` 的转换不变.

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

* `Decimal` 编码到 `str`.

  ```python
  @dataclass
  class Obj(J):
      a: Decimal

  Obj(a=Decimal("3.1")).json()  # => {'a': '3.1'}
  ```

* `datetime` 通过 `.timestamp()` 方法编码到时间戳整数.
  `timedelta` 通过 `.total_seconds()` 方法编码到整数.

  ```python
  @dataclass
  class Obj(J):
      a: datetime
      b: timedelta

  Obj(a=datetime.now(), b=timedelta(minutes=1)).json()
  # => {'a': 1660062019, 'b': 60}
  ```

* `Enum` 和 `IntEnum` 通过 `.value` 属性编码到枚举值:

  ```python
  @dataclass
  class Obj(J):
      status: Status

  Obj(status=Status.DONE).json()  # => {'status': 1}
  ```

* `Any` 根据自身类型编码:

  ```python
  @dataclass
  class Obj(J):
      a: Any

  Obj(1).json()  # {'a': 1}
  Obj("a").json()  # {'a': 'a'}
  Obj.from_json({"a": 1})  # Obj(a=1)
  ```

* `Optional[X]` 是支持的, 但是一般的 `Union[X, Y, ...]` 不被支持:

  ```python
  @dataclass
  class Obj(J):
      a: Optional[int] = None

  Obj(a=1).json()  # => {'a': 1}
  ```

* `List[X]`, `Tuple[X]`, `Set[X]` 将全部映射到 `list`:

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

* `Dict[str, X]` 映射到 `dict`:

  ```python
  @dataclass
  class Obj(J):
      a: Dict[str, int]
  Obj(a={"x": 1}).json()  # => {'a': {'x': 1}}
  Obj.from_json({"a": {"x": 1}}) # => Obj(a={'x': 1})
  ```

* 嵌套的 `JSONAble` (或者叫 `J`) dataclasses:

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

* 后置定义的字符串类型注解 ([PEP 563](https://www.python.org/dev/peps/pep-0563/) 中的 `ForwardRef`).

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

如果这些内置的默认转换规则无法满足需求，或者你的类型不在其中，你仍然可以采用 [json_options](#customization--overriding-examples)  来自定义转换规则。

## 自定义 / 重载 示例

我们可以通过 `json_options` 来重载默认的转换行为，它通过 dataclass 的 metadata 来支持字段级别的自定义目的，
其命名空间是 `j`.

以下的伪代码以说明模式:

```python
from dataclasses import field
from dataclass_jsonable import json_options

@dataclass
class Struct(J):
    attr: T = field(metadata={"j": json_options(**kwds)})
```

一些使用 `json_options` 的示例:

* 采用一个自定义的字典键，而不是默认的字段名:

   ```python
   @dataclass
   class Person(J):
       attr: str = field(metadata={"j": json_options(name="new_attr")})
   Person(attr="value").json() # => {"new_attr": "value"}
   ```

  而且，我们甚至可以用一个函数来自定义这个字典键。
  在和 class 级别的 `__default_json_options__` 属性一起时，会很有用 (后续会讲到).

  ```python
  @dataclass
  class Obj(J):
      simple_value: int = field(metadata={"j": json_options(name_converter=to_camel_case)})
  Obj(simple_value=1).json()  # => {"simpleValue": 1}
  ```

  我们也可以指明自定义的命名转换器, 从字典到 dataclass, 或者反过来:

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

  比如上面的 `Person` class, 转换到字典可以是 `{"Name": "Jack"}`, 可以从 `{"nickname": "Jack"}` 构造而来。

* 如果一个字段的值是空的，那么在转换时忽略它:

   ```python
   @dataclass
   class Book(J):
       name: str = field(metadata={"j": json_options(omitempty=True)})
   Book(name="").json() # => {}
   ```

  进一步地，我们可以定义什么叫做 '空的', 通过设置  `omitempty_tester`:

   ```python
   @dataclass
   class Book(J):
       attr: Optional[str] = field(
           default=None,
           metadata={
               # 默认地，我们测试 `空` 是通过 `not x`
               "j": json_options(omitempty=True, omitempty_tester=lambda x: x is None)
           },
       )

   Book(attr="").json()  # => {'attr': ''}
   Book(attr=None).json()  # => {}
   ```

* 总是跳过一个字段. 这样我们可以忽略一些 "私有" 字段转换到 JSON:

   ```python
   @dataclass
   class Obj(J):
       attr: str = field(metadata={"j": json_options(skip=True)})

   Obj(attr="private").json() # => {}
   ```

* dataclasses 的 `field` 允许我们传入 `default` 或者 `default_factory` 参数来设置默认字段值:

  ```python
  @dataclass
  class Obj(J):
      attr: List[str] = field(default_factory=list, metadata={"j": json_options(**kwds)})
  ```

  dataclass-jsonable 提供了一个类似的选项叫做 `default_before_decoding`.
  在解码前，如果一个字段的字典键是缺失的，它可以指明默认值用什么。有时候这种方式指明默认值更简洁:

  ```python
  @dataclass
  class Obj(J):
      updated_at: datetime = field(metadata={"j": json_options(default_before_decoding=0)})

  Obj.from_json({})  # => Obj(updated_at=datetime.datetime(1970, 1, 1, 8, 0))
  ```

  dataclass-jsonable 也有一个 class 级别的选项叫做 `__default_factory__`.
  如果一个字段没有定义 `default` 或者 `default_factory` 参数, 也没有使用 `default_before_decoding` 选项,
  这个函数就会根据字段的类型给它生成一个默认值, 来防止在构造实例时出现 "missing positional arguments" 之类的错误:

  ```python
  from dataclass_jsonable import J, zero

  @dataclass
  class Obj(J):
      # 默认都采用零值
      __default_factory__ = zero

      n: int
      s: str
      k: List[str]

  Obj.from_json({})  # => Obj(n=0, s='', k=[])
  ```

* 重载默认的编码和解码函数

  如此，对于如何编解码的转换函数，你可以完全掌控:

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

  下面的关于 `datetime` 的代码示例采用 ISO 格式而非默认的时间戳:

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

* 对于一些非常少见的场景，我们需要在解码前执行一些动作，比如，一些要解码的数据是序列化的 json 字符串，
  但是我们仍然希望沿用默认的解码函数而不想自己写一个解码函数，比如说：

  ```python
  import json

  @dataclass
  class Obj(J):
      data: Dict[str, Any] = field(metadata={"j": json_options(before_decoder=json.loads)})

  Obj.from_json({"data": '{"k": "v"}'})
  # => Obj(data={'k': 'v'})
  ```

* 自定义类级别的 `json_options` 选项.

  如果一个字段没有明确设置字段级别的 `json_options` 选项，就会降级采用这个类上的 `json_options`.

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

每一个由 dataclass-jsonable 构造而来的 dataclass 实例，都有个方法 `obj._get_origin_json()`,
它返回通过 `from_json()` 构造这个实例的原始的 json 字典。

```python
d = {"a": 1}
obj = Obj.from_json(d)
obj._get_origin_json()
# => {"a": 1}
```

## License

BSD.
