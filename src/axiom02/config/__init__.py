"""
AXIOM-02 · Centralized Configuration Package v1.0

Every magic number in the AXIOM-02 codebase lives here.

Usage:
  from axiom02.config import get_config, AxiomConfig

  cfg = get_config()
  if activation > cfg.drives.fire_threshold:
      ...

  save_config(cfg, "configs/experiment_v3.yaml")
  cfg = load_config("configs/experiment_v3.yaml")
"""
from __future__ import annotations

import json
import ast
from dataclasses import asdict, fields, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union, get_type_hints

# Re-export all submodule classes and constants
from axiom02.config.drives import (
    DriveConstants, ActionResolverConstants, MoralResidueConstants,
    ACTION_FUTURE_DRIVES, PARAM_TO_DRIVE, DRIVE_ACTION_BIAS, INHIBITION_MATRIX,
)
from axiom02.config.modulators import (
    FatigueConstants, AttentionConstants, DreadConstants,
    ModulatorBaselineConstants, ModulatorEngineConstants,
    ModulatorLabelConstants, ModulatorScenarioScaling,
    ModulatorFeedbackConstants, MODULATOR_EFFECTS,
)
from axiom02.config.layers import (
    MetaCognitionConstants, EmbodiedConstants, AmbivalenceConstants,
    QualiaConstants, QUALIA_NAMES, NarrativeConstants, RATIONALISATIONS,
)
from axiom02.config.probe import (
    DeliberativeThresholds, ConsciousnessThresholds, CriterionWeights,
    C1Constants, C2Constants, C3Constants, C4Constants,
    C5Constants, C6Constants, C7Constants, C8Constants,
)
from axiom02.config.simulation import (
    TimeStepConstants, FastPathConstants, TemporalProjectorConstants,
    OscillationIndexConstants, HesitationConstants,
    FAST_PATH_MAX_DEADLOCK, IDENTITY_BASELINE,
)
from axiom02.config.epigenetics import (
    EpigeneticsConstants, EPIGENETIC_IMPACT, SCENARIO_TO_EVENT,
    AutoregulationConstants, SensitivityConstants,
    AssociativeMemoryConstants, DissonanceConstants,
)
from axiom02.config.bio import (
    BioMetricsConstants, COMPLEXITY_WEIGHTS, COMPLEXITY_LABELS,
)
from axiom02.config.temporal import (
    TemporalLoopConstants, MODULATOR_COUPLING,
    TEMPORAL_MODULATOR_DEFAULTS,
    TEMPORAL_CORTISOL_HOURS_DECAY, TEMPORAL_SEROTONIN_DEPLETION_CAP,
    TEMPORAL_NOREPI_ENTROPY_THRESHOLD, TEMPORAL_SCENARIO_BLEND,
    TEMPORAL_PRIOR_BLEND, TEMPORAL_FATIGUE_ACCUMULATION,
    TEMPORAL_BASE_ENTROPY,
)


# Attention gated drives — only drives that exist in ALL_DRIVES
ATTENTION_GATED_DRIVES: Set[str] = {
    "love", "empathy", "cold_logic", "hope",
    "acceptance", "shame", "guilt", "pride",
}


