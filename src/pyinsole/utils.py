from typing import Any

from ._compat import TypeIs, iscoroutinefunction
from .types import AsyncCallable


def is_async_callable(val: Any) -> TypeIs[AsyncCallable]:
    return iscoroutinefunction(val) or (callable(val) and iscoroutinefunction(val.__call__))
