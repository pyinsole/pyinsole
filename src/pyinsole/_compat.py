import sys

if sys.version_info >= (3, 12):
    from inspect import iscoroutinefunction
    from typing import override
else:
    from asyncio import iscoroutinefunction

    from typing_extensions import override

if sys.version_info >= (3, 13):
    from typing import TypeIs
else:
    from typing_extensions import TypeIs


__all__ = [
    "iscoroutinefunction",
    "override",
    "TypeIs",
]
