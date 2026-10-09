# Tiny Transformer, Modular Addition, and Grokking: Progress Summary

## 1. Project Goal

The goal of this project is to build a tiny transformer from first principles in PyTorch, train it on modular addition, study delayed generalization / grokking, and investigate what changes internally as the model moves from memorization toward generalization.

The broader research question is:

> When the training data stays fixed but optimization continues, what changes inside the model when held-out generalization improves?

This extends earlier work on neural concept learning and mechanistic analysis, where the main distinctions were:

- decodability does not imply causal use,
- causal influence does not imply reusable abstraction,
- behavioral success does not by itself identify the internal mechanism.

---

## 2. PyTorch Foundations

The project started by rebuilding a familiar 4 -> 3 -> 1 sigmoid MLP in PyTorch.

### Concepts implemented and verified

- Tensor creation and tensor shapes.
- Single-example versus batched computation.
- Matrix multiplication with `@`.
- Broadcasting of bias vectors.
- Binary cross-entropy loss.
- `requires_grad=True`.
- Autograd via `loss.backward()`.
- Inspection of `.grad`.
- Manual gradient descent.
- Gradient accumulation and zeroing.
- `torch.optim.SGD`.
- `nn.Module`.
- `nn.Linear`.
- Model parameters versus activations.
- `state_dict()` saving and loading.
- `torch.no_grad()` for analysis.

### Important shape lesson

A tensor's number of axes is different from the dimensionality of the vector space represented along one axis.

For example:

```text
X.shape = (3, 4)
```

means:

- `X` is a 2D tensor,
- it contains 3 token vectors,
- each token vector lives in a 4-dimensional feature space.

This distinction became important later in attention.

---

## 3. Self-Attention From Scratch

Self-attention was implemented manually rather than using `nn.MultiheadAttention`.

For an input:

```text
X: (sequence, d_model)
```

three learned projections were created:

```text
Q = X W_Q
K = X W_K
V = X W_V
```

with:

```text
Q, K, V: (sequence, d_head)
```

### Attention scores

The score matrix is:

```text
Q K^T
```

with shape:

```text
(sequence, sequence)
```

The two axes represent:

- query position,
- source/key position.

The feature dimension is contracted by the dot product.

### Attention weights

Scores are scaled:

```text
scores / sqrt(d_head)
```

then passed through softmax along the source-position axis.

Each row becomes a probability distribution over source positions.

### Value mixing

The output is:

```text
attention @ V
```

which produces:

```text
(sequence, d_head)
```

The attention matrix determines how much to read from each source position.

The value vectors determine what information is transmitted.

A useful decomposition became:

```text
Q + K -> where / how much to read
V     -> what to read
```

---

## 4. Causal Masking

A causal mask was added before softmax.

For:

```text
[5, 4, =]
```

the allowed attention pattern became:

```text
position 0 -> {0}
position 1 -> {0, 1}
position 2 -> {0, 1, 2}
```

Masked scores were set to `-inf`, which gives zero probability after softmax.

This preserved the autoregressive interpretation: the final `=` position can use both operands, but earlier positions cannot read the future.

---

## 5. Output Projection and Residual Stream

Because attention operated in `d_head` dimensions while the main representation lived in `d_model`, an output projection was added:

```text
W_O: d_head -> d_model
```

This allowed the attention output to be added back to the original representation:

```text
X' = X + attention_update
```

This introduced the residual-stream view:

> attention contributes an update to an existing running representation rather than replacing it.

---

## 6. Per-Position MLP

A transformer MLP was added:

```text
d_model -> d_mlp -> d_model
```

The MLP is applied independently to every sequence position.

The conceptual distinction became:

```text
attention -> communicate across positions
MLP       -> compute across features within each position
```

The hidden expansion does not mean the final token representation contains more raw information. Its benefit is computational capacity: the model gets a larger temporary nonlinear workspace before writing an update back into the fixed `d_model` residual space.

---

## 7. Token and Positional Embeddings

The model was changed from arbitrary input vectors to actual token IDs.

For modulus 7, the vocabulary initially contained:

