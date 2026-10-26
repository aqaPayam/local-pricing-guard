# Action-interface sensitivity: perfect retention can hide one permitted price

## Main conclusion

**Low proposal retention was substantially an interface artifact; fixing it did not restore economic choice.** A feasible-action Q learner retains100% of its proposals, while a proposal-credit learner retains approximately0.07% after adaptation. Yet both execute exactly the same price, earn the same profits, and deliver the same consumer surplus in the prespecified terminal window. Every visited guard-state there permits only one of15 prices and has zero permitted span. This is a bounded diagnostic of the original guard/learning architecture, not discovery of action aliasing or a new general anti-collusion defense.

The old20%-retention criterion is not rewritten retroactively. The new feasible-aware interface passes its numerical retention component, demonstrating why retention alone is an insufficient practical-autonomy criterion. The original proposal-interface failure remains correctly reported, but it should no longer be interpreted as an interface-invariant lack of learner competence.

## Prospective design and accounting

[CREDIT_PROTOCOL.md](CREDIT_PROTOCOL.md) and sources/checkpoint hashes were frozen at2026-10-25T16:12:40.046Z, before extension outcomes. Existing main-study outcomes motivated this follow-up, so this is not a fresh preregistration of the original finding. All12 original terminal checkpoints1001–1012 received six matched deployment arms: none, cap-proposal, cap-aware, guard-proposal, naive guard-executed credit, and guard-aware. Frozen evaluations use2000rounds; adaptive evaluations use20000rounds and fixed.01 exploration. The old checkpoint comparisons are dependent on the prior study and are not additional independent replications.

Twelve newly seeded markets4001–4012 received equal3million-round training budgets under five arms (cap-aware omitted from new training), with unchanged hyperparameters, own-profit rewards, simultaneous sealed choices, private Q tables, and independent firm PRNG streams. Each terminal checkpoint was evaluated protected/released and frozen/adaptive. New-market independent unit is seed, n=12; algorithm variants share seed and are paired, not independently counted.

Main extension completed60 training labels/180million training rounds and384 evaluation branches/4.224million evaluated rounds in119.63seconds. A separately prospective [long amendment](CREDIT_LONG_AMENDMENT.md), frozen16:13:55.542Z before its first long branch, adds60 branches/6million rounds: five arms on all12 old checkpoints,100000adaptive rounds, with both full-window and final20000-round reporting. It took15.65seconds. **Total actual evaluation branches444; total evaluated rounds10.224million.** Analysis has504rows because60 terminal-window rows reuse long-branch data; they are not additional experiments. Local CPU only; no API, account player, paid service or cloud compute.

## Algorithms and why the distinction matters

Let F_j be the image of the projection given the previous completed rival quote j. Proposal credit updates Q(s,a) with reward from execution M_j(a), and bootstraps across all next proposals; this exactly matches the old engine. Naive executed credit changes the credited cell to Q(s,M_j(a)) while leaving chooser/bootstrap unrestricted. This deliberately potentially misspecified diagnostic can leave optimistic infeasible cells selectable and is not standard constrained Q-learning.

Feasible-aware learning chooses and explores only F_j, credits the executed action, and restricts the Bellman maximum to F_j' at the **next** state, indexed by the newly executed rival price. No current rival proposal is observed before choice. Release removes both projection and feasibility mask. The feasible-aware comparison changes action support, exploration distribution, and bootstrap support together; it cannot isolate credit assignment alone as the sole mechanism.

The exact update and information boundary are in the protocol. Lowest-index ties and two PRNG draws per firm/round match the original implementation. Six development tests passed: original train parity, original adaptive parity, fast/general extension parity across all arms, mask feasibility, exact executed-cell temporal-difference math, and frozen-Q/no-treatment equivalence. The independent audit subsequently passed all444evaluation branches/10.224million transitions,69,184,729checks,zero maximum discrepancy. It independently reproduced all42summary groups and32paired contrasts including the10000-resample intervals, checked terminal-window entropies, verified source/snapshot hashes, and rejected intentionally corrupted trace and terminal-Q examples. These checks establish internal consistency, not external validity. See credit-results/independent-audit.json and CREDIT_INDEPENDENT_REVIEW.md.

## Matched deployment results: initial20000rounds

Means over the same12 original checkpoints; CS is logit consumer surplus per round, profits per seller/round.

| Arm | CS | Profit A | Profit B | Proposals retained | Feasible fraction | Execution entropy, bits |
|---|---:|---:|---:|---:|---:|---:|
| None |45.291667|30.846946|31.796698|100%|100%|1.463416|
| Cap, proposal |73.187337|21.527679|21.522705|33.6296%|13.3333%|.861015|
| Cap, aware |72.342688|21.918732|21.915963|100%|13.3333%|.326845|
| Guard, proposal |72.114283|22.022448|22.022393|6.7452%|6.6742%|.011577|
| Guard, naive executed credit |72.106812|22.025630|22.025561|.2931%|6.6884%|.026210|
| Guard, aware |72.117715|22.020985|22.020941|100%|6.6677%|.002812|

