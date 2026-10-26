# Prospective compact matched-clock viewer contract

Status: source-only draft before new outcomes/source freeze. This is a proposed
read-only export and display contract, not a generated payload, implementation
or permission to read new Q. It follows `MATCHED_CLOCK_PLAY_BRIEF.md`; existing
V11 one-shop manual practice and its evidence remain separate and immutable.

## Gate and default

The exporter requires a current authoritative audit accepting the complete
24-run/48-checkpoint-slot inventory and exact source/input/output bindings.
Scientific values are gated per endpoint. A final endpoint needs independent
from-zero 2M replay, all 200 transcript hashes, final dense bits/counts/actors/
history/clock/windows and complete graph checks. A failed/missing 1M secondary
slot does not lock a separately accepted final endpoint. The planned twelve-pair
mean is available iff all 24 final endpoints are accepted. Missing finals give
a null planned mean. Both aggregate `fullTrainingReplay` and `replayComplete`
require all 48 checkpoint checks; they stay false on any secondary failure.
Never substitute an inventory `passed:true` for endpoint or full-replay status.

Normalized browser gate names are `meta.inventoryAccepted:true`,
`meta.independentAuditPassed:true` and `meta.audit.passed:true`: each refers to
authoritative inventory/integrity acceptance, not all 48 numerical successes.
`independentAuditSha256` and `primaryManifestSha256` are provenance labels.
Available checkpoint `replayStatus.accepted:true` is endpoint-specific; the
aggregate `fullTrainingReplay`/`replayComplete` flags keep their stricter scope.

Default is prospectively fixed: seed 907001, final 2M endpoint, both arms side by
side, actual histories and NEXT phase4. Retain that selection on negative/null
results. This display choice is not a scientific factor. No outcome-selected
best seed or attractive preview, no fresh activation phase0, no common-history
reset and no viewer training/exploration are permitted.

## Proposed top-level object (schemaVersion 1)

    meta, orderedSeeds[12], arms[2], finiteGame,
    runs[24], checkpoints[48], finalPolicyPairs[24],
    pairedRows[12], primarySummary, completePairDescription,
    resourceReceipt, scope

`meta` includes current manifest/results/index/completion/audit refs with
SHA256/bytes, primary and independent runtime/source identities, inventory audit
status, endpoint-acceptance counts, aggregate `fullTrainingReplay` and
`replayComplete`, actual replayed/matched rounds, failure counts/reasons, and
`defaultSelection:{seed:907001,checkpointStep:2000000,arms:['startup','recurring4'],
chosenBeforeMatchedOutcomeInspection:true}`. This means before NEW matched-study
outcomes; old seed907001/project results were already known when this staged
follow-up was proposed. Any browser hash strings are provenance
labels; local validation is not a replacement for the offline replay/audit.

`finiteGame` is one unchanged bound numerical table, shared by both panels:

    source:{file,bytes,sha256,indexSha256}, scenario, n,
    prices[n], capIndex, sets[n], upper[n],
    rewards:{consumerSurplus[n*n],profitA[n*n],profitB[n*n],
             quantityA[n*n],quantityB[n*n]}

Keep the exact saved JSON binary64 numeric values and original indices; never
round the policy lookup or score inputs. Browser finite sums use exact rationals
of those binary64 values. Displayed decimals may be rounded and labelled. No
new market payoff enumeration, continuum point-model payload, reward sampling
or arithmetic recomputation changes these saved tables.

Each arm defines a stable ID, ordinary-language label, five phase transitions,
which phases cap, common allocated dimensions and its unchanged guard/cap rules.
Both have `nextPhase:[1,2,3,4,1]`; startup caps only phase0, recurring caps phases
0 and4. Equal allocated memory is not labelled equal legal experience/visits.

## Runs, endpoint statuses and compact policies

Every `runs[]` entry keeps ID, seed, arm, initialization, planned 2M horizon,
execution status/failure, process/resource receipts and both checkpoint IDs.
Every planned `checkpoints[]` slot exists, including failures:

    id,runId,seed,arm,step,status,reason,
    executionSucceeded,scientificAvailable,
    receiptTiming,sourceRefs,replayStatus,
    terminal:{phase,previousIndices,capExecutions},
    trainingTail,coverage,frozen,preview128

The normalized checkpoint ID is `${runId}--t${step}`. `frozen` preserves the full
accepted graph object, including `actualTerminal.cycleMetrics.consumerSurplus`,
`transientRounds`, `cycleNodesFromStart` and per-firm `trainingSupport`.
`trainingTail.metrics` is the matching exact windowMetrics entry. Public
`reason` is the retained raw unavailableReason, without dropping failed slots.

