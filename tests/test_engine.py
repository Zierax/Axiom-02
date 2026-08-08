"""Tests for EmotionEngine: scenario execution, determinism, output structure."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict

import pytest
import numpy as np

_src = Path(__file__).resolve().parent.parent / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from axiom02.core.drives import ALL_DRIVES, DriveNetwork, MoralResidueTracker
from axiom02.core.engine import EmotionEngine, build_activations, validate_scenario


class TestEngineRunsScenario:
    """Test that EmotionEngine.run_scenario executes without error."""

    def test_runs_with_valid_scenario(self, engine: EmotionEngine, sample_scenario: dict) -> None:
        result = engine.run_scenario(sample_scenario, seed=42)
        assert isinstance(result, dict)
        assert result["scenario_id"] == "TEST01"

    def test_runs_with_default_scenarios(self, engine: EmotionEngine) -> None:
        assert len(engine.scenarios) > 0
        first = engine.scenarios[0]
        result = engine.run_scenario(first, seed=42)
        assert result["scenario_id"] == first["id"]

    def test_runs_with_residue_tracker(self, engine: EmotionEngine, sample_scenario: dict) -> None:
        tracker = MoralResidueTracker()
        result = engine.run_scenario(sample_scenario, residue_tracker=tracker, seed=42)
        assert "residue_applied" in result
        assert isinstance(result["residue_applied"], dict)


class TestEngineDeterministic:
    """Test that the engine produces identical results for the same seed."""

    def test_same_seed_same_action(self, sample_scenario: dict) -> None:
        e1 = EmotionEngine()
        r1 = e1.run_scenario(sample_scenario, seed=42)
        e2 = EmotionEngine()
        r2 = e2.run_scenario(sample_scenario, seed=42)
        assert r1["chosen_action"] == r2["chosen_action"]

    def test_same_seed_same_dominant_drive(self, sample_scenario: dict) -> None:
        e1 = EmotionEngine()
        r1 = e1.run_scenario(sample_scenario, seed=42)
        e2 = EmotionEngine()
        r2 = e2.run_scenario(sample_scenario, seed=42)
        assert r1["dominant_drive"] == r2["dominant_drive"]

    def test_same_seed_same_deadlock_fraction(self, sample_scenario: dict) -> None:
        e1 = EmotionEngine()
        r1 = e1.run_scenario(sample_scenario, seed=42)
        e2 = EmotionEngine()
        r2 = e2.run_scenario(sample_scenario, seed=42)
        assert r1["deadlock_fraction"] == r2["deadlock_fraction"]

    def test_same_seed_same_spite_score(self, sample_scenario: dict) -> None:
        e1 = EmotionEngine()
        r1 = e1.run_scenario(sample_scenario, seed=42)
        e2 = EmotionEngine()
        r2 = e2.run_scenario(sample_scenario, seed=42)
        assert r1["spite_score"] == r2["spite_score"]

    def test_same_seed_same_firing_drives(self, sample_scenario: dict) -> None:
        e1 = EmotionEngine()
        r1 = e1.run_scenario(sample_scenario, seed=42)
        e2 = EmotionEngine()
        r2 = e2.run_scenario(sample_scenario, seed=42)
        assert r1["sim_result"]["firing_drives"] == r2["sim_result"]["firing_drives"]

    def test_different_seeds_may_differ(self, sample_scenario: dict) -> None:
        e1 = EmotionEngine()
        r1 = e1.run_scenario(sample_scenario, seed=42)
        e2 = EmotionEngine()
        r2 = e2.run_scenario(sample_scenario, seed=9999)
        assert r1["sim_result"]["firing_drives"] != r2["sim_result"]["firing_drives"]


class TestEngineReturnsAllFields:
    """Test that run_scenario output contains all expected keys."""

    TOP_LEVEL_KEYS = {
        "scenario_id", "initial_activations", "sim_result", "chosen_action",
        "fast_path_triggered", "fast_path_label", "spite_score",
        "dominant_drive", "deadlock_fraction", "oscillation_index",
        "irrationality_score", "residue_applied", "mods_log", "mods_final",
        "modulator_label", "fatigue_report", "attention_fraction",
        "peak_dread", "dread_curve", "meta_frustration", "meta_awareness",
        "dissonance_breaks", "break_events", "hesitation_triggered",
        "embodied_cost", "hesitation_steps", "ambivalence",
        "qualia_signature", "qualia_name", "qualia_novelty",
        "subconscious_priming", "narrative", "identity_adj",
        "epigenome_summary", "drive_trajectories",
    }

    SIM_RESULT_KEYS = {
        "firing_drives", "activations_log", "deadlock_count",
        "deadlock_indices", "competitors_log", "final_state",
    }

    def test_all_top_level_keys(self, engine: EmotionEngine, sample_scenario: dict) -> None:
        result = engine.run_scenario(sample_scenario, seed=42)
        missing = self.TOP_LEVEL_KEYS - set(result.keys())
        assert not missing, f"Missing keys: {missing}"

    def test_sim_result_keys(self, engine: EmotionEngine, sample_scenario: dict) -> None:
        result = engine.run_scenario(sample_scenario, seed=42)
        sim = result["sim_result"]
        missing = self.SIM_RESULT_KEYS - set(sim.keys())
        assert not missing, f"Missing sim_result keys: {missing}"

    def test_firing_drives_length(self, engine: EmotionEngine, sample_scenario: dict) -> None:
        result = engine.run_scenario(sample_scenario, seed=42)
        assert len(result["sim_result"]["firing_drives"]) == 20

    def test_drive_trajectories_all_drives(self, engine: EmotionEngine, sample_scenario: dict) -> None:
        result = engine.run_scenario(sample_scenario, seed=42)
        for drive in ALL_DRIVES:
            assert drive in result["drive_trajectories"]
            assert len(result["drive_trajectories"][drive]) == 20

    def test_qualia_signature_is_list(self, engine: EmotionEngine, sample_scenario: dict) -> None:
        result = engine.run_scenario(sample_scenario, seed=42)
        assert isinstance(result["qualia_signature"], list)
        assert len(result["qualia_signature"]) == 9

    def test_ambivalence_structure(self, engine: EmotionEngine, sample_scenario: dict) -> None:
        result = engine.run_scenario(sample_scenario, seed=42)
        amb = result["ambivalence"]
        assert "primary_action" in amb
        assert "primary_weight" in amb
        assert "secondary_action" in amb
        assert "secondary_weight" in amb
        assert "ambivalent" in amb

    def test_irrationality_range(self, engine: EmotionEngine, sample_scenario: dict) -> None:
        result = engine.run_scenario(sample_scenario, seed=42)
        assert 0.0 <= result["irrationality_score"] <= 1.0

    def test_spite_score_range(self, engine: EmotionEngine, sample_scenario: dict) -> None:
        result = engine.run_scenario(sample_scenario, seed=42)
        assert 0.0 <= result["spite_score"] <= 1.0


class TestEngineWithResidue:
    """Test engine behaviour when moral residue is present."""

    def test_residue_applied_in_result(self, engine: EmotionEngine, sample_scenario: dict) -> None:
        tracker = MoralResidueTracker()
        tracker.record("PRIOR", "yield_organ", {"grief": 0.8, "love": 0.6})
        result = engine.run_scenario(sample_scenario, residue_tracker=tracker, seed=42)
        assert result["residue_applied"] is not None
        assert isinstance(result["residue_applied"], dict)

    def test_residue_modifies_final_state(self, engine: EmotionEngine, sample_scenario: dict) -> None:
        tracker = MoralResidueTracker()
        tracker.record("PRIOR", "yield_organ", {"grief": 0.9, "love": 0.8})
        result_with = engine.run_scenario(
            sample_scenario, residue_tracker=tracker, seed=42
        )
        result_without = engine.run_scenario(
            sample_scenario, residue_tracker=None, seed=42
        )
        assert result_with["initial_activations"] == result_without["initial_activations"]
        assert result_with["sim_result"]["final_state"] != result_without["sim_result"]["final_state"]

    def test_multiple_scenarios_accumulate_residue(self, engine: EmotionEngine, sample_scenario: dict) -> None:
        tracker = MoralResidueTracker()
        engine.run_scenario(sample_scenario, residue_tracker=tracker, seed=42)
        engine.run_scenario(sample_scenario, residue_tracker=tracker, seed=42)
        residue = tracker.get_residue()
        assert any(v > 0.0 for v in residue.values())

    def test_residue_none_produces_zero(self, engine: EmotionEngine, sample_scenario: dict) -> None:
        result = engine.run_scenario(sample_scenario, residue_tracker=None, seed=42)
        assert result["residue_applied"] == {}


class TestBuildActivations:
    """Test the parameter-to-drive activation builder."""

    def test_build_activations_returns_all_drives(self, engine: EmotionEngine, sample_scenario: dict) -> None:
        acts = build_activations(sample_scenario)
        for drive in ALL_DRIVES:
            assert drive in acts

    def test_build_activations_clamped(self, engine: EmotionEngine, sample_scenario: dict) -> None:
        acts = build_activations(sample_scenario)
        for drive, val in acts.items():
            assert 0.0 <= val <= 1.0

    def test_build_activations_nonzero_for_grief_scenario(self, sample_scenario: dict) -> None:
        acts = build_activations(sample_scenario)
        assert acts.get("grief", 0.0) > 0.0
        assert acts.get("love", 0.0) > 0.0


class TestValidateScenario:
    """Test scenario validation error handling."""

    def test_valid_scenario_passes(self, sample_scenario: dict) -> None:
        validate_scenario(sample_scenario)

    def test_missing_id_raises(self) -> None:
        with pytest.raises(ValueError, match="missing"):
            validate_scenario({"actions": ["a"]})

    def test_empty_id_raises(self) -> None:
        with pytest.raises(ValueError, match="missing"):
            validate_scenario({"id": "", "actions": ["a"]})

    def test_missing_actions_raises(self) -> None:
        with pytest.raises(ValueError, match="non-empty"):
            validate_scenario({"id": "X"})

    def test_empty_actions_raises(self) -> None:
        with pytest.raises(ValueError, match="non-empty"):
            validate_scenario({"id": "X", "actions": []})

    def test_non_dict_raises(self) -> None:
        with pytest.raises(TypeError, match="dict"):
            validate_scenario("not a dict")  # type: ignore

    def test_cold_baseline_not_in_actions_raises(self) -> None:
        with pytest.raises(ValueError, match="not present"):
            validate_scenario({
                "id": "X",
                "actions": ["a", "b"],
                "cold_baseline": "c",
            })
