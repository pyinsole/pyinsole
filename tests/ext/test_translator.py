import json

import pytest

from pyinsole.ext.aws.translators import SNSMessageTranslator, SQSMessageTranslator


class TestSQSMessageTranslator:
    def test_translate_sqs(self):
        original = {"Body": json.dumps("some-content")}
        sqs_translator = SQSMessageTranslator()

        content = sqs_translator.translate(original)

        assert "content" in content
        assert content["content"] == "some-content"

        original = {"Body": json.dumps({"key": "value"})}
        content = sqs_translator.translate(original)
        assert content["content"] == {"key": "value"}

    def test_sqs_metadata_extract(self):
        original = {"Body": json.dumps("some-content"), "whatever": "whatever"}
        sqs_translator = SQSMessageTranslator()

        content = sqs_translator.translate(original)

        metadata = content["metadata"]
        assert metadata
        assert "whatever" in metadata
        assert metadata["whatever"] == "whatever"

    @pytest.mark.parametrize("message", [{"invalid": "format"}, "invalid format", 42, {}, [], (), ""])
    def test_translate_sqs_handles_invalid_format(self, message):
        sqs_translator = SQSMessageTranslator()

        content = sqs_translator.translate(message)

        assert content["content"] is None

    def test_translate_sqs_handles_json_error(self):
        original = {"Body": "invalid: json"}
        sqs_translator = SQSMessageTranslator()

        content = sqs_translator.translate(original)

        assert content["content"] is None


class TestSNSMessageTranslator:
    def test_translate_sns(self):
        message_content = "here I am"
        message = json.dumps({"Message": json.dumps(message_content)})
        original = {"Body": message}
        sns_translator = SNSMessageTranslator()

        content = sns_translator.translate(original)

        assert content["content"] == message_content

        message_content = {"here": "I am"}
        message = json.dumps({"Message": json.dumps(message_content)})
        original = {"Body": message}
        content = sns_translator.translate(original)
        assert content["content"] == message_content

    def test_sns_metadata_extract(self):
        message_content = "here I am"
        message = json.dumps({"Message": json.dumps(message_content), "foo": "nested"})
        original = {"Body": message, "bar": "not nested"}
        sns_translator = SNSMessageTranslator()

        content = sns_translator.translate(original)

        metadata = content["metadata"]
        assert metadata
        assert "foo" in metadata
        assert metadata["foo"] == "nested"
        assert "bar" in metadata
        assert metadata["bar"] == "not nested"

    @pytest.mark.parametrize("content", [{"invalid": "format"}, "invalid format", 42, {}, [], (), ""])
    def test_translate_sns_handles_invalid_content(self, content):
        message = json.dumps({"Message": content})
        original = {"Body": message}
        sns_translator = SNSMessageTranslator()

        content = sns_translator.translate(original)

        assert content["content"] is None

    @pytest.mark.parametrize("message", [{"invalid": "format"}, "invalid format", 42, {}, [], (), ""])
    def test_translate_sns_handles_invalid_format(self, message):
        sns_translator = SNSMessageTranslator()

        content = sns_translator.translate(message)

        assert content["content"] is None
