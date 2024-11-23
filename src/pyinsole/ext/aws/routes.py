from collections.abc import Callable
from typing import Any

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
        provider_options: dict[str, Any] | None = None,
        translator: AbstractTranslator | None = None,
        name: str | None = None,
        error_handler: Callable[[Exception, Any], bool] | None = None,
    ):
        provider_options = provider_options or {}
        provider = SQSProvider(provider_queue, **provider_options)

        translator = translator or SQSMessageTranslator()
        name = name or provider_queue

        super().__init__(
            provider=provider,
            handler=handler,
            name=name,
            translator=translator,
            error_handler=error_handler,
        )
