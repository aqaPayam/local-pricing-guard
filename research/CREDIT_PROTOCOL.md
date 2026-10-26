# Prospective action-credit extension

Frozen October25,2026 before this extension's substantive outcomes. This is a post-main-study follow-up, not an independent preregistration of the original findings. The old markets and results remain untouched. Existing main outcomes motivated the question; no parameters or acceptance thresholds are retuned.

## Questions and fixed design

1. Is low proposal retention partly a representation artifact? Verify projection idempotence at every grid-state/action and reexpress actual proposals as their projected actions. This must preserve executed prices, rewards, and transitions while making retention100%. Reexpression is an ex-post path description, not a learned policy or new experiment.
2. Does actual constrained-action Q-learning remove corrections without restoring meaningful economic discretion?
3. Do guard variants improve customer welfare or seller profit compared with the simple competitive-price cap, and what happens when protection is removed?

Matched deployment: all12 original final checkpoints1001–1012; none, cap-proposal, cap-aware, guard-proposal, guard-executed, guard-aware. For each branch frozen2000rounds/no exploration/no updates and adaptive20000rounds/.01 exploration/updates. Each starts from the same complete market checkpoint including PRNG streams. Comparison with the old main study is an exact parity target; these markets are not new independent replications.

Equal-budget training:12 NEW independent seeds4001–4012;3million rounds each; none, cap-proposal, guard-proposal, guard-executed and guard-aware. Five variants use paired seeds and identical initial Q tables/PRNG states; variants are dependent, independent unit is market seed. Hyperparameters exactly original alpha.15 gamma.95 beta4e-6,15 prices,1period executed-pair memory, own-profit reward. Save terminal Q checkpoints,10k training bins, and full execution of evaluation actions in compact traces. Evaluate every trained market protected and released, frozen2000 and adaptive20000. Release removes both projector and feasible mask; credit mode remains but proposal=execution when unprotected. No selected seeds, tuning, APIs, account inference or purchased compute. Target total<=600wall seconds; do not selectively extend attractive markets. Frozen manifest records original checkpoint hashes, all source hashes and source copies.

## Distinct algorithms and math

Let M_j(a) be guard/cap projection given prior rival index j, F_j=image(M_j), r own profit, s' next executed pair.

- Proposal: choose/explore any grid action; execute x=M_j(a); update Q(s,a)+=alpha[r+gamma max_b Q(s',b)-Q(s,a)]. This matches original learning-market.js.
- Executed-credit diagnostic: choose/explore any action; execute x=M_j(a); update Q(s,x) using max over ALL next actions. Unexecuted optimistic cells remain selectable/bootstrap targets. This is deliberately a potentially misspecified diagnostic, not standard constrained MDP Q-learning.
- Aware: greedy and uniform exploration restricted to F_j; execute a=x; credit x; bootstrap max ONLY over F_{j'}, where j' is rival newly executed action. Feasibility uses the completed prior quote, never current rival proposal. With one feasible action,100% retention is guaranteed but freedom is zero. Lowest-index greedy ties; independent2draws/firm/round exactly original. Plain none/cap baselines have identical update opportunities and clock.

## Outcomes and analysis

Consumer surplus, both profits, mean prices, actual proposal retention, feasible-action fraction, mean feasible price span, correction distance, marginal proposal/execution entropy (bits). Entropy summarizes the empirical marginal action distribution; it does not measure strategic or conditional freedom. Feasible span is geometric scope, not proof of useful choice. Report seed-level and paired mean differences,95% whole-market percentile bootstrap10000resamples fixed seed20261025; no rounds or training variants counted as independent. Core contrasts guard-aware minus guard-proposal and guard-aware minus cap-proposal for CS/profits/retention/feasible fraction. Include cap-aware matched deployment. New training contrasts paired within seed and own trained model; protected/released evaluate identical terminal checkpoint.

## Verification and boundaries

Parity against original train and advance for none/cap/guard proposal modes; fast/general extension parity for all variants; exact update math and executed-credit indexing; aware actions always feasible; frozen Q immutable; no-treatment interfaces identical. Full compact traces have4unsigned bytes/round (proposalA,proposalB,executedA,executedB), initial/final checkpoints, result/sample updates, source snapshots. Independent auditor should reconstruct economics, feasibility, action selection and Q updates from those artifacts. Snapshot manifest timestamps are local ordering evidence, not third-party preregistration.

Action aliasing, shielding, and projection learning are established ideas; this is a targeted sensitivity analysis, not their discovery. See main prior work and newly identified related sources arXiv2509.12833 and doi10.1016/j.ifacol.2020.12.2276; verify bibliographic details before submission. Small finite toy market, bounded horizons, deterministic tie behavior, optimistic initialization and narrow grids limit generalization. Reexpression cannot establish agent understanding, robust autonomy, equilibrium, or absence of collusion.
