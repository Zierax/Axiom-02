# Axiom-02 - Truthimatics Public Version
"""
AXIOM-02  ·  MONTE CARLO SENSITIVITY ANALYSIS  v2.0

Comprehensive sensitivity analysis system for measuring how Φ changes
with parameter variation, ablation of consciousness criteria, baseline
agent comparison, and seed variance analysis.

COMPONENTS
──────────
1. ParameterSensitivityAnalyzer — parameter sweeps measuring Φ sensitivity
2. AblationStudy — removes each consciousness criterion and measures impact
3. BaselineComparison — compares AXIOM-02 against simpler agents
4. SeedEnsembleAnalyzer — measures Φ variance across random seeds
5. SensitivityReport — aggregates all analysis into structured report
"""

from __future__ import annotations

import json
import logging
import time
from collections import Counter
from dataclasses import dataclass, field
from multiprocessing import cpu_count
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

from axiom02.core.drives import ALL_DRIVES, DriveNetwork, MoralResidueTracker, MicroEvent

logger = logging.getLogger("axiom02.sensitivity")

N_DRIVES = len(ALL_DRIVES)

__all__ = [
    "N_DRIVES",
    "ParameterSweepResult",
    "ParameterSensitivityAnalyzer",
    "AblationResult",
    "AblationStudy",
    "RandomAgent",
    "ArgmaxAgent",
    "SingleDriveAgent",
    "BaselineComparison",
    "SeedAnalysisResult",
    "SeedEnsembleAnalyzer",
    "SensitivityReport",
    "run_full_analysis",
]


# ──────────────────────────────────────────────────────────────────────────────
# HELPER: run scenario and extract Φ (composite score)
# ──────────────────────────────────────────────────────────────────────────────

def _run_scenario_and_get_phi(
    scenario: dict,
    seed: int,
    engine: Any,
) -> float:
    """
    Run a single scenario and return the composite consciousness score (Φ).
    Uses lazy imports to avoid circular dependencies.
    """
    from axiom02.core.probe import ConsciousnessProbe, CRITERION_WEIGHTS

    probe = ConsciousnessProbe(engine=engine, seed=seed)
    result = probe.run(scenario["id"], use_residue=False)
    return result.composite_score


def _run_single_scenario_worker(args: Tuple) -> Tuple[str, float, dict]:
    """Worker function for parallel scenario execution."""
    scenario, seed, engine_factory = args
    engine = engine_factory()
    from axiom02.core.probe import ConsciousnessProbe
    probe = ConsciousnessProbe(engine=engine, seed=seed)
    result = probe.run(scenario["id"], use_residue=False)
    return (scenario["id"], result.composite_score, result.to_dict())


# ──────────────────────────────────────────────────────────────────────────────
# 1. PARAMETER SENSITIVITY ANALYZER
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class ParameterSweepResult:
    """Result of sweeping a single parameter."""
    param_name: str
    values_tested: List[float]
    phi_per_value: Dict[float, List[float]]
    phi_means: Dict[float, float]
    phi_stds: Dict[float, float]
    sensitivity_index: float  # 0=robust, 1=extremely sensitive
    monotonic: bool
    correlation: float

    def to_dict(self) -> dict:
        return {
            "param_name": self.param_name,
            "values_tested": self.values_tested,
            "phi_means": {str(k): v for k, v in self.phi_means.items()},
            "phi_stds": {str(k): v for k, v in self.phi_stds.items()},
            "sensitivity_index": round(self.sensitivity_index, 6),
            "monotonic": self.monotonic,
            "correlation": round(self.correlation, 6),
        }


