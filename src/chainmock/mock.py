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


class _ANY_TYPE:  # pylint: disable=invalid-name
    """A helper object that compares equal to any given type."""

    def __init__(self, kind: Type[Any]) -> None:
        self._kind = kind

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self._kind)

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        return f"<ANY_{self._kind.__name__.upper()}>"


ANY_BOOL = _ANY_TYPE(bool)
ANY_BYTES = _ANY_TYPE(bytes)
ANY_COMPLEX = _ANY_TYPE(complex)
ANY_DICT = _ANY_TYPE(dict)
ANY_FLOAT = _ANY_TYPE(float)
ANY_INT = _ANY_TYPE(int)
ANY_LIST = _ANY_TYPE(list)
ANY_SET = _ANY_TYPE(set)
ANY_STR = _ANY_TYPE(str)
ANY_TUPLE = _ANY_TYPE(tuple)
