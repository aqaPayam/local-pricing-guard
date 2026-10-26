# Current research and reproduction guide

The latest controlled follow-up asks what changes when the guard is removed after the same initial cap: [all twelve reference comparisons](GUARD_REFERENCE_RESULTS.md), [independent review](GUARD_REFERENCE_REVIEW.md), [prospective protocol](GUARD_REFERENCE_PROTOCOL.md) and [plain explanation](REFERENCE_PLAIN_LANGUAGE.md). Watch the saved shops at `/reference`; choose human prices at `/recurring`. All twelve full-grid-minus-guard cycle-benefit differences are negative, with exact planned mean approximately −12.732973. This supports the guard’s observed usefulness under this budget, alongside the separate limitation of its stronger all-policy promise. It does not prove convergence, universal prevention or equal competence with more legal actions.

The accepted new audit SHA is `2443c1f0874aac903c2125b68b47d6c7a7401d801969829b433d79a47e14bc7b`. With manifest-pinned Python 3.13.0, `python -B research/audit-guard-reference-study.py` performs a read-only full 24M-round replay of the new twelve runs. It reuses authenticated old comparator endpoints; it does not retrain them. The six derivatives rebuild using `python -B research/build-guard-reference-web.py --audit research/guard-reference-results/independent-audit.json --audit-sha <new accepted SHA> --output <new scratch directory>`. The figure uses `build-guard-reference-figure.py --audit-sha <new accepted SHA> --output <new scratch directory>`. The V13 report uses `build-main-report-v13.py --audit-sha <matched accepted SHA below> --reference-audit-sha <new accepted SHA>`; it validates accepted evidence without training. Keep the original output directories and closed receipts intact.

The preceding equal-memory follow-up remains a separate controlled result: [all twelve matched comparisons](MATCHED_CLOCK_RESULTS.md), [independent review](MATCHED_CLOCK_REVIEW.md), and [prospective protocol](MATCHED_CLOCK_PROTOCOL.md). The `/matched` view replays both actual final histories together. That 24-run study has a complete independent 48M-round replay; the older 192-run trajectory remains unreplayed in full. Its mean continuing-enforcement advantage is approximately +0.955595 customer-benefit units, with no convergence or collusion-prevention claim.

Recheck the new study using the manifest-pinned Python 3.13.0 executable and `python -B research/audit-matched-clock-study.py`; the default verifies without rewriting the closed receipt. Deterministic derivatives use `build-matched-clock-web.py --audit research/matched-clock-results/independent-audit.json --audit-sha a19425072110d514f7a0630383eaf2973f465204aa87d2edc3bb6350ae9864f6`. The full evidence archive is required for numerical reproduction; the viewer omits raw audit inputs.

