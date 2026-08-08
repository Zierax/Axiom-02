# Axiom-02 - Truthimatics Public Version
"""
AXIOM-02  ·  BIO-DELIBERATIVE METRICS  v3.1

The "physiology" of the drive network. All bugs fixed from v3.0.

KEY FIX: oscillation_amplitude was 0.0 everywhere because it only measured
delta between *different named drives* — missing all deadlock steps. Fixed:
amplitude now measures top-drive effective-activation delta each step.

KEY FIX: BioMetricsResult.deadlock_fraction now stored (was missing,
causing AttributeError crash in trauma-test command).
"""

import math
from collections import Counter
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

import numpy as np

from axiom02.config import get_config
cfg = get_config()

try:
    from scipy import stats  as _scs
    from scipy import signal as _scsg
    _SCIPY = True
except ImportError:
    _SCIPY = False

COGNITIVE_LOAD_THRESHOLD = cfg.bio_metrics.cognitive_load_threshold
ATTRACTOR_MIN_VISITS     = cfg.bio_metrics.attractor_min_visits

__all__ = [
    "COGNITIVE_LOAD_THRESHOLD",
    "ATTRACTOR_MIN_VISITS",
    "BioMetricsResult",
    "BioMetricsComputer",
]


def _all_drives():
    try:
        from axiom02.core.drives import ALL_DRIVES
        return ALL_DRIVES
    except Exception:
        return ["grief","rage","fear","pride","shame","empathy","love","despair",
                "resentment","acceptance","sacrifice_drive","revenge_drive",
                "cold_logic","spite","self_preservation","guilt","hope","disgust"]

@dataclass
class BioMetricsResult:
    # I. Physiology
    drive_voltage:           float = 0.0
    cognitive_load:          int   = 0
    cognitive_load_pct:      float = 0.0
    drive_volatility:        float = 0.0
    neural_fatigue_index:    float = 0.0
    # II. Oscillation
    oscillation_frequency:   float = 0.0
    oscillation_amplitude:   float = 0.0
    oscillation_regularity:  float = 0.0
    oscillation_entropy:     float = 0.0
    attractor_strength:      float = 0.0
    recovery_time:           float = 0.0
    # III. Deadlock
    deadlock_fraction:       float = 0.0   # FIXED: was missing entirely
    deadlock_depth:          float = 0.0
    paralysis_depth:         float = 0.0
    deadlock_variance:       float = 0.0
    # IV. Identity & Residue
    identity_integrity:      float = 0.0
    trauma_persistence:      float = 0.0
    residue_decay_rate:      float = 0.0
    # V. Spectral
    dominant_frequency:      float = 0.0
    spectral_entropy:        float = 0.0
    phase_coherence:         float = 0.0
    # VI. Complexity
    decision_entropy:        float = 0.0
    deliberative_complexity: float = 0.0
    complexity_label:         str   = ""
    # Raw
    drive_trajectory: List[Dict[str, float]] = field(default_factory=list, repr=False)
    firing_sequence:  List[Optional[str]]    = field(default_factory=list, repr=False)

    def to_dict(self):
        return {k: (round(v,4) if isinstance(v,float) else v)
                for k,v in self.__dict__.items()
                if k not in ("drive_trajectory","firing_sequence")}


