"""Escape-rate LP certificate for AXIOM-02 (Proposition "Modulator escape directions").

For each drive i, solves (exactly, via scipy.optimize.linprog):
  rho_i = max t   s.t.   slope_i >= t,
                         slope_i - slope_j >= t   for all j != i,
                         |w|_inf <= 1,
where  slope_i  is the per-step slope of the EFFECTIVE activation of
drive i under the constant bounded modulator deviation w:
  slope_i(w) = (Delta^T w)_i - sum_j [I]_ji (Delta^T w)_j
with Delta = MODULATOR_EFFECTS (modulator x drive coupling matrix, sigma=0.60
applied in the engine) and [I]_ji the MUTUAL-INHIBITION matrix in
INCOMING orientation, i.e. the inhibition that drive j applies TO drive i
(drives.INHIBITION[key]=row of inhibitor drive: entry INHIBITION[j][i] is
the weight with which drive j suppresses drive i; this matches
eq:effective of the paper and drives.py's effective-activation formula).

Interpretation (Proposition in Sec. 3.5 of the paper, ideal model):
- rho_i > 0  =>  a constant bounded modulator input exists that drives
  drive i's effective activation above tau_f with lead over every
  competitor above tau_s within finitely many steps (witness printed).
- rho_i = 0  =>  no bounded single-modulator input can give drive i
  strict lead over every competitor; escape must go through the
  deadlock-regime decay branch or co-modulation.

Run: python3 harness/escape_lp.py
Expected output (released matrix, seed-independent): 15 escapable drives,
3 trapped {grief, guilt, shame}.
"""
import sys
import numpy as np
from scipy.optimize import linprog

sys.path.insert(0, "src")

from axiom02.config.modulators import MODULATOR_EFFECTS
from axiom02.core.drives import INHIBITION

SIGMA = 0.60

def build_matrices():
    mods = list(MODULATOR_EFFECTS.keys())
    drives = sorted({d for dd in MODULATOR_EFFECTS.values() for d in dd})
    M, n = len(mods), len(drives)
    idx = {d: k for k, d in enumerate(drives)}
    delta = np.zeros((M, n))
    for m in range(M):
        for d, e in MODULATOR_EFFECTS[mods[m]].items():
            delta[m, idx[d]] = e
    inh = np.zeros((n, n))
    for a, dd in INHIBITION.items():
        for b, v in dd.items():
            inh[idx[a], idx[b]] = v
    I = inh  # I[j, i] = inhibition applied TO drive i BY drive j (incoming)
    return mods, drives, delta, I

def escape_rate(i, delta, I):
    M = delta.shape[0]
    alpha_i = delta[:, i] - delta @ I[:, i]
    c = np.zeros(M + 1)
    c[-1] = -1.0
    A, b = [], []
    row = np.zeros(M + 1)
    row[:M] = -alpha_i
    row[-1] = 1.0
    A.append(row)
    b.append(0.0)
    for j in range(delta.shape[1]):
        if j == i:
            continue
        alpha_j = delta[:, j] - delta @ I[:, j]
        row = np.zeros(M + 1)
        row[:M] = -(alpha_i - alpha_j)
        row[-1] = 1.0
        A.append(row)
        b.append(0.0)
    for m in range(M):
        row = np.zeros(M + 1)
        row[m] = 1.0
        A.append(row)
        b.append(1.0)
        row = np.zeros(M + 1)
        row[m] = -1.0
        A.append(row)
        b.append(1.0)
    res = linprog(c, A_ub=np.array(A), b_ub=np.array(b))
    if not res.success:
        raise RuntimeError(f"LP infeasible/unbounded for drive {i}")
    return -res.fun, res.x[:M]

def main():
    mods, drives, delta, I = build_matrices()
    print("== Escape-rate LP certificate (Proposition 'escape directions') ==")
    print(f"   modulators: {len(mods)} ({', '.join(mods)}); drives: {len(drives)}; sigma={SIGMA}")
    escapable, trapped = [], []
    for i, d in enumerate(drives):
        rho, w = escape_rate(i, delta, I)
        e = delta.T @ w
        slope = e[i] - I[:, i] @ e
        kind = "ESCAPABLE" if rho > 1e-7 else "TRAPPED"
        (escapable if kind == "ESCAPABLE" else trapped).append(d)
        print(f"  {d:>18}  rho={rho:+.4f}  slope_i={slope:+.4f}  {kind}  "
              f"w={np.round(w * SIGMA, 3)} (modulator deviations at sigma)")
    print(f"\nescapable ({len(escapable)}/{len(drives)}): {escapable}")
    print(f"trapped ({len(trapped)}/{len(drives)}): {trapped}")
    assert len(escapable) == 15 and trapped == ["grief", "guilt", "shame"], \
        "certificate mismatch vs paper claim"

if __name__ == "__main__":
    main()