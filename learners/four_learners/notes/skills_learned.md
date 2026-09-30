# What I practised in the four-learner experiment

This is a record of methods I used and distinctions I want to carry forward. Doing them once gives me practice. Being able to explain and apply them independently to another problem is the next check.

## Methods I practised

### Comparing learners and their assumptions

I compared exemplar, prototype, Bayesian symbolic, and neural learners on the same objects and labels. This made inductive bias concrete:

- Exemplar: Hamming distance gives every feature equal importance; ties depend on example order.
- Prototype: each class is represented by its average feature vector.
- Bayesian: the logical language limits the candidate rules, and the prior favours shorter programs.
- Neural: architecture, initialisation, training order, and optimisation shape the solution found.

The question to carry forward: what does the learner assume beyond the examples it receives?

### Reasoning over programs

I enumerated logical programs using features, NOT, AND, and OR, then assigned posterior probabilities using a length prior and consistency with the observations. This connects to the enumerative search I built in Week 0, but now I retain uncertainty over explanations.

Two lessons matter here:

- Several functions can fit the same observations. A preferred explanation is not guaranteed to be the intended one.
- Several program trees can implement the same function. If the prior is over program syntax, combining equivalent programs requires adding their probability mass, not simply deleting duplicates.

Equivalence on observed inputs also needs to be distinguished from equivalence over the whole domain. In this experiment, I can check all 16 objects.

### Building and checking a small neural network

I worked through a 4-input, 3-hidden-unit, 1-output MLP: forward propagation, sigmoid activations, binary cross-entropy, backpropagation, and gradient updates. Finite-difference gradient checks connected the derivatives to the implementation.

The useful debugging habit is to isolate a claim and check it before changing code. An implementation error, a poorly designed comparison, and a model that generalises badly are different problems.

### Comparing training conditions

I compared six-example and eight-example datasets using matching seeds, the same architecture, learning rate, and number of epochs. These were separately trained networks, not one network trained further after receiving new examples.

One detail to remember: equal epochs do not mean equal numbers of parameter updates when dataset sizes differ. The eight-example condition performs more updates per epoch. This comparison tests the two training conditions as implemented; it does not isolate every possible explanation for their difference.

I also separated training fit from matching the target on the full 16-object world. The recorded 100-seed result was 0/100 exact matches with six examples and 100/100 with eight, under the tested settings.

### Inspecting representations

I used several tools, each answering a different question:

| Method | What I checked |
|---|---|
| Feature sensitivity | How much do hidden activations and output logits change when one input feature flips? |
| Linear probes | Can a simple classifier decode a feature or the target from frozen hidden states? |
| Leave-one-out probing | Can the probe predict an object excluded from its own training set? |
| Probe/output alignment | How closely does the probe direction align with the network's output weights? |

Leave-one-out here holds an object out of **probe training**. It does not necessarily hold that object out of the original network's training.

### Testing causal influence

I used mean ablation and activation patching, then measured logit changes, probability changes, and prediction flips. Same-class donor controls helped assess whether opposite-class patching effects were specific to class differences.

These interventions give evidence about causal influence inside the model. They do not automatically identify a symbolic concept. Even a patch using a real donor activation can create a combination of hidden values that never occurs naturally.

The architecture also matters. For output logit `z = w · h + b`, steering the hidden state by `alpha * d` gives:

```text
Δz = alpha * (w · d)
```

That effect follows directly from the output layer. Observing it is not independent evidence that the direction implements a logical operator.

### Checking variation across seeds

I compared means, medians, standard deviations, quartiles, and extremes across 100 seeds. This helped separate a striking seed-7 example from patterns that persisted across the tested initialisations.

Single-neuron causal dominance varied. Target decodability, probe/output alignment, and reduced nuisance sensitivity were more consistent in the eight-example condition. These are findings about this setup, not universal properties of neural networks.

## Distinctions I want to keep clear

**Correct behaviour, decodable information, and causal use are different claims.** A network can make wrong predictions while its hidden state still contains information a separate probe can recover. A successful probe does not by itself show that the original output uses that information.

**A neuron's role is different from its index.** The most target-aligned neuron could be neuron 0, 1, or 2 in different runs. Separately, the architecture has a permutation symmetry: reordering hidden neurons together with their incoming parameters and corresponding output weights preserves the function. The cross-seed observation illustrates variable neuron identity; it is not a proof of that symmetry.

**Stable alignment is different from a shared direction across networks.** Each network has its own hidden coordinates. I measured alignment between a probe and the output weights within each network. Similar alignment scores across seeds do not establish that all networks learned the same direction in a common coordinate system.

**Matching a function does not identify its implementation.** The symbolic learner has explicit logical programs among its hypotheses. The MLP represents its solution through numerical parameters and activations. Matching predictions does not make those representations equivalent.

## Questions still open

I find these questions useful for organising the evidence:

- Is target information decodable?
- How consistently can a simple decoder recover it?
- Do interventions show causal influence on the output?
- Which measured properties persist across seeds?
- Can the representation be reused in another task or composition?

This is my working checklist, not an established hierarchy. Evidence for one item does not automatically settle the others.

The experiment provides evidence about decoding, alignment, causal influence, and their variation across seeds. It does not yet demonstrate reusable compositional abstraction. Here, the positive class is exactly `blue AND large`, so representing the final answer and representing that conjunction give the same labels.

A next experiment could require reusing the conjunction inside different rules, such as `(blue AND large) OR striped`. I would need to check whether the earlier representation actually transfers and contributes causally, rather than assuming that success means it was reused.

For my own learning, the next test is whether I can choose these methods, explain their limits, and use them on a different problem without following this experiment step by step.
