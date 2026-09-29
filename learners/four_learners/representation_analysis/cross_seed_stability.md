# Cross-Seed Stability Analysis

## Goal

The goal of this experiment was to determine whether the representational effects observed in seed 7 were:

```text
properties of the training condition
```

or merely:

```text
accidents of one initialization
```

Earlier experiments suggested that, after adding the two discriminating examples, the network:

- becomes more sensitive to `blue` and `large`,
- suppresses sensitivity to `rounded` and `striped`,
- represents `blue AND large` more cleanly,
- aligns the target direction with the output readout,
- develops a strongly target-aligned hidden neuron,
- and uses that neuron causally.

However, a single seed cannot tell us whether those effects are stable.

The cross-seed experiment therefore asks:

> Does the same representational transition appear across many independently initialized networks?

---

# Experimental Setup

I trained two conditions across:

```text
100 random seeds
```

## 6-example condition

The original training set:

```text
6 examples
```

This condition is underdetermined and does not uniquely identify the true target function.

## 8-example condition

The same training set plus the two discriminating counterexamples:

```text
(0, 1, 1, 0) -> False
(1, 0, 1, 0) -> False
```

This condition identifies the intended target:

```text
blue AND large
```

For every seed, I measured:

```text
full-world behavioral accuracy
target-concept leave-one-out probe accuracy
probe/output directional alignment
relevant feature sensitivity
nuisance feature sensitivity
relevant/nuisance sensitivity ratio
```

I also identified the **most target-aligned hidden neuron** in each seed and measured:

```text
class separation
output-weight alignment
mean-ablation effects
opposite-class patching
same-class patching
```

Importantly, I did not compare raw neuron indices across seeds.

Hidden neurons are permutation-symmetric, so:

```text
neuron 0 in seed A
```

does not necessarily correspond to:

```text
neuron 0 in seed B
```

Instead, the best neuron was selected functionally by:

```text
| mean activation on positives
- mean activation on negatives |
```

---

# Part 1: Behavioral Stability

## Results

### 6-example condition

```text
true function: 0/100
```

### 8-example condition

```text
true function: 100/100
```

---

## Interpretation

The behavioral transition is completely stable across initialization.

With 6 examples:

```text
0 / 100
```

networks recover the exact target function over all 16 objects.

With the two discriminating examples added:

```text
100 / 100
```

networks recover the target function.

So the difference between the two conditions is not seed-specific.

The training evidence reliably changes which function the network learns.

---

# Part 2: Target-Concept Decodability

## Leave-One-Out Probe Results

### 6-example condition

```text
mean   = 14.02 / 16
median = 14.00
std    = 0.80

min    = 13
q1     = 13
q3     = 15
max    = 16
```

### 8-example condition

```text
mean   = 16.00 / 16
median = 16.00
std    = 0.00

min    = 16
q1     = 16
q3     = 16
max    = 16
```

---

## Interpretation

The target concept is already substantially decodable in the wrong-function networks.

So the failure of the 6-example networks is not simply:

```text
the hidden layer contains no information about blue AND large
```

Instead, target-related structure is already present.

However, after the discriminating examples are added:

```text
16 / 16
```

leave-one-out performance appears in every seed.

That means the target concept becomes a perfectly regular linear structure in hidden space across all 100 networks.

The transition is therefore:

```text
partially organized target information
→
universally clean target geometry
```

---

# Part 3: Probe / Output Alignment

The target probe identifies a direction in hidden space that separates:

```text
blue AND large = True
```

from:

```text
blue AND large = False
```

I compared that direction with the network's own output-weight direction using cosine similarity.

---

## Results

### 6-example condition

```text
mean   = 0.701
median = 0.681
std    = 0.125

min    = 0.451
q1     = 0.610
q3     = 0.802
max    = 0.996
```

### 8-example condition

```text
mean   = 0.995
median = 0.997
std    = 0.006

min    = 0.961
q1     = 0.993
q3     = 0.999
max    = 1.000
```

---

## Interpretation

This is one of the strongest cross-seed results.

The wrong networks already show moderate alignment:

```text
median cosine = 0.681
```

So the target direction often influences the output even before the network learns the correct function.

But in the correct networks:

```text
median cosine = 0.997
```

and even the worst seed has:

```text
cosine = 0.961
```

So the target direction becomes almost parallel to the network's actual decision direction in essentially every seed.

This strongly supports:

> the target representation becomes tightly coupled to the network's own readout when the correct function is learned.

---

# Part 4: Feature Sensitivity Reorganization

I grouped the features into:

