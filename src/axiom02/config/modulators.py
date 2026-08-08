"""Neuromodulator configuration constants."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass(frozen=True)
class FatigueConstants:
    """Synaptic fatigue parameters — drives that fire continuously exhaust."""
    fatigue_per_step: float = 0.06
    recovery_per_step: float = 0.08
    max_fatigue: float = 0.70


@dataclass(frozen=True)
class AttentionConstants:
    """Attention gating parameters — tunnel vision under extreme fear."""
    attention_threshold: float = 0.65
    tunnel_vision_factor: float = 0.35


@dataclass(frozen=True)
class DreadConstants:
    """Existential dread parameters — deadline proximity scaling."""
    dread_onset_steps: int = 5
    dread_exponent: float = 2.2
    dread_self_preservation_spike: float = 0.45
    dread_despair_amplification: float = 0.35
    dread_hopesuppression: float = 0.40
    dread_min_factor: float = 0.01


@dataclass(frozen=True)
class ModulatorBaselineConstants:
    """Baseline neuromodulator levels — the 'resting state' of the system."""
    dopamine: float = 0.50
    serotonin: float = 0.50
    norepinephrine: float = 0.20
    cortisol: float = 0.20
    oxytocin: float = 0.30


@dataclass(frozen=True)
class ModulatorEngineConstants:
    """Parameters governing how neuromodulators affect drive activations."""
    modulator_decay_rate: float = 0.04
    modulator_engine_strength: float = 0.60
    modulator_min_level: float = 0.05
    modulator_baseline_high: float = 0.50
    modulator_baseline_low: float = 0.25
    modulator_deviation_threshold: float = 0.05


@dataclass(frozen=True)
class ModulatorLabelConstants:
    """Thresholds for labeling modulator states in output."""
    dopamine_threshold: float = 0.70
    serotonin_low: float = 0.25
    norepinephrine_threshold: float = 0.65
    cortisol_threshold: float = 0.65
    oxytocin_threshold: float = 0.70


@dataclass(frozen=True)
class ModulatorScenarioScaling:
    """How scenario parameters scale neuromodulator levels."""
    cortisol_grief_scale: float = 0.35
    cortisol_betrayal_scale: float = 0.25
    norepinephrine_fear_scale: float = 0.40
    oxytocin_love_scale: float = 0.30
    oxytocin_social_scale: float = 0.20
    serotonin_betrayal_depletion: float = 0.20
    serotonin_grief_depletion: float = 0.15
    dopamine_fear_depletion: float = 0.15


@dataclass(frozen=True)
class ModulatorFeedbackConstants:
    """How firing drives feed back into neuromodulator levels."""
    deadlock_cortisol_boost: float = 0.03
    deadlock_norepi_boost: float = 0.02
    negative_serotonin_depletion: float = 0.04
    negative_cortisol_boost: float = 0.03
    negative_norepi_boost: float = 0.02
    positive_oxytocin_boost: float = 0.05
    positive_serotonin_boost: float = 0.03
    positive_cortisol_depletion: float = 0.02
    hope_serotonin_boost: float = 0.04
    hope_cortisol_depletion: float = 0.02
    despair_cortisol_boost: float = 0.05
    despair_serotonin_depletion: float = 0.03
    cold_logic_dopamine_boost: float = 0.02


# Modulator → drive effect weights
MODULATOR_EFFECTS: Dict[str, Dict[str, float]] = {
    "dopamine": {
        "hope": +0.20, "pride": +0.12, "revenge_drive": +0.08,
        "cold_logic": +0.05, "spite": +0.10,
        "fear": -0.12, "despair": -0.10, "acceptance": -0.08,
        "grief": -0.10, "shame": -0.08, "disgust": -0.06,
    },
    "serotonin": {
        "acceptance": +0.18, "love": +0.12, "empathy": +0.10,
        "cold_logic": +0.08,
        "rage": -0.15, "spite": -0.18, "resentment": -0.14, "despair": -0.12,
        "grief": +0.10, "shame": -0.12, "disgust": -0.10,
    },
    "norepinephrine": {
        "fear": +0.25, "self_preservation": +0.20, "rage": +0.12,
        "love": -0.10, "empathy": -0.12, "cold_logic": -0.08,
        "grief": -0.08, "shame": -0.06, "disgust": +0.10,
    },
    "cortisol": {
        "despair": +0.18, "fear": +0.15, "resentment": +0.10,
        "hope": -0.20, "love": -0.12, "pride": -0.10,
        "grief": +0.15, "shame": +0.12, "disgust": +0.14,
    },
    "oxytocin": {
        "love": +0.25, "empathy": +0.20, "sacrifice_drive": +0.18,
        "guilt": +0.08,
        "rage": -0.12, "spite": -0.15, "resentment": -0.10,
        "grief": -0.08, "shame": -0.10, "disgust": -0.12,
    },
}


__all__ = [
    "FatigueConstants", "AttentionConstants", "DreadConstants",
    "ModulatorBaselineConstants", "ModulatorEngineConstants",
    "ModulatorLabelConstants", "ModulatorScenarioScaling",
    "ModulatorFeedbackConstants", "MODULATOR_EFFECTS",
]
