"""Exact K-way one-shot classification for the finite BPL-inspired model.

Assumptions: K independent types drawn from the type prior; one reference image
per type; query label C has an explicitly specified prior; query is a fresh
independent token from the selected reference's type. This is not the paper's
full handwriting system.
"""
from fractions import Fraction
from bpl_recognition import predictive_same


def classify(references: tuple[str, ...], query: str,
             class_prior: tuple[Fraction, ...] | None = None) -> tuple[Fraction, ...]:
    """Return exact P(C=k | query, references) for each reference index k."""
    if not references:
        raise ValueError('At least one reference is required')
    n = len(references)
    if class_prior is None:
        class_prior = (Fraction(1, n),) * n
    if len(class_prior) != n or any(p < 0 for p in class_prior) or sum(class_prior) != 1:
        raise ValueError('Class prior must be normalized and nonnegative')
    weights = tuple(p * predictive_same(ref, query)
                    for p, ref in zip(class_prior, references))
    total = sum(weights, Fraction(0))
    if total == 0:
        raise ValueError('Query has zero likelihood under all candidate classes')
    return tuple(w / total for w in weights)


def classify_reference_joint(references: tuple[str, ...], query: str,
                             class_prior: tuple[Fraction, ...] | None = None):
    """Independent check using joint likelihood and reference evidence."""
    from bpl_recognition import joint_same, predictive_different
    if not references:
        raise ValueError('At least one reference is required')
    n = len(references)
    if class_prior is None:
        class_prior = (Fraction(1, n),) * n
    if len(class_prior) != n or any(p < 0 for p in class_prior) or sum(class_prior) != 1:
        raise ValueError('Class prior must be normalized and nonnegative')
    evidences = [predictive_different(r) for r in references]
    if any(e == 0 for e in evidences):
        raise ValueError('Reference image has zero probability')
    weights = []
    for k in range(n):
        mass = class_prior[k] * joint_same(references[k], query)
        for j, evidence in enumerate(evidences):
            if j != k:
                mass *= evidence
        weights.append(mass)
    total = sum(weights, Fraction(0))
    if total == 0:
        raise ValueError('Query has zero likelihood under all candidate classes')
    return tuple(w / total for w in weights)


if __name__ == '__main__':
    from bpl_minimal import Stroke, Token, render
    from bpl_finite import CANVAS_HEIGHT, CANVAS_WIDTH
    def horizontal(length):
        return render(Token((Stroke((12-length//2,5), (12+length//2,5)),)), CANVAS_WIDTH, CANVAS_HEIGHT)
    refs = (horizontal(6), horizontal(10), horizontal(4))
    q = horizontal(4)
    print('Predictive likelihoods:', *(predictive_same(r,q) for r in refs))
    print('Class posterior:', classify(refs,q))
