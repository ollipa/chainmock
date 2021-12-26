"""Chainmock.

Spy, stub, and mock library for Python and Pytest.
"""
from . import _doctest  # imported for side-effects
from ._api import Assert, Mock, mocker

__all__ = [
    "Assert",
    "Mock",
    "mocker",
]
