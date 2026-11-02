
## Pre-commitment

Date: 13 October, 2026
Frozen: 20 October, 2026 (setup, predictions, outcomes), before any scored run

### Tasks

I pick 30 tasks randomly. They are taken from training set but only out of the 233 that are not in ARC-AGI-1, since frontier models have most probably trained on the ARC-AGI-1 ones. Using a fixed seed.

Not from evaluation/: it stays unseen, Solver v1 is scored on it in Week 5.

Caveats:
- the 233 are public since March 2025, the model may still have seen them
- difficulty not calibrated, only evaluation/ has the 66% human score

If the model solves more than 25/30: add 10 more from the remaining 203 minus the 3 pilot tasks (seed 1, pick_fallback in pick_tasks.py), log it under Changes.

- source: pick_tasks.py
- seed: 0
- list:

  18447a8d 
  25c199f5 
  305b1341
  320afe60 
  458e3a53
  5034a0b5
  522fdd07
  5623160b 
  5a719d11
  68bc2e87
  753ea09b
  7d7772cc
  7ec998c9
  8dab14c2
  8fff9e47
  963c33f8
  9720b24f
  985ae207
  a09f6c25
  a6953f00
  aaef0977
  bd5af378
  d749d46f
  d753a70b
  db7260a4
  df9fd884
  e729b7be
  e84fef15
  ecb67b6d
  fbf15a0b


### Setup

- model: mlx-community/Qwen3.8-27B-4bit (Qwen/Qwen3.8-27B, dense, 4-bit MLX), open weights, thinking model with vision, revision 10c35caafbb80f7dc6a7a432cdd11af10a6d4818
- hardware: M4 Pro, 24 GB unified memory, local
- runtime: mlx-vlm 0.7.8 in arc/.venv, server started with harness.server_command():
  mlx_vlm.server --model mlx-community/Qwen3.8-27B-4bit --port 8080 --kv-bits 8 --prefill-step-size 512 --max-num-seqs 2
  same server settings for the whole run
- kv-bits 8: needed for memory (cache compressed 16 -> 8 bit), small quality risk, kept for every call
- thinking: on, reasoning_effort medium, thinking_budget 16000 (server forces </think> at 16000 thinking tokens, the model then answers with what it has), max_tokens 22000
- forced stops: answers after a forced stop are scored like any other, flagged maybe_forced in the summary
- no answer by max_tokens, or a server error: format failure, not retried
- sampling: temperature 1.0, top_p 0.95, top_k 20 (model card values for thinking mode)
- samples per task: 3 (pilot ~20-23 min per call, under the 30 min rule)
- variants: text grid / rule-in-words-first now. Image grid later as a separate block (option B), with its own addendum here before it runs
- prompt: v1, hash 79d1a33708c3, one fixed template per variant, not edited during the run
- run order: by sample. Sample 1 of both variants for all 30 tasks, then sample 2, then sample 3
- concurrency: 2 calls at once only if their combined context (prompt + 16450) stays under ~45000 tokens, 753ea09b runs alone
- results: one file per call, runs/main/<task>_<variant>_s<k>.json, never overwritten
- scoring: exact match on every test output (tasks with 2 test inputs need both).
  Main number: per-sample accuracy (correct samples / all samples).
  Human comparison: pass@2 (first 2 samples, ARC rule), against my 29/30
- pilot: 3 tasks from the remaining 203 (not my 30), only to fix settings, not scored

### Pilot record (settings above come from here, not scored)

- f3e14006 xhigh, max 12000, no budget (command line, not server): thinking cut, no answer, 14 min, peak 17.65 GB
- f3e14006 medium, max 30000, no budget: thinking cut, no answer, 40 min, peak 17.75 GB
- afe3afe9 thinking off, max 8000: reasoning moved into the answer, cut, no grid, 11 min
- afe3afe9 medium, budget 16000: forced stop, answer given, 22.6 min, peak 17.86 GB
- 33067df9 medium, budget 16000, batched (2 at once): natural finish at 11841 tokens, 20 min, peak 18.35 GB
- f3e14006 medium, budget 16000: forced stop, answers to both tests, 22.7 min (added after freeze, pilot only)
- batching: ~10.4 tok/s per call x 2 vs 12.9 alone -> ~1.6x throughput

### Predictions

