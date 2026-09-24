# Four Learners, One Concept

## Goal

I gave four different learners a small Boolean concept-learning problem.

Each object had four binary features:
- `blue`
- `large`
- `rounded`
- `striped`

The hidden rule was:

```python
blue and large
```

So an object was positive only when both `blue = 1` and `large = 1`.

I showed each learner **6 labelled examples** and kept the other **10 objects unseen**. The learners never saw the rule itself, only the examples. I then compared how they generalized to the unseen objects.

The point of the experiment was not only to measure accuracy, but to see **how different inductive biases lead to different generalizations from the same evidence**.

---

# 1. Exemplar Learner

## Core idea

The exemplar learner stores the training examples directly.

For a new object, it finds the most similar stored example using Hamming distance and copies its label.

It does not learn an explicit rule. It only learns:

```text
"objects similar to this example probably have the same label"
```

## Important inductive bias

Its behavior depends on **local similarity**.

If two training examples are equally close but have different labels, the implementation returns the first one encountered. This means training-example order can affect the prediction.

## Result

On the fixed six-example dataset, the exemplar learner got:

```text
6 / 10 unseen objects correct
```

Its errors came from the fact that closeness in raw feature space is not the same as knowing which features actually define the concept.

## Main lesson

The exemplar learner remembers concrete cases well, but it does not automatically discover the abstract rule behind them.

---

# 2. Prototype Learner

## Core idea

The prototype learner compresses each class into an average feature vector:

```text
positive prototype = average of positive examples
negative prototype = average of negative examples
```

For a new object, it chooses the label of the closest prototype using Euclidean distance.

Instead of remembering every example, it learns a rough summary of each class. This is a stronger abstraction than the exemplar learner, but it is still geometric rather than symbolic.

## Important inductive bias

It assumes that class membership can be represented well by **distance to an average point**. That works when categories form compact clusters, but it can fail when the real concept depends on a logical relation.

## Result

On the same fixed six-example dataset, the prototype learner got:

```text
10 / 10 unseen objects correct
```

Its geometric decision happened to agree with the hidden rule on the complete unseen set. However, this does not mean it explicitly learned the symbolic rule `blue AND large`.

## Main lesson

Prototype learning compresses examples into category summaries, but the summary can lose the logical structure that actually defines the concept.

---

# 3. Bayesian Program-Induction Learner

## Core idea

The Bayesian learner considers many possible symbolic programs, such as:

```text
blue
large
blue AND large
blue OR large
blue AND (large OR rounded)
...
```

Programs are generated automatically from a small DSL:

```python
("var", i)
("not", child)
("and", left, right)
("or", left, right)
```

The learner assigns probability to programs using `prior × likelihood`

#### Prior

Shorter programs receive larger prior weight:

```python
2 ** (-program_size)
```

So the learner prefers simpler explanations before seeing the data.

#### Likelihood

The current experiment uses a deterministic, noise-free likelihood:

```text
consistent with all examples → likelihood 1
inconsistent                 → likelihood 0
```

#### Posterior

The learner combines prior and likelihood, then normalizes the surviving weights.

Unlike the other learners, it can maintain uncertainty over several possible explanations instead of immediately committing to one.

## Program induction result

Programs up to size 5 produced:

```text
852 syntactic programs
238 consistent programs
18 distinct consistent Boolean behaviors
```

This showed that many different programs can explain the same training evidence.

It also showed that **syntax and behavior are different**: two different ASTs can implement the same Boolean function.

## How evidence changed the posterior

With less informative evidence, simpler alternatives initially received more posterior mass than the true rule:

```text
blue                ≈ 21.6%
large               ≈ 21.6%
blue AND large      ≈ 9.7%
```

After adding informative counterexamples, posterior mass on the true function increased:

```text
9.68% → 25.64% → 78.95%
```

The prior itself did not change. The new evidence eliminated inconsistent hypotheses, and the remaining probability mass was renormalized.

## Baseline result

On the fixed six-example comparison, the Bayesian learner got:

```text
10 / 10 unseen objects correct
```

But this did **not** mean it was completely certain about the hidden rule. It still had three surviving behavioral classes:

```text
blue AND large                                   ≈ 78.95%
blue AND (large OR rounded)                      ≈ 10.53%
large AND (blue OR rounded)                      ≈ 10.53%
```

The alternatives made the same thresholded predictions as the true rule on the unseen objects except with lower posterior probability on some cases, so classification accuracy alone hid the remaining uncertainty.


## Active learning

I also extended the Bayesian learner with active learning.

Instead of manually choosing the next example, the learner chooses an unobserved object where its surviving hypotheses disagree. It then asks the oracle for the label and updates the posterior.

The learner does not know the hidden rule. It only knows which query would be informative under its current uncertainty.

Two additional queries were enough to reduce the remaining behavioral ambiguity to a single function.

## Main lesson

Bayesian program induction makes uncertainty explicit. I can inspect which rules remain plausible, how much probability they receive, and how new evidence changes that distribution.

