"""Tests for mock module."""

# ruff: noqa: N806
from chainmock import mock

from .common import SomeClass


class MockModuleTestCase:
    def test_anyof(self) -> None:
        ANY_STR = mock.AnyOf(str)
        assert ANY_STR == "foo"
        assert ANY_STR == "bar"
        assert ANY_STR != 123
        assert repr(ANY_STR) == "<ANY_STR>"

    def test_anyof_with_class(self) -> None:
        ANY_SOMECLASS = mock.AnyOf(SomeClass)
        assert SomeClass() == ANY_SOMECLASS

    def test_any_types(self) -> None:
        assert {
            "bool": True,
            "bytes": b"some_bytes",
            "complex": complex("1+2j"),
            "dict": {"nested": "value"},
            "float": 1.23,
            "int": 7983,
            "list": [1, 2, 3],
            "set": {"foo", "bar"},
            "string": "some_string",
            "tuple": (1, 2),
        } == {
            "bool": mock.ANY_BOOL,
            "bytes": mock.ANY_BYTES,
            "complex": mock.ANY_COMPLEX,
            "dict": mock.ANY_DICT,
            "float": mock.ANY_FLOAT,
            "int": mock.ANY_INT,
            "list": mock.ANY_LIST,
            "set": mock.ANY_SET,
            "string": mock.ANY_STR,
            "tuple": mock.ANY_TUPLE,
        }

    def test_anyof_hash(self) -> None:
        ANY_STR = mock.AnyOf(str)
        assert hash(ANY_STR) == hash(str)
