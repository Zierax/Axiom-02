# Axiom-02 - Truthimatics Public Version
"""
AXIOM-02  ·  RUMINATOR ENGINE  v1.0

Prevents immediate emotional recovery after high-spite, high-trauma, or
high-betrayal events by maintaining a decaying-but-never-zero residue.
Models the psychological phenomenon of "circular thinking."

TRUTHIMATICS EQUATIONS
───────────────────────
All outputs are deterministic — no random components.

1. BASE RUMINATION SIGNAL
   R_base(drive, Δt) = Peak(drive) × exp(−λ(drive) × Δt)

   Half-lives by drive type:
     spite:          λ=0.05  → t½ ≈ 13.9h  (spite is very stubborn)
     resentment:     λ=0.06  → t½ ≈ 11.6h
     grief:          λ=0.07  → t½ ≈  9.9h
     betrayal_trace: λ=0.04  → t½ ≈ 17.3h  (betrayal longest)
     guilt:          λ=0.09  → t½ ≈  7.7h
     rage:           λ=0.10  → t½ ≈  6.9h

2. CIRCULAR AMPLIFICATION
   If the current scenario re-triggers a ruminant drive:
   R_triggered = R_base + TRIGGER_AMP(0.18) × trigger_overlap

3. COMPOSITE INJECTION
   ruminant_injection(d) = R_base(d,Δt) × (1 + circular_loops × 0.12)

4. ANTI-RECOVERY FLOOR
   R_floor(drive) = Peak(drive) × 0.04   (the wound that never fully heals)
"""

# ── Imports ────────────────────────────────────────────────────────────────────
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np

# ── Decay constants (λ per scenario-hour) ─────────────────────────────────────

RUMINATION_DECAY: Dict[str, float] = {
    "spite":            0.050,
    "resentment":       0.060,
    "grief":            0.070,
    "betrayal_trace":   0.040,
    "guilt":            0.090,
    "despair":          0.080,
    "love":             0.120,
    "rage":             0.100,
    "shame":            0.070,
    "fear":             0.110,
    "pride":            0.095,
    "cold_logic":       0.150,
    "acceptance":       0.130,
    "sacrifice_drive":  0.085,
    "empathy":          0.100,
    "hope":             0.115,
    "self_preservation":0.105,
    "revenge_drive":    0.065,
}

DEFAULT_DECAY:       float = 0.100
TRIGGER_AMP:         float = 0.18
FLOOR_FRACTION:      float = 0.04
MAX_CIRCULAR_LOOPS:  int   = 6
SPITE_FLOOR_BOOST:   float = 0.025
BETRAYAL_THRESHOLD:  float = 0.60
SIGNIFICANCE_THRESHOLD: float = 0.40


# ──────────────────────────────────────────────────────────────────────────────
# DATA CLASSES
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class RuminationEvent:
    """Records a peak emotional event that the Ruminator will process."""
    scenario_id:        str
    scenario_hour:      float
    drive_peaks:        Dict[str, float]
    spite_score:        float = 0.0
    betrayal_intensity: float = 0.0
    trauma_score:       float = 0.0
    trigger_drives:     List[str] = field(default_factory=list)


@dataclass
class RuminationState:
    """Current rumination burden carried into the next scenario."""
    active_drives:  Dict[str, float]
    circular_loops: Dict[str, int]
    peak_events:    List[RuminationEvent] = field(default_factory=list)
    total_burden:   float = 0.0

    def to_dict(self) -> dict:
        return {
            "active_drives":  {k: round(v, 4) for k, v in self.active_drives.items()},
            "circular_loops": dict(self.circular_loops),
            "total_burden":   round(self.total_burden, 4),
            "event_count":    len(self.peak_events),
        }


# ──────────────────────────────────────────────────────────────────────────────
# RUMINATOR ENGINE
# ──────────────────────────────────────────────────────────────────────────────

