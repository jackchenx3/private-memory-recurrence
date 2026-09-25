#!/usr/bin/env python3
"""Portable access to fixed study061. Default: tiny fixtures, never a full solve.

CPython3.9+; standard library only. See docs/PORTABLE_STATIONARY061.md.
"""
import argparse
import contextlib
import gzip
import hashlib
import importlib.util
import json
import multiprocessing
from pathlib import Path
import runpy
import sys
import time
import traceback
from fractions import Fraction

ROOT = Path(__file__).resolve().parents[1]
KERNELS = ('ACTIVE_ZERO', 'ACTIVE_HALF', 'NEUTRAL_ZERO', 'NEUTRAL_HALF')
TIME_LIMIT_SECONDS = 1800
OUTPUT_LIMIT_BYTES = 64 * 1024 * 1024


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def authenticate(root):
    binding = json.loads((root / 'tools/stationary061_sources.json').read_text())
    if binding['baseline_commit'] != '651c4289b1ac34efb30d1a81560e88cd74b1609f':
        raise ValueError('Unexpected scientific baseline')
    for name, expected in binding['files'].items():
        if digest(root / name) != expected:
            raise ValueError('Published source changed: ' + name)
    return binding


@contextlib.contextmanager
def operators(root):
    """Scope the original absolute numerics import; leave no aliases or bytecode."""
    previous = {name: sys.modules.get(name) for name in ('kernel', 'numerics', 'outcomes')}
    bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    loaded = {}
    try:
        for name in ('kernel', 'numerics', 'outcomes'):
            spec = importlib.util.spec_from_file_location(name, root / ('code/061/' + name + '.py'))
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            loaded[name] = module
        if tuple(loaded['kernel'].KERNELS) != KERNELS or tuple(loaded['outcomes'].KERNELS) != KERNELS:
            raise ValueError('Kernel catalog differs from frozen specification')
        if loaded['numerics'].PRECISION != 80 or loaded['numerics'].GRID_DIGITS != 60:
            raise ValueError('Numerical precision differs from frozen specification')
        yield loaded['kernel'], loaded['numerics'], loaded['outcomes']
    finally:
        sys.dont_write_bytecode = bytecode
        for name, module in previous.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module


def reserve_output(path, root):
    output = Path(path).expanduser().resolve()
    root = root.resolve()
    if output == root or root in output.parents:
        rebuilt = root / '_rebuilt'
        if output == rebuilt or rebuilt not in output.parents:
            raise ValueError('Use a new directory outside the repository or below _rebuilt/')
    if output in root.parents:
        raise ValueError('Output cannot contain the repository')
    # Even an empty existing directory is rejected. No resume or automatic retry.
    output.mkdir(parents=True, exist_ok=False)
    return output


class Store:
    def __init__(self, directory):
        self.directory = Path(directory)

    def save(self, name, value):
        relative = Path(name)
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError('Output name must be relative')
        path = self.directory / relative
        if path.exists():
            raise FileExistsError('Refusing to replace output: ' + name)
        data = (json.dumps(value, indent=2, allow_nan=False) + '\n').encode()
        if path.suffix == '.gz':
            data = gzip.compress(data, compresslevel=6, mtime=0)
        used = sum(p.stat().st_size for p in self.directory.rglob('*') if p.is_file())
        if used + len(data) > OUTPUT_LIMIT_BYTES - 16384:
            raise ValueError('64 MiB output limit reached; no write performed')
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as stream:
            stream.write(data)


def smoke(kernel, numerics, outcomes):
    """Analytic two-state fixture plus constructed outcome inputs, no study rows."""
    A = [[3, 1], [2, 2]]
    solution = numerics.solve(A, 4)
    weights = numerics.rounded_weights(solution)
    certificate = numerics.certify(A, 4, weights, Fraction(1, 2))
    error = numerics.from_rational(certificate['total_variation_bound'])
    if not certificate['criterion_pass'] or abs(Fraction(weights[0], sum(weights)) - Fraction(2, 3)) > error:
        raise AssertionError('Analytic two-state fixture failed')
    for state in (0, 36, 255):
        if kernel.encode(kernel.decode(state)) != state:
            raise AssertionError('State encoding fixture failed')
    rejected = {name: {'status': 'REJECTED', 'reason': 'constructed rejection fixture'} for name in KERNELS}
    unavailable = outcomes.calculate(rejected)
    if len(unavailable) != 14 or any(q['status'] != 'UNAVAILABLE' for q in unavailable.values()):
        raise AssertionError('Unavailable-outcome propagation failed')
    return dict(status='PASS',mode='smoke',constructed_two_state_solves=1,
                analytic_stationary_probability='2/3',rejected_outcome_fixture_records=14,
                production_rows=0,production_stationary_solves=0,population_paths=0,
                scope='Constructed fixtures only; not full scientific regeneration.')


def generate_one(name, kernel, numerics, store, states=range(256)):
    """Fixed production caller uses256 states; tiny fixtures can test wiring."""
    store.save('receipts/' + name + '-intent.json', dict(kernel=name, matrix_attempts=1, automatic_retry=False))
    A = [kernel.row(state, name) for state in states]
    checks = kernel.check_matrix(A, name)
    store.save('matrices/' + name + '.json.gz',dict(kernel=name,denominator=kernel.D,numerators=A,state_order='increasing ID0..255'))
    store.save('receipts/' + name + '-solve-intent.json',dict(attempts=1,precision=80,grid_digits=60,automatic_retry=False))
    try:
        solution = numerics.solve(A, kernel.D)
        store.save('solutions/' + name + '.json.gz',solution)
        k = numerics.rounded_weights(solution)
        certificate = numerics.certify(A, kernel.D, k)
        vector = dict(status='COMPUTED',kernel=name,k=[str(x) for x in k],certificate=certificate,solution=solution)
        if name.startswith('NEUTRAL'):
            K = int(certificate['K'])
            center = Fraction(sum(x * (((s >> 2) & 1) + ((s >> 5) & 1)) for s,x in enumerate(k)), 2*K)
            error = numerics.from_rational(certificate['total_variation_bound'])
            if not center-error <= Fraction(1,2) <= center+error:
                raise AssertionError('Neutral H symmetry/certificate contradiction')
    except Exception as error:
        # Same rejection/retention policy as the archived producer; never a retry.
        vector = dict(status='REJECTED',kernel=name,reason=str(error),traceback=traceback.format_exc()[-12000:],precision=80,grid_digits=60,automatic_retry=False)
    store.save('vectors/' + name + '.json.gz',vector)
    return vector, checks


