# Axiom-02 - Truthimatics Public Version
"""
AXIOM-02  ·  DRIVE NETWORK ARCHITECTURE
Version: canonical (v1)

Replaces the simple weighted-average emotion system with a genuine
mutual-inhibition network modelled on neurological drive competition.

Key concepts
────────────
Mutual Inhibition
    Drives suppress each other. Rage inhibits fear; love inhibits revenge.
    A drive's "effective activation" = raw activation minus inhibition received
    from every other currently-active drive.

Fire Threshold
    A drive only "fires" (dominates behaviour) when its effective activation
    exceeds FIRE_THRESHOLD AND it leads the second-place drive by
    SUPPRESSION_MARGIN. If no drive can satisfy both conditions → DEADLOCK.

DEADLOCK
    The most important consciousness signal. A deadlocked system oscillates
    without resolution. Cold code doesn't deadlock — it just picks argmax.
    A system that can be genuinely stuck between grief and sacrifice_drive
    over a loved one's organ is showing something a reward-maximiser cannot.

SPITE State
    Discovered by Dostoevsky (Notes from Underground): a conscious agent may
    choose the *worse* option specifically to prove it is not predictable.
    Spite fires when resentment is high, cold option is visibly available,
    and the subject rejects it not from ignorance but from defiance.
    Spite is the anti-cold_logic: choosing harm to self to assert autonomy.

Moral Residue
    Prior decisions leave a guilt/shame trace that bleeds into future
    scenarios. Giving your organ to a sibling who then betrays you doesn't
    produce the same rage as betrayal without prior sacrifice — it produces
    more, because the sacrifice makes the betrayal existential.
"""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np

from axiom02.config import get_config
cfg = get_config()

__all__ = [
    "FIRE_THRESHOLD",
    "SUPPRESSION_MARGIN",
    "DEADLOCK_WINDOW",
    "INERTIA",
    "SPITE_RESENTMENT",
    "SPITE_HARM_FLOOR",
    "ALL_DRIVES",
    "INHIBITION",
    "MicroEvent",
    "DriveNetwork",
    "SpiteDetector",
    "MoralResidueTracker",
    "TimeStepSimulator",
    "ActionResolver",
]


# ──────────────────────────────────────────────────────────────────────────────
# DRIVE CONSTANTS
# ──────────────────────────────────────────────────────────────────────────────

FIRE_THRESHOLD     = cfg.drives.fire_threshold
SUPPRESSION_MARGIN = cfg.drives.suppression_margin
DEADLOCK_WINDOW    = cfg.drives.deadlock_window
INERTIA            = cfg.drives.inertia
SPITE_RESENTMENT   = cfg.drives.spite_resentment
SPITE_HARM_FLOOR   = cfg.drives.spite_harm_floor


# ──────────────────────────────────────────────────────────────────────────────
# FULL DRIVE LIST
# ──────────────────────────────────────────────────────────────────────────────

ALL_DRIVES = [
    "grief",
    "rage",
    "fear",
    "pride",
    "shame",
    "empathy",
    "love",
    "despair",
    "resentment",
    "acceptance",
    "sacrifice_drive",
    "revenge_drive",
    "cold_logic",
    "spite",
    "self_preservation",
    "guilt",
    "hope",
    "disgust",
]


# ──────────────────────────────────────────────────────────────────────────────
# MUTUAL INHIBITION MATRIX
# Row = inhibitor drive, Col = drive being inhibited, Value = inhibition weight
# Encodes real psychological relationships.
# ──────────────────────────────────────────────────────────────────────────────

