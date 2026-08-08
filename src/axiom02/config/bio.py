"""Bio-metrics configuration constants."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class BioMetricsConstants:
    """Parameters for consciousness bio-metrics computation."""
    cognitive_load_threshold: float = 0.28
    attractor_min_visits: int = 3


# Complexity score weights (sum to ~1.0)
COMPLEXITY_WEIGHTS: Dict[str, float] = {
    "drive_voltage": 0.08,
    "cognitive_load": 0.06,
    "drive_volatility": 0.05,
    "decision_entropy": 0.09,
    "oscillation_frequency": 0.06,
    "oscillation_amplitude": 0.10,
    "oscillation_entropy": 0.08,
    "attractor_strength": 0.07,
    "paralysis_depth": 0.25,
    "trauma_persistence": 0.08,
    "spectral_entropy": 0.04,
    "phase_coherence": 0.04,
}

# Complexity labels: score threshold → human-readable label
COMPLEXITY_LABELS: List[Tuple[float, str]] = [
    (0.65, "CRITICAL — extreme internal conflict"),
    (0.45, "HIGH — significant drive conflict"),
    (0.25, "MODERATE — measurable above baseline"),
    (0.12, "LOW — marginal signal above noise floor"),
    (0.00, "MINIMAL — near-baseline emotional state"),
]


__all__ = [
    "BioMetricsConstants", "COMPLEXITY_WEIGHTS", "COMPLEXITY_LABELS",
]
