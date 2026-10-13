# Mechanistic Interpretability of a Tiny Modular-Addition Transformer

**Experiment report | 12 October 2026**  
**Task:** `(a + b) % 17`  
**Status:** Six experiments completed; mechanistic account remains partial.

## 1. Research question and setup

The goal was to distinguish memorization from generalization in a one-layer transformer trained on modular addition, test whether modular-answer geometry emerges, and identify which internal computations are causally necessary. A secondary hypothesis proposed an intermediate ordinary-addition representation before modular reduction. The study deliberately avoided importing mechanisms from prior modular-addition interpretability work.

### Architecture and split

- Sequence: `[a, b, =]`; `a,b ∈ {0,...,16}`.
- Token and positional embeddings, one self-attention head with output projection, residual connection, positionwise MLP and second residual connection, then a linear classifier reading the final `=` residual.
- Residual width: **32**.
- The 289 ordered input pairs were split by **unordered pairs** so `(a,b)` and `(b,a)` could not fall on opposite sides of the split.
- The analyzed split contained **200 training** and **89 held-out** ordered examples.
- Primary run **G**: seed 0, split 2, weight decay 1.0.
- Comparison run **W**: same seed/split, weight decay 0.1.
- A later timing replication covered **15 runs** at weight decay 1.0: five seeds × three splits.

Train accuracy at both 5k and 180k was 100% for G and W. G reached 95.5% held-out accuracy at 180k, while W reached 37.1%.

### Evidence standards

- **Behavior:** correct predictions and logits, not a claim about the internal algorithm.
- **Geometry:** information reflected in residual similarity, not necessarily information the classifier uses causally.
- **Causality:** intervention-dependent behavior, subject to intervention severity and pathway confounding.
- **Reusable abstraction:** stronger claim than any of the current experiments establishes.

## 2. Experiment 1: Wrap versus no-wrap behavior

**Hypothesis.** If the model learns ordinary addition before modular reduction, no-wrap test cases (`a+b < 17`) should improve before wrap cases (`a+b ≥ 17`).

**Measurement.** Held-out accuracy and mean correct-class logit margin in each group. The margin is `true-class logit − maximum wrong-class logit`.

| G step | No-wrap acc | Wrap acc | Accuracy gap (NW−W) | No-wrap margin | Wrap margin |
|---:|---:|---:|---:|---:|---:|
| 5k | 0.000 | 0.000 | +0.000 | -20.341 | -16.583 |
| 20k | 0.128 | 0.000 | +0.128 | -19.556 | -22.941 |
| 55k | 0.511 | 0.571 | -0.061 | -0.071 | -2.308 |
| 120k | 0.723 | 0.905 | -0.181 | +3.828 | +6.140 |
| 180k | 0.957 | 0.952 | +0.005 | +7.222 | +11.034 |
| 200k | 0.766 | 0.952 | -0.186 | +4.451 | +2.774 |

**Finding.** There is an early no-wrap advantage at 20k, but it disappears by 55k and reverses substantially at 120k and 200k. The predicted sustained no-wrap-first learning sequence is **not supported**. This does **not** rule out an internal ordinary-sum representation, since these categories also differ in operand and target distributions.

## 3. Experiment 2: Final-residual answer geometry

**Hypothesis.** As G generalizes, representations at `=` immediately before the classifier become more organized by modular answer, especially across train/held-out examples.

**Measurement.** For residuals `h_i`, compute the gap between mean same-answer and different-answer cosine similarity. Exclude comparisons where the two input examples share **any operand value**; exclude self-comparisons and duplicate unordered comparisons for train–train analysis. Two variants were evaluated:

1. **Uncentered:** cosine on original residual vectors.
2. **Centered:** subtract the **training-set mean for that checkpoint** from both train and test residuals before normalizing. Each checkpoint uses its own training mean.

The metric is `mean cosine(same answer) − mean cosine(different answer)`; it is descriptive geometry, not classifier accuracy.

### G: centering check

| Checkpoint/comparison | Uncentered gap | Centered gap |
|---|---:|---:|
| G 5k train–train | +0.316 | +0.368 |
| G 180k train–train | +0.237 | +0.537 |
| G 5k train–test | +0.045 | +0.067 |
| G 180k train–test | +0.217 | +0.502 |

