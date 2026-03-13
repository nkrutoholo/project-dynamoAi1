from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from rich.console import Console

from personal_assistant.books.address_book import AddressBook
from personal_assistant.books.notes_book import NotesBook
from personal_assistant.cli.parser import parse_input
from personal_assistant.cli.command_suggester import suggest_command
from personal_assistant.cli.completer import command_completer
from personal_assistant.storage.json_storage import JsonStorage
from personal_assistant.models.record import Record
from personal_assistant.models.note import Note
from personal_assistant.utils.decorators import input_error
from personal_assistant.utils.formatters import format_contacts, format_notes
from personal_assistant.utils.validators import (
    validate_birthday,
    validate_email,
    validate_phone,
    validate_note_id,
)

console = Console()
history = InMemoryHistory()

address_book = AddressBook()
notes_book = NotesBook()


def _prompt_with_cancel(prompt_text: str) -> str:
    bindings = KeyBindings()
    cancel_token = "__CANCEL_INPUT__"

    @bindings.add("escape")
    def _(event):
        event.app.exit(result=cancel_token)

    value = prompt(prompt_text, key_bindings=bindings).strip()
    if value == cancel_token:
        raise ValueError("Input cancelled.")
    return value


def prompt_required_field(
    prompt_text: str,
    validator=None,
    error_message: str = "Invalid value.",
) -> str:
    while True:
        value = _prompt_with_cancel(prompt_text)
        if not value:
            console.print("[red]This field is required.[/red]")
            continue

        if validator and not validator(value):
            console.print(f"[red]{error_message}[/red]")
            continue

        return value


def get_contact_by_name(name: str) -> Record:
    record = address_book.find(name)
    if not record:
        raise KeyError("Contact not found.")
    return record


def _update_contact_field(
    args: list[str],
    field_name: str,
    setter_name: str,
    prompt_text: str,
    validator=None,
    error_message: str = "Invalid value.",
    existing_getter=None,
    is_add: bool = False,
    action_word: str | None = None,
) -> str:
    name = args[0].strip() if len(args) > 0 else None
    value = args[1].strip() if len(args) > 1 else None

    if not name:
        name = prompt_required_field("Name: ")

    record = get_contact_by_name(name)

    if is_add and existing_getter and existing_getter(record):
        edit_cmd = f"edit-{field_name}"
        raise ValueError(f"{field_name.capitalize()} already exists. Use {edit_cmd} to change it.")

    if not value:
        value = prompt_required_field(prompt_text, validator=validator, error_message=error_message)
    elif validator and not validator(value):
        console.print(f"[red]Invalid {field_name} passed in command.[/red]")
        value = prompt_required_field(prompt_text, validator=validator, error_message=error_message)

    getattr(record, setter_name)(value)
    action = action_word or ("added" if is_add else "updated")
    return f"{field_name.capitalize()} {action} for '{record.name.value}'."


@input_error
def add_contact(args: list[str]) -> str:
    name = args[0].strip() if len(args) > 0 else None
    phone = args[1].strip() if len(args) > 1 else None

    if not name:
        name = prompt_required_field("Name: ")

    phone_err = "Phone must be in format +380XXXXXXXXX or 0XXXXXXXXX."
    if phone and not validate_phone(phone):
        console.print(f"[red]{phone_err}[/red]")
        phone = None
    if not phone:
        phone = prompt_required_field("Phone: ", validate_phone, phone_err)

    record = Record(name)
    record.add_phone(phone)
    address_book.add_record(record)
    return "Contact added."


@input_error
def show_contact(args: list[str]) -> str:
    if not args:
        name = prompt_required_field("Name: ")
    else:
        name = " ".join(args).strip()

    record = get_contact_by_name(name)
    return str(record)


@input_error
def edit_contact(args: list[str]) -> str:
    old_name = args[0].strip() if len(args) > 0 else None
    new_name = args[1].strip() if len(args) > 1 else None

    if not old_name:
        old_name = prompt_required_field("Current name: ")
    if not new_name:
        new_name = prompt_required_field("New name: ")

    record = get_contact_by_name(old_name)
    old_key = old_name.strip().lower()

    record.name.value = new_name
    new_key = record.name.value.lower()

    if old_key != new_key:
        if new_key in address_book.data:
            record.name.value = old_name
            raise ValueError(f"Contact '{new_name}' already exists.")
        del address_book.data[old_key]
        address_book.data[new_key] = record

    return f"Contact renamed to '{record.name.value}'."


