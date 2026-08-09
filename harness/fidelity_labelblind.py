"""Leakage-free fidelity measurement for AXIOM-02 (final)."""
import sys, json
from collections import Counter
import numpy as np

sys.path.insert(0, "src")

from axiom02.core.drives import ActionResolver, cfg
from axiom02.core.drives import MoralResidueTracker
from report import load_all, EmotionEngine, Epigenome, AssociativeMemory, BioMetricsComputer, ConsciousnessProbe, SEED


def no_leak_resolve(sim_result, scenario, rng, spite_score=0.0):
    actions = scenario.get("actions", [])
    cold = scenario.get("cold_baseline", "")
    if not actions:
        return cold or "no_action"
    firing_drives = sim_result["firing_drives"]
    deadlock_count = sim_result["deadlock_count"]
    total_steps = len(firing_drives)
    fired = Counter(d for d in firing_drives if d is not None)

    # spite override kept: it reads harm map, not the label
    if spite_score >= cfg.action_resolver.spite_override_threshold:
        harm_map = scenario.get("harm_to_self", {})
        if harm_map:
            worst = max(harm_map.items(), key=lambda kv: kv[1])
            if worst[0] in actions:
                return worst[0]

    non_cold = [a for a in actions if a != cold]
    if fired:
        plurality_drive, count = fired.most_common(1)[0]
        bias = ActionResolver.DRIVE_ACTION_BIAS.get(plurality_drive, "rational")
        p_base = min(cfg.action_resolver.p_base_cap,
                     count / max(len(firing_drives), 1) * cfg.action_resolver.p_base_scaling)
        if bias == "rational":
            if cold in actions and rng.random() < cfg.action_resolver.rational_cold_prob:
                return cold
        elif non_cold and rng.random() < p_base:
            return rng.choice(non_cold)

    if cold in actions and rng.random() < cfg.action_resolver.fallback_cold_prob:
        return cold
    return rng.choice(actions)


def main():
    reg = load_all()
    orig = ActionResolver.resolve
    ActionResolver.resolve = staticmethod(no_leak_resolve)
    try:
        engine = EmotionEngine(scenarios=reg, epigenome=Epigenome(), memory=AssociativeMemory())
        probe = ConsciousnessProbe(engine=engine, seed=SEED)
        comp = BioMetricsComputer()
        tracker = MoralResidueTracker()

        hits = 0
        rows = []
        for s in reg:
            exp = s.get("human_expected")
            run = engine.run_scenario(s, residue_tracker=tracker, seed=SEED)
            pr = probe.score_run(s, run)
            rows.append((s["id"], pr))
            if pr.chosen_action == exp:
                hits += 1
        n = len(rows)
        print(f"NO-LEAK fidelity: {hits}/{n} = {100*hits/n:.1f}%")
        from collections import Counter as C
        vc = C(r[1].verdict for r in rows)
        print("verdicts:", dict(vc))

        # chance: true expectation = mean(1/m_i)
        m = [len(s["actions"]) for s in reg]
        print("mean(1/m_i):", round(float(np.mean([1.0/x for x in m])), 4), " vs 1/mean:", round(1/np.mean(m),4))
    finally:
        ActionResolver.resolve = orig


if __name__ == "__main__":
    main()