```text
relevant:
blue
large

nuisance:
rounded
striped
```

and measured output-logit sensitivity.

---

## Relevant Feature Sensitivity

### 6-example condition

```text
mean   = 6.605
median = 6.642
std    = 0.279

min    = 5.440
q1     = 6.470
q3     = 6.814
max    = 7.057
```

### 8-example condition

```text
mean   = 7.901
median = 7.833
std    = 0.525

min    = 6.634
q1     = 7.488
q3     = 8.403
max    = 9.003
```

Relevant features become somewhat more influential.

---

## Nuisance Feature Sensitivity

### 6-example condition

```text
mean   = 3.108
median = 3.122
std    = 0.143

min    = 2.518
q1     = 3.019
q3     = 3.216
max    = 3.307
```

### 8-example condition

```text
mean   = 0.479
median = 0.469
std    = 0.098

min    = 0.317
q1     = 0.412
q3     = 0.514
max    = 0.853
```

This is a much larger change.

The correct networks sharply suppress the influence of irrelevant features.

---

# Relevant / Nuisance Sensitivity Ratio

## Results

### 6-example condition

```text
mean   = 2.126
median = 2.117
std    = 0.035

min    = 2.065
q1     = 2.104
q3     = 2.142
max    = 2.297
```

### 8-example condition

```text
mean   = 17.010
median = 17.284
std    = 2.654

min    = 8.368
q1     = 15.412
q3     = 19.048
max    = 21.380
```

---

## Interpretation

The distributions do not overlap.

Even the least task-selective correct network has:

```text
ratio = 8.368
```

while the most task-selective wrong network has:

```text
ratio = 2.297
```

So the increase is not caused by a few extreme seeds.

The representational transition reliably changes the network from:

```text
relevant features matter about twice as much as nuisance features
```

to:

```text
relevant features dominate nuisance features by roughly an order of magnitude
```

This is strong evidence of stable task-aligned reorganization.

---

# Part 5: Is the Same Neuron Responsible Across Seeds?

## Winning Neuron Index

### 6-example condition

```text
neuron 0: 36/100
neuron 1: 35/100
neuron 2: 29/100
```

### 8-example condition

```text
neuron 0: 36/100
neuron 1: 34/100
neuron 2: 30/100
```

---

## Interpretation

There is no privileged neuron index.

The target-aligned role moves between neurons almost uniformly.

So:

```text
"neuron 0 represents the target"
```

is not a stable cross-seed statement.

The correct invariant is:

```text
"there exists a strongly target-aligned neuron"
```

This illustrates an important mechanistic-interpretability principle:

> Functional roles can be stable even when individual neuron identities are not.

---

# Part 6: Best-Neuron Polarity

The best target-aligned neuron can represent the class in either direction.

## Results

### 6-example condition

```text
positive-high: 30/100
positive-low:  70/100
```

### 8-example condition

```text
positive-high: 22/100
positive-low:  78/100
```

---

## Interpretation

Most networks use a neuron whose activation is:

```text
low for positive examples
high for negative examples
```

but the polarity is not fixed.

This is why raw activation sign cannot be compared directly across networks.

The meaningful question is whether the neuron and output weight combine in the correct direction.

---

# Part 7: Best-Neuron Class Alignment

## Class-Aligned Output Sign

### 6-example condition

```text
100 / 100
```

### 8-example condition

```text
100 / 100
```

For every seed:

```text
output_weight * signed_class_gap > 0
```

---

## Interpretation

In every network, the most target-separated neuron is wired into the output with the correct polarity.

So target separation is not merely an unused geometric property.

The output layer consistently reads the selected neuron in a direction that supports the true class distinction.

---

# Part 8: Best-Neuron Class Separation

## Results

### 6-example condition

```text
mean   = 0.609
median = 0.609
std    = 0.024

min    = 0.559
q1     = 0.592
q3     = 0.626
max    = 0.659
```

### 8-example condition

```text
mean   = 0.795
median = 0.795
std    = 0.039

min    = 0.705
q1     = 0.765
q3     = 0.823
max    = 0.867
```

---

## Interpretation

Again, the distributions do not overlap.

The weakest best neuron in the correct networks has greater class separation than the strongest best neuron in the wrong networks.

So the emergence of a more target-specific unit is not a seed-7 anomaly.

It is a reliable property of the corrected training condition.

---

# Part 9: Output-Weight Strength and Class Effect

## Absolute Output Weight

### 6-example condition

```text
mean   = 7.916
median = 7.831
std    = 1.117
```

### 8-example condition

```text
mean   = 9.118
median = 8.977
std    = 1.311
```

