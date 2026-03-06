import xxhash


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

        If an ISBN exists, it will be used as the seed. If no ISBN exists, the
        title, edition, and authors will be concatenated and used as the seed.

        Returns:
            str: A 64-bit id encoded in hexadecimal.
        """
        x = xxhash.xxh64()

        if self.isbn:
            x.update(bytes(self.isbn, "utf-8"))
        else:
            x.update(bytes(self.title, "utf-8"))
            x.update(bytes(self.subtitle, "utf-8"))
            x.update(bytes(self.edition, "utf-8"))
            for author in self.authors:
                x.update(bytes(author, "utf-8"))

        return x.hexdigest()