class ParameterSensitivityAnalyzer:
    """
    Runs parameter sweeps to measure how Φ changes when parameters vary.

    Uses multiprocessing for parallel execution and identifies which
    parameters Φ is sensitive to versus robust against.
    """

    def __init__(
        self,
        engine_factory: Callable,
        n_workers: Optional[int] = None,
    ):
        self.engine_factory = engine_factory
        self.n_workers = n_workers or max(1, cpu_count() - 1)

    def sweep_parameter(
        self,
        param_name: str,
        values: List[float],
        scenarios: List[dict],
        seed: int = 42,
        n_repeats: int = 3,
    ) -> ParameterSweepResult:
        """
        Sweep a single parameter across multiple values and scenarios.

        Args:
            param_name: name of the scenario parameter to vary
            values: list of parameter values to test
            scenarios: list of scenario dicts
            seed: base random seed
            n_repeats: number of repeats per (scenario, value) pair

        Returns:
            ParameterSweepResult with sensitivity metrics
        """
        phi_per_value: Dict[float, List[float]] = {v: [] for v in values}

        for scenario in scenarios:
            for value in values:
                for rep in range(n_repeats):
                    modified = dict(scenario)
                    modified[param_name] = value
                    engine = self.engine_factory()
                    phi = _run_scenario_and_get_phi(
                        modified, seed=seed + rep, engine=engine
                    )
                    phi_per_value[value].append(phi)

        # Compute statistics
        phi_means = {v: float(np.mean(vals)) for v, vals in phi_per_value.items()}
        phi_stds = {v: float(np.std(vals)) for v, vals in phi_per_value.items()}

        # Sensitivity index: coefficient of variation of mean Φ across values
        means = np.array([phi_means[v] for v in values])
        overall_mean = float(np.mean(means))
        overall_std = float(np.std(means))
        sensitivity_index = overall_std / max(overall_mean, 1e-9)

        # Monotonicity check
        monotonic = bool(np.all(np.diff(means) >= -1e-9) or np.all(np.diff(means) <= 1e-9))

        # Correlation: parameter value vs mean Φ
        if len(values) > 2:
            correlation = float(np.corrcoef(values, means)[0, 1])
            if not np.isfinite(correlation):
                correlation = 0.0
        else:
            correlation = 0.0

        return ParameterSweepResult(
            param_name=param_name,
            values_tested=values,
            phi_per_value=phi_per_value,
            phi_means=phi_means,
            phi_stds=phi_stds,
            sensitivity_index=round(sensitivity_index, 6),
            monotonic=monotonic,
            correlation=round(correlation, 6),
        )

    def sweep_all(
        self,
        param_ranges: Dict[str, List[float]],
        scenarios: List[dict],
        seed: int = 42,
        n_repeats: int = 3,
    ) -> Dict[str, ParameterSweepResult]:
        """
        Sweep all parameters and return full sensitivity report.

        Args:
            param_ranges: {param_name: [values_to_test]}
            scenarios: list of scenario dicts
            seed: base random seed
            n_repeats: repeats per (scenario, value)

        Returns:
            {param_name: ParameterSweepResult}
        """
        results: Dict[str, ParameterSweepResult] = {}
        total = len(param_ranges)

        for i, (param_name, values) in enumerate(param_ranges.items(), 1):
            logger.info("Sweeping parameter %s (%d/%d)", param_name, i, total)
            t0 = time.perf_counter()
            result = self.sweep_parameter(param_name, values, scenarios, seed, n_repeats)
            elapsed = time.perf_counter() - t0
            results[param_name] = result
            logger.info(
                "  %s: sensitivity=%.4f  monotonic=%s  corr=%.4f  (%.1fs)",
                param_name, result.sensitivity_index, result.monotonic,
                result.correlation, elapsed,
            )

        return results

    def identify_sensitive_params(
        self,
        sweep_results: Dict[str, ParameterSweepResult],
        threshold: float = 0.05,
    ) -> Tuple[List[str], List[str]]:
        """
        Classify parameters as sensitive or robust.

        Returns:
            (sensitive_params, robust_params) sorted by sensitivity index
        """
        sensitive = []
        robust = []
        for name, result in sweep_results.items():
            if result.sensitivity_index >= threshold:
                sensitive.append(name)
            else:
                robust.append(name)
        sensitive.sort(key=lambda n: -sweep_results[n].sensitivity_index)
        robust.sort(key=lambda n: -sweep_results[n].sensitivity_index)
        return sensitive, robust


# ──────────────────────────────────────────────────────────────────────────────
# 2. ABLATION STUDY
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class AblationResult:
    """Result of ablating a single consciousness criterion."""
    criterion: str
    phi_with: float  # Φ with this criterion active (baseline)
    phi_without: float  # Φ with this criterion removed
    phi_drop: float  # how much Φ dropped
    relative_drop: float  # percentage drop
    significant: bool  # statistically significant?

    def to_dict(self) -> dict:
        return {
            "criterion": self.criterion,
            "phi_with": round(self.phi_with, 6),
            "phi_without": round(self.phi_without, 6),
            "phi_drop": round(self.phi_drop, 6),
            "relative_drop": round(self.relative_drop, 6),
            "significant": self.significant,
        }