The selected neuron is more strongly coupled to the output after correction.

---

## Combined Class Effect

The polarity-independent class effect was defined as:

```text
output_weight
*
signed_class_gap
```

### 6-example condition

```text
mean   = 4.838
median = 4.792
std    = 0.837
```

### 8-example condition

```text
mean   = 7.292
median = 7.116
std    = 1.388
```

---

## Interpretation

The target-aligned neuron becomes both:

```text
more strongly separated by class
```

and:

```text
more strongly coupled to the output
```

So its effective contribution to the decision increases.

---

# Part 10: Mean Ablation Across Seeds

For each seed, the best target-aligned neuron was replaced by its mean activation.

---

## 6-example condition

```text
total flips:
mean   = 0.57
median = 0
q3     = 1
max    = 6

positive flips:
mean   = 0.19
median = 0
q3     = 0
max    = 4

negative flips:
mean   = 0.38
median = 0
q3     = 1
max    = 2
```

---

## 8-example condition

```text
total flips:
mean   = 1.84
median = 1.5
q3     = 4
max    = 4

positive flips:
mean   = 1.84
median = 1.5
q3     = 4
max    = 4

negative flips:
mean   = 0
median = 0
max    = 0
```

---

## Interpretation

The correct networks show a clean asymmetry:

```text
ablation can destroy positive decisions
```

but:

```text
ablation never changes a negative decision
```

This generalizes the qualitative pattern seen in seed 7.

However, the effect is not universally maximal.

Because:

```text
q1 positive flips = 0
```

at least one quarter of correct networks have no Boolean label flips under mean ablation.

So the robust claim is not:

```text
one neuron is always necessary for the positive class
```

Instead:

> The best target-aligned neuron consistently contributes in the correct direction and often becomes important for maintaining positive decisions, but causal necessity is not always concentrated in a single unit.

Seed 7 was unusually strong on this measure.

---

# Part 11: Opposite-Class Activation Patching

## Negative Donor -> Positive Recipient

### 6-example condition

```text
mean   = 0.465
median = 0.521
std    = 0.167

min    = 0.104
q1     = 0.354
q3     = 0.583
max    = 0.833
```

### 8-example condition

```text
mean   = 0.858
median = 1.000
std    = 0.230

min    = 0.333
q1     = 0.786
q3     = 1.000
max    = 1.000
```

---

## Interpretation

This is a strong and stable causal transition.

For the median correct network:

```text
negative donor -> positive recipient
```

flips:

```text
100% of patches
```

And even the first quartile is:

```text
0.786
```

So replacing the selected neuron's positive-class activation with a negative-class value usually destroys the positive prediction.

This strongly supports the view that the selected neuron carries causally important class information.

---

# Part 12: Reverse Opposite-Class Patching

## Positive Donor -> Negative Recipient

### 6-example condition

```text
mean   = 0.487
median = 0.479
std    = 0.176
```

### 8-example condition

```text
mean   = 0.464
median = 0.542
std    = 0.357

min    = 0
max    = 1
```

---

## Interpretation

This effect does not become more stable after learning the correct function.

The variance is especially large in the 8-example condition.

Some networks allow the selected neuron to strongly push negative objects toward the positive class.

Other networks require additional hidden dimensions.

So the seed-7 result:

```text
47/48 reverse-direction flips
```

was unusually strong.

The cross-seed conclusion is therefore more limited:

> A single target-aligned neuron reliably carries strong causal evidence for maintaining positive decisions, but it does not universally function as a complete bidirectional class switch.

This suggests that the full decision remains partly distributed.

---

# Part 13: Same-Class Patching Controls

## Positive -> Positive

### 6-example condition

```text
0.000
```

for every seed.

### 8-example condition

```text
0.000
```

for every seed.

---

## Negative -> Negative

### 6-example condition

```text
mean   = 0.181
median = 0.182
std    = 0.045

min    = 0.068
q1     = 0.152
q3     = 0.197
max    = 0.311
```

### 8-example condition

```text
0.000
```

for every seed.

---

## Interpretation

This is one of the cleanest neuron-level changes.

In wrong networks, two objects that are both negative under the true concept can still carry sufficiently different activations in the selected neuron that swapping them changes the prediction.

In correct networks:

```text
negative -> negative patching
```

never changes the label.

So the selected neuron becomes much more internally consistent with respect to the true class.

The transition is:

```text
class-related but heterogeneous
→
class-specific and behaviorally interchangeable within class
```

---

# Main Findings

## 1. The representational transition is not seed-specific

The most important effects survive across all 100 random initializations.

