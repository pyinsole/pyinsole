from collections.abc import Callable

from pyinsole.handlers import Handler
from pyinsole.routes import Route
from pyinsole.translators import AbstractTranslator

from .providers import SQSProvider
from .translators import SQSMessageTranslator


class SQSRoute(Route):
    def __init__(
        self,
        provider_queue: str,
        handler: Handler,
        *,
        provider_options: dict | None = None,
        error_handler: Callable | None = None,
        translator: AbstractTranslator = None,
        **kwargs,
    ):
        provider_options = provider_options or {}
        provider = SQSProvider(provider_queue, **provider_options)

        translator = translator or SQSMessageTranslator()
        name = kwargs.pop("name", None) or provider_queue

        super().__init__(
            provider=provider,
            handler=handler,
            name=name,
            translator=translator,
            error_handler=error_handler,
            **kwargs,
        )
