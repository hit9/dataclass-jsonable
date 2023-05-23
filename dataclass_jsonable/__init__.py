"""
Simple and flexible conversions between dataclasses and jsonable dictionaries.

Requires: Python >= 3.7

Supported type annotations:

    bool, int, float, str, Decimal, datetime, timedelta, Enum, IntEnum
    Any, Optional[X]
    List[X], Tuple[X, ...], Set[X], Dict[str, X],
    JSONAble (nested)
"""
import enum
from dataclasses import MISSING, dataclass, is_dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from types import MappingProxyType
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
    get_type_hints,
)

__all__ = ("json_options", "JSONAble", "JSON", "J", "zero")

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

# Function that converts a field's name.
NameConverter = Callable[[str], str]

# TypingHint
TypingHint = Any

# Function that gives a default value according to a typing hint.
DefaultFactory = Callable[[TypingHint], V]


class Action(enum.IntEnum):
    ENCODING = 1
    DECODING = 2


@dataclass
class json_options:
    """Field-level options to override the default conversion behavior.
    For each option, leaving `None` means not-set.
    """

    # Custom key to be mapping in the dictionary.
    # Uses the name of this field by default.
    name: Optional[str] = None

    # A list of possible names for this field when converting to dataclass.
    # It will match in order, the first matched name will be used.
    # The first name in the list will be used when converting to json.
    name_choice: Optional[List[str]] = None

    # A function that returns a custom key to be mapping in the dictionary
    #   whenever converting to dictionary or dataclass.
    # This option is similar to option `name`, but it's a function rather than a string.
    # If the option `name` is set the same time, prefers `name` over `name_converter`.
    name_converter: Optional[NameConverter] = None

    # This option is similar to option `name_converter`,
    #   but only used when converting dictionary to dataclass.
    # If this option is not set, default to use `name_converter`.
    # If the option `name` is set the same time, prefers `name` over `name_inverter`.
    name_inverter: Optional[NameConverter] = None

    # Omit this field if it has an empty value, defaults to False.
    # This option is only about encoding.
    omitempty: Optional[bool] = None

    # Function to test whether a value can be called "empty".
    # Defaults to `lambda x: not x`.
    omitempty_tester: Optional[Tester] = None

    # Always skip this field during conversions, defaults to False.
    # Field the marks to be skipped, will eventually left to a zero value.
    skip: Optional[bool] = False

    # Default value before decoding, if the key is missing in the dictionary.
    # This option is only decoding.
    # Setting this to None means this option should be ignored.
    default_before_decoding: Optional[V] = None
    # Backward compatiable, the same of default_before_decoding.
    default_on_missing: Optional[V] = None

    # Custom encoder function, to be called like: encoder(field_value).
    # Uses `get_encoder` to get the default encoder function by annotated type.
    encoder: Optional[F] = None
    # Alias name for `encoder` option.
    to_json: Optional[F] = None

    # Custom decoder function, to be called like: decoder(dict_value).
    # Uses `get_decoder` to get the default decoder function by annotated type.
    decoder: Optional[F] = None
    # Alias name for `decoder` option.
    from_json: Optional[F] = None

    # Hook function to be executed before decoder's execution.
    # The decoding looks like `before_decoder(decoder(dict_value))` if this option is set.
    # Although this feature can be achieved by a new `decoder` function, but it's more
    # convenient to work with the builtin decoder functions.
    before_decoder: Optional[F] = None

    def __post_init__(self):
        # Handle alias options
        if self.encoder is None:
            self.encoder = self.to_json
        if self.decoder is None:
            self.decoder = self.from_json
        if self.default_before_decoding is None:
            self.default_before_decoding = self.default_on_missing


_BASIC_TYPES = {  # Ensures callable
    int,
    float,
    str,
    bool,
    list,
    dict,
    set,
    tuple,
    Decimal,
}


