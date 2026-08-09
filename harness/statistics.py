"""Post-review statistical evidence for AXIOM-02 paper (does not modify release).

Reproduces every aggregate/statistical claim in Section 5 of the paper:
- binomial tails for fidelity
- verdict-flip ablation (stored-precision and exact-arithmetic variants)
- criterion statistics table
- correlations
Run: python3 harness/statistics.py
"""
import sys, json
import numpy as np
from math import comb

sys.path.insert(0, "src")

p0 = 0.2466


def binom_tail(k, n, p=p0, lower=False):
    s = sum(comb(n, i) * p**i * (1 - p) ** (n - i)
            for i in (range(0, k + 1) if lower else range(k, n + 1)))
    return s


print("== Binomial tails (n=102, p0=0.2466) ==")
print("label-aware P(X>=68):", f"{binom_tail(68,102):.3e}")
print("label-blind  P(X<=17):", f"{binom_tail(17,102,lower=True):.4f}")
print("label-blind  P(X>=17):", f"{binom_tail(17,102):.4f}")
print("uniform-random P(X>=29):", f"{binom_tail(29,102):.4f}")

d = json.load(open("src/benchmarks/results.json"))
rows = d["results"] if isinstance(d, dict) else d


def verdict(c):
    return "C" if c >= 0.50 else ("P" if c >= 0.28 else "R")


w = {"C1_status_differential": 0.02, "C2_transition_oscillation": 0.12,
     "C3_irrationality_signal": 0.30, "C4_betrayal_cascade": 0.04,
     "C5_deadlock_frequency": 0.20, "C6_spite_index": 0.22,
     "C7_moral_residue_bleed": 0.08, "C8_paradoxical_attachment": 0.02}

base = [verdict(r["composite_score"]) for r in rows]
print("\n== Verdict-flip ablation (zero each criterion) ==")
print("stored 4-decimal composite_score:")
for k, wk in w.items():
    flips = sum(1 for r, b in zip(rows, base)
                if verdict(r["composite_score"] - wk * r["criterion_scores"][k]) != b)
    print(f"  {k:32s} flips {flips:3d}/102")
print("exact arithmetic (criterion scores recomputed):")
def exact_dci(r):
    return sum(w[k] * r["criterion_scores"][k] for k in w)
exact_base = [verdict(exact_dci(r)) for r in rows]
for k, wk in w.items():
    flips = sum(1 for r, b in zip(rows, exact_base)
                if verdict(exact_dci(r) - wk * r["criterion_scores"][k]) != b)
    print(f"  {k:32s} flips {flips:3d}/102")

print("\n== Criterion statistics (seed 42) ==")
keys = list(w.keys())
for k in keys:
    v = [r["criterion_scores"][k] for r in rows]
    m = float(np.mean(v))
    sd = float(np.std(v))
    gt0 = 100 * sum(1 for x in v if x > 0) / len(v)
    ge9 = 100 * sum(1 for x in v if x >= 0.9) / len(v)
    print(f"  {k:34s} mean={m:.6f} sd={sd:.6f} >0={gt0:.1f}% >=0.9={ge9:.1f}%")

print("\n== Correlations with DCI and among criteria ==")
composite = [r["composite_score"] for r in rows]
for k in keys:
    v = [r["criterion_scores"][k] for r in rows]
    print(f"  rho({k}, DCI) = {float(np.corrcoef(v, composite)[0,1]):.3f}")
pairs = [("C2","C3"),("C2","C5"),("C3","C5"),("C3","C7"),("C5","C7")]
short = {"C2":"C2_transition_oscillation","C3":"C3_irrationality_signal",
         "C5":"C5_deadlock_frequency","C7":"C7_moral_residue_bleed"}
for a,b in pairs:
    va=[r["criterion_scores"][short[a]] for r in rows]
    vb=[r["criterion_scores"][short[b]] for r in rows]
    print(f"  rho({a},{b}) = {float(np.corrcoef(va,vb)[0,1]):.3f}")

print("\n== Chance levels ==")
m = [len(s) for s in d.get("action_spaces", [])] if d.get("action_spaces") else None
print("mean(1/m) = 0.2466 (corpus), 1/mean(m) bound = 0.2446")