import abc
from contextlib import AbstractAsyncContextManager


class AbstractProvider(AbstractAsyncContextManager):
    """
    Abstract message provider.

    This class is used internally as a Context Manager.
    """

    @abc.abstractmethod
    async def fetch_messages(self) -> list:
        """Return a sequence of messages to be processed.

        If no messages are available, this coroutine should return an empty list.
        """

    @abc.abstractmethod
    async def confirm_message(self, message):
        """Confirm the message processing.

        After the message confirmation we should not receive the same message again.
        This usually means we need to delete the message in the provider.
        """

    async def message_not_processed(self, message):
        """Perform actions when a message was not processed."""

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass
