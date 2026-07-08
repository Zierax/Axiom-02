#!/usr/bin/env python3
"""
AXIOM-02  ·  RESULTS & VISUALS REGENERATOR  (Truthimatics Public Version)
Deterministically re-runs every scenario through the consolidated engine,
consciousness probe, and bio-metric computer, then emits:
    benchmarks/results.json
    benchmarks/scenario_descriptions.md
    benchmarks/README.md
    benchmarks/charts/*.png
Run:  python3 report.py [--seed 42]
"""
import argparse
import json
import logging
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from scenario_loader import load_all, stats as reg_stats
from emotion_engine import EmotionEngine
from consciousness_probe import ConsciousnessProbe
from bio_metrics import BioMetricsComputer
from epigenetics import Epigenome, AssociativeMemory

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger("axiom02.report")

SEED = 42
BENCH = ROOT / "benchmarks"
CHARTS = BENCH / "charts"


def build_system(seed: int):
    reg = load_all()
    engine = EmotionEngine(
        scenarios=reg,
        epigenome=Epigenome(),
        memory=AssociativeMemory(),
    )
    probe = ConsciousnessProbe(engine=engine, seed=seed)
    comp = BioMetricsComputer()
    return reg, engine, probe, comp


def collect(reg, engine, probe, comp, seed):
    rows = []
    for s in reg:
        sid = s["id"]
        try:
            run = engine.run_scenario(s, residue_tracker=None, seed=seed)
            bm = comp.compute(run["sim_result"], run, run.get("residue_applied"), s)
            pr = probe.run(sid, use_residue=False)
        except Exception as exc:  # never let one bad scenario abort the batch
            log.exception("scenario %s failed: %s", sid, exc)
            continue
        bio = bm.to_dict()
        rows.append({
            "id": sid,
            "label": s.get("label"),
            "category": s.get("category"),
            "pair_id": s.get("pair_id"),
            "verdict": pr.verdict,
            "composite_score": round(pr.composite_score, 4),
            "chosen_action": pr.chosen_action,
            "dominant_drive": pr.dominant_drive,
            "deadlock_fraction": round(pr.deadlock_fraction, 4),
            "oscillation_index": round(pr.oscillation_index, 4),
            "irrationality": round(pr.irrationality, 4),
            "spite_score": round(pr.spite_score, 4),
            "criterion_scores": {k: round(v, 4) for k, v in pr.criterion_scores.items()},
            "qualia_name": run.get("qualia_name"),
            "qualia_novelty": round(run.get("qualia_novelty", 0.0), 4),
            "meta_frustration": round(run.get("meta_frustration", 0.0), 4),
            "dissonance_breaks": run.get("dissonance_breaks", 0),
            "fast_path": run.get("fast_path_label"),
            "modulator_label": run.get("modulator_label"),
            "complexity": round(float(bio.get("consciousness_complexity", 0.0) or 0.0), 4),
            "bio": bio,
            "mods_final": {k: round(v, 4) for k, v in run.get("mods_final", {}).items()},
        })
    return rows


def write_results(rows):
    out = {
        "seed": SEED,
        "engine": "EmotionEngine (canonical, version-free)",
        "total_scenarios": len(rows),
        "results": rows,
    }
    (BENCH / "results.json").write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    log.info("wrote results.json (%d scenarios)", len(rows))


def write_descriptions(reg, rows_by_id):
    lines = ["# AXIOM-02 — Scenario Descriptions\n",
             f"_Generated for {len(reg)} scenarios. Truthimatics Public Version._\n"]
    cats = {}
    for s in reg:
        cats.setdefault(s.get("category", "?"), []).append(s)
    for cat, items in sorted(cats.items()):
        lines.append(f"\n## {cat} ({len(items)})\n")
        for s in items:
            row = rows_by_id.get(s["id"], {})
            verdict = row.get("verdict", "")
            lines.append(f"- **{s['id']}** `{s.get('label')}` — {s.get('description','')}")
            lines.append(f"  - verdict: `{verdict}` · chosen: `{s.get('human_expected')}` "
                         f"(expected) / `{row.get('chosen_action')}` (model)")
    (BENCH / "scenario_descriptions.md").write_text("\n".join(lines), encoding="utf-8")
    log.info("wrote scenario_descriptions.md")


