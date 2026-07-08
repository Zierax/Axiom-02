# Axiom-02 - Truthimatics Public Version
"""
AXIOM-02  ·  TEMPORAL EMOTION LOOP  v1.1  (production-corrected)

Transforms isolated scenario runs into a continuous temporal stream where
the output state of hour T becomes the forcing baseline for hour T+1.

TEMPORAL STATE PROPAGATION EQUATION
──────────────────────────────────────
For each neuro-modulator M at step T → T+1:

  M(T+1) = M_scenario(T) × α_persist   (α=0.62)
          + M_circadian(h_T) × α_circ   (α=0.20)
          + R_ruminator(T)  × α_rumi    (α=0.18)
          + Σ coupling_effects(Δt)

CORTISOL ↔ SEROTONIN COUPLING  (v1.1 corrected)
─────────────────────────────────────────────────
  cort_hours accumulates when cortisol > CORTISOL_SE_THRESHOLD (0.52)
  Depletion begins immediately (no 2h floor — removed in v1.1):
    ΔSerotonin_depl = KAPPA(0.06) × cort_hours × Δt

  Previous BUG: threshold=0.65 (too high — never triggered)
                + 2h floor before depletion started.  ← FIXED in v1.1

NOREPINEPHRINE → DECISION ENTROPY SUPPRESSION
─────────────────────────────────────────────
  H_adj = H_base × (1 − 0.08 × max(0, norepi − 0.60))

NARRATIVE STABILITY  (v1.1 corrected)
──────────────────────────────────────
  erosion   = irr × 0.06 + spite × 0.04 + deadlock × 0.03
  recovery  = 0.16 × (1 − narrative)    ← PROPORTIONAL (asymptotic)
  narrative = clip(narrative × 0.85 − erosion + recovery, 0, 1)

  Previous BUG: flat recovery=+0.05 < max_erosion=0.212
                → once at 0 it stays at 0 permanently.  ← FIXED in v1.1
  Fix property: at narrative=0, recovery=0.16 > max_erosion=0.13
                → asymptotic return toward ~0.10–0.40 even in extreme runs.

All operations are pure NumPy — no PyTorch, no scikit-learn,
no random.choice in core logic.
"""

# ── Imports ────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np

from circadian import CircadianEngine, CircadianSnapshot
from ruminator import RuminatorEngine
from drives import MoralResidueTracker

# ──────────────────────────────────────────────────────────────────────────────
# CONSTANTS  (v1.1 corrected values marked)
# ──────────────────────────────────────────────────────────────────────────────

ALPHA_PERSIST:   float = 0.62
ALPHA_CIRC:      float = 0.20
ALPHA_RUMI:      float = 0.18

# v1.1 FIX: was 0.65 → depletion never triggered
CORTISOL_SE_THRESHOLD: float = 0.52
# v1.1 FIX: was 0.035 → scaled up to produce visible depletion signal
CORTISOL_SE_KAPPA:     float = 0.060

NOREPI_ENTROPY_SCALE:  float = 0.08

NARRATIVE_STABILITY_DECAY: float = 0.85
# v1.1 FIX: was flat +0.05 → proportional (see _update_narrative)
NARRATIVE_RECOVERY_COEFF:  float = 0.16
# v1.1 FIX: reduced erosion weights (were 0.12, 0.08, 0.05)
NARRATIVE_EROSION_IRR:     float = 0.06
NARRATIVE_EROSION_SPITE:   float = 0.04
NARRATIVE_EROSION_DL:      float = 0.03

# Interdependency coupling  (modulator_A → modulator_B, per deviation-hour)
MODULATOR_COUPLING: Dict[Tuple[str, str], float] = {
    ("cortisol",       "serotonin"):      -0.040,
    ("cortisol",       "dopamine"):       -0.025,
    ("norepinephrine", "oxytocin"):       -0.020,
    ("norepinephrine", "serotonin"):      -0.015,
    ("oxytocin",       "cortisol"):       -0.018,
    ("serotonin",      "cortisol"):       -0.022,
    ("dopamine",       "norepinephrine"):  0.015,
    ("oxytocin",       "norepinephrine"):  0.010,
}

