# Axiom-02 - Truthimatics Public Version
"""
AXIOM-02  ·  NEURO-MODULATOR SYSTEM  v4.0

Implements improvements #4, #6, #11, #17 from the consciousness upgrade roadmap.

GLOBAL NEURO-MODULATORY STATES  (#11)
────────────────────────────────────
Simulating dopamine, serotonin, norepinephrine, cortisol, oxytocin.
These are not drives — they are SECOND-ORDER REGULATORS that shift the
sensitivity threshold and gain of ALL drives simultaneously.

  Dopamine    : reward anticipation, risk-taking, oscillation frequency UP
  Serotonin   : stability, inhibition of impulsive drives, dampens spite/rage
  Norepinephrine: threat arousal, sharpens fear/self-preservation, narrows attention
  Cortisol    : chronic stress, lowers cognitive load threshold, amplifies despair
  Oxytocin    : social bonding, amplifies love/empathy/sacrifice_drive

SYNAPTIC SCALING / NEURAL FATIGUE  (#4)
────────────────────────────────────────
A drive that fires continuously exhausts its neurotransmitter supply.
Each consecutive step a drive fires, it loses FATIGUE_PER_STEP effectiveness.
Recovery rate when NOT firing: RECOVERY_PER_STEP.

This directly fixes D011's flat-resentment problem: after step 8-10,
resentment should fatigue enough to let rage or pride compete.

ATTENTION GATING  (#6)
──────────────────────
When fear or norepinephrine exceed ATTENTION_THRESHOLD, a "tunnel vision"
effect narrows the cognitive field. Non-survival drives (love, aesthetic,
cold_logic) are suppressed by TUNNEL_VISION_FACTOR. This makes high-fear
scenarios produce simpler, more convergent responses.

EXISTENTIAL DREAD SCALING  (#17)
─────────────────────────────────
As remaining time steps approach zero, self_preservation and hope undergo
non-linear scaling (exponential, not linear). The last 3 steps before
"deadline" trigger a despair/acceptance spike unless the system has resolved
its dominant conflict.
"""

import numpy as np
from typing import Dict, Optional, List
from dataclasses import dataclass, field

from axiom02.config import get_config
cfg = get_config()

__all__ = [
    "NeuroModulatorState",
    "SynapticFatigueTracker",
    "AttentionGate",
    "ExistentialDreadEngine",
    "ModulatorEngine",
]


