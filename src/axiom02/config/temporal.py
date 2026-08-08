"""Temporal loop configuration constants."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class TemporalLoopConstants:
    """Parameters for continuous temporal state propagation."""
    alpha_persist: float = 0.62
    alpha_circ: float = 0.20
    alpha_rumi: float = 0.18
    cortisol_se_threshold: float = 0.52
    cortisol_se_kappa: float = 0.060
    norepi_entropy_scale: float = 0.08
    narrative_stability_decay: float = 0.85
    narrative_recovery_coeff: float = 0.16
    narrative_erosion_irr: float = 0.06
    narrative_erosion_spite: float = 0.04
    narrative_erosion_dl: float = 0.03


# Modulator interdependency coupling matrix
MODULATOR_COUPLING: Dict[Tuple[str, str], float] = {
    ("cortisol", "serotonin"): -0.040,
    ("cortisol", "dopamine"): -0.025,
    ("norepinephrine", "oxytocin"): -0.020,
    ("norepinephrine", "serotonin"): -0.015,
    ("oxytocin", "cortisol"): -0.018,
    ("serotonin", "cortisol"): -0.022,
    ("dopamine", "norepinephrine"): 0.015,
    ("oxytocin", "norepinephrine"): 0.010,
}

# Modulator baselines (same as ModulatorBaselineConstants but as dict for propagation)
TEMPORAL_MODULATOR_DEFAULTS: Dict[str, float] = {
    "dopamine": 0.50, "serotonin": 0.50,
    "norepinephrine": 0.20, "cortisol": 0.20, "oxytocin": 0.30,
}

# Temporal-specific modulator parameters
TEMPORAL_CORTISOL_HOURS_DECAY: float = -0.12
TEMPORAL_SEROTONIN_DEPLETION_CAP: float = 0.40
TEMPORAL_NOREPI_ENTROPY_THRESHOLD: float = 0.60
TEMPORAL_SCENARIO_BLEND: float = 0.60
TEMPORAL_PRIOR_BLEND: float = 0.40
TEMPORAL_FATIGUE_ACCUMULATION: float = 0.20
TEMPORAL_BASE_ENTROPY: float = 0.50


__all__ = [
    "TemporalLoopConstants", "MODULATOR_COUPLING",
    "TEMPORAL_MODULATOR_DEFAULTS",
    "TEMPORAL_CORTISOL_HOURS_DECAY", "TEMPORAL_SEROTONIN_DEPLETION_CAP",
    "TEMPORAL_NOREPI_ENTROPY_THRESHOLD", "TEMPORAL_SCENARIO_BLEND",
    "TEMPORAL_PRIOR_BLEND", "TEMPORAL_FATIGUE_ACCUMULATION",
    "TEMPORAL_BASE_ENTROPY",
]
