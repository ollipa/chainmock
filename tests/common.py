"""Common data structures for testing."""
# pylint: disable=missing-docstring,no-self-use


class SomeClass:
    ATTR = "class_attr"

    def __init__(self) -> None:
        self.attr = "instance_attr"

    def instance_method(self) -> str:
        return self.attr

    def instance_method_with_args(self, arg1: int) -> int:
        return arg1

    @classmethod
    def class_method(cls) -> str:
        return cls.ATTR

    @staticmethod
    def staticmethod() -> str:
        return "static_value"
