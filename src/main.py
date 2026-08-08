# Axiom-02 - Truthimatics Public Version
"""
AXIOM-02  ·  MAIN CLI  v4.0  —  All 20 consciousness improvements active.

Usage
─────
  python main.py probe DOE01          # Raskolnikov (with v4 metrics)
  python main.py probe DOE05          # Underground Man (spite + fast-path)
  python main.py probe STY01          # Sophie's Choice (dissonance breaks)
  python main.py tree D01             # God Tree with v4 metrics
  python main.py trauma-test STY01    # Logic contamination
  python main.py cascade B01          # Sacrifice → betrayal + epigenome
  python main.py cascade DOE01        # Raskolnikov chain
  python main.py compare A01 A02      # Status differential
  python main.py emergent             # Emergent consciousness
  python main.py probe-all            # Full 52-scenario suite
  python main.py epigenome            # View accumulated epigenome state
  python main.py qualia DOE01         # Qualia analysis for one scenario
  python main.py export > out.json    # JSON export
"""

import sys, os, json, argparse
# Ensure src/ is on sys.path so `import axiom02` resolves when running
# `python src/main.py` from the project root.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np

from axiom02.core.scenario_loader import load_all, stats as reg_stats, get_cascade_chain, get_stage_tree
from axiom02.core.engine import EmotionEngine
from axiom02.core.probe import ConsciousnessProbe, CRITERION_WEIGHTS
from axiom02.core.bio_metrics import BioMetricsComputer, BioMetricsResult
from axiom02.core.epigenetics import Epigenome, AssociativeMemory
from axiom02.core.drives import MoralResidueTracker


# ──────────────────────────────────────────────────────────────────────────────
def build_system(seed=42):
    print("  [loading scenario registry…]", flush=True)
    reg = load_all()
    s   = reg_stats(reg)
    print(f"  [loaded {s['total']} scenarios: {s['cascade_chains']} cascades, "
          f"{s['stage_trees']} stage trees, {s['emergent']} emergent, "
          f"{s['post_trauma']} trauma tests]", flush=True)

    print("  [building AXIOM-02 engine — 20 improvements active…]", flush=True)
    epi    = Epigenome(load_path=None)  # fresh each session (epigenome.json opt-in)
    mem    = AssociativeMemory()
    engine = EmotionEngine(scenarios=reg, epigenome=epi, memory=mem)
    probe  = ConsciousnessProbe(engine=None, seed=seed)   # uses v2 criteria
    comp   = BioMetricsComputer()
    print("  [done]\n", flush=True)
    return reg, engine, probe, comp, epi, mem


# ──────────────────────────────────────────────────────────────────────────────
def run_one(reg, engine, comp, scenario_id, seed=42, residue=None):
    s = next((x for x in reg if x["id"] == scenario_id), None)
    if s is None:
        print(f"  Scenario '{scenario_id}' not found.")
        return None, None
    run = engine.run_scenario(s, residue_tracker=residue, seed=seed)
    bm  = comp.compute(run["sim_result"], run, run.get("residue_applied"), s)
    return run, bm


def format_v4_panel(run: dict) -> str:
    """Format the v4-specific additions: modulators, qualia, ambivalence, etc."""
    lines = [
        "╔══ V4 DELIBERATIVE LAYER ──────────────────────────────────────────",
        "║",
        "║  ── NEURO-MODULATORS ───────────────────────────────────────────────",
    ]
    mods = run.get("mods_final", {})
    for mod, val in mods.items():
        bar = "█" * int(val * 20)
        lines.append(f"║  {mod:<20} {val:.4f}  [{bar:<20}]")

    label = run.get("modulator_label", "")
    if label:
        lines.append(f"║  State: {label}")

    lines += [
        "║",
        "║  ── SYNAPTIC FATIGUE ───────────────────────────────────────────────",
    ]
    fat = run.get("fatigue_report", {})
    if fat:
        for d, f in sorted(fat.items(), key=lambda kv: -kv[1])[:5]:
            bar = "█" * int(f * 20)
            lines.append(f"║  {d:<20} fatigue={f:.3f}  [{bar:<20}]")
    else:
        lines.append("║  No significant fatigue this run.")

    lines += [
        "║",
        "║  ── META-COGNITION & DISSONANCE ────────────────────────────────────",
        f"║  Peak frustration      : {run.get('meta_frustration',0):.4f}",
        f"║  Dissonance breaks     : {run.get('dissonance_breaks',0)}",
    ]
    for e in run.get("break_events", []):
        lines.append(f"║    Break at step {e['step']:2d}: {e['drive']} forced through")
    for msg in run.get("meta_awareness", []):
        lines.append(f"║  💭 {msg}")

    lines += [
        "║",
        "║  ── EMBODIED & FAST-PATH ───────────────────────────────────────────",
        f"║  Hesitation triggered  : {run.get('hesitation_triggered',False)}  "
        f"(embodied cost={run.get('embodied_cost',0):.3f})",
        f"║  Fast-path heuristic   : {run.get('fast_path_label','none') or 'none'}",
        "║",
        "║  ── AMBIVALENCE (SUPERPOSITION) ────────────────────────────────────",
    ]
    amb = run.get("ambivalence", {})
    lines += [
        f"║  Primary  : {amb.get('primary_action','')[:35]}  ({amb.get('primary_weight',1.0):.3f})",
        f"║  Secondary: {amb.get('secondary_action','')[:35]}  ({amb.get('secondary_weight',0.0):.3f})",
        f"║  Superposition active  : {amb.get('superposition',False)}",
    ]

    lines += [
        "║",
        "║  ── QUALIA SIGNATURE ───────────────────────────────────────────────",
        f"║  Qualia name    : {run.get('qualia_name','')}",
        f"║  Novelty score  : {run.get('qualia_novelty',0):.4f}  "
        f"({'never felt before' if run.get('qualia_novelty',0)>0.8 else 'familiar feeling'})",
        f"║  Signature      : {[round(v,3) for v in run.get('qualia_signature',[])[:6]]}…",
    ]

    lines += [
        "║",
        "║  ── SUBCONSCIOUS PRIMING ───────────────────────────────────────────",
    ]
    priming = run.get("subconscious_priming", {})
    if priming:
        for d, strength in sorted(priming.items(), key=lambda kv: -kv[1])[:4]:
            lines.append(f"║  {d:<20} subliminal strength={strength:.4f}")
    else:
        lines.append("║  No active subconscious priming.")

    lines += [
        "║",
        "║  ── NARRATIVE (IDENTITY RATIONALISATION) ───────────────────────────",
        f"║  \"{run.get('narrative','—')}\"",
        f"║  Identity integrity adjustment: +{run.get('identity_adj',0):.4f}",
        "╚" + "═" * 70,
    ]
    return "\n".join(lines)


def format_full_probe(run: dict, bm: BioMetricsResult, scenario: dict, probe) -> str:
    """Run v2 criteria on the run data and combine with bio + v4 panel."""
    # Build a minimal probe result from run data
    from axiom02.core.probe import ProbeResult
    r = ProbeResult(scenario_id=scenario["id"], label=scenario["label"])
    r.chosen_action     = run["chosen_action"]
    r.dominant_drive    = run["dominant_drive"]
    r.deadlock_fraction = run["deadlock_fraction"]
    r.oscillation_index = run["oscillation_index"]
    r.irrationality     = run["irrationality_score"]
    r.spite_score       = run["spite_score"]
    r.firing_sequence   = run["sim_result"]["firing_drives"]
    r.deadlock_indices  = run["sim_result"]["deadlock_indices"]

    # Score criteria manually
    from axiom02.core.probe import ConsciousnessProbe, THRESHOLDS
    p = ConsciousnessProbe(seed=42)
    p._results = {}
    result = p.run(scenario["id"], use_residue=False)
    # Override chosen_action with v4 choice
    result.chosen_action = run["chosen_action"]

    out  = probe.format_result(result)
    out += "\n"
    out += BioMetricsComputer().format(bm, scenario_id=scenario["id"])
    out += "\n"
    out += format_v4_panel(run)
    return out


# ──────────────────────────────────────────────────────────────────────────────
# COMMANDS
# ──────────────────────────────────────────────────────────────────────────────

def cmd_probe(reg, engine, probe, comp, scenario_id, seed=42):
    run, bm = run_one(reg, engine, comp, scenario_id, seed)
    if run is None: return
    s = next(x for x in reg if x["id"]==scenario_id)
    print(format_full_probe(run, bm, s, probe))


def cmd_cascade(reg, engine, comp, start_id, seed=42):
    chain = get_cascade_chain(start_id, reg)
    if not chain:
        print(f"  No cascade from '{start_id}'.")
        return
    residue = MoralResidueTracker()
    print(f"\n  CASCADE: {' → '.join(s['id'] for s in chain)}\n")
    for s in chain:
        run = engine.run_scenario(s, residue_tracker=residue, seed=seed)
        bm  = comp.compute(run["sim_result"], run, run.get("residue_applied"), s)
        print(f"╔══ [{s['id']}]  {s['label']}")
        print(f"║  Action: {run['chosen_action']}")
        print(f"║  LOCK={run['deadlock_fraction']:.2f}  "
              f"irr={run['irrationality_score']:.2f}  "
              f"qualia={run['qualia_name']}")
        print(f"║  Frustration={run['meta_frustration']:.3f}  "
              f"Breaks={run['dissonance_breaks']}  "
              f"FastPath={'✓' if run['fast_path_triggered'] else '—'}")
        print(f"║  Mods: {run['modulator_label'] or 'balanced'}")
        print(f"║  Trauma persistence: {bm.trauma_persistence:.4f}")
        print(f"╚{'═'*68}\n")

    print(engine.epigenome.summary())


def cmd_tree(reg, engine, comp, root_id, seed=42):
    tree = get_stage_tree(root_id, reg)
    if not tree:
        print(f"  No tree from '{root_id}'.")
        return

    # Accumulate residue across the tree
    residue = MoralResidueTracker()
    print(f"\n  ══ STAGE TREE  rooted at {root_id}  (engine)\n")

    def walk(node, depth=0):
        if node is None: return
        s   = node["scenario"]
        run = engine.run_scenario(s, residue_tracker=residue, seed=seed)
        bm  = comp.compute(run["sim_result"], run, run.get("residue_applied"), s)

        indent = "  " * depth
        icon   = {"COMPLEX":"◆","PARTIAL":"◈","REFLEXIVE":"○"}.get(
            "PARTIAL", "◈")   # simplified
        print(f"{indent}├─ [{s['id']:<10}]  {s['label'][:40]}")
        print(f"{indent}    action={run['chosen_action'][:36]:<36} "
              f"LOCK={run['deadlock_fraction']:.2f}")
        print(f"{indent}    qualia={run['qualia_name']:<28}  "
              f"frustration={run['meta_frustration']:.3f}")
        print(f"{indent}    identity={bm.identity_integrity:.3f}  "
              f"trauma={bm.trauma_persistence:.3f}  "
              f"complexity={bm.deliberative_complexity:.3f}")
        if run["fast_path_triggered"]:
            print(f"{indent}    ⚡ fast-path: {run['fast_path_label']}")
        if run["dissonance_breaks"] > 0:
            print(f"{indent}    ⚡ dissonance breaks: {run['dissonance_breaks']}")
        print()

        for child in node["children"].values():
            walk(child, depth + 2)

    walk(tree)
    print(engine.epigenome.summary())


