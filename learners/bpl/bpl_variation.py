"""Exact experiment: structured token length variation versus pixel-flip noise.

A controlled extension of bpl_finite.py, not the published BPL implementation.
Both models share the same 36 type hypotheses, type prior, renderer, canvas,
and observation noise. Only P(token length | type profile) differs.

Run: python bpl_variation.py
"""
from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from itertools import product

from bpl_finite import CANVAS_HEIGHT, CANVAS_WIDTH, enumerate_types, type_prior
from bpl_minimal import generate_token, render
from bpl_noise import hamming_distance, validate_epsilon, validate_image

ALL_LENGTHS = (4, 6, 8, 10)
SHORT = (4, 6)
LONG = (8, 10)
PIXELS = CANVAS_WIDTH * CANVAS_HEIGHT
ZERO = Fraction(0)
ONE = Fraction(1)


@dataclass(frozen=True)
class Model:
    """Spill is the chance of sampling a length outside the type's profile."""
    spill: Fraction
    epsilon: Fraction

    def __post_init__(self):
        for name, value in (("spill", self.spill), ("epsilon", self.epsilon)):
            if not isinstance(value, (Fraction, int)) or isinstance(value, bool):
                raise ValueError(f"{name} must be an exact rational number")
            object.__setattr__(self, name, Fraction(value))
        if not ZERO <= self.spill <= ONE:
            raise ValueError("spill must be in [0, 1]")
        validate_epsilon(self.epsilon)
        if self.epsilon == ONE:
            raise ValueError("epsilon=1 is excluded by scaled-likelihood arithmetic")


RESTRICTED = Model(Fraction(0), Fraction(1, 100))
FLEXIBLE = Model(Fraction(1, 4), Fraction(1, 100))


def length_distribution(profile: tuple[int, ...], spill: Fraction):
    """Return normalized P(length | short/long profile), retaining zero masses."""
    if profile not in (SHORT, LONG):
        raise ValueError("Unknown length profile")
    if not ZERO <= spill <= ONE:
        raise ValueError("Invalid spill")
    return tuple((length, (ONE - spill) / 2 if length in profile else spill / 2)
                 for length in ALL_LENGTHS)


class _ChoiceSequence:
    """Deterministic adapter for the original token generator."""
    def __init__(self, choices):
        self.choices = iter(choices)

    def choice(self, _options):
        # _options is the old fixed profile; broader values are supplied here
        # deliberately by the experimental model, not by the old generator.
        return next(self.choices)


@lru_cache(maxsize=None)
def rendered_distribution(character_type, spill: Fraction):
    """Enumerate tokens then aggregate raster collisions within each type."""
    if not type_prior(character_type):
        raise ValueError("Type not in the baseline grammar")
    choices = [length_distribution(spec.lengths, spill) for spec in character_type.strokes]
    by_image = defaultdict(Fraction)
    for selected in product(*choices):
        probability = ONE
        lengths = []
        for length, mass in selected:
            probability *= mass
            lengths.append(length)
        if probability == ZERO:
            continue
        token = generate_token(character_type, _ChoiceSequence(lengths))
        clean = render(token, CANVAS_WIDTH, CANVAS_HEIGHT)
        by_image[clean] += probability
    return dict(by_image)


@lru_cache(maxsize=None)
def scaled_type_likelihood(character_type, observed: str, model: Model) -> Fraction:
    """Return P(observed|type,model) / (1-epsilon)**N.

    This positive image-independent factor cancels in posteriors and Bayes
    factors when epsilon is fixed. Do NOT use this as an absolute probability.
    """
    validate_image(observed)
    odds = model.epsilon / (ONE - model.epsilon)
    return sum((prob * odds ** hamming_distance(clean, observed)
                for clean, prob in rendered_distribution(character_type, model.spill).items()),
               ZERO)


def image_likelihood(character_type, observed: str, model: Model) -> Fraction:
    """Actual normalized per-image likelihood, including the noise factor."""
    return ((ONE - model.epsilon) ** PIXELS
            * scaled_type_likelihood(character_type, observed, model))


def scaled_evidence(observed: str, model: Model) -> Fraction:
    validate_image(observed)
    return sum((type_prior(t) * scaled_type_likelihood(t, observed, model)
                for t in enumerate_types()), ZERO)