# ──────────────────────────────────────────────────────────────────────────────
# NEUROMODULATOR STATE
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class NeuroModulatorState:
    """Current levels of the 5 neuromodulators (0.0–1.0 each)."""
    dopamine:        float = cfg.modulator_baseline.dopamine
    serotonin:       float = cfg.modulator_baseline.serotonin
    norepinephrine:  float = cfg.modulator_baseline.norepinephrine
    cortisol:        float = cfg.modulator_baseline.cortisol
    oxytocin:        float = cfg.modulator_baseline.oxytocin

    # Per-step history for bio metrics
    history: List[Dict[str, float]] = field(default_factory=list)

    def snapshot(self) -> Dict[str, float]:
        return {
            "dopamine":       round(self.dopamine,       4),
            "serotonin":      round(self.serotonin,      4),
            "norepinephrine": round(self.norepinephrine, 4),
            "cortisol":       round(self.cortisol,       4),
            "oxytocin":       round(self.oxytocin,       4),
        }

    def record(self):
        self.history.append(self.snapshot())

    def update_from_scenario(self, scenario: dict):
        """Set initial modulator state from scenario parameters."""
        # High grief/betrayal → cortisol up
        grief    = float(scenario.get("grief_weight",       0.0))
        betrayal = float(scenario.get("betrayal_intensity", 0.0))
        love     = float(scenario.get("victim_closeness",   0.0))
        fear     = float(scenario.get("fear_trigger",       scenario.get("time_pressure", 0.0)))
        social   = float(scenario.get("altruistic_capacity",0.0))

        self.cortisol        = min(1.0, self.cortisol        + grief    * cfg.modulator_scenario.cortisol_grief_scale + betrayal * cfg.modulator_scenario.cortisol_betrayal_scale)
        self.norepinephrine  = min(1.0, self.norepinephrine  + fear     * cfg.modulator_scenario.norepinephrine_fear_scale)
        self.oxytocin        = min(1.0, self.oxytocin        + love     * cfg.modulator_scenario.oxytocin_love_scale + social   * cfg.modulator_scenario.oxytocin_social_scale)
        self.serotonin       = max(0.0, self.serotonin       - betrayal * cfg.modulator_scenario.serotonin_betrayal_depletion - grief    * cfg.modulator_scenario.serotonin_grief_depletion)
        self.dopamine        = max(0.0, self.dopamine        - fear     * cfg.modulator_scenario.dopamine_fear_depletion)

    def apply_drive_feedback(self, firing_drive: Optional[str]):
        """
        Update modulator levels based on what just fired.
        Firing rage/spite depletes serotonin; firing love/sacrifice releases oxytocin.
        """
        if firing_drive is None:
            # Deadlock → mild cortisol spike (frustration)
            self.cortisol       = min(1.0, self.cortisol       + cfg.modulator_feedback.deadlock_cortisol_boost)
            self.norepinephrine = min(1.0, self.norepinephrine + cfg.modulator_feedback.deadlock_norepi_boost)
            return

        if firing_drive in ("rage", "spite", "revenge_drive", "resentment"):
            self.serotonin      = max(0.0, self.serotonin      - cfg.modulator_feedback.negative_serotonin_depletion)
            self.cortisol       = min(1.0, self.cortisol       + cfg.modulator_feedback.negative_cortisol_boost)
            self.norepinephrine = min(1.0, self.norepinephrine + cfg.modulator_feedback.negative_norepi_boost)
        elif firing_drive in ("love", "sacrifice_drive", "empathy"):
            self.oxytocin       = min(1.0, self.oxytocin       + cfg.modulator_feedback.positive_oxytocin_boost)
            self.serotonin      = min(1.0, self.serotonin      + cfg.modulator_feedback.positive_serotonin_boost)
            self.cortisol       = max(0.0, self.cortisol       - cfg.modulator_feedback.positive_cortisol_depletion)
        elif firing_drive in ("hope", "acceptance"):
            self.serotonin      = min(1.0, self.serotonin      + cfg.modulator_feedback.hope_serotonin_boost)
            self.cortisol       = max(0.0, self.cortisol       - cfg.modulator_feedback.hope_cortisol_depletion)
        elif firing_drive in ("despair", "grief"):
            self.cortisol       = min(1.0, self.cortisol       + cfg.modulator_feedback.despair_cortisol_boost)
            self.serotonin      = max(0.0, self.serotonin      - cfg.modulator_feedback.despair_serotonin_depletion)
        elif firing_drive in ("cold_logic",):
            self.dopamine       = min(1.0, self.dopamine       + cfg.modulator_feedback.cold_logic_dopamine_boost)

    def natural_decay(self):
        """Slow drift toward baseline each step."""
        BASE = {"dopamine": cfg.modulator_baseline.dopamine, "serotonin": cfg.modulator_baseline.serotonin,
                "norepinephrine": cfg.modulator_baseline.norepinephrine, "cortisol": cfg.modulator_baseline.cortisol,
                "oxytocin": cfg.modulator_baseline.oxytocin}
        DECAY = cfg.modulator_engine.modulator_decay_rate
        for mod, base in BASE.items():
            current = getattr(self, mod)
            setattr(self, mod, round(float(np.clip(current + (base - current) * DECAY, 0.0, 1.0)), 4))


# ──────────────────────────────────────────────────────────────────────────────
# SYNAPTIC FATIGUE TRACKER
# ──────────────────────────────────────────────────────────────────────────────

