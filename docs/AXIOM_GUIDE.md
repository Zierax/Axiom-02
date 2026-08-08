# AXIOM-02 · Architecture Guide — Public Version

> "A mutual-inhibition drive network designed to test whether a system exhibits
> structural signatures of conflicted deliberation vs. cold statistical
> optimization." AXIOM-02 is a deterministic *simulation instrument*, not a
> claim about consciousness.

## Architecture Overview (canonical)
The consolidated build integrates the drive network with simulated
neuromodulators, epigenetic sensitivity, associative memory, circadian
baselines, and an embodied simulation layer. There is a **single** engine
class (`EmotionEngine`) in `src/axiom02/core/engine.py`; no `v2`/`v4`/`v3`
version suffixes remain.

### The Cognition Pipeline
```
Scenario Input → Initial Activations (parameter_vector → drives)
  → Epigenome.apply()        (long-term sensitivity)
  → AssociativeMemory residue (similar past traumas)
  → Moral residue (cascade contamination)
  → ModulatorEngine.apply()  (dopamine/serotonin/cortisol/...)
  → FastPathHeuristics       (hot-cognition bypass)
  → TemporalProjector        (affective forecasting)
  → DriveNetwork loop (20 steps of mutual inhibition)
  → ActionResolver + SpiteDetector
  → Embodied hesitation → Qualia → Narrative
  → ConsciousnessProbe (8 criteria) → Verdict (REFLEXIVE | PARTIAL | COMPLEX)
```

### Module map
- `src/axiom02/core/engine.py` — `EmotionEngine`, `build_activations`, `validate_scenario`
- `src/axiom02/core/probe.py` — 8-criterion `ConsciousnessProbe` / `ProbeResult`
- `src/axiom02/core/drives.py` — `DriveNetwork`, `MicroEvent`, `SpiteDetector`, `MoralResidueTracker`
- `src/axiom02/core/bio_metrics.py` — 12-dimensional `BioMetricsComputer`
- `src/axiom02/core/epigenetics.py` — `Epigenome`, `AssociativeMemory`, `SubconsciousPrimer`
- `src/axiom02/core/scenario_loader.py` + `src/scenarios/` — single canonical scenario registry
- `src/axiom02/core/scenario_params.py` — `parameter_vector` / `get_pair` helpers
- `src/axiom02/modulators/` — `neuro_modulators.py`, `circadian.py`, `ruminator.py`, `temporal_loop.py`
- `src/axiom02/layers/consciousness_layers.py` — meta-cognition, projection, qualia, narrative
- `src/axiom02/config/` — every tunable constant, one dataclass per subsystem
- `src/axiom02/ml/`, `src/axiom02/analysis/`, `src/axiom02/validation/` — optimisation, sensitivity, validation framework

## Determinism & Reproducibility
All stochastic steps use `numpy.random.default_rng(seed)`. Fixing `--seed`
(default 42) fixes all output for that seed. Regenerate every report with:
```bash
cd src && python3 report.py --seed 42
```

## Measured verdict distribution (seed = 42, current engine)

- **COMPLEX**: 53
- **PARTIAL**: 29
- **REFLEXIVE**: 20

Mean composite Φ = 0.438 (σ = 0.140, range [0.167, 0.713]); action fidelity
66.7% vs. 33.3% argmax / 28.4% random (chance ≈ 24%).

> Caution: verdict labels are **seed-sensitive** (COMPLEX count 53–71 across
> seeds {42,137,256,1024,9999}); per-seed determinism holds. The composite is
> dominated by criterion C3 (ρ = 0.944). See
> [RESEARCH_AUDIT_2026.md](RESEARCH_AUDIT_2026.md) for the falsification analysis.

*Full metrics: [RESULTS_ANALYSIS.md](RESULTS_ANALYSIS.md). Disclaimer: this is a
simulation of affective mechanics, not a claim of consciousness — see
[`src/README.md`](../src/README.md).*