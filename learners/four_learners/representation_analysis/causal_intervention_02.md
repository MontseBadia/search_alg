# Probe-Direction Intervention Analysis

## Goal

The goal of this experiment was to test whether the **distributed hidden-space direction associated with `blue AND large`** is aligned with the direction the network actually uses to produce its output.

Earlier experiments showed that:

- `blue AND large` is linearly decodable from the hidden representation,
- the correct network organizes that target concept more cleanly,
- neuron 0 becomes a strong class-aligned causal variable.

The next question was:

> Does the full hidden-space direction identified by the linear probe also align with the network's own decision direction?

This experiment tests a **distributed concept direction**, rather than focusing on a single neuron.

---

## Networks compared

I used the same two frozen networks as before:

- **Wrong-function network:** trained on the original 6 examples.
- **Correct-function network:** trained on the original 6 examples plus the two discriminating counterexamples.

The networks were not retrained during this experiment.

---

# Core idea

The linear probe for `blue AND large` has weights:

```text
[w0, w1, w2]
```

These weights define a direction in the three-dimensional hidden space.

After normalization:

```text
probe direction = d
```

Moving a hidden representation along this direction means:

```text
h' = h + alpha * d
```

where:

```text
alpha > 0
→ move toward the probe's positive concept direction

alpha < 0
→ move away from the probe's positive concept direction
```

The original network output layer remains frozen.

So the experiment asks:

> If I move the hidden state along the direction that encodes `blue AND large`, does the original network's output move in the expected direction?

---

# Why the output effect is predictable

The network's output logit is linear in hidden space:

```text
output_z = output_weights · hidden + output_bias
```

After intervention:

```text
hidden' = hidden + alpha * probe_direction
```

the new output logit is:

```text
output_z'
=
output_weights · hidden'
+ output_bias
```

Therefore:

```text
change in output_z
=
alpha
*
(output_weights · probe_direction)
```

So the effect depends on the alignment between:

```text
probe direction
```

and:

```text
network output direction
```

This means the experiment is mainly a test of **readout alignment**.

---

# Measuring alignment

I measured two quantities.

## Dot product

```text
output_weights · probe_direction
```

This controls how strongly moving along the probe direction changes the output logit.

A larger absolute value means stronger coupling.

## Cosine similarity

Cosine similarity measures directional alignment.

```text
cosine ≈ +1
→ probe direction and output direction are almost parallel

cosine ≈ 0
→ probe direction is mostly ignored by the output

cosine ≈ -1
→ probe direction is used with opposite polarity
```

---

# Results

## Wrong-function network

Probe direction:

```text
[-0.842, -0.155, 0.517]
```

Alignment:

```text
probe/output cosine: 0.843
probe/output dot:    8.484
```

### Intervention sweep

| Alpha | Direction | Mean logit change | Label flips | Out of range |
|---:|---|---:|---:|---:|
| 0.01 | +concept | +0.085 | 0/16 | 1/16 |
| 0.01 | -concept | -0.085 | 0/16 | 1/16 |
| 0.05 | +concept | +0.424 | 0/16 | 2/16 |
| 0.05 | -concept | -0.424 | 0/16 | 3/16 |
| 0.10 | +concept | +0.848 | 2/16 | 3/16 |
| 0.10 | -concept | -0.848 | 0/16 | 3/16 |
| 0.20 | +concept | +1.697 | 2/16 | 4/16 |
| 0.20 | -concept | -1.697 | 0/16 | 6/16 |

---

## Correct-function network

Probe direction:

```text
[-0.775, -0.503, 0.384]
```

Alignment:

```text
probe/output cosine: 0.961
probe/output dot:    11.316
```

### Intervention sweep

| Alpha | Direction | Mean logit change | Label flips | Out of range |
|---:|---|---:|---:|---:|
| 0.01 | +concept | +0.113 | 0/16 | 0/16 |
| 0.01 | -concept | -0.113 | 0/16 | 4/16 |
| 0.05 | +concept | +0.566 | 0/16 | 0/16 |
| 0.05 | -concept | -0.566 | 0/16 | 4/16 |
| 0.10 | +concept | +1.132 | 0/16 | 4/16 |
| 0.10 | -concept | -1.132 | 0/16 | 4/16 |
| 0.20 | +concept | +2.263 | 0/16 | 4/16 |
| 0.20 | -concept | -2.263 | 0/16 | 9/16 |

---

# Main Findings

## 1. The target direction is already aligned in the wrong network

The wrong network has:

```text
cosine = 0.843
```

This is already a strong positive alignment.

So the target concept is not only decodable from the wrong network's hidden representation.

The network's own output direction already points substantially along that target-related direction.

This matches earlier findings:

```text
target information exists before behavior becomes fully correct
```

---

## 2. The correct network becomes much more strongly aligned

The correct network has:

```text
cosine = 0.961
```

This is very close to perfect parallel alignment.