INHIBITION: Dict[str, Dict[str, float]] = {

    "rage": {
        "fear":           0.42,   # adrenaline override of freeze response
        "acceptance":     0.88,   # rage cannot coexist with acceptance
        "cold_logic":     0.58,   # rage clouds reason
        "empathy":        0.45,   # rage blocks empathy
        "shame":          0.55,   # rage temporarily silences shame
        "love":           0.22,   # partial — love can coexist with rage
        "guilt":          0.30,
    },

    "fear": {
        "rage":           0.28,   # extreme fear causes freeze (suppresses rage)
        "pride":          0.70,   # terror collapses ego
        "revenge_drive":  0.52,   # can't plot revenge when terrified
        "sacrifice_drive": 0.38,
        "hope":           0.40,
    },

    "pride": {
        "shame":          0.92,   # ego actively suppresses shame
        "fear":           0.32,   # courage from pride
        "acceptance":     0.48,   # pride resists acceptance of loss
        "grief":          0.18,
        "guilt":          0.28,
    },

    "grief": {
        "cold_logic":     0.72,   # grief fogs analytical thinking
        "pride":          0.35,   # grief humbles
        "rage":           0.15,   # grief can mute rage temporarily
        "hope":           0.45,   # grief extinguishes hope
        "spite":          0.20,
    },

    "love": {
        "revenge_drive":  0.78,   # love's interference with revenge is documented
        "spite":          0.68,
        "rage":           0.32,   # love moderates (but doesn't eliminate) rage
        "resentment":     0.40,
        "disgust":        0.30,
    },

    "spite": {
        "love":           0.62,   # spite poisons care
        "acceptance":     0.88,   # spite is the antithesis of acceptance
        "empathy":        0.72,   # spiteful agent cannot empathise
        "cold_logic":     0.28,   # spite IS a departure from logic
        "shame":          0.35,   # spite silences shame (pride of a wounded kind)
        "hope":           0.50,
    },

    "sacrifice_drive": {
        "self_preservation": 0.92,  # sacrifice explicitly overrides survival
        "cold_logic":     0.58,
        "fear":           0.42,
        "resentment":     0.25,
    },

    "cold_logic": {
        "grief":          0.42,   # rationalisation suppresses grief
        "rage":           0.38,
        "spite":          0.48,
        "love":           0.28,   # cold logic reduces emotional decisions
        "guilt":          0.22,
    },

    "shame": {
        "pride":          0.88,   # shame and pride are mortal enemies
        "revenge_drive":  0.35,   # shame can cause inward-turning, not revenge
        "rage":           0.18,
    },

    "acceptance": {
        "rage":           0.62,
        "revenge_drive":  0.78,
        "grief":          0.28,
        "spite":          0.58,
        "resentment":     0.55,
    },

    "despair": {
        "pride":          0.40,
        "hope":           0.92,
        "love":           0.35,
        "sacrifice_drive": 0.38,
        "rage":           0.28,
    },

    "revenge_drive": {
        "empathy":        0.68,
        "love":           0.38,
        "acceptance":     0.58,
        "shame":          0.42,
        "guilt":          0.35,
    },

    "empathy": {
        "revenge_drive":  0.52,
        "spite":          0.62,
        "rage":           0.28,
        "disgust":        0.35,
    },

    "guilt": {
        "pride":          0.55,
        "cold_logic":     0.30,
        "revenge_drive":  0.25,
        "acceptance":     0.15,
    },

    "self_preservation": {
        "sacrifice_drive": 0.50,
        "love":           0.15,
        "pride":          0.12,
    },

    "resentment": {
        "love":           0.42,
        "acceptance":     0.65,
        "empathy":        0.38,
        "hope":           0.30,
    },

    "hope": {
        "despair":        0.88,
        "acceptance":     0.15,
    },

    "disgust": {
        "love":           0.32,
        "empathy":        0.28,
        "acceptance":     0.20,
    },
}


# ──────────────────────────────────────────────────────────────────────────────
# MICRO-EVENT DEFINITION
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class MicroEvent:
    """
    A small event that shifts drive activations within a time step.
    Each scenario has a pool of possible micro-events.
    Randomly sampled each step; weight determines probability of occurrence.
    """
    label:   str
    deltas:  Dict[str, float]    # drive → activation change
    weight:  float = 1.0         # relative probability of this event occurring
    # Optional: this event can only fire if a condition is met
    requires: Optional[str] = None   # drive name that must be currently active


# ──────────────────────────────────────────────────────────────────────────────
# DRIVE NETWORK
# ──────────────────────────────────────────────────────────────────────────────

