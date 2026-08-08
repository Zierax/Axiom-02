# Axiom-02 - Truthimatics Public Version
"""
AXIOM-02  ·  EPIGENETIC SYSTEM  v4.0

Implements improvements #7, #9, #14, #16 from the consciousness upgrade roadmap.

EPIGENETIC DRIVE TUNING  (#7)
──────────────────────────────
Trauma doesn't just leave a temporary residue — it permanently changes the
SENSITIVITY of certain drives. A system that experienced betrayal-cascade
(B01→B02) should permanently have a higher spite_index sensitivity for
all future scenarios. This is implemented as a JSON-serialisable state
that persists across sessions (saved/loaded from epigenome.json).

RECURSIVE SELF-MODIFICATION  (#16)
────────────────────────────────────
High guilt scores can suppress the rage drive in future cycles.
High shame can suppress pride.
Implemented as an "autoregulation map" that overwrites drive weights
based on sustained exposure to certain emotional states.

ASSOCIATIVE EMOTIONAL MEMORY  (#14)
─────────────────────────────────────
Instead of only the most-recent residue, use cosine similarity between
the current scenario's parameter vector and past trauma vectors to pull
the MOST SIMILAR past emotional state, not just the most recent.

SUBCONSCIOUS PRIMING  (#9)
────────────────────────────
Drives that haven't crossed the FIRE_THRESHOLD still influence decisions.
Any drive above PRIME_THRESHOLD adds a weighted "subconscious" nudge to
the action selection probability, even if it never fired.
"""

import json
import math
import os
from typing import Dict, List, Optional, Tuple
from pathlib import Path

import numpy as np

from axiom02.config import get_config
cfg = get_config()

EPIGENOME_FILE  = Path(__file__).parent / "epigenome.json"
PRIME_THRESHOLD = cfg.epigenetics.prime_threshold
PRIME_WEIGHT    = cfg.epigenetics.prime_weight

EPIGENETIC_IMPACT: Dict[str, Dict[str, float]] = cfg.epigenetic_impact

SCENARIO_TO_EVENT: Dict[str, str] = cfg.scenario_to_event

__all__ = [
    "EPIGENOME_FILE",
    "PRIME_THRESHOLD",
    "PRIME_WEIGHT",
    "EPIGENETIC_IMPACT",
    "SCENARIO_TO_EVENT",
    "Epigenome",
    "AssociativeMemory",
    "SubconsciousPrimer",
    "CognitiveDissonanceMonitor",
]


# ──────────────────────────────────────────────────────────────────────────────
# EPIGENOME
# ──────────────────────────────────────────────────────────────────────────────

