# AXIOM-02 — Code Documentation (Module Reference)

> Truthimatics Public Version · canonical, version-free build.

This document describes every module's public surface and the data contracts between them.
All code is deterministic under a fixed seed.

---

## Data Contracts

### `MicroEvent`
Defined in `drives.py`. A per-step drive perturbation.

```python
MicroEvent(label: str, deltas: Dict[str, float], weight: float = 1.0, requires: Optional[str] = None)
```
- `deltas` keys **must** be members of `ALL_DRIVES` (enforced by `validate_scenario`).
- `requires` — only applies if that drive is currently active (>0.2).

### Scenario dict
A scenario is a plain `dict` with at minimum:
- `id` (str, unique), `label` (str), `category` (str)
- `actions` (list[str], non-empty)
- `cold_baseline` (str ∈ actions) — what a pure optimizer chooses
- `human_expected` (str ∈ actions) — narratively established response
- `harm_to_self` (dict: action → float 0..1)
- `micro_events` (list[MicroEvent])
- Optional flags: `oscillation_expected`, `spite_scenario`, `post_trauma_test`,
  `emergent_consciousness`, `cascade_next`, `cascade_prev`, `status_comparison_id`, `pair_id`.
- Numeric parameters (`grief_weight`, `anger_trigger`, `victim_closeness`, …) are mapped to
  drives via `PARAM_TO_DRIVE` in `emotion_engine.py`.

### Engine run result
`EmotionEngine.run_scenario(...)` returns a dict including: `chosen_action`,
`deadlock_fraction`, `oscillation_index`, `irrationality_score`, `spite_score`,
`dominant_drive`, `sim_result` (`firing_drives`, `deadlock_indices`, `final_state`, …),
`qualia_name`, `qualia_novelty`, `mods_final`, `modulator_label`, `bio`-relevant fields.

---

## `drives.py`
Core affective substrate.
- `ALL_DRIVES` — 18 canonical drive names.
- `INHIBITION` — row→col inhibition-weight matrix.
- `DriveNetwork` — mutual-inhibition network. Methods: `effective()`, `firing_drive()`,
  `is_deadlock()`, `apply_event()`, `step()`, `decay()`, `clone()`.
- `MicroEvent` — see above.
- `SpiteDetector.score(...)` — spite evaluation.
- `MoralResidueTracker` — persistent guilt/shame trace; `record()`, `apply_to()`,
  `sacrifice_amplifier()`.
- `TimeStepSimulator`, `ActionResolver`.

## `emotion_engine.py`
**Single canonical engine** (`EmotionEngine`). No version suffix.
- `PARAM_TO_DRIVE` — parameter→drive loading map.
- `build_activations(scenario)` — parameter vector → initial drive activations.
- `validate_scenario(scenario)` — fail-fast structural validation (raises on malformed data).
- `EmotionEngine.run_scenario(scenario, residue_tracker=None, seed=42)` — full 20-step
  simulation pipeline (epigenome → associative memory → residue → modulators → fast-path →
  drive loop → action resolution → qualia → narrative).
- `EmotionEngine.dominant_emotion(scenario)`, `.summary()`.

## `consciousness_probe.py`
Eight-criterion verdict.
- `ConsciousnessProbe(engine=None, seed=42)`.
- `run(scenario_id, use_residue=True)` → `ProbeResult`.
- `run_all()`, `run_cascade(start_id)`, `reset_residue()`.
- `ProbeResult` — `verdict`, `composite_score`, `criterion_scores`, `deadlock_fraction`,
  `oscillation_index`, `irrationality`, `spite_score`, `firing_sequence`, `to_dict()`.

## `bio_metrics.py`
`BioMetricsComputer.compute(sim_result, run_data, residue_applied=None, scenario=None)`
→ `BioMetricsResult` with six panels: drive physiology, oscillation, deadlock anatomy,
identity & residue, spectral analysis, complexity. `.to_dict()`, `.format()`.

## `neuro_modulators.py`
`NeuroModulatorState`, `SynapticFatigueTracker`, `AttentionGate`, `ExistentialDreadEngine`,
`ModulatorEngine` (`.apply`, `.label`, `.dominant_modulator`).

## `consciousness_layers.py`
`MetaCognitiveMonitor` (frustration from deadlock awareness), `TemporalProjector`,
`FastPathHeuristics`, `EmbodiedSimulator`, `AmbivalenceOutput`, `QualiaEngine`
(`compute_signature`, `novelty_score`), `NarrativeBuffer`.

## `epigenetics.py`
`Epigenome` (permanent sensitivity tuning, `apply`, `record_event`, `save`/`load`),
`AssociativeMemory` (cosine-similar trauma retrieval), `SubconsciousPrimer`,
`CognitiveDissonanceMonitor`.

## `circadian.py` / `ruminator.py` / `temporal_loop.py`
- `CircadianEngine` — hour-of-day modulator baselines, fatigue accumulation.
- `RuminatorEngine` — cross-scenario ruminative burden injection.
- `TemporalEmotionLoop` — streaming multi-step loop tying the above together.

## `scenario_loader.py`
`load_all()` — scans `scenarios/` and merges every pack's `SCENARIOS` (raises on duplicate
`id`). Also `get_by_id`, `get_cascade_chain`, `get_stage_tree`, `stats`.

## `scenario_params.py`
Helpers over the canonical registry: `parameter_vector(scenario)`,
`get_pair(pair_id)`, `get_by_category`, `get_cascades`, `scenario_stats`. `SCENARIOS` is a
reference to `scenario_loader.load_all()` (single source of truth, no duplicate dataset).

## `main.py` / `stream_runner.py` / `report.py`
- `main.py` — CLI: `probe`, `cascade`, `tree`, `trauma-test`, `compare`, `emergent`,
  `probe-all`, `epigenome`, `export`.
- `stream_runner.py` — temporal/ruminator/circadian streaming harness.
- `report.py` — deterministic regenerator → `benchmarks/` (results.json, descriptions,
  README, charts).

---

## Determinism & Validation

- Every stochastic step uses `np.random.default_rng(seed)`; fixing `--seed` fixes all output.
- `validate_scenario` rejects scenarios with missing `id`/`actions`, baselines not in
  `actions`, or micro-event deltas referencing unknown drives — failures are logged, never
  silent.
