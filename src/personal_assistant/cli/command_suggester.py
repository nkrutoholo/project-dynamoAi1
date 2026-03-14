from difflib import get_close_matches

from personal_assistant.cli.completer import COMMANDS


def suggest_command(command: str) -> str | None:
    matches = [c for c in COMMANDS if c.startswith(command)]
    if matches:
        return matches[0]
    matches = get_close_matches(command, COMMANDS, n=1, cutoff=0.5)
    return matches[0] if matches else None