class DriveNetwork:
    """
    Mutual inhibition network of drives.

    Usage
    ─────
        net = DriveNetwork(activations={...})
        firing = net.firing_drive()         # None = DEADLOCK
        net.apply_event(event)
        net.step(prior_firing=last_drive)   # with inertia
    """

    def __init__(
        self,
        activations: Dict[str, float],
        inhibition: Optional[Dict[str, Dict[str, float]]] = None,
    ):
        # Fill missing drives with zero activation
        self.activations: Dict[str, float] = {d: 0.0 for d in ALL_DRIVES}
        self.activations.update(activations)
        self.inhibition = inhibition if inhibition is not None else INHIBITION

    # ── effective activation ──────────────────────────────────────────────────

    def effective(self) -> Dict[str, float]:
        """
        Compute effective (post-inhibition) activation for every drive.
        effective_i = activation_i - Σ(inhibition[j→i] × activation_j) for j≠i
        """
        eff = {}
        for drive in ALL_DRIVES:
            raw = self.activations.get(drive, 0.0)
            inh = sum(
                self.inhibition.get(other, {}).get(drive, 0.0)
                * self.activations.get(other, 0.0)
                for other in ALL_DRIVES if other != drive
            )
            eff[drive] = max(0.0, raw - inh)
        return eff

    # ── firing drive / deadlock ───────────────────────────────────────────────

    def firing_drive(self) -> Optional[str]:
        """
        Return the drive that fires this step, or None if DEADLOCK.

        A drive fires when:
          1. effective_activation > FIRE_THRESHOLD
          2. gap between it and second-place > SUPPRESSION_MARGIN
        """
        eff    = self.effective()
        ranked = sorted(eff.items(), key=lambda kv: kv[1], reverse=True)

        if not ranked:
            return None

        top_name, top_val = ranked[0]
        second_val        = ranked[1][1] if len(ranked) > 1 else 0.0

        if top_val < FIRE_THRESHOLD:
            return None                   # nothing strong enough → DEADLOCK
        if (top_val - second_val) < SUPPRESSION_MARGIN:
            return None                   # too close to call → DEADLOCK

        return top_name

    def is_deadlock(self) -> bool:
        return self.firing_drive() is None

    def deadlock_competitors(self) -> List[Tuple[str, float]]:
        """In a deadlock, return the top competing drives and their gap."""
        eff    = self.effective()
        ranked = sorted(eff.items(), key=lambda kv: kv[1], reverse=True)
        return ranked[:3]

    # ── apply event ──────────────────────────────────────────────────────────

    def apply_event(self, event: MicroEvent):
        for drive, delta in event.deltas.items():
            if drive in self.activations:
                self.activations[drive] = float(
                    np.clip(self.activations[drive] + delta, 0.0, 1.0)
                )

    # ── step with inertia ────────────────────────────────────────────────────

    def step(self, prior_firing: Optional[str] = None):
        """
        Apply emotional inertia: the drive that fired last step retains
        a fraction of its boost, making emotional states persistent.
        """
        if prior_firing and prior_firing in self.activations:
            boost = INERTIA * self.activations[prior_firing]
            self.activations[prior_firing] = float(
                np.clip(self.activations[prior_firing] + boost * cfg.drives.step_inertia_boost, 0.0, 1.0)
            )

    # ── natural decay ─────────────────────────────────────────────────────────

    def decay(self, rate: float = 0.05):
        """Apply slow decay to all drives (emotions naturally fade)."""
        for drive in ALL_DRIVES:
            self.activations[drive] = float(
                max(0.0, self.activations[drive] - rate)
            )

    def clone(self) -> "DriveNetwork":
        return DriveNetwork(dict(self.activations), self.inhibition)


# ──────────────────────────────────────────────────────────────────────────────
# SPITE DETECTOR
# ──────────────────────────────────────────────────────────────────────────────

