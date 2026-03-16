import pytest

from personal_assistant.cli import commands
from personal_assistant.cli.commands import App


@pytest.fixture
def app(tmp_path, monkeypatch):
    monkeypatch.setenv("PERSONAL_ASSISTANT_DATA_DIR", str(tmp_path))
    monkeypatch.setattr(commands, "prompt", lambda *args, **kwargs: "__CANCEL_INPUT__")
    return App()


def test_prompt_with_cancel_raises(app):
    match_text = "Input cancelled."
    with pytest.raises(ValueError, match=match_text):
        app._prompt_with_cancel("Name: ")


def test_add_contact_returns_cancel_message(app):
    result = app.add_contact([])
    assert result == "Value error: Input cancelled."


def test_add_note_returns_cancel_message(app):
    result = app.add_note([])
    assert result == "Value error: Input cancelled."


def test_show_contact_returns_cancel_message(app):
    result = app.show_contact([])
    assert result == "Value error: Input cancelled."
