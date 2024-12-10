import asyncio
from unittest import mock

import pytest

from pyinsole.dispatchers import Dispatcher
from pyinsole.routes import Route


def create_mock_route(messages):
    provider = mock.AsyncMock(
        fetch_messages=mock.AsyncMock(return_value=messages),
        confirm_message=mock.AsyncMock(),
        message_not_processed=mock.AsyncMock(),
    )

    translator = mock.Mock(translate=mock.Mock(side_effect=[{"content": message} for message in messages]))
    return mock.AsyncMock(
        provider=provider,
        handler=mock.AsyncMock(),
        translator=translator,
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

    with pytest.raises(asyncio.CancelledError):
        await dispatcher._dispatch_message(message, route)  # noqa: SLF001

    route.deliver.assert_awaited_once_with(message)


@pytest.mark.asyncio
async def test_dispatch_providers(route):
    dispatcher = Dispatcher([route])
    dispatcher._dispatch_message = mock.AsyncMock()  # noqa: SLF001

    await dispatcher.dispatch(forever=False)

    dispatcher._dispatch_message.assert_awaited_once_with("message", route)  # noqa: SLF001
    route.__aenter__.assert_awaited_once()
    route.__aexit__.assert_awaited_once()


@pytest.mark.asyncio
async def test_dispatch_providers_forever(route):
    dispatcher = Dispatcher([route])
    dispatcher._dispatch_message = mock.AsyncMock()  # noqa: SLF001

    with pytest.raises(TimeoutError):
        async with asyncio.timeout(5):
            await dispatcher.dispatch(forever=True)

    assert dispatcher._dispatch_message.await_count > 0  # noqa: SLF001


@pytest.mark.asyncio
async def test_dispatch_providers_cancellation(route):
    dispatcher = Dispatcher([route])
    cancellation_token = asyncio.Event()
    dispatcher._dispatch_message = mock.AsyncMock()  # noqa: SLF001

    async def wait_and_cancel():
        await asyncio.sleep(2)
        cancellation_token.set()

    async with asyncio.timeout(5):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(dispatcher.dispatch(cancellation_token=cancellation_token, forever=True))
            tg.create_task(wait_and_cancel())

    assert dispatcher._dispatch_message.await_count > 0  # noqa: SLF001


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

    route1.__aenter__.assert_awaited_once()
    route1.__aexit__.assert_awaited_once()
    route2.__aenter__.assert_awaited_once()
    route2.__aexit__.assert_awaited_once()


@pytest.mark.asyncio
async def test_dispatch_providers_with_error(route):
    route.provider.fetch_messages.side_effect = ValueError
    dispatcher = Dispatcher([route])

    with pytest.raises(ExceptionGroup) as exc_info:
        await dispatcher.dispatch(forever=False)

    assert exc_info.value.subgroup(ValueError) is not None
    route.__aenter__.assert_awaited_once()
    route.__aexit__.assert_awaited_once()