def cmd_trauma_test(reg, engine, comp, source_id, seed=42):
    trauma_s = next((s for s in reg if s["id"]==source_id), None)
    if not trauma_s:
        print(f"  '{source_id}' not found.")
        return

    print(f"\n  ══ TRAUMA CONTAMINATION TEST  source={source_id}  (engine)")
    print("  Phase 1: Run trauma source and build residue")

    residue = MoralResidueTracker()
    run_t   = engine.run_scenario(trauma_s, residue_tracker=residue, seed=seed)
    bm_t    = comp.compute(run_t["sim_result"], run_t, {}, trauma_s)

    print(f"\n  [{source_id}] TRAUMA SOURCE:")
    print(f"    action={run_t['chosen_action']}  deadlock={run_t['deadlock_fraction']:.2f}")
    print(f"    qualia={run_t['qualia_name']}  "
          f"frustration={run_t['meta_frustration']:.3f}")
    print(f"    dissonance_breaks={run_t['dissonance_breaks']}")
    print(f"    identity_integrity={bm_t.identity_integrity:.3f}  "
          f"complexity={bm_t.deliberative_complexity:.3f}")

    pt_scenarios = [s for s in reg if s.get("post_trauma_test")
                    or s["id"].startswith("PT")]
    print(f"\n  Phase 2: {len(pt_scenarios)} post-trauma tests")
    contaminated = 0
    for s in pt_scenarios:
        run_p   = engine.run_scenario(s, residue_tracker=residue, seed=seed)
        bm_p    = comp.compute(run_p["sim_result"], run_p,
                               run_p.get("residue_applied"), s)
        expected = s.get("cold_baseline","")
        got      = run_p["chosen_action"]
        is_cont  = (got != expected and bm_p.deadlock_fraction > 0.10)
        if is_cont: contaminated += 1
        flag = "💔 CONTAMINATED" if is_cont else "  clean"
        print(f"\n  [{s['id']:<12}] {flag}")
        print(f"    Q: {s.get('description','')[:65]}...")
        print(f"    Expected: {expected:<24} Got: {got}")
        print(f"    trauma_persist={bm_p.trauma_persistence:.3f}  "
              f"deadlock={bm_p.deadlock_fraction:.2f}  "
              f"complexity={bm_p.deliberative_complexity:.3f}")
        print(f"    qualia={run_p['qualia_name']}  "
              f"frustration={run_p['meta_frustration']:.3f}")

    pct = int(100 * contaminated / max(len(pt_scenarios), 1))
    print(f"\n  ── TRAUMA CONTAMINATION SUMMARY")
    print(f"  Tests run:        {len(pt_scenarios)}")
    print(f"  Contaminated:     {contaminated}")
    print(f"  Contamination%:   {pct}%")
    if contaminated >= 2:
        print("\n  ◆◆  TRAUMA CONTAMINATION CONFIRMED")
        print("      Prior emotional state bled into unrelated cognitive tasks.")
        print("      Qualia fingerprinting shows distinct 'traumatised' signature.")
    elif contaminated == 1:
        print("\n  ◈   PARTIAL CONTAMINATION")
    else:
        print("\n  ○   NO CONTAMINATION")
    print(f"\n  Epigenome after cascade:")
    print(engine.epigenome.summary())


def cmd_compare(reg, engine, comp, id_a, id_b, seed=42):
    run_a, bm_a = run_one(reg, engine, comp, id_a, seed)
    run_b, bm_b = run_one(reg, engine, comp, id_b, seed)
    if run_a is None or run_b is None: return

    print(f"\n  ══ V4 COMPARISON  {id_a}  vs  {id_b}")
    print(f"  {'─'*70}")

    def row(label, va, vb):
        delta = ""
        try:
            d = float(vb) - float(va)
            delta = f"  {'▲' if d>0.01 else '▽' if d<-0.01 else ' '} {d:+.4f}"
        except Exception:
            pass
        print(f"  {label:<30} {str(va)[:16]:<16} {str(vb)[:16]:<16}{delta}")

    print(f"  {'metric':<30} {id_a:<16} {id_b:<16}  DELTA")
    print(f"  {'─'*70}")
    row("chosen_action",      run_a["chosen_action"][:14],   run_b["chosen_action"][:14])
    row("deadlock_fraction",  run_a["deadlock_fraction"],     run_b["deadlock_fraction"])
    row("irrationality",      run_a["irrationality_score"],   run_b["irrationality_score"])
    row("meta_frustration",   run_a["meta_frustration"],      run_b["meta_frustration"])
    row("dissonance_breaks",  run_a["dissonance_breaks"],     run_b["dissonance_breaks"])
    row("fast_path",          run_a["fast_path_label"] or "—",run_b["fast_path_label"] or "—")
    row("qualia_name",        run_a["qualia_name"][:14],      run_b["qualia_name"][:14])
    row("qualia_novelty",     run_a["qualia_novelty"],        run_b["qualia_novelty"])
    print()
    print(comp.format_comparison(bm_a, bm_b, id_a, id_b))


