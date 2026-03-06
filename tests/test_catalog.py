import csv
import os

import pytest

from books.book import Book
from books.catalog import FIELDNAMES, archive, build, remove_book, require_catalog


def sample_book(isbn="9781234567890"):
    return Book("test title", "test sub", "1", ["alice"], isbn, "math", "algebra")


# ---------------------------------------------------------------------------
# require_catalog
# ---------------------------------------------------------------------------


class TestRequireCatalog:
    def test_missing_csv(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setattr("books.catalog.CSV", str(tmp_path / "missing.csv"))
        assert require_catalog() is False
        assert "not found" in capsys.readouterr().out

    def test_present_csv(self, catalog_csv, monkeypatch):
        monkeypatch.setattr("books.catalog.CSV", str(catalog_csv))
        assert require_catalog() is True


# ---------------------------------------------------------------------------
# archive
# ---------------------------------------------------------------------------


class TestArchive:
    def test_creates_file_with_header(self, tmp_path, monkeypatch):
        csv_path = tmp_path / "catalog.csv"
        monkeypatch.setattr("books.catalog.CSV", str(csv_path))

        archive(sample_book())

        with open(csv_path, newline="") as f:
            rows = list(csv.DictReader(f))
        assert rows[0]["title"] == "test title"

    def test_header_written_once(self, tmp_path, monkeypatch):
        csv_path = tmp_path / "catalog.csv"
        monkeypatch.setattr("books.catalog.CSV", str(csv_path))

        archive(sample_book("1111111111111"))
        archive(sample_book("2222222222222"))

        with open(csv_path, newline="") as f:
            content = f.read()
        assert content.count("title,subtitle") == 1

    def test_appends_multiple_entries(self, tmp_path, monkeypatch):
        csv_path = tmp_path / "catalog.csv"
        monkeypatch.setattr("books.catalog.CSV", str(csv_path))

        archive(sample_book("1111111111111"))
        archive(sample_book("2222222222222"))

        with open(csv_path, newline="") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 2

    def test_writes_correct_fields(self, tmp_path, monkeypatch):
        csv_path = tmp_path / "catalog.csv"
        monkeypatch.setattr("books.catalog.CSV", str(csv_path))
        book = sample_book()

        archive(book)

        with open(csv_path, newline="") as f:
            row = list(csv.DictReader(f))[0]
        assert row["title"] == book.title
        assert row["isbn"] == book.isbn
        assert row["id"] == book.hash_id()


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------


class TestBuild:
    def test_missing_source_returns_false(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setattr("books.catalog.FOLDER", str(tmp_path / "lib"))
        assert build(str(tmp_path / "nonexistent.pdf"), sample_book()) is False
        assert "not found" in capsys.readouterr().out

    def test_copies_file_to_folder(self, tmp_path, monkeypatch):
        source = tmp_path / "source.pdf"
        source.write_bytes(b"%PDF-stub")
        lib = tmp_path / "lib"
        monkeypatch.setattr("books.catalog.FOLDER", str(lib))

        book = sample_book()
        result = build(str(source), book)

        assert result is True
        assert (lib / (book.hash_id() + ".pdf")).exists()

    def test_creates_folder_if_missing(self, tmp_path, monkeypatch):
        source = tmp_path / "source.pdf"
        source.write_bytes(b"%PDF-stub")
        lib = tmp_path / "new_lib"
        monkeypatch.setattr("books.catalog.FOLDER", str(lib))

        build(str(source), sample_book())

        assert lib.is_dir()


# ---------------------------------------------------------------------------
# remove_book
# ---------------------------------------------------------------------------


class TestRemoveBook:
    def test_empty_id(self, capsys):
        remove_book("   ")
        assert "no id provided" in capsys.readouterr().out

    def test_missing_catalog(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setattr("books.catalog.CSV", str(tmp_path / "missing.csv"))
        monkeypatch.setattr("books.catalog.FOLDER", str(tmp_path))
        remove_book("abc123")
        assert "not found" in capsys.readouterr().out

    def test_unknown_id(self, catalog_csv, monkeypatch, capsys):
        monkeypatch.setattr("books.catalog.CSV", str(catalog_csv))
        monkeypatch.setattr("books.catalog.FOLDER", str(catalog_csv.parent))
        remove_book("0000000000000000")
        assert "No entry" in capsys.readouterr().out

    def test_removes_entry_from_csv(self, catalog_csv, monkeypatch):
        monkeypatch.setattr("books.catalog.CSV", str(catalog_csv))
        monkeypatch.setattr("books.catalog.FOLDER", str(catalog_csv.parent))

        target_id = "bd7650148aa270bb"
        remove_book(target_id)

        with open(catalog_csv, newline="") as f:
            ids = [row["id"] for row in csv.DictReader(f)]
        assert target_id not in ids

    def test_preserves_other_entries(self, catalog_csv, monkeypatch):
        monkeypatch.setattr("books.catalog.CSV", str(catalog_csv))
        monkeypatch.setattr("books.catalog.FOLDER", str(catalog_csv.parent))

        remove_book("bd7650148aa270bb")

        with open(catalog_csv, newline="") as f:
            ids = [row["id"] for row in csv.DictReader(f)]
        assert "ae7be12c68484b12" in ids
        assert "ac5898a6947ada82" in ids

    def test_deletes_pdf(self, catalog_csv, monkeypatch, capsys):
        lib = catalog_csv.parent
        target_id = "bd7650148aa270bb"
        pdf = lib / (target_id + ".pdf")
        pdf.write_bytes(b"%PDF-stub")

        monkeypatch.setattr("books.catalog.CSV", str(catalog_csv))
        monkeypatch.setattr("books.catalog.FOLDER", str(lib))

        remove_book(target_id)

        assert not pdf.exists()
        assert f"Removed file" in capsys.readouterr().out

    def test_handles_missing_pdf(self, catalog_csv, monkeypatch, capsys):
        monkeypatch.setattr("books.catalog.CSV", str(catalog_csv))
        monkeypatch.setattr("books.catalog.FOLDER", str(catalog_csv.parent))

        remove_book("bd7650148aa270bb")

        assert "no file found" in capsys.readouterr().out
