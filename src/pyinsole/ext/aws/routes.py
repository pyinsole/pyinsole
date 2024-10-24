from typing import Callable

from pyinsole.routes import Route
from pyinsole.handlers import IHandler

from .translators import SQSMessageTranslator
from .providers import SQSProvider


class SQSRoute(Route):
    def __init__(
        self,
        provider_queue: str,
        handler: Callable | IHandler,
        *,
        provider_options: dict=None,
        error_handler: Callable=None,
        **kwargs
    ):
        provider_options = provider_options or {}
        provider = SQSProvider(provider_queue, **provider_options)

        name = kwargs.pop("name", None) or provider_queue
        translator = kwargs.get("translator", None) or SQSMessageTranslator()

        super().__init__(
            provider=provider,
            handler=handler,
            name=name,
            translator=translator,
            error_handler=error_handler,
            **kwargs
        )
