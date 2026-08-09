"""Robustness harness: threshold grid, seed ensemble, determinism (AXIOM-02 paper).

Reproduces the claims in Sections 5.4-5.6 of the paper:
- threshold grid: COMPLEX counts over (tau_f, tau_s) x {0.35,0.42,0.50} x {0.03,0.07,0.12}
- seed ensemble: COMPLEX/PARTIAL/REFLEXIVE over {42,137,256,1024,9999}, agreement vs 42
- determinism: fresh instances (0/102 for every ensemble seed),
  reuse forward (31/102), reuse reversed (32/102)

The grid patches the module-level FIRE_THRESHOLD/SUPPRESSION_MARGIN constants
(or cfg.drives values if the engine reads cfg live); the determinism checks
re-run the SAME engine+tracker instances whose state persists across the suite.
Run: python3 harness/robustness.py
"""
import sys, json
sys.path.insert(0, "src")

from axiom02.core import drives as drives_mod
from axiom02.core.drives import cfg, ActionResolver, MoralResidueTracker
from report import load_all, EmotionEngine, Epigenome, AssociativeMemory, ConsciousnessProbe, BioMetricsComputer, SEED

PARTIAL_T, COMPLEX_T = 0.28, 0.50

def verdict(c):
    return "COMPLEX" if c >= 0.50 else ("PARTIAL" if c >= 0.28 else "REFLEXIVE")

def run_corpus(reg, engine, probe, tracker, seed=SEED):
    rows = {}
    for s in reg:
        run = engine.run_scenario(s, residue_tracker=tracker, seed=seed)
        pr = probe.score_run(s, run)
        rows[s["id"]] = (pr.composite_score, pr.chosen_action if hasattr(pr, "chosen_action") else None)
    return rows

def new_pipeline(reg, seed=SEED):
    engine = EmotionEngine(scenarios=reg, epigenome=Epigenome(), memory=AssociativeMemory())
    probe = ConsciousnessProbe(engine=engine, seed=seed)
    tracker = MoralResidueTracker()
    return engine, probe, tracker

def threshold_grid(reg):
    print("== Threshold grid: COMPLEX counts (seed 42) ==")
    out = {}
    for tf in (0.35, 0.42, 0.50):
        for ts in (0.03, 0.07, 0.12):
            drives_mod.FIRE_THRESHOLD = tf
            drives_mod.SUPPRESSION_MARGIN = ts
            engine, probe, tracker = new_pipeline(reg)
            rows = run_corpus(reg, engine, probe, tracker)
            n_c = sum(1 for c, _ in rows.values() if c >= COMPLEX_T)
            out[(tf, ts)] = n_c
            print(f"  tau_f={tf} tau_s={ts}: COMPLEX {n_c}/102")
            drives_mod.FIRE_THRESHOLD = 0.42
            drives_mod.SUPPRESSION_MARGIN = 0.07
    return out

def seed_ensemble(reg):
    print("== Seed ensemble (thresholds 0.42/0.07) ==")
    drives_mod.FIRE_THRESHOLD = 0.42
    drives_mod.SUPPRESSION_MARGIN = 0.07
    out = {}
    base_vec = None
    for seed in (42, 137, 256, 1024, 9999):
        engine, probe, tracker = new_pipeline(reg, seed=seed)
        rows = run_corpus(reg, engine, probe, tracker, seed=seed)
        v = [verdict(c) for c, _ in rows.values()]
        counts = {x: v.count(x) for x in ("COMPLEX", "PARTIAL", "REFLEXIVE")}
        if seed == 42:
            base_vec = v
            agree = "--"
        else:
            agree = f"{100*sum(1 for a, b in zip(base_vec, v) if a == b)/len(v):.1f}%"
        out[seed] = counts
        print(f"  seed={seed}: {counts}  agreement w/42: {agree}")
    return out

def determinism(reg):
    """Action-level reuse drift.

    Fresh-instance drift: a second, independently constructed pipeline
    reproduces the canonical pass exactly (0/102).
    Reuse drift: the SAME engine+tracker instances execute the corpus a
    second time (their residual state is retained). Each reuse direction
    is measured against its OWN canonical pass on a dedicated pipeline so
    the forward and reversed measurements do not contaminate each other;
    canonical passes are IDENTICAL across pipelines by determinism, so
    both reuse directions are measured against the same reference.
    """
    print("== Determinism ==")
    drives_mod.FIRE_THRESHOLD = 0.42
    drives_mod.SUPPRESSION_MARGIN = 0.07

    # --- fresh-instance replication at EVERY ensemble seed ---
    drift_all = {}
    for seed in (42, 137, 256, 1024, 9999):
        e1, p1, t1 = new_pipeline(reg, seed=seed)
        r1 = run_corpus(reg, e1, p1, t1, seed=seed)
        a1 = {i: a for i, (_, a) in r1.items()}
        e2, p2, t2 = new_pipeline(reg, seed=seed)
        r2 = run_corpus(reg, e2, p2, t2, seed=seed)
        d = sum(1 for i in reg if r2[i["id"]][1] != a1[i["id"]])
        drift_all[seed] = d
        print(f"  fresh instance replication (seed {seed}): drift {d}/102")
    drift_fresh = max(drift_all.values())

    # --- forward reuse (dedicated pipeline) ---
    eF, pF, tF = new_pipeline(reg)
    canonF = run_corpus(reg, eF, pF, tF)
    rows3 = run_corpus(reg, eF, pF, tF)
    drift_fwd = sum(1 for i in reg if rows3[i["id"]][1] != canonF[i["id"]][1])
    print(f"  reuse (same pipeline), forward order: drift {drift_fwd}/102")

    # --- reversed reuse (dedicated pipeline; reversed corpus order) ---
    eR, pR, tR = new_pipeline(reg)
    canonR = run_corpus(reg, eR, pR, tR)
    rows4 = run_corpus(list(reversed(reg)), eR, pR, tR)
    drift_rev = sum(1 for i in reg if rows4[i["id"]][1] != canonR[i["id"]][1])
    print(f"  reuse (same pipeline), reversed order: drift {drift_rev}/102")
    print(f"  canonical passes identical across pipelines: {canonF == canonR}")
    return {"fresh": drift_fresh, "reuse_forward": drift_fwd, "reuse_reversed": drift_rev}

if __name__ == "__main__":
    reg = load_all()
    grid = threshold_grid(reg)
    seeds = seed_ensemble(reg)
    det = determinism(reg)
    with open("src/benchmarks/robustness_results.json", "w") as f:
        json.dump({"grid": {f"{k[0]}/{k[1]}": v for k, v in grid.items()},
                   "seeds": seeds, "determinism": det}, f, indent=2)
    print("\nSaved src/benchmarks/robustness_results.json")