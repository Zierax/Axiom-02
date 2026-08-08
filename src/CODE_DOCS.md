# AXIOM-02 Code Documentation

*Module map (canonical layout under `src/axiom02/`).* This file documents the
package structure; all constants live in `src/axiom02/config/`.

## `core/`
### `engine.py`
**Single canonical engine** (`EmotionEngine`). No version suffix. Resides at
`src/axiom02/core/engine.py`.
- `PARAM_TO_DRIVE` — parameter→drive loading map (`config/`).
- `build_activations(scenario)` — parameter vector → initial drive activations.
- `validate_scenario(scenario)` — fail-fast structural validation (raises on malformed data).
- `EmotionEngine.run_scenario(scenario, residue_tracker=None, seed=42)` — full 20-step
  simulation pipeline (epigenome → associative memory → residue → modulators → fast-path →
  drive loop → action resolution → qualia → narrative).
- `EmotionEngine.dominant_emotion(scenario)`, `.summary()`.

### `drives.py`
- `DriveNetwork`, `TimeStepSimulator`, `ActionResolver`, `SpiteDetector`,
  `MoralResidueTracker` (persistent guilt/shame trace; `record()`, `apply_to()`,
  `sacrifice_amplifier()`).

### `probe.py`
Eight-criterion verdict.
- `ConsciousnessProbe(engine=None, seed=42)`.
- `run(scenario_id, use_residue=True)` → `ProbeResult`.
- `run_all()`, `run_cascade(start_id)`, `reset_residue()`.
- `ProbeResult` — `verdict`, `composite_score`, `criterion_scores`, `deadlock_fraction`,
  `oscillation_index`, `irrationality`, `spite_score`, `firing_sequence`, `to_dict()`.

### `bio_metrics.py`
`BioMetricsComputer.compute(sim_result, run_data, residue_applied=None, scenario=None)`
→ `BioMetricsResult` with six panels: drive physiology, oscillation, deadlock anatomy,
identity & residue, spectral analysis, complexity. `.to_dict()`, `.format()`.

### `epigenetics.py`
`Epigenome` (permanent sensitivity tuning, `apply`, `record_event`, `save`/`load`),
`AssociativeMemory` (cosine-similar trauma retrieval), `SubconsciousPrimer`,
`CognitiveDissonanceMonitor`.

### `scenario_loader.py` / `scenario_params.py`
- `load_all()` — scans `scenarios/` and merges every pack's `SCENARIOS` (raises on duplicate
  `id`). Also `get_by_id`, `get_cascade_chain`, `get_stage_tree`, `stats`.
- `parameter_vector(scenario)`, `get_pair(pair_id)`, `get_by_category`, `get_cascades`,
  `scenario_stats`. `SCENARIOS` references `scenario_loader.load_all()` (single source of
  truth, no duplicate dataset).

## `modulators/`
- `neuro_modulators.py` — `NeuroModulatorState`, `SynapticFatigueTracker`, `AttentionGate`,
  `ExistentialDreadEngine`, `ModulatorEngine` (`.apply`, `.label`, `.dominant_modulator`).
- `circadian.py` — `CircadianEngine`: hour-of-day modulator baselines, fatigue accumulation.
- `ruminator.py` — `RuminatorEngine`: cross-scenario ruminative burden injection.
- `temporal_loop.py` — `TemporalEmotionLoop`: streaming multi-step loop tying the above.

## `layers/consciousness_layers.py`
`MetaCognitiveMonitor` (frustration from deadlock awareness), `TemporalProjector`,
`FastPathHeuristics`, `EmbodiedSimulator`, `AmbivalenceOutput`, `QualiaEngine`
(`compute_signature`, `novelty_score`), `NarrativeBuffer`.

## `config/` (all constants)
Dataclass per subsystem: drives, modulators, layers, probe, simulation, epigenetics,
bio, temporal. Serialization: `save_config`/`load_config` (JSON and YAML round-trip;
tuple keys encoded/restored).

## `main.py` / `report.py` / `stream_runner.py` (top-level `src/`)
- `main.py` — CLI: `probe`, `cascade`, `tree`, `trauma-test`, `compare`, `emergent`,
  `probe-all`, `report`, `export`.
- `report.py` — deterministic regenerator → `benchmarks/` (results.json, descriptions,
  charts).
- `stream_runner.py` — temporal/ruminator/circadian streaming harness.