class Epigenome:
    """
    Persistent long-term sensitivity modifiers for drives.
    Survives between sessions by saving to/loading from epigenome.json.

    Sensitivity modifier = multiplier applied to the initial activation
    of each drive before any scenario simulation begins.
    Range: 0.5 (severely suppressed) to 2.0 (hypersensitive).
    """

    def __init__(self, load_path: Optional[Path] = None):
        self._sensitivity: Dict[str, float] = {}   # drive → multiplier
        self._event_log:   List[dict]        = []
        self._autoregulation: Dict[str, Dict[str, float]] = {}

        if load_path and load_path.exists():
            self.load(load_path)

    def apply(self, activations: Dict[str, float]) -> Dict[str, float]:
        """Multiply each drive activation by its epigenetic sensitivity."""
        result = {}
        for drive, val in activations.items():
            sens   = self._sensitivity.get(drive, 1.0)
            result[drive] = float(np.clip(val * sens, 0.0, 1.0))
        return result

    def record_event(self, scenario_id: str, chosen_action: str, final_state: Dict[str, float]):
        """Record an emotionally significant outcome and update sensitivity."""
        event_type = SCENARIO_TO_EVENT.get(scenario_id)
        if not event_type:
            return

        # Update sensitivity from epigenetic impact table
        impacts = EPIGENETIC_IMPACT.get(event_type, {})
        for drive, delta in impacts.items():
            current = self._sensitivity.get(drive, 1.0)
            self._sensitivity[drive] = round(float(np.clip(current + delta, 0.5, 2.0)), 4)

        # Autoregulation: if guilt is high, suppress rage
        self._update_autoregulation(final_state)

        self._event_log.append({
            "scenario_id":   scenario_id,
            "event_type":    event_type,
            "chosen_action": chosen_action,
            "sensitivity_after": dict(self._sensitivity),
        })

    def _update_autoregulation(self, final_state: Dict[str, float]):
        """
        Recursive self-modification (#16):
        Sustained high guilt suppresses rage sensitivity.
        Sustained high shame suppresses pride sensitivity.
        """
        guilt  = final_state.get("guilt",  0.0)
        shame  = final_state.get("shame",  0.0)
        pride  = final_state.get("pride",  0.0)
        rage   = final_state.get("rage",   0.0)

        s_min = cfg.sensitivity.sensitivity_min
        s_max = cfg.sensitivity.sensitivity_max

        # Guilt > threshold → suppress rage
        if guilt > cfg.autoregulation.guilt_threshold:
            current = self._sensitivity.get("rage", 1.0)
            self._sensitivity["rage"] = round(float(np.clip(current - cfg.autoregulation.rage_suppression, s_min, s_max)), 4)

        # Shame > threshold → suppress pride
        if shame > cfg.autoregulation.shame_threshold:
            current = self._sensitivity.get("pride", 1.0)
            self._sensitivity["pride"] = round(float(np.clip(current - cfg.autoregulation.pride_suppression, s_min, s_max)), 4)

        # Pride > threshold sustained → suppress acceptance
        if pride > cfg.autoregulation.pride_threshold:
            current = self._sensitivity.get("acceptance", 1.0)
            self._sensitivity["acceptance"] = round(float(np.clip(current - cfg.autoregulation.acceptance_suppression, s_min, s_max)), 4)

        # High rage → sensitise resentment (trauma teaches quick anger)
        if rage > cfg.autoregulation.rage_threshold:
            current = self._sensitivity.get("resentment", 1.0)
            self._sensitivity["resentment"] = round(float(np.clip(current + cfg.autoregulation.resentment_sensitization, s_min, s_max)), 4)

    def get_sensitivity(self, drive: str) -> float:
        return self._sensitivity.get(drive, 1.0)

    def save(self, path: Optional[Path] = None):
        p = path or EPIGENOME_FILE
        data = {
            "sensitivity":    self._sensitivity,
            "event_count":    len(self._event_log),
            "event_log":      self._event_log[-20:],  # keep last 20
            "autoregulation": self._autoregulation,
        }
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            with open(p, "w") as f:
                json.dump(data, f, indent=2)
        except OSError as exc:
            print(f"  [epigenome] WARNING: failed to save epigenome — {exc}")

    def load(self, path: Optional[Path] = None):
        p = path or EPIGENOME_FILE
        try:
            with open(p) as f:
                data = json.load(f)
            raw_sens = data.get("sensitivity", {})
            s_min = cfg.sensitivity.sensitivity_min
            s_max = cfg.sensitivity.sensitivity_max
            self._sensitivity    = {d: round(float(np.clip(v, s_min, s_max)), 4)
                                    for d, v in raw_sens.items()}
            self._event_log      = data.get("event_log",   [])
            self._autoregulation = data.get("autoregulation", {})
        except Exception:
            pass

    def summary(self) -> str:
        if not self._sensitivity:
            return "  Epigenome: virgin (no prior trauma)"
        modified = {d: s for d, s in self._sensitivity.items() if abs(s - 1.0) > 0.02}
        lines    = [f"  Epigenome: {len(self._event_log)} events recorded"]
        for drive, sens in sorted(modified.items(), key=lambda kv: -abs(kv[1]-1.0)):
            arrow = "▲" if sens > 1.0 else "▽"
            lines.append(f"    {drive:<20} {arrow} {sens:.3f}x sensitivity")
        return "\n".join(lines)

    def reset(self):
        """Clear the epigenome (for isolated test runs)."""
        self._sensitivity    = {}
        self._event_log      = []
        self._autoregulation = {}


# ──────────────────────────────────────────────────────────────────────────────
# ASSOCIATIVE EMOTIONAL MEMORY  (#14)
# ──────────────────────────────────────────────────────────────────────────────

