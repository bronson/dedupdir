# [dedupdir](https://github.com/bronson/dedupdir) Changelog

## [0.2.XX] - 2026-XX
* convert the two-pane UI back to single-pane and simplify the file view
* automatically collapse child dirs when they're 100% redundant
* add automatic caching to speed up subsequent runs
* also add the -C/--no-cache option to disable caching
* confirm quitting unless you're at the top level
* add scroll indicators to panes
* can now 'o' on directories to open them in the platform viewer
* parent dirs now incorporate their children's redundancy scores
* added 's'/'S' to switch the column used to sort the data
* make the trash viewer hierarchical so it can handle lots of files
* added 'P' key to promote (move) a single item to their parent
* added '^R' key to reload and refresh all redundancy scores
* added run_tests.py to provide some simple unit tests
* added 'D' to group trash similar files in the current directory

## [0.1.0] - 2026-01-21
* Rename project from redundir to dedupdir.
  * (previous name suggested making dirs more redundant)
* Add the '?' keystroke to bring up a help screen anywhere.
* Add a hint bar that shows the most common keystrokes.
* Add 'v' key to view file contents within the app.
* Add 'o' key to open the. file in the platform's viewer.
* show current deduping statistics in the upper right corner.
* Remove any mention of 'deleting' files. We only Trash them.
* Fix terminal resize handling. No more blank screen.

[0.1.0]: https://github.com/bronson/dedupdir/releases/tag/v0.1.0
