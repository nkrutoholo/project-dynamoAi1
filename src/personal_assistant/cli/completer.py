from __future__ import annotations

from prompt_toolkit.completion import FuzzyCompleter, WordCompleter

COMMANDS = [
    "help",
    "add-contact",
    "edit-contact",
    "show-contact",
    "delete-contact",
    "all-contacts",
    "find-contact",
    "add-phone",
    "edit-phone",
    "remove-phone",
    "add-email",
    "edit-email",
    "add-address",
    "edit-address",
    "add-birthday",
    "edit-birthday",
    "birthdays",
    "add-note",
    "show-note",
    "edit-note",
    "delete-note",
    "all-notes",
    "find-note",
    "add-tag",
    "delete-tag",
    "change-tag",
    "has-tag",
    "find-by-tag",
    "sort-notes-by-tags",
    "exit",
    "quit",
    "close",
]

command_completer = FuzzyCompleter(WordCompleter(COMMANDS, ignore_case=True, sentence=True))
