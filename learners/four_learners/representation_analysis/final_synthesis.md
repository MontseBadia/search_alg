# Final Unified Synthesis: Representation Formation in the Four-Learner Experiment

## Central Question

The neural-network part of this project asked a narrower question than:

```text
Did the network classify the objects correctly?
```

The real question was:

> **What changes inside the network when it moves from an underdetermined training set to evidence that uniquely supports the intended concept?**

The intended concept was:

```text
blue AND large
```

The network architecture was deliberately small:

```text
4 inputs
→ 3 sigmoid hidden neurons
→ 1 sigmoid output
```

Two training conditions were compared.

### 6-example condition

The original six examples are consistent with the intended concept, but they do not uniquely determine it.

Across 100 random seeds:

```text
0 / 100 networks recovered the exact target function
```

The networks fit the observed evidence but extrapolated incorrectly somewhere in the 16-object world.

### 8-example condition

Two discriminating counterexamples were added:

```text
(0, 1, 1, 0) -> False
(1, 0, 1, 0) -> False
```

Across 100 random seeds:

```text
100 / 100 networks recovered the exact target function
```

So the empirical transition is:

```text
same architecture
+
same optimizer
+
same training procedure
+
two additional discriminating examples

→

wrong extrapolation in every seed
becomes
correct extrapolation in every seed
```

The representation experiments asked what internal change accompanies that behavioral transition.

---

# 1. Behavioral Result

The first important distinction is:

```text
fitting the training data
≠
recovering the true function
```

The 6-example networks can fit the observed labels while still implementing the wrong function on unseen objects.

The 8-example networks match:

```text
blue AND large
```

on all 16 possible inputs.

Therefore:

```text
6 examples:
0/100 exact target recovery

8 examples:
100/100 exact target recovery
```

This behavioral transition gives us the two conditions whose internal representations we compare.

---

# 2. Representation Sensitivity

## Question

Which input features actually influence the hidden representation and output?

The four features were:

```text
relevant:
blue
large

nuisance:
rounded
striped
```

Feature sensitivity was measured by flipping one feature while holding the others fixed and observing:

```text
hidden-state change
output-logit change
```

---

## Seed-7 Result

In the wrong network:

```text
blue      output sensitivity ≈ 6.28
large     output sensitivity ≈ 6.36
rounded   output sensitivity ≈ 2.21
striped   output sensitivity ≈ 3.71
```

In the correct network:

```text
blue      output sensitivity ≈ 7.36
large     output sensitivity ≈ 7.43
rounded   output sensitivity ≈ 0.44
striped   output sensitivity ≈ 0.57
```

The main transition was not merely:

```text
relevant features become stronger
```

It was also:

```text
nuisance influence collapses
```

---

## Cross-Seed Result

Across 100 seeds:

```text
Relevant sensitivity
6.605 → 7.901

Nuisance sensitivity
3.108 → 0.479

Relevant / nuisance ratio
2.126 → 17.010
```

The ratio distributions do not overlap:

```text
6 examples:
min = 2.065
max = 2.297

8 examples:
min = 8.368
max = 21.380
```

So task alignment is not a seed-specific effect.

---

## Finding

Learning the correct function is associated with a strong change in what the network treats as relevant.

The correct networks become:

```text
more sensitive to task-relevant structure
and
much less sensitive to nuisance structure
```

This is evidence for **task-aligned representational reorganization**.

It is not yet evidence for a symbolic AND operation.

---

# 3. Linear Probing

## Question

What information is present in hidden space?

A linear probe was trained on frozen hidden activations to predict:

```text
blue
large
rounded
striped
blue AND large
```

The probe does not modify the original network.

It asks whether a concept can be recovered by a linear readout from the hidden representation.

---

## Full-Fit Probe

For `blue AND large`:

```text
wrong network:   16/16
correct network: 16/16
```

So even the wrong network contains a linearly separable representation of the target concept.

This immediately rules out the simple explanation:

```text
the wrong network fails because it lacks target information
```

It does not lack the information.

The important question becomes how that information is organized and used.

---

## Leave-One-Out Probe

Seed 7:

```text
wrong network:   14/16
correct network: 16/16
```

Across 100 seeds:

```text
6 examples:
mean   = 14.02
median = 14
range  = 13–16

8 examples:
16/16 in every seed
```

---

## Finding

The target concept is already present in the wrong networks, but its geometry is less regular.

