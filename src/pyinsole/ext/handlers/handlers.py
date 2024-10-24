import logging
import abc
from typing import Any, Generic, TypeVar

from pyinsole.handlers import IHandler

logger = logging.getLogger(__name__)

T = TypeVar("T")


class Handler(IHandler):
    """Helper class that provides a standard way to create synchronous loafer handlers."""

    @abc.abstractmethod
    def process(self, message: Any, meta: list[Any], **kwargs) -> bool:
        """
        Process a single message.

        This method should be overriden in child classes.

        Parameters
        ----------
            message: Any
                the message to process
            meta: list[Any]
                metadata associated with the message

        Returns
        -------
        True if the message was succefully processed and should be deleted.
        """

    def handle(self, *args) -> bool:
        """
        Handle a single message.

        This method is called by loafer and it actually calls process.
        """
        message, *meta = args
        return self.process(message, meta=meta)


class AsyncHandler(IHandler):
    """Helper class that provides a standard way to create asyncio-compatible loafer handlers."""

    @abc.abstractmethod
    async def process(self, message: Any, meta: list, **kwargs) -> bool:
        """
        Process a single message.

        This method should be overriden in child classes.

        Parameters
        ----------
            message: Any
                the message to process
            meta: list[Any]
                metadata associated with the message

        Returns
        -------
        True if the message was succefully processed and should be deleted.
        """

    async def handle(self, *args) -> bool:
        """
        Handle a single message.

        This method is called by loafer and it actually calls process.
        """
        message, *meta = args
        return await self.process(message, meta=meta)


class ModelHandler(Generic[T], IHandler):
    """
    Helper class that provides a standard way to create synchronous loafer handlers.

    This handler casts the message to a model type.

    Attributes
    ----------
        model_class: type
            the model type to use. The message will be forwarded to the model constructor.
    """

    model_class: type[T]

    @abc.abstractmethod
    def process(self, message: T, *, meta: list, **kwargs) -> bool:
        """
        Process a single message.

        This method should be overriden in child classes.

        Parameters
        ----------
            message: T
                the message to process
            meta: list[Any]
                metadata associated with the message

        Returns
        -------
        True if the message was succefully processed and should be deleted.
        """

    def handle(self, *args) -> bool:
        """
        Handle a single message.

        This method is called by loafer and it actually calls process.
        """
        message, *meta = args
        return self.process(self.model_class(**message), meta=meta)


class AsyncModelHandler(Generic[T], IHandler):
    """
    Helper class that provides a standard way to create asyncio-compatible loafer handlers.

    This handler casts the message to a model type.

    Attributes
    ----------
        model_class: type
            the model type to use. The message will be forwarded to the model constructor.
    """

    model_class: type[T]

    @abc.abstractmethod
    async def process(self, message: T, *, meta: list, **kwargs) -> bool:
        """
        Process a single message.

        This method should be overriden in child classes.

        Parameters
        ----------
            message: T
                the message to process
            meta: list[Any]
                metadata associated with the message

        Returns
        -------
        True if the message was succefully processed and should be deleted.
        """

    async def handle(self, *args) -> bool:
        """
        Handle a single message.

        This method is called by loafer and it actually calls process.
        """
        message, *meta = args
        return await self.process(self.model_class(**message), meta=meta)
