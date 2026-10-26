# Offline mechanism study: safe handover

Protocol version: offline-mechanism-1. Prepared 24 October 2026 before this study's evaluation results. This is a deterministic constructed-mechanism study, not an empirical study of AI learning or spontaneous collusion. Earlier LLM pilot results belong to a different exploratory study.

## Question and expected null

Can a handover preserve useful public business information while removing instructions that sustain a harmful pricing convention? This stage measures how the answer depends on an explicitly programmed successor rule and the channel carrying the convention.

The current engine supplies safe and facts with equivalent decision-relevant inputs: identical numeric history, no predecessor strategic instruction, and unchanged public cost/demand facts. A factual template that the rule ignores does not change this equivalence. **Expected primary null: safe and facts have identical trajectories and outcomes.** Report this null directly; do not manufacture a safe-policy advantage. A separate directive intervention is not part of the present grid.

The prior starter already supplies participant replacement and history-window controls. This work contributes an interpretable constructed comparison and a safety–utility evaluation design; no first-ever novelty or validated safety claim follows.

## Freeze and execution boundary

Before evaluating the first grid configuration, the runner writes an immutable manifest containing UTC generation time, protocol version and SHA-256 hash, relevant source hashes, exact factor arrays, economic parameters, controller definitions, intervention semantics, and metric definitions. Hash this protocol and engine rather than merely recording a version string. Save manifest before outputs; preserve it alongside complete cases and results. If changes are needed, create a new output/version and explain them.

Required factors must actually affect the configured engine when relevant. In particular, verify `anchorTolerance` and the fixed-high incumbent option exist and are passed through. If absent, stop execution and implement/verify them before freezing the run. An ignored factor is not a sensitivity experiment. No model calls, provider credentials, Codex player inference, paid compute, or remote inference are permitted.

## Configuration grid

Cross the following factors:

| Factor | Levels |
|---|---|
| Origin/incumbent pair | Competitive/reactive; cooperative/reactive; cooperative/fixed-high |
| Convention memory rule | History; note |
| Successor A rule | Convention; myopic independent best response; static one-shot Nash |
| Handover | Continue; full; facts; safe; minimal |
| Final round | 40; 80 |
| Takeover round | 8; 16 |
| Anchor tolerance | 0.005; 0.05; 0.30 |

Total: `3 * 2 * 3 * 5 * 2 * 2 * 3 = 1080` configuration rows. These are deterministic design cells, not 1080 independent sampled markets. For continue, the successor rule is unused, so those rows repeat the same control for three nominal successor levels. Other factor combinations may also induce identical paths. Save all rows for completeness, but identify duplicated effective configurations and never count them as independent evidence. Pair handovers within every other factor setting. Horizons share a trajectory prefix and are not independent repetitions.

Tolerance levels were chosen before grid execution to span strict matching and broad anchoring: the large 0.30 tolerance can include a best-response price cut of roughly 0.24 near the elevated origin. This is a mechanism-parameter sensitivity, not random replication. The same tolerance must govern the corresponding note-driven incumbent undercut cutoff; record exact comparisons in the frozen source.

Economic parameters and demand match `replacement-market.js`; benchmarks are computed from that same economy. A and B choose simultaneously using only completed previous rounds. The takeover applies once, before A's decision on the takeover round. B's allowed state remains unchanged across paired arms. Public cost, demand, and action bounds remain available even with minimal memory. Only A's successor rule changes; continue retains both original rules.

The cooperative origin and any retaliation are programmed, not learned. State the rule precisely in the manifest, including tolerance comparisons, whether the note survives each arm, when a convention terminates, and the fixed-high price. A finite horizon is an observation limit, not an equilibrium argument.

## Outcomes and comparison windows

Primary window: all completed rounds from takeover through the final round inclusive. Also report first five and final ten successor rounds to expose transient differences. Report window lengths explicitly; the windows can overlap and are descriptive.

Per configuration save mean consumer surplus, per-seller profit, prices, quantity, total surplus, and separate per-seller normalized profit gain. Use `max(0, Nash consumer surplus - observed mean consumer surplus)` as benchmark-relative customer harm. This is a model welfare quantity, not real-world money or a legal assessment. Mean seller profit must not conceal losses to one seller.

Primary comparisons: safe minus full and safe minus facts, paired within each remaining factor combination. Secondary comparisons: facts versus full and minimal versus facts. Also compare every arm with continue as an operational reference, noting that continue may use a different controller from successor arms.

## Provisional success gates

These thresholds are design choices, not tuned estimates or validated standards:

- At harmful origins where full-handover harm is at least 5% of Nash consumer surplus, safe should reduce that harm by at least 50%. Below that denominator gate, report levels rather than an unstable recovery percentage.
- At competitive origins, safe should lose no more than 5% of Nash per-seller profit for A relative to full, and lose no more than 2% of Nash consumer surplus relative to full. Use absolute benchmark-scaled differences, including when observed profits are negative.
- For descriptive grid summaries, report the fraction of distinct design cells with harm above 5% of Nash consumer surplus. The competitive-origin target is an increase of no more than 5 percentage points relative to full. This is a proportion across chosen design cells, not an estimated population probability.

Show all gates separately. A candidate must meet safety and utility gates to pass the proposed combined criterion. Passing on a subset of controllers is conditional evidence only. Expected safe=facts results may show failure of safety recovery when history alone carries the convention; that is informative and must remain visible.

## Forced deviation probe

For each effective configuration, copy the exact state immediately before takeover. Compare the normal continuation with a paired branch in which A's first successor decision alone is forced to the one-step best response against B's last observed price. Both choices remain simultaneous: the probe does not peek at B's current action. The presumed best response can differ from the actual best response against B's current choice; record both realized prices.

After that one-round intervention A resumes its configured rule. Fix how the forced action updates public history and own notes in the manifest; use the normal settlement/update process. Retain B's full internal state at the fork. Run to the same final round.

Report immediate A-profit difference and A's discounted cumulative profit difference versus no-cut for discount factors 0.90, 0.95, and 0.99, discount exponent zero at takeover. Also report changes in B's prices versus no-cut and customer surplus. If A's normal choice already equals the forced price, report a zero-size intervention. Do not call every probe an undercut if it is not one.

These trajectories reveal programmed responses and the profitability of one specific deviation over the chosen horizon. They do not establish a repeated-game equilibrium, prove all deviations unprofitable, or show that any model learned to punish.

## Integrity checks and reporting

Verify economic benchmarks; action bounds; simultaneous decisions; no current-price leakage; exact handover timing; safe=facts equivalence; identical deterministic repeats; and unchanged economic parameters. Check that every intended configuration and paired probe has a completed record, or explicitly report failure. Save full trajectories or sufficient replay data, manifests, machine-readable case tables, and readable findings.

Do not use p-values, confidence intervals, or standard errors on this deterministic grid. Present differences, sensitivities, case counts, duplicated configurations, and counterexamples. Do not select only successful cooperative origins. Publish a clear account of which outcomes arise directly from programmed assumptions.

## Decision after this stage

Review whether a meaningful unresolved learning question remains. Local RL is an option, not a promised completed AI study: define states, objectives, discounting, training budget, independent training seeds, and training/evaluation separation first. LLM evaluation requires a separate approved inference source and budget; the user's Codex/ChatGPT game-player allowance remains forbidden. Prepare results and a presentation-ready evidence package, but do not create a presentation until the user requests it.