For the uncentered comparisons, train–train included **1,034** same-answer and **14,671** different-answer pairs; train–test included **946** same-answer and **13,078** different-answer pairs. These pairwise comparisons are dependent because individual examples recur.

Uncentered underlying similarities:

| Comparison | Same-answer | Different-answer |
|---|---:|---:|
| G 5k train–train | +0.450 | +0.135 |
| G 5k train–test | +0.196 | +0.150 |
| G 180k train–train | +0.793 | +0.556 |
| G 180k train–test | +0.773 | +0.556 |

The high uncentered cosine values at 180k suggest that a common mean direction may contribute substantially; this motivated centering. Centering strengthened rather than eliminated the measured answer organization.

### G versus W, centered

| Run/checkpoint | Test acc | Train–train gap | Train–test gap | Alignment disparity (TT−TTest) |
|---|---:|---:|---:|---:|
| G 5k | 0.000 | +0.368 | +0.067 | +0.301 |
| G 180k | 0.955 | +0.537 | +0.502 | +0.035 |
| W 5k | 0.000 | +0.256 | -0.033 | +0.289 |
| W 180k | 0.371 | +0.586 | +0.382 | +0.204 |

**Finding.** At 5k, answer-dependent geometry is much stronger within training data than across the train/test divide. At 180k, G's cross-split geometry becomes nearly as strong as its training geometry. W also develops substantial geometry, and has even **higher train–train gap** than G at 180k despite much worse held-out accuracy. Thus **training geometry alone is insufficient** to explain generalization. Strong cross-split alignment correlates with better generalization in this comparison but does not prove a reusable computation or causal mechanism. Since the final residual is directly consumed by the classifier, these observations are particularly close to the trained decision readout.

## 4. Experiment 3: Raw-sum versus modular-answer geometry

**Hypothesis.** The memorizing model might geometrically favor identical ordinary sums; the generalizing model might align examples whose ordinary sums differ by 17 but share the same modular answer.

**Measurement.** Train-mean-centered train–test cosine similarity between examples sharing no operand, separated into:

- **Same raw sum:** `a+b = c+d`.
- **Same modular answer, different raw sums:** sums differ by 17.
- **Different modular answer:** baseline.

`Raw preference = cosine(same raw) − cosine(same modular answer, different raw)`.

| Run | Same raw (n=578) | Same mod, different raw (n=368) | Different mod (n=13,078) | Raw preference |
|---|---:|---:|---:|---:|
| G 5k | +0.076 | -0.102 | -0.061 | +0.177 |
| G 180k | +0.413 | +0.490 | -0.059 | -0.077 |
| W 5k | -0.020 | -0.227 | -0.068 | +0.206 |
| W 180k | +0.347 | +0.321 | -0.045 | +0.026 |

**Finding.** Both early models have a **relative** same-raw preference, but the low absolute cosine similarities do not support a strong, coherent ordinary-addition representation at 5k. By 180k, G shows a dramatic increase in alignment across raw sums differing by 17: **-0.102 → +0.490**; raw preference reverses sign. W shows a weaker but similar convergence toward modular equivalence. This supports the emergence of **modular-answer geometry** in the final residual, **not** the claim that the network executes a temporal algorithm `ordinary sum → modular reduction`. Same-raw and cross-wrap pair sets have different operand distributions, limiting causal interpretation.

## 5. Experiment 4: Timing of representational alignment

**Hypothesis.** Answer-dependent train–test residual geometry begins developing before strong held-out generalization.

**Measurement.** Centered train–test answer cosine gap across training checkpoints, compared with held-out accuracy. A threshold-based summary (`t50`) was computed by the experimenter, representing the first halfway crossing under the implemented method; exact threshold definition should be recorded if these numbers are reused for formal reporting.

### Detailed G trajectory