Score I expect, per variant, considering it's not a frontier model:
- 15/30 text grids pass@2
- 15/30 images pass@2
- 20/30 rule-first pass@2

Score that would surprise me (low and high):
- so bad: < 5/30
- so well: > 25/30
in any variant

Which variant I think wins, and why:
Rule-first because telling the rule at start will minimise chances of getting the wrong rule.

Will the model do better on the tasks I found easy?
Model's pass@2 on my difficulty 1-2 tasks (15) and on my 4-5 tasks (8) within 20 points of each other.
Hand solving log was made thinking on frontier model, now I am making these predictions thinking of strong open source model.

### What counts as what

Decide the boundary now, otherwise I'll draw it wherever the transcript makes it convenient.

Every sample gets one outcome, first that applies, in this order:
1. format failure: no parseable grid, hit max tokens, or server error
2. solved: exact match on all test outputs
3. perception failure: misreads the input (grid size, colors, object count) before any rule
4. got rule, failed execution: rule matches my final rule, grid wrong
5. partial rule: has some parts of my final rule, misses at least one
6. underdetermined: rule fits all train pairs but isn't the intended one
7. wrong rule: contradicts a train pair or misses the main idea
8. unresolved: can't tell from the transcript
Plus any number of failure tags (below).

Judged against the final rule in hand_solving_log.md.
Text/image variants: rule taken from the thinking. Rule-first: the stated rule.
Rule outcome decided before I see the score.

Provisional failure tags (expect to change these after reading transcripts, log the change):

- miscounted / wrong grid size
- wrong object segmentation
- right transform, wrong color
- overfit to one train pair
- constant from examples: rule needs a value only learnable across pairs (a color, a cycle, a size), model invents or misses it
- simpler rule: model finds an easier rule that fits most pairs but not all
- off-by-one stop: right transform, wrong stopping point (touching vs overlapping)
- noisy task, invented explanation: task has unexplained anomalies, model makes up a rule to cover them
- right grid, wrong stated rule: output correct but the stated rule wouldn't produce it

### Addendum, 26 October 2026, before any scored run

Pilot answers were 0/3, so accuracy could be near zero. Without other
measures the variants couldn't be compared (floor effect). Added before
any result on the 30 tasks exists.

Secondary measures (same for every variant):
- rule components captured: fraction of the parts of my final rule present
  in the model's rule. Components for each task written in
  notes/rule_components.md before reading any transcript
- outcome distribution: counts of the 8 outcome categories per variant
- shape correct: fraction of answers with the right output size
- cells correct: among right-size answers, fraction of matching cells.
  Diagnostic only, never credit

Variant comparison: by accuracy as planned. If accuracy is near zero
(pass@2 at most 2/30 in each variant), the comparison uses rule components
and the outcome distribution instead. My rule-first prediction then reads:
rule-first captures more rule components and has fewer "wrong rule"
outcomes than text.

Low-score rule: if pass@2 is at most 2/30 in both variants after sample 1,
- samples 2 and 3 still run as planned
- plus an exploratory frontier check: 10 of the 30 tasks (seed 2), text
  variant, 1 sample, on a frontier model through its API, same prompt v1.
  Model and settings fixed in their own addendum before it runs. Reported
  separately as exploratory, never mixed with the main results

Server crash without a complete response (connection dropped, reply cut
off or not valid JSON, or no answer within 4 hours): not the model's
outcome. Saved as a crash record beside the result (_crash-<time>.json),
rerun alone once memory allows, never scored.
Server errors that do return an answer stay format failures, as in Setup.

If a call ever has more than one completed result (_dup files, e.g. the
same call started twice by mistake), only the first completed attempt in
attempts.jsonl counts; the others are kept on record and never scored.

---

### Changes after seeing results

26 October 2026, sample 1 in progress

- 320afe60 (both variants): 500 from the server, Metal "Insufficient Memory",
  after ~30 min. Machine failure, not the model's, so treated as a crash
  (rerun alone), not a format failure as Setup would say. Decided before any
  output existed for this task (there is none).
  Other server errors stay format failures.
  scoring.score_result now does this: 500 with "Insufficient Memory" in the
  body -> "crash, rerun".
- cause: the two calls ran together but were over the concurrency limit
  (prompt + 16450 each, 48598 combined vs ~45000). The rule was right,
  I only listed 753ea09b. Exact counts with the model's tokenizer, these
  are over too and run alone: 753ea09b, 320afe60, a09f6c25, e84fef15,
  985ae207 (45352, barely). 8dab14c2 (44714) and 305b1341 (44452) are just
  under. 305b1341 finished fine.