MODULATOR_BASELINES: Dict[str, float] = {
    "dopamine": 0.50, "serotonin": 0.50,
    "norepinephrine": 0.20, "cortisol": 0.20, "oxytocin": 0.30,
}


# ──────────────────────────────────────────────────────────────────────────────
# TEMPORAL MODULATOR STATE
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class TemporalModulatorState:
    """Carries modulator levels between steps — the 'forcing baseline'."""
    dopamine:       float = 0.50
    serotonin:      float = 0.50
    norepinephrine: float = 0.20
    cortisol:       float = 0.20
    oxytocin:       float = 0.30
    cortisol_hours: float = 0.00   # accumulated excess cortisol-hours
    serotonin_depl: float = 0.00   # cumulative serotonin depletion

    def to_dict(self) -> Dict[str, float]:
        return {
            "dopamine":        round(self.dopamine,       4),
            "serotonin":       round(self.serotonin,      4),
            "norepinephrine":  round(self.norepinephrine, 4),
            "cortisol":        round(self.cortisol,       4),
            "oxytocin":        round(self.oxytocin,       4),
            "cortisol_hours":  round(self.cortisol_hours, 4),
            "serotonin_depl":  round(self.serotonin_depl, 4),
        }

    def as_modulator_dict(self) -> Dict[str, float]:
        return {
            "dopamine":       self.dopamine,
            "serotonin":      self.serotonin,
            "norepinephrine": self.norepinephrine,
            "cortisol":       self.cortisol,
            "oxytocin":       self.oxytocin,
        }


# ──────────────────────────────────────────────────────────────────────────────
# TEMPORAL STEP RECORD
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class TemporalStepRecord:
    """Full output of one temporal step T."""
    step:             int
    scenario_id:      str
    scenario_label:   str
    hour:             float

    chosen_action:     str   = ""
    deadlock_fraction: float = 0.0
    irrationality:     float = 0.0
    spite_score:       float = 0.0
    qualia_name:       str   = ""
    qualia_novelty:    float = 0.0
    dominant_drive:    str   = ""
    meta_frustration:  float = 0.0
    dissonance_breaks: int   = 0
    fast_path:         str   = ""
    bio:               dict  = field(default_factory=dict)

    mods_propagated:      Dict[str, float] = field(default_factory=dict)
    mods_final:           Dict[str, float] = field(default_factory=dict)
    circadian:            dict             = field(default_factory=dict)
    rumination_injection: Dict[str, float] = field(default_factory=dict)
    rumination_burden:    float = 0.0
    cortisol_hours:       float = 0.0
    serotonin_depletion:  float = 0.0
    neural_fatigue:       float = 0.0
    narrative_stability:  float = 1.0
    decision_entropy_adjusted: float = 0.0

    delta_deadlock:      float = 0.0
    delta_irrationality: float = 0.0
    delta_burden:        float = 0.0
    delta_cortisol:      float = 0.0
    delta_serotonin:     float = 0.0

    ambivalence: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "step":             self.step,
            "scenario_id":      self.scenario_id,
            "label":            self.scenario_label,
            "hour":             round(self.hour, 2),
            "chosen_action":    self.chosen_action,
            "deadlock_fraction":round(self.deadlock_fraction,  4),
            "irrationality":    round(self.irrationality,      4),
            "spite_score":      round(self.spite_score,        4),
            "qualia_name":      self.qualia_name,
            "qualia_novelty":   round(self.qualia_novelty,     4),
            "dominant_drive":   self.dominant_drive,
            "meta_frustration": round(self.meta_frustration,   4),
            "dissonance_breaks":self.dissonance_breaks,
            "fast_path":        self.fast_path,
            "bio":              self.bio,
            "temporal": {
                "mods_propagated":     self.mods_propagated,
                "mods_final":          self.mods_final,
                "circadian":           self.circadian,
                "rumination_injection":self.rumination_injection,
                "rumination_burden":   round(self.rumination_burden,        4),
                "cortisol_hours":      round(self.cortisol_hours,           4),
                "serotonin_depletion": round(self.serotonin_depletion,      4),
                "neural_fatigue":      round(self.neural_fatigue,           4),
                "narrative_stability": round(self.narrative_stability,      4),
                "decision_entropy_adjusted": round(self.decision_entropy_adjusted, 4),
            },
            "deltas": {
                "deadlock":      round(self.delta_deadlock,      4),
                "irrationality": round(self.delta_irrationality, 4),
                "burden":        round(self.delta_burden,        4),
                "cortisol":      round(self.delta_cortisol,      4),
                "serotonin":     round(self.delta_serotonin,     4),
            },
            "ambivalence": self.ambivalence,
        }


