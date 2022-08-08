"""
Simple, practical and overridable conversions between dataclasses
and jsonable dictionaries.

Requires: Python >= 3.7
Supported type annotation X:
    bool,int,float,str,Decimal,datetime,timedelta
    Any
    List[X],Tuple[X],Set[X],Dict[str, X]
    Optional[X]
    JSONAble (nested)
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Any, Callable, Dict, Optional, TypeVar

__all__ = ("json_options", "JSONAble", "JSON", "J")

# Any value, in short.
V = Any

# Jsonable dataclasses, bound to JSONAble.
T = TypeVar("T", bound="JSONAble")

# encoder/decoder function.
F = Callable[[V], V]

# Jsonable dictionary.
JSON = Dict[str, V]


@dataclass
class json_options:
    """Field-level options to override the default conversion behavior."""

    # Custom key to be mapping in the dictionary.
    # Uses the name of this field by default.
    name: Optional[str] = None

    # Omit this field if it has an empty value.
    # This option is only about encoding.
    omitempty: bool = False

    # Always skip this field during conversions.
    skip: bool = False

    # Default value before decoding, if the key is missing in the dictionary.
    # This option is only decoding.
    # Setting this to None means this option should be ignored.
    default_on_missing: V = None

    # Custom encoder function, to be called like: encoder(field_value).
    # Uses `get_encoder` to get the default encoder function by annotated type.
    encoder: Optional[F] = None

    # Custom encoder function, to be called like: decoder(dict_value).
    # Uses `get_decoder` to get the default decoder function by annotated type.
    decoder: Optional[F] = None


@dataclass
class JSONAble:
    """Base of jsonable dataclass."""

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
        elif isinstance(t, type) and issubclass(t, JSONAble):
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
        elif isinstance(t, type) and issubclass(t, JSONAble):
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
        raise NotImplementedError(f"get_decoder not support type {t}")

    def json(self) -> JSON:
        """Converts this dataclass instance to a dictionary recursively."""

        d: JSON = {}

        for name, f in self.__dataclass_fields__.items():
            t = f.type  # Field's type annotated
            v = getattr(self, name)  # Field's value
            opts = f.metadata.get("j") or json_options()

            if opts.skip:
                continue

            if opts.omitempty and not v:
                continue

            # Key in dictionary `d`.
            k = opts.name or name
            encoder = opts.encoder or self.get_encoder(t)
            d[k] = encoder(v)

        return d

    @classmethod
    def from_json(cls, d: JSON) -> T:
        """Constructs an instance of this dataclass from given jsonable dictionary."""

        # Arguments for class `cls()`.
        kwds = {}

        for name, f in cls.__dataclass_fields__.items():
            t = f.type  # Field's type annotated.
            opts = f.metadata.get("j") or json_options()
            # Key in dictionary.
            k = opts.name or name

            if opts.skip:
                continue

            v = None

            if k not in d:
                # Key is missing in dictionary.
                if opts.default_on_missing is not None:
                    # Gives a default value before decoding.
                    v = opts.default_on_missing
                else:
                    # Just continue going if the value is missing.
                    # An error like "missing 1 required positional argument" will be raised if this field doesn't
                    # have a default value declared.
                    continue

            # Value in dictionary `d`.
            if v is None:
                v = d[k]

            # Obtain the decoder function.
            decoder = opts.decoder or cls.get_decoder(t)
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

# Utils
def _is_generics(t) -> bool:
    return hasattr(t, "__origin__") and hasattr(t, "__args__")


def _get_generics_origin(t):
    return getattr(t, "__origin__", None)


def _get_generics_args(t):
    return getattr(t, "__args__", tuple())