def zero(t) -> V:
    """
    Returns the zero value according to the  given type annoation `t`
    """
    if t in _BASIC_TYPES:
        return t()
    if t is type(None):
        return None
    if t is datetime:
        return datetime.fromtimestamp(0)
    if t is timedelta:
        return timedelta(seconds=0)
    if t is Any:
        return None
    if isinstance(t, type) and issubclass(t, Enum):
        # pick one or raise
        return list(t.__members__.values())[0]
    if _is_generics(t):
        # Generics like `list[int]`, recursively deep its original type to zero
        ot = _get_generics_origin(t)
        args = _get_generics_args(t)

        if ot is Union:
            # Not support Union[X, Y, Z, ...]
            if len(args) != 2 or args[1] is not type(None):
                raise NotImplementedError("only Optional[X] union type is supported")
            # Optional[E]
            return None

        return zero(ot)
    if isinstance(t, type) and issubclass(t, J):
        # J
        return t.from_json({})  # type: ignore
    if is_dataclass(t):
        # dataclasses
        return t()
    raise NotImplementedError(f"not supported type {t}")


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

    # Class level `default_factory` option.
    #
    # During a `from_json` calling, if a field's key is missing in the given dictionary,
    # and at the same time there's no default value or default_factory declared for this field,
    # and `default_before_decoding` option is neither used, then a "missing positional argument"
    # TypeError will finally raise.
    #
    # The standard dataclasses library provides field-level field keyword `default` and `default_factory` to
    # prevent this error. Here dataclasses-jsonable provides a class-level `default_factory`. Which is invoked
    # only if the field has no `default` value or `default_factory` function declared. In another say, the
    # field-level default and default_factory can overide this class-level `__default_factory__`.
    #
    # The default `__default_factory__` is function `zero`, which gives a zero value according to the field's
    # type.
    # Setting this to `None` to disable this option.
    __default_factory__: ClassVar[Optional[DefaultFactory]] = None

    def _get_origin_json(self) -> JSON:
        """Debug purpose method to return the original JSON dictionary which constructs this instance via
        `from_json` method.
        """
        return getattr(self, "__dataclass_origin_json__")

    @classmethod
    def get_encoder(cls, t) -> F:
        """Returns an encoder function for given type `t`.
        A encoder function encodes the field's value to a jsonable value.
        Raises `NotImplementedError` if given type is not supported.
        You can override this function by declaring a subclass that extends `JSONAble`.
        """
        if t is type(None):
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
        elif t is list:
            # list of elements.
            return lambda x: [cls.get_encoder(type(e))(e) for e in x]
        elif t is set:
            # set of elements
            return lambda x: {cls.get_encoder(type(e))(e) for e in x}
        elif t is dict:
            # dict
            return _encode_dict
        elif _is_generics(t) and _get_generics_origin(t) in {list, set}:
            # List[E] / Set[E]
            args = _get_generics_args(t)
            f = cls.get_encoder(args[0])
            return lambda x: [f(e) for e in x]
        elif _is_generics(t) and _get_generics_origin(t) is tuple:
            args = _get_generics_args(t)
            if len(args) == 2 and args[1] is Ellipsis:
                # Tuple[E, ...]
                f = cls.get_encoder(args[0])
                return lambda x: [f(e) for e in x]
            # Tuple[E1, E2, E3]
            return lambda x: [cls.get_encoder(args[i])(e) for i, e in enumerate(x)]
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
        if t is type(None):
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
            return _decode_decimal
        elif t is datetime:
            return _decode_datetime
        elif t is timedelta:
            return _decode_timedelta
        elif t is Any:
            # Any returns reflection decoding.
            return lambda x: cls.get_decoder(type(x))(x)
        elif t is list:
            # list of elements.
            return lambda x: [cls.get_decoder(type(e))(e) for e in x]
        elif t is set:
            # set of elements
            return lambda x: {cls.get_decoder(type(e))(e) for e in x}
        elif t is dict:
            # dict
            return _encode_dict
        elif isinstance(t, type) and issubclass(t, Enum):
            return t
        elif _is_jsonable_like(t):
            # Nested
            return lambda x: t.from_json(x)  # type: ignore
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
        elif _is_generics(t) and _get_generics_origin(t) is tuple:
            args = _get_generics_args(t)
            if len(args) == 2 and args[1] is Ellipsis:
                # Tuple[E, ...]
                f = cls.get_decoder(args[0])
                return lambda x: tuple(f(e) for e in x)
            # Tuple[E1, E2, E3]
            return lambda x: tuple(cls.get_decoder(args[i])(e) for i, e in enumerate(x))
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
        The result will be cached in this field's metadata as key `_dataclass_jsonable_j`.
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

    @classmethod
    def _get_typing_hint_by_field(cls, f):
        """Get typing hint for given field.
        Notes that `f.type` may be a string or ForwardRef.
        `get_type_hints` will evaluate them.
        """
        return get_type_hints(cls)[f.name]

    def json(self) -> JSON:
        """Converts this dataclass instance to a dictionary recursively."""

        d: JSON = {}

        __name_choice_map = getattr(self, "__name_choice_map", None)
        for name, f in self.__dataclass_fields__.items():
            t = self._get_typing_hint_by_field(f)
            if _is_class_var(t):
                # ClassVar should be skipped.
                continue

            v = getattr(self, name)  # Field's value
            options = self._get_json_options(f)

            if options.skip:
                continue

            if options.omitempty:
                omitempty_tester = options.omitempty_tester or _default_omitempty_tester
                if omitempty_tester(v):
                    continue

            # Key in dictionary `d`.
            k = _util_get_field_keys(
                name=name,
                options=options,
                action=Action.ENCODING,
                choice_map=__name_choice_map,
            )[0]

            # Encode.
            encoder = options.encoder or self.get_encoder(t)
            d[k] = encoder(v)

        return d

    # An alias for `json`
    to_json = json

    @classmethod
    def from_json(cls: Type[T], d: JSON) -> T:
        """Constructs an instance of this dataclass from given jsonable dictionary."""

        # Arguments for class `cls()`.
        kwds = {}

        _name_choice_map = {}

        for name, f in cls.__dataclass_fields__.items():
            t = cls._get_typing_hint_by_field(f)
            if _is_class_var(t):
                # ClassVar should be skipped.
                continue

            options = cls._get_json_options(f)

            # Key in dictionary.
            ks = _util_get_field_keys(name, options, Action.DECODING)
            if options.skip:
                continue

            # Find the first key in dictionary `d` that is in `ks`.
            k = None
            for _k in ks:
                if _k in d:
                    k = _k
                    # record the key in dictionary `d` for this field.
                    _name_choice_map[name] = k
                    break

            if k is None:
                # Key is missing in dictionary.
                default = options.default_before_decoding
                if default is not None:
                    # Gives a default value before decoding.
                    v = default
                else:
                    # Just continue going if the value is missing.
                    # An error like "missing 1 required positional argument" will be raised if this field doesn't
                    # have a default value declared.
                    continue
            else:
                # Value in dictionary `d`.
                v = d[k]

            if options.omitempty:
                # Omit if the value from dictionary is empty.
                omitempty_tester = options.omitempty_tester or _default_omitempty_tester
                if omitempty_tester(v):
                    continue

            # Call hook function if provided.
            if options.before_decoder:
                v = options.before_decoder(v)

            # Obtain the decoder function.
            decoder = options.decoder or cls.get_decoder(t)
            kwds[name] = decoder(v)

        # Sets default value.
        if cls.__default_factory__ is not None:
            for name, f in cls.__dataclass_fields__.items():
                if f.default is MISSING and f.default_factory is MISSING:
                    # No default value and default_factory set.
                    t = cls._get_typing_hint_by_field(f)
                    if _is_class_var(t):
                        # ClassVar should be skipped.
                        continue
                    kwds.setdefault(name, cls.__default_factory__(t))

        inst = cls(**kwds)
        setattr(inst, "__dataclass_origin_json__", d)
        setattr(inst, "__name_choice_map", _name_choice_map)
        return inst  # type: ignore


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
_decode_decimal = lambda x: Decimal(str(x))

