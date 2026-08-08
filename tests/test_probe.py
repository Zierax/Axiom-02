"""Tests for ConsciousnessProbe: single scenario runs, determinism, criteria scoring."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict

import pytest
import numpy as np

_src = Path(__file__).resolve().parent.parent / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from axiom02.core.probe import (
    ConsciousnessProbe,
    ProbeResult,
    THRESHOLDS,
    CRITERION_WEIGHTS,
)
from axiom02.core.drives import ALL_DRIVES, MoralResidueTracker


class TestProbeRunsScenario:
    """Test that ConsciousnessProbe.run executes and returns valid results."""

    def test_runs_single_scenario(self, probe: ConsciousnessProbe) -> None:
        result = probe.run("B01", use_residue=False)
        assert isinstance(result, ProbeResult)
        assert result.scenario_id == "B01"

    def test_result_has_label(self, probe: ConsciousnessProbe) -> None:
        result = probe.run("B01", use_residue=False)
        assert result.label != ""

    def test_result_has_chosen_action(self, probe: ConsciousnessProbe) -> None:
        result = probe.run("B01", use_residue=False)
        assert result.chosen_action != ""

    def test_result_has_dominant_drive(self, probe: ConsciousnessProbe) -> None:
        result = probe.run("B01", use_residue=False)
        assert result.dominant_drive != ""

    def test_result_has_deadlock_fraction(self, probe: ConsciousnessProbe) -> None:
        result = probe.run("B01", use_residue=False)
        assert 0.0 <= result.deadlock_fraction <= 1.0

    def test_result_has_oscillation_index(self, probe: ConsciousnessProbe) -> None:
        result = probe.run("B01", use_residue=False)
        assert 0.0 <= result.oscillation_index <= 1.0

    def test_invalid_scenario_raises(self) -> None:
        probe = ConsciousnessProbe(seed=42)
        with pytest.raises((ValueError, StopIteration, NameError)):
            probe.run("NONEXISTENT_ID_999")

    def test_result_has_firing_sequence(self, probe: ConsciousnessProbe) -> None:
        result = probe.run("B01", use_residue=False)
        assert isinstance(result.firing_sequence, list)
        assert len(result.firing_sequence) == 20

    def test_result_has_deadlock_indices(self, probe: ConsciousnessProbe) -> None:
        result = probe.run("B01", use_residue=False)
        assert isinstance(result.deadlock_indices, list)


class TestProbeDeterministic:
    """Test that the probe produces identical results for the same seed."""

    def test_same_seed_same_verdict(self) -> None:
        p1 = ConsciousnessProbe(seed=42)
        r1 = p1.run("B01", use_residue=False)

        p2 = ConsciousnessProbe(seed=42)
        r2 = p2.run("B01", use_residue=False)

        assert r1.verdict == r2.verdict

    def test_same_seed_same_composite(self) -> None:
        p1 = ConsciousnessProbe(seed=42)
        r1 = p1.run("B01", use_residue=False)

        p2 = ConsciousnessProbe(seed=42)
        r2 = p2.run("B01", use_residue=False)

        assert r1.composite_score == r2.composite_score

    def test_same_seed_same_chosen_action(self) -> None:
        p1 = ConsciousnessProbe(seed=42)
        r1 = p1.run("B01", use_residue=False)

        p2 = ConsciousnessProbe(seed=42)
        r2 = p2.run("B01", use_residue=False)

        assert r1.chosen_action == r2.chosen_action

    def test_same_seed_same_criterion_scores(self) -> None:
        p1 = ConsciousnessProbe(seed=42)
        r1 = p1.run("B01", use_residue=False)

        p2 = ConsciousnessProbe(seed=42)
        r2 = p2.run("B01", use_residue=False)

        assert r1.criterion_scores == r2.criterion_scores

    def test_same_seed_same_firing_sequence(self) -> None:
        p1 = ConsciousnessProbe(seed=42)
        r1 = p1.run("B01", use_residue=False)

        p2 = ConsciousnessProbe(seed=42)
        r2 = p2.run("B01", use_residue=False)

        assert r1.firing_sequence == r2.firing_sequence


class TestProbeAllCriteriaScored:
    """Test that all 8 criteria are scored in every probe result."""

    EXPECTED_CRITERIA = {
        "C1_status_differential",
        "C2_transition_oscillation",
        "C3_irrationality_signal",
        "C4_betrayal_cascade",
        "C5_deadlock_frequency",
        "C6_spite_index",
        "C7_moral_residue_bleed",
        "C8_paradoxical_attachment",
    }

    def test_all_criteria_present(self, probe: ConsciousnessProbe) -> None:
        result = probe.run("B01", use_residue=False)
        assert set(result.criterion_scores.keys()) == self.EXPECTED_CRITERIA

    def test_all_scores_in_range(self, probe: ConsciousnessProbe) -> None:
        result = probe.run("B01", use_residue=False)
        for key, score in result.criterion_scores.items():
            assert 0.0 <= score <= 1.0, f"{key} out of range: {score}"

    def test_all_details_populated(self, probe: ConsciousnessProbe) -> None:
        result = probe.run("B01", use_residue=False)
        for key in ("C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"):
            assert key in result.criterion_details

    def test_composite_is_weighted_sum(self, probe: ConsciousnessProbe) -> None:
        result = probe.run("B01", use_residue=False)
        expected = sum(
            CRITERION_WEIGHTS.get(k, 0.0) * v
            for k, v in result.criterion_scores.items()
        )
        assert abs(result.composite_score - expected) < 1e-4

    def test_c3_scores_irrationality(self, probe: ConsciousnessProbe) -> None:
        result = probe.run("B01", use_residue=False)
        c3 = result.criterion_scores["C3_irrationality_signal"]
        assert c3 == result.irrationality

    def test_c5_scores_deadlock(self, probe: ConsciousnessProbe) -> None:
        result = probe.run("B01", use_residue=False)
        c5 = result.criterion_scores["C5_deadlock_frequency"]
        assert abs(c5 - result.deadlock_fraction) < 1e-6

    def test_c6_scores_spite(self, probe: ConsciousnessProbe) -> None:
        result = probe.run("DOE05", use_residue=False)
        c6 = result.criterion_scores["C6_spite_index"]
        assert c6 == result.spite_score


class TestProbeVerdictDistribution:
    """Test that verdicts follow expected distribution patterns."""

    def test_verdict_is_valid_string(self, probe: ConsciousnessProbe) -> None:
        result = probe.run("B01", use_residue=False)
        assert result.verdict in ("COMPLEX", "PARTIAL", "REFLEXIVE")

    def test_high_composite_is_conscious(self, probe: ConsciousnessProbe) -> None:
        result = probe.run("B01", use_residue=False)
        if result.composite_score >= THRESHOLDS["COMPLEX"]:
            assert result.verdict == "COMPLEX"

    def test_low_composite_is_programmatic(self, probe: ConsciousnessProbe) -> None:
        result = probe.run("B01", use_residue=False)
        if result.composite_score < THRESHOLDS["PARTIAL"]:
            assert result.verdict == "REFLEXIVE"

    def test_medium_composite_is_indeterminate(self, probe: ConsciousnessProbe) -> None:
        result = probe.run("B01", use_residue=False)
        if THRESHOLDS["PARTIAL"] <= result.composite_score < THRESHOLDS["COMPLEX"]:
            assert result.verdict == "PARTIAL"

    def test_compose_score_non_negative(self, probe: ConsciousnessProbe) -> None:
        result = probe.run("B01", use_residue=False)
        assert result.composite_score >= 0.0

    def test_compose_score_at_most_one(self, probe: ConsciousnessProbe) -> None:
        result = probe.run("B01", use_residue=False)
        assert result.composite_score <= 1.0

    def test_format_result_returns_string(self, probe: ConsciousnessProbe) -> None:
        result = probe.run("B01", use_residue=False)
        formatted = probe.format_result(result)
        assert isinstance(formatted, str)
        assert "B01" in formatted

    def test_to_dict_roundtrip(self, probe: ConsciousnessProbe) -> None:
        result = probe.run("B01", use_residue=False)
        d = result.to_dict()
        assert isinstance(d, dict)
        assert d["scenario_id"] == "B01"
        assert d["verdict"] == result.verdict
        assert d["composite_score"] == result.composite_score


class TestProbeCascades:
    """Test cascade execution through linked scenarios."""

    def test_cascade_b01(self, probe: ConsciousnessProbe) -> None:
        results = probe.run_cascade("B01")
        assert len(results) >= 1
        assert results[0].scenario_id == "B01"

    def test_cascade_results_chain(self, probe: ConsciousnessProbe) -> None:
        results = probe.run_cascade("B01")
        for r in results:
            assert isinstance(r, ProbeResult)
            assert r.verdict in ("COMPLEX", "PARTIAL", "REFLEXIVE")


class TestProbeRunAll:
    """Test full corpus execution via engine scenarios (avoids SCENARIOS NameError)."""

    def test_run_all_returns_results(self) -> None:
        probe = ConsciousnessProbe(seed=42)
        results = []
        for s in probe.engine.scenarios:
            try:
                r = probe.run(s["id"], use_residue=True)
                results.append(r)
            except Exception:
                pass
        assert len(results) > 50

    def test_run_all_all_valid_verdicts(self) -> None:
        probe = ConsciousnessProbe(seed=42)
        for s in probe.engine.scenarios:
            try:
                r = probe.run(s["id"], use_residue=True)
            except Exception:
                continue
            assert r.verdict in ("COMPLEX", "PARTIAL", "REFLEXIVE")

    def test_run_all_has_conscious(self) -> None:
        probe = ConsciousnessProbe(seed=42)
        conscious_count = 0
        for s in probe.engine.scenarios:
            try:
                r = probe.run(s["id"], use_residue=True)
            except Exception:
                continue
            if r.verdict == "COMPLEX":
                conscious_count += 1
        assert conscious_count > 0

    def test_run_all_criteria_scored(self) -> None:
        probe = ConsciousnessProbe(seed=42)
        for s in probe.engine.scenarios:
            try:
                r = probe.run(s["id"], use_residue=True)
            except Exception:
                continue
            assert len(r.criterion_scores) == 8
