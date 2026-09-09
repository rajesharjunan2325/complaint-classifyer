"""Agreement calculation for a manually reviewed subset."""
def cohens_kappa(human, judge):
    assert len(human) == len(judge) and human
    observed = sum(left == right for left, right in zip(human, judge)) / len(human)
    labels = set(human) | set(judge)
    expected = sum((human.count(label) / len(human)) * (judge.count(label) / len(judge)) for label in labels)
    return round((observed - expected) / (1 - expected), 3) if expected != 1 else 1.0

HUMAN_SUBSET = [1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1]
JUDGE_SUBSET = [1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1]
