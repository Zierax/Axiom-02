# Axiom-02 - Truthimatics Public Version
"""
AXIOM-02  ·  WHITE-BOX ML COMPONENTS  v2.0

Interpretable, auditable neural network and ML components that complement
the existing drive-based system. Every weight is logged, every forward pass
is pure matrix multiplication, and every component provides human-readable
weight analysis.

COMPONENTS
──────────
1. AttentionGateNN        — learns which drives to attend to per scenario
2. DriveInteractionPredictor — predicts drive-pair interaction strengths
3. DeliberativePredictor      — fast DCI prediction from scenario parameters
4. ScenarioEmbedding         — learnable low-dimensional scenario representation
5. DriveEvolutionPredictor   — predicts drive activations at t+1
6. GradientFreeTrainer       — SGD training loop with numerical gradients
"""

from __future__ import annotations

import logging
import time
from typing import Any, Callable, Dict, List, Optional, Protocol, Tuple, runtime_checkable

import numpy as np

from axiom02.core.drives import ALL_DRIVES

logger = logging.getLogger("axiom02.ml")

N_DRIVES = len(ALL_DRIVES)  # 18
DRIVE_INDEX: Dict[str, int] = {d: i for i, d in enumerate(ALL_DRIVES)}


# ──────────────────────────────────────────────────────────────────────────────
# UTILITIES
# ──────────────────────────────────────────────────────────────────────────────

def _relu(x: np.ndarray) -> np.ndarray:
    return np.maximum(0.0, x)


def _relu_grad(x: np.ndarray) -> np.ndarray:
    return (x > 0.0).astype(np.float64)


def _softmax(x: np.ndarray) -> np.ndarray:
    e = np.exp(x - np.max(x, axis=-1, keepdims=True))
    return e / np.sum(e, axis=-1, keepdims=True)


def _sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))


def _xavier_init(fan_in: int, fan_out: int, rng: np.random.Generator) -> np.ndarray:
    std = np.sqrt(2.0 / (fan_in + fan_out))
    return rng.standard_normal((fan_in, fan_out)) * std


def _count_params(shapes: List[Tuple[int, ...]]) -> int:
    return int(sum(np.prod(s) for s in shapes))


# ──────────────────────────────────────────────────────────────────────────────
# PROTOCOL DEFINITIONS  (type-safe state dictionaries)
# ──────────────────────────────────────────────────────────────────────────────

@runtime_checkable
class Activations(Protocol):
    """Type-safe protocol for drive activation dictionaries."""
    def __getitem__(self, key: str) -> float: ...
    def __setitem__(self, key: str, value: float) -> None: ...
    def __contains__(self, key: object) -> bool: ...
    def keys(self) -> Any: ...
    def values(self) -> Any: ...
    def items(self) -> Any: ...
    def get(self, key: str, default: float = 0.0) -> float: ...


@runtime_checkable
class ModelWeights(Protocol):
    """Type-safe protocol for model weight dictionaries."""
    def __getitem__(self, key: str) -> np.ndarray: ...
    def __setitem__(self, key: str, value: np.ndarray) -> None: ...
    def __contains__(self, key: object) -> bool: ...
    def keys(self) -> Any: ...
    def values(self) -> Any: ...
    def items(self) -> Any: ...


@runtime_checkable
class PredictionResult(Protocol):
    """Type-safe protocol for model prediction results."""
    @property
    def prediction(self) -> float: ...
    @property
    def confidence(self) -> float: ...
    def to_dict(self) -> Dict[str, Any]: ...


# Type aliases for common patterns
DriveVector = np.ndarray  # Shape: (N_DRIVES,) — activation values
ScenarioVector = np.ndarray  # Shape: (N_PARAMS,) — scenario parameters
WeightMatrix = np.ndarray  # Shape: (N_DRIVES, N_DRIVES) — interaction weights


# ──────────────────────────────────────────────────────────────────────────────
# 1. ATTENTION GATE NN  (white-box attention mechanism)
# ──────────────────────────────────────────────────────────────────────────────