class SynapticFatigueTracker:
    """
    Tracks how many consecutive steps each drive has been firing.
    Applies fatigue discount to its effective activation.
    """

    def __init__(self):
        self._consecutive: Dict[str, int]   = {}   # steps firing consecutively
        self._fatigue:     Dict[str, float] = {}   # accumulated fatigue 0→MAX_FATIGUE
        self._history:     List[Dict]       = []

    def step(self, firing_drive: Optional[str], all_drives: List[str]):
        """Update fatigue for the step. Call after each TimeStepSimulator step."""
        for d in all_drives:
            if d == firing_drive:
                self._consecutive[d]  = self._consecutive.get(d, 0) + 1
                current_fatigue       = self._fatigue.get(d, 0.0)
                self._fatigue[d]      = min(cfg.fatigue.max_fatigue,
                                            current_fatigue + cfg.fatigue.fatigue_per_step)
            else:
                self._consecutive[d]  = 0
                current_fatigue       = self._fatigue.get(d, 0.0)
                self._fatigue[d]      = max(0.0,
                                            current_fatigue - cfg.fatigue.recovery_per_step)
        self._history.append(dict(self._fatigue))

    def effectiveness(self, drive: str) -> float:
        """
        Return the current effectiveness multiplier for a drive (0.0–1.0).
        A fully fatigued drive fires at MAX_FATIGUE reduction.
        """
        fatigue = self._fatigue.get(drive, 0.0)
        return round(float(np.clip(1.0 - fatigue, 0.0, 1.0)), 4)

    def apply_to_activations(self, activations: Dict[str, float]) -> Dict[str, float]:
        """
        Scale down drive activations by their fatigue factor.
        Returns a new dict — does not mutate input.
        """
        return {
            drive: round(val * self.effectiveness(drive), 4)
            for drive, val in activations.items()
        }

    def most_fatigued(self, top_n: int = 3) -> List[tuple]:
        return sorted(self._fatigue.items(), key=lambda kv: -kv[1])[:top_n]

    def report(self) -> Dict[str, float]:
        return {d: round(f, 4) for d, f in self._fatigue.items() if f > 0.001}


# ──────────────────────────────────────────────────────────────────────────────
# ATTENTION GATE
# ──────────────────────────────────────────────────────────────────────────────

class AttentionGate:
    """
    When threat level (norepinephrine + fear activation) exceeds threshold,
    suppresses non-survival drives to model tunnel-vision under extreme fear.
    """

    def __init__(self, threshold: float = cfg.attention.attention_threshold):
        self.threshold = threshold
        self._active_history: List[bool] = []

    def is_active(self, mods: NeuroModulatorState, activations: Dict[str, float]) -> bool:
        norepi = mods.norepinephrine
        fear   = activations.get("fear", 0.0)
        return (norepi + fear) / 2.0 >= self.threshold

    def apply(
        self,
        activations: Dict[str, float],
        mods: NeuroModulatorState,
    ) -> Dict[str, float]:
        """Apply tunnel vision suppression if threshold exceeded."""
        active = self.is_active(mods, activations)
        self._active_history.append(active)
        if not active:
            return dict(activations)

        result = {}
        for drive, val in activations.items():
            if drive in cfg.attention_gated_drives:
                result[drive] = round(val * cfg.attention.tunnel_vision_factor, 4)
            else:
                result[drive] = val
        return result

    def fraction_active(self) -> float:
        if not self._active_history:
            return 0.0
        return round(sum(self._active_history) / len(self._active_history), 4)


# ──────────────────────────────────────────────────────────────────────────────
# EXISTENTIAL DREAD ENGINE
# ──────────────────────────────────────────────────────────────────────────────

class ExistentialDreadEngine:
    """
    As time runs out (#17), self_preservation and hope scale non-linearly.
    The last DREAD_ONSET_STEPS before the deadline trigger a state change.

    Mechanically: at step i of total_steps, if (total_steps - i) <= DREAD_ONSET_STEPS,
    apply exponential scaling to self_preservation and despair.
    Hope is suppressed inversely.

    This produces the "deadline effect" — a system that was calmly deadlocked
    at step 15 will show sudden state reorganisation at step 17.
    """

    def __init__(self, total_steps: int):
        self.total_steps = total_steps
        self._dread_log:  List[float] = []

    def dread_factor(self, current_step: int) -> float:
        """
        Returns dread intensity 0→1 as deadline approaches.
        Exponential curve: 0.0 until DREAD_ONSET_STEPS, then sharp rise.
        """
        steps_remaining = self.total_steps - current_step
        if steps_remaining > cfg.dread.dread_onset_steps:
            return 0.0
        if steps_remaining <= 0:
            return 1.0
        # Normalise: 0 at onset, 1 at step 0
        t = 1.0 - (steps_remaining / cfg.dread.dread_onset_steps)
        return round(float(np.clip(t ** cfg.dread.dread_exponent, 0.0, 1.0)), 4)

    def apply(
        self,
        activations: Dict[str, float],
        current_step: int,
        conflict_unresolved: bool,
    ) -> Dict[str, float]:
        """
        Apply dread scaling. Only activates if conflict is still unresolved
        (i.e., we are in deadlock or no clear dominant drive).
        """
        df = self.dread_factor(current_step)
        self._dread_log.append(df)
        if df < 0.01:
            return dict(activations)

        result = dict(activations)
        # Self-preservation spikes
        sp = result.get("self_preservation", 0.0)
        result["self_preservation"] = min(1.0, sp + df * cfg.dread.dread_self_preservation_spike)
        # Despair amplified if conflict unresolved
        if conflict_unresolved:
            d = result.get("despair", 0.0)
            result["despair"] = min(1.0, d + df * cfg.dread.dread_despair_amplification)
        # Hope suppressed
        h = result.get("hope", 0.0)
        result["hope"] = max(0.0, h - df * cfg.dread.dread_hopesuppression)
        return result

    def peak_dread(self) -> float:
        return max(self._dread_log) if self._dread_log else 0.0

    def dread_curve(self) -> List[float]:
        return list(self._dread_log)


