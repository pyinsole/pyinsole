from pyinsole.ext.aws.translators import SQSMessageTranslator
from pyinsole.ext.aws.providers import SQSProvider
from pyinsole.ext.aws.routes import SQSRoute


def test_sqs_route(dummy_handler):
    route = SQSRoute("what", handler=dummy_handler)
    assert isinstance(route.translator, SQSMessageTranslator)
    assert isinstance(route.provider, SQSProvider)
    assert route.name == "what"


def test_sqs_route_keep_message_translator(dummy_handler, dummy_translator):
    route = SQSRoute("what", handler=dummy_handler, translator=dummy_translator)
    assert isinstance(route.translator, dummy_translator.__class__)


def test_sqs_route_keep_name(dummy_handler):
    route = SQSRoute("what", handler=dummy_handler, name="foobar")
    assert route.name == "foobar"


def test_sqs_route_provider_options(dummy_handler):
    route = SQSRoute("what", handler=dummy_handler, provider_options={"use_ssl": False}, name="foobar")
    assert "use_ssl" in route.provider._client_options  # noqa: SLF001
    assert route.provider._client_options["use_ssl"] is False  # noqa: SLF001
