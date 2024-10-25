import logging
from typing import Callable

from .translators import ITranslator, ITranslatedMessage
from .providers import IProvider
from .handlers import ICallable, IHandler
from .compat import iscoroutinefunction, to_thread

logger = logging.getLogger(__name__)


async def to_coroutine(func, *args, **kwargs):
    if iscoroutinefunction(func):
        logger.debug("handler is coroutine! %r", func)
        return await func(*args, **kwargs)

    logger.debug("handler will run in a separate thread: %r", func)
    return await to_thread(func, *args, **kwargs)


class Route:
    def __init__(
        self,
        provider: IProvider,
        handler: ICallable | IHandler,
        *,
        name: str = "default",
        translator: ITranslator | None = None,
        error_handler: Callable | None = None,
    ):
        if not isinstance(provider, IProvider):
            msg = f"invalid provider instance: {provider!r}"
            raise TypeError(msg)

        if translator and not isinstance(translator, ITranslator):
            msg = f"invalid message translator instance: {translator!r}"
            raise TypeError(msg)

        if error_handler and not callable(error_handler):
            msg = f"error_handler must be a callable object: {error_handler!r}"
            raise TypeError(msg)

        self.name = name
        self.provider = provider
        self.translator = translator

        self._error_handler = error_handler
        self._handler_instance = None

        if callable(handler):
            self.handler = handler
        else:
            self.handler = getattr(handler, "handle", None)
            self._handler_instance = handler

        if not self.handler:
            msg = f"handler must be a callable object or implement `IHandler` interface: {self.handler!r}"
            raise TypeError(msg)

    def __str__(self):
        return (
            f"<{type(self).__name__}(name={self.name} provider={self.provider!r} handler={self.handler!r})>"
        )

    def prepare_message(self, raw_message) -> ITranslatedMessage:
        default_message = {"content": raw_message, "metadata": {}}

        if not self.translator:
            return default_message

        message = self.translator.translate(raw_message)

        if not message["content"]:
            msg = f"{self.translator} failed to translate message={message}"
            raise ValueError(msg)

        return message

    async def deliver(self, raw_message):
        message = self.prepare_message(raw_message)
        logger.info("delivering message route=%s, message=%r", self, message)

        return await to_coroutine(self.handler, message["content"], message["metadata"])

    async def error_handler(self, exc_info, message):
        logger.info("error handler process originated by message=%s", message)

        if self._error_handler is not None:
            return await to_coroutine(self._error_handler, exc_info, message)

        return False

    def stop(self):
        logger.info("stopping route %s", self)
        self.provider.stop()

        if self._handler_instance:
            self._handler_instance.stop()
