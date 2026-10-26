# Prompts: task loading and the frozen prompt templates.
#
# The prompt is part of the pre-commitment: fixed per variant, versioned,
# never edited during a run. Change it -> bump PROMPT_VERSION. prompt_hash()
# catches the case where I forget. Its value is in precommit (79d1a33708c3).
#
# Tests: tests/test_prompts.py

import hashlib
import inspect
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
TRAINING = os.path.join(HERE, "data", "data", "training")

PROMPT_VERSION = "v1"

VARIANTS = ("text", "rule_first")  # "image" comes later, needs rendering

INTRO = (
    "Solve this ARC puzzle. Each example shows an input grid and its output grid. "
    "Grids are rows of digits 0-9, each digit is a color. "
    "Find the rule that turns every example input into its output, "
    "then apply it to the test input."
)

ANSWER_ONE = (
    "Give the output grid inside a ``` block, one row per line, "
    "digits separated by spaces, same format as above."
)

ANSWER_MANY = (
    "Give one output grid per test input, in order, each inside its own ``` block, "
    "one row per line, digits separated by spaces, same format as above."
)

RULE_FIRST = (
    "Before the grid, state the rule in one or two sentences "
    "on a line starting with 'Rule:'."
)


def load_task(task_id):
    with open(os.path.join(TRAINING, task_id + ".json")) as f:
        return json.load(f)


# Spaces between digits: without them the tokenizer can merge "005" into one
# token and the model stops seeing single cells.
def grid_to_text(grid):
    return "\n".join(" ".join(str(c) for c in row) for row in grid)


# Only train pairs and test INPUTS go in. Test outputs stay with the scorer.
def build_prompt(task, variant):
    if variant not in VARIANTS:
        raise ValueError(f"unknown variant {variant!r}")
    parts = [INTRO, ""]
    for i, pair in enumerate(task["train"], 1):
        parts += [f"Example {i}", "Input:", grid_to_text(pair["input"]),
                  "Output:", grid_to_text(pair["output"]), ""]
    tests = task["test"]
    if len(tests) == 1:
        parts += ["Test input:", grid_to_text(tests[0]["input"]), ""]
    else:
        for i, pair in enumerate(tests, 1):
            parts += [f"Test input {i}:", grid_to_text(pair["input"]), ""]
    if variant == "rule_first":
        parts.append(RULE_FIRST)
    parts.append(ANSWER_ONE if len(tests) == 1 else ANSWER_MANY)
    return "\n".join(parts)


# Hash of everything that shapes the prompt: templates + the code that
# assembles them. Same hash = same prompt for the same task.
def prompt_hash():
    parts = [INTRO, ANSWER_ONE, ANSWER_MANY, RULE_FIRST,
             inspect.getsource(grid_to_text), inspect.getsource(build_prompt)]
    return hashlib.sha256("\n".join(parts).encode()).hexdigest()[:12]


# getsource reads the file from disk, so hash once at import: that's the code
# actually running. Editing prompts.py during a long run can't change it.
PROMPT_HASH = prompt_hash()


def text_sha(text):
    return hashlib.sha256(text.encode()).hexdigest()[:12]
