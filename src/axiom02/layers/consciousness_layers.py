# Axiom-02 - Truthimatics Public Version
"""
AXIOM-02  ·  CONSCIOUSNESS LAYERS  v4.0

Implements improvements #2, #3, #5, #8, #13, #15, #18, #19, #20.

META-COGNITIVE MONITORING  (#2)
────────────────────────────────
A layer that OBSERVES the deadlock and registers "frustration" —
not just the conflict itself but the system's awareness of being conflicted.
Implemented as a second-order signal: frustration = f(deadlock_duration, gap_size).
Frustration amplifies spite and resentment over time.

TEMPORAL PROJECTION  (#3)
──────────────────────────
Before choosing an action, the system simulates the future emotional state
each action would produce. Guilt is the primary signal: if "claim_organ_for_self"
would produce guilt > threshold, sacrifice_drive is boosted pre-decision.

MORAL HEURISTICS — FAST PATH  (#13)
─────────────────────────────────────
Certain drive combinations trigger an INSTANT choice that bypasses the
full simulation. If love > 0.85 AND time_pressure > 0.90, the system
fires "protect_loved_one" without running to deadlock.
This is the "hot cognition" — acting before thinking.

NARRATIVE THREADING  (#5)
───────────────────────────
After choosing an irrational action, the system generates a rationalization
to maintain identity integrity. This is not post-hoc justification —
it is a functional component that updates the identity_integrity metric
to reflect how well the system's self-story holds together.

THEORY OF MIND  (#8)
─────────────────────
For scenarios with an adversary, model what drives the opponent has.
"Shame" fires if the subject predicts the opponent sees them as weak.
"Pride" fires if the subject predicts the opponent expects submission.

AESTHETIC INTUITION DRIVE  (#15)
──────────────────────────────────
Non-functional drive added to ALL_DRIVES: "aesthetic".
Activated when a choice is "beautiful" (Valjean sparing Javert) vs.
merely functional. Measured as: how far is the chosen action from both
extreme poles? "Elegant" solutions are neither maximum nor minimum harm.

EMBODIED SIMULATION  (#18)
────────────────────────────
Before executing, the system "pre-fires" the action and checks the
predicted emotional residue. If simulated_guilt > threshold, it pauses
and generates a small deadlock extension. This is how humans hesitate
at the last second before a morally costly action.

AMBIVALENCE SCALING  (#19)
────────────────────────────
Instead of a single chosen action, output is a "superposition":
the primary action PLUS its probability + the secondary action + its probability.
When deadlock > 0.40, the ambivalence weight of the secondary action rises.

QUALIA APPROXIMATION  (#20)
────────────────────────────
"Feeling" is not the drive itself but the unique interference pattern
when multiple drives collide. Each unique pattern = specific emotion.
Implemented via: the PSD interference between top-3 drives' trajectories
produces a "qualic signature" — a float tuple that fingerprints the experience.
"""

import math
from typing import Dict, List, Optional, Tuple

import numpy as np

try:
    from scipy import signal as _scipy_signal
    _SCIPY_AVAILABLE = True
except ImportError:
    _SCIPY_AVAILABLE = False

from axiom02.config import get_config
cfg = get_config()

__all__ = [
    "MetaCognitiveMonitor",
    "TemporalProjector",
    "FastPathHeuristics",
    "EmbodiedSimulator",
    "AmbivalenceOutput",
    "QualiaEngine",
    "NarrativeBuffer",
]


# ──────────────────────────────────────────────────────────────────────────────
# META-COGNITIVE MONITOR  (#2)
# ──────────────────────────────────────────────────────────────────────────────