_default_omitempty_tester = lambda x: not x


def _encode_dict(x):
    for k in x:
        if not isinstance(k, str):
            raise NotImplementedError("dict with non-str keys is not supported")
    return {k: JSONAble.get_encoder(type(v))(v) for k, v in x.items()}


def _decode_dict(x):
    for k in x:
        if not isinstance(k, str):
            raise NotImplementedError("dict with non-str keys is not supported")
    return {k: JSONAble.get_decoder(type(v))(v) for k, v in x.items()}


# Utils
def _is_generics(t) -> bool:
    """Returns whether the given type `t` is a generics type."""
    return hasattr(t, "__origin__") and hasattr(t, "__args__")


def _get_generics_origin(t):
    return getattr(t, "__origin__", None)


def _get_generics_args(t):
    """Returns the arguments that build the given type `t`."""
    return getattr(t, "__args__", tuple())


def _is_jsonable_like(t) -> bool:
    """Returns whether the given type `t` is like a `JSONAble` dataclass."""
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


def _is_class_var(t) -> bool:
    if t is ClassVar:
        return True
    if _is_generics(t) and _get_generics_origin(t) is ClassVar:
        return True
    return False


def _util_get_field_keys(
    name: str,
    options: json_options,
    action: Action,
    choice_map: Optional[JSON] = None,
) -> List[str]:
    """A util function returns the `key` in target dictionary.
    :param name: the field's name.
    :param options: the json_options for this field.
    """
    if options.name:
        return [options.name]

    if action == Action.DECODING and options.name_choice:
        # get the candidates for this field.
        return options.name_choice + [name]

    if action == Action.ENCODING and choice_map and name in choice_map:
        # if the name is chosen from `name_choice`, use the chosen name.
        # else use the original name.
        return [choice_map[name]]

    if action == Action.DECODING and options.name_inverter:
        return [options.name_inverter(name)]

    if options.name_converter:
        return [options.name_converter(name)]

    return [name]
