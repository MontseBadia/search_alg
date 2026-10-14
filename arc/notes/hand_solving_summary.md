## Hand-solving summary (30 tasks)

From hand_solving_log.md. Counts by script, tags from reviews.

### Me

- solved 29/30 by ARC rules (max 2 attempts). e84fef15 took 3 -> fail
- ~81 min total, median 2 min. Long ones: e84fef15 15, 963c33f8 10, 5a719d11 6, 8fff9e47 5
- revised rule in 5: 5034a0b5, 5623160b, 963c33f8, d753a70b, e84fef15. Every revision cost an attempt, every first-try solve had no revision
- difficulty: 1 x6, 2 x9, 3 x7, 4 x6, 5 x2

### My guesses for the model

- 19 yes / 11 no
- no's cluster on legends, overlaps, topology, output size
- yes on 3 tasks I rated 4-5 (5034a0b5, 5623160b, e84fef15): expected the model to find easy what I found hard

### Ops

50 names, 33 used only once.

| in 2+ tasks | count |
|---|---|
| find_objects | 22 |
| split_grid, move_to_edge, recolor | 6 |
| read_legend | 5 |
| filter_by_color, translate, crop, erase | 4 |
| stack_object, fill, draw_line | 3 |
| bounding_box, has_open_hole, shrink_from_center, expand_from_center, find_edge_notches | 2 |

Week 5: some of the tail will merge (drop_through and stack_object are both gravity, different stop). find_objects needs a connectivity param, ecb67b6d needs 8-connected.

### Task properties

| property | tasks |
|---|---|
| legend / key inside the grid | 305b1341, 5034a0b5, 7d7772cc, 8fff9e47, fbf15a0b |
| constant only learnable across pairs | aaef0977, bd5af378, d749d46f, d753a70b |
| underdetermined | 522fdd07, 7ec998c9, a6953f00 (df9fd884 maybe) |
| noisy / unresolved | 963c33f8 |
| topology (enclosed vs open) | 320afe60, db7260a4 |
| output built from scratch / resized | 8fff9e47, d749d46f, 68bc2e87, 458e3a53, a6953f00, fbf15a0b |

### My own process

- right grid, rule stated wrong or incomplete: 320afe60, 985ae207, db7260a4, maybe a09f6c25. Stated rules are noisy evidence for humans too, keep that in mind when judging the model's rule-in-words variant
- one execution slip: wrong grid size in 8fff9e47 (one of the pre-committed tags)
