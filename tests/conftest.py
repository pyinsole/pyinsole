import pytest

from pyinsole.providers import IProvider
from pyinsole.translators import ITranslator


@pytest.fixture
def dummy_handler():
    def handler(message, *args):  # noqa: ARG001
        msg = "I should not be called"
        raise AssertionError(msg)

    return handler


@pytest.fixture
def dummy_provider():
    class Dummy(IProvider):
        async def fetch_messages(self):
            msg = "I should not be called"
            raise AssertionError(msg)

        async def confirm_message(self):
            msg = "I should not be called"
            raise AssertionError(msg)

        async def message_not_processed(self):
            msg = "I should not be called"
            raise AssertionError(msg)

        def stop(self):
            msg = "I should not be called"
            raise AssertionError(msg)

    return Dummy()


@pytest.fixture
def dummy_translator():
    class StringMessageTranslator(ITranslator):
        def translate(self, raw_message: dict):
            return {"content": str(raw_message), "metadata": {}}

    return StringMessageTranslator()
