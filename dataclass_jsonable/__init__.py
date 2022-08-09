"""
Simple, practical and overridable conversions between dataclasses
and jsonable dictionaries.

Requires: Python >= 3.7

Supported type annotation X:

    bool int float str Decimal datetime timedelta
    Any Optional[X]
    List[X] Tuple[X] Set[X] Dict[str, X]
    JSONAble (nested)
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from types import MappingProxyType
from typing import Any, Callable, Dict, Optional, TypeVar, Union

__all__ = ("json_options", "JSONAble", "JSON", "J")

# Any value, in short.
V = Any

# Jsonable dataclasses, bound to JSONAble.
T = TypeVar("T", bound="JSONAble")

# encoder/decoder function.
F = Callable[[V], V]

# Function that tests a value.
# Returns a bool and accepts a given argument.
Tester = Callable[[V], bool]

# Jsonable dictionary.
JSON = Dict[str, V]


@dataclass(frozen=True)
class json_options:
    """Field-level options to override the default conversion behavior.
    For each option, leaving `None` means not-set.
    """

    # Custom key to be mapping in the dictionary.
    # Uses the name of this field by default.
    name: Optional[str] = None

    # Omit this field if it has an empty value, defaults to False.
    # This option is only about encoding.
    omitempty: Optional[bool] = None

    # Function to test whether a value can be called "empty".
    # Defaults to `lambda x: not x`.
    omitempty_tester: Optional[Tester] = None

    # Always skip this field during conversions, defaults to False.
    skip: Optional[bool] = False

    # Default value before decoding, if the key is missing in the dictionary.
    # This option is only decoding.
    # Setting this to None means this option should be ignored.
    default_on_missing: Optional[V] = None

    # Custom encoder function, to be called like: encoder(field_value).
    # Uses `get_encoder` to get the default encoder function by annotated type.
    encoder: Optional[F] = None

    # Custom encoder function, to be called like: decoder(dict_value).
    # Uses `get_decoder` to get the default decoder function by annotated type.
    decoder: Optional[F] = None


@dataclass
class JSONAble:
    """Base of jsonable dataclass."""

    # Default json_options for this dataclass.
    #
    # Override this variable to achieve class-level custom behaviors. For example,
    # setting this to `json_options(omitempty=True)` means that by default, each field
    # will be omitted if its value is empty.
    #
    # Further, we can still override class-level `__default_json_options__` options by
    # field-level json_options. For each option, we first checkout it in the field-level
    # json_options (if declared), and then in the class-level `__default_json_options__`.
    __default_json_options__ = json_options()

    @classmethod
    def get_encoder(cls, t) -> F:
        """Returns an encoder function for given type `t`.
        A encoder function encodes the field's value to a jsonable value.
        Raises `NotImplementedError` if given type is not supported.
        You can override this function by declaring a subclass that extends `JSONAble`.
        """
        if t is None:
            return _encode_None
        elif t is bool:
            return bool
        elif t is str:
            return str
        elif t is int:
            return int
        elif t is float:
            return float
        elif t is Decimal:
            return str
        elif t is datetime:
            return _encode_datetime
        elif t is timedelta:
            return _encode_timedelta
        elif isinstance(t, type) and issubclass(t, Enum):
            return _encode_enum
        elif t is Any:
            # Any runs reflection encoding.
            return lambda x: cls.get_encoder(type(x))(x)
        elif _is_jsonable_like(t):
            # Nested
            return _encode_jsonable
        elif _is_generics(t) and _get_generics_origin(t) is list:
            # List[E]
            args = _get_generics_args(t)
            f = cls.get_encoder(args[0])
            return lambda x: [f(e) for e in x]
        elif _is_generics(t) and _get_generics_origin(t) is set:
            # Set[E]
            args = _get_generics_args(t)
            f = cls.get_encoder(args[0])
            return lambda x: {f(e) for e in x}
        elif _is_generics(t) and _get_generics_origin(t) is set:
            # Tuple[E]
            args = _get_generics_args(t)
            f = cls.get_encoder(args[0])
            return lambda x: tuple(f(e) for e in x)
        elif _is_generics(t) and _get_generics_origin(t) is dict:
            # Dict[K, E]
            args = _get_generics_args(t)
            if args[0] is not str:
                raise NotImplementedError("dict with non-str keys is not supported")
            # Dict[str, E]
            f = cls.get_encoder(args[1])
            return lambda x: {str(k): f(v) for k, v in x.items()}
        elif _is_generics(t) and _get_generics_origin(t) is Union:
            # Union[A, B, C, D]
            args = _get_generics_args(t)
            if len(args) != 2 or args[1] is not type(None):
                raise NotImplementedError("only Optional[X] union type is supported")
            # Optional[E]
            f = cls.get_encoder(args[0])
            return lambda x: None if x is None else f(x)
        raise NotImplementedError(f"get_encoder not support type {t}")

    @classmethod
    def get_decoder(cls, t) -> F:
        """Returns an decoder function for given type.
        A decoder function decodes the value from dictionary onto this field.
        Raises `NotImplementedError` if given type is not supported.
        You can override this function by declaring a subclass that extends `JSONAble`.
        """
        if t is None:
            return _decode_None
        elif t is bool:
            return bool
        elif t is str:
            return str
        elif t is int:
            return int
        elif t is float:
            return float
        elif t is Decimal:
            return Decimal
        elif t is datetime:
            return _decode_datetime
        elif t is timedelta:
            return _decode_timedelta
        elif t is Any:
            # Any returns reflection decoding.
            return lambda x: cls.get_decoder(type(x))(x)
        elif isinstance(t, type) and issubclass(t, Enum):
            return t
        elif _is_jsonable_like(t):
            # Nested
            return lambda x: t.from_json(x)
        elif _is_generics(t) and _get_generics_origin(t) is list:
            # List[E]
            args = _get_generics_args(t)
            f = cls.get_decoder(args[0])
            return lambda x: [f(e) for e in x]
        elif _is_generics(t) and _get_generics_origin(t) is set:
            # Set[E]
            args = _get_generics_args(t)
            f = cls.get_decoder(args[0])
            return lambda x: {f(e) for e in x}
        elif _is_generics(t) and _get_generics_origin(t) is set:
            # Tuple[E]
            args = _get_generics_args(t)
            f = cls.get_decoder(args[0])
            return lambda x: tuple(f(e) for e in x)
        elif _is_generics(t) and _get_generics_origin(t) is dict:
            # Dict[K, E]
            args = _get_generics_args(t)
            if args[0] is not str:
                raise NotImplementedError("dict with non-str keys is not supported")
            # Dict[str, E]
            f = cls.get_decoder(args[1])
            return lambda x: {str(k): f(v) for k, v in x.items()}
        elif _is_generics(t) and _get_generics_origin(t) is Union:
            # Union[A, B, C, D]
            args = _get_generics_args(t)
            if len(args) != 2 or args[1] is not type(None):
                raise NotImplementedError("only Optional[X] union type is supported")
            # Optional[E]
            f = cls.get_decoder(args[0])
            return lambda x: None if x is None else f(x)
        raise NotImplementedError(f"get_decoder not support type {t}")

    @classmethod
    def _get_json_options(cls, f) -> json_options:
        """Internal method to help to get the right json_options to use for given field `f`.
        For each field, we firstly checkout field-level json_options, if declared. And then
        the class-level json_options.
        The result will be cached as `_dataclass_jsonable_j` in the field.
        """
        k = "_dataclass_jsonable_j"

        # Check cache at first.
        if k in f.metadata:
            return f.metadata[k]

        # Initial json_options from class-level json_options.
        options = cls.__default_json_options__

        # Field-level declared json_options, may be None.
        field_options = f.metadata.get("j")

        if field_options:
            # Update options with field_options.

            # kwds1 is arguments that were set in field_options.
            kwds1 = {k: v for k, v in field_options.__dict__.items() if v is not None}
            # kwds2 is arguments that were set at class-level.
            kwds2 = {k: v for k, v in options.__dict__.items() if v is not None}
            # kwds1 first (aka field-level options first).
            kwds2.update(kwds1)
            # And we should make a new json_options.
            options = json_options(**kwds2)

        # Cache this result in field.metadata.
        f.metadata = _replace_mapping_proxy(f.metadata, {k: options})
        return options

    def json(self) -> JSON:
        """Converts this dataclass instance to a dictionary recursively."""

        d: JSON = {}

        for name, f in self.__dataclass_fields__.items():
            t = f.type  # Field's type annotated
            v = getattr(self, name)  # Field's value
            options = self._get_json_options(f)

            if options.skip:
                continue

            if options.omitempty:
                omitempty_tester = options.omitempty_tester or _default_omitempty_tester
                if omitempty_tester(v):
                    continue

            # Key in dictionary `d`.
            k = options.name or name

            # Encode.
            encoder = options.encoder or self.get_encoder(t)
            d[k] = encoder(v)

        return d

    @classmethod
    def from_json(cls, d: JSON) -> T:
        """Constructs an instance of this dataclass from given jsonable dictionary."""

        # Arguments for class `cls()`.
        kwds = {}

        for name, f in cls.__dataclass_fields__.items():
            t = f.type  # Field's type annotated.

            options = cls._get_json_options(f)

            # Key in dictionary.
            k = options.name or name

            if options.skip:
                continue

            v = None

            if k not in d:
                # Key is missing in dictionary.
                default_on_missing = options.default_on_missing
                if default_on_missing is not None:
                    # Gives a default value before decoding.
                    v = default_on_missing
                else:
                    # Just continue going if the value is missing.
                    # An error like "missing 1 required positional argument" will be raised if this field doesn't
                    # have a default value declared.
                    continue

            # Value in dictionary `d`.
            if v is None:
                v = d[k]

            # Obtain the decoder function.
            decoder = options.decoder or cls.get_decoder(t)
            kwds[name] = decoder(v)

        return cls(**kwds)  # type: ignore


J = JSONAble  # short alias


# Makes some encoder/decoder function be static.

_encode_datetime = lambda x: int(x.timestamp())
_encode_timedelta = lambda x: int(x.total_seconds())
_encode_enum = lambda x: x.value
_encode_None = lambda _: None
_encode_jsonable = lambda x: x.json()
_decode_datetime = lambda x: datetime.fromtimestamp(int(x))
_decode_timedelta = lambda x: timedelta(seconds=int(x))
_decode_None = lambda _: None

_default_omitempty_tester = lambda x: not x

# Utils
def _is_generics(t) -> bool:
    return hasattr(t, "__origin__") and hasattr(t, "__args__")


def _get_generics_origin(t):
    return getattr(t, "__origin__", None)


def _get_generics_args(t):
    return getattr(t, "__args__", tuple())


def _is_jsonable_like(t) -> bool:
    if isinstance(t, type):
        if issubclass(t, JSONAble):
            return True
        if hasattr(t, "from_json") and hasattr(t, "json"):
            # `t` has from_json and json methods defined.
            return True
    return False


def _replace_mapping_proxy(m: MappingProxyType, kwds) -> MappingProxyType:
    """Copy a MappingProxyType `m`, and update it with `kwds`."""
    d = dict(m)
    d.update(**kwds)
    return MappingProxyType(d)
