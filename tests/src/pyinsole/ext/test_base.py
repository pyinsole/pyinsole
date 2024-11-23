
import pytest

from pyinsole.ext.aws.base import BaseSQSProvider


@pytest.fixture
def base_sqs_provider():
    return BaseSQSProvider()


@pytest.mark.asyncio
async def test_sqs_get_client(mock_boto_session_sqs, base_sqs_provider, boto_client_sqs):
    with mock_boto_session_sqs as mock_session:
        client_generator = base_sqs_provider.get_client()
        assert mock_session.called
        async with client_generator as client:
            assert boto_client_sqs is client
