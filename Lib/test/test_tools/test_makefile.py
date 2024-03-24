"""
Tests for `Makefile`.
"""

import os
import unittest
from test import support
import sysconfig

MAKEFILE = sysconfig.get_makefile_filename()

if not support.check_impl_detail(cpython=True):
    raise unittest.SkipTest('cpython only')
if not os.path.exists(MAKEFILE) or not os.path.isfile(MAKEFILE):
    raise unittest.SkipTest('Makefile could not be found')


class TestMakefile(unittest.TestCase):
    def list_test_dirs(self):
        result = []
        found_testsubdirs = False
        with open(MAKEFILE, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('TESTSUBDIRS='):
                    found_testsubdirs = True
                    result.append(
                        line.removeprefix('TESTSUBDIRS=').replace(
                            '\\', '',
                        ).strip(),
                    )
                    continue
                if found_testsubdirs:
                    if '\t' not in line:
                        break
                    result.append(line.replace('\\', '').strip())
        return result

    def test_makefile_test_folders(self):
        test_dirs = self.list_test_dirs()
        idle_test = 'idlelib/idle_test'
        self.assertIn(idle_test, test_dirs)

        used = [idle_test]
        for dirpath, _, _ in os.walk(support.TEST_HOME_DIR):
            dirname = os.path.basename(dirpath)
            if (
                dirname == '__pycache__'
                or dirname.startswith('.')
                or not os.listdir(dirpath)
            ):
                continue

            relpath = os.path.relpath(dirpath, support.STDLIB_DIR)
            with self.subTest(relpath=relpath):
                self.assertIn(
                    relpath,
                    test_dirs,
                    msg=(
                        f"{relpath!r} is not included in the Makefile's list "
                        "of test directories to install"
                    )
                )
                used.append(relpath)

        # Check that there are no extra entries:
        unique_test_dirs = set(test_dirs)
        self.assertSetEqual(unique_test_dirs, set(used))
        self.assertEqual(len(test_dirs), len(unique_test_dirs))
