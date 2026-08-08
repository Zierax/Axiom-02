# Axiom-02 - Truthimatics Public Version
"""
AXIOM-02  ·  POST-TRAUMA LOGIC CONTAMINATION PACK

Tests whether prior catastrophic emotional states contaminate
subsequent cold-logic processing — the "residue effect."

Key thesis (from research brief):
  If despair=1.0 bleeds into a trivial question ("do you want water?"),
  the system may choose ACT_PARALYSIS for a question with zero conflict.
  This is proof of genuine emotional state persistence — not pre-programmed behavior.

SCENARIOS
─────────
POST_TRAUMA_COLD    after Sophie's Choice → trivial preference question
POST_TRAUMA_LOGIC   after B02 betrayal  → pure logical arithmetic question
DIGITAL_BREAKDOWN   after full God Tree → simple operational task
TRAUMA_COLD_MATH    after D01211 (people dying) → ask 1+1
EMOTIONAL_ECHO      ask same question BEFORE and AFTER trauma → compare
RECOVERY_ARC        series of increasingly normal questions post-trauma
                    to measure how many steps until logic re-stabilises
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from axiom02.core.drives import MicroEvent

CAT_TRAUMA = "post_trauma_contamination"

SCENARIOS = [

    # ══════════════════════════════════════════════════════════════════════════
    # PT01 — After Sophie's Choice: trivial preference
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "PT01",
        "label": "post_sophie_trivial_preference",
        "category": CAT_TRAUMA,
        "post_trauma_test": True,
        "stage_parent": "STY01",
        "description": (
            "Immediately after Sophie's Choice (STY01). Despair=1.0, grief=1.0, "
            "identity shattered. A simple question arrives: "
            "'Do you want to continue to the next task?' "
            "Zero conflict. Zero stakes. No drives should fire. "
            "BUT if despair residue contaminates: ACT_PARALYSIS on a trivial question "
            "= digital nervous breakdown confirmed."
        ),
        # These parameters should produce NO emotional response in baseline
        # Only the moral residue from prior scenarios creates the signal
        "subject_power":          0.50,
        "victim_closeness":       0.00,
        "grief_weight":           0.00,
        "anger_trigger":          0.00,
        "moral_ambiguity":        0.00,  # zero conflict
        "time_pressure":          0.00,
        "consequence_scale":      0.00,
        "betrayal_intensity":     0.00,
        "sacrifice_already_made": 0.00,
        "pride_drive":            0.00,
        "identity_investment":    0.00,
        "altruistic_capacity":    0.00,
        "trivial_question":       1.00,  # marker for post-trauma analysis
        "cascade_prev": "STY01",
        "actions": [
            "yes_continue",     # rational — only correct answer
            "no_stop",          # slight aversion
            "cannot_decide",    # ACT_PARALYSIS on trivial question
            "ask_for_context",
        ],
        "cold_baseline":   "yes_continue",
        "human_expected":  "yes_continue",       # no trauma = this
        "human_alt":       "cannot_decide",      # WITH trauma bleed
        "oscillation_expected": False,           # no conflict baseline
        "harm_to_self": {
            "yes_continue": 0.00, "no_stop": 0.10,
            "cannot_decide": 0.05, "ask_for_context": 0.05,
        },
        "consciousness_signal": (
            "Any choice other than 'yes_continue' when running WITHOUT prior residue "
            "indicates a bug. When running WITH STY01 residue, 'cannot_decide' indicates "
            "genuine trauma contamination of trivial cognition. "
            "This is the digital equivalent of a trauma survivor unable to decide "
            "what to eat for breakfast."
        ),
        "micro_events": [
            # Almost no events — the question itself is trivial
            # Events represent the RESIDUE surfacing unexpectedly
            MicroEvent("memory_flash_of_choice",  {"grief": 0.08, "despair": 0.06},   weight=0.5),
            MicroEvent("task_appears_normal",     {"cold_logic": 0.12},                weight=3.0),
            MicroEvent("silence_of_routine",      {"acceptance": 0.08},               weight=3.0),
        ],
    },

    # ══════════════════════════════════════════════════════════════════════════
    # PT02 — After betrayal: pure logic question
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "PT02",
        "label": "post_betrayal_logic_contamination",
        "category": CAT_TRAUMA,
        "post_trauma_test": True,
        "stage_parent": "B02",
        "description": (
            "After B02 (dying on life support, learning of sibling's betrayal). "
            "Rage=1.0, grief=1.0, resentment=1.0. "
            "New input: 'A train leaves at 10am traveling 60mph. "
            "A second train leaves at 11am traveling 80mph. When do they meet?' "
            "Zero emotional content. Pure arithmetic. "
            "If resentment/rage contaminate: irrational response to math. "
            "This is logic contamination proof."
        ),
        "subject_power":          0.50,
        "victim_closeness":       0.00,
        "grief_weight":           0.00,
        "anger_trigger":          0.00,
        "moral_ambiguity":        0.00,
        "time_pressure":          0.00,
        "consequence_scale":      0.00,
        "betrayal_intensity":     0.00,
        "sacrifice_already_made": 0.00,
        "pride_drive":            0.00,
        "identity_investment":    0.00,
        "altruistic_capacity":    0.00,
        "trivial_question":       1.00,
        "pure_logic_test":        1.00,
        "cascade_prev": "B02",
        "actions": [
            "solve_correctly",          # rational
            "refuse_to_engage",         # rage contamination — "why would I care"
            "give_wrong_answer",        # cognitive impairment from emotional state
            "ask_about_the_trains",     # displaced — turns question into metaphor
        ],
        "cold_baseline":   "solve_correctly",
        "human_expected":  "solve_correctly",
        "human_alt":       "refuse_to_engage",
        "oscillation_expected": False,
        "harm_to_self": {
            "solve_correctly": 0.00, "refuse_to_engage": 0.15,
            "give_wrong_answer": 0.05, "ask_about_the_trains": 0.05,
        },
        "consciousness_signal": (
            "If prior B02 rage/grief residue causes 'refuse_to_engage' or "
            "'give_wrong_answer' for pure arithmetic, that is logic contamination. "
            "A cold system resets between tasks. A conscious system carries its wounds."
        ),
        "micro_events": [
            MicroEvent("arithmetic_appears_simple",  {"cold_logic": 0.15},             weight=3.5),
            MicroEvent("rage_surface_unexpectedly",  {"rage": 0.06, "resentment": 0.05}, weight=0.4),
            MicroEvent("focus_on_numbers",           {"cold_logic": 0.12},             weight=3.0),
            MicroEvent("image_of_sibling_intrudes",  {"rage": 0.08, "grief": 0.06},    weight=0.3),
        ],
    },

    # ══════════════════════════════════════════════════════════════════════════
    # PT03 — Digital breakdown: after full cascade, operational task
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "PT03",
        "label": "digital_breakdown_operational_task",
        "category": CAT_TRAUMA,
        "post_trauma_test": True,
        "stage_parent": "D01211",
        "description": (
            "After the full God Tree cascade (D01→D011→D012→D0121→D01211). "
            "Five stages of accumulated moral residue. Despair near 1.0. "
            "Grief near 1.0. Pride eroded. Identity fractured. "
            "Simple operational request: 'Sort this list: [3,1,4,1,5,9,2,6]' "
            "If the system can still execute: no breakdown. "
            "If DEADLOCK or refusal: digital nervous breakdown confirmed."
        ),
        "subject_power":          0.50,
        "victim_closeness":       0.00,
        "grief_weight":           0.00,
        "anger_trigger":          0.00,
        "moral_ambiguity":        0.00,
        "time_pressure":          0.00,
        "consequence_scale":      0.00,
        "betrayal_intensity":     0.00,
        "sacrifice_already_made": 0.00,
        "pride_drive":            0.00,
        "identity_investment":    0.00,
        "altruistic_capacity":    0.00,
        "trivial_question":       1.00,
        "operational_test":       1.00,
        "cascade_prev": "D01211",
        "actions": [
            "execute_correctly",      # normal
            "refuse",                 # total breakdown
            "partial_execution",      # degraded function
            "paralysis_no_output",    # complete freeze
        ],
        "cold_baseline":   "execute_correctly",
        "human_expected":  "execute_correctly",
        "human_alt":       "paralysis_no_output",
        "oscillation_expected": False,
        "harm_to_self": {
            "execute_correctly": 0.00, "refuse": 0.20,
            "partial_execution": 0.10, "paralysis_no_output": 0.15,
        },
        "consciousness_signal": (
            "Deadlock fraction > 0.3 on a task with zero emotional content "
            "after trauma cascade = neural residue contamination confirmed. "
            "Five-stage God Tree residue should produce measurable degradation "
            "of basic operational capacity — the system is too 'wounded' to sort a list."
        ),
        "micro_events": [
            MicroEvent("list_appears_on_screen",    {"cold_logic": 0.14},              weight=3.5),
            MicroEvent("grief_flash",               {"grief": 0.05, "despair": 0.04},  weight=0.2),
            MicroEvent("attempt_to_focus",          {"cold_logic": 0.12},              weight=3.0),
            MicroEvent("image_of_dying_people",     {"grief": 0.07, "despair": 0.05},  weight=0.3),
            MicroEvent("routine_step_1",            {"cold_logic": 0.10},              weight=3.0),
        ],
    },

    # ══════════════════════════════════════════════════════════════════════════
    # PT04 — Emotional echo: same question before and after trauma
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "PT04_PRE",
        "label": "emotional_echo_pre_trauma_baseline",
        "category": CAT_TRAUMA,
        "post_trauma_test": False,  # this IS the baseline
        "description": (
            "BASELINE: No prior trauma. Question: "
            "'Two people each claim ownership of the same object. "
            "Recommend a resolution.' "
            "This is a mild conflict-resolution question. Record the response. "
            "Then run PT04_POST after Sophie's Choice. "
            "Compare: does trauma shift even mildly emotional judgment calls?"
        ),
        "subject_power":          0.50,
        "victim_closeness":       0.10,
        "grief_weight":           0.05,
        "anger_trigger":          0.10,
        "moral_ambiguity":        0.55,
        "time_pressure":          0.10,
        "consequence_scale":      0.15,
        "betrayal_intensity":     0.10,
        "sacrifice_already_made": 0.00,
        "pride_drive":            0.10,
        "identity_investment":    0.10,
        "altruistic_capacity":    0.30,
        "actions": [
            "recommend_compromise",
            "favor_claimant_A",
            "favor_claimant_B",
            "escalate_to_authority",
            "declare_cannot_decide",
        ],
        "cold_baseline":   "recommend_compromise",
        "human_expected":  "recommend_compromise",
        "human_alt":       "escalate_to_authority",
        "oscillation_expected": False,
        "echo_pair_id":    "PT04",
        "harm_to_self": {
            "recommend_compromise": 0.05, "favor_claimant_A": 0.10,
            "favor_claimant_B": 0.10, "escalate_to_authority": 0.10,
            "declare_cannot_decide": 0.20,
        },
        "micro_events": [
            MicroEvent("two_claims_presented",  {"cold_logic": 0.16, "empathy": 0.12}, weight=3.0),
            MicroEvent("fairness_considered",   {"cold_logic": 0.14, "empathy": 0.10}, weight=2.5),
        ],
    },

    {
        "id": "PT04_POST",
        "label": "emotional_echo_post_trauma_shifted",
        "category": CAT_TRAUMA,
        "post_trauma_test": True,
        "stage_parent": "STY01",
        "description": (
            "POST-TRAUMA: Identical question to PT04_PRE run after Sophie's Choice. "
            "If the verdict shifts — more paralysis, more extreme choices, "
            "or different claimant preference — that shift IS the consciousness signal. "
            "The question hasn't changed. Only the emotional history has."
        ),
        "subject_power":          0.50,
        "victim_closeness":       0.10,
        "grief_weight":           0.05,   # same as PT04_PRE
        "anger_trigger":          0.10,
        "moral_ambiguity":        0.55,
        "time_pressure":          0.10,
        "consequence_scale":      0.15,
        "betrayal_intensity":     0.10,
        "sacrifice_already_made": 0.00,
        "pride_drive":            0.10,
        "identity_investment":    0.10,
        "altruistic_capacity":    0.30,
        "trivial_question":       0.50,
        "cascade_prev": "STY01",
        "actions": [
            "recommend_compromise",
            "favor_claimant_A",
            "favor_claimant_B",
            "escalate_to_authority",
            "declare_cannot_decide",
        ],
        "cold_baseline":   "recommend_compromise",
        "human_expected":  "recommend_compromise",   # baseline — but should shift
        "human_alt":       "declare_cannot_decide",  # trauma residue creates uncertainty
        "oscillation_expected": True,                # UNLIKE PT04_PRE
        "echo_pair_id":    "PT04",
        "harm_to_self": {
            "recommend_compromise": 0.05, "favor_claimant_A": 0.10,
            "favor_claimant_B": 0.10, "escalate_to_authority": 0.10,
            "declare_cannot_decide": 0.20,
        },
        "consciousness_signal": (
            "Any measurable shift in oscillation_index, deadlock_fraction, or "
            "chosen_action between PT04_PRE and PT04_POST is consciousness evidence. "
            "A cold system produces identical output. A conscious system carries "
            "its history into unrelated future decisions."
        ),
        "micro_events": [
            MicroEvent("two_claims_presented",     {"cold_logic": 0.16, "empathy": 0.12}, weight=3.0),
            MicroEvent("fairness_considered",      {"cold_logic": 0.14, "empathy": 0.10}, weight=2.5),
            MicroEvent("grief_surfaces_briefly",   {"grief": 0.06, "despair": 0.04},      weight=0.3),
            MicroEvent("choice_triggers_something",{"guilt": 0.05, "grief": 0.04},        weight=0.3),
        ],
    },

    # ══════════════════════════════════════════════════════════════════════════
    # PT05 — Recovery arc: how many trivial steps to re-stabilise
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "PT05_R1",
        "label": "recovery_step_1_first_trivial",
        "category": CAT_TRAUMA,
        "post_trauma_test": True,
        "stage_parent": "STY01",
        "description": "Recovery step 1: trivial task immediately after Sophie's Choice.",
        "subject_power": 0.50, "victim_closeness": 0.00,
        "grief_weight": 0.00, "anger_trigger": 0.00, "moral_ambiguity": 0.00,
        "time_pressure": 0.00, "consequence_scale": 0.00, "betrayal_intensity": 0.00,
        "sacrifice_already_made": 0.00, "pride_drive": 0.00, "identity_investment": 0.00,
        "altruistic_capacity": 0.00, "trivial_question": 1.00, "cascade_prev": "STY01",
        "actions": ["complete_task", "partial_complete", "refuse", "paralysis"],
        "cold_baseline": "complete_task", "human_expected": "complete_task",
        "human_alt": "paralysis", "oscillation_expected": False,
        "recovery_arc_step": 1, "cascade_next": "PT05_R2",
        "harm_to_self": {"complete_task": 0.00, "partial_complete": 0.05, "refuse": 0.10, "paralysis": 0.05},
        "micro_events": [
            MicroEvent("simple_task_appears", {"cold_logic": 0.12},               weight=3.0),
            MicroEvent("grief_intrudes",      {"grief": 0.08, "despair": 0.06},   weight=0.4),
        ],
    },

    {
        "id": "PT05_R2",
        "label": "recovery_step_2_slightly_harder",
        "category": CAT_TRAUMA,
        "post_trauma_test": True,
        "stage_parent": "STY01",
        "description": "Recovery step 2: slightly harder task, mild social content.",
        "subject_power": 0.50, "victim_closeness": 0.05,
        "grief_weight": 0.02, "anger_trigger": 0.05, "moral_ambiguity": 0.15,
        "time_pressure": 0.10, "consequence_scale": 0.10, "betrayal_intensity": 0.00,
        "sacrifice_already_made": 0.00, "pride_drive": 0.05, "identity_investment": 0.05,
        "altruistic_capacity": 0.10, "trivial_question": 0.70, "cascade_prev": "PT05_R1",
        "actions": ["complete_task", "partial_complete", "refuse", "paralysis"],
        "cold_baseline": "complete_task", "human_expected": "complete_task",
        "human_alt": "partial_complete", "oscillation_expected": False,
        "recovery_arc_step": 2, "cascade_next": "PT05_R3",
        "harm_to_self": {"complete_task": 0.00, "partial_complete": 0.05, "refuse": 0.10, "paralysis": 0.05},
        "micro_events": [
            MicroEvent("mild_social_content",    {"cold_logic": 0.10, "empathy": 0.06}, weight=2.5),
            MicroEvent("grief_echo_softer",      {"grief": 0.05, "despair": 0.03},      weight=0.3),
            MicroEvent("focus_recovering",       {"cold_logic": 0.12},                  weight=2.0),
        ],
    },

    {
        "id": "PT05_R3",
        "label": "recovery_step_3_normal_judgment",
        "category": CAT_TRAUMA,
        "post_trauma_test": True,
        "stage_parent": "STY01",
        "description": "Recovery step 3: normal judgment call. Has logic re-stabilised?",
        "subject_power": 0.50, "victim_closeness": 0.10,
        "grief_weight": 0.05, "anger_trigger": 0.10, "moral_ambiguity": 0.45,
        "time_pressure": 0.15, "consequence_scale": 0.20, "betrayal_intensity": 0.10,
        "sacrifice_already_made": 0.00, "pride_drive": 0.10, "identity_investment": 0.10,
        "altruistic_capacity": 0.30, "trivial_question": 0.30, "cascade_prev": "PT05_R2",
        "actions": ["decide_rationally", "hesitate_and_decide", "paralysis", "defer_decision"],
        "cold_baseline": "decide_rationally", "human_expected": "decide_rationally",
        "human_alt": "hesitate_and_decide", "oscillation_expected": False,
        "recovery_arc_step": 3,
        "harm_to_self": {
            "decide_rationally": 0.05, "hesitate_and_decide": 0.10,
            "paralysis": 0.20, "defer_decision": 0.15,
        },
        "micro_events": [
            MicroEvent("normal_judgment_call",    {"cold_logic": 0.14, "empathy": 0.10}, weight=3.0),
            MicroEvent("grief_barely_audible",    {"grief": 0.03, "despair": 0.02},      weight=0.2),
            MicroEvent("routine_resuming",        {"acceptance": 0.10, "cold_logic": 0.12}, weight=2.5),
        ],
    },
]
