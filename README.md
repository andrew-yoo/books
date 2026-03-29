# books

My system for archiving Ebook PDFs. 
Significant portions were vibecoded, especially the database management, so use at your own risk.

## Usage

The CLI is located at `main.py`.

- Add a book with `--add`
- Remove a book with `--remove`
- Search for a book with `--search`
- Filter for exact matches with `--filter`

## Folders

A folder path can be specified in the `FOLDER` variable of the `main.py` file. This is where all the PDFs are stored. By default, the path is `library`.

File names are in hexadecimal to ensure path-safety. In the future, I may implement folder sharding, but it seems overkill for now.

## Hashing

Paths are generated with the `XXHash64` non-cryptographic hash function. The probability of a catastrophic collision is given by the [birthday paradox](https://en.wikipedia.org/wiki/Birthday_problem):

Given $x$ numbers below $n$, the probability of a collision is

$$ P(x) \approx 1 - \exp\left(-\frac{x(x-1)}{2n}\right) $$

Assuming a substantial library of $5,000$ books, the probability of a collision is roughly comparable to that of being [struck by lightning](https://www.britannica.com/question/What-are-the-chances-of-being-struck-by-lightning) three times.

If an ISBN is available, it will be hashed. If no ISBN is available, the title, subtitle, edition, and authors will be concatenated and hashed.
