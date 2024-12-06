import logging
from contextlib import AsyncExitStack
from http import HTTPStatus

import botocore.exceptions

from pyinsole.exceptions import ProviderError
from pyinsole.providers import AbstractProvider

from .base import BaseSQSProvider

logger = logging.getLogger(__name__)


class SQSProvider(AbstractProvider, BaseSQSProvider):
    def __init__(self, queue_url, options=None, **kwargs):
        self.queue_url = queue_url
        self._options = options or {}
        self._client = kwargs.get("sqs_client")

        super().__init__(**kwargs)

    def __str__(self):
        return f"<{type(self).__name__}: {self.queue_url}>"

    async def confirm_message(self, message):
        receipt = message["ReceiptHandle"]
        logger.info("confirm message (ack/deletion), receipt=%r", receipt)

        try:
            return await self._client.delete_message(QueueUrl=self.queue_url, ReceiptHandle=receipt)
        except botocore.exceptions.ClientError as exc:
            if exc.response["ResponseMetadata"]["HTTPStatusCode"] == HTTPStatus.NOT_FOUND:
                return True

            raise

    async def fetch_messages(self):
        logger.debug("fetching messages on %s", self.queue_url)
        try:
            response = await self._client.receive_message(QueueUrl=self.queue_url, **self._options)
        except (
            botocore.exceptions.BotoCoreError,
            botocore.exceptions.ClientError,
        ) as exc:
            msg = f"error fetching messages from queue={self.queue_url}: {exc!s}"
            raise ProviderError(msg) from exc

        return response.get("Messages", [])

    async def __aenter__(self):
        if not self._client:
            async with AsyncExitStack() as exit_stack:
                self._client = await exit_stack.enter_async_context(self.get_client())

                self._exit_stack = exit_stack.pop_all()

        return await super().__aenter__()

    async def __aexit__(self, exc_type, exc_value, traceback):
        if hasattr(self, "_exit_stack"):
            await self._exit_stack.aclose()
        return await super().__aexit__(exc_type, exc_value, traceback)
