import pytest

from personal_assistant.cli.command_suggester import suggest_command
from personal_assistant.cli.parser import parse_input


class TestParser:
    def test_simple_command(self):
        cmd, args = parse_input("find-contact John Doe")
        assert cmd == "find-contact"
        assert args == ["John", "Doe"]

    def test_quoted_string(self):
        cmd, args = parse_input('add-note "Buy milk and eggs" home')
        assert cmd == "add-note"
        assert args == ["Buy milk and eggs", "home"]

    def test_empty_input(self):
        cmd, args = parse_input("   ")
        assert cmd == ""
        assert args == []

    def test_command_lowercased(self):
        cmd, args = parse_input("ADD-CONTACT John")
        assert cmd == "add-contact"

    def test_single_command_no_args(self):
        cmd, args = parse_input("all-contacts")
        assert cmd == "all-contacts"
        assert args == []

    def test_extra_whitespace(self):
        cmd, args = parse_input("  add-phone   John   +380991112233  ")
        assert cmd == "add-phone"
        assert args == ["John", "+380991112233"]

    def test_unclosed_quote_returns_empty(self):
        cmd, args = parse_input('add-note "unclosed quote')
        assert cmd == ""
        assert args == []

    def test_multiple_quoted_args(self):
        cmd, args = parse_input('edit-phone "John Doe" "+380991112233" "+380997776655"')
        assert cmd == "edit-phone"
        assert args == ["John Doe", "+380991112233", "+380997776655"]


class TestCommandSuggester:
    def test_close_match(self):
        assert suggest_command("ad-contact") == "add-contact"

    def test_no_match(self):
        assert suggest_command("xyzabc") is None

    def test_typo_in_note_command(self):
        result = suggest_command("add-noe")
        assert result == "add-note"

    def test_missing_dash(self):
        result = suggest_command("addcontact")
        assert result == "add-contact"

    def test_exact_match_returns_self(self):
        assert suggest_command("help") == "help"

    def test_exit_suggestion(self):
        result = suggest_command("exut")
        assert result == "exit"
