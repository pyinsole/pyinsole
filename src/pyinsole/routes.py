import asyncio
import logging
from collections.abc import Awaitable, Callable
from functools import partial
from typing import Any, ParamSpec, TypeVar, overload

from .compat import iscoroutinefunction
from .handlers import AbstractHandler, Handler
from .providers import AbstractProvider
from .translators import AbstractTranslator, TranslatedMessage

logger = logging.getLogger(__name__)

P = ParamSpec("P")
T = TypeVar("T")


async def to_coroutine(
    handler: Callable[P, Awaitable[T]] | Callable[P, T], *args: P.args, **kwargs: P.kwargs
) -> T:
    if not callable(handler):
        raise ValueError("handler must be a callable")

    if iscoroutinefunction(handler):
        logger.debug("handler is coroutine! %r", handler)
        return await handler(*args, **kwargs)  # type: ignore[no-any-return]

    if iscoroutinefunction(handler.__call__):  # type: ignore[operator]
        logger.debug("handler.__call__ is coroutine! %r", handler)
        return await handler(*args, **kwargs)  # type: ignore[misc,no-any-return]

    logger.debug("handler will run in a separate thread: %r", handler)
    return await asyncio.to_thread(handler, *args, **kwargs)  # type: ignore[arg-type]


class Route:
    def __init__(
        self,
        provider: AbstractProvider,
        handler: Handler,
        *,
        name: str = "default",
        translator: AbstractTranslator | None = None,
        error_handler: Callable[[Exception, Any], bool] | None = None,
    ):
        if not isinstance(provider, AbstractProvider):
            msg = f"invalid provider instance: {provider!r}"
            raise TypeError(msg)

        # handler must be a callable or a instante of AbstractHandler
        if not callable(handler):
            msg = f"handler must be a callable object or implement `AbstractHandler` interface: {handler!r}"
            raise TypeError(msg)

        if translator and not isinstance(translator, AbstractTranslator):
            msg = f"invalid message translator instance: {translator!r}"
            raise TypeError(msg)

        if error_handler and not callable(error_handler):
            msg = f"error_handler must be a callable object: {error_handler!r}"
            raise TypeError(msg)

        self.name = name
        self.handler = handler
        self.provider = provider
        self.translator = translator

        self._error_handler = error_handler
        self._handler_instance = None

    def __str__(self) -> str:
        return (
            f"<{type(self).__name__}(name={self.name} provider={self.provider!r} handler={self.handler!r})>"
        )

    def prepare_message(self, raw_message: Any) -> TranslatedMessage:
        default_message: TranslatedMessage = {"content": raw_message, "metadata": {}}

        if not self.translator:
            return default_message

        message = self.translator.translate(raw_message)

        if not message["content"]:
            msg = f"{self.translator} failed to translate message={message}"
            raise ValueError(msg)

        return message

    async def deliver(self, raw_message: Any) -> bool:
        message = self.prepare_message(raw_message)
        logger.info("delivering message route=%s, message=%r", self, message)

        return await to_coroutine(self.handler, message["content"], message["metadata"])  # type: ignore[arg-type]

    async def error_handler(self, exc_info: Exception, message: Any) -> bool:
        logger.info("error handler process originated by message=%s", message)

        if self._error_handler is not None:
            return await to_coroutine(self._error_handler, exc_info, message)

        return False

    def stop(self) -> None:
        logger.info("stopping route %s", self)
        self.provider.stop()

        if isinstance(self.handler, AbstractHandler):
            self.handler.stop()
