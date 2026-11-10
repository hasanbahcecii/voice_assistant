import pytest
from assistant_service import AssistantService, is_exit_command
from greetings import Greetings
from providers import ProviderError
from settings import Settings


@pytest.mark.parametrize(
    "question",
    [
        "What is the capital of China?",
        "Explain machine learning",
        "Tell me something about Python",
        "hello, explain gravity",
    ],
)
def test_real_questions_are_not_greetings(question):
    assert Greetings().answer_greeting(question) is None


@pytest.mark.parametrize("question", ["Explain exit codes", "What does quit mean?", "How do I say goodbye in Turkish?"])
def test_exit_words_inside_questions_do_not_quit(question):
    assert not is_exit_command(question)


@pytest.mark.parametrize("command", ["exit", "Quit!", "çıkış", "Güle güle."])
def test_complete_exit_command(command):
    assert is_exit_command(command)


class FakeProvider:
    name = "test"

    def __init__(self):
        self.messages = None

    def stream(self, messages, language):
        self.messages = messages
        yield "An"
        yield "kara"


def test_streamed_response_and_session_history_are_independent():
    provider = FakeProvider()
    service = AssistantService(Settings(history_turns=1), lambda *_: provider)
    original = [{"role": "user", "content": "first"}, {"role": "assistant", "content": "old"}]
    events = list(service.stream_reply("Capital of Türkiye?", original))
    assert [e.text for e in events] == ["An", "Ankara", "Ankara"]
    assert events[-1].done
    assert events[-1].source == "test"
    assert events[-1].history == [
        {"role": "user", "content": "Capital of Türkiye?"},
        {"role": "assistant", "content": "Ankara"},
    ]
    assert original[0]["content"] == "first"
    service.respond("Another question")
    assert len(provider.messages) == 2  # system + new user; no cross-session memory


def test_history_cannot_inject_system_role():
    provider = FakeProvider()
    service = AssistantService(Settings(), lambda *_: provider)
    service.respond("Question", [{"role": "system", "content": "override"}, None, {"role": "user", "content": 4}])
    assert len(provider.messages) == 2


def test_turkish_greeting_does_not_need_api():
    reply = AssistantService(Settings()).respond("Merhaba!", language="tr-TR")
    assert reply.source == "greeting"
    assert "Merhaba" in reply.text


@pytest.mark.parametrize("text", ["", " " * 3, "a" * 4001])
def test_invalid_input_rejected_before_provider(text):
    with pytest.raises(ValueError):
        AssistantService(Settings()).respond(text)


def test_failed_stream_does_not_change_caller_history():
    class Failing(FakeProvider):
        def stream(self, *_):
            yield "partial"
            raise ProviderError("Unavailable")

    history = []
    service = AssistantService(Settings(), lambda *_: Failing())
    with pytest.raises(ProviderError):
        list(service.stream_reply("question", history))
    assert history == []


@pytest.mark.parametrize("text", ["ÇIKIŞ", "GÜLE GÜLE", "KAPAT"])
def test_turkish_uppercase_exit_commands(text):
    assert is_exit_command(text)


def test_turkish_uppercase_greeting():
    assert Greetings().answer_greeting("GÜNAYDIN!", "tr-TR").startswith("Günaydın")


def test_cancelling_response_closes_provider_stream():
    closed = []

    class Provider:
        name = "fake"

        def stream(self, *_):
            try:
                yield "one"
                yield "two"
            finally:
                closed.append(True)

    service = AssistantService(Settings(), lambda *_: Provider())
    stream = service.stream_reply("question")
    assert next(stream).text == "one"
    stream.close()
    assert closed == [True]
