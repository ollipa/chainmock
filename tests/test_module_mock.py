"""Tests for mock module."""
# pylint: disable=missing-docstring,no-self-use
from chainmock import mock


class TestMockModule:
    def test_any_type(self) -> None:
        ANY_STR = mock._ANY_TYPE(str)  # pylint: disable=protected-access, invalid-name
        assert ANY_STR == "foo"
        assert ANY_STR == "bar"
        assert ANY_STR != 123
        assert repr(ANY_STR) == "<ANY_STR>"

    def test_any_types(self) -> None:
        assert {
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
        } == {
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
        }
