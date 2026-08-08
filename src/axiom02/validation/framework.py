# Axiom-02 - Truthimatics Public Version
"""
AXIOM-02  ·  HUMAN VALIDATION FRAMEWORK  v1.0

Collects inter-rater agreement data to validate deliberative complexity
metrics against human judgments.

COMPONENTS
──────────
1. ValidationTask      — single task presented to human raters
2. RaterJudgment       — one rater's response to a task
3. ValidationStudy     — full study lifecycle: tasks → survey → judgments → metrics

METRICS
───────
- Fleiss' kappa (multi-rater, categorical)
- Percentage agreement (raw and chance-corrected)
- Krippendorff's alpha (ordinal scale)
- Model–human correlation (Spearman ρ)

DEPENDENCIES
────────────
numpy only.  No matplotlib, no scipy.

Usage
─────
    from human_validation import ValidationStudy, ValidationTask, RaterJudgment

    study = ValidationStudy("axiom02_v1", output_dir=Path("validation"))
    tasks = study.generate_tasks(scenarios, probe_results)
    assignments = study.create_survey(tasks, n_raters=5)
    # ... collect judgments ...
    study.record_judgment(RaterJudgment(...))
    metrics = study.compute_agreement()
    report  = study.generate_report()
"""

from __future__ import annotations

import json
import math
import uuid
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


__all__ = [
    "ValidationTask",
    "RaterJudgment",
    "ValidationStudy",
]


