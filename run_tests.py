#!/usr/bin/env python3
"""
Standalone test runner for dedupdir tests using unittest.

Usage:
    ./tests/run_tests.py          # Run all tests
    ./tests/run_tests.py -v       # Run with verbose output
    ./tests/run_tests.py TestClass.test_method  # Run specific test
"""

import sys
import os
import unittest
import types
import tempfile
import shutil
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


def load_module_from_file(filepath, module_name):
    """Load a Python module from a file without .py extension."""
    filepath = Path(filepath)
    if not filepath.exists():
        raise ImportError(f"Could not find {filepath}")

    with open(filepath, 'r') as f:
        code = f.read()

    module = types.ModuleType(module_name)
    module.__file__ = str(filepath)
    sys.modules[module_name] = module
    exec(code, module.__dict__)
    return module


# Load modules once
DEDUPDIR = load_module_from_file(PROJECT_ROOT / "dedupdir", 'dedupdir')
TUI_MODULE = load_module_from_file(PROJECT_ROOT / "dedupdir-tui", 'dedupdir_tui')


class TempDirMixin:
    """Mixin providing temporary directory setup/teardown."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix='dedupdir_test_'))

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)


class TestFindDuplicates(TempDirMixin, unittest.TestCase):
    """Tests for the find_duplicates function."""

    def create_simple_test_dirs(self):
        """Create simple test structure with duplicates."""
        root1 = self.temp_dir / 'root1'
        root2 = self.temp_dir / 'root2'
        root1.mkdir()
        root2.mkdir()

        (root1 / 'duplicate.txt').write_text('duplicate content')
        (root2 / 'duplicate.txt').write_text('duplicate content')
        (root1 / 'unique1.txt').write_text('unique to root1')
        (root2 / 'unique2.txt').write_text('unique to root2')

        return root1, root2

    def test_finds_duplicate_files(self):
        """Should identify files with identical content as duplicates."""
        root1, root2 = self.create_simple_test_dirs()
        result = DEDUPDIR.find_duplicates([root1, root2], quiet=True, use_cache=False, jobs=1)
        dir_stats, total_dups, total_files, file_to_hash, hash_to_dirs, dir_all_files, _ = result

        self.assertGreater(total_dups, 0)
        self.assertEqual(total_files, 4)

    def test_unique_files_not_duplicates(self):
        """Unique files should not be counted as duplicates."""
        root1, root2 = self.create_simple_test_dirs()
        result = DEDUPDIR.find_duplicates([root1, root2], quiet=True, use_cache=False, jobs=1)
        _, _, _, file_to_hash, hash_to_dirs, _, _ = result

        unique1_path = root1 / 'unique1.txt'
        if unique1_path in file_to_hash:
            unique_hash = file_to_hash[unique1_path]
            self.assertEqual(len(hash_to_dirs.get(unique_hash, set())), 1)


class TestRedundancyScore(unittest.TestCase):
    """Tests for redundancy score calculation."""

    def test_full_redundancy_is_1(self):
        """Directory with all duplicates should be 1.0 (100%) redundant."""
        score = DEDUPDIR.calculate_redundancy_score(10, 10)
        self.assertEqual(score, 1.0)

    def test_no_redundancy_is_0(self):
        """Directory with no duplicates should be 0.0 redundant."""
        score = DEDUPDIR.calculate_redundancy_score(0, 10)
        self.assertEqual(score, 0.0)

    def test_partial_redundancy(self):
        """Partial redundancy should calculate correctly."""
        score = DEDUPDIR.calculate_redundancy_score(5, 10)
        self.assertEqual(score, 0.5)

    def test_empty_directory_is_0(self):
        """Empty directory should be 0.0 redundant."""
        score = DEDUPDIR.calculate_redundancy_score(0, 0)
        self.assertEqual(score, 0.0)


class TestTUIInitialization(TempDirMixin, unittest.TestCase):
    """Tests for TUI initialization and scanning."""

    def test_tui_creates_with_single_root(self):
        """TUI should initialize with a single root directory."""
        root = self.temp_dir / 'single'
        root.mkdir()
        (root / 'file.txt').write_text('content')

        tui = TUI_MODULE.DedupdirTUI(root, use_cache=False)
        self.assertEqual(len(tui.root_paths), 1)

    def test_tui_creates_with_multiple_roots(self):
        """TUI should initialize with multiple root directories."""
        root1 = self.temp_dir / 'root1'
        root2 = self.temp_dir / 'root2'
        root1.mkdir()
        root2.mkdir()
        (root1 / 'file.txt').write_text('content')
        (root2 / 'file.txt').write_text('content')

        tui = TUI_MODULE.DedupdirTUI([root1, root2], use_cache=False)
        self.assertEqual(len(tui.root_paths), 2)

    def test_scan_populates_data_structures(self):
        """Scanning should populate all data structures."""
        root = self.temp_dir / 'root'
        root.mkdir()
        (root / 'file1.txt').write_text('content1')
        (root / 'file2.txt').write_text('content2')

        tui = TUI_MODULE.DedupdirTUI(root, use_cache=False)
        tui.scan(quiet=True)

        self.assertIsNotNone(tui.file_to_hash)
        self.assertIsNotNone(tui.hash_to_dirs)
        self.assertIsNotNone(tui.dir_all_files)


class TestTrashOperations(TempDirMixin, unittest.TestCase):
    """Tests for trash functionality."""

    def create_tui_with_files(self):
        """Create TUI with test files."""
        root1 = self.temp_dir / 'root1'
        root2 = self.temp_dir / 'root2'
        root1.mkdir()
        root2.mkdir()

        (root1 / 'duplicate.txt').write_text('duplicate content')
        (root2 / 'duplicate.txt').write_text('duplicate content')
        (root1 / 'unique1.txt').write_text('unique to root1')

        tui = TUI_MODULE.DedupdirTUI([root1, root2], use_cache=False)
        tui.scan(quiet=True)
        return tui, root1, root2

    def test_trash_item_moves_file(self):
        """Trashing a file should move it to trash directory."""
        tui, root1, root2 = self.create_tui_with_files()
        file_to_trash = root1 / 'unique1.txt'

        self.assertTrue(file_to_trash.exists())
        tui.trash_item(file_to_trash, 'file')
        self.assertFalse(file_to_trash.exists())

    def test_trash_creates_undo_entry(self):
        """Trashing should add entry to undo stack."""
        tui, root1, root2 = self.create_tui_with_files()
        file_to_trash = root1 / 'unique1.txt'

        initial_stack_size = len(tui.trash_stack)
        tui.trash_item(file_to_trash, 'file')
        self.assertEqual(len(tui.trash_stack), initial_stack_size + 1)

    def test_undo_restores_file(self):
        """Undo should restore trashed file."""
        tui, root1, root2 = self.create_tui_with_files()
        file_to_trash = root1 / 'unique1.txt'
        original_content = file_to_trash.read_text()

        tui.trash_item(file_to_trash, 'file')
        self.assertFalse(file_to_trash.exists())

        tui.undo_last_trash()
        self.assertTrue(file_to_trash.exists())
        self.assertEqual(file_to_trash.read_text(), original_content)


class TestCacheInvalidation(TempDirMixin, unittest.TestCase):
    """Tests for cache invalidation."""

    def test_invalidate_all_caches_clears_caches(self):
        """invalidate_all_caches should clear all cache dictionaries."""
        root = self.temp_dir / 'root'
        root.mkdir()
        (root / 'file.txt').write_text('content')

        tui = TUI_MODULE.DedupdirTUI(root, use_cache=False)
        tui.scan(quiet=True)

        # Add test data to caches
        tui._recursive_stats_cache['test'] = 'data'
        tui._dir_contents_cache['test'] = 'data'
        tui._dir_sizes_cache['test'] = 'data'

        tui.invalidate_all_caches()

        self.assertEqual(len(tui._recursive_stats_cache), 0)
        self.assertEqual(len(tui._dir_contents_cache), 0)
        self.assertEqual(len(tui._dir_sizes_cache), 0)

    def test_rescan_updates_after_external_changes(self):
        """Rescan should pick up external filesystem changes."""
        # Create two roots with duplicates so files get tracked
        root1 = self.temp_dir / 'root1'
        root2 = self.temp_dir / 'root2'
        root1.mkdir()
        root2.mkdir()

        # Create duplicate files (needed for tracking in file_to_hash)
        (root1 / 'dup.txt').write_text('duplicate content')
        (root2 / 'dup.txt').write_text('duplicate content')

        tui = TUI_MODULE.DedupdirTUI([root1, root2], use_cache=False)
        tui.scan(quiet=True)

        # Check dir_all_files instead of file_to_hash (which only tracks duplicates)
        initial_total_files = sum(len(files) for files in tui.dir_all_files.values())

        # Add a new file externally
        (root1 / 'new_file.txt').write_text('new content')

        tui.rescan()

        new_total_files = sum(len(files) for files in tui.dir_all_files.values())
        self.assertEqual(new_total_files, initial_total_files + 1)


class TestViewStack(TempDirMixin, unittest.TestCase):
    """Tests for view stack navigation."""

    def create_tui(self):
        """Create a basic TUI instance."""
        root = self.temp_dir / 'root'
        root.mkdir()
        (root / 'file.txt').write_text('content')

        tui = TUI_MODULE.DedupdirTUI(root, use_cache=False)
        tui.scan(quiet=True)
        return tui

    def test_push_view_adds_to_stack(self):
        """push_view should add view to stack."""
        tui = self.create_tui()
        initial_depth = len(tui.view_stack)
        tui.push_view({'type': 'dir_detail', 'data': {'dir_path': Path('/test')}})
        self.assertEqual(len(tui.view_stack), initial_depth + 1)

    def test_pop_view_removes_from_stack(self):
        """pop_view should remove view from stack."""
        tui = self.create_tui()
        tui.push_view({'type': 'dir_detail', 'data': {'dir_path': Path('/test')}})
        depth_after_push = len(tui.view_stack)

        tui.pop_view()
        self.assertEqual(len(tui.view_stack), depth_after_push - 1)

    def test_pop_view_restores_selection(self):
        """pop_view should restore previous selection state."""
        tui = self.create_tui()
        tui.selected_idx = 5
        tui.scroll_offset = 2

        tui.push_view({'type': 'dir_detail', 'data': {'dir_path': Path('/test')}})

        # Selection resets on push
        self.assertEqual(tui.selected_idx, 0)
        self.assertEqual(tui.scroll_offset, 0)

        tui.pop_view()

        # Selection restored on pop
        self.assertEqual(tui.selected_idx, 5)
        self.assertEqual(tui.scroll_offset, 2)


class TestConfirmationLogic(TempDirMixin, unittest.TestCase):
    """Tests for trash confirmation logic."""

    def test_unique_file_needs_confirmation(self):
        """File with count=1 should require confirmation."""
        root1 = self.temp_dir / 'root1'
        root2 = self.temp_dir / 'root2'
        root1.mkdir()
        root2.mkdir()

        (root1 / 'duplicate.txt').write_text('dup')
        (root2 / 'duplicate.txt').write_text('dup')
        (root1 / 'unique.txt').write_text('unique')

        tui = TUI_MODULE.DedupdirTUI([root1, root2], use_cache=False)
        tui.scan(quiet=True)

        unique_file = root1 / 'unique.txt'
        count = tui.get_file_redundancy_count(unique_file)

        self.assertLessEqual(count, 1)

    def test_duplicate_file_no_confirmation(self):
        """File with count>1 should not require confirmation."""
        root1 = self.temp_dir / 'root1'
        root2 = self.temp_dir / 'root2'
        root1.mkdir()
        root2.mkdir()

        (root1 / 'duplicate.txt').write_text('dup')
        (root2 / 'duplicate.txt').write_text('dup')

        tui = TUI_MODULE.DedupdirTUI([root1, root2], use_cache=False)
        tui.scan(quiet=True)

        dup_file = root1 / 'duplicate.txt'
        count = tui.get_file_redundancy_count(dup_file)

        self.assertGreater(count, 1)


def main():
    # Parse arguments
    verbosity = 2 if '-v' in sys.argv else 1

    # Remove our flags from argv so unittest doesn't see them
    argv = [arg for arg in sys.argv if arg not in ['-v']]

    # Discover and run tests
    loader = unittest.TestLoader()

    if len(argv) > 1:
        # Run specific test(s)
        suite = unittest.TestSuite()
        for pattern in argv[1:]:
            try:
                suite.addTests(loader.loadTestsFromName(pattern, module=sys.modules[__name__]))
            except Exception as e:
                print(f"Error loading test '{pattern}': {e}")
                return 1
    else:
        # Run all tests
        suite = loader.loadTestsFromModule(sys.modules[__name__])

    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)

    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(main())
