import abc
from typing import Any, Generic, TypeVar

from pyinsole.handlers import IHandler

T = TypeVar("T")


class Handler(IHandler):
    """Helper class that provides a standard way to create synchronous handlers."""

    @abc.abstractmethod
    def process(self, message: Any, metadata: list[Any], **kwargs) -> bool:
        """
        Process a single message.

        This method should be overriden in child classes.

        Parameters
        ----------
            message: dict
                the message to process
            metadata: list[Any]
                metadata associated with the message

        Returns
        -------
        True if the message was succefully processed and should be deleted.
        """

    def handle(self, *args, **kwargs) -> bool:
        """
        Handle a single message.

        This method is called by deliver from route and it actually calls process.
        """
        message, *metadata = args
        return self.process(message, metadata=metadata, **kwargs)


class AsyncHandler(IHandler):
    """Helper class that provides a standard way to create asyncio-compatible handlers."""

    @abc.abstractmethod
    async def process(self, message: Any, metadata: list[Any], **kwargs) -> bool:
        """
        Process a single message.

        This method should be overriden in child classes.

        Parameters
        ----------
            message: Any
                the message to process
            metadata: list[Any]
                metadata associated with the message

        Returns
        -------
        True if the message was succefully processed and should be deleted.
        """

    async def handle(self, *args, **kwargs) -> bool:
        """
        Handle a single message.

        This method is called by loafer and it actually calls process.
        """
        message, *metadata = args
        return await self.process(message, metadata=metadata, **kwargs)


class ModelHandler(Generic[T], IHandler):
    """
    Helper class that provides a standard way to create synchronous handlers.

    This handler casts the message to a model type.

    Attributes
    ----------
        model_class: type
            the model type to use. The message will be forwarded to the model constructor.
    """

    model_class: type[T]

    @abc.abstractmethod
    def process(self, message: T, metadata: list[Any], **kwargs) -> bool:
        """
        Process a single message.

        This method should be overriden in child classes.

        Parameters
        ----------
            message: T
                the message to process
            metadata: list[Any]
                metadata associated with the message

        Returns
        -------
        True if the message was succefully processed and should be deleted.
        """

    def handle(self, *args, **kwargs) -> bool:
        """
        Handle a single message.

        This method is called by deliver from route and it actually calls process.
        """
        message, *metadata = args
        return self.process(self.model_class(**message), metadata=metadata, **kwargs)


class AsyncModelHandler(Generic[T], IHandler):
    """
    Helper class that provides a standard way to create asyncio-compatible handlers.

    This handler casts the message to a model type.

    Attributes
    ----------
        model_class: type
            the model type to use. The message will be forwarded to the model constructor.
    """

    model_class: type[T]

    @abc.abstractmethod
    async def process(self, message: T, metadata: list[Any], **kwargs) -> bool:
        """
        Process a single message.

        This method should be overriden in child classes.

        Parameters
        ----------
            message: T
                the message to process
            metadata: list[Any]
                metadata associated with the message

        Returns
        -------
        True if the message was succefully processed and should be deleted.
        """

    async def handle(self, *args, **kwargs) -> bool:
        """
        Handle a single message.

        This method is called by deliver from route and it actually calls process.
        """
        message, *metadata = args
        return await self.process(self.model_class(**message), metadata=metadata, **kwargs)
