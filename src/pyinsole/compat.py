import sys

if sys.version_info >= (3, 12):
    from inspect import iscoroutinefunction
else:
    from asyncio import iscoroutinefunction


__all__ = [
    "iscoroutinefunction",
]