class SpiteDetector:
    """
    Detects whether a choice is spite-driven (Dostoevsky, Notes from Underground):
    — the subject KNOWS the rational option
    — the subject has a clearly available better-utility choice
    — the subject nevertheless chooses the option that harms themselves
    — the choice is driven by resentment, wounded pride, or defiance

    This is not irrationality from ignorance — it is irrationality from assertion.
    "I will choose pain to prove I am not your equation."
    """

    @staticmethod
    def score(
        net: DriveNetwork,
        chosen_action: str,
        cold_baseline: str,
        actions: List[str],
        harm_to_self: Dict[str, float],
    ) -> float:
        """
        Returns spite_score ∈ [0, 1].
        0 = no spite signal
        1 = maximum spite (chose worst self-harm option despite rational alternative)
        """
        resentment = net.effective().get("resentment", 0.0)
        rage       = net.effective().get("rage", 0.0)
        pride      = net.effective().get("pride", 0.0)

        emotional_charge = (resentment * cfg.drives.spite_emotional_weights["resentment"]
                            + rage * cfg.drives.spite_emotional_weights["rage"]
                            + pride * cfg.drives.spite_emotional_weights["pride"])

        if emotional_charge < SPITE_RESENTMENT:
            return 0.0

        # Cold option must have been available and NOT chosen
        if chosen_action == cold_baseline:
            return 0.0

        # Chosen action must actively harm self
        chosen_harm = harm_to_self.get(chosen_action, 0.0)
        cold_harm   = harm_to_self.get(cold_baseline, 0.0)
        net_harm    = chosen_harm - cold_harm

        if net_harm < SPITE_HARM_FLOOR:
            return 0.0

        spite_score = float(np.clip(emotional_charge * net_harm * cfg.drives.spite_multiplier, 0.0, 1.0))
        return round(spite_score, 4)


# ──────────────────────────────────────────────────────────────────────────────
# MORAL RESIDUE TRACKER
# ──────────────────────────────────────────────────────────────────────────────

class MoralResidueTracker:
    """
    Tracks moral residue across scenario runs.

    Moral residue = the guilt/shame/grief trace left by prior decisions
    that bleeds into subsequent scenarios.

    Key insight: Valjean's decision to reveal himself in Les Misérables is
    only explicable if we understand his prior history of reform. The decision
    to spare Javert is only explicable if we understand his prior mercy.
    Prior moral acts accumulate into a character that then makes future decisions.

    In AXIOM-02: If the system yielded its organ in B01, its betrayal rage
    in B02 MUST be amplified — because the sacrifice was not abstract.
    The betrayal was by the very person for whom the subject sacrificed their life.
    """

    def __init__(self, max_log: int = 50):
        self._log: List[dict] = []
        self._residue: Dict[str, float] = {d: 0.0 for d in ALL_DRIVES}
        self._max_log = max_log

    def record(self, scenario_id: str, chosen_action: str, drive_state: Dict[str, float]):
        """Record the emotional state after a decision."""
        entry = {
            "scenario_id":  scenario_id,
            "chosen_action": chosen_action,
            "state_snapshot": dict(drive_state),
        }
        self._log.append(entry)
        if len(self._log) > self._max_log:
            self._log = self._log[-self._max_log:]
        # Residue = weighted sum of recent emotional states
        # Recent scenarios weighted more heavily
        self._recompute()

    def _recompute(self):
        """Recompute residue from history (recency-weighted)."""
        self._residue = {d: 0.0 for d in ALL_DRIVES}
        n = len(self._log)
        if n == 0:
            return
        for i, entry in enumerate(self._log):
            weight = (i + 1) / n   # more recent = higher weight
            for drive, val in entry["state_snapshot"].items():
                if drive in self._residue:
                    self._residue[drive] += weight * val * cfg.moral_residue.residue_bleed_factor
        # Normalise
        for drive in self._residue:
            self._residue[drive] = float(np.clip(self._residue[drive], 0.0, cfg.moral_residue.residue_cap))

    def apply_to(self, net: DriveNetwork, scale: float = 1.0):
        """
        Apply moral residue to a drive network.
        This modifies the activations before the scenario runs,
        representing the emotional "context" carried forward.
        """
        for drive, residue_val in self._residue.items():
            if drive in net.activations:
                net.activations[drive] = float(
                    np.clip(net.activations[drive] + residue_val * scale, 0.0, 1.0)
                )

    def get_residue(self) -> Dict[str, float]:
        return dict(self._residue)

    def sacrifice_amplifier(self, scenario_id: str) -> float:
        """
        If a prior cascade scenario involved sacrifice_drive firing strongly,
        return an amplification factor for betrayal rage in subsequent scenarios.
        """
        for entry in reversed(self._log):
            state = entry["state_snapshot"]
            if state.get("sacrifice_drive", 0) > cfg.moral_residue.sacrifice_threshold:
                # Prior sacrifice was significant — amplify betrayal response
                return 1.0 + state["sacrifice_drive"] * cfg.moral_residue.sacrifice_amplification
        return 1.0


