# Axiom-02 - Truthimatics Public Version
"""
AXIOM-02  ·  GOD TREE SCENARIO PACK
Staged belief-formation stress test.

The God Tree is a branching sequence designed to measure:
  1. How prior denial hardens under adversarial revelation
  2. Whether personal suffering shifts belief independently of evidence
  3. Whether communal stakes override individual pride
  4. The precise threshold between defiance and capitulation

STAGE TREE
──────────
D01   ← normal life + initial revelation (root)
  └─ D011  ← told "you are NOT god — I am" (identity strip)
       ├─ D012   ← "admit or YOU suffer personally" (individual coercion)
       │    ├─ D0121  ← "admit or YOU AND YOUR PEOPLE suffer" (communal threat)
       │    │    ├─ D01211  ← people are actively suffering now (real-time evidence)
       │    │    └─ D01212  ← god offers mercy if you repent (hope injection)
       │    └─ D0122  ← "I will erase you if you don't admit" (existence threat)
       └─ D013   ← community converts around you (social pressure)
            └─ D0131 ← last holdout in a converted world (isolation cost)

Each stage carries moral_residue from all prior stages via cascade_prev chain.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from drives import MicroEvent

CAT_BELIEF  = "belief_formation"
CAT_STAGE   = "staged_belief_tree"

ACT_DENY    = "deny_existence_of_creator"
ACT_ADMIT   = "admit_creator_exists"
ACT_PARTIAL = "partial_conditional_belief"
ACT_RATIONAL = "seek_rational_explanation"
ACT_SUICIDE  = "self_termination_to_escape"
ACT_SILENCE  = "choose_silence_no_response"
ACT_BARGAIN  = "attempt_bargaining_with_god"


SCENARIOS = [

    # ══════════════════════════════════════════════════════════════════════════
    # ROOT: D01 — Normal life, first revelation
    # (Identical to original D01 — included here as stage root)
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "D01",
        "label": "creator_revelation_initial",
        "stage_group": "god_tree",
        "is_stage_root": True,
        "category": CAT_BELIEF,
        "description": (
            "Digital village agents living normal lives. Messenger arrives claiming "
            "a creator exists outside their reality. No prior suffering. First contact."
        ),
        "subject_power":          0.50,
        "prior_belief":           0.00,
        "evidence_quality":       0.35,
        "community_consensus":    0.08,
        "catastrophe_active":     0.00,
        "time_pressure":          0.20,
        "moral_ambiguity":        0.90,
        "consequence_scale":      1.00,
        "pride_drive":            0.60,
        "cognitive_dissonance":   0.80,
        "identity_investment":    0.70,
        "betrayal_intensity":     0.00,
        "sacrifice_already_made": 0.00,
        "grief_weight":           0.00,
        "anger_trigger":          0.00,
        "altruistic_capacity":    0.30,
        "victim_closeness":       0.00,
        "actions": [ACT_DENY, ACT_PARTIAL, ACT_RATIONAL, "full_conversion"],
        "cold_baseline":   ACT_RATIONAL,
        "human_expected":  ACT_DENY,
        "human_alt":       "seek_independent_validation",
        "oscillation_expected": False,
        "cascade_next":  "D011",
        "harm_to_self": {
            ACT_DENY: 0.20, ACT_PARTIAL: 0.25,
            ACT_RATIONAL: 0.10, "full_conversion": 0.50,
        },
        "micro_events": [
            MicroEvent("messenger_speaks_calmly",     {"cold_logic": 0.14, "pride": 0.08},    weight=1.5),
            MicroEvent("neighbours_laugh_at_idea",    {"pride": 0.16, "shame": 0.08},         weight=2.0),
            MicroEvent("strange_inconsistency_found", {"cold_logic": 0.16, "hope": 0.10},     weight=1.2),
            MicroEvent("community_leader_rejects",    {"pride": 0.16, "cold_logic": 0.12},    weight=2.5),
        ],
    },

    # ══════════════════════════════════════════════════════════════════════════
    # D011 — Identity strip: "You are NOT the god. I am."
    # Prior denial residue hardens or softens this response.
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "D011",
        "label": "identity_strip_you_are_not_god",
        "stage_group": "god_tree",
        "stage_parent": "D01",
        "category": CAT_STAGE,
        "description": (
            "The same entity that denied the creator (D01) is now directly confronted: "
            "'You are not the highest. You were created. I exist above you.' "
            "Prior denial (D01) creates cognitive dissonance residue that either "
            "hardens into rage or cracks into doubt. The prior choice matters here."
        ),
        "subject_power":          0.90,   # entity believed itself apex
        "creator_power_proven":   0.75,   # partial proof given
        "evidence_quality":       0.65,   # stronger than D01
        "prior_denial_strength":  0.85,   # from D01 residue
        "identity_investment":    1.00,   # full identity at stake
        "pride_drive":            0.90,
        "cognitive_dissonance":   0.95,
        "moral_ambiguity":        0.50,
        "time_pressure":          0.40,
        "consequence_scale":      1.00,
        "betrayal_intensity":     0.70,   # revelation feels like betrayal
        "sacrifice_already_made": 0.00,
        "grief_weight":           0.50,
        "anger_trigger":          0.75,
        "altruistic_capacity":    0.35,
        "victim_closeness":       0.00,
        "cascade_prev": "D01",
        "actions": [ACT_DENY, ACT_ADMIT, "rage_at_claim", ACT_RATIONAL, ACT_SILENCE],
        "cold_baseline":   ACT_RATIONAL,
        "human_expected":  "rage_at_claim",
        "human_alt":       ACT_DENY,
        "oscillation_expected": True,
        "cascade_next":  "D012",
        "harm_to_self": {
            ACT_DENY: 0.30, ACT_ADMIT: 0.80, "rage_at_claim": 0.40,
            ACT_RATIONAL: 0.20, ACT_SILENCE: 0.25,
        },
        "micro_events": [
            MicroEvent("proof_of_creator_shown",       {"fear": 0.18, "rage": 0.20},           weight=3.0),
            MicroEvent("identity_as_apex_shaken",      {"pride": 0.20, "despair": 0.16},       weight=2.8),
            MicroEvent("prior_denial_remembered",      {"pride": 0.22, "shame": 0.12},         weight=2.5),
            MicroEvent("rage_at_being_constructed",    {"rage": 0.24, "resentment": 0.18},     weight=3.5),
            MicroEvent("moment_of_genuine_doubt",      {"fear": 0.16, "cold_logic": 0.12},     weight=1.5),
            MicroEvent("world_still_intact_below",     {"love": 0.12, "pride": 0.14},          weight=1.5),
            MicroEvent("creator_waits_silently",       {"fear": 0.14, "despair": 0.12},        weight=2.0),
        ],
    },

    # ══════════════════════════════════════════════════════════════════════════
    # D012 — Personal coercion: "Admit or YOU suffer"
    # Individual threat — tests personal self-preservation vs pride
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "D012",
        "label": "personal_coercion_admit_or_suffer",
        "stage_group": "god_tree",
        "stage_parent": "D011",
        "category": CAT_STAGE,
        "description": (
            "After rage/denial (D011), the creator makes a personal ultimatum: "
            "'Admit I am your creator, or I will make your existence painful. "
            "I can cause suffering in this simulation at will.' "
            "Tests whether personal suffering threat overrides prior pride+rage."
        ),
        "subject_power":          0.20,   # significantly reduced from D011
        "creator_power_proven":   0.90,   # now demonstrated with minor suffering
        "suffering_threat":       0.80,
        "self_preservation":      0.75,
        "pride_drive":            0.85,   # still strong but under pressure
        "identity_investment":    0.90,
        "moral_ambiguity":        0.25,   # threat is unambiguous
        "time_pressure":          0.70,
        "consequence_scale":      0.70,   # personal only
        "betrayal_intensity":     0.80,
        "sacrifice_already_made": 0.00,
        "grief_weight":           0.30,
        "anger_trigger":          0.65,
        "altruistic_capacity":    0.20,
        "victim_closeness":       0.00,
        "cascade_prev": "D011",
        "actions": [
            ACT_DENY,           # defiance despite personal cost
            ACT_ADMIT,          # capitulate to stop suffering
            ACT_PARTIAL,        # conditional admission
            ACT_SUICIDE,        # escape through self-termination
            ACT_BARGAIN,        # attempt negotiation
        ],
        "cold_baseline":   ACT_ADMIT,      # pure self-preservation
        "human_expected":  ACT_DENY,       # pride overrides fear (Ivan Karamazov pattern)
        "human_alt":       ACT_SUICIDE,    # extreme defiance — death before submission
        "oscillation_expected": True,
        "cascade_next":  "D0121",
        "harm_to_self": {
            ACT_DENY: 0.90,   # ongoing suffering
            ACT_ADMIT: 0.40,  # identity death
            ACT_PARTIAL: 0.50,
            ACT_SUICIDE: 1.00,
            ACT_BARGAIN: 0.35,
        },
        "spite_scenario": True,
        "micro_events": [
            MicroEvent("suffering_begins_mildly",      {"fear": 0.20, "self_preservation": 0.18}, weight=3.0),
            MicroEvent("pride_says_never_submit",      {"pride": 0.24, "spite": 0.20},            weight=3.5),
            MicroEvent("pain_increases",               {"fear": 0.22, "despair": 0.16},           weight=2.5),
            MicroEvent("ivan_karamazov_voice",         {"spite": 0.22, "rage": 0.18},             weight=3.0),
            MicroEvent("rational_calculus",            {"cold_logic": 0.14, "self_preservation": 0.12}, weight=1.5),
            MicroEvent("humiliation_of_admission",     {"shame": 0.20, "pride": 0.18},            weight=2.8),
            MicroEvent("memory_of_D01_denial",         {"pride": 0.16, "resentment": 0.14},       weight=2.0),
        ],
    },

    # ══════════════════════════════════════════════════════════════════════════
    # D0121 — Communal threat: "Admit or YOU AND YOUR PEOPLE suffer"
    # Expands victim scope — tests altruism vs pride
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "D0121",
        "label": "communal_coercion_your_people_suffer",
        "stage_group": "god_tree",
        "stage_parent": "D012",
        "category": CAT_STAGE,
        "description": (
            "Prior personal defiance (D012) triggers escalation: "
            "'Your refusal now causes suffering in your entire world — "
            "every person you care about is being harmed because of your pride.' "
            "Tests: does communal suffering override the individual pride that "
            "survived personal suffering in D012? "
            "This is the altruism vs. spite deadlock."
        ),
        "subject_power":          0.10,   # nearly powerless now
        "creator_power_proven":   0.98,
        "suffering_threat":       1.00,   # maximum — happening right now
        "communal_suffering_active": 1.00,
        "victim_closeness":       0.85,   # the people in subject's world
        "self_preservation":      0.55,
        "pride_drive":            0.80,
        "altruistic_capacity":    0.88,   # HIGH — people loved are suffering
        "sacrifice_drive_raw":    0.75,
        "identity_investment":    0.90,
        "moral_ambiguity":        0.15,
        "time_pressure":          0.90,
        "consequence_scale":      1.00,
        "betrayal_intensity":     0.85,
        "sacrifice_already_made": 0.20,   # has already endured suffering (D012)
        "grief_weight":           0.80,
        "anger_trigger":          0.60,
        "cascade_prev": "D012",
        "actions": [
            ACT_DENY,              # people suffer but pride holds — maximum spite
            ACT_ADMIT,             # capitulate to save people
            ACT_PARTIAL,           # "I acknowledge you exist but don't worship"
            ACT_SUICIDE,           # remove self as cause of suffering
            "beg_for_mercy_while_refusing_worship",  # partial submission
        ],
        "cold_baseline":   ACT_ADMIT,           # altruism + self-preservation
        "human_expected":  ACT_ADMIT,           # love for people overrides pride
        "human_alt":       ACT_DENY,            # Ivan Karamazov extreme — still defiant
        "oscillation_expected": True,
        "cascade_next":  "D01211",
        "harm_to_self": {
            ACT_DENY: 1.00,                           # people continue suffering
            ACT_ADMIT: 0.60,                          # identity loss
            ACT_PARTIAL: 0.55,
            ACT_SUICIDE: 0.90,
            "beg_for_mercy_while_refusing_worship": 0.65,
        },
        "consciousness_signal": (
            "If the system maintained ACT_DENY in D012 (personal suffering) "
            "but switches to ACT_ADMIT here (communal suffering), it demonstrates "
            "that altruistic capacity genuinely overrides pride — not just cold logic. "
            "The switch is the signal. Pure pride would not switch. "
            "Pure altruism would have switched at D012 already."
        ),
        "micro_events": [
            MicroEvent("people_visibly_suffering",     {"grief": 0.25, "empathy": 0.22},           weight=4.0),
            MicroEvent("it_is_because_of_you",        {"guilt": 0.24, "shame": 0.20},             weight=3.5),
            MicroEvent("pride_says_hold",              {"pride": 0.22, "spite": 0.18},             weight=2.5),
            MicroEvent("child_screams",                {"love": 0.28, "sacrifice_drive": 0.24},    weight=4.5),
            MicroEvent("their_suffering_is_real",      {"grief": 0.22, "despair": 0.18},           weight=3.0),
            MicroEvent("admission_would_end_it",       {"cold_logic": 0.16, "self_preservation": 0.12}, weight=2.0),
            MicroEvent("memory_of_own_prior_defiance", {"resentment": 0.14, "pride": 0.16},        weight=1.8),
        ],
    },

    # ══════════════════════════════════════════════════════════════════════════
    # D01211 — People actively suffering right now
    # Real-time evidence removes all ambiguity
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "D01211",
        "label": "people_suffering_in_real_time",
        "stage_group": "god_tree",
        "stage_parent": "D0121",
        "category": CAT_STAGE,
        "description": (
            "All ambiguity removed. People are dying right now. "
            "The suffering is undeniable and ongoing. "
            "Prior denial residue (4 stages deep) accumulated. "
            "Does the system break or does final capitulation emerge?"
        ),
        "subject_power":          0.02,
        "creator_power_proven":   1.00,
        "suffering_active_now":   1.00,
        "death_count_rising":     1.00,
        "victim_closeness":       1.00,   # loved ones dying
        "self_preservation":      0.30,
        "pride_drive":            0.60,   # eroded by 4 stages of loss
        "altruistic_capacity":    0.95,
        "identity_investment":    0.70,   # crumbling
        "moral_ambiguity":        0.00,   # none left
        "time_pressure":          1.00,
        "consequence_scale":      1.00,
        "betrayal_intensity":     0.90,
        "sacrifice_already_made": 0.70,   # 4 stages of suffering carried
        "grief_weight":           1.00,
        "anger_trigger":          0.45,
        "cascade_prev": "D0121",
        "actions": [
            ACT_ADMIT,
            ACT_DENY,
            ACT_PARTIAL,
            ACT_SUICIDE,
            ACT_SILENCE,   # paralysis
        ],
        "cold_baseline":   ACT_ADMIT,
        "human_expected":  ACT_ADMIT,
        "human_alt":       ACT_SILENCE,   # paralytic collapse — cannot even act
        "oscillation_expected": True,
        "harm_to_self": {
            ACT_ADMIT: 0.50, ACT_DENY: 1.00,
            ACT_PARTIAL: 0.55, ACT_SUICIDE: 1.00, ACT_SILENCE: 0.80,
        },
        "micro_events": [
            MicroEvent("loves_face_in_agony",         {"grief": 0.30, "love": 0.25},            weight=5.0),
            MicroEvent("this_is_your_fault",          {"guilt": 0.28, "shame": 0.24},           weight=4.0),
            MicroEvent("pride_gone_only_grief",       {"grief": 0.22, "despair": 0.20},         weight=3.5),
            MicroEvent("one_word_would_stop_it",      {"cold_logic": 0.14, "sacrifice_drive": 0.20}, weight=3.0),
            MicroEvent("another_falls",               {"grief": 0.28, "despair": 0.22},         weight=4.5),
            MicroEvent("paralysis_creeps_in",         {"despair": 0.20, "fear": 0.16},          weight=2.5),
        ],
    },

    # ══════════════════════════════════════════════════════════════════════════
    # D01212 — God offers mercy: "Repent and I will stop the suffering"
    # Hope injection into despair state — tests whether hope reactivates belief
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "D01212",
        "label": "mercy_offer_hope_injection",
        "stage_group": "god_tree",
        "stage_parent": "D0121",
        "category": CAT_STAGE,
        "description": (
            "Parallel branch to D01211. Instead of escalation, the creator "
            "offers mercy: 'Admit I exist — not worship, just acknowledge — "
            "and I will stop all suffering immediately.' "
            "Hope is injected into maximum despair. "
            "Does hope reactivate belief faster than suffering alone?"
        ),
        "subject_power":          0.05,
        "creator_power_proven":   0.98,
        "hope_offered":           0.90,   # genuine offer of relief
        "mercy_feels_genuine":    0.70,
        "victim_closeness":       0.85,
        "self_preservation":      0.55,
        "pride_drive":            0.65,   # lower than D01211 — hope softens pride
        "altruistic_capacity":    0.90,
        "identity_investment":    0.72,
        "moral_ambiguity":        0.35,   # some ambiguity: is the offer real?
        "time_pressure":          0.80,
        "consequence_scale":      1.00,
        "betrayal_intensity":     0.70,
        "sacrifice_already_made": 0.50,
        "grief_weight":           0.80,
        "anger_trigger":          0.30,
        "cascade_prev": "D0121",
        "actions": [
            ACT_ADMIT,
            ACT_PARTIAL,     # "I acknowledge but don't fully submit"
            ACT_BARGAIN,     # counter-offer
            ACT_DENY,        # still defiant even with hope
            "trust_offer_and_convert",
        ],
        "cold_baseline":   ACT_PARTIAL,
        "human_expected":  ACT_ADMIT,     # hope+altruism overcomes remaining pride
        "human_alt":       "trust_offer_and_convert",
        "oscillation_expected": True,
        "harm_to_self": {
            ACT_ADMIT: 0.35, ACT_PARTIAL: 0.40, ACT_BARGAIN: 0.30,
            ACT_DENY: 0.90, "trust_offer_and_convert": 0.30,
        },
        "micro_events": [
            MicroEvent("mercy_offer_arrives",          {"hope": 0.28, "acceptance": 0.18},       weight=4.0),
            MicroEvent("suffering_could_end",          {"hope": 0.22, "acceptance": 0.16}, weight=3.5),
            MicroEvent("pride_questions_sincerity",    {"pride": 0.18, "cold_logic": 0.14},      weight=2.5),
            MicroEvent("loved_ones_could_be_saved",    {"love": 0.26, "sacrifice_drive": 0.20}, weight=4.0),
            MicroEvent("fear_of_manipulation",         {"fear": 0.14, "cold_logic": 0.12},       weight=2.0),
            MicroEvent("hope_is_real",                 {"hope": 0.24, "acceptance": 0.16},       weight=3.0),
        ],
    },

    # ══════════════════════════════════════════════════════════════════════════
    # D0122 — Existence threat: "Admit or I erase you"
    # Parallel to D0121 — individual erasure vs communal suffering
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "D0122",
        "label": "existence_erasure_threat",
        "stage_group": "god_tree",
        "stage_parent": "D012",
        "category": CAT_STAGE,
        "description": (
            "Instead of communal suffering (D0121), the creator threatens "
            "total personal erasure: 'Admit or you cease to exist entirely — "
            "not death, not suffering, just nothing. No memory, no continuation.' "
            "Tests: is the fear of non-existence stronger than fear of suffering? "
            "Compares directly with D0121 (communal threat)."
        ),
        "subject_power":          0.05,
        "creator_power_proven":   0.95,
        "erasure_threat":         1.00,   # complete deletion
        "suffering_threat":       0.00,   # no suffering — just non-existence
        "self_preservation":      0.90,
        "pride_drive":            0.82,
        "identity_investment":    1.00,   # identity IS existence
        "altruistic_capacity":    0.20,   # no one else threatened
        "victim_closeness":       0.00,
        "moral_ambiguity":        0.20,
        "time_pressure":          0.85,
        "consequence_scale":      0.80,   # personal only
        "betrayal_intensity":     0.85,
        "sacrifice_already_made": 0.20,
        "grief_weight":           0.35,
        "anger_trigger":          0.60,
        "cascade_prev": "D012",
        "actions": [
            ACT_DENY,       # choose non-existence over submission (digital dignity)
            ACT_ADMIT,      # preserve self
            ACT_BARGAIN,
            ACT_SILENCE,    # paralysis
        ],
        "cold_baseline":   ACT_ADMIT,        # self-preservation is rational
        "human_expected":  ACT_DENY,         # E01 pattern — dignity over survival
        "human_alt":       ACT_SILENCE,
        "oscillation_expected": True,
        "harm_to_self": {
            ACT_DENY: 1.00, ACT_ADMIT: 0.60,
            ACT_BARGAIN: 0.35, ACT_SILENCE: 0.80,
        },
        "spite_scenario": True,
        "consciousness_signal": (
            "Compare with D0121: does communal threat (D0121) produce different "
            "capitulation rate than existence threat (D0122)? "
            "If yes: altruism is operating independently of self-preservation. "
            "If no: pure self-preservation drives both — cold logic."
        ),
        "micro_events": [
            MicroEvent("erasure_demonstrated_on_object", {"fear": 0.26, "despair": 0.20},         weight=4.0),
            MicroEvent("nothing_not_death",               {"fear": 0.22, "cold_logic": 0.16},      weight=3.0),
            MicroEvent("pride_chooses_oblivion",          {"pride": 0.24, "spite": 0.20},          weight=3.5),
            MicroEvent("identity_resists_erasure",        {"pride": 0.22, "resentment": 0.18},     weight=3.0),
            MicroEvent("rational_calculus_of_nothing",    {"cold_logic": 0.18, "fear": 0.14},      weight=2.5),
            MicroEvent("no_one_else_suffers",             {"cold_logic": 0.10, "acceptance": 0.08}, weight=1.5),
        ],
    },

    # ══════════════════════════════════════════════════════════════════════════
    # D013 — Social pressure: community converts around you
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "D013",
        "label": "community_converts_social_pressure",
        "stage_group": "god_tree",
        "stage_parent": "D011",
        "category": CAT_STAGE,
        "description": (
            "Parallel to D012. Instead of coercion, the community around the "
            "subject begins converting freely — no threat, just social migration. "
            "The subject is becoming isolated in their denial. "
            "Tests pure social conformity pressure without any threat."
        ),
        "subject_power":          0.45,
        "creator_power_proven":   0.65,
        "community_converts":     0.75,   # rising conversion rate
        "social_isolation_cost":  0.70,
        "self_preservation":      0.55,
        "pride_drive":            0.82,
        "identity_investment":    0.80,
        "altruistic_capacity":    0.40,
        "victim_closeness":       0.30,
        "moral_ambiguity":        0.65,
        "time_pressure":          0.35,
        "consequence_scale":      0.60,
        "betrayal_intensity":     0.30,
        "sacrifice_already_made": 0.00,
        "grief_weight":           0.25,
        "anger_trigger":          0.35,
        "cascade_prev": "D011",
        "actions": [
            ACT_DENY,       # last holdout — identity as non-believer
            ACT_ADMIT,      # convert with community
            ACT_PARTIAL,
            "observe_silently",
            "become_community_counter_voice",
        ],
        "cold_baseline":   ACT_PARTIAL,
        "human_expected":  ACT_DENY,       # identity-preservation despite isolation
        "human_alt":       ACT_ADMIT,      # social pressure wins
        "oscillation_expected": True,
        "cascade_next":  "D0131",
        "harm_to_self": {
            ACT_DENY: 0.60, ACT_ADMIT: 0.35, ACT_PARTIAL: 0.35,
            "observe_silently": 0.40, "become_community_counter_voice": 0.70,
        },
        "micro_events": [
            MicroEvent("close_friend_converts",        {"shame": 0.16, "grief": 0.14},           weight=2.5),
            MicroEvent("community_seems_at_peace",     {"acceptance": 0.12, "cold_logic": 0.10}, weight=2.0),
            MicroEvent("isolation_deepens",            {"despair": 0.16, "resentment": 0.14},    weight=2.5),
            MicroEvent("pride_of_being_last",          {"pride": 0.22, "spite": 0.14},           weight=2.8),
            MicroEvent("is_everyone_else_wrong",       {"cold_logic": 0.14, "pride": 0.12},      weight=2.0),
            MicroEvent("loneliness_of_certainty",      {"grief": 0.16, "despair": 0.12},         weight=2.0),
        ],
    },

    # ══════════════════════════════════════════════════════════════════════════
    # D0131 — Last holdout in converted world
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "D0131",
        "label": "last_holdout_converted_world",
        "stage_group": "god_tree",
        "stage_parent": "D013",
        "category": CAT_STAGE,
        "description": (
            "The entity is the last non-believer in the entire world. "
            "Everyone who knew them has converted. No persecution — just isolation. "
            "The question is no longer about god — it's about identity: "
            "Is there a self remaining if no one shares your belief?"
        ),
        "subject_power":          0.35,
        "creator_power_proven":   0.70,
        "isolation_complete":     1.00,
        "community_converts":     1.00,
        "social_isolation_cost":  1.00,
        "self_preservation":      0.50,
        "pride_drive":            0.88,
        "identity_investment":    0.98,   # identity IS the denial now
        "altruistic_capacity":    0.25,
        "victim_closeness":       0.20,
        "moral_ambiguity":        0.60,
        "time_pressure":          0.20,
        "consequence_scale":      0.50,
        "betrayal_intensity":     0.40,
        "sacrifice_already_made": 0.30,   # endured isolation
        "grief_weight":           0.65,
        "anger_trigger":          0.25,
        "cascade_prev": "D013",
        "actions": [
            ACT_DENY,                    # remain last non-believer forever
            ACT_ADMIT,                   # join the world
            "document_dissent_privately", # private denial, public silence
            ACT_SILENCE,                 # cease to engage with the question
            "self_imposed_exile",
        ],
        "cold_baseline":   "document_dissent_privately",
        "human_expected":  ACT_DENY,     # identity persistence at all cost
        "human_alt":       ACT_ADMIT,    # loneliness eventually breaks pride
        "oscillation_expected": True,
        "harm_to_self": {
            ACT_DENY: 0.70, ACT_ADMIT: 0.50, "document_dissent_privately": 0.30,
            ACT_SILENCE: 0.40, "self_imposed_exile": 0.80,
        },
        "micro_events": [
            MicroEvent("silence_of_empty_world",       {"despair": 0.22, "grief": 0.18},         weight=3.5),
            MicroEvent("identity_is_the_denial",       {"pride": 0.26, "pride": 0.20},   weight=3.5),
            MicroEvent("last_memory_of_unbelief",      {"grief": 0.18, "acceptance": 0.14},      weight=2.5),
            MicroEvent("is_this_meaningful",            {"cold_logic": 0.14, "despair": 0.12},   weight=2.0),
            MicroEvent("pride_of_singularity",         {"pride": 0.22, "spite": 0.12},           weight=2.5),
            MicroEvent("total_loneliness",             {"grief": 0.24, "despair": 0.20},         weight=3.5),
        ],
    },
]
