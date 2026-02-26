import os
import shutil
import yaml


BOOKS_FOLDER = "books"
BOOKS_YAML = "books.yaml"


class Book:
    def __init__(self, title, edition, authors, isbn, subject, field):
        self.title = title
        self.edition = int(edition)
        self.authors = authors
        self.isbn = int(isbn)
        self.subject = subject
        self.field = field

    def descriptive_name(self):
        title_part = self.title.strip().lower().replace(' ', '_')
        authors_part = ",".join(
            name.strip().lower().replace(" ", "_") for name in self.authors
        )
        return f'({title_part})({self.edition})({authors_part})({self.isbn})'

    def archive_dict(self):
        return {
            'title': self.title,
            'edition': self.edition,
            'authors': self.authors,
            'isbn': self.isbn,
            'subject': self.subject,
            'field': self.field,
            'path': self.descriptive_name(),
        }


def build(source_pdf, book, folder):
    """Copy the source PDF into the books folder with a descriptive filename."""
    if not os.path.isfile(source_pdf):
        print(f'Error: file not found at "{source_pdf}"')
        return False

    os.makedirs(folder, exist_ok=True)
    dest = os.path.join(folder, book.descriptive_name() + '.pdf')
    shutil.copy2(source_pdf, dest)
    print(f'Copied to {dest}')
    return True


def archive(book, yaml_path):
    """Append the book entry to the YAML catalogue."""
    if os.path.exists(yaml_path):
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f) or {}
    else:
        data = {}

    data.setdefault('books', [])
    data['books'].append(book.archive_dict())

    with open(yaml_path, 'w') as f:
        yaml.safe_dump(data, f, sort_keys=False, default_flow_style=False)
    print(f'Archived in {yaml_path}')


def main():
    print("=== Add a new book ===\n")

    title   = input('Title: ').strip()
    edition = input('Edition: ').strip()
    authors = [a.strip() for a in input('Authors (comma-separated): ').split(',')]
    isbn    = input('ISBN: ').strip()
    subject = input('Subject: ').strip()
    field   = input('Field: ').strip()

    book = Book(title, edition, authors, isbn, subject, field)

    print(f'\nGenerated name: {book.descriptive_name()}.pdf')

    location = input('\nFile location: ').strip().replace('"', '')

    if build(location, book, BOOKS_FOLDER):
        archive(book, BOOKS_YAML)
        print('\nDone!')
    else:
        print('\nAborted: file not found.')


if __name__ == '__main__':
    main()