@input_error
def add_phone(args: list[str]) -> str:
    return _update_contact_field(
        args, "phone", "add_phone", "Phone: ",
        validate_phone, "Phone must be in format +380XXXXXXXXX or 0XXXXXXXXX.",
        is_add=True,
    )


@input_error
def edit_phone(args: list[str]) -> str:
    name = args[0].strip() if len(args) > 0 else None
    old_phone = args[1].strip() if len(args) > 1 else None
    new_phone = args[2].strip() if len(args) > 2 else None

    if not name:
        name = prompt_required_field("Name: ")

    record = get_contact_by_name(name)
    phone_err = "Phone must be in format +380XXXXXXXXX or 0XXXXXXXXX."

    if old_phone and not validate_phone(old_phone):
        console.print(f"[red]{phone_err}[/red]")
        old_phone = None
    if not old_phone:
        old_phone = prompt_required_field("Old phone: ", validate_phone, phone_err)

    if new_phone and not validate_phone(new_phone):
        console.print(f"[red]{phone_err}[/red]")
        new_phone = None
    if not new_phone:
        new_phone = prompt_required_field("New phone: ", validate_phone, phone_err)

    record.edit_phone(old_phone, new_phone)
    return f"Phone updated for '{record.name.value}'."


@input_error
def remove_phone(args: list[str]) -> str:
    return _update_contact_field(
        args, "phone", "remove_phone", "Phone to remove: ",
        action_word="removed",
    )


@input_error
def add_email(args: list[str]) -> str:
    return _update_contact_field(
        args, "email", "set_email", "Email: ",
        validate_email, "Invalid email format.",
        existing_getter=lambda r: r.email, is_add=True,
    )


@input_error
def edit_email(args: list[str]) -> str:
    return _update_contact_field(
        args, "email", "set_email", "New email: ",
        validate_email, "Invalid email format.",
    )


@input_error
def add_address(args: list[str]) -> str:
    return _update_contact_field(
        args, "address", "set_address", "Address: ",
        existing_getter=lambda r: r.address, is_add=True,
    )


@input_error
def edit_address(args: list[str]) -> str:
    return _update_contact_field(
        args, "address", "set_address", "New address: ",
    )


@input_error
def add_birthday(args: list[str]) -> str:
    return _update_contact_field(
        args, "birthday", "set_birthday", "Birthday (DD.MM.YYYY): ",
        validate_birthday, "Birthday must be in format DD.MM.YYYY.",
        existing_getter=lambda r: r.birthday, is_add=True,
    )


@input_error
def edit_birthday(args: list[str]) -> str:
    return _update_contact_field(
        args, "birthday", "set_birthday", "New birthday (DD.MM.YYYY): ",
        validate_birthday, "Birthday must be in format DD.MM.YYYY.",
    )


@input_error
def all_contacts(_: list[str]) -> str:
    return format_contacts(address_book.all_records())


@input_error
def find_contact(args: list[str]) -> str:
    if not args:
        query = prompt_required_field("Search query: ")
    else:
        query = " ".join(args).strip()

    results = address_book.search(query)
    return format_contacts(results)


@input_error
def delete_contact(args: list[str]) -> str:
    if not args:
        name = prompt_required_field("Name: ")
    else:
        name = " ".join(args).strip()

    address_book.delete(name)
    return f"Contact '{name}' deleted."


@input_error
def birthdays(args: list[str]) -> str:
    if not args:
        days_raw = prompt_required_field("Days: ")
    else:
        days_raw = args[0].strip()

    if not days_raw.isdigit():
        raise ValueError("Days must be a positive integer.")

    results = address_book.get_upcoming_birthdays(int(days_raw))
    return format_contacts(results)


def _get_note_by_id(note_id_raw: str) -> Note:
    validated_id = validate_note_id(note_id_raw)
    note = notes_book.get_note_by_id(validated_id)
    if not note:
        raise KeyError("Note not found.")
    return note


@input_error
def add_note(args: list[str]) -> str:
    text = args[0].strip() if len(args) > 0 else None
    raw_tags = [arg.strip() for arg in args[1:]] if len(args) > 1 else []

    if not text:
        text = prompt_required_field("Text: ")

    if not raw_tags:
        tags_input = _prompt_with_cancel("Tags (space separated, optional): ")
        raw_tags = [t.strip() for t in tags_input.split() if t.strip()]

    note = Note(text=text, tags=raw_tags if raw_tags else None)
    notes_book.add_note(note)
    return f"Note added with ID {note.id}."


