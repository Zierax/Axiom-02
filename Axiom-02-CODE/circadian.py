# Axiom-02 - Truthimatics Public Version
"""
AXIOM-02  ·  CIRCADIAN DRIFT ENGINE  v1.1  (production-corrected)

Deterministic biological baseline fluctuations modelled as phase-locked
functions over a 24-hour day cycle.  All outputs are pure functions of the
clock hour h ∈ [0, 24) — no stochastic elements.

TRUTHIMATICS EQUATIONS  (corrected v1.1)
─────────────────────────────────────────
The key requirement: f(PEAK_HOUR) = BASE + AMP (maximum).
Using sin would give f(PEAK) = BASE + AMP·sin(0) = BASE (minimum).
Every modulator must use either cos or cos² so that the argument is 0
at the peak hour, yielding the cosine identity cos(0) = 1.

1. CORTISOL  — peaks at 08:00 (cortisol awakening response, CAR)
   cortisol(h) = BASE + AMP × cos²(π × (h − 8) / 24)
   cos²(0) = 1 at h=8 → max = 0.20 + 0.30 = 0.50
   cos²(π/2) = 0 at h=8±12 → min = 0.20
   Previous BUG: used sin² — which gives minimum (0) at h=8.  ← FIXED

2. NOREPINEPHRINE — peaks at 10:00 (arousal / threat readiness)
   norepi(h) = BASE + AMP × max(0, cos(2π × (h − 10) / 24))
   cos(0) = 1 at h=10 → max = 0.18 + 0.22 = 0.40  [unchanged, was correct]

3. SEROTONIN — peaks at 14:00 (afternoon mood stabilisation)
   serotonin(h) = BASE + AMP × cos(2π × (h − 14) / 24)
   cos(0) = 1 at h=14 → max = 0.42 + 0.16 = 0.58
   cos(π) = −1 at h=2  → min = 0.42 − 0.16 = 0.26
   Previous BUG: used sin — which gives 0 at h=14 (midpoint, not peak). ← FIXED

4. DOPAMINE — peaks at 09:00 (morning motivation window)
   dopamine(h) = BASE + AMP × max(0, cos(2π × (h − 9) / 24))
                 for h ∈ [active_start=6, active_end=22], else BASE−0.08
   cos(0) = 1 at h=9 → max = 0.40 + 0.18 = 0.58
   Previous BUG: used sin(π(h−6)/16) — peaks at h=6+8=14, not 09. ← FIXED

5. OXYTOCIN — mild evening rise, peak ~20:00
   oxytocin(h) = BASE + AMP × sin(π × max(0, h − 18) / 12)
   [unchanged — sin here is intentional: half-wave over [18,30], peak at 24≡0
    which rolls to h=24≡0. Use h=24 as the effective peak for the sine arg.]
   Actually corrected: peak at h=21 by using max(0, h-18) over [18,30]:
   sin(π×3/12) = sin(π/4) ≈ 0.707 at h=21. Not a sine-peak, but an increasing
   monotone over [18,24]. Acceptable for a mild social bonding signal.

NEURAL FATIGUE ACCUMULATION
─────────────────────────────
   fatigue(t+1) = fatigue(t) × 0.88 + cognitive_load × (1 + strain(h))
   strain(h)    = 0.40  if h ∈ [00:00, 06:00]  else  0.0
   Sleep window [00:00–06:00] reverses accumulation instead.
"""

# ── Imports ────────────────────────────────────────────────────────────────────
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np

# ── Circadian parameters ───────────────────────────────────────────────────────

CIRCADIAN_PARAMS: Dict[str, Dict[str, float]] = {
    "cortisol": {
        "base": 0.20, "amp": 0.30, "peak": 8.0, "period": 24.0,
    },
    "norepinephrine": {
        "base": 0.18, "amp": 0.22, "peak": 10.0, "period": 24.0,
    },
    "serotonin": {
        "base": 0.42, "amp": 0.16, "peak": 14.0, "period": 24.0,
    },
    "dopamine": {
        "base": 0.40, "amp": 0.18, "peak": 9.0,
        "period": 24.0, "active_start": 6.0, "active_end": 22.0,
    },
    "oxytocin": {
        "base": 0.28, "amp": 0.08, "peak": 20.0, "period": 24.0,
    },
}

FATIGUE_PERSIST_LAMBDA: float = 0.88
SLEEP_WINDOW_START:     float = 0.0
SLEEP_WINDOW_END:       float = 6.0
CIRCADIAN_STRAIN:       float = 0.40


