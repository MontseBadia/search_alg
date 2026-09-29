from learning_setup import TRAINING_DATA, TEST_OBJECTS, hidden_concept

from exemplar import exemplar_predict, hamming_distance
from prototype import make_prototypes, predict_with_prototypes, euclidean_distance
from bayesian import enumerate_hypotheses, posterior, bayesian_predict
from neural import train, predict



# ---------------------------------------------------------
# EXPLANATION HELPERS
# ---------------------------------------------------------

def exemplar_explain(training_data, query):
    nearest = min(training_data, key=lambda item: hamming_distance(item[0], query))

    return {
        "prediction": nearest[1],
        "nearest_example": nearest[0],
        "distance": hamming_distance(nearest[0], query),
    }

def prototype_explain(prototypes, query):
    return [
        {
            "label": label,
            "prototype": prototype,
            "distance": euclidean_distance(prototype, query)
        }
        for prototype, label in prototypes
    ]

def bayesian_explain(hypotheses, probabilities, query):
    p_true = bayesian_predict(hypotheses, probabilities, query)

    return {
        "p_true": p_true,
        "p_false": 1 - p_true,
    }


# ---------------------------------------------------------
# MAIN COMPARISON
# ---------------------------------------------------------

def run_comparison():
    threshold = 0.5

    # Prototype
    prototypes = make_prototypes(TRAINING_DATA)

    # Bayesian
    hypotheses, _ = enumerate_hypotheses()
    bayesian_probabilities = posterior(hypotheses, TRAINING_DATA, length_prior=True)

    # Neural
    trained_params = train(TRAINING_DATA, epochs=2000, learning_rate=0.1, seed=7, verbose=False, log_every=200)

    correct_exemplar = 0
    correct_prototype = 0
    correct_bayesian = 0
    correct_neural = 0

    brier_bayesian = 0.0
    brier_neural = 0.0

    disagreements = []

    print("\nquery          truth  exemplar  prototype  bayes P  bayes  neural P  neural")

    for x in TEST_OBJECTS:
        truth = hidden_concept(x)
        target = float(truth)

        # Exemplar
        prediction_exemplar = exemplar_predict(TRAINING_DATA, x)
        correct_exemplar += prediction_exemplar == truth

        # Prototype
        prediction_prototype = predict_with_prototypes(prototypes, x)
        correct_prototype += prediction_prototype == truth

        # Bayesian
        bayesian_p_true = bayesian_predict(hypotheses, bayesian_probabilities, x)
        prediction_bayesian = bayesian_p_true >= threshold
        correct_bayesian += prediction_bayesian == truth
        brier_bayesian += (bayesian_p_true - target) ** 2

        # Neural
        neural_p_true, prediction_neural, hidden_activations = predict(trained_params, x, threshold)
        correct_neural += prediction_neural == truth
        brier_neural += (neural_p_true - target) ** 2

        # Disagreements
        # It means disagreement between learners, not against ground truth
        predictions = {prediction_exemplar, prediction_prototype, prediction_bayesian, prediction_neural}
        if len(predictions) > 1:
            disagreements.append(
                {
                    "object": x,
                    "truth": truth,
                    "exemplar": prediction_exemplar,
                    "prototype": prediction_prototype,
                    "bayesian": prediction_bayesian,
                    "bayesian_p": bayesian_p_true,
                    "neural": prediction_neural,
                    "neural_p": neural_p_true,
                    "hidden": hidden_activations,
                }
            )

        print(
            f"{str(x):14} "
            f"{str(truth):5} "
            f"{str(prediction_exemplar):8} "
            f"{str(prediction_prototype):9} "
            f"{bayesian_p_true:7.3f} "
            f"{str(prediction_bayesian):6} "
            f"{neural_p_true:8.3f} "
            f"{prediction_neural}"
        )


    # Accuracy
    total = len(TEST_OBJECTS)
    print(f"\nAccuracy Exemplar: {correct_exemplar}/{total}")
    print(f"Accuracy Prototype: {correct_prototype}/{total}")
    print(f"Accuracy Bayesian: {correct_bayesian}/{total}")
    print(f"Accuracy Neural: {correct_neural}/{total}\n")


    # Brier
    # The lower, the better
    brier_bayesian /= total
    brier_neural /= total
    print(f"Brier Bayesian: {brier_bayesian}")
    print(f"Brier Neural: {brier_neural}\n")


    # Disagreement
    print("\n-- Disagreement Analysis --")
    for item in disagreements:
        x = item["object"]

        print("\n================================")
        print(f"Object: {x}")
        print(f"Truth:  {item['truth']}")
        print("================================")

        # --- Exemplar Explanation ----
        exemplar_exp = exemplar_explain(TRAINING_DATA, x)
        print("\nExemplar")
        print(f"  prediction:      {exemplar_exp['prediction']}")
        print(f"  nearest example: {exemplar_exp['nearest_example']}")
        print(f"  distance:        {exemplar_exp['distance']}")

        # --- Prototype Explanation ----
        print("\nPrototype")
        print(f"  prediction: {item['prototype']}")
        for result in prototype_explain(prototypes, x):
            print(f"  label={result['label']:<5} distance={result['distance']:.3f} prototype={result['prototype']}")

        # --- Bayesian Explanation ----
        bayesian_exp = bayesian_explain(hypotheses, bayesian_probabilities, x)
        print("\nBayesian")
        print(f"  prediction: {item['bayesian']}")
        print(f"  P(True):  {bayesian_exp['p_true']:.3f}")
        print(f"  P(False): {bayesian_exp['p_false']:.3f}")

        # --- Neural Explanation ----
        print("\nNeural")
        print(f"  prediction: {item['neural']}")
        print(f"  P(True):    {item['neural_p']:.3f}")
        hidden_rounded = [round(value, 3) for value in item["hidden"]]
        print(f"  hidden:     {hidden_rounded}")





if __name__ == "__main__":
    run_comparison()
