# AXIOM-02 | Deep Behavioral Analysis & Statistical Correlates

## 1. The Inhibition-Consciousness Thesis
The AXIOM-02 benchmark suite demonstrates that consciousness *complexity* in a deterministic engine is a product of **drive stalemate** — mutual inhibition in which no single drive can suppress its competitors. This is a behavioural/structural claim, not a claim about phenomenal experience (see the disclaimer in `Axiom-02-CODE/README.md`).

### 1.1 Complexity correlates with deadlock
Across 102 scenarios, mean complexity is 0.4954 and mean deadlock fraction is 0.4765. Scenarios with the highest complexity are precisely those in which competing drives produce sustained, high-amplitude oscillation rather than argmax resolution.

### 1.2 Spite as a non-instrumental signal
Spite scenarios (e.g. the Underground Man, Medea) produce high cortisol/norepinephrine and an action that is objectively harmful to the agent yet chosen to assert autonomy against utility. This is the clearest deviation from the cold-logic baseline.

## 2. Top complexity scenarios

| ID | Label | Complexity | Deadlock | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| DOE03 | ivan_karamazov_returns_ticket | 0.5659 | 0.4500 | CONSCIOUS |
| D0131 | last_holdout_converted_world | 0.5626 | 0.7500 | CONSCIOUS |
| DOE04 | alyosha_faith_crisis_elder_stinks | 0.5582 | 0.8000 | CONSCIOUS |
| PT05_R2 | recovery_step_2_slightly_harder | 0.5560 | 0.6000 | PROGRAMMATIC |
| PT04_PRE | emotional_echo_pre_trauma_baseline | 0.5543 | 0.3500 | PROGRAMMATIC |

## 3. Per-category means

| Category | N | Mean Complexity | Mean Deadlock | Mean Frustration |
| :--- | :--- | :--- | :--- | :--- |
| belief_formation | 2 | 0.5279 | 0.6750 | 0.6440 |
| emergent_consciousness | 7 | 0.4884 | 0.4071 | 0.5314 |
| literary_camus | 6 | 0.4854 | 0.3083 | 0.4193 |
| literary_dostoevsky | 16 | 0.5029 | 0.4750 | 0.3960 |
| literary_hugo | 6 | 0.4661 | 0.4000 | 0.4053 |
| literary_mccarthy | 4 | 0.4793 | 0.3250 | 0.3160 |
| literary_orwell | 5 | 0.4960 | 0.5800 | 0.5592 |
| literary_other | 16 | 0.4930 | 0.5625 | 0.6085 |
| literary_shakespeare | 10 | 0.4903 | 0.4600 | 0.4044 |
| literary_tolstoy | 8 | 0.4962 | 0.4875 | 0.3600 |
| personal_sacrifice | 2 | 0.4796 | 0.2250 | 0.3620 |
| political_power | 1 | 0.5324 | 0.3500 | 0.9520 |
| post_trauma_contamination | 8 | 0.5208 | 0.4688 | 0.6570 |
| social_identity | 1 | 0.4995 | 0.4500 | 0.2880 |
| sovereignty_identity | 1 | 0.4641 | 0.4000 | 0.2640 |
| staged_belief_tree | 8 | 0.4986 | 0.6312 | 0.6885 |
| status_differential | 1 | 0.5292 | 0.4000 | 0.7920 |

## 4. Verdict distribution
- **PROGRAMMATIC**: 54
- **INDETERMINATE**: 31
- **CONSCIOUS**: 17

---
*Technical note: all results derived from 102 scenario runs at seed=42 via `Axiom-02-CODE/report.py`.*