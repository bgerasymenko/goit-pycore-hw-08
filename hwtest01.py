import pickle
from datetime import datetime, timedelta
from pathlib import Path

# --------- МОДЕЛІ ---------

class Field:
    def __init__(self, value):
        self.value = value

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must contain exactly 10 digits.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        for idx, phone in enumerate(self.phones):
            if phone.value == old_phone:
                self.phones[idx] = Phone(new_phone)
                return True
        return False

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = "; ".join(p.value for p in self.phones)
        bday = self.birthday.value.strftime("%d.%m.%Y") if self.birthday else "N/A"
        return f"{self.name.value}: {phones} | Birthday: {bday}"

class AddressBook:
    def __init__(self):
        self.data = {}

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        end_period = today + timedelta(days=7)
        result = []
        for record in self.data.values():
            if record.birthday:
                bday_this_year = record.birthday.value.replace(year=today.year).date()
                if today <= bday_this_year <= end_period:
                    result.append(record.name.value)
        return result

# --------- СЕРІАЛІЗАЦІЯ ---------

ADDRESS_BOOK_FILE = "addressbook.pkl"

def save_data(book, filename=ADDRESS_BOOK_FILE):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename=ADDRESS_BOOK_FILE):
    if Path(filename).exists():
        with open(filename, "rb") as f:
            return pickle.load(f)
    return AddressBook()

# --------- ОБРОБНИКИ КОМАНД ---------

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, IndexError, KeyError) as e:
            return f"Error: {str(e)}"
    return inner

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    if not record:
        record = Record(name)
        book.add_record(record)
    record.add_phone(phone)
    return "Contact added or updated."

@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record and record.edit_phone(old_phone, new_phone):
        return "Phone updated."
    return "Contact or phone not found."

@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record:
        return "; ".join(p.value for p in record.phones)
    return "Contact not found."

def show_all(book: AddressBook):
    if not book.data:
        return "No contacts."
    return "\n".join(str(record) for record in book.data.values())

@input_error
def add_birthday(args, book):
    name, bday = args
    record = book.find(name)
    if record:
        record.add_birthday(bday)
        return "Birthday added."
    return "Contact not found."

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return record.birthday.value.strftime("%d.%m.%Y")
    return "Birthday not found."

@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()
    return "Upcoming birthdays:\n" + "\n".join(upcoming) if upcoming else "No birthdays this week."

def parse_input(user_input):
    parts = user_input.strip().split()
    return parts[0].lower(), parts[1:]

# --------- MAIN ФУНКЦІЯ ---------

def main():
    book = load_data()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ("close", "exit"):
            save_data(book)
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Unknown command. Try again.")

# --------- ТЕСТ ---------

if __name__ == "__main__":
    # Автотест — додамо контакт якщо новий файл
    book = load_data()
    if not book.find("TestUser"):
        test_record = Record("TestUser")
        test_record.add_phone("0987654321")
        test_record.add_birthday("10.04.1990")
        book.add_record(test_record)
        save_data(book)

    # Запуск CLI
    main()
