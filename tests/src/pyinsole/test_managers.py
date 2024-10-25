import asyncio
from unittest import mock

import pytest

from pyinsole.dispatchers import Dispatcher
from pyinsole.exceptions import ProviderError
from pyinsole.managers import Manager
from pyinsole.routes import Route
from pyinsole.runners import Runner


@pytest.fixture
def dummy_route(dummy_provider):
    return Route(dummy_provider, handler=mock.Mock())


def test_dispatcher(dummy_route):
    manager = Manager(routes=[dummy_route])
    assert manager.dispatcher
    assert isinstance(manager.dispatcher, Dispatcher)


def test_default_runner():
    manager = Manager(routes=[])
    assert manager.runner
    assert isinstance(manager.runner, Runner)


def test_custom_runner():
    runner = mock.Mock()
    manager = Manager(routes=[], runner=runner)
    assert manager.runner
    assert isinstance(manager.runner, mock.Mock)


def test_on_future_errors():
    manager = Manager(routes=[])
    manager.runner = mock.Mock()
    future = asyncio.Future()
    future.set_exception(ProviderError)
    manager._on_future_done_callback(future)

    assert manager.runner.stop_loop.called
    manager.runner.stop_loop.assert_called_once_with()


def test_on_future_errors_cancelled():
    manager = Manager(routes=[])
    manager.runner = mock.Mock()
    future = asyncio.Future()
    future.cancel()
    manager._on_future_done_callback(future)

    assert manager.runner.stop_loop.called
    manager.runner.stop_loop.assert_called_once_with()


def test_on_loop__stop():
    manager = Manager(routes=[])
    manager.dispatcher = mock.Mock()
    manager._future = mock.Mock()  # noqa: SLF001
    manager._on_loop_stop_callback()

    assert manager.dispatcher.stop.called
    assert manager._future.cancel.called  # noqa: SLF001
