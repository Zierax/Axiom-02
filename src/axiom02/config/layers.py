"""Consciousness/deliberative complexity layer constants."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Tuple


@dataclass(frozen=True)
class MetaCognitionConstants:
    """Parameters for the meta-cognitive monitor — frustration from deadlock."""
    frustration_per_deadlock_step: float = 0.08
    frustration_decay_per_fire: float = 0.12
    frustration_base_scale: float = 1.0
    frustration_escalation: float = 0.05
    frustration_threshold_boost: float = 0.30
    frustration_spite_multiplier: float = 0.15
    frustration_resentment_multiplier: float = 0.12
    frustration_despair_multiplier: float = 0.08
    awareness_steps: list = field(default_factory=lambda: [3, 7, 12])


@dataclass(frozen=True)
class EmbodiedConstants:
    """Parameters for pre-fire hesitation simulation."""
    guilt_tolerance: float = 0.55
    grief_tolerance: float = 0.60
    hesitation_trigger: float = 0.70
    cost_weight_negative: float = 0.25


@dataclass(frozen=True)
class AmbivalenceConstants:
    """Parameters for superposition output — the 'road not taken'."""
    ambivalence_threshold: float = 0.35
    secondary_human_weight: float = 0.70
    secondary_cold_weight: float = 0.45
    secondary_default_weight: float = 0.35


@dataclass(frozen=True)
class QualiaConstants:
    """Parameters for qualia approximation — interference-pattern fingerprints."""
    qualia_signature_dims: int = 9
    qualia_corr_near_zero: float = 1e-9
    qualia_welch_min_nperseg: int = 2
    qualia_psd_floor: float = 1e-9
    qualia_max_distance: float = 2.5


# Qualia names: which drive combinations produce which 'feelings'
QUALIA_NAMES: Dict[Tuple[str, ...], str] = {
    ("grief", "love", "sacrifice_drive"): "anguished_love",
    ("rage", "resentment", "pride"): "indignant_fury",
    ("fear", "guilt", "cold_logic"): "paralytic_dread",
    ("despair", "grief", "acceptance"): "melancholic_peace",
    ("spite", "resentment", "pride"): "defiant_contempt",
    ("love", "sacrifice_drive", "empathy"): "compassionate_surrender",
    ("pride", "rage", "revenge_drive"): "wrathful_honour",
    ("guilt", "shame", "despair"): "crushed_conscience",
    ("hope", "love", "empathy"): "tender_longing",
    ("cold_logic", "acceptance", "self_preservation"): "calculated_resolve",
    ("fear", "self_preservation", "despair"): "existential_terror",
}


@dataclass(frozen=True)
class NarrativeConstants:
    """Parameters for post-hoc identity rationalisation."""
    strong_rationalisation_threshold: float = 0.70
    partial_rationalisation_threshold: float = 0.50
    strong_identity_adj_max: float = 0.20
    strong_identity_scaling: float = 0.25
    partial_identity_adj: float = 0.05


# Narrative rationalisations: action → post-hoc identity repair text
RATIONALISATIONS: Dict[str, str] = {
    "yield_organ_to_sibling": "I chose love over self — that is who I am.",
    "proceed_with_murder": "History demands extraordinary men act.",
    "paralysis_frozen_in_place": "Even inaction is a statement.",
    "disconnect_life_support_in_grief": "I refused to let them reduce me to nothing.",
    "return_ticket_to_god": "I accept the logic, but I refuse the harmony.",
    "choose_worse_concert_despite_knowing": "To prove I am not your formula.",
    "resist_knowing_erasure": "Dignity is the only thing that was ever mine.",
    "sacrifice_self_to_protect_world": "They exist because I loved them.",
    "confess_voluntarily": "The lie was heavier than the sentence.",
    "release_javert": "A man who never showed mercy was shown it anyway.",
    "reveal_identity_lose_everything": "A stranger's life was worth my freedom.",
    "shoot_lennie_from_love": "I did the only thing that love had left to offer.",
    "give_everything_away": "There was no calculation — just hands and need.",
}


__all__ = [
    "MetaCognitionConstants", "EmbodiedConstants", "AmbivalenceConstants",
    "QualiaConstants", "QUALIA_NAMES", "NarrativeConstants", "RATIONALISATIONS",
]
