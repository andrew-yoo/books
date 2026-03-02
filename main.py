import argparse
import os
import shutil
import xxhash
import csv


FOLDER = "books"
CSV = "archive.csv"


class Book:
    def __init__(self, title, edition, authors, isbn, subject, field):
        self.title = title
        self.edition = edition
        self.authors = authors
        self.isbn = isbn
        self.subject = subject
        self.field = field

    def hash_id(self):
        """Create a 64-bit ID for a book using XXHash64.

        If an ISBN exists, it will be used as the seed. If no ISBN exists, the title, edition, and author will be concatenated and used as the seed.

        Args:
            book (Book): A Book Object.

        Returns:
            str: A 64-bit id encoded in hexadecimal.
        """
        if self.isbn != "":
            x = xxhash.xxh64()
            x.update(bytes(self.isbn, "utf-8"))
            id = x.hexdigest()
        else:
            x = xxhash.xxh64()
            x.update(bytes(self.title, "utf-8"))
            x.update(bytes(self.edition, "utf-8"))

            for author in self.authors:
                x.update(bytes(author, "utf-8"))

            id = x.hexdigest()

        return id


def parse():
    parser = argparse.ArgumentParser()

    parser.add_argument("-a", "--add", help="add an ebook")

    args = parser.parse_args()

    if args.add:
        return "add", args.add

    return None, None


def build(source, book, folder):
    """Copy the source PDF into the books folder with a descriptive filename."""
    if not os.path.isfile(source):
        print(f'Error: file not found at "{source}"')
        return False

    os.makedirs(folder, exist_ok=True)
    destination = os.path.join(folder, book.hash_id() + ".pdf")

    shutil.copy2(source, destination)
    print(f"Copied to {destination}")

    return True


def archive(book):
    line = {
        "title": book.title,
        "edition": book.edition,
        "authors": book.authors,
        "isbn": book.isbn,
        "subject": book.subject,
        "field": book.field,
        "id": book.hash_id(),
    }

    file_exists = os.path.exists(CSV)
    file_empty = True
    if file_exists:
        try:
            file_empty = os.path.getsize(CSV) == 0
        except OSError:
            file_empty = True

    with open(CSV, "a", newline="") as file:
        fieldnames = [
            "title",
            "edition",
            "authors",
            "isbn",
            "subject",
            "field",
            "id",
        ]

        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if not file_exists or file_empty:
            writer.writeheader()

        writer.writerow(line)


def main():
    mode, other = parse()  # Other is a temporary placeholder

    if mode == "add":
        path = other

        title = input("Title: ").lower().strip()
        edition = input("Edition: ").lower().strip()
        authors = [
            a.strip() for a in input("Authors (comma-separated): ").lower().split(",")
        ]
        isbn = input("ISBN: ").lower().strip()
        subject = input("Subject: ").lower().strip()
        field = input("Field: ").lower().strip()

        new_book = Book(title, edition, authors, isbn, subject, field)

        # Build the book

        if build(path, new_book, FOLDER):
            archive(new_book)

        else:
            print("\nAborted: file not found.")


if __name__ == "__main__":
    main()
