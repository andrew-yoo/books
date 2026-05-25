import csv
import os
import shutil
from .book import Book


BASE_DIR = "."
FOLDER = os.path.join(BASE_DIR, "library")
CSV = os.path.join(FOLDER, "_catalog.csv")


FIELDNAMES = [
    "title",
    "subtitle",
    "edition",
    "authors",
    "isbn",
    "subject",
    "field",
    "id",
]


def require_catalog():
    """Return True if the catalog CSV exists, otherwise print an error and return False."""
    if not os.path.exists(CSV):
        print(f'Error: catalog "{CSV}" not found.')
        return False
    return True


def build(source, book):
    """Copy the source PDF into the library folder using the book's hash as the filename."""
    if not os.path.isfile(source):
        print(f'Error: file not found at "{source}"')
        return False

    os.makedirs(FOLDER, exist_ok=True)
    destination = os.path.join(FOLDER, book.hash_id() + ".pdf")

    shutil.copy2(source, destination)
    print(f"Copied to {destination}")

    return True


def archive(book):
    """Append a book entry to the catalog CSV, writing the header if the file is new."""
    line = {
        "title": book.title,
        "subtitle": book.subtitle,
        "edition": book.edition,
        "authors": book.authors,
        "isbn": book.isbn,
        "subject": book.subject,
        "field": book.field,
        "id": book.hash_id(),
    }

    with open(CSV, "a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)

        if file.tell() == 0:
            writer.writeheader()

        writer.writerow(line)


def add_book(path):
    """Prompt for book metadata, copy the PDF, and add the entry to the catalog."""
    title = input("Title: ").lower().strip()
    subtitle = input("Subtitle: ").lower().strip()
    edition = input("Edition: ").lower().strip()
    authors = [
        a.strip() for a in input("Authors (comma-separated): ").lower().split(",")
    ]
    isbn = input("ISBN: ").lower().strip()
    subject = input("Subject: ").lower().strip()
    field = input("Field: ").lower().strip()

    book = Book(title, subtitle, edition, authors, isbn, subject, field)

    if build(path, book):
        archive(book)
    else:
        print("\nAborted: file not found.")


def remove_book(id_to_remove):
    """Remove a book entry from the catalog and delete its PDF from the library."""
    id_to_remove = id_to_remove.strip()

    if not id_to_remove:
        print("Error: no id provided for removal.")
        return

    if not require_catalog():
        return

    entries = []
    found = False

    with open(CSV, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row.get("id") == id_to_remove:
                found = True
            else:
                entries.append(row)

    if not found:
        print(f"No entry with id {id_to_remove} found in archive.")
        return

    try:
        with open(CSV, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
            writer.writeheader()
            for r in entries:
                writer.writerow(r)
    except OSError as e:
        print(f"Failed to update archive: {e}")
        return

    pdf_path = os.path.join(FOLDER, id_to_remove + ".pdf")
    if os.path.exists(pdf_path):
        try:
            os.remove(pdf_path)
            print(f"Removed file {pdf_path}")
        except OSError as e:
            print(f"Removed archive entry but failed to delete file: {e}")
            return
    else:
        print("Removed archive entry; no file found to remove.")

    print("Removal complete.")
