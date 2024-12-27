from collections.abc import Awaitable, Callable
from typing import ParamSpec, Protocol, TypeVar

ReturnT = TypeVar("ReturnT")
P = ParamSpec("P")

AsyncCallable = Callable[P, Awaitable[ReturnT]]


class Handler(Protocol):
    async def __call__(self, message: dict, metadata: dict) -> bool:
        """Process a given message and its associated metadata, and return a status.

        This abstract method should be implemented by subclasses to handle and process the
        `message` and `metadata`. The method can accept additional keyword arguments (`**kwargs`)
        for customization. The result of the processing is a boolean indicating success or failure.

        Parameters:
        -----------
        message : dict
            The input message to be processed. This dictionary can contain various fields required
            for handling.

        metadata : dict
            The associated metadata for the message. This dictionary may include contextual
            information such as source, timestamp, or other relevant details.

        Returns:
        --------
        bool
            Returns `True` if the message processing was successful, and `False` if it failed.
        """
