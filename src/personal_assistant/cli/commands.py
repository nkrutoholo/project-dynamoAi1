from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from rich.console import Console

from personal_assistant.books.address_book import AddressBook
from personal_assistant.books.notes_book import NotesBook
from personal_assistant.storage.json_storage import JsonStorage
from personal_assistant.models.record import Record
from personal_assistant.utils.decorators import input_error
from personal_assistant.utils.formatters import format_contacts
from personal_assistant.utils.validators import (
    validate_birthday,
    validate_email,
    validate_phone,
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