| Step | Test acc | Geometry gap |
|---:|---:|---:|
| 0 | 0.090 | +0.030 |
| 5k | 0.000 | +0.067 |
| 10k | 0.112 | +0.075 |
| 20k | 0.067 | +0.110 |
| 30k | 0.292 | +0.160 |
| 40k | 0.315 | +0.200 |
| 50k | 0.360 | +0.255 |
| 60k | 0.416 | +0.233 |
| 70k | 0.404 | +0.217 |
| 80k | 0.494 | +0.297 |
| 90k | 0.494 | +0.302 |
| 100k | 0.697 | +0.389 |
| 110k | 0.764 | +0.453 |
| 120k | 0.809 | +0.463 |
| 130k | 0.843 | +0.494 |
| 140k | 0.629 | +0.215 |
| 150k | 0.831 | +0.422 |
| 160k | 0.742 | +0.468 |
| 170k | 0.798 | +0.398 |
| 180k | 0.955 | +0.502 |
| 190k | 0.854 | +0.426 |
| 200k | 0.854 | +0.514 |

Reported for G: **t50 accuracy = 90k**, **t50 geometry = 55k**, a **35k-step geometry lead**.

### Detailed W trajectory

| Step | Test acc | Geometry gap |
|---:|---:|---:|
| 0 | 0.090 | +0.030 |
| 5k | 0.000 | -0.033 |
| 10k | 0.011 | -0.017 |
| 20k | 0.022 | +0.021 |
| 30k | 0.045 | +0.008 |
| 40k | 0.067 | +0.006 |
| 50k | 0.101 | +0.044 |
| 60k | 0.090 | +0.094 |
| 70k | 0.101 | +0.037 |
| 80k | 0.258 | +0.239 |
| 90k | 0.315 | +0.172 |
| 100k | 0.281 | +0.286 |
| 110k | 0.416 | +0.145 |
| 120k | 0.281 | +0.330 |
| 130k | 0.281 | +0.157 |
| 140k | 0.281 | +0.293 |
| 150k | 0.281 | +0.117 |
| 160k | 0.337 | +0.428 |
| 170k | 0.292 | +0.219 |
| 180k | 0.371 | +0.382 |
| 190k | 0.371 | +0.097 |
| 200k | 0.393 | +0.385 |

Reported for W: **t50 accuracy = 85k**, **t50 geometry = 85k**, **no lead**. W shows substantial, unstable geometry without comparable behavioral accuracy.

### Replication: 15 runs at weight decay 1.0

| Run | Final acc | t50 acc | t50 geometry | Lead (acc−geometry) |
|---|---:|---:|---:|---:|
| seed 0, split 0 | 0.795 | 125k | 90k | +35k |
| seed 0, split 1 | 0.674 | 130k | 120k | +10k |
| seed 0, split 2 | 0.854 | 90k | 55k | +35k |
| seed 1, split 0 | 0.534 | 30k | 30k | 0 |
| seed 1, split 1 | 0.430 | 20k | 15k | +5k |
| seed 1, split 2 | 0.674 | 15k | 15k | 0 |
| seed 2, split 0 | 0.716 | 25k | 25k | 0 |
| seed 2, split 1 | 0.779 | 35k | 15k | +20k |
| seed 2, split 2 | 0.315 | 120k | 105k | +15k |
| seed 3, split 0 | 0.614 | 40k | 25k | +15k |
| seed 3, split 1 | 0.430 | 45k | 40k | +5k |
| seed 3, split 2 | 0.596 | 30k | 15k | +15k |
| seed 4, split 0 | 0.364 | 130k | 90k | +40k |
| seed 4, split 1 | 0.767 | 65k | 60k | +5k |
| seed 4, split 2 | 0.708 | 60k | 40k | +20k |

**Aggregate:** Geometry first in **12/15**, accuracy first in **0/15**, tied in **3/15**. Median lead **15k** steps; mean lead approximately **14.7k** steps, range **0–40k**.

**Finding.** Under the current threshold definition, geometric alignment typically reaches its halfway point before accuracy. This is the clearest cross-run support for the **timing hypothesis**. But threshold crossings in fluctuating signals need not identify the formation time of an abstraction, and relative half-max thresholds can differ in substantive meaning across runs. G at 200k also has **higher** geometry than at 180k (+0.514 vs +0.502) despite **lower** accuracy (85.4% vs 95.5%), demonstrating that the gap alone does not determine classification success. A sustained-threshold robustness check was suggested but is **not reported as completed**.

