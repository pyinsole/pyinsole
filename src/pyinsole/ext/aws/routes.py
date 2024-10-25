from typing import Callable

from pyinsole.routes import Route
from pyinsole.handlers import Handler
from pyinsole.translators import AbstractTranslator

from .translators import SQSMessageTranslator
from .providers import SQSProvider


class SQSRoute(Route):
    def __init__(
        self,
        provider_queue: str,
        handler: Handler,
        *,
        provider_options: dict = None,
        error_handler: Callable = None,
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
