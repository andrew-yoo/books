import argparse
import os
import shutil
import csv
import xxhash
import duckdb


FOLDER = "library"
CSV = "catalog.csv"


class Book:
    def __init__(self, title, subtitle, edition, authors, isbn, subject, field):
        self.title = title
        self.subtitle = subtitle
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
            x.update(bytes(self.subtitle, "utf-8"))
            x.update(bytes(self.edition, "utf-8"))

            for author in self.authors:
                x.update(bytes(author, "utf-8"))

            id = x.hexdigest()

        return id


def parse():
    parser = argparse.ArgumentParser()

    parser.add_argument("-a", "--add", help="add an ebook")
    parser.add_argument("-r", "--remove", help="remove an ebook")
    parser.add_argument(
        "-s", "--search", action="store_true", help="search for an ebook"
    )
    parser.add_argument(
        "-f", "--filter", action="store_true", help="filter for exact matches"
    )

    args = parser.parse_args()

    if args.add:
        return "add", args.add

    elif args.remove:
        return "remove", args.remove

    elif args.search:
        return "search", None

    elif args.filter:
        return "filter", None

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
        "subtitle": book.subtitle,
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
            "subtitle",
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


FILTER_FIELDS = [
    ("Title", "title", "lower(title) = lower(?)"),
    ("Author", "authors", "authors ILIKE '%' || ? || '%'"),
    ("ISBN", "isbn", "isbn = ?"),
    ("Subject", "subject", "lower(subject) = lower(?)"),
    ("Field", "field", "lower(field) = lower(?)"),
]

SEARCH_COLS = ["title", "subtitle", "authors", "subject", "field"]


def run_query(query, params):
    """Execute a DuckDB query against the catalog and print the results."""
    con = duckdb.connect()
    try:
        rows = con.execute(query, params).fetchall()
        if not rows:
            print("No results")
        else:
            for r in rows:
                print(r)
    finally:
        con.close()


def main():
    mode, other = parse()  # Other is a temporary placeholder

    if mode == "add":
        path = other

        title = input("Title: ").lower().strip()
        subtitle = input("Subtitle: ").lower().strip()
        edition = input("Edition: ").lower().strip()
        authors = [
            a.strip() for a in input("Authors (comma-separated): ").lower().split(",")
        ]
        isbn = input("ISBN: ").lower().strip()
        subject = input("Subject: ").lower().strip()
        field = input("Field: ").lower().strip()

        new_book = Book(title, subtitle, edition, authors, isbn, subject, field)

        # Build the book

        if build(path, new_book, FOLDER):
            archive(new_book)

        else:
            print("\nAborted: file not found.")

    elif mode == "remove":
        id_to_remove = other.strip()

        if id_to_remove == "":
            print("Error: no id provided for removal.")
            return

        # Read archive and keep rows that do not match the id
        entries = []
        found = False

        if not os.path.exists(CSV):
            print(f'Archive file "{CSV}" not found.')
            return

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

        # Write back filtered archive
        fieldnames = [
            "title",
            "subtitle",
            "edition",
            "authors",
            "isbn",
            "subject",
            "field",
            "id",
        ]

        try:
            with open(CSV, "w", newline="") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for r in entries:
                    writer.writerow(r)
        except OSError as e:
            print(f"Failed to update archive: {e}")
            return

        # Remove the PDF file if present
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

    elif mode == "search":
        keywords = input("Keywords: ").strip().split()
        print("")

        if not keywords:
            print("No keywords provided.")
            return

        # Each keyword must match at least one searchable column (AND across keywords, OR across columns)
        conditions = []
        params = [CSV]
        for kw in keywords:
            col_checks = " OR ".join(
                f"{col} ILIKE '%' || ? || '%'" for col in SEARCH_COLS
            )
            conditions.append(f"({col_checks})")
            params.extend([kw] * len(SEARCH_COLS))

        query = (
            "SELECT title, subtitle, edition, authors, isbn, subject, field, id"
            " FROM read_csv_auto(?)"
            " WHERE " + " AND ".join(conditions) + " ORDER BY title"
        )
        run_query(query, params)

    elif mode == "filter":
        inputs = [
            (label, cond, input(f"{label}: ").strip())
            for label, _, cond in FILTER_FIELDS
        ]
        print("")

        conditions = [cond for _, cond, val in inputs if val]
        params = [CSV] + [val for _, _, val in inputs if val]

        query = (
            "SELECT title, subtitle, edition, authors, isbn, subject, field, id"
            " FROM read_csv_auto(?)"
            + (" WHERE " + " AND ".join(conditions) if conditions else "")
            + " ORDER BY title"
        )
        run_query(query, params)


if __name__ == "__main__":
    main()
