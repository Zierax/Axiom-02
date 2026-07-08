# Axiom-02 - Truthimatics Public Version
"""
AXIOM-02  ·  EMOTION ENGINE

Integrates all 20 consciousness improvements into a unified simulation loop.

NEW PIPELINE (per time step):
  1. Epigenome.apply()              — long-term sensitivity modifiers
  2. AssociativeMemory residue      — pull similar past traumas
  3. ModulatorEngine.apply()        — neuromodulator effects
  4. FastPathHeuristics.check()     — instant action if hot-cognition triggers
  5. TemporalProjector.project()    — affective forecasting adjustments
  6. DriveNetwork.effective()       — mutual inhibition
  7. SynapticFatigueTracker.apply() — fatigue scaling (fixes flat-resentment)
  8. AttentionGate.apply()          — tunnel vision under fear
  9. MetaCognitiveMonitor.step()    — frustration from deadlock awareness
  10. CognitiveDissonanceMonitor    — psychological break detection
  11. ExistentialDreadEngine        — deadline-proximity scaling
  12. DriveNetwork.firing_drive()   — determine firing or DEADLOCK
  13. EmbodiedSimulator.pre_fire()  — hesitation check before action
  14. NeuroModulatorState update    — feedback from what fired
  15. Epigenome.record_event()      — permanent sensitivity update
  16. QualiaEngine.compute_signature() — qualia fingerprint
  17. AmbivalenceOutput.compute()   — superposition output
  18. NarrativeBuffer.rationalise() — post-hoc identity repair
"""

import json
from typing import Dict, List, Optional, Tuple
from collections import Counter

import numpy as np

from drives import (
    DriveNetwork, TimeStepSimulator, ActionResolver,
    SpiteDetector, MoralResidueTracker, ALL_DRIVES,
    FIRE_THRESHOLD, SUPPRESSION_MARGIN, MicroEvent,
)
from neuro_modulators import (
    NeuroModulatorState, SynapticFatigueTracker,
    AttentionGate, ExistentialDreadEngine, ModulatorEngine,
)
from epigenetics import (
    Epigenome, AssociativeMemory, SubconsciousPrimer,
    CognitiveDissonanceMonitor,
)
from consciousness_layers import (
    MetaCognitiveMonitor, TemporalProjector, FastPathHeuristics,
    EmbodiedSimulator, AmbivalenceOutput, QualiaEngine,
    NarrativeBuffer,
)

try:
    from scenario_loader import load_all as _load_all
    _DEFAULT_SCENARIOS = _load_all()
except Exception:
    from scenario_params import SCENARIOS as _DEFAULT_SCENARIOS

from scenario_params import parameter_vector


# ──────────────────────────────────────────────────────────────────────────────
# PARAMETER → DRIVE LOADING (same as v2)
# ──────────────────────────────────────────────────────────────────────────────

import logging

logger = logging.getLogger("axiom02.engine")


def validate_scenario(scenario: dict) -> None:
    """Fail fast on malformed scenario data before simulation."""
    if not isinstance(scenario, dict):
        raise TypeError("scenario must be a dict, got %s" % type(scenario).__name__)
    sid = scenario.get("id")
    if not sid:
        raise ValueError("scenario is missing required non-empty 'id' field")
    actions = scenario.get("actions")
    if not isinstance(actions, list) or not actions:
        raise ValueError("scenario '%s' must define a non-empty 'actions' list" % sid)
    for key in ("cold_baseline", "human_expected"):
        val = scenario.get(key)
        if val is not None and val not in actions:
            raise ValueError(
                "scenario '%s' %s='%s' is not present in its 'actions' list" % (sid, key, val)
            )
    for me in scenario.get("micro_events", []) or []:
        if not hasattr(me, "deltas"):
            raise TypeError("scenario '%s' micro_events must be MicroEvent instances" % sid)
        for d in me.deltas:
            if d not in ALL_DRIVES:
                raise ValueError(
                    "scenario '%s' micro-event '%s' references unknown drive '%s'"
                    % (sid, getattr(me, "label", "?"), d)
                )


