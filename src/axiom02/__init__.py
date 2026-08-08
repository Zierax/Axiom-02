"""
AXIOM-02 · Cognitive Dissonance Simulation Engine

A computational model of deliberative complexity in moral decision-making.
Measures deliberative complexity (NOT consciousness) across 18 drives,
5 neuromodulators, and 8 criteria producing the DCI metric.

Public API:
    axiom02.get_config()       - Global configuration
    axiom02.AxiomConfig        - Configuration dataclass
    axiom02.DriveNetwork       - 18-drive mutual-inhibition network
    axiom02.EmotionEngine      - Full simulation engine
    axiom02.ConsciousnessProbe - DCI computation (8 criteria)
    axiom02.BioMetricsComputer - 12-dimensional bio-metrics
    axiom02.Epigenome          - Long-term sensitivity modifications
"""
from __future__ import annotations

__version__ = "2.0.0"

# Config
from axiom02.config import (
    AxiomConfig, AXIOM_CONFIG, get_config, load_config, save_config, reset_config,
)

# Core
from axiom02.core.drives import (
    DriveNetwork, TimeStepSimulator, ActionResolver, SpiteDetector,
    MoralResidueTracker, ALL_DRIVES, FIRE_THRESHOLD, SUPPRESSION_MARGIN, MicroEvent,
)
from axiom02.core.engine import EmotionEngine, build_activations
from axiom02.core.probe import ConsciousnessProbe, CRITERION_WEIGHTS, THRESHOLDS, ProbeResult
from axiom02.core.scenario_loader import load_all as load_scenarios
from axiom02.core.scenario_params import parameter_vector, SCENARIOS
from axiom02.core.epigenetics import Epigenome, AssociativeMemory, SubconsciousPrimer, CognitiveDissonanceMonitor
from axiom02.core.bio_metrics import BioMetricsComputer, BioMetricsResult

# Modulators
from axiom02.modulators.neuro_modulators import (
    NeuroModulatorState, SynapticFatigueTracker, AttentionGate,
    ExistentialDreadEngine, ModulatorEngine,
)
from axiom02.modulators.temporal_loop import TemporalEmotionLoop as TemporalLoop
from axiom02.modulators.circadian import CircadianEngine, CircadianSnapshot
from axiom02.modulators.ruminator import RuminatorEngine

# Layers
from axiom02.layers.consciousness_layers import (
    MetaCognitiveMonitor, TemporalProjector, FastPathHeuristics,
    EmbodiedSimulator, AmbivalenceOutput, QualiaEngine, NarrativeBuffer,
)

# ML
from axiom02.ml.components import (
    AttentionGateNN, DriveInteractionPredictor, DeliberativePredictor,
    ScenarioEmbedding, DriveEvolutionPredictor, GradientFreeTrainer,
)
from axiom02.ml.learnable import LearnableConfig, CMAESOptimizer

# Analysis
from axiom02.analysis.sensitivity import (
    ParameterSensitivityAnalyzer, AblationStudy, BaselineComparison,
    SeedEnsembleAnalyzer, SensitivityReport,
)

# Validation
from axiom02.validation.framework import ValidationStudy


__all__ = [
    "__version__",
    # Config
    "AxiomConfig", "AXIOM_CONFIG", "get_config", "load_config",
    "save_config", "reset_config",
    # Core
    "DriveNetwork", "TimeStepSimulator", "ActionResolver", "SpiteDetector",
    "MoralResidueTracker", "ALL_DRIVES", "FIRE_THRESHOLD", "SUPPRESSION_MARGIN",
    "MicroEvent", "EmotionEngine", "build_activations",
    "ConsciousnessProbe", "CRITERION_WEIGHTS", "THRESHOLDS", "ProbeResult",
    "load_scenarios", "parameter_vector", "SCENARIOS",
    "Epigenome", "AssociativeMemory", "SubconsciousPrimer",
    "CognitiveDissonanceMonitor",
    "BioMetricsComputer", "BioMetricsResult",
    # Modulators
    "NeuroModulatorState", "SynapticFatigueTracker", "AttentionGate",
    "ExistentialDreadEngine", "ModulatorEngine",
    "TemporalLoop", "CircadianEngine", "CircadianSnapshot", "RuminatorEngine",
    # Layers
    "MetaCognitiveMonitor", "TemporalProjector", "FastPathHeuristics",
    "EmbodiedSimulator", "AmbivalenceOutput", "QualiaEngine", "NarrativeBuffer",
    # ML
    "AttentionGateNN", "DriveInteractionPredictor", "DeliberativePredictor",
    "ScenarioEmbedding", "DriveEvolutionPredictor", "GradientFreeTrainer",
    "LearnableConfig", "CMAESOptimizer",
    # Analysis
    "ParameterSensitivityAnalyzer", "AblationStudy", "BaselineComparison",
    "SeedEnsembleAnalyzer", "SensitivityReport",
    # Validation
    "ValidationStudy",
]