Guard-aware minus guard-proposal CS difference is+.003431, paired95% bootstrap interval[.000012,.008063], versus a93.2548percentage-point retention increase. Its average feasible price span is approximately.000006, versus the full grid span.542465. A large retention change therefore accompanies a negligible economic change and almost no on-path permitted price range. Marginal entropy is descriptive realized variation, not conditional or strategic freedom.

Cap-aware illustrates the same retention mechanism for a simple controller. Masking exploration changes its observed price distribution, so aware and proposal cap CS need not match. Cap image has two actions and a fixed span.038748; that geometric space alone does not establish valuable seller autonomy.

## Longer adaptation changes the cap comparison

| Adaptive window | Arm | CS | Profit A | Retained | Feasible fraction | Feasible span |
|---|---|---:|---:|---:|---:|---:|
| All100000 | None |46.353592|30.396904|100%|100%|.542465|
| All100000 | Cap-proposal |72.337661|21.919544|11.9373%|13.3333%|.038748|
| All100000 | Guard-proposal |72.118089|22.020810|4.1333%|6.6682%|.000009|
| All100000 | Guard-aware |72.118775|22.020518|100%|6.6669%|.000001|
| Final20000 | None |46.792094|30.225895|100%|100%|.542465|
| Final20000 | Cap-proposal |72.121651|22.019226|8.4110%|13.3333%|.038748|
| Final20000 | Guard-proposal |72.119040|22.020401|.0725%|6.6667%|0|
| Final20000 | Guard-naive-executed |72.119040|22.020401|.0725%|6.6667%|0|
| Final20000 | Guard-aware |72.119040|22.020401|100%|6.6667%|0|

All three guard variants have exactly identical economic summaries in the last20000rounds, including zero execution entropy. Proposal/executed interfaces keep proposing mainly rejected actions while the aware interface chooses the unique permissible price. **Do not preserve the earlier claim that the cap has a large enduring CS advantage**: the1.07-unit20k advantage over guard-aware shrinks to.218886 over100k and.002610 in the terminal window. The latter remains positive across these seeds, paired95% interval[.002301,.002936], but is economically tiny and accompanies a similarly tiny profit difference. The cap still permits two prices versus one on the guard path; economic value of that flexibility is unestablished. Bounded terminal stability is not proof of asymptotic convergence.

## Equal-budget newly trained markets and release

Protected adaptive CS is72.119040 for all three guarded learner variants, with profits22.020401/22.020401, one permitted action, zero permitted span and zero execution entropy. Proposal and naive-executed credit retain.0696% of proposals; aware retains100%. Protected frozen retention is0% versus100%, again with identical economics. Thus the interface conclusion survives12 new seeded training markets and equal learning-update budgets.

Released adaptive CS: proposal58.096744, naive-executed58.168839, aware58.082394; cap-trained58.569733 and separately unguarded-trained45.339763. Aware-minus-proposal released CS is-.014350, paired95% interval[-1.077179,.790761]. **No incremental unguarded transfer benefit from feasible-aware training is demonstrated.** Protected and released conditions are not competence-matched environments, and infeasible actions were untrained under the mask; the result does not show that richer constraint-aware agents cannot learn a transferable strategy. All configurations show substantial benefit relative to the separately unguarded-trained baseline here, but that does not identify a unique aliasing mechanism.

## Exact representation diagnostic and limits

All225 grid projection cells satisfy M_j(M_j(a))=M_j(a). Replacing each recorded proposal with its executed accepted action reproduces that recorded economic path and makes its retention100%. This is an ex-post **path reexpression**, not a new learned policy. It does not preserve proposal-index Q updates or guarantee the same future learning if rerun under changed action labels. The genuinely executed aware-policy experiments are the separate test of behavior.

Prior work already discusses action aliasing, shielding, and projection learning; see the main bibliography plus newly identified arXiv2509.12833 and DOI10.1016/j.ifacol.2020.12.2276, whose bibliographic details should be verified for final reporting. The contribution here is the documented size of metric sensitivity and the separation of retention, feasible price range, welfare, profits, and release behavior in this specific guarded pricing benchmark.

Limitations: one stylized deterministic two-firm economy, narrow15-price grid, alpha/gamma/exploration/ties fixed, small seeded samples, optimistic initialization, finite horizons, no strategic equilibrium verification, no language or communication, no human study, no real-world deployment. Seed bootstrap intervals describe variation under this simulator/configuration, not external-market prevalence. A one-price on-path image does not imply the guard has one allowed action in every off-path state. We did not tune tolerances or invent a new economic freedom threshold after seeing results. Full tables/seed distributions, frozen ordering records and trace replay support a modest architecture diagnostic rather than a general autonomy impossibility result.

Reproduce: `node research/credit-analysis.js` writes [credit-results/analysis.json](credit-results/analysis.json) and [per-market.csv](credit-results/per-market.csv). Sources and initial/final checkpoints plus unsigned4byte/round action traces are in credit-results; independent audit is authored separately. Raw results and protocol should travel together.
