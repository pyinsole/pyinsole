import pytest

from pyinsole.providers import AbstractProvider
from pyinsole.translators import AbstractTranslator


@pytest.fixture
def dummy_handler():
    def handler(message, *args):  # noqa: ARG001
        msg = "I should not be called"
        raise AssertionError(msg)

    return handler


@pytest.fixture
def dummy_provider():
    class Dummy(AbstractProvider):
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
    class StringMessageTranslator(AbstractTranslator):
        def translate(self, raw_message: dict):
            return {"content": str(raw_message), "metadata": {}}

    return StringMessageTranslator()