The transition is:

```text
target information present
→
target information organized into a perfectly generalizable linear structure
```

This is a crucial distinction:

> **Information being present is not the same as an abstraction being cleanly formed.**

---

# 4. Probe Direction and Output Readout

## Question

Even if the target concept is decodable, does the network's own output layer use the same direction?

The target probe defines a direction in hidden space.

The network output layer also defines a direction:

```text
output_weights
```

Their cosine similarity measures alignment.

---

## Seed-7 Result

```text
wrong network:
cosine = 0.843

correct network:
cosine = 0.961
```

---

## Cross-Seed Result

```text
6 examples:
mean   = 0.701
median = 0.681
min    = 0.451
max    = 0.996

8 examples:
mean   = 0.995
median = 0.997
min    = 0.961
max    = 1.000
```

The correct networks almost universally make their decision along the same direction that linearly represents:

```text
blue AND large
```

---

## Finding

The target concept does not merely become decodable.

It becomes aligned with the network's own readout.

The transition is:

```text
target information exists
→
target information becomes the direction the network actually uses
```

This is stronger evidence than probing alone.

---

# 5. Neuron-Level Mean Ablation

## Question

Is any individual hidden neuron causally important for the target decision?

For each neuron, its activation was replaced by its mean activation across all 16 objects.

Then the original output layer was evaluated.

---

## Seed-7 Result

For the correct network, neuron 0 stood out:

```text
mean logit change = 3.355
label flips       = 4/16
```

The four flipped objects were exactly the four positive examples:

```text
blue = 1
large = 1
```

All changed:

```text
True → False
```

This suggested that neuron 0 was causally important for maintaining positive predictions.

---

## Cross-Seed Result

For the most target-aligned neuron in each correct network:

```text
mean positive ablation flips = 1.84
mean negative ablation flips = 0.00
```

But:

```text
q1 positive flips = 0
```

So the seed-7 effect was stronger than the typical network.

---

## Finding

The stable claim is not:

```text
one neuron is always necessary for the concept
```

The stable claim is:

> A strongly target-aligned neuron often becomes causally important for maintaining positive decisions, but causal necessity is not always concentrated in a single unit.

---

# 6. Opposite-Class Activation Patching

## Question

What happens if one neuron's activation is replaced with a real activation from an object in the opposite class?

This is stronger than mean ablation because the donor activation actually occurs in the network.

---

## Seed-7 Result

Correct network, neuron 0:

```text
negative donor → positive recipient:
48/48 flips

positive donor → negative recipient:
47/48 flips
```

This looked almost like a bidirectional class switch.

---

## Cross-Seed Result

For the best target-aligned neuron:

```text
Negative → Positive

6 examples:
mean   = 0.465
median = 0.521

8 examples:
mean   = 0.858
median = 1.000
```

So in the typical correct network, inserting a negative-class activation into a positive recipient destroys the positive decision almost every time.

But the reverse direction is much less stable:

```text
Positive → Negative

8 examples:
mean   = 0.464
median = 0.542
range  = 0–1
```

---

## Finding

Seed 7 overstated how completely one neuron controls the whole decision.

The robust conclusion is:

```text
one neuron often carries strong causal evidence
for maintaining the positive class
```

but:

```text
the full classifier is still partly distributed
```

---

# 7. Same-Class Patching Control

## Question

Are patching effects genuinely class-specific, or does changing a neuron simply destabilize the network?

The control patches:

```text
positive donor → positive recipient
negative donor → negative recipient
```

---

## Cross-Seed Result

Positive → Positive:

```text
0 flips in every seed
```

Negative → Negative:

```text
6 examples:
mean flip rate = 0.181

8 examples:
0 flips in every seed
```

---

## Finding

This is one of the cleanest neuron-level transitions.

In wrong networks:

```text
same true class
does not imply
behaviorally interchangeable neuron activation
```

In correct networks:

```text
same true class
→ selected-neuron activations become behaviorally interchangeable
```

So the selected neuron becomes much more internally consistent with the target class.

This supports a transition from:

```text
class-related but entangled representation
```

to:

```text
class-specific representation
```

---

# 8. Probe-Direction Intervention

## Question

If we move hidden states along the distributed target-concept direction, does the network's output move accordingly?

For a normalized probe direction `d`:

```text
h' = h + alpha * d
```

Because the output layer is linear in hidden space:

```text
z = w · h + b
```