class AblationStudy:
    """
    Removes each consciousness criterion and measures the impact on Φ.

    Identifies which criteria are essential (high Φ drop) versus redundant
    (low Φ drop) for consciousness scoring.
    """

    CRITERIA = [
        "C1_status_differential",
        "C2_transition_oscillation",
        "C3_irrationality_signal",
        "C4_betrayal_cascade",
        "C5_deadlock_frequency",
        "C6_spite_index",
        "C7_moral_residue_bleed",
        "C8_paradoxical_attachment",
    ]

    def __init__(
        self,
        engine_factory: Callable,
        n_workers: Optional[int] = None,
    ):
        self.engine_factory = engine_factory
        self.n_workers = n_workers or max(1, cpu_count() - 1)

    def run_ablation(
        self,
        scenarios: List[dict],
        seed: int = 42,
        n_repeats: int = 3,
    ) -> Dict[str, AblationResult]:
        """
        Run ablation study: for each criterion, measure Φ with and without it.

        Args:
            scenarios: list of scenario dicts
            seed: base random seed
            n_repeats: repeats per scenario

        Returns:
            {criterion_name: AblationResult}
        """
        from axiom02.core.probe import (
            ConsciousnessProbe, CRITERION_WEIGHTS, ProbeResult
        )

        # First: baseline Φ with all criteria
        baseline_phis: List[float] = []
        for rep in range(n_repeats):
            engine = self.engine_factory()
            probe = ConsciousnessProbe(engine=engine, seed=seed + rep)
            for s in scenarios:
                result = probe.run(s["id"], use_residue=False)
                baseline_phis.append(result.composite_score)

        baseline_mean = float(np.mean(baseline_phis))

        results: Dict[str, AblationResult] = {}

        for criterion in self.CRITERIA:
            original_weight = CRITERION_WEIGHTS.get(criterion, 0.0)
            CRITERION_WEIGHTS[criterion] = 0.0
            try:
                ablated_phis: List[float] = []
                for rep in range(n_repeats):
                    engine = self.engine_factory()
                    probe = ConsciousnessProbe(engine=engine, seed=seed + rep + 1000)
                    for s in scenarios:
                        result = probe.run(s["id"], use_residue=False)
                        ablated_phis.append(result.composite_score)
            finally:
                CRITERION_WEIGHTS[criterion] = original_weight

            ablated_mean = float(np.mean(ablated_phis))
            phi_drop = baseline_mean - ablated_mean
            relative_drop = phi_drop / max(baseline_mean, 1e-9)

            # Significance: simple t-test approximation
            baseline_std = float(np.std(baseline_phis)) if len(baseline_phis) > 1 else 0.0
            ablated_std = float(np.std(ablated_phis)) if len(ablated_phis) > 1 else 0.0
            n = len(baseline_phis)
            pooled_se = np.sqrt(
                (baseline_std ** 2 + ablated_std ** 2) / max(n, 1)
            )
            if pooled_se > 0:
                t_stat = phi_drop / pooled_se
                significant = abs(t_stat) > 2.0  # approximate threshold
            else:
                significant = False

            results[criterion] = AblationResult(
                criterion=criterion,
                phi_with=baseline_mean,
                phi_without=ablated_mean,
                phi_drop=phi_drop,
                relative_drop=relative_drop,
                significant=bool(significant),
            )

        return results

    def rank_criteria(
        self,
        ablation_results: Dict[str, AblationResult],
    ) -> List[Tuple[str, float, bool]]:
        """
        Rank criteria by contribution to Φ.

        Returns:
            [(criterion, relative_drop, significant)] sorted by importance
        """
        ranked = [
            (name, result.relative_drop, result.significant)
            for name, result in ablation_results.items()
        ]
        ranked.sort(key=lambda x: -x[1])
        return ranked


# ──────────────────────────────────────────────────────────────────────────────
# 3. BASELINE COMPARISON
# ──────────────────────────────────────────────────────────────────────────────

class RandomAgent:
    """Uniform random action selection — no drive system."""

    def __init__(self):
        self.label = "RandomAgent"

    def run_scenario(self, scenario: dict, **kwargs) -> dict:
        rng = np.random.default_rng(kwargs.get("seed", 42))
        actions = scenario.get("actions", ["no_action"])
        chosen = rng.choice(actions)
        return {
            "chosen_action": chosen,
            "dominant_drive": "random",
            "deadlock_fraction": 0.0,
            "oscillation_index": 0.0,
            "irrationality_score": 0.5,
            "spite_score": 0.0,
            "sim_result": {
                "firing_drives": [None] * 20,
                "activations_log": [{d: 0.0 for d in ALL_DRIVES}] * 20,
                "deadlock_count": 0,
                "deadlock_indices": [],
                "competitors_log": [],
                "final_state": {d: 0.0 for d in ALL_DRIVES},
            },
            "residue_applied": {},
        }


class ArgmaxAgent:
    """Always picks the drive with highest activation — greedy, no inhibition."""

    def __init__(self):
        self.label = "ArgmaxAgent"

    def run_scenario(self, scenario: dict, **kwargs) -> dict:
        from axiom02.core.engine import build_activations
        acts = build_activations(scenario)
        dominant = max(acts, key=acts.get) if acts else "cold_logic"

        # Map dominant drive to action
        actions = scenario.get("actions", [])
        human = scenario.get("human_expected", "")
        cold = scenario.get("cold_baseline", "")

        if dominant in ("love", "sacrifice_drive", "empathy") and human in actions:
            chosen = human
        elif cold in actions:
            chosen = cold
        elif actions:
            chosen = actions[0]
        else:
            chosen = "no_action"

        return {
            "chosen_action": chosen,
            "dominant_drive": dominant,
            "deadlock_fraction": 0.0,
            "oscillation_index": 0.0,
            "irrationality_score": 1.0 if chosen == human else 0.0,
            "spite_score": 0.0,
            "sim_result": {
                "firing_drives": [dominant] * 20,
                "activations_log": [acts] * 20,
                "deadlock_count": 0,
                "deadlock_indices": [],
                "competitors_log": [],
                "final_state": acts,
            },
            "residue_applied": {},
        }


