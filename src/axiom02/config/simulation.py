"""Simulation and time-step constants."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TimeStepConstants:
    """Simulation time parameters."""
    time_steps: int = 20
    step_duration: int = 5
    deadlock_jitter: float = 0.04
    step_decay_rate: float = 0.03
    event_condition_threshold: float = 0.2


@dataclass(frozen=True)
class FastPathConstants:
    """Thresholds for instant action selection (hot cognition bypass)."""
    parental_love_threshold: float = 0.88
    parental_sacrifice_threshold: float = 0.75
    parental_closure_threshold: float = 0.90
    pride_threshold: float = 0.85
    resentment_threshold: float = 0.70
    consequence_threshold: float = 0.50
    mercy_empathy_threshold: float = 0.82
    mercy_love_threshold: float = 0.65
    mercy_rage_max: float = 0.30
    freeze_fear_threshold: float = 0.90
    freeze_sp_threshold: float = 0.80
    freeze_love_max: float = 0.40


@dataclass(frozen=True)
class TemporalProjectorConstants:
    """Parameters for affective forecasting — projecting future emotional cost."""
    guilt_threshold: float = 0.35
    sacrifice_boost_max: float = 0.25
    guilt_scaling: float = 0.40
    guilt_boost_max: float = 0.15
    guilt_boost_scaling: float = 0.20
    pride_boost: float = 0.08


@dataclass(frozen=True)
class OscillationIndexConstants:
    """Parameters for the oscillation index computation."""
    transition_weight: float = 0.65
    deadlock_weight: float = 0.35


@dataclass(frozen=True)
class HesitationConstants:
    """Parameters for hesitation (embodied simulation) behavior."""
    seed_offset: int = 99
    deadlock_extension: int = 2


FAST_PATH_MAX_DEADLOCK: int = 8
IDENTITY_BASELINE: float = 0.5


__all__ = [
    "TimeStepConstants", "FastPathConstants", "TemporalProjectorConstants",
    "OscillationIndexConstants", "HesitationConstants",
    "FAST_PATH_MAX_DEADLOCK", "IDENTITY_BASELINE",
]