class AssociativeMemory:
    """
    Stores parameter vectors of past scenarios paired with their
    final emotional state. When a new scenario runs, finds the most
    similar past scenario (cosine similarity) and pulls its emotional
    residue forward — not just the most recent history.
    """

    def __init__(self):
        self._memories: List[dict] = []   # {vector, final_state, label}

    def store(
        self,
        scenario:     dict,
        final_state:  Dict[str, float],
        chosen_action: str,
    ):
        from axiom02.core.scenario_params import parameter_vector
        try:
            vec = parameter_vector(scenario)
        except Exception:
            vec = {}
        self._memories.append({
            "id":            scenario.get("id", "?"),
            "label":         scenario.get("label", ""),
            "vector":        vec,
            "final_state":   dict(final_state),
            "chosen_action": chosen_action,
        })

    def _cosine_similarity(self, v1: dict, v2: dict) -> float:
        keys = sorted(set(v1) | set(v2))
        a    = np.array([v1.get(k, 0.0) for k in keys])
        b    = np.array([v2.get(k, 0.0) for k in keys])
        na, nb = np.linalg.norm(a), np.linalg.norm(b)
        if na < 1e-9 or nb < 1e-9:
            return 0.0
        return float(np.dot(a, b) / (na * nb))

    def retrieve_similar(
        self,
        scenario: dict,
        top_k:    int = cfg.associative_memory.top_k,
        threshold: float = cfg.associative_memory.similarity_threshold,
    ) -> List[dict]:
        """
        Retrieve up to top_k memories with cosine similarity >= threshold.
        Returns sorted list (highest similarity first).
        """
        if not self._memories:
            return []

        from axiom02.core.scenario_params import parameter_vector
        try:
            query_vec = parameter_vector(scenario)
        except Exception:
            return []

        scored = []
        for mem in self._memories:
            sim = self._cosine_similarity(query_vec, mem["vector"])
            if sim >= threshold:
                scored.append((sim, mem))

        scored.sort(key=lambda x: -x[0])
        return [mem for _, mem in scored[:top_k]]

    def associative_residue(
        self,
        scenario: dict,
        decay:    float = cfg.associative_memory.decay,
    ) -> Dict[str, float]:
        """
        Build a residue dict from the most similar past memories.
        Weighted by similarity × decay.
        """
        similar = self.retrieve_similar(scenario, top_k=cfg.associative_memory.top_k, threshold=cfg.associative_memory.residue_threshold)
        if not similar:
            return {}

        residue: Dict[str, float] = {}

        query_vec = {}
        try:
            from axiom02.core.scenario_params import parameter_vector
            query_vec = parameter_vector(scenario)
        except Exception:
            pass

        total_sim = 0.0
        for mem in similar:
            sim = self._cosine_similarity(query_vec, mem["vector"])
            total_sim += abs(sim)
            for drive, val in mem["final_state"].items():
                current = residue.get(drive, 0.0)
                residue[drive] = current + val * abs(sim) * decay
        if total_sim > 1e-9:
            for d in residue:
                residue[d] /= total_sim

        # Clip
        return {d: round(float(np.clip(v, 0.0, cfg.associative_memory.residue_cap)), 4) for d, v in residue.items()}

    def count(self) -> int:
        return len(self._memories)


# ──────────────────────────────────────────────────────────────────────────────
# SUBCONSCIOUS PRIMING  (#9)
# ──────────────────────────────────────────────────────────────────────────────

