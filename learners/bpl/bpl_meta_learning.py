"""A tiny exact learning-to-learn experiment inspired by BPL, not its training code.

Learn a shared token-variation parameter from *background* character tokens,
then transfer the inferred distribution to a new character type.
Run: python bpl_meta_learning.py
"""
from fractions import Fraction

SHORT = (4, 6)
LONG = (8, 10)
LENGTHS = SHORT + LONG
DELTA_VALUES = (Fraction(0), Fraction(1, 10), Fraction(1, 4), Fraction(1, 2))
DELTA_PRIOR = {delta: Fraction(1, len(DELTA_VALUES)) for delta in DELTA_VALUES}
HALF = Fraction(1, 2)
ZERO = Fraction(0)


def length_probability(profile, length, delta):
    """P(execution length | known type profile, shared variation parameter)."""
    if profile not in (SHORT, LONG) or length not in LENGTHS:
        raise ValueError("Invalid profile or length")
    if not ZERO <= delta <= 1:
        raise ValueError("Variation parameter outside [0, 1]")
    return (1 - delta) / 2 if length in profile else delta / 2


def posterior_delta(background, delta_prior=DELTA_PRIOR):
    """Exact P(delta | clean background lengths and KNOWN type profiles).

    background is a sequence of (profile, measured_length) pairs. Do not feed
    the new concept's observation here: background is the transfer source.
    """
    if not background:
        raise ValueError("Need background examples")
    if not delta_prior or any(prob < 0 for prob in delta_prior.values()) or sum(delta_prior.values()) != 1:
        raise ValueError("Parameter prior must be normalized")
    unnormalized = {}
    for delta, prior in delta_prior.items():
        mass = prior
        for profile, length in background:
            mass *= length_probability(profile, length, delta)
        unnormalized[delta] = mass
    evidence = sum(unnormalized.values(), ZERO)
    if evidence == 0:
        raise ValueError("Zero background evidence")
    return {delta: mass / evidence for delta, mass in unnormalized.items()}


def predictive_length(profile, length, delta_distribution):
    """Integrate uncertainty over delta rather than choosing a best delta."""
    return sum((mass * length_probability(profile, length, delta)
                for delta, mass in delta_distribution.items()), ZERO)


def posterior_new_type(length, delta_distribution):
    """One-shot posterior over previously unseen short/long types, 50/50 prior."""
    weights = {profile: HALF * predictive_length(profile, length, delta_distribution)
               for profile in (SHORT, LONG)}
    total = sum(weights.values(), ZERO)
    if total == 0:
        raise ValueError("New example impossible")
    return {profile: mass / total for profile, mass in weights.items()}


# Two background concepts with KNOWN profiles and several clean executions each.
# Short: 8 in-profile executions, 2 outside. Long: 10 in-profile executions.
BACKGROUND = tuple((SHORT, n) for n in (4, 6, 4, 6, 4, 6, 4, 6, 8, 10)) + \
             tuple((LONG, n) for n in (8, 10, 8, 10, 8, 10, 8, 10, 8, 10))


def experiment():
    learned = posterior_delta(BACKGROUND)
    prior_mean = sum((d * p for d, p in DELTA_PRIOR.items()), ZERO)
    posterior_mean = sum((d * p for d, p in learned.items()), ZERO)
    print("Background: 18 in-profile, 2 out-of-profile executions")
    print(f"E[delta] before learning = {float(prior_mean):.6f}")
    for delta, weight in learned.items():
        print(f"P(delta={float(delta):.2f} | background) = {float(weight):.6f}")
    print(f"E[delta] after learning  = {float(posterior_mean):.6f}")
    print(f"P(length=10 | new SHORT type) before = {float(predictive_length(SHORT, 10, DELTA_PRIOR)):.6f}")
    print(f"P(length=10 | new SHORT type) after  = {float(predictive_length(SHORT, 10, learned)):.6f}")
    print(f"P(new type=LONG | one length-10 example) before = {float(posterior_new_type(10, DELTA_PRIOR)[LONG]):.6f}")
    print(f"P(new type=LONG | one length-10 example) after  = {float(posterior_new_type(10, learned)[LONG]):.6f}")


if __name__ == "__main__":
    experiment()
