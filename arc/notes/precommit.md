
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

- model:
- samples per task:
- temperature:
- variants: text grid / image grid / rule-in-words-first
- scoring: exact match on the test output grid, any of k samples? majority?

### Predictions

Score I expect, per variant:

Score that would surprise me (low and high):

Which variant I think wins, and why:

Will the model do better on the tasks I found easy? (check against hand_solving_log.md)

### What counts as what

Decide the boundary now, otherwise I'll draw it wherever the transcript makes it convenient.

- solved: output grid matches exactly
- got the rule, failed execution: the stated rule would produce the right grid if applied correctly.
  Who checks this? me by hand, or run the stated rule?
- partial rule: 
- wrong rule: 
- no rule / format failure: 

Provisional failure tags (expect to change these after reading transcripts, log the change):

- miscounted / wrong grid size
- wrong object segmentation
- right transform, wrong color
- overfit to one train pair
- underdetermined rule: train pairs allow 2+ rules, model picked one that fails the test
- constant from examples: rule needs a value only learnable across pairs (a color, a cycle, a size), model invents or misses it
- simpler rule: model finds an easier rule that fits most pairs but not all
- off-by-one stop: right transform, wrong stopping point (touching vs overlapping)
- noisy task, invented explanation: task has unexplained anomalies, model makes up a rule to cover them
- right grid, wrong stated rule: output correct but the stated rule wouldn't produce it
- 

---

### Changes after seeing results