## 6. Experiment 5: Attention patterns versus component updates

**Hypotheses.** (a) Attention routing changes relatively little; (b) MLP contribution changes substantially as representations evolve.

**Measurements.** Attention weights from `=` toward `[a,b,=]`; norm of attention and MLP updates at `=`; reported change summaries for patterns and activation updates. **Attention total variation and activation change scores are on different scales; they must not be numerically compared as if identical metrics.** The precise activation-change normalization was not supplied.

### Mean attention allocation

| Checkpoint | To a | To b | To = |
|---|---:|---:|---:|
| G 5k | 0.490 | 0.490 | 0.020 |
| G 180k | 0.498 | 0.498 | 0.004 |
| W 5k | 0.474 | 0.467 | 0.059 |
| W 180k | 0.496 | 0.496 | 0.009 |

### Mean update norm at `=`

| Checkpoint | Attention norm | MLP norm | MLP/attention |
|---|---:|---:|---:|
| G 5k | 6.4 | 27.6 | 4.3× |
| G 180k | 21.2 | 101.0 | 4.8× |
| W 5k | 14.3 | 36.9 | 2.6× |
| W 180k | 10.8 | 132.5 | 12.3× |

### Reported changes over training, 5k → 180k

| Run | Attention pattern (TV) | Attention update | MLP update | Final residual |
|---|---:|---:|---:|---:|
| G | 0.061 | 0.563 | 0.794 | 0.792 |
| W | 0.145 | 0.584 | 0.739 | 0.721 |

### Reported G vs W differences

| Step | Attention pattern (TV) | Attention update | MLP update | Final residual |
|---|---:|---:|---:|---:|
| 5k | 0.125 | 0.444 | 0.689 | 0.628 |
| 180k | 0.045 | 0.546 | 0.612 | 0.637 |

**Finding.** Attention allocation from `=` remains almost evenly split between operands and very low on `=` itself. Meanwhile, projected attention information and MLP contributions change substantially. The MLP has larger update norms than attention, but W has the **largest** MLP norm and weak generalization; magnitude alone is not an explanation of success. Stable **mean** attention patterns do not imply stable per-example routing or stable value/output projections. Evidence is consistent with the preregistered descriptive hypotheses, but does not prove MLP causal dominance.

## 7. Experiment 6: Causal component and pathway interventions

**Hypothesis.** Some internal computation in a generalizing model should be disproportionately important for held-out generalization rather than memorized training predictions.

**Conditions:**

- **Baseline:** unchanged network.
- **Zero attention:** zero the projected attention update (severe intervention).
- **No direct attention:** preserve the normal attention-enriched input to the MLP, but remove the attention update **only from the final residual's direct additive pathway**. The experimenter confirmed this exact meaning.
- **Zero MLP:** zero the MLP update.
- **Mean MLP:** replace the MLP update with its mean under the experiment's implementation.

**Measurements:** train/test accuracy, mean correct-class margins, and change from baseline.

### G at 180k

| Condition | Train acc | Test acc | Train margin | Test margin | Δ train acc | Δ test acc | Δ test margin |
|---|---:|---:|---:|---:|---:|---:|---:|
| Baseline | 1.000 | 0.955 | +13.15 | +9.02 | 0.000 | 0.000 | 0.00 |
| Zero attention | 0.065 | 0.045 | -7.52 | -8.51 | -0.935 | -0.910 | -17.53 |
| No direct attn | 1.000 | 0.933 | +10.55 | +7.51 | 0.000 | -0.022 | -1.51 |
| Zero MLP | 0.075 | 0.067 | -6.90 | -7.30 | -0.925 | -0.888 | -16.32 |
| Mean MLP | 0.105 | 0.045 | -13.33 | -14.71 | -0.895 | -0.910 | -23.73 |

### W at 180k

