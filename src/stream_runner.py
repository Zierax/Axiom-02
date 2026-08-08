# Axiom-02 - Truthimatics Public Version
"""
AXIOM-02  ·  STREAM RUNNER  v1.1  (production-corrected)

CLI entry-point for the Temporal Emotion Loop.

USAGE
─────
  python stream_runner.py stream B01,B02,DOE03,STY01
  python stream_runner.py stream --preset dostoevsky
  python stream_runner.py stream --preset full-day --start-hour 2.0
  python stream_runner.py stream --all
  python stream_runner.py stream --cascade B01
  python stream_runner.py stream B01,B02 --json > out.json
  python stream_runner.py ruminator-probe B02
  python stream_runner.py circadian-plot
  python stream_runner.py stress-test

STREAM PRESETS
──────────────
  dostoevsky    DOE01–DOE06
  shakespeare   SHA01–SHA03
  hugo          HUG01–HUG02
  tolstoy       TOL01–TOL03
  sacrifice     B01–B02
  god-tree      D01–D011–D012–D0121–D01211
  full-day      14 scenarios across a simulated working day
  spite-chain   high-spite scenarios in sequence
  recovery-arc  trauma then de-escalation

v1.1 changes
─────────────
  · circadian-plot depletion demo uses SUSTAINED high stress (fixed cortisol
    scenario_mods = 0.75 every step), not self-referential mods that decay
    themselves below the threshold within one step.
"""

# ── Imports ────────────────────────────────────────────────────────────────────
from __future__ import annotations

import argparse
import importlib
import json
import sys
import os
from typing import Dict, List, Optional

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
# Ensure src/ is on sys.path so `import axiom02` resolves when running
# `python src/stream_runner.py` from the project root.
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from axiom02.core.scenario_loader import load_all, get_cascade_chain
from axiom02.core.engine import EmotionEngine
from axiom02.core.bio_metrics import BioMetricsComputer
from axiom02.core.epigenetics import Epigenome, AssociativeMemory
from axiom02.modulators.temporal_loop import TemporalEmotionLoop, TemporalStepRecord
from axiom02.modulators.circadian import CircadianEngine

# ── Stream presets ─────────────────────────────────────────────────────────────

PRESETS: Dict[str, List[str]] = {
    "dostoevsky":  ["DOE01", "DOE02", "DOE03", "DOE04", "DOE05", "DOE06"],
    "shakespeare": ["SHA01", "SHA02", "SHA03"],
    "hugo":        ["HUG01", "HUG02"],
    "tolstoy":     ["TOL01", "TOL02", "TOL03"],
    "sacrifice":   ["B01",   "B02"],
    "god-tree":    ["D01",   "D011", "D012", "D0121", "D01211"],
    "orwell":      ["ORW01"],
    "full-day": [
        "A01",  "B01",  "B02",  "DOE01", "DOE02",
        "STY01","SHA01","SHA02","MCR01",
        "HUG01","HUG02","DOE03","TOL01", "TOL02",
    ],
    "spite-chain":  ["DOE03", "DOE05", "D012", "D0122", "TOL02"],
    "recovery-arc": ["STY01", "PT01",  "PT05_R1", "PT05_R2", "PT05_R3"],
}


# ──────────────────────────────────────────────────────────────────────────────
# SCENARIO LOADING
# ──────────────────────────────────────────────────────────────────────────────

def _load_fallback() -> List[dict]:
    """Load from root-level pack files when scenarios/ subdir does not exist."""
    merged: Dict[str, dict] = {}
    for name in ["scenario_params","original_axiom","dostoevsky",
                 "tolstoy_shakespeare","god_tree","post_trauma","emergent"]:
        try:
            mod  = importlib.import_module(name)
            for s in getattr(mod, "SCENARIOS", []):
                sid = s.get("id")
                if sid and sid not in merged:
                    merged[sid] = s
        except ImportError:
            pass
    return list(merged.values())


def build_system(verbose: bool = True):
    if verbose:
        print("  [loading scenario registry…]", flush=True)
    reg = load_all()
    if not reg:
        reg = _load_fallback()
        if verbose:
            print("  [using root-level pack files]", flush=True)
    if verbose:
        print(f"  [loaded {len(reg)} scenarios]", flush=True)
        print("  [building AXIOM-02 engine…]", flush=True)
    epi    = Epigenome()
    mem    = AssociativeMemory()
    engine = EmotionEngine(scenarios=reg, epigenome=epi, memory=mem)
    comp   = BioMetricsComputer()
    if verbose:
        print("  [done]\n", flush=True)
    return reg, engine, comp, epi, mem


def resolve_ids(
    id_string: str,
    reg:       List[dict],
    cascade:   str  = "",
    category:  str  = "",
    preset:    str  = "",
    all_flag:  bool = False,
) -> List[str]:
    if all_flag:
        return [s["id"] for s in reg]
    if preset and preset in PRESETS:
        return PRESETS[preset]
    if cascade:
        return [s["id"] for s in get_cascade_chain(cascade, reg)]
    if category:
        return [s["id"] for s in reg if s.get("category") == category]
    if id_string:
        return [x.strip() for x in id_string.split(",") if x.strip()]
    return []


def get_scenarios(ids: List[str], reg: List[dict]) -> List[dict]:
    lookup  = {s["id"]: s for s in reg}
    missing = [i for i in ids if i not in lookup]
    if missing:
        print(f"  WARNING: unknown scenario ids: {missing}", file=sys.stderr)
    return [lookup[i] for i in ids if i in lookup]


# ──────────────────────────────────────────────────────────────────────────────
# COMMANDS
# ──────────────────────────────────────────────────────────────────────────────

def cmd_stream(args, reg, engine, comp) -> None:
    ids = resolve_ids(
        id_string = getattr(args, "scenarios", "") or "",
        reg       = reg,
        cascade   = getattr(args, "cascade",  "") or "",
        category  = getattr(args, "category", "") or "",
        preset    = getattr(args, "preset",   "") or "",
        all_flag  = getattr(args, "all",      False),
    )
    if not ids:
        print("  No scenarios specified.")
        print(f"  Available presets: {', '.join(PRESETS)}")
        return

    scenarios  = get_scenarios(ids, reg)
    start_hour = float(getattr(args, "start_hour", 8.0) or 8.0)
    hps        = float(getattr(args, "hours_per_scenario", 1.0) or 1.0)
    seed       = int(getattr(args, "seed", 42) or 42)
    as_json    = getattr(args, "json", False)

    if not as_json:
        print(f"\n  ══ TEMPORAL EMOTION LOOP  {len(scenarios)} scenarios  "
              f"start_hour={start_hour:.1f}h  hps={hps:.1f}\n")

    loop    = TemporalEmotionLoop(engine=engine, hours_per_scenario=hps,
                                  start_hour=start_hour)
    records = loop.run_stream(scenarios, seed_base=seed, verbose=not as_json)

    if as_json:
        print(loop.export_json(records))
        return

    print()
    print(loop.format_timeline(records))
    print()
    print(loop.format_temporal_bio(records))
    print()
    _print_insights(records)


def cmd_ruminator_probe(args, reg, engine, comp) -> None:
    sid      = args.scenario_id
    lookup   = {s["id"]: s for s in reg}
    scenario = lookup.get(sid)
    if not scenario:
        print(f"  Scenario '{sid}' not found.")
        return

    print(f"\n  ══ RUMINATOR PROBE  {sid}\n")
    loop     = TemporalEmotionLoop(engine=engine)
    records1 = loop.run_stream([scenario], seed_base=42, verbose=True)
    print()
    print(loop._ruminator.format())
    print()
    print("  ── Second pass (ruminator loaded) ─────────────────────────────")
    records2 = loop.run_stream([scenario], seed_base=43, verbose=True)
    print()
    r1, r2 = records1[0], records2[0]
    print(f"  Deadlock  Δ : {r2.deadlock_fraction  - r1.deadlock_fraction:+.4f}")
    print(f"  Irrat.    Δ : {r2.irrationality      - r1.irrationality:+.4f}")
    print(f"  Spite     Δ : {r2.spite_score         - r1.spite_score:+.4f}")
    print(f"  Burden    Δ : {r2.rumination_burden   - r1.rumination_burden:+.4f}")
    print()
    for inj in loop._ruminator.injection_history():
        for d, v in sorted(inj.items(), key=lambda kv: -kv[1]):
            bar = "█" * int(v * 20)
            print(f"    {d:<20} {v:.4f}  [{bar}]")


