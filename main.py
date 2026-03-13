from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from personal_assistant.cli.commands import run_cli  # noqa: E402


if __name__ == "__main__":
    run_cli()
