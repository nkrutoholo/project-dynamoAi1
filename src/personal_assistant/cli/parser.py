import shlex


def parse_input(user_input: str) -> tuple[str, list[str]]:
    try:
        parts = shlex.split(user_input.strip())
    except ValueError:
        return "", []

    if not parts:
        return "", []

    command = parts[0].lower()
    args = parts[1:]
    return command, args
