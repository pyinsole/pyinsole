from collections.abc import Awaitable, Callable
from typing import Any, ParamSpec, TypeVar

from ._compat import TypeIs, iscoroutinefunction

ReturnT = TypeVar("ReturnT")
P = ParamSpec("P")

AsyncCallable = Callable[P, Awaitable[ReturnT]]


def is_async_callable(val: Any) -> TypeIs[AsyncCallable]:
    return iscoroutinefunction(val) or (callable(val) and iscoroutinefunction(val.__call__))
