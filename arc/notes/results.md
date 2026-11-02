## Results, Week 3, sample 1

Qwen3.8-27B 4-bit, 30 tasks x 2 variants, one sample. Setup in precommit.md, why in decisions.md.
Full report: runs/main/analysis_s1.txt (python3 analysis.py).

### Predictions vs results

| | solved | 95% CI | predicted | |
|---|---|---|---|---|
| text | 6/30 (20%) | 10-37% | 15/30 | over by 9 |
| rule-first | 11/30 (37%) | 22-54% | 20/30 | over by 9 |
| me, first attempt | 24/30 (80%) | 63-90% | | |
| me, 2 attempts (ARC rule) | 29/30 (97%) | 83-99% | | |

- fair comparison is my first attempt: model pass@1 vs my pass@1, 80% vs 20% and 37%. Mine needing a 2nd: 305b1341, 5034a0b5, 5623160b, 963c33f8, d753a70b, e84fef15 (3, so failed). Rule-first solved e84fef15 first try
- predictions were pass@2, read on pass@1 (precommit Changes). Both too high by the same amount
- rule-first wins, as predicted
- not near zero, so the comparison stays on accuracy. Nothing surprising (< 5 or > 25), no extra tasks
- difficulty 1-2 vs 4-5 within 20 points: no. text 4/15 vs 0/8 (27 points), rule-first 7/15 vs 2/8 (22). Only 8 hard tasks, one solve moves it ~12 points

### Variant comparison

- every task text solved, rule-first solved too. Rule-first only: 5a719d11, 7d7772cc, 9720b24f, db7260a4, e84fef15
- 5 vs 0 discordant, McNemar exact p = 0.031 one-sided, 0.0625 two-sided. Suggestive, one sample
  - McNemar: paired test, only tasks where the variants disagree count (here 5, all rule-first). Equal prompts = each disagreement a coin flip, 5 heads in a row = 1/32
  - exact: that coin-flip probability computed directly, the usual chi-square approximation is off with this few
  - in short: likely real, but 5 tasks from one run could flip with noise
- components 0.56 vs 0.61, got rule 8 vs 10 (judged, before solved overrides it), "wrong" 4 in each. Of the 5 rule-first-only solves, 3 are text missing the rule (7d7772cc, 9720b24f, db7260a4), 2 text getting it and botching the grid (5a719d11, e84fef15). Helps on both, too few to say which more
- shape correct 25/29 vs 26/30, cells 0.87 vs 0.90 on right-size grids

Outcome distribution (final: format failure and solved from the score, the rest judged):

| outcome | text | rule-first |
|---|---|---|
| format failure | 1 | 0 |
| solved | 6 | 11 |
| perception | 0 | 0 |
| got rule, grid wrong | 4 | 3 |
| partial | 15 | 12 |
| underdetermined | 0 | 0 |
| wrong | 4 | 4 |
| unresolved | 0 | 0 |

- perception 0: none given. The two input misreads in text (522fdd07 rf reads 5x5 as 4x5, 8fff9e47 text reads 4x4 as 4x6) got the miscounted tag instead. Underdetermined 0: other rules that fit go in the note (rule_components, 28 Oct)

### Forced stops

| | solved |
|---|---|
| maybe_forced | 4/45 (9%) |
| not forced | 13/15 (87%) |

Strongest pattern in the data. Not causal: calls that don't converge are the ones hitting the budget, so forced mostly marks "lost". Whether the budget cut off a solution needs the thinking-token counts and a look at where the forced ones were going. maybe_forced overcounts (decisions, limitation 1).

### Rule judgments vs grids

Got rule, grid wrong (7):
- one row short: 5a719d11 text (29 vs 30), 985ae207 text (24 vs 25). Same as the pilot (two answers one row short). 985ae207 rule-first too, judged partial so not in the 7
- extra rule broke grid: 522fdd07 text (no shrinking at the border), 5623160b rule-first (0s as walls), d753a70b rule-first (clipped shapes shift up). The "all components + extra -> got rule" convention puts these under execution, they're closer to rule errors
- near misses: 5623160b rule-first also stops one cell short of the edge, e729b7be rule-first 5 cells slipped, e84fef15 text one erased cell missed
- 522fdd07 text also puts the 9x9 at the top-left, not centred on the 0 its rule names