the logit change is exactly:

```text
Δz = alpha * (w · d)
```

---

## Result

Seed 7:

```text
wrong network:
probe/output cosine = 0.843
dot product         = 8.484

correct network:
probe/output cosine = 0.961
dot product         = 11.316
```

Moving toward the concept direction raises the output logit.

Moving away lowers it.

---

## Interpretation

This experiment is not independent evidence of a new mechanism, because once:

```text
probe direction
```

and:

```text
output weights
```

are known, the logit shift follows algebraically.

Its value is different:

> It shows that the linearly decodable target direction is also the direction the network's output layer is increasingly aligned with.

This connects:

```text
representation geometry
```

with:

```text
causal readout
```

---

# 9. Cross-Seed Stability

The cross-seed experiment tested whether the entire story survived random initialization.

The answer was yes at the representation level.

---

## Behavioral Stability

```text
6 examples:
0/100 exact target recovery

8 examples:
100/100 exact target recovery
```

---

## Target Probe Stability

```text
6 examples:
mean LOO = 14.02 / 16

8 examples:
16 / 16 in every seed
```

---

## Probe / Output Alignment

```text
6 examples:
median cosine = 0.681

8 examples:
median cosine = 0.997
minimum       = 0.961
```

---

## Sensitivity Reorganization

```text
relevant sensitivity:
6.605 → 7.901

nuisance sensitivity:
3.108 → 0.479

relevant/nuisance ratio:
2.126 → 17.010
```

---

## Best-Neuron Separation

```text
6 examples:
mean = 0.609

8 examples:
mean = 0.795
```

The distributions do not overlap.

---

## Neuron Identity

The winning neuron index is roughly uniform:

```text
6 examples:
36 / 35 / 29

8 examples:
36 / 34 / 30
```

So the functional role is stable while the raw unit identity is not.

---

# 10. What Seed 7 Got Right

Seed 7 correctly revealed the qualitative direction of the transition.

It showed:

```text
greater task alignment
cleaner target geometry
stronger target/output coupling
a strongly target-aligned neuron
causal use of target-related hidden structure
```

All of these generalize.

---

# 11. What Seed 7 Overstated

Seed 7 made the single-neuron mechanism appear cleaner than it usually is.

In seed 7:

```text
mean ablation destroyed all four positive classifications
opposite-class patching was almost perfectly bidirectional
```

Across seeds, these effects are weaker and more variable.

Therefore the stable mechanism is better summarized as:

```text
distributed target representation
+
one strongly target-aligned causal contributor
```

rather than:

```text
one neuron implements the whole concept
```

---

# 12. Unified Mechanistic Story

The evidence now forms a coherent sequence.

## Stage 1: Target information is already present

The 6-example networks do not recover the correct function:

```text
0/100 exact recovery
```

But hidden space already contains substantial target information:

```text
mean target LOO = 14.02 / 16
mean probe/output cosine = 0.701
```

So incorrect behavior does not imply absence of relevant internal information.

---

## Stage 2: The representation becomes task-selective

After the discriminating examples:

```text
nuisance sensitivity collapses
relevant sensitivity increases
```

The network stops relying heavily on:

```text
rounded
striped
```

and organizes its computation around:

```text
blue
large
```

---

## Stage 3: The target concept becomes geometrically regular

The target probe becomes:

```text
16/16 leave-one-out
```

in every seed.

The target concept is no longer merely decodable.

It becomes a highly regular direction in hidden space.

---

## Stage 4: The output aligns with that representation

Probe/output cosine becomes:

```text
median = 0.997
```

So the representation that best encodes the target concept is almost exactly the representation the output layer reads.

---

## Stage 5: Target-aligned hidden structure is causally used

Neuron ablation and activation patching show that changing target-aligned hidden activations changes the network's actual decision.

So the target representation is not merely:

```text
present
```

It is:

```text
used
```

---

## Stage 6: The stable abstraction is more geometric than neuronal

The identity of the most target-aligned neuron changes across seeds.

But the target direction itself is highly stable.

Therefore:

> **The robust object of analysis is the representation/subspace, not the raw neuron index.**

This is an important mechanistic-interpretability lesson.

---

# 13. Precise Final Claim

The strongest claim supported by the full experiment is:

> **When the training evidence becomes sufficient to identify the intended `blue AND large` concept, the MLP undergoes a reliable task-aligned representational reorganization. Target information that was already partially present becomes more geometrically regular, nuisance influence is strongly suppressed, the target direction becomes almost perfectly aligned with the network's output readout, and target-aligned hidden structure is causally used in producing the decision. This transition is stable across random initialization.**

A shorter version is:

> **The network does not simply acquire target information; it reorganizes existing information into a cleaner, more invariant, more causally used task representation.**

This is the main empirical result.

---

# 14. What We Can Claim

The experiments support:

```text
✓ target-related information exists before exact target recovery

✓ correct learning makes the target more linearly regular

✓ correct learning suppresses nuisance influence

✓ the target direction becomes strongly aligned with the output readout

✓ target-aligned hidden structure causally affects predictions

✓ these effects are stable across 100 random seeds

✓ the representation-level effect is more stable than individual-neuron identity
```

---

# 15. What We Cannot Claim

The experiments do not support:

```text
✗ the network learned a symbolic AND operator

✗ one neuron literally represents AND

✗ the network decomposes the concept into explicit BLUE and LARGE symbols

✗ the network learned a reusable program fragment for conjunction

✗ the learned representation would transfer compositionally to a new task

✗ this toy result establishes abstraction formation in the stronger ARC/program-synthesis sense
```

The main reason is structural.

In this task:

```text
positive class
=
blue AND large
```

So these two hypotheses are observationally indistinguishable:

```text
H1:
the network represents the final positive class

H2:
the network explicitly constructs the conjunction
blue AND large
```

Every object that satisfies one satisfies the other.

No intervention in the current task can separate them.

---

# 16. The Abstraction Boundary

This experiment demonstrates something stronger than memorization but weaker than compositional abstraction.

A useful hierarchy is:

```text
1. Information present
2. Information geometrically organized
3. Information causally used
4. Representation invariant across seeds
5. Representation reused compositionally
6. Reusable abstraction / program-like component
```

This experiment reaches approximately:

```text
levels 1–4
```

It does not yet establish:

```text
levels 5–6
```

That distinction is essential for the broader ARC-AGI research goal.

---

# 17. Connection to Program Synthesis and ARC-AGI

The result maps naturally onto program synthesis.

In enumerative synthesis, many programs can initially remain consistent with sparse evidence.

Additional discriminating examples eliminate spurious hypotheses and concentrate search on the intended structure.

Something analogous happens here:

```text
6 examples:
many internal solutions remain compatible with the data

8 examples:
spurious dependencies become unnecessary
and representations reorganize around the true task structure
```

But there is an important difference.

The symbolic learner explicitly represents:

```text
AND(blue, large)
```

The neural learner only gives us evidence for:

```text
a target-aligned internal geometry
```

The symbolic decomposition is explicit in one case and inferred indirectly in the other.

That gap is exactly where the next abstraction experiment should focus.

---

# 18. What the Next Experiment Must Separate

The next task should make these hypotheses behaviorally different:

```text
"encode the final answer"
```

versus:

```text
"learn a reusable intermediate abstraction"
```

For example, the network could first need to learn:

```text
blue AND large
```

as an intermediate concept and then reuse it inside multiple new rules:

```text
(blue AND large) OR striped

NOT(blue AND large)

(blue AND large) AND rounded
```

If the same internal representation is:

```text
reused
transferred
causally necessary
across multiple compositions
```

then we would have much stronger evidence for a compositional abstraction.

That would move the experiment closer to the kind of structure needed in:

```text
program synthesis
DreamCoder-style library learning
ARC-style reusable transformations
```

---

# Final Conclusion

The experiment began with a simple behavioral puzzle:

```text
Why does a tiny MLP trained on six examples learn the wrong function,
while two additional counterexamples make it recover the correct one?
```

The final answer is not merely:

```text
because it saw more data
```

The internal change is structured.

Across 100 seeds, correct learning reliably produces:

```text
less nuisance dependence
+
stronger task-relevant sensitivity
+
perfect target-concept linear generalization
+
near-perfect target/readout alignment
+
causally used target-aligned hidden structure
```

The strongest stable object is not one particular neuron.

It is the **geometry of the hidden representation**.

So the most precise conclusion is:

> **The discriminating examples induce a robust reorganization of hidden space around the true task concept. The resulting representation is cleaner, more invariant to nuisance features, more aligned with the network's decision rule, and causally used. This is strong evidence for abstraction-like representational formation, but not yet for a reusable symbolic or compositional abstraction.**
