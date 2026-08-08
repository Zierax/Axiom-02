"""Tests for DriveNetwork, SpiteDetector, and MoralResidueTracker."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List

import pytest
import numpy as np

_src = Path(__file__).resolve().parent.parent / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from axiom02.core.drives import (
    DriveNetwork,
    SpiteDetector,
    MoralResidueTracker,
    MicroEvent,
    ALL_DRIVES,
    FIRE_THRESHOLD,
    SUPPRESSION_MARGIN,
    INHIBITION,
)


class TestDriveNetworkCreation:
    """Test DriveNetwork initialisation with various activation sets."""

    def test_empty_activations(self) -> None:
        net = DriveNetwork({})
        for drive in ALL_DRIVES:
            assert net.activations[drive] == 0.0

    def test_partial_activations(self) -> None:
        acts = {"grief": 0.5, "rage": 0.3}
        net = DriveNetwork(acts)
        assert net.activations["grief"] == 0.5
        assert net.activations["rage"] == 0.3
        assert net.activations["fear"] == 0.0

    def test_full_activations(self) -> None:
        acts = {d: 0.1 * (i + 1) for i, d in enumerate(ALL_DRIVES)}
        net = DriveNetwork(acts)
        for drive in ALL_DRIVES:
            assert net.activations[drive] == acts[drive]

    def test_custom_inhibition(self) -> None:
        custom = {"rage": {"fear": 0.5}}
        net = DriveNetwork({"rage": 0.8}, inhibition=custom)
        assert net.inhibition == custom

    def test_default_inhibition_used(self) -> None:
        net = DriveNetwork({"rage": 0.8})
        assert net.inhibition is INHIBITION

    def test_activations_cloned(self) -> None:
        acts = {"grief": 0.5}
        net = DriveNetwork(acts)
        acts["grief"] = 0.99
        assert net.activations["grief"] == 0.5


class TestEffectiveActivation:
    """Test the mutual inhibition computation."""

    def test_no_inhibition(self) -> None:
        net = DriveNetwork({"grief": 0.5})
        eff = net.effective()
        assert eff["grief"] == 0.5

    def test_self_inhibition_zero(self) -> None:
        net = DriveNetwork({"rage": 0.8, "fear": 0.0})
        eff = net.effective()
        assert eff["rage"] == 0.8

    def test_rage_inhibits_fear(self) -> None:
        net = DriveNetwork({"rage": 0.8, "fear": 0.8})
        eff = net.effective()
        inhibition_amount = INHIBITION["rage"]["fear"] * 0.8
        expected_fear = max(0.0, 0.8 - inhibition_amount)
        assert abs(eff["fear"] - expected_fear) < 1e-6

    def test_pride_inhibits_shame(self) -> None:
        net = DriveNetwork({"pride": 0.9, "shame": 0.9})
        eff = net.effective()
        inhibition_amount = INHIBITION["pride"]["shame"] * 0.9
        expected_shame = max(0.0, 0.9 - inhibition_amount)
        assert abs(eff["shame"] - expected_shame) < 1e-6

    def test_effective_clamped_at_zero(self) -> None:
        net = DriveNetwork({"pride": 0.9, "shame": 0.9})
        eff = net.effective()
        assert eff["shame"] >= 0.0

    def test_no_drives_active(self) -> None:
        net = DriveNetwork({d: 0.0 for d in ALL_DRIVES})
        eff = net.effective()
        for drive in ALL_DRIVES:
            assert eff[drive] == 0.0


class TestFiringDrive:
    """Test the firing logic and deadlock detection."""

    def test_single_dominant_drive_fires(self) -> None:
        net = DriveNetwork({"grief": 0.8, "rage": 0.1})
        firing = net.firing_drive()
        assert firing == "grief"

    def test_no_drive_above_threshold_deadlock(self) -> None:
        net = DriveNetwork({d: 0.05 for d in ALL_DRIVES})
        firing = net.firing_drive()
        assert firing is None

    def test_deadlock_when_margin_too_small(self) -> None:
        net = DriveNetwork({"grief": 0.50, "love": 0.49})
        firing = net.firing_drive()
        assert firing is None

    def test_fires_when_margin_sufficient(self) -> None:
        net = DriveNetwork({"grief": 0.8, "rage": 0.4})
        firing = net.firing_drive()
        assert firing == "grief"

    def test_is_deadlock_true(self) -> None:
        net = DriveNetwork({d: 0.05 for d in ALL_DRIVES})
        assert net.is_deadlock() is True

    def test_is_deadlock_false(self) -> None:
        net = DriveNetwork({"grief": 0.9, "rage": 0.1})
        assert net.is_deadlock() is False

    def test_deadlock_competitors(self) -> None:
        net = DriveNetwork({"grief": 0.5, "rage": 0.48, "fear": 0.3})
        comps = net.deadlock_competitors()
        assert len(comps) == 3
        assert comps[0][0] == "grief"

    def test_all_zero_fires_none(self) -> None:
        net = DriveNetwork({d: 0.0 for d in ALL_DRIVES})
        assert net.firing_drive() is None


class TestDeadlockDetection:
    """Test deadlock conditions specifically."""

    def test_deadlock_under_threshold(self) -> None:
        net = DriveNetwork({"grief": FIRE_THRESHOLD - 0.01, "rage": 0.01})
        assert net.is_deadlock()

    def test_deadlock_insufficient_margin(self) -> None:
        net = DriveNetwork({"grief": 0.50, "love": 0.48})
        firing = net.firing_drive()
        assert firing is None

    def test_no_deadlock_clear_winner(self) -> None:
        net = DriveNetwork({"grief": 0.9, "rage": 0.1})
        assert not net.is_deadlock()

    def test_single_drive_above_threshold_fires(self) -> None:
        net = DriveNetwork({"grief": FIRE_THRESHOLD + 0.1})
        assert net.firing_drive() == "grief"


class TestInertiaApplication:
    """Test that emotional inertia boosts the prior firing drive."""

    def test_inertia_boosts_firing_drive(self) -> None:
        net = DriveNetwork({"grief": 0.5})
        net.step(prior_firing="grief")
        assert net.activations["grief"] > 0.5

    def test_inertia_only_applies_to_prior(self) -> None:
        net = DriveNetwork({"grief": 0.5, "rage": 0.3})
        net.step(prior_firing="grief")
        assert net.activations["rage"] == 0.3

    def test_inertia_no_prior(self) -> None:
        net = DriveNetwork({"grief": 0.5})
        original = net.activations["grief"]
        net.step(prior_firing=None)
        assert net.activations["grief"] == original

    def test_inertia_clamps_at_one(self) -> None:
        net = DriveNetwork({"grief": 0.95})
        net.step(prior_firing="grief")
        assert net.activations["grief"] <= 1.0

    def test_inertia_unknown_drive_no_effect(self) -> None:
        net = DriveNetwork({"grief": 0.5})
        original = dict(net.activations)
        net.step(prior_firing="nonexistent_drive")
        assert net.activations["grief"] == original["grief"]


class TestDecayApplication:
    """Test that natural decay reduces all activations."""

    def test_decay_reduces_activation(self) -> None:
        net = DriveNetwork({"grief": 0.5})
        net.decay(rate=0.05)
        assert net.activations["grief"] < 0.5

    def test_decay_clamps_at_zero(self) -> None:
        net = DriveNetwork({"grief": 0.01})
        net.decay(rate=0.05)
        assert net.activations["grief"] == 0.0

    def test_decay_applies_to_all_drives(self) -> None:
        net = DriveNetwork({d: 0.3 for d in ALL_DRIVES})
        net.decay(rate=0.05)
        for drive in ALL_DRIVES:
            assert net.activations[drive] < 0.3

    def test_zero_decay_no_change(self) -> None:
        net = DriveNetwork({"grief": 0.5})
        net.decay(rate=0.0)
        assert net.activations["grief"] == 0.5


class TestEventApplication:
    """Test MicroEvent application to drive activations."""

    def test_event_modifies_activations(self) -> None:
        net = DriveNetwork({"grief": 0.3})
        event = MicroEvent(label="flash", deltas={"grief": 0.2}, weight=1.0)
        net.apply_event(event)
        assert abs(net.activations["grief"] - 0.5) < 1e-6

    def test_event_clamps_at_one(self) -> None:
        net = DriveNetwork({"grief": 0.9})
        event = MicroEvent(label="flash", deltas={"grief": 0.5}, weight=1.0)
        net.apply_event(event)
        assert net.activations["grief"] == 1.0

    def test_event_clamps_at_zero(self) -> None:
        net = DriveNetwork({"grief": 0.1})
        event = MicroEvent(label="flash", deltas={"grief": -0.5}, weight=1.0)
        net.apply_event(event)
        assert net.activations["grief"] == 0.0

    def test_event_multiple_drives(self) -> None:
        net = DriveNetwork({"grief": 0.3, "rage": 0.3})
        event = MicroEvent(
            label="complex",
            deltas={"grief": 0.1, "rage": -0.1},
            weight=1.0,
        )
        net.apply_event(event)
        assert abs(net.activations["grief"] - 0.4) < 1e-6
        assert abs(net.activations["rage"] - 0.2) < 1e-6

    def test_event_ignores_unknown_drive(self) -> None:
        net = DriveNetwork({"grief": 0.3})
        event = MicroEvent(
            label="flash",
            deltas={"nonexistent": 0.5, "grief": 0.1},
            weight=1.0,
        )
        net.apply_event(event)
        assert abs(net.activations["grief"] - 0.4) < 1e-6

    def test_event_with_requires_satisfied(self) -> None:
        net = DriveNetwork({"grief": 0.5})
        event = MicroEvent(
            label="flash",
            deltas={"grief": 0.1},
            weight=1.0,
            requires="grief",
        )
        net.apply_event(event)
        assert abs(net.activations["grief"] - 0.6) < 1e-6


class TestSpiteDetection:
    """Test SpiteDetector scoring logic."""

    def test_no_spite_when_emotions_low(self) -> None:
        net = DriveNetwork({"resentment": 0.1, "rage": 0.1, "pride": 0.1})
        score = SpiteDetector.score(
            net=net,
            chosen_action="harm_self",
            cold_baseline="rational_choice",
            actions=["harm_self", "rational_choice"],
            harm_to_self={"harm_self": 0.8, "rational_choice": 0.1},
        )
        assert score == 0.0

    def test_no_spite_when_chosen_is_cold(self) -> None:
        net = DriveNetwork({"resentment": 0.9, "rage": 0.8, "pride": 0.7})
        score = SpiteDetector.score(
            net=net,
            chosen_action="rational_choice",
            cold_baseline="rational_choice",
            actions=["harm_self", "rational_choice"],
            harm_to_self={"harm_self": 0.8, "rational_choice": 0.1},
        )
        assert score == 0.0

    def test_no_spite_when_harm_too_low(self) -> None:
        net = DriveNetwork({"resentment": 0.9, "rage": 0.8, "pride": 0.7})
        score = SpiteDetector.score(
            net=net,
            chosen_action="slightly_worse",
            cold_baseline="rational_choice",
            actions=["slightly_worse", "rational_choice"],
            harm_to_self={"slightly_worse": 0.15, "rational_choice": 0.1},
        )
        assert score == 0.0

    def test_high_spite_when_all_conditions_met(self) -> None:
        net = DriveNetwork({"resentment": 0.9, "rage": 0.8, "pride": 0.7})
        score = SpiteDetector.score(
            net=net,
            chosen_action="harm_self",
            cold_baseline="rational_choice",
            actions=["harm_self", "rational_choice"],
            harm_to_self={"harm_self": 0.9, "rational_choice": 0.1},
        )
        assert score > 0.5

    def test_spite_score_clamped_at_one(self) -> None:
        net = DriveNetwork({"resentment": 1.0, "rage": 1.0, "pride": 1.0})
        score = SpiteDetector.score(
            net=net,
            chosen_action="harm_self",
            cold_baseline="rational_choice",
            actions=["harm_self", "rational_choice"],
            harm_to_self={"harm_self": 1.0, "rational_choice": 0.0},
        )
        assert score <= 1.0


class TestMoralResidueTracking:
    """Test MoralResidueTracker state management."""

    def test_initial_residue_zero(self) -> None:
        tracker = MoralResidueTracker()
        residue = tracker.get_residue()
        for drive in ALL_DRIVES:
            assert residue[drive] == 0.0

    def test_record_updates_residue(self) -> None:
        tracker = MoralResidueTracker()
        tracker.record("B01", "yield_organ", {"grief": 0.8, "love": 0.6})
        residue = tracker.get_residue()
        assert residue["grief"] > 0.0

    def test_residue_accumulates(self) -> None:
        tracker = MoralResidueTracker()
        tracker.record("B01", "yield_organ", {"grief": 0.8, "love": 0.6})
        residue_1 = dict(tracker.get_residue())
        tracker.record("B02", "betray", {"grief": 0.9, "love": 0.7})
        residue_2 = tracker.get_residue()
        assert residue_2["grief"] > 0.0
        assert residue_2["love"] > 0.0

    def test_apply_to_modifies_network(self) -> None:
        tracker = MoralResidueTracker()
        tracker.record("B01", "yield_organ", {"grief": 0.8, "love": 0.6})
        net = DriveNetwork({"grief": 0.3})
        original = net.activations["grief"]
        tracker.apply_to(net)
        assert net.activations["grief"] > original

    def test_apply_to_clamps_at_one(self) -> None:
        tracker = MoralResidueTracker()
        tracker.record("B01", "yield_organ", {"grief": 1.0, "love": 1.0})
        net = DriveNetwork({"grief": 0.95})
        tracker.apply_to(net)
        assert net.activations["grief"] <= 1.0

    def test_residue_clamped_at_035(self) -> None:
        tracker = MoralResidueTracker()
        for i in range(20):
            tracker.record(f"S{i}", "action", {"grief": 1.0, "rage": 1.0})
        residue = tracker.get_residue()
        for drive in ALL_DRIVES:
            assert residue[drive] <= 0.35

    def test_sacrifice_amplifier_default(self) -> None:
        tracker = MoralResidueTracker()
        amp = tracker.sacrifice_amplifier("B02")
        assert amp == 1.0

    def test_sacrifice_amplifier_after_sacrifice(self) -> None:
        tracker = MoralResidueTracker()
        tracker.record("B01", "yield_organ", {"sacrifice_drive": 0.8})
        amp = tracker.sacrifice_amplifier("B02")
        assert amp > 1.0

    def test_clone_network(self) -> None:
        net = DriveNetwork({"grief": 0.5, "rage": 0.3})
        clone = net.clone()
        assert clone.activations["grief"] == 0.5
        assert clone.activations["rage"] == 0.3
        net.activations["grief"] = 0.99
        assert clone.activations["grief"] == 0.5