Solved, judged partial (6):
- 7ec998c9 text, df9fd884 both: tagged "another rule fits", and that rule gives the right test answer too. Underdetermined in fact, partial only because of the outcome order
- 18447a8d rule-first, 7ec998c9 rule-first, db7260a4 rule-first: the missing part isn't needed on this test
- so components are stricter than the test. Not "right grid, wrong stated rule": the stated rule allows that grid

Nothing at all, both variants: 8dab14c2, 8fff9e47 (12x12 instead of 8x8 both times), 963c33f8 (the noisy one).
One format failure: 320afe60 text, ragged rows, not a cutoff.

### Failure taxonomy (tags, both variants)

- fails own train pairs 7
- miscounted / wrong grid size 5
- another rule fits 4
- step left out 3
- says one thing, does another 3
- extra rule broke grid 3
- off-by-one stop 2, constant from examples 2, cell slips 2
- simpler rule 1, right idea dropped 1, overfit to one train pair 1

Most failures are in the rule, not the execution: 35 rows end partial or wrong, 7 got the rule and missed the grid, and in 3 of those an extra rule broke it, so only 4 are pure execution.
Biggest single group: rules that fail their own train pairs, and that's a floor, only rows checked in the re-review got it. The model states a rule it could have checked against the examples.

### Task properties (exploratory)

30 tasks, many comparisons, so leads, not findings. Solved counts per variant.

| property | yes: text / rf | no: text / rf |
|---|---|---|
| I revised my rule hand-solving (5 tasks) | 0/5, 1/5 | 6/25, 10/25 |
| prompt over median (2908 tokens) | 1/15, 3/15 | 5/15, 8/15 |
| more than 4 ops | 1/6, 3/6 | 5/24, 8/24 |

- revised: what tripped me up trips the model too (rf only got e84fef15)
- prompt size: solved ones go up to 7001 tokens, failed ones down to 753, so overlap. Likely mixed up with grid size and forced stops
- number of ops: nothing

Ops (hand-solving log), 3+ tasks only, solved text / rf, mean components:

| op | tasks | solved | components |
|---|---|---|---|
| crop | 4 | 3, 3 | 0.88 |
| split_grid | 6 | 2, 4 | 0.89 |
| filter_by_color | 4 | 2, 2 | 0.72 |
| translate | 4 | 2, 2 | 0.66 |
| draw_line | 3 | 1, 2 | 0.68 |
| stack_object | 3 | 1, 2 | 0.62 |
| find_objects | 22 | 4, 7 | 0.56 |
| move_to_edge | 6 | 1, 3 | 0.56 |
| fill | 3 | 0, 1 | 0.69 |
| recolor | 6 | 0, 2 | 0.60 |
| read_legend | 5 | 0, 1 | 0.54 |
| erase | 4 | 0, 1 | 0.51 |

- easy for the model: cutting the grid up (crop, split_grid)
- hard: read_legend, recolor, erase, fill. Rules where a colour or a part depends on something else in the grid (a key, a property)
- 34 of 46 ops are in 1-2 tasks only, can't say anything per op. The 3 with nothing in both variants have their own ops: 8dab14c2 (edge bumps/notches, mirror), 8fff9e47 (split_blocks, draw_frame), 963c33f8 (drop_through)
- ops overlap (fbf15a0b has read_legend, split_grid, crop, erase), so these aren't independent
- for Week 5: the DSL earns its keep where the model fails, so read_legend, conditional recolor and fill matter more than crop/split

### Open

- thinking-token counts: how many of the 45 were really forced
- the one-row-short answers: long grids, the model likely loses a row writing them out. A check against the input size would catch it when output = input size, as in both tasks (Week 5 solver, or a verify step)
- s2 drift as exploratory, maybe

Limitations: decisions.md, Accepted limitations.
