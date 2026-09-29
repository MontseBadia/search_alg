## Comparison Results

#### Questions:

This comparison answers three questions:

1. **Who was correct?**
    → accuracy

2. **How confident were the probabilistic learners?**
    → Brier score + probabilities

3. **Where did their inductive biases produce different generalizations?**
    → disagreement cases + predictive mechanisms

#### Results:

| Query | Truth | Exemplar | Prototype | Bayes P(True) | Bayes | Neural P(True) | Neural |
|---|---:|---:|---:|---:|---:|---:|---:|
| `(0, 0, 0, 1)` | False | False | False | 0.000 | False | 0.000 | False |
| `(0, 0, 1, 1)` | False | False | False | 0.000 | False | 0.000 | False |
| `(0, 1, 0, 0)` | False | True | False | 0.000 | False | 0.367 | False |
| `(0, 1, 1, 0)` | False | False | False | 0.105 | False | 0.965 | True |
| `(0, 1, 1, 1)` | False | True | False | 0.105 | False | 0.054 | False |
| `(1, 0, 0, 0)` | False | True | False | 0.000 | False | 0.351 | False |
| `(1, 0, 1, 0)` | False | False | False | 0.105 | False | 0.960 | True |
| `(1, 0, 1, 1)` | False | True | False | 0.105 | False | 0.053 | False |
| `(1, 1, 0, 1)` | True | True | True | 1.000 | True | 0.967 | True |
| `(1, 1, 1, 0)` | True | True | True | 1.000 | True | 0.998 | True |

#### Accuracy + Brier Score:

| Learner | Accuracy | Brier score |
|---|---:|---:|
| Exemplar | **6/10** | — |
| Prototype | **10/10** | — |
| Bayesian | **10/10** | **0.0044321** |
| Neural | **8/10** | **0.2116972** |

Lower Brier score is better.

The Brier score is only shown for Bayesian and Neural because they produce probabilities. Exemplar and Prototype return class labels directly.

#### Main Findings:

- **Exemplar**: makes four errors because local similarity is a poor approximation for the real logical rule
- **Prototype**: achieves perfect classification but gives no probability
- **Bayesian**: achieves perfect classification and very strong probabilistic predictions
- **Neural**: MLP makes only two errors but those are high confidence errors, so the Brier score is much worse

Accuracy only measures whether the final class label is correct. The Brier score penalizes **how confidently wrong** a learner is.

#### Disagreements:

The learners disagreed on six of the ten unseen objects:

```text
(0, 1, 0, 0)
(0, 1, 1, 0)
(0, 1, 1, 1)
(1, 0, 0, 0)
(1, 0, 1, 0)
(1, 0, 1, 1)
```

#### Disagreement Cases:

They expose the different inductive biases.

---

#### Object: (0, 1, 0, 0) ---- Truth: False

- **Exemplar:**
```
  prediction:      True
  nearest example: (1, 1, 0, 0)
  distance:        1
```
- **Prototype:**
```
  prediction: False
  label=1     distance=1.225 prototype=(1.0, 1.0, 0.5, 0.5)
  label=0     distance=0.968 prototype=(0.25, 0.25, 0.25, 0.5)
```
- **Bayesian:**
```
  prediction: False
  P(True):  0.000
  P(False): 1.000
```
- **Neural:**
```
  prediction: False
  P(True):    0.367
  hidden:     [0.494, 0.465, 0.652]
```

---

#### Object: (0, 1, 1, 0) ---- Truth: False

- **Exemplar:**
```
  prediction:      False
  nearest example: (0, 0, 1, 0)
  distance:        1
```
- **Prototype:**
```
  prediction: False
  label=1     distance=1.225 prototype=(1.0, 1.0, 0.5, 0.5)
  label=0     distance=1.199 prototype=(0.25, 0.25, 0.25, 0.5)
```
- **Bayesian:**
```
  prediction: False
  P(True):  0.105
  P(False): 0.895
```
- **Neural:**
```
  prediction: True
  P(True):    0.965
  hidden:     [0.2, 0.174, 0.513]
```

