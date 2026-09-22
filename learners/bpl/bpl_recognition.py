# Exact one-shot pair recognition built on the finite BPL-inspired model.

from collections import defaultdict
from fractions import Fraction
from functools import lru_cache

from bpl_finite import (
    CANVAS_HEIGHT, CANVAS_WIDTH, enumerate_token_outcomes, enumerate_types,
    type_prior,
)
from bpl_minimal import render


@lru_cache(maxsize=1)
def _exact_tables():
    """Precompute P(I|type) and P(I) without identifying distinct types.

    Rendering is expensive relative to rational arithmetic. There are only 136
    token outcomes, so execute each exactly once; accumulate raster collisions
    *within* each type before combining types through their prior probabilities.
    """
    likelihoods = {}
    image_masses = defaultdict(Fraction)
    for character_type in enumerate_types():
        by_image = defaultdict(Fraction)
        for token, token_probability in enumerate_token_outcomes(character_type):
            image = render(token, CANVAS_WIDTH, CANVAS_HEIGHT)
            by_image[image] += token_probability
        likelihoods[character_type] = dict(by_image)
        for image, likelihood in by_image.items():
            image_masses[image] += type_prior(character_type) * likelihood
    return likelihoods, dict(image_masses)


def _evidence(image: str) -> Fraction:
    return _exact_tables()[1].get(image, Fraction(0))


def predictive_same(reference_image: str, query_image: str) -> Fraction:
    """P(query | reference, same type), integrating over the inferred type."""
    evidence = _evidence(reference_image)
    if evidence == 0:
        raise ValueError("Reference image has zero probability under this model")
    likelihoods, _ = _exact_tables()
    return sum(
        (type_prior(t) * by_image.get(reference_image, Fraction(0)) / evidence
         * by_image.get(query_image, Fraction(0))
         for t, by_image in likelihoods.items()),
        Fraction(0),
    )


def predictive_different(query_image: str) -> Fraction:
    """P(query | reference, independently sampled types) = P(query)."""
    return _evidence(query_image)


def joint_same(reference_image: str, query_image: str) -> Fraction:
    """P(reference, query | shared type), summing over all possible types."""
    likelihoods, _ = _exact_tables()
    return sum(
        (type_prior(t) * by_image.get(reference_image, Fraction(0))
         * by_image.get(query_image, Fraction(0))
         for t, by_image in likelihoods.items()),
        Fraction(0),
    )


def joint_different(reference_image: str, query_image: str) -> Fraction:
    """P(reference, query | independent types)."""
    return _evidence(reference_image) * _evidence(query_image)


def bayes_factor(reference_image: str, query_image: str) -> Fraction:
    """Evidence for shared versus independently sampled types.

    Out-of-support images are rejected rather than assigned an invented likelihood.
    """
    same = predictive_same(reference_image, query_image)
    different = predictive_different(query_image)
    if different == 0:
        raise ValueError("Query image has zero probability under this model")
    return same / different


def posterior_same(
    reference_image: str,
    query_image: str,
    prior_same: Fraction = Fraction(1, 2),
) -> Fraction:
    """P(shared type | both images), incorporating the hypothesis prior."""
    if not 0 <= prior_same <= 1:
        raise ValueError("prior_same must be a probability between 0 and 1")
    same = joint_same(reference_image, query_image)
    different = joint_different(reference_image, query_image)
    evidence = prior_same * same + (1 - prior_same) * different
    if evidence == 0:
        raise ValueError("Image pair has zero probability under both hypotheses")
    return prior_same * same / evidence


if __name__ == "__main__":
    from bpl_minimal import Stroke, Token, render
    from bpl_finite import CANVAS_HEIGHT, CANVAS_WIDTH

    def line(length: int) -> str:
        return render(Token((Stroke((12 - length // 2, 5),
                                     (12 + length // 2, 5)),)),
                      CANVAS_WIDTH, CANVAS_HEIGHT)

    reference = line(6)
    for name, query in (("shorter horizontal (length 4)", line(4)),
                        ("same horizontal (length 6)", line(6)),
                        ("long horizontal (length 10)", line(10))):
        print(name)
        print(" P(query|reference, shared):", predictive_same(reference, query))
        print(" P(query|independent):     ", predictive_different(query))
        print(" Bayes factor:             ", bayes_factor(reference, query))
        print(" P(shared|pair), 50% prior:", posterior_same(reference, query))