def cmd_circadian_plot(_args) -> None:
    """
    Print the 24-hour circadian profile and demonstrate the
    cortisol×serotonin depletion mechanism.

    v1.1 FIX: depletion demo now uses SUSTAINED high-cortisol scenario_mods
    (cortisol=0.75 held constant each step) so the propagated cortisol stays
    above CORTISOL_SE_THRESHOLD=0.52 and cort_hours accumulate visibly.
    The previous version passed self-referential mods which decayed below the
    threshold within one step, making the depletion bar always empty.
    """
    circ = CircadianEngine()

    print("\n  ══ 24-HOUR CIRCADIAN PROFILE  v1.1  (Truthimatics Biological Baseline)\n")
    print(f"  Corrections vs v1.0:")
    print(f"    cortisol  : sin²→cos²  (peak now at 08:00, was 20:00)")
    print(f"    serotonin : sin→cos    (peak now at 14:00, was 20:00)")
    print(f"    dopamine  : sin→cos    (peak now at 09:00, was 14:00)")
    print()
    print(f"  {'Hour':<6} {'Phase':<30} {'Cort':>5} {'Nore':>5} "
          f"{'Sero':>5} {'Dopa':>5} {'Oxyt':>5} {'Strain':>7}")
    print("  " + "─" * 74)

    PHASES = [
        (range(0,  6),  "SLEEP-WINDOW  🌙"),
        (range(6,  10), "MORNING-RAMP  ☀"),
        (range(10, 14), "PEAK-ALERT    ⚡"),
        (range(14, 18), "AFTERNOON     ☀"),
        (range(18, 22), "EVENING       🌆"),
    ]

    for h in range(24):
        snap  = circ.snapshot(float(h))
        phase = "NIGHT-WIND    🌙"
        for rng, label in PHASES:
            if h in rng:
                phase = label
                break
        flag = "⚠ " if snap.sleep_window else "  "
        print(
            f"  {h:02d}:00  {phase:<28} "
            f"{snap.cortisol:>5.3f} "
            f"{snap.norepinephrine:>5.3f} "
            f"{snap.serotonin:>5.3f} "
            f"{snap.dopamine:>5.3f} "
            f"{snap.oxytocin:>5.3f} "
            f"{flag}{snap.circadian_strain:>5.3f}"
        )

    # Depletion demo — v1.1 FIX: use sustained stress scenario_mods
    print()
    print("  ── CORTISOL × SEROTONIN DEPLETION  (8h sustained stress) ─────────")
    print("  Sustained scenario: cortisol=0.75 every step (e.g. B02→STY01→SHA01)")
    print(f"  Threshold={0.52}  Kappa={0.060}  starts at H=08")
    print()

    from axiom02.modulators.temporal_loop import ModulatorPropagator, TemporalModulatorState

    # SUSTAINED stress: scenario_mods keeps cortisol high every step
    SUSTAINED_STRESS_MODS = {
        "dopamine": 0.45, "serotonin": 0.38,
        "norepinephrine": 0.58, "cortisol": 0.78, "oxytocin": 0.30,
    }

    mods_state = TemporalModulatorState(
        cortisol=0.78, serotonin=0.50,
        norepinephrine=0.50, dopamine=0.45, oxytocin=0.30
    )
    for h_offset in range(10):
        h    = 8 + h_offset
        snap = circ.snapshot(float(h))
        mods_state = ModulatorPropagator.propagate(
            prior         = mods_state,
            scenario_mods = SUSTAINED_STRESS_MODS,   # held constant
            circadian     = snap,
            rumi_injection= {},
            hours_elapsed = 1.0,
        )
        depl_bar = "█" * int(mods_state.serotonin_depl * 40)
        flag_sev = (
            " ⚠ SEVERE"   if mods_state.serotonin_depl > 0.15 else
            " ⚑ moderate" if mods_state.serotonin_depl > 0.05 else ""
        )
        print(
            f"  H={h:02d}  cort={mods_state.cortisol:.3f}  "
            f"cort_h={mods_state.cortisol_hours:.3f}  "
            f"sero={mods_state.serotonin:.3f}  "
            f"depl=[{depl_bar:<16}] {mods_state.serotonin_depl:.4f}{flag_sev}"
        )
    print()


