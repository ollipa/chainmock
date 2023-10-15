"""Chainmock tests."""
from .test_async_mocking import AsyncMockingTestCase
from .test_async_spying import AsyncSpyingTestCase
from .test_chainmock import ChainmockTestCase
from .test_mocking import MockingTestCase
from .test_module_mock import MockModuleTestCase
from .test_patching import PatchingTestCase
from .test_spying import SpyingTestCase
from .test_stubbing import StubbingTestCase


class DefaultTestCase(
    MockingTestCase,
    AsyncMockingTestCase,
    AsyncSpyingTestCase,
    ChainmockTestCase,
    MockModuleTestCase,
    PatchingTestCase,
    SpyingTestCase,
    StubbingTestCase,
):
    """Base class for all tests. Integrations should inherit this test case."""
