# Linear Probing Analysis

## Goal

The goal of this experiment was to understand **what information is present in the MLP's hidden representation**.

The original network was trained first and then frozen. After that, I trained small linear classifiers, called **probes**, on top of the hidden activations. The probe does not change the original network. It is only an analysis tool.

The question is:

> Can a simple linear classifier recover a concept from the hidden representation?

The concepts tested were:

```text
blue
large
rounded
striped
blue AND large
```

I compared two networks:

- **Wrong-function network:** trained on the original 6 examples. It fits the training data but does not recover the true Boolean function.
- **Correct-function network:** trained on the original 6 examples plus two discriminating counterexamples. It recovers the correct Boolean function.

---

## What a linear probe measures

For each object, the frozen MLP produces a hidden representation:

```text
[h0, h1, h2]
```

A linear probe receives only this hidden vector:

```text
[h0, h1, h2]
    ↓
linear classifier
    ↓
concept prediction
```

The probe has the form:

```python
prediction = sigmoid(w0 * h0 + w1 * h1 + w2 * h2 + bias)
```

If the probe can predict a concept accurately, then that concept is **linearly decodable** from the hidden representation.

However, this does not automatically mean that the original MLP uses that concept internally. The key distinction is:

```text
information is present
≠
information is used
```

---

# Experiment 1: Full-data linear probing

## Setup

For each network:

1. Compute hidden activations for all 16 possible objects.
2. Choose one concept, such as `blue` or `blue AND large`.
3. Label all 16 hidden states according to that concept.
4. Train a fresh linear probe on all 16 labeled hidden states.
5. Measure how well the probe fits the complete set.
6. Repeat for all five concepts.

This experiment asks:

> Is the concept linearly separable in the hidden representation?

Because the probe sees all 16 labels during training, this is a **representation geometry test**, not a generalization test.

---

## Results

| Concept | Wrong network | Correct network |
|---|---:|---:|
| `blue` | 14/16 | 13/16 |
| `large` | 12/16 | 13/16 |
| `rounded` | 16/16 | 16/16 |
| `striped` | 11/16 | 12/16 |
| `blue AND large` | 16/16 | 16/16 |

---

## Interpretation

The most important result is:

```text
blue AND large
wrong network   16/16
correct network 16/16
```

The target concept is perfectly linearly decodable from **both** hidden representations. This means the wrong network did not fail because the hidden layer completely lacked the information needed to recover `blue AND large`. A different linear readout can recover the correct concept perfectly from the hidden state of the wrong network.

So:

> The target information is already present in the wrong network's representation, even though the network's own output layer does not use it correctly.

Another important result is:

```text
rounded
wrong network   16/16
correct network 16/16
```

`rounded` is irrelevant to the true concept, but it remains perfectly linearly decodable in both networks. 

This shows that learning the correct function does not require the hidden representation to erase irrelevant information.

---

# Experiment 2: Leave-one-out probing

## Motivation

The full-data probe can fit all 16 labeled hidden states directly. That tells me whether a linear separator exists, but it does not tell me whether the concept is encoded in a way that generalizes to a hidden state whose label was not used to train the probe.

To test this, I used leave-one-out probing.

---

## Setup

For each concept and for each network:

1. Hold out one object.
2. Train a fresh probe on the other 15 hidden representations.
3. Test the probe on the held-out hidden representation.
4. Repeat this once for each of the 16 objects.
5. Count how many held-out objects were classified correctly.

So each concept requires 16 separate probe trainings.

With:

```text
5 concepts
× 16 leave-one-out folds
× 2 networks
= 160 probe trainings
```

Each probe is still tiny: only three weights and one bias.

This experiment asks:

> Is the concept encoded in a sufficiently regular linear structure that the probe can generalize to an unseen representation?

---

## Results

| Concept | Wrong network | Correct network |
|---|---:|---:|
| `blue` | 10/16 | 8/16 |
| `large` | 11/16 | 11/16 |
| `rounded` | 13/16 | 13/16 |
| `striped` | 10/16 | 8/16 |
| `blue AND large` | 14/16 | 16/16 |

