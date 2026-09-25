"""Supervisor-only audit primitives written from frozen revision 1.

No producer imports and no stationary solver. Row reconstruction is restricted
by the caller to the eight prospectively selected rows in each saved kernel.
Creating this module does not compute a study kernel or stationary outcome.
"""
from fractions import Fraction as F
from itertools import product

D = 377864847360
ALPHA = F(1, 3774873600)
ROWS = (0, 36, 85, 113, 142, 170, 219, 255)
KERNELS = ('ACTIVE_ZERO', 'ACTIVE_HALF', 'NEUTRAL_ZERO', 'NEUTRAL_HALF')


def decode(state):
    b = [(state >> i) & 1 for i in range(8)]
    return (tuple(b[:3]), tuple(b[3:6])), b[6], b[7]


def encode(first, second, a, b):
    bits = (*first, *second, a, b)
    return sum(x << i for i, x in enumerate(bits))


def reconstruct_row(state, kernel):
    """Direct rational branch enumeration, independent of producer layout."""
    if state not in ROWS or kernel not in KERNELS:
        raise ValueError('Outside the prospectively fixed audit scope')
    parents, a, b = decode(state)
    active = kernel.startswith('ACTIVE_')
    recurrent = kernel.endswith('_HALF')
    total = [F(0) for _ in range(256)]
    for target in (0, 1):
        p_target = F(3 if target == a else 1, 4) if recurrent else F(1, 2)
        for fresh0, fresh1, scout0, scout1, flip0, flip1 in product((0, 1), repeat=6):
            fresh = (fresh0, fresh1)
            scouts = (scout0, scout1)
            flips = (flip0, flip1)
            probes = [parents[i][1] if active and parents[i][2] else fresh[i] for i in range(2)]
            best = [target if target in (parents[i][0], probes[i], scouts[i]) else 1-target for i in range(2)]
            children = [best[i] ^ flips[i] for i in range(2)]
            candidates = list(parents)
            for family in (probes, scouts, children):
                candidates.extend((family[i], parents[i][0], parents[i][2]) for i in range(2))
            weights = [1 + (c[0] == target) for c in candidates]
            W = sum(weights)
            p_draws = p_target * F(1, 16)
            for flip in flips:
                p_draws *= F(1 if flip else 3, 4)
            for first in range(8):
                for second in range(8):
                    if first == second:
                        continue
                    p_selected = p_draws * F(weights[first], W) * F(weights[second], W-weights[first])
                    c0, c1 = candidates[first], candidates[second]
                    for switch0, switch1 in product((0, 1), repeat=2):
                        p_switch = F(1 if switch0 else 15, 16) * F(1 if switch1 else 15, 16)
                        dest = encode((c0[0], c0[1], c0[2] ^ switch0),
                                      (c1[0], c1[1], c1[2] ^ switch1), b, target)
                        total[dest] += p_selected * p_switch
    assert sum(total) == 1
    numerators = [x * D for x in total]
    assert all(x.denominator == 1 for x in numerators)
    return [int(x) for x in numerators]


def exact_certificate(A, k, denominator=D, alpha=ALPHA):
    """Recompute the residual with integers, without solving stationarity."""
    n = len(k)
    assert len(A) == n and all(len(row) == n for row in A)
    assert all(type(x) is int and x >= 0 for row in A for x in row)
    assert all(sum(row) == denominator for row in A)
    assert all(type(x) is int and x >= 0 for x in k)
    K = sum(k)
    assert K > 0
    R = sum(abs(sum(k[i] * A[i][j] for i in range(n)) - k[j]*denominator) for j in range(n))
    residual = F(R, K*denominator)
    return {'K': K, 'R': R, 'r': residual, 'E': min(F(1), residual/alpha)}


def verify_symmetries_and_support(A, kernel):
    assert len(A) == 256 and all(len(r) == 256 for r in A)
    assert all(sum(r) == D for r in A)
    masks = (219, 36) if kernel.startswith('NEUTRAL_') else (219,)
    for mask in masks:
        assert all(A[i][j] == A[i ^ mask][j ^ mask] for i in range(256) for j in range(256))
    # One SCC: reach all states from state zero in the forward and reverse graph.
    for reverse in (False, True):
        seen = {0}; stack = [0]
        while stack:
            i = stack.pop()
            for j in range(256):
                if (A[j][i] if reverse else A[i][j]) > 0 and j not in seen:
                    seen.add(j); stack.append(j)
        assert len(seen) == 256
    # In an irreducible finite chain a positive self-loop certifies period one.
    assert any(A[i][i] > 0 for i in range(256))


def outcomes(vectors, errors):
    """All 14 exact centers and numerical enclosures from saved rational p."""
    records = {}
    for kernel in KERNELS:
        k = vectors[kernel]; K = sum(k); E = errors[kernel]
        for metric in ('H', 'U'):
            twice_weighted_sum = 0
            for state, numerator in enumerate(k):
                parents, _, b = decode(state)
                reward2 = sum(p[2] for p in parents) if metric == 'H' else 2-sum(p[0] ^ b for p in parents)
                twice_weighted_sum += numerator * reward2
            center = F(twice_weighted_sum, 2*K)
            records[kernel+'|'+metric] = (center, max(F(0), center-E), min(F(1), center+E))
    contrasts = (
        ('ACTIVE_HALF_MINUS_ZERO|H', 'ACTIVE_HALF|H', 'ACTIVE_ZERO|H'),
        ('ACTIVE_ZERO_MINUS_HALF_SHARE|H', 'ACTIVE_ZERO|H', None),
        ('ACTIVE_HALF_MINUS_HALF_SHARE|H', 'ACTIVE_HALF|H', None),
        ('ACTIVE_HALF_MINUS_ZERO|U', 'ACTIVE_HALF|U', 'ACTIVE_ZERO|U'),
        ('ACTIVE_MINUS_NEUTRAL_ZERO|U', 'ACTIVE_ZERO|U', 'NEUTRAL_ZERO|U'),
        ('ACTIVE_MINUS_NEUTRAL_HALF|U', 'ACTIVE_HALF|U', 'NEUTRAL_HALF|U'),
    )
    for name, pos, neg in contrasts:
        center = records[pos][0] - (records[neg][0] if neg else F(1, 2))
        radius = errors[pos.split('|')[0]] + (errors[neg.split('|')[0]] if neg else 0)
        records[name] = (center, center-radius, center+radius)
    assert len(records) == 14
    for kernel in ('NEUTRAL_ZERO', 'NEUTRAL_HALF'):
        assert records[kernel+'|H'][1] <= F(1, 2) <= records[kernel+'|H'][2]
    return records


if __name__ == '__main__':
    # Constructed small-chain fixture only; not a study-061 calculation.
    cert = exact_certificate([[3, 1], [2, 2]], [2, 1], 4, F(1, 2))
    assert cert['R'] == 0 and cert['E'] == 0
    for state in range(256):
        parents, a, b = decode(state)
        assert encode(*parents, a, b) == state
    print('PASS: independent audit primitives, codec and constructed certificate fixture; no production rows or outcomes evaluated.')
