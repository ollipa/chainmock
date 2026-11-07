"""Chainmock.

Spy, stub, and mock library for Python and Pytest.
"""

from . import (
    _doctest,  # imported for side-effects # noqa: F401
    _unittest,  # imported for side-effects # noqa: F401
)
from ._api import Assert, Mock, Mocker, mocker

__all__ = [
    "Assert",
    "Mock",
    "Mocker",
    "mocker",
]