---

# Main findings

## 1. The target concept is already present in the wrong network

The wrong-function network gets:

```text
full-fit probe:       16/16
leave-one-out probe:  14/16
```

for `blue AND large`.

So the hidden layer already contains substantial linearly accessible information about the correct target concept. The failure of the original MLP is therefore not simply:

```text
"the hidden layer never represented blue AND large"
```

Instead, the hidden representation contains enough information for another readout to recover the correct rule.

---

## 2. The correct network organizes the target concept more cleanly

For `blue AND large`:

```text
wrong network   14/16 leave-one-out
correct network 16/16 leave-one-out
```

Both networks allow a perfect linear fit over all 16 objects, but only the correct network gives perfect leave-one-out generalization. This suggests that the correct network's hidden geometry is more regularly aligned with the task-level concept.

The target concept does not appear suddenly from nothing. Rather, the representation becomes better organized around it.

---

## 3. Individual features do not become cleaner in the same way

For example:

```text
blue
wrong network   10/16
correct network  8/16

large
wrong network   11/16
correct network 11/16
```

The transition to correct behavior does not correspond to a cleaner linear representation of `blue` and `large` individually.

But the conjunction:

```text
blue AND large
```

does improve from:

```text
14/16 → 16/16
```

under leave-one-out probing.

This suggests that the representational change may be aligned more strongly with the **combined task concept** than with its individual input features.

---

## 4. Irrelevant information remains represented

`rounded` remains highly decodable:

```text
full-fit:       16/16 → 16/16
leave-one-out:  13/16 → 13/16
```

This connects directly to the earlier sensitivity experiment.

The corrected network became much less sensitive to `rounded` and `striped` at the output, but information about those features was still present in the hidden representation.

So:

```text
information present
≠
information influential
```

A network can retain information about an irrelevant feature while learning not to rely strongly on it for the final decision.

---

# Connection to the sensitivity experiment

The previous sensitivity experiment showed that, after adding the discriminating examples:

- sensitivity to `blue` and `large` increased,
- sensitivity to `rounded` and `striped` decreased strongly at the output.

Linear probing adds a different piece of evidence.

Together:

```text
Sensitivity analysis
→ what changes the representation and output?

Linear probing
→ what information can be recovered from the representation?
```

The results show that the corrected network does not simply delete nuisance information.

Instead, the representation changes so that:

- the target concept becomes more cleanly linearly organized,
- irrelevant information remains decodable,
- but irrelevant features have much less influence on the output.

---

# Caveats

1. The world contains only 16 possible objects, so probing is being performed on a very small finite representation space.
2. A successful probe only shows that information is **decodable**; it does not prove that the original network causally uses that information.
3. The probe itself has an inductive bias because it is restricted to a linear decision boundary.
4. Leave-one-out is stronger than fitting all 16 states, but each fold still trains on 15 of only 16 possible objects.
5. These results are currently for one network seed. Cross-seed analysis is still needed before claiming that the representational pattern is stable.

---

# Conclusion

The linear-probing experiments show that the target concept `blue AND large` is already linearly recoverable from the hidden representation of the wrong-function network.

However, when the network learns the correct Boolean function, the hidden geometry becomes more reliably aligned with that concept:

```text
blue AND large leave-one-out accuracy
14/16 → 16/16
```

At the same time, irrelevant information such as `rounded` remains strongly decodable, even though earlier sensitivity analysis showed that its influence on the final output decreases substantially.

The emerging picture is:

```text
wrong network:
target information exists,
but is not organized or used optimally

correct network:
target information remains present,
becomes more regularly organized,
and nuisance features influence the output much less
```

This is evidence of **task-relevant representational reorganization**, but it is not yet evidence that the network causally computes through a clean symbolic `blue AND large` abstraction.

The next step is therefore **causal intervention**: directly modify hidden activations or directions and measure which internal information actually controls the network's output.