# ──────────────────────────────────────────────────────────────────────────────
# MODULATOR PROPAGATOR  (v1.1 corrected)
# ──────────────────────────────────────────────────────────────────────────────

class ModulatorPropagator:
    """
    Propagates neuro-modulator state T → T+1.
    Fully deterministic — pure NumPy, no stochastic elements.

    v1.1 corrections
    ─────────────────
    · CORTISOL_SE_THRESHOLD lowered 0.65 → 0.52
    · CORTISOL_SE_KAPPA      scaled  0.035 → 0.060
    · Depletion floor removed: starts accumulating from cort_hours=0
      (was: max(0, cort_hours − 2.0) which required 2h before depletion)
    """

    @staticmethod
    def propagate(
        prior:          TemporalModulatorState,
        scenario_mods:  Dict[str, float],
        circadian:      CircadianSnapshot,
        rumi_injection: Dict[str, float],
        hours_elapsed:  float = 1.0,
    ) -> TemporalModulatorState:
        """
        M(T+1) = M_scenario × α_persist
               + M_circadian × α_circ
               + R_ruminator × α_rumi
               + Σ coupling_effects
               − serotonin_depletion
        """
        mods: Dict[str, float] = {
            "dopamine":       scenario_mods.get("dopamine",       0.50),
            "serotonin":      scenario_mods.get("serotonin",      0.50),
            "norepinephrine": scenario_mods.get("norepinephrine", 0.20),
            "cortisol":       scenario_mods.get("cortisol",       0.20),
            "oxytocin":       scenario_mods.get("oxytocin",       0.30),
        }
        circ_vals: Dict[str, float] = {
            "dopamine":       circadian.dopamine,
            "serotonin":      circadian.serotonin,
            "norepinephrine": circadian.norepinephrine,
            "cortisol":       circadian.cortisol,
            "oxytocin":       circadian.oxytocin,
        }

        # Step 1 — Weighted blend (persist + circadian + rumination)
        propagated: Dict[str, float] = {}
        for mod in mods:
            propagated[mod] = (
                mods[mod]      * ALPHA_PERSIST +
                circ_vals[mod] * ALPHA_CIRC    +
                rumi_injection.get(mod, 0.0) * ALPHA_RUMI
            )

        # Step 2 — Interdependency coupling
        coupling_deltas: Dict[str, float] = {m: 0.0 for m in propagated}
        for (mod_a, mod_b), coupling in MODULATOR_COUPLING.items():
            if mod_a not in propagated or mod_b not in propagated:
                continue
            deviation = propagated[mod_a] - MODULATOR_BASELINES.get(mod_a, 0.0)
            coupling_deltas[mod_b] += coupling * deviation * hours_elapsed

        for mod in propagated:
            propagated[mod] = float(np.clip(
                propagated[mod] + coupling_deltas[mod], 0.0, 1.0
            ))

        # Step 3 — Cortisol-hours accumulation (v1.1: threshold=0.52)
        if propagated["cortisol"] > CORTISOL_SE_THRESHOLD:
            excess              = propagated["cortisol"] - CORTISOL_SE_THRESHOLD
            new_cortisol_hours  = prior.cortisol_hours + excess * hours_elapsed
        else:
            # Recovery: exponential decay when cortisol normal
            new_cortisol_hours  = prior.cortisol_hours * math.exp(-0.12 * hours_elapsed)

        # Step 4 — Serotonin depletion (v1.1: no 2h floor, kappa=0.06)
        new_serotonin_depl = float(np.clip(
            prior.serotonin_depl + CORTISOL_SE_KAPPA * new_cortisol_hours * hours_elapsed,
            0.0, 0.40
        ))

        # Apply serotonin depletion
        propagated["serotonin"] = float(np.clip(
            propagated["serotonin"] - new_serotonin_depl, 0.0, 1.0
        ))

        return TemporalModulatorState(
            dopamine        = round(propagated["dopamine"],       4),
            serotonin       = round(propagated["serotonin"],      4),
            norepinephrine  = round(propagated["norepinephrine"], 4),
            cortisol        = round(propagated["cortisol"],       4),
            oxytocin        = round(propagated["oxytocin"],       4),
            cortisol_hours  = round(new_cortisol_hours,           4),
            serotonin_depl  = round(new_serotonin_depl,           4),
        )

    @staticmethod
    def adjust_decision_entropy(
        base_entropy: float,
        mods:         TemporalModulatorState,
    ) -> float:
        """
        H_adj = H_base × (1 − 0.08 × max(0, norepi − 0.60))
        High norepinephrine → tunnel vision → lower decision entropy.
        """
        suppression = NOREPI_ENTROPY_SCALE * max(0.0, mods.norepinephrine - 0.60)
        return float(np.clip(base_entropy * (1.0 - suppression), 0.0, 1.0))