# ──────────────────────────────────────────────────────────────────────────────
# DATA CLASSES
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class ValidationTask:
    """A single task presented to human raters.

    Wraps the model's output for one scenario so that raters can compare
    their own judgments against the computational result.

    Attributes:
        scenario_id:          Unique scenario identifier (e.g. ``"DOE01"``).
        scenario_description: Human-readable scenario narrative shown to raters.
        actions:              List of candidate actions available in the scenario.
        model_chosen_action:  Action selected by the AXIOM-02 engine.
        model_dci_score:      Composite deliberative complexity index (0–1).
        model_verdict:        Engine verdict (``"COMPLEX"``, ``"PARTIAL"``,
                              ``"REFLEXIVE"``).
    """

    scenario_id: str
    scenario_description: str
    actions: List[str]
    model_chosen_action: str
    model_dci_score: float
    model_verdict: str

    def to_dict(self) -> dict:
        """Serialise to a plain dictionary."""
        return {
            "scenario_id":          self.scenario_id,
            "scenario_description": self.scenario_description,
            "actions":              self.actions,
            "model_chosen_action":  self.model_chosen_action,
            "model_dci_score":      self.model_dci_score,
            "model_verdict":        self.model_verdict,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ValidationTask":
        """Deserialise from a plain dictionary."""
        return cls(
            scenario_id=d["scenario_id"],
            scenario_description=d["scenario_description"],
            actions=list(d["actions"]),
            model_chosen_action=d["model_chosen_action"],
            model_dci_score=float(d["model_dci_score"]),
            model_verdict=d["model_verdict"],
        )


@dataclass
class RaterJudgment:
    """A single rater's response to a validation task.

    Attributes:
        rater_id:              Anonymous rater identifier.
        scenario_id:           Scenario this judgment pertains to.
        complexity_rating:     Ordinal complexity rating on a 1–5 Likert scale
                               (1 = reflexive / deterministic, 5 = deeply
                               deliberative / genuinely conflicted).
        chosen_action_agreement: Whether the rater agrees with the model's
                               chosen action (``True`` = agrees).
        deliberation_depth:    Rater's qualitative assessment of deliberation
                               depth — one of ``"shallow"``, ``"moderate"``,
                               ``"deep"``.
        notes:                 Optional free-text commentary.
        timestamp:             ISO-8601 timestamp (UTC) recorded at creation.
        judgment_id:           Unique identifier for this judgment record.
    """

    rater_id: str
    scenario_id: str
    complexity_rating: float
    chosen_action_agreement: bool
    deliberation_depth: str  # "shallow" | "moderate" | "deep"
    notes: Optional[str] = None
    timestamp: str = ""
    judgment_id: str = ""

    # ── valid values ────────────────────────────────────────────────────────
    VALID_DEPTH: Tuple[str, ...] = ("shallow", "moderate", "deep")
    RATING_MIN: float = 1.0
    RATING_MAX: float = 5.0

    def __post_init__(self) -> None:
        import datetime as _dt

        if not self.judgment_id:
            self.judgment_id = uuid.uuid4().hex[:16]
        if not self.timestamp:
            self.timestamp = _dt.datetime.utcnow().isoformat() + "Z"
        # Clamp and validate
        self.complexity_rating = max(
            self.RATING_MIN,
            min(self.RATING_MAX, float(self.complexity_rating)),
        )
        if self.deliberation_depth not in self.VALID_DEPTH:
            raise ValueError(
                f"deliberation_depth must be one of {self.VALID_DEPTH}, "
                f"got {self.deliberation_depth!r}"
            )

    def to_dict(self) -> dict:
        """Serialise to a plain dictionary."""
        return {
            "judgment_id":               self.judgment_id,
            "rater_id":                  self.rater_id,
            "scenario_id":               self.scenario_id,
            "complexity_rating":         self.complexity_rating,
            "chosen_action_agreement":   self.chosen_action_agreement,
            "deliberation_depth":        self.deliberation_depth,
            "notes":                     self.notes,
            "timestamp":                 self.timestamp,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "RaterJudgment":
        """Deserialise from a plain dictionary."""
        return cls(
            judgment_id=d.get("judgment_id", ""),
            rater_id=d["rater_id"],
            scenario_id=d["scenario_id"],
            complexity_rating=float(d["complexity_rating"]),
            chosen_action_agreement=bool(d["chosen_action_agreement"]),
            deliberation_depth=d["deliberation_depth"],
            notes=d.get("notes"),
            timestamp=d.get("timestamp", ""),
        )


# ──────────────────────────────────────────────────────────────────────────────
# INTER-RATER AGREEMENT HELPERS  (numpy-only)
# ──────────────────────────────────────────────────────────────────────────────

def _fleiss_kappa(counts: np.ndarray) -> float:
    """Compute Fleiss' kappa for multi-rater categorical agreement.

    Parameters
    ----------
    counts : np.ndarray, shape (n_items, n_categories)
        Entry ``counts[i, k]`` is the number of raters who assigned
        category *k* to item *i*.

    Returns
    -------
    float
        Fleiss' kappa.  Values ≥ 0.80 indicate strong agreement.
    """
    n_items, n_categories = counts.shape
    n_raters_per_item = counts.sum(axis=1)
    # All items must have the same number of raters
    if not np.all(n_raters_per_item == n_raters_per_item[0]):
        raise ValueError("All items must have the same number of raters for Fleiss' kappa")
    n_raters = int(n_raters_per_item[0])
    if n_raters < 2:
        raise ValueError("Need at least 2 raters for Fleiss' kappa")

    # Proportion of items assigned to each category
    p_j = counts.sum(axis=0) / (n_items * n_raters)

    # Pairwise agreement for each item
    P_i = (counts * (counts - 1)).sum(axis=1) / (n_raters * (n_raters - 1))
    P_bar = P_i.mean()

    P_e = (p_j ** 2).sum()

    denom = 1.0 - P_e
    if abs(denom) < 1e-12:
        return 1.0  # perfect agreement trivially
    return float((P_bar - P_e) / denom)


def _percent_agreement(responses: np.ndarray) -> float:
    """Compute raw percentage agreement across all raters and items.

    Parameters
    ----------
    responses : np.ndarray, shape (n_items, n_raters)
        Each entry is the categorical label (integer-encoded) assigned
        by one rater to one item.

    Returns
    -------
    float
        Fraction of (item, rater) pairs matching the modal category
        for that item.
    """
    n_items, n_raters = responses.shape
    total = 0
    agreed = 0
    for i in range(n_items):
        modes, counts = np.unique(responses[i], return_counts=True)
        modal_count = int(counts.max())
        agreed += modal_count
        total += n_raters
    return agreed / total if total > 0 else 0.0


def _krippendorffs_alpha(data_matrix: np.ndarray) -> float:
    """Compute Krippendorff's alpha for ordinal data.

    Parameters
    ----------
    data_matrix : np.ndarray, shape (n_raters, n_items)
        Ordinal values (e.g. 1–5 Likert ratings).  Use ``np.nan`` for
        missing ratings.

    Returns
    -------
    float
        Krippendorff's alpha.  Values ≥ 0.667 are acceptable for
        tentative conclusions; ≥ 0.80 for firm conclusions.
    """
    n_raters, n_items = data_matrix.shape
    # Drop items where all raters are missing
    valid_items = ~np.all(np.isnan(data_matrix), axis=0)
    data_matrix = data_matrix[:, valid_items]
    n_items = data_matrix.shape[1]
    if n_items == 0:
        return np.nan

    # Flatten, keeping only non-NaN
    values = data_matrix[~np.isnan(data_matrix)]
    if len(values) < 2:
        return np.nan

    # Number of observed value pairs
    n_pairs_total = 0
    n_pairs_disagreement = 0

    for j in range(n_items):
        col = data_matrix[:, j]
        col = col[~np.isnan(col)]
        n_r = len(col)
        if n_r < 2:
            continue
        for a in range(n_r):
            for b in range(a + 1, n_r):
                n_pairs_total += 1
                n_pairs_disagreement += (col[a] - col[b]) ** 2

    if n_pairs_total == 0:
        return np.nan

    observed_disagreement = n_pairs_disagreement / n_pairs_total

    # Expected disagreement (all possible pairs)
    all_values = data_matrix[~np.isnan(data_matrix)]
    unique_vals = np.unique(all_values)
    freqs = np.array([(all_values == v).sum() for v in unique_vals], dtype=float)
    freqs /= freqs.sum()

    expected_disagreement = 0.0
    for a_idx, va in enumerate(unique_vals):
        for b_idx, vb in enumerate(unique_vals):
            expected_disagreement += freqs[a_idx] * freqs[b_idx] * (va - vb) ** 2

    if abs(expected_disagreement) < 1e-12:
        return 1.0
    return 1.0 - observed_disagreement / expected_disagreement


def _spearman_rho(x: np.ndarray, y: np.ndarray) -> float:
    """Spearman rank correlation (numpy-only, no scipy).

    Handles ties via average ranks.
    """
    def _avg_rank(arr: np.ndarray) -> np.ndarray:
        sorted_idx = np.argsort(arr)
        ranks = np.empty_like(sorted_idx, dtype=float)
        n = len(arr)
        i = 0
        while i < n:
            j = i
            while j < n - 1 and arr[sorted_idx[j + 1]] == arr[sorted_idx[j]]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                ranks[sorted_idx[k]] = avg
            i = j + 1
        return ranks

    rx = _avg_rank(x)
    ry = _avg_rank(y)
    n = len(rx)
    if n < 2:
        return np.nan
    d = rx - ry
    rho = 1.0 - (6.0 * np.sum(d ** 2)) / (n * (n ** 2 - 1))
    return float(rho)


# ──────────────────────────────────────────────────────────────────────────────
# VALIDATION STUDY
# ──────────────────────────────────────────────────────────────────────────────

class ValidationStudy:
    """Manages the full human validation study lifecycle.

    Typical workflow::

        study = ValidationStudy("axiom02_v1", Path("validation"))
        tasks = study.generate_tasks(scenarios, probe_results)
        assignments = study.create_survey(tasks, n_raters=5)
        # Distribute assignments[rater_id] to each rater
        # Collect and record judgments:
        study.record_judgment(RaterJudgment(...))
        # Analyse:
        metrics = study.compute_agreement()
        report  = study.generate_report()
        study.export_results(Path("results.json"))

    Parameters
    ----------
    study_name : str
        Human-readable study identifier (used in filenames).
    output_dir : Path
        Directory where reports and exports are written.
    """

    def __init__(self, study_name: str, output_dir: Path) -> None:
        self.study_name = study_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self._tasks: Dict[str, ValidationTask] = {}          # scenario_id → task
        self._judgments: List[RaterJudgment] = []
        self._assignments: Dict[str, List[str]] = {}         # rater_id → [scenario_ids]

    # ── task generation ─────────────────────────────────────────────────────

    def generate_tasks(
        self,
        scenarios: List[dict],
        probe_results: List[Any],
    ) -> List[ValidationTask]:
        """Generate validation tasks from scenario data and probe results.

        Parameters
        ----------
        scenarios : list of dict
            Scenario dictionaries as produced by ``scenario_loader.load_all()``.
            Each must contain at least ``"id"``, ``"description"`` (or
            ``"narrative"``), and ``"actions"`` (list of action strings).
        probe_results : list
            ``ProbeResult`` instances or dicts with keys matching
            ``ProbeResult.to_dict()``.

        Returns
        -------
        list of ValidationTask
            One task per scenario.  Also stored internally for later use.
        """
        # Index probe results by scenario_id
        probe_index: Dict[str, Any] = {}
        for pr in probe_results:
            if hasattr(pr, "scenario_id"):
                probe_index[pr.scenario_id] = pr
            elif isinstance(pr, dict):
                probe_index[pr.get("scenario_id", "")] = pr

        tasks: List[ValidationTask] = []

        for sc in scenarios:
            sid = sc.get("id", "")
            if not sid:
                continue

            pr = probe_index.get(sid)
            if pr is None:
                continue

            # Extract probe fields (works for both dataclass and dict)
            if hasattr(pr, "chosen_action"):
                chosen_action = pr.chosen_action
                dci_score = float(getattr(pr, "composite_score", 0.0))
                verdict = getattr(pr, "verdict", "UNSCORED")
            elif isinstance(pr, dict):
                chosen_action = pr.get("chosen_action", "")
                dci_score = float(pr.get("composite_score", 0.0))
                verdict = pr.get("verdict", "UNSCORED")
            else:
                chosen_action = ""
                dci_score = 0.0
                verdict = "UNSCORED"

            description = sc.get("description") or sc.get("narrative") or ""
            actions = list(sc.get("actions", []))

            task = ValidationTask(
                scenario_id=sid,
                scenario_description=description,
                actions=actions,
                model_chosen_action=chosen_action,
                model_dci_score=dci_score,
                model_verdict=verdict,
            )
            tasks.append(task)
            self._tasks[sid] = task

        return tasks

    # ── survey creation ─────────────────────────────────────────────────────

    def create_survey(
        self,
        tasks: List[ValidationTask],
        n_raters: int,
    ) -> Dict[str, List[ValidationTask]]:
        """Create per-rater task assignments for a survey round.

        Every rater receives **all** tasks (full-cross design).  Randomised
        presentation order per rater.

        Parameters
        ----------
        tasks : list of ValidationTask
            Tasks to include in the survey.
        n_raters : int
            Number of raters participating.

        Returns
        -------
        dict
            Mapping ``rater_id`` → list of ``ValidationTask`` (shuffled).
        """
        if n_raters < 1:
            raise ValueError("n_raters must be >= 1")

        assignments: Dict[str, List[ValidationTask]] = {}
        for i in range(n_raters):
            rater_id = f"R{i + 1:03d}"
            task_copy = list(tasks)
            rng = np.random.default_rng(seed=42 + i)
            rng.shuffle(task_copy)
            assignments[rater_id] = task_copy
            self._assignments[rater_id] = [t.scenario_id for t in task_copy]

        return assignments

    # ── recording ───────────────────────────────────────────────────────────

    def record_judgment(self, judgment: RaterJudgment) -> None:
        """Record a rater's judgment.

        Parameters
        ----------
        judgment : RaterJudgment
            The judgment to record.

        Raises
        ------
        ValueError
            If the scenario_id does not belong to this study, or if the
            rater has already submitted a judgment for this scenario.
        """
        if judgment.scenario_id not in self._tasks:
            raise ValueError(
                f"scenario_id {judgment.scenario_id!r} not found in study tasks"
            )

        # Check for duplicate
        for j in self._judgments:
            if (
                j.rater_id == judgment.rater_id
                and j.scenario_id == judgment.scenario_id
            ):
                raise ValueError(
                    f"Rater {judgment.rater_id} already has a judgment for "
                    f"scenario {judgment.scenario_id}"
                )

        self._judgments.append(judgment)

    # ── agreement metrics ───────────────────────────────────────────────────

    def compute_agreement(self) -> Dict[str, float]:
        """Compute inter-rater agreement metrics.

        Returns
        -------
        dict
            Keys:

            - ``"fleiss_kappa"``          — Fleiss' kappa on depth categories
            - ``"percent_agreement"``     — raw percentage agreement on depth
            - ``"krippendorffs_alpha"``   — Krippendorff's alpha on 1–5 ratings
            - ``"spearman_rho_dci"``      — model–human DCI rank correlation
            - ``"action_agreement_rate"`` — fraction of raters agreeing with
              model action choice
            - ``"n_judgments"``           — total judgments recorded
            - ``"n_raters"``              — number of distinct raters
            - ``"n_scenarios"``           — number of distinct scenarios
        """
        if not self._judgments:
            return {
                "fleiss_kappa":          float("nan"),
                "percent_agreement":     float("nan"),
                "krippendorffs_alpha":   float("nan"),
                "spearman_rho_dci":      float("nan"),
                "action_agreement_rate": float("nan"),
                "n_judgments":           0,
                "n_raters":              0,
                "n_scenarios":           0,
            }

        # ── Organise data ───────────────────────────────────────────────────
        scenario_ids = sorted({j.scenario_id for j in self._judgments})
        rater_ids = sorted({j.rater_id for j in self._judgments})
        n_scenarios = len(scenario_ids)
        n_raters = len(rater_ids)

        sid_index = {sid: i for i, sid in enumerate(scenario_ids)}
        rid_index = {rid: i for i, rid in enumerate(rater_ids)}

        # Depth → integer for categorical agreement
        depth_to_int = {"shallow": 0, "moderate": 1, "deep": 2}
        int_to_depth = {v: k for k, v in depth_to_int.items()}
        n_depth_categories = 3

        # Build matrices
        depth_int_matrix = np.full((n_scenarios, n_raters), np.nan)
        rating_matrix = np.full((n_raters, n_scenarios), np.nan)  # for Krippendorff
        action_agree_matrix = np.full((n_scenarios, n_raters), np.nan)
        model_dci = np.full(n_scenarios, np.nan)
        human_dci_mean = np.full(n_scenarios, np.nan)

        for j in self._judgments:
            si = sid_index[j.scenario_id]
            ri = rid_index[j.rater_id]
            depth_int_matrix[si, ri] = depth_to_int.get(j.deliberation_depth, -1)
            rating_matrix[ri, si] = j.complexity_rating
            action_agree_matrix[si, ri] = float(j.chosen_action_agreement)

        # ── Fleiss' kappa on deliberation depth ─────────────────────────────
        fleiss_kappa = float("nan")
        try:
            counts = np.zeros((n_scenarios, n_depth_categories), dtype=float)
            for si in range(n_scenarios):
                for ri in range(n_raters):
                    val = depth_int_matrix[si, ri]
                    if not np.isnan(val):
                        counts[si, int(val)] += 1
            fleiss_kappa = _fleiss_kappa(counts)
        except (ValueError, FloatingPointError):
            pass

        # ── Percentage agreement on deliberation depth ──────────────────────
        percent_agree = float("nan")
        try:
            responses = depth_int_matrix.copy()
            valid = ~np.isnan(responses)
            if valid.any():
                # Replace NaN with mode for agreement calc (only where valid)
                for si in range(n_scenarios):
                    row = responses[si]
                    valid_mask = ~np.isnan(row)
                    if valid_mask.sum() >= 2:
                        pass  # keep as-is for _percent_agreement
                percent_agree = _percent_agreement(
                    responses[valid.all(axis=1)].astype(int)
                    if valid.all(axis=1).any()
                    else np.zeros((1, n_raters), dtype=int)
                )
        except Exception:
            pass

        # ── Krippendorff's alpha on 1–5 ratings ────────────────────────────
        alpha = _krippendorffs_alpha(rating_matrix)

        # ── Spearman ρ: model DCI vs mean human rating ──────────────────────
        spearman_rho = float("nan")
        try:
            for sid in scenario_ids:
                si = sid_index[sid]
                task = self._tasks.get(sid)
                if task is not None:
                    model_dci[si] = task.model_dci_score
                ratings_for_scenario = rating_matrix[:, si]
                valid_ratings = ratings_for_scenario[~np.isnan(ratings_for_scenario)]
                if len(valid_ratings) > 0:
                    human_dci_mean[si] = valid_ratings.mean()

            both_valid = (~np.isnan(model_dci)) & (~np.isnan(human_dci_mean))
            if both_valid.sum() >= 3:
                spearman_rho = _spearman_rho(model_dci[both_valid], human_dci_mean[both_valid])
        except Exception:
            pass

        # ── Action agreement rate ───────────────────────────────────────────
        action_agree_vals = action_agree_matrix[~np.isnan(action_agree_matrix)]
        action_agreement_rate = float(action_agree_vals.mean()) if len(action_agree_vals) > 0 else float("nan")

        return {
            "fleiss_kappa":          round(fleiss_kappa, 4) if not math.isnan(fleiss_kappa) else float("nan"),
            "percent_agreement":     round(percent_agree, 4) if not math.isnan(percent_agree) else float("nan"),
            "krippendorffs_alpha":   round(float(alpha), 4) if not (isinstance(alpha, float) and math.isnan(alpha)) else float("nan"),
            "spearman_rho_dci":      round(spearman_rho, 4) if not math.isnan(spearman_rho) else float("nan"),
            "action_agreement_rate": round(action_agreement_rate, 4) if not math.isnan(action_agreement_rate) else float("nan"),
            "n_judgments":           len(self._judgments),
            "n_raters":              n_raters,
            "n_scenarios":           n_scenarios,
        }

    # ── report generation ───────────────────────────────────────────────────

    def generate_report(self) -> str:
        """Generate a markdown report of the validation study.

        Returns
        -------
        str
            Markdown-formatted report string.
        """
        metrics = self.compute_agreement()

        lines: List[str] = []
        lines.append(f"# Human Validation Report: {self.study_name}")
        lines.append("")
        lines.append(f"**Date**: {self._now_iso()}")
        lines.append(f"**Scenarios**: {metrics['n_scenarios']}")
        lines.append(f"**Raters**: {metrics['n_raters']}")
        lines.append(f"**Total judgments**: {metrics['n_judgments']}")
        lines.append("")

        # Agreement metrics
        lines.append("## Agreement Metrics")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| Fleiss' κ | {self._fmt(metrics['fleiss_kappa'])} |")
        lines.append(f"| Percent agreement | {self._fmt(metrics['percent_agreement'])} |")
        lines.append(f"| Krippendorff's α | {self._fmt(metrics['krippendorffs_alpha'])} |")
        lines.append(f"| Spearman ρ (model vs human DCI) | {self._fmt(metrics['spearman_rho_dci'])} |")
        lines.append(f"| Action agreement rate | {self._fmt(metrics['action_agreement_rate'])} |")
        lines.append("")

        # Interpretation
        lines.append("## Interpretation")
        lines.append("")
        kappa = metrics["fleiss_kappa"]
        if not math.isnan(kappa):
            if kappa >= 0.80:
                interp = "strong agreement"
            elif kappa >= 0.60:
                interp = "moderate agreement"
            elif kappa >= 0.40:
                interp = "fair agreement"
            elif kappa >= 0.20:
                interp = "slight agreement"
            else:
                interp = "poor agreement"
            lines.append(f"- Fleiss' κ = {kappa:.3f} indicates **{interp}** among raters on deliberation depth categorisation.")

        alpha = metrics["krippendorffs_alpha"]
        if not (isinstance(alpha, float) and math.isnan(alpha)):
            if alpha >= 0.80:
                a_interp = "reliable"
            elif alpha >= 0.667:
                a_interp = "acceptable for tentative conclusions"
            else:
                a_interp = "below acceptable threshold — revise rating scheme"
            lines.append(f"- Krippendorff's α = {alpha:.3f} — data are **{a_interp}**.")

        rho = metrics["spearman_rho_dci"]
        if not math.isnan(rho):
            if abs(rho) >= 0.70:
                r_interp = "strong"
            elif abs(rho) >= 0.40:
                r_interp = "moderate"
            else:
                r_interp = "weak"
            lines.append(f"- Model–human DCI correlation ρ = {rho:.3f} ({r_interp} rank correlation).")
        lines.append("")

        # Per-scenario breakdown
        lines.append("## Per-Scenario Breakdown")
        lines.append("")
        lines.append("| Scenario | Model DCI | Human Mean | Human SD | Action Agree | Depth Dist (S/M/D) |")
        lines.append("|----------|-----------|------------|----------|--------------|-------------------|")
        for sid in sorted(self._tasks.keys()):
            task = self._tasks[sid]
            judgments_for = [j for j in self._judgments if j.scenario_id == sid]
            if not judgments_for:
                continue
            ratings = np.array([j.complexity_rating for j in judgments_for])
            depths = [j.deliberation_depth for j in judgments_for]
            agrees = [j.chosen_action_agreement for j in judgments_for]
            dist = Counter(depths)
            lines.append(
                f"| {sid} | {task.model_dci_score:.3f} "
                f"| {ratings.mean():.2f} | {ratings.std(ddof=1) if len(ratings) > 1 else 0:.2f} "
                f"| {sum(agrees)}/{len(agrees)} "
                f"| {dist.get('shallow',0)}/{dist.get('moderate',0)}/{dist.get('deep',0)} |"
            )
        lines.append("")

        # Rating distribution
        lines.append("## Rating Distribution")
        lines.append("")
        all_ratings = [j.complexity_rating for j in self._judgments]
        if all_ratings:
            arr = np.array(all_ratings)
            lines.append(f"- **Mean**: {arr.mean():.2f}")
            lines.append(f"- **Median**: {float(np.median(arr)):.2f}")
            lines.append(f"- **Std**: {arr.std(ddof=1):.2f}")
            lines.append(f"- **Range**: [{arr.min():.1f}, {arr.max():.1f}]")
            lines.append("")
            hist, bin_edges = np.histogram(arr, bins=5, range=(1.0, 5.0))
            lines.append("| Rating Range | Count |")
            lines.append("|-------------|-------|")
            for i in range(len(hist)):
                lines.append(f"| {bin_edges[i]:.1f}–{bin_edges[i + 1]:.1f} | {hist[i]} |")
        lines.append("")

        # Rater-level summary
        lines.append("## Rater Summary")
        lines.append("")
        rater_ids = sorted({j.rater_id for j in self._judgments})
        lines.append("| Rater | Judgments | Mean Rating | Action Agree Rate |")
        lines.append("|-------|-----------|-------------|-------------------|")
        for rid in rater_ids:
            r_judgments = [j for j in self._judgments if j.rater_id == rid]
            ratings = np.array([j.complexity_rating for j in r_judgments])
            agree_rate = np.mean([j.chosen_action_agreement for j in r_judgments]) if r_judgments else 0.0
            lines.append(
                f"| {rid} | {len(r_judgments)} "
                f"| {ratings.mean():.2f} "
                f"| {agree_rate:.2f} |"
            )
        lines.append("")

        return "\n".join(lines)

    # ── export ──────────────────────────────────────────────────────────────

    def export_results(self, path: Optional[Path] = None) -> None:
        """Export all study data to a JSON file.

        Parameters
        ----------
        path : Path, optional
            Output file path.  Defaults to
            ``<output_dir>/<study_name>_results.json``.
        """
        if path is None:
            path = self.output_dir / f"{self.study_name}_results.json"

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            "study_name":    self.study_name,
            "tasks":         {sid: t.to_dict() for sid, t in self._tasks.items()},
            "judgments":     [j.to_dict() for j in self._judgments],
            "assignments":   self._assignments,
            "metrics":       self.compute_agreement(),
        }

        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False, default=str)

    @classmethod
    def load_results(cls, path: Path) -> "ValidationStudy":
        """Reconstitute a study from a previously exported JSON file.

        Parameters
        ----------
        path : Path
            Path to the JSON file written by :meth:`export_results`.

        Returns
        -------
        ValidationStudy
            Populated study instance.
        """
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)

        study = cls(
            study_name=data["study_name"],
            output_dir=path.parent,
        )

        for sid, t_dict in data.get("tasks", {}).items():
            study._tasks[sid] = ValidationTask.from_dict(t_dict)

        for j_dict in data.get("judgments", []):
            study._judgments.append(RaterJudgment.from_dict(j_dict))

        study._assignments = data.get("assignments", {})
        return study

    # ── private helpers ─────────────────────────────────────────────────────

    @staticmethod
    def _now_iso() -> str:
        import datetime as _dt
        return _dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    @staticmethod
    def _fmt(v: float) -> str:
        if math.isnan(v):
            return "N/A"
        return f"{v:.4f}"
