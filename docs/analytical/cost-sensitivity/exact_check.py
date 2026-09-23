"""Finite rational checks of the cost-sensitivity algebra; no population model."""
from fractions import Fraction as F
from itertools import combinations, permutations, product
import json
import math

counts = {}


def check(condition, category):
    assert condition, category
    counts[category] = counts.get(category, 0) + 1


base = (F(1), F(2), F(3), F(5))
scales = tuple(map(F, ('1/16', '1/4', '1/2', '1', '2', '4', '16')))
for j in range(1001):
    p = F(j, 1000)
    check(0 <= p * (1-p) <= F(1, 4), 'bernoulli_derivative_bound')

for tags in product((0, 1), repeat=4):
    for size in range(1, 5):
        for remain in combinations(range(4), size):
            vectors = []
            for z in scales:
                weights = {i: base[i] * (z if tags[i] else 1) for i in remain}
                total = sum(weights.values())
                probabilities = {i: weights[i] / total for i in remain}
                p = sum(probabilities[i] for i in remain if tags[i])
                # theta = -log(z); derivative of log(weight_i) is -tags[i].
                derivative = {i: probabilities[i] * (p-tags[i]) for i in remain}
                check(sum(probabilities.values()) == 1, 'one_draw_normalization')
                check(sum(derivative.values()) == 0, 'one_draw_derivative_mass')
                check(sum(abs(x) for x in derivative.values()) / 2 == p*(1-p),
                      'one_draw_total_variation_derivative')
                vectors.append((probabilities, p))
            for (a, pa), (b, pb) in combinations(vectors, 2):
                check(sum(abs(a[i]-b[i]) for i in remain)/2 == abs(pa-pb),
                      'group_mixture_total_variation_identity')

    # Enumerate probability vectors of ordered selections, not realized trajectories.
    for z in scales:
        weights = [base[i]*(z if tags[i] else 1) for i in range(4)]
        for k in range(1, 5):
            masses, derivatives = [], []
            for ordered in permutations(range(4), k):
                remain = set(range(4))
                mass, logarithmic_derivative = F(1), F(0)
                for i in ordered:
                    total = sum(weights[j] for j in remain)
                    p = sum(weights[j] for j in remain if tags[j])/total
                    mass *= weights[i]/total
                    logarithmic_derivative += p-tags[i]
                    remain.remove(i)
                masses.append(mass)
                derivatives.append(mass*logarithmic_derivative)
            check(sum(masses) == 1, 'ordered_sampling_normalization')
            check(sum(derivatives) == 0, 'ordered_sampling_derivative_mass')
            check(sum(abs(x) for x in derivatives)/2 <= F(k, 4),
                  'ordered_sampling_derivative_bound')

# A finite grid need not give continuity at a cross-group tie. With equal
# base weights and deterministic carrier-first tie breaking, cost zero
# chooses the carrier when its uniform is at least the resident uniform;
# infinitesimal positive cost removes the equal-word cases. This is a
# two-entry, one-draw probability count, not an experimental model run.
for m in range(1, 33):
    equal = sum(i == j for i in range(m) for j in range(m))
    at_zero = F(sum(i >= j for i in range(m) for j in range(m)), m*m)
    right_limit = F(sum(i > j for i in range(m) for j in range(m)), m*m)
    check(equal == m and at_zero-right_limit == F(1, m),
          'finite_grid_discontinuity_example')

result = dict(status='PASS', exact_checks=sum(counts.values()), categories=counts,
              sampling_probability_vectors='four abstract weighted entries, all tag patterns',
              random_draws=0, objective_calls=0, propagated_population_paths=0,
              K=32, T=40, ideal_lipschitz_constant=320*math.log(2),
              scope='Rational algebra checks support the explicit proof; not a population result or finite-grid approximation bound.')
if __name__ == '__main__':
    print(json.dumps(result, indent=2))