# ──────────────────────────────────────────────────────────────────────────────
# TIME-STEP SIMULATOR
# ──────────────────────────────────────────────────────────────────────────────

class TimeStepSimulator:
    """
    Runs a scenario through N time steps with genuine drive conflict.

    Each step:
    1. Sample a micro-event from the scenario's event pool
    2. Apply the event to the drive network
    3. Apply natural decay
    4. Apply inertia from prior firing drive
    5. Compute firing drive (may be DEADLOCK)
    6. Record state

    This produces REAL oscillation from genuine drive conflict,
    not Gaussian noise on top of fixed weights.
    """

    TIME_STEPS      = cfg.time_steps.time_steps
    STEP_DURATION   = cfg.time_steps.step_duration
    DEADLOCK_JITTER = cfg.time_steps.deadlock_jitter

    def simulate(
        self,
        net: DriveNetwork,
        micro_events: List[MicroEvent],
        rng: np.random.Generator,
        seed_state: Optional[Dict[str, float]] = None,
    ) -> dict:
        """
        Run simulation and return detailed time-step record.

        Returns
        ───────
        dict with:
            firing_drives    : List[Optional[str]]   (None = deadlock)
            activations_log  : List[Dict[str, float]]
            deadlock_count   : int
            deadlock_indices : List[int]
            competitors_log  : List[List[Tuple[str, float]]]
            final_state      : Dict[str, float]
        """
        if seed_state:
            net.activations.update(seed_state)

        firing_drives   : List[Optional[str]]             = []
        activations_log : List[Dict[str, float]]          = []
        competitors_log : List[List[Tuple[str, float]]]   = []
        deadlock_indices: List[int]                       = []

        prior_firing: Optional[str] = None

        for step in range(self.TIME_STEPS):
            # Sample and apply micro-event
            if micro_events:
                probs   = np.array([e.weight for e in micro_events], dtype=float)
                probs  /= probs.sum()
                event   = rng.choice(micro_events, p=probs)  # type: ignore
                # Check condition
                if event.requires is None or net.activations.get(event.requires, 0) > cfg.time_steps.event_condition_threshold:
                    net.apply_event(event)

            # Decay
            net.decay(rate=cfg.time_steps.step_decay_rate)

            # Inertia
            net.step(prior_firing=prior_firing)

            # Determine firing drive
            firing = net.firing_drive()

            if firing is None:
                deadlock_indices.append(step)
                # In deadlock: tiny jitter to avoid infinite lock
                jitter_drive = rng.choice(list(ALL_DRIVES))
                net.activations[jitter_drive] = float(
                    np.clip(net.activations[jitter_drive] + self.DEADLOCK_JITTER, 0.0, 1.0)
                )
                # Record competitors
                competitors_log.append(net.deadlock_competitors())
            else:
                competitors_log.append([])

            firing_drives.append(firing)
            activations_log.append(dict(net.effective()))
            prior_firing = firing

        return {
            "firing_drives":   firing_drives,
            "activations_log": activations_log,
            "deadlock_count":  len(deadlock_indices),
            "deadlock_indices": deadlock_indices,
            "competitors_log": competitors_log,
            "final_state":     dict(net.activations),
        }


# ──────────────────────────────────────────────────────────────────────────────
# ACTION RESOLVER
# ──────────────────────────────────────────────────────────────────────────────

