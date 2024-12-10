from collections.abc import Callable

from pyinsole.handlers import Handler
from pyinsole.routes import Route
from pyinsole.translators import AbstractTranslator

from .providers import SQSProvider
from .translators import SNSMessageTranslator, SQSMessageTranslator


class SQSRoute(Route):
    def __init__(
        self,
        provider_queue: str,
        handler: Handler,
        *,
        provider_options: dict | None = None,
        error_handler: Callable | None = None,
        translator: AbstractTranslator | None = None,
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


class SNSQueueRoute(SQSRoute):
    def __init__(
        self,
        provider_queue: str,
        handler: Handler,
        *,
        provider_options: dict | None = None,
        error_handler: Callable | None = None,
        translator: AbstractTranslator | None = None,
        **kwargs,
    ):
        translator = translator or SNSMessageTranslator()
        super().__init__(
            provider_queue,
            handler,
            provider_options=provider_options,
            error_handler=error_handler,
            translator=translator,
            **kwargs,
        )
