import json

import pytest

from pyinsole.ext.aws.translators import SQSMessageTranslator


@pytest.fixture
def sqs_translator():
    return SQSMessageTranslator()


def test_translate_sqs(sqs_translator):
    original = {"Body": json.dumps("some-content")}
    content = sqs_translator.translate(original)
    assert "content" in content
    assert content["content"] == "some-content"

    original = {"Body": json.dumps({"key": "value"})}
    content = sqs_translator.translate(original)
    assert content["content"] == {"key": "value"}


def test_sqs_metadata_extract(sqs_translator):
    original = {"Body": json.dumps("some-content"), "whatever": "whatever"}
    content = sqs_translator.translate(original)
    metadata = content["metadata"]
    assert metadata
    assert "whatever" in metadata
    assert metadata["whatever"] == "whatever"


@pytest.fixture(params=[{"invalid": "format"}, "invalid format", 42, {}, [], (), ""])
def parametrize_invalid_messages(request):
    return request.param


def test_translate_sqs_handles_invalid_format(sqs_translator, parametrize_invalid_messages):
    content = sqs_translator.translate(parametrize_invalid_messages)
    assert content["content"] is None


def test_translate_sqs_handles_json_error(sqs_translator):
    original = {"Body": "invalid: json"}
    content = sqs_translator.translate(original)
    assert content["content"] is None
