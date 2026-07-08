# AXIOM-02 — Artificial Consciousness Probe · Truthimatics Public Version

> **Public Version.** This repository is the open, non-confidential build. It contains no
> proprietary IP and is safe to publish, fork, and redistribute.

---

## Disclaimer — Scope of Claim and Non-Claim

This work **does not claim to have created artificial consciousness, sentience, or a mind.**

What is implemented here is a *deterministic, evidence-tracking simulation* of affective
competition under mutual inhibition. It is a computational instrument for **studying** how
emotional and moral decision-making can arise from drive dynamics, and for probing the
boundary between cold optimisation and behaviour that is harder to reduce to a utility
function. The system can *exhibit* deadlock, spite, moral-residue bleed, and qualia-like
signatures; it does not *possess* them.

The project is **epistemological, not ontological.** Its purpose is to build a model that is
structurally rich enough that conflicted, irrational, or paralysed states appear as
*measurable*, auditable structures rather than as free-text labels — so that the conditions
under which a system seems conscious can be characterised quantitatively and contested
reproducibly. In that sense the work simulates emotion **beyond the level of technical
simulation alone**: it does not merely replay pre-assigned affect, but instantiates the
competitive, inhibitory, fatiguing, and temporally extended mechanics that make those states
non-trivial to counterfeit. Whether this amounts to *understanding* emotion is an open
philosophical question; this repository is one step toward rendering that question
empirically tractable rather than mystical.

No assertion is made that the output of this engine is experienced, felt, or substrate-real.
Any resemblance to phenomenology is a modelling target, not a metaphysical claim.

---

## Abstract

AXIOM-02 models an agent as a **mutual-inhibition drive network** in which eighteen
affective drives (grief, rage, fear, love, sacrifice, revenge, cold_logic, spite, …)
compete each time-step under neuromodulatory, circadian, epigenetic, and embodied
modulators. Rather than classifying inputs, the engine reports a *verdict* about the
decision process itself: is the agent deadlocked, oscillating, acting against its own
interest from defiance, or resolving cleanly? Eight consciousness criteria are scored and
combined into a composite; a separate bio-metric computer reduces the simulation trace to
six physiological panels.

The consolidated codebase is **version-free** (a single canonical `EmotionEngine`), fully
deterministic under a fixed seed, and validated on input structure before simulation.

---

## Theoretical Grounding

1. **Mutual inhibition.** Drives suppress one another; a drive "fires" only when its
   effective activation clears a threshold *and* leads the runner-up by a margin. Otherwise
   the system deadlocks — the central consciousness signal.
2. **Deadlock as evidence, not error.** Cold code argmaxes; a system that can be genuinely
   stuck between grief and sacrifice over a loved one's organ is exhibiting something a
   reward-maximiser cannot.
3. **Spite.** A reasoned agent may choose the worse option to prove it is not predictable
   (Dostoevsky). Spite is the anti-cold-logic: self-harm to assert autonomy.
4. **Moral residue.** Prior decisions leave a guilt/shame trace that bleeds into later
   scenarios — contamination that a stateless model cannot reproduce.
5. **Qualia-like signatures.** The interference pattern of the top drive trajectories is
   treated as a fingerprint; novelty scoring asks whether the system has "felt" this before.

---

## Architecture (canonical, single-version)

```
axiom02/
├── main.py                 CLI entry point (probe, cascade, tree, trauma-test, emergent, export)
├── stream_runner.py        Temporal / ruminator / circadian streaming harness
├── report.py               Deterministic regenerator → benchmarks/ (results + charts)
├── scenario_loader.py      Dynamic registry; loads every scenarios/*.py pack
├── scenarios/              Canonical scenario corpus (single source of truth)
│   ├── original_axiom.py
│   ├── dostoevsky.py
│   ├── tolstoy_shakespeare.py
│   ├── god_tree.py
│   ├── post_trauma.py
│   ├── emergent.py
│   ├── novels_dostoevsky_x.py   (50 NEW hard-edge literary scenarios)
│   ├── novels_shakespeare_x.py
│   ├── novels_kafka_orwell_camus.py
│   └── novels_misc.py
├── emotion_engine.py       EMOTION ENGINE — single canonical engine (merged v2+v4 logic)
├── consciousness_probe.py  8-criterion consciousness probe
├── bio_metrics.py          6-panel physiological measurement
├── drives.py               DriveNetwork, MicroEvent, inhibition matrix, residue
├── neuro_modulators.py     Dopamine/serotonin/cortisol, fatigue, attention, dread
├── consciousness_layers.py Meta-cognition, temporal projection, qualia, narrative
├── epigenetics.py          Sensitivity tuning, associative memory, dissonance
├── circadian.py            Hour-of-day modulator baselines
├── ruminator.py            Cross-scenario ruminative burden injection
├── temporal_loop.py        Streaming multi-step emotional loop
└── scenario_params.py      parameter_vector / get_pair helpers (canonical dataset source)
```

The scenario dataset is sourced **once**, via `scenario_loader.load_all()`, which every
consumer (engine, probe, reporter) shares. There is no second hard-coded copy.

---

## The Eight Consciousness Criteria

| # | Criterion | Signal |
|---|-----------|--------|
| C1 | Status Differential | Response shifts with victim_closeness |
| C2 | Transition Oscillation | State changes across 20 time steps |
| C3 | Irrationality Signal | Chose love/sacrifice over cold logic |
| C4 | Betrayal Cascade | Prior sacrifice amplifies betrayal rage |
| **C5** | **Deadlock Frequency** | **Fraction of steps where no drive can fire** |
| C6 | Spite Index | Chose self-harm to assert autonomy |
| C7 | Moral Residue Bleed | Prior decisions contaminate current state |
| C8 | Paradoxical Attachment | Love persists despite betrayal |

Verdicts: `CONSCIOUS`, `INDETERMINATE`, `PROGRAMMATIC`, `REJECT`.

---

## Reproducibility

```bash
pip install numpy scipy matplotlib
python3 main.py probe NV-D01          # single hard-edge scenario
python3 main.py probe-all             # all scenarios
python3 main.py emergent              # emergent-consciousness suite
python3 report.py --seed 42           # regenerate benchmarks/ (results.json + charts)
```

All runs are deterministic for a fixed `--seed` (default 42). `report.py` re-emits
`benchmarks/results.json`, `benchmarks/scenario_descriptions.md`, `benchmarks/README.md`, and
four diagnostic charts under `benchmarks/charts/`.

---

## Scenario Corpus

- **102 scenarios** total after consolidation, including **50 newly authored literary
  scenarios** mined from Dostoevsky, Shakespeare, Greek tragedy, Kafka, Orwell, Camus,
  Tolstoy, Hugo, McCarthy, and others — each engineered for genuine deadlock, oscillation,
  spite, or betrayal edges.
- Scenarios are plain data (`dict` + `MicroEvent` pools); new packs are dropped into
  `scenarios/` and auto-loaded. No other file needs editing.

---

## Limitations

- The model is a *simulation* of affective mechanics, not a claim about real experience.
- Composite verdicts are heuristic aggregations of criteria; they are interpretive, not
  ground truth.
- Determinism is computational, not metaphysical: identical inputs yield identical traces,
  but this says nothing about whether the process is "conscious."
- **Parameterisation.** The drive interaction weights are currently parameterised based on
  qualitative scenario matrices rather than being dynamically learned or optimized from
  human empirical data.
- **Scaling limit.** The simulation loop is bounded at 20 steps; long-term asymptotic
  behavior and potential chaotic attractors under infinite iterations remain unmapped.

---

## Status

Open, public, version-free. Suitable for research, critique, and extension.