---

# 4. Neural Network / MLP

## Core idea

The MLP has:

```text
4 input features
→ 3 hidden sigmoid neurons
→ 1 sigmoid output neuron
```

Unlike the Bayesian learner, it does not search over symbolic programs. It learns numerical weights by gradient descent.

---

## Training pipeline

The implementation was built from scratch:

```text
forward pass
→ binary cross-entropy loss
→ backpropagation
→ gradient check
→ gradient descent
→ repeated training
```

The analytical gradients from backpropagation were independently checked against numerical finite differences before training.

## Baseline result

The network fit the six training examples almost perfectly, but on the 10 unseen objects it got:

```text
8 / 10 correct
```

The same two false positives appeared repeatedly:

```text
(0, 1, 1, 0)
(1, 0, 1, 0)
```

Training for many more epochs did not fix these errors. The network had already optimized the training objective; the missing information was not present in the original evidence.

## Random-seed experiment

I trained the same architecture from 100 different random initializations. With the original six training examples:

```text
99/100 → same wrong Boolean function
1/100  → another wrong function
0/100  → true function
```

The internal weights and hidden activations varied across seeds, but almost all runs produced the same wrong input-output behavior. So:

```text
different internal representation does not necessarily mean 
different learned function
```

## Adding discriminating evidence

I then added examples that directly ruled out the spurious generalization.

I then added examples that directly ruled out the spurious generalization.

```text
Original 6 examples:
0 / 100 seeds recovered the true function

+ first discriminating example:
95 / 100 seeds recovered the true function

+ symmetric second discriminating example:
100 / 100 seeds recovered the true function
```

This showed that the problem was not simply insufficient training time.

The original evidence was **underspecified**, and a small amount of strategically informative evidence changed which function gradient descent reliably learned.

## Did the MLP learn the abstraction?

Behaviorally, after the two extra examples, it computed the correct Boolean function on all 16 possible objects. But that does **not** prove that one hidden neuron explicitly represented:

```text
blue AND large
```

The hidden neurons still depended on `rounded` and `striped`, and the representation varied considerably across random seeds. So I need to distinguish:

```text
correct behavior
≠
clean internal abstraction
```

## Main lesson

The MLP can fit the data and eventually recover the correct function, but its internal representation is distributed and harder to interpret.

Its inductive bias is implicit in the architecture, initialization, loss, optimizer, and training dynamics.

# Overall Comparison

| Learner | Baseline accuracy | Main representation | Generalization mechanism |
|---|---:|---|---|
| Exemplar | **6/10** | Stored examples | Nearest observed example |
| Prototype | **10/10** | Class averages | Nearest class prototype |
| Bayesian | **10/10** | Probability distribution over symbolic programs | Posterior over candidate rules |
| MLP | **8/10** | Distributed numerical weights | Gradient-learned decision boundary |

The accuracy numbers are useful, but they do not tell the whole story.

The prototype reached 10/10 without explicitly representing the symbolic rule. The Bayesian learner also reached 10/10 while still assigning probability to alternative functions. The MLP fit the training set almost perfectly but generalized incorrectly until it received more informative evidence.

# Main Result

All four learners saw essentially the same concept-learning problem, but they generalized differently because they had different inductive biases.

The central lesson is:

> **The data alone does not determine the learned concept. The learner's representation and inductive bias determine how it generalizes beyond the observed examples.**

The Bayesian learner made that ambiguity explicit by maintaining several possible rules.

The MLP hid the ambiguity inside parameter space, but the 100-seed experiment revealed that gradient descent strongly preferred a particular wrong function when the evidence was underspecified.

Adding carefully chosen evidence changed both systems dramatically.

---

# What I Take Away

1. **The same examples can support different generalizations.** What a learner infers depends on its inductive bias, not only on the data.
2. **Accuracy does not tell me what representation was learned.** A learner can predict perfectly without explicitly representing the generating rule.
3. **Bayesian inference makes ambiguity visible, while the MLP expresses it implicitly through optimization and parameter space.**
4. **Perfect training fit does not guarantee the correct function.** The MLP's 8/10 result was a generalization problem, not an optimization problem.
5. **Informative evidence matters.** Two carefully chosen counterexamples changed MLP recovery from 0/100 to 100/100 seeds.

---

# Caveats

1. The world contains only **16 possible objects**, so I can exhaustively evaluate every input.
2. The data is synthetic and noise-free, and the training examples were deliberately chosen.
3. The Bayesian results depend on the finite program-size cutoff and on a prior defined over program syntax.
4. The MLP results depend on this particular architecture, loss, optimizer, learning rate, training order, and initialization scheme.
5. Matching the complete truth table does **not** prove that the MLP formed a clean internal `blue AND large` abstraction.

---

# What comes next

The behavioral comparison is now mostly complete.

The next question is deeper:

> When a neural network computes the correct function, what evidence would justify saying that an abstraction has actually formed inside the network?

That requires moving from behavioral evaluation to representation analysis and mechanistic interpretability.
