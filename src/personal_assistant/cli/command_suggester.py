from __future__ import annotations

from difflib import get_close_matches

from personal_assistant.cli.completer import COMMANDS


def suggest_command(command: str) -> str | None:
    matches = get_close_matches(command, COMMANDS, n=1, cutoff=0.5)
    return matches[0] if matches else None
