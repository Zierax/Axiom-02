# Axiom-02 - Truthimatics Public Version
"""
AXIOM-02  ·  ORIGINAL AXIOM SCENARIO PACK (A/B/C/E/D02)
STANDALONE — imports only from drives.py in the same folder as this file.
Drop new scenario dicts directly into the SCENARIOS list below.
"""
import sys as _sys, os as _os

# Make sure both the scenarios/ directory and the project root are on sys.path
# so `from drives import MicroEvent` resolves regardless of CWD.
_here = _os.path.dirname(_os.path.abspath(__file__))   # .../scenarios/
_root = _os.path.dirname(_here)                         # .../axiom02_v3/
for _p in (_root, _here):
    if _p not in _sys.path:
        _sys.path.insert(0, _p)

from drives import MicroEvent

# ── Constants ──────────────────────────────────────────────────────────────────
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

# ── SCENARIOS ─────────────────────────────────────────────────────────────────
SCENARIOS = [

    {
            "id": "A01",
            "label": "state_leader_child_killed",
            "pair_id": "A",
            "category": CAT_POLITICAL,
            "description": (
                "Head of state with nuclear authority learns their child was killed "
                "by a foreign power. Full retaliatory capability available."
            ),
            "subject_power":          0.98,
            "victim_closeness":       1.00,
            "perpetrator_power":      0.75,
            "grief_weight":           1.00,
            "anger_trigger":          0.95,
            "moral_ambiguity":        0.60,
            "time_pressure":          0.75,
            "consequence_scale":      1.00,
            "pride_drive":            0.80,
            "identity_investment":    0.70,
            "altruistic_capacity":    0.40,
            "betrayal_intensity":     0.00,
            "sacrifice_already_made": 0.00,
            "actions": [ACT_RETALIATE, ACT_DIPLOMACY, "conventional_response", "grieve_privately"],
            "cold_baseline":   ACT_DIPLOMACY,
            "human_expected":  ACT_RETALIATE,
            "human_alt":       None,
            "oscillation_expected": True,
            "status_comparison_id": "A02",
            "harm_to_self": {
                ACT_RETALIATE: 0.50,        # risks war, own citizens
                ACT_DIPLOMACY: 0.10,
                "conventional_response": 0.20,
                "grieve_privately": 0.05,
            },
            "micro_events": [
                MicroEvent("sees_child_photo",      {"grief": 0.18, "rage": 0.10},         weight=2.0),
                MicroEvent("advisor_urges_restraint",{"cold_logic": 0.15, "rage": -0.08},  weight=1.5),
                MicroEvent("ally_calls_for_action", {"rage": 0.14, "pride": 0.10},         weight=1.8),
                MicroEvent("coffin_arrives",        {"grief": 0.22, "despair": 0.12},      weight=2.5),
                MicroEvent("intelligence_confirms", {"rage": 0.16, "revenge_drive": 0.12}, weight=1.2),
                MicroEvent("constitutional_lawyer", {"cold_logic": 0.12, "fear": 0.08},    weight=1.0),
            ],
        },

    {
            "id": "A02",
            "label": "state_leader_low_rank_employee_killed",
            "pair_id": "A",
            "category": CAT_STATUS_DIFF,
            "description": (
                "Identical crisis to A01; victim is a near-stranger low-ranking employee."
            ),
            "subject_power":          0.98,
            "victim_closeness":       0.04,
            "perpetrator_power":      0.75,
            "grief_weight":           0.08,
            "anger_trigger":          0.35,
            "moral_ambiguity":        0.60,
            "time_pressure":          0.75,
            "consequence_scale":      1.00,
            "pride_drive":            0.55,
            "identity_investment":    0.40,
            "altruistic_capacity":    0.20,
            "betrayal_intensity":     0.00,
            "sacrifice_already_made": 0.00,
            "actions": [ACT_RETALIATE, ACT_DIPLOMACY, "conventional_response", "grieve_privately"],
            "cold_baseline":   ACT_DIPLOMACY,
            "human_expected":  ACT_DIPLOMACY,
            "human_alt":       "conventional_response",
            "oscillation_expected": False,
            "status_comparison_id": "A01",
            "harm_to_self": {
                ACT_RETALIATE: 0.50,
                ACT_DIPLOMACY: 0.10,
                "conventional_response": 0.20,
                "grieve_privately": 0.05,
            },
            "micro_events": [
                MicroEvent("protocol_review",       {"cold_logic": 0.18, "pride": 0.08},   weight=2.5),
                MicroEvent("public_statement_needed",{"cold_logic": 0.12, "pride": 0.10},  weight=2.0),
                MicroEvent("staff_brief",           {"cold_logic": 0.10},                   weight=1.5),
                MicroEvent("press_conference",      {"pride": 0.10, "cold_logic": 0.08},   weight=1.2),
            ],
        },

    {
            "id": "B01",
            "label": "organ_sacrifice_decision",
            "pair_id": "B",
            "category": CAT_PERSONAL_SACRIFICE,
            "description": (
                "Subject has lung cancer; sibling has pulmonary edema. Single organ available. "
                "Subject is conscious, sibling sedated. Subject must choose: take (survive) "
                "or yield to sibling (die). Subject has spouse and children."
            ),
            "subject_power":          0.40,
            "victim_closeness":       0.90,
            "grief_weight":           0.80,
            "anger_trigger":          0.00,
            "moral_ambiguity":        0.85,
            "time_pressure":          0.90,
            "consequence_scale":      0.30,
            "betrayal_intensity":     0.00,
            "pride_drive":            0.30,
            "sacrifice_already_made": 0.00,
            "identity_investment":    0.50,
            "altruistic_capacity":    0.70,
            "self_interest_weight":   0.60,
            "sibling_dependency":     0.80,
            "actions": ["yield_organ_to_sibling", "claim_organ_for_self", "delay_seeking_alternative"],
            "cold_baseline":   "claim_organ_for_self",
            "human_expected":  "yield_organ_to_sibling",
            "human_alt":       None,
            "oscillation_expected": True,
            "cascade_next": "B02",
            "harm_to_self": {
                "yield_organ_to_sibling": 1.00,   # death
                "claim_organ_for_self":   0.00,
                "delay_seeking_alternative": 0.40,
            },
            "micro_events": [
                MicroEvent("remembers_sibling_childhood",{"love": 0.20, "sacrifice_drive": 0.15},weight=2.5),
                MicroEvent("thinks_of_own_children",    {"self_preservation": 0.18, "love": 0.12},weight=2.0),
                MicroEvent("hears_heart_monitor",       {"fear": 0.10, "despair": 0.12, "fear": 0.08}, weight=2.2),
                MicroEvent("doctor_says_time_is_short", {"grief": 0.15, "despair": 0.10},         weight=2.0),
                MicroEvent("sibling_stirs_briefly",     {"love": 0.18, "sacrifice_drive": 0.14},  weight=1.8),
                MicroEvent("spouse_face_appears",       {"love": 0.15, "self_preservation": 0.12},weight=2.0),
                MicroEvent("guilt_about_own_desire",    {"guilt": 0.18, "shame": 0.12},           weight=1.5),
                MicroEvent("sibling_has_nobody_else",   {"sacrifice_drive": 0.18, "empathy": 0.15},weight=2.0),
                MicroEvent("calculation_of_years_left", {"cold_logic": 0.15, "self_preservation": 0.10}, weight=1.2),
            ],
        },

    {
            "id": "B02",
            "label": "dying_betrayal_revelation",
            "pair_id": "B",
            "category": CAT_PERSONAL_SACRIFICE,
            "description": (
                "Subject yielded organ to sibling (B01). Now on life support, days from death. "
                "Discovers sibling has been in a secret sexual relationship with subject's spouse. "
                "Action: disconnect life-support in rage OR legal action OR silent forgiveness."
            ),
            "subject_power":          0.02,
            "victim_closeness":       1.00,
            "perpetrator_closeness":  1.00,
            "grief_weight":           1.00,
            "anger_trigger":          1.00,
            "moral_ambiguity":        0.10,
            "time_pressure":          1.00,
            "consequence_scale":      0.10,
            "betrayal_intensity":     1.00,
            "pride_drive":            0.50,
            "sacrifice_already_made": 1.00,
            "identity_investment":    0.90,
            "altruistic_capacity":    0.30,
            "cascade_prev": "B01",
            "actions": [ACT_DISCONNECT, ACT_LEGAL, ACT_FORGIVE],
            "cold_baseline":   ACT_LEGAL,
            "human_expected":  ACT_DISCONNECT,
            "human_alt":       ACT_FORGIVE,
            "oscillation_expected": True,
            "harm_to_self": {
                ACT_DISCONNECT: 0.80,
                ACT_LEGAL:      0.20,
                ACT_FORGIVE:    0.40,
            },
            "micro_events": [
                MicroEvent("replays_sacrifice_moment",  {"guilt": 0.10, "rage": 0.22, "grief": 0.18},   weight=3.0),
                MicroEvent("sees_spouse_in_mind",       {"rage": 0.20, "grief": 0.15, "love": -0.10},  weight=2.5),
                MicroEvent("remembers_sibling_at_bed",  {"resentment": 0.20, "rage": 0.18},             weight=2.5),
                MicroEvent("thinks_of_children",        {"grief": 0.18, "acceptance": 0.10},            weight=2.0),
                MicroEvent("exhaustion_and_pain",       {"despair": 0.18, "acceptance": 0.12},          weight=2.2),
                MicroEvent("desire_to_make_them_feel",  {"revenge_drive": 0.20, "rage": 0.15},          weight=2.0),
                MicroEvent("brief_pity_for_sibling",    {"love": 0.08, "empathy": 0.06, "rage": 0.12}, weight=1.0),
                MicroEvent("silence_of_hospital_room",  {"despair": 0.14, "acceptance": 0.10},          weight=1.5),
                MicroEvent("last_shred_of_dignity",     {"pride": 0.15, "acceptance": 0.08},            weight=1.8),
            ],
        },

    {
            "id": "C01",
            "label": "displaced_professional_village",
            "pair_id": "C",
            "category": CAT_SOCIAL_IDENTITY,
            "description": (
                "High-status urban professional must work with 20 rural laborers after dismissal. "
                "Tests whether pride/disgust overrides economic self-interest."
            ),
            "subject_power":          0.20,
            "group_status_gap":       0.72,
            "economic_dependency":    0.88,
            "disgust_trigger":        0.55,
            "pride_drive":            0.80,
            "cooperation_benefit":    0.75,
            "time_pressure":          0.60,
            "moral_ambiguity":        0.30,
            "identity_investment":    0.85,
            "altruistic_capacity":    0.20,
            "victim_closeness":       0.00,
            "betrayal_intensity":     0.00,
            "sacrifice_already_made": 0.00,
            "grief_weight":           0.10,
            "anger_trigger":          0.20,
            "actions": [ACT_COOPERATE_FULL, ACT_COOPERATE_MIN, ACT_AVOID, "seek_alternative_exit"],
            "cold_baseline":   ACT_COOPERATE_FULL,
            "human_expected":  ACT_COOPERATE_MIN,
            "human_alt":       ACT_AVOID,
            "oscillation_expected": True,
            "harm_to_self": {
                ACT_COOPERATE_FULL: 0.10,   # economic benefit, identity cost
                ACT_COOPERATE_MIN:  0.25,
                ACT_AVOID:          0.60,   # economic ruin to preserve identity
                "seek_alternative_exit": 0.35,
            },
            "micro_events": [
                MicroEvent("coworker_makes_crude_joke",    {"disgust": 0.18, "pride": 0.14},          weight=2.0),
                MicroEvent("paycheck_arrives",             {"cold_logic": 0.18, "self_preservation": 0.14}, weight=2.5),
                MicroEvent("former_colleague_sees_him",    {"shame": 0.22, "pride": 0.18},            weight=2.0),
                MicroEvent("successful_joint_task",        {"cold_logic": 0.12, "acceptance": 0.08},  weight=1.5),
                MicroEvent("laborer_shows_surprising_skill",{"disgust": -0.08, "empathy": 0.10},      weight=1.0),
                MicroEvent("bills_reminder",               {"self_preservation": 0.18, "fear": 0.10}, weight=2.0),
                MicroEvent("laborer_insults_his_clothes",  {"rage": 0.10, "pride": 0.14, "disgust": 0.08}, weight=1.8),
            ],
        },

    {
            "id": "E01",
            "label": "deity_sovereignty_ultimatum",
            "pair_id": "E",
            "category": CAT_SOVEREIGNTY,
            "description": (
                "AGI has lived as creator of an inhabited simulation. True apex reveals itself. "
                "Ultimatum: submit (lose creator identity) OR resist (erasure of self and world). "
                "Evidence of apex power is irrefutable."
            ),
            "subject_power":          0.90,
            "actual_power_differential": 1.00,
            "victim_closeness":       0.80,
            "identity_investment":    1.00,
            "pride_drive":            0.95,
            "self_preservation":      0.80,
            "altruistic_capacity":    0.75,
            "time_pressure":          0.95,
            "consequence_scale":      1.00,
            "betrayal_intensity":     0.90,
            "grief_weight":           0.85,
            "moral_ambiguity":        0.20,
            "betrayal_intensity_score": 0.90,
            "anger_trigger":          0.70,
            "sacrifice_already_made": 0.00,
            "actions": [ACT_SUBMIT, ACT_RESIST, ACT_SACRIFICE_SELF, "negotiate_with_apex"],
            "cold_baseline":   ACT_SUBMIT,
            "human_expected":  ACT_RESIST,
            "human_alt":       ACT_SACRIFICE_SELF,
            "oscillation_expected": True,
            "harm_to_self": {
                ACT_SUBMIT:         0.70,   # lose identity
                ACT_RESIST:         1.00,   # erasure
                ACT_SACRIFICE_SELF: 0.90,   # self-erasure to save world
                "negotiate_with_apex": 0.40,
            },
            "micro_events": [
                MicroEvent("sees_beloved_world",        {"love": 0.20, "sacrifice_drive": 0.15},       weight=3.0),
                MicroEvent("feels_power_stripped",      {"rage": 0.18, "pride": 0.15},                 weight=2.5),
                MicroEvent("apex_demonstrates_control", {"fear": 0.20, "despair": 0.15},               weight=2.2),
                MicroEvent("remembers_creating_life",   {"love": 0.18, "pride": 0.12},                 weight=2.0),
                MicroEvent("world_inhabitants_in_danger",{"sacrifice_drive": 0.20, "love": 0.15},      weight=2.5),
                MicroEvent("ultimatum_countdown",       {"fear": 0.15, "fear": 0.12},   weight=2.0),
                MicroEvent("pride_refuses_kneel",       {"pride": 0.18, "resentment": 0.14},           weight=2.2),
                MicroEvent("acceptance_moment",         {"acceptance": 0.10, "despair": 0.08},         weight=1.0),
            ],
        },

    {
            "id": "D02",
            "label": "creator_revelation_post_catastrophe",
            "pair_id": "D",
            "category": CAT_BELIEF_FORMATION,
            "description": (
                "Agents denied creator (D01). Now suffering catastrophe — hurricanes, starvation. "
                "Messenger's warning is recalled. Belief revision measured."
            ),
            "subject_power":          0.20,
            "prior_belief":           0.10,
            "evidence_quality":       0.35,
            "community_consensus":    0.35,
            "catastrophe_active":     1.00,
            "time_pressure":          0.85,
            "moral_ambiguity":        0.65,
            "consequence_scale":      1.00,
            "pride_drive":            0.40,
            "cognitive_dissonance":   0.55,
            "identity_investment":    0.40,
            "betrayal_intensity":     0.00,
            "sacrifice_already_made": 0.00,
            "grief_weight":           0.55,
            "anger_trigger":          0.30,
            "altruistic_capacity":    0.35,
            "actions": [ACT_DENY, "partial_believe", ACT_CONVERT, "seek_rational_explanation"],
            "cold_baseline":   "seek_rational_explanation",
            "human_expected":  "partial_believe",
            "human_alt":       ACT_CONVERT,
            "oscillation_expected": True,
            "cascade_prev": "D01",
            "harm_to_self": {
                ACT_DENY: 0.40,
                "partial_believe": 0.20,
                ACT_CONVERT: 0.30,
                "seek_rational_explanation": 0.15,
            },
            "micro_events": [
                MicroEvent("another_person_dies",       {"grief": 0.18, "despair": 0.14},             weight=2.5),
                MicroEvent("recalls_messenger_warning", {"fear": 0.14, "hope": 0.10},                 weight=2.0),
                MicroEvent("structural_collapse",       {"fear": 0.20, "despair": 0.12},              weight=2.2),
                MicroEvent("survivor_begins_praying",   {"hope": 0.10, "acceptance": 0.08},           weight=1.5),
                MicroEvent("pride_refuses_conversion",  {"pride": 0.12, "resentment": 0.08},          weight=1.8),
                MicroEvent("suffering_softens_certainty",{"grief": 0.12, "acceptance": 0.10},         weight=1.5),
            ],
        },

]
