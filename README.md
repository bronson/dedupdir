# redundir

A command-line utility that finds directories containing duplicate files and ranks them by redundancy.

Includes both a CLI tool (`redundir`) and an interactive TUI (`redundir-tui`).

## Installation

```sh
curl -o ~/.local/bin/redundir https://raw.githubusercontent.com/USER/redundirs/main/redundir
curl -o ~/.local/bin/redundir-tui https://raw.githubusercontent.com/USER/redundirs/main/redundir-tui
chmod +x ~/.local/bin/redundir ~/.local/bin/redundir-tui
```

Or just copy `redundir` and `redundir-tui` anywhere in your `$PATH`. Both scripts must be in the same directory. Requires Python 3.10+ with no external dependencies.

## CLI Usage

```
redundir [directory] [-a ALGORITHM] [-j N] [-v] [-q]
```

| Option | Description |
|--------|-------------|
| `directory` | Directory to scan (default: `.`) |
| `-a, --algorithm` | Hash algorithm: `md5`, `sha1`, `sha256`, `blake2b`, `blake2s` (default: `blake2b`) |
| `-j, --jobs` | Number of parallel hashing jobs (default: `4`, use `1` to disable) |
| `-v, --verbose` | Show related directories and hypothetical redundancy scores |
| `-q, --quiet` | Suppress progress messages |

## Example

```
$ redundir ~/Documents
Scanning /home/user/Documents...
  Collecting files...
  Found 1523 files
  Hashing 412 files, skipping 1111 files with unique sizes
  Hashed 412 files
  Found 89 duplicate files in 3 directories (overall redundancy: 21.60%)

100.00%  4/4  backups/old
 75.00%  3/4  photos/2023
 66.67%  2/3  projects/archive
```

### Verbose Mode

With `-v`, each directory shows related directories that share files with it, along with their **hypothetical redundancy** - the redundancy they would have if the current directory didn't exist:

```
$ redundir ~/Documents -v
...
100.00%  4/4  backups/old
      0.00%  0/4  backups/new
     50.00%  2/4  photos/2023
```

This shows that if `backups/old` was removed, `backups/new` would have 0% redundancy (all its duplicates were with `old`), while `photos/2023` would still have 50% redundancy (duplicates exist elsewhere too).

## Interactive TUI

`redundir-tui` provides a split-pane interface for exploring duplicate files:

```
redundir-tui [directory] [-a ALGORITHM] [-j N]
```

**Features:**
- **Progress display**: Shows scanning progress before starting the TUI (just like CLI)
- **Top pane**: List of directories with redundancy scores
- **Bottom pane**: Shows for the selected directory:
  - Related directories that share files (with hypothetical redundancy if current dir didn't exist)
  - List of all duplicate files in the directory
- **Active pane** is highlighted with bold border and can be navigated independently
- Press `Tab` to switch between panes

**Keys:**
- `Tab` - Switch between top and bottom panes
- `Enter` - From top pane, switch to bottom pane (drill down)
- `Esc` - From bottom pane, switch to top pane (go back); from top pane, show quit prompt
- `↑`/`↓` or `j`/`k` - Navigate items in active pane
- `PgUp`/`PgDn` or `Ctrl-B`/`Ctrl-F` - Page up/down in active pane
- `Home`/`End` - Jump to first/last item in active pane
- `q` - Quit

**Example:**
```
$ redundir-tui ~/Documents
Scanning /home/user/Documents...
  Found 1523 total files
  Hashing 412 files, skipping 1111 files with unique sizes
  Hashed 412 files
  Found 89 duplicate files in 3 directories (overall redundancy: 21.60%)

[Interactive TUI starts here with split panes]
```

The TUI shows full progress information during scanning, then starts the interactive interface where you can explore which directories share files and see exactly which files are duplicated.

## How It Works

1. Recursively scans all files and groups them by size (fast, no hashing needed)
2. Only hashes files that have potential duplicates (same size as another file)
3. Uses parallel processing (4 workers by default) to hash files quickly
4. Identifies duplicates (files with identical content anywhere in the tree)
5. Calculates each directory's **redundancy score**: `duplicate_files / total_files`
6. Outputs directories sorted by score (most redundant first)

**Performance optimizations:**
- Size-based pre-filtering skips hashing files with unique sizes
- BLAKE2b hashing is faster than SHA256
- Parallel processing utilizes multiple CPU cores
- 8MB chunk size for efficient I/O

## License

MIT

## Maybe todo?

* Probably need to be smarter about handling symlinks.
* It's not hardened against malicious content.
* Do I need to worry about filesystem boundaries? Probably not?
