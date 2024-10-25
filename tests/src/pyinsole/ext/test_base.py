from unittest import mock

import pytest

from pyinsole.ext.aws.base import BaseSQSProvider


@pytest.fixture
def base_sqs_provider():
    return BaseSQSProvider()


@pytest.mark.asyncio
async def test_get_queue_url(mock_boto_session_sqs, boto_client_sqs, base_sqs_provider):
    with mock_boto_session_sqs as mock_sqs:
        queue_url = await base_sqs_provider.get_queue_url("queue-name")
        assert queue_url.startswith("https://")
        assert queue_url.endswith("queue-name")

        assert mock_sqs.called
        assert boto_client_sqs.get_queue_url.called
        assert boto_client_sqs.get_queue_url.call_args == mock.call(QueueName="queue-name")


@pytest.mark.asyncio
async def test_cache_get_queue_url(mock_boto_session_sqs, boto_client_sqs, base_sqs_provider):
    with mock_boto_session_sqs:
        await base_sqs_provider.get_queue_url("queue-name")
        queue_url = await base_sqs_provider.get_queue_url("queue-name")
        assert queue_url.startswith("https://")
        assert queue_url.endswith("queue-name")
        assert boto_client_sqs.get_queue_url.call_count == 1


@pytest.mark.asyncio
async def test_get_queue_url_when_queue_name_is_url(
    mock_boto_session_sqs, boto_client_sqs, base_sqs_provider
):
    with mock_boto_session_sqs:
        queue_url = await base_sqs_provider.get_queue_url("https://aws-whatever/queue-name")
        assert queue_url.startswith("https://")
        assert queue_url.endswith("queue-name")
        assert boto_client_sqs.get_queue_url.call_count == 0


@pytest.mark.asyncio
async def test_sqs_get_client(mock_boto_session_sqs, base_sqs_provider, boto_client_sqs):
    with mock_boto_session_sqs as mock_session:
        client_generator = base_sqs_provider.get_client()
        assert mock_session.called
        async with client_generator as client:
            assert boto_client_sqs is client
