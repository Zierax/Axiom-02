"""FastAPI HTTP interface for AXIOM-02.

Optional. Install with:  pip install "axiom-02[api]"
Run with:                python main.py api [--host ..] [--port ..] [--seed ..]

The app holds one engine + probe instance per server, so the stateful moral
residue accumulates across requests exactly as in `ConsciousnessProbe.run_all()`
(server-side calls are serialized). `POST /run` additionally accepts a ``seed``
for a one-off, state-free measurement on a throwaway engine.
"""

from __future__ import annotations

import threading
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from axiom02.core.engine import EmotionEngine
from axiom02.core.epigenetics import AssociativeMemory, Epigenome
from axiom02.core.probe import ConsciousnessProbe
from axiom02.core.scenario_loader import load_all

APP_TITLE = "AXIOM-02"
APP_VERSION = "2.0.0"


class RunRequest(BaseModel):
    scenario_id: str
    seed: Optional[int] = None


class RunResponse(BaseModel):
    scenario_id: str
    verdict: str
    composite_score: float
    criterion_scores: dict
    chosen_action: str
    dominant_drive: str
    deadlock_fraction: float
    oscillation_index: float
    irrationality: float
    spite_score: float


def _result_to_model(result) -> RunResponse:
    return RunResponse(
        scenario_id=result.scenario_id,
        verdict=result.verdict,
        composite_score=result.composite_score,
        criterion_scores=result.criterion_scores,
        chosen_action=result.chosen_action,
        dominant_drive=result.dominant_drive,
        deadlock_fraction=result.deadlock_fraction,
        oscillation_index=result.oscillation_index,
        irrationality=result.irrationality,
        spite_score=result.spite_score,
    )


def build_app(seed: int = 42) -> FastAPI:
    reg = load_all()
    engine = EmotionEngine(scenarios=reg, epigenome=Epigenome(), memory=AssociativeMemory())
    probe = ConsciousnessProbe(engine=engine, seed=seed)
    lock = threading.Lock()
    probe.reset_residue()

    app = FastAPI(title=APP_TITLE, version=APP_VERSION)

    @app.get("/")
    def root() -> dict:
        return {
            "name": APP_TITLE,
            "version": APP_VERSION,
            "scenarios": len(reg),
            "seed": seed,
            "docs": "/docs",
        }

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    @app.get("/scenarios")
    def scenarios(category: Optional[str] = None) -> List[dict]:
        rows = []
        for s in reg:
            if category and s.get("category") != category:
                continue
            rows.append({"id": s["id"], "label": s.get("label"),
                         "category": s.get("category"),
                         "pair_id": s.get("pair_id")})
        return rows

    @app.get("/scenarios/{scenario_id}", response_model=RunResponse)
    def get_scenario(scenario_id: str) -> RunResponse:
        ids = {s["id"] for s in reg}
        if scenario_id not in ids:
            raise HTTPException(status_code=404, detail=f"Unknown scenario '{scenario_id}'")
        with lock:
            result = probe.run(scenario_id)
        return _result_to_model(result)

    @app.post("/run", response_model=RunResponse)
    def run(req: RunRequest) -> RunResponse:
        ids = {s["id"] for s in reg}
        if req.scenario_id not in ids:
            raise HTTPException(status_code=404, detail=f"Unknown scenario '{req.scenario_id}'")
        if req.seed is None or req.seed == seed:
            with lock:
                result = probe.run(req.scenario_id)
        else:
            fresh = EmotionEngine(scenarios=reg, epigenome=Epigenome(), memory=AssociativeMemory())
            fresh_probe = ConsciousnessProbe(engine=fresh, seed=req.seed)
            result = fresh_probe.run(req.scenario_id)
        return _result_to_model(result)

    return app
