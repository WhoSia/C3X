"""Compare pinned original SARFA with C3X on shared-support synthetic fixtures."""
import argparse
from contextlib import redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import random

from scipy.special import softmax
from scipy.stats import entropy

from c3x_030_r1_sarfa_logdomain import sarfa_logdomain

def compare(path):
    spec = importlib.util.spec_from_file_location("original_sarfa", path)
    upstream = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(upstream)
    rng = random.Random(20261114)
    errors = []
    directional_errors = []
    for _ in range(256):
        keys = ("a", "b", "c", "d")
        old = {key: rng.uniform(-5, 5) for key in keys}
        new = {key: old[key] + rng.uniform(-3, 3) for key in keys}
        ours = sarfa_logdomain(old, new, "a")
        with redirect_stdout(io.StringIO()):
            score, delta, relevance, *_ = upstream.computeSaliencyUsingSarfa("a", old, new)
        old_other = softmax([old[k] for k in keys if k != "a"])
        new_other = softmax([new[k] for k in keys if k != "a"])
        directional_errors.append([
            abs(float(relevance) - 1 / (1 + entropy(old_other, new_other))),
            abs(ours["offtarget_relevance"] - 1 / (1 + entropy(new_other, old_other))),
        ])
        errors.append([abs(float(score) - ours["sarfa_harmonic_saliency"]),
                       abs(float(delta) - ours["specificity_delta_raw_signed"]),
                       abs(float(relevance) - ours["offtarget_relevance"])])
    return dict(fixtures=len(errors), max_absolute_deltas=list(map(max, zip(*errors))),
                kl_direction_reconstruction_errors=list(map(max, zip(*directional_errors))))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("upstream", type=Path)
    print(json.dumps(compare(parser.parse_args().upstream), indent=2))
