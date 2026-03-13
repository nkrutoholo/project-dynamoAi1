# Personal Assistant CLI

CLI-додаток для управління контактами та нотатками з автодоповненням, валідацією, кольоровим виводом і збереженням у JSON.

## Встановлення

```bash
pip install -r requirements.txt
```

## Запуск

```bash
python main.py
```

або

```bash
python -m personal_assistant
```

## Команди

### Контакти

| Команда | Опис |
|---------|------|
| `add-contact <name> <phone>` | Додати контакт |
| `show-contact <name>` | Показати контакт |
| `edit-contact <old_name> <new_name>` | Перейменувати контакт |
| `delete-contact <name>` | Видалити контакт |
| `all-contacts` | Список всіх контактів |
| `find-contact <query>` | Пошук контактів |
| `add-phone <name> <phone>` | Додати телефон |
| `edit-phone <name> <old> <new>` | Змінити телефон |
| `remove-phone <name> <phone>` | Видалити телефон |
| `add-email <name> <email>` | Додати email |
| `edit-email <name> <email>` | Змінити email |
| `add-address <name> <address>` | Додати адресу |
| `edit-address <name> <address>` | Змінити адресу |
| `add-birthday <name> <DD.MM.YYYY>` | Додати день народження |
| `edit-birthday <name> <DD.MM.YYYY>` | Змінити день народження |
| `birthdays <days>` | Найближчі дні народження |

### Нотатки

| Команда | Опис |
|---------|------|
| `add-note "<text>" [tag1] [tag2]` | Додати нотатку з тегами |
| `show-note <id>` | Показати нотатку |
| `edit-note <id>` | Редагувати нотатку |
| `delete-note <id>` | Видалити нотатку |
| `all-notes` | Список всіх нотаток |
| `find-note <query>` | Пошук нотаток |
| `add-tag <id> <tag1> [tag2]` | Додати теги |
| `delete-tag <id> <tag>` | Видалити тег |
| `change-tag <id> <old> <new>` | Замінити тег |
| `has-tag <id> <tag>` | Перевірити наявність тегу |
| `find-by-tag <tag>` | Знайти нотатки за тегом |
| `sort-notes-by-tags` | Сортувати нотатки за тегами |

### Інше

| Команда | Опис |
|---------|------|
| `help` | Список команд |
| `exit` / `quit` / `close` | Вийти з програми |

## Можливості

- **Автодоповнення** — Tab для підказок команд
- **Підказки** — "Did you mean?" при помилках в команді
- **Валідація** — телефон (+380XXXXXXXXX), email, дати
- **ESC** — скасування введення поля
- **Ctrl+C** — коректний вихід зі збереженням даних
- **Збереження** — автоматичне збереження в `~/.personal_assistant/`

## Тести

```bash
pytest
```

## Структура проекту

```
src/personal_assistant/
├── books/           # AddressBook, NotesBook
├── cli/             # App, parser, completer, command_suggester
├── models/          # Record, Note, Fields (Name, Phone, Email, ...)
├── storage/         # JsonStorage (atomic write)
├── utils/           # validators, formatters, decorators
├── constants.py
└── __main__.py
```
