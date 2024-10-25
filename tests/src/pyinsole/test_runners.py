import asyncio
from contextlib import nullcontext as does_not_raise
from unittest import mock

import pytest

from pyinsole.runners import Runner

_path = "pyinsole.runners"

@mock.patch(f"{_path}.Runner.loop", new_callable=mock.PropertyMock)
def test_runner_start(loop_mock):
    runner = Runner()

    runner.start_loop()

    assert loop_mock.return_value.run_forever.called


@mock.patch(f"{_path}.Runner.loop", new_callable=mock.PropertyMock)
def test_runner_start_with_debug(loop_mock):
    runner = Runner()

    runner.start_loop(debug=True)

    loop_mock.return_value.set_debug.assert_called_once_with(enabled=True)


@mock.patch(f"{_path}.Runner.loop", new_callable=mock.PropertyMock)
def test_runner_start_and_stop(loop_mock):
    runner = Runner()
    runner.stop = mock.Mock()

    runner.start_loop()

    assert runner.stop.called
    assert loop_mock.return_value.run_forever.called
    assert loop_mock.return_value.close.called


@mock.patch(f"{_path}.Runner.loop", new_callable=mock.PropertyMock)
def test_runner_stop_loop(loop_mock):
    loop_mock.return_value.is_running.return_value = True
    runner = Runner()

    runner.stop_loop()

    loop_mock.return_value.stop.assert_called_once_with()


@mock.patch(f"{_path}.asyncio.get_event_loop")
def test_runner_stop_loop_already_stopped(get_loop_mock):
    loop = mock.Mock(is_running=mock.Mock(return_value=False))
    get_loop_mock.return_value = loop
    runner = Runner()

    runner.stop_loop()

    loop.is_running.assert_called_once_with()
    assert loop.stop.called is False


def test_runner_stop_with_callback():
    callback = mock.Mock()
    runner = Runner(on_stop_callback=callback)

    runner.stop()

    assert callback.called


def test_runner_stop_dont_raise_cancelled_error():
    async def some_coro():
        raise asyncio.CancelledError

    runner = Runner()
    loop = runner.loop
    task = loop.create_task(some_coro())

    assert task.done() is False
    assert task.cancelled() is False

    runner.stop()

    assert task.done() is True
    assert task.cancelled() is True
    with pytest.raises(asyncio.CancelledError):
        task.exception()


@mock.patch(f"{_path}.Runner._cancel_all_tasks")
def test_runner_stop_dont_raise_runtime_error(cancel_all_tasks_mock):
    cancel_all_tasks_mock.side_effect = RuntimeError("faiô!")
    runner = Runner()

    with does_not_raise():
        runner.loop.stop()
        runner.stop()
