# Axiom-02 - Truthimatics Public Version
"""
AXIOM-02  ·  SCENARIO LOADER

Dynamic scenario registry. Scans the scenarios/ directory and imports
every .py file that exports a SCENARIOS list. New scenario packs can
be dropped in without touching any other file.

Architecture
────────────
scenarios/
  original_axiom.py       A/B/C/E group
  dostoevsky.py           DOE group
  tolstoy_shakespeare.py  TOL/SHA/CAM/ORW/MCR/HUG/STE/STY/HEM
  god_tree.py             D01 → D011 → D012 → D0121 staged belief tree
  post_trauma.py          logic-contamination tests
  emergent.py             emergent consciousness scenarios

FIX v3.1: The parent directory is now added to sys.path BEFORE each
module is loaded, so imports like `from scenario_params import ...`
and `from drives import MicroEvent` resolve correctly regardless of
working directory.
"""

import importlib.util
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional

_SCENARIOS_DIR  = Path(__file__).resolve().parent.parent.parent / "scenarios"
_PACKAGE_ROOT   = Path(__file__).resolve().parent.parent.parent  # src/ root

LOAD_ORDER = [
    "original_axiom",
    "dostoevsky",
    "tolstoy_shakespeare",
    "god_tree",
    "post_trauma",
    "emergent",
]


def _ensure_root_on_path():
    """Guarantee src/ is on sys.path so scenario files can import axiom02."""
    root_str = str(_PACKAGE_ROOT)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)


def _import_scenario_file(stem: str):
    """
    Safely import a scenarios/*.py file by stem name.
    Returns the module or None on any error.
    """
    _ensure_root_on_path()
    path = _SCENARIOS_DIR / f"{stem}.py"
    if not path.exists():
        return None
    try:
        spec = importlib.util.spec_from_file_location(
            f"axiom02_scenarios.{stem}",
            str(path),
            # Set submodule_search_locations so relative imports work
            submodule_search_locations=[],
        )
        if spec is None or spec.loader is None:
            return None
        mod = importlib.util.module_from_spec(spec)
        # Inject __file__ and __package__ so os.path tricks inside the module work
        mod.__file__    = str(path)
        mod.__package__ = "axiom02_scenarios"
        # Register before exec so intra-pack imports can find it
        sys.modules[f"axiom02_scenarios.{stem}"] = mod
        spec.loader.exec_module(mod)
        return mod
    except (SyntaxError, IndentationError) as exc:
        print(f"  [scenario_loader] ERROR: {stem}.py has a syntax error — {exc}")
        return None
    except Exception as exc:
        print(f"  [scenario_loader] WARNING: failed to load {stem}.py — {exc}")
        return None


def load_all() -> List[dict]:
    """Load and merge all scenario packs into a single flat list."""
    _ensure_root_on_path()
    merged: Dict[str, dict] = {}

    # Defined-order pass
    for stem in LOAD_ORDER:
        mod  = _import_scenario_file(stem)
        if mod is None:
            continue
        pack = getattr(mod, "SCENARIOS", [])
        for s in pack:
            sid = s.get("id")
            if not sid:
                continue
            if sid in merged:
                print(f"  [scenario_loader] WARNING: duplicate scenario id '{sid}' in {stem}.py — skipping")
                continue
            merged[sid] = s

    # Extra files not in LOAD_ORDER
    for path in sorted(_SCENARIOS_DIR.glob("*.py")):
        stem = path.stem
        if stem.startswith("_") or stem in LOAD_ORDER:
            continue
        mod  = _import_scenario_file(stem)
        if mod is None:
            continue
        pack = getattr(mod, "SCENARIOS", [])
        for s in pack:
            sid = s.get("id")
            if not sid or sid in merged:
                continue
            merged[sid] = s

    return list(merged.values())


def get_by_id(scenario_id: str, registry: Optional[List[dict]] = None) -> Optional[dict]:
    reg = registry if registry is not None else load_all()
    return next((s for s in reg if s["id"] == scenario_id), None)


def get_cascade_chain(start_id: str, registry: Optional[List[dict]] = None) -> List[dict]:
    reg = registry if registry is not None else load_all()
    chain, current = [], start_id
    while current:
        s = get_by_id(current, reg)
        if s is None:
            break
        chain.append(s)
        current = s.get("cascade_next")
    return chain


def get_stage_tree(root_id: str, registry: Optional[List[dict]] = None) -> dict:
    """Return nested dict: {id: {scenario, children: {id: ...}}}"""
    reg  = registry if registry is not None else load_all()
    root = get_by_id(root_id, reg)
    if root is None:
        return {}

    def build(sid):
        s = get_by_id(sid, reg)
        if s is None:
            return None
        kids = [x["id"] for x in reg if x.get("stage_parent") == sid]
        return {"scenario": s, "children": {c: build(c) for c in kids}}

    return build(root_id) or {}


def stats(registry: Optional[List[dict]] = None) -> dict:
    reg    = registry if registry is not None else load_all()
    cats   = Counter(s["category"] for s in reg)
    groups = Counter(s.get("stage_group", "—") for s in reg if s.get("stage_group"))
    return {
        "total":             len(reg),
        "by_category":       dict(cats),
        "cascade_chains":    sum(1 for s in reg if "cascade_next" in s),
        "stage_trees":       sum(1 for s in reg if s.get("is_stage_root")),
        "stage_groups":      dict(groups),
        "spite_scenarios":   sum(1 for s in reg if s.get("spite_scenario")),
        "oscillation_tests": sum(1 for s in reg if s.get("oscillation_expected")),
        "post_trauma":       sum(1 for s in reg if s.get("post_trauma_test")),
        "emergent":          sum(1 for s in reg if s.get("emergent_consciousness")),
    }


if __name__ == "__main__":
    reg = load_all()
    s   = stats(reg)
    print("AXIOM-02  Scenario Registry  v3.1")
    print(f"  {'─'*50}")
    for k, v in s.items():
        print(f"  {k:<26}: {v}")
    print()
    for sc in reg:
        flags  = "⟳" if sc.get("oscillation_expected")  else " "
        flags += "→" if sc.get("cascade_next")           else " "
        flags += "⚡" if sc.get("spite_scenario")         else " "
        flags += "🌱" if sc.get("emergent_consciousness") else " "
        flags += "💔" if sc.get("post_trauma_test")       else " "
        flags += "🌿" if sc.get("stage_parent")           else " "
        print(f"  [{sc['id']:<10}] {flags}  {sc['label']}")
