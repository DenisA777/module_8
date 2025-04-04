from collections import UserDict
from datetime import datetime, timedelta
import pickle

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except IndexError:
            return "Not enough arguments provided."
        except ValueError as e:
            return f"Value error: {e}"
        except KeyError:
            return "Contact not found."
        except Exception as e:
            return f"Error: {e}"
    return wrapper

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if len(value) != 10 or not value.isdigit():
            raise ValueError("Phone number must be 10 digits.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            dt = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        if dt > datetime.now():
            raise ValueError("Date of birth cannot be in the future")
        super().__init__(value)

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def edit_phone(self, old_phone, new_phone):
        for i, p in enumerate(self.phones):
            if p.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return
        raise ValueError("Phone number not found.")

    def add_birthday(self, birthday_str):
        self.birthday = Birthday(birthday_str)

    def __str__(self):
        phones_str = ", ".join(p.value for p in self.phones) if self.phones else "No phones"
        birthday_str = self.birthday.value if self.birthday else "Not set"
        return f"{self.name.value}: Phones: {phones_str}, Birthday: {birthday_str}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name, None)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise ValueError("No record.")

    def get_upcoming_birthdays(self):
        upcoming_birthdays = []
        today = datetime.now()
        week_later = today + timedelta(days=7)
        for record in self.data.values():
            if record.birthday:
                birthday_dt = datetime.strptime(record.birthday.value, "%d.%m.%Y")
                birthday_this_year = birthday_dt.replace(year=today.year)
                if today <= birthday_this_year <= week_later:
                    if birthday_this_year.weekday() in [5, 6]:
                        birthday_this_year += timedelta(days=(7 - birthday_this_year.weekday()))
                    upcoming_birthdays.append({
                        "name": record.name.value,
                        "birthday": birthday_this_year.strftime("%d.%m.%Y")
                    })
        return upcoming_birthdays

    def __str__(self):
        if not self.data:
            return "Address book is empty."
        return "\n".join(str(record) for record in self.data.values())

@input_error
def add_contact(args, book):
    name, phone = args[0], args[1]
    record = book.find(name)
    if not record:
        record = Record(name)
        book.add_record(record)
    record.add_phone(phone)
    return f"Contact {name} added/updated with phone {phone}."

@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args[0], args[1], args[2]
    record = book.find(name)
    if not record:
        raise KeyError
    record.edit_phone(old_phone, new_phone)
    return f"Phone number changed for {name}: {old_phone} -> {new_phone}"

@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find(name)
    if not record:
        raise KeyError
    if not record.phones:
        return f"No phone numbers for {name}."
    phones = ", ".join(p.value for p in record.phones)
    return f"{name}'s phones: {phones}"

@input_error
def add_birthday(args, book):
    name, birthday = args[0], args[1]
    record = book.find(name)
    if not record:
        raise KeyError
    record.add_birthday(birthday)
    return f"Birthday added for {name}."

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if not record:
        raise KeyError
    if not record.birthday:
        return f"Birthday not set for {name}."
    return f"{name}'s birthday: {record.birthday.value}"

def birthdays(book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays in the next 7 days."
    return "\n".join(f"{item['name']}: {item['birthday']}" for item in upcoming)

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ").strip()
        if not user_input:
            continue
        parts = user_input.split()
        command = parts[0].lower()
        args = parts[1:]

        if command in ["close", "exit"]:
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
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "all":
            print(book)
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()