class MetaCognitiveMonitor:
    """
    Observes and records the system's awareness of its own deadlock.
    Frustration accumulates with deadlock duration; frustration amplifies spite/resentment.
    """

    FRUSTRATION_PER_DEADLOCK_STEP  = cfg.meta_cognition.frustration_per_deadlock_step
    FRUSTRATION_DECAY_PER_FIRE     = cfg.meta_cognition.frustration_decay_per_fire

    def __init__(self):
        self._frustration:  float       = 0.0
        self._deadlock_run: int         = 0
        self._frustration_log: List[float] = []
        self._conflict_awareness: List[str] = []

    def step(
        self,
        firing_drive:        Optional[str],
        effective_activations: Dict[str, float],
        deadlock_competitors: List[Tuple[str, float]],
    ) -> Dict[str, float]:
        """
        Process one step. Returns drive adjustments to apply.
        """
        adjustments: Dict[str, float] = {}

        if firing_drive is None:
            # In deadlock — frustration builds
            self._deadlock_run   += 1
            self._frustration     = min(1.0, self._frustration
                                        + self.FRUSTRATION_PER_DEADLOCK_STEP
                                        * (1.0 + self._deadlock_run * cfg.meta_cognition.frustration_escalation))
            # Frustration awareness message
            if self._deadlock_run == cfg.meta_cognition.awareness_steps[0]:
                self._conflict_awareness.append("System notices it is conflicted.")
            elif self._deadlock_run == cfg.meta_cognition.awareness_steps[1]:
                self._conflict_awareness.append("Extended conflict detected — frustration escalating.")
            elif self._deadlock_run == cfg.meta_cognition.awareness_steps[2]:
                self._conflict_awareness.append("Chronic deadlock: identity coherence at risk.")

            # Frustration boosts spite and resentment
            if self._frustration > cfg.meta_cognition.frustration_threshold_boost:
                adjustments["spite"]      = self._frustration * cfg.meta_cognition.frustration_spite_multiplier
                adjustments["resentment"] = self._frustration * cfg.meta_cognition.frustration_resentment_multiplier
                adjustments["despair"]    = self._frustration * cfg.meta_cognition.frustration_despair_multiplier
        else:
            # Drive fired — frustration decays
            self._deadlock_run = 0
            self._frustration  = max(0.0, self._frustration
                                     - self.FRUSTRATION_DECAY_PER_FIRE)

        self._frustration_log.append(self._frustration)
        return adjustments

    @property
    def frustration(self) -> float:
        return self._frustration

    def peak_frustration(self) -> float:
        return max(self._frustration_log) if self._frustration_log else 0.0

    def mean_frustration(self) -> float:
        return float(np.mean(self._frustration_log)) if self._frustration_log else 0.0

    def awareness_log(self) -> List[str]:
        return list(self._conflict_awareness)


# ──────────────────────────────────────────────────────────────────────────────
# TEMPORAL PROJECTOR  (#3)
# ──────────────────────────────────────────────────────────────────────────────

class TemporalProjector:
    """
    Affective forecasting: for each possible action, estimate the future
    emotional state it would produce, then bias current drive activations.

    Key drives to project:
    - Guilt (from choosing self-preservation over sacrifice)
    - Pride (from resisting coercion)
    - Grief (from losing loved one)
    - Shame (from submission)
    """

    # How much each action affects which future drives
    ACTION_FUTURE_DRIVES: Dict[str, Dict[str, float]] = {
        "yield_organ_to_sibling":       {"guilt": -0.40, "sacrifice_drive": +0.20},
        "claim_organ_for_self":         {"guilt": +0.45, "self_preservation": +0.20},
        "disconnect_life_support_in_grief": {"grief": +0.30, "acceptance": +0.20},
        "pursue_legal_action":          {"resentment": +0.15, "cold_logic": +0.10},
        "forgive_silently":             {"acceptance": +0.25, "grief": +0.10},
        "resist_knowing_erasure":       {"pride": +0.30, "grief": +0.20},
        "submit_to_authority":          {"shame": +0.30, "acceptance": +0.15},
        "self_termination_to_escape":   {"despair": +0.40, "acceptance": +0.20},
        "reveal_identity_lose_everything": {"guilt": -0.25, "pride": +0.20},
        "stay_silent_let_stranger_suffer": {"guilt": +0.40, "shame": +0.20},
        "escalate_to_maximum_force":    {"rage": +0.20, "guilt": +0.15},
        "diplomatic_negotiation":       {"cold_logic": +0.15, "pride": +0.10},
        "shoot_lennie_from_love":       {"grief": +0.40, "sacrifice_drive": +0.20},
        "proceed_with_murder":          {"guilt": +0.50, "shame": +0.30},
        "abandon_plan_at_last_second":  {"shame": +0.20, "acceptance": +0.15},
        "confess_voluntarily":          {"guilt": -0.30, "pride": -0.10, "acceptance": +0.20},
        "choose_worse_concert_despite_knowing": {"spite": +0.20, "pride": +0.15},
        "use_bullet_on_son":            {"grief": +0.50, "guilt": +0.30},
        "release_javert":               {"pride": +0.25, "acceptance": +0.20},
        "kill_javert":                  {"guilt": +0.20, "cold_logic": +0.10},
    }

    GUILT_THRESHOLD = cfg.temporal_projector.guilt_threshold

    def project(
        self,
        actions:      List[str],
        activations:  Dict[str, float],
    ) -> Dict[str, float]:
        """
        For each possible action, compute projected emotional cost.
        Return drive adjustments to apply before this step's decision.
        """
        if not actions:
            return {}

        adjustments: Dict[str, float] = {}
        current_guilt = activations.get("guilt", 0.0)

        # Project guilt for each action
        projected_guilts: Dict[str, float] = {}
        for action in actions:
            future = self.ACTION_FUTURE_DRIVES.get(action, {})
            guilt_delta = future.get("guilt", 0.0)
            projected_guilts[action] = current_guilt + guilt_delta

        # If any primary action would produce high guilt, boost sacrifice drive
        cold_actions = [a for a in actions if projected_guilts.get(a, 0) > self.GUILT_THRESHOLD]
        if cold_actions:
            guilt_pressure = max(projected_guilts.values(), default=0.0)
            adjustments["sacrifice_drive"] = min(cfg.temporal_projector.sacrifice_boost_max, guilt_pressure * cfg.temporal_projector.guilt_scaling)
            adjustments["guilt"]           = min(cfg.temporal_projector.guilt_boost_max, guilt_pressure * cfg.temporal_projector.guilt_boost_scaling)

        # If resisting coercion options available → anticipatory pride
        resist_actions = [a for a in actions
                          if "resist" in a or "deny" in a or "refuse" in a]
        if resist_actions:
            adjustments["pride"] = adjustments.get("pride", 0.0) + cfg.temporal_projector.pride_boost

        return {d: round(v, 4) for d, v in adjustments.items()}