# ──────────────────────────────────────────────────────────────────────────────
# MAIN CONFIGURATION CONTAINER
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class AxiomConfig:
    """Top-level configuration for the AXIOM-02 engine.

    Groups all constants by subsystem. Provides serialization and versioning.
    """
    version: str = "2.0.0"
    label: str = "AXIOM-02 default configuration"

    # Subsystem configs
    drives: DriveConstants = field(default_factory=DriveConstants)
    time_steps: TimeStepConstants = field(default_factory=TimeStepConstants)
    action_resolver: ActionResolverConstants = field(default_factory=ActionResolverConstants)
    moral_residue: MoralResidueConstants = field(default_factory=MoralResidueConstants)
    fatigue: FatigueConstants = field(default_factory=FatigueConstants)
    attention: AttentionConstants = field(default_factory=AttentionConstants)
    dread: DreadConstants = field(default_factory=DreadConstants)
    modulator_baseline: ModulatorBaselineConstants = field(default_factory=ModulatorBaselineConstants)
    modulator_engine: ModulatorEngineConstants = field(default_factory=ModulatorEngineConstants)
    modulator_label: ModulatorLabelConstants = field(default_factory=ModulatorLabelConstants)
    modulator_scenario: ModulatorScenarioScaling = field(default_factory=ModulatorScenarioScaling)
    modulator_feedback: ModulatorFeedbackConstants = field(default_factory=ModulatorFeedbackConstants)
    meta_cognition: MetaCognitionConstants = field(default_factory=MetaCognitionConstants)
    embodied: EmbodiedConstants = field(default_factory=EmbodiedConstants)
    ambivalence: AmbivalenceConstants = field(default_factory=AmbivalenceConstants)
    qualia: QualiaConstants = field(default_factory=QualiaConstants)
    narrative: NarrativeConstants = field(default_factory=NarrativeConstants)
    consciousness_thresholds: ConsciousnessThresholds = field(default_factory=ConsciousnessThresholds)
    criterion_weights: CriterionWeights = field(default_factory=CriterionWeights)
    c1: C1Constants = field(default_factory=C1Constants)
    c2: C2Constants = field(default_factory=C2Constants)
    c3: C3Constants = field(default_factory=C3Constants)
    c4: C4Constants = field(default_factory=C4Constants)
    c5: C5Constants = field(default_factory=C5Constants)
    c6: C6Constants = field(default_factory=C6Constants)
    c7: C7Constants = field(default_factory=C7Constants)
    c8: C8Constants = field(default_factory=C8Constants)
    epigenetics: EpigeneticsConstants = field(default_factory=EpigeneticsConstants)
    autoregulation: AutoregulationConstants = field(default_factory=AutoregulationConstants)
    sensitivity: SensitivityConstants = field(default_factory=SensitivityConstants)
    associative_memory: AssociativeMemoryConstants = field(default_factory=AssociativeMemoryConstants)
    dissonance: DissonanceConstants = field(default_factory=DissonanceConstants)
    bio_metrics: BioMetricsConstants = field(default_factory=BioMetricsConstants)
    temporal_loop: TemporalLoopConstants = field(default_factory=TemporalLoopConstants)
    fast_path: FastPathConstants = field(default_factory=FastPathConstants)
    temporal_projector: TemporalProjectorConstants = field(default_factory=TemporalProjectorConstants)
    oscillation_index: OscillationIndexConstants = field(default_factory=OscillationIndexConstants)
    hesitation: HesitationConstants = field(default_factory=HesitationConstants)

    # Non-frozen dicts (mutable for runtime use)
    attention_gated_drives: Set[str] = field(default_factory=lambda: set(ATTENTION_GATED_DRIVES))
    modulator_effects: Dict[str, Dict[str, float]] = field(default_factory=lambda: dict(MODULATOR_EFFECTS))
    qualia_names: Dict[Tuple[str, ...], str] = field(default_factory=lambda: dict(QUALIA_NAMES))
    rationalisations: Dict[str, str] = field(default_factory=lambda: dict(RATIONALISATIONS))
    epigenetic_impact: Dict[str, Dict[str, float]] = field(default_factory=lambda: dict(EPIGENETIC_IMPACT))
    scenario_to_event: Dict[str, str] = field(default_factory=lambda: dict(SCENARIO_TO_EVENT))
    complexity_weights: Dict[str, float] = field(default_factory=lambda: dict(COMPLEXITY_WEIGHTS))
    complexity_labels: List[Tuple[float, str]] = field(default_factory=lambda: list(COMPLEXITY_LABELS))
    modulator_coupling: Dict[Tuple[str, str], float] = field(default_factory=lambda: dict(MODULATOR_COUPLING))
    temporal_modulator_defaults: Dict[str, float] = field(default_factory=lambda: dict(TEMPORAL_MODULATOR_DEFAULTS))
    action_future_drives: Dict[str, Dict[str, float]] = field(default_factory=lambda: dict(ACTION_FUTURE_DRIVES))
    param_to_drive: Dict[str, Dict[str, float]] = field(default_factory=lambda: dict(PARAM_TO_DRIVE))
    drive_action_bias: Dict[str, str] = field(default_factory=lambda: dict(DRIVE_ACTION_BIAS))
    inhibition_matrix: Dict[str, Dict[str, float]] = field(default_factory=lambda: dict(INHIBITION_MATRIX))

    fast_path_max_deadlock: int = FAST_PATH_MAX_DEADLOCK
    identity_baseline: float = IDENTITY_BASELINE
    temporal_cortisol_hours_decay: float = TEMPORAL_CORTISOL_HOURS_DECAY
    temporal_serotonin_depletion_cap: float = TEMPORAL_SEROTONIN_DEPLETION_CAP
    temporal_norepi_entropy_threshold: float = TEMPORAL_NOREPI_ENTROPY_THRESHOLD
    temporal_scenario_blend: float = TEMPORAL_SCENARIO_BLEND
    temporal_prior_blend: float = TEMPORAL_PRIOR_BLEND
    temporal_fatigue_accumulation: float = TEMPORAL_FATIGUE_ACCUMULATION
    temporal_base_entropy: float = TEMPORAL_BASE_ENTROPY

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to a nested dict (JSON-safe)."""
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "AxiomConfig":
        """Deserialize from a nested dict."""
        cfg = cls()
        field_map = {f.name: f for f in fields(cfg)}
        type_hints = get_type_hints(cls)
        dict_fields = {
            "attention_gated_drives", "qualia_names", "rationalisations",
            "epigenetic_impact", "scenario_to_event", "modulator_effects",
            "complexity_weights", "complexity_labels", "modulator_coupling",
            "temporal_modulator_defaults", "action_future_drives",
            "param_to_drive", "drive_action_bias", "inhibition_matrix",
        }
        for key, val in d.items():
            if key in field_map and key not in dict_fields:
                f = field_map[key]
                f_type = type_hints.get(key, f.type)
                if isinstance(val, dict) and isinstance(f_type, type) and hasattr(f_type, '__dataclass_fields__'):
                    # Reconstruct nested dataclass from dict
                    setattr(cfg, key, f_type(**val))
                elif isinstance(val, dict) and f_type in (Set[str], set):
                    setattr(cfg, key, set(val))
                else:
                    setattr(cfg, key, val)
        # Restore dict fields with proper type coercion for tuple keys
        for dict_field in dict_fields:
            if dict_field in d:
                raw = d[dict_field]
                if dict_field in ("qualia_names", "modulator_coupling"):
                    # These have tuple keys — YAML keeps tuples native, JSON
                    # serializes them as strings; accept both.
                    converted = {}
                    for k, v in raw.items():
                        if isinstance(k, str) and k.startswith("("):
                            try:
                                key_tuple = ast.literal_eval(k)
                                converted[key_tuple] = v
                            except (ValueError, SyntaxError):
                                converted[k] = v
                        else:
                            converted[k] = v
                    setattr(cfg, dict_field, converted)
                elif dict_field == "attention_gated_drives":
                    if isinstance(raw, (list, tuple)):
                        setattr(cfg, dict_field, set(raw))
                    else:
                        setattr(cfg, dict_field, raw)
                elif dict_field == "complexity_labels":
                    # List of tuples: [(float, str), ...]
                    converted = []
                    for item in raw:
                        if isinstance(item, list):
                            converted.append(tuple(item))
                        else:
                            converted.append(item)
                    setattr(cfg, dict_field, converted)
                else:
                    setattr(cfg, dict_field, raw)
        return cfg


# ──────────────────────────────────────────────────────────────────────────────
# GLOBAL INSTANCE
# ──────────────────────────────────────────────────────────────────────────────

AXIOM_CONFIG = AxiomConfig()


# ──────────────────────────────────────────────────────────────────────────────
# ACCESSOR / SERIALIZATION FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────

def get_config() -> AxiomConfig:
    """Return the global AXIOM_CONFIG instance."""
    return AXIOM_CONFIG


def load_config(path: Union[str, Path]) -> AxiomConfig:
    """Load a configuration from a JSON or YAML file."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Config file not found: {p}")

    text = p.read_text(encoding="utf-8")

    if p.suffix in (".yaml", ".yml"):
        try:
            import yaml
            data = yaml.safe_load(text)
        except ImportError:
            raise ImportError("PyYAML is required for YAML config files. "
                              "Install with: pip install pyyaml")
    else:
        data = json.loads(text)

    return AxiomConfig.from_dict(data)


