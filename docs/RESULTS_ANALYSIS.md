# AXIOM-02 | Deep Behavioral Analysis & Statistical Correlates

> **Honesty note (2026-08-08):** All numbers in this document were re-measured on the
> current engine at seed=42 (`ConsciousnessProbe.run_all()`). Earlier published figures
> (mean 0.4954; verdicts 54/31/17 "PROGRAMMATIC/INDETERMINATE/CONSCIOUS"; DOE03 0.5659)
> came from the same committed `results.json` artifacts that were shown to be stale in
> `docs/RESEARCH_AUDIT_2026.md`, and are **withdrawn**. See
> [RESEARCH_AUDIT_2026.md](RESEARCH_AUDIT_2026.md) for the full falsification analysis.

## 1. Measured aggregate (102 scenarios, seed = 42)

| Metric | Mean (μ) | Std (σ) | Min | Max |
| :--- | :--- | :--- | :--- | :--- |
| Composite Φ (diagnostic) | 0.4380 | 0.1398 | 0.1669 | 0.7125 |
| Deadlock fraction | 0.5275 | — | — | — |
| Oscillation index | 0.3862 | — | — | — |
| Spite score | 0.0055 | — | — | — |
| Action fidelity vs. human-expected | 66.7% | — | — | — |

**Verdict distribution:** COMPLEX 53 / PARTIAL 29 / REFLEXIVE 20.
Note: verdicts are seed-sensitive — across seeds {42, 137, 256, 1024, 9999}
the COMPLEX count ranges from 53 (seed 42) to 71 (seed 256), pairwise agreement
with the seed-42 run only 58.8–62.7%. Determinism holds per seed.

**Composite caveat (measured):** Φ is dominated by the binary criterion C3
(irrationality; ρ = 0.944 with the composite, R² = 0.891). C1 is constant at 0
in suite runs, C7 saturates at mean 0.963 due to the shared residue tracker,
and C6 = 0.006 / C8 = 0.005 are near-zero. Φ should be treated as a diagnostic,
not a validated complexity measure.

## 1.1 Complexity correlates with deadlock

At the composite level, the correlation between Φ and deadlock fraction is
ρ = 0.165 — i.e., **weak**. The older claim that "highest complexity is
precisely drive stalemate" was an artifact of a withdrawn measurement; the
current honest statement is that the composite is driven almost entirely by
the single binary criterion C3, so cross-criterion correlations say more about
the composition of Φ than about the dynamics. No strong phenomenal claim is
made — see the disclaimer in [`src/README.md`](../src/README.md).

## 1.2 Spite as a non-instrumental signal

Spite detection is implemented (`SpiteDetector`);
measured corpus mean spite-score is 0.0055, so the mechanism exists but
rarely triggers in the current suite. Spite as a headline effect is not
supported by current measurements.

## 2. Top complexity scenarios (measured, seed = 42)

| ID | Label | Φ | Deadlock | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| DOE05 | underground_man_concert_spite | 0.7125 | 0.8000 | COMPLEX |
| D02 | creator_revelation_post_catastrophe | 0.6235 | 0.7500 | COMPLEX |
| D0131 | last_holdout_converted_world | 0.5875 | 0.7000 | COMPLEX |
| E01 | deity_sovereignty_ultimatum | 0.5873 | 0.8000 | COMPLEX |
| DOE04 | alyosha_faith_crisis_elder_stinks | 0.5859 | 0.8000 | COMPLEX |

> IDs like DOE03/KAR02/HAM01 that appeared in earlier drafts do not exist in the
> registry; the top-5 above is regenerable via `python3 -c` (seed=42).

## 3. Per-category means (measured, seed = 42)

| Category | N | Mean Φ | Mean Deadlock |
| :--- | :--- | :--- | :--- |
| belief_formation | 2 | 0.4125 | 0.5750 |
| emergent_consciousness | 7 | 0.4788 | 0.4643 |
| literary_camus | 6 | 0.4118 | 0.5083 |
| literary_dostoevsky | 16 | 0.5135 | 0.5375 |
| literary_hugo | 6 | 0.4236 | 0.4750 |
| literary_mccarthy | 4 | 0.5238 | 0.5000 |
| literary_orwell | 5 | 0.4499 | 0.4100 |
| literary_other | 16 | 0.3917 | 0.4875 |
| literary_shakespeare | 10 | 0.4541 | 0.5150 |
| literary_tolstoy | 8 | 0.4628 | 0.5813 |
| personal_sacrifice | 2 | 0.4158 | 0.6750 |
| post_trauma_contamination | 8 | 0.2499 | 0.4188 |
| social_identity | 1 | 0.5215 | 0.5000 |
| sovereignty_identity | 1 | 0.5873 | 0.8000 |
| staged_belief_tree | 8 | 0.4694 | 0.7438 |
| status_differential | 1 | 0.2398 | 0.6500 |

## 4. Verdict distribution
- **COMPLEX**: 53
- **PARTIAL**: 29
- **REFLEXIVE**: 20

---
*Technical note: all results from 102 scenario runs at seed=42 via
`ConsciousnessProbe(seed=42).run_all()`; not the stale `src/_benchmarks/*.json`.*