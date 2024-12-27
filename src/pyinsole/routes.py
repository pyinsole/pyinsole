import logging
from collections.abc import Callable
from contextlib import AbstractAsyncContextManager, AsyncExitStack

from .handlers import Handler
from .providers import AbstractProvider
from .translators import AbstractTranslator, TranslatedMessage
from .utils import is_async_callable

logger = logging.getLogger(__name__)


class Route(AbstractAsyncContextManager):
    def __init__(
        self,
        provider: AbstractProvider,
        handler: Handler,
        *,
        name: str = "default",
        translator: AbstractTranslator | None = None,
        error_handler: Callable | None = None,
    ):
        if not isinstance(provider, AbstractProvider):
            msg = f"invalid provider instance: {provider!r}"
            raise TypeError(msg)

        if not is_async_callable(handler):
            msg = f"handler must be a coroutine function: {handler!r}"
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

    def __str__(self):
        return f"<{type(self).__name__}(name={self.name} provider={self.provider!r} handler={self.handler!r})>"

    def prepare_message(self, raw_message) -> TranslatedMessage:
        default_message: TranslatedMessage = {"content": raw_message, "metadata": {}}

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

        return await self.handler(message["content"], message["metadata"])

    async def error_handler(self, exc_info, message):
        logger.info("error handler process originated by message=%s", message)

        if self._error_handler is not None:
            return await self._error_handler(exc_info, message)

        return False

    async def __aenter__(self):
        async with AsyncExitStack() as exit_stack:
            await exit_stack.enter_async_context(self.provider)
            self._exit_stack = exit_stack.pop_all()
        return await super().__aenter__()

    async def __aexit__(self, exc_type, exc_value, traceback):
        logger.info("stopping route %s", self)

        if hasattr(self, "_exit_stack"):
            await self._exit_stack.aclose()
