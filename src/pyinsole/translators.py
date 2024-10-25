import abc
import logging
from typing import TypedDict

logger = logging.getLogger(__name__)


class TranslatedMessage(TypedDict):
    content: str
    metadata: dict


class AbstractTranslator(abc.ABC):
    @abc.abstractmethod
    def translate(self, raw_message: dict) -> TranslatedMessage:
        """Translate a given message to an appropriate format to message processing.

        This method should return a `dict` instance with two keys: `content`
        and `metadata`.
        The `content` should contain the translated message and, `metadata` a
        dictionary with translation metadata or an empty `dict`.
        """