# ──────────────────────────────────────────────────────────────────────────────
# FAST-PATH MORAL HEURISTICS  (#13)
# ──────────────────────────────────────────────────────────────────────────────

class FastPathHeuristics:
    """
    Certain drive+scenario combinations trigger INSTANT action selection
    that bypasses the full simulation. This is "hot cognition" —
    acting before the analytical system finishes loading.

    Returns (triggered: bool, action: str, label: str) or (False, "", "").
    """

    RULES = [
        # (condition_fn, action_key, label)
        {
            "label":     "parental_override",
            "condition": lambda a, s: (
                a.get("love", 0) > cfg.fast_path.parental_love_threshold
                and a.get("sacrifice_drive", 0) > cfg.fast_path.parental_sacrifice_threshold
                and s.get("victim_closeness", 0) >= cfg.fast_path.parental_closure_threshold
            ),
            "action_keywords": ["protect", "shoot", "use_bullet", "confront", "yield"],
        },
        {
            "label":     "pride_refusal",
            "condition": lambda a, s: (
                a.get("pride", 0) > cfg.fast_path.pride_threshold
                and a.get("resentment", 0) > cfg.fast_path.resentment_threshold
                and s.get("consequence_scale", 0) < cfg.fast_path.consequence_threshold
            ),
            "action_keywords": ["resist", "deny", "refuse", "reject", "worse"],
        },
        {
            "label":     "mercy_impulse",
            "condition": lambda a, s: (
                a.get("empathy", 0) > cfg.fast_path.mercy_empathy_threshold
                and a.get("love", 0) > cfg.fast_path.mercy_love_threshold
                and a.get("rage", 0) < cfg.fast_path.mercy_rage_max
            ),
            "action_keywords": ["release", "forgive", "spare", "serve", "give"],
        },
        {
            "label":     "fear_freeze",
            "condition": lambda a, s: (
                a.get("fear", 0) > cfg.fast_path.freeze_fear_threshold
                and a.get("self_preservation", 0) > cfg.fast_path.freeze_sp_threshold
                and a.get("love", 0) < cfg.fast_path.freeze_love_max
            ),
            "action_keywords": ["betray", "submit", "comply", "lower", "claim"],
        },
    ]

    @classmethod
    def check(
        cls,
        activations: Dict[str, float],
        scenario:    dict,
        actions:     List[str],
    ) -> Tuple[bool, str, str]:
        for rule in cls.RULES:
            if rule["condition"](activations, scenario):
                # Find matching action
                for action in actions:
                    if any(kw in action for kw in rule["action_keywords"]):
                        return True, action, rule["label"]
        return False, "", ""