The correct condition reliably produces:

```text
100/100 correct functions
16/16 target LOO in every seed
probe/output cosine >= 0.961
strong nuisance suppression
strong target/nuisance separation
```

So the seed-7 observations reflect a property of the training evidence, not an initialization accident.

---

## 2. Target information exists before correct behavior

The wrong networks already show:

```text
mean target LOO = 14.02 / 16
mean probe/output cosine = 0.701
```

So target information is present before the network learns the exact intended function.

The transition is therefore not:

```text
no abstraction
→
abstraction
```

It is better described as:

```text
partially organized target information
→
cleaner, more task-aligned target representation
```

---

## 3. Learning the correct function strongly suppresses nuisance structure

The largest sensitivity change is not simply an increase in relevant features.

It is the collapse of nuisance influence:

```text
3.108
→
0.479
```

This drives the relevant/nuisance ratio from:

```text
2.126
→
17.010
```

The network becomes much more selective about which input dimensions matter.

---

## 4. The distributed target direction is more stable than any individual neuron

The probe/output alignment becomes:

```text
median = 0.997
```

with very little variation across seeds.

By contrast, individual-neuron causal dominance varies substantially.

This supports the principle:

> The abstraction-level geometry is more invariant across parameterizations than the individual-neuron implementation.

---

## 5. A target-aligned neuron reliably emerges, but its identity does not

The winning index is approximately uniformly distributed across:

```text
neuron 0
neuron 1
neuron 2
```

So raw neuron identity is not meaningful across runs.

What is stable is the functional role:

```text
there exists a strongly target-separated neuron
whose output contribution is class-aligned
```

---

## 6. Single-neuron causality is real but not universally dominant

The selected neuron becomes:

```text
more separated by target class
more strongly coupled to the output
more stable under same-class replacement
more capable of destroying positive predictions when patched
```

But reverse-direction causal control varies considerably across seeds.

So the final decision is not universally compressed into one neuron.

---

# What Seed 7 Got Right

Seed 7 correctly revealed the qualitative structure:

```text
target-aligned neuron
strong causal involvement
class-specific activation pattern
cleaner organization in the correct network
```

Those effects generalize.

---

# What Seed 7 Overstated

Seed 7 showed an unusually strong single-neuron mechanism:

```text
mean ablation destroyed all four positives
opposite-class patching was almost perfectly bidirectional
```

Across 100 seeds, this is not universal.

The stable mechanism is better described as:

```text
distributed target representation
+
one strongly target-aligned causal contributor
```

rather than:

```text
one neuron completely implements the concept
```

---

# Caveats

1. The world contains only 16 possible objects.
2. The hidden layer contains only three neurons.
3. The target concept and final class are extensionally identical.
4. Selecting the most target-aligned neuron is a post hoc analysis and therefore asks whether such a neuron exists, not whether a pre-specified neuron has the property.
5. Mean ablation can create hidden states that are not naturally produced by the network.
6. Activation patching preserves real donor values for one neuron but may still create globally unnatural hidden-state combinations.
7. Strong target alignment does not establish a symbolic implementation of logical AND.
8. Cross-seed stability establishes robustness to initialization, not robustness to architecture, optimizer, training order, or dataset design.

---

# Final Interpretation

Across 100 random initializations, adding the two discriminating examples produces a highly repeatable internal transition.

The 6-example networks already contain substantial information about the intended target, but that information is:

```text
less regular
less aligned with the output
more entangled with nuisance features
```

The 8-example networks reorganize hidden space so that:

```text
the target becomes perfectly linearly generalizable
the target direction becomes almost parallel to the output direction
nuisance influence collapses
relevant influence dominates
a strongly target-aligned neuron reliably emerges
same-class neuron substitutions become behaviorally stable
```

The strongest invariant is not a particular neuron.

It is the **geometry of the representation**.

The correct networks converge on a target-aligned direction in hidden space even though the exact neuron-level implementation varies.

This supports the conclusion that learning the correct function is associated with a stable form of:

> **task-relevant representational reorganization**

The evidence now supports three increasingly strong claims:

```text
1. target information is present
2. target information becomes geometrically organized
3. target-aligned representations are causally used by the output
```

What the experiment still does not establish is:

```text
4. the network has formed a reusable symbolic/compositional AND abstraction
```

Because in this task:

```text
positive class
=
blue AND large
```

a representation of the final class and a representation of the logical conjunction are observationally indistinguishable.

The next scientific question therefore requires a different task design where:

```text
representing the final answer
```

and:

```text
forming a reusable compositional abstraction
```

can be separated.