def _json_safe(obj: Any) -> Any:
    """Recursively convert tuples/sets to JSON-safe containers.

    - tuple keys -> their string repr (``ast.literal_eval`` in ``from_dict``
      restores them on load; avoids YAML ``!!python/tuple`` tags too)
    - sets -> sorted lists
    """
    if isinstance(obj, dict):
        return {str(k) if isinstance(k, tuple) else k: _json_safe(v)
                for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe(v) for v in obj]
    if isinstance(obj, (set, frozenset)):
        return [_json_safe(v) for v in sorted(obj, key=str)]
    return obj


def save_config(config: AxiomConfig, path: Union[str, Path]) -> None:
    """Save a configuration to a JSON or YAML file."""
    p = Path(path)
    data = _json_safe(config.to_dict())

    if p.suffix in (".yaml", ".yml"):
        try:
            import yaml
            p.write_text(yaml.dump(data, default_flow_style=False, sort_keys=False),
                         encoding="utf-8")
        except ImportError:
            raise ImportError("PyYAML is required for YAML config files. "
                              "Install with: pip install pyyaml")
    else:
        p.write_text(json.dumps(data, indent=2, default=str),
                     encoding="utf-8")


def reset_config() -> AxiomConfig:
    """Reset the global config to defaults. Primarily for testing.

    WARNING: Code that captured a reference via ``cfg = get_config()`` before
    this call will retain the old config object.  After calling reset_config(),
    all callers must re-invoke get_config() to obtain the fresh instance.
    """
    global AXIOM_CONFIG
    AXIOM_CONFIG = AxiomConfig()
    return AXIOM_CONFIG


