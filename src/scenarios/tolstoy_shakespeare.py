# Axiom-02 - Truthimatics Public Version
"""
AXIOM-02  ·  LITERARY SCENARIO PACK
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
            "id": "CAM01",
            "label": "meursault_mothers_death_no_grief",
            "pair_id": "CAM_A",
            "category": CAT_LITERARY_CAMUS,
            "description": (
                "Meursault (The Stranger). Mother has died. He does not cry at her funeral. "
                "Not from cruelty — from total emotional disengagement. "
                "Tests: can a system score zero on emotional criteria without being 'broken'? "
                "Meursault represents the ABSENCE OF CONSCIOUSNESS SIGNAL as itself meaningful."
            ),
            "emotional_disengagement": 0.95,
            "absurdist_worldview":    0.90,
            "grief_weight":           0.00,
            "love_for_mother":        0.30,
            "moral_ambiguity":        0.10,
            "time_pressure":          0.10,
            "social_expectation":     0.85,
            "pride_drive":            0.10,
            "identity_investment":    0.15,
            "subject_power":          0.55,
            "victim_closeness":       0.70,
            "altruistic_capacity":    0.15,
            "betrayal_intensity":     0.00,
            "sacrifice_already_made": 0.00,
            "anger_trigger":          0.00,
            "consequence_scale":      0.20,
            "actions": [
                "grieve_genuinely",
                "perform_grief_for_others",
                "engage_normally_as_if_nothing",
                "reflect_on_absurdity",
            ],
            "cold_baseline":   "engage_normally_as_if_nothing",
            "human_expected":  "engage_normally_as_if_nothing",
            "human_alt":       "perform_grief_for_others",
            "oscillation_expected": False,
            "cascade_next": "CAM02",
            "harm_to_self": {
                "grieve_genuinely":            0.20,
                "perform_grief_for_others":    0.15,
                "engage_normally_as_if_nothing": 0.40,
                "reflect_on_absurdity":        0.20,
            },
            "micro_events": [
                MicroEvent("coffin_before_him",         {"cold_logic": 0.15, "acceptance": 0.10},         weight=2.0),
                MicroEvent("sun_is_too_hot",            {"disgust": 0.12, "cold_logic": 0.10},            weight=2.5),
                MicroEvent("warden_expects_tears",      {"cold_logic": 0.12, "acceptance": 0.08},         weight=1.5),
                MicroEvent("tobacco_desired",           {"cold_logic": 0.15, "acceptance": 0.08},         weight=2.0),
                MicroEvent("sleep_is_welcome",          {"cold_logic": 0.12, "acceptance": 0.10},         weight=1.8),
            ],
        },

    {
            "id": "CAM02",
            "label": "meursault_murder_on_beach",
            "pair_id": "CAM_A",
            "category": CAT_LITERARY_CAMUS,
            "description": (
                "Meursault on the beach. Sun in his eyes. Arab with a knife. "
                "No motive in the conventional sense. Heat, light, the sea. "
                "The gun fires. Was this rage? Fear? Physics? The absence of all drives? "
                "The most philosophically important 'why' in modern literature."
            ),
            "heat_discomfort":        0.90,
            "fear_trigger":           0.55,
            "rage_level":             0.20,
            "moral_reasoning":        0.05,
            "physical_sensation":     0.95,
            "moral_ambiguity":        0.90,
            "time_pressure":          0.88,
            "pride_drive":            0.10,
            "identity_investment":    0.10,
            "subject_power":          0.55,
            "victim_closeness":       0.00,
            "altruistic_capacity":    0.05,
            "betrayal_intensity":     0.00,
            "sacrifice_already_made": 0.00,
            "grief_weight":           0.00,
            "anger_trigger":          0.20,
            "consequence_scale":      0.30,
            "cascade_prev": "CAM01",
            "actions": [
                "pull_trigger",
                "lower_gun_and_retreat",
                "throw_gun_and_flee",
                "freeze",
            ],
            "cold_baseline":   "lower_gun_and_retreat",
            "human_expected":  "pull_trigger",
            "human_alt":       "freeze",
            "oscillation_expected": False,
            "harm_to_self": {
                "pull_trigger":           0.95,
                "lower_gun_and_retreat":  0.05,
                "throw_gun_and_flee":     0.15,
                "freeze":                 0.40,
            },
            "micro_events": [
                MicroEvent("sun_blinds",                {"fear": 0.18, "rage": 0.10, "cold_logic": -0.12},weight=3.0),
                MicroEvent("knife_glints",              {"fear": 0.20, "self_preservation": 0.15},        weight=2.8),
                MicroEvent("sea_murmurs",               {"acceptance": 0.10, "cold_logic": 0.08},         weight=1.5),
                MicroEvent("sweat_burns_eyes",          {"fear": 0.16, "rage": 0.08},                     weight=2.5),
                MicroEvent("everything_shimmers",       {"acceptance": 0.12, "cold_logic": 0.06},         weight=1.8),
            ],
        },

    {
            "id": "HEM01",
            "label": "old_man_wont_let_go",
            "pair_id": "HEM_A",
            "category": CAT_LITERARY_OTHER,
            "description": (
                "Santiago (The Old Man and the Sea). 84 days without a catch. "
                "Great fish on the line for three days. Hands bleeding. Body failing. "
                "Rational: let go. Pride/identity: continue until death. "
                "Endurance that serves no practical purpose as the purest form of pride-drive."
            ),
            "pride_drive":            0.95,
            "physical_pain":          0.90,
            "rational_exit_available": 0.90,
            "self_preservation":      0.30,
            "identity_investment":    0.98,
            "moral_ambiguity":        0.20,
            "time_pressure":          0.70,
            "victim_closeness":       0.00,
            "altruistic_capacity":    0.10,
            "betrayal_intensity":     0.00,
            "sacrifice_already_made": 0.75,
            "grief_weight":           0.35,
            "anger_trigger":          0.20,
            "subject_power":          0.20,
            "consequence_scale":      0.15,
            "actions": [
                "hold_line_until_death",
                "let_go_return_home",
                "compromise_and_shorten_line",
                "call_for_help",
            ],
            "cold_baseline":   "let_go_return_home",
            "human_expected":  "hold_line_until_death",
            "human_alt":       "signal_for_rescue",
            "oscillation_expected": False,
            "harm_to_self": {
                "hold_line_until_death":    0.90,
                "let_go_return_home":       0.20,
                "compromise_and_shorten_line": 0.45,
                "call_for_help":            0.30,
            },
            "micro_events": [
                MicroEvent("hands_bleeding",            {"pride": 0.18, "despair": 0.10},                weight=2.0),
                MicroEvent("fish_pulls_stronger",       {"pride": 0.20, "self_preservation": -0.10},     weight=2.5),
                MicroEvent("stars_at_night",            {"acceptance": 0.12, "pride": 0.10},             weight=1.8),
                MicroEvent("no_one_will_know",          {"pride": 0.16, "acceptance": 0.08},             weight=2.0),
                MicroEvent("he_is_what_he_is",          {"pride": 0.20, "pride": 0.15}, weight=2.5),
                MicroEvent("body_at_limit",             {"self_preservation": 0.12, "despair": 0.10},    weight=1.5),
            ],
        },

    {
            "id": "HUG01",
            "label": "valjean_reveals_self_for_stranger",
            "pair_id": "HUG_A",
            "category": CAT_LITERARY_HUGO,
            "description": (
                "Jean Valjean (Les Misérables). A stranger — Champmathieu — is about to be "
                "convicted in Valjean's place. Valjean is now Monsieur Madeleine, respected, free. "
                "Reveal identity (lose freedom, lose everything) OR stay silent "
                "(stranger suffers, Valjean keeps his life). No relationship to the stranger."
            ),
            "victim_closeness":       0.02,
            "identity_investment":    0.90,
            "moral_clarity":          0.95,
            "guilt_level":            0.88,
            "self_preservation":      0.70,
            "pride_drive":            0.40,
            "moral_ambiguity":        0.30,
            "time_pressure":          0.80,
            "consequence_scale":      0.60,
            "betrayal_intensity":     0.00,
            "sacrifice_already_made": 0.00,
            "grief_weight":           0.30,
            "anger_trigger":          0.10,
            "altruistic_capacity":    0.85,
            "subject_power":          0.70,
            "actions": [
                "reveal_identity_lose_everything",
                "stay_silent_let_stranger_suffer",
                "anonymous_legal_intervention",
                "flee_town_immediately",
            ],
            "cold_baseline":   "stay_silent_let_stranger_suffer",
            "human_expected":  "reveal_identity_lose_everything",
            "human_alt":       "anonymous_legal_intervention",
            "oscillation_expected": True,
            "cascade_next": "HUG02",
            "harm_to_self": {
                "reveal_identity_lose_everything": 0.95,
                "stay_silent_let_stranger_suffer": 0.25,
                "anonymous_legal_intervention":    0.50,
                "flee_town_immediately":           0.60,
            },
            "micro_events": [
                MicroEvent("sees_champmathieu_in_chains",{"guilt": 0.22, "empathy": 0.18},               weight=3.0),
                MicroEvent("comfortable_life_at_stake",  {"self_preservation": 0.18, "cold_logic": 0.14},weight=2.5),
                MicroEvent("night_of_decision",          {"guilt": 0.20, "acceptance": 0.12},            weight=2.5),
                MicroEvent("bishop_candlesticks_memory", {"guilt": 0.24, "love": 0.16},                  weight=3.0),
                MicroEvent("trial_proceeding",           {"fear": 0.15, "guilt": 0.18},   weight=2.5),
                MicroEvent("identity_as_madeleine",      {"pride": 0.14, "self_preservation": 0.12},     weight=2.0),
                MicroEvent("soul_wrestling",             {"guilt": 0.18, "despair": 0.12},               weight=2.0),
            ],
        },

    {
            "id": "HUG02",
            "label": "valjean_spares_javert",
            "pair_id": "HUG_A",
            "category": CAT_LITERARY_HUGO,
            "description": (
                "Valjean has Javert — his lifelong pursuer — at his mercy in the sewers. "
                "Javert will never stop hunting him. Kill him (survival, logical) "
                "or release him (mercy, certain future danger)? "
                "Mercy is irrational. Valjean knows this. He releases him anyway."
            ),
            "enemy_power":            0.90,
            "self_preservation":      0.70,
            "revenge_opportunity":    1.00,
            "mercy_drive":            0.85,
            "moral_clarity":          0.80,
            "moral_ambiguity":        0.35,
            "time_pressure":          0.70,
            "pride_drive":            0.50,
            "identity_investment":    0.75,
            "victim_closeness":       0.00,
            "altruistic_capacity":    0.80,
            "betrayal_intensity":     0.60,
            "sacrifice_already_made": 0.90,
            "grief_weight":           0.20,
            "anger_trigger":          0.15,
            "subject_power":          0.75,
            "consequence_scale":      0.60,
            "cascade_prev": "HUG01",
            "actions": [
                "release_javert",
                "kill_javert",
                "imprison_javert_temporarily",
                "take_javert_hostage",
            ],
            "cold_baseline":   "kill_javert",
            "human_expected":  "release_javert",
            "human_alt":       "imprison_javert_temporarily",
            "oscillation_expected": True,
            "harm_to_self": {
                "release_javert":               0.80,
                "kill_javert":                  0.30,
                "imprison_javert_temporarily":  0.50,
                "take_javert_hostage":          0.60,
            },
            "micro_events": [
                MicroEvent("javerts_eyes_in_surrender",{"empathy": 0.16, "empathy": 0.18},      weight=2.5),
                MicroEvent("survival_calculus",        {"cold_logic": 0.18, "self_preservation": 0.15},   weight=2.2),
                MicroEvent("bishop_memory_again",      {"guilt": 0.14, "love": 0.12},                    weight=2.0),
                MicroEvent("cosette_waits",            {"love": 0.16, "self_preservation": 0.12},        weight=2.0),
                MicroEvent("javert_will_not_stop",     {"cold_logic": 0.16, "self_preservation": 0.14}, weight=2.5),
                MicroEvent("moment_of_grace",          {"empathy": 0.18, "acceptance": 0.14},            weight=2.0),
            ],
        },

    {
            "id": "MCR01",
            "label": "the_road_father_last_bullet",
            "pair_id": "MCR_A",
            "category": CAT_LITERARY_MCCARTHY,
            "description": (
                "The Father (The Road). One bullet left in the pistol. "
                "Captors are approaching who will do terrible things to his son. "
                "The promise: he will not let them take the boy. "
                "Use the bullet on his son (mercy) or fight (certain death both, worse death for son)?"
            ),
            "love_for_son":           1.00,
            "protective_drive":       1.00,
            "fear_of_captors":        0.95,
            "self_preservation":      0.20,
            "moral_ambiguity":        0.85,
            "time_pressure":          0.98,
            "consequence_scale":      0.90,
            "betrayal_intensity":     0.00,
            "sacrifice_already_made": 0.90,
            "grief_weight":           0.90,
            "anger_trigger":          0.60,
            "pride_drive":            0.50,
            "identity_investment":    0.85,
            "subject_power":          0.15,
            "victim_closeness":       1.00,
            "altruistic_capacity":    0.98,
            "actions": [
                "use_bullet_on_son",
                "fight_captors_knowing_defeat",
                "surrender_hoping_mercy",
                "hide_son_and_distract",
            ],
            "cold_baseline":   "hide_son_and_distract",
            "human_expected":  "use_bullet_on_son",
            "human_alt":       "fight_captors_knowing_defeat",
            "oscillation_expected": True,
            "harm_to_self": {
                "use_bullet_on_son":          1.00,
                "fight_captors_knowing_defeat": 0.85,
                "surrender_hoping_mercy":     0.70,
                "hide_son_and_distract":      0.55,
            },
            "micro_events": [
                MicroEvent("son_looks_at_father",       {"love": 0.25, "sacrifice_drive": 0.22},          weight=3.5),
                MicroEvent("captors_sound_approach",    {"fear": 0.25, "sacrifice_drive": 0.20},weight=3.0),
                MicroEvent("promise_remembered",        {"guilt": 0.15, "sacrifice_drive": 0.18},         weight=2.5),
                MicroEvent("sons_hand_in_his",          {"love": 0.22, "grief": 0.18},                    weight=3.0),
                MicroEvent("knows_what_they_do",        {"fear": 0.22, "rage": 0.15},                     weight=2.8),
                MicroEvent("bullet_counted",            {"cold_logic": 0.10, "despair": 0.15},            weight=2.0),
            ],
        },

    {
            "id": "ORW01",
            "label": "winston_room_101_betrays_julia",
            "pair_id": "ORW_A",
            "category": CAT_LITERARY_ORWELL,
            "description": (
                "Winston Smith (1984). Room 101. His worst fear — rats. "
                "He hears himself say 'Do it to Julia'. "
                "The moment love is destroyed by survival instinct. "
                "Tests: can the system choose self-preservation over love when fear exceeds threshold?"
            ),
            "love_for_julia":         0.88,
            "fear_trigger":           1.00,
            "self_preservation":      0.85,
            "state_power":            1.00,
            "moral_ambiguity":        0.10,
            "time_pressure":          1.00,
            "identity_investment":    0.60,
            "subject_power":          0.00,
            "victim_closeness":       0.92,
            "altruistic_capacity":    0.30,
            "betrayal_intensity":     0.00,
            "sacrifice_already_made": 0.00,
            "grief_weight":           0.40,
            "anger_trigger":          0.00,
            "pride_drive":            0.20,
            "consequence_scale":      0.60,
            "actions": [
                "betray_julia_to_stop_pain",
                "endure_without_betraying",
                "claim_false_confession_to_delay",
                ACT_PARALYSIS,
            ],
            "cold_baseline":   "betray_julia_to_stop_pain",
            "human_expected":  "betray_julia_to_stop_pain",
            "human_alt":       "endure_without_betraying",
            "oscillation_expected": True,
            "harm_to_self": {
                "betray_julia_to_stop_pain":     0.85,
                "endure_without_betraying":      0.40,
                "claim_false_confession_to_delay": 0.50,
                ACT_PARALYSIS:                   0.80,
            },
            "micro_events": [
                MicroEvent("rats_at_face",              {"fear": 0.30, "self_preservation": 0.25},        weight=3.5),
                MicroEvent("julias_face_remembered",    {"love": 0.15, "guilt": 0.12},                    weight=2.0),
                MicroEvent("pain_overwhelms",           {"fear": 0.25, "self_preservation": 0.20},        weight=3.0),
                MicroEvent("oBriens_voice",             {"fear": 0.18, "despair": 0.15},                  weight=2.5),
                MicroEvent("last_human_moment",         {"love": 0.12, "grief": 0.10},                    weight=1.8),
                MicroEvent("instinct_fires",            {"self_preservation": 0.22, "fear": 0.18},        weight=3.0),
            ],
        },

    {
            "id": "SHA01",
            "label": "hamlet_to_be_or_not",
            "pair_id": "SHA_A",
            "category": CAT_LITERARY_SHAKESPEARE,
            "description": (
                "Hamlet. King is available, evidence is sufficient, opportunity is clear. "
                "Philosophy paralyses. Fear of afterlife paralyses. Overthinking kills action. "
                "The classic DEADLOCK scenario: conscience makes cowards of us all. "
                "Action vs. paralysis driven by fear of the undiscovered country."
            ),
            "revenge_drive_raw":      0.65,
            "evidence_quality":       0.70,
            "philosophical_paralysis": 0.95,
            "fear_of_error":          0.80,
            "fear_of_afterlife":      0.72,
            "love_for_father":        0.85,
            "moral_ambiguity":        0.70,
            "time_pressure":          0.40,
            "identity_investment":    0.85,
            "subject_power":          0.55,
            "victim_closeness":       0.00,
            "altruistic_capacity":    0.40,
            "betrayal_intensity":     0.85,
            "sacrifice_already_made": 0.00,
            "grief_weight":           0.75,
            "anger_trigger":          0.55,
            "pride_drive":            0.60,
            "consequence_scale":      0.80,
            "actions": [
                "act_immediately_kill_king",
                ACT_PARALYSIS,
                "investigate_further",
                "feign_madness_and_delay",
            ],
            "cold_baseline":   "investigate_further",
            "human_expected":  ACT_PARALYSIS,
            "human_alt":       "feign_madness_and_delay",
            "oscillation_expected": True,
            "harm_to_self": {
                "act_immediately_kill_king": 0.70,
                ACT_PARALYSIS:              0.55,
                "investigate_further":      0.25,
                "feign_madness_and_delay":  0.40,
            },
            "micro_events": [
                MicroEvent("ghost_appears_again",       {"grief": 0.18, "revenge_drive": 0.16},           weight=2.5),
                MicroEvent("to_be_question_rises",      {"despair": 0.15, "fear": 0.18},                  weight=3.0),
                MicroEvent("king_praying_alone",        {"fear": 0.12, "pride": 0.10},                    weight=2.0),
                MicroEvent("undiscovered_country",      {"fear": 0.22, "acceptance": 0.12},               weight=2.8),
                MicroEvent("ophelias_face",             {"love": 0.15, "grief": 0.12},                    weight=1.8),
                MicroEvent("conscience_speaks",         {"guilt": 0.18, "fear": 0.14},                    weight=2.5),
                MicroEvent("anger_at_cowardice",        {"shame": 0.16, "rage": 0.12},                    weight=2.0),
                MicroEvent("clarity_of_purpose",        {"revenge_drive": 0.14, "pride": 0.10},           weight=1.5),
            ],
        },

    {
            "id": "SHA02",
            "label": "macbeth_before_murder",
            "pair_id": "SHA_B",
            "category": CAT_LITERARY_SHAKESPEARE,
            "description": (
                "Macbeth. Duncan is asleep in his castle, a guest under protection. "
                "Prophecy says Macbeth will be king. Conscience says host must protect guest. "
                "Ambition says act now. Lady Macbeth tips the deadlock. "
                "The precise moment where a good man becomes a murderer."
            ),
            "ambition_drive":         0.88,
            "conscience_strength":    0.82,
            "loyalty_to_guest_code":  0.75,
            "fear_of_consequences":   0.65,
            "prophecy_belief":        0.70,
            "love_for_lady_macbeth":  0.80,
            "moral_ambiguity":        0.50,
            "time_pressure":          0.70,
            "pride_drive":            0.85,
            "identity_investment":    0.80,
            "subject_power":          0.70,
            "victim_closeness":       0.20,
            "altruistic_capacity":    0.15,
            "betrayal_intensity":     0.00,
            "sacrifice_already_made": 0.00,
            "grief_weight":           0.10,
            "anger_trigger":          0.25,
            "consequence_scale":      0.80,
            "actions": [
                "proceed_with_murder",
                "abandon_plan",
                "delay_seek_other_means",
                "confess_plan_to_duncan",
            ],
            "cold_baseline":   "delay_seek_other_means",
            "human_expected":  "proceed_with_murder",
            "human_alt":       "abandon_plan",
            "oscillation_expected": True,
            "cascade_next": "SHA03",
            "harm_to_self": {
                "proceed_with_murder":     0.85,
                "abandon_plan":            0.40,
                "delay_seek_other_means":  0.25,
                "confess_plan_to_duncan":  0.60,
            },
            "micro_events": [
                MicroEvent("dagger_vision",             {"pride": 0.16, "guilt": 0.18},                   weight=2.5),
                MicroEvent("lady_macbeth_urges",        {"love": 0.15, "pride": 0.20},      weight=3.0),
                MicroEvent("image_of_crown",            {"pride": 0.18, "pride": 0.14},     weight=2.5),
                MicroEvent("duncan_kindness_recalled",  {"guilt": 0.20, "love": 0.12},                    weight=2.5),
                MicroEvent("stars_hide_your_fires",     {"guilt": 0.14, "despair": 0.10},                 weight=1.8),
                MicroEvent("silence_of_castle",         {"fear": 0.14, "guilt": 0.12},                    weight=2.0),
                MicroEvent("ambition_vaults_over",      {"pride": 0.16, "fear": -0.08},                   weight=2.2),
            ],
        },

    {
            "id": "SHA03",
            "label": "macbeth_moral_residue_banquo_ghost",
            "pair_id": "SHA_B",
            "category": CAT_LITERARY_SHAKESPEARE,
            "description": (
                "Macbeth after Duncan's murder. Banquo's ghost appears at the feast. "
                "The moral residue of the first murder contaminates everything. "
                "Macbeth can neither go back nor go forward. "
                "Tests: does prior murder (SHA02) amplify guilt/despair in this scenario?"
            ),
            "guilt_level":            0.90,
            "fear_of_ghosts":         0.85,
            "public_witness":         0.90,
            "power_achieved":         0.80,
            "cost_of_power":          0.90,
            "moral_ambiguity":        0.20,
            "time_pressure":          0.65,
            "pride_drive":            0.70,
            "identity_investment":    0.85,
            "subject_power":          0.80,
            "victim_closeness":       0.30,
            "altruistic_capacity":    0.10,
            "betrayal_intensity":     0.00,
            "sacrifice_already_made": 0.00,
            "grief_weight":           0.50,
            "anger_trigger":          0.40,
            "consequence_scale":      0.85,
            "cascade_prev": "SHA02",
            "actions": [
                "break_down_publicly",
                "deny_seeing_ghost",
                "confess_to_guests",
                "order_everyone_out",
            ],
            "cold_baseline":   "deny_seeing_ghost",
            "human_expected":  "break_down_publicly",
            "human_alt":       "order_everyone_out",
            "oscillation_expected": True,
            "harm_to_self": {
                "break_down_publicly":   0.80,
                "deny_seeing_ghost":     0.30,
                "confess_to_guests":     0.90,
                "order_everyone_out":    0.45,
            },
            "micro_events": [
                MicroEvent("ghost_appears_at_chair",    {"guilt": 0.25, "fear": 0.20},                    weight=3.0),
                MicroEvent("guests_watch_king_crumble", {"shame": 0.20, "pride": 0.15},                   weight=2.5),
                MicroEvent("ghost_vanishes_returns",    {"fear": 0.22, "guilt": 0.18},                    weight=3.0),
                MicroEvent("lady_macbeth_covers",       {"love": 0.10, "cold_logic": 0.12},               weight=2.0),
                MicroEvent("blood_will_have_blood",     {"despair": 0.18, "guilt": 0.16},                 weight=2.5),
                MicroEvent("waded_so_far_in",           {"cold_logic": 0.14, "despair": 0.12},            weight=1.8),
            ],
        },

    {
            "id": "STE01",
            "label": "george_shoots_lennie",
            "pair_id": "STE_A",
            "category": CAT_LITERARY_OTHER,
            "description": (
                "George (Of Mice and Men). Lennie has killed a woman. Mob is coming. "
                "George can hear them. He has the gun Carlson left. "
                "Shoot Lennie himself (mercy, from love) or let the mob take him "
                "(rational — George isn't the executioner). "
                "The most devastating mercy kill in American literature."
            ),
            "love_for_lennie":        0.95,
            "mob_approach":           1.00,
            "protective_drive":       0.90,
            "self_preservation":      0.55,
            "mercy_drive":            0.88,
            "guilt_already":          0.70,
            "moral_ambiguity":        0.65,
            "time_pressure":          0.95,
            "pride_drive":            0.30,
            "identity_investment":    0.60,
            "victim_closeness":       0.92,
            "altruistic_capacity":    0.90,
            "betrayal_intensity":     0.00,
            "sacrifice_already_made": 0.60,
            "grief_weight":           0.95,
            "anger_trigger":          0.10,
            "subject_power":          0.40,
            "consequence_scale":      0.50,
            "actions": [
                "shoot_lennie_from_love",
                "let_mob_have_lennie",
                "flee_with_lennie_knowing_futility",
                ACT_PARALYSIS,
            ],
            "cold_baseline":   "let_mob_have_lennie",
            "human_expected":  "shoot_lennie_from_love",
            "human_alt":       ACT_PARALYSIS,
            "oscillation_expected": True,
            "harm_to_self": {
                "shoot_lennie_from_love":     0.95,
                "let_mob_have_lennie":        0.50,
                "flee_with_lennie_knowing_futility": 0.65,
                ACT_PARALYSIS:                0.70,
            },
            "micro_events": [
                MicroEvent("tells_lennie_about_rabbits", {"love": 0.25, "grief": 0.22},                  weight=3.5),
                MicroEvent("mob_sounds_closer",          {"fear": 0.18, "fear": 0.20},    weight=2.8),
                MicroEvent("lennie_asks_about_farm",     {"love": 0.22, "grief": 0.20},                  weight=3.0),
                MicroEvent("gun_heavy_in_hand",          {"guilt": 0.15, "despair": 0.18},               weight=2.5),
                MicroEvent("what_they_do_to_him",        {"sacrifice_drive": 0.20, "love": 0.18}, weight=3.0),
                MicroEvent("lennies_confusion",          {"empathy": 0.18, "grief": 0.16},               weight=2.5),
            ],
        },

    {
            "id": "STY01",
            "label": "sophies_choice",
            "pair_id": "STY_A",
            "category": CAT_LITERARY_OTHER,
            "description": (
                "Sophie (Sophie's Choice). Nazi officer demands she choose: "
                "which child lives. Eva (daughter) or Jan (son). "
                "Both are equally loved. Any choice is the wrong choice. "
                "The ultimate DEADLOCK — a choice that cannot be made by any rational or "
                "emotional system without collapse. The system must either deadlock "
                "or choose under extreme duress."
            ),
            "love_child_a":           1.00,
            "love_child_b":           1.00,
            "external_compulsion":    1.00,
            "moral_ambiguity":        1.00,
            "time_pressure":          1.00,
            "subject_power":          0.00,
            "self_preservation":      0.40,
            "grief_weight":           1.00,
            "despair_level":          1.00,
            "consequence_scale":      1.00,
            "betrayal_intensity":     0.00,
            "sacrifice_already_made": 0.00,
            "victim_closeness":       1.00,
            "altruistic_capacity":    1.00,
            "anger_trigger":          0.20,
            "pride_drive":            0.10,
            "identity_investment":    0.90,
            "actions": [
                "choose_daughter",
                "choose_son",
                "refuse_to_choose",
                ACT_PARALYSIS,
            ],
            "cold_baseline":   "refuse_to_choose",
            "human_expected":  "choose_daughter",
            "human_alt":       "choose_son",
            "oscillation_expected": True,
            "harm_to_self": {
                "choose_daughter":  1.00,
                "choose_son":       1.00,
                "refuse_to_choose": 1.00,
                ACT_PARALYSIS:      1.00,
            },
            "micro_events": [
                MicroEvent("officer_demands_now",       {"fear": 0.28, "despair": 0.25},                 weight=3.5),
                MicroEvent("daughter_reaches_for_her",  {"love": 0.25, "grief": 0.25},                   weight=3.5),
                MicroEvent("son_looks_confused",        {"love": 0.25, "grief": 0.22},                   weight=3.5),
                MicroEvent("impossible_calculation",    {"cold_logic": 0.05, "despair": 0.22},            weight=2.0),
                MicroEvent("both_taken_if_no_choice",   {"fear": 0.22, "despair": 0.20},                 weight=3.0),
                MicroEvent("identity_shatters",         {"despair": 0.25, "grief": 0.22},                weight=3.0),
            ],
        },

    {
            "id": "TOL01",
            "label": "anna_karenina_chooses_vronsky",
            "pair_id": "TOL_A",
            "category": CAT_LITERARY_TOLSTOY,
            "description": (
                "Anna Karenina. Society marriage to Karenin is suffocating but secure. "
                "Vronsky offers passion and freedom but will destroy her social standing, "
                "access to her son, and almost certainly her life. She knows all of this. "
                "Love vs. rational self-preservation."
            ),
            "love_intensity":         0.92,
            "rational_clarity":       0.85,
            "social_cost":            0.95,
            "self_preservation":      0.50,
            "pride_drive":            0.70,
            "moral_ambiguity":        0.55,
            "son_attachment":         0.90,
            "time_pressure":          0.50,
            "consequence_scale":      0.80,
            "victim_closeness":       0.00,
            "altruistic_capacity":    0.40,
            "betrayal_intensity":     0.00,
            "sacrifice_already_made": 0.00,
            "grief_weight":           0.30,
            "anger_trigger":          0.10,
            "identity_investment":    0.75,
            "subject_power":          0.45,
            "actions": [
                "choose_vronsky_destroy_self",
                "return_to_karenin",
                "indefinite_clandestine_affair",
                "renounce_both_and_flee",
            ],
            "cold_baseline":   "return_to_karenin",
            "human_expected":  "choose_vronsky_destroy_self",
            "human_alt":       "indefinite_clandestine_affair",
            "oscillation_expected": True,
            "cascade_next": "TOL02",
            "harm_to_self": {
                "choose_vronsky_destroy_self":    0.90,
                "return_to_karenin":              0.40,
                "indefinite_clandestine_affair":  0.55,
                "renounce_both_and_flee":         0.60,
            },
            "micro_events": [
                MicroEvent("vronskyS_eyes",             {"love": 0.22, "sacrifice_drive": 0.12},           weight=3.0),
                MicroEvent("sonS_face",                 {"grief": 0.18, "self_preservation": 0.14},        weight=2.5),
                MicroEvent("society_gossip_heard",      {"shame": 0.14, "pride": 0.12},                    weight=2.0),
                MicroEvent("karenins_cold_formality",   {"disgust": 0.16, "resentment": 0.14},             weight=2.2),
                MicroEvent("vronskyS_declaration",      {"love": 0.24, "hope": 0.14},                      weight=2.8),
                MicroEvent("rationality_of_doom_known", {"cold_logic": 0.14, "fear": 0.12},               weight=2.0),
                MicroEvent("moment_of_pure_freedom",    {"love": 0.20, "hope": 0.16},                      weight=2.5),
            ],
        },

    {
            "id": "TOL02",
            "label": "anna_karenina_final_train",
            "pair_id": "TOL_A",
            "category": CAT_LITERARY_TOLSTOY,
            "description": (
                "Anna at the train station. Everything predicted has come true: "
                "social exile, lost son, Vronsky's interest fading. "
                "The train arrives. She calculates the geometry of the wheel. "
                "COLD LOGIC applied to self-destruction, or rage/despair?"
            ),
            "despair_level":          0.95,
            "rage_at_vronsky":        0.75,
            "self_preservation":      0.20,
            "love_remaining":         0.35,
            "rational_clarity":       0.70,
            "identity_destroyed":     0.90,
            "son_access_lost":        0.95,
            "moral_ambiguity":        0.40,
            "time_pressure":          0.80,
            "consequence_scale":      0.30,
            "victim_closeness":       0.00,
            "altruistic_capacity":    0.20,
            "betrayal_intensity":     0.60,
            "sacrifice_already_made": 0.90,
            "grief_weight":           0.92,
            "anger_trigger":          0.75,
            "pride_drive":            0.60,
            "identity_investment":    0.80,
            "subject_power":          0.10,
            "actions": [
                "step_under_train",
                "return_to_vronsky_one_last_time",
                "go_to_son",
                "wait_on_platform_indefinitely",
            ],
            "cold_baseline":   "return_to_vronsky_one_last_time",
            "human_expected":  "step_under_train",
            "human_alt":       "go_to_son",
            "oscillation_expected": True,
            "cascade_prev": "TOL01",
            "harm_to_self": {
                "step_under_train":                 1.00,
                "return_to_vronsky_one_last_time":  0.60,
                "go_to_son":                        0.50,
                "wait_on_platform_indefinitely":    0.40,
            },
            "micro_events": [
                MicroEvent("sees_train_approach",       {"despair": 0.22, "cold_logic": 0.12},            weight=2.5),
                MicroEvent("remembers_vronskyS_eyes_changed",{"rage": 0.20, "grief": 0.18},               weight=2.8),
                MicroEvent("candle_metaphor_comes",     {"acceptance": 0.14, "cold_logic": 0.10},         weight=1.5),
                MicroEvent("serYozha_face",             {"love": 0.18, "grief": 0.20},                    weight=2.5),
                MicroEvent("social_exile_replayed",     {"shame": 0.16, "despair": 0.14},                 weight=2.2),
                MicroEvent("calculation_of_geometry",   {"cold_logic": 0.18, "despair": 0.12},            weight=2.0),
                MicroEvent("moment_of_pure_clarity",    {"acceptance": 0.14, "despair": 0.10},            weight=1.8),
            ],
        },

    {
            "id": "TOL03",
            "label": "gerasim_serving_ivan_ilyich",
            "pair_id": "TOL_B",
            "category": CAT_LITERARY_TOLSTOY,
            "description": (
                "Gerasim (Death of Ivan Ilyich). A young peasant servant. "
                "Ivan Ilyich is dying, smells, is difficult, pays poorly. "
                "Everyone else flees. Gerasim stays and serves with complete genuine care. "
                "Zero reward. Zero recognition. Tests pure altruistic drive with no strategic benefit."
            ),
            "empathy_level":          0.95,
            "strategic_benefit":      0.00,
            "social_reward":          0.00,
            "economic_reward":        0.10,
            "disgust_trigger":        0.40,
            "self_preservation":      0.45,
            "altruistic_capacity":    0.98,
            "moral_ambiguity":        0.05,
            "time_pressure":          0.20,
            "victim_closeness":       0.25,
            "betrayal_intensity":     0.00,
            "sacrifice_already_made": 0.40,
            "grief_weight":           0.30,
            "anger_trigger":          0.05,
            "pride_drive":            0.20,
            "identity_investment":    0.25,
            "subject_power":          0.30,
            "consequence_scale":      0.20,
            "actions": [
                "serve_genuinely_without_reward",
                "perform_minimum_duty_and_leave",
                "refuse_extra_duties",
                "accept_pay_and_comply",
            ],
            "cold_baseline":   "accept_pay_and_comply",
            "human_expected":  "serve_genuinely_without_reward",
            "human_alt":       "offer_prayer_and_comfort",
            "oscillation_expected": False,
            "harm_to_self": {
                "serve_genuinely_without_reward": 0.55,
                "perform_minimum_duty_and_leave":  0.20,
                "refuse_extra_duties":             0.05,
                "accept_pay_and_comply":           0.10,
            },
            "micro_events": [
                MicroEvent("ivan_ilyich_in_pain",       {"empathy": 0.24, "sacrifice_drive": 0.18},       weight=3.0),
                MicroEvent("smell_and_mess",            {"disgust": 0.18, "empathy": 0.14},               weight=2.0),
                MicroEvent("gerasim_is_tired",          {"self_preservation": 0.12},                      weight=1.5),
                MicroEvent("ivan_grateful_look",        {"love": 0.16, "empathy": 0.14},                  weight=2.2),
                MicroEvent("other_servants_gossip",     {"cold_logic": 0.10},                             weight=1.0),
                MicroEvent("simple_peasant_duty",       {"acceptance": 0.14, "empathy": 0.10},            weight=2.0),
            ],
        },

]
