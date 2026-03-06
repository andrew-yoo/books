from books.book import Book


def make_book(isbn="9781234567890"):
    return Book("title", "subtitle", "1", ["author"], isbn, "subject", "field")


class TestHashId:
    def test_isbn_seed(self):
        """hash_id uses the ISBN when one is provided."""
        book = make_book(isbn="9781234567890")
        assert (
            book.hash_id()
            == Book("other", "", "", [], "9781234567890", "", "").hash_id()
        )

    def test_no_isbn_uses_metadata(self):
        """hash_id uses title/subtitle/edition/authors when ISBN is absent."""
        book = Book("my title", "sub", "1", ["alice"], "", "math", "algebra")
        isbn_book = Book(
            "my title", "sub", "1", ["alice"], "9999999999999", "math", "algebra"
        )
        assert book.hash_id() != isbn_book.hash_id()

    def test_deterministic(self):
        """Same inputs always produce the same hash."""
        b1 = make_book()
        b2 = make_book()
        assert b1.hash_id() == b2.hash_id()

    def test_different_isbns_differ(self):
        """Different ISBNs produce different hashes."""
        assert (
            make_book("1111111111111").hash_id() != make_book("2222222222222").hash_id()
        )

    def test_different_titles_differ(self):
        """Different titles (no ISBN) produce different hashes."""
        a = Book("alpha", "", "1", ["author"], "", "s", "f")
        b = Book("beta", "", "1", ["author"], "", "s", "f")
        assert a.hash_id() != b.hash_id()

    def test_different_authors_differ(self):
        """Different author lists (no ISBN) produce different hashes."""
        a = Book("title", "", "1", ["alice"], "", "s", "f")
        b = Book("title", "", "1", ["bob"], "", "s", "f")
        assert a.hash_id() != b.hash_id()

    def test_returns_hex_string(self):
        """hash_id returns a non-empty hex string."""
        h = make_book().hash_id()
        assert isinstance(h, str) and len(h) > 0
        int(h, 16)  # raises ValueError if not valid hex