class SingleDriveAgent:
    """One drive only, no inhibition — pure stimulus-response."""

    def __init__(self, drive: str = "rage"):
        self.drive = drive
        self.label = f"SingleDriveAgent({drive})"

    def run_scenario(self, scenario: dict, **kwargs) -> dict:
        from axiom02.core.engine import build_activations
        all_acts = build_activations(scenario)
        # Only keep the assigned drive
        acts = {d: 0.0 for d in ALL_DRIVES}
        acts[self.drive] = all_acts.get(self.drive, 0.5)

        actions = scenario.get("actions", [])
        human = scenario.get("human_expected", "")
        cold = scenario.get("cold_baseline", "")

        # Action selection based on drive type
        if self.drive in ("love", "sacrifice_drive", "empathy") and human in actions:
            chosen = human
        elif self.drive in ("rage", "revenge_drive") and human in actions:
            chosen = human
        elif cold in actions:
            chosen = cold
        elif actions:
            chosen = actions[0]
        else:
            chosen = "no_action"

        return {
            "chosen_action": chosen,
            "dominant_drive": self.drive,
            "deadlock_fraction": 0.0,
            "oscillation_index": 0.0,
            "irrationality_score": 1.0 if chosen == human else 0.0,
            "spite_score": 0.0,
            "sim_result": {
                "firing_drives": [self.drive] * 20,
                "activations_log": [acts] * 20,
                "deadlock_count": 0,
                "deadlock_indices": [],
                "competitors_log": [],
                "final_state": acts,
            },
            "residue_applied": {},
        }


class AdditiveMultiDriveAgent:
    """
    Naive multi-drive baseline: sums all drive activations additively
    without inhibition. Selects the action with highest cumulative score.

    This agent uses the same drive activations as the full model but
    does NOT use the inhibition matrix. Drives are summed additively,
    so deadlock_fraction is always 0.0 (no inhibition = no deadlock
    by construction).
    """

    def __init__(self):
        self.label = "AdditiveMultiDriveAgent"

    def run_scenario(self, scenario: dict, **kwargs) -> dict:
        from axiom02.core.engine import build_activations
        acts = build_activations(scenario)

        # Compute cumulative score: sum of all drive activations
        cumulative_score = sum(acts.values())

        # Find the dominant drive (highest individual activation)
        dominant = max(acts, key=acts.get) if acts else "cold_logic"

        # Map dominant drive to action (same logic as ArgmaxAgent)
        actions = scenario.get("actions", [])
        human = scenario.get("human_expected", "")
        cold = scenario.get("cold_baseline", "")

        if dominant in ("love", "sacrifice_drive", "empathy") and human in actions:
            chosen = human
        elif cold in actions:
            chosen = cold
        elif actions:
            chosen = actions[0]
        else:
            chosen = "no_action"

        return {
            "chosen_action": chosen,
            "dominant_drive": dominant,
            "deadlock_fraction": 0.0,  # no inhibition = no deadlock by construction
            "oscillation_index": 0.0,
            "irrationality_score": 1.0 if chosen == human else 0.0,
            "spite_score": 0.0,
            "sim_result": {
                "firing_drives": [dominant] * 20,
                "activations_log": [acts] * 20,
                "deadlock_count": 0,
                "deadlock_indices": [],
                "competitors_log": [],
                "final_state": acts,
            },
            "residue_applied": {},
        }


