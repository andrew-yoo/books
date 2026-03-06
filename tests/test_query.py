import pytest

from books.query import filter_books, run_query, search, _SELECT


# ---------------------------------------------------------------------------
# run_query
# ---------------------------------------------------------------------------


class TestRunQuery:
    def test_no_results(self, catalog_csv, capsys):
        query = _SELECT + " WHERE isbn = ?" + " ORDER BY title"
        run_query(query, [str(catalog_csv), "0000000000000"])
        assert "No results" in capsys.readouterr().out

    def test_prints_rows(self, catalog_csv, capsys):
        query = _SELECT + " ORDER BY title"
        run_query(query, [str(catalog_csv)])
        out = capsys.readouterr().out
        assert "linear algebra" in out
        assert "real analysis" in out

    def test_exact_row_count(self, catalog_csv, capsys):
        query = _SELECT + " ORDER BY title"
        run_query(query, [str(catalog_csv)])
        lines = [l for l in capsys.readouterr().out.splitlines() if l.strip()]
        assert len(lines) == 3  # three sample rows


# ---------------------------------------------------------------------------
# search
# ---------------------------------------------------------------------------


class TestSearch:
    def test_no_keywords(self, patch_catalog, monkeypatch, capsys):
        monkeypatch.setattr("builtins.input", lambda _: "")
        search()
        assert "No keywords provided" in capsys.readouterr().out

    def test_single_keyword_match(self, patch_catalog, monkeypatch, capsys):
        monkeypatch.setattr("builtins.input", lambda _: "algebra")
        search()
        out = capsys.readouterr().out
        assert "linear algebra" in out

    def test_single_keyword_no_match(self, patch_catalog, monkeypatch, capsys):
        monkeypatch.setattr("builtins.input", lambda _: "quantum")
        search()
        assert "No results" in capsys.readouterr().out

    def test_multi_keyword_narrows_results(self, patch_catalog, monkeypatch, capsys):
        # "linear" alone matches one book; adding "algebra" should still return it
        monkeypatch.setattr("builtins.input", lambda _: "linear algebra")
        search()
        out = capsys.readouterr().out
        assert "linear algebra" in out
        assert "real analysis" not in out

    def test_missing_catalog(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setattr("books.catalog.CSV", str(tmp_path / "missing.csv"))
        monkeypatch.setattr("books.query.CSV", str(tmp_path / "missing.csv"))
        search()
        assert "not found" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# filter_books
# ---------------------------------------------------------------------------


class TestFilterBooks:
    def _mock_input(self, responses):
        """Return an input() mock that yields responses in order."""
        it = iter(responses)
        return lambda _: next(it)

    def test_no_criteria_returns_all(self, patch_catalog, monkeypatch, capsys):
        # All five prompts left blank → no WHERE clause → all rows returned
        monkeypatch.setattr("builtins.input", lambda _: "")
        filter_books()
        out = capsys.readouterr().out
        assert "linear algebra" in out
        assert "real analysis" in out
        assert "competition" in out

    def test_filter_by_field(self, patch_catalog, monkeypatch, capsys):
        # Title="", Author="", ISBN="", Subject="", Field="linear algebra"
        responses = ["", "", "", "", "linear algebra"]
        monkeypatch.setattr("builtins.input", self._mock_input(responses))
        filter_books()
        out = capsys.readouterr().out
        assert "linear algebra" in out
        assert "real analysis" not in out

    def test_filter_by_subject(self, patch_catalog, monkeypatch, capsys):
        responses = ["", "", "", "math", ""]
        monkeypatch.setattr("builtins.input", self._mock_input(responses))
        filter_books()
        out = capsys.readouterr().out
        assert "linear algebra" in out
        assert "real analysis" in out

    def test_filter_by_isbn(self, patch_catalog, monkeypatch, capsys):
        responses = ["", "", "9780980232714", "", ""]
        monkeypatch.setattr("builtins.input", self._mock_input(responses))
        filter_books()
        out = capsys.readouterr().out
        assert "linear algebra" in out
        assert "real analysis" not in out

    def test_filter_no_match(self, patch_catalog, monkeypatch, capsys):
        responses = ["", "", "0000000000000", "", ""]
        monkeypatch.setattr("builtins.input", self._mock_input(responses))
        filter_books()
        assert "No results" in capsys.readouterr().out

    def test_missing_catalog(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setattr("books.catalog.CSV", str(tmp_path / "missing.csv"))
        monkeypatch.setattr("books.query.CSV", str(tmp_path / "missing.csv"))
        filter_books()
        assert "not found" in capsys.readouterr().out