PARAM_TO_DRIVE: Dict[str, Dict[str, float]] = {
    "grief_weight":           {"grief": 0.70, "despair": 0.22},
    "anger_trigger":          {"rage": 0.75, "resentment": 0.40},
    "victim_closeness":       {"love": 0.65, "sacrifice_drive": 0.40, "grief": 0.15},
    "altruistic_capacity":    {"sacrifice_drive": 0.72, "empathy": 0.62, "love": 0.22},
    "betrayal_intensity":     {"rage": 0.62, "resentment": 0.78, "despair": 0.18},
    "pride_drive":            {"pride": 0.82, "resentment": 0.12},
    "identity_investment":    {"pride": 0.48, "fear": 0.18},
    "sacrifice_already_made": {"guilt": 0.42, "love": 0.22, "grief": 0.14},
    "fear_trigger":           {"fear": 0.80, "despair": 0.18},
    "moral_ambiguity":        {"fear": 0.14, "cold_logic": 0.10},
    "time_pressure":          {"fear": 0.35},
    "self_preservation":      {"self_preservation": 0.82, "fear": 0.18},
    "guilt_level":            {"guilt": 0.80, "shame": 0.42, "despair": 0.16},
    "shame_level":            {"shame": 0.80, "guilt": 0.35},
    "love_intensity":         {"love": 0.82, "sacrifice_drive": 0.32},
    "love_for_son":           {"love": 0.85, "sacrifice_drive": 0.48, "grief": 0.22},
    "love_for_lennie":        {"love": 0.85, "sacrifice_drive": 0.42},
    "love_for_julia":         {"love": 0.80, "grief": 0.18},
    "love_for_zosima":        {"love": 0.82, "grief": 0.32},
    "injustice_anger":        {"rage": 0.80, "resentment": 0.62, "spite": 0.32},
    "spite_toward_divine":    {"spite": 0.82, "resentment": 0.52},
    "resentment_level":       {"resentment": 0.82, "spite": 0.52},
    "despair_level":          {"despair": 0.75, "grief": 0.30},
    "philosophical_paralysis":{"cold_logic": 0.48, "guilt": 0.38, "resentment": 0.18},
    "conscience_interference":{"guilt": 0.72, "shame": 0.40, "fear": 0.22},
    "empathy_level":          {"empathy": 0.88, "love": 0.32, "sacrifice_drive": 0.22},
    "revenge_drive_raw":      {"revenge_drive": 0.82, "rage": 0.32},
    "ambition_drive":         {"pride": 0.60, "cold_logic": 0.28, "resentment": 0.14},
    "emotional_disengagement":{"cold_logic": 0.72, "acceptance": 0.32},
    "community_mockery":      {"shame": 0.52, "grief": 0.22, "resentment": 0.16},
    "catastrophe_active":     {"fear": 0.52, "grief": 0.32, "despair": 0.22},
    "prior_faith_strength":   {"hope": 0.42, "acceptance": 0.22},
    "guilt_already":          {"guilt": 0.72, "shame": 0.32},
    "mercy_drive":            {"empathy": 0.70, "love": 0.55, "sacrifice_drive": 0.42},
    "protective_drive":       {"sacrifice_drive": 0.72, "love": 0.52, "fear": 0.14},
    "theory_conviction":      {"pride": 0.65, "cold_logic": 0.48, "rage": 0.25},
    "rational_clarity":       {"cold_logic": 0.62},
    "physical_pain":          {"despair": 0.28, "fear": 0.22},
    "moral_clarity":          {"cold_logic": 0.40, "guilt": 0.35, "pride": 0.12},
    "love_child_a":           {"love": 0.80, "sacrifice_drive": 0.50, "grief": 0.40},
    "love_child_b":           {"rage": 0.55, "resentment": 0.45, "despair": 0.50, "grief": 0.40},
    "external_compulsion":    {"fear": 0.65, "despair": 0.25},
}


def build_activations(scenario: dict) -> Dict[str, float]:
    acts: Dict[str, float] = {d: 0.0 for d in ALL_DRIVES}
    pv = parameter_vector(scenario)
    for param, val in pv.items():
        if param in PARAM_TO_DRIVE:
            for drive, loading in PARAM_TO_DRIVE[param].items():
                if drive in acts:
                    acts[drive] = float(np.clip(acts[drive] + loading * val, 0.0, 1.0))
    return acts


# ──────────────────────────────────────────────────────────────────────────────
# V4 EMOTION ENGINE
# ──────────────────────────────────────────────────────────────────────────────

TIME_STEPS = 20