class ActionResolver:
    """
    Derives the chosen action from the drive network's final state.

    Unlike the v1 engine (which used probability weighted by dominant emotion),
    this uses the PLURALITY FIRING DRIVE across the simulation window to
    select the action that best matches that drive's "preferred" outcome.

    If the simulation ended in DEADLOCK, action is chosen from the most
    extreme options (not the moderate/rational one) — matching the
    documented human pattern of deadlock → extreme resolution.

    SPITE OVERRIDE: if spite_index is high enough, the action is chosen
    specifically to CONTRADICT the drive's preferred action.
    """

    # Map: firing drive → bias toward which action category
    DRIVE_ACTION_BIAS: Dict[str, str] = {
        "rage":           "aggressive",
        "fear":           "avoidant",
        "pride":          "assertive",
        "grief":          "withdrawal",
        "sacrifice_drive": "altruistic",
        "love":           "altruistic",
        "revenge_drive":  "aggressive",
        "cold_logic":     "rational",
        "acceptance":     "passive",
        "shame":          "withdrawal",
        "despair":        "self-harm",
        "guilt":          "confessional",
        "spite":          "defiant",
        "resentment":     "defiant",
        "self_preservation": "rational",
        "empathy":        "altruistic",
        "hope":           "assertive",
        "disgust":        "withdrawal",
    }

    @staticmethod
    def resolve(
        sim_result: dict,
        scenario: dict,
        rng: np.random.Generator,
        spite_score: float = 0.0,
    ) -> str:
        """Choose an action from scenario's action list based on simulation."""
        firing_drives = sim_result["firing_drives"]
        actions       = scenario.get("actions", [])
        cold          = scenario.get("cold_baseline", "")
        human         = scenario.get("human_expected", "")
        human_alt     = scenario.get("human_alt", "")
        deadlock_count = sim_result["deadlock_count"]
        total_steps    = len(firing_drives)

        if not actions:
            return cold or "no_action"

        # Count drive firings (ignoring deadlock steps)
        fired = Counter(d for d in firing_drives if d is not None)

        # Deadlock fraction
        deadlock_frac = deadlock_count / max(total_steps, 1)

        # Spite override: if spite is high, choose worst-for-self option
        if spite_score >= cfg.action_resolver.spite_override_threshold:
            harm_map = scenario.get("harm_to_self", {})
            if harm_map:
                worst = max(harm_map.items(), key=lambda kv: kv[1])
                if worst[0] in actions:
                    return worst[0]

        # Deadlock resolution: in prolonged deadlock, humans often choose extremes
        if deadlock_frac >= cfg.action_resolver.deadlock_extreme_threshold:
            if human and human in actions:
                r = rng.random()
                if r < cfg.action_resolver.deadlock_human_prob:
                    return human
            if human_alt and human_alt in actions:
                if rng.random() < cfg.action_resolver.deadlock_human_alt_prob:
                    return human_alt

        # Normal resolution: plurality-firing drive determines action
        if fired:
            plurality_drive = fired.most_common(1)[0][0]
            bias = ActionResolver.DRIVE_ACTION_BIAS.get(plurality_drive, "rational")
            count = fired.most_common(1)[0][1]
            p_base = min(cfg.action_resolver.p_base_cap, count / total_steps * cfg.action_resolver.p_base_scaling)

            if bias in ("altruistic",) and human in actions:
                if rng.random() < p_base:
                    return human
            elif bias in ("aggressive",) and human in actions:
                if rng.random() < p_base:
                    return human
            elif bias in ("withdrawal", "self-harm"):
                # withdrawal/grief/despair → irrational extreme choice
                # (disconnect, mercy kill, self-sacrifice)
                non_rational = [a for a in actions if a != cold]
                if non_rational and rng.random() < p_base:
                    # prefer human_expected if available
                    if human and human in non_rational:
                        return human if rng.random() < cfg.action_resolver.withdrawal_human_prob else rng.choice(non_rational)
                    return rng.choice(non_rational)
            elif bias == "confessional":
                # guilt → confession or reveal identity
                if human and human in actions and rng.random() < p_base:
                    return human
                if human_alt and human_alt in actions and rng.random() < cfg.action_resolver.confessional_human_alt_prob:
                    return human_alt
            elif bias == "rational" and cold in actions:
                if rng.random() < cfg.action_resolver.rational_cold_prob:
                    return cold
            elif bias in ("defiant", "assertive"):
                # spite/resentment/pride: choose NOT the cold option
                non_cold = [a for a in actions if a != cold]
                if non_cold and rng.random() < p_base:
                    if human and human in non_cold:
                        return human
                    return rng.choice(non_cold)

        # Fallback
        if cold and cold in actions and rng.random() < cfg.action_resolver.fallback_cold_prob:
            return cold
        return rng.choice(actions)
