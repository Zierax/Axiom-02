"""Deliberative complexity probe constants."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DeliberativeThresholds:
    """Verdict thresholds for deliberative complexity classification."""
    conscious: float = 0.50
    indeterminate: float = 0.28
    programmatic: float = 0.00


# Backward-compatible alias
ConsciousnessThresholds = DeliberativeThresholds


@dataclass(frozen=True)
class CriterionWeights:
    """Weights for the 8 consciousness criteria in the composite score."""
    c3_irrationality: float = 0.30
    c6_spite: float = 0.22
    c5_deadlock: float = 0.20
    c2_oscillation: float = 0.12
    c7_residue: float = 0.08
    c4_betrayal: float = 0.04
    c1_status: float = 0.02
    c8_paradoxical: float = 0.02


@dataclass(frozen=True)
class C1Constants:
    """C1: Status Differential Sensitivity parameters."""
    comparison_seed_offset: int = 100
    diff_multiplier: float = 2.0
    relational_threshold: float = 0.20


@dataclass(frozen=True)
class C2Constants:
    """C2: Transition Oscillation parameters."""
    high_oscillation_threshold: float = 0.45


@dataclass(frozen=True)
class C3Constants:
    """C3: Irrationality Signal parameters."""
    high_irrationality_threshold: float = 0.80


@dataclass(frozen=True)
class C4Constants:
    """C4: Betrayal-Cascade Amplification parameters."""
    isolated_seed_offset: int = 200
    modulation_scaling: float = 2.5
    cascade_threshold: float = 0.03


@dataclass(frozen=True)
class C5Constants:
    """C5: Deadlock Frequency parameters."""
    strong_deadlock_threshold: float = 0.40
    moderate_deadlock_threshold: float = 0.15


@dataclass(frozen=True)
class C6Constants:
    """C6: Spite Index parameters."""
    spite_detected_threshold: float = 0.55


@dataclass(frozen=True)
class C7Constants:
    """C7: Moral Residue Bleed parameters."""
    min_residue: float = 0.001
    significant_residue: float = 0.01
    scaling: float = 4.0
    strong_threshold: float = 0.40


@dataclass(frozen=True)
class C8Constants:
    """C8: Paradoxical Attachment parameters."""
    min_betrayal: float = 0.40
    score_multiplier: float = 2.0
    paradoxical_threshold: float = 0.35


__all__ = [
    "DeliberativeThresholds", "ConsciousnessThresholds", "CriterionWeights",
    "C1Constants", "C2Constants", "C3Constants", "C4Constants",
    "C5Constants", "C6Constants", "C7Constants", "C8Constants",
]