So after the discriminating examples are added, the direction that best linearly represents `blue AND large` becomes almost the same direction that the output layer uses to make its decision.

This is an important representational change.

The transition is not:

```text
no target direction
→ target direction suddenly appears
```

It is closer to:

```text
partially aligned target direction
→ strongly aligned target direction
```

---

## 3. Coupling strength also increases

The dot product increases from:

```text
8.484
```

to:

```text
11.316
```

So moving along the target direction has a stronger causal effect on the output logit in the correct network.

For example:

```text
alpha = +0.10
```

produces approximately:

```text
wrong network:
+0.848 logit change

correct network:
+1.132 logit change
```

So the correct network does not only align more closely with the target direction.

It also couples that direction more strongly to the output.

---

## 4. No label flips in the correct network does not mean no causal effect

Even with:

```text
alpha = ±0.20
```

the correct network produced no label flips.

But the logit changed by:

```text
±2.263
```

This is a substantial causal effect.

The reason labels did not change is that the correct network's predictions have large margins.

For example:

```text
strong positive logit
→ subtract 2.26
→ still positive
```

or:

```text
strong negative logit
→ add 2.26
→ still negative
```

So:

```text
large causal movement
≠
decision-boundary crossing
```

Label flips depend on both intervention strength and the original margin.

---

## 5. The constant logit shift is expected

For a fixed alpha:

```text
change in output_z
=
alpha
*
(output_weights · probe_direction)
```

This does not depend on the original hidden state.

So every object receives the same logit shift for the same alpha.

That is why:

```text
alpha = +0.10
```

produces the same mean shift as the individual shift for every object.

This is a direct consequence of the network's linear output layer.

---

# Contrast Between Wrong and Correct Networks

The results can be summarized as:

```text
Wrong network:
target direction is already present
and already influences the output

Correct network:
target direction becomes almost parallel
to the network's actual readout
and its effect on the output becomes stronger
```

This fits the broader pattern from the previous experiments.

---

# Connection to Earlier Experiments

## Sensitivity analysis

The correct network:

```text
increases sensitivity to blue and large
decreases sensitivity to rounded and striped
```

## Linear probing

The target concept:

```text
is decodable in both networks
but generalizes more cleanly in the correct network
```

## Neuron-level causal intervention

Neuron 0 becomes:

```text
class-aligned
causally necessary
almost sufficient to switch the output
```

## Probe-direction intervention

The distributed target direction becomes:

```text
almost parallel to the network's output direction
```

Together, these results suggest a consistent representational transition.

---

# Out-of-range interventions

The hidden neurons use sigmoid activations, so naturally occurring hidden states lie in:

```text
[0, 1]
```

Moving along the probe direction can push hidden activations outside this range.

For example, in the correct network:

```text
alpha = -0.20
→ 9/16 hidden states leave the natural activation range
```

These states cannot be produced naturally by the hidden sigmoid layer.

So large interventions should be interpreted cautiously.

This is why the alignment measurements:

```text
cosine similarity
dot product
```

are cleaner evidence than simply increasing alpha until predictions flip.

---

# What This Experiment Does and Does Not Show

This experiment shows that:

```text
the direction that linearly encodes blue AND large
is strongly aligned with
the direction the network actually reads out
```

especially in the correct network.

It therefore connects:

```text
decodability
```

with:

```text
network readout
```

However, because the output layer is linear, once the probe direction and output weights are known, the intervention effect follows algebraically from their dot product.

So this is not an independent discovery of a new causal mechanism.

Its main value is demonstrating that:

> the decodable target direction and the network's actual decision direction become strongly aligned when the network learns the correct function.

---

# Caveats

1. The experiment uses one training seed.
2. The hidden space has only three dimensions, so directional structure is unusually simple.
3. Large alpha values can create hidden states outside the natural sigmoid range.
4. Because the output layer is linear, the logit shift is mathematically determined by the dot product between the output weights and probe direction.
5. Strong target-direction alignment still does not prove that the network implements a symbolic or compositional AND operation.

---

# Conclusion

The probe-direction intervention shows that the target concept is not only linearly decodable from hidden space.

In the correct network, the direction that represents `blue AND large` becomes almost parallel to the direction the network's own output layer uses:

```text
Wrong network:
cosine = 0.843
dot    = 8.484

Correct network:
cosine = 0.961
dot    = 11.316
```

This means learning the correct function is accompanied by stronger **alignment and coupling** between the target representation and the network's readout.

The emerging picture across all representation experiments is:

```text
wrong network:
target-related information already exists,
but it is less cleanly organized and less aligned

correct network:
target-related information becomes cleaner,
more causally concentrated,
and more strongly aligned with the output
```

This is further evidence of **task-relevant representational reorganization**.

It still does not prove symbolic compositionality.

The next major test is **cross-seed stability**: whether the same representational story appears across independently trained networks rather than only in seed 7.
