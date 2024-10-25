import asyncio
import abc
import logging
import signal
from concurrent.futures import CancelledError
from contextlib import suppress

from typing import Callable


logger = logging.getLogger(__name__)


class IRunner:
    @abc.abstractmethod
    def start_loop(self, debug: bool):
        pass

    @abc.abstractmethod
    def stop_loop(self):
        pass

    @abc.abstractmethod
    def stop(self):
        pass


class Runner:
    def __init__(self, *, on_start_callback: Callable = None, on_stop_callback: Callable = None):
        self._on_start_callback = on_start_callback
        self._on_stop_callback = on_stop_callback

    @property
    def loop(self):
        return asyncio.get_event_loop()

    def start_loop(self, debug: bool = False):
        if debug:
            self.loop.set_debug(enabled=debug)

        logger.info("starting pyinsole...")

        self.loop.add_signal_handler(signal.SIGINT, self.stop_loop)
        self.loop.add_signal_handler(signal.SIGTERM, self.stop_loop)

        if self._on_start_callback:
            self.loop.call_soon(self._on_start_callback)

        try:
            self.loop.run_forever()
        finally:
            self.stop()
            self.loop.close()
            logger.debug("loop.is_running=%s", self.loop.is_running())
            logger.debug("loop.is_closed=%s", self.loop.is_closed())

    def stop_loop(self, *args):  # noqa: ARG002
        if self.loop.is_running():
            # signals loop.run_forever to exit in the next iteration
            self.loop.stop()

    def stop(self):
        logger.info("stopping pyinsole...")

        if self._on_stop_callback:
            self._on_stop_callback()

        logger.info("cancel schedulled operations ...")
        with suppress(CancelledError, RuntimeError):
            self._cancel_all_tasks()

    def _cancel_all_tasks(self):
        if not (tasks := asyncio.all_tasks(self.loop)):
            return

        for task in tasks:
            task.cancel()

        self.loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))

        not_cancelled_tasks = (task for task in tasks if task.cancelled() is False)

        for task in not_cancelled_tasks:
            if task.exception() is not None:
                self.loop.call_exception_handler(
                    {
                        "message": "unhandled exception during asyncio.run() shutdown",
                        "exception": task.exception(),
                        "task": task,
                    }
                )
