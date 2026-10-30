# Viewer for blind judging: one transcript, answer grids hidden.
# Never loads the test outputs or calls the scorer. The thinking still has the
# model's draft grids, hiding those would also hide what the perception
# judgments need. Skip them, don't compare.
#
# python3 view.py 7ec998c9 text 1 | less

import json
import sys

from harness import run_path
from scoring import CODE_BLOCK
from server import summarize


def show(task_id, variant, sample):
    with open(run_path(task_id, variant, sample)) as f:
        result = json.load(f)
    s = summarize(result)
    print(f"== {task_id} {variant} s{sample}")
    print("  ".join(f"{k}={s[k]}" for k in ("outcome", "finish_reason", "completion_tokens", "maybe_forced")
                    if k in s))
    if s["outcome"] != "response":
        return
    msg = result["response"]["choices"][0]["message"]
    print("\n---- thinking ----\n")
    print(msg.get("reasoning_content") or "(none)")
    # Same blocks the parser reads, so whatever would be scored is what's hidden
    print("\n---- answer ----\n")
    print(CODE_BLOCK.sub("[grid hidden]\n", msg.get("content") or "(none)"))


if __name__ == "__main__":
    show(sys.argv[1], sys.argv[2], int(sys.argv[3]))
