import asyncio
from unittest import mock

import pytest

from pyinsole.dispatchers import Dispatcher
from pyinsole.exceptions import DeleteMessage
from pyinsole.routes import Route


def create_mock_route(messages):
    provider = mock.AsyncMock(
        fetch_messages=mock.AsyncMock(side_effect=[messages]),
        confirm_message=mock.AsyncMock(),
        message_not_processed=mock.AsyncMock(),
    )

    message_translator = mock.Mock(translate=mock.Mock(side_effect=[{"content": message} for message in messages]))
    return mock.AsyncMock(
        provider=provider,
        handler=mock.AsyncMock(),
        message_translator=message_translator,
        spec=Route,
    )


@pytest.fixture
def route():
    return create_mock_route(["message"])


@pytest.mark.asyncio
async def test_dispatch_message(route):
    route.deliver = mock.AsyncMock(return_value="confirmation")
    dispatcher = Dispatcher([route])

    message = "foobar"
    confirmation = await dispatcher._dispatch_message(message, route)  # noqa: SLF001
    assert confirmation == "confirmation"

    route.deliver.assert_awaited_once_with(message)


@pytest.mark.asyncio
@pytest.mark.parametrize("message", [None, ""])
async def test_dispatch_invalid_message(route, message):
    route.deliver = mock.AsyncMock()
    dispatcher = Dispatcher([route])

    confirmation = await dispatcher._dispatch_message(message, route)  # noqa: SLF001
    assert confirmation is False
    route.deliver.assert_not_awaited()


@pytest.mark.asyncio
async def test_dispatch_message_task_delete_message(route):
    route.deliver = mock.AsyncMock(side_effect=DeleteMessage)
    dispatcher = Dispatcher([route])
    message = "rejected-message"

    confirmation = await dispatcher._dispatch_message(message, route)  # noqa: SLF001

    assert confirmation is True
    assert route.deliver.called
    route.deliver.assert_awaited_once_with(message)


@pytest.mark.asyncio
async def test_dispatch_message_task_error(route):
    exc = Exception()
    route.deliver = mock.AsyncMock(side_effect=exc)
    route.error_handler = mock.AsyncMock(return_value="confirmation")
    dispatcher = Dispatcher([route])
    message = "message"

    confirmation = await dispatcher._dispatch_message(message, route)  # noqa: SLF001

    assert confirmation == "confirmation"
    route.deliver.assert_awaited_once_with(message)
    route.error_handler.assert_awaited_once_with((Exception, exc, mock.ANY), message)


@pytest.mark.asyncio
async def test_dispatch_message_task_cancel(route):
    route.deliver = mock.AsyncMock(side_effect=asyncio.CancelledError)
    dispatcher = Dispatcher([route])
    message = "message"

    confirmation = await dispatcher._dispatch_message(message, route)  # noqa: SLF001

    assert confirmation is False
    route.deliver.assert_awaited_once_with(message)


@pytest.mark.asyncio
async def test_dispatch_providers(route):
    dispatcher = Dispatcher([route])
    dispatcher._dispatch_message = mock.AsyncMock()  # noqa: SLF001

    await dispatcher.dispatch(forever=False)

    dispatcher._dispatch_message.assert_awaited_once_with("message", route)  # noqa: SLF001


@pytest.mark.asyncio
async def test_dispatch_providers_multiple_routes():
    route1 = create_mock_route(["message1", "message2"])
    route2 = create_mock_route(["message3"])
    dispatcher = Dispatcher([route1, route2])
    dispatcher._dispatch_message = mock.AsyncMock()  # noqa: SLF001

    await dispatcher.dispatch(forever=False)

    dispatcher._dispatch_message.assert_has_awaits(  # noqa: SLF001
        [
            mock.call("message1", route1),
            mock.call("message2", route1),
            mock.call("message3", route2),
        ],
        any_order=True,
    )


@pytest.mark.asyncio
async def test_dispatch_providers_with_error(route):
    route.provider.fetch_messages.side_effect = ValueError
    dispatcher = Dispatcher([route])

    with pytest.raises(ExceptionGroup) as exc_info:
        await dispatcher.dispatch(forever=False)

    assert exc_info.value.subgroup(ValueError) is not None


def test_dispatcher_stop(route):
    route.stop = mock.Mock()
    dispatcher = Dispatcher([route])

    dispatcher.stop()

    assert route.stop.called
