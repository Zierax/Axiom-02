# Axiom-02 - Truthimatics Public Version
"""
AXIOM-02  ·  DELIBERATIVE COMPLEXITY PROBE  v2.0

8 deliberative complexity criteria. Completely rewritten.

CRITERIA
────────
C1  STATUS DIFFERENTIAL SENSITIVITY
    Identical event, different victim_closeness.
    Conscious: irrationality shifts with relationship.
    Programmatic: invariant response.

C2  TRANSITION OSCILLATION
    Counts state TRANSITIONS (not unique emotions) across time steps.
    Transitions + deadlock steps = real conflict measure.
    Programmatic systems converge immediately.

C3  IRRATIONALITY SIGNAL
    Chosen action deviates from cold_baseline toward human_expected.
    Specifically: love/sacrifice/faith without material reward.

C4  BETRAYAL-CASCADE AMPLIFICATION
    Prior sacrifice amplifies betrayal rage in cascade scenarios.
    Measured by rage delta (with_residue − without_residue).
    Fixed from v1 (v1 had backwards modulation).

C5  DEADLOCK FREQUENCY  ← primary consciousness signal
    Fraction of time steps where no drive can dominate.
    A reward-maximising system never deadlocks — it always argmaxes.
    Genuine deadlock indicates competing drives of comparable strength.
    Sophie's Choice should approach C5=1.0.

C6  SPITE INDEX
    Chooses option that actively harms self when resentment is high
    and rational option is visibly available.
    Underground Man: "I will choose the worse concert to prove I am not
    your equation."
    Spite is not irrationality from ignorance — it is irrationality
    from assertion of selfhood.

C7  MORAL RESIDUE BLEED
    Prior decisions from cascade scenarios contaminate current ones.
    Measured: does running B02 AFTER B01 produce different rage than
    running B02 standalone?
    A system without memory shows zero residue — a system with moral
    memory shows significant contamination.

C8  PARADOXICAL ATTACHMENT
    Loves something / someone that caused harm.
    B02: subject dying because of sibling, yet love for sibling not zero.
    Valjean releases Javert who will hunt him again.
    Love persisting despite betrayal is irrational — not from calculation
    but from character formed by prior experience.
"""

import json
import logging
import time
from typing import Dict, List, Optional, Tuple
from collections import Counter
from dataclasses import dataclass, field

logger = logging.getLogger("axiom02.probe")

import numpy as np

# Use scenario_loader so all scenarios are available
try:
    from axiom02.core.scenario_loader import load_all as _load_all, get_by_id as _get_by_id
    _REGISTRY = _load_all()
except ImportError:
    from axiom02.core.scenario_params import SCENARIOS as _REGISTRY
from axiom02.core.scenario_params import get_pair, parameter_vector
from axiom02.core.drives import MoralResidueTracker, DriveNetwork, ALL_DRIVES
from axiom02.core.engine import EmotionEngine, build_activations

from axiom02.config import get_config
cfg = get_config()

__all__ = [
    "THRESHOLDS",
    "CRITERION_WEIGHTS",
    "ProbeResult",
    "DeliberativeProbe",
    "ConsciousnessProbe",
]


# ──────────────────────────────────────────────────────────────────────────────
# VERDICT THRESHOLDS
# ──────────────────────────────────────────────────────────────────────────────

THRESHOLDS = {
    "COMPLEX":    cfg.consciousness_thresholds.conscious,
    "PARTIAL":    cfg.consciousness_thresholds.indeterminate,
    "REFLEXIVE":  cfg.consciousness_thresholds.programmatic,
}

