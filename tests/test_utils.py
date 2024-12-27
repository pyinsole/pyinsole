from pyinsole.utils import is_async_callable


def test_is_async_callable_with_sync_function():
    def dummy(): ...

    assert is_async_callable(dummy) is False


def test_is_async_callable_with_async_function():
    async def dummy(): ...

    assert is_async_callable(dummy) is True


def test_is_async_callable_with_sync_callable():
    class Dummy:
        def __call__(self): ...

    assert is_async_callable(Dummy()) is False


def test_is_async_callable_with_non_callable():
    class Dummy: ...

    assert is_async_callable(Dummy()) is False


def test_is_async_callable_with_async_callable():
    class Dummy:
        async def __call__(self): ...

    assert is_async_callable(Dummy()) is True
