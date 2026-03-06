import argparse

from books.catalog import add_book, remove_book
from books.query import filter_books, search


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


def main():
    mode, other = parse()

    if mode == "add":
        add_book(other)
    elif mode == "remove":
        remove_book(other)
    elif mode == "search":
        search()
    elif mode == "filter":
        filter_books()


if __name__ == "__main__":
    main()
