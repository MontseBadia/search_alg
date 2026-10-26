# Tests for server.py. Run all: python3 -m unittest discover arc/tests
# No test talks to the real model server: fake servers on free ports only.

import http.server
import json
import os
import socket
import struct
import sys
import threading
import time
import unittest
import urllib.error

ARC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ARC)

from server import (MODEL, SETTINGS, call_model, check_server, observe_server,  # noqa: E402
                    request_body, run_info, server_command, summarize)


# Fake servers. Each one reads the request, waits `delay` seconds, then sends
# `reply` as raw bytes and closes. Raw bytes so a reply can be broken in
# exactly one way: b"" = hang up without answering.
def http_reply(status, body):
    return (f"HTTP/1.1 {status} X\r\nContent-Type: application/json\r\n"
            f"Content-Length: {len(body)}\r\n\r\n").encode() + body


ERROR_500 = http_reply(500, b'{"detail": "out of memory"}')


def fake_server(reply, delay=0):  # -> (url, stop)
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_POST(self):
            self.rfile.read(int(self.headers["Content-Length"]))
            time.sleep(delay)
            self.wfile.write(reply)
            self.wfile.flush()
            self.close_connection = True

        def log_message(self, *args):
            pass
    s = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=s.serve_forever, daemon=True).start()

    def stop():
        s.shutdown()      # stops the serve loop
        s.server_close()  # and closes the listening socket
    return f"http://127.0.0.1:{s.server_port}/v1/chat/completions", stop


def call_fake(reply):
    url, stop = fake_server(reply)
    try:
        return call_model("hi", url=url)
    finally:
        stop()


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))  # port 0: the OS picks a free one
    port = s.getsockname()[1]
    s.close()
    return port


class TestRequestAndInfo(unittest.TestCase):

    def test_request_body(self):
        body = request_body("hi")
        self.assertEqual(body["messages"], [{"role": "user", "content": "hi"}])
        self.assertEqual(body["top_k"], 20)  # must be sent, server default is off
        self.assertIs(body["enable_thinking"], True)
        self.assertEqual(body["model"], MODEL)

    def test_overrides_apply_but_cannot_replace_the_prompt(self):
        self.assertEqual(request_body("hi", {**SETTINGS, "max_tokens": 5})["max_tokens"], 5)
        self.assertEqual(request_body("hi", {"messages": "oops"})["messages"][0]["content"], "hi")

    def test_none_settings_left_out(self):
        self.assertNotIn("thinking_budget", request_body("hi", {**SETTINGS, "thinking_budget": None}))

    def test_run_info(self):
        info = run_info()
        self.assertTrue(info["model_revision"])
        self.assertTrue(info["mlx_vlm"])
        self.assertEqual(info["server"]["max_num_seqs"], 2)
        json.dumps(info)  # goes into every result file

    def test_server_command_has_frozen_flags(self):
        cmd = server_command()
        self.assertIn("--kv-bits 8", cmd)
        self.assertIn("--max-num-seqs 2", cmd)


class TestSummarize(unittest.TestCase):

    def test_real_medium30k_pilot(self):
        path = os.path.join(ARC, "runs", "pilot", "f3e14006_text_medium30k.json")
        if not os.path.exists(path):
            self.skipTest("pilot file not present")
        with open(path) as f:
            s = summarize(json.load(f))
        self.assertEqual((s["outcome"], s["finish_reason"], s["answer_chars"]), ("response", "length", 0))
        self.assertIs(s["maybe_forced"], False)  # no thinking_budget in that request

    def test_forced_heuristic_and_counts(self):
        fake = {"request": {"thinking_budget": 100}, "seconds": 1.0,
                "response": {"choices": [{"finish_reason": "stop",
                                          "message": {"reasoning_content": "abc", "content": "```\n1\n```"}}],
                             "usage": {"prompt_tokens": 5, "completion_tokens": 120}}}
        s = summarize(fake)
        self.assertTrue(s["maybe_forced"])
        self.assertEqual((s["answer_chars"], s["thinking_chars"]), (9, 3))

    def test_odd_reply_gets_a_note_not_a_crash(self):
        s = summarize({"request": {}, "seconds": 1.0, "response": {"error": "out of memory"}})
        self.assertIn("summary_error", s)