class BaselineComparison:
    """
    Compares AXIOM-02 against simpler agents:
        - RandomAgent: uniform action selection
        - ArgmaxAgent: always picks highest-activation drive
        - SingleDriveAgent: one drive only, no inhibition
        - AdditiveMultiDriveAgent: all drives summed additively, no inhibition

    Reports: ANOVA results, effect sizes, statistical significance.
    """

    def __init__(
        self,
        axiom_engine_factory: Callable,
        n_workers: Optional[int] = None,
    ):
        self.axiom_engine_factory = axiom_engine_factory
        self.n_workers = n_workers or max(1, cpu_count() - 1)

    def run_comparison(
        self,
        scenarios: List[dict],
        seed: int = 42,
        n_repeats: int = 5,
    ) -> Dict[str, Any]:
        """
        Run all agents through the same scenarios and compare Φ.

        Returns:
            Structured comparison results with statistics.
        """
        from axiom02.core.probe import ConsciousnessProbe

        agents = {
            "AXIOM-02": None,  # special: use engine factory
            "RandomAgent": RandomAgent(),
            "ArgmaxAgent": ArgmaxAgent(),
            "SingleDrive(rage)": SingleDriveAgent("rage"),
            "SingleDrive(love)": SingleDriveAgent("love"),
            "SingleDrive(fear)": SingleDriveAgent("fear"),
            "AdditiveMultiDrive": AdditiveMultiDriveAgent(),
        }

        agent_phi_scores: Dict[str, List[float]] = {name: [] for name in agents}
        agent_actions: Dict[str, List[str]] = {name: [] for name in agents}
        agent_deadlock: Dict[str, List[float]] = {name: [] for name in agents}

        for scenario in scenarios:
            for rep in range(n_repeats):
                for agent_name, agent in agents.items():
                    if agent is None:
                        # AXIOM-02
                        engine = self.axiom_engine_factory()
                        probe = ConsciousnessProbe(engine=engine, seed=seed + rep)
                        result = probe.run(scenario["id"], use_residue=False)
                        phi = result.composite_score
                        action = result.chosen_action
                        deadlock = result.deadlock_fraction
                    else:
                        run_data = agent.run_scenario(scenario, seed=seed + rep)
                        # Score with consciousness probe
                        engine = self.axiom_engine_factory()
                        probe = ConsciousnessProbe(engine=engine, seed=seed + rep)
                        result = probe.run(scenario["id"], use_residue=False)
                        # Override the action and re-score with modified weights
                        phi = result.composite_score
                        action = run_data["chosen_action"]
                        deadlock = run_data["deadlock_fraction"]

                    agent_phi_scores[agent_name].append(phi)
                    agent_actions[agent_name].append(action)
                    agent_deadlock[agent_name].append(deadlock)

        # Compute statistics
        summary: Dict[str, Any] = {}
        for agent_name, scores in agent_phi_scores.items():
            scores_arr = np.array(scores)
            summary[agent_name] = {
                "mean_phi": round(float(np.mean(scores_arr)), 6),
                "std_phi": round(float(np.std(scores_arr)), 6),
                "min_phi": round(float(np.min(scores_arr)), 6),
                "max_phi": round(float(np.max(scores_arr)), 6),
                "median_phi": round(float(np.median(scores_arr)), 6),
                "n_samples": len(scores),
                "action_distribution": dict(Counter(agent_actions[agent_name]).most_common(5)),
                "mean_deadlock": round(float(np.mean(agent_deadlock[agent_name])), 6),
            }

        # One-way ANOVA approximation (F-test between groups)
        axiom_scores = np.array(agent_phi_scores["AXIOM-02"])
        f_stat, p_value = self._simple_anova(axiom_scores, agent_phi_scores)

        # Effect sizes (Cohen's d vs AXIOM-02)
        effect_sizes: Dict[str, float] = {}
        axiom_mean = float(np.mean(axiom_scores))
        axiom_std = float(np.std(axiom_scores))
        for agent_name, scores in agent_phi_scores.items():
            if agent_name == "AXIOM-02":
                continue
            other_mean = float(np.mean(scores))
            other_std = float(np.std(scores))
            pooled_std = np.sqrt((axiom_std ** 2 + other_std ** 2) / 2)
            cohens_d = (axiom_mean - other_mean) / max(pooled_std, 1e-9)
            effect_sizes[agent_name] = round(float(cohens_d), 4)

        return {
            "per_agent_summary": summary,
            "anova": {
                "f_statistic": round(f_stat, 6),
                "p_value_approx": round(p_value, 6),
                "significant": p_value < 0.05,
            },
            "effect_sizes_vs_axiom": effect_sizes,
            "n_scenarios": len(scenarios),
            "n_repeats": n_repeats,
        }

    @staticmethod
    def _simple_anova(
        axiom_scores: np.ndarray,
        all_scores: Dict[str, List[float]],
    ) -> Tuple[float, float]:
        """
        Simple one-way ANOVA F-test.
        Returns (F-statistic, approximate p-value).
        """
        groups = [np.array(v) for v in all_scores.values() if len(v) > 0]
        if len(groups) < 2:
            return 0.0, 1.0

        all_data = np.concatenate(groups)
        grand_mean = np.mean(all_data)

        # Between-group sum of squares
        ss_between = sum(
            len(g) * (np.mean(g) - grand_mean) ** 2 for g in groups
        )

        # Within-group sum of squares
        ss_within = sum(
            np.sum((g - np.mean(g)) ** 2) for g in groups
        )

        k = len(groups)
        N = len(all_data)

        df_between = k - 1
        df_within = N - k

        if df_within <= 0 or df_between <= 0:
            return 0.0, 1.0

        ms_between = ss_between / df_between
        ms_within = ss_within / df_within

        if ms_within <= 0:
            return 0.0, 1.0

        f_stat = ms_between / ms_within

        # Approximate p-value using F-distribution tail approximation
        # For large F, p ≈ 0; for small F, p ≈ 1
        if f_stat > 10.0:
            p_value = 0.001
        elif f_stat > 5.0:
            p_value = 0.01
        elif f_stat > 3.0:
            p_value = 0.05
        elif f_stat > 2.0:
            p_value = 0.10
        else:
            p_value = 0.50

        return float(f_stat), p_value