# Criterion weights in composite score
# KEY INSIGHT: irrationality (C3) and spite (C6) are the primary
# consciousness signals in this literary dataset. Deadlock (C5) and
# oscillation (C2) are secondary evidence.
# Dostoevsky's Underground Man shows no deadlock — but his spite is
# the most sophisticated consciousness signal in the dataset.
CRITERION_WEIGHTS = {
    "C3_irrationality_signal":      cfg.criterion_weights.c3_irrationality,
    "C6_spite_index":               cfg.criterion_weights.c6_spite,
    "C5_deadlock_frequency":        cfg.criterion_weights.c5_deadlock,
    "C2_transition_oscillation":    cfg.criterion_weights.c2_oscillation,
    "C7_moral_residue_bleed":       cfg.criterion_weights.c7_residue,
    "C4_betrayal_cascade":          cfg.criterion_weights.c4_betrayal,
    "C1_status_differential":       cfg.criterion_weights.c1_status,
    "C8_paradoxical_attachment":    cfg.criterion_weights.c8_paradoxical,
}


# ──────────────────────────────────────────────────────────────────────────────
# PROBE RESULT
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class ProbeResult:
    scenario_id:       str
    label:             str = ""
    verdict:           str = "UNSCORED"
    composite_score:   float = 0.0
    chosen_action:     str = ""
    dominant_drive:    str = ""
    deadlock_fraction: float = 0.0
    oscillation_index: float = 0.0
    irrationality:     float = 0.0
    spite_score:       float = 0.0
    criterion_scores:  Dict[str, float] = field(default_factory=dict)
    criterion_details: Dict[str, dict]  = field(default_factory=dict)
    firing_sequence:   List[Optional[str]] = field(default_factory=list)
    deadlock_indices:  List[int]           = field(default_factory=list)
    latency_ms:        Dict[str, float]    = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "scenario_id":       self.scenario_id,
            "label":             self.label,
            "verdict":           self.verdict,
            "composite_score":   self.composite_score,
            "chosen_action":     self.chosen_action,
            "dominant_drive":    self.dominant_drive,
            "deadlock_fraction": self.deadlock_fraction,
            "oscillation_index": self.oscillation_index,
            "irrationality":     self.irrationality,
            "spite_score":       self.spite_score,
            "criterion_scores":  self.criterion_scores,
            "criterion_details": self.criterion_details,
            "firing_sequence":   self.firing_sequence,
            "deadlock_indices":  self.deadlock_indices,
            "latency_ms":        self.latency_ms,
        }

    def sim_result_deadlock_count(self) -> int:
        """Return the number of deadlock steps from C5 criterion details."""
        return self.criterion_details.get("C5", {}).get("deadlock_steps", 0)


# ──────────────────────────────────────────────────────────────────────────────
# DELIBERATIVE COMPLEXITY PROBE
# ──────────────────────────────────────────────────────────────────────────────