def posterior_types(observed: str, model: Model):
    evidence = scaled_evidence(observed, model)
    if evidence == ZERO:
        raise ValueError("Observation has zero probability")
    return {t: type_prior(t) * scaled_type_likelihood(t, observed, model) / evidence
            for t in enumerate_types()
            if scaled_type_likelihood(t, observed, model) != ZERO}


def scaled_joint_same(reference: str, query: str, model: Model) -> Fraction:
    """P(reference,query|shared,model)/(1-epsilon)**(2N)."""
    validate_image(reference)
    validate_image(query)
    return sum((type_prior(t)
                * scaled_type_likelihood(t, reference, model)
                * scaled_type_likelihood(t, query, model)
                for t in enumerate_types()), ZERO)


def bayes_factor(reference: str, query: str, model: Model) -> Fraction:
    """Shared versus independent type, keeping same model on both sides."""
    prior_reference = scaled_evidence(reference, model)
    prior_query = scaled_evidence(query, model)
    if prior_reference == ZERO or prior_query == ZERO:
        raise ValueError("Image has zero evidence")
    return scaled_joint_same(reference, query, model) / (prior_reference * prior_query)


def posterior_shared(reference: str, query: str, model: Model,
                     prior_shared: Fraction = Fraction(1, 2)) -> Fraction:
    if not ZERO <= prior_shared <= ONE:
        raise ValueError("Invalid hypothesis prior")
    same = scaled_joint_same(reference, query, model)
    different = scaled_evidence(reference, model) * scaled_evidence(query, model)
    total = prior_shared * same + (ONE - prior_shared) * different
    if total == ZERO:
        raise ValueError("Pair has zero evidence")
    return prior_shared * same / total


def posterior_both_clean(reference: str, query: str, model: Model) -> Fraction:
    """P(clean_ref==ref AND clean_query==query | images, shared type, model).

    This is a diagnostic for noise-free explanations of *both* images, not a
    unique causal decomposition of every variation into noise versus geometry.
    """
    validate_image(reference)
    validate_image(query)
    denominator = scaled_joint_same(reference, query, model)
    if denominator == ZERO:
        raise ValueError("Pair impossible under shared type")
    numerator = sum((type_prior(t)
                     * rendered_distribution(t, model.spill).get(reference, ZERO)
                     * rendered_distribution(t, model.spill).get(query, ZERO)
                     for t in enumerate_types()), ZERO)
    return numerator / denominator


def compare_shared_models(reference: str, query: str,
                          restricted: Model = RESTRICTED,
                          flexible: Model = FLEXIBLE) -> Fraction:
    """Shared-pair evidence ratio P(images|shared,flex)/P(images|shared,restrict).

    Only compare models with IDENTICAL epsilon because the image-scale factors
    are removed. With equal model priors, this is the posterior odds ratio.
    """
    if restricted.epsilon != flexible.epsilon:
        raise ValueError("Model comparison requires a shared epsilon")
    denominator = scaled_joint_same(reference, query, restricted)
    if denominator == ZERO:
        raise ValueError("Restricted model assigns zero shared-pair probability")
    return scaled_joint_same(reference, query, flexible) / denominator


def horizontal_image(length: int) -> str:
    """Make a reference clean image independently of the sampled length profile."""
    from bpl_minimal import Stroke, Token
    if length not in ALL_LENGTHS:
        raise ValueError("Unexpected line length")
    return render(Token((Stroke((12 - length // 2, 5), (12 + length // 2, 5)),)),
                  CANVAS_WIDTH, CANVAS_HEIGHT)


def experiment():
    reference = horizontal_image(6)
    for query_length in (4, 6, 10):
        query = horizontal_image(query_length)
        print(f"Query length {query_length} (reference length 6):")
        for label, model in (("restricted", RESTRICTED), ("flexible", FLEXIBLE)):
            factor = bayes_factor(reference, query, model)
            clean = posterior_both_clean(reference, query, model)
            print(f"  {label:10s} BF(shared/independent)={float(factor):.6g} "
                  f"P(both clean|pair,shared)={float(clean):.6g} "
                  f"P(shared|pair)={float(posterior_shared(reference, query, model)):.6g}")
        print("  shared-model evidence ratio (flex/restricted):",
              f"{float(compare_shared_models(reference, query)):.6g}")


if __name__ == "__main__":
    experiment()