- 18447a8d sample 1: saw the score (both solved) and both rules before
  judging. Rule components for that sample are not blind.
- 320afe60 text rerun alone: crash again, Metal "Insufficient Memory" after 15.2 s,
  still reading the prompt. Not scored, rerun. Likely cause: little free
  memory and the server's memory state after the earlier crash. Next rerun on a restarted server.
- crash files (the "saved" path in attempts.jsonl still says _s1.json):
  320afe60_text_s1@20261026-221312-580109 -> 320afe60_text_s1_crash.json
  320afe60_rule_first_s1@20261026-221440-057678 -> 320afe60_rule_first_s1_crash.json
  320afe60_text_s1@20261026-235045-917279 -> 320afe60_text_s1_crash_00.json

27 October 2026

- 963c33f8 (both variants), 14:14: Metal "Insufficient Memory" after ~22 min,
  paired, 39940 combined, under the limit. Crash, rerun alone. The limit alone
  doesn't prevent these; cause unknown (other apps?).
  963c33f8_text_s1@20261027-135131-835542 -> 963c33f8_text_s1_crash.json
  963c33f8_rule_first_s1@20261027-135212-905130 -> 963c33f8_rule_first_s1_crash.json

29 October 2026

- 985ae207 text s2: runner killed when VS Code restarted, before any
  reply. Start in attempts.jsonl with no end, no result file. Not scored, rerun.
  985ae207_text_s2@20261029-003025-901907
- 985ae207 text s2 rerun, alone, 09:38: Metal "Insufficient Memory" after
  ~23 min (~15000 tokens, decode slowed to 2.8 tok/s the minute before).
  Crash, rerun. Fine later.
  985ae207_text_s2@20261029-091545-977725 -> 985ae207_text_s2_crash.json

- Samples cut to 1. No seed in the request, so mlx-vlm uses seed 0: the token
  noise depends only on position, every request draws the same. Calls run
  alone repeat exactly (10 of 60 s2 calls identical to s1: 320afe60,
  753ea09b, 985ae207, a09f6c25, e84fef15, both variants). Paired calls only
  drift apart through batching float noise, after sharing the first 91-7019
  chars of thinking with s1 (33-65 for really different seeds). So s2 isn't
  an independent sample. Every s1 call is.
  Rerunning s2 and s3 alone with seeds costs ~2 days I don't have, so sample 1
  only. Decided after seeing the aggregate s1 solve rate (7/22, mid-sample 1),
  but for the bug and the time, not the results.
  - main number: per-sample accuracy on s1 (= pass@1)
  - pass@2 dropped. Human comparison is s1 pass@1 against my 29/30 (2
    attempts), and the pass@2 predictions (15/30, 20/30) get read against
    pass@1, which can only be lower
  - every other pass@2 threshold reads on s1 pass@1 too: more than 25/30
    (10 more tasks), at most 2/30 (variant comparison on components, low-score
    rule) and the difficulty prediction (within 20 points)
  - s2 kept on record, never scored as a sample. Maybe exploratory: does
    the drift after the shared start change the outcome
  - no per-task systematic vs noise check (needs independent samples)
  - any later run sends a seed per call from (task, variant, sample)
- Image variant dropped, for time. Never run, so text vs rule-first is the
  only comparison. The image prediction (15/30) stays above unscored.

2 November 2026, before scoring

- Tags added while tagging sample 1 blind, none of the provisional ones
  fit these:
  - fails own train pairs: stated rule contradicts a train pair
  - another rule fits: a different rule fits all train pairs
  - step left out: rule right so far, a step never stated or entailed
  - says one thing, does another: stated rule and its own application disagree
  - right idea dropped: thinking had the rule, the final rule doesn't
  Score-dependent tags (right transform wrong colour, right grid wrong
  stated rule) added after scoring.
- After scoring, from the answer grids (got rule, grid wrong rows):
  - extra rule broke grid: an extra rule part the convention left in "got rule" causes wrong cells
  - cell slips: a few cells wrong in an otherwise right grid
  "right grid, wrong stated rule" not used: the 6 solved-but-partial rows
  all give that grid from their stated rule