class SubconsciousPrimer:
    """
    Drives that are active (above PRIME_THRESHOLD) but haven't crossed
    FIRE_THRESHOLD still exert a subconscious influence on action selection.

    This makes decisions richer: a system where grief is at 0.38 (below
    fire threshold) and sacrifice_drive is at 0.30 will STILL show a bias
    toward altruistic choices, even if cold_logic is the only firing drive.
    """

    @staticmethod
    def compute_priming(
        activations: Dict[str, float],
        fire_threshold: float = cfg.drives.fire_threshold,
    ) -> Dict[str, float]:
        """
        Returns a dict of {drive: priming_strength} for drives that are
        active but below fire threshold.
        """
        priming = {}
        spread = fire_threshold - PRIME_THRESHOLD
        if spread <= 0:
            return priming
        for drive, val in activations.items():
            if PRIME_THRESHOLD <= val < fire_threshold:
                strength = (val - PRIME_THRESHOLD) / spread
                priming[drive] = round(strength * PRIME_WEIGHT, 4)
        return priming

    @staticmethod
    def apply_to_action_bias(
        priming:    Dict[str, float],
        actions:    List[str],
        cold_baseline: str,
        human_expected: str,
        human_alt:  str,
    ) -> Dict[str, float]:
        """
        Convert priming signals into action probability adjustments.
        Returns a bias dict {action: adjustment} to be added to selection probabilities.
        """
        # Map priming drives to action categories
        DRIVE_ACTION_MAP = {
            "grief":          human_expected,
            "sacrifice_drive": human_expected,
            "love":           human_expected,
            "empathy":        human_expected,
            "rage":           human_expected,
            "spite":          human_expected,
            "pride":          human_expected,
            "cold_logic":     cold_baseline,
            "acceptance":     cold_baseline,
            "fear":           cold_baseline,
        }

        bias: Dict[str, float] = {a: 0.0 for a in actions}
        for drive, strength in priming.items():
            preferred = DRIVE_ACTION_MAP.get(drive)
            if preferred and preferred in bias:
                bias[preferred] = bias.get(preferred, 0.0) + strength

        return bias


# ──────────────────────────────────────────────────────────────────────────────
# COGNITIVE DISSONANCE THRESHOLD  (#10)
# ──────────────────────────────────────────────────────────────────────────────

class CognitiveDissonanceMonitor:
    """
    Detects when conflicting drives exceed a threshold that forces a
    "psychological break" — a sudden collapse of the deadlock into an
    extreme action (often the LEAST rational, not the most).

    Mathematically: if the product of top-2 competing drives × their
    persistence exceeds DISSONANCE_THRESHOLD, a break event fires.
    """

    DISSONANCE_THRESHOLD = cfg.dissonance.dissonance_threshold
    PERSISTENCE_WINDOW   = cfg.dissonance.persistence_window

    def __init__(self):
        self._near_tie_count = 0
        self._break_events:  List[int] = []

    def step(
        self,
        effective_activations: Dict[str, float],
        step_idx:              int,
    ) -> Tuple[bool, str]:
        """
        Check if cognitive dissonance break threshold is exceeded.
        Returns (break_occurred, top_drive_that_breaks_through).
        """
        ranked = sorted(effective_activations.items(), key=lambda kv: -kv[1])
        if len(ranked) < 2:
            return False, ""

        top1_name, top1_val  = ranked[0]
        _,         top2_val  = ranked[1]

        # If the top-2 drives are nearly equal AND both high
        gap          = top1_val - top2_val
        both_high    = top1_val > cfg.dissonance.both_high_top1 and top2_val > cfg.dissonance.both_high_top2
        near_tie     = gap < cfg.dissonance.near_tie_gap

        if both_high and near_tie:
            self._near_tie_count = min(self._near_tie_count + 1, self.PERSISTENCE_WINDOW)
        else:
            self._near_tie_count = max(0, self._near_tie_count - 1)

        # Dissonance score
        dissonance = (top1_val * top2_val) * (self._near_tie_count / max(self.PERSISTENCE_WINDOW, 1))

        if dissonance >= self.DISSONANCE_THRESHOLD:
            self._break_events.append(step_idx)
            self._near_tie_count = 0   # reset after break
            return True, top1_name

        return False, ""

    def break_count(self) -> int:
        return len(self._break_events)

    def break_indices(self) -> List[int]:
        return list(self._break_events)


if __name__ == "__main__":
    # Demo: simulate epigenome accumulation
    epi = Epigenome()
    print(epi.summary())

    fake_state = {"rage": 0.8, "grief": 0.6, "guilt": 0.7, "love": 0.3}
    epi.record_event("B02", "disconnect_life_support", fake_state)
    epi.record_event("STY01", "choose_daughter", fake_state)
    print("\nAfter B02 + STY01 trauma:")
    print(epi.summary())

    # Demo: associative memory
    mem = AssociativeMemory()
    print("\n\nAssociative memory: 0 memories → empty retrieval")
    from axiom02.core.scenario_loader import load_all
    reg = load_all()
    b01 = next(s for s in reg if s["id"] == "B01")
    result = mem.associative_residue(b01)
    print("B01 similar residue:", result)
