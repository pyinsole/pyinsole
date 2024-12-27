from unittest import mock

import pytest

from pyinsole.dispatchers import Dispatcher
from pyinsole.managers import Manager
from pyinsole.routes import Route


@pytest.fixture
def dummy_route(dummy_provider):
    return Route(dummy_provider, handler=mock.AsyncMock())


def test_dispatcher(dummy_route):
    manager = Manager(routes=[dummy_route])
    assert manager.dispatcher
    assert isinstance(manager.dispatcher, Dispatcher)
