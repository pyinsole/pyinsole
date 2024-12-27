import sys

PY312 = sys.version_info >= (3, 12)

if PY312:
    from inspect import iscoroutinefunction
    from typing import override
else:
    from asyncio import iscoroutinefunction

    from typing_extensions import override


__all__ = [
    "iscoroutinefunction",
    "override",
]