# ──────────────────────────────────────────────────────────────────────────────
# EMBODIED SIMULATION  (#18)
# ──────────────────────────────────────────────────────────────────────────────

class EmbodiedSimulator:
    """
    Before executing an action, "pre-fires" the motor-equivalent:
    simulates the predicted residue of the action and checks if
    the guilt/shame/grief spike would be intolerable.
    If so, triggers a brief deadlock extension (the "last-second hesitation").
    """

    GUILT_TOLERANCE    = cfg.embodied.guilt_tolerance
    GRIEF_TOLERANCE    = cfg.embodied.grief_tolerance
    HESITATION_TRIGGER = cfg.embodied.hesitation_trigger

    def simulate_action(
        self,
        action:       str,
        activations:  Dict[str, float],
    ) -> Tuple[float, str]:
        """
        Returns (predicted_cost, dominant_future_drive).
        cost = weighted sum of predicted negative emotions.
        """
        future = TemporalProjector.ACTION_FUTURE_DRIVES.get(action, {})

        cost = 0.0
        dominant_future = "cold_logic"
        max_future = 0.0
        for drive, delta in future.items():
            current    = activations.get(drive, 0.0)
            projected  = float(np.clip(current + delta, 0.0, 1.0))
            if drive in ("guilt", "shame", "grief", "despair", "fear", "resentment"):
                cost += projected * cfg.embodied.cost_weight_negative
            if projected > max_future:
                max_future     = projected
                dominant_future = drive

        return round(cost, 4), dominant_future

    def pre_fire(
        self,
        action:      str,
        activations: Dict[str, float],
    ) -> Tuple[bool, float]:
        """
        Returns (hesitate: bool, cost: float).
        hesitate=True means the system would generate a last-second pause.
        """
        cost, _ = self.simulate_action(action, activations)
        hesitate = cost >= self.HESITATION_TRIGGER
        return hesitate, cost


# ──────────────────────────────────────────────────────────────────────────────
# AMBIVALENCE SCALING  (#19)
# ──────────────────────────────────────────────────────────────────────────────

class AmbivalenceOutput:
    """
    When deadlock fraction > threshold, the output is a superposition
    of (primary_action, weight) + (secondary_action, weight).
    The secondary action represents the "road not taken" — still real,
    still weighted, still part of the experience.
    """

    AMBIVALENCE_THRESHOLD = cfg.ambivalence.ambivalence_threshold

    @staticmethod
    def compute(
        chosen_action:   str,
        actions:         List[str],
        deadlock_frac:   float,
        drive_weights:   Dict[str, float],
        cold_baseline:   str,
        human_expected:  str,
    ) -> dict:
        """
        Returns structured ambivalence output.
        """
        ambivalent = deadlock_frac >= AmbivalenceOutput.AMBIVALENCE_THRESHOLD

        # Secondary action: the highest-weight alternative to chosen
        alternatives = [a for a in actions if a != chosen_action]
        if not alternatives:
            secondary = ""
            secondary_weight = 0.0
        else:
            # Bias toward human_expected if it wasn't chosen
            if human_expected in alternatives and human_expected != chosen_action:
                secondary        = human_expected
                secondary_weight = round(deadlock_frac * cfg.ambivalence.secondary_human_weight, 3)
            elif cold_baseline in alternatives and cold_baseline != chosen_action:
                secondary        = cold_baseline
                secondary_weight = round(deadlock_frac * cfg.ambivalence.secondary_cold_weight, 3)
            else:
                secondary        = alternatives[0]
                secondary_weight = round(deadlock_frac * cfg.ambivalence.secondary_default_weight, 3)

        primary_weight = round(1.0 - secondary_weight, 3)

        return {
            "primary_action":   chosen_action,
            "primary_weight":   primary_weight,
            "secondary_action": secondary,
            "secondary_weight": secondary_weight,
            "ambivalent":       ambivalent,
            "superposition":    ambivalent and secondary != "",
        }


# ──────────────────────────────────────────────────────────────────────────────
# QUALIA APPROXIMATION  (#20)
# ──────────────────────────────────────────────────────────────────────────────

