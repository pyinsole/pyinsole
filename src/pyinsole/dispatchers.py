import abc
import asyncio
import logging
import sys
from collections.abc import Sequence
from typing import Any

from .exceptions import DeleteMessage
from .routes import Route

logger = logging.getLogger(__name__)


class AbstractDispatcher:
    @abc.abstractmethod
    def dispatch(self, *, forever: bool):
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
        except DeleteMessage:
            logger.info("explicit message deletion\n%s\n", message)
            confirm_message = True
        except asyncio.CancelledError:
            msg = '"{!r}" was cancelled, the message will not be acknowledged:\n{}\n'
            logger.warning(msg.format(route.handler, message))
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

    async def _fetch_messages(
        self,
        processing_queue: asyncio.Queue,
        tg: asyncio.TaskGroup,
        *,
        forever: bool = True,
    ):
        routes = list(self.routes)
        tasks = [tg.create_task(route.provider.fetch_messages()) for route in routes]

        while routes or tasks:
            await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

            new_routes = []
            new_tasks = []

            for task, route in zip(tasks, routes, strict=False):
                if task.done():
                    if exc := task.exception():
                        raise exc

                    for message in task.result():
                        await processing_queue.put((message, route))

                    if forever:
                        # when execute forever, we should reappending a new task that was
                        # completed...
                        new_routes.append(route)
                        new_tasks.append(tg.create_task(route.provider.fetch_messages()))

                    # when it isn't forever, the list will decrease in each interation...
                    # decreasing one route and one task.
                    # after all tasks are done, the while will stop

                else:
                    # reappending task not done yet...
                    new_routes.append(route)
                    new_tasks.append(task)

            routes = new_routes
            tasks = new_tasks

    async def _consume_messages(self, processing_queue: asyncio.Queue) -> None:
        while True:
            message, route = await processing_queue.get()

            await self._process_message(message, route)
            processing_queue.task_done()

    async def dispatch(self, *, forever: bool = True):
        processing_queue: asyncio.Queue[tuple[Any, Route]] = asyncio.Queue(self.queue_size)

        async with asyncio.TaskGroup() as tg:
            provider_task = tg.create_task(self._fetch_messages(processing_queue, tg, forever=forever))
            consumer_tasks = [tg.create_task(self._consume_messages(processing_queue)) for _ in range(self.workers)]

            async def join():
                await provider_task
                await processing_queue.join()

                for consumer_task in consumer_tasks:
                    consumer_task.cancel()

                await asyncio.gather(*consumer_tasks, return_exceptions=True)

            tg.create_task(join())

    def stop(self) -> None:
        for route in self.routes:
            route.stop()
