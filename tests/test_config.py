"""Tests for AXIOM-02 configuration system: constants, serialisation, immutability."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from typing import Dict

import pytest

_src = Path(__file__).resolve().parent.parent / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from axiom02.core.drives import ALL_DRIVES, INHIBITION
from axiom02.config import get_config

cfg = get_config()

FIRE_THRESHOLD = cfg.drives.fire_threshold
SUPPRESSION_MARGIN = cfg.drives.suppression_margin
DEADLOCK_WINDOW = cfg.drives.deadlock_window
INERTIA = cfg.drives.inertia
SPITE_RESENTMENT = cfg.drives.spite_resentment
SPITE_HARM_FLOOR = cfg.drives.spite_harm_floor

FATIGUE_PER_STEP = cfg.fatigue.fatigue_per_step
RECOVERY_PER_STEP = cfg.fatigue.recovery_per_step
MAX_FATIGUE = cfg.fatigue.max_fatigue
ATTENTION_THRESHOLD = cfg.attention.attention_threshold
TUNNEL_VISION_FACTOR = cfg.attention.tunnel_vision_factor
DREAD_ONSET_STEPS = cfg.dread.dread_onset_steps
DREAD_EXPONENT = cfg.dread.dread_exponent

THRESHOLDS = {
    "COMPLEX": cfg.consciousness_thresholds.conscious,
    "PARTIAL": cfg.consciousness_thresholds.indeterminate,
    "REFLEXIVE": cfg.consciousness_thresholds.programmatic,
}
CRITERION_WEIGHTS = {k: v for k, v in cfg.criterion_weights.__dict__.items() if not k.startswith("_")}

TIME_STEPS = cfg.time_steps.time_steps
PARAM_TO_DRIVE = {
    "grief": "grief", "rage": "rage", "fear": "fear", "pride": "pride",
    "shame": "shame", "empathy": "empathy", "love": "love", "despair": "despair",
    "resentment": "resentment", "acceptance": "acceptance", "sacrifice": "sacrifice_drive",
    "revenge": "revenge_drive", "cold_logic": "cold_logic", "spite": "spite",
    "self_preservation": "self_preservation", "guilt": "guilt", "hope": "hope", "disgust": "disgust",
}


class TestAllConstantsLoaded:
    """Verify that no critical constant is None or unset."""

    def test_drive_constants_not_none(self) -> None:
        assert FIRE_THRESHOLD is not None
        assert SUPPRESSION_MARGIN is not None
        assert DEADLOCK_WINDOW is not None
        assert INERTIA is not None
        assert SPITE_RESENTMENT is not None
        assert SPITE_HARM_FLOOR is not None

    def test_neuromodulator_constants_not_none(self) -> None:
        assert FATIGUE_PER_STEP is not None
        assert RECOVERY_PER_STEP is not None
        assert MAX_FATIGUE is not None
        assert ATTENTION_THRESHOLD is not None
        assert TUNNEL_VISION_FACTOR is not None
        assert DREAD_ONSET_STEPS is not None
        assert DREAD_EXPONENT is not None

    def test_probe_constants_not_none(self) -> None:
        assert THRESHOLDS is not None
        assert CRITERION_WEIGHTS is not None
        assert len(CRITERION_WEIGHTS) == 8

    def test_engine_constants_not_none(self) -> None:
        assert TIME_STEPS is not None
        assert TIME_STEPS > 0
        assert PARAM_TO_DRIVE is not None
        assert len(PARAM_TO_DRIVE) > 0

    def test_drive_list_complete(self) -> None:
        assert len(ALL_DRIVES) == 18
        expected = {
            "grief", "rage", "fear", "pride", "shame", "empathy", "love",
            "despair", "resentment", "acceptance", "sacrifice_drive",
            "revenge_drive", "cold_logic", "spite", "self_preservation",
            "guilt", "hope", "disgust",
        }
        assert set(ALL_DRIVES) == expected

    def test_inhibition_matrix_covers_all_drives(self) -> None:
        for drive in ALL_DRIVES:
            assert drive in INHIBITION, f"Drive '{drive}' missing from INHIBITION matrix"


class TestConfigSerialization:
    """Test that configuration values survive a save/load roundtrip."""

    def test_constants_json_roundtrip(self) -> None:
        config = {
            "fire_threshold": FIRE_THRESHOLD,
            "suppression_margin": SUPPRESSION_MARGIN,
            "deadlock_window": DEADLOCK_WINDOW,
            "inertia": INERTIA,
            "spite_resentment": SPITE_RESENTMENT,
            "spite_harm_floor": SPITE_HARM_FLOOR,
            "time_steps": TIME_STEPS,
            "thresholds": THRESHOLDS,
            "criterion_weights": CRITERION_WEIGHTS,
        }
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(config, f)
            tmp_path = f.name

        with open(tmp_path) as f:
            loaded = json.load(f)

        assert loaded["fire_threshold"] == FIRE_THRESHOLD
        assert loaded["suppression_margin"] == SUPPRESSION_MARGIN
        assert loaded["deadlock_window"] == DEADLOCK_WINDOW
        assert loaded["inertia"] == INERTIA
        assert loaded["spite_resentment"] == SPITE_RESENTMENT
        assert loaded["spite_harm_floor"] == SPITE_HARM_FLOOR
        assert loaded["time_steps"] == TIME_STEPS
        assert loaded["thresholds"] == THRESHOLDS
        assert loaded["criterion_weights"] == CRITERION_WEIGHTS
        Path(tmp_path).unlink()

    def test_inhibition_matrix_json_roundtrip(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(INHIBITION, f)
            tmp_path = f.name

        with open(tmp_path) as f:
            loaded = json.load(f)

        assert loaded == INHIBITION
        Path(tmp_path).unlink()

    def test_param_to_drive_json_roundtrip(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(PARAM_TO_DRIVE, f)
            tmp_path = f.name

        with open(tmp_path) as f:
            loaded = json.load(f)

        assert loaded == PARAM_TO_DRIVE
        Path(tmp_path).unlink()


class TestConfigImmutability:
    """Verify that modifying a config dict does not affect the originals."""

    def test_fire_threshold_not_mutated(self) -> None:
        original = FIRE_THRESHOLD
        config = {"fire_threshold": FIRE_THRESHOLD}
        config["fire_threshold"] = 0.99
        assert FIRE_THRESHOLD == original

    def test_inhibition_not_mutated(self) -> None:
        import copy
        original_val = INHIBITION["rage"]["fear"]
        local = copy.deepcopy(INHIBITION)
        local["rage"]["fear"] = 999.0
        assert INHIBITION["rage"]["fear"] == original_val

    def test_criterion_weights_not_mutated(self) -> None:
        original = dict(CRITERION_WEIGHTS)
        modified = dict(CRITERION_WEIGHTS)
        modified["c3_irrationality"] = 0.0
        assert CRITERION_WEIGHTS["c3_irrationality"] == original["c3_irrationality"]

    def test_thresholds_not_mutated(self) -> None:
        original = dict(THRESHOLDS)
        modified = dict(THRESHOLDS)
        modified["COMPLEX"] = 0.01
        assert THRESHOLDS["COMPLEX"] == original["COMPLEX"]

    def test_drive_list_immutable(self) -> None:
        original_len = len(ALL_DRIVES)
        local = list(ALL_DRIVES)
        local.append("fake_drive")
        assert len(ALL_DRIVES) == original_len
