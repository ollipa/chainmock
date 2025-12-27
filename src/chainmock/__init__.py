"""Chainmock.

Spy, stub, and mock library for Python and Pytest.
"""

from . import _doctest  # imported for side-effects # noqa: F401
from . import _unittest  # imported for side-effects # noqa: F401
from ._api import Assert, Mock, mocker

__all__ = [
    "Assert",
    "Mock",
    "mocker",
]
