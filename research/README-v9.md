# Current research and reproduction guide

Start with [When a Local Pricing Guard Is Not a Welfare Promise](../output/pdf/local-guard-welfare-report.pdf). It connects the guarantee-capacity result, recurring use of a fixed physical cap, calibration sensitivity, private incentives and the latest adaptive learner study. The [local viewer](http://127.0.0.1:3003/) provides one entry point after starting `node research/demo-server.js` from the project root.

## Explore the result

| View | What it shows |
|---|---|
| [Protection game](http://127.0.0.1:3003/recurring) | Coordinate both shops, execute real cap/guard rounds and inspect the separate customer-benefit ledger. |
| [Profit challenge](http://127.0.0.1:3003/profit-challenge) | Choose one shop's prices against a transparent fixed public opponent; compare exact profit after a complete block. Optional hints are stored actions. |
| [Adaptive evidence](http://127.0.0.1:3003/adaptive) | Inspect saved frozen-policy executions, actual training-window means, visit support, both profits/prices and four paired seed comparisons. No browser training occurs. |
| [Calibration assumptions](http://127.0.0.1:3003/uncertainty) | Compare four declared quality-error bounds while keeping enforcement and absolute targets fixed. |
| [Price precision](http://127.0.0.1:3003/refinement) | Distinguish a finite-grid promise from the separately validated continuous result. |

The user's preexisting game and market scaffold and the published sprint starter are prior work. Current sprint contributions are the explicitly source-frozen analyses, controller demonstrations, reproducible numerical evidence and prospectively specified learner follow-up. Established Q-learning, shielding, dynamic programming and numerical verification methods are not claimed as new algorithms.

## Current learner evidence

Read [ADAPTIVE_LEARNING_RESULTS.md](ADAPTIVE_LEARNING_RESULTS.md), the [protocol](ADAPTIVE_LEARNING_PROTOCOL.md), [prospective analysis contract](ADAPTIVE_ANALYSIS_CONTRACT.md), and [independent review](ADAPTIVE_LEARNING_REVIEW.md). The [manifest](adaptive-learning-results/manifest.json), [passed independent receipt](adaptive-learning-results/independent-audit.json) and [complete descriptive summary](adaptive-learning-results/summary.json) retain all 192 runs and 384 checkpoints. The [pre-outcome independent-auditor snapshot](adaptive-learning-audit-provenance/before-outcome.py) is preserved separately.

The two masks share one economic calibration. Four primary comparisons retain twelve paired whole-market seeds in each mask/initialization stratum. The endpoint is final saved-history/clock frozen-greedy eventual-cycle customer benefit. Startup-only receives no new cap. Fresh-cap replays, 1M checkpoints, last-100k exploratory training means and all-state policy graphs are separately labeled secondary diagnostics. The bootstrap intervals describe conditional seed variation, not market uncertainty or simultaneous confidence.

Independent code reconstructs saved-Q greedy policies, counts, complete graphs, exact saved-weight means, cloned diagnostic updates and sampled updates. Every main training update was not independently replayed. Local binary64 Q learning and exact saved-weight graph arithmetic have distinct scopes. The 407.8 MB largest after-run RSS sample exceeded the 256 MB soft target; it is not a measured instantaneous peak. No outcome, seed or checkpoint was dropped.

## Verify saved evidence

Run commands from the project root. Node 24+ uses built-in modules. Python 3.11+ uses standard-library arithmetic for the learner audit.

```text
node --test --test-isolation=none tests/adaptive-learning.test.js tests/adaptive-bootstrap.test.js
python -B -m unittest discover -s tests -p test_adaptive_learning_audit.py
node research/adaptive-learning.js verify
python -B research/audit-adaptive-learning.py
node research/adaptive-analysis.js
node research/build-adaptive-web.js --output reproduced-adaptive-data.json
```

Default independent audits are read-only and do not replace saved receipts. Existing primary execution artifacts block destructive reruns. A fresh full training reproduction requires a new directory and its own source/input freeze; it uses local CPU and substantial checkpoint storage.

Optional graphics/report rebuilding requires numpy, matplotlib, reportlab, pypdf and Pillow:

```text
python -B research/build-capacity-figures.py --structural-only
python -B research/build-main-report.py
```

Read-only presentation adapters test implementation behavior rather than human comprehension or complete accessibility. [ADAPTIVE_REPLAY_QA.md](ADAPTIVE_REPLAY_QA.md) records actual browser observations and limitations after final inspection. The streaming delivery builder is `research/package-adaptive.py`; the external delivery receipt is saved beside the resulting archive. All checkpoints and audited new provenance are preserved; older giant learning traces and account-backed pilot outputs are outside this delivery.

## Historical evidence, retained without stacked 'current' claims

| Stage | Reviewed findings | Report |
|---|---|---|
| Finite coordinated-seller graph audit | [Cycle results](CYCLE_RESULTS.md) | [Finite audit paper](../output/pdf/price-guard-study-v3.pdf) |
| One real activation cap | [Initializer results](HANDOVER_INIT_RESULTS.md) | [Initializer note](../output/pdf/handover-init-note.pdf) |
| Continuous limit and grid sensitivity | [Refinement results](REFINEMENT_RESULTS.md) | [Continuous note](../output/pdf/continuous-refinement-note.pdf) |
| Recurring same-cap timing | [Timing results](RECURRING_RESULTS.md) | [Recurring note](../output/pdf/recurring-cap-note.pdf) |
| Fixed-enforcement calibration reserve | [Calibration results](MODEL_MISSPEC_RESULTS.md) | [Calibration note](../output/pdf/demand-calibration-note.pdf) |
| Individual response to a fixed upper script | [Incentive results](INCENTIVE_RESULTS.md) | [Incentive note](../output/pdf/individual-incentive-note.pdf) |

Earlier archives, frozen sources and interpretations remain historical evidence, not extra independent replications. The [preserved pre-Goal7 research README](README-v8.md) and [root README](../README-before-goal7.md) retain their distinct original bytes; [preservation metadata](README_PRESERVATION_GOAL7.json) records source labels and hashes. Historical model commands in those originals are not part of the current reproduction path.

Author: **Mohammadpayam Teabi**; affiliation remains unsupplied. The main report discloses substantial Codex/AI-agent assistance and its limits. Current experiments use local tabular learners, without language-model/chat/API seller calls, paid inference or external submission. No human participant validation or submission-ready completeness is claimed.
