# Tests for prompts.py. Run all: python3 -m unittest discover arc/tests

import copy
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pick_tasks import pick, pick_pilot  # noqa: E402
from prompts import (PROMPT_HASH, VARIANTS, build_prompt, grid_to_text, load_task,  # noqa: E402
                     prompt_hash, text_sha)

TASKS = pick() + pick_pilot()


def poison_test_outputs(task):
    poisoned = copy.deepcopy(task)
    for pair in poisoned["test"]:
        pair["output"] = [["LEAK"]]
    return poisoned


class TestPrompts(unittest.TestCase):

    def test_grid_to_text_spaces_between_cells(self):
        self.assertEqual(grid_to_text([[0, 0, 5], [0, 5, 0]]), "0 0 5\n0 5 0")

    # Checked at the source, not by searching the text: with every test output
    # poisoned, the prompt must come out byte-identical and without the poison.
    # Catches any use of a test output (any format, partial, identity tasks too).
    def test_no_test_output_reaches_any_prompt(self):
        for tid in TASKS:
            task = load_task(tid)
            poisoned = poison_test_outputs(task)
            for v in VARIANTS:
                with self.subTest(task=tid, variant=v):
                    p = build_prompt(task, v)
                    self.assertEqual(build_prompt(poisoned, v), p)
                    self.assertNotIn("LEAK", p)

    def test_leak_check_catches_a_leaky_builder(self):
        def leaky(task, variant):
            return build_prompt(task, variant) + str(task["test"][0]["output"])
        task = load_task("f3e14006")
        poisoned = poison_test_outputs(task)
        self.assertNotEqual(leaky(poisoned, "text"), leaky(task, "text"))
        self.assertIn("LEAK", leaky(poisoned, "text"))

    def test_every_example_and_test_input_is_in_the_prompt(self):
        for tid in TASKS:
            task = load_task(tid)
            for v in VARIANTS:
                with self.subTest(task=tid, variant=v):
                    p = build_prompt(task, v)
                    for pair in task["train"]:
                        self.assertIn(grid_to_text(pair["input"]), p)
                        self.assertIn(grid_to_text(pair["output"]), p)
                    for pair in task["test"]:
                        self.assertIn(grid_to_text(pair["input"]), p)

    def test_rule_line_only_in_rule_first(self):
        task = load_task("f3e14006")
        self.assertIn("Rule:", build_prompt(task, "rule_first"))
        self.assertNotIn("Rule:", build_prompt(task, "text"))

    def test_tasks_with_two_test_inputs_are_numbered(self):
        multi = [tid for tid in TASKS if len(load_task(tid)["test"]) > 1]
        self.assertTrue(multi)
        for tid in multi:
            with self.subTest(task=tid):
                p = build_prompt(load_task(tid), "text")
                self.assertIn("Test input 1:", p)
                self.assertIn("Test input 2:", p)
                self.assertIn("one output grid per test input", p)

    def test_unknown_variant_rejected(self):
        with self.assertRaises(ValueError):
            build_prompt(load_task("f3e14006"), "image")

    # The frozen value from precommit. If this fails, the prompt changed.
    def test_prompt_hash_is_the_frozen_one(self):
        self.assertEqual(prompt_hash(), PROMPT_HASH)
        self.assertEqual(PROMPT_HASH, "79d1a33708c3")

    def test_prompt_sha_same_prompt_same_sha(self):
        task = load_task("f3e14006")
        self.assertEqual(text_sha(build_prompt(task, "text")), text_sha(build_prompt(task, "text")))
        self.assertNotEqual(text_sha(build_prompt(task, "text")), text_sha(build_prompt(task, "rule_first")))


if __name__ == "__main__":
    unittest.main()