Start with [When a Local Pricing Guard Is Not a Welfare Promise](../output/pdf/local-guard-welfare-report-v13.pdf). It connects the guarantee-capacity result, recurring use of a fixed physical cap, calibration sensitivity, private incentives, the adaptive learner study and funded mixed-gap timing. The [local viewer](http://127.0.0.1:3003/) provides one entry point after starting `node research/demo-server.js` from the project root.

## Explore the result

| View | What it shows |
|---|---|
| [Guard kept or removed](http://127.0.0.1:3003/reference) | Watch two actual saved worlds, all twelve differences, both shops’ profits and exact static anchors. Guard removal still uses the original bounded price grid. |
| [Equal-memory comparison](http://127.0.0.1:3003/matched) | Advance two actual final market worlds together; keep earned prefixes, complete cycles and all twelve matched differences separate. |
| [Saved learner challenge](http://127.0.0.1:3003/opponent) | Run one shop against an actual deterministic saved learner, with exact finite earned/reference ledgers and separate audited infinite values. No fresh cap or browser training. |
| [Flexible cap timing](http://127.0.0.1:3003/timing) | Control both shops and distinguish actual benefit from the guaranteed credit that funds a longer gap. Continuous results remain interval explanations. |
| [Protection game](http://127.0.0.1:3003/recurring) | Coordinate both shops, execute real cap/guard rounds and inspect the separate customer-benefit ledger. |
| [Profit challenge](http://127.0.0.1:3003/profit-challenge) | Choose one shop's prices against a transparent fixed public opponent; compare exact profit after a complete block. Optional hints are stored actions. |
| [Adaptive evidence](http://127.0.0.1:3003/adaptive) | Inspect saved frozen-policy executions, actual training-window means, visit support, both profits/prices and four paired seed comparisons. No browser training occurs. |
| [Calibration assumptions](http://127.0.0.1:3003/uncertainty) | Compare four declared quality-error bounds while keeping enforcement and absolute targets fixed. |
| [Price precision](http://127.0.0.1:3003/refinement) | Distinguish a finite-grid promise from the separately validated continuous result. |

The user's preexisting game and market scaffold and the published sprint starter are prior work. Current sprint contributions are the explicitly source-frozen analyses, controller demonstrations, reproducible numerical evidence and prospectively specified learner follow-up. Established Q-learning, shielding, dynamic programming and numerical verification methods are not claimed as new algorithms.

## Matched study reproduction

The accepted audit SHA is `a19425072110d514f7a0630383eaf2973f465204aa87d2edc3bb6350ae9864f6`. New actual derivatives are exclusive outputs: regenerate the four files into a separate `--output` directory when they already exist, then compare bytes. The figure and report rebuilds use `python -B research/build-matched-clock-figure.py --audit-sha <accepted SHA>` and `python -B research/build-main-report-v12.py --audit-sha <accepted SHA>`. Those builders validate the accepted summary against deterministic reconstruction and do not train sellers. The report keeps eight body pages and discloses old versus new replay coverage.

## Responses against frozen learned partners

Read [the complete 48-label findings](LEARNED_OPPONENT_RESULTS.md), [prospective protocol](LEARNED_OPPONENT_PROTOCOL.md), [certificate mathematics](LEARNED_OPPONENT_THEORY.md), [fixed analysis contract](LEARNED_OPPONENT_ANALYSIS_CONTRACT.md), [pre-case independent review](LEARNED_OPPONENT_PROSPECTIVE_REVIEW.md), and [outcome review](LEARNED_OPPONENT_REVIEW.md). The [manifest](learned-opponent-results/manifest.json), [passed authoritative audit](learned-opponent-results/independent-audit.json), and [complete exact summary](learned-opponent-results/summary.json) bind every planned label and original checkpoint.

The targeted original-tolerance/zero-initialization stratum uses all twelve old seeds, both shops and the original startup-only/selected95 K=4 clocks at final2M. It was chosen after earlier welfare findings and before any new response computation. This is not whole-project preregistration. All 48 executions and certificates passed; achieved gains are positive in 33 cases and exactly zero in 15, with remaining best-response gaps below 4.58e-9 absolute discounted-profit units. No baseline/response continuation uses originally unvisited states or never-tried chosen actions for either firm. Selected95 cycle customer benefit falls in 16/24 responses, rises in 6 and is unchanged in 2. These descriptive dependent labels do not demonstrate intent, equilibrium, discoverability, mutual adaptation or a causal effect of frequency alone.

```text
python -B research/audit-learned-opponent.py
```

This read-only independent audit reconstructs all selected saved-Q masked policies, clocks, exact complete paths, count coverage, final proposal quantization, every-state argmax and every legal Bellman edge. It checks 24 checkpoints, 553,536 world states and 3,660,480 legal edges, rejecting 19 corruption controls. It does not replay original full training or every optimizer sweep, and reuses hash-bound accepted old numerical economic tables. Mathematical gamma 19/20 differs from training's binary64 discount. The white-box optimizer knows the complete frozen partner, masks and rewards.

Frozen derivative rebuilds use `node research/learned-opponent-analysis.js` and `node research/build-learned-opponent-web.js` only after accepted audit bindings. The distinct figure builder is `python -B research/build-learned-opponent-figure.py`; the preserved V11 report builder is `python -B research/build-main-report-v11.py`. Builders preserve V9/V10 reports and figures. The one-shop game is manual explanatory practice, with its own counterfactual original-policy history; finite earned totals and infinite certified values are different quantities. No model/API player, training or data upload runs in the browser.

The primary used about 79.727 seconds, 19,979,290 bytes before completion and an approximately paired sampled process working set of 105,566,208 bytes; no soft target was exceeded. Samples are not simultaneous unique physical memory or a continuous peak. Legacy schema compatibility and isolation/timeout fixes preceded the final source freeze. Both artificial benchmark versions and the abandoned worker-termination history are preserved; only the final v2 benchmark is bound to this study. The full delivery must preserve required `.local` benchmark dependencies despite normal temporary-file exclusions.

## Mixed-gap timing evidence

Read [MIXED_TIMING_RESULTS.md](MIXED_TIMING_RESULTS.md), the [frozen protocol](MIXED_TIMING_PROTOCOL.md), [conditional theory](MIXED_TIMING_THEORY.md), [analysis contract](MIXED_TIMING_ANALYSIS_CONTRACT.md), and [independent review](MIXED_TIMING_REVIEW.md). The [manifest](mixed-timing-results/manifest.json), [authoritative passed audit](mixed-timing-results/independent-audit.json) and [complete summary](mixed-timing-results/summary.json) retain 40 saved finite-game and 80 continuous-model target labels separately. Duplicate, exact-zero, unavailable, unresolved and censored statuses are supported without replacing them with numerical zero.

The same physical cap and full guard stay fixed. Protection covers every prefix since the first real cap, not separately restarted blocks or sliding windows. Each target uses its own fixed-period comparator; a continuous conservative calendar is not declared the exact unknown optimum. The new output exceeded its 50 MB soft target and is retained. No new learning is part of this timing study; adjacent mixing and funded budgets have prior literature. Its audit rechecks inherited scalar-root certificates and every used sum/timing certificate while reusing explicitly bound accepted global premises.

## Adaptive learner evidence

Read [ADAPTIVE_LEARNING_RESULTS.md](ADAPTIVE_LEARNING_RESULTS.md), the [protocol](ADAPTIVE_LEARNING_PROTOCOL.md), [prospective analysis contract](ADAPTIVE_ANALYSIS_CONTRACT.md), and [independent review](ADAPTIVE_LEARNING_REVIEW.md). The [manifest](adaptive-learning-results/manifest.json), [passed independent receipt](adaptive-learning-results/independent-audit.json) and [complete descriptive summary](adaptive-learning-results/summary.json) retain all 192 runs and 384 checkpoints. The [pre-outcome independent-auditor snapshot](adaptive-learning-audit-provenance/before-outcome.py) is preserved separately.

The two masks share one economic calibration. Four primary comparisons retain twelve paired whole-market seeds in each mask/initialization stratum. The endpoint is final saved-history/clock frozen-greedy eventual-cycle customer benefit. Startup-only receives no new cap. Fresh-cap replays, 1M checkpoints, last-100k exploratory training means and all-state policy graphs are separately labeled secondary diagnostics. The bootstrap intervals describe conditional seed variation, not market uncertainty or simultaneous confidence.

Independent code reconstructs saved-Q greedy policies, counts, complete graphs, exact saved-weight means, cloned diagnostic updates and sampled updates. The complete main training trajectory was not independently replayed; sampled updates and cloned probes were checked. Local binary64 Q learning and exact saved-weight graph arithmetic have distinct scopes. The 407.8 MB largest after-run RSS sample exceeded the 256 MB soft target; it is not a measured instantaneous peak. No outcome, seed or checkpoint was dropped.

## Verify saved evidence

Run commands from the project root. Node 24+ uses built-in modules. Python 3.11+ uses standard-library arithmetic for the learner audit.

For the new timing study, use the authoritative Python driver, which computes continuous checks in process and invokes the independent JavaScript checker. A JavaScript-only component receipt is insufficient:

```text
python -B research/audit-mixed-study.py
node research/mixed-timing-analysis.js
node research/build-mixed-timing-web.js --output reproduced-timing-data.json
```

For the saved learner evidence:

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
python -B research/build-main-report-v10.py
```

The V10 report builder regenerates only its new timing figure and report; it reads the immutable V9 figures. Read-only presentation adapters test implementation behavior rather than human comprehension or complete accessibility. [Timing QA](MIXED_TIMING_REPLAY_QA.md) and [learner QA](ADAPTIVE_REPLAY_QA.md) record actual browser observations and limitations. The delivery builder is `research/package-mixed-timing.py`; full and viewer-only receipts are saved beside their archives. The full archive preserves the numerical evidence and inherited checkpoints. The smaller viewer-only archive omits raw audit dependencies and points to the full archive by hash; it cannot reproduce those audits. Older giant learning traces and account-backed pilot outputs are outside this delivery.

## Historical evidence, retained without stacked 'current' claims

| Stage | Reviewed findings | Report |
|---|---|---|
| Finite coordinated-seller graph audit | [Cycle results](CYCLE_RESULTS.md) | [Finite audit paper](../output/pdf/price-guard-study-v3.pdf) |
| One real activation cap | [Initializer results](HANDOVER_INIT_RESULTS.md) | [Initializer note](../output/pdf/handover-init-note.pdf) |
| Continuous limit and grid sensitivity | [Refinement results](REFINEMENT_RESULTS.md) | [Continuous note](../output/pdf/continuous-refinement-note.pdf) |
| Recurring same-cap timing | [Timing results](RECURRING_RESULTS.md) | [Recurring note](../output/pdf/recurring-cap-note.pdf) |
| Fixed-enforcement calibration reserve | [Calibration results](MODEL_MISSPEC_RESULTS.md) | [Calibration note](../output/pdf/demand-calibration-note.pdf) |
| Individual response to a fixed upper script | [Incentive results](INCENTIVE_RESULTS.md) | [Incentive note](../output/pdf/individual-incentive-note.pdf) |
| V9 consolidated report and adaptive follow-up | [Learner results](ADAPTIVE_LEARNING_RESULTS.md) | [Preserved V9 report](../output/pdf/local-guard-welfare-report.pdf) |

Earlier archives, frozen sources and interpretations remain historical evidence, not extra independent replications. The [preserved pre-Goal7 research README](README-v8.md) and [root README](../README-before-goal7.md) retain their distinct original bytes; [preservation metadata](README_PRESERVATION_GOAL7.json) records source labels and hashes. Historical model commands in those originals are not part of the current reproduction path.

The exact [V9 research README](README-v9.md), [root README](../README-before-goal8.md), report, builder and navigation copies are preserved with [V9 source hashes](README_PRESERVATION_GOAL8.json). Current README/navigation files are explicitly mutable in the V10 delivery; V9 science, figures, report and archive remain unchanged.

Author: **Mohammadpayam Teabi**; affiliation remains unsupplied. The main report discloses substantial Codex/AI-agent assistance and its limits. Current experiments use local tabular learners, without language-model/chat/API seller calls, paid inference or external submission. No human participant validation or submission-ready completeness is claimed.