class AttentionGateNN:
    """
    Simple 2-layer attention network that learns which drives to attend to
    based on scenario context. NOT a black-box — every weight is interpretable.

    Architecture:
        Linear(scenario_dim, 32) → ReLU → Linear(32, N_DRIVES) → Softmax
        Output: attention weights over 18 drives

    The forward pass multiplies drive activations by the learned attention
    weights, producing attended activations. Weight analysis reveals which
    scenario parameters drive attention to which drives.
    """

    def __init__(
        self,
        scenario_dim: int = N_DRIVES,
        hidden_dim: int = 32,
        rng: Optional[np.random.Generator] = None,
    ):
        self.scenario_dim = scenario_dim
        self.hidden_dim = hidden_dim
        self.output_dim = N_DRIVES
        rng = rng or np.random.default_rng(42)

        # Weights: [scenario_dim, hidden_dim]
        self.W1: np.ndarray = _xavier_init(scenario_dim, hidden_dim, rng)
        self.b1: np.ndarray = np.zeros(hidden_dim)
        # Weights: [hidden_dim, N_DRIVES]
        self.W2: np.ndarray = _xavier_init(hidden_dim, self.output_dim, rng)
        self.b2: np.ndarray = np.zeros(self.output_dim)

        self._weight_shapes: List[Tuple[str, Tuple[int, ...]]] = [
            ("W1", self.W1.shape), ("b1", self.b1.shape),
            ("W2", self.W2.shape), ("b2", self.b2.shape),
        ]

    def forward(self, scenario_params: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute attention weights and attended activations.

        Args:
            scenario_params: (scenario_dim,) parameter vector

        Returns:
            attention_weights: (N_DRIVES,) softmax weights
            attended: (N_DRIVES,) — zeros (caller provides activations separately)
        """
        x = np.asarray(scenario_params, dtype=np.float64).ravel()
        # Layer 1
        z1 = x @ self.W1 + self.b1
        h1 = _relu(z1)
        # Layer 2 → logits
        z2 = h1 @ self.W2 + self.b2
        attention = _softmax(z2)
        return attention, np.zeros(N_DRIVES)

    def attend(
        self,
        scenario_params: np.ndarray,
        activations: np.ndarray,
    ) -> np.ndarray:
        """
        Apply attention weights to drive activations.

        Args:
            scenario_params: (scenario_dim,) parameter vector
            activations: (N_DRIVES,) current drive activations

        Returns:
            attended: (N_DRIVES,) activation × attention weight
        """
        attention, _ = self.forward(scenario_params)
        return attention * np.asarray(activations, dtype=np.float64)

    def weight_analysis(self) -> Dict[str, Any]:
        """
        Interpret which scenario parameters most strongly influence
        attention to each drive.
        """
        # W2 maps hidden → drive attention; W1 maps scenario → hidden
        # Combined importance: |W1| @ |W2| per drive
        combined = np.abs(self.W1) @ np.abs(self.W2)  # (scenario_dim, N_DRIVES)

        result: Dict[str, Any] = {
            "weight_shapes": dict(self._weight_shapes),
            "total_parameters": _count_params([s for _, s in self._weight_shapes]),
            "per_drive_top_params": {},
            "drive_attention_bias": {},
        }

        for i, drive in enumerate(ALL_DRIVES):
            drive_importance = combined[:, i]
            top_indices = np.argsort(drive_importance)[::-1]
            result["per_drive_top_params"][drive] = [
                (int(idx), float(drive_importance[idx]))
                for idx in top_indices[:5]
            ]
            result["drive_attention_bias"][drive] = float(self.b2[i])

        # Which parameter has the strongest influence overall
        param_total = np.sum(combined, axis=1)
        top_params = np.argsort(param_total)[::-1]
        result["most_influential_params"] = [
            (int(idx), float(param_total[idx]))
            for idx in top_params[:10]
        ]

        return result

    @property
    def param_shapes(self) -> List[Tuple[str, Tuple[int, ...]]]:
        return list(self._weight_shapes)

    def get_flat_params(self) -> np.ndarray:
        return np.concatenate([
            self.W1.ravel(), self.b1.ravel(),
            self.W2.ravel(), self.b2.ravel(),
        ])

    def set_flat_params(self, flat: np.ndarray) -> None:
        offset = 0
        for name, shape in self._weight_shapes:
            size = int(np.prod(shape))
            arr = flat[offset:offset + size].reshape(shape)
            if name == "W1": self.W1 = arr
            elif name == "b1": self.b1 = arr
            elif name == "W2": self.W2 = arr
            elif name == "b2": self.b2 = arr
            offset += size


# ──────────────────────────────────────────────────────────────────────────────
# 2. DRIVE INTERACTION PREDICTOR  (white-box regression)
# ──────────────────────────────────────────────────────────────────────────────

class DriveInteractionPredictor:
    """
    Predicts which drive pairs will interact most strongly in a given scenario.

    Architecture:
        Input: scenario_params(N) + drive_activations(N) → 2N features
        Linear(2N, 64) → ReLU → Linear(64, N×N) → reshape to N×N
        Output: predicted interaction matrix (N_DRIVES × N_DRIVES)

    Can be trained on actual simulation results to predict interaction patterns.
    All weights logged and interpretable.
    """

    def __init__(
        self,
        scenario_dim: int = N_DRIVES,
        hidden_dim: int = 64,
        rng: Optional[np.random.Generator] = None,
    ):
        self.scenario_dim = scenario_dim
        self.hidden_dim = hidden_dim
        self.input_dim = scenario_dim + N_DRIVES
        self.output_dim = N_DRIVES * N_DRIVES
        rng = rng or np.random.default_rng(42)

        self.W1: np.ndarray = _xavier_init(self.input_dim, hidden_dim, rng)
        self.b1: np.ndarray = np.zeros(hidden_dim)
        self.W2: np.ndarray = _xavier_init(hidden_dim, self.output_dim, rng)
        self.b2: np.ndarray = np.zeros(self.output_dim)

        self._weight_shapes: List[Tuple[str, Tuple[int, ...]]] = [
            ("W1", self.W1.shape), ("b1", self.b1.shape),
            ("W2", self.W2.shape), ("b2", self.b2.shape),
        ]

    def forward(
        self,
        scenario_params: np.ndarray,
        activations: np.ndarray,
    ) -> np.ndarray:
        """
        Predict the interaction matrix for a given scenario and drive state.

        Args:
            scenario_params: (scenario_dim,) parameter vector
            activations: (N_DRIVES,) current drive activations

        Returns:
            interaction_matrix: (N_DRIVES, N_DRIVES) pairwise interaction strengths
        """
        x = np.concatenate([
            np.asarray(scenario_params, dtype=np.float64).ravel(),
            np.asarray(activations, dtype=np.float64).ravel(),
        ])
        z1 = x @ self.W1 + self.b1
        h1 = _relu(z1)
        z2 = h1 @ self.W2 + self.b2
        return z2.reshape(N_DRIVES, N_DRIVES)

    def weight_analysis(self) -> Dict[str, Any]:
        """
        Interpret which input features most influence each interaction.
        """
        # Feature importance: |W1| @ |W2| per output
        combined = np.abs(self.W1) @ np.abs(self.W2)  # (input_dim, output_dim)

        input_labels = (
            [f"param_{i}" for i in range(self.scenario_dim)]
            + [f"drive_{ALL_DRIVES[i]}" for i in range(N_DRIVES)]
        )

        result: Dict[str, Any] = {
            "weight_shapes": dict(self._weight_shapes),
            "total_parameters": _count_params([s for _, s in self._weight_shapes]),
            "input_dim": self.input_dim,
            "output_dim": self.output_dim,
            "per_interaction_top_features": {},
        }

        # Sample a few key interactions for interpretation
        key_pairs = [
            (DRIVE_INDEX["rage"], DRIVE_INDEX["fear"]),
            (DRIVE_INDEX["love"], DRIVE_INDEX["sacrifice_drive"]),
            (DRIVE_INDEX["grief"], DRIVE_INDEX["despair"]),
            (DRIVE_INDEX["spite"], DRIVE_INDEX["cold_logic"]),
        ]

        for i, j in key_pairs:
            out_idx = i * N_DRIVES + j
            feat_imp = combined[:, out_idx]
            top_indices = np.argsort(feat_imp)[::-1][:5]
            pair_key = f"{ALL_DRIVES[i]}↔{ALL_DRIVES[j]}"
            result["per_interaction_top_features"][pair_key] = [
                (input_labels[int(idx)], float(feat_imp[idx]))
                for idx in top_indices
            ]

        return result

    @property
    def param_shapes(self) -> List[Tuple[str, Tuple[int, ...]]]:
        return list(self._weight_shapes)

    def get_flat_params(self) -> np.ndarray:
        return np.concatenate([
            self.W1.ravel(), self.b1.ravel(),
            self.W2.ravel(), self.b2.ravel(),
        ])

    def set_flat_params(self, flat: np.ndarray) -> None:
        offset = 0
        for name, shape in self._weight_shapes:
            size = int(np.prod(shape))
            arr = flat[offset:offset + size].reshape(shape)
            if name == "W1": self.W1 = arr
            elif name == "b1": self.b1 = arr
            elif name == "W2": self.W2 = arr
            elif name == "b2": self.b2 = arr
            offset += size


# ──────────────────────────────────────────────────────────────────────────────
# 3. DELIBERATIVE PREDICTOR  (white-box DCI predictor)
# ──────────────────────────────────────────────────────────────────────────────

class DeliberativePredictor:
    """
    Predicts DCI (deliberative complexity composite score) directly from scenario
    parameters without running the full simulation.

    Architecture:
        Linear(40, 64) → ReLU → Linear(64, 32) → ReLU → Linear(32, 1) → Sigmoid
        Output: predicted DCI ∈ [0, 1]

    Weight importance analysis shows which parameters matter most for DCI.
    """

    def __init__(
        self,
        input_dim: int = 40,
        hidden1: int = 64,
        hidden2: int = 32,
        rng: Optional[np.random.Generator] = None,
    ):
        self.input_dim = input_dim
        rng = rng or np.random.default_rng(42)

        self.W1: np.ndarray = _xavier_init(input_dim, hidden1, rng)
        self.b1: np.ndarray = np.zeros(hidden1)
        self.W2: np.ndarray = _xavier_init(hidden1, hidden2, rng)
        self.b2: np.ndarray = np.zeros(hidden2)
        self.W3: np.ndarray = _xavier_init(hidden2, 1, rng)
        self.b3: np.ndarray = np.zeros(1)

        self._weight_shapes: List[Tuple[str, Tuple[int, ...]]] = [
            ("W1", self.W1.shape), ("b1", self.b1.shape),
            ("W2", self.W2.shape), ("b2", self.b2.shape),
            ("W3", self.W3.shape), ("b3", self.b3.shape),
        ]

    def forward(self, params: np.ndarray) -> float:
        """
        Predict DCI from scenario parameter vector.

        Args:
            params: (input_dim,) scenario parameter vector

        Returns:
            predicted DCI ∈ [0, 1]
        """
        x = np.asarray(params, dtype=np.float64).ravel()[:self.input_dim]
        z1 = x @ self.W1 + self.b1
        h1 = _relu(z1)
        z2 = h1 @ self.W2 + self.b2
        h2 = _relu(z2)
        z3 = h2 @ self.W3 + self.b3
        return float(_sigmoid(z3)[0])

    def weight_analysis(self) -> Dict[str, Any]:
        """
        Identify which input parameters most influence DCI prediction.
        Uses |W1| · |W2| · |W3| chain to trace feature importance.
        """
        chain1 = np.abs(self.W1) @ np.abs(self.W2)  # (input_dim, hidden2)
        chain2 = chain1 @ np.abs(self.W3)            # (input_dim, 1)
        importance = chain2.ravel()

        top_indices = np.argsort(importance)[::-1]

        result: Dict[str, Any] = {
            "weight_shapes": dict(self._weight_shapes),
            "total_parameters": _count_params([s for _, s in self._weight_shapes]),
            "input_dim": self.input_dim,
            "most_important_params": [
                (int(idx), float(importance[idx]))
                for idx in top_indices[:15]
            ],
            "per_layer_norms": {
                "W1_frobenius": float(np.linalg.norm(self.W1)),
                "W2_frobenius": float(np.linalg.norm(self.W2)),
                "W3_frobenius": float(np.linalg.norm(self.W3)),
            },
        }
        return result

    @property
    def param_shapes(self) -> List[Tuple[str, Tuple[int, ...]]]:
        return list(self._weight_shapes)

    def get_flat_params(self) -> np.ndarray:
        return np.concatenate([
            self.W1.ravel(), self.b1.ravel(),
            self.W2.ravel(), self.b2.ravel(),
            self.W3.ravel(), self.b3.ravel(),
        ])

    def set_flat_params(self, flat: np.ndarray) -> None:
        offset = 0
        for name, shape in self._weight_shapes:
            size = int(np.prod(shape))
            arr = flat[offset:offset + size].reshape(shape)
            if name == "W1": self.W1 = arr
            elif name == "b1": self.b1 = arr
            elif name == "W2": self.W2 = arr
            elif name == "b2": self.b2 = arr
            elif name == "W3": self.W3 = arr
            elif name == "b3": self.b3 = arr
            offset += size


# ──────────────────────────────────────────────────────────────────────────────
# 4. SCENARIO EMBEDDING  (learnable scenario representation)
# ──────────────────────────────────────────────────────────────────────────────

class ScenarioEmbedding:
    """
    Learns a low-dimensional embedding of scenarios that captures their
    emotional structure. Similar scenarios cluster in embedding space.

    Architecture:
        Linear(40, 16) → ReLU → Linear(16, 8)
        Output: 8-dimensional embedding

    Can be used for scenario recommendation via cosine similarity.
    """

    def __init__(
        self,
        input_dim: int = 40,
        hidden_dim: int = 16,
        embed_dim: int = 8,
        rng: Optional[np.random.Generator] = None,
    ):
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.embed_dim = embed_dim
        rng = rng or np.random.default_rng(42)

        self.W1: np.ndarray = _xavier_init(input_dim, hidden_dim, rng)
        self.b1: np.ndarray = np.zeros(hidden_dim)
        self.W2: np.ndarray = _xavier_init(hidden_dim, embed_dim, rng)
        self.b2: np.ndarray = np.zeros(embed_dim)

        self._weight_shapes: List[Tuple[str, Tuple[int, ...]]] = [
            ("W1", self.W1.shape), ("b1", self.b1.shape),
            ("W2", self.W2.shape), ("b2", self.b2.shape),
        ]

    def forward(self, params: np.ndarray) -> np.ndarray:
        """
        Compute scenario embedding.

        Args:
            params: (input_dim,) scenario parameter vector

        Returns:
            embedding: (embed_dim,) normalized embedding vector
        """
        x = np.asarray(params, dtype=np.float64).ravel()[:self.input_dim]
        z1 = x @ self.W1 + self.b1
        h1 = _relu(z1)
        z2 = h1 @ self.W2 + self.b2
        norm = np.linalg.norm(z2)
        if norm > 1e-8:
            z2 = z2 / norm
        return z2

    def similarity(self, params_a: np.ndarray, params_b: np.ndarray) -> float:
        """
        Cosine similarity between two scenario embeddings.
        """
        emb_a = self.forward(params_a)
        emb_b = self.forward(params_b)
        dot = float(np.dot(emb_a, emb_b))
        return float(np.clip(dot, -1.0, 1.0))

    def recommend(
        self,
        target_params: np.ndarray,
        candidate_params_list: List[np.ndarray],
        top_k: int = 5,
    ) -> List[Tuple[int, float]]:
        """
        Find the top_k most similar scenarios to the target.
        """
        target_emb = self.forward(target_params)
        scores = []
        for i, cand in enumerate(candidate_params_list):
            cand_emb = self.forward(cand)
            sim = float(np.dot(target_emb, cand_emb))
            scores.append((i, float(np.clip(sim, -1.0, 1.0))))
        scores.sort(key=lambda x: -x[1])
        return scores[:top_k]

    def weight_analysis(self) -> Dict[str, Any]:
        """
        Interpret which input features dominate each embedding dimension.
        """
        combined = np.abs(self.W1) @ np.abs(self.W2)  # (input_dim, embed_dim)

        result: Dict[str, Any] = {
            "weight_shapes": dict(self._weight_shapes),
            "total_parameters": _count_params([s for _, s in self._weight_shapes]),
            "embedding_dimensions": {},
        }

        for dim in range(self.embed_dim):
            feat_imp = combined[:, dim]
            top_indices = np.argsort(feat_imp)[::-1][:5]
            result["embedding_dimensions"][f"dim_{dim}"] = [
                (int(idx), float(feat_imp[idx]))
                for idx in top_indices
            ]

        return result

    @property
    def param_shapes(self) -> List[Tuple[str, Tuple[int, ...]]]:
        return list(self._weight_shapes)

    def get_flat_params(self) -> np.ndarray:
        return np.concatenate([
            self.W1.ravel(), self.b1.ravel(),
            self.W2.ravel(), self.b2.ravel(),
        ])

    def set_flat_params(self, flat: np.ndarray) -> None:
        offset = 0
        for name, shape in self._weight_shapes:
            size = int(np.prod(shape))
            arr = flat[offset:offset + size].reshape(shape)
            if name == "W1": self.W1 = arr
            elif name == "b1": self.b1 = arr
            elif name == "W2": self.W2 = arr
            elif name == "b2": self.b2 = arr
            offset += size


# ──────────────────────────────────────────────────────────────────────────────
# 5. DRIVE EVOLUTION PREDICTOR  (temporal prediction)
# ──────────────────────────────────────────────────────────────────────────────

class DriveEvolutionPredictor:
    """
    Predicts drive activations at time t+1 given activations at time t,
    neuromodulator state, and the current step number.

    Architecture:
        Input: activations(N) + neuromodulators(5) + step(1) = N+6
        Linear(N+6, 48) → ReLU → Linear(48, N) → Sigmoid
        Output: predicted activations at t+1 ∈ [0, 1]^N

    Can replace the hand-crafted dynamics with learned dynamics.
    All weights interpretable.
    """

    def __init__(
        self,
        hidden_dim: int = 48,
        rng: Optional[np.random.Generator] = None,
    ):
        self.input_dim = N_DRIVES + 5 + 1  # activations + neuromodulators + step
        self.output_dim = N_DRIVES
        rng = rng or np.random.default_rng(42)

        self.W1: np.ndarray = _xavier_init(self.input_dim, hidden_dim, rng)
        self.b1: np.ndarray = np.zeros(hidden_dim)
        self.W2: np.ndarray = _xavier_init(hidden_dim, self.output_dim, rng)
        self.b2: np.ndarray = np.zeros(self.output_dim)

        self._weight_shapes: List[Tuple[str, Tuple[int, ...]]] = [
            ("W1", self.W1.shape), ("b1", self.b1.shape),
            ("W2", self.W2.shape), ("b2", self.b2.shape),
        ]

    def forward(
        self,
        activations: np.ndarray,
        neuromodulators: np.ndarray,
        step: float,
    ) -> np.ndarray:
        """
        Predict next-step activations.

        Args:
            activations: (N_DRIVES,) current drive activations
            neuromodulators: (5,) [dopamine, serotonin, norepinephrine, cortisol, oxytocin]
            step: current time step (normalized 0..1)

        Returns:
            predicted_activations: (N_DRIVES,) activations at t+1
        """
        x = np.concatenate([
            np.asarray(activations, dtype=np.float64).ravel()[:N_DRIVES],
            np.asarray(neuromodulators, dtype=np.float64).ravel()[:5],
            [float(step)],
        ])
        z1 = x @ self.W1 + self.b1
        h1 = _relu(z1)
        z2 = h1 @ self.W2 + self.b2
        return _sigmoid(z2)

    def weight_analysis(self) -> Dict[str, Any]:
        """
        Interpret which inputs most influence each drive's evolution.
        """
        combined = np.abs(self.W1) @ np.abs(self.W2)  # (input_dim, N_DRIVES)

        input_labels = (
            [f"drive_{ALL_DRIVES[i]}" for i in range(N_DRIVES)]
            + ["dopamine", "serotonin", "norepinephrine", "cortisol", "oxytocin"]
            + ["step"]
        )

        result: Dict[str, Any] = {
            "weight_shapes": dict(self._weight_shapes),
            "total_parameters": _count_params([s for _, s in self._weight_shapes]),
            "per_drive_top_inputs": {},
        }

        for i, drive in enumerate(ALL_DRIVES):
            feat_imp = combined[:, i]
            top_indices = np.argsort(feat_imp)[::-1][:5]
            result["per_drive_top_inputs"][drive] = [
                (input_labels[int(idx)], float(feat_imp[idx]))
                for idx in top_indices
            ]

        return result

    @property
    def param_shapes(self) -> List[Tuple[str, Tuple[int, ...]]]:
        return list(self._weight_shapes)

    def get_flat_params(self) -> np.ndarray:
        return np.concatenate([
            self.W1.ravel(), self.b1.ravel(),
            self.W2.ravel(), self.b2.ravel(),
        ])

    def set_flat_params(self, flat: np.ndarray) -> None:
        offset = 0
        for name, shape in self._weight_shapes:
            size = int(np.prod(shape))
            arr = flat[offset:offset + size].reshape(shape)
            if name == "W1": self.W1 = arr
            elif name == "b1": self.b1 = arr
            elif name == "W2": self.W2 = arr
            elif name == "b2": self.b2 = arr
            offset += size


# ──────────────────────────────────────────────────────────────────────────────
# 6. GRADIENT-FREE TRAINER  (numerical gradient SGD with momentum)
# ──────────────────────────────────────────────────────────────────────────────

class GradientFreeTrainer:
    """
    Training loop for all white-box components using numerical gradients.

    Features:
        - Simple SGD with momentum
        - Tracks training loss per epoch
        - Supports early stopping
        - Logs weight statistics per epoch
        - Compatible with any model that implements get/set_flat_params

    The numerical gradient approach computes ∂L/∂w ≈ (L(w+ε) - L(w-ε)) / (2ε)
    for each parameter. This is slow but reliable and requires no autodiff.
    """

    def __init__(
        self,
        learning_rate: float = 0.01,
        momentum: float = 0.9,
        epsilon: float = 1e-5,
        early_stopping_patience: int = 20,
    ):
        self.learning_rate = learning_rate
        self.momentum = momentum
        self.epsilon = epsilon
        self.early_stopping_patience = early_stopping_patience

    def train(
        self,
        model: Any,
        X: np.ndarray,
        y: np.ndarray,
        loss_fn: Callable[[np.ndarray, np.ndarray], float],
        predict_fn: Callable[[Any, np.ndarray], np.ndarray],
        epochs: int = 500,
        batch_size: int = 0,
        log_every: int = 50,
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None,
    ) -> Dict[str, Any]:
        """
        Train a model using numerical gradient descent with momentum.

        Args:
            model: any object with get_flat_params() / set_flat_params()
            X: (N, input_dim) training inputs
            y: (N, ...) training targets
            loss_fn: loss_fn(predictions, targets) → scalar loss
            predict_fn: predict_fn(model, x_i) → prediction for single sample
            epochs: maximum training epochs
            batch_size: 0 = full batch, >0 = mini-batch
            log_every: log stats every N epochs
            X_val, y_val: optional validation data for early stopping

        Returns:
            training_history dict with loss curves, weight stats, timing
        """
        N = len(X)
        n_params = len(model.get_flat_params())

        # Initialise momentum
        velocity = np.zeros(n_params)
        best_val_loss = float("inf")
        patience_counter = 0

        history: Dict[str, Any] = {
            "train_loss": [],
            "val_loss": [],
            "epoch_times": [],
            "weight_norms": [],
            "weight_means": [],
            "weight_stds": [],
            "learning_rates": [],
            "epochs_trained": 0,
        }

        t_start = time.perf_counter()

        for epoch in range(epochs):
            t_epoch = time.perf_counter()

            # Shuffle training data
            if batch_size > 0:
                indices = np.random.permutation(N)
                epoch_loss = 0.0
                n_batches = 0
                for start in range(0, N, batch_size):
                    batch_idx = indices[start:start + batch_size]
                    grad = self._compute_gradient(model, X[batch_idx], y[batch_idx],
                                                  loss_fn, predict_fn)
                    velocity = self.momentum * velocity - self.learning_rate * grad
                    new_params = model.get_flat_params() + velocity
                    model.set_flat_params(new_params)
                    epoch_loss += loss_fn(
                        predict_fn(model, X[batch_idx]), y[batch_idx]
                    )
                    n_batches += 1
                epoch_loss /= max(n_batches, 1)
            else:
                grad = self._compute_gradient(model, X, y, loss_fn, predict_fn)
                velocity = self.momentum * velocity - self.learning_rate * grad
                new_params = model.get_flat_params() + velocity
                model.set_flat_params(new_params)
                preds = predict_fn(model, X)
                epoch_loss = float(loss_fn(preds, y))

            history["train_loss"].append(epoch_loss)
            history["epoch_times"].append(time.perf_counter() - t_epoch)

            # Weight statistics
            params = model.get_flat_params()
            history["weight_norms"].append(float(np.linalg.norm(params)))
            history["weight_means"].append(float(np.mean(params)))
            history["weight_stds"].append(float(np.std(params)))
            history["learning_rates"].append(self.learning_rate)

            # Validation + early stopping
            if X_val is not None and y_val is not None:
                val_preds = predict_fn(model, X_val)
                val_loss = float(loss_fn(val_preds, y_val))
                history["val_loss"].append(val_loss)

                if val_loss < best_val_loss:
                    best_val_loss = val_loss
                    patience_counter = 0
                else:
                    patience_counter += 1
                    if patience_counter >= self.early_stopping_patience:
                        logger.info("Early stopping at epoch %d (val_loss=%.6f)",
                                    epoch, val_loss)
                        break

            # Logging
            if (epoch + 1) % log_every == 0 or epoch == 0:
                val_str = ""
                if history["val_loss"]:
                    val_str = f"  val={history['val_loss'][-1]:.6f}"
                logger.info(
                    "Epoch %d/%d  loss=%.6f%s  norm=%.4f  time=%.3fs",
                    epoch + 1, epochs, epoch_loss, val_str,
                    history["weight_norms"][-1], history["epoch_times"][-1],
                )

        history["total_time"] = time.perf_counter() - t_start
        history["epochs_trained"] = len(history["train_loss"])
        return history

    def _compute_gradient(
        self,
        model: Any,
        X: np.ndarray,
        y: np.ndarray,
        loss_fn: Callable,
        predict_fn: Callable,
    ) -> np.ndarray:
        """
        Compute numerical gradient of loss w.r.t. all model parameters.
        Uses central differences: ∂L/∂w ≈ (L(w+ε) - L(w-ε)) / (2ε)
        """
        params = model.get_flat_params()
        n_params = len(params)
        gradient = np.zeros(n_params)

        BATCH_SIZE = 500
        for batch_start in range(0, n_params, BATCH_SIZE):
            batch_end = min(batch_start + BATCH_SIZE, n_params)
            for i in range(batch_start, batch_end):
                # Forward perturbation
                params_plus = params.copy()
                params_plus[i] += self.epsilon
                model.set_flat_params(params_plus)
                loss_plus = loss_fn(predict_fn(model, X), y)

                # Backward perturbation
                params_minus = params.copy()
                params_minus[i] -= self.epsilon
                model.set_flat_params(params_minus)
                loss_minus = loss_fn(predict_fn(model, X), y)

                gradient[i] = (loss_plus - loss_minus) / (2.0 * self.epsilon)

        # Restore original parameters
        model.set_flat_params(params)
        return gradient


# ──────────────────────────────────────────────────────────────────────────────
# LOSS FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────

def mse_loss(predictions: np.ndarray, targets: np.ndarray) -> float:
    """Mean squared error loss."""
    diff = np.asarray(predictions, dtype=np.float64) - np.asarray(targets, dtype=np.float64)
    return float(np.mean(diff ** 2))


def binary_crossentropy(predictions: np.ndarray, targets: np.ndarray) -> float:
    """Binary cross-entropy loss for sigmoid outputs."""
    preds = np.clip(np.asarray(predictions, dtype=np.float64), 1e-7, 1.0 - 1e-7)
    targs = np.asarray(targets, dtype=np.float64)
    return float(-np.mean(targs * np.log(preds) + (1.0 - targs) * np.log(1.0 - preds)))


def huber_loss(predictions: np.ndarray, targets: np.ndarray, delta: float = 1.0) -> float:
    """Huber loss (robust to outliers)."""
    diff = np.asarray(predictions, dtype=np.float64) - np.asarray(targets, dtype=np.float64)
    abs_diff = np.abs(diff)
    quadratic = np.minimum(abs_diff, delta)
    linear = abs_diff - quadratic
    return float(np.mean(0.5 * quadratic ** 2 + delta * linear))


# ──────────────────────────────────────────────────────────────────────────────
# CONVENIENCE: Prediction wrappers for the trainer
# ──────────────────────────────────────────────────────────────────────────────

def _attention_predict(model: AttentionGateNN, x: np.ndarray) -> np.ndarray:
    """Predict attention weights for a batch."""
    return np.array([model.forward(xi)[0] for xi in x])


def _interaction_predict(model: DriveInteractionPredictor, x: np.ndarray) -> np.ndarray:
    """Predict interaction matrices for a batch."""
    return np.array([model.forward(xi[:N_DRIVES], xi[N_DRIVES:]) for xi in x])


def _deliberative_predict(model: DeliberativePredictor, x: np.ndarray) -> np.ndarray:
    """Predict DCI for a batch."""
    return np.array([model.forward(xi) for xi in x])


def _evolution_predict(model: DriveEvolutionPredictor, x: np.ndarray) -> np.ndarray:
    """Predict next-step activations for a batch."""
    return np.array([
        model.forward(xi[:N_DRIVES], xi[N_DRIVES:N_DRIVES + 5], xi[-1])
        for xi in x
    ])


# ──────────────────────────────────────────────────────────────────────────────
# PUBLIC API
# ──────────────────────────────────────────────────────────────────────────────

# Backward-compatible alias
ConsciousnessPredictor = DeliberativePredictor


__all__ = [
    "AttentionGateNN",
    "DriveInteractionPredictor",
    "DeliberativePredictor",
    "ConsciousnessPredictor",
    "ScenarioEmbedding",
    "DriveEvolutionPredictor",
    "GradientFreeTrainer",
    "mse_loss",
    "binary_crossentropy",
    "huber_loss",
    "N_DRIVES",
    "DRIVE_INDEX",
]