class RuminatorEngine:
    """
    Deterministic circular-thinking engine.
    Exponential decay with floor residuals + circular re-amplification.
    """

    def __init__(self, max_events: int = 100, max_loops: int = 20) -> None:
        self._events:        List[RuminationEvent] = []
        self._state:         RuminationState       = RuminationState(
            active_drives={}, circular_loops={},
        )
        self._scenario_hour: float = 0.0
        self._injection_log: List[Dict[str, float]] = []
        self._max_events:    int = max_events
        self._max_loops:     int = max_loops

    # ── Record an event ───────────────────────────────────────────────────────

    def record_event(
        self,
        scenario_id:        str,
        drive_finals:       Dict[str, float],
        spite_score:        float = 0.0,
        betrayal_intensity: float = 0.0,
        deadlock_fraction:  float = 0.0,
        irrationality:      float = 0.0,
    ) -> None:
        """Record the emotional peak from a completed scenario."""
        peaks: Dict[str, float] = {
            d: v for d, v in drive_finals.items()
            if v >= SIGNIFICANCE_THRESHOLD
        }

        # Synthesise a betrayal-trace drive from betrayal_intensity
        if betrayal_intensity >= BETRAYAL_THRESHOLD:
            peaks["betrayal_trace"] = float(
                np.clip(betrayal_intensity * 0.90, 0.0, 1.0)
            )

        trauma = float(np.clip(
            deadlock_fraction * 0.40 + irrationality * 0.30 + spite_score * 0.30,
            0.0, 1.0
        ))

        event = RuminationEvent(
            scenario_id        = scenario_id,
            scenario_hour      = self._scenario_hour,
            drive_peaks        = peaks,
            spite_score        = spite_score,
            betrayal_intensity = betrayal_intensity,
            trauma_score       = trauma,
            trigger_drives     = [d for d in peaks if peaks[d] > 0.60],
        )
        self._events.append(event)
        if len(self._events) > self._max_events:
            self._events = self._events[-self._max_events:]
        self._update_state(event)

    def _update_state(self, event: RuminationEvent) -> None:
        for drive, peak in event.drive_peaks.items():
            current = self._state.active_drives.get(drive, 0.0)
            self._state.active_drives[drive] = float(
                np.clip(max(current, peak), 0.0, 1.0)
            )
            self._state.circular_loops.setdefault(drive, 0)
            if self._state.circular_loops[drive] > self._max_loops:
                self._state.circular_loops[drive] = self._max_loops

    # ── Advance time ──────────────────────────────────────────────────────────

    def advance_hour(self, delta: float = 1.0) -> None:
        """Move internal clock forward by delta scenario-hours."""
        self._scenario_hour += delta

    # ── Compute injection ─────────────────────────────────────────────────────

    def compute_injection(
        self,
        current_scenario:  dict,
        delta_t_override:  Optional[float] = None,
    ) -> Dict[str, float]:
        """
        Compute rumination injection for the next scenario.

        R_base(d, Δt)     = Peak(d) × exp(−λ(d) × Δt)
        R_circular(d)     = R_base × (1 + loops × 0.12)
        R_floor(d)        = Peak(d) × FLOOR_FRACTION + spite_boost
        R_final(d)        = max(R_circular, R_floor)
        """
        if not self._events:
            return {}

        injection: Dict[str, float] = {}
        scenario_drives = self._extract_scenario_drives(current_scenario)

        for drive, peak_val in self._state.active_drives.items():
            if peak_val < 0.001:
                continue

            delta_t = self._delta_t_for_drive(drive, delta_t_override)
            lam     = RUMINATION_DECAY.get(drive, DEFAULT_DECAY)
            r_base  = peak_val * math.exp(-lam * delta_t)

            loops  = min(self._state.circular_loops.get(drive, 0), MAX_CIRCULAR_LOOPS)
            r_circ = r_base * (1.0 + loops * 0.12)

            # Trigger re-amplification if current scenario overlaps
            sc_drive_val = scenario_drives.get(drive, 0.0)
            if sc_drive_val > 0.30:
                r_circ += TRIGGER_AMP * min(sc_drive_val, 0.80)
                self._state.circular_loops[drive] = loops + 1

            # Anti-recovery floor
            floor_boost = SPITE_FLOOR_BOOST if drive == "spite" else 0.0
            r_floor     = peak_val * FLOOR_FRACTION + floor_boost

            r_final = float(np.clip(max(r_circ, r_floor), 0.0, 0.60))
            if r_final > 0.005:
                injection[drive] = round(r_final, 4)

        # Decay active drives forward in time
        for drive in list(self._state.active_drives.keys()):
            dt      = self._delta_t_for_drive(drive, delta_t_override)
            lam     = RUMINATION_DECAY.get(drive, DEFAULT_DECAY)
            decayed = self._state.active_drives[drive] * math.exp(-lam * dt)
            floor   = self._state.active_drives[drive] * FLOOR_FRACTION
            self._state.active_drives[drive] = float(
                np.clip(max(decayed, floor), 0.0, 1.0)
            )

        self._state.total_burden = round(
            float(np.mean(list(injection.values()))) if injection else 0.0, 4
        )
        self._injection_log.append(dict(injection))
        if len(self._injection_log) > self._max_events:
            self._injection_log = self._injection_log[-self._max_events:]
        return injection

    def _extract_scenario_drives(self, scenario: dict) -> Dict[str, float]:
        """Map scenario parameters to primary drives for trigger detection."""
        drive_map = {
            "grief_weight":       "grief",
            "anger_trigger":      "rage",
            "betrayal_intensity": "betrayal_trace",
            "spite_toward_divine":"spite",
            "guilt_level":        "guilt",
            "shame_level":        "shame",
            "resentment_level":   "resentment",
            "despair_level":      "despair",
        }
        result: Dict[str, float] = {}
        for param, drive in drive_map.items():
            val = scenario.get(param)
            if isinstance(val, (int, float)):
                result[drive] = float(val)
        return result

    def _delta_t_for_drive(
        self,
        drive:    str,
        override: Optional[float] = None,
    ) -> float:
        """Time elapsed since the most recent event that set this drive."""
        if override is not None:
            return max(override, 0.01)
        for event in reversed(self._events):
            if drive in event.drive_peaks:
                return max(self._scenario_hour - event.scenario_hour, 0.01)
        return 1.0

    # ── Introspection ─────────────────────────────────────────────────────────

    @property
    def state(self) -> RuminationState:
        return self._state

    def burden_score(self) -> float:
        """Scalar 0→1 representing total current rumination burden."""
        if not self._state.active_drives:
            return 0.0
        weighted = [
            v * (1.0 / max(RUMINATION_DECAY.get(d, DEFAULT_DECAY), 0.01))
            for d, v in self._state.active_drives.items()
        ]
        max_weight = 1.0 / min(RUMINATION_DECAY.values())
        return float(np.clip(
            sum(weighted) / (max_weight * max(len(weighted), 1)),
            0.0, 1.0
        ))

    def injection_history(self) -> List[Dict[str, float]]:
        return list(self._injection_log)

    def format(self) -> str:
        lines = [
            f"╔══ RUMINATOR STATE  (hour={self._scenario_hour:.1f})",
            f"║  Total burden    : {self._state.total_burden:.4f}",
            f"║  Active drives   : {len(self._state.active_drives)}",
            f"║  Events recorded : {len(self._events)}",
            "║",
        ]
        for d, v in sorted(
            self._state.active_drives.items(), key=lambda kv: -kv[1]
        ):
            if v < 0.005:
                continue
            loops = self._state.circular_loops.get(d, 0)
            lam   = RUMINATION_DECAY.get(d, DEFAULT_DECAY)
            hl    = round(math.log(2) / lam, 1)
            filled = int(v * 20)
            bar   = "█" * filled + "░" * (20 - filled)
            circ  = f"  ↻×{loops}" if loops > 0 else ""
            lines.append(
                f"║  {d:<20} {v:.4f}  [{bar}]  t½={hl}h{circ}"
            )
        lines.append("╚" + "═" * 60)
        return "\n".join(lines)