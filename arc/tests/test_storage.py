# Tests for storage.py. Run all: python3 -m unittest discover arc/tests

import glob
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from storage import crash_path, log_attempt, save_new  # noqa: E402


class TestSaveNew(unittest.TestCase):

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.path = os.path.join(self.dir, "x_text_s1.json")

    def read(self, p):
        with open(p) as f:
            return json.load(f)

    def test_never_overwrites_never_discards(self):
        self.assertEqual(save_new(self.path, {"a": 1}), self.path)
        second = save_new(self.path, {"a": 2})
        third = save_new(self.path, {"a": 3})
        self.assertTrue(second.endswith("x_text_s1_dup1.json"))
        self.assertTrue(third.endswith("x_text_s1_dup2.json"))
        self.assertEqual([self.read(p) for p in (self.path, second, third)], [{"a": 1}, {"a": 2}, {"a": 3}])

    def test_no_temp_files_left(self):
        save_new(self.path, {"a": 1})
        save_new(self.path, {"a": 2})
        self.assertEqual(glob.glob(os.path.join(self.dir, ".tmp-*")), [])

    def test_interrupted_while_syncing_leaves_nothing_and_does_not_block(self):
        with mock.patch("os.fsync", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                save_new(self.path, {"a": 1})
        self.assertEqual(os.listdir(self.dir), [])
        self.assertEqual(save_new(self.path, {"a": 1}), self.path)

    def test_failed_publish_removes_temp_and_publishes_nothing(self):
        with mock.patch("os.link", side_effect=OSError("disk problem")):
            with self.assertRaises(OSError):
                save_new(self.path, {"a": 1})
        self.assertEqual(os.listdir(self.dir), [])

    def test_unserialisable_data_leaves_no_file(self):
        with self.assertRaises(TypeError):
            save_new(self.path, {"a": object()})
        self.assertEqual(os.listdir(self.dir), [])


class TestCrashPathAndLog(unittest.TestCase):

    def test_crash_path_never_the_result_path(self):
        path = "/x/runs/main/18447a8d_text_s1.json"
        cp = crash_path(path)
        self.assertNotEqual(cp, path)
        self.assertIn("18447a8d_text_s1_crash-", cp)
        self.assertTrue(cp.endswith(".json"))

    def test_log_attempt_appends_one_line_per_record(self):
        d = tempfile.mkdtemp()
        path = os.path.join(d, "x_text_s1.json")
        log_attempt(path, {"event": "start"})
        log_attempt(path, {"event": "end"})
        with open(os.path.join(d, "attempts.jsonl")) as f:
            self.assertEqual([json.loads(line)["event"] for line in f], ["start", "end"])


if __name__ == "__main__":
    unittest.main()