```text
0, 1, 2, 3, 4, 5, 6, =
```

The `=` symbol was assigned token ID 7.

Token embeddings:

```text
token_id -> d_model-dimensional vector
```

were combined with positional embeddings:

```text
token_embedding + position_embedding
```

to form the initial residual-stream representation.

A crucial conceptual point:

> Integer token IDs are identifiers, not arithmetic quantities. The embedding for token `5` does not automatically encode the numerical meaning of five.

---

## 8. Final Classifier

The final representation at the `=` position was passed through a classifier:

```text
d_model -> p logits
```

For modulus 7:

```text
7 logits
```

corresponded to classes `0..6`.

The model therefore implemented:

```text
[a, b, =]
    ↓
embeddings
    ↓
transformer block
    ↓
final "=" representation
    ↓
classifier
    ↓
logits over answers
```

Cross-entropy loss was used directly on raw logits.

---

## 9. Batching

The transformer was extended from one sequence to batched input.

The standard shape became:

```text
(batch, sequence, features)
```

For attention:

```text
X:       (B, S, d_model)
Q,K,V:   (B, S, d_head)
scores:  (B, S, S)
output:  (B, S, d_head)
```

The key change was replacing:

```python
K.T
```

with:

```python
K.transpose(-2, -1)
```

so only the last two axes are transposed while preserving the batch axis.

The final classifier used:

```python
output[:, -1, :]
```

to select the final sequence position from every batch example.

---

## 10. Modular-Addition Dataset

All ordered pairs were generated for modulus `p`.

For `p = 7`:

```text
7^2 = 49
```

total ordered pairs existed.

Each example had the form:

```text
[a, b, =]
```

with target:

```text
(a + b) mod p
```

The first version used a random train/held-out split.

---

## 11. Initial Training Diagnostics

The original very small model used approximately:

```text
d_model = 4
d_head  = 2
d_mlp   = 8
```

It failed to fit the full training set.

### Diagnostic process

Before changing architecture, the model was tested on one example.

It easily memorized it:

```text
accuracy -> 1.0
loss -> near 0
```

This established that:

- forward propagation worked,
- gradients worked,
- the optimizer worked,
- the classifier worked.

The full training-set failure was therefore not a basic implementation bug.

The model capacity was increased to approximately:

```text
d_model = 32
d_head  = 16
d_mlp   = 64
```

The larger model successfully reached:

```text
train accuracy = 1.0
train loss ≈ 0
```

while held-out accuracy stayed poor.

This established the desired overfitting regime.

---

## 12. Weight Decay and Delayed Generalization

Long training with AdamW and weight decay was explored.

A parameter L2 norm was also tracked:

```text
||theta||_2 = sqrt(sum(theta_i^2))
```

This summarizes the overall magnitude of the model parameters.

An early bug accidentally printed test accuracy instead of parameter norm. After fixing it, real norms were around tens rather than values like `0.067`.

### Important result

Weight decay did not imply monotonic norm decrease.

Gradient updates could increase parameter magnitudes faster than weight decay reduced them.

Therefore:

```text
smaller norm != automatically better generalization
```

---

## 13. First Apparent Grokking-Like Run at p = 7

With stronger weight decay, one seed showed:

```text
train accuracy -> 1.0 early

test accuracy:
~0.13
-> 0.40
-> 0.53
-> 0.80
```

while the training set had already been solved.

This initially looked like a strong delayed-generalization / grokking-like trajectory.

However, cross-seed replication showed:

```text
seed 0: 0.80
seed 1: 0.00
seed 2: 0.27
seed 3: 0.33
seed 4: 0.27
```

Seed 0 was therefore an outlier rather than evidence of a robust phenomenon.

---

## 14. Discovery of a Major Split Confound

The original random split treated `(a,b)` and `(b,a)` independently.

Because modular addition is commutative:

```text
(a + b) mod p = (b + a) mod p
```

a held-out pair could have its swapped equivalent in the training set.

Example:

```text
train: [2, 5, =]
test:  [5, 2, =]
```

