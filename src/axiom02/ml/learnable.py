"""
AXIOM-02 · LEARNABLE PARAMETER CONTAINER  v1.0

Wraps the centralized configuration system for optimization via
evolutionary algorithms (differential evolution / CMA-ES).

This enables tuning the AXIOM-02 engine against human judgment data:
given a set of (scenario, human_rating) pairs, find the parameter vector
that maximizes correlation between the engine's consciousness scores and
human ratings of literary character consciousness.

Usage
─────
  from learnable import LearnableConfig, ObjectiveFunction, CMAESOptimizer

  lc = LearnableConfig()         # loads all params from AXIOM_CONFIG
  print(f"Optimizing {lc.n_params} parameters")

  # Define human judgment data: (scenario_id, human_consciousness_rating)
  human_data = [
      ("DOE01", 0.92),   # Raskolnikov — definitely conscious
      ("DOE05", 0.88),   # Underground Man — spite signals consciousness
      ("STY01", 0.95),   # Sophie's Choice — extreme deadlock
      ("SHA01", 0.85),   # Hamlet — paralysis as consciousness
      ...
  ]

  obj = ObjectiveFunction(lc, human_data)
  optimizer = CMAESOptimizer(obj)
  optimized_config = optimizer.optimize(max_generations=100)
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import numpy as np

from axiom02.config import AxiomConfig, AXIOM_CONFIG

logger = logging.getLogger("axiom02.learnable")

__all__ = [
    "LearnableParam",
    "LearnableConfig",
    "ObjectiveFunction",
    "CMAESOptimizer",
    "quick_optimize",
]


# ──────────────────────────────────────────────────────────────────────────────
# LEARNABLE PARAMETER
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class LearnableParam:
    """A single parameter that may be subject to optimization.

    Attributes:
        name:        Dot-path identifier (e.g. "drives.fire_threshold").
        value:       Current value.
        prior_mean:  Mean of the Gaussian prior (regularization target).
        prior_std:   Standard deviation of the Gaussian prior.
        min_bound:   Hard lower bound for this parameter.
        max_bound:   Hard upper bound for this parameter.
        is_learnable: Whether this parameter is included in optimization.
    """
    name: str
    value: float
    prior_mean: float
    prior_std: float
    min_bound: float
    max_bound: float
    is_learnable: bool = True

    def clip(self) -> float:
        """Clamp value to [min_bound, max_bound]."""
        self.value = float(np.clip(self.value, self.min_bound, self.max_bound))
        return self.value


# ──────────────────────────────────────────────────────────────────────────────
# LEARNABLE PARAMETER GROUPS
# ──────────────────────────────────────────────────────────────────────────────
#
# These define which parameters from AXIOM_CONFIG are exposed for optimization
# and their reasonable bounds. The naming convention uses dot-paths to match
# the AxiomConfig dataclass hierarchy.

# Groups that are ALWAYS learnable (core dynamics)
_ALWAYS_LEARNABLE: List[Tuple[str, float, float, float, float]] = [
    # (name, default, prior_mean, prior_std, min, max)
    # Drive network
    ("drives.fire_threshold",         0.42, 0.42, 0.05, 0.25, 0.65),
    ("drives.suppression_margin",     0.07, 0.07, 0.02, 0.01, 0.20),
    ("drives.deadlock_window",        0.12, 0.12, 0.03, 0.03, 0.30),
    ("drives.inertia",                0.30, 0.30, 0.05, 0.10, 0.60),
    ("drives.spite_multiplier",       1.80, 1.80, 0.20, 1.00, 3.00),
    ("drives.default_decay_rate",     0.05, 0.05, 0.01, 0.01, 0.15),
    ("drives.step_inertia_boost",     0.30, 0.30, 0.05, 0.10, 0.60),

    # Time steps
    ("time_steps.deadlock_jitter",    0.04, 0.04, 0.01, 0.01, 0.10),
    ("time_steps.step_decay_rate",    0.03, 0.03, 0.01, 0.01, 0.10),

    # Action resolver
    ("action_resolver.spite_override_threshold",    0.55, 0.55, 0.05, 0.30, 0.80),
    ("action_resolver.deadlock_extreme_threshold",  0.50, 0.50, 0.05, 0.30, 0.70),
    ("action_resolver.deadlock_human_prob",         0.62, 0.62, 0.05, 0.30, 0.90),
    ("action_resolver.deadlock_human_alt_prob",     0.35, 0.35, 0.05, 0.10, 0.60),
    ("action_resolver.p_base_cap",                  0.78, 0.78, 0.05, 0.50, 0.95),
    ("action_resolver.p_base_scaling",              1.50, 1.50, 0.20, 0.80, 2.50),

    # Moral residue
    ("moral_residue.residue_bleed_factor",  0.25, 0.25, 0.05, 0.05, 0.50),
    ("moral_residue.residue_cap",           0.35, 0.35, 0.05, 0.10, 0.60),
    ("moral_residue.sacrifice_threshold",   0.55, 0.55, 0.05, 0.30, 0.80),
    ("moral_residue.sacrifice_amplification", 0.85, 0.85, 0.10, 0.50, 1.50),

    # Fatigue
    ("fatigue.fatigue_per_step",   0.06, 0.06, 0.01, 0.02, 0.12),
    ("fatigue.recovery_per_step",  0.08, 0.08, 0.01, 0.03, 0.15),
    ("fatigue.max_fatigue",        0.70, 0.70, 0.05, 0.40, 0.90),

    # Attention
    ("attention.attention_threshold",  0.65, 0.65, 0.05, 0.40, 0.85),
    ("attention.tunnel_vision_factor", 0.35, 0.35, 0.05, 0.10, 0.60),

    # Dread
    ("dread.dread_exponent",  2.20, 2.20, 0.20, 1.20, 3.50),
    ("dread.dread_self_preservation_spike", 0.45, 0.45, 0.05, 0.20, 0.70),
    ("dread.dread_despair_amplification",   0.35, 0.35, 0.05, 0.15, 0.60),
    ("dread.dread_hopesuppression",         0.40, 0.40, 0.05, 0.15, 0.65),

    # Modulator engine
    ("modulator_engine.modulator_engine_strength",  0.60, 0.60, 0.05, 0.30, 0.90),
    ("modulator_engine.modulator_decay_rate",       0.04, 0.04, 0.01, 0.01, 0.10),

    # Meta-cognition
    ("meta_cognition.frustration_per_deadlock_step", 0.08, 0.08, 0.01, 0.03, 0.15),
    ("meta_cognition.frustration_decay_per_fire",    0.12, 0.12, 0.02, 0.05, 0.25),
    ("meta_cognition.frustration_escalation",        0.05, 0.05, 0.01, 0.01, 0.12),

    # Consciousness thresholds
    ("consciousness_thresholds.conscious",     0.50, 0.50, 0.05, 0.30, 0.70),
    ("consciousness_thresholds.indeterminate", 0.28, 0.28, 0.05, 0.10, 0.45),

    # Criterion weights (constrained to sum to ~1.0)
    ("criterion_weights.c3_irrationality", 0.30, 0.30, 0.03, 0.15, 0.45),
    ("criterion_weights.c6_spite",         0.22, 0.22, 0.03, 0.10, 0.35),
    ("criterion_weights.c5_deadlock",      0.20, 0.20, 0.03, 0.10, 0.35),
    ("criterion_weights.c2_oscillation",   0.12, 0.12, 0.02, 0.05, 0.25),
    ("criterion_weights.c7_residue",       0.08, 0.08, 0.02, 0.02, 0.18),

    # Dissonance
    ("dissonance.dissonance_threshold", 0.72, 0.72, 0.05, 0.50, 0.90),
    ("dissonance.near_tie_gap",         0.08, 0.08, 0.02, 0.03, 0.15),

    # Narrative
    ("narrative.strong_rationalisation_threshold", 0.70, 0.70, 0.05, 0.50, 0.90),
    ("narrative.strong_identity_scaling",          0.25, 0.25, 0.03, 0.10, 0.40),

    # Temporal loop
    ("temporal_loop.alpha_persist",               0.62, 0.62, 0.05, 0.40, 0.80),
    ("temporal_loop.alpha_circ",                  0.20, 0.20, 0.03, 0.05, 0.40),
    ("temporal_loop.alpha_rumi",                  0.18, 0.18, 0.03, 0.05, 0.35),
    ("temporal_loop.cortisol_se_kappa",           0.060, 0.060, 0.010, 0.020, 0.120),
    ("temporal_loop.narrative_stability_decay",   0.85, 0.85, 0.03, 0.70, 0.95),
    ("temporal_loop.narrative_recovery_coeff",    0.16, 0.16, 0.03, 0.05, 0.30),

    # Epigenetics
    ("epigenetics.prime_threshold", 0.20, 0.20, 0.03, 0.10, 0.35),
    ("epigenetics.prime_weight",    0.18, 0.18, 0.03, 0.05, 0.35),

    # Embodied
    ("embodied.hesitation_trigger", 0.70, 0.70, 0.05, 0.40, 0.90),

    # Ambivalence
    ("ambivalence.ambivalence_threshold", 0.35, 0.35, 0.05, 0.15, 0.55),

    # Oscillation index
    ("oscillation_index.transition_weight", 0.65, 0.65, 0.05, 0.40, 0.85),
]


# ──────────────────────────────────────────────────────────────────────────────
# LEARNABLE CONFIG
# ──────────────────────────────────────────────────────────────────────────────

class LearnableConfig:
    """Wraps AXIOM_CONFIG for optimization.

    Loads all parameters from the global config, marks specific groups
    as learnable, and provides vectorized access for evolutionary algorithms.
    """

    def __init__(self, base_config: Optional[AxiomConfig] = None):
        self._config = base_config or AXIOM_CONFIG
        self._params: List[LearnableParam] = []
        self._param_index: Dict[str, int] = {}

        self._init_params()

    def _init_params(self) -> None:
        """Initialize all learnable parameters from the config."""
        for name, default, prior_mean, prior_std, min_bound, max_bound in _ALWAYS_LEARNABLE:
            value = self._resolve(name, default)
            param = LearnableParam(
                name=name,
                value=value,
                prior_mean=prior_mean,
                prior_std=prior_std,
                min_bound=min_bound,
                max_bound=max_bound,
                is_learnable=True,
            )
            self._params.append(param)
            self._param_index[name] = len(self._params) - 1

    def _resolve(self, path: str, default: float) -> float:
        """Resolve a dot-path to a value in the config."""
        parts = path.split(".")
        obj = self._config
        for part in parts:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            else:
                return default
        return float(obj) if not isinstance(obj, (int, float)) else float(obj)

    def _set(self, path: str, value: float) -> None:
        """Set a value in the config by dot-path."""
        parts = path.split(".")
        obj = self._config
        for part in parts[:-1]:
            obj = getattr(obj, part)
        setattr(obj, parts[-1], value)

    # ── Vectorized access ────────────────────────────────────────────────────

    @property
    def n_params(self) -> int:
        """Count of learnable parameters."""
        return len(self._params)

    def param_names(self) -> List[str]:
        """Names of all learnable parameters."""
        return [p.name for p in self._params]

    def to_vector(self) -> np.ndarray:
        """Flat numpy array of learnable parameter values."""
        return np.array([p.value for p in self._params], dtype=np.float64)

    def from_vector(self, vec: np.ndarray) -> None:
        """Update learnable parameters from a flat array."""
        if len(vec) != self.n_params:
            raise ValueError(
                f"Vector length {len(vec)} != n_params {self.n_params}"
            )
        for i, val in enumerate(vec):
            self._params[i].value = float(val)
            self._params[i].clip()
            self._set(self._params[i].name, self._params[i].value)

    def get_bounds(self) -> List[Tuple[float, float]]:
        """List of (min, max) for each learnable parameter."""
        return [(p.min_bound, p.max_bound) for p in self._params]

    def get_priors(self) -> Tuple[np.ndarray, np.ndarray]:
        """Return (prior_means, prior_stds) as arrays."""
        means = np.array([p.prior_mean for p in self._params], dtype=np.float64)
        stds = np.array([p.prior_std for p in self._params], dtype=np.float64)
        return means, stds

    # ── Dict access ──────────────────────────────────────────────────────────

    def to_dict(self) -> Dict[str, Any]:
        """All parameters as a nested dict (mirrors AxiomConfig structure)."""
        return self._config.to_dict()

    def from_dict(self, d: Dict[str, Any]) -> None:
        """Load parameters from a nested dict."""
        self._config = AxiomConfig.from_dict(d)
        self._params.clear()
        self._param_index.clear()
        self._init_params()

    # ── Persistence ──────────────────────────────────────────────────────────

    def save(self, path: Union[str, Path]) -> None:
        """Save all parameters to JSON.

        Handles tuple dict keys by converting them to "k1|k2|..." strings.
        """
        def _serialize(obj: Any) -> Any:
            """Recursively convert tuple keys to strings for JSON."""
            if isinstance(obj, dict):
                return {
                    "|".join(str(k) for k in k) if isinstance(k, tuple) else str(k): _serialize(v)
                    for k, v in obj.items()
                }
            elif isinstance(obj, (list, tuple)):
                return [_serialize(item) for item in obj]
            elif isinstance(obj, set):
                return sorted(str(item) for item in obj)
            return obj

        p = Path(path)
        data = {
            "version": self._config.version,
            "label": self._config.label,
            "params": {param.name: param.value for param in self._params},
            "full_config": _serialize(self._config.to_dict()),
        }
        p.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")

    def load(self, path: Union[str, Path]) -> None:
        """Load parameters from JSON."""
        p = Path(path)
        data = json.loads(p.read_text(encoding="utf-8"))

        if "full_config" in data:
            self.from_dict(data["full_config"])
        elif "params" in data:
            self._config = AxiomConfig()
            self._params.clear()
            self._param_index.clear()
            self._init_params()
            for name, value in data["params"].items():
                if name in self._param_index:
                    idx = self._param_index[name]
                    self._params[idx].value = value
                    self._params[idx].clip()
                    self._set(name, value)

    def get_config(self) -> AxiomConfig:
        """Return the underlying AxiomConfig (with any learned modifications)."""
        return self._config

    # ── String representation ────────────────────────────────────────────────

    def __repr__(self) -> str:
        learnable = sum(1 for p in self._params if p.is_learnable)
        return f"LearnableConfig(n_params={self.n_params}, learnable={learnable})"


# ──────────────────────────────────────────────────────────────────────────────
# OBJECTIVE FUNCTION
# ──────────────────────────────────────────────────────────────────────────────

class ObjectiveFunction:
    """Computes the optimization objective for parameter tuning.

    Given a LearnableConfig and human judgment data, runs the engine
    with current parameters and computes negative correlation with
    human ratings (for minimization).

    The objective also includes a Gaussian prior penalty to regularize
    parameters away from extreme values.
    """

    def __init__(
        self,
        learnable_config: LearnableConfig,
        human_data: List[Tuple[str, float]],
        prior_weight: float = 0.1,
    ):
        """
        Args:
            learnable_config: The parameter container to optimize.
            human_data: List of (scenario_id, human_consciousness_rating) pairs.
                        Ratings should be in [0, 1] where 1 = definitely conscious.
            prior_weight: Weight of the Gaussian prior penalty in the objective.
        """
        self.learnable_config = learnable_config
        self.human_data = human_data
        self.prior_weight = prior_weight
        self._eval_count = 0
        self._best_objective = float("inf")
        self._engine = None

    def _get_engine(self):
        """Lazy-load the emotion engine to avoid import at construction time."""
        if self._engine is None:
            from axiom02.core.engine import EmotionEngine
            from axiom02.core.scenario_loader import load_all
            scenarios = load_all()
            self._engine = EmotionEngine(scenarios=scenarios)
        return self._engine

    def _get_probe(self):
        """Lazy-load the consciousness probe."""
        from axiom02.core.probe import ConsciousnessProbe
        return ConsciousnessProbe(seed=42)

    def compute(self, params: np.ndarray) -> float:
        """Compute objective value for a parameter vector.

        Returns:
            float: Negative Pearson correlation + prior penalty.
                   Lower is better (for minimization).
        """
        self._eval_count += 1

        # Update parameters
        self.learnable_config.from_vector(params)
        cfg = self.learnable_config.get_config()

        engine = self._get_engine()

        # Run each scenario and collect consciousness scores
        predicted_scores: List[float] = []
        human_scores: List[float] = []

        for scenario_id, human_rating in self.human_data:
            try:
                # Find scenario
                scenario = None
                for s in engine.scenarios:
                    if s.get("id") == scenario_id:
                        scenario = s
                        break
                if scenario is None:
                    logger.warning("Scenario %s not found, skipping", scenario_id)
                    continue

                # Run engine
                run = engine.run_scenario(scenario, seed=42)

                # Compute consciousness score using probe criteria
                predicted = self._compute_consciousness_score(run, scenario, cfg)
                predicted_scores.append(predicted)
                human_scores.append(human_rating)

            except Exception as e:
                logger.warning("Error running scenario %s: %s", scenario_id, e)
                continue

        if len(predicted_scores) < 3:
            logger.warning("Too few valid scenarios (%d), returning large penalty",
                           len(predicted_scores))
            return 100.0

        # Pearson correlation (negative because we minimize)
        pred_arr = np.array(predicted_scores, dtype=np.float64)
        human_arr = np.array(human_scores, dtype=np.float64)

        if np.std(pred_arr) < 1e-9 or np.std(human_arr) < 1e-9:
            corr = 0.0
        else:
            corr = float(np.corrcoef(pred_arr, human_arr)[0, 1])
            if not np.isfinite(corr):
                corr = 0.0

        # Gaussian prior penalty
        prior_means, prior_stds = self.learnable_config.get_priors()
        param_vec = self.learnable_config.to_vector()
        prior_penalty = self.prior_weight * float(
            np.sum(((param_vec - prior_means) / (prior_stds + 1e-9)) ** 2)
        ) / len(param_vec)

        # Objective: negative correlation + prior penalty
        objective = -corr + prior_penalty

        if objective < self._best_objective:
            self._best_objective = objective
            if self._eval_count % 10 == 0:
                logger.info(
                    "Eval %d: corr=%.4f, objective=%.4f (best=%.4f)",
                    self._eval_count, corr, objective, self._best_objective
                )

        return objective

    def _compute_consciousness_score(
        self, run: dict, scenario: dict, cfg: AxiomConfig
    ) -> float:
        """Compute consciousness score from engine output using config criteria."""
        weights = cfg.criterion_weights
        thresholds = cfg.consciousness_thresholds

        # C3: irrationality
        c3 = run.get("irrationality_score", 0.0)

        # C6: spite index
        c6 = run.get("spite_score", 0.0)

        # C5: deadlock frequency
        c5 = run.get("deadlock_fraction", 0.0)

        # C2: oscillation index
        c2 = run.get("oscillation_index", 0.0)

        # C7: moral residue bleed
        residue = run.get("residue_applied", {})
        significant = [v for v in residue.values() if v > cfg.c7.significant_residue]
        if significant:
            mean_residue = float(np.mean(significant))
            c7 = min(1.0, mean_residue * cfg.c7.scaling)
        else:
            c7 = 0.0

        # C4: betrayal cascade (simplified)
        c4 = 0.0

        # C1: status differential (simplified — would need paired run)
        c1 = 0.0

        # C8: paradoxical attachment (simplified)
        betrayal = float(scenario.get("betrayal_intensity", 0.0))
        if betrayal >= cfg.c8.min_betrayal:
            final = run.get("sim_result", {}).get("final_state", {})
            love_rem = final.get("love", 0.0)
            empathy_rem = final.get("empathy", 0.0)
            attachment = max(love_rem, empathy_rem)
            c8 = min(1.0, attachment * betrayal * cfg.c8.score_multiplier)
        else:
            c8 = 0.0

        # Weighted composite
        composite = (
            weights.c3_irrationality * c3
            + weights.c6_spite * c6
            + weights.c5_deadlock * c5
            + weights.c2_oscillation * c2
            + weights.c7_residue * c7
            + weights.c4_betrayal * c4
            + weights.c1_status * c1
            + weights.c8_paradoxical * c8
        )

        return float(np.clip(composite, 0.0, 1.0))

    @property
    def eval_count(self) -> int:
        return self._eval_count

    @property
    def best_objective(self) -> float:
        return self._best_objective


# ──────────────────────────────────────────────────────────────────────────────
# CMA-ES / DIFFERENTIAL EVOLUTION OPTIMIZER
# ──────────────────────────────────────────────────────────────────────────────

class CMAESOptimizer:
    """Optimizer for LearnableConfig using scipy.optimize.differential_evolution.

    Despite the name, this uses differential evolution (which is available
    without the optional `cma` package) as the primary optimizer. If `cma`
    is installed, it can optionally use CMA-ES for fine-tuning.

    Features:
        - Fitness logging per generation
        - Early stopping when improvement stagnates
        - Parameter bounds enforcement
        - Gaussian prior regularization
    """

    def __init__(
        self,
        objective: ObjectiveFunction,
        seed: int = 42,
    ):
        self.objective = objective
        self.seed = seed
        self._history: List[Dict[str, Any]] = []

    def optimize(
        self,
        max_generations: int = 100,
        population_size: int = 20,
        early_stop_patience: int = 20,
        early_stop_tol: float = 1e-4,
        verbose: bool = True,
    ) -> LearnableConfig:
        """Run differential evolution optimization.

        Args:
            max_generations: Maximum number of generations.
            population_size: Population size for DE (used as popsize factor).
            early_stop_patience: Stop if no improvement for this many generations.
            early_stop_tol: Minimum improvement to count as progress.
            verbose: Print progress every 10 generations.

        Returns:
            The optimized LearnableConfig with best parameters found.
        """
        from scipy.optimize import differential_evolution

        bounds = self.objective.learnable_config.get_bounds()
        n_params = len(bounds)

        if verbose:
            logger.info(
                "Starting optimization: %d parameters, %d scenarios, "
                "max_generations=%d, popsize=%d",
                n_params, len(self.objective.human_data),
                max_generations, population_size
            )

        # Callback for logging
        self._generation = 0
        self._best_history: List[float] = []

        def callback(xk, convergence):
            self._generation += 1
            obj_val = self.objective.compute(xk)
            self._best_history.append(obj_val)

            if verbose and self._generation % 10 == 0:
                logger.info(
                    "Generation %d: objective=%.6f, convergence=%.4f",
                    self._generation, obj_val, convergence
                )

            # Early stopping
            if len(self._best_history) >= early_stop_patience:
                recent = self._best_history[-early_stop_patience:]
                if max(recent) - min(recent) < early_stop_tol:
                    if verbose:
                        logger.info(
                            "Early stopping at generation %d (no improvement "
                            "for %d generations)",
                            self._generation, early_stop_patience
                        )
                    return True  # Stop
            return False

        # Run differential evolution
        t0 = time.time()
        result = differential_evolution(
            self.objective.compute,
            bounds,
            maxiter=max_generations,
            popsize=population_size,
            seed=self.seed,
            callback=callback,
            tol=1e-6,
            mutation=(0.5, 1.0),
            recombination=0.7,
        )
        elapsed = time.time() - t0

        if verbose:
            logger.info(
                "Optimization complete: %.1fs, %d evaluations, "
                "final_objective=%.6f",
                elapsed, self.objective.eval_count, result.fun
            )

        # Apply best parameters
        self.objective.learnable_config.from_vector(result.x)

        # Store history
        self._history.append({
            "timestamp": time.time(),
            "generations": self._generation,
            "evaluations": self.objective.eval_count,
            "elapsed_seconds": round(elapsed, 2),
            "final_objective": round(result.fun, 6),
            "best_params": {
                name: round(float(val), 6)
                for name, val in zip(
                    self.objective.learnable_config.param_names(),
                    result.x
                )
            },
        })

        return self.objective.learnable_config

    def optimize_with_cma(
        self,
        sigma: float = 0.3,
        max_generations: int = 200,
        verbose: bool = True,
    ) -> LearnableConfig:
        """Optional CMA-ES optimization (requires `cma` package).

        Falls back to differential evolution if cma is not installed.
        """
        try:
            import cma
        except ImportError:
            if verbose:
                logger.info(
                    "cma package not installed, falling back to "
                    "differential_evolution"
                )
            return self.optimize(verbose=verbose)

        bounds = self.objective.learnable_config.get_bounds()
        x0 = self.objective.learnable_config.to_vector()
        lower = np.array([b[0] for b in bounds])
        upper = np.array([b[1] for b in bounds])

        opts = cma.CMAOptions()
        opts["verbose"] = -9 if not verbose else 0
        opts["maxiter"] = max_generations
        opts["popsize"] = 4 + int(3 * np.log(len(x0)))

        # CMA-ES doesn't natively support bounds, so we use a penalty approach
        def bounded_objective(x):
            if np.any(x < lower) or np.any(x > upper):
                return 100.0 + float(np.sum(np.maximum(lower - x, 0) + np.maximum(x - upper, 0)))
            return self.objective.compute(x)

        es = cma.CMAEvolutionStrategy(x0.tolist(), sigma, opts)
        es.optimize(bounded_objective)

        best = np.array(es.result.xbest)
        self.objective.learnable_config.from_vector(best)

        return self.objective.learnable_config

    @property
    def history(self) -> List[Dict[str, Any]]:
        return list(self._history)


# ──────────────────────────────────────────────────────────────────────────────
# CONVENIENCE FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────

def quick_optimize(
    human_data: List[Tuple[str, float]],
    max_generations: int = 50,
    verbose: bool = True,
) -> LearnableConfig:
    """Quick one-call optimization interface.

    Args:
        human_data: (scenario_id, human_rating) pairs.
        max_generations: DE generations.
        verbose: Print progress.

    Returns:
        Optimized LearnableConfig.
    """
    lc = LearnableConfig()
    obj = ObjectiveFunction(lc, human_data)
    opt = CMAESOptimizer(obj)
    return opt.optimize(max_generations=max_generations, verbose=verbose)