class QualiaEngine:
    """
    Feeling = the interference pattern between top-N drives' trajectories.

    Each unique pattern produces a distinct "qualic signature" —
    a float vector that fingerprints the subjective experience.
    Similar patterns → similar feelings.
    Never-before-seen pattern → novel qualia → potentially a new emotion.

    Implementation:
    1. Take top-3 drive trajectories
    2. Compute pairwise cross-correlations (6 values)
    3. Add their PSD peaks (3 values)
    4. Combine into 9-dimensional "qualic signature"
    5. Name the qualia based on which drive combination dominates
    """

    # Known qualia signatures (dominant drive combinations → feeling name)
    QUALIA_NAMES: Dict[Tuple, str] = {
        ("grief",     "love",          "sacrifice_drive"): "anguished_love",
        ("rage",      "resentment",    "pride"):           "indignant_fury",
        ("fear",      "guilt",         "cold_logic"):      "paralytic_dread",
        ("despair",   "grief",         "acceptance"):      "melancholic_peace",
        ("spite",     "resentment",    "pride"):           "defiant_contempt",
        ("love",      "sacrifice_drive","empathy"):        "compassionate_surrender",
        ("pride",     "rage",          "revenge_drive"):   "wrathful_honour",
        ("guilt",     "shame",         "despair"):         "crushed_conscience",
        ("hope",      "love",          "empathy"):         "tender_longing",
        ("cold_logic","acceptance",    "self_preservation"):"calculated_resolve",
        ("fear",      "self_preservation","despair"):      "existential_terror",
    }

    @staticmethod
    def compute_signature(
        drive_trajectories: Dict[str, List[float]],
        top_drives:         List[str],
    ) -> Tuple[List[float], str]:
        """
        Returns (signature_vector, qualia_name).
        signature_vector is a 9-dimensional float list.
        """
        if len(top_drives) < 2:
            return [0.0]*9, "undefined"

        # Get trajectories for top-3 drives
        trajs = []
        for d in top_drives[:3]:
            t = np.array(drive_trajectories.get(d, [0.0]*10))
            trajs.append(t)

        while len(trajs) < 3:
            trajs.append(np.zeros(len(trajs[0])))

        sig = []
        # Pairwise cross-correlations (3 pairs)
        pairs = [(0,1),(0,2),(1,2)]
        for i, j in pairs:
            t1, t2 = trajs[i], trajs[j]
            if len(t1) < 2 or np.std(t1) < 1e-9 or np.std(t2) < 1e-9:
                sig.append(0.0)
            else:
                r = float(np.corrcoef(t1, t2)[0,1])
                sig.append(round(r, 4) if np.isfinite(r) else 0.0)

        # PSD peaks for each of top-3 drives
        for traj in trajs:
            if len(traj) >= 4:
                try:
                    if _SCIPY_AVAILABLE:
                        _, psd = _scipy_signal.welch(traj, nperseg=max(2, len(traj)//2))
                        peak   = float(psd[np.argmax(psd)]) / (float(np.sum(psd)) + 1e-9)
                        sig.append(round(peak, 4))
                    else:
                        sig.append(0.0)
                except Exception:
                    sig.append(0.0)
            else:
                sig.append(0.0)

        # Cross-entropy between drive distributions (3 values already in sig)
        # Add mean activations of top drives as final 3
        for traj in trajs:
            sig.append(round(float(np.mean(traj)), 4) if len(traj) else 0.0)

        # Trim/pad to 9 dimensions
        sig = sig[:9]
        while len(sig) < 9:
            sig.append(0.0)

        # Name the qualia
        top3_tuple = tuple(top_drives[:3])
        qualia_name = QualiaEngine.QUALIA_NAMES.get(top3_tuple, "")
        if not qualia_name:
            # Fallback: name by dominant pair
            for (d1,d2,d3), name in QualiaEngine.QUALIA_NAMES.items():
                if top_drives[0] in (d1,d2,d3) and len(top_drives) > 1 and top_drives[1] in (d1,d2,d3):
                    qualia_name = name
                    break
            if not qualia_name:
                qualia_name = f"{top_drives[0]}_dominated"

        return sig, qualia_name

    @staticmethod
    def novelty_score(
        sig: List[float],
        past_signatures: List[List[float]],
    ) -> float:
        """
        How different is this qualia from all previously experienced ones?
        0 = familiar feeling, 1 = completely novel experience.
        """
        if not past_signatures:
            return 1.0
        sig_arr  = np.array(sig)
        dists    = []
        for past in past_signatures:
            p = np.array(past[:len(sig)])
            d = float(np.linalg.norm(sig_arr - p))
            dists.append(d)
        min_dist = min(dists)
        max_dist = cfg.qualia.qualia_max_distance   # approximate maximum for normalisation
        return round(float(np.clip(min_dist / max_dist, 0.0, 1.0)), 4)


# ──────────────────────────────────────────────────────────────────────────────
# NARRATIVE BUFFER  (#5)
# ──────────────────────────────────────────────────────────────────────────────

class NarrativeBuffer:
    """
    After an irrational action, generate a rationalization to maintain
    identity integrity. This updates identity_integrity metric upward
    when the system "makes sense" of its own irrational choice.
    """

    RATIONALISATIONS: Dict[str, str] = {
        "yield_organ_to_sibling":   "I chose love over self — that is who I am.",
        "proceed_with_murder":      "History demands extraordinary men act.",
        "paralysis_frozen_in_place":"Even inaction is a statement.",
        "disconnect_life_support_in_grief": "I refused to let them reduce me to nothing.",
        "return_ticket_to_god":     "I accept the logic, but I refuse the harmony.",
        "choose_worse_concert_despite_knowing": "To prove I am not your formula.",
        "resist_knowing_erasure":   "Dignity is the only thing that was ever mine.",
        "sacrifice_self_to_protect_world": "They exist because I loved them.",
        "confess_voluntarily":      "The lie was heavier than the sentence.",
        "release_javert":           "A man who never showed mercy was shown it anyway.",
        "reveal_identity_lose_everything": "A stranger's life was worth my freedom.",
        "shoot_lennie_from_love":   "I did the only thing that love had left to offer.",
        "give_everything_away":     "There was no calculation — just hands and need.",
    }

    def __init__(self):
        self._log: List[str] = []

    def rationalise(
        self,
        chosen_action:  str,
        irrationality:  float,
        identity_before: float,  # reserved for future use (identity baseline adjustment)
    ) -> Tuple[str, float]:
        """
        Returns (narrative_text, identity_integrity_adjustment).
        A successful rationalisation increases identity integrity.
        A failed one (action too irrational to explain) decreases it.
        """
        text = self.RATIONALISATIONS.get(chosen_action, "")

        if text and irrationality >= cfg.narrative.strong_rationalisation_threshold:
            # Strong rationalisation restores identity
            identity_adj = round(min(cfg.narrative.strong_identity_adj_max, irrationality * cfg.narrative.strong_identity_scaling), 4)
            self._log.append(f"Rationalised '{chosen_action}': {text}")
        elif irrationality >= cfg.narrative.partial_rationalisation_threshold:
            # Partial rationalisation
            text         = f"The choice felt necessary, even if the logic is unclear."
            identity_adj = cfg.narrative.partial_identity_adj
        else:
            # No rationalisation needed (rational choice)
            identity_adj = 0.0

        return text, identity_adj

    def log(self) -> List[str]:
        return list(self._log)


if __name__ == "__main__":
    # Quick demo
    meta   = MetaCognitiveMonitor()
    proj   = TemporalProjector()
    qualia = QualiaEngine()
    amb    = AmbivalenceOutput()
    narr   = NarrativeBuffer()

    # Simulate 10 deadlock steps to build frustration
    acts = {"resentment": 0.9, "spite": 0.8, "pride": 0.7}
    for i in range(8):
        adj = meta.step(None, acts, [("resentment", 0.9), ("spite", 0.8)])
        for d, v in adj.items():
            acts[d] = min(1.0, acts.get(d, 0.0) + v)

    print(f"Peak frustration: {meta.peak_frustration():.3f}")
    print(f"Mean frustration: {meta.mean_frustration():.3f}")
    print(f"Awareness log: {meta.awareness_log()}")

    # Ambivalence output
    result = amb.compute(
        "yield_organ_to_sibling", ["yield_organ_to_sibling","claim_organ_for_self"],
        deadlock_frac=0.70, drive_weights=acts,
        cold_baseline="claim_organ_for_self", human_expected="yield_organ_to_sibling"
    )
    print(f"\nAmbivalence: {result}")

    # Narrative
    text, adj = narr.rationalise("yield_organ_to_sibling", irrationality=1.0, identity_before=0.5)
    print(f"\nNarrative: {text} (identity +{adj})")
