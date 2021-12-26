"""Common data structures for testing."""
# pylint: disable=missing-docstring,no-self-use
from typing import Any


class SomeClass:
    ATTR = "class_attr"

    def __init__(self) -> None:
        self.attr = "instance_attr"

    def _private(self) -> str:
        return "private_value"

    def __very_private(self) -> str:  # pylint: disable=unused-private-member
        return "very_private_value"

    def instance_method(self) -> str:
        return self.attr

    async def async_instance_method(self) -> str:
        return self.attr

    def instance_method_with_args(self, arg1: int) -> int:
        return arg1

    async def async_instance_method_with_args(self, arg1: int) -> int:
        return arg1

    @classmethod
    def class_method(cls) -> str:
        return cls.ATTR

    @classmethod
    def class_method_with_args(cls, arg1: int) -> int:
        return arg1

    @classmethod
    async def async_class_method(cls) -> str:
        return cls.ATTR

    @classmethod
    async def async_class_method_with_args(cls, arg1: int) -> int:
        return arg1

    @staticmethod
    def static_method() -> str:
        return "static_value"

    @staticmethod
    def static_method_with_args(arg1: int) -> int:
        return arg1

    @staticmethod
    async def async_static_method() -> str:
        return "static_value"

    @staticmethod
    async def async_static_method_with_args(arg1: int) -> int:
        return arg1

    @property
    def some_property(self) -> str:
        return self.attr


class DerivedClass(SomeClass):
    pass


class Proxy:
    """Proxy to another object.

    This can be used to test mocking proxied objects.

    Code from OBJECT PROXYING (PYTHON RECIPE):
    https://code.activestate.com/recipes/496741-object-proxying/
    """

    def __init__(self, obj: Any) -> None:
        object.__setattr__(self, "_obj", obj)

    def __getattribute__(self, name: str) -> Any:
        return getattr(object.__getattribute__(self, "_obj"), name)

    def __delattr__(self, name: str) -> None:
        delattr(object.__getattribute__(self, "_obj"), name)

    def __setattr__(self, name: str, value: Any) -> None:
        setattr(object.__getattribute__(self, "_obj"), name, value)

    def __nonzero__(self) -> bool:
        return bool(object.__getattribute__(self, "_obj"))

    def __str__(self) -> str:
        return str(object.__getattribute__(self, "_obj"))

    def __repr__(self) -> str:
        return repr(object.__getattribute__(self, "_obj"))

    _special_names = [
        "__abs__",
        "__add__",
        "__and__",
        "__call__",
        "__cmp__",
        "__coerce__",
        "__contains__",
        "__delitem__",
        "__delslice__",
        "__div__",
        "__divmod__",
        "__eq__",
        "__float__",
        "__floordiv__",
        "__ge__",
        "__getitem__",
        "__getslice__",
        "__gt__",
        "__hash__",
        "__hex__",
        "__iadd__",
        "__iand__",
        "__idiv__",
        "__idivmod__",
        "__ifloordiv__",
        "__ilshift__",
        "__imod__",
        "__imul__",
        "__int__",
        "__invert__",
        "__ior__",
        "__ipow__",
        "__irshift__",
        "__isub__",
        "__iter__",
        "__itruediv__",
        "__ixor__",
        "__le__",
        "__len__",
        "__long__",
        "__lshift__",
        "__lt__",
        "__mod__",
        "__mul__",
        "__ne__",
        "__neg__",
        "__oct__",
        "__or__",
        "__pos__",
        "__pow__",
        "__radd__",
        "__rand__",
        "__rdiv__",
        "__rdivmod__",
        "__reduce__",
        "__reduce_ex__",
        "__repr__",
        "__reversed__",
        "__rfloorfiv__",
        "__rlshift__",
        "__rmod__",
        "__rmul__",
        "__ror__",
        "__rpow__",
        "__rrshift__",
        "__rshift__",
        "__rsub__",
        "__rtruediv__",
        "__rxor__",
        "__setitem__",
        "__setslice__",
        "__sub__",
        "__truediv__",
        "__xor__",
        "next",
    ]

    @classmethod
    def _create_class_proxy(cls, theclass: Any) -> Any:
        """Creates a proxy for the given class."""

        def make_method(name: str) -> Any:
            def method(self: Any, *args: Any, **kwargs: Any) -> Any:
                return getattr(object.__getattribute__(self, "_obj"), name)(*args, **kwargs)

            return method

        namespace = {}
        for name in cls._special_names:
            if hasattr(theclass, name):
                namespace[name] = make_method(name)
        return type(f"{cls.__name__}({theclass.__name__})", (cls,), namespace)

    def __new__(cls, obj: Any, *args: Any, **kwargs: Any) -> Any:
        """Creates an proxy instance referencing `obj`.

        (obj, *args, **kwargs) are passed to this class' `__init__`, so deriving
        classes can define an __init__ method of their own.

        Note: `_class_proxy_cache` is unique per deriving class (each deriving
        class must hold its own cache).
        """
        try:
            cache = cls.__dict__["_class_proxy_cache"]
        except KeyError:
            cls._class_proxy_cache = cache = {}
        try:
            theclass = cache[obj.__class__]
        except KeyError:
            cache[obj.__class__] = theclass = cls._create_class_proxy(obj.__class__)
        ins = object.__new__(theclass)
        theclass.__init__(ins, obj, *args, **kwargs)
        return ins


def some_function(arg1: str) -> str:
    return arg1


async def some_async_function(arg1: str) -> str:
    return arg1