@input_error
def show_note(args: list[str]) -> str:
    if not args:
        note_id_raw = prompt_required_field("Note ID: ")
    else:
        note_id_raw = args[0].strip()

    note = _get_note_by_id(note_id_raw)
    return str(note)


@input_error
def edit_note(args: list[str]) -> str:
    if not args:
        note_id_raw = prompt_required_field("Note ID: ")
    else:
        note_id_raw = args[0].strip()

    note = _get_note_by_id(note_id_raw)

    console.print(f"[dim]Current text: {note.text}[/dim]")
    new_text = _prompt_with_cancel("New text (leave empty to keep): ")

    tags_str = ", ".join(tag.value for tag in note.tags) if note.tags else "-"
    console.print(f"[dim]Current tags: {tags_str}[/dim]")
    new_tags_input = _prompt_with_cancel("New tags (space separated, leave empty to keep): ")

    changed = False

    if new_text:
        note.text = new_text
        changed = True

    if new_tags_input:
        new_tags = [t.strip() for t in new_tags_input.split() if t.strip()]
        for tag in list(note.tags):
            note.delete_tag(tag.value)
        for tag in new_tags:
            note.add_tag(tag)
        changed = True

    if not changed:
        return "Nothing changed."

    return f"Note {note.id} updated."


@input_error
def delete_note(args: list[str]) -> str:
    if not args:
        note_id_raw = prompt_required_field("Note ID: ")
    else:
        note_id_raw = args[0].strip()

    validated_id = validate_note_id(note_id_raw)
    if not notes_book.delete_note(validated_id):
        raise KeyError("Note not found.")
    return f"Note {validated_id} deleted."


@input_error
def all_notes(_: list[str]) -> str:
    return format_notes(notes_book.all_notes())


@input_error
def find_note(args: list[str]) -> str:
    if not args:
        query = prompt_required_field("Search query: ")
    else:
        query = " ".join(args).strip()

    results = notes_book.find_notes(query)
    return format_notes(results)


@input_error
def add_tag(args: list[str]) -> str:
    if not args:
        note_id_raw = prompt_required_field("Note ID: ")
    else:
        note_id_raw = args[0].strip()

    note = _get_note_by_id(note_id_raw)
    raw_tags = [arg.strip() for arg in args[1:]] if len(args) > 1 else []

    if not raw_tags:
        tags_input = prompt_required_field("Tags (space separated): ")
        raw_tags = [t.strip() for t in tags_input.split() if t.strip()]

    for tag in raw_tags:
        note.add_tag(tag)

    return f"Tags added to note {note.id}."


@input_error
def delete_tag(args: list[str]) -> str:
    if len(args) < 1:
        note_id_raw = prompt_required_field("Note ID: ")
    else:
        note_id_raw = args[0].strip()

    note = _get_note_by_id(note_id_raw)

    if len(args) < 2:
        tag = prompt_required_field("Tag to delete: ")
    else:
        tag = args[1].strip()

    if not note.delete_tag(tag):
        raise ValueError(f"Tag '{tag}' not found on note {note.id}.")
    return f"Tag '{tag}' deleted from note {note.id}."


@input_error
def change_tag(args: list[str]) -> str:
    if len(args) < 1:
        note_id_raw = prompt_required_field("Note ID: ")
    else:
        note_id_raw = args[0].strip()

    note = _get_note_by_id(note_id_raw)

    if len(args) < 2:
        old_tag = prompt_required_field("Old tag: ")
    else:
        old_tag = args[1].strip()

    if len(args) < 3:
        new_tag = prompt_required_field("New tag: ")
    else:
        new_tag = args[2].strip()

    if not note.change_tag(old_tag, new_tag):
        raise ValueError(f"Tag '{old_tag}' not found on note {note.id}.")
    return f"Tag changed from '{old_tag}' to '{new_tag}' on note {note.id}."


@input_error
def has_tag(args: list[str]) -> str:
    if len(args) < 1:
        note_id_raw = prompt_required_field("Note ID: ")
    else:
        note_id_raw = args[0].strip()

    note = _get_note_by_id(note_id_raw)

    if len(args) < 2:
        tag = prompt_required_field("Tag: ")
    else:
        tag = args[1].strip()

    if note.has_tag(tag):
        return f"Note {note.id} has tag '{tag}'."
    return f"Note {note.id} does not have tag '{tag}'."