The held-out result therefore did not necessarily require learning the modular-addition rule.

### Swap versus no-swap analysis

Held-out examples were divided into:

- swap pairs: reverse ordering appeared in training,
- no-swap pairs: neither ordering appeared in training.

The model generalized strongly only on swap pairs.

Across conditions:

```text
no-swap accuracy = 0
```

This showed that much of the apparent generalization was actually exploitation of commutativity.

This was a major methodological correction.

---

## 15. Corrected Grouped Split

The split was redesigned over unordered pairs.

`(a,b)` and `(b,a)` were grouped together and assigned entirely to train or test.

Therefore, if `(2,5)` was held out, `(5,2)` was also held out.

This removed the commutativity leakage and made held-out performance a much stronger test of genuinely unseen operand combinations.

---

## 16. Corrected p = 7 Results

With the grouped split, multiple seeds and weight decays were tested.

The model still reached:

```text
train accuracy = 1.0
```

but genuine held-out performance remained close to chance in most runs.

The conclusion became:

> The p=7 setup reliably supports memorization but does not reliably produce genuine unseen-pair generalization.

This ruled out treating the earlier p=7 seed-0 run as evidence of full modular-addition grokking.

---

## 17. Increasing the Modulus to p = 17

The modulus was increased to:

```text
p = 17
```

This created:

```text
17^2 = 289
```

ordered pairs.