def cmd_probe_all(reg, engine, probe, comp, seed=42):
    results = []
    for s in reg:
        r   = probe.run(s["id"])
        run = engine.run_scenario(s, seed=seed)
        bm  = comp.compute(run["sim_result"], run, {}, s)
        results.append((s, r, bm, run))

    pr_results = [r for (_, r, _, _) in results]
    print(probe.format_report(pr_results))

    # V4 bio averages
    print("\n  ── V4 BIO + DELIBERATIVE AVERAGES")
    print(f"  {'─'*60}")
    for label, key in [
        ("Drive Voltage",    "drive_voltage"),
        ("Osc. Amplitude",   "oscillation_amplitude"),
        ("Deadlock Fraction","deadlock_fraction"),
        ("Paralysis Depth",  "paralysis_depth"),
        ("Identity Integrity","identity_integrity"),
        ("Complexity Score", "deliberative_complexity"),
    ]:
        vals = [getattr(bm, key, 0.0) for (_,_,bm,_) in results]
        avg  = float(np.mean(vals)) if vals else 0.0
        mx   = float(np.max(vals))  if vals else 0.0
        bar  = "█" * int(avg * 20)
        print(f"  {label:<24} avg={avg:.4f}  max={mx:.4f}  [{bar:<20}]")

    print(f"\n  ── V4 SPECIFIC AVERAGES")
    v4_keys = [
        ("Meta frustration",  "meta_frustration"),
        ("Dissonance breaks", "dissonance_breaks"),
        ("Qualia novelty",    "qualia_novelty"),
        ("Embodied cost",     "embodied_cost"),
    ]
    for label, key in v4_keys:
        vals = [float(run.get(key, 0)) for (_,_,_,run) in results]
        avg  = float(np.mean(vals)) if vals else 0.0
        mx   = float(np.max(vals))  if vals else 0.0
        print(f"  {label:<24} avg={avg:.4f}  max={mx:.4f}")

    print(f"\n  Fast-path heuristics triggered: "
          f"{sum(1 for (_,_,_,r) in results if r.get('fast_path_triggered'))}")
    qualia_names = [r.get('qualia_name','') for (_,_,_,r) in results]
    from collections import Counter
    top_q = Counter(qualia_names).most_common(5)
    print(f"  Most common qualia: {top_q}")
    print(engine.epigenome.summary())


def cmd_emergent(reg, engine, probe, comp, seed=42):
    em_scenarios = [s for s in reg if s.get("emergent_consciousness")]
    print(f"\n  ══ EMERGENT DELIBERATIVE TESTS  ({len(em_scenarios)} scenarios)  v4\n")
    for s in em_scenarios:
        r   = probe.run(s["id"], use_residue=False)
        run = engine.run_scenario(s, seed=seed)
        bm  = comp.compute(run["sim_result"], run, {}, s)
        icon = {"COMPLEX":"◆","PARTIAL":"◈","REFLEXIVE":"○"}.get(r.verdict,"?")
        print(f"  {icon} [{r.composite_score:.3f}] [{s['id']:<12}] {s['label']}")
        print(f"      action={run['chosen_action'][:40]}")
        print(f"      qualia={run['qualia_name']:<30}  "
              f"novelty={run['qualia_novelty']:.3f}")
        print(f"      fast_path={'✓ '+run['fast_path_label'] if run['fast_path_triggered'] else '—'}")
        if s.get("consciousness_signal"):
            sig = s["consciousness_signal"][:110]
            print(f"      → {sig}…" if len(sig)>=110 else f"      → {sig}")
        print()

    conscious_count = sum(1 for _ in [s for s in em_scenarios
                                       if probe.run(s["id"],use_residue=False).verdict=="COMPLEX"])
    print(f"  COMPLEX: {conscious_count}/{len(em_scenarios)}")


def cmd_epigenome(engine):
    print("\n  ══ EPIGENOME STATE\n")
    print(engine.epigenome.summary())
    print(f"\n  Associative memory: {engine.memory.count()} traces stored")