def regenerate(kernel, numerics, outcomes, store):
    vectors = {}
    checks = {}
    for name in KERNELS:
        vectors[name], checks[name] = generate_one(name,kernel,numerics,store)
    records = outcomes.calculate(vectors)
    store.save('OUTCOMES.json',records)
    store.save('ASSESSMENT.json',outcomes.assess(records))
    store.save('MATRIX_CHECKS.json',checks)
    certified = sum(v.get('certificate',{}).get('criterion_pass',False) and v['status']=='COMPUTED' for v in vectors.values())
    return dict(status='PASS' if certified==4 else 'NUMERICAL_CERTIFICATION_FAILED',mode='regenerate',
                production_rows=1024,production_stationary_solve_attempts=4,certified_vectors=certified,
                mathematical_records=14,population_paths=0,random_draws=0,
                scope='Fixed original operators; no rate grid, precision fallback or empirical replication.')


def verify_saved(root, store):
    """Reuse the existing public checker, redirected into the fresh output folder."""
    prior_argv, prior_path = sys.argv[:], sys.path[:]
    prior_module = sys.modules.get('stationary061_audit_core')
    bytecode = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        sys.path.insert(0,str(root/'scripts'))
        sys.modules.pop('stationary061_audit_core',None)
        target = store.directory/'SAVED_CERTIFICATES_CHECK.json'
        sys.argv = [str(root/'scripts/check_061_certificates.py'),'--output',str(target)]
        runpy.run_path(sys.argv[0],run_name='__main__')
        result = json.loads(target.read_text())
        if result['status']!='PASS' or result['records']!=14 or result['stationary_solves']!=0:
            raise AssertionError('Saved-certificate checker did not pass')
        return dict(status='PASS',mode='verify-saved',certified_mathematical_records=14,
                    production_rows=0,production_stationary_solves=0,population_paths=0,
                    scope='Verification of archived inputs; not regeneration or independent empirical replication.')
    finally:
        sys.argv,sys.path = prior_argv,prior_path
        sys.dont_write_bytecode = bytecode
        if prior_module is None:
            sys.modules.pop('stationary061_audit_core',None)
        else:
            sys.modules['stationary061_audit_core'] = prior_module


def worker(mode, root_name, output_name):
    root, output = Path(root_name), Path(output_name)
    store = Store(output)
    try:
        authenticate(root)
        if mode == 'verify-saved':
            result = verify_saved(root,store)
        else:
            with operators(root) as (kernel,numerics,outcomes):
                result = smoke(kernel,numerics,outcomes) if mode=='smoke' else regenerate(kernel,numerics,outcomes,store)
        store.save('RESULT.json',result)
        if result['status']!='PASS':
            raise SystemExit(2)
    except Exception as error:
        try:
            store.save('FAILURE.json',dict(status='FAILED',error=str(error),traceback=traceback.format_exc()[-12000:],automatic_retry=False))
        except Exception:
            pass  # Parent still reports the failure if the output budget is exhausted.
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode',choices=('smoke','verify-saved','regenerate'),default='smoke')
    parser.add_argument('--output',required=True,help='New directory, outside source/evidence; existing directories are refused')
    args = parser.parse_args(argv)
    if not __debug__:
        parser.error('Do not use -O or PYTHONOPTIMIZE; original operator assertions are required')
    binding = authenticate(ROOT)
    output = reserve_output(args.output,ROOT)
    store = Store(output)
    store.save('REQUEST.json',dict(mode=args.mode,baseline_commit=binding['baseline_commit'],source_files=binding['files'],
                                  wrapper_sha256=digest(Path(__file__)),python=sys.version,time_limit_seconds=TIME_LIMIT_SECONDS,
                                  output_limit_bytes=OUTPUT_LIMIT_BYTES,automatic_retry=False))
    start = time.monotonic()
    process = multiprocessing.get_context('spawn').Process(target=worker,args=(args.mode,str(ROOT),str(output)))
    process.start()
    process.join(TIME_LIMIT_SECONDS)
    timed_out = process.is_alive()
    if timed_out:
        process.terminate();process.join(5)
        if process.is_alive():
            process.kill();process.join()
    result_path = output/'RESULT.json'
    passed = not timed_out and process.exitcode==0 and result_path.is_file()
    summary = dict(status='PASS' if passed else 'TIME_LIMIT' if timed_out else 'FAILED',mode=args.mode,
                   worker_exitcode=process.exitcode,elapsed_seconds=time.monotonic()-start,automatic_retry=False,
                   full_regeneration_requested=args.mode=='regenerate',production_execution_success=passed and args.mode=='regenerate')
    # Tiny terminal receipt is reserved independently so budget/worker failure remains visible.
    with (output/'STATUS.json').open('x') as stream:
        json.dump(summary,stream,indent=2);stream.write('\n')
    print(json.dumps(summary))
    return 0 if passed else 1


if __name__=='__main__':
    raise SystemExit(main())
