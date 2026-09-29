# Neuron-Level Causal Intervention Analysis

## Goal

The goal of this experiment was to test whether a hidden neuron is not only correlated with the target concept, but **causally involved in producing the network's output**.

The target concept is:

```text
blue AND large
```

Previous experiments showed that:

- the correct network becomes less sensitive to irrelevant features,
- `blue AND large` is linearly decodable from the hidden representation,
- the correct network organizes the target concept more cleanly than the wrong network.

However, those results were still observational.

The next question was:

> If I directly change the hidden representation, does the network's own prediction change in a predictable way?

I focused on **hidden neuron 0**, because earlier inspection showed that its activation was strongly aligned with the target class.

---

## Networks compared

I used the same two frozen networks as before:

- **Wrong-function network:** trained on the original 6 examples.
- **Correct-function network:** trained on the original 6 examples plus the two discriminating counterexamples.

The networks were not retrained during these experiments.

Only hidden activations were intervened on.

---

## Why causal intervention is different

Previous analyses asked:

```text
Sensitivity:
What changes when an input feature changes?

Linear probing:
What information can be decoded from hidden space?
```

Causal intervention asks:

```text
What happens to the network's own output
when I directly modify hidden space?
```

This moves from:

```text
correlation / decodability
```

toward:

```text
causal use
```

---

# Experiment 1: Mean ablation

## Setup

For each hidden neuron, I replaced its activation with that neuron's **mean activation across all 16 objects**.

For example:

```text
original hidden state:
[h0, h1, h2]

ablate neuron 0:
[mean(h0), h1, h2]
```

Then I passed the modified hidden state through the original frozen output layer.

I measured:

```text
mean absolute logit change
mean absolute probability change
number of Boolean label flips
```

The mean activation was used instead of zero so that the replacement value was closer to a typical activation.

---

## Results

### Wrong-function network

| Neuron | Mean logit change | Mean probability change | Label flips |
|---|---:|---:|---:|
| 0 | 2.660 | 0.123 | 0/16 |
| 1 | 1.748 | 0.049 | 0/16 |
| 2 | 0.229 | 0.010 | 0/16 |

### Correct-function network

| Neuron | Mean logit change | Mean probability change | Label flips |
|---|---:|---:|---:|
| 0 | **3.355** | **0.207** | **4/16** |
| 1 | 1.164 | 0.011 | 0/16 |
| 2 | 0.322 | 0.001 | 0/16 |

---

## Interpretation

Neuron 0 is clearly the most causally important hidden unit in the correct network.

When neuron 0 is replaced by its mean activation:

```text
4 / 16 labels flip
```

Those four flipped objects are exactly the four positive objects:

```text
(1, 1, 0, 0)
(1, 1, 0, 1)
(1, 1, 1, 0)
(1, 1, 1, 1)
```

All four satisfy:

```text
blue AND large
```

and all four change:

```text
True → False
```

No negative object changes class.

This means the intervention does not cause generic degradation. It specifically removes the network's ability to make positive decisions.

Neuron 0 therefore appears to be **causally necessary for the positive class under this ablation**.

---

# Neuron 0 activation pattern

In the correct network, neuron 0 has a strong class-aligned pattern.

Approximately:

```text
blue AND large = True
→ neuron 0 activation is very low

blue AND large = False
→ neuron 0 activation is high
```

So the neuron behaves roughly like a reversed class detector:

```text
low neuron 0
≈ evidence for blue AND large

high neuron 0
≈ evidence against blue AND large
```

Its output weight is also strongly negative.

That means:

```text
high neuron 0
×
large negative output weight
→ strong evidence toward False
```

This explains why replacing the very low positive-class activation with the neuron's mean value pushes positive examples across the decision boundary.

---

# Experiment 2: Opposite-Class Activation Patching

## Motivation

Mean ablation uses an artificial replacement value.

To make the intervention more natural, I next replaced neuron 0 with an activation taken from a **real object**.

This is activation patching.

For example:

```text
positive recipient hidden state
[h0_positive, h1, h2]

replace neuron 0 using a negative donor

[h0_negative, h1, h2]
```

The rest of the recipient representation remains unchanged.

---

## Two intervention directions

I tested:

```text
negative donor → positive recipient
```

and:

```text
positive donor → negative recipient
```

For each patch I measured:

```text
signed logit change
signed probability change
whether the label flipped
```

The sign matters here because the intervention has a predicted direction.

---

## Results

### Wrong-function network

| Intervention | Mean logit change | Mean probability change | Label flips |
|---|---:|---:|---:|
| Negative → Positive | -5.063 | -0.522 | 26/48 |
| Positive → Negative | +5.063 | +0.475 | 27/48 |

### Correct-function network

| Intervention | Mean logit change | Mean probability change | Label flips |
|---|---:|---:|---:|
| Negative → Positive | **-8.945** | **-0.964** | **48/48** |
| Positive → Negative | **+8.945** | **+0.797** | **47/48** |

---

## Interpretation

The correct network shows a very strong bidirectional causal effect.

When a negative-class neuron-0 activation is inserted into a positive example:

```text
48 / 48 predictions flip
```

When a positive-class neuron-0 activation is inserted into a negative example:

```text
47 / 48 predictions flip
```

So changing **only one hidden activation** is almost sufficient to reverse the network's decision.

The signed logit changes also match the expected direction:

```text
negative donor → positive recipient
logit strongly decreases

positive donor → negative recipient
logit strongly increases
```

This means neuron 0 is not merely correlated with the target class.

