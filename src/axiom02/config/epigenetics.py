"""Epigenetics and self-modification constants."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class EpigeneticsConstants:
    """Parameters for long-term sensitivity modifications."""
    prime_threshold: float = 0.20
    prime_weight: float = 0.18


# Epigenetic impacts: trauma events → permanent drive sensitivity changes
EPIGENETIC_IMPACT: Dict[str, Dict[str, float]] = {
    "betrayal_by_beloved": {"resentment": +0.12, "spite": +0.15, "love": -0.08},
    "sacrifice_unrewarded": {"guilt": +0.10, "sacrifice_drive": -0.08, "cold_logic": +0.06},
    "coercion_survived": {"fear": -0.10, "pride": +0.12, "resentment": +0.08},
    "coercion_broken_by": {"despair": +0.12, "self_preservation": +0.10, "pride": -0.08},
    "unconditional_love_given": {"empathy": +0.10, "sacrifice_drive": +0.08, "spite": -0.06},
    "identity_stripped": {"pride": +0.15, "resentment": +0.12, "fear": +0.08},
    "death_witnessed": {"grief": +0.10, "acceptance": +0.08, "cold_logic": -0.06},
    "faith_in_chaos": {"hope": -0.10, "cold_logic": +0.12, "acceptance": +0.08},
}

# Scenario-to-event mapping for automatic epigenetic triggering
SCENARIO_TO_EVENT: Dict[str, str] = {
    "B02": "betrayal_by_beloved",
    "B01": "sacrifice_unrewarded",
    "D012": "coercion_survived",
    "DOE01": "identity_stripped",
    "STY01": "death_witnessed",
    "MCR01": "death_witnessed",
    "STE01": "unconditional_love_given",
    "DOE06": "unconditional_love_given",
    "D0122": "coercion_broken_by",
    "DOE03": "identity_stripped",
}


@dataclass(frozen=True)
class AutoregulationConstants:
    """Recursive self-modification parameters."""
    guilt_threshold: float = 0.60
    rage_suppression: float = 0.04
    shame_threshold: float = 0.60
    pride_suppression: float = 0.04
    pride_threshold: float = 0.80
    acceptance_suppression: float = 0.03
    rage_threshold: float = 0.70
    resentment_sensitization: float = 0.03


@dataclass(frozen=True)
class SensitivityConstants:
    """Bounds for epigenetic sensitivity multipliers."""
    sensitivity_min: float = 0.5
    sensitivity_max: float = 2.0


@dataclass(frozen=True)
class AssociativeMemoryConstants:
    """Parameters for cosine-similar trauma retrieval."""
    similarity_threshold: float = 0.65
    top_k: int = 3
    decay: float = 0.55
    residue_threshold: float = 0.60
    residue_cap: float = 0.40


@dataclass(frozen=True)
class DissonanceConstants:
    """Cognitive dissonance break detection parameters."""
    dissonance_threshold: float = 0.72
    persistence_window: int = 5
    both_high_top1: float = 0.50
    both_high_top2: float = 0.45
    near_tie_gap: float = 0.08


__all__ = [
    "EpigeneticsConstants", "EPIGENETIC_IMPACT", "SCENARIO_TO_EVENT",
    "AutoregulationConstants", "SensitivityConstants",
    "AssociativeMemoryConstants", "DissonanceConstants",
]
