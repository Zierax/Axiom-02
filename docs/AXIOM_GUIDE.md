# AXIOM-02 · Artificial Consciousness Guide — Truthimatics Public Version

> "A mutual-inhibition drive network designed to test whether a system exhibits genuine emotional processing vs. cold statistical optimization."

## Architecture Overview (canonical, version-free)
The consolidated build integrates the drive network with simulated neuromodulators, epigenetic sensitivity, associative memory, circadian baselines, and an embodied simulation layer. There is a **single** engine module (`emotion_engine.py`, class `EmotionEngine`); no `v2`/`v4`/`v3` version suffixes remain.

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
  → ConsciousnessProbe (8 criteria) → Verdict
```

### Module map
- `emotion_engine.py` — `EmotionEngine`, `build_activations`, `validate_scenario`
- `consciousness_probe.py` — 8-criterion `ConsciousnessProbe` / `ProbeResult`
- `bio_metrics.py` — 6-panel `BioMetricsComputer`
- `drives.py` — `DriveNetwork`, `MicroEvent`, `INHIBITION`, `MoralResidueTracker`
- `neuro_modulators.py`, `consciousness_layers.py`, `epigenetics.py`, `circadian.py`, `ruminator.py`, `temporal_loop.py`
- `scenario_loader.py` + `scenarios/` — single canonical scenario registry
- `scenario_params.py` — `parameter_vector` / `get_pair` helpers

## Determinism & Reproducibility
All stochastic steps use `numpy.random.default_rng(seed)`. Fixing `--seed` (default 42) fixes all output. Regenerate every report with:
```bash
cd src && python3 report.py --seed 42
```

## Verdict distribution (this build)

- **PROGRAMMATIC**: 54
- **INDETERMINATE**: 31
- **CONSCIOUS**: 17

*Full metrics: [METRICS_DEEP_DIVE.md](METRICS_DEEP_DIVE.md). Disclaimer: this is a simulation of affective mechanics, not a claim of consciousness — see [`src/README.md`](../src/README.md).*