def cmd_stress_test(args, reg, engine, comp) -> None:
    print("\n  ══ STRESS TEST  ·  Sleep-deprived day from 02:00\n")
    scenarios = get_scenarios(PRESETS["full-day"], reg)
    loop      = TemporalEmotionLoop(engine=engine, hours_per_scenario=1.5,
                                    start_hour=2.0)
    records   = loop.run_stream(scenarios, seed_base=42, verbose=True)
    print()
    print(loop.format_timeline(records))
    print()
    _print_insights(records, "STRESS TEST INSIGHTS")


# ──────────────────────────────────────────────────────────────────────────────
# TEMPORAL INSIGHTS SUMMARY
# ──────────────────────────────────────────────────────────────────────────────

def _print_insights(
    records: List[TemporalStepRecord],
    title:   str = "TEMPORAL INSIGHTS",
) -> None:
    if not records:
        return
    print(f"  ── {title} ──────────────────────────────────────────────────")

    peak_cort = max(records, key=lambda r: r.mods_final.get("cortisol", 0))
    print(f"  Peak cortisol   : step {peak_cort.step} ({peak_cort.scenario_id})"
          f"  → {peak_cort.mods_final.get('cortisol',0):.4f}")

    low_sero  = min(records, key=lambda r: r.mods_final.get("serotonin", 1))
    print(f"  Nadir serotonin : step {low_sero.step} ({low_sero.scenario_id})"
          f"  → {low_sero.mods_final.get('serotonin',0):.4f}")

    peak_brd  = max(records, key=lambda r: r.rumination_burden)
    print(f"  Peak rumination : step {peak_brd.step} ({peak_brd.scenario_id})"
          f"  → {peak_brd.rumination_burden:.4f}")

    peak_depl = max(records, key=lambda r: r.serotonin_depletion)
    if peak_depl.serotonin_depletion > 0.001:
        sev = ("SEVERE" if peak_depl.serotonin_depletion > 0.15 else
               "moderate" if peak_depl.serotonin_depletion > 0.05 else "mild")
        print(f"  Max SE depletion: step {peak_depl.step}"
              f"  → {peak_depl.serotonin_depletion:.4f}  ({sev})")

    low_narr  = min(records, key=lambda r: r.narrative_stability)
    print(f"  Nadir stability : step {low_narr.step} ({low_narr.scenario_id})"
          f"  → {low_narr.narrative_stability:.4f}")

    spite_steps = [r for r in records if r.spite_score >= 0.30]
    if spite_steps:
        print(f"  Spite events    : {len(spite_steps)} → "
              f"{', '.join(r.scenario_id for r in spite_steps)}")

    dl_steps = [r for r in records if r.deadlock_fraction >= 0.70]
    if dl_steps:
        print(f"  Deep deadlock   : {len(dl_steps)} ≥ 0.70 → "
              f"{', '.join(r.scenario_id for r in dl_steps)}")
    print()


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="AXIOM-02  ·  Temporal Emotion Loop  v1.1",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="command")

    sp = sub.add_parser("stream")
    sp.add_argument("scenarios", nargs="?", default="")
    sp.add_argument("--preset",   default="")
    sp.add_argument("--cascade",  default="")
    sp.add_argument("--category", default="")
    sp.add_argument("--all",      action="store_true")
    sp.add_argument("--start-hour",         type=float, default=8.0)
    sp.add_argument("--hours-per-scenario", type=float, default=1.0)
    sp.add_argument("--seed",               type=int,   default=42)
    sp.add_argument("--json",               action="store_true")

    sp2 = sub.add_parser("ruminator-probe")
    sp2.add_argument("scenario_id")

    sub.add_parser("circadian-plot")
    sub.add_parser("stress-test")

    return p.parse_args()


def main() -> None:
    args = parse_args()

    if args.command == "circadian-plot":
        cmd_circadian_plot(args)
        return

    reg, engine, comp, epi, mem = build_system()

    if   args.command == "stream":
        cmd_stream(args, reg, engine, comp)
    elif args.command == "ruminator-probe":
        cmd_ruminator_probe(args, reg, engine, comp)
    elif args.command == "stress-test":
        cmd_stress_test(args, reg, engine, comp)
    else:
        print("  No command given. Use --help.\n")
        print("  Quick start:")
        print("    python stream_runner.py stream --preset dostoevsky")
        print("    python stream_runner.py circadian-plot")
        print("    python stream_runner.py ruminator-probe B02")
        print("    python stream_runner.py stress-test")
        print(f"\n  Presets: {', '.join(PRESETS)}")


if __name__ == "__main__":
    main()