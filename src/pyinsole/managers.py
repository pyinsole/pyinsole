import asyncio
import logging
import os
import signal
import threading
from collections.abc import Sequence
from functools import partial

from .dispatchers import AbstractDispatcher, Dispatcher
from .routes import Route

logger = logging.getLogger(__name__)


class Manager:
    def __init__(
        self,
        routes: Sequence[Route],
        *,
        dispatcher: AbstractDispatcher | None = None,
        queue_size: int | None = None,
        workers: int | None = None,
    ):
        self.dispatcher = dispatcher or Dispatcher(routes, queue_size, workers)

    def run(self, *, graceful_timeout: int = 30, forever: bool = True, debug: bool = False):
        cancellation_token = asyncio.Event()
        if threading.current_thread() is threading.main_thread():
            signal.signal(signal.SIGTERM, partial(self.handle_signal, event=cancellation_token))

        logger.info("running pyinsole's manager, pid=%s, forever=%s", os.getpid(), forever)
        asyncio.run(
            self._run(
                cancellation_token=cancellation_token,
                graceful_timeout=graceful_timeout,
                forever=forever,
            ),
            debug=debug,
        )

    def handle_signal(self, signum, frame, event: asyncio.Event):  # noqa: ARG002
        event.set()

    async def _run(self, *, cancellation_token: asyncio.Event, graceful_timeout: int, forever):
        async with asyncio.TaskGroup() as tasks:
            dispatcher_task = tasks.create_task(
                self.dispatcher.dispatch(cancellation_token=cancellation_token, forever=forever)
            )
            cancellation_task = tasks.create_task(cancellation_token.wait())

            async def handle_cancellation():
                await asyncio.wait([cancellation_task, dispatcher_task], return_when=asyncio.FIRST_COMPLETED)

                if not dispatcher_task.done():
                    try:
                        async with asyncio.timeout(graceful_timeout):
                            await dispatcher_task
                    except TimeoutError:
                        dispatcher_task.cancel()
                else:
                    cancellation_task.cancel()

            tasks.create_task(handle_cancellation())