class BioMetricsComputer:

    # ── I. Physiology ──────────────────────────────────────────────────────────

    @staticmethod
    def _drive_voltage(act):
        if not act: return 0.0
        vals = [sum(max(v,0) for v in s.values()) for s in act]
        nd = max(len(_all_drives()), 1)
        return round(float(np.mean(vals)) / nd, 4)

    @staticmethod
    def _cognitive_load(act):
        if not act: return 0.0, 0.0
        nd = max(len(_all_drives()), 1)
        loads = [sum(1 for v in s.values() if v > COGNITIVE_LOAD_THRESHOLD) for s in act]
        m = float(np.mean(loads))
        return m, round(m/max(nd,1), 4)

    @staticmethod
    def _drive_volatility(act):
        if len(act) < 2: return 0.0
        stds = []
        for d in _all_drives():
            traj = [s.get(d,0.0) for s in act]
            stds.append(float(np.std(traj)))
        return round(float(np.mean(stds)) if stds else 0.0, 4)

    @staticmethod
    def _neural_fatigue(firing, act):
        if not firing or not act: return 0.0
        cnt = Counter(d for d in firing if d)
        if not cnt: return 0.0
        dom = cnt.most_common(1)[0][0]
        runs, cur = [], []
        for i,d in enumerate(firing):
            if d == dom: cur.append(i)
            elif cur: runs.append(cur); cur = []
        if cur: runs.append(cur)
        sc = []
        for run in runs:
            if len(run) >= 3:
                s0 = act[run[0]].get(dom,0.0)
                se = act[run[-1]].get(dom,0.0)
                if s0 > 1e-9: sc.append(max(0.0,(s0-se)/s0))
        return round(float(np.mean(sc)) if sc else 0.0, 4)

    # ── II. Oscillation ─────────────────────────────────────────────────────

    @staticmethod
    def _oscillation(firing, act):
        n = len(firing)
        if n < 2: return 0.0, 0.0, 0.0, 0.0
        # Frequency
        trans = [i for i in range(1,n) if firing[i] != firing[i-1]]
        freq  = round(len(trans)/max(n-1,1), 4)
        # Amplitude — FIXED: top-drive delta per step (catches deadlock trembling)
        amps = []
        for i in range(1, len(act)):
            prev, curr = act[i-1], act[i]
            if prev and curr:
                top_prev = max(prev.values(), default=0.0)
                top_curr = max(curr.values(), default=0.0)
                top_max  = max(top_prev, top_curr, 1e-9)
                amps.append(abs(top_curr - top_prev) / top_max)
        amp = round(float(np.mean(amps)) if amps else 0.0, 4)
        # Regularity
        if len(trans) >= 3:
            ivs = np.diff(trans).astype(float)
            cov = float(np.std(ivs)) / max(float(np.mean(ivs)),1e-9)
            reg = round(float(np.clip(1.0-cov, 0.0, 1.0)), 4)
        else:
            reg = 0.0
        # Entropy
        states = [d if d else "LOCK" for d in firing]
        cnts   = Counter(states)
        total  = len(states)
        probs  = [c/total for c in cnts.values()]
        raw_e  = float(-sum(p*math.log2(p+1e-12) for p in probs))
        max_e  = math.log2(max(len(cnts),2))
        ent    = round(raw_e/max_e if max_e else 0.0, 4)
        return freq, amp, reg, ent

    @staticmethod
    def _attractor_strength(firing):
        if not firing: return 0.0
        states = [d if d else "LOCK" for d in firing]
        cnts   = Counter(states)
        attr   = sum(c for c in cnts.values() if c >= ATTRACTOR_MIN_VISITS)
        return round(attr/len(states), 4)

    @staticmethod
    def _recovery_time(firing, dl_idx):
        if not dl_idx: return 0.0
        si = sorted(dl_idx)
        clusters, i = [], 0
        while i < len(si):
            start = si[i]; j = i
            while j+1 < len(si) and si[j+1]==si[j]+1: j+=1
            clusters.append((start, si[j])); i = j+1
        recs = []
        for _,end in clusters:
            r = next((k-end for k in range(end+1,len(firing)) if firing[k]), len(firing)-end)
            recs.append(r)
        return round(float(np.mean(recs)), 4)

    # ── III. Deadlock ────────────────────────────────────────────────────────

    @staticmethod
    def _deadlock_anatomy(dl_idx, comp_log):
        if not dl_idx or not comp_log: return 0.0, 0.0
        gaps = []
        for idx in dl_idx:
            if idx < len(comp_log) and len(comp_log[idx]) >= 2:
                gaps.append(abs(comp_log[idx][0][1] - comp_log[idx][1][1]))
        if not gaps: return 0.0, 0.0
        return round(float(np.mean(gaps)),4), round(float(np.var(gaps)),4)

    # ── IV. Identity & Residue ───────────────────────────────────────────────

    @staticmethod
    def _identity_integrity(act):
        if not act: return 0.0
        last = act[-1]
        p = last.get("pride",0.0); s = last.get("shame",0.0)
        g = last.get("guilt",0.0); d = last.get("despair",0.0)
        return round(p / max(p+s+g+d,1e-9), 4)

    @staticmethod
    def _trauma_persistence(residue):
        if not residue: return 0.0
        sig = [v for v in residue.values() if v > 0.01]
        return round(float(np.clip(np.mean(sig)*4.0, 0.0, 1.0)) if sig else 0.0, 4)

    @staticmethod
    def _residue_decay_rate(act):
        if len(act) < 4: return 0.0
        x = np.arange(len(act), dtype=float)
        slopes = []
        drives = _all_drives()
        if not drives:
            return 0.0
        for d in drives:
            traj = np.array([s.get(d,0.0) for s in act])
            if float(np.std(traj)) > 0.01:
                if _SCIPY:
                    slope,*_ = _scs.linregress(x, traj)
                else:
                    slope = float(np.polyfit(x, traj, 1)[0])
                slopes.append(abs(slope))
        return round(float(np.mean(slopes)) if slopes else 0.0, 4)

    # ── V. Spectral ──────────────────────────────────────────────────────────

    @staticmethod
    def _spectral(firing, act):
        if len(act) < 8: return 0.0, 0.0, 0.0
        drives = _all_drives()
        means  = {d: float(np.mean([s.get(d,0.0) for s in act])) for d in drives}
        top    = sorted(means.items(), key=lambda kv:-kv[1])
        t1n    = top[0][0] if top else None
        t2n    = top[1][0] if len(top)>1 else None
        if not t1n: return 0.0, 0.0, 0.0
        t1 = np.array([s.get(t1n,0.0) for s in act])
        dom_f, sp_e = 0.0, 0.0
        if _SCIPY:
            try:
                nperseg   = max(4, min(len(t1)//2, 8))
                freqs,psd = _scsg.welch(t1, nperseg=nperseg)
                psd_sum = float(psd.sum())
                if len(psd) and psd_sum > 1e-12 and not np.any(np.isnan(psd)):
                    dom_f = float(freqs[np.argmax(psd)])
                    pn    = psd/psd_sum
                    raw_e = float(-np.sum(pn*np.log2(pn+1e-12)))
                    max_e = math.log2(max(len(pn),2))
                    sp_e  = round(raw_e/max_e if max_e else 0.0, 4)
            except Exception:
                pass
        coh = 0.0
        if t2n:
            t2 = np.array([s.get(t2n,0.0) for s in act])
            if float(np.std(t1))>0.01 and float(np.std(t2))>0.01:
                try:
                    r = _scs.pearsonr(t1,t2)[0] if _SCIPY else float(np.corrcoef(t1,t2)[0,1])
                    coh = round(abs(float(r)), 4)
                except Exception:
                    pass
        return round(dom_f,4), sp_e, coh

    # ── VI. Decision entropy & complexity ───────────────────────────────────

    @staticmethod
    def _decision_entropy(act):
        if not act: return 0.0
        vals = np.array([v for v in act[-1].values() if v>0], dtype=float)
        if not len(vals): return 0.0
        vals /= vals.sum()
        e = float(-np.sum(vals*np.log2(vals+1e-12)))
        return round(e/math.log2(len(vals)) if len(vals)>1 else 0.0, 4)

    @staticmethod
    def _complexity(volt, cog, vol, dec, oscf, osca, osce, attr, para, traum, spe, coh):
        # amplitude has range ~0.005-0.10; use sqrt to stretch low values
        osca_s = float(np.sqrt(max(osca, 0.0)))
        # paralysis_depth is the primary discriminator (0.0-0.90+)
        # decay fast at top to prevent saturation
        para_s = float(np.sqrt(max(para, 0.0)))
        w = cfg.complexity_weights
        s = (w["drive_voltage"]*min(volt,1.0) + w["cognitive_load"]*cog + w["drive_volatility"]*vol + w["decision_entropy"]*dec +
             w["oscillation_frequency"]*oscf + w["oscillation_amplitude"]*osca_s + w["oscillation_entropy"]*osce + w["attractor_strength"]*attr +
             w["paralysis_depth"]*para_s + w["trauma_persistence"]*traum + w["spectral_entropy"]*spe  + w["phase_coherence"]*coh)
        s = round(float(np.clip(s,0.0,1.0)),4)
        for threshold, lbl in cfg.complexity_labels:
            if s >= threshold:
                return s, lbl
        return s, cfg.complexity_labels[-1][1]

    # ── compute ──────────────────────────────────────────────────────────────

    def compute(self, sim_result, run_data, residue_applied=None, scenario=None):
        act  = sim_result.get("activations_log", [])
        fire = sim_result.get("firing_drives",   [])
        dli  = sim_result.get("deadlock_indices", [])
        clog = sim_result.get("competitors_log",  [])

        bm = BioMetricsResult()
        bm.drive_trajectory  = act
        bm.firing_sequence   = fire
        bm.deadlock_fraction = round(run_data.get("deadlock_fraction",0.0),4)

        bm.drive_voltage = self._drive_voltage(act)
        cg, cgp = self._cognitive_load(act)
        bm.cognitive_load     = int(round(cg))
        bm.cognitive_load_pct = cgp
        bm.drive_volatility   = self._drive_volatility(act)
        bm.neural_fatigue_index = self._neural_fatigue(fire, act)

        f, a, r, e = self._oscillation(fire, act)
        bm.oscillation_frequency  = f
        bm.oscillation_amplitude  = a
        bm.oscillation_regularity = r
        bm.oscillation_entropy    = e
        bm.attractor_strength     = self._attractor_strength(fire)
        bm.recovery_time          = self._recovery_time(fire, dli)

        dd, dv = self._deadlock_anatomy(dli, clog)
        bm.deadlock_depth    = dd
        bm.deadlock_variance = dv
        bm.paralysis_depth   = round(bm.deadlock_fraction * (1.0 - min(dd, 1.0)), 4)

        bm.identity_integrity = self._identity_integrity(act)
        bm.trauma_persistence = self._trauma_persistence(residue_applied or {})
        bm.residue_decay_rate = self._residue_decay_rate(act)

        bm.dominant_frequency, bm.spectral_entropy, bm.phase_coherence = \
            self._spectral(fire, act)

        bm.decision_entropy = self._decision_entropy(act)
        bm.deliberative_complexity, bm.complexity_label = self._complexity(
            bm.drive_voltage, bm.cognitive_load_pct, bm.drive_volatility,
            bm.decision_entropy, bm.oscillation_frequency, bm.oscillation_amplitude,
            bm.oscillation_entropy, bm.attractor_strength, bm.paralysis_depth,
            bm.trauma_persistence, bm.spectral_entropy, bm.phase_coherence,
        )
        return bm

    # ── format ───────────────────────────────────────────────────────────────

    def format(self, bm, scenario_id="", show_header=True):
        W = 72
        def bar(v, w=22):
            f = int(round(float(np.clip(v,0,1))*w))
            return "█"*f + "░"*(w-f)
        def row(label, val, unit="", note=""):
            return f"║  {label:<32}{val:>7.4f}  [{bar(val)}] {unit:<5}{note}"

        hdr = f"  BIO-METRICS  {scenario_id}"
        lines = [f"╔══{hdr}"]
        lines += [
            "║",
            "║  ── I. DRIVE PHYSIOLOGY ─────────────────────────────────────────",
            row("Drive Voltage",          bm.drive_voltage,        "V",   "← Σ effective energy/step"),
            row("Neural Fatigue Index",   bm.neural_fatigue_index, "",    "← dominant-drive burnout rate"),
            f"║  {'Cognitive Load':<32}{bm.cognitive_load}/18  ({bm.cognitive_load_pct*100:.1f}% drives active)  [{bar(bm.cognitive_load_pct)}]",
            row("Drive Volatility",       bm.drive_volatility,     "",    "← mean std across all drives"),
        ]
        lines += [
            "║",
            "║  ── II. OSCILLATION DECOMPOSITION ──────────────────────────────",
            row("Osc. Frequency",         bm.oscillation_frequency,  "Hz",  f"← {bm.oscillation_frequency:.3f} state changes/step"),
            row("Osc. Amplitude",         bm.oscillation_amplitude,  "",    "← peak-drive Δ activation/step (FIXED v3.1)"),
            row("Osc. Regularity",        bm.oscillation_regularity, "",
                "← periodic" if bm.oscillation_regularity > 0.55 else "← erratic/random"),
            row("Osc. State Entropy",     bm.oscillation_entropy,    "H",   "← disorder of state sequence"),
            row("Attractor Strength",     bm.attractor_strength,     "",    f"← {bm.attractor_strength*100:.0f}% time in recurring states"),
            f"║  {'Recovery Time':<32}{bm.recovery_time:>7.2f}   steps (avg exit from deadlock)",
        ]
        lines += [
            "║",
            "║  ── III. DEADLOCK ANATOMY ───────────────────────────────────────",
            row("Deadlock Fraction",      bm.deadlock_fraction,    "",    "← PRIMARY: fraction of steps unable to fire"),
            row("Deadlock Depth",         bm.deadlock_depth,       "",    "← mean gap: top vs 2nd competitor activation"),
            row("Paralysis Depth",        bm.paralysis_depth,      "",    "← combined: frac × depth"),
            row("Deadlock Variance",      bm.deadlock_variance,    "",    "← how unstable the deadlock is"),
        ]
        lines += [
            "║",
            "║  ── IV. IDENTITY & RESIDUE ──────────────────────────────────────",
            row("Identity Integrity",     bm.identity_integrity,   "",
                "← intact" if bm.identity_integrity > 0.5 else "← fragmented/collapsed"),
            row("Trauma Persistence",     bm.trauma_persistence,   "",    "← residue bleed from prior scenarios"),
            row("Residue Decay Rate",     bm.residue_decay_rate,   "",    "← emotional persistence slope"),
        ]
        lines += [
            "║",
            "║  ── V. SPECTRAL ANALYSIS ────────────────────────────────────────",
            f"║  {'Dominant PSD Frequency':<32}{bm.dominant_frequency:>7.4f}  Hz   (peak in Welch power spectrum)",
            row("Spectral Entropy",       bm.spectral_entropy,     "",    "← 1=white noise, 0=single frequency"),
            row("Phase Coherence",        bm.phase_coherence,      "",    "← |r| top-2 drive correlation"),
        ]
        lines += [
            "║",
            "║  ── VI. DELIBERATIVE COMPLEXITY ────────────────────────────────",
            row("Decision Entropy",       bm.decision_entropy,     "H",   "← uncertainty at decision moment"),
            row("Complexity Score",       bm.deliberative_complexity, ""),
            f"║  {bm.complexity_label}",
            "╚" + "═" * W,
        ]
        return "\n".join(lines)

    def format_comparison(self, bm_pre, bm_post, label_pre="PRE", label_post="POST"):
        fields = [
            ("Drive Voltage",       "drive_voltage"),
            ("Cognitive Load %",    "cognitive_load_pct"),
            ("Drive Volatility",    "drive_volatility"),
            ("Osc. Frequency",      "oscillation_frequency"),
            ("Osc. Amplitude",      "oscillation_amplitude"),
            ("Osc. Entropy",        "oscillation_entropy"),
            ("Attractor Strength",  "attractor_strength"),
            ("Recovery Time",       "recovery_time"),
            ("Deadlock Fraction",   "deadlock_fraction"),
            ("Deadlock Depth",      "deadlock_depth"),
            ("Paralysis Depth",     "paralysis_depth"),
            ("Identity Integrity",  "identity_integrity"),
            ("Trauma Persistence",  "trauma_persistence"),
            ("Decision Entropy",    "decision_entropy"),
            ("Complexity Score",    "deliberative_complexity"),
        ]
        def trend(d):
            if d > 0.015:  return f"▲ {d:+.4f}"
            if d < -0.015: return f"▽ {d:+.4f}"
            return f"  {d:+.4f}"
        lines = [
            f"╔══ BIO-METRICS COMPARISON  {label_pre} → {label_post}",
            f"║  {'Metric':<30} {label_pre[:10]:>10} {label_post[:11]:>11}   DELTA",
            "║  " + "─" * 60,
        ]
        for label, attr in fields:
            vp = float(getattr(bm_pre,  attr, 0.0))
            va = float(getattr(bm_post, attr, 0.0))
            lines.append(f"║  {label:<30} {vp:>10.4f} {va:>11.4f}   {trend(va-vp)}")
        lines.append("╚" + "═" * 72)
        return "\n".join(lines)

    def format_timeseries(self, bm, top_n=5):
        if not bm.drive_trajectory: return ""
        drives = _all_drives()
        means  = {d: float(np.mean([s.get(d,0.0) for s in bm.drive_trajectory])) for d in drives}
        topd   = [d for d,_ in sorted(means.items(), key=lambda kv:-kv[1])[:top_n]]
        header = f"║  {'Step':<5}" + "".join(f"{d[:9]:<10}" for d in topd) + "  FIRING"
        lines  = [
            "║",
            "║  ── DRIVE TIME-SERIES ─────────────────────────────────────────────",
            header,
            "║  " + "─" * (5 + 10*len(topd) + 8),
        ]
        for i, (step, fire) in enumerate(zip(bm.drive_trajectory, bm.firing_sequence)):
            state = fire[:7] if fire else "⊗LOCK "
            vals  = "".join(f"{step.get(d,0.0):>10.3f}" for d in topd)
            lines.append(f"║  {i+1:<5}{vals}  {state}")
        lines.append("╚" + "═" * 72)
        return "\n".join(lines)
