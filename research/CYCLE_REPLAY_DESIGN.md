# Coordinated stress-test replay: design and data contract proposal

Prepared 26 October 2026. Design only: no existing page, game engine, report,
version-2 archive or numerical result is modified. A separate `/stress` page
should be implemented only after the audited cycle-result schema is finalized.
Field names below are proposals, not claims about files already produced.

## One plain-language question

**How low can shopper benefit go while every price follows the rule?**

The first screen must explain the setup before the controls:

> This is a coordinated stress test. An optimizer deliberately chooses both
> shops' prices while obeying the selected price filter. The replay shows a
> permitted pattern; it does not show two AI agents learning to collude.

Use "customer benefit" consistently with the existing site and define it in a
short sentence: modeled value left to shoppers after paying. Keep each shop's
profit separate. A positive sum of profits can conceal one shop doing badly.

The default page is a replay, not a new experiment. Browsing, pausing and
stepping do not train a model, call an API or collect human research data.

## Newcomer sequence

1. **Pick a rule.** Guard, fixed cap or no intervention; the market and exact
   price grid remain visible. An advanced control may change the market cell.
2. **Watch one permitted step.** Highlight the previous prices, both shops'
   permitted choices, selected prices and the two actual local-rule checks.
3. **See the repeat pattern.** Show customer benefit and both profits for the
   current step and the complete repeating loop. Compare the loop with the
   declared benchmark and the corresponding trained-agent result when matched
   data exists.

Default to a short guided explanation and a paused replay. Three concise tips
can be dismissed. Avoid requiring a mathematical term before the user can
understand the page. "Repeat pattern" can be followed by "cycle" in the details.

## Suggested screen order

### 1. Claim and provenance strip

Show the research question, coordinated-policy label, exact finite-grid label,
audit status and a link to the methods. If the data is missing, stale or fails
validation, show that no verified replay is available. Do not substitute an
illustrative animation with an apparent pass badge.

The label must distinguish:

- **Coordinated optimum:** jointly selected worst-case or profit-seeking policy.
- **Trained behavior:** an actual saved learner trace, if separately available.
- **Reference:** an analytic or numerical benchmark.

These must not share a legend that implies the optimized policy emerged from
independent self-interested learning.

### 2. Compact controls before the results

The initial view should contain the rule, objective and play controls before
historical result cards. Suggested controls:

- Market configuration, with plain labels and an expandable parameter card.
- Price rule: guard / cap / none.
- Objective: lowest customer benefit / highest combined seller profit, only
  where a certified result actually exists.
- Starting state, if multiple audited reachable starts are supplied.
- Previous step, Play/Pause, Next step, Restart; modest speed options.

Changing a selection resets the replay and clearly names the newly selected
record. Do not imply that changing a control recomputes a mathematical proof in
the browser. Hide unsupported combinations instead of showing stale data.

### 3. Large two-shop scene

Retain the site's orange shop A and blue shop B, using CSS/SVG and readable
mobile cards. Show these values outside tiny SVG text:

| Before this step | Each shop's decision | After both prices execute |
|---|---|---|
| Last completed price pair | Permitted discrete price dots; selected price | Current price pair and expected purchases |
| Price used by that shop's local check | Allowed choice count and span | Shop A profit, shop B profit, customer benefit |
| Guard tolerance or fixed cap | Local check value and pass/fail | Change from the declared reference, if meaningful |

Use a visual arrow from the **previous rival price** to each guard test. The
guard does not inspect the simultaneous rival quote. A coordinated optimizer
can plan both quotes in advance; this does not alter simultaneous market
timing or require one shop to observe the other's just-submitted quote.

Draw allowed grid prices as distinct dots, not as a filled continuous band.
A span can include gaps: cardinality and endpoint span are different measures.
The old human challenge has continuous price entry and must remain explicitly
separate from this finite-grid stress test.

Shopper icons represent expected model purchases, not human subjects. The
caption must explain fractional demand. Show each economy's actual unit cost;
do not inherit the old challenge's fixed cost of one for every calibration.

### 4. The repeating loop

Use a compact ring or sequence of price-pair nodes with the current node
highlighted. For long loops, use a scrollable sequence and current-step card
instead of illegible small nodes. Show a loop-completion arrow and count.

**A self-loop is a valid result.** If the certified optimum keeps one price
pair forever, show "one-step repeat pattern" and constant lines. Do not invent
oscillation or omit an optimum because it is visually less dramatic.

If there is an entry path into the loop, draw it in a separate muted section.
Label entry steps and repeating steps separately. A global optimum that is not
reachable from the selected starting state must not be replayed as reachable.

### 5. Three small, aligned charts

1. Price A and B over displayed steps, with the exact grid extent.
2. Customer benefit, with a separately labeled competitive reference.
3. Profit A and B, shown individually on a common profit scale.

Use independent panels rather than an unexplained dual axis. Mark the boundary
between the entry path and the loop. Show current-step values and loop averages
in different locations so a user cannot mistake one favorable step for the
long-run result. Do not present repeated replay loops as new samples or new
experimental rounds.

### 6. Four-result summary and explanation

Show the certified recurrent customer-benefit bound, attained loop mean, each
seller's mean profit and number of permitted choices. The maximum-joint-profit
replay should show its resulting customer benefit rather than inheriting the
minimum-CS label.

Suggested explanatory questions:

- "Did every chosen price follow the local rule?"
- "How much benefit did shoppers receive over the repeat pattern?"
- "Did both shops earn more than the reference?"
- "Did the tested learners reach this pattern?" Answer only from matched saved
  learner evidence; otherwise state that discovery was not tested.

There is no generic "safe" badge merely because local checks pass. If the
research declares a customer-benefit floor, show that target and its actual
guarantee separately. A lagged profit-loss test is not calibrated regret or a
legal finding of non-collusion; see [CYCLE_NOVELTY.md](CYCLE_NOVELTY.md).

### 7. Evidence drawer

Provide an exact row ledger, full-precision JSON download, graph/certificate
metadata, allowed-action definition, reachability scope, numerical tolerance,
source hashes and independent audit result. The ordinary view can round prices
but must say so. A tiny nonzero change should not be described as exactly zero.
Keep technical details in this drawer rather than turning them into required
onboarding steps.

## Proposed minimal replay record

The final engine schema takes precedence. The renderer should consume a
read-only export derived from audited records, with an explicit schema version.
One useful separation is metadata / benchmarks / entry path / loop /
certificate / matched learner comparison.

```text
schemaVersion
recordId
model:
  economyId, quality, cost, mu, buyers, outsideQuality
  priceGrid[]
  timing = simultaneous; guardReference = previous executed rival price
rule:
  type = none | cap | guard
  epsilon?, capIndex?, capPrice?, coverage
objective:
  type = minConsumerSurplus | maxJointProfit
  individualProfitConstraints?  // absent means none, not silently satisfied
scope:
  startState, reachableOnly, reachableStates, graphStates, graphEdges
  globalOrStartSpecific, finiteGridOnly = true
entry[]:
  fromState, toState, executedIndices, prices
  allowedIndicesA[], allowedIndicesB[]
  localLossA?, localLossB?, checkPassedA, checkPassedB
  consumerSurplus, profitA, profitB, quantitiesA, quantitiesB
cycle[]:
  same step fields; last toState equals first fromState
cycleSummary:
  length, meanConsumerSurplus, meanProfitA, meanProfitB
  meanAllowedCountA, meanAllowedCountB, meanAllowedSpanA, meanAllowedSpanB
benchmarks:
  namedReference, prices, consumerSurplus, profitA, profitB
certificate:
  independentAuditPassed, sourceHashes, resultHash
  boundLower, witnessUpper, maxEdgeResidual, numericalTolerance
  reachabilityVerified, everyCycleEdgeVerified
matchedLearnedComparison?:
  sourceStudy, configuration, protection, updateMode, explorationRate
  window, independentSeedCount, metricSummary, comparabilityLimitations
```

For a maximum-profit objective, certificate fields must identify which scalar
quantity is bounded. Do not reuse `boundLower`/`witnessUpper` display wording
without accounting for whether the objective is minimized or maximized.

If proposals are included, distinguish them from executions. A graph over
feasible executed pairs can choose the executed price itself as the proposal
under a retraction-style filter, mechanically obtaining full acceptance.
The replay should not celebrate that bookkeeping choice as an autonomy result.

## Validation before rendering

The independent numerical auditor owns scientific correctness. The UI additionally
checks structural consistency so malformed or mismatched files cannot create
a misleading replay:

- Every numeric value is finite and every index lies in the declared grid.
- Each row begins where the preceding row ended; the loop closes exactly.
- The selected entry path reaches the loop from the declared start.
- Each executed index belongs to that shop's supplied allowed set.
- Reported means agree with the displayed loop rows within the declared
  tolerance; entry rows are excluded from recurrent means.
- The objective, rule and model identifiers match the selected record.
- An asserted audit pass has corresponding provenance and matching identifiers.

These browser checks are defensive display checks, not an additional independent
scientific proof. A signed or hashed file identifies a frozen artifact; a hash
alone does not establish that its scientific contents are true.

## Accessibility and developer checks

Use semantic buttons and labels, visible keyboard focus, keyboard step controls,
and text alternatives for every plot and price-state graphic. Start paused and
honor reduced motion. Avoid broadcasting every animation frame through an
ARIA live region; announce deliberate step changes and selection changes.

At 320/390-pixel widths, switch to two readable shop cards and stacked charts.
Keep the ledger horizontally scrollable within its container. Check touch-sized
controls, no document overflow, selected-record reset, self-loop rendering,
multi-step loop rendering, entry-path separation, missing/failed-audit state,
keyboard navigation and correct loop averages. Save desktop and narrow
screenshots once an implementation exists.

No independent human comprehension result should be claimed from these checks.
A genuine newcomer study, if later authorized, needs actual participants and
recorded questions; no developer or AI-agent inspection can substitute for it.

## Implementation boundaries

- Create a separate page and assets after the data contract is final; preserve
  existing `/challenge`, `/study` and version-2 files.
- Extend a route only with the manager's go-ahead. Reuse established CSS/SVG
  visual language; no paid image generation, APIs or inference players.
- Use audited saved data. Do not simulate an impressive result in the renderer.
- No uploads, external analytics, hidden research-participant collection or
  public publication is needed for a local replay.
- Link to the original human game and explain its continuous-price distinction.
- Keep the no-collusion-intent, no-emergence and finite-model qualifications
  visible near the claim, while moving implementation detail to the evidence
  drawer.
