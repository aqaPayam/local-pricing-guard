# Independent review of the local-learning study

Started 25 October 2026. This is a live review record. Pending checks are not passed checks. Reviewer agreement does not establish scientific truth or novelty.

## Current status

Protocol and corrected implementation reviewed; main, diagnostic, initialization and bounded-extension numerical audits passed as detailed below. The supported practical-advantage finding is negative. Portable extraction tests, complete main audit and analysis-regeneration verification passed. The existing continuous-price contract theorem does not automatically apply to a finite-grid action guard.

## First protocol/implementation review

The proposed protocol is scientifically defensible as a bounded, potentially negative local-learning experiment. It distinguishes formation from programmed cooperation, policy replacement from observation reset, frozen from adaptive evaluation, and ordinary controllers from the proposed guard. Its practical success gate includes retained proposals rather than welfare alone.

The initial runner does not yet implement that protocol. Critical discrepancies were sent to the root and implementation agent before substantive training: 500/2,000 rather than 10,000/100,000 evaluation rounds; no adaptive exploration rather than .01; initial competitive rather than random completed state; and fixed-opponent warm training passed to an engine routine that ignored the option. The latter would make the purported competence control identical to unguarded self-play. Seed/cohort definitions and replacement/deviation branches also differed. These must be corrected or prospectively amended before freezing the main study.

Additional engine issues: continuous treatment silently unsupported in the fast training path; policy replacement automatically resets observation; accepted-action fraction computed from guard intervals even for other controllers; pure equilibria inferred only from a single tie-selected best response. Corrections must preserve an auditable distinction between actual feasible choices and diagnostic quantities.

The core budget estimate must cover unguarded, warm-competence, and guarded-training cohorts, not just the first 36 million steps. No run-time or formation result is assumed here.

### Engine corrections reviewed

The implementation agent corrected the identified fast-training, warm-opponent, replacement/reset, tie-set and feasible-action-count issues. Random initial grid pairs now replace the initial competitive pair. The deviation probe changes executed action while retaining the original proposed-action Q credit. Compact evaluation settlements retain all actions and states, with periodic verbose Q audits. The runner now requests 2,000 frozen and 20,000 adaptive rounds; these are prospective changes requiring the amendment document before the manifest is frozen.

### Prospective training gate cleared

Read the completed `LEARNING_PROTOCOL_AMENDMENT.md` against the current runner before main training. Inventory, 1m/2m checkpoint evaluations, horizons, exploration floor, donor mapping, compact trace policy, 72 training markets/216m steps, and bounded continuous diagnostics agree. Gate cleared to freeze and run this bounded numeric study. This approves experimental coherence, not anticipated findings. Sensitivities lack matched nonmain baseline training, so hyperparameter-effect comparisons remain descriptive. Fixed-rival competence still needs measurement before calling the transferred warm policy competent. No formation outcomes were observed before this gate; only an engineering timing result was supplied.

### Sharper continuous bound

The reviewer independently differentiated the supplied best-response derivative, obtaining the stated critical-point condition `exp(w-3)*w*(w*w+2*w+2)=1`. Its left side is strictly increasing for positive w. Independent Python arithmetic confirmed the bracket [1.14,1.15], conservative product upper bound 0.43995961934304906 below .44, and every row of the 20-round perturbed-contraction/consumer-surplus envelope. The fifth-round floor is 55.23001023759295 for epsilon .005 under the original assumptions. Accepted as a tightening of the original ideal continuous-model bound, not a theorem for finite-grid learners or a formal floating-point certificate. The old frozen six-round bound remains valid.

### Bounded boundary checks

Independent Python arithmetic checked 3,528 retained search/shock/timing/structural rows with 48,069 numeric assertions: all settlement quantities/profits/surplus, interval-optimum first-order conditions, nonboundary interval-endpoint losses, structural Nash stationarity and source hashes. Output: `boundary-results/independent-audit.json`. This checks saved numeric trajectories; it additionally replays all timing observation indices, inactive prices and active endpoint losses. It does not independently rerun beam enumeration/pruning or certify global optimality. Three-firm and asymmetric-product checks remain deterministic toy extensions, not learned-agent robustness evidence.

