# [dedupdir](https://github.com/bronson/dedupdir) Changelog

## [0.2.XX] - 2026-XX
* convert the two-pane UI back to single-pane and simplify the file view
* automatically collapse child dirs when they're 100% redundant
* confirm quitting unless you're at the top level
* add scroll indicators to panes

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
