"""Re-exports from stdlib unittest.mock and extensions to it."""
from typing import Any, Type
from unittest.mock import (
    ANY,
    DEFAULT,
    FILTER_DIR,
    AsyncMock,
    MagicMock,
    Mock,
    NonCallableMagicMock,
    NonCallableMock,
    PropertyMock,
    call,
    create_autospec,
    mock_open,
    patch,
    seal,
    sentinel,
)

__all__ = [
    "ANY",
    "ANY_BOOL",
    "ANY_BYTES",
    "ANY_COMPLEX",
    "ANY_DICT",
    "ANY_FLOAT",
    "ANY_INT",
    "ANY_LIST",
    "ANY_SET",
    "ANY_STR",
    "ANY_TUPLE",
    "DEFAULT",
    "FILTER_DIR",
    "AnyOf",
    "AsyncMock",
    "MagicMock",
    "Mock",
    "NonCallableMagicMock",
    "NonCallableMock",
    "PropertyMock",
    "call",
    "create_autospec",
    "mock_open",
    "patch",
    "seal",
    "sentinel",
]


class AnyOf:  # pylint: disable=invalid-name
    """A helper object that compares equal to any given type."""

    def __init__(self, kind: Type[Any]) -> None:
        self._kind = kind

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self._kind)

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        return f"<ANY_{self._kind.__name__.upper()}>"


ANY_BOOL = AnyOf(bool)
ANY_BYTES = AnyOf(bytes)
ANY_COMPLEX = AnyOf(complex)
ANY_DICT = AnyOf(dict)
ANY_FLOAT = AnyOf(float)
ANY_INT = AnyOf(int)
ANY_LIST = AnyOf(list)
ANY_SET = AnyOf(set)
ANY_STR = AnyOf(str)
ANY_TUPLE = AnyOf(tuple)
