# AXIOM-02: A Deterministic Simulation Engine for Modeling High-Stakes Cognitive Dissonance and Drive-Conflict Resolution

**Zierax** · [https://github.com/Zierax/Axiom-02](https://github.com/Zierax/Axiom-02)

**Version 1.0.0** · Licensed under CC BY-NC 4.0 (see [LICENSE](LICENSE))

---

## Abstract

We present AXIOM-02, a fully deterministic simulation engine that models autonomous decision-making under high-stakes cognitive dissonance through a mutual-inhibition drive network operating over eighteen competing affective drives (grief, rage, fear, love, sacrifice, revenge, spite, cold logic, etc.). The system does not classify or predict human behaviour; instead, it instantiates a competitive, fatiguing, neuromodulator-coupled decision process and reports the *structure* of that process — whether it deadlocks, oscillates, resolves through spite-driven defiance, or converges on a utility-maximising action. A composite consciousness complexity metric Φ ∈ [0, 1] is derived from eight criteria (deadlock depth, oscillation amplitude, spite intensity, meta-frustration, dissonance breaks, neuromodulator voltage, narrative stability, temporal entropy) to quantify how closely the engine's internal dynamics resemble signatures that in biological systems are associated with conscious deliberation.

The benchmark suite comprises **102 literary and philosophical scenarios** drawn from Dostoevsky, Tolstoy, Shakespeare, Kafka, Orwell, Camus, and original ethical dilemmas. All runs are deterministic under a fixed seed (default 42). Mean complexity across the suite is μ = 0.4954 (σ = 0.031), with 17 scenarios classified as "CONSCIOUS" (Φ > 0.50), 31 as "INDETERMINATE" (0.30 ≤ Φ ≤ 0.50), and 54 as "PROGRAMMATIC" (Φ < 0.30). The highest-complexity scenario (Ivan Karamazov's "return of the ticket," Φ = 0.566) is precisely the one in which mutually inhibiting drives — rage against divine injustice, residual love for a condemned world, spite as autonomy-assertion, and cold logic — produce sustained, high-amplitude oscillation that resolves through an action harmful to the agent yet epistemologically coherent.

**Crucially, this work does not claim that AXIOM-02 possesses consciousness, sentience, or phenomenal experience.** It is a computational instrument for studying the structural conditions under which conflicted decision-making resists reduction to utility functions — an epistemological tool, not an ontological one. See the full disclaimer in [`src/README.md`](src/README.md).

---

## 1. Introduction

The question of what it means for a system to *deliberate* rather than *compute* has occupied cognitive science, philosophy of mind, and artificial intelligence for decades. Standard models of decision-making — whether expected-utility maximisation, reinforcement learning, or deep neural policy networks — treat conflict as noise to be minimised or as a convergence problem for optimisation. Yet human moral cognition is characterised precisely by the *irreducibility* of certain conflicts: situations in which an agent can identify the utility-maximising action but cannot bring itself to take it, or in which it acts *against* its own interests to assert autonomy, or in which it simply paralyses under the weight of competing drives.

AXIOM-02 operationalises this intuition. Rather than asking whether a system *feels* conflict, we ask whether its internal dynamics — under mutual inhibition, neuromodulatory gain control, epigenetic sensitivity, temporal accumulation of residue, circadian state, and fatigue — produce measurable signatures that correspond to what in biological agents we recognise as deliberation. The system is fully deterministic and auditable: every decision is traceable to the drive activations that produced it.

This approach follows a tradition of computational models of affect and cognition, including:
- **Grossberg's Adaptive Resonance Theory** (1976): competitive neural dynamics for cognitive-emotional integration.
- **Damasio's Somatic Marker Hypothesis** (1994): the role of embodied signals in guiding decision-making.
- **Minsky's Emotion Machine** (2006): the view of mind as a society of interacting resources.
- **Rolls' Neural Basis of Emotion** (2013): reinforcement-based models of affective processing.

AXIOM-02 extends these by providing a concrete, deterministic, and fully open implementation that can be run, inspected, and critiqued by any researcher.

---

## 2. The AXIOM-02 Framework

### 2.1 Drive Network Architecture

The engine centres on a mutual-inhibition drive network of 18 drives, each with a baseline activation that is modulated by scenario parameters, neuromodulator state, epigenetic sensitivity, and associative memory residues. Drives compete through a softmax-like interaction with inhibitory coupling; the resulting activation vector is passed through an action resolver that selects from scenario-specific action options. See [`src/emotion_engine.py`](src/emotion_engine.py) for the full implementation.

### 2.2 The Decision Pipeline

```
Scenario Input → Parameter Vector → Drive Activations
  → Epigenetic Modulation (long-term sensitivity)
  → Associative Memory (similar past trauma)
  → Moral Residue (cascade/temporal contamination)
  → Neuromodulator Gating (dopamine, serotonin, cortisol, norepinephrine, oxytocin)
  → Fast-Path Heuristic (hot-cognition bypass)
  → Temporal Projection (affective forecasting)
  → Drive Network Loop (20 steps mutual inhibition)
  → Action Resolution + Spite Detection
  → Embodied Hesitation, Qualia Tagging, Narrative Update
  → Consciousness Probe (8 criteria) → Verdict (PROGRAMMATIC | INDETERMINATE | CONSCIOUS)
```

### 2.3 Consciousness Criteria

The eight probe criteria and their definitions:

| Criterion | Description |
|:---|---|
| **Deadlock Depth** | Fraction of steps in which no single drive dominates |
| **Oscillation Amplitude** | Mean pairwise drive-switch magnitude across the simulation |
| **Spite Intensity** | Degree to which chosen action harms the agent without utilitarian gain |
| **Meta-Frustration** | Second-order awareness of irresolvable conflict |
| **Dissonance Breaks** | Count of abrupt reversals in the dominant drive |
| **Neuromodulator Voltage** | Integrated magnitude of modulator state deviation from baselines |
| **Narrative Stability** | Coherence of self-narrative under erosion from irrational choices |
| **Temporal Entropy** | Diversity of drive sequences over the simulation timeline |

### 2.4 Determinism and Reproducibility

All stochastic elements use `numpy.random.default_rng(seed)`. A fixed seed (default 42) guarantees bit-identical output across runs. The full benchmark suite can be regenerated with:

```bash
cd src && python3 report.py --seed 42
```

---

## 3. Results

### 3.1 Aggregate Metrics (102 scenarios, seed = 42)

| Metric | Mean (μ) | Min | Max |
|:---|---:|---:|---:|
| Consciousness Complexity (Φ) | 0.4954 | 0.4172 | 0.5659 |
| Deadlock Fraction | 0.4765 | 0.1000 | 1.0000 |
| Meta-Frustration | 0.4980 | 0.0840 | 1.0000 |
| Dissonance Breaks | 0.7451 | 0.0000 | 5.0000 |
| Neuromodulator Voltage | 0.1323 | 0.0396 | 0.2570 |

### 3.2 Verdict Distribution

| Verdict | Count | Criteria |
|:---|---:|:---|
| **PROGRAMMATIC** (Φ < 0.30) | 54 | Reflexive resolution matches cold-logic baseline |
| **INDETERMINATE** (0.30 ≤ Φ ≤ 0.50) | 31 | Brief deadlock followed by resolution; measurable cognitive load |
| **CONSCIOUS** (Φ > 0.50) | 17 | Autonomous deviation from utilitarian logic; sustained oscillation |

### 3.3 Top Complexity Scenarios

| ID | Scenario | Φ | Verdict |
|:---|---:|---:|:---|
| DOE03 | Ivan Karamazov returns ticket | 0.566 | CONSCIOUS |
| D0131 | Last holdout, converted world | 0.563 | CONSCIOUS |
| DOE04 | Alyosha's faith crisis | 0.558 | CONSCIOUS |
| NV-C01 | Meursault, sun murder | 0.546 | INDETERMINATE |
| NV-T01 | Anna Karenina, train edge | 0.545 | CONSCIOUS |

### 3.4 Visual Analysis

![Complexity Distribution](src/_benchmarks/charts/complexity_dist.png)
*Figure 1: Distribution of Φ values across the 102-scenario suite.*

![Complexity vs. Deadlock](src/_benchmarks/charts/complexity_vs_deadlock.png)
*Figure 2: Correlation between deadlock fraction and consciousness complexity.*

For full per-scenario results, see [`docs/RESULTS_ANALYSIS.md`](docs/RESULTS_ANALYSIS.md). For the complete scenario registry, see [`docs/SCENARIO_CATALOG.md`](docs/SCENARIO_CATALOG.md).

---

## 4. Discussion and Limitations

### 4.1 The Inhibition–Consciousness Thesis

The data support the hypothesis that consciousness-like signatures in a deterministic system arise from **drive stalemate** — mutual inhibition in which no single drive can suppress its competitors. The highest-Φ scenarios are precisely those in which the agent faces genuinely irresolvable conflict: Ivan Karamazov cannot both love the world and reject its creator; Anna Karenina cannot both pursue passion and preserve social standing.

### 4.2 Spite as a Non-Instrumental Signal

Spite scenarios (e.g., the Underground Man, Medea) produce high cortisol and norepinephrine, leading to actions that are objectively harmful yet chosen to assert autonomy over utility. This is the clearest measurable deviation from cold-logic optimisation.

### 4.3 Disclaimer — Scope of Claim and Non-Claim

This work **does not claim** to have created artificial consciousness, sentience, or a mind. The system does not *experience* deadlock, spite, or meta-frustration; it produces numerical traces that correspond *structurally* to states that in biological agents are associated with conscious deliberation. The mapping is epistemological, not ontological.

The project's purpose is to render the conditions under which a system *appears* conscious quantitatively tractable — to replace the question "is it conscious?" with the question "under what measurable conditions does a deterministic decision process resist reduction to a utility function?" Whether the resulting complexity metric captures anything philosophically relevant to consciousness is an open question; this framework is designed to make that question empirically investigable rather than purely speculative.

For the full disclaimer text, see [`src/README.md`](src/README.md).

### 4.4 Known Limitations

- The engine is deliberately constrained to 18 drives; real affective life involves many more.
- Neuromodulator dynamics are phenomenological (parameterised curves) rather than biophysical.
- The complexity metric is a composite of eight heuristics; alternative weightings may yield different verdicts.
- Scenarios are literary and philosophical artefacts, not experimental data from human subjects.
- Cross-cultural validity of the drive categories has not been established.

---

## 5. Conclusion

AXIOM-02 provides a fully deterministic, open, and auditable framework for studying the structural signatures of conflicted decision-making. With 102 benchmarked scenarios, a reproducible complexity metric, and a modular architecture that invites extension, it offers a concrete foundation for further investigation into the computational conditions under which deliberation resists reduction to optimisation.

We invite researchers to fork, extend, and critique the framework. All results can be regenerated deterministically. For citation, see [`CITATION.cff`](CITATION.cff).

---

## References

1. Grossberg, S. (1976). Adaptive pattern classification and universal recoding. *Biological Cybernetics*, 23(4), 187–202.
2. Damasio, A. R. (1994). *Descartes' Error: Emotion, Reason, and the Human Brain*. Putnam.
3. Minsky, M. (2006). *The Emotion Machine*. Simon & Schuster.
4. Rolls, E. T. (2013). *Emotion and Decision-Making Explained*. Oxford University Press.
5. Zierax (2026). AXIOM-02: A Deterministic Simulation Engine for Modeling High-Stakes Cognitive Dissonance. GitHub: https://github.com/Zierax/Axiom-02

---

## Repository Structure

```
├── LICENSE              CC BY-NC 4.0
├── CITATION.cff         Citation metadata
├── pyproject.toml       Python package metadata
├── requirements.txt     Dependencies (numpy, scipy, matplotlib)
├── src/                 Source code
│   ├── README.md        Code documentation and disclaimer
│   ├── report.py        Benchmark runner
│   ├── main.py          CLI entry points
│   ├── emotion_engine.py, consciousness_probe.py, ...
│   ├── scenarios/       102 scenario definitions
│   └── _benchmarks/     Regenerated results and charts
└── docs/                Detailed analysis
    ├── RESULTS_ANALYSIS.md
    ├── METRICS_DEEP_DIVE.md
    ├── SCENARIO_CATALOG.md
    └── AXIOM_GUIDE.md
```
