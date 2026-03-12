from __future__ import annotations

from pathlib import Path
import os

APP_DIR_NAME = ".personal_assistant"
CONTACTS_FILE_NAME = "contacts.json"
NOTES_FILE_NAME = "notes.json"
HISTORY_FILE_NAME = "history.txt"
DATE_FORMAT = "%d.%m.%Y"


def get_data_dir() -> Path:
    custom = os.getenv("PERSONAL_ASSISTANT_DATA_DIR")
    if custom:
        return Path(custom).expanduser().resolve()
    return (Path.home() / APP_DIR_NAME).resolve()


def get_contacts_file() -> Path:
    return get_data_dir() / CONTACTS_FILE_NAME


def get_notes_file() -> Path:
    return get_data_dir() / NOTES_FILE_NAME


def get_history_file() -> Path:
    return get_data_dir() / HISTORY_FILE_NAME