class TestCallModelFailures(unittest.TestCase):

    def test_server_error_kept_as_data(self):
        r = call_fake(ERROR_500)
        self.assertEqual(r["error"]["status"], 500)
        self.assertIn("out of memory", r["error"]["body"])
        self.assertNotIn("response", r)
        self.assertTrue(r["started"])
        self.assertEqual(summarize(r)["outcome"], "error")

    def test_server_dies_before_replying_is_a_crash(self):
        r = call_fake(b"")
        self.assertEqual(r["crash"]["stage"], "reply")
        self.assertFalse({"response", "error"} & set(r))
        self.assertEqual(summarize(r)["crash"], r["crash"]["type"])

    def test_cut_off_json_is_bad_response_with_raw_kept(self):
        cut_json = b'{"choices": [{"message": {"content": "```\\n1 2'
        r = call_fake(http_reply(200, cut_json))
        self.assertEqual(r["bad_response"]["raw"], cut_json.decode())
        self.assertFalse({"response", "crash", "error"} & set(r))

    def test_body_shorter_than_announced_is_a_crash(self):
        r = call_fake(b"HTTP/1.1 200 X\r\nContent-Length: 1000\r\n\r\n" + b'{"choices": [{"mess')
        self.assertEqual(r["crash"]["type"], "IncompleteRead")

    def test_garbage_reply_is_a_crash(self):
        r = call_fake(b"garbage instead of a status line\r\n\r\n")
        self.assertIn("crash", r)

    def test_refused_connection_raises(self):
        with self.assertRaises(urllib.error.URLError) as ctx:
            call_model("hi", url=f"http://127.0.0.1:{free_port()}/v1/chat/completions", timeout=2)
        self.assertIsInstance(ctx.exception.reason, ConnectionRefusedError)

    # The server may already have the request, so a crash at stage "send", not
    # "unreachable". Needs a raw socket (an HTTP server always reads the request
    # first): accept, reset at once; a large body keeps the client sending.
    def test_reset_while_sending_is_a_crash_not_unreachable(self):
        srv = socket.socket()
        srv.bind(("127.0.0.1", 0))
        srv.listen(1)

        def accept_and_reset():
            conn, _ = srv.accept()
            conn.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack("ii", 1, 0))  # close = RST
            conn.close()
        threading.Thread(target=accept_and_reset, daemon=True).start()
        try:
            r = call_model("x" * 20_000_000, url=f"http://127.0.0.1:{srv.getsockname()[1]}/v1/chat/completions")
        finally:
            srv.close()
        self.assertEqual(r["crash"]["stage"], "send")
        self.assertNotIn("response", r)


class TestServerCheck(unittest.TestCase):

    GOOD_HEALTH = {"loaded_model": MODEL, "apc_enabled": False}
    FROZEN_ARGS = "/x/.venv/bin/python3.13 /x/.venv/bin/" + server_command()

    def test_frozen_command_passes(self):
        self.assertEqual(check_server({"args": self.FROZEN_ARGS, "health": self.GOOD_HEALTH}), [])

    def test_every_deviation_caught(self):
        a, h = self.FROZEN_ARGS, self.GOOD_HEALTH
        deviations = {
            "wrong kv-bits": (a.replace("--kv-bits 8", "--kv-bits 4"), h),
            "kv-bits written with =": (a.replace("--kv-bits 8", "--kv-bits=8"), h),
            "missing max-num-seqs": (a.replace(" --max-num-seqs 2", ""), h),
            "extra flag at the end": (a + " --draft-model x", h),
            "extra flag in the middle": (a.replace(" --kv-bits", " --draft-model x --kv-bits"), h),
            "flags reordered": ("/x/python3.13 /x/mlx_vlm.server --port 8080 --model " + MODEL
                                + " --kv-bits 8 --prefill-step-size 512 --max-num-seqs 2", h),
            "other model, command and health": (a.replace(MODEL, "other/model"), {**h, "loaded_model": "other/model"}),
            # command right, but /health shows another model: only the health check can see this
            "other model, health only": (a, {**h, "loaded_model": "other/model"}),
            "prefix caching on": (a, {**h, "apc_enabled": True}),
        }
        for name, (args, health) in deviations.items():
            with self.subTest(name):
                self.assertTrue(check_server({"args": args, "health": health}))

    def test_nothing_listening_says_so(self):
        with self.assertRaises(RuntimeError) as ctx:
            observe_server(free_port())
        self.assertIn("no mlx_vlm server listening", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
