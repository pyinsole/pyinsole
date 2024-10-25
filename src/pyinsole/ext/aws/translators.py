import json
import logging

from pyinsole.translators import AbstractTranslator, TranslatedMessage

logger = logging.getLogger(__name__)


class SQSMessageTranslator(AbstractTranslator):
    def translate(self, raw_message: dict) -> TranslatedMessage:
        translated_message: TranslatedMessage = {"content": None, "metadata": {}}

        try:
            body = raw_message["Body"]
        except (KeyError, TypeError):
            logger.exception(
                "missing Body key in SQS message. It really came from SQS ?\nmessage=%r",
                raw_message,
            )
            return translated_message

        try:
            translated_message["content"] = json.loads(body)
        except json.decoder.JSONDecodeError as exc:
            logger.exception("error=%r, message=%r", exc, raw_message)  # noqa: TRY401
            return translated_message

        translated_message["metadata"] |= raw_message

        return translated_message
