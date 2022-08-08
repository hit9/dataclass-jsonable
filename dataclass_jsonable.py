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
            return lambda _: None
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
            return lambda x: int(x.timestamp())
        elif t is timedelta:
            return lambda x: int(x.total_seconds())
        elif isinstance(t, type) and issubclass(t, Enum):
            return lambda x: x.value
        elif isinstance(t, type) and issubclass(t, JSONAble):  # Nested
            return lambda x: x.json()
        elif getattr(t, "__origin__", None) is list:  # List[E]
            f = cls.get_encoder(t.__args__[0])  # type: ignore
            return lambda x: [f(e) for e in x]
        elif getattr(t, "__origin__", None) is set:  # Set[E]
            f = cls.get_encoder(t.__args__[0])  # type: ignore
            return lambda x: {f(e) for e in x}
        elif getattr(t, "__origin__", None) is tuple:  # Tuple[E]
            f = cls.get_encoder(t.__args__[0])  # type: ignore
            return lambda x: tuple(f(e) for e in x)
        raise NotImplementedError(f"get_encoder not support type {t}")

    @classmethod
    def get_decoder(cls, t) -> F:
        """Returns an decoder function for given type.
        A decoder function decodes the value from dictionary onto this field.
        Raises `NotImplementedError` if given type is not supported.
        You can override this function by declaring a subclass that extends `JSONAble`.
        """
        if t is None:
            return lambda _: None
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
            return lambda x: datetime.fromtimestamp(int(x))
        elif t is timedelta:
            return lambda x: timedelta(seconds=x)
        elif isinstance(t, type) and issubclass(t, Enum):
            return t
        elif isinstance(t, type) and issubclass(t, JSONAble):  # Nested
            return lambda x: t.from_json(x)
        elif getattr(t, "__origin__", None) is list:  # List[E]
            f = cls.get_decoder(t.__args__[0])  # type: ignore
            return lambda x: [f(e) for e in x]
        elif getattr(t, "__origin__", None) is set:  # Set[E]
            f = cls.get_decoder(t.__args__[0])  # type: ignore
            return lambda x: {f(e) for e in x}
        elif getattr(t, "__origin__", None) is tuple:  # Tuple[E]
            f = cls.get_decoder(t.__args__[0])  # type: ignore
            return lambda x: tuple(f(e) for e in x)
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
