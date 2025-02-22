from unittest import mock

import pytest

from pyinsole.routes import Route
from pyinsole.translators import AbstractTranslator, TranslatedMessage


class StringMessageTranslator(AbstractTranslator):
    def translate(self, raw_message: dict) -> TranslatedMessage:
        return {"content": str(raw_message), "metadata": {}}


def test_provider(dummy_provider):
    route = Route(dummy_provider, handler=mock.AsyncMock())
    assert route.provider is dummy_provider


def test_provider_invalid():
    with pytest.raises(TypeError):
        Route("invalid-provider", handler=mock.Mock())


def test_name(dummy_provider):
    route = Route(dummy_provider, handler=mock.AsyncMock(), name="foo")
    assert route.name == "foo"


def test_translator(dummy_provider):
    translator = StringMessageTranslator()
    route = Route(dummy_provider, handler=mock.AsyncMock(), translator=translator)
    assert isinstance(route.translator, StringMessageTranslator)


def test_default_translator(dummy_provider):
    route = Route(dummy_provider, handler=mock.AsyncMock())
    assert route.translator is None


def test_translator_invalid(dummy_provider):
    with pytest.raises(TypeError):
        Route(dummy_provider, handler=mock.AsyncMock(), translator="invalid")


def test_prepare_message_translator(dummy_provider):
    translator = StringMessageTranslator()
    translator.translate = mock.Mock(return_value={"content": "foobar", "metadata": {}})
    route = Route(dummy_provider, mock.AsyncMock(), translator=translator)
    translated = route.prepare_message("message")

    assert translated["content"] == "foobar"
    assert translated["metadata"] == {}
    assert translator.translate.called

    translator.translate.assert_called_once_with("message")


def test_prepare_message_translator_error(dummy_provider):
    translator = StringMessageTranslator()
    translator.translate = mock.Mock(return_value={"content": "", "metadata": {}})
    route = Route(dummy_provider, mock.AsyncMock(), translator=translator)

    with pytest.raises(ValueError, match="failed to translate"):
        route.prepare_message("message")

    assert translator.translate.called
    translator.translate.assert_called_once_with("message")


@pytest.mark.asyncio
async def test_error_handler_unset(dummy_provider):
    route = Route(dummy_provider, mock.AsyncMock())
    exc = TypeError()
    exc_info = (type(exc), exc, None)
    result = await route.error_handler(exc_info, "whatever")
    assert result is False


def test_error_handler_invalid(dummy_provider):
    with pytest.raises(TypeError):
        Route(dummy_provider, handler=mock.Mock(), error_handler="invalid")


@pytest.mark.asyncio
async def test_error_handler(dummy_provider):
    attrs = {}

    async def error_handler(exc_info, message):
        attrs["exc_info"] = exc_info
        attrs["message"] = message
        return True

    # we cant mock regular functions in error handlers, because it will
    # be checked with asyncio.iscoroutinefunction() and pass as coro
    route = Route(dummy_provider, mock.AsyncMock(), error_handler=error_handler)
    exc = TypeError()
    exc_info = (type(exc), exc, "traceback")
    result = await route.error_handler(exc_info, "whatever")
    assert result is True
    assert attrs["exc_info"] == exc_info
    assert attrs["message"] == "whatever"


@pytest.mark.asyncio
async def test_error_handler_coroutine(dummy_provider):
    error_handler = mock.AsyncMock(return_value=True)
    route = Route(dummy_provider, mock.AsyncMock(), error_handler=error_handler)
    exc = TypeError()
    exc_info = (type(exc), exc, "traceback")
    result = await route.error_handler(exc_info, "whatever")
    assert result is True
    assert error_handler.called
    error_handler.assert_called_once_with(exc_info, "whatever")


@pytest.mark.asyncio
async def test_handler_class_based(dummy_provider):
    class Handler:
        async def __call__(self, *args, **kwargs):
            pass

    handler = Handler()
    route = Route(dummy_provider, handler=handler)
    assert route.handler == handler


@pytest.mark.asyncio
async def test_handler_function_based(dummy_provider):
    async def some_handler(*args, **kwargs):
        pass

    route = Route(dummy_provider, handler=some_handler)
    assert route.handler == some_handler


@pytest.mark.asyncio
async def test_handler_class_based_invalid(dummy_provider):
    class Handler:
        pass

    handler = Handler()
    with pytest.raises(TypeError, match="handler must be a coroutine function"):
        Route(dummy_provider, handler=handler)


@pytest.mark.asyncio
async def test_handler_invalid(dummy_provider):
    with pytest.raises(TypeError, match="handler must be a coroutine function"):
        Route(dummy_provider, "invalid-handler")


@pytest.mark.asyncio
async def test_route_lifecycle(dummy_provider):
    dummy_provider.__aenter__ = mock.AsyncMock()
    dummy_provider.__aexit__ = mock.AsyncMock()
    async with Route(dummy_provider, handler=mock.AsyncMock()):
        pass

    assert dummy_provider.__aenter__.awaited
    assert dummy_provider.__aexit__.awaited


# FIXME: Improve all test_deliver* tests


@pytest.mark.asyncio
async def test_deliver(dummy_provider):
    attrs = {}

    async def test_handler(*args, **kwargs):
        attrs["args"] = args
        attrs["kwargs"] = kwargs
        return True

    route = Route(dummy_provider, handler=test_handler)
    message = "test"
    result = await route.deliver(message)

    assert result is True
    assert message in attrs["args"]


@pytest.mark.asyncio
async def test_deliver_with_coroutine(dummy_provider):
    mock_handler = mock.AsyncMock(return_value=False)
    route = Route(dummy_provider, mock_handler)
    message = "test"
    result = await route.deliver(message)
    assert result is False
    assert mock_handler.called
    assert message in mock_handler.call_args[0]


@pytest.mark.asyncio
async def test_deliver_with_message_translator(dummy_provider):
    mock_handler = mock.AsyncMock(return_value=True)
    route = Route(dummy_provider, mock_handler)
    route.prepare_message = mock.Mock(return_value={"content": "whatever", "metadata": {}})
    result = await route.deliver("test")

    assert result is True
    assert route.prepare_message.called
    assert mock_handler.called
    mock_handler.assert_called_once_with("whatever", {})