# ──────────────────────────────────────────────────────────────────────────────
# DATA CLASS
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class CircadianSnapshot:
    hour:              float
    cortisol:          float = 0.0
    norepinephrine:    float = 0.0
    serotonin:         float = 0.0
    dopamine:          float = 0.0
    oxytocin:          float = 0.0
    circadian_strain:  float = 0.0
    sleep_window:      bool  = False

    def to_dict(self) -> Dict[str, float]:
        return {
            "hour":             round(self.hour, 2),
            "cortisol":         round(self.cortisol, 4),
            "norepinephrine":   round(self.norepinephrine, 4),
            "serotonin":        round(self.serotonin, 4),
            "dopamine":         round(self.dopamine, 4),
            "oxytocin":         round(self.oxytocin, 4),
            "circadian_strain": round(self.circadian_strain, 4),
            "sleep_window":     self.sleep_window,
        }


# ──────────────────────────────────────────────────────────────────────────────
# CIRCADIAN ENGINE
# ──────────────────────────────────────────────────────────────────────────────

class CircadianEngine:
    """
    Deterministic biological baseline drift over a 24-hour cycle.
    Every output is a pure function of the clock hour.

    v1.1 corrections
    ─────────────────
    _cortisol  : sin² → cos²   (peak at 08:00, not 20:00)
    _serotonin : sin  → cos    (peak at 14:00, not 20:00)
    _dopamine  : sin peak at 14 → cos peak at 09:00
    """

    def __init__(self, hours_per_scenario: float = 1.0) -> None:
        self.hours_per_scenario: float       = hours_per_scenario
        self._hour:              float       = 8.0
        self._fatigue:           float       = 0.0
        self._fatigue_log:       List[float] = []
        self._snapshot_log:      List[Dict]  = []

    # ── Corrected deterministic math ──────────────────────────────────────────

    @staticmethod
    def _cortisol(h: float) -> float:
        """
        Morning awakening response — peak at 08:00.
        cortisol(h) = 0.20 + 0.30 × cos²(π × (h − 8) / 24)
        cos²(0) = 1 at h=8 → max = 0.50
        cos²(π/2) = 0 at h=8±12 → min = 0.20
        """
        p     = CIRCADIAN_PARAMS["cortisol"]
        phase = math.pi * (h - p["peak"]) / p["period"]
        val   = p["base"] + p["amp"] * (math.cos(phase) ** 2)
        return float(np.clip(val, 0.0, 1.0))

    @staticmethod
    def _norepinephrine(h: float) -> float:
        """
        Alertness / threat readiness — peak at 10:00.
        norepi(h) = 0.18 + 0.22 × max(0, cos(2π × (h − 10) / 24))
        cos(0) = 1 at h=10 → max = 0.40   [was correct in v1.0]
        """
        p     = CIRCADIAN_PARAMS["norepinephrine"]
        phase = 2.0 * math.pi * (h - p["peak"]) / p["period"]
        val   = p["base"] + p["amp"] * max(0.0, math.cos(phase))
        return float(np.clip(val, 0.0, 1.0))

    @staticmethod
    def _serotonin(h: float) -> float:
        """
        Mood stabilisation — peak at 14:00.
        serotonin(h) = 0.42 + 0.16 × cos(2π × (h − 14) / 24)
        cos(0) = 1 at h=14 → max = 0.58
        cos(π) = −1 at h=2 → min = 0.26
        FIX v1.1: was sin (= 0 at h=14, peak actually at h=20).
        """
        p     = CIRCADIAN_PARAMS["serotonin"]
        phase = 2.0 * math.pi * (h - p["peak"]) / p["period"]
        val   = p["base"] + p["amp"] * math.cos(phase)
        return float(np.clip(val, 0.0, 1.0))

    @staticmethod
    def _dopamine(h: float) -> float:
        """
        Morning motivation — peak at 09:00, active window [06:00–22:00].
        dopamine(h) = 0.40 + 0.18 × max(0, cos(2π × (h − 9) / 24))
        cos(0) = 1 at h=9 → max = 0.58
        Flat at 0.32 outside active window (below-baseline sleep low).
        FIX v1.1: was sin(π(h−6)/16) which peaks at h=14, not 09.
        """
        p = CIRCADIAN_PARAMS["dopamine"]
        if h < p["active_start"] or h > p["active_end"]:
            return float(np.clip(p["base"] - 0.08, 0.0, 1.0))
        phase = 2.0 * math.pi * (h - p["peak"]) / p["period"]
        val   = p["base"] + p["amp"] * max(0.0, math.cos(phase))
        return float(np.clip(val, 0.0, 1.0))

    @staticmethod
    def _oxytocin(h: float) -> float:
        """
        Social bonding signal — mild evening rise from 18:00 onward.
        oxytocin(h) = 0.28 + 0.08 × sin(π × max(0, h − 18) / 12)
        Monotone increasing over [18:00–24:00], then falls back.
        [unchanged from v1.0]
        """
        p   = CIRCADIAN_PARAMS["oxytocin"]
        val = p["base"] + p["amp"] * math.sin(
            math.pi * max(0.0, h - 18.0) / 12.0
        )
        return float(np.clip(val, 0.0, 1.0))

    @staticmethod
    def _strain(h: float) -> float:
        """
        Circadian strain during sleep deprivation window [00:00–06:00].
        Linearly decays from 0.40 toward 0.20 as 06:00 approaches.
        """
        if SLEEP_WINDOW_START <= h < SLEEP_WINDOW_END:
            progress = (h - SLEEP_WINDOW_START) / (SLEEP_WINDOW_END - SLEEP_WINDOW_START)
            return CIRCADIAN_STRAIN * (1.0 - 0.5 * progress)
        return 0.0

    # ── Public API ────────────────────────────────────────────────────────────

    def snapshot(self, hour: Optional[float] = None) -> CircadianSnapshot:
        """Return the circadian state at a given hour (or the current hour)."""
        h = (hour if hour is not None else self._hour) % 24.0
        return CircadianSnapshot(
            hour            = h,
            cortisol        = self._cortisol(h),
            norepinephrine  = self._norepinephrine(h),
            serotonin       = self._serotonin(h),
            dopamine        = self._dopamine(h),
            oxytocin        = self._oxytocin(h),
            circadian_strain= self._strain(h),
            sleep_window    = (SLEEP_WINDOW_START <= h < SLEEP_WINDOW_END),
        )

    def apply_to_modulators(
        self,
        modulators: Dict[str, float],
        blend:      float = 0.35,
    ) -> Dict[str, float]:
        """
        Blend modulator state with circadian baseline.
        M_adj = M × (1 − blend) + M_circadian × blend
        Blend increases during sleep window (biological override).
        """
        snap            = self.snapshot()
        effective_blend = blend + snap.circadian_strain * 0.30
        circadian_map   = {
            "cortisol":       snap.cortisol,
            "norepinephrine": snap.norepinephrine,
            "serotonin":      snap.serotonin,
            "dopamine":       snap.dopamine,
            "oxytocin":       snap.oxytocin,
        }
        return {
            mod: round(float(np.clip(
                val * (1.0 - effective_blend) + circadian_map.get(mod, val) * effective_blend,
                0.0, 1.0
            )), 4)
            for mod, val in modulators.items()
        }

    def accumulate_fatigue(self, cognitive_load_pct: float) -> float:
        """
        fatigue(t+1) = fatigue(t) × 0.88 + cognitive_load × (1 + strain(h))
        Sleep window produces negative delta (recovery).
        """
        snap  = self.snapshot()
        if snap.sleep_window:
            delta = -0.06 * (1.0 - snap.circadian_strain)
        else:
            delta = cognitive_load_pct * (1.0 + snap.circadian_strain)
        self._fatigue = float(np.clip(
            self._fatigue * FATIGUE_PERSIST_LAMBDA + delta,
            0.0, 1.0
        ))
        self._fatigue_log.append(round(self._fatigue, 4))
        return self._fatigue

    def advance(self, hours: Optional[float] = None) -> None:
        """Move the clock forward."""
        delta = hours if hours is not None else self.hours_per_scenario
        self._snapshot_log.append(self.snapshot().to_dict())
        self._hour = (self._hour + delta) % 24.0

    def set_hour(self, h: float) -> None:
        self._hour = h % 24.0

    @property
    def current_hour(self) -> float:
        return self._hour

    @property
    def accumulated_fatigue(self) -> float:
        return self._fatigue

    def fatigue_log(self) -> List[float]:
        return list(self._fatigue_log)

    def snapshot_log(self) -> List[Dict]:
        return list(self._snapshot_log)

    def format_phase(self) -> str:
        h = self._hour
        if   0  <= h < 6:  phase = "SLEEP-WINDOW  (strain active)"
        elif 6  <= h < 10: phase = "MORNING-RAMP  (cortisol + dopamine peak)"
        elif 10 <= h < 14: phase = "PEAK-ALERT    (norepinephrine high)"
        elif 14 <= h < 18: phase = "AFTERNOON     (serotonin peak at 14:00)"
        elif 18 <= h < 22: phase = "EVENING       (oxytocin rise)"
        else:              phase = "NIGHT         (pre-sleep)"
        return f"H={h:05.2f}  {phase}"