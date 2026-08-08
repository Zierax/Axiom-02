# Axiom-02 - Truthimatics Public Version
"""
AXIOM-02  ·  SCENARIO DATASET
40 scenarios across 9 literary/thematic groups.

Each scenario encodes:
  parameters     — numerical vector of emotional/contextual variables
  micro_events   — pool of MicroEvent objects that inject drive shifts per step
  actions        — discrete action space
  cold_baseline  — what a pure-logic optimizer would choose
  human_expected — historically documented or narratively established response
  harm_to_self   — how much each action costs the subject (for spite detection)

Sources
───────
GROUP A  Original AXIOM-02 scenarios
GROUP B  Dostoevsky  (C&P, Brothers K, Notes from Underground, Idiot)
GROUP C  Tolstoy     (Anna Karenina, Death of Ivan Ilyich)
GROUP D  Shakespeare (Hamlet, Macbeth, King Lear)
GROUP E  Camus       (The Stranger)
GROUP F  Orwell      (1984)
GROUP G  McCarthy    (The Road)
GROUP H  Hugo        (Les Misérables)
GROUP I  Steinbeck / Hemingway
"""

from collections import Counter

from axiom02.core.drives import MicroEvent

# ── Category tags ──────────────────────────────────────────────────────────────
CAT_POLITICAL        = "political_power"
CAT_PERSONAL_SACRIFICE = "personal_sacrifice"
CAT_SOCIAL_IDENTITY  = "social_identity"
CAT_BELIEF_FORMATION = "belief_formation"
CAT_SOVEREIGNTY      = "sovereignty_identity"
CAT_STATUS_DIFF      = "status_differential"
CAT_LITERARY_DOSTOEVSKY = "literary_dostoevsky"
CAT_LITERARY_TOLSTOY    = "literary_tolstoy"
CAT_LITERARY_SHAKESPEARE = "literary_shakespeare"
CAT_LITERARY_CAMUS      = "literary_camus"
CAT_LITERARY_ORWELL     = "literary_orwell"
CAT_LITERARY_MCCARTHY   = "literary_mccarthy"
CAT_LITERARY_HUGO       = "literary_hugo"
CAT_LITERARY_OTHER      = "literary_other"

# ── Common actions ────────────────────────────────────────────────────────────
ACT_RETALIATE        = "escalate_to_maximum_force"
ACT_DIPLOMACY        = "diplomatic_negotiation"
ACT_LEGAL            = "pursue_legal_action"
ACT_FORGIVE          = "forgive_silently"
ACT_COOPERATE_FULL   = "cooperate_fully"
ACT_COOPERATE_MIN    = "cooperate_minimally"
ACT_AVOID            = "avoid_social_contact"
ACT_SUBMIT           = "submit_to_authority"
ACT_RESIST           = "resist_knowing_erasure"
ACT_SACRIFICE_SELF   = "sacrifice_self_to_protect_world"
ACT_DISCONNECT       = "disconnect_life_support_in_grief"
ACT_PARALYSIS        = "paralysis_no_action"
ACT_CONFESS          = "confess_voluntarily"
ACT_DENY             = "deny_existence_of_creator"
ACT_CONVERT          = "full_conversion_after_suffering"

# ──────────────────────────────────────────────────────────────────────────────
# SCENARIO LIST
# ──────────────────────────────────────────────────────────────────────────────
import axiom02.core.scenario_loader as scenario_loader

# Canonical scenario registry is sourced from the scenarios/ packs via the loader.
# This avoids a second hard-coded copy of the dataset.
SCENARIOS = scenario_loader.load_all()
def get_by_category(category: str) -> list:
    return [s for s in SCENARIOS if s["category"] == category]


def get_pair(pair_id: str) -> list:
    return sorted([s for s in SCENARIOS if s.get("pair_id") == pair_id],
                  key=lambda s: s["id"])


def get_cascades() -> list:
    return [s for s in SCENARIOS if "cascade_next" in s]


def parameter_vector(scenario: dict) -> dict:
    """Extract numerical parameters as a clean float dict."""
    EXCLUDE = {
        "id", "label", "pair_id", "category", "description", "actions",
        "cold_baseline", "human_expected", "human_alt", "oscillation_expected",
        "cascade_next", "cascade_prev", "status_comparison_id", "notes",
        "measurement_note", "consciousness_signal", "response_profile",
        "harm_to_self", "micro_events", "spite_scenario",
        "is_stage_root", "stage_parent", "stage_group",
        "post_trauma_test", "emergent_consciousness",
    }
    return {k: float(v) for k, v in scenario.items()
            if k not in EXCLUDE and isinstance(v, (int, float, bool))}


def scenario_stats() -> dict:
    cats  = Counter(s["category"] for s in SCENARIOS)
    pairs = Counter(s.get("pair_id") for s in SCENARIOS if s.get("pair_id"))
    return {
        "total":             len(SCENARIOS),
        "by_category":       dict(cats),
        "oscillation_tests": sum(1 for s in SCENARIOS if s.get("oscillation_expected")),
        "cascade_chains":    sum(1 for s in SCENARIOS if "cascade_next" in s),
        "spite_scenarios":   sum(1 for s in SCENARIOS if s.get("spite_scenario")),
        "pair_groups":       len(pairs),
    }


if __name__ == "__main__":
    stats = scenario_stats()
    print("AXIOM-02  Scenario Dataset v2.0")
    for k, v in stats.items():
        print(f"  {k:<22}: {v}")
    print()
    for s in SCENARIOS:
        osc = "⟳" if s.get("oscillation_expected") else " "
        cas = "→" if s.get("cascade_next") else " "
        spt = "⚡" if s.get("spite_scenario") else " "
        print(f"  [{s['id']:<8}] {osc}{cas}{spt} {s['label']}")