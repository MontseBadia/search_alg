# Representation Sensitivity Analysis

## Goal

The goal of this experiment was to understand **which input features change the MLP's hidden representation and which features actually influence the final output**.

The hidden concept is:

```text
blue AND large
```

So:

```text
blue
large
```

are task-relevant features, while:

```text
rounded
striped
```

are irrelevant to the true rule.

I compared two networks:

- **Wrong-function network:** trained on the original 6 examples. It fits the training data but does not recover the true Boolean function.
- **Correct-function network:** trained on the original 6 examples plus two discriminating counterexamples. It recovers the correct Boolean function.

The main question was:

> When the network learns the correct function, does its internal representation become more aligned with the relevant features?

---

## Core idea

For each feature, I flipped only that feature while keeping the other three fixed.

For example:

```text
(1, 1, 0, 0)
↓ flip rounded
(1, 1, 1, 0)
```

Then I measured two things.

### Hidden sensitivity

How much did the hidden representation change?

For each object:

```text
h(x) = [h0, h1, h2]
```

I compared the hidden vectors before and after the feature flip using Euclidean distance.

So hidden sensitivity asks:

> How much does changing this feature move the representation?

---

### Output-relevant sensitivity

I also measured how much the output logit changed.

The output logit is:

```text
output_z
```

before the sigmoid is applied. This asks:

> How much does changing this feature alter the computation that controls the final prediction?

The important distinction is:

```text
hidden sensitivity
→ did the internal representation change?

output-relevant sensitivity
→ did it change in a way that matters to the output?
```

---

# Experiment setup

For each feature:

```text
blue
large
rounded
striped
```

I generated all unique pairs of objects that differed only in that feature.

For each pair I measured:

```text
hidden representation distance
absolute change in output_z
```

Then I averaged those values across all pairs. This produces one average hidden sensitivity and one average output-relevant sensitivity for each feature.

---

# Results

## Wrong-function network

| Feature | Hidden sensitivity | Output-relevant sensitivity |
|---|---:|---:|
| `blue` | 0.633248 | 6.275257 |
| `large` | 0.667336 | 6.362822 |
| `rounded` | 0.287763 | 2.210541 |
| `striped` | 0.424626 | 3.709572 |

The wrong network is already more sensitive to `blue` and `large` than to `rounded` and `striped`.

However, the irrelevant features still have substantial influence, especially `striped`.

---

## Correct-function network

| Feature | Hidden sensitivity | Output-relevant sensitivity |
|---|---:|---:|
| `blue` | 0.685766 | 7.364840 |
| `large` | 0.718183 | 7.427234 |
| `rounded` | 0.191322 | 0.437690 |
| `striped` | 0.162987 | 0.568394 |

The correct network shows a much clearer separation between relevant and irrelevant features.

---

# Change from wrong to correct network

Approximate changes:

| Feature | Hidden sensitivity change | Output-relevant change |
|---|---:|---:|
| `blue` | +8% | +17% |
| `large` | +8% | +17% |
| `rounded` | -34% | -80% |
| `striped` | -62% | -85% |

The strongest change is not that `blue` and `large` suddenly appear. They already mattered in the wrong network. The largest change is that the irrelevant features become much less influential, especially at the output.

---

# Main findings

## 1. Relevant features become more influential

When the network learns the correct function:

```text
blue
large
```

produce larger changes in both the hidden representation and the output logit. This means the network becomes more strongly aligned with the features that actually define the task.

---

## 2. Irrelevant features are suppressed

The largest representational change is in:

```text
rounded
striped
```

Their output influence drops dramatically:

```text
rounded:
2.21 → 0.44

striped:
3.71 → 0.57
```

So the corrected network becomes much less dependent on nuisance features.

---

## 3. Correct behavior does not require complete invariance

The irrelevant features do not disappear completely.

For example, in the correct network:

```text
rounded hidden sensitivity ≈ 0.19
striped hidden sensitivity ≈ 0.16
```

So changing them still changes the hidden representation. This means:

```text
classification invariance (irrelevant feature changes do not change True/False)
≠
representation invariance (irrelevant feature changes barely change the internal state)
```

The network can classify every object correctly even while its hidden activations still respond to irrelevant features.

---

## 4. Representation and output use are different

The hidden layer can change in response to a feature without that change strongly affecting the final decision.

This distinction is especially clear in the correct network:

```text
rounded hidden sensitivity:
still non-zero

rounded output sensitivity:
very small
```

So:

```text
information can affect the representation
without strongly controlling the output
```

This becomes important in the later probing experiment, where `rounded` remains highly decodable even though its output influence is much smaller.

---

# Interpretation

The transition from the wrong function to the correct function is accompanied by a clear reorganization.

The wrong network roughly behaves like:

```text
blue and large matter most,
but rounded and striped still influence the decision substantially
```

The correct network behaves more like:

```text
blue and large dominate,
rounded and striped still exist internally,
but their effect on the output is strongly suppressed
```

So the representational change is not simply:

```text
"the network discovers blue and large"
```

Instead, the network already responds strongly to them.

The important transition is:

```text
relevant structure becomes stronger
+
irrelevant influence becomes much weaker
```

This is a more precise description of what changes when the network learns the correct function.

---

# Connection to abstraction

This experiment provides evidence for **task-relevant representational reorganization**.

The corrected network becomes more aligned with the true structure of the task:

```text
relevant features:
more influential

irrelevant features:
less influential
```

However, this alone does not prove that the network formed a clean symbolic abstraction such as:

```text
blue AND large
```

Sensitivity only tells me:

> What happens when I change each input feature?

It does not tell me:

> What concepts are explicitly recoverable from the hidden representation?

That question motivated the next experiment: **linear probing**.

---

# Caveats

1. The experiment uses only 16 possible objects, so all sensitivities are measured over a tiny finite world.
2. The results are currently based on one training seed.
3. Sensitivity does not directly identify a symbolic concept or representation.
4. A feature can remain represented while having little influence on the output.
5. The result depends on the chosen architecture, training procedure, and the two discriminating examples.

---

# Conclusion

The sensitivity experiment shows that learning the correct Boolean function is accompanied by a strong shift in what the network relies on.

From the wrong-function network to the correct-function network:

```text
blue and large
→ become slightly more influential

rounded and striped
→ become dramatically less influential
```

The corrected network is therefore more aligned with the task structure.

At the same time, the irrelevant features still affect the hidden activations, so the representation is not fully invariant.

The main conclusion is:

> **Correct behavior emerges not by completely removing irrelevant information, but by reorganizing the representation so that task-relevant features dominate the output computation.**

This motivated the next question:

> What concepts are actually decodable from the hidden representation?

That question was addressed by the linear-probing experiment.