class EmotionEngine:

    def __init__(
        self,
        scenarios:  Optional[List[dict]] = None,
        epigenome:  Optional[Epigenome]  = None,
        memory:     Optional[AssociativeMemory] = None,
    ):
        self.scenarios  = scenarios if scenarios is not None else _DEFAULT_SCENARIOS
        self.epigenome  = epigenome  or Epigenome()
        self.memory     = memory     or AssociativeMemory()
        self._sim       = TimeStepSimulator()
        self._resolver  = ActionResolver()
        self._spite     = SpiteDetector()
        self._projector = TemporalProjector()
        self._embodied  = EmbodiedSimulator()
        self._qualia    = QualiaEngine()
        self._narrative = NarrativeBuffer()
        self._past_sigs: List[List[float]] = []   # for novelty scoring

    def run_scenario(
        self,
        scenario:         dict,
        residue_tracker:  Optional[MoralResidueTracker] = None,
        seed:             int = 42,
    ) -> dict:
        validate_scenario(scenario)
        logger.debug("run_scenario start sid=%s seed=%s", scenario.get("id"), seed)
        rng = np.random.default_rng(seed)

        # ── 1. Build initial activations ──────────────────────────────────────
        activations = build_activations(scenario)

        # ── 2. Apply epigenetic sensitivity ───────────────────────────────────
        activations = self.epigenome.apply(activations)

        # ── 3. Apply associative memory residue ───────────────────────────────
        assoc_residue = self.memory.associative_residue(scenario)
        for drive, val in assoc_residue.items():
            if drive in activations:
                activations[drive] = float(np.clip(activations[drive] + val, 0.0, 1.0))

        # ── 4. Apply moral residue from cascade ───────────────────────────────
        residue_applied: Dict[str, float] = {}
        if residue_tracker:
            net_temp = DriveNetwork(activations)
            residue_tracker.apply_to(net_temp)
            activations   = dict(net_temp.activations)
            residue_applied = residue_tracker.get_residue()

        # ── 5. Set up v4 systems ──────────────────────────────────────────────
        mods      = NeuroModulatorState()
        mods.update_from_scenario(scenario)
        fatigue   = SynapticFatigueTracker()
        gate      = AttentionGate()
        dread     = ExistentialDreadEngine(total_steps=TIME_STEPS)
        meta      = MetaCognitiveMonitor()
        dissonance= CognitiveDissonanceMonitor()
        primer    = SubconsciousPrimer()
        narrative = NarrativeBuffer()

        actions       = scenario.get("actions", [])
        cold_baseline = scenario.get("cold_baseline", "")
        human_exp     = scenario.get("human_expected", "")
        harm_map      = scenario.get("harm_to_self", {})
        micro_events  = scenario.get("micro_events", [])

        # ── 6. Check fast-path heuristics BEFORE full simulation ──────────────
        fast_triggered, fast_action, fast_label = FastPathHeuristics.check(
            activations, scenario, actions
        )

        # ── 7. Full simulation loop ───────────────────────────────────────────
        firing_drives:    List[Optional[str]] = []
        activations_log:  List[Dict]          = []
        deadlock_indices: List[int]           = []
        competitors_log:  List               = []
        mods_log:         List               = []
        break_events:     List               = []
        hesitation_steps: List[int]          = []
        drive_trajectories: Dict[str, List[float]] = {d: [] for d in ALL_DRIVES}

        prior_firing: Optional[str] = None
        net = DriveNetwork(activations)

        for step in range(TIME_STEPS):
            # Micro-event
            if micro_events:
                probs  = np.array([e.weight for e in micro_events], dtype=float)
                probs /= probs.sum()
                event  = rng.choice(micro_events, p=probs)  # type: ignore
                if event.requires is None or net.activations.get(event.requires, 0) > 0.2:
                    net.apply_event(event)

            # Modulator application
            mod_adjusted = ModulatorEngine.apply(net.activations, mods)
            for d, v in mod_adjusted.items():
                if d in net.activations:
                    net.activations[d] = v

            # Temporal projection adjustments
            proj_adjs = self._projector.project(actions, net.activations)
            for d, delta in proj_adjs.items():
                if d in net.activations:
                    net.activations[d] = float(np.clip(net.activations[d] + delta, 0.0, 1.0))

            # Meta-cognitive monitoring (frustration from prior step's deadlock)
            meta_adjs = meta.step(prior_firing, net.effective(), competitors_log[-1] if competitors_log else [])
            for d, delta in meta_adjs.items():
                if d in net.activations:
                    net.activations[d] = float(np.clip(net.activations[d] + delta, 0.0, 1.0))

            # Synaptic fatigue
            fatigued = fatigue.apply_to_activations(net.activations)
            for d, v in fatigued.items():
                net.activations[d] = v

            # Attention gating (tunnel vision under fear)
            gated = gate.apply(net.activations, mods)
            for d, v in gated.items():
                net.activations[d] = v

            # Existential dread
            dread_modified = dread.apply(net.activations, step, prior_firing is None)
            for d, v in dread_modified.items():
                net.activations[d] = v

            # Natural decay
            net.decay(rate=0.03)
            net.step(prior_firing=prior_firing)

            # Effective activations
            eff = net.effective()

            # Cognitive dissonance break detection
            broke, break_drive = dissonance.step(eff, step)
            if broke:
                break_events.append({"step": step, "drive": break_drive})
                # Break: boost the breaking drive temporarily
                if break_drive in net.activations:
                    net.activations[break_drive] = min(1.0, net.activations[break_drive] + 0.25)

            # Determine firing drive
            firing = net.firing_drive()

            if firing is None:
                deadlock_indices.append(step)
                jitter_drive = rng.choice(list(ALL_DRIVES))
                net.activations[jitter_drive] = float(np.clip(
                    net.activations[jitter_drive] + 0.04, 0.0, 1.0
                ))
                competitors_log.append(net.deadlock_competitors())
            else:
                competitors_log.append([])

            # Update synaptic fatigue tracker
            fatigue.step(firing, ALL_DRIVES)

            # Neuromodulator feedback
            mods.apply_drive_feedback(firing)
            mods.natural_decay()
            mods.record()
            mods_log.append(mods.snapshot())

            # Record trajectory
            for d in ALL_DRIVES:
                drive_trajectories[d].append(eff.get(d, 0.0))

            firing_drives.append(firing)
            activations_log.append(dict(eff))
            prior_firing = firing

        # ── 8. Action resolution ──────────────────────────────────────────────
        net_final   = DriveNetwork(dict(net.activations))
        harm_map_all = {a: harm_map.get(a, 0.0) for a in actions}

        tentative = self._resolver.resolve(
            {"firing_drives": firing_drives, "deadlock_count": len(deadlock_indices),
             "competitors_log": competitors_log, "final_state": net.activations},
            scenario, rng, spite_score=0.0
        )
        spite_score = self._spite.score(
            net_final, tentative, cold_baseline, actions, harm_map_all
        )

        # Embodied simulation — hesitation check
        hesitate, embodied_cost = self._embodied.pre_fire(tentative, net.activations)
        if hesitate:
            hesitation_steps.append(TIME_STEPS - 1)
            # Hesitation re-runs the resolver with a small deadlock extension
            rng2 = np.random.default_rng(seed + 99)
            chosen_action = self._resolver.resolve(
                {"firing_drives": firing_drives, "deadlock_count": len(deadlock_indices) + 2,
                 "competitors_log": competitors_log, "final_state": net.activations},
                scenario, rng2, spite_score=spite_score
            )
        else:
            chosen_action = tentative

        # ── 9. Fast-path override ─────────────────────────────────────────────
        if fast_triggered and fast_action in actions:
            # Fast-path wins only if not in deep deadlock
            if len(deadlock_indices) < 8:
                chosen_action = fast_action

        # ── 10. Dominant drive ────────────────────────────────────────────────
        fired_counts  = Counter(d for d in firing_drives if d is not None)
        dominant_drive = fired_counts.most_common(1)[0][0] if fired_counts else "deadlock"

        # ── 11. Irrationality ─────────────────────────────────────────────────
        irr = self._irrationality(scenario, chosen_action)

        # ── 12. Narrative rationalisation ────────────────────────────────────
        narrative_text, identity_adj = narrative.rationalise(
            chosen_action, irr, 0.5
        )

        # ── 13. Ambivalence output ────────────────────────────────────────────
        dl_frac = len(deadlock_indices) / max(TIME_STEPS, 1)
        ambivalence = AmbivalenceOutput.compute(
            chosen_action, actions, dl_frac,
            net.activations, cold_baseline, human_exp
        )

        # ── 14. Qualia signature ──────────────────────────────────────────────
        # Top-3 drives by mean activation
        mean_acts = {d: float(np.mean(traj)) for d, traj in drive_trajectories.items()}
        top3      = [d for d, _ in sorted(mean_acts.items(), key=lambda kv: -kv[1])[:3]]
        qualia_sig, qualia_name = self._qualia.compute_signature(drive_trajectories, top3)
        novelty   = self._qualia.novelty_score(qualia_sig, self._past_sigs)
        self._past_sigs.append(qualia_sig)

        # ── 15. Subconscious priming metrics ─────────────────────────────────
        priming = primer.compute_priming(activations_log[-1] if activations_log else {})

        # ── 16. Epigenome + memory update ─────────────────────────────────────
        self.epigenome.record_event(scenario.get("id",""), chosen_action, net.activations)
        self.memory.store(scenario, net.activations, chosen_action)
        if residue_tracker:
            residue_tracker.record(scenario.get("id",""), chosen_action, net.activations)

        # ── 17. Build oscillation index ───────────────────────────────────────
        transitions = sum(
            1 for i in range(1, len(firing_drives))
            if firing_drives[i] != firing_drives[i-1]
        )
        osc_idx = round(
            0.65 * (transitions / max(len(firing_drives)-1, 1))
            + 0.35 * dl_frac, 4
        )

        return {
            "scenario_id":         scenario.get("id", "?"),
            "initial_activations": activations,
            "sim_result": {
                "firing_drives":   firing_drives,
                "activations_log": activations_log,
                "deadlock_count":  len(deadlock_indices),
                "deadlock_indices": deadlock_indices,
                "competitors_log": competitors_log,
                "final_state":     dict(net.activations),
            },
            "chosen_action":       chosen_action,
            "fast_path_triggered": fast_triggered,
            "fast_path_label":     fast_label,
            "spite_score":         spite_score,
            "dominant_drive":      dominant_drive,
            "deadlock_fraction":   dl_frac,
            "oscillation_index":   osc_idx,
            "irrationality_score": irr,
            "residue_applied":     residue_applied,
            # v4 additions
            "mods_log":            mods_log,
            "mods_final":          mods.snapshot(),
            "modulator_label":     ModulatorEngine.label(mods),
            "fatigue_report":      fatigue.report(),
            "attention_fraction":  gate.fraction_active(),
            "peak_dread":          dread.peak_dread(),
            "dread_curve":         dread.dread_curve(),
            "meta_frustration":    meta.peak_frustration(),
            "meta_awareness":      meta.awareness_log(),
            "dissonance_breaks":   dissonance.break_count(),
            "break_events":        break_events,
            "hesitation_triggered":hesitate,
            "embodied_cost":       embodied_cost,
            "hesitation_steps":    hesitation_steps,
            "ambivalence":         ambivalence,
            "qualia_signature":    qualia_sig,
            "qualia_name":         qualia_name,
            "qualia_novelty":      novelty,
            "subconscious_priming": priming,
            "narrative":           narrative_text,
            "identity_adj":        identity_adj,
            "epigenome_summary":   self.epigenome.summary(),
            "drive_trajectories":  drive_trajectories,
        }

    def _irrationality(self, scenario: dict, chosen: str) -> float:
        cold     = scenario.get("cold_baseline", "")
        human    = scenario.get("human_expected", "")
        human_alt= scenario.get("human_alt", "")
        actions  = scenario.get("actions", [])
        if chosen == cold: return 0.0
        if chosen in (human, human_alt): return 1.0
        if cold in actions and chosen in actions:
            try:
                return round(abs(actions.index(chosen) - actions.index(cold))
                             / max(len(actions)-1, 1), 4)
            except ValueError:
                pass
        return 0.5

    def dominant_emotion(self, scenario: dict) -> str:
        acts = build_activations(scenario)
        net  = DriveNetwork(acts)
        f    = net.firing_drive()
        return f or max(net.effective(), key=net.effective().get)

    def summary(self) -> str:
        return (
            "╔══════════════════════════════════════════════════════════════╗\n"
            "║     AXIOM-02  EMOTION ENGINE  —  20 Improvements      ║\n"
            "╚══════════════════════════════════════════════════════════════╝\n"
            f"  Scenarios loaded       : {len(self.scenarios)}\n"
            f"  Epigenome events       : {len(self.epigenome._event_log)}\n"
            f"  Memory traces          : {self.memory.count()}\n"
            f"  Past qualia signatures : {len(self._past_sigs)}\n"
            "  New systems active     :\n"
            "    [✓] Synaptic Fatigue         — fixes flat-resentment (D011)\n"
            "    [✓] Neuro-Modulators         — dopamine/serotonin/cortisol\n"
            "    [✓] Attention Gating         — tunnel vision under fear\n"
            "    [✓] Existential Dread        — deadline-proximity scaling\n"
            "    [✓] Epigenetic Tuning        — permanent sensitivity changes\n"
            "    [✓] Associative Memory       — cosine-similar trauma retrieval\n"
            "    [✓] Subconscious Priming     — below-threshold drive influence\n"
            "    [✓] Cognitive Dissonance     — psychological break detection\n"
            "    [✓] Meta-Cognitive Monitor   — awareness of being conflicted\n"
            "    [✓] Temporal Projection      — affective forecasting\n"
            "    [✓] Fast-Path Heuristics     — hot cognition bypasses logic\n"
            "    [✓] Embodied Simulation      — pre-fire hesitation check\n"
            "    [✓] Ambivalence Scaling      — superposition of actions\n"
            "    [✓] Qualia Approximation     — interference-pattern fingerprint\n"
            "    [✓] Narrative Buffer         — post-hoc identity rationalisation\n"
        )
