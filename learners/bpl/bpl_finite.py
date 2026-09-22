# A finite, exactly enumerable Bayesian drawing model inspired by BPL.

from collections import defaultdict
from fractions import Fraction
from itertools import product
from math import lcm
from random import Random

from bpl_minimal import CharacterType, StrokeSpec, Token, generate_token, render

# Type-level random variables. Each table is a normalized discrete distribution.
STROKE_COUNTS = ((1, Fraction(1, 3)), (2, Fraction(2, 3)))
ORIENTATIONS = (("horizontal", Fraction(3, 5)), ("vertical", Fraction(2, 5)))
LENGTH_PROFILES = (((4, 6), Fraction(2, 5)), ((8, 10), Fraction(3, 5)))
SECOND_RELATIONS = (("independent", Fraction(1, 4)), ("midpoint", Fraction(3, 4)))
CANVAS_WIDTH = 32
CANVAS_HEIGHT = 32


def weighted_choice(rng: Random, distribution: tuple):
    """Draw exactly from a rational, normalized categorical distribution."""
    if sum((p for _, p in distribution), Fraction(0)) != 1:
        raise ValueError("Distribution must sum to 1")
    denominator = lcm(*(prob.denominator for _, prob in distribution))
    ticket = rng.randrange(denominator)
    cumulative = 0
    for outcome, probability in distribution:
        cumulative += probability.numerator * (denominator // probability.denominator)
        if ticket < cumulative:
            return outcome
    raise AssertionError("Normalized categorical distribution had no selected outcome")


def generate_type(rng: Random) -> CharacterType:
    """Sample a type by ancestral sampling, not by drawing from a prebuilt list."""
    count = weighted_choice(rng, STROKE_COUNTS)
    specs = []
    for index in range(count):
        orientation = weighted_choice(rng, ORIENTATIONS)
        lengths = weighted_choice(rng, LENGTH_PROFILES)
        relation = "independent" if index == 0 else weighted_choice(rng, SECOND_RELATIONS)
        parent = 0 if relation == "midpoint" else None
        specs.append(StrokeSpec(orientation, lengths, parent, relation))
    return CharacterType(tuple(specs))


def enumerate_types() -> tuple[CharacterType, ...]:
    """Enumerate all structurally distinct types, independently of sampling."""
    first_options = tuple(
        StrokeSpec(orientation, lengths)
        for orientation, _ in ORIENTATIONS
        for lengths, _ in LENGTH_PROFILES
    )
    types = [CharacterType((first,)) for first in first_options]
    for first, orientation, lengths, relation in product(
        first_options,
        (o for o, _ in ORIENTATIONS),
        (lengths for lengths, _ in LENGTH_PROFILES),
        (r for r, _ in SECOND_RELATIONS),
    ):
        second = StrokeSpec(
            orientation, lengths,
            attach_to=0 if relation == "midpoint" else None,
            attachment=relation,
        )
        types.append(CharacterType((first, second)))
    return tuple(types)


def type_prior(character_type: CharacterType) -> Fraction:
    """Compute P(type) from factorized probabilities; zero outside the grammar."""
    strokes = character_type.strokes
    count = len(strokes)
    count_probs = dict(STROKE_COUNTS)
    orientation_probs = dict(ORIENTATIONS)
    profile_probs = dict(LENGTH_PROFILES)
    relation_probs = dict(SECOND_RELATIONS)
    if count not in count_probs:
        return Fraction(0)
    probability = count_probs[count]
    for index, spec in enumerate(strokes):
        if spec.orientation not in orientation_probs or spec.lengths not in profile_probs:
            return Fraction(0)
        if index == 0:
            if spec.attachment != "independent" or spec.attach_to is not None:
                return Fraction(0)
        elif spec.attachment not in relation_probs:
            return Fraction(0)
        elif spec.attach_to != (0 if spec.attachment == "midpoint" else None):
            return Fraction(0)
        probability *= orientation_probs[spec.orientation] * profile_probs[spec.lengths]
        if index > 0:
            probability *= relation_probs[spec.attachment]
    return probability


class _FixedChoices:
    """Adapter: run the existing token generator for enumerated length choices."""
    def __init__(self, lengths: tuple[int, ...]):
        self._lengths = iter(lengths)

    def choice(self, options: tuple[int, ...]) -> int:
        selected = next(self._lengths)
        if selected not in options:
            raise ValueError("Length outside the type's token distribution")
        return selected


def enumerate_token_outcomes(character_type: CharacterType) -> tuple[tuple[Token, Fraction], ...]:
    """Enumerate all token executions, with their exact probabilities."""
    if not type_prior(character_type):
        raise ValueError("Type is outside the finite model")
    options = [spec.lengths for spec in character_type.strokes]
    mass_per_choice = Fraction(1, 1)
    for choices in options:
        mass_per_choice /= len(choices)
    return tuple(
        (generate_token(character_type, _FixedChoices(lengths)), mass_per_choice)
        for lengths in product(*options)
    )


def sample_image(rng: Random) -> tuple[CharacterType, Token, str]:
    """Sample the complete ancestral chain: type -> token -> raster."""
    character_type = generate_type(rng)
    token = generate_token(character_type, rng)
    image = render(token, CANVAS_WIDTH, CANVAS_HEIGHT)
    return character_type, token, image


def image_likelihood(character_type: CharacterType, image: str) -> Fraction:
    """P(image|type): marginalize token choices, including raster collisions."""
    return sum(
        (mass for token, mass in enumerate_token_outcomes(character_type)
         if render(token, CANVAS_WIDTH, CANVAS_HEIGHT) == image),
        Fraction(0),
    )


def posterior_types(image: str) -> dict[CharacterType, Fraction]:
    """Exact P(type|image); zero-likelihood types are omitted."""
    joint = {
        character_type: type_prior(character_type) * image_likelihood(character_type, image)
        for character_type in enumerate_types()
    }
    evidence = sum(joint.values(), Fraction(0))
    if evidence == 0:
        raise ValueError("Observation has zero probability under this model")
    return {
        character_type: mass / evidence
        for character_type, mass in joint.items()
        if mass > 0
    }


def image_prior_probability(image: str) -> Fraction:
    """P(image), computed by exhaustive marginalization over types and tokens."""
    return sum(
        (type_prior(t) * image_likelihood(t, image) for t in enumerate_types()),
        Fraction(0),
    )


def image_distribution() -> dict[str, Fraction]:
    """Full prior predictive distribution; merge *images*, not latent types."""
    masses = defaultdict(Fraction)
    for character_type in enumerate_types():
        for token, token_prob in enumerate_token_outcomes(character_type):
            image = render(token, CANVAS_WIDTH, CANVAS_HEIGHT)
            masses[image] += type_prior(character_type) * token_prob
    return dict(masses)


if __name__ == "__main__":
    rng = Random(7)
    hypothesis_space = enumerate_types()
    print("Number of character types:", len(hypothesis_space))
    print("Sum of type-prior masses:", sum(map(type_prior, hypothesis_space), Fraction(0)))
    print("Unique rendered images:", len(image_distribution()))
    character_type, token, image = sample_image(rng)
    print("Sampled type:", character_type)
    print("Sampled token:", token)
    print("Sample image:\n", image, sep="")
    posterior = posterior_types(image)
    print("Posterior hypotheses with nonzero mass:", len(posterior))
    print("Posterior normalization:", sum(posterior.values(), Fraction(0)))
    print("Observed-image evidence P(I):", image_prior_probability(image))
