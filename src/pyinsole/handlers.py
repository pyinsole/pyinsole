import abc
import logging

logger = logging.getLogger(__name__)


class IHandler(abc.ABC):
    @abc.abstractmethod
    def handle(self, message: dict, metadata: dict, **kwargs) -> bool:
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

        **kwargs : dict, optional
            Additional keyword arguments that can be passed to modify or extend the handling
            behavior. These arguments are optional and can vary depending on the implementation.

        Returns:
        --------
        bool
            Returns `True` if the message processing was successful, and `False` if it failed.
        """

    def stop(self):
        """Stop the handler.

        If needed, the handler should perform clean-up actions.
        This method is called whenever we need to shutdown the handler when necessary.
        """