## Empirical interpretation — main numerical audit passed

The main completion records 72 training markets, 216 million training steps, 1,230 evaluation branches and 15.63 million evaluation rounds in approximately 499 seconds. Scientific primary sample size remains 12 independently trained markets.

Initial summary inspection finds adaptive mean consumer benefit 45.2917 without intervention and 72.1143 with the epsilon-.1 guard. However, the guard changes 93.2548% of proposals, retaining only 6.7452%; it **fails the prespecified 20% retained-action practical-success gate**. A simpler competitive-price cap produces consumer benefit 73.1873 while retaining approximately 33.6296% of proposals. Mean A profit differs (guard 22.0224; cap 21.5277), so this is not an unqualified Pareto-dominance result. It is strong evidence against presenting the proposed guard as a demonstrated practical advantage in this calibration.

Proposal retention is an **interface-sensitive intervention-burden measure**, not an intrinsic measure of retained intelligence or all economically useful freedom. Multiple proposed indices can execute identically through the guard; finite Q learning, initialization and deterministic tie behavior can retain these aliases. A guard-aware proposer could report its already-projected action and reach 100% apparent retention without changing executed prices at all. The prespecified gate still fails for the tested proposal interface, but this does not prove a general autonomy impossibility. Accepted-grid fraction and both profits must accompany retention. No outcome-driven threshold change or additional experiment is needed to state that limitation honestly.

Information-only reset mean benefit is 45.1460, close to unchanged continuation; fresh-Q replacement gives 61.5295. These aggregate differences need the full paired analysis and cold-start controls before a mechanism claim. None establishes textual handover efficacy. An independent calculation of the declared basic formation screen (five terminal training bins plus final frozen evaluation, lowest symmetric grid-Nash reference) finds all 12 markets pass. This supports the learned high-price premise for this calibration and budget, without establishing intent, equilibrium credibility, or general convergence.

## Completed independent numerical audits

`audit-learning-study.js` imports none of the study's engine/economy modules. It independently checked **250,232,326 assertions**, **15,630,000 evaluation rounds** and **1,230 branches**. Starting from saved Q checkpoints, it replayed evaluation observations, RNG draws, proposed actions, discrete action maps/coverage, economic settlement, evolving Q tables, periodic update journals, branch metrics and the primary paired difference. Continuous projections were independently approximated with golden-section profit maximization and loss-root calculations. Maximum observed arithmetic disagreement was approximately 2.16e-12; no near-tied greedy-action tolerance was needed. Source snapshots, grid payoff matrices, all pure grid equilibria and joint-profit references were checked. Output: `.local/learning-study-v1/learning-audit.json`.

The auditor checks sampled training updates, not every one of the 216 million training transitions. A passing arithmetic audit is not a formal proof or an empirical novelty certificate. The primary paired customer-benefit gain is 26.82261635534053; the failed retained-discretion gate remains failed despite numerical correctness.

Separate independent Python audits checked diagnostics (308,898 assertions, including all warm-policy state gaps and diagnostic settlements) and initialization extensions (528,000 rows, 2,643,216 assertions, including guard/cap mapping, aggregate economics and sampled Q arithmetic). Their `independent-audit.json` records are in the corresponding evidence folders. Warm policies achieve fixed-rival realized profit gaps below 9.5e-13 in that trained context, while unvisited-state greedy gaps remain substantial. Transfer competence against arbitrary adaptive rivals is therefore not established.

The three distinct loss measures were additionally derived from all 108 wrong-model branches. Independent scalar recomputation verified all three means/maxima for the seed-1001 frozen low-mu, high-mu and wrong-cost branches (6,000 settlements, 18 aggregate assertions). Output: `learning-results/model-losses-independent-audit.json`. The other 105 derived branch aggregates were not separately recomputed in that supplemental check; the main auditor already verified their true-loss metrics and believed-model guard maps. These are retrospective derivations from full numeric logs, not three originally logged metric columns.

## Claim decision and backlog review

