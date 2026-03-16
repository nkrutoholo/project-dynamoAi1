from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from rich.console import Console

from personal_assistant.cli.command_suggester import suggest_command
from personal_assistant.cli.completer import command_completer
from personal_assistant.cli.parser import parse_input
from personal_assistant.models.note import Note
from personal_assistant.models.record import Record
from personal_assistant.storage.json_storage import JsonStorage
from personal_assistant.utils.decorators import input_error
from personal_assistant.utils.formatters import format_contacts, format_notes
from personal_assistant.utils.validators import (
    validate_birthday,
    validate_email,
    validate_note_id,
    validate_phone,
)


class App:
    def __init__(self):
        self.address_book = JsonStorage.load_address_book()
        self.notes_book = JsonStorage.load_notes_book()
        self.console = Console()
        self.history = InMemoryHistory()

    def _prompt_with_cancel(self, prompt_text: str) -> str:
        bindings = KeyBindings()
        cancel_token = "__CANCEL_INPUT__"

        @bindings.add("escape", eager=True)
        def _(event):
            event.app.exit(result=cancel_token)

        value = prompt(prompt_text, key_bindings=bindings).strip()
        if value == cancel_token:
            raise ValueError("Input cancelled.")
        return value

    def _prompt_required_field(
        self,
        prompt_text: str,
        validator=None,
        error_message: str = "Invalid value.",
    ) -> str:
        while True:
            value = self._prompt_with_cancel(prompt_text)
            if not value:
                self.console.print("[red]This field is required.[/red]")
                continue

            if validator and not validator(value):
                self.console.print(f"[red]{error_message}[/red]")
                continue

            return value

    def _get_contact_by_name(self, name: str) -> Record:
        record = self.address_book.find(name)
        if not record:
            raise KeyError("Contact not found.")
        return record

    def _update_contact_field(
        self,
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
            name = self._prompt_required_field("Name: ")

        record = self._get_contact_by_name(name)

        if is_add and existing_getter and existing_getter(record):
            edit_cmd = f"edit-{field_name}"
            raise ValueError(f"{field_name.capitalize()} already exists. Use {edit_cmd} to change it.")

        if not value:
            value = self._prompt_required_field(prompt_text, validator=validator, error_message=error_message)
        elif validator and not validator(value):
            self.console.print(f"[red]Invalid {field_name} passed in command.[/red]")
            value = self._prompt_required_field(prompt_text, validator=validator, error_message=error_message)

        getattr(record, setter_name)(value)
        action = action_word or ("added" if is_add else "updated")
        return f"{field_name.capitalize()} {action} for '{record.name.value}'."

    def _get_note_by_id(self, note_id_raw: str) -> Note:
        validated_id = validate_note_id(note_id_raw)
        note = self.notes_book.get_note_by_id(validated_id)
        if not note:
            raise KeyError("Note not found.")
        return note

    @input_error
    def add_contact(self, args: list[str]) -> str:
        name = args[0].strip() if len(args) > 0 else None
        phone = args[1].strip() if len(args) > 1 else None

        if not name:
            name = self._prompt_required_field("Name: ")

        phone_err = "Phone must be in format +380XXXXXXXXX or 0XXXXXXXXX."
        if phone and not validate_phone(phone):
            self.console.print(f"[red]{phone_err}[/red]")
            phone = None
        if not phone:
            phone = self._prompt_required_field("Phone: ", validate_phone, phone_err)

        record = Record(name)
        record.add_phone(phone)
        self.address_book.add_record(record)
        return "Contact added."

    @input_error
    def show_contact(self, args: list[str]) -> str:
        if not args:
            name = self._prompt_required_field("Name: ")
        else:
            name = " ".join(args).strip()

        record = self._get_contact_by_name(name)
        return str(record)

    @input_error
    def edit_contact(self, args: list[str]) -> str:
        old_name = args[0].strip() if len(args) > 0 else None
        new_name = args[1].strip() if len(args) > 1 else None

        if not old_name:
            old_name = self._prompt_required_field("Current name: ")
        if not new_name:
            new_name = self._prompt_required_field("New name: ")

        record = self._get_contact_by_name(old_name)
        old_key = old_name.strip().lower()

        record.name.value = new_name
        new_key = record.name.value.lower()

        if old_key != new_key:
            if new_key in self.address_book.data:
                record.name.value = old_name
                raise ValueError(f"Contact '{new_name}' already exists.")
            del self.address_book.data[old_key]
            self.address_book.data[new_key] = record

        return f"Contact renamed to '{record.name.value}'."

    @input_error
    def add_phone(self, args: list[str]) -> str:
        return self._update_contact_field(
            args,
            "phone",
            "add_phone",
            "Phone: ",
            validate_phone,
            "Phone must be in format +380XXXXXXXXX or 0XXXXXXXXX.",
            is_add=True,
        )

    @input_error
    def edit_phone(self, args: list[str]) -> str:
        name = args[0].strip() if len(args) > 0 else None
        old_phone = args[1].strip() if len(args) > 1 else None
        new_phone = args[2].strip() if len(args) > 2 else None

        if not name:
            name = self._prompt_required_field("Name: ")

        record = self._get_contact_by_name(name)
        phone_err = "Phone must be in format +380XXXXXXXXX or 0XXXXXXXXX."

        if old_phone and not validate_phone(old_phone):
            self.console.print(f"[red]{phone_err}[/red]")
            old_phone = None
        if not old_phone:
            old_phone = self._prompt_required_field("Old phone: ", validate_phone, phone_err)

        if new_phone and not validate_phone(new_phone):
            self.console.print(f"[red]{phone_err}[/red]")
            new_phone = None
        if not new_phone:
            new_phone = self._prompt_required_field("New phone: ", validate_phone, phone_err)

        record.edit_phone(old_phone, new_phone)
        return f"Phone updated for '{record.name.value}'."

    @input_error
    def delete_phone(self, args: list[str]) -> str:
        return self._update_contact_field(
            args,
            "phone",
            "remove_phone",
            "Phone to delete: ",
            action_word="deleted",
        )

    @input_error
    def add_email(self, args: list[str]) -> str:
        return self._update_contact_field(
            args,
            "email",
            "set_email",
            "Email: ",
            validate_email,
            "Invalid email format.",
            existing_getter=lambda r: r.email,
            is_add=True,
        )

    @input_error
    def edit_email(self, args: list[str]) -> str:
        return self._update_contact_field(
            args,
            "email",
            "set_email",
            "New email: ",
            validate_email,
            "Invalid email format.",
        )

    @input_error
    def add_address(self, args: list[str]) -> str:
        return self._update_contact_field(
            args,
            "address",
            "set_address",
            "Address: ",
            existing_getter=lambda r: r.address,
            is_add=True,
        )

    @input_error
    def edit_address(self, args: list[str]) -> str:
        return self._update_contact_field(
            args,
            "address",
            "set_address",
            "New address: ",
        )

    @input_error
    def add_birthday(self, args: list[str]) -> str:
        return self._update_contact_field(
            args,
            "birthday",
            "set_birthday",
            "Birthday (DD.MM.YYYY): ",
            validate_birthday,
            "Birthday must be in format DD.MM.YYYY.",
            existing_getter=lambda r: r.birthday,
            is_add=True,
        )

    @input_error
    def edit_birthday(self, args: list[str]) -> str:
        return self._update_contact_field(
            args,
            "birthday",
            "set_birthday",
            "New birthday (DD.MM.YYYY): ",
            validate_birthday,
            "Birthday must be in format DD.MM.YYYY.",
        )

    @input_error
    def delete_email(self, args: list[str]) -> str:
        if not args:
            name = self._prompt_required_field("Name: ")
        else:
            name = " ".join(args).strip()
        record = self._get_contact_by_name(name)
        if not record.email:
            raise ValueError(f"Contact '{record.name.value}' has no email.")
        record.set_email(None)
        return f"Email deleted for '{record.name.value}'."

    @input_error
    def delete_birthday(self, args: list[str]) -> str:
        if not args:
            name = self._prompt_required_field("Name: ")
        else:
            name = " ".join(args).strip()
        record = self._get_contact_by_name(name)
        if not record.birthday:
            raise ValueError(f"Contact '{record.name.value}' has no birthday.")
        record.set_birthday(None)
        return f"Birthday deleted for '{record.name.value}'."

    @input_error
    def delete_address(self, args: list[str]) -> str:
        if not args:
            name = self._prompt_required_field("Name: ")
        else:
            name = " ".join(args).strip()
        record = self._get_contact_by_name(name)
        if not record.address:
            raise ValueError(f"Contact '{record.name.value}' has no address.")
        record.set_address(None)
        return f"Address deleted for '{record.name.value}'."

    @input_error
    def all_contacts(self, _: list[str]) -> str:
        return format_contacts(self.address_book.all_records())

    @input_error
    def find_contact(self, args: list[str]) -> str:
        if not args:
            query = self._prompt_required_field("Search query: ")
        else:
            query = " ".join(args).strip()

        results = self.address_book.search(query)
        return format_contacts(results)

    @input_error
    def delete_contact(self, args: list[str]) -> str:
        if not args:
            name = self._prompt_required_field("Name: ")
        else:
            name = " ".join(args).strip()

        self.address_book.delete(name)
        return f"Contact '{name}' deleted."

    @input_error
    def birthdays(self, args: list[str]) -> str:
        if not args:
            days_raw = self._prompt_required_field("Days: ")
        else:
            days_raw = args[0].strip()

        if not days_raw.isdigit():
            raise ValueError("Days must be a positive integer.")

        results = self.address_book.get_upcoming_birthdays(int(days_raw))
        return format_contacts(results)

    @input_error
    def add_note(self, args: list[str]) -> str:
        text = args[0].strip() if len(args) > 0 else None
        raw_tags = [arg.strip() for arg in args[1:]] if len(args) > 1 else []

        if not text:
            text = self._prompt_required_field("Text: ")

        if not raw_tags:
            tags_input = self._prompt_with_cancel("Tags (space separated, optional): ")
            raw_tags = [t.strip() for t in tags_input.split() if t.strip()]

        note = Note(text=text, tags=raw_tags if raw_tags else None)
        self.notes_book.add_note(note)
        return f"Note added with ID {note.id}."

    @input_error
    def show_note(self, args: list[str]) -> str:
        if not args:
            note_id_raw = self._prompt_required_field("Note ID: ")
        else:
            note_id_raw = args[0].strip()

        note = self._get_note_by_id(note_id_raw)
        return str(note)

    @input_error
    def edit_note(self, args: list[str]) -> str:
        if not args:
            note_id_raw = self._prompt_required_field("Note ID: ")
        else:
            note_id_raw = args[0].strip()

        note = self._get_note_by_id(note_id_raw)

        self.console.print(f"[dim]Current text: {note.text}[/dim]")
        new_text = self._prompt_with_cancel("New text (leave empty to keep): ")

        tags_str = ", ".join(tag.value for tag in note.tags) if note.tags else "-"
        self.console.print(f"[dim]Current tags: {tags_str}[/dim]")
        new_tags_input = self._prompt_with_cancel("New tags (space separated, leave empty to keep): ")

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
    def delete_note(self, args: list[str]) -> str:
        if not args:
            note_id_raw = self._prompt_required_field("Note ID: ")
        else:
            note_id_raw = args[0].strip()

        validated_id = validate_note_id(note_id_raw)
        if not self.notes_book.delete_note(validated_id):
            raise KeyError("Note not found.")
        return f"Note {validated_id} deleted."

    @input_error
    def all_notes(self, _: list[str]) -> str:
        return format_notes(self.notes_book.all_notes())

    @input_error
    def find_note(self, args: list[str]) -> str:
        if not args:
            query = self._prompt_required_field("Search query: ")
        else:
            query = " ".join(args).strip()

        results = self.notes_book.find_notes(query)
        return format_notes(results)

    @input_error
    def add_tag(self, args: list[str]) -> str:
        if not args:
            note_id_raw = self._prompt_required_field("Note ID: ")
        else:
            note_id_raw = args[0].strip()

        note = self._get_note_by_id(note_id_raw)
        raw_tags = [arg.strip() for arg in args[1:]] if len(args) > 1 else []

        if not raw_tags:
            tags_input = self._prompt_required_field("Tags (space separated): ")
            raw_tags = [t.strip() for t in tags_input.split() if t.strip()]

        for tag in raw_tags:
            note.add_tag(tag)

        return f"Tags added to note {note.id}."

    @input_error
    def delete_tag(self, args: list[str]) -> str:
        if len(args) < 1:
            note_id_raw = self._prompt_required_field("Note ID: ")
        else:
            note_id_raw = args[0].strip()

        note = self._get_note_by_id(note_id_raw)

        if len(args) < 2:
            tag = self._prompt_required_field("Tag to delete: ")
        else:
            tag = args[1].strip()

        if not note.delete_tag(tag):
            raise ValueError(f"Tag '{tag}' not found on note {note.id}.")
        return f"Tag '{tag}' deleted from note {note.id}."

    @input_error
    def change_tag(self, args: list[str]) -> str:
        if len(args) < 1:
            note_id_raw = self._prompt_required_field("Note ID: ")
        else:
            note_id_raw = args[0].strip()

        note = self._get_note_by_id(note_id_raw)

        if len(args) < 2:
            old_tag = self._prompt_required_field("Old tag: ")
        else:
            old_tag = args[1].strip()

        if len(args) < 3:
            new_tag = self._prompt_required_field("New tag: ")
        else:
            new_tag = args[2].strip()

        if not note.change_tag(old_tag, new_tag):
            raise ValueError(f"Tag '{old_tag}' not found on note {note.id}.")
        return f"Tag changed from '{old_tag}' to '{new_tag}' on note {note.id}."

    @input_error
    def has_tag(self, args: list[str]) -> str:
        if len(args) < 1:
            note_id_raw = self._prompt_required_field("Note ID: ")
        else:
            note_id_raw = args[0].strip()

        note = self._get_note_by_id(note_id_raw)

        if len(args) < 2:
            tag = self._prompt_required_field("Tag: ")
        else:
            tag = args[1].strip()

        if note.has_tag(tag):
            return f"Note {note.id} has tag '{tag}'."
        return f"Note {note.id} does not have tag '{tag}'."

    @input_error
    def find_by_tag(self, args: list[str]) -> str:
        if not args:
            tag = self._prompt_required_field("Tag: ")
        else:
            tag = args[0].strip()

        results = self.notes_book.find_by_tag(tag)
        return format_notes(results)

    @input_error
    def sort_notes_by_tags(self, _: list[str]) -> str:
        notes = self.notes_book.all_notes()
        sorted_notes = sorted(
            notes,
            key=lambda n: (
                tuple(t.value for t in sorted(n.tags, key=lambda t: t.value)),
                n.id,
            ),
        )
        return format_notes(sorted_notes)

    @input_error
    def list_tags(self, _: list[str]) -> str:
        all_tags: set[str] = set()
        for note in self.notes_book.all_notes():
            for tag in note.tags:
                all_tags.add(tag.value)
        if not all_tags:
            return "No tags found."
        return "Tags: " + ", ".join(sorted(all_tags))

    def _show_help(self) -> None:
        self.console.print("[bold cyan]Personal Assistant[/bold cyan]")
        self.console.print("Available commands:")
        self.console.print("  help")
        self.console.print("  add-contact <name> <phone>")
        self.console.print("  show-contact <name>")
        self.console.print("  edit-contact <old_name> <new_name>")
        self.console.print("  delete-contact <name>")
        self.console.print("  all-contacts")
        self.console.print("  find-contact <query>")
        self.console.print("  add-phone <name> <phone>")
        self.console.print("  edit-phone <name> <old_phone> <new_phone>")
        self.console.print("  delete-phone <name> <phone>")
        self.console.print("  add-email <name> <email>")
        self.console.print("  edit-email <name> <email>")
        self.console.print("  add-address <name> <address>")
        self.console.print("  edit-address <name> <address>")
        self.console.print("  add-birthday <name> <birthday: DD.MM.YYYY>")
        self.console.print("  edit-birthday <name> <birthday: DD.MM.YYYY>")
        self.console.print("  delete-email <name>")
        self.console.print("  delete-birthday <name>")
        self.console.print("  delete-address <name>")
        self.console.print("  birthdays <days>")
        self.console.print('  add-note "<text>" [tag1] [tag2] ...')
        self.console.print("  show-note <id>")
        self.console.print("  edit-note <id>")
        self.console.print("  delete-note <id>")
        self.console.print("  all-notes")
        self.console.print("  find-note <query>")
        self.console.print("  add-tag <id> <tag1> [tag2] ...")
        self.console.print("  delete-tag <id> <tag>")
        self.console.print("  change-tag <id> <old_tag> <new_tag>")
        self.console.print("  has-tag <id> <tag>")
        self.console.print("  find-by-tag <tag>")
        self.console.print("  sort-notes-by-tags")
        self.console.print("  list-tags")
        self.console.print("  exit | quit | close")
        self.console.print("[dim]Tip: press Esc while entering a field to cancel the current command.[/dim]")

    def _save_all(self) -> None:
        JsonStorage.save_address_book(self.address_book)
        JsonStorage.save_notes_book(self.notes_book)

    def run(self) -> None:
        self._show_help()

        handlers = {
            "help": lambda _: self._show_help() or "",
            "add-contact": self.add_contact,
            "show-contact": self.show_contact,
            "edit-contact": self.edit_contact,
            "delete-contact": self.delete_contact,
            "all-contacts": self.all_contacts,
            "find-contact": self.find_contact,
            "add-phone": self.add_phone,
            "edit-phone": self.edit_phone,
            "delete-phone": self.delete_phone,
            "add-email": self.add_email,
            "edit-email": self.edit_email,
            "add-address": self.add_address,
            "edit-address": self.edit_address,
            "add-birthday": self.add_birthday,
            "edit-birthday": self.edit_birthday,
            "birthdays": self.birthdays,
            "delete-email": self.delete_email,
            "delete-birthday": self.delete_birthday,
            "delete-address": self.delete_address,
            "add-note": self.add_note,
            "show-note": self.show_note,
            "edit-note": self.edit_note,
            "delete-note": self.delete_note,
            "all-notes": self.all_notes,
            "find-note": self.find_note,
            "add-tag": self.add_tag,
            "delete-tag": self.delete_tag,
            "change-tag": self.change_tag,
            "has-tag": self.has_tag,
            "find-by-tag": self.find_by_tag,
            "sort-notes-by-tags": self.sort_notes_by_tags,
            "list-tags": self.list_tags,
        }

        while True:
            try:
                user_input = prompt(">>> ", completer=command_completer, history=self.history)
            except (KeyboardInterrupt, EOFError):
                # graceful exit: always save data on Ctrl+C or unexpected crash
                self._save_all()
                self.console.print("\n[bold red]Good bye![/bold red]")
                break

            command, args = parse_input(user_input)

            if not command:
                continue

            if command in ("exit", "quit", "close"):
                self._save_all()
                self.console.print("[bold red]Good bye![/bold red]")
                break

            handler = handlers.get(command)
            if handler:
                result = handler(args)
                if result:
                    self.console.print(result)
                self._save_all()
                continue

            suggested = suggest_command(command)
            if suggested:
                self.console.print(f"[yellow]Unknown command. Did you mean:[/yellow] [bold]{suggested}[/bold]?")
            else:
                self.console.print("[red]Unknown command.[/red]")


def run_cli() -> None:
    app = App()
    app.run()
