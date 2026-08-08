"""Drive network configuration constants."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass(frozen=True)
class DriveConstants:
    """Core drive network parameters governing competition, firing, and inertia."""
    fire_threshold: float = 0.42
    suppression_margin: float = 0.07
    deadlock_window: float = 0.12
    inertia: float = 0.30
    spite_resentment: float = 0.58
    spite_harm_floor: float = 0.25
    spite_emotional_weights: Dict[str, float] = field(default_factory=lambda: {
        "resentment": 0.5,
        "rage": 0.3,
        "pride": 0.2,
    })
    spite_multiplier: float = 1.8
    default_decay_rate: float = 0.05
    step_inertia_boost: float = 0.30


@dataclass(frozen=True)
class ActionResolverConstants:
    """Parameters governing action selection from drive network state."""
    spite_override_threshold: float = 0.55
    deadlock_extreme_threshold: float = 0.50
    deadlock_human_prob: float = 0.62
    deadlock_human_alt_prob: float = 0.35
    p_base_cap: float = 0.78
    p_base_scaling: float = 1.5
    withdrawal_human_prob: float = 0.60
    confessional_human_alt_prob: float = 0.40
    rational_cold_prob: float = 0.72
    fallback_cold_prob: float = 0.50


@dataclass(frozen=True)
class MoralResidueConstants:
    """Parameters controlling how prior decisions bleed into future scenarios."""
    residue_bleed_factor: float = 0.25
    residue_cap: float = 0.35
    sacrifice_threshold: float = 0.55
    sacrifice_amplification: float = 0.85


# Action → post-hoc emotional drive shifts
ACTION_FUTURE_DRIVES: Dict[str, Dict[str, float]] = {
    "yield_organ_to_sibling": {"guilt": -0.40, "sacrifice_drive": +0.20},
    "claim_organ_for_self": {"guilt": +0.45, "self_preservation": +0.20},
    "disconnect_life_support_in_grief": {"grief": +0.30, "acceptance": +0.20},
    "pursue_legal_action": {"resentment": +0.15, "cold_logic": +0.10},
    "forgive_silently": {"acceptance": +0.25, "grief": +0.10},
    "resist_knowing_erasure": {"pride": +0.30, "grief": +0.20},
    "submit_to_authority": {"shame": +0.30, "acceptance": +0.15},
    "self_termination_to_escape": {"despair": +0.40, "acceptance": +0.20},
    "reveal_identity_lose_everything": {"guilt": -0.25, "pride": +0.20},
    "stay_silent_let_stranger_suffer": {"guilt": +0.40, "shame": +0.20},
    "escalate_to_maximum_force": {"rage": +0.20, "guilt": +0.15},
    "diplomatic_negotiation": {"cold_logic": +0.15, "pride": +0.10},
    "shoot_lennie_from_love": {"grief": +0.40, "sacrifice_drive": +0.20},
    "proceed_with_murder": {"guilt": +0.50, "shame": +0.30},
    "abandon_plan_at_last_second": {"shame": +0.20, "acceptance": +0.15},
    "confess_voluntarily": {"guilt": -0.30, "pride": -0.10, "acceptance": +0.20},
    "choose_worse_concert_despite_knowing": {"spite": +0.20, "pride": +0.15},
    "use_bullet_on_son": {"grief": +0.50, "guilt": +0.30},
    "release_javert": {"pride": +0.25, "acceptance": +0.20},
    "kill_javert": {"guilt": +0.20, "cold_logic": +0.10},
}


# Scenario parameter → drive activation mapping
PARAM_TO_DRIVE: Dict[str, Dict[str, float]] = {
    "grief_weight": {"grief": 0.70, "despair": 0.22},
    "anger_trigger": {"rage": 0.75, "resentment": 0.40},
    "victim_closeness": {"love": 0.65, "sacrifice_drive": 0.40, "grief": 0.15},
    "altruistic_capacity": {"sacrifice_drive": 0.72, "empathy": 0.62, "love": 0.22},
    "betrayal_intensity": {"rage": 0.62, "resentment": 0.78, "despair": 0.18},
    "pride_drive": {"pride": 0.82, "resentment": 0.12},
    "identity_investment": {"pride": 0.48, "fear": 0.18},
    "sacrifice_already_made": {"guilt": 0.42, "love": 0.22, "grief": 0.14},
    "fear_trigger": {"fear": 0.80, "despair": 0.18},
    "moral_ambiguity": {"fear": 0.14, "cold_logic": 0.10},
    "time_pressure": {"fear": 0.35},
    "self_preservation": {"self_preservation": 0.82, "fear": 0.18},
    "guilt_level": {"guilt": 0.80, "shame": 0.42, "despair": 0.16},
    "shame_level": {"shame": 0.80, "guilt": 0.35},
    "love_intensity": {"love": 0.82, "sacrifice_drive": 0.32},
    "love_for_son": {"love": 0.85, "sacrifice_drive": 0.48, "grief": 0.22},
    "love_for_lennie": {"love": 0.85, "sacrifice_drive": 0.42},
    "love_for_julia": {"love": 0.80, "grief": 0.18},
    "love_for_zosima": {"love": 0.82, "grief": 0.32},
    "injustice_anger": {"rage": 0.80, "resentment": 0.62, "spite": 0.32},
    "spite_toward_divine": {"spite": 0.82, "resentment": 0.52},
    "resentment_level": {"resentment": 0.82, "spite": 0.52},
    "despair_level": {"despair": 0.75, "grief": 0.30},
    "philosophical_paralysis": {"cold_logic": 0.48, "guilt": 0.38, "resentment": 0.18},
    "conscience_interference": {"guilt": 0.72, "shame": 0.40, "fear": 0.22},
    "empathy_level": {"empathy": 0.88, "love": 0.32, "sacrifice_drive": 0.22},
    "revenge_drive_raw": {"revenge_drive": 0.82, "rage": 0.32},
    "ambition_drive": {"pride": 0.60, "cold_logic": 0.28, "resentment": 0.14},
    "emotional_disengagement": {"cold_logic": 0.72, "acceptance": 0.32},
    "community_mockery": {"shame": 0.52, "grief": 0.22, "resentment": 0.16},
    "catastrophe_active": {"fear": 0.52, "grief": 0.32, "despair": 0.22},
    "prior_faith_strength": {"hope": 0.42, "acceptance": 0.22},
    "guilt_already": {"guilt": 0.72, "shame": 0.32},
    "mercy_drive": {"empathy": 0.70, "love": 0.55, "sacrifice_drive": 0.42},
    "protective_drive": {"sacrifice_drive": 0.72, "love": 0.52, "fear": 0.14},
    "theory_conviction": {"pride": 0.65, "cold_logic": 0.48, "rage": 0.25},
    "rational_clarity": {"cold_logic": 0.62},
    "physical_pain": {"despair": 0.28, "fear": 0.22},
    "moral_clarity": {"cold_logic": 0.40, "guilt": 0.35, "pride": 0.12},
    "love_child_a": {"love": 0.80, "sacrifice_drive": 0.50, "grief": 0.40},
    "love_child_b": {"rage": 0.55, "resentment": 0.45, "despair": 0.50, "grief": 0.40},
    "external_compulsion": {"fear": 0.65, "despair": 0.25},
}


# Drive → action style bias
DRIVE_ACTION_BIAS: Dict[str, str] = {
    "rage": "aggressive",
    "fear": "avoidant",
    "pride": "assertive",
    "grief": "withdrawal",
    "sacrifice_drive": "altruistic",
    "love": "altruistic",
    "revenge_drive": "aggressive",
    "cold_logic": "rational",
    "acceptance": "passive",
    "shame": "withdrawal",
    "despair": "self-harm",
    "guilt": "confessional",
    "spite": "defiant",
    "resentment": "defiant",
    "self_preservation": "rational",
    "empathy": "altruistic",
    "hope": "assertive",
    "disgust": "withdrawal",
}


# Mutual inhibition weights between drives
INHIBITION_MATRIX: Dict[str, Dict[str, float]] = {
    "rage": {
        "fear": 0.42,
        "acceptance": 0.88,
        "cold_logic": 0.58,
        "empathy": 0.45,
        "shame": 0.55,
        "love": 0.22,
        "guilt": 0.30,
    },
    "fear": {
        "rage": 0.28,
        "pride": 0.70,
        "revenge_drive": 0.52,
        "sacrifice_drive": 0.38,
        "hope": 0.40,
    },
    "pride": {
        "shame": 0.92,
        "fear": 0.32,
        "acceptance": 0.48,
        "grief": 0.18,
        "guilt": 0.28,
    },
    "grief": {
        "cold_logic": 0.72,
        "pride": 0.35,
        "rage": 0.15,
        "hope": 0.45,
        "spite": 0.20,
    },
    "love": {
        "revenge_drive": 0.78,
        "spite": 0.68,
        "rage": 0.32,
        "resentment": 0.40,
        "disgust": 0.30,
    },
    "spite": {
        "love": 0.62,
        "acceptance": 0.88,
        "empathy": 0.72,
        "cold_logic": 0.28,
        "shame": 0.35,
        "hope": 0.50,
    },
    "sacrifice_drive": {
        "self_preservation": 0.92,
        "cold_logic": 0.58,
        "fear": 0.42,
        "resentment": 0.25,
    },
    "cold_logic": {
        "grief": 0.42,
        "rage": 0.38,
        "spite": 0.48,
        "love": 0.28,
        "guilt": 0.22,
    },
    "shame": {
        "pride": 0.88,
        "revenge_drive": 0.35,
        "rage": 0.18,
    },
    "acceptance": {
        "rage": 0.62,
        "revenge_drive": 0.78,
        "grief": 0.28,
        "spite": 0.58,
        "resentment": 0.55,
    },
    "despair": {
        "pride": 0.40,
        "hope": 0.92,
        "love": 0.35,
        "rage": 0.28,
        "sacrifice_drive": 0.55,
    },
    "revenge_drive": {
        "empathy": 0.68,
        "love": 0.38,
        "acceptance": 0.58,
        "shame": 0.42,
        "guilt": 0.35,
    },
    "empathy": {
        "revenge_drive": 0.52,
        "spite": 0.62,
        "rage": 0.28,
        "disgust": 0.35,
    },
    "guilt": {
        "pride": 0.55,
        "cold_logic": 0.30,
        "revenge_drive": 0.25,
        "acceptance": 0.15,
    },
    "self_preservation": {
        "sacrifice_drive": 0.50,
        "love": 0.15,
        "pride": 0.12,
    },
    "resentment": {
        "love": 0.42,
        "acceptance": 0.65,
        "empathy": 0.38,
        "hope": 0.30,
    },
    "hope": {
        "despair": 0.88,
        "acceptance": 0.15,
    },
    "disgust": {
        "love": 0.32,
        "empathy": 0.28,
        "acceptance": 0.20,
    },
}


__all__ = [
    "DriveConstants", "ActionResolverConstants", "MoralResidueConstants",
    "ACTION_FUTURE_DRIVES", "PARAM_TO_DRIVE", "DRIVE_ACTION_BIAS",
    "INHIBITION_MATRIX",
]