The supported result is a **negative practical-advantage finding with a useful mechanism benchmark**: actual profit-only learners develop high pricing in this calibration; the proposed guard reduces consumer harm but achieves it through extensive intervention, fails its prespecified discretion target, and does not outperform the simpler cap on consumer benefit plus retained proposals. Profit tradeoffs must remain visible. This is more meaningful empirical evidence than the original scripted demonstration, but it is incremental and does not establish a new broadly effective anti-collusion algorithm.

Reviewed `BACKLOG_COMPLETION.md` against the original 52-task list. Its distinction between bounded toy extensions and learned-agent evidence is essential. Task 49's human-comprehension component remains unverified; developer/browser checks cannot substitute for a real independent participant. Alternative action-credit learning, language semantics and learned multi-firm/shock/timing robustness remain outside the tested claim. Tasks 50–52 require the final portable extraction/provenance record and report scope to be closed; passing the main arithmetic audit alone does not close packaging or human-evidence gaps.

I accept reporting this scoped negative result with its complete controls and limitations. Acceptance is not a ranking prediction or a requirement that future reviewers agree. New evidence that overturns the interpretation should change the conclusion.

## Final portable-artifact acceptance

The extracted portable copy passed all 31 tests and the complete independent main audit again: 250,232,326 checks, 15.63 million settlements and 1,230 branches, with the same approximately 2.16e-12 maximum discrepancy. Regenerating analysis in that extracted copy reproduced all six CSV tables and three PNG figures byte for byte, including the added cumulative customer-benefit/profit columns. Content hashes and the final archive provenance are recorded by the packaging workflow; this acceptance does not substitute for its final archive-integrity record.

I accept the current report scope and the 52-task evidence ledger for delivery as a bounded comparative research artifact with a negative prespecified practical-gate result. The corrected report avoids treating proposal retention as intrinsic intelligence or finite guarded training as a universal impossibility result. Human first-time comprehension remains unverified; the mathematical guarantee remains specific to the original continuous economy; learned-agent results remain confined to the stated finite-grid protocol. No further experiment or engine change is required to support those limited claims, and no first-place or general anti-collusion-success claim is justified.

## Required evidence before substantive training

- A primary-source protocol comparison and declared departures, including feasible training duration and grid resolution.
- Individual-profit rewards without cooperative instruction or seeded monopoly labels; initialization and random initial states disclosed.
- Exact definitions of replacement, learned-policy inheritance, observation reset, warm-start competence, frozen evaluation and online adaptation.
- Fixed primary outcomes and comparison controllers before evaluation.
- Independent training-market seeds as the sampling unit; branches and rounds remain dependent.
- Explicit state, proposed action, executed action, reward and Q-update semantics, including aliases introduced by the guard.
- Frozen configuration/source manifest, resource budget and formation go/pivot rule.

## Independent audit plan

Recompute logit shares, profits and consumer surplus directly, without importing the learning engine. Recompute finite-grid best responses, Nash candidates and joint-profit references, including ties. Check guard acceptance/projection maps; distinguish discrete and continuous guarantees. Replay logged updates from old Q, action, reward, next-state maximum, alpha and gamma. Check source/config hashes, checkpoint identities and preintervention matching. Recompute evaluation metrics and paired seed aggregates. Inspect replacement asymmetries and all main failures.

Retain checkpoint Q tables, previous executed-price state, exploration clock, and RNG state. Evaluation traces must identify proposed and executed action indices. Sampled training updates must contain enough values for independent arithmetic replay. An audit cannot infer missing evidence from summary tables.

## Claim gates

1. Protocol valid and feasible before substantive training.
2. Learning verified against fixed-opponent diagnostics before formation claims.
3. Formation without programmed cooperation established or explicitly reported absent.
4. Matched intervention and simple-controller comparisons complete before guard-value claims.
5. Independent numerical audit and claim-evidence review complete before presentation scope is settled.

## Evidence boundary maintained

All 52 backlog items are mapped in `BACKLOG_COMPLETION.md`, with the final packaging record retaining artifact-integrity evidence. Human comprehension cannot be marked verified without observed independent playtesting. Asynchronous, three-firm and unequal-product extensions are bounded deterministic checks; they do not establish learned-agent robustness. No text-semantics claim follows from tabular Q learning.