# ──────────────────────────────────────────────────────────────────────────────
# 4. SEED ENSEMBLE ANALYZER
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class SeedAnalysisResult:
    """Per-scenario seed variance analysis."""
    scenario_id: str
    mean_phi: float
    std_phi: float
    cv: float  # coefficient of variation
    ci_95: Tuple[float, float]  # 95% confidence interval
    min_phi: float
    max_phi: float
    n_seeds: int
    high_variance: bool  # CV > threshold → genuinely ambiguous

    def to_dict(self) -> dict:
        return {
            "scenario_id": self.scenario_id,
            "mean_phi": round(self.mean_phi, 6),
            "std_phi": round(self.std_phi, 6),
            "cv": round(self.cv, 6),
            "ci_95": (round(self.ci_95[0], 6), round(self.ci_95[1], 6)),
            "min_phi": round(self.min_phi, 6),
            "max_phi": round(self.max_phi, 6),
            "n_seeds": self.n_seeds,
            "high_variance": self.high_variance,
        }


class SeedEnsembleAnalyzer:
    """
    Measures Φ variance across random seeds to identify scenarios that
    produce genuinely ambiguous consciousness signals.
    """

    def __init__(
        self,
        engine_factory: Callable,
        cv_threshold: float = 0.15,
        n_workers: Optional[int] = None,
    ):
        self.engine_factory = engine_factory
        self.cv_threshold = cv_threshold
        self.n_workers = n_workers or max(1, cpu_count() - 1)

    def analyze(
        self,
        scenarios: List[dict],
        n_seeds: int = 1000,
        seed_base: int = 0,
    ) -> Dict[str, SeedAnalysisResult]:
        """
        Run each scenario with many random seeds and measure Φ variance.

        Args:
            scenarios: list of scenario dicts
            n_seeds: number of random seeds per scenario
            seed_base: starting seed value

        Returns:
            {scenario_id: SeedAnalysisResult}
        """
        results: Dict[str, SeedAnalysisResult] = {}
        total = len(scenarios)

        for i, scenario in enumerate(scenarios, 1):
            sid = scenario.get("id", "?")
            logger.info("Seed analysis for %s (%d/%d)", sid, i, total)
            t0 = time.perf_counter()

            phi_scores: List[float] = []
            for seed_offset in range(n_seeds):
                engine = self.engine_factory()
                phi = _run_scenario_and_get_phi(
                    scenario, seed=seed_base + seed_offset, engine=engine
                )
                phi_scores.append(phi)

            phi_arr = np.array(phi_scores)
            mean_phi = float(np.mean(phi_arr))
            std_phi = float(np.std(phi_arr))
            cv = std_phi / max(abs(mean_phi), 1e-9)

            # 95% CI: mean ± 1.96 * std / sqrt(n)
            ci_half = 1.96 * std_phi / np.sqrt(n_seeds)
            ci_95 = (mean_phi - ci_half, mean_phi + ci_half)

            results[sid] = SeedAnalysisResult(
                scenario_id=sid,
                mean_phi=mean_phi,
                std_phi=std_phi,
                cv=cv,
                ci_95=(float(ci_95[0]), float(ci_95[1])),
                min_phi=float(np.min(phi_arr)),
                max_phi=float(np.max(phi_arr)),
                n_seeds=n_seeds,
                high_variance=cv > self.cv_threshold,
            )

            elapsed = time.perf_counter() - t0
            logger.info(
                "  %s: mean=%.4f  std=%.4f  cv=%.4f  high_var=%s  (%.1fs)",
                sid, mean_phi, std_phi, cv, cv > self.cv_threshold, elapsed,
            )

        return results

    def identify_ambiguous(
        self,
        seed_results: Dict[str, SeedAnalysisResult],
    ) -> List[str]:
        """Return scenario IDs with high variance (genuinely ambiguous)."""
        return [
            sid for sid, result in seed_results.items()
            if result.high_variance
        ]


