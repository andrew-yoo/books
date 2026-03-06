import duckdb

from .catalog import CSV, require_catalog


FILTER_FIELDS = [
    ("Title", "title", "lower(title) = lower(?)"),
    ("Author", "authors", "authors ILIKE '%' || ? || '%'"),
    ("ISBN", "isbn", "isbn = ?"),
    ("Subject", "subject", "lower(subject) = lower(?)"),
    ("Field", "field", "lower(field) = lower(?)"),
]

SEARCH_COLS = ["title", "subtitle", "authors", "subject", "field"]

_SELECT = "SELECT title, subtitle, edition, authors, isbn, subject, field, id FROM read_csv_auto(?)"


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


def search():
    """Prompt for keywords and return all books that match every keyword across the searchable columns."""
    if not require_catalog():
        return

    keywords = input("Keywords: ").strip().split()
    print("")

    if not keywords:
        print("No keywords provided.")
        return

    # Each keyword must match at least one searchable column (AND across keywords, OR across columns)
    conditions = []
    params = [CSV]
    for kw in keywords:
        col_checks = " OR ".join(f"{col} ILIKE '%' || ? || '%'" for col in SEARCH_COLS)
        conditions.append(f"({col_checks})")
        params.extend([kw] * len(SEARCH_COLS))

    query = _SELECT + " WHERE " + " AND ".join(conditions) + " ORDER BY title"
    run_query(query, params)


def filter_books():
    """Prompt for exact-match filter criteria and return all matching books."""
    if not require_catalog():
        return

    inputs = [
        (label, cond, input(f"{label}: ").strip()) for label, _, cond in FILTER_FIELDS
    ]
    print("")

    conditions = [cond for _, cond, val in inputs if val]
    params = [CSV] + [val for _, _, val in inputs if val]

    query = (
        _SELECT
        + (" WHERE " + " AND ".join(conditions) if conditions else "")
        + " ORDER BY title"
    )
    run_query(query, params)
