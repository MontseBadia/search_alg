# Storage: writing results and the attempt log.
#
# Tests: tests/test_storage.py

import datetime
import json
import os
import tempfile


# Write `data` to `path` complete or not at all, never overwriting, never
# discarding. Hidden temp file in the same folder, fsync (on disk before the
# name appears), then os.link: atomic, and fails if the name exists
# (os.replace would overwrite). Name taken -> _dup1, _dup2... Temp removed
# whatever happens. JSON serialised first: a failure there leaves no file.
# Returns the path actually written.
def save_new(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    blob = json.dumps(data, indent=1).encode()

    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".tmp-")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(blob)
            f.flush()
            os.fsync(f.fileno())
        for n in range(1000):
            target = path if n == 0 else f"{path[:-len('.json')]}_dup{n}.json"
            try:
                os.link(tmp, target)
                return target
            except FileExistsError:
                continue
        raise RuntimeError(f"no free name for {path}")
    finally:
        os.unlink(tmp)


# Where a crash record goes: beside the result path, never on it. Resume skips
# existing result files, so the call gets rerun on the next pass.
def crash_path(path):
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    return path[:-len(".json")] + f"_crash-{stamp}.json"


# Attempt log: attempts.jsonl next to the results, one line per event, only
# appended. "start" before every call, "end" after with the outcome. A start
# with no end = the Python process itself died. Also the proof that each
# scored result is the first completed attempt, not a rerun until it looked good.
# One write per line, append mode: two lanes can't interleave lines.
# A crash mid-append can leave a cut last line: readers (the report) must
# skip a line that doesn't parse instead of failing.
def log_attempt(result_path, record):
    line = json.dumps(record) + "\n"
    with open(os.path.join(os.path.dirname(result_path), "attempts.jsonl"), "a") as f:
        f.write(line)
