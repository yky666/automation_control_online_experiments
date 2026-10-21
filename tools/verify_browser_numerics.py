"""Compare actual browser traces with independent continuous-time SciPy responses.

Run after npm run export:online. Does not require MATLAB or claim native validation.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import scipy
from scipy.signal import lsim

ROOT = Path(__file__).resolve().parents[1]


def reference(case, run):
    t, u = np.asarray(run['time']), np.asarray(run['input'])
    num, den = case['num'], case['den']
    mask = np.ones(t.size, dtype=bool)
    if case['kind'] == 'circuit':
        lab, task, p = case['lab'], case['task'], case['params']
        if lab == 2:
            gain, tau = abs(p['K']), p.get('T', .1)
            if task in ('d', 'pd'):
                rise = case['settings']['rise']
                derivative = np.where((t > 0) & (t < rise), case['settings']['amplitude'] / rise, 0)
                y = -gain * (tau * derivative + (u if task == 'pd' else 0))
                # Ideal derivative is discontinuous at the ramp corners.
                mask = (t > t[2]) & (np.abs(t - rise) > 2 * (t[1] - t[0]))
                return y, mask
            num = -np.abs(num)
        elif lab == 5 and task == 'bandwidth':
            # Two inverting finite-open-loop-gain stages, each A(s)=A0/(tau*s+1).
            a, gbw, k = case['opamp']['A0'], case['opamp']['GBW'], p['K']
            tau = a / (2 * np.pi * gbw)
            num = [a * a * k / ((a + 1 + k) * (a + 2))]
            den = np.convolve([tau / (a + 1 + k), 1], [tau / (a + 2), 1])
        elif lab == 5:
            num = -np.asarray(num)  # Actual course circuits are inverting.
    return lsim((num, den), U=u, T=t)[1], mask


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'docs/browser-numerical-audit.json')
    args = parser.parse_args()
    results = []
    process = subprocess.Popen(['node', 'tools/browser_numerical_cases.mjs'], cwd=ROOT,
                               stdout=subprocess.PIPE, text=True)
    try:
        for line in process.stdout:
            case = json.loads(line)
            errors = []
            for run in case['runs']:
                expected, mask = reference(case, run)
                actual = np.asarray(run['output'])
                error = float(np.max(np.abs(expected[mask] - actual[mask])) /
                              max(1, np.max(np.abs(expected[mask]))))
                errors.append(error)
            passed = bool(np.isfinite(errors).all() and errors[-1] < .02)
            if len(errors) == 2:
                passed = passed and errors[1] <= errors[0] * 1.1 + 1e-8
            results.append(dict(kind=case['kind'], lab=case['lab'], task=case['task'],
                                normalized_max_errors=errors, passed=bool(passed)))
    finally:
        process.stdout.close()
        if process.poll() is None:
            process.wait()
    counts = {kind: sum(r['kind'] == kind for r in results) for kind in ('signal', 'circuit')}
    passed = process.returncode == 0 and counts == {'signal': 37, 'circuit': 17} and all(r['passed'] for r in results)
    sources = ['frontend/signal-solver.js', 'frontend/circuits.js', 'frontend/blocks.js',
               'tools/browser_numerical_cases.mjs', 'tools/verify_browser_numerics.py']
    report = dict(passed=passed, counts=counts, scipy=scipy.__version__,
                  threshold=.02, normalization='max(1, max(abs(reference)))',
                  signal_points=[10001, 20001], circuit_points=20001,
                  scope='Default course cases only; not all editable configurations or native MATLAB',
                  exclusions=['Non-proper algebraic task has no time response',
                              'Signal D/PD audit compares the filtered Scope; ideal impulse has no finite peak',
                              'Circuit D/PD excludes two samples around ramp corners and at startup'],
                  source_sha256={p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in sources},
                  results=results)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(f"Browser numerical audit: {counts}; passed={passed}; max fine error={max(r['normalized_max_errors'][-1] for r in results):.4%}")
    for result in results:
        if not result['passed']:
            print(result)
    return 0 if passed else 1


if __name__ == '__main__':
    sys.exit(main())
