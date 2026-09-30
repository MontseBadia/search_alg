# Four learners, one concept

I compared four ways of learning the same concept, then looked more closely at what happened inside the neural network.

The world was small: 16 objects with four yes/no properties, **blue, large, rounded, and striped**. An object was positive if and only if it was both blue and large. Each learner started with the same six labelled examples and was evaluated on the ten unseen objects.

- **Exemplar:** remembers individual examples and predicts from the nearest one. It got 6/10 unseen objects right. Hamming distance treats all four features equally, and ties depend on example order, so similarity did not reliably recover the target function.
- **Prototype:** forms an average object for each class and compares new objects with those averages. It got 10/10 right on this particular setup. That does not mean class averages will work for every concept or dataset.
- **Bayesian symbolic learner:** considers logical programs built from features, AND, OR, and NOT. It keeps a probability distribution over programs consistent with the evidence, with a prior favouring shorter programs. Its combined predictions got 10/10 right, even though several distinct functions still fit the six examples.
- **Neural network:** learns weights in a small network with four inputs, three hidden neurons, and one output. The seed-7 comparison got 8/10 right. In the recorded 100-seed experiment, none of the six-example networks matched the target on all 16 objects. With two extra counterexamples, all 100 eight-example networks did.

The first lesson: **the same evidence can lead to different generalisations because learners have different inductive biases.** Here those biases came from similarity, class averages, a prior over logical programs, or the network architecture and optimisation procedure.

The Bayesian learner made the uncertainty especially clear. Several programs could explain the observations, so the best current explanation was not necessarily the true function. Additional discriminating examples narrowed the posterior within the chosen hypothesis space.

Even this tiny logical language produced many programs as their size increased. The search space, and how I search it, are part of the learning method.

## What changed inside the network?

The symbolic learner exposes its candidate programs. The neural network's solution is spread across weights and hidden activations. I wanted to understand what distinguished the networks that generalised correctly from those that did not.

I compared networks trained from scratch on six examples with networks trained from scratch on eight, using matching seeds. The two added examples were:

```text
(blue, large, rounded, striped)
(0, 1, 1, 0) → False
(1, 0, 1, 0) → False
```

The analysis built up in stages:

1. **Feature sensitivity.** Flipping rounded or striped changed the output much less in the eight-example condition. Blue and large remained influential. The network became less sensitive to irrelevant features, though their influence did not disappear completely.

2. **Linear probes.** A simple classifier could already recover much of the target information from the wrong networks' hidden states. In the eight-example condition, target decoding reached 16/16 under leave-one-out evaluation in every recorded seed. This shows that the target was easier to decode consistently; a probe alone does not show that the network uses that information.

3. **Probe/output alignment.** The direction found by the target probe was much more closely aligned with the network's output weights in the eight-example condition. This connects decodable target information to the network's decision, but does not establish a symbolic AND operation.

4. **Causal interventions.** Replacing a neuron's activation with its mean, or with an activation from another object, could change the prediction. These experiments showed causal influence of selected hidden neurons. They also used same-class replacements as controls. Such replacements can still create hidden states the network would not naturally produce.

5. **Cross-seed stability.** A strongly class-aligned neuron appeared across runs, but its index and causal dominance varied. The more consistent findings were target decodability, probe/output alignment, and reduced nuisance sensitivity. One neuron did not universally control the whole decision.

Together, these results suggest that the extra evidence led training towards a cleaner organisation of target information that was already partly decodable in the six-example condition. This was a comparison between separately trained networks, not a direct observation of one network reorganising during continued training.

## What this does and does not show

Matching the target on all 16 objects establishes correct behaviour across this tiny world. It does not prove that the network learned a reusable logical operator.

Here, **the positive class and blue AND large are the same thing**. The experiments cannot distinguish a clean representation of the final answer from a reusable conjunction that could become part of another task.

The findings support organised, causally useful internal representations. Reusable compositional abstraction remains an open question. The 100-seed results test robustness to initialisation within this setup; they do not establish the same outcome for other architectures, concepts, or datasets.

My main takeaway: learning depends on the evidence, the representation, and the assumptions and procedures used to find a solution. Correct predictions are one part of understanding what was learned.
