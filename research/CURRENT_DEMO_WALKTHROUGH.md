# A short walkthrough of the current research

This guide accompanies the V13 report. It is a demonstration script, not a
record of human participants or an extra scientific experiment.

## The question in one sentence

Can a rule that checks each shop’s immediate profit protect customers over
many rounds, and what changes when that rule is kept, removed or periodically
interrupted by the same price ceiling?

## Three minutes in the viewer

1. Start `node research/demo-server.js` from the project root and open
   [Market Lab](http://127.0.0.1:3003/). The two entry choices are **Play**
   (you choose both prices) and **Watch** (saved shops choose).
2. Open **Play** to see a real capped market round, permitted subsequent
   prices, both shops’ profits and the customer-benefit ledger. The person
   knowingly controls both shops. This explains a possible continuation;
   it supplies no evidence of independently learned coordination.
3. Open [Watch](http://127.0.0.1:3003/reference). Keep the default Example 1.
   Both worlds already finished learning after the same initial ceiling.
   Initial displayed prices are remembered history and have earned nothing
   in this replay. Neither world receives another starting cap.
4. Click **Watch both: 1 round**. Both saved worlds advance. Example 1’s
   displayed customer-benefit difference is approximately **−23.168** for
   that first round. This is a newly earned prefix, not the whole-cycle result.
   Click **Watch 20 rounds**, **Undo 1 round**, then **Start replay again**
   to see exactly what those controls change.
5. Look at **all twelve examples**. Every full-grid-minus-guard difference
   is negative; the exact all-twelve mean displays approximately **−12.733**.
   Keeping the guard helped these trained shops’ customers under this budget.
   The reference still uses the original bounded price board.
6. Open the checkpoint and static-anchor details. All 24 new checkpoints and
   12 inherited comparator finals remain visible. Static Nash and joint-profit
   maxima describe the one-round table, not equilibrium of learned programs.
   Exact prices and both firms’ profits remain available in the metrics CSV;
   static exact fractions are in the anchor CSV.

For the separate question of repeating the ceiling, open
[the matched-clock comparison](http://127.0.0.1:3003/matched). Its twelve
recurring-minus-startup differences are all positive, with exact planned mean
approximately **+0.955595**. It is a different treatment contrast.

## What is research, and what is an illustration?

| Item | What supports it | Its limit |
|---|---|---|
| A local check is weaker than an all-policy welfare promise | Finite-state worst-cycle calculations and separate continuous bounds | Conditional on the explicitly specified market and numerical premises |
| Keeping the guard helps these learners | Twelve new equal-clock/equal-allocation full-grid runs compared with accepted guard endpoints; full independent 24M-round replay | One finite-budget model; more legal choices change learning difficulty |
| Repeating the cap helps in the matched study | Separate 24-run comparison; full independent 48M-round replay | Training and execution constraints change together; no convergence proof |
| A shop can sometimes improve against its frozen learned partner | All 48 response labels, dynamic programming and checked Bellman bounds | Full-information fixed-partner responses, not mutual adaptation or equilibrium |
| A visitor can inspect the mechanism | Graphical play/watch views and developer checks | No human comprehension or usability study was performed |

## Algorithms and mathematics, without novelty inflation

The market uses logit demand and consumer surplus. The guard restricts feasible
prices using immediate own profit against the rival’s last price. Finite-policy
paths are functional graphs: a transient leads to a cycle whose saved-weight
mean is computed exactly. Worst permitted cycles and interval calculations
address guarantees. The learned shops use established tabular Q-learning;
frozen-partner responses use established discounted dynamic programming.
Source snapshots, private random streams, exact arithmetic on saved binary64
weights and separately authored replay make the case auditable. These methods
are established tools, not new algorithms invented here.

## What is new relative to the starter?

The public starter already supplies replacement, checkpoint branches,
history-window controls and changed objectives; the user’s earlier game is also
prior work. Our bounded addition is the explicit guard/cap guarantee audit and
the linked, source-frozen control, sensitivity and learning comparisons. The
report credits nearby pricing, shielding, intervention and frozen-partner
response work. It makes no first-ever algorithm or broad market claim.

## Answers that should remain candid

- **Does this prove collusion?** No. High prices or a repeating frozen cycle do
  not establish intent, stable collusion, punishment or equilibrium. In the
  full-grid reference, 23 of 24 individual cycle profits exceed static Nash;
  seed 907009 Shop B is the retained exception.
- **Is the guard useless?** No. It helps every observed reference pair. The
  mathematical limitation concerns a stronger promise over all allowed paths.
- **Have the learners converged?** Not established. All 24 matched-study
  cycle-benefit endpoints and 3 of 12 new reference endpoints change between
  1M and 2M. Unchanged checkpoints alone would not prove convergence either.
- **Would an LLM make this stronger?** Only with a separately justified question
  and approved experiment. No account-backed model player or paid inference
  was used in these studies. AI coding and review assistance is disclosed.
- **Can the small viewer reproduce the science?** It opens the exact displays
  and report. Numerical reproduction needs the separately hash-bound full
  evidence archive with checkpoints and audit inputs.

See [the complete reference findings](GUARD_REFERENCE_RESULTS.md),
[independent AI review](GUARD_REFERENCE_REVIEW.md),
[developer QA and its limits](GUARD_REFERENCE_REPLAY_QA.md) and
[reproduction instructions](README.md). AI-agent agreement does not replace
external human review or predict the competition ranking.
