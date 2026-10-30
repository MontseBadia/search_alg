# Tests for harness.py. Run all: python3 -m unittest discover arc/tests
#
# The model call is replaced (mock.patch("harness.call_model")): HTTP is
# tested in test_server.py, here only what harness does with each outcome.
# harness imports call_model by name, so the patch target is harness.call_model
# (patching server.call_model would have no effect here).
# Scored-path tests also fake the server check and use a temp results folder:
# no test can make a real call or touch runs/main.

import json
import os
import sys
import tempfile
import threading
import time
import unittest
import urllib.error
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import harness  # noqa: E402
from server import MODEL, SETTINGS, server_command  # noqa: E402

TASK = "f3e14006"  # pilot task: small, never scored

OK_RESPONSE = {"choices": [{"finish_reason": "stop",
                            "message": {"reasoning_content": "x", "content": "```\n1\n```"}}],
               "usage": {"prompt_tokens": 1, "completion_tokens": 1}}


def fake_result(**kind):
    def call(prompt, settings, url=None):
        return {"request": {"prompt": prompt, **settings}, "started": "t", "seconds": 1.0, **kind}
    return call


def raises(exc):
    def call(*args, **kwargs):
        raise exc
    return call


def read_attempts(d):
    with open(os.path.join(d, "attempts.jsonl")) as f:
        return [json.loads(line) for line in f]


class TestCallAndSave(unittest.TestCase):

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.path = os.path.join(self.dir, "a_text_s1.json")

    def run_with(self, call, **extra):
        with mock.patch("harness.call_model", call):
            return harness.call_and_save(TASK, "text", self.path, SETTINGS, **extra)

    def test_response_saved_at_result_path_and_linked_to_its_attempt(self):
        saved = self.run_with(fake_result(response=OK_RESPONSE), sample=1)
        self.assertEqual(saved, self.path)
        with open(saved) as f:
            result = json.load(f)
        start, end = read_attempts(self.dir)
        self.assertEqual((start["event"], end["event"], end["outcome"]), ("start", "end", "response"))
        self.assertEqual(result["attempt"], start["attempt"])
        self.assertEqual((start["sample"], result["sample"]), (1, 1))
        self.assertEqual(result["prompt_sha"], start["prompt_sha"])

    def test_server_error_saved_at_result_path(self):
        saved = self.run_with(fake_result(error={"status": 500, "body": "oom"}))
        self.assertEqual(saved, self.path)
        self.assertEqual(read_attempts(self.dir)[-1]["outcome"], "error")

    def test_crash_saved_beside_result_path(self):
        saved = self.run_with(fake_result(crash={"type": "RemoteDisconnected", "detail": "", "stage": "reply"}))
        self.assertIn("_crash-", saved)
        self.assertFalse(os.path.exists(self.path))  # left free: rerun next pass
        self.assertEqual(read_attempts(self.dir)[-1]["saved"], saved)

    def test_bad_response_saved_beside_result_path(self):
        saved = self.run_with(fake_result(bad_response={"detail": "cut", "raw": "{"}))
        self.assertIn("_crash-", saved)
        self.assertFalse(os.path.exists(self.path))

    def test_refused_logged_as_unreachable_and_raised(self):
        refused = urllib.error.URLError(ConnectionRefusedError())
        with self.assertRaises(urllib.error.URLError):
            self.run_with(raises(refused))
        self.assertEqual(read_attempts(self.dir)[-1]["outcome"], "unreachable")
        self.assertEqual(os.listdir(self.dir), ["attempts.jsonl"])  # nothing saved

    def test_ctrl_c_logged_as_interrupted_and_raised(self):
        with self.assertRaises(KeyboardInterrupt):
            self.run_with(raises(KeyboardInterrupt))
        self.assertEqual(read_attempts(self.dir)[-1]["outcome"], "interrupted")

    def test_every_start_has_an_end(self):
        self.run_with(fake_result(response=OK_RESPONSE))
        events = [e["event"] for e in read_attempts(self.dir)]
        self.assertEqual(events, ["start", "end"])

    def test_existing_result_stops_before_any_call(self):
        with open(self.path, "w") as f:
            f.write("{}")
        with self.assertRaises(FileExistsError):
            self.run_with(raises(AssertionError("a call was made")))
        self.assertFalse(os.path.exists(os.path.join(self.dir, "attempts.jsonl")))

    # Started twice by mistake, at the same time: both run, neither is lost or
    # overwritten, the second becomes _dup1. Precommit: the first counts.
    def test_same_call_twice_gives_dup_not_loss(self):
        def slow_ok(prompt, settings, url=None):
            time.sleep(0.5)  # both calls start before either saves
            return fake_result(response=OK_RESPONSE)(prompt, settings, url)
        outcomes = []
        with mock.patch("harness.call_model", slow_ok):
            lanes = [threading.Thread(target=lambda: outcomes.append(
                harness.call_and_save(TASK, "text", self.path, SETTINGS))) for _ in range(2)]
            for t in lanes:
                t.start()
            for t in lanes:
                t.join()
        self.assertEqual(sorted(outcomes), [self.path, self.path[:-len(".json")] + "_dup1.json"])
        self.assertEqual(sorted(e["event"] for e in read_attempts(self.dir)), ["end", "end", "start", "start"])