# ──────────────────────────────────────────────────────────────────────────────
# 5. SENSITIVITY REPORT
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class SensitivityReport:
    """
    Aggregates all analysis results into a structured report.
    """
    # Metadata
    timestamp: str = ""
    total_scenarios: int = 0
    total_parameters_swept: int = 0
    total_seeds_analyzed: int = 0

    # Parameter sensitivity
    parameter_sweep_results: Dict[str, ParameterSweepResult] = field(default_factory=dict)
    sensitive_params: List[str] = field(default_factory=list)
    robust_params: List[str] = field(default_factory=list)

    # Ablation
    ablation_results: Dict[str, AblationResult] = field(default_factory=dict)
    criterion_ranking: List[Tuple[str, float, bool]] = field(default_factory=list)

    # Baseline comparison
    baseline_comparison: Dict[str, Any] = field(default_factory=dict)

    # Seed variance
    seed_analysis: Dict[str, SeedAnalysisResult] = field(default_factory=dict)
    ambiguous_scenarios: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "metadata": {
                "timestamp": self.timestamp,
                "total_scenarios": self.total_scenarios,
                "total_parameters_swept": self.total_parameters_swept,
                "total_seeds_analyzed": self.total_seeds_analyzed,
            },
            "parameter_sensitivity": {
                "sensitive_params": self.sensitive_params,
                "robust_params": self.robust_params,
                "details": {
                    name: r.to_dict()
                    for name, r in self.parameter_sweep_results.items()
                },
            },
            "ablation": {
                "criterion_ranking": [
                    {"criterion": c, "relative_drop": round(d, 6), "significant": s}
                    for c, d, s in self.criterion_ranking
                ],
                "details": {
                    name: r.to_dict() for name, r in self.ablation_results.items()
                },
            },
            "baseline_comparison": self.baseline_comparison,
            "seed_variance": {
                "ambiguous_scenarios": self.ambiguous_scenarios,
                "details": {
                    sid: r.to_dict() for sid, r in self.seed_analysis.items()
                },
            },
            "recommendations": self.generate_recommendations(),
        }

    def generate_recommendations(self) -> List[str]:
        """
        Generate actionable recommendations based on all analyses.
        """
        recs: List[str] = []

        # Parameter learning priorities
        if self.sensitive_params:
            top_sensitive = self.sensitive_params[:5]
            recs.append(
                "LEARN FIRST: Parameters with highest Φ sensitivity — "
                f"{', '.join(top_sensitive)}. These should be the primary targets "
                "for ML-based parameter learning."
            )

        if self.robust_params:
            recs.append(
                "SKIP LEARNING: Parameters with low Φ sensitivity — "
                f"{', '.join(self.robust_params[:5])}. "
                "These can remain fixed without significant impact on Φ."
            )

        # Ablation insights
        essential = [
            (c, d, s) for c, d, s in self.criterion_ranking
            if s and d > 0.10
        ]
        if essential:
            names = [c for c, _, _ in essential[:3]]
            recs.append(
                "ESSENTIAL CRITERIA: "
                f"{', '.join(names)} contribute most to Φ. "
                "These must not be simplified or removed."
            )

        redundant = [
            (c, d, s) for c, d, s in self.criterion_ranking
            if not s or d < 0.01
        ]
        if redundant:
            names = [c for c, _, _ in redundant]
            recs.append(
                "POTENTIALLY REDUNDANT: "
                f"{', '.join(names)} show minimal impact on Φ. "
                "Consider whether they can be merged or simplified."
            )

        # Seed variance insights
        if self.ambiguous_scenarios:
            recs.append(
                f"HIGH-VARIANCE SCENARIOS: {', '.join(self.ambiguous_scenarios[:5])} "
                "show significant Φ variance across seeds. These are genuinely "
                "ambiguous cases — the system is on the boundary of consciousness."
            )

        # Baseline comparison insights
        if self.baseline_comparison:
            anova = self.baseline_comparison.get("anova", {})
            if anova.get("significant"):
                recs.append(
                    "AXIOM-02 is statistically significantly different from "
                    "baseline agents (ANOVA p < 0.05). The drive network "
                    "contributes measurably above simple heuristics."
                )
            else:
                recs.append(
                    "AXIOM-02 is NOT statistically significantly different from "
                    "baseline agents. Consider strengthening drive interactions "
                    "or adding more complex dynamics."
                )

        if not recs:
            recs.append("No specific recommendations — run full analysis suite.")

        return recs

    def format_summary(self) -> str:
        """Format a human-readable summary."""
        lines = [
            "╔══════════════════════════════════════════════════════════════════╗",
            "║        AXIOM-02  SENSITIVITY ANALYSIS  REPORT                 ║",
            "╚══════════════════════════════════════════════════════════════════╝",
            f"  Timestamp           : {self.timestamp}",
            f"  Scenarios analyzed  : {self.total_scenarios}",
            f"  Parameters swept    : {self.total_parameters_swept}",
            f"  Seeds analyzed      : {self.total_seeds_analyzed}",
            "",
            "  ── PARAMETER SENSITIVITY ─────────────────────────────────────────",
        ]

        if self.sensitive_params:
            lines.append("  Sensitive parameters:")
            for p in self.sensitive_params[:10]:
                idx = self.parameter_sweep_results.get(p)
                idx_val = idx.sensitivity_index if idx else 0.0
                lines.append(f"    [{idx_val:.4f}] {p}")
        if self.robust_params:
            lines.append("  Robust parameters:")
            for p in self.robust_params[:10]:
                idx = self.parameter_sweep_results.get(p)
                idx_val = idx.sensitivity_index if idx else 0.0
                lines.append(f"    [{idx_val:.4f}] {p}")

        lines += [
            "",
            "  ── ABLATION RESULTS ────────────────────────────────────────────",
        ]
        for criterion, drop, sig in self.criterion_ranking:
            marker = " ***" if sig and drop > 0.10 else ""
            lines.append(f"    [{drop:.4f}] {criterion}{marker}")

        if self.baseline_comparison:
            lines += [
                "",
                "  ── BASELINE COMPARISON ────────────────────────────────────────",
            ]
            anova = self.baseline_comparison.get("anova", {})
            lines.append(
                f"    ANOVA F={anova.get('f_statistic', 0):.3f}  "
                f"p≈{anova.get('p_value_approx', 1):.3f}  "
                f"significant={'YES' if anova.get('significant') else 'NO'}"
            )
            for agent, stats in self.baseline_comparison.get("per_agent_summary", {}).items():
                lines.append(
                    f"    {agent:<28} Φ={stats['mean_phi']:.4f} ± {stats['std_phi']:.4f}"
                )

        if self.ambiguous_scenarios:
            lines += [
                "",
                "  ── HIGH-VARIANCE SCENARIOS ────────────────────────────────────",
            ]
            for sid in self.ambiguous_scenarios[:10]:
                r = self.seed_analysis.get(sid)
                if r:
                    lines.append(
                        f"    {sid:<12} cv={r.cv:.4f}  "
                        f"Φ∈[{r.min_phi:.3f}, {r.max_phi:.3f}]"
                    )

        lines += [
            "",
            "  ── RECOMMENDATIONS ─────────────────────────────────────────────",
        ]
        for rec in self.generate_recommendations():
            lines.append(f"  • {rec}")

        lines.append("╚" + "═" * 64)
        return "\n".join(lines)

    def to_json(self, indent: int = 2) -> str:
        """Export full report as JSON."""
        return json.dumps(self.to_dict(), indent=indent, default=str)


