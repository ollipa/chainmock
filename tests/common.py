"""Common data structures for testing."""
# pylint: disable=missing-docstring,no-self-use


class SomeClass:
    ATTR = "class_attr"

    def __init__(self) -> None:
        self.attr = "instance_attr"

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


def some_function(arg1: str) -> str:
    return arg1


async def some_async_function(arg1: str) -> str:
    return arg1
