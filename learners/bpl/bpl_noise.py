"""Exact binary pixel-flip observation model for the finite BPL teaching model.

Images are 32x32 strings of '.' and '#', separated by newlines.
All likelihood calculations use fractions. Noise is conditional on a clean
rendering, not a replacement for token-level variation.
"""
from collections import defaultdict
from fractions import Fraction

from bpl_finite import (CANVAS_HEIGHT, CANVAS_WIDTH, enumerate_token_outcomes,
                        enumerate_types, type_prior)
from bpl_minimal import render

N_PIXELS = CANVAS_WIDTH * CANVAS_HEIGHT


def validate_image(image: str) -> str:
    """Return flattened binary pixels; reject malformed/out-of-model images."""
    if not isinstance(image, str):
        raise ValueError("Image must be a string")
    rows = image.split('\n')
    if len(rows) != CANVAS_HEIGHT or any(len(row) != CANVAS_WIDTH for row in rows):
        raise ValueError("Image dimensions must match the 32x32 canvas")
    flat = ''.join(rows)
    if any(pixel not in '.#' for pixel in flat):
        raise ValueError("Image pixels must be '.' or '#'")
    return flat


def validate_epsilon(epsilon) -> Fraction:
    """Require an exact rational epsilon in [0, 1]."""
    if not isinstance(epsilon, (Fraction, int)) or isinstance(epsilon, bool):
        raise ValueError("Use Fraction (or int) for exact noise probabilities")
    epsilon = Fraction(epsilon)
    if not 0 <= epsilon <= 1:
        raise ValueError("Noise probability must lie in [0, 1]")
    return epsilon


def hamming_distance(clean: str, observed: str) -> int:
    a, b = validate_image(clean), validate_image(observed)
    return sum(x != y for x, y in zip(a, b))


def pixel_flip_likelihood(clean: str, observed: str, epsilon: Fraction) -> Fraction:
    epsilon = validate_epsilon(epsilon)
    distance = hamming_distance(clean, observed)
    return epsilon ** distance * (1 - epsilon) ** (N_PIXELS - distance)


def noisy_image_likelihood(token, image: str, epsilon: Fraction) -> Fraction:
    """P(observed image | token): stochastic rendering with independent flips."""
    return pixel_flip_likelihood(render(token, CANVAS_WIDTH, CANVAS_HEIGHT), image, epsilon)


def _render_distribution(character_type):
    images = defaultdict(Fraction)
    for token, mass in enumerate_token_outcomes(character_type):
        images[render(token, CANVAS_WIDTH, CANVAS_HEIGHT)] += mass
    return images


def noisy_type_likelihood(character_type, image: str, epsilon: Fraction) -> Fraction:
    """P(image|type): marginalize all token executions, including collisions."""
    validate_image(image)
    epsilon = validate_epsilon(epsilon)
    return sum((mass * pixel_flip_likelihood(clean, image, epsilon)
                for clean, mass in _render_distribution(character_type).items()), Fraction(0))


def noisy_posterior_types(image: str, epsilon: Fraction):
    """Exact normalized posterior over types with nonzero mass."""
    validate_image(image)
    epsilon = validate_epsilon(epsilon)
    joint = {t: type_prior(t) * noisy_type_likelihood(t, image, epsilon)
             for t in enumerate_types()}
    evidence = sum(joint.values(), Fraction(0))
    if evidence == 0:
        raise ValueError("Observation has zero evidence")
    return {t: mass / evidence for t, mass in joint.items() if mass > 0}


def noisy_evidence(image: str, epsilon: Fraction) -> Fraction:
    validate_image(image)
    epsilon = validate_epsilon(epsilon)
    return sum((type_prior(t) * noisy_type_likelihood(t, image, epsilon)
                for t in enumerate_types()), Fraction(0))
