from typing import Iterable


def format_contacts(contacts: Iterable) -> str:
    contacts = list(contacts)

    if not contacts:
        return "No contacts found."

    lines = []
    for record in contacts:
        phones = ", ".join(phone.value for phone in record.phones) if getattr(record, "phones", None) else "-"
        email = record.email.value if getattr(record, "email", None) else "-"
        address = record.address.value if getattr(record, "address", None) else "-"
        birthday = record.birthday.value if getattr(record, "birthday", None) else "-"

        lines.append(
            f"Name: {record.name.value} | "
            f"Phones: {phones} | "
            f"Email: {email} | "
            f"Address: {address} | "
            f"Birthday: {birthday}"
        )

    return "\n".join(lines)


def format_notes(notes: Iterable) -> str:
    notes = list(notes)
    if not notes:
        return "No notes found."
    return "\n".join(str(note) for note in notes)