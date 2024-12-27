import abc
import asyncio
import logging
import sys
from collections.abc import Sequence
from contextlib import AsyncExitStack
from typing import Any

from ._compat import override
from .routes import Route

logger = logging.getLogger(__name__)


class AbstractDispatcher:
    @abc.abstractmethod
    async def dispatch(self, *, cancellation_token: asyncio.Event | None = None, forever: bool = True):
        """Method that connects providers to consumers and dispatches and manages messages in transit.
        Calling Message acknowledgment and unacknowledged methods.

        Args:
            forever (bool): It dispatches messages continuously through the communication channel between provider and consumer.
                If not, execution will only occur once.
        """


class Dispatcher(AbstractDispatcher):
    def __init__(
        self,
        routes: Sequence[Route],
        queue_size: int | None = None,
        workers: int | None = None,
    ):
        self.routes = routes
        self.queue_size = queue_size or len(routes) * 10
        self.workers = workers or max(len(routes), 3)

    async def _dispatch_message(self, message: Any, route: Route) -> bool:
        logger.debug("dispatching message to route=%s", route)
        confirm_message = False

        if not message:
            logger.warning("message will be ignored:\n%r\n", message)
            return confirm_message

        try:
            confirm_message = await route.deliver(message)
        except asyncio.CancelledError:
            msg = '"{!r}" was cancelled, the message will not be acknowledged:\n{}\n'
            logger.warning(msg.format(route.handler, message))
            raise
        except Exception as exc:
            logger.exception("%r", exc)  # noqa: TRY401
            exc_info = sys.exc_info()
            confirm_message = await route.error_handler(exc_info, message)

        return confirm_message

    async def _process_message(self, message: Any, route: Route) -> bool:
        if confirmation := await self._dispatch_message(message, route):
            await route.provider.confirm_message(message)
        else:
            await route.provider.message_not_processed(message)

        return confirmation

    def _check_cancellation(self, cancellation_token: asyncio.Event | None) -> bool:
        return cancellation_token is not None and cancellation_token.is_set()

    async def _fetch_messages(
        self,
        processing_queue: asyncio.Queue,
        route: Route,
        *,
        cancellation_token: asyncio.Event | None = None,
        forever: bool = True,
    ):
        while True:
            messages = await route.provider.fetch_messages()
            for message in messages:
                await processing_queue.put((message, route))

            if (not forever) or (self._check_cancellation(cancellation_token)):
                break

    async def _consume_messages(self, processing_queue: asyncio.Queue) -> None:
        while True:
            message, route = await processing_queue.get()

            await self._process_message(message, route)
            processing_queue.task_done()

    @override
    async def dispatch(self, *, cancellation_token: asyncio.Event | None = None, forever: bool = True):
        processing_queue: asyncio.Queue[tuple[Any, Route]] = asyncio.Queue(self.queue_size)
        async with AsyncExitStack() as exit_stack:
            for route in self.routes:
                await exit_stack.enter_async_context(route)

            async with asyncio.TaskGroup() as tg:
                provider_tasks = [
                    tg.create_task(
                        self._fetch_messages(
                            processing_queue,
                            route,
                            cancellation_token=cancellation_token,
                            forever=forever,
                        )
                    )
                    for route in self.routes
                ]
                consumer_tasks = [tg.create_task(self._consume_messages(processing_queue)) for _ in range(self.workers)]

                async def join():
                    await asyncio.wait(provider_tasks)
                    await processing_queue.join()

                    for consumer_task in consumer_tasks:
                        consumer_task.cancel()

                    await asyncio.gather(*consumer_tasks, return_exceptions=True)

                tg.create_task(join())
