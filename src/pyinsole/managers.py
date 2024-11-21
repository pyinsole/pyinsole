import asyncio
import logging
import os
from collections.abc import Sequence

from .dispatchers import AbstractDispatcher, Dispatcher
from .routes import Route
from .runners import AbstractRunner, Runner

logger = logging.getLogger(__name__)


class Manager:
    def __init__(
        self,
        routes: Sequence[Route],
        *,
        runner: AbstractRunner | None = None,
        dispatcher: AbstractDispatcher | None = None,
        queue_size: int | None = None,
        workers: int | None = None,
    ):
        self.runner = runner or Runner(on_stop_callback=self._on_loop_stop_callback)
        self.dispatcher = dispatcher or Dispatcher(routes, queue_size, workers)

        self._future: asyncio.Future = None

    def run(self, *, forever: bool = True, debug: bool = False):
        loop = self.runner.loop

        self._future = asyncio.ensure_future(
            self.dispatcher.dispatch(forever=forever),
            loop=loop,
        )

        self._future.add_done_callback(self._on_future_done_callback)

        if not forever:
            self._future.add_done_callback(self.runner.stop_loop)

        logger.info("running pyinsole's manager, pid=%s, forever=%s", os.getpid(), forever)
        self.runner.start_loop(debug=debug)

    def _on_future_done_callback(self, future: asyncio.Future):
        if future.cancelled():
            return self.runner.stop_loop()

        exc = future.exception()

        # Unhandled errors crashes the event loop execution
        if isinstance(exc, BaseException):
            logger.critical("fatal error caught: %r", exc)
            self.runner.stop_loop()
            return None
        return None

    def _on_loop_stop_callback(self):
        logger.info("cancelling pyinsole's manager dispatcher operations ...")

        if self._future:
            self._future.cancel()

        self.dispatcher.stop()
