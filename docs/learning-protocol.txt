# Prospective bounded-run amendment

Version local-learning-amendment-1, 25 October 2026. This amendment is written **before main-run freeze and before substantive learning outcomes are inspected**. The only timing result supplied is a development engineering pilot: 100,000 steps in approximately .154 seconds. That result supports budgeting, not a formation claim. The original `LEARNING_PROTOCOL.md` is retained; this amendment takes precedence where explicitly different.

## Why change the plan?

The complete matched learner study includes base, competence-control, guarded-training, sensitivities, and many continuation branches. Shorter continuation windows and bounded continuous diagnostics reduce runtime/storage while preserving comparisons. This limits claims to immediate and short-run adaptation; 20,000 steps cannot establish long-run robustness or replacement equilibrium.

## Exact core run now frozen

- Twelve main seeds 1001–1012, 3,000,000 unguarded training steps each. Save Q checkpoints at 1m, 2m, and 3m. At 1m/2m evaluate unchanged frozen policies for 2,000 rounds for all seeds.
- Twelve competence controls, one per same seed and equal 3m own-update budget, against a fixed rival at the grid price nearest continuous Nash. Both policies may have bookkeeping, but only independently trained A is transferred; do not call the fixed rival an independently learned competitor.
- Twelve bilateral epsilon=.1 guard-trained markets, 3m steps each. After training evaluate protected and released policies in frozen and adaptive modes.
- Each terminal primary treatment is evaluated frozen for **2,000** rounds, with Q updates and exploration off; adaptive for **20,000** rounds with updates and constant exploration probability **.01**; and updating-greedy for **20,000** rounds with updates but exploration off. This replaces 10k/100k earlier windows. Adaptive exploration is a deliberate floor/restart, not continuation of exp(−12).
- Recovery remains five consecutive 200-step qualifying windows, requiring at least 1,000 rounds. Nonrecovery is censored at the actual branch length. Primary mean-CS contrast is bilateral discrete guard .1 minus unchanged over the 20,000-round adaptive window, all 12 markets. Existing practical success thresholds remain unchanged.

## Exact primary treatment inventory

For every primary seed: unchanged; inherited sham; observation reset; fresh Q with retained observation; fresh Q plus observation reset; cyclic cross-play donor from the next main seed; separately competitive-pretrained successor; bilateral discrete guards epsilon0/.005/.1/**1**/8; A-only and B-only guards at .1; bilateral .1 released after **250** protected rounds; bilateral .1 with believed mu **.20/.50** or believed cost **1.2**; direct grid best response; fixed nearest-Nash grid price; cap at that price; and one forced first-round best-response undercut probe. The undercut may be zero-sized or a price increase; identify rather than relabel it. The forced branch is compared with unchanged at identical starting state.

The added epsilon1 is a prespecified intermediate freedom level, not selected from observed success. Release250 is a short protection test replacing proposed later release windows; it does not establish robustness of long deployments. The larger wrong-model offsets replace the initially suggested mild ones as explicit assumption-breaking stress tests. They are not a sweep proving realistic estimation robustness.

The only continuous diagnostic is **epsilon=.1**, bilateral, seeds **1001 and 1002**, **1,000 rounds** in each of frozen/adaptive/updating-greedy modes. Exact last executed continuous rival prices enter `projectQuote`; only learner observations are quantized. These six branches are diagnostics, not part of the 12-market discrete primary estimate. Epsilon0/.005 continuous diagnostics from the earlier proposal are omitted, not silently claimed completed.

Discrete guards and direct-BR baselines use their exact frozen tie semantics. If a proposal is already one of several grid maximizers, nearest-maximizer projection retains it; otherwise ties between equally near accepted prices choose lower index. Exact guard/direct-BR equivalence must use the same rule. This does not imply uniqueness of a grid Nash equilibrium or inherit the continuous theorem.

## Sensitivities, units, and omissions

Nine one-factor conditions, each trained 3m steps on independent nonmain seeds2001–2004: grid11; grid21; gamma0; gamma.5; beta2e−6; beta8e−6; memoryzero; alpha.05; alpha.30. Baseline values otherwise remain fixed. For each, evaluate unchanged, guard0, guard.1, fresh-Q, and price cap in frozen/adaptive modes. This is **36 sensitivity markets**, not 36 primary replications. Compare descriptively with the declared main reference and disclose the different seed set; a paired within-sensitivity untrained-baseline claim would require separately matched baseline runs.

Zero initialization and executed-action-credit sensitivities from the initial list are **not part of this freeze**. Additional shock, accepted-harm optimization, asymmetric/more-firm/timing work, accessibility checks, and independent human comprehension require separate bounded evidence. Do not mark those backlog tasks complete from the main matrix or substitute programmed extensions for learned-agent results.

Main+warm+guard training totals108m steps; sensitivities add108m, for216m training steps across72 markets. These include dependent equal-seed comparative cohorts; report training resource totals separately from scientific sample size. Development seeds11/22 remain excluded from the held-out analysis; only one timing pilot is recorded so far, not two completed development formation studies.

## Recording and analysis

Record **every evaluated settlement** as compact numeric arrays with declared columns, actual observations, proposals, executed prices, own profits, customer benefit, and coverage. Keep verbose update audits every1,000 evaluation steps and training transition samples every100,000 steps; retain 10k training bins and checkpoint Q tables. This replaces an implied verbose full-Q journal, not the full numeric settlement record. Replayable PRNG and source snapshots remain required.

Formation assessment still uses five terminal 10k training bins and the **2,000-round** separate frozen evaluation. All seeds and failed screens stay in the primary comparisons. Use explicit grid benchmark reference: choose the lowest symmetric pure-grid Nash price if several exist. If none exists, display all pure pairs; use their average as a descriptive normalization only and clearly report lack of symmetric reference. Never silently select the equilibrium closest to an attractive result. If no pure equilibrium exists, benchmark normalized formation claims must be revised before interpretation.

Bootstrap primary paired market-level differences using the already declared fixed analysis seed and10,000 resamples. Use separate frozen/adaptive/updating-greedy tables. Cross-play donors create dependencies, so its interval must not use naive independent paired-market resampling; descriptive reporting is acceptable. Show per-seed outcomes and all treatments, not a selected trajectory. Continuous diagnostics remain separate.

## Budget and freeze integrity

Core budget is a **900-second prospective compute estimate and review cap**, based on measured throughput over all planned base/warm/guard training and evaluations. The runner is not assumed to implement a hard wall-clock kill. Report actual elapsed seconds and any overrun. Do not claim a timeout was enforced when it was not. If the estimate exceeds the cap, revise the actual configuration and freeze before execution; no post-outcome truncation or success-dependent extra training.

The runner saves both protocol files, engine/runner/test hashes, exact treatment inventory and horizon arrays in its manifest before training. Independent review must compare that actual plan with this amendment; written scientific approval does not approve an earlier mismatched runner. Any later change creates a new version/output or a clearly prospective separately labeled extension. No paid resources, API calls, account-backed game players, or slides are authorized.
