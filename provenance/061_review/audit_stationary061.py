"""Focused saved-output audit. Never imports producer code or solves stationarity."""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal
from datetime import datetime, timezone
import json, gzip, hashlib, time
from stationary061_independent_core import (
    D, ALPHA, ROWS, KERNELS, reconstruct_row, exact_certificate,
    verify_symmetries_and_support, outcomes)

ROOT = Path(__file__).resolve().parents[1]
P = ROOT.parent/'you-are-responsible-for-implementing-the/outputs/stationary_policy_v1'
OUT = ROOT/'outputs/org-stationary-061-review'
OUT.mkdir(exist_ok=True)

def read(path):
    path = Path(path)
    if path.suffix == '.gz':
        with gzip.open(path, 'rt') as f:
            return json.load(f)
    return json.loads(path.read_text())

def rational(record):
    return F(int(record['numerator']), int(record['denominator']))

def verify_manifest(name):
    count = 0
    for line in (P/name).read_text().splitlines():
        expected, rel = line.split('  ', 1)
        assert hashlib.sha256((P/rel).read_bytes()).hexdigest() == expected, rel
        count += 1
    return count

def nearest_even(q):
    integer, remainder = divmod(q.numerator, q.denominator)
    return integer + int(2*remainder > q.denominator or
                         (2*remainder == q.denominator and integer % 2 == 1))

def main():
    assert not (OUT/'AUDIT.json').exists(), 'Completed audit already exists; read its receipt'
    started = time.monotonic()
    verified = {n: verify_manifest(n) for n in ('SOURCE_SHA256SUMS','SCIENCE_SHA256SUMS','RESULT_SHA256SUMS')}
    assert read(P/'LIVE_RESULT.json')['status'] == 'COMPLETE'
    frozen = read(ROOT/'outputs/coordination/CURRENT_TASK.json')
    assert hashlib.sha256((P/'ASSIGNMENT.md').read_bytes()).hexdigest() == frozen['task_sha256']
    reconstructed = {}; vectors = {}; errors = {}; certificates = {}
    for kernel in KERNELS:
        stored = read(P/'matrices'/f'{kernel}.json.gz')
        assert stored['denominator'] == D
        A = stored['numerators']
        verify_symmetries_and_support(A, kernel)
        reconstructed[kernel] = {}
        for row in ROWS:
            expected = reconstruct_row(row, kernel)
            assert expected == A[row], (kernel, row, 'independent transition mismatch')
            reconstructed[kernel][str(row)] = expected
        v = read(P/'vectors'/f'{kernel}.json.gz')
        assert v['status'] == 'COMPUTED', (kernel, 'Preserved numerical rejection; no new solve')
        k = [int(x) for x in v['k']]
        assert len(k) == 256
        sol = v['solution']
        assert sol['precision_digits'] == 80 and sol['grid_digits'] == 60
        raw = [F(Decimal(x)) for x in sol['normalized_decimal']]
        assert min(raw) >= 0
        assert [nearest_even(x*10**60) for x in raw] == k
        cert = exact_certificate(A, k)
        saved = v['certificate']
        assert int(saved['K']) == cert['K'] and int(saved['R']) == cert['R']
        assert rational(saved['residual']) == cert['r']
        assert rational(saved['alpha']) == ALPHA
        assert rational(saved['total_variation_bound']) == cert['E']
        assert rational(saved['criterion']) == F(1,10**30)
        assert saved['criterion_pass'] == (cert['r'] <= F(1,10**30))
        assert saved['criterion_pass'], (kernel, 'Preserved fixed numerical-criterion failure')
        vectors[kernel] = k; errors[kernel] = cert['E']
        certificates[kernel] = {key:str(value) for key,value in cert.items()}
        print(json.dumps({'kernel':kernel,'independent_rows':8,'certificate':'PASS'}),flush=True)
    calculated = outcomes(vectors, errors)
    actual = read(P/'OUTCOMES.json')
    assert set(actual) == set(calculated) and len(actual) == 14
    for key, (center, lower, upper) in calculated.items():
        q = actual[key]
        assert tuple(rational(q[x]) for x in ('center','lower','upper')) == (center,lower,upper), key
        assert q['status'] == 'CERTIFIED'
        sign = 'positive' if lower > 0 else 'negative' if upper < 0 else 'contains_zero'
        assert q['sign'] == sign, key
        for scale,lofield,hifield in ((1,'lower_decimal','upper_decimal'),
                                      (100,'lower_percentage_points','upper_percentage_points')):
            assert F(Decimal(q[lofield])) <= scale*lower
            assert F(Decimal(q[hifield])) >= scale*upper
        radius = errors[key.split('|')[0]] if key.split('|')[0] in KERNELS else None
        if radius is None:
            if key == 'ACTIVE_ZERO_MINUS_HALF_SHARE|H': radius = errors['ACTIVE_ZERO']
            elif key == 'ACTIVE_HALF_MINUS_HALF_SHARE|H': radius = errors['ACTIVE_HALF']
            elif key.startswith('ACTIVE_HALF_MINUS_ZERO|'): radius = errors['ACTIVE_HALF']+errors['ACTIVE_ZERO']
            elif key == 'ACTIVE_MINUS_NEUTRAL_ZERO|U': radius = errors['ACTIVE_ZERO']+errors['NEUTRAL_ZERO']
            else: radius = errors['ACTIVE_HALF']+errors['NEUTRAL_HALF']
        assert rational(q['radius']) == radius
    primary = actual['ACTIVE_HALF_MINUS_ZERO|H']
    expected_decision = {'positive':'supports_positive','negative':'contradicts_positive','contains_zero':'sign_uncertified'}[primary['sign']]
    assert read(P/'ASSESSMENT.json')['decision'] == expected_decision
    with gzip.open(OUT/'SUPERVISOR_RECONSTRUCTED_ROWS.json.gz','wt') as f:
        json.dump(reconstructed,f,separators=(',',':'))
    receipt = {'task_id':'ORG-STATIONARY-061','status':'PASS',
        'completed_at_utc':datetime.now(timezone.utc).isoformat(),
        'job_id':read(P/'LIVE_RESULT.json')['job_id'], 'elapsed_seconds':time.monotonic()-started,
        'verified_manifests':verified,'independent_rows':32,'independent_numerators':8192,
        'exact_certificates':4,'saved_outcomes':14,'repeated_stationary_solves':0,
        'producer_imports':0,'support_and_global_symmetry_kernels':4,'neutral_policy_symmetry_kernels':2,
        'rounded_vector_entries_checked':1024,'outward_endpoint_checks':56,
        'certificates':certificates,'primary_decision':expected_decision,
        'primary_center_pp':primary['center_percentage_points'],
        'source_manifest_sha256':hashlib.sha256((P/'SOURCE_SHA256SUMS').read_bytes()).hexdigest(),
        'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'core_sha256':hashlib.sha256((ROOT/'work/stationary061_independent_core.py').read_bytes()).hexdigest()}
    (OUT/'AUDIT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (P/'SUPERVISOR_AUDIT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k not in ('certificates','verified_manifests')}),flush=True)

if __name__ == '__main__':
    main()