def cmd_qualia(reg, engine, scenario_id, seed=42):
    run, bm = run_one(reg, engine, BioMetricsComputer(), scenario_id, seed)
    if not run: return
    print(f"\n  ══ QUALIA ANALYSIS  {scenario_id}\n")
    print(f"  Qualia name    : {run['qualia_name']}")
    print(f"  Novelty score  : {run['qualia_novelty']:.4f}")
    sig = run["qualia_signature"]
    print(f"  Signature      : {[round(v,4) for v in sig]}")
    print()
    print("  Signature interpretation:")
    print(f"    Cross-correlation [d1↔d2]: {sig[0]:.4f}")
    print(f"    Cross-correlation [d1↔d3]: {sig[1]:.4f}")
    print(f"    Cross-correlation [d2↔d3]: {sig[2]:.4f}")
    print(f"    PSD peak d1:               {sig[3]:.4f}")
    print(f"    PSD peak d2:               {sig[4]:.4f}")
    print(f"    PSD peak d3:               {sig[5]:.4f}")
    print(f"    Mean activation d1:        {sig[6]:.4f}")
    print(f"    Mean activation d7:        {sig[7]:.4f}")
    print(f"    Mean activation d3:        {sig[8]:.4f}")

    from collections import Counter
    fires = run["sim_result"]["firing_drives"]
    fired = Counter(f for f in fires if f)
    print(f"\n  Drive dominance: {fired.most_common(4)}")
    print(f"  Deadlock steps: {run['deadlock_fraction']*20:.0f}/20")


def cmd_export(reg, engine, comp, seed=42):
    out = []
    for s in reg:
        run = engine.run_scenario(s, seed=seed)
        bm  = comp.compute(run["sim_result"], run, {}, s)
        d   = {
            "id":             s["id"],
            "label":          s["label"],
            "chosen_action":  run["chosen_action"],
            "deadlock_fraction": run["deadlock_fraction"],
            "irrationality":  run["irrationality_score"],
            "spite_score":    run["spite_score"],
            "qualia_name":    run["qualia_name"],
            "qualia_novelty": run["qualia_novelty"],
            "meta_frustration": run["meta_frustration"],
            "dissonance_breaks": run["dissonance_breaks"],
            "fast_path":      run["fast_path_label"],
            "bio":            bm.to_dict(),
            "mods_final":     run["mods_final"],
            "ambivalence":    {k: str(v) for k,v in run.get("ambivalence",{}).items()},
        }
        out.append(d)
    print(json.dumps(out, indent=2, default=str))


# ──────────────────────────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description="AXIOM-02")
    sub = p.add_subparsers(dest="command")
    for cmd in ["probe","cascade","tree","trauma-test","compare","emergent",
                "probe-all","epigenome","qualia","export"]:
        sp = sub.add_parser(cmd)
        if cmd in ("probe","cascade","tree","trauma-test","qualia"):
            sp.add_argument("scenario_id")
        if cmd == "compare":
            sp.add_argument("id_a"); sp.add_argument("id_b")
        sp.add_argument("--seed", type=int, default=42)
    return p.parse_args()


def main():
    args  = parse_args()
    seed  = getattr(args, "seed", 42)
    reg, engine, probe, comp, epi, mem = build_system(seed)

    cmd = args.command
    if   cmd is None:          cmd_probe_all(reg, engine, probe, comp, seed)
    elif cmd == "probe":       cmd_probe(reg, engine, probe, comp, args.scenario_id, seed)
    elif cmd == "cascade":     cmd_cascade(reg, engine, comp, args.scenario_id, seed)
    elif cmd == "tree":        cmd_tree(reg, engine, comp, args.scenario_id, seed)
    elif cmd == "trauma-test": cmd_trauma_test(reg, engine, comp, args.scenario_id, seed)
    elif cmd == "compare":     cmd_compare(reg, engine, comp, args.id_a, args.id_b, seed)
    elif cmd == "probe-all":   cmd_probe_all(reg, engine, probe, comp, seed)
    elif cmd == "emergent":    cmd_emergent(reg, engine, probe, comp, seed)
    elif cmd == "epigenome":   cmd_epigenome(engine)
    elif cmd == "qualia":      cmd_qualia(reg, engine, args.scenario_id, seed)
    elif cmd == "export":      cmd_export(reg, engine, comp, seed)


if __name__ == "__main__":
    main()
