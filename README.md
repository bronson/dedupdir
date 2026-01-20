# redundir

A command-line utility that finds directories containing duplicate files and ranks them by redundancy.

## Installation

```sh
curl -o ~/.local/bin/redundir https://raw.githubusercontent.com/USER/redundirs/main/redundir
chmod +x ~/.local/bin/redundir
```

Or just copy `redundir` anywhere in your `$PATH`. Requires Python 3.10+ with no external dependencies.

## Usage

```
redundir [directory] [-a ALGORITHM] [-v] [-q]
```

| Option | Description |
|--------|-------------|
| `directory` | Directory to scan (default: `.`) |
| `-a, --algorithm` | Hash algorithm: `md5`, `sha1`, `sha256`, `blake2b`, `blake2s` (default: `blake2b`) |
| `-v, --verbose` | Show scan progress |
| `-q, --quiet` | Suppress status messages |

## Example

```
$ redundir ~/Documents
Scanning /home/user/Documents...
100.00% (4/4) /home/user/Documents/backups/old
 75.00% (3/4) /home/user/Documents/photos/2023
 66.67% (2/3) /home/user/Documents/projects/archive

Found 3 directories with duplicate files.
```

## How It Works

1. Recursively scans all files and computes hashes (BLAKE2b by default for speed)
2. Identifies duplicates (files with identical content anywhere in the tree)
3. Calculates each directory's **redundancy score**: `duplicate_files / total_files`
4. Outputs directories sorted by score (most redundant first)

## License

MIT

## Maybe todo?

* Probably need to be smarter about handling symlinks.
* It's not hardened against malicious content.
* Do I need to worry about filesystem boundaries? Probably not?