---

#### Object: (0, 1, 1, 1) ---- Truth: False

- **Exemplar:**
```
  prediction:      True
  nearest example: (1, 1, 1, 1)
  distance:        1
```
- **Prototype:**
```
  prediction: False
  label=1     distance=1.225 prototype=(1.0, 1.0, 0.5, 0.5)
  label=0     distance=1.199 prototype=(0.25, 0.25, 0.25, 0.5)
```
- **Bayesian:**
```
  prediction: False
  P(True):  0.105
  P(False): 0.895
```
- **Neural:**
```
  prediction: False
  P(True):    0.054
  hidden:     [0.648, 0.554, 0.287]
```

---

#### Object: (1, 0, 0, 0) ---- Truth: False

- **Exemplar:**
```
  prediction:      True
  nearest example: (1, 1, 0, 0)
  distance:        1
```
- **Prototype:**
```
  prediction: False
  label=1     distance=1.225 prototype=(1.0, 1.0, 0.5, 0.5)
  label=0     distance=0.968 prototype=(0.25, 0.25, 0.25, 0.5)
```
- **Bayesian:**
```
  prediction: False
  P(True):  0.000
  P(False): 1.000
```
- **Neural:**
```
  prediction: False
  P(True):    0.351
  hidden:     [0.484, 0.455, 0.515]
```

---

#### Object: (1, 0, 1, 0) ---- Truth: False

- **Exemplar:**
```
  prediction:      False
  nearest example: (0, 0, 1, 0)
  distance:        1
```
- **Prototype:**
```
  prediction: False
  label=1     distance=1.225 prototype=(1.0, 1.0, 0.5, 0.5)
  label=0     distance=1.199 prototype=(0.25, 0.25, 0.25, 0.5)
```
- **Bayesian:**
```
  prediction: False
  P(True):  0.105
  P(False): 0.895
```
- **Neural:**
```
  prediction: True
  P(True):    0.960
  hidden:     [0.194, 0.168, 0.373]
```

---

#### Object: (1, 0, 1, 1) ---- Truth: False

- **Exemplar:**
```
  prediction:      True
  nearest example: (1, 1, 1, 1)
  distance:        1
```
- **Prototype:**
```
  prediction: False
  label=1     distance=1.225 prototype=(1.0, 1.0, 0.5, 0.5)
  label=0     distance=1.199 prototype=(0.25, 0.25, 0.25, 0.5)
```
- **Bayesian:**
```
  prediction: False
  P(True):  0.105
  P(False): 0.895
```
- **Neural:**
```
  prediction: False
  P(True):    0.053
  hidden:     [0.639, 0.545, 0.186]
```

---

#### How each learner explains a prediction:

#### Exemplar:

The explanation is local:

```text
prediction because
nearest training example = X
at Hamming distance = d
```

#### Prototype:

The explanation is geometric:

```text
distance to positive prototype
vs
distance to negative prototype
```

The closest prototype determines the label.

#### Bayesian:

The explanation is probabilistic and symbolic:

```text
posterior mass predicting True
vs
posterior mass predicting False
```

This also exposes uncertainty over alternative rules.

#### Neural:

There is no symbolic explanation yet. The following can be inspected, but it does not automatically tell which human-readable rule the network uses internally.

```text
output probability
hidden activations
learned weights
```

That question belongs to the next stage: representation analysis and mechanistic interpretability.

#### Final Interpretation:

The comparison shows that the same six training examples can produce different generalizations.

- The **Exemplar learner** relies on local similarity.
- The **Prototype learner** relies on geometric class summaries.
- The **Bayesian learner** reasons over explicit symbolic hypotheses and their posterior probabilities.
- The **MLP** learns a decision boundary through optimization in parameter space.

The important result is not simply which learner obtained the highest accuracy.

It is that **each learner's representation and inductive bias determine what it infers beyond the observed examples**.

This is clearest in the disagreement cases: the learners received the same evidence but reached different conclusions because they represented and processed that evidence differently.