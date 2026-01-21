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
redundir [directory...] [-a ALGORITHM] [-j N] [-v] [-q]
```

| Option | Description |
|--------|-------------|
| `directory` | Directory or directories to scan (default: `.`) |
| `-a, --algorithm` | Hash algorithm: `md5`, `sha1`, `sha256`, `blake2b`, `blake2s` (default: `blake2b`) |
| `-j, --jobs` | Number of parallel hashing jobs (default: `4`, use `1` to disable) |
| `-v, --verbose` | Show related directories and hypothetical redundancy scores |
| `-q, --quiet` | Suppress progress messages |

## Examples

**Single directory:**
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

**Multiple directories (scanned together):**
```
$ redundir ~/backups ~/archive ~/old-projects
Scanning 3 directories...
  /home/user/backups
  /home/user/archive
  /home/user/old-projects
  Collecting files...
  Found 2847 files
  Hashing 892 files, skipping 1955 files with unique sizes
  Hashed 892 files
  Found 456 duplicate files in 12 directories (overall redundancy: 16.02%)

100.00%  24/24  backups/2023
 87.50%  14/16  archive/photos
 75.00%   9/12  old-projects/website
...
```

When scanning multiple directories, duplicates are detected across all of them, making it easy to find redundancy between separate backup locations or project directories.

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
redundir-tui [directory...] [-a ALGORITHM] [-j N]
```

Supports scanning multiple directories just like the CLI tool.

**Features:**
- **Progress display**: Shows scanning progress before starting the TUI (just like CLI)
- **Top pane**: List of directories (sorted by redundancy, or filtered by selected file)
- **Bottom pane**: Shows all files in the selected directory with:
  - **Directory count column**: Shows how many directories contain each file
  - **Sorted by count**: Most duplicated files first, unique files (count=1) last
  - All files listed, not just duplicates
- **Automatic filtering**: As you navigate files in the bottom pane, the top pane instantly updates to show only directories containing that file
- **Drill down navigation**: Press `→`/`Enter`/`Tab` on a file to switch to the filtered top pane; press `←` to go back
- **Active pane** is highlighted with bold border
- **Smart navigation** in bottom pane skips headers

**Keys:**
- `↑`/`↓` or `j`/`k` - Navigate (top pane auto-filters as you move through files in bottom pane)
- `→`/`l` or `Enter` or `Tab` - Drill down / switch to filtered top pane
- `←`/`h` or `Esc` - Go back / clear filter
- `PgUp`/`PgDn` or `Ctrl-B`/`Ctrl-F` - Page up/down
- `Home`/`End` or `<`/`>` - Jump to first/last item
- `d` - Delete selected file or directory (moves to `~redundir-trash/` with confirmation for non-redundant items)
- `u` - Undo last deletion (progressively restores deleted items)
- `t` - Toggle trash viewer (`r` to restore items, `t` or `Esc` to exit)
- `q` - Quit

### Deletion & Cleanup

The TUI includes a safe deletion system that moves files to `~redundir-trash/` (in each root directory) instead of permanently deleting them:

- **Smart deletion**: Fully redundant items deleted immediately; non-redundant items require confirmation
- **Progressive undo**: Press `u` repeatedly to undo recent deletions
- **Trash viewer**: Press `t` to toggle trash view, restore with `r`, press `t` again to return
- **Safe by design**: All items can be restored until you manually delete each root's `~redundir-trash/`
- **Per-root trash**: Each root directory gets its own `~redundir-trash/` subdirectory (visible, not hidden)



**Example (single directory):**
```
$ redundir-tui ~/Documents
Scanning /home/user/Documents...
  Collecting files...
  Found 1523 total files
  Hashing 412 files, skipping 1111 files with unique sizes
  Hashed 412 files
  Found 89 duplicate files in 3 directories (overall redundancy: 21.60%)

[Interactive TUI starts here with split panes]
```

**Example (multiple directories):**
```
$ redundir-tui ~/backups ~/archive ~/old-stuff
Scanning 3 directories...
  /home/user/backups
  /home/user/archive
  /home/user/old-stuff
  Collecting files...
  Found 3421 total files
  Hashing 892 files, skipping 2529 files with unique sizes
  Hashed 892 files
  Found 456 duplicate files in 15 directories (overall redundancy: 13.33%)

[Interactive TUI starts here with split panes]
```

The TUI shows full progress information during scanning, then starts the interactive interface where you can explore which directories share files and see exactly which files are duplicated. When scanning multiple directories, duplicates are detected across all of them.

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
