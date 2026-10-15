
## Pre-commitment

Date: 13 October, 2026

### Tasks

I pick 30 tasks randomly. They are taken from training set but only out of the 233 that are not in ARC-AGI-1, since frontier models have most probably trained on the ARC-AGI-1 ones. Using a fixed seed.

Not from evaluation/: it stays unseen, Solver v1 is scored on it in Week 5.

Caveats:
- the 233 are public since March 2025, the model may still have seen them
- difficulty not calibrated, only evaluation/ has the 66% human score

If the model solves more than 25/30: add 10 more from the remaining 203 (seed 1), log it under Changes.

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
  fbf15a0b - done


### Setup

- model: mlx-community/Qwen3.8-27B-4bit (Qwen/Qwen3.8-27B, dense, 4-bit MLX), open weights, thinking model with vision
- hardware: M4 Pro, 24 GB unified memory, local
- runtime: mlx-vlm in its own venv (arc/.venv), served with mlx_vlm.server on localhost:8080, harness calls /v1/chat/completions over HTTP
- thinking: on. Full thinking text is logged (it's the transcript data)
- sampling: temperature 1.0, top_p 0.95, top_k 20 (model card values for thinking mode)
- thinking depth: TBD after smoke test, reasoning_effort if mlx-vlm exposes it, else --thinking-budget. Same value for every call
- max tokens: TBD after pilot. Hitting the cap counts as a failure ("ran out of tokens"), not retried
- KV cache compression (--kv-bits): only if the smoke test runs out of memory, recorded here if used
- samples per task: 3. If the pilot averages more than 30 min per call, drop to 2, decided before the full run
- variants: text grid / image grid (native vision, same model) / rule-in-words-first (text grid, rule stated before the grid)
- prompt: one fixed template per variant, saved with a version, not edited during the run
- scoring: exact match on every test output (tasks with 2 test inputs need both).
  Main number: per-sample accuracy (correct samples / all samples).
  Human comparison: pass@2 (first 2 samples, ARC rule), against my 29/30
- pilot: 3 tasks from the remaining 203 (not my 30), used only to measure speed, memory and thinking length and to fix the TBDs. Pilot results are not scored

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
Mdel's pass@2 on my difficulty 1-2 tasks (15) and on my 4-5 tasks (8) within 20 points of each other.
Hand solving log was made thinking on frontier model, now I am making these predictions thinking of strong open source model.

### What counts as what

Decide the boundary now, otherwise I'll draw it wherever the transcript makes it convenient.

Every sample gets one outcome, first that applies, in this order:
1. format failure: no parseable grid, or hit max tokens
2. solved: exact match on all test outputs
3. perception failure: misreads the input (grid size, colors, object count) before any rule
4. got rule, failed execution: rule matches my final rule, grid wrong
5. partial rule: has some parts of my final rule, misses at least one
6. underdetermined: rule fits all train pairs but isn't the intended one
7. wrong rule: contradicts a train pair or misses the main idea
8. unresolved: can't tell from the transcript
Plus any number of failure tags (below).

Judged by me, by hand, against the final rule in hand_solving_log.md.
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
- 

---

### Changes after seeing results