The first p=17 runs still used the **ordered split** (the grouped split from section 15 wasn't switched on yet), so the headline held-out accuracy includes swap pairs.

Seed 0, wd = 0.1, split into the 55 swap and 32 no-swap held-out pairs:

```text
step   held-out   swap   no-swap
2k     0.14       0.22   0.00     (train acc = 1.0)
10k    0.29       0.45   0.00
20k    0.56       0.84   0.09
30k    0.71       1.00   0.22
50k    0.84       1.00   0.56
60k    0.89       1.00   0.69
85k    0.91       1.00   0.75
```

The headline number is inflated by the leak: swap pairs are solved by 30k. But no-swap pairs also climb from 0 to 0.75, which never happened at p=7. So p=17 shows real unseen-pair generalization, even in the leaky run.

Only seeds 0 and 1 of 5 looked like this. Seeds 2-4 were at 0.17, 0.33 and 0.41 held-out at 85k.

---

## 18. p = 17 Cross-Seed / Cross-Split Replication

The corrected grouped unordered-pair split was retained.

Multiple seeds and splits were tested with:

```text
weight_decay = 0.1
weight_decay = 1.0
```

The stronger regularization regime generally produced better partial delayed generalization.

Representative `wd = 1.0` runs reached best held-out accuracies such as:

```text
0.85
0.84
0.81
0.95
0.82
```

while other seeds remained much weaker.

### Correct interpretation

The model has not yet shown complete generalization across runs.

The current evidence supports:

> reproducible but seed-dependent partial delayed generalization.

It does not yet support:

> robust full grokking to perfect held-out accuracy.

---

## 19. Experimental Efficiency Decision

After many diagnostic conditions, the project shifted away from broad hyperparameter search.

The priority became:

- keep the corrected grouped split,
- use a reasonable fixed configuration,
- avoid endless tuning,
- preserve checkpoints,
- move toward mechanistic comparison once the behavioral regime is sufficiently useful.

A simple possible next adjustment is increasing the training fraction from roughly 70% toward 80-85% while preserving grouped unordered-pair splitting.

This gives the model more evidence about the modular rule without reintroducing swap leakage.

---

## 20. Checkpointing Design

Checkpoints were introduced to support both reproducibility and later mechanistic analysis.

What the code actually saves, every 5k steps, in `checkpoints_p17/<split>/wd<wd>/run_seed_<seed>_split_<split_seed>/step_<N>.pt`:

### Per-checkpoint state

```text
step
model_state       (model.state_dict())
optimizer_state   (optimizer.state_dict(), AdamW moments)
```

### Experiment-level metadata

Stored in every checkpoint too (small, so duplication is fine):

```text
config:  init_seed, split_seed, split, p, d_model, d_head, d_mlp,
         d_voc, d_pos, lr, weight_decay, steps
train_idx, test_idx
```

### History

The cumulative history is copied into every checkpoint and also written to `history.csv` in the run folder (overwritten at each save):

```text
step
train loss
test loss
train accuracy
test accuracy
parameter norm
```

Storing it once per run would be cleaner, but each checkpoint is only ~113 KB.

### Data tensors

The full generated dataset does not need to be stored in every checkpoint because it can be reconstructed deterministically from `p` plus the saved split indices.

---

## 21. Current Epistemic Position

Several important claims were refined during the project.

### Established

The transformer implementation can:

- represent modular-addition examples,
- train with batched PyTorch operations,
- memorize the training set,
- support checkpointed longitudinal analysis.

### Supported by current experiments

- Regularization strongly affects delayed held-out behavior.
- Training dynamics are highly seed-dependent.
- Random ordered-pair splits can substantially overestimate generalization because of commutativity leakage.
- Increasing `p` from 7 to 17 produces much stronger delayed held-out improvement.
- `wd = 1.0` gives stronger partial generalization than weaker decay in the tested p=17 regime.

### Not yet established

- reliable full grokking,
- a robust internal mechanism of grokking,
- genuine reusable arithmetic abstraction,
- compositional decomposition into reusable addition and modulus components.

---

## 22. Most Important Methodological Lessons

### 1. Prove the model can overfit before studying generalization

The one-example test separated implementation failure from capacity / optimization issues.

### 2. Accuracy and loss reveal different things

Accuracy can stay constant while confidence changes substantially.

Held-out loss exposed cases where the model was extremely confident on incorrect examples.

### 3. Cross-seed replication matters

A single impressive trajectory can be an outlier.

### 4. Split design defines what "generalization" means

The original ordered-pair split accidentally tested commutativity rather than fully unseen operand combinations.

### 5. Subgroup analysis can overturn the main interpretation

Breaking held-out accuracy into swap versus no-swap pairs revealed the confound.

### 6. Lower parameter norm is not equivalent to better generalization

Weight decay changes optimization bias, but total norm alone does not identify a generalizing solution.

### 7. Behavioral contrast should precede mechanistic interpretation

It is dangerous to mechanistically interpret one successful seed before establishing whether the behavior is reproducible and what kind of generalization is actually occurring.

---

## 23. Skills Acquired

### PyTorch

- tensor shape reasoning,
- batching,
- broadcasting,
- autograd,
- optimizers,
- `nn.Module`,
- embeddings,
- checkpointing,
- loss and accuracy evaluation.

### Transformer mechanics

- Q/K/V projections,
- scaled dot-product attention,
- causal masking,
- value mixing,
- attention output projection,
- residual connections,
- per-position MLP,
- positional information,
- classifier logits.

### Experimental methodology

- train/test split design,
- overfitting diagnostics,
- cross-seed replication,
- regularization sweeps,
- parameter-norm tracking,
- subgroup analysis,
- confound detection,
- distinguishing partial generalization from complete grokking.

### Research interpretation

- memorization versus generalization,
- delayed generalization versus ordinary fitting,
- decodability versus causal use,
- behavioral evidence versus mechanism,
- task-specific generalization versus reusable abstraction.

---

## 24. Current State of the Project

The project has progressed through:

```text
learn PyTorch
    ↓
implement self-attention
    ↓
build a tiny transformer
    ↓
train on modular addition
    ↓
establish memorization
    ↓
observe apparent delayed generalization
    ↓
replicate across seeds
    ↓
discover commutativity leakage
    ↓
fix the split
    ↓
increase p
    ↓
obtain stronger genuine partial delayed generalization
```

The main remaining transition is:

```text
behavioral experiment
    ↓
select useful checkpoint trajectories
    ↓
measure internal representation changes
    ↓
form mechanistic hypotheses
    ↓
test them with causal interventions
```

The central open question remains:

> What internal changes distinguish a model that only memorizes the training pairs from one that increasingly generalizes to genuinely unseen modular-addition pairs?