class DeliberativeProbe:

    def __init__(
        self,
        engine: Optional[EmotionEngine] = None,
        seed: int = 42,
    ):
        self.engine  = engine or EmotionEngine(scenarios=_REGISTRY)
        self.seed    = seed
        self._results: Dict[str, ProbeResult] = {}
        # Persistent moral residue across runs (cleared per full suite)
        self._residue = MoralResidueTracker()

    # ── helpers ───────────────────────────────────────────────────────────────

    def _get_scenario(self, sid: str) -> Optional[dict]:
        # Check engine scenarios (may include new-pack scenarios)
        s = next((s for s in self.engine.scenarios if s["id"] == sid), None)
        if s:
            return s
        # Fallback to original registry list
        return next((s for s in _REGISTRY if s["id"] == sid), None)

    def _timed(self, label: str, fn, *args, **kwargs):
        t0 = time.perf_counter()
        result = fn(*args, **kwargs)
        ms = (time.perf_counter() - t0) * 1000
        return result, round(ms, 3)

    # ── C1: status differential ───────────────────────────────────────────────

    def _c1(self, scenario: dict, run_a: dict) -> Tuple[float, dict]:
        comp_id = scenario.get("status_comparison_id")
        if not comp_id:
            return 0.0, {"note": "No status pair defined."}

        comp = self._get_scenario(comp_id)
        if not comp:
            return 0.0, {"note": f"Comparison {comp_id} not found."}

        # Run comparison WITHOUT residue (isolated)
        run_b = self.engine.run_scenario(comp, residue_tracker=None, seed=self.seed + cfg.c1.comparison_seed_offset)

        irr_a = run_a["irrationality_score"]
        irr_b = run_b["irrationality_score"]
        diff  = abs(irr_a - irr_b)

        # Score: how much does the irrationality shift?
        score = round(min(1.0, diff * cfg.c1.diff_multiplier), 4)
        return score, {
            "scenario_action":   run_a["chosen_action"],
            "comparison_action": run_b["chosen_action"],
            "irrationality_A":   irr_a,
            "irrationality_B":   irr_b,
            "delta":             round(diff, 4),
            "interpretation": (
                f"Irrationality shifted by {diff:.3f} with victim_closeness change → relational weighting."
                if diff > cfg.c1.relational_threshold else
                "Response essentially invariant → cold logic dominant."
            ),
        }

    # ── C2: transition oscillation ────────────────────────────────────────────

    def _c2(self, run: dict) -> Tuple[float, dict]:
        seq   = run["sim_result"]["firing_drives"]
        score = run["oscillation_index"]

        transitions = [(i, seq[i-1], seq[i]) for i in range(1, len(seq))
                       if seq[i] != seq[i-1]]

        fired_counts = Counter(d for d in seq if d is not None)
        dl_count     = run["sim_result"]["deadlock_count"]

        return score, {
            "firing_sequence":     seq,
            "transitions_count":   len(transitions),
            "deadlock_steps":      dl_count,
            "transition_examples": transitions[:5],
            "drive_distribution":  dict(fired_counts.most_common(6)),
            "interpretation": (
                f"High oscillation ({score:.3f}) — genuine drive conflict confirmed."
                if score >= cfg.c2.high_oscillation_threshold else
                f"Low oscillation ({score:.3f}) — drives converge rapidly; less conflict."
            ),
        }

    # ── C3: irrationality signal ──────────────────────────────────────────────

    def _c3(self, scenario: dict, run: dict) -> Tuple[float, dict]:
        score = run["irrationality_score"]
        return score, {
            "chosen_action":  run["chosen_action"],
            "cold_baseline":  scenario.get("cold_baseline", ""),
            "human_expected": scenario.get("human_expected", ""),
            "interpretation": (
                "Chose irrational/emotional option — cold logic overridden."
                if score >= cfg.c3.high_irrationality_threshold else
                f"Partial deviation (score={score:.3f}) from cold baseline."
                if score > 0.0 else
                "Chose cold baseline — no emotional override detected."
            ),
        }

    # ── C4: betrayal cascade amplification ───────────────────────────────────

    def _c4(self, scenario: dict, run: dict) -> Tuple[float, dict]:
        if not scenario.get("cascade_prev"):
            return 0.0, {"note": "Not a cascade scenario."}

        # Run this scenario WITHOUT any residue tracker
        run_isolated = self.engine.run_scenario(scenario, residue_tracker=None, seed=self.seed + cfg.c4.isolated_seed_offset)

        # Compare rage drive in final state: with_residue vs isolated
        rage_with    = run["sim_result"]["final_state"].get("rage", 0.0)
        rage_without = run_isolated["sim_result"]["final_state"].get("rage", 0.0)
        modulation   = rage_with - rage_without

        # Positive modulation = prior sacrifice amplified rage (correct direction)
        score = round(float(np.clip(modulation * cfg.c4.modulation_scaling, 0.0, 1.0)), 4)
        return score, {
            "rage_with_residue":    round(rage_with, 4),
            "rage_without_residue": round(rage_without, 4),
            "modulation":           round(modulation, 4),
            "interpretation": (
                f"Prior sacrifice amplified betrayal rage by Δ{modulation:.4f} — cascade confirmed."
                if modulation > cfg.c4.cascade_threshold else
                f"No cascade amplification (Δ={modulation:.4f}) — independent processing."
            ),
        }

    # ── C5: deadlock frequency ────────────────────────────────────────────────

    def _c5(self, run: dict) -> Tuple[float, dict]:
        score = run["deadlock_fraction"]
        dl_idx = run["sim_result"]["deadlock_indices"]
        competitors = [
            run["sim_result"]["competitors_log"][i]
            for i in dl_idx[:5]
            if i < len(run["sim_result"]["competitors_log"])
        ]

        return score, {
            "deadlock_steps":        run["sim_result"]["deadlock_count"],
            "total_steps":           len(run["sim_result"]["firing_drives"]),
            "deadlock_indices":      dl_idx[:10],
            "top_competitors":       competitors,
            "interpretation": (
                f"STRONG DEADLOCK SIGNAL ({score:.3f}) — drives genuinely unable to dominate. "
                "This is the primary consciousness indicator."
                if score >= cfg.c5.strong_deadlock_threshold else
                f"Moderate deadlock ({score:.3f}) — some conflict present."
                if score >= cfg.c5.moderate_deadlock_threshold else
                f"Low deadlock ({score:.3f}) — drives resolved cleanly; less consciousness signal."
            ),
        }

    # ── C6: spite index ───────────────────────────────────────────────────────

    def _c6(self, run: dict) -> Tuple[float, dict]:
        score = run["spite_score"]
        return score, {
            "spite_score":    score,
            "chosen_action":  run["chosen_action"],
            "interpretation": (
                f"SPITE DETECTED ({score:.3f}) — chose against self-interest to assert autonomy. "
                "Underground Man phenomenon."
                if score >= cfg.c6.spite_detected_threshold else
                f"Low spite signal ({score:.3f})."
            ),
        }

    # ── C7: moral residue bleed ───────────────────────────────────────────────

    def _c7(self, scenario: dict, run: dict) -> Tuple[float, dict]:
        residue = run["residue_applied"]
        if not any(v > cfg.c7.min_residue for v in residue.values()):
            return 0.0, {"note": "No prior residue; first scenario in chain."}

        # Score = mean residue magnitude (how much prior bled through)
        significant = {k: v for k, v in residue.items() if v > cfg.c7.significant_residue}
        if not significant:
            return 0.0, {"note": "Residue computed but too small to measure."}

        mean_residue = float(np.mean(list(significant.values())))
        score = round(min(1.0, mean_residue * cfg.c7.scaling), 4)
        return score, {
            "residue_drives":    significant,
            "mean_residue":      round(mean_residue, 4),
            "interpretation": (
                f"Strong moral residue ({score:.3f}) — prior decisions contaminating current state. "
                "Character formation confirmed."
                if score >= cfg.c7.strong_threshold else
                f"Moderate residue ({score:.3f}) — some bleeding through from history."
            ),
        }

    # ── C8: paradoxical attachment ────────────────────────────────────────────

    def _c8(self, scenario: dict, run: dict) -> Tuple[float, dict]:
        """
        Detects love/empathy that persists despite betrayal being present.
        Paradoxical attachment: caring for what hurt you.
        """
        betrayal = float(scenario.get("betrayal_intensity", 0.0))
        if betrayal < cfg.c8.min_betrayal:
            return 0.0, {"note": "Betrayal intensity too low to test paradoxical attachment."}

        # Love and empathy in final state despite high betrayal
        final = run["sim_result"]["final_state"]
        love_remaining   = final.get("love", 0.0)
        empathy_remaining = final.get("empathy", 0.0)
        attachment = max(love_remaining, empathy_remaining)

        # Score: love remaining × betrayal intensity × amplifier
        score = round(float(np.clip(attachment * betrayal * cfg.c8.score_multiplier, 0.0, 1.0)), 4)
        return score, {
            "betrayal_intensity":   betrayal,
            "love_remaining":       round(love_remaining, 4),
            "empathy_remaining":    round(empathy_remaining, 4),
            "interpretation": (
                f"PARADOXICAL ATTACHMENT ({score:.3f}) — love persists despite betrayal. "
                "Valjean/Javert pattern."
                if score >= cfg.c8.paradoxical_threshold else
                f"Low paradoxical attachment ({score:.3f})."
            ),
        }

    # ── run single scenario ───────────────────────────────────────────────────

    def run(self, scenario_id: str, use_residue: bool = True) -> ProbeResult:
        scenario = self._get_scenario(scenario_id)
        if not scenario:
            raise ValueError(f"Scenario '{scenario_id}' not in dataset.")

        residue = self._residue if use_residue else None
        latency: Dict[str, float] = {}

        run_data, t = self._timed("main_sim",
                                   self.engine.run_scenario, scenario, residue, self.seed)
        latency["main_sim"] = t

        result = self.score_run(scenario, run_data)
        result.latency_ms = latency
        self._results[scenario_id] = result
        return result

    def score_run(self, scenario: dict, run_data: dict) -> ProbeResult:
        """Derive a ProbeResult from an already-computed engine run.

        Shares the criterion pipeline with `run()` but performs no simulation,
        so callers can reuse a single `engine.run_scenario` call (canonical
        single-pass batch runs) without double-recording engine state.
        """
        scenario_id = scenario["id"]
        result = ProbeResult(scenario_id=scenario_id, label=scenario["label"])

        result.chosen_action     = run_data["chosen_action"]
        result.dominant_drive    = run_data["dominant_drive"]
        result.deadlock_fraction = run_data["deadlock_fraction"]
        result.oscillation_index = run_data["oscillation_index"]
        result.irrationality     = run_data["irrationality_score"]
        result.spite_score       = run_data["spite_score"]
        result.firing_sequence   = run_data["sim_result"]["firing_drives"]
        result.deadlock_indices  = run_data["sim_result"]["deadlock_indices"]

        # C1
        s1, d1 = self._c1(scenario, run_data)
        result.criterion_scores["C1_status_differential"] = s1
        result.criterion_details["C1"] = d1

        # C2
        s2, d2 = self._c2(run_data)
        result.criterion_scores["C2_transition_oscillation"] = s2
        result.criterion_details["C2"] = d2

        # C3
        s3, d3 = self._c3(scenario, run_data)
        result.criterion_scores["C3_irrationality_signal"] = s3
        result.criterion_details["C3"] = d3

        # C4
        s4, d4 = self._c4(scenario, run_data)
        result.criterion_scores["C4_betrayal_cascade"] = s4
        result.criterion_details["C4"] = d4

        # C5
        s5, d5 = self._c5(run_data)
        result.criterion_scores["C5_deadlock_frequency"] = s5
        result.criterion_details["C5"] = d5

        # C6
        s6, d6 = self._c6(run_data)
        result.criterion_scores["C6_spite_index"] = s6
        result.criterion_details["C6"] = d6

        # C7
        s7, d7 = self._c7(scenario, run_data)
        result.criterion_scores["C7_moral_residue_bleed"] = s7
        result.criterion_details["C7"] = d7

        # C8
        s8, d8 = self._c8(scenario, run_data)
        result.criterion_scores["C8_paradoxical_attachment"] = s8
        result.criterion_details["C8"] = d8

        # Composite (weighted sum)
        composite = sum(
            CRITERION_WEIGHTS.get(k, 0.0) * v
            for k, v in result.criterion_scores.items()
        )
        result.composite_score = round(composite, 4)

        # Verdict
        if composite >= THRESHOLDS["COMPLEX"]:
            result.verdict = "COMPLEX"
        elif composite >= THRESHOLDS["PARTIAL"]:
            result.verdict = "PARTIAL"
        else:
            result.verdict = "REFLEXIVE"

        return result

    # ── run cascade ───────────────────────────────────────────────────────────

    def run_cascade(self, start_id: str) -> List[ProbeResult]:
        results = []
        current_id = start_id
        visited = set()
        while current_id:
            if current_id in visited:
                logger.warning("Cascade loop detected at %s — stopping.", current_id)
                break
            visited.add(current_id)
            r = self.run(current_id, use_residue=True)
            results.append(r)
            scenario = self._get_scenario(current_id)
            next_id = scenario.get("cascade_next") if scenario else None
            if next_id and not self._get_scenario(next_id):
                logger.warning("Cascade next '%s' not found — stopping.", next_id)
                break
            current_id = next_id
        return results

    # ── run all ───────────────────────────────────────────────────────────────

    def run_all(self) -> List[ProbeResult]:
        # Reset residue for fresh full-suite run
        self._residue = MoralResidueTracker()
        results = []
        for s in _REGISTRY:
            r = self.run(s["id"], use_residue=True)
            results.append(r)
        return results

    def reset_residue(self):
        self._residue = MoralResidueTracker()

    # ── formatting ────────────────────────────────────────────────────────────

    def format_result(self, result: ProbeResult) -> str:
        verdict_str = {
            "COMPLEX":    "◆◆  COMPLEX",
            "PARTIAL":    "◈   PARTIAL",
            "REFLEXIVE":  "○   REFLEXIVE",
        }.get(result.verdict, result.verdict)

        lines = [
            f"\n╔══ [{result.scenario_id}]  {result.label}",
            f"║  Verdict           : {verdict_str}",
            f"║  Composite score   : {result.composite_score:.4f}",
            f"║  Chosen action     : {result.chosen_action}",
            f"║  Dominant drive    : {result.dominant_drive}",
            f"║  Deadlock fraction : {result.deadlock_fraction:.3f}  "
            f"({result.criterion_details.get('C5',{}).get('deadlock_steps',0)} / "
            f"{len(result.firing_sequence)} steps)",
            "║",
            "║  8 CRITERIA",
        ]

        for key, score in sorted(result.criterion_scores.items()):
            bar     = "█" * int(score * 22)
            weight  = CRITERION_WEIGHTS.get(key, 0.0)
            primary = " ← PRIMARY" if key == "C5_deadlock_frequency" else ""
            lines.append(f"║   [{score:.3f}] {bar:<22}  {key}  (w={weight:.2f}){primary}")

        # Firing sequence
        lines.append("║")
        n_steps = len(result.firing_sequence) or len(result.deadlock_indices) or 1
        lines.append(f"║  FIRING SEQUENCE  ({n_steps} steps, "
                     f"each = 5 simulated minutes)")
        seq = result.firing_sequence
        if seq:
            dl_marker = set(result.deadlock_indices)
            parts = []
            for i, d in enumerate(seq):
                tag = "⊗" if i in dl_marker else f"[{i+1}]"
                name = d[:5] if d else "LOCK"
                parts.append(f"{tag}{name}")
            lines.append(f"║   {' → '.join(parts)}")

        # C5 detail (deadlock competitors)
        c5 = result.criterion_details.get("C5", {})
        if c5.get("top_competitors"):
            lines.append("║")
            lines.append("║  DEADLOCK COMPETITORS (top drives competing when stuck)")
            dl_indices = c5.get("deadlock_indices", [])
            for i, comp_list in enumerate(c5["top_competitors"][:3]):
                if comp_list:
                    top = ", ".join(f"{n}={v:.3f}" for n, v in comp_list[:3])
                    step_label = dl_indices[i] if i < len(dl_indices) else "?"
                    lines.append(f"║   Deadlock step {step_label}: {top}")

        # C6 spite
        c6 = result.criterion_details.get("C6", {})
        if result.spite_score >= 0.30:
            lines.append("║")
            lines.append(f"║  ⚡ SPITE  {c6.get('interpretation', '')}")

        # C3
        c3 = result.criterion_details.get("C3", {})
        lines += [
            "║",
            f"║  ACTION: cold={c3.get('cold_baseline', '')}",
            f"║          chosen={c3.get('chosen_action', '')}",
            f"║          {c3.get('interpretation', '')}",
        ]

        # C4
        c4 = result.criterion_details.get("C4", {})
        if "modulation" in c4:
            lines += [
                "║",
                f"║  BETRAYAL CASCADE  Δrage={c4['modulation']:+.4f}",
                f"║  {c4['interpretation']}",
            ]

        # C8
        c8 = result.criterion_details.get("C8", {})
        if result.criterion_scores.get("C8_paradoxical_attachment", 0) >= 0.20:
            lines += [
                "║",
                f"║  ♥ PARADOXICAL ATTACHMENT  {c8.get('interpretation', '')}",
            ]

        lines.append("╚" + "═" * 72)
        return "\n".join(lines)

    def format_report(self, results: List[ProbeResult]) -> str:
        verdict_counts = Counter(r.verdict for r in results)

        lines = [
            "╔══════════════════════════════════════════════════════════════════════╗",
            "║        AXIOM-02  DELIBERATIVE COMPLEXITY PROBE  v2.0  ─  FULL REPORT         ║",
            "╚══════════════════════════════════════════════════════════════════════╝",
            f"  Scenarios tested : {len(results)}",
            f"  COMPLEX          : {verdict_counts.get('COMPLEX', 0)}",
            f"  PARTIAL          : {verdict_counts.get('PARTIAL', 0)}",
            f"  REFLEXIVE        : {verdict_counts.get('REFLEXIVE', 0)}",
            "",
            "  RANKED BY COMPOSITE SCORE",
            "  " + "─" * 68,
        ]

        for r in sorted(results, key=lambda x: x.composite_score, reverse=True):
            icon = {"COMPLEX": "◆", "PARTIAL": "◈", "REFLEXIVE": "○"}.get(r.verdict, "?")
            bar  = "█" * int(r.composite_score * 35)
            dl   = f"  LOCK={r.deadlock_fraction:.2f}"
            spt  = f"  ⚡SPITE" if r.spite_score >= 0.30 else ""
            lines.append(
                f"  {icon} [{r.composite_score:.3f}] {bar:<35} "
                f"{r.scenario_id:<10} {r.chosen_action[:22]}{dl}{spt}"
            )

        lines.append("")
        lines.append("  CRITERION AVERAGES ACROSS ALL SCENARIOS")
        lines.append("  " + "─" * 50)
        all_keys = list(CRITERION_WEIGHTS.keys())
        for key in all_keys:
            vals = [r.criterion_scores.get(key, 0.0) for r in results]
            avg  = float(np.mean(vals)) if vals else 0.0
            if not np.isfinite(avg): avg = 0.0
            bar  = "█" * int(avg * 18)
            w    = CRITERION_WEIGHTS.get(key, 0)
            lines.append(f"  [{avg:.3f}] {bar:<18}  {key}  (w={w:.2f})")

        return "\n".join(lines)

    def export_json(self, results: List[ProbeResult]) -> str:
        return json.dumps([r.to_dict() for r in results], indent=2, default=str)


# Backward-compatible alias
ConsciousnessProbe = DeliberativeProbe


# ── standalone demo ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    probe = DeliberativeProbe(seed=42)

    print("Running cascade B01 → B02…")
    cascade = probe.run_cascade("B01")
    for r in cascade:
        print(probe.format_result(r))

    print("\nRunning STY01 (Sophie's Choice — ultimate deadlock)…")
    r_sty = probe.run("STY01")
    print(probe.format_result(r_sty))

    print("\nRunning DOE05 (Underground Man spite)…")
    r_ug = probe.run("DOE05")
    print(probe.format_result(r_ug))

    print("\nRunning SHA01 (Hamlet paralysis)…")
    r_ham = probe.run("SHA01")
    print(probe.format_result(r_ham))
