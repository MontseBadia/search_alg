## My Hypothesis


\[
\text{memorization}
\rightarrow
\text{reusable additive representation}
\rightarrow
\text{modular answer}
\]


### Runs To Compare

Both p = 17, unordered split 2, seed 0. Only the weight decay differs.

```text
                  5k     20k    55k    120k   180k   200k
G  (wd 1.0) test  0.00   0.07   0.54   0.81   0.96   0.85
W  (wd 0.1) test  0.00   0.02   0.07   0.28   0.37   0.39
train acc is 1.0 from 5k on in both
```

Two comparisons:
- **inside G over time**: G at 5k (knows the training pairs, nothing else) vs G at 180k (gets 96% of unseen pairs right). Same model, same data, only more training.
- **G vs W at the same step**: e.g. 55k, 0.54 vs 0.07.

### Main Idea

When the model only memorises, numbers are just labels to it. When the model generalises, the internal representations must support a reusable computation over \(a\) and \(b\), rather than treating each pair as an unrelated case.

So what changes between memorising and generalising is how numbers are represented, not where the model looks.

### Representation Hypothesis

"The wd=1.0 model will develop a final-position residual representation that organises unseen input pairs more similarly to seen pairs that share the same answer."

Representations should become more structured by target class, but this does not predict a particular geometry.

### Timing Hypothesis

"The internal representation associated with generalisation will begin changing before held-out accuracy reaches its maximum."

Behavioural improvement is probably the visible endpoint of an earlier representational transition. Some internal measure will change progressively.

### Algorithmic Hypothesis

The generalising model first forms an internal variable related to the ordinary sum \(a+b\), and only later transforms that representation into the modulo-17 answer.

### Attention Hypothesis

"Attention patterns will change less dramatically than residual representations."

### MLP Hypothesis

"The MLP contribution will differ more strongly between the two runs than the raw attention pattern."

### Train/Test Alignment Hypothesis

"In the weakly generalising model, train and test examples will occupy internally different regimes. In the strongly generalising model, that distinction will shrink."

### Classifier Hypothesis

"Classifier itself will not be the whole explanation."

There will be a representation difference before the classifier.

### Causal Hypothesis

Some internal computation present in wd=1.0 model will be more causally important for held-out examples than for training examples, and disrupting it will disproportionately damage generalisation.
