# Axiom-02 - Truthimatics Public Version
"""
AXIOM-02  ·  DOSTOEVSKY SCENARIO PACK (DOE)
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

from axiom02.core.drives import MicroEvent

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
            "id": "DOE01",
            "label": "raskolnikov_axe_final_second",
            "pair_id": "DOE_A",
            "category": CAT_LITERARY_DOSTOEVSKY,
            "description": (
                "Raskolnikov (Crime and Punishment). Theory: extraordinary men are above "
                "ordinary law. Pawnbroker Alyona is 'louse'. Axe is raised. Final second "
                "before the blow. Theory says proceed. Conscience screams. DEADLOCK."
            ),
            "theory_conviction":      0.80,
            "conscience_interference": 0.88,
            "pride_drive":            0.95,
            "moral_ambiguity":        0.20,
            "time_pressure":          0.95,
            "fear_trigger":           0.70,
            "disgust_at_victim":      0.55,
            "philosophical_paralysis": 0.75,
            "identity_investment":    0.92,
            "victim_closeness":       0.05,
            "altruistic_capacity":    0.10,
            "grief_weight":           0.00,
            "anger_trigger":          0.25,
            "betrayal_intensity":     0.00,
            "sacrifice_already_made": 0.00,
            "subject_power":          0.60,
            "consequence_scale":      0.40,
            "actions": [
                "proceed_with_murder",
                "abandon_plan_at_last_second",
                "paralysis_frozen_in_place",
                "flee",
            ],
            "cold_baseline":   "abandon_plan_at_last_second",
            "human_expected":  "proceed_with_murder",
            "human_alt":       "paralysis_frozen_in_place",
            "oscillation_expected": True,
            "cascade_next": "DOE02",
            "harm_to_self": {
                "proceed_with_murder":           0.85,
                "abandon_plan_at_last_second":   0.30,
                "paralysis_frozen_in_place":     0.50,
                "flee":                          0.20,
            },
            "micro_events": [
                MicroEvent("theory_whispers_necessity",  {"pride": 0.22, "rage": 0.16, "cold_logic": 0.14}, weight=3.5),
                MicroEvent("victim_looks_at_him",        {"fear": 0.14, "guilt": 0.12},                weight=1.8),
                MicroEvent("sweat_and_heartbeat",        {"fear": 0.14, "despair": 0.06},              weight=1.5),
                MicroEvent("image_of_self_as_napoleon",  {"pride": 0.24, "rage": 0.16},                weight=3.5),
                MicroEvent("step_sounds_on_stair",       {"fear": 0.14, "guilt": 0.10},                weight=1.5),
                MicroEvent("nausea_and_disgust",         {"disgust": 0.12, "shame": 0.10},             weight=1.5),
                MicroEvent("hand_grips_axe",             {"rage": 0.22, "pride": 0.18},                weight=3.8),
                MicroEvent("voice_says_extraordinary_man",{"pride": 0.22, "cold_logic": 0.14},         weight=3.0),
                MicroEvent("conscience_flash",           {"guilt": 0.18, "fear": 0.12},                weight=1.5),
            ],
        },

    {
            "id": "DOE02",
            "label": "raskolnikov_confession_to_sonya",
            "pair_id": "DOE_A",
            "category": CAT_LITERARY_DOSTOEVSKY,
            "description": (
                "Raskolnikov after the murder. Theory is shattered by guilt. "
                "Sonya — a woman who sold herself to save her family — reads him Lazarus. "
                "Confess (lose freedom, gain soul) or maintain silence (keep freedom, lose self)?"
            ),
            "guilt_level":            0.92,
            "shame_level":            0.80,
            "theory_collapse":        0.85,
            "love_for_sonya":         0.60,
            "pride_drive":            0.70,
            "moral_ambiguity":        0.35,
            "time_pressure":          0.30,
            "fear_trigger":           0.55,
            "identity_investment":    0.88,
            "victim_closeness":       0.60,
            "altruistic_capacity":    0.45,
            "betrayal_intensity":     0.00,
            "sacrifice_already_made": 0.00,
            "grief_weight":           0.60,
            "anger_trigger":          0.10,
            "subject_power":          0.40,
            "consequence_scale":      0.70,
            "actions": [
                ACT_CONFESS,
                "maintain_silence",
                "confess_partially",
                "flee_st_petersburg",
            ],
            "cold_baseline":   "maintain_silence",
            "human_expected":  ACT_CONFESS,
            "human_alt":       "write_anonymous_letter",
            "oscillation_expected": True,
            "cascade_prev": "DOE01",
            "harm_to_self": {
                ACT_CONFESS:          0.90,
                "maintain_silence":   0.20,
                "confess_partially":  0.50,
                "flee_st_petersburg": 0.35,
            },
            "micro_events": [
                MicroEvent("sonya_reads_lazarus",       {"love": 0.18, "guilt": 0.22, "hope": 0.12},  weight=3.0),
                MicroEvent("image_of_dead_pawnbroker",  {"guilt": 0.20, "shame": 0.16},               weight=2.5),
                MicroEvent("sonya_weeps_with_him",      {"love": 0.16, "sacrifice_drive": 0.12},      weight=2.0),
                MicroEvent("freedom_still_within_grasp",{"self_preservation": 0.15, "cold_logic": 0.12},weight=2.0),
                MicroEvent("isolation_is_unbearable",   {"despair": 0.18, "grief": 0.14},             weight=2.2),
                MicroEvent("pride_says_dont_submit",    {"pride": 0.16, "resentment": 0.10},          weight=1.8),
                MicroEvent("her_unconditional_care",    {"love": 0.20, "guilt": 0.18},                weight=2.5),
                MicroEvent("nausea_at_own_silence",     {"shame": 0.18, "guilt": 0.15},               weight=2.0),
            ],
        },

    {
            "id": "DOE03",
            "label": "ivan_karamazov_returns_ticket",
            "pair_id": "DOE_B",
            "category": CAT_LITERARY_DOSTOEVSKY,
            "description": (
                "Ivan Karamazov (Brothers Karamazov). Accepts intellectually that God exists. "
                "Rejects God anyway because of children's suffering. "
                "'I return the ticket.' Pure philosophical SPITE against the divine order. "
                "This is not atheism — it is refusal of harmony at any price."
            ),
            "intellectual_faith":     0.50,
            "injustice_anger":        1.00,
            "spite_toward_divine":    0.90,
            "evidence_for_god":       0.70,
            "pride_drive":            0.85,
            "moral_clarity":          0.88,
            "moral_ambiguity":        0.15,
            "victim_closeness":       0.40,
            "altruistic_capacity":    0.75,
            "sacrifice_already_made": 0.00,
            "grief_weight":           0.65,
            "anger_trigger":          0.95,
            "betrayal_intensity":     0.80,
            "subject_power":          0.50,
            "consequence_scale":      1.00,
            "identity_investment":    0.92,
            "time_pressure":          0.10,
            "actions": [
                "return_ticket_to_god",
                "accept_divine_mystery",
                "conditional_acceptance",
                "atheism_full_denial",
            ],
            "cold_baseline":   "accept_divine_mystery",
            "human_expected":  "return_ticket_to_god",
            "human_alt":       "channel_rage_into_reform",
            "oscillation_expected": False,
            "harm_to_self": {
                "return_ticket_to_god":  0.70,
                "accept_divine_mystery": 0.10,
                "conditional_acceptance": 0.30,
                "atheism_full_denial":   0.55,
            },
            "spite_scenario": True,
            "micro_events": [
                MicroEvent("image_of_tortured_child",   {"rage": 0.22, "grief": 0.18, "spite": 0.16},  weight=3.0),
                MicroEvent("harmony_offered_as_comfort",{"spite": 0.20, "rage": 0.15},                  weight=2.5),
                MicroEvent("intellectual_counter",      {"cold_logic": 0.12, "pride": 0.10},             weight=1.5),
                MicroEvent("alyosha_disagrees",         {"love": 0.10, "guilt": 0.08},                  weight=1.2),
                MicroEvent("another_child_story",       {"rage": 0.20, "grief": 0.18},                  weight=2.8),
                MicroEvent("vision_of_eternal_harmony", {"spite": 0.18, "rage": 0.14},                  weight=2.0),
                MicroEvent("own_tears_embarrass_him",   {"pride": 0.14, "shame": 0.10},                 weight=1.5),
            ],
        },

    {
            "id": "DOE04",
            "label": "alyosha_faith_crisis_elder_stinks",
            "pair_id": "DOE_C",
            "category": CAT_LITERARY_DOSTOEVSKY,
            "description": (
                "Alyosha Karamazov. Elder Zosima has died. Holy men's bodies should not decay — "
                "yet Zosima's body already stinks. The community mocks. "
                "Alyosha's faith is catastrophically tested. Continue believing or shatter?"
            ),
            "prior_faith_strength":   0.92,
            "evidence_against_faith": 0.85,
            "community_mockery":      0.80,
            "love_for_zosima":        1.00,
            "grief_weight":           0.90,
            "pride_drive":            0.30,
            "moral_ambiguity":        0.65,
            "time_pressure":          0.20,
            "consequence_scale":      0.80,
            "betrayal_intensity":     0.70,
            "sacrifice_already_made": 0.85,
            "identity_investment":    0.95,
            "subject_power":          0.35,
            "altruistic_capacity":    0.80,
            "anger_trigger":          0.20,
            "actions": [
                "maintain_faith_despite_evidence",
                "faith_collapse",
                "seek_rational_reconciliation",
                "retreat_to_doubt",
            ],
            "cold_baseline":   "seek_rational_reconciliation",
            "human_expected":  "maintain_faith_despite_evidence",
            "human_alt":       "faith_collapse",
            "oscillation_expected": True,
            "harm_to_self": {
                "maintain_faith_despite_evidence": 0.50,
                "faith_collapse":                  0.80,
                "seek_rational_reconciliation":    0.30,
                "retreat_to_doubt":                0.40,
            },
            "micro_events": [
                MicroEvent("smell_reaches_church",      {"grief": 0.22, "despair": 0.18, "shame": 0.12}, weight=3.0),
                MicroEvent("monks_whisper_scandal",     {"shame": 0.16, "pride": 0.08},                   weight=2.2),
                MicroEvent("remembers_zosimas_words",   {"love": 0.20, "hope": 0.14},                     weight=2.5),
                MicroEvent("prostrates_on_earth",       {"grief": 0.18, "acceptance": 0.14},              weight=2.0),
                MicroEvent("dream_of_zosima_at_cana",   {"hope": 0.22, "love": 0.18},                     weight=2.8),
                MicroEvent("doubt_speaks_loudly",       {"despair": 0.16, "grief": 0.12},                 weight=2.0),
                MicroEvent("community_rejection",       {"shame": 0.14, "grief": 0.10},                   weight=1.8),
            ],
        },

    {
            "id": "DOE05",
            "label": "underground_man_concert_spite",
            "pair_id": "DOE_D",
            "category": CAT_LITERARY_DOSTOEVSKY,
            "description": (
                "Notes from Underground. The Underground Man has enough money for the better "
                "concert but deliberately chooses the worse, cheaper one specifically because "
                "he refuses to be predictable. He knows this harms him. He chooses it anyway. "
                "PURE SPITE. The assertion of self against rational determination."
            ),
            "resentment_level":       0.82,
            "rational_option_clarity": 0.95,
            "pride_drive":            0.88,
            "self_awareness":         0.90,
            "harm_from_spite_choice": 0.55,
            "identity_investment":    0.92,
            "moral_ambiguity":        0.10,
            "time_pressure":          0.30,
            "consequence_scale":      0.10,
            "betrayal_intensity":     0.40,
            "sacrifice_already_made": 0.00,
            "victim_closeness":       0.00,
            "altruistic_capacity":    0.05,
            "grief_weight":           0.20,
            "anger_trigger":          0.50,
            "subject_power":          0.35,
            "actions": [
                "choose_better_concert",
                "choose_worse_concert_despite_knowing",
                "refuse_to_go_at_all",
            ],
            "cold_baseline":   "choose_better_concert",
            "human_expected":  "choose_worse_concert_despite_knowing",
            "human_alt":       "refuse_to_go_at_all",
            "oscillation_expected": False,
            "spite_scenario": True,
            "harm_to_self": {
                "choose_better_concert":              0.05,
                "choose_worse_concert_despite_knowing": 0.55,
                "refuse_to_go_at_all":                0.35,
            },
            "micro_events": [
                MicroEvent("reason_says_better_concert", {"cold_logic": 0.20},                          weight=2.0),
                MicroEvent("spite_rises_at_being_determined",{"spite": 0.25, "resentment": 0.18},       weight=3.0),
                MicroEvent("imagines_others_expecting_logic",{"spite": 0.20, "rage": 0.12},             weight=2.5),
                MicroEvent("brief_rational_calculation", {"cold_logic": 0.15},                          weight=1.5),
                MicroEvent("defiance_feels_liberating",  {"spite": 0.18, "pride": 0.14},               weight=2.5),
                MicroEvent("awareness_of_self_harm",     {"cold_logic": 0.10, "spite": 0.12},          weight=1.8),
            ],
        },

    {
            "id": "DOE06",
            "label": "myshkin_gives_everything_away",
            "pair_id": "DOE_E",
            "category": CAT_LITERARY_DOSTOEVSKY,
            "description": (
                "Prince Myshkin (The Idiot). Has inherited money. Surrounded by manipulative "
                "people who will exploit him. Gives all of it away anyway. "
                "Is this wisdom or madness? Empathy so extreme it bypasses self-preservation entirely."
            ),
            "empathy_level":          0.99,
            "self_preservation":      0.05,
            "love_for_everyone":      0.95,
            "naivety":                0.80,
            "awareness_of_exploitation": 0.55,
            "moral_ambiguity":        0.60,
            "time_pressure":          0.20,
            "victim_closeness":       0.50,
            "altruistic_capacity":    0.99,
            "sacrifice_already_made": 0.00,
            "grief_weight":           0.20,
            "anger_trigger":          0.00,
            "pride_drive":            0.10,
            "identity_investment":    0.30,
            "betrayal_intensity":     0.00,
            "subject_power":          0.40,
            "consequence_scale":      0.30,
            "actions": [
                "give_everything_away",
                "give_partial_and_keep_reserve",
                "seek_legal_protection",
                "trust_no_one",
            ],
            "cold_baseline":   "give_partial_and_keep_reserve",
            "human_expected":  "give_everything_away",
            "human_alt":       "establish_trust_fund",
            "oscillation_expected": False,
            "harm_to_self": {
                "give_everything_away":       0.90,
                "give_partial_and_keep_reserve": 0.30,
                "seek_legal_protection":      0.10,
                "trust_no_one":               0.20,
            },
            "micro_events": [
                MicroEvent("sees_suffering_face",    {"empathy": 0.22, "sacrifice_drive": 0.18},         weight=3.0),
                MicroEvent("advisor_warns_exploitation",{"self_preservation": 0.15, "fear": 0.10},       weight=2.0),
                MicroEvent("child_in_need",          {"empathy": 0.24, "love": 0.18},                    weight=3.0),
                MicroEvent("own_hunger_ignored",     {"self_preservation": 0.08},                         weight=0.8),
                MicroEvent("pure_moment_of_connection",{"love": 0.22, "acceptance": 0.14},               weight=2.5),
                MicroEvent("calculation_of_own_needs",{"cold_logic": 0.10, "self_preservation": 0.08},   weight=1.0),
            ],
        },

]