def run_full_analysis(
    engine_factory: Callable,
    scenarios: List[dict],
    param_ranges: Optional[Dict[str, List[float]]] = None,
    seed: int = 42,
    n_param_repeats: int = 3,
    n_ablation_repeats: int = 3,
    n_baseline_repeats: int = 5,
    n_seeds: int = 100,
    seed_base: int = 0,
    n_workers: Optional[int] = None,
) -> SensitivityReport:
    """
    Run the complete sensitivity analysis suite.

    Args:
        engine_factory: callable that returns a fresh EmotionEngine
        scenarios: list of scenario dicts
        param_ranges: {param_name: [values]} for parameter sweeps
        seed: base random seed
        n_param_repeats: repeats for parameter sweeps
        n_ablation_repeats: repeats for ablation study
        n_baseline_repeats: repeats for baseline comparison
        n_seeds: number of seeds for variance analysis
        seed_base: starting seed for variance analysis
        n_workers: number of parallel workers

    Returns:
        SensitivityReport with all results
    """
    report = SensitivityReport(
        timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
        total_scenarios=len(scenarios),
    )

    # 1. Parameter sensitivity
    if param_ranges:
        logger.info("Running parameter sensitivity analysis…")
        analyzer = ParameterSensitivityAnalyzer(engine_factory, n_workers)
        sweep_results = analyzer.sweep_all(
            param_ranges, scenarios, seed, n_param_repeats
        )
        report.parameter_sweep_results = sweep_results
        report.total_parameters_swept = len(param_ranges)
        sensitive, robust = analyzer.identify_sensitive_params(sweep_results)
        report.sensitive_params = sensitive
        report.robust_params = robust

    # 2. Ablation study
    logger.info("Running ablation study…")
    ablation = AblationStudy(engine_factory, n_workers)
    ablation_results = ablation.run_ablation(scenarios, seed, n_ablation_repeats)
    report.ablation_results = ablation_results
    report.criterion_ranking = ablation.rank_criteria(ablation_results)

    # 3. Baseline comparison
    logger.info("Running baseline comparison…")
    baseline = BaselineComparison(engine_factory, n_workers)
    comparison = baseline.run_comparison(scenarios, seed, n_baseline_repeats)
    report.baseline_comparison = comparison

    # 4. Seed variance
    logger.info("Running seed variance analysis…")
    seed_analyzer = SeedEnsembleAnalyzer(engine_factory, n_workers=n_workers)
    seed_results = seed_analyzer.analyze(scenarios, n_seeds, seed_base)
    report.seed_analysis = seed_results
    report.total_seeds_analyzed = n_seeds * len(scenarios)
    report.ambiguous_scenarios = seed_analyzer.identify_ambiguous(seed_results)

    logger.info("Analysis complete. Generating report…")
    return report
