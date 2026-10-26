# Prospective adaptive-study summary and display contract

This contract fixes descriptive field names before outcomes. The adapter cannot
publish them until the primary run, final dependency checks and independent
checkpoint/policy/graph/probe audit pass. It performs no new training.

## Summary

`summary.json` retains `runs[192]`. Each run has:

```text
{id, scenario, controller, qInit, seed, status, source,
 checkpoints: [{step, terminalStart, trainingTail,
   frozen: {actualTerminal, freshCap, allStates},
   controllerFloor, old95Target, preview128}]}
```

`terminalStart` binds the actual step, phase and completed original-world quote
indices. `actualTerminal` is primary only for the final 2M checkpoint.
`freshCap` explicitly resets high old history and clock to phase 0 and is always
secondary. Startup-only never receives a new cap in `actualTerminal` evaluation.

Each trajectory summary retains cycle ID, transient length, cycle length,
consumer-surplus mean, both profit/price means, visited-state/action support,
same-controller floor gap and original 95% target gap. Exact saved-weight
rationals/signs and approximate display values are separate. All-state summaries
retain basin/cycle coverage, unvisited-state flags and policy-cap reachability;
they do not imply that arbitrary states were trained or occupied.

`trainingTail` keeps its fixed window length, CS/both-profit/price means,
permitted action count/fraction/span, largest-permitted-action use, actual cap
activation rate and exploration scope. Training-window means are not the same
endpoint as a frozen long-run cycle. Cap activation is not correction frequency
or economic cost. Acceptance is 100% by construction and is not called freedom.

`primaryPairs[48]` bind scenario, Q initialization, seed, selected95 and
startup-only final actual-terminal cycle values and their exact signed
difference. `primaryContrasts[4]` retain all twelve ordered seed IDs/pairs,
mean/median/range, missingness, bootstrap matrix identity and approximate marginal
95% percentile interval. No unresolved seed is silently removed. Other conditions,
checkpoints and fresh-cap comparisons remain secondary. Four strata are not
pooled as 48 independent markets.

## Browser export

The browser payload contains metadata/provenance, the two immutable finite game
tables, compact summaries for all runs/checkpoints, all primary pair/contrast
rows, and `preview128`. It omits Q tables, visit binaries and full policy arrays.

The normalized top-level interface is:

```text
{schemaVersion:1, meta,
 scenarios:[2 raw records with scenario.id/finite/cap/originalTargets],
 orderedSeeds:[12], runs:[192], primaryPairs:[48], primaryContrasts:[4]}
```

Each browser run uses `controller:{id,period}` and adds a rounded-display-only
`learningCurve:[{endStep,means:{consumerSurplus,profits:[A,B],prices:[A,B]}}]`.
Checkpoint `terminalStart` has `phase` and `previousIndices`; its step is the
outer checkpoint's `step`. Endpoint means use flat exact saved-weight ratios
`{numerator,denominator,approximate}` for consumer surplus, both profits and both
prices. Named A/B support metadata may remain named rather than positional.

Each preview retains the first at most 128 frozen-policy executions from the
actual saved terminal state, preserving its phase/clock and initial history.
Quote pairs index the saved game reward tables; plotting may read those tables
locally without new optimization. The preview is explicitly truncated and does
not estimate the full cycle mean. Exact full-cycle metrics remain separate.
Preview entries contain only `phase`, `previousIndices`, `executedIndices` and
`nextPhase`; truncation and execution-count metadata remain on the checkpoint.
Metadata independently gates the complete 192-run/384-checkpoint inventory and
passed current audit identity.

The default is prospectively fixed: base-g15-t1, zero initialization, the first
ordered seed (907001), selected95 controller and final 2M checkpoint. It is not
chosen for visual appeal or a favorable result. This presentation choice was
made before outcome inspection but is not part of the frozen scientific
preregistration. Metadata uses `chosenBeforeOutcomeInspection:true` with that
explicit scope. All other saved rows remain
selectable. A long-run floor is shown for the saved terminal phase/history,
whose cap-start envelope is checked; it is not generally a fresh-cap prefix.
Arbitrary old states remain separate graph diagnostics. The cap-first finite-
prefix guarantee is not transferred to the terminal preview.

Compact rows must be regenerated against raw audited evidence or byte-match the
fully regenerated gated summary. Declared source hashes alone cannot authorize
manually edited summary values. The export states that full training was not
independently replayed unless that separate claim is actually supported.