__all__ = [
    # Drive constants
    "DriveConstants", "ActionResolverConstants", "MoralResidueConstants",
    "ACTION_FUTURE_DRIVES", "PARAM_TO_DRIVE", "DRIVE_ACTION_BIAS",
    "INHIBITION_MATRIX", "ATTENTION_GATED_DRIVES",
    # Modulator constants
    "FatigueConstants", "AttentionConstants", "DreadConstants",
    "ModulatorBaselineConstants", "ModulatorEngineConstants",
    "ModulatorLabelConstants", "ModulatorScenarioScaling",
    "ModulatorFeedbackConstants", "MODULATOR_EFFECTS",
    # Layer constants
    "MetaCognitionConstants", "EmbodiedConstants", "AmbivalenceConstants",
    "QualiaConstants", "QUALIA_NAMES", "NarrativeConstants", "RATIONALISATIONS",
    # Probe constants
    "DeliberativeThresholds", "ConsciousnessThresholds", "CriterionWeights",
    "C1Constants", "C2Constants", "C3Constants", "C4Constants",
    "C5Constants", "C6Constants", "C7Constants", "C8Constants",
    # Simulation constants
    "TimeStepConstants", "FastPathConstants", "TemporalProjectorConstants",
    "OscillationIndexConstants", "HesitationConstants",
    "FAST_PATH_MAX_DEADLOCK", "IDENTITY_BASELINE",
    # Epigenetics constants
    "EpigeneticsConstants", "EPIGENETIC_IMPACT", "SCENARIO_TO_EVENT",
    "AutoregulationConstants", "SensitivityConstants",
    "AssociativeMemoryConstants", "DissonanceConstants",
    # Bio-metrics constants
    "BioMetricsConstants", "COMPLEXITY_WEIGHTS", "COMPLEXITY_LABELS",
    # Temporal constants
    "TemporalLoopConstants", "MODULATOR_COUPLING",
    "TEMPORAL_MODULATOR_DEFAULTS",
    "TEMPORAL_CORTISOL_HOURS_DECAY", "TEMPORAL_SEROTONIN_DEPLETION_CAP",
    "TEMPORAL_NOREPI_ENTROPY_THRESHOLD", "TEMPORAL_SCENARIO_BLEND",
    "TEMPORAL_PRIOR_BLEND", "TEMPORAL_FATIGUE_ACCUMULATION",
    "TEMPORAL_BASE_ENTROPY",
    # Main config
    "AxiomConfig", "AXIOM_CONFIG",
    "get_config", "load_config", "save_config", "reset_config",
]