Its activation is directly coupled to the output in a way that controls the decision.

---

# Experiment 3: Same-Class Patching Control

## Motivation

Opposite-class patching caused many label flips.

But that could still happen if neuron 0 were simply fragile and any substantial perturbation caused the network to fail.

So I added a control:

```text
positive donor → positive recipient
negative donor → negative recipient
```

The donor and recipient were always different objects.

If neuron 0 carries class-specific information, then swapping values **within the same class** should usually preserve the prediction.

---

## Results

### Wrong-function network

| Intervention | Mean abs. logit change | Mean abs. probability change | Label flips |
|---|---:|---:|---:|
| Positive → Positive | 0.672 | 0.008 | 0/12 |
| Negative → Negative | 2.724 | 0.212 | 24/132 |

### Correct-function network

| Intervention | Mean abs. logit change | Mean abs. probability change | Label flips |
|---|---:|---:|---:|
| Positive → Positive | **0.169** | **0.001** | **0/12** |
| Negative → Negative | **0.863** | **0.001** | **0/132** |

---

## Interpretation

The correct network shows a very clean control pattern.

Opposite-class patching:

```text
Negative → Positive: 48/48 flips
Positive → Negative: 47/48 flips
```

Same-class patching:

```text
Positive → Positive: 0/12 flips
Negative → Negative: 0/132 flips
```

This rules out the explanation:

```text
"any perturbation to neuron 0 breaks the network"
```

Instead, the effect depends on **which class-specific activation value is inserted**.

The network is stable when neuron 0 is replaced with another value from the same class, but highly unstable when the value comes from the opposite class.

That is strong evidence that neuron 0 carries **class-aligned causal information**.

---

# Contrast with the Wrong-Function Network

The wrong network also shows that neuron 0 matters.

Opposite-class patching changes many predictions:

```text
26/48
27/48
```

So target-related information is already present there.

However, same-class negative patching still causes:

```text
24/132 label flips
```

This means neuron 0 is not cleanly organized by the true target class in the wrong network.

Two objects that are both negative under `blue AND large` can still have neuron-0 activations different enough that swapping them changes the network's decision.

The contrast is:

```text
wrong network:
neuron 0 contains target-related information,
but its relationship to the true class is noisy and entangled

correct network:
neuron 0 becomes highly class-aligned
and directly controls the output
```

---

# Main Findings

## 1. Neuron 0 is causally important in the correct network

Mean ablation of neuron 0 flips all four positive examples and no negatives.

So neuron 0 is not merely correlated with the target class.

Its activity is necessary for the positive decisions under this intervention.

## 2. Neuron 0 is almost sufficient to switch the decision

Opposite-class patching changes only neuron 0.

Yet:

```text
48/48 positive recipients become False
47/48 negative recipients become True
```

So neuron 0 behaves almost like a bidirectional control variable for the target decision.

## 3. The effect is class-specific, not generic perturbation sensitivity

Same-class patching produces:

```text
0/12 flips
0/132 flips
```

in the correct network.

This strongly suggests that what matters is the **class identity carried by the donor activation**, not simply the fact that neuron 0 was modified.

## 4. The correct network reorganizes target information into a cleaner causal variable

The wrong network already contains substantial target-related information.

But the correct network transforms that information into something much more cleanly aligned with the true class and much more directly connected to the output.

This matches the earlier progression:

```text
Sensitivity:
relevant features become more influential,
irrelevant features become less influential

Linear probing:
blue AND large becomes more regularly decodable

Causal intervention:
neuron 0 becomes a clean class-aligned causal control variable
```

---

# What This Does Not Prove

The evidence does **not** yet prove that neuron 0 implements a symbolic logical operation:

```text
blue
AND
large
```

The experiments show that neuron 0 has become strongly aligned with the final class:

```text
blue AND large = True
vs
blue AND large = False
```

In this tiny task, the final class and the conjunction are extensionally identical.

So a neuron that encodes:

```text
"positive class"
```

and a neuron that explicitly computes:

```text
blue AND large
```

would produce the same behavior over all 16 objects.

Distinguishing those possibilities would require a task where compositional structure can be separated from final-class identity.

---

# Caveats

1. The world contains only 16 objects, so the causal structure is being studied in a very small finite system.
2. The current results come from one training seed.
3. Mean ablation introduces an activation state that may not correspond to a naturally occurring example.
4. Activation patching is more natural, but changing one neuron while freezing the others can still create hidden states the original network never encountered.
5. The evidence supports a class-aligned causal representation, but not yet a symbolic or compositional AND operation.

---

# Conclusion

The neuron-level causal experiments provide the strongest evidence so far that the correct network does more than merely contain decodable information about the target concept.

Neuron 0 is:

```text
strongly aligned with blue AND large
+
causally necessary for positive decisions
+
almost sufficient to reverse the output when patched
+
stable under same-class replacement
```

The most striking result is:

```text
Correct network

opposite-class patching:
48/48 flips
47/48 flips

same-class patching:
0/12 flips
0/132 flips
```

This supports the conclusion that:

> **Neuron 0 has become a causally used, highly target-aligned representation of the final `blue AND large` class.**

The wrong network already contains related information, but that information is less cleanly organized and less reliably tied to the true target class.

This is strong evidence of **causal representational reorganization**.

It is still not sufficient to claim that the network has formed a symbolic compositional AND operation.

The next experiment is **probe-direction intervention**, which tests whether the distributed `blue AND large` direction identified by linear probing is also causally used by the network.
