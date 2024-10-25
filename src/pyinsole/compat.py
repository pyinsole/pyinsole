import sys
from asyncio import TaskGroup, to_thread

PY312 = sys.version_info >= (3, 12)

if PY312:
    from inspect import iscoroutinefunction
else:
    from asyncio import iscoroutinefunction


__all__ = [
    "to_thread",
    "iscoroutinefunction",
    "TaskGroup",
]