Unavailable numerical fields are null with a reason. An accepted final endpoint
may coexist with a later execution failure, which stays visible. Do not hide a
failed 1M slot or falsely set aggregate replay flags because final results exist.
`replayStatus` exposes independently replayed rounds, matched transcript-block
counts, exact checkpoint-bit/actor/window/graph status and its failure reasons.

For each accepted final checkpoint, `finalPolicyPairs[]` carries:

    checkpointId,runId,seed,arm,available,reason,
    start:{phase,previousIndices},
    encoding:'uint8 WORLD row-major (phase,previousA,previousB)',
    states:5*n*n, policies:{A:{base64,bytes,sha256},B:{base64,bytes,sha256}}

Both arrays are WORLD-indexed: B's own/rival lookup has ALREADY been transposed
once by the offline audited exporter. Browser lookup uses the same WORLD state
for A and B and never transposes B again. Validate canonical base64 length and
decoded bytes, each original-index action and its actual arm/phase/rival mask.
Unavailable final slots retain null policy refs; do not fill them with default
zero actions. A pair of n=62 arrays is only 38,440 raw bytes; the 24 final pairs
avoid shipping dense Q/count arrays. Offline Q provenance remains bound by refs.

Only final policies are interactive in this initial compact design. Accepted
1M secondary slots may carry their own stored 128-step previews and exact graph
summaries; do not imply an unbounded interactive 1M replay without its policy
arrays. If a secondary preview is missing it remains unavailable, while accepted
final replay stays usable.

`frozen` retains the actual-terminal exact cycle/transient means and lengths,
cap-first floor scope where valid, cycle/path support and arbitrary-state graph
summary. Exact values use canonical `{numerator,denominator,approximate}` with
signed decimal integer strings and positive denominator; only exact numerator
determines signs/zero. The approximate member is a finite display convenience,
not sign authority. Do not ship every all-state cycle node if a compact summary
suffices; its full audited file/hash stays linked.

`preview128` stores outgoing phase/source history, actions, next phase and
saved reward indices for exactly 128 actual-terminal frozen transitions when
available. Prefer indices plus the one shared table over duplicated rewards.
Validate its continuity, natural clock, masks and agreement with final policies
before displaying. Its finite length never substitutes for exact eventual-cycle
statistics or a controller proof.

## Primary comparison and finite replay behavior

All twelve `pairedRows` remain in seed order, with both final checkpoint refs,
availability/reasons, exact cycle benefit for each arm and signed recurring-minus-
startup difference. `primarySummary` has planned denominator 12 and exact mean
only when all finals are accepted; no CI or significance label. A complete-pair
description must have an explicit secondary label, its own denominator/seed IDs,
and never appear in the planned-mean card. The common-scale difference chart
includes all zero/negative values and a zero line; unavailable rows are gaps
with reasons, not zero-height bars.

Normalized paired fields are `startup:{checkpointId,consumerSurplus}` and
`recurring4:{checkpointId,consumerSurplus}`, with exact `difference`, `available`
and `reason`. `primarySummary` uses `available`, `reason`, `plannedPairs:12`,
`acceptedPairs` and exact `mean` (or null). No partial subset replaces it.

The viewer begins at zero newly replayed rounds. Saved previous prices are
unearned memory. A user advances the two frozen worlds together by one or 20
rounds, with each world retaining its own history and clock. Execute both saved
actions from the previous completed state before revealing reward. Undo/restart
restore both histories, phases and exact finite ledgers. No player chooses
quotes or changes policies in this comparison; the existing V11 one-shop game
serves that different purpose. Neither panel gets a fresh cap when restarted:
restart means its saved actual endpoint.

Show per-round prices, expected purchases and both profits, with customer benefit
in that round and the exact running-prefix average separately. Use the checked
ten-expected-purchases-per-full-basket scale. Infinite-cycle means remain
separate from newly earned finite sums/averages; neither is a training resumption
or a finite-prefix proof. If one final arm is unavailable, paired step controls
lock and explain why; an accepted other arm may still show its static research
summary, never silently replace the comparison with a one-arm run.

## Scope and future ownership

Root owns live routes/navigation/report and actual native browser QA. The
game-clarity agent may own a new paired frozen-replay engine and viewer assets
after authoritative endpoint acceptance and explicit root implementation GO.
Root separately permits prospective preparation of the pure browser-compatible
paired replay engine and artificial tests before endpoint acceptance; this does
not authorize actual evidence reads, export, outcome UI or numerical execution.
The derivative/export owner should transform only accepted saved evidence,
never solve/train or modify frozen primary files. The independent referee
reviews gate and source/display semantics. No current UI or generated data is
created by this draft.

The eventual page must retain readable 320/390px controls, stacked panels,
contained scroll charts and text/pattern distinctions. Developer DOM/browser
checks are not a human comprehension study, device or accessibility certificate.
Any shared runtime/hash assurances and wrapper errors are reported truthfully.
