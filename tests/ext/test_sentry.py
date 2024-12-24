from typing import TYPE_CHECKING
from unittest import mock

import pytest
import sentry_sdk.envelope
from faker import Faker

if TYPE_CHECKING:
    import sentry_sdk
else:
    sentry_sdk = pytest.importorskip("sentry_sdk")

from pyinsole.ext.sentry import sentry_handler

pytestmark = pytest.mark.asyncio


async def test_sentry_handler_defaults(faker: Faker):
    error_handler = sentry_handler()
    given_message = faker.pydict()
    given_exception = Exception()

    with (
        sentry_sdk.isolation_scope(),
        mock.patch("pyinsole.ext.sentry.sentry_sdk.capture_exception") as mock_capture_exception,
    ):
        current_scope = sentry_sdk.get_current_scope()
        got = await error_handler(given_exception, given_message)

    assert got is False
    assert current_scope._extras.get("message") == given_message  # noqa: SLF001
    mock_capture_exception.assert_called_once_with(given_exception)


async def test_sentry_handler_delete_message(faker: Faker):
    error_handler = sentry_handler(delete_message=True)
    given_message = faker.pydict()
    given_exception = Exception()

    with (
        sentry_sdk.isolation_scope(),
        mock.patch("pyinsole.ext.sentry.sentry_sdk.capture_exception") as mock_capture_exception,
    ):
        current_scope = sentry_sdk.get_current_scope()
        got = await error_handler(given_exception, given_message)

    assert got is True
    assert current_scope._extras.get("message") == given_message  # noqa: SLF001
    mock_capture_exception.assert_called_once_with(given_exception)