@input_error
def find_by_tag(args: list[str]) -> str:
    if not args:
        tag = prompt_required_field("Tag: ")
    else:
        tag = args[0].strip()

    results = notes_book.find_by_tag(tag)
    return format_notes(results)


@input_error
def sort_notes_by_tags(_: list[str]) -> str:
    notes = notes_book.all_notes()
    sorted_notes = sorted(
        notes,
        key=lambda n: (
            tuple(t.value for t in sorted(n.tags, key=lambda t: t.value)),
            n.id,
        ),
    )
    return format_notes(sorted_notes)


def show_help() -> None:
    console.print("[bold cyan]Personal Assistant[/bold cyan]")
    console.print("Available commands:")
    console.print("  help")
    console.print("  add-contact <name> <phone>")
    console.print("  show-contact <name>")
    console.print("  edit-contact <old_name> <new_name>")
    console.print("  delete-contact <name>")
    console.print("  all-contacts")
    console.print("  find-contact <query>")
    console.print("  add-phone <name> <phone>")
    console.print("  edit-phone <name> <old_phone> <new_phone>")
    console.print("  remove-phone <name> <phone>")
    console.print("  add-email <name> <email>")
    console.print("  edit-email <name> <email>")
    console.print("  add-address <name> <address>")
    console.print("  edit-address <name> <address>")
    console.print("  add-birthday <name> <birthday: DD.MM.YYYY>")
    console.print("  edit-birthday <name> <birthday: DD.MM.YYYY>")
    console.print("  birthdays <days>")
    console.print('  add-note "<text>" [tag1] [tag2] ...')
    console.print("  show-note <id>")
    console.print("  edit-note <id>")
    console.print("  delete-note <id>")
    console.print("  all-notes")
    console.print("  find-note <query>")
    console.print("  add-tag <id> <tag1> [tag2] ...")
    console.print("  delete-tag <id> <tag>")
    console.print("  change-tag <id> <old_tag> <new_tag>")
    console.print("  has-tag <id> <tag>")
    console.print("  find-by-tag <tag>")
    console.print("  sort-notes-by-tags")
    console.print("  exit | quit | close")
    console.print("[dim]Tip: press Esc while entering a field to cancel the current command.[/dim]")


def _save_all() -> None:
    JsonStorage.save_address_book(address_book)
    JsonStorage.save_notes_book(notes_book)


def run_cli() -> None:
    global address_book, notes_book
    address_book = JsonStorage.load_address_book()
    notes_book = JsonStorage.load_notes_book()

    show_help()

    handlers = {
        "help": lambda _: (show_help() or ""),
        "add-contact": add_contact,
        "show-contact": show_contact,
        "edit-contact": edit_contact,
        "delete-contact": delete_contact,
        "all-contacts": all_contacts,
        "find-contact": find_contact,
        "add-phone": add_phone,
        "edit-phone": edit_phone,
        "remove-phone": remove_phone,
        "add-email": add_email,
        "edit-email": edit_email,
        "add-address": add_address,
        "edit-address": edit_address,
        "add-birthday": add_birthday,
        "edit-birthday": edit_birthday,
        "birthdays": birthdays,
        "add-note": add_note,
        "show-note": show_note,
        "edit-note": edit_note,
        "delete-note": delete_note,
        "all-notes": all_notes,
        "find-note": find_note,
        "add-tag": add_tag,
        "delete-tag": delete_tag,
        "change-tag": change_tag,
        "has-tag": has_tag,
        "find-by-tag": find_by_tag,
        "sort-notes-by-tags": sort_notes_by_tags,
    }

    while True:
        user_input = prompt(">>> ", completer=command_completer, history=history)
        command, args = parse_input(user_input)

        if not command:
            continue

        if command in ("exit", "quit", "close"):
            _save_all()
            console.print("[bold red]Good bye![/bold red]")
            break

        handler = handlers.get(command)
        if handler:
            result = handler(args)
            if result:
                console.print(result)
            _save_all()
            continue

        suggested = suggest_command(command)
        if suggested:
            console.print(f"[yellow]Unknown command. Did you mean:[/yellow] [bold]{suggested}[/bold]?")
        else:
            console.print("[red]Unknown command.[/red]")