class TestPilotCall(unittest.TestCase):

    def test_overrides_reach_the_call_but_not_the_frozen_settings(self):
        seen = {}

        def capture(prompt, settings, url=None):
            seen.update(settings)
            return fake_result(response=OK_RESPONSE)(prompt, settings, url)
        with mock.patch("harness.RUNS", tempfile.mkdtemp()), mock.patch("harness.call_model", capture):
            saved = harness.pilot_call(TASK, "text", "test", max_tokens=5)
        self.assertEqual(seen["max_tokens"], 5)
        self.assertEqual(SETTINGS["max_tokens"], 22000)
        self.assertTrue(saved.endswith(os.path.join("pilot", f"{TASK}_text_test.json")))


class TestRunCall(unittest.TestCase):

    FROZEN = {"pid": 4242, "args": "/x/python3.13 /x/" + server_command(),
              "health": {"loaded_model": MODEL, "apc_enabled": False}}

    def setUp(self):
        self.runs = tempfile.mkdtemp()

    def test_path_format(self):
        self.assertTrue(harness.run_path("18447a8d", "text", 2).endswith(
            os.path.join("runs", "main", "18447a8d_text_s2.json")))

    def test_bad_input_rejected_before_the_server_is_even_checked(self):
        with mock.patch("harness.observe_server", raises(AssertionError("server checked"))):
            for bad in [("33067df9", "text", 1), ("18447a8d", "image", 1), ("18447a8d", "text", 4)]:
                with self.subTest(bad=bad), self.assertRaises(ValueError):
                    harness.run_call(*bad)

    def test_misconfigured_server_refused_nothing_sent(self):
        wrong = {**self.FROZEN, "args": self.FROZEN["args"].replace("--kv-bits 8", "--kv-bits 4")}
        with mock.patch("harness.RUNS", self.runs), \
                mock.patch("harness.observe_server", lambda: wrong), \
                mock.patch("harness.call_model", raises(AssertionError("a model call was made"))):
            with self.assertRaises(RuntimeError) as ctx:
                harness.run_call("18447a8d", "text", 1)
        self.assertIn("--kv-bits", str(ctx.exception))
        log = read_attempts(os.path.join(self.runs, "main"))
        self.assertEqual([e["event"] for e in log], ["refused"])

    # The path every scored call takes: server checked, then its details
    # recorded in the result and the attempt log.
    def test_scored_call_records_the_observed_server(self):
        with mock.patch("harness.RUNS", self.runs), \
                mock.patch("harness.observe_server", lambda: self.FROZEN), \
                mock.patch("harness.call_model", fake_result(response=OK_RESPONSE)):
            saved = harness.run_call("18447a8d", "rule_first", 1)
        self.assertEqual(saved, os.path.join(self.runs, "main", "18447a8d_rule_first_s1.json"))
        with open(saved) as f:
            result = json.load(f)
        self.assertEqual(result["run_info"]["server_observed"]["pid"], 4242)
        self.assertEqual((result["sample"], result["run_name"]), (1, "main"))
        start = read_attempts(os.path.join(self.runs, "main"))[0]
        self.assertEqual((start["server_pid"], start["sample"], start["run_name"]), (4242, 1, "main"))
        self.assertEqual(result["request"]["max_tokens"], SETTINGS["max_tokens"])  # frozen settings used


if __name__ == "__main__":
    unittest.main()
