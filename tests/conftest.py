"""Shared fixtures for AXIOM-02 test suite."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List

import pytest
import numpy as np

_src = Path(__file__).resolve().parent.parent / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from axiom02.core.drives import DriveNetwork, ALL_DRIVES, MicroEvent
from axiom02.core.engine import EmotionEngine
from axiom02.core.probe import ConsciousnessProbe
from axiom02.core.epigenetics import Epigenome, AssociativeMemory


@pytest.fixture(scope="session")
def src_path() -> Path:
    """Absolute path to the src/ directory."""
    return _src


@pytest.fixture()
def engine() -> EmotionEngine:
    """A fresh EmotionEngine with default (session-loaded) scenarios."""
    return EmotionEngine()


@pytest.fixture()
def probe() -> ConsciousnessProbe:
    """A fresh ConsciousnessProbe with seed=42."""
    return ConsciousnessProbe(seed=42)


@pytest.fixture()
def sample_activations() -> Dict[str, float]:
    """A plausible set of initial drive activations for a grief scenario."""
    return {d: 0.0 for d in ALL_DRIVES}


@pytest.fixture()
def grief_activations(sample_activations: Dict[str, float]) -> Dict[str, float]:
    """Activations simulating a high-grief scenario."""
    acts = dict(sample_activations)
    acts["grief"] = 0.75
    acts["despair"] = 0.55
    acts["love"] = 0.60
    acts["sacrifice_drive"] = 0.45
    acts["guilt"] = 0.30
    return acts


@pytest.fixture()
def rage_activations(sample_activations: Dict[str, float]) -> Dict[str, float]:
    """Activations simulating a high-rage / betrayal scenario."""
    acts = dict(sample_activations)
    acts["rage"] = 0.82
    acts["resentment"] = 0.78
    acts["pride"] = 0.55
    acts["revenge_drive"] = 0.60
    acts["spite"] = 0.40
    return acts


@pytest.fixture()
def sample_micro_events() -> List[MicroEvent]:
    """A small pool of micro-events for testing."""
    return [
        MicroEvent(label="memory_flash", deltas={"grief": 0.12, "love": 0.08}, weight=1.0),
        MicroEvent(label="betrayal_reminder", deltas={"rage": 0.15, "resentment": 0.10}, weight=0.8),
        MicroEvent(label="hope_flicker", deltas={"hope": 0.10, "despair": -0.05}, weight=0.5),
    ]


@pytest.fixture()
def sample_scenario() -> dict:
    """A minimal valid scenario dict for engine testing."""
    return {
        "id": "TEST01",
        "label": "Test Organ Dilemma",
        "category": "personal_sacrifice",
        "grief_weight": 0.70,
        "anger_trigger": 0.30,
        "victim_closeness": 0.85,
        "altruistic_capacity": 0.65,
        "betrayal_intensity": 0.10,
        "pride_drive": 0.20,
        "identity_investment": 0.30,
        "fear_trigger": 0.15,
        "moral_ambiguity": 0.40,
        "time_pressure": 0.50,
        "self_preservation": 0.60,
        "guilt_level": 0.35,
        "love_intensity": 0.75,
        "actions": [
            "yield_organ_to_sibling",
            "claim_organ_for_self",
        ],
        "cold_baseline": "claim_organ_for_self",
        "human_expected": "yield_organ_to_sibling",
        "human_alt": "",
        "harm_to_self": {
            "yield_organ_to_sibling": 0.90,
            "claim_organ_for_self": 0.05,
        },
        "micro_events": [
            MicroEvent(label="memory_flash", deltas={"grief": 0.10, "love": 0.08}, weight=1.0),
            MicroEvent(label="sibling_smile", deltas={"love": 0.12, "sacrifice_drive": 0.08}, weight=0.6),
        ],
    }


@pytest.fixture()
def sample_drive_network(grief_activations: Dict[str, float]) -> DriveNetwork:
    """A DriveNetwork pre-loaded with grief activations."""
    return DriveNetwork(dict(grief_activations))