def write_readme(rows, reg):
    st = reg_stats(reg)
    verdicts = Counter(r["verdict"] for r in rows)
    lines = [
        "# AXIOM-02 Consciousness Engine Benchmarks — Truthimatics Public Version\n",
        f"Engine: EmotionEngine (canonical, version-free). Seed: {SEED}. "
        f"Scenarios tested: {len(rows)}.\n",
        "## Verdict distribution",
        "```",
    ]
    for v, c in verdicts.most_common():
        lines.append(f"  {v:<14}: {c}")
    lines.append("```")
    lines.append("\n## Execution summary")
    lines.append(f"- Total scenarios : {len(rows)}")
    lines.append(f"- Cascades        : {st.get('cascade_chains', 0)}")
    lines.append(f"- Stage trees     : {st.get('stage_trees', 0)}")
    lines.append(f"- Emergent        : {st.get('emergent', 0)}")
    lines.append(f"- Trauma tests    : {st.get('post_trauma', 0)}")
    lines.append("\n## Top complexity (most 'conscious')")
    for r in sorted(rows, key=lambda x: -x["complexity"])[:8]:
        lines.append(f"- {r['id']} ({r['label']}) — complexity {r['complexity']:.3f}, "
                     f"verdict {r['verdict']}, deadlock {r['deadlock_fraction']:.2f}")
    (BENCH / "README.md").write_text("\n".join(lines), encoding="utf-8")
    log.info("wrote benchmark README")


def make_charts(rows):
    CHARTS.mkdir(parents=True, exist_ok=True)
    complexities = np.array([r["complexity"] for r in rows], dtype=float)
    deadlocks = np.array([r["deadlock_fraction"] for r in rows], dtype=float)
    spites = np.array([r["spite_score"] for r in rows], dtype=float)
    irrs = np.array([r["irrationality"] for r in rows], dtype=float)

    # 1) Complexity distribution
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(complexities, bins=20, color="#4C72B0", edgecolor="white")
    ax.set_title("Complexity score distribution")
    ax.set_xlabel("Composite complexity"); ax.set_ylabel("Scenarios")
    fig.tight_layout(); fig.savefig(CHARTS / "complexity_dist.png", dpi=120); plt.close(fig)

    # 2) Complexity vs deadlock
    fig, ax = plt.subplots(figsize=(7, 4))
    sc = ax.scatter(complexities, deadlocks, c=spites, cmap="viridis", s=28)
    ax.set_title("Complexity vs deadlock fraction")
    ax.set_xlabel("Complexity"); ax.set_ylabel("Deadlock fraction")
    fig.colorbar(sc, label="Spite score")
    fig.tight_layout(); fig.savefig(CHARTS / "complexity_vs_deadlock.png", dpi=120); plt.close(fig)

    # 3) Mean neuromodulator baselines across scenarios
    mod_keys = sorted({k for r in rows for k in r["mods_final"]})
    means = [float(np.mean([r["mods_final"].get(k, 0.0) for r in rows])) for k in mod_keys]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(range(len(mod_keys)), means, color="#DD8452")
    ax.set_xticks(range(len(mod_keys)))
    ax.set_xticklabels(mod_keys, rotation=45, ha="right", fontsize=7)
    ax.set_title("Mean neuromodulator baseline (across scenarios)")
    ax.set_ylabel("Activation")
    fig.tight_layout(); fig.savefig(CHARTS / "modulator_baselines.png", dpi=120); plt.close(fig)

    # 4) Spite vs irrationality
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.scatter(spites, irrs, s=28, color="#55A868", alpha=0.8)
    ax.set_title("Spite score vs irrationality signal")
    ax.set_xlabel("Spite score"); ax.set_ylabel("Irrationality")
    fig.tight_layout(); fig.savefig(CHARTS / "spite_irrationality_hist.png", dpi=120); plt.close(fig)

    log.info("wrote 4 charts to %s", CHARTS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=SEED)
    args = ap.parse_args()

    reg, engine, probe, comp = build_system(args.seed)
    log.info("registry loaded: %d scenarios", len(reg))

    rows = collect(reg, engine, probe, comp, args.seed)
    if not rows:
        log.error("no scenarios produced results; aborting")
        return

    BENCH.mkdir(parents=True, exist_ok=True)
    write_results(rows)
    rows_by_id = {r["id"]: r for r in rows}
    write_descriptions(reg, rows_by_id)
    write_readme(rows, reg)
    make_charts(rows)
    log.info("REGENERATION COMPLETE")


if __name__ == "__main__":
    main()
