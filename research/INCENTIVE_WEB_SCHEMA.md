# Goal 6 descriptive and human-challenge interface

This is an adapter contract, not a substitute for numerical evidence. The export is blocked until
the primary manifest, complete journals/results/index, current independent auditor
and all transitive inputs are bound by a passed independent receipt. No DP search
is performed by the descriptive analysis or graphical exporter.

## Identities and quantities

The summary retains `rows[8]`, each with `scenario`, original `economy`, physical
cap identity and `periodSlots[3]`. A period slot carries `slotId`, imported `K`,
`duplicateOf`, period-source identity and its separate finite welfare certificate.
It contains `focalSellers.A` and `.B`, each with two discount comparisons keyed by
`19/20` and `0/1`. There are exactly 96 retained comparison labels, including
duplicate slots and failures. They are deterministic labels, not statistical
replicates.

Every exact rational is represented by decimal-string `numerator` and positive
decimal-string `denominator`, optionally accompanied by an explicitly approximate
display value. Exact integer signs determine positive/zero/negative labels;
display rounding cannot convert a positive gain to zero. A relative gain is null
when its baseline value is nonpositive.

Each comparison retains its status/failure, source-record identity, exact cap
baseline and optimal finite-block values, separate infinite discounted values,
exact gains, all baseline-path phase diagnostics, last-guard screen (or the K=1
cap screen), and baseline/optimal full-block replay traces. Each phase diagnostic
retains phase/prior state, prescribed and optimal quote indices, immediate gain
and finite/infinite baseline/optimal values and gains. Zero findings remain rows.
Saved binary argmax policies are referenced by path/hash/length rather than
duplicated into the compact graphical data.

The welfare panel retains exact both-upper cycle and minimum nonempty-prefix
customer-benefit means and all five original fixed-target comparisons. It does
not infer finite-mesh 95% protection from the source of the imported continuous
period. Discounted private profit and undiscounted customer-benefit averages
remain different quantities.

## Flat and compact views

The analysis also exposes `records[96]`, `phaseRows`, `screenRows` and distinct
`welfareRows`, with original context on every row. Summary `counts` report exact
sign/status counts and duplicate counts, never significance or convergence.
Unresolved labels are retained with null unavailable values and explicit failure.

The later compact graphical payload carries `meta` with the exact evidence/source
hashes and passed audit identity, plus these same eight grouped rows. It must be
regenerated read-only from raw independently audited evidence (or byte-match the
fully regenerated descriptive summary), so manually edited compact rows cannot
pass merely because their declared input hashes still match.

## Implemented playable export

`build-incentive-web.js` writes `incentive-results/web-data.json` with
`{schemaVersion, meta, periodSlots[3], discounts[2], records[8]}`. Each record keeps
the full original finite numerical game, adds `comparisons[12]`, and replaces
`finite.certificates` with its distinct new-period compatible certificates. Each
certificate's exact cycle and minimum-prefix mean, path and minimizing prefix
are checked against the independently audited welfare certificate. This is
presentation conversion, not a new optimized welfare controller.

Select a comparison by `slotId`, `focalSeller` and `discountId`. It carries `cap`,
`phases`, `screen`, `baselineBlockTrace`, `optimalBlockReplay` and original source
references. The directly usable `comparison.challenge` contract is:

```text
{period: K, focal: 0|1, discount: {numerator,denominator},
 optimalBlockProfit: exactRational, baselineBlockProfit: exactRational,
 capAction: integer,
 phasePolicies: [{phase, actions: Array(n*n), source:{file,sha256,bytes}}]}
```

Every actions array is copied from the audited saved unsigned-byte policy file.
Its focal-row-major index is `previousOwn*n + previousRival`. There is no browser
optimization or model player. `createProfitChallenge(record, challenge)` compares
the exact human discounted block profit only after all K actual executions.
The full-block optimum must not be presented as a partial-block performance gap.
The separate welfare panel remains active during play. Optional stored-action
hints are a deterministic coach, not a language model or a learned opponent.

## Presentation scope

The opponent remains the specified public deterministic upper script after a
deviation. A positive gain rejects only that script's best-response optimality
at the stated phase/discount against this fixed opponent. A zero recorded gain
does not establish a general equilibrium. Gamma=0 at cap cannot hide later-phase
incentives; the complete phase view and elementary last-guard explanation must
remain visible. Any individually profitable permitted deviation remains covered
by the separate all-policy welfare certificate. No learned collusion, empirical
market behavior, human validation or general controller optimum is claimed.
