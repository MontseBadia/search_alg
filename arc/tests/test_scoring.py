# Tests for scoring.py. Run all: python3 -m unittest discover arc/tests

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scoring import parse_answer, parse_grid, score, score_result  # noqa: E402

TASK = {"test": [{"input": [[0]], "output": [[1, 2], [3, 4]]}]}
TWO_TESTS = {"test": [{"input": [[0]], "output": [[1, 2], [3, 4]]},
                      {"input": [[0]], "output": [[5]]}]}


def response(content, finish_reason="stop"):
    return {"response": {"choices": [{"message": {"content": content},
                                      "finish_reason": finish_reason}]}}


class TestParseGrid(unittest.TestCase):

    def test_spaces_commas_and_bare_digits(self):
        self.assertEqual(parse_grid("0 1 2\n3 4 5\n"), [[0, 1, 2], [3, 4, 5]])
        self.assertEqual(parse_grid("0,1,2\n3,4,5"), [[0, 1, 2], [3, 4, 5]])
        self.assertEqual(parse_grid("0, 1, 2\n3, 4, 5"), [[0, 1, 2], [3, 4, 5]])
        self.assertEqual(parse_grid("012\n345"), [[0, 1, 2], [3, 4, 5]])

    def test_blank_lines_skipped(self):
        self.assertEqual(parse_grid("\n1 2\n\n3 4\n"), [[1, 2], [3, 4]])

    def test_rejects_with_reason(self):
        for bad, why in [("0 1\n2", "ragged"), ("a b", "digits"), ("10 2", "digits"),
                         ("-1 2", "digits"), ("  \n", "empty")]:
            with self.subTest(block=bad):
                with self.assertRaises(ValueError) as cm:
                    parse_grid(bad)
                self.assertIn(why, str(cm.exception))

    # str.isdigit() is Unicode: '٣' and '５' passed it and int() turned them
    # into 3 and 5, '²' passed it and then int() failed with its own message.
    def test_non_ascii_digits_rejected(self):
        for bad in ["1 ٣\n3 4", "１２\n34", "1 ²\n3 4", "1 ①\n3 4"]:
            with self.subTest(block=bad):
                with self.assertRaises(ValueError) as cm:
                    parse_grid(bad)
                self.assertIn("not digits 0-9", str(cm.exception))


class TestParseAnswer(unittest.TestCase):

    # last N blocks, intermediate grids ignored
    def test_takes_last_blocks(self):
        two = "map:\n```\n9 9\n9 9\n```\nanswer:\n```text\n1 2\n3 4\n```"
        self.assertEqual(parse_answer(two, 1), ([[[1, 2], [3, 4]]], None))
        self.assertEqual(parse_answer(two, 2)[0], [[[9, 9], [9, 9]], [[1, 2], [3, 4]]])

    def test_too_few_blocks(self):
        self.assertEqual(parse_answer("no blocks here", 1), (None, "0 code block(s) for 1 test input(s)"))
        self.assertEqual(parse_answer("```\n1\n```", 2), (None, "1 code block(s) for 2 test input(s)"))

    def test_empty_answer(self):
        self.assertEqual(parse_answer("", 1), (None, "no answer text"))
        self.assertEqual(parse_answer(None, 1), (None, "no answer text"))
        self.assertEqual(parse_answer("  \n", 1), (None, "no answer text"))

    def test_bad_grid_gives_reason_not_exception(self):
        grids, reason = parse_answer("```\n1 x\n```", 1)
        self.assertIsNone(grids)
        self.assertIn("not digits 0-9", reason)


class TestScore(unittest.TestCase):

    def test_solved(self):
        s = score(TASK, "```\n1 2\n3 4\n```")
        self.assertEqual(s["auto_outcome"], "solved")
        self.assertIsNone(s["format_reason"])

    def test_wrong_grid_counts_cells(self):
        s = score(TASK, "```\n1 2\n3 0\n```")
        self.assertEqual(s["auto_outcome"], "wrong grid")
        self.assertEqual(s["per_test"][0]["cells_match"], 3)
        self.assertEqual(s["per_test"][0]["cells_total"], 4)

    def test_wrong_shape_no_cell_count(self):
        t = score(TASK, "```\n1 2 0\n3 4 0\n```")["per_test"][0]
        self.assertFalse(t["exact"])
        self.assertEqual(t["shape"], (2, 3))
        self.assertEqual(t["expected_shape"], (2, 2))
        self.assertIsNone(t["cells_match"])

    # all or nothing: one right out of two is still wrong
    def test_two_tests_one_wrong(self):
        s = score(TWO_TESTS, "```\n1 2\n3 4\n```\n```\n6\n```")
        self.assertEqual(s["auto_outcome"], "wrong grid")
        self.assertEqual([t["exact"] for t in s["per_test"]], [True, False])
        self.assertEqual(score(TWO_TESTS, "```\n1 2\n3 4\n```\n```\n5\n```")["auto_outcome"], "solved")

    def test_hit_max_tokens(self):
        self.assertEqual(score(TASK, "", "length")["format_reason"], "hit max_tokens, no answer")
        self.assertEqual(score(TASK, None, "length")["format_reason"], "hit max_tokens, no answer")
        r = score(TASK, "thinking out loud...", "length")["format_reason"]
        self.assertTrue(r.startswith("hit max_tokens mid-answer"), r)

    # cut off but the grid is complete: scored like any other answer
    def test_length_with_full_answer_is_scored(self):
        self.assertEqual(score(TASK, "```\n1 2\n3 4\n```", "length")["auto_outcome"], "solved")

    def test_no_grid_finished(self):
        s = score(TASK, "no grid, finished", "stop")
        self.assertEqual(s["auto_outcome"], "format failure")
        self.assertTrue(s["format_reason"].startswith("0 code block"))
        self.assertEqual(s["per_test"], [])


class TestScoreResult(unittest.TestCase):

    # crash record: never scored as a model failure
    def test_crash_is_rerun(self):
        crash = {"crash": {"type": "RemoteDisconnected", "detail": ""}, "seconds": 600.0}
        self.assertEqual(score_result(TASK, crash),
                         {"auto_outcome": "crash, rerun", "format_reason": "RemoteDisconnected", "per_test": []})

    def test_bad_response_is_rerun(self):
        bad = {"bad_response": {"detail": "Unterminated string", "raw": "{"}, "seconds": 600.0}
        self.assertEqual(score_result(TASK, bad),
                         {"auto_outcome": "crash, rerun", "format_reason": "bad response", "per_test": []})

    def test_server_error_is_format_failure(self):
        err = {"error": {"status": 500, "body": "oom"}, "seconds": 1.0}
        self.assertEqual(score_result(TASK, err),
                         {"auto_outcome": "format failure", "format_reason": "server error 500", "per_test": []})

    def test_metal_out_of_memory_is_rerun(self):
        body = ('{"detail":"Generation failed: [METAL] Command buffer execution failed: '
                'Insufficient Memory (00000008:kIOGPUCommandBufferCallbackErrorOutOfMemory)."}')
        err = {"error": {"status": 500, "body": body}, "seconds": 1883.9}
        self.assertEqual(score_result(TASK, err),
                         {"auto_outcome": "crash, rerun", "format_reason": "out of memory", "per_test": []})

    def test_response_goes_through_score(self):
        self.assertEqual(score_result(TASK, response("```\n1 2\n3 4\n```"))["auto_outcome"], "solved")
        self.assertEqual(score_result(TASK, response("", "length"))["format_reason"], "hit max_tokens, no answer")


if __name__ == "__main__":
    unittest.main()