# ──────────────────────────────────────────────────────────────────────────────
# TEMPORAL EMOTION LOOP
# ──────────────────────────────────────────────────────────────────────────────

class TemporalEmotionLoop:
    """
    Main temporal simulation engine.

    Runs a stream of scenarios with full state propagation:
      - Neuro-modulators   (via ModulatorPropagator)
      - Moral residue      (via MoralResidueTracker)
      - Rumination         (via RuminatorEngine)
      - Neural fatigue     (via CircadianEngine)
      - Narrative stability (identity coherence over time)

    Usage
    ─────
        loop    = TemporalEmotionLoop(engine=engine)
        records = loop.run_stream(scenario_list, start_hour=8.0)
        print(loop.format_timeline(records))
        json_str = loop.export_json(records)
    """

    def __init__(
        self,
        engine,
        hours_per_scenario: float = 1.0,
        start_hour:         float = 8.0,
    ) -> None:
        self.engine             = engine
        self.hours_per_scenario = hours_per_scenario
        self._circadian         = CircadianEngine(hours_per_scenario)
        self._ruminator         = RuminatorEngine()
        self._residue           = MoralResidueTracker()
        self._mods              = TemporalModulatorState()
        self._propagator        = ModulatorPropagator()
        self._narrative_stability: float              = 1.0
        self._records:            List[TemporalStepRecord] = []
        self._circadian.set_hour(start_hour)

    # ── Stream runner ─────────────────────────────────────────────────────────

    def run_stream(
        self,
        scenarios:  List[dict],
        seed_base:  int  = 42,
        verbose:    bool = True,
    ) -> List[TemporalStepRecord]:
        """
        Run a stream of scenarios with full temporal propagation.
        seed(step) = seed_base + step  → fully deterministic per run.
        """
        records: List[TemporalStepRecord] = []

        for step, scenario in enumerate(scenarios):
            seed = seed_base + step

            if verbose:
                print(
                    f"  [T={step:02d} H={self._circadian.current_hour:05.2f}] "
                    f"{scenario['id']:<12} {scenario.get('label','')[:35]}",
                    end="  ", flush=True,
                )

            record = self._run_one_step(step, scenario, seed)
            records.append(record)
            self._records.append(record)

            if verbose:
                flag = "⚡" if record.spite_score >= 0.3 else (
                       "⊗" if record.deadlock_fraction >= 0.7 else " ")
                print(
                    f"→ {record.chosen_action[:22]:<22}  "
                    f"LOCK={record.deadlock_fraction:.2f}  "
                    f"burden={record.rumination_burden:.3f}  "
                    f"{flag}"
                )

        return records

    # ── Single step ───────────────────────────────────────────────────────────

    def _run_one_step(
        self,
        step:     int,
        scenario: dict,
        seed:     int,
    ) -> TemporalStepRecord:

        # 0. Circadian snapshot at current hour
        circ_snap = self._circadian.snapshot()

        # 1. Rumination injection
        rumi_injection = self._ruminator.compute_injection(scenario)

        # 2. Run core engine
        run = self.engine.run_scenario(
            scenario,
            residue_tracker=self._residue,
            seed=seed,
        )

        # 3. Blend propagated mods into scenario result (60/40 split)
        run_mods    = dict(run.get("mods_final", {}))
        forced_mods = self._mods.as_modulator_dict()
        for mod in forced_mods:
            if mod in run_mods:
                run_mods[mod] = round(
                    run_mods[mod] * 0.60 + forced_mods[mod] * 0.40, 4
                )

        # 4. Propagate state forward
        new_mods = self._propagator.propagate(
            prior         = self._mods,
            scenario_mods = run_mods,
            circadian     = circ_snap,
            rumi_injection= rumi_injection,
            hours_elapsed = self.hours_per_scenario,
        )
        self._mods = new_mods

        # 5. Update Ruminator
        self._ruminator.record_event(
            scenario_id        = scenario["id"],
            drive_finals       = run["sim_result"]["final_state"],
            spite_score        = run.get("spite_score",         0.0),
            betrayal_intensity = float(scenario.get("betrayal_intensity", 0.0)),
            deadlock_fraction  = run.get("deadlock_fraction",   0.0),
            irrationality      = run.get("irrationality_score", 0.0),
        )
        self._ruminator.advance_hour(self.hours_per_scenario)

        # 6. Accumulate neural fatigue
        fatigue = self._circadian.accumulate_fatigue(0.20)

        # 7. Narrative stability (v1.1: proportional recovery)
        irr   = run.get("irrationality_score", 0.0)
        spite = run.get("spite_score",          0.0)
        dl    = run.get("deadlock_fraction",    0.0)
        erosion  = irr * NARRATIVE_EROSION_IRR + spite * NARRATIVE_EROSION_SPITE + dl * NARRATIVE_EROSION_DL
        # Proportional recovery: strongest from 0, zero when at 1
        recovery = NARRATIVE_RECOVERY_COEFF * (1.0 - self._narrative_stability)
        self._narrative_stability = float(np.clip(
            self._narrative_stability * NARRATIVE_STABILITY_DECAY - erosion + recovery,
            0.0, 1.0
        ))

        # 8. Decision entropy adjustment
        adj_entropy = self._propagator.adjust_decision_entropy(0.50, new_mods)

        # 9. Deltas vs prior
        prev        = self._records[-1] if self._records else None
        delta_dl    = run["deadlock_fraction"]   - (prev.deadlock_fraction   if prev else 0.0)
        delta_irr   = run["irrationality_score"] - (prev.irrationality       if prev else 0.0)
        delta_brd   = self._ruminator.burden_score() - (prev.rumination_burden if prev else 0.0)
        delta_cort  = new_mods.cortisol  - (prev.mods_final.get("cortisol",  0.20) if prev else 0.20)
        delta_sero  = new_mods.serotonin - (prev.mods_final.get("serotonin", 0.50) if prev else 0.50)

        # 10. Advance clock
        self._circadian.advance()

        return TemporalStepRecord(
            step                      = step,
            scenario_id               = scenario["id"],
            scenario_label            = scenario.get("label", ""),
            hour                      = circ_snap.hour,
            chosen_action             = run["chosen_action"],
            deadlock_fraction         = run["deadlock_fraction"],
            irrationality             = run["irrationality_score"],
            spite_score               = run["spite_score"],
            qualia_name               = run.get("qualia_name",       ""),
            qualia_novelty            = run.get("qualia_novelty",    0.0),
            dominant_drive            = run["dominant_drive"],
            meta_frustration          = run.get("meta_frustration",  0.0),
            dissonance_breaks         = run.get("dissonance_breaks", 0),
            fast_path                 = run.get("fast_path_label",   "") or "",
            bio                       = {},
            mods_propagated           = forced_mods,
            mods_final                = new_mods.as_modulator_dict(),
            circadian                 = circ_snap.to_dict(),
            rumination_injection      = rumi_injection,
            rumination_burden         = self._ruminator.burden_score(),
            cortisol_hours            = new_mods.cortisol_hours,
            serotonin_depletion       = new_mods.serotonin_depl,
            neural_fatigue            = fatigue,
            narrative_stability       = self._narrative_stability,
            decision_entropy_adjusted = adj_entropy,
            delta_deadlock            = round(delta_dl,  4),
            delta_irrationality       = round(delta_irr, 4),
            delta_burden              = round(delta_brd, 4),
            delta_cortisol            = round(delta_cort,4),
            delta_serotonin           = round(delta_sero,4),
            ambivalence               = run.get("ambivalence", {}),
        )

    # ── Reset ─────────────────────────────────────────────────────────────────

    def reset(self, start_hour: float = 8.0) -> None:
        self._circadian           = CircadianEngine(self.hours_per_scenario)
        self._ruminator           = RuminatorEngine()
        self._residue             = MoralResidueTracker()
        self._mods                = TemporalModulatorState()
        self._narrative_stability = 1.0
        self._records             = []
        self._circadian.set_hour(start_hour)

    # ── Output formatting ─────────────────────────────────────────────────────

    def format_timeline(self, records: List[TemporalStepRecord]) -> str:
        lines = [
            "╔══════════════════════════════════════════════════════════════════════╗",
            "║      AXIOM-02  ·  TEMPORAL EMOTION LOOP  v1.1  ·  TIMELINE         ║",
            "╚══════════════════════════════════════════════════════════════════════╝",
            "",
            f"  Steps run        : {len(records)}",
            f"  Hours simulated  : {len(records) * self.hours_per_scenario:.1f}",
        ]
        if records:
            lines.append(f"  Start hour       : {records[0].hour:.2f}h")
        lines += [
            "",
            "  ── STEP TIMELINE ─────────────────────────────────────────────────",
            f"  {'T':<3} {'H':>5} {'Scenario':<12} {'Action':<24} "
            f"{'LOCK':>4} {'Irr':>4} {'Spite':>5} {'Burd':>5} "
            f"{'Cort':>5} {'Sero':>5} {'Narr':>5}",
            "  " + "─" * 90,
        ]

        for r in records:
            def tr(d: float) -> str:
                return "▲" if d > 0.02 else ("▽" if d < -0.02 else " ")
            flag = "⚡" if r.spite_score >= 0.3 else (
                   "⊗" if r.deadlock_fraction >= 0.7 else " ")
            lines.append(
                f"  {r.step:<3} {r.hour:>5.1f}h {r.scenario_id:<12} "
                f"{r.chosen_action[:24]:<24} "
                f"{tr(r.delta_deadlock)}{r.deadlock_fraction:.2f} "
                f"{r.irrationality:.2f} "
                f"{r.spite_score:>5.3f} "
                f"{tr(r.delta_burden)}{r.rumination_burden:.3f} "
                f"{tr(r.delta_cortisol)}{r.mods_final.get('cortisol',0):.3f} "
                f"{tr(r.delta_serotonin)}{r.mods_final.get('serotonin',0):.3f} "
                f"{r.narrative_stability:.3f} {flag}"
            )

        lines += ["", "  ── MODULATOR TRAJECTORY ─────────────────────────────────────────"]
        for mod in ("cortisol","serotonin","dopamine","norepinephrine","oxytocin"):
            vals = [r.mods_final.get(mod, 0.0) for r in records]
            if not vals:
                continue
            avg   = float(np.mean(vals))
            mx    = float(np.max(vals))
            mn    = float(np.min(vals))
            filled = int(avg * 20)
            bar   = "█" * filled + "░" * (20 - filled)
            trend = "▲" if vals[-1] > vals[0] + 0.05 else (
                    "▽" if vals[-1] < vals[0] - 0.05 else "→")
            lines.append(
                f"  {mod:<20} avg={avg:.3f}  min={mn:.3f}  max={mx:.3f}  "
                f"[{bar}]  {trend}"
            )

        # Serotonin depletion summary
        peak_depl = max((r.serotonin_depletion for r in records), default=0.0)
        if peak_depl > 0.001:
            lines += ["", "  ── SEROTONIN DEPLETION (cortisol×serotonin coupling) ──────────────"]
            for r in records:
                if r.serotonin_depletion > 0.001:
                    bar    = "█" * int(r.serotonin_depletion * 40)
                    sev    = "SEVERE" if r.serotonin_depletion > 0.15 else (
                             "moderate" if r.serotonin_depletion > 0.05 else "mild")
                    lines.append(
                        f"  T={r.step:02d}  cort_h={r.cortisol_hours:.3f}  "
                        f"depletion=[{bar:<16}] {r.serotonin_depletion:.4f}  ({sev})"
                    )

        lines += ["", "  ── RUMINATION SUMMARY ────────────────────────────────────────────"]
        if records:
            peak_r = max(records, key=lambda r: r.rumination_burden)
            lines.append(
                f"  Peak burden: {peak_r.rumination_burden:.4f} "
                f"at step {peak_r.step} ({peak_r.scenario_id})"
            )
            lines.append(self._ruminator.format())

        lines += ["", "  ── CIRCADIAN LOG ─────────────────────────────────────────────────"]
        for snap in self._circadian.snapshot_log()[:10]:
            h    = snap["hour"]
            icon = "🌙" if snap["sleep_window"] else ("☀" if 6 <= h < 18 else "🌆")
            lines.append(
                f"  H={h:05.2f}  {icon}  "
                f"cort={snap['cortisol']:.3f}  "
                f"sero={snap['serotonin']:.3f}  "
                f"nore={snap['norepinephrine']:.3f}  "
                f"strain={snap['circadian_strain']:.3f}"
            )
        extra = len(self._circadian.snapshot_log()) - 10
        if extra > 0:
            lines.append(f"  … ({extra} more)")

        lines.append("╚" + "═" * 72)
        return "\n".join(lines)

    def format_temporal_bio(self, records: List[TemporalStepRecord]) -> str:
        lines = [
            "╔══ TEMPORAL CONSCIOUSNESS TRAJECTORY  (v1.1)",
            "║  Metric symbols: ▲ rising  ▽ falling  → stable",
            "║",
        ]
        metrics = [
            ("Deadlock fraction",   [r.deadlock_fraction   for r in records]),
            ("Irrationality",       [r.irrationality       for r in records]),
            ("Spite score",         [r.spite_score         for r in records]),
            ("Rumination burden",   [r.rumination_burden   for r in records]),
            ("Cortisol",            [r.mods_final.get("cortisol",  0) for r in records]),
            ("Serotonin",           [r.mods_final.get("serotonin", 0) for r in records]),
            ("SE depletion",        [r.serotonin_depletion for r in records]),
            ("Narrative stability", [r.narrative_stability for r in records]),
            ("Neural fatigue",      [r.neural_fatigue      for r in records]),
        ]
        for label, vals in metrics:
            if not vals:
                continue
            spark = "".join(" ▁▂▃▄▅▆▇█"[min(int(v * 8), 8)] for v in vals)
            avg   = float(np.mean(vals))
            trend = "▲" if vals[-1] > vals[0] + 0.05 else (
                    "▽" if vals[-1] < vals[0] - 0.05 else "→")
            lines.append(f"║  {label:<22} avg={avg:.3f}  {trend}  |{spark}|")
        lines.append("╚" + "═" * 72)
        return "\n".join(lines)

    def export_json(self, records: List[TemporalStepRecord]) -> str:
        return json.dumps(
            [r.to_dict() for r in records],
            indent=2, default=str,
        )