| Condition | Train acc | Test acc | Train margin | Test margin | Δ train acc | Δ test acc | Δ test margin |
|---|---:|---:|---:|---:|---:|---:|---:|
| Baseline | 1.000 | 0.371 | +13.67 | -7.45 | 0.000 | 0.000 | 0.00 |
| Zero attention | 0.045 | 0.090 | -5.61 | -6.36 | -0.955 | -0.281 | +1.10 |
| No direct attn | 1.000 | 0.416 | +13.40 | -6.98 | 0.000 | +0.045 | +0.48 |
| Zero MLP | 0.075 | 0.000 | -1.59 | -2.37 | -0.925 | -0.371 | +5.08 |
| Mean MLP | 0.075 | 0.022 | -7.53 | -10.03 | -0.925 | -0.348 | -2.58 |

**Finding.** Removing either the attention computation or MLP computation collapses G's train **and** test performance almost to chance (`1/17 ≈ 5.9%`). W also depends heavily on both for memorized training performance. The broad ablations therefore establish **component necessity for normal function**, but **not generalization-selective necessity**.

The **no-direct-attention** intervention is more diagnostic: G test accuracy changes only **95.5% → 93.3%**, preserving 100% train accuracy; W changes **37.1% → 41.6%**. Because the MLP still receives attention-enriched input, this is evidence that the direct additive attention-to-final-residual route is comparatively dispensable; the attention-to-MLP route remains available. It does **not** prove that the MLP independently implements modular addition. These pathway interventions are more specific than full component ablations, but remain subject to off-distribution concerns.

## 8. Preregistered hypothesis ledger

| Original hypothesis | Assessment | Critical evidence / limitation |
|---|---|---|
| No-wrap improves before wrap (behavioral addition-first prediction) | **Not supported as a sustained sequence** | Brief G 20k advantage, reversed by 55k and at 120k |
| Final residual develops answer-dependent organization on unseen examples | **Supported descriptively** | G centered train–test gap +0.067 → +0.502 |
| Train/test representational disparity shrinks | **Supported descriptively** | G alignment disparity +0.301 → +0.035; W +0.289 → +0.204 |
| Representation changes precede peak / substantial generalization | **Supported under t50 metric** | Geometry leads in 12/15 wd=1.0 runs, tied in 3 |
| Attention patterns change relatively little | **Supported descriptively for mean routing** | Near-50/50 allocation to operands at 5k and 180k |
| MLP contribution changes substantially | **Supported descriptively** | Large MLP norm and update-change values; stronger-than-attention conclusion depends on metric definition |
| Classifier alone cannot explain transition | **Not directly isolated** | Geometry measured before linear classifier but still classifier-facing; no separate readout test |
| A computation is selectively necessary for test generalization | **Not established** | Zero attention/MLP collapse both train and test; direct attention route mostly dispensable |
| Ordinary sum is computed before modular reduction | **Not established** | Raw preference at 5k and modular equivalence at 180k are compatible but cannot identify a computational sequence |
| Reusable abstraction exists beyond this task | **Not tested** | No transfer or recombination task; geometry is not proof of abstraction |

## 9. Unified mechanistic picture

The best-supported picture is **not** a fully recovered algorithm, but a sequence of representational and pathway observations:

1. **Memorization regime:** At 5k, both runs perfectly fit the training pairs and fail on held-out pairs. G has answer-dependent training geometry (centered gap +0.368) but minimal train–test alignment (+0.067). Raw-sum identity is relatively favored over modular equivalence in the final residual.
2. **Emergent alignment:** With training, centered answer-dependent geometry increasingly bridges seen and unseen pairs. In most of the 15 weight-decay-1.0 runs, its halfway threshold precedes the accuracy threshold. This temporal lead is a robust descriptive pattern under the implemented metric, not demonstrated causation.
3. **Generalizing regime:** G at 180k reaches 95.5% held-out accuracy; final-residual train–test geometry (+0.502) almost matches train–train geometry (+0.537). Examples with different ordinary sums but equal modular answers exhibit strong alignment (+0.490). These findings support modular-answer organization, not necessarily an explicit ordinary-sum intermediate.
4. **Routing versus content:** Attention from `=` routes about equally to both operands throughout, while attention and MLP update vectors undergo substantial changes. The routing pattern alone cannot explain G's success over W.
5. **Causal architecture:** Both attention and MLP processing are necessary for intact performance. Yet the *direct* attention addition to the final residual can be removed with little G accuracy loss if the MLP still receives the attention-enriched stream. This identifies a relatively dispensable output pathway, while leaving the essential indirect attention-to-MLP route intact.
6. **Incomplete sufficiency:** W can show strong answer-dependent geometry and large MLP updates without G-level accuracy. G's geometry can remain high even when accuracy declines (180k → 200k). Neither cosine gap nor update norm is sufficient to specify the learned solution.

**Most defensible claim:** During training, a tiny transformer transitions from train-specific answer-dependent final-residual geometry to much stronger train/test-aligned geometry organized by modular answer. That geometric transition tends to precede behavioral generalization under a relative-threshold measure. Attention routing changes relatively little, while the content of attention and MLP updates changes; causally, both components matter, but the direct attention-to-final-residual pathway is largely dispensable when attention's input to the MLP is preserved.

**What we cannot claim:** That the model first computes ordinary addition and then reduces modulo 17; that a particular component alone implements modular addition; that answer geometry causes generalization; or that the observed representations constitute a reusable abstraction outside this task.

## 10. Methodological limitations and next research directions

### Limitations

- **Final-residual readout confound:** High classifier accuracy implies successful linear decision regions at its direct input. Cosine clustering is not mathematically guaranteed by accuracy, but it is still close to the classifier-facing representation.
- **Cosine origin dependence:** Centered and uncentered results differ; both were retained. Training-set centering is appropriate for cross-split comparison within each checkpoint, but does not define a unique intrinsic geometry.
- **Dependent comparisons:** Pairwise similarities reuse examples and cannot be treated as independent samples for ordinary significance tests.
- **Pair-type confounding:** Same raw sum versus cross-wrap modular equivalence also changes operand distributions; raw preference is descriptive.
- **Timing metric sensitivity:** Halfway crossing depends on normalization, interpolation and transients. The 15 runs share seed and split factors; not 15 wholly independent designs. A sustained-crossing sensitivity analysis was proposed, not carried out.
- **Undefined activation-change metric:** The table of update changes was supplied without its exact distance/normalization formula. Pattern TV and update changes should not be compared directly in magnitude.
- **Ablation severity:** Zeroing whole components yields out-of-distribution inputs and floor effects. Train/test differences in baseline accuracy make raw drops hard to compare as selective generalization effects.

### Highest-value follow-ups (not part of the completed six experiments)

1. **Timing robustness:** Recompute t50 using a sustained threshold (e.g., threshold maintained for the next two measured checkpoints), documenting the exact definition, with seed/split-level summaries.
2. **More selective causal tests:** Patch or ablate a narrowly defined contribution, and compare its effect on train and held-out margins in a way that avoids full component collapse.
3. **Readout versus encoding:** With a strict held-out protocol, compare a frozen-residual linear readout with the original classifier, especially for W. A probe would establish decodability only.
4. **Abstraction/algorithm test:** Introduce tests distinguishing computation of a raw sum from mere modular-answer geometry, ideally at an intermediate stage or under controlled counterfactual interventions. The current final-residual-only study cannot settle that mechanism.

## 11. Concise abstract

We analyzed a one-layer, one-head transformer trained on modular addition modulo 17 across memorizing and generalizing checkpoints, comparing strongly generalizing G (weight decay 1.0) against weaker W (weight decay 0.1). The predicted sustained no-wrap-first behavioral sequence was not observed. In G, the centered final-residual train–test answer-similarity gap rose from 0.067 at 5k (0% test accuracy) to 0.502 at 180k (95.5% test accuracy), approaching its train–train gap of 0.537. Residual geometry increasingly aligned examples whose raw sums differed by 17, consistent with modular equivalence but not proof of an intermediate ordinary-addition algorithm. Across 15 weight-decay-1.0 runs, the geometry halfway threshold preceded the accuracy threshold in 12 and tied in three, with median lead 15k steps. Attention allocation from `=` remained approximately evenly split between operands, while attention and MLP updates changed substantially. Zeroing attention or MLP computation collapsed performance, but removing attention's direct final-residual contribution while preserving its input to the MLP barely affected G's accuracy (95.5% → 93.3%). Results support emergent, train/test-aligned modular-answer geometry and causal reliance on attention-to-MLP processing, while leaving the precise learned algorithm and its potential reuse unresolved.