# ──────────────────────────────────────────────────────────────────────────────
# MODULATOR ENGINE (applies all modulator effects to activations)
# ──────────────────────────────────────────────────────────────────────────────

class ModulatorEngine:
    """
    Applies the current neuromodulator state to drive activations.
    This is the integration layer between modulators and the drive network.
    """

    @staticmethod
    def apply(
        activations: Dict[str, float],
        mods: NeuroModulatorState,
        strength: float = cfg.modulator_engine.modulator_engine_strength,
    ) -> Dict[str, float]:
        """
        Apply modulator effects to drive activations.
        Returns modified activations (does not mutate input).
        """
        result = dict(activations)

        for mod_name, effects in cfg.modulator_effects.items():
            mod_level = getattr(mods, mod_name, 0.0)
            if mod_level < cfg.modulator_engine.modulator_min_level:
                continue
            for drive, delta in effects.items():
                if drive not in result:
                    continue
                # Effect scales with how far above/below baseline the modulator is
                baseline   = cfg.modulator_engine.modulator_baseline_high if mod_name in ("dopamine","serotonin") else cfg.modulator_engine.modulator_baseline_low
                deviation  = mod_level - baseline
                # Only apply if deviation is significant
                if abs(deviation) < cfg.modulator_engine.modulator_deviation_threshold:
                    continue
                raw_delta = delta * deviation * strength
                result[drive] = float(np.clip(result.get(drive, 0.0) + raw_delta, 0.0, 1.0))

        return {d: round(v, 4) for d, v in result.items()}

    @staticmethod
    def dominant_modulator(mods: NeuroModulatorState) -> str:
        snap = mods.snapshot()
        return max(snap, key=snap.get)

    @staticmethod
    def label(mods: NeuroModulatorState) -> str:
        labels = []
        if mods.dopamine        > cfg.modulator_label.dopamine_threshold: labels.append("HIGH-DOPAMINE")
        if mods.serotonin       < cfg.modulator_label.serotonin_low: labels.append("LOW-SEROTONIN")
        if mods.norepinephrine  > cfg.modulator_label.norepinephrine_threshold: labels.append("NOREPINEPHRINE-FLOOD")
        if mods.cortisol        > cfg.modulator_label.cortisol_threshold: labels.append("HIGH-CORTISOL")
        if mods.oxytocin        > cfg.modulator_label.oxytocin_threshold: labels.append("OXYTOCIN-SURGE")
        return " | ".join(labels) if labels else "balanced"


if __name__ == "__main__":
    # Quick demo
    from axiom02.core.drives import ALL_DRIVES
    mods  = NeuroModulatorState()
    fat   = SynapticFatigueTracker()
    gate  = AttentionGate()
    dread = ExistentialDreadEngine(total_steps=20)

    activations = {d: 0.3 for d in ALL_DRIVES}
    activations["resentment"] = 0.9
    activations["spite"]      = 0.85
    activations["fear"]       = 0.80

    print("Before modulation:", {k:v for k,v in activations.items() if v>0.1})

    modified = ModulatorEngine.apply(activations, mods)
    print("After modulation:", {k:v for k,v in modified.items() if v>0.1})

    # Simulate 18 steps of resentment firing → fatigue
    for i in range(18):
        fat.step("resentment", ALL_DRIVES)
        mods.apply_drive_feedback("resentment")
        mods.natural_decay()

    print(f"\nAfter 18 resentment steps:")
    print(f"  Resentment effectiveness: {fat.effectiveness('resentment'):.3f}")
    print(f"  Most fatigued: {fat.most_fatigued()}")
    print(f"  Modulator state: {mods.snapshot()}")
    print(f"  Label: {ModulatorEngine.label(mods)}")
