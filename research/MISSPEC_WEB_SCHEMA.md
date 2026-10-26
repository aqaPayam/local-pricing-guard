# Compact calibration-error presentation schema

Prospective adapter contract; no sensitivity outcomes or numerical certification
are part of this document. Export only after the independently audited primary
manifest/results and current source hashes match exactly. Primary evidence stays
in `misspec-results/records/` and `results.json`; compact fields do not replace it.

The web payload has `meta`, `levels[4]`, and `rows[8]`. Exact interval endpoints,
targets, displacements and radius endpoints are decimal **strings**, not rounded
numbers used to decide safety. Approximate plotting coordinates must be labeled
as display values. Only four declared levels may select certified views.

```text
meta: {
  primaryManifestSha256, primaryResultsSha256, independentAuditSha256,
  sourceHashes, primaryAudit, scope, provenance
}
levels: [{id, dExact, numerator, denominator, units}]    // 0, .001, .01, .05
rows: [{
  scenario: string, economy: object, physicalCap: object,
  effective: ModelView, nominal: ModelView
}]
ModelView: {
  status: string, actualDemand: string, nominalEnforcement: object,
  targetGroups: [{
    label: string,
    requestedExact: string | null, thresholdExact: string | null,
    targetIdentityAvailable: boolean,
    d0ReproducesClosedSelection: boolean,
    policySlots: [{
      slotId: "guard-only" | "closed-selected" | "permanent-cap",
      available: boolean,
      policyKind: "guard" | "periodic" | "unavailable",
      period: integer | null, startupCaps: integer | null,
      duplicateOf: slotId | null,
      frequency: {lower: string, upper: string} | null,
      singleStartupCapVariant: object | null,
      radius: {
        status: string, safeSet: string | null,
        lower?: string, upper?: string,
        censoredLowerBound?: string,
        simpleSufficientLower?: string,
        source: object
      },
      levels: [{
        dExact: string, status: string,
        surplus: {lower: string, upper: string} | null,
        reserve: {lower: string, upper: string} | null,
        finiteActivationAverageFromArbitraryOldPrices: boolean | null
      }]
    }],
    robustPeriods: [{
      dExact: string, status: string,
      largestPeriod?: integer | null,
      certifiedSafePeriodLowerBound?: integer,
      certifiedFailingPeriodUpperBound?: integer | null,
      source: object
    }]
  }]
}
```

Mapping from the prospective primary schema: `targets` becomes `targetGroups`;
`policies` becomes `policySlots`; `slot` becomes `slotId`; `sensitivity` becomes
`levels`; `dbar.exactDecimal` becomes `dExact`; `startupCapCount` becomes
`startupCaps`; `actualThresholdExact` (or exact imported actual threshold) becomes
`thresholdExact`. Other scientific statuses and enclosures are copied verbatim.
When a target identity is unverified, keep its slot with null target fields and
`targetIdentityAvailable=false`; the page must show unavailable evidence rather
than inventing a threshold or suppressing the row.

For a certified radius, copy `radiusEnclosure.lower/upper`. If the nonnegative
safe set is empty because the policy already fails at zero, omit radius endpoints
and say **already below target at zero**; do not draw an ordinary zero-radius
safe interval. Certified exact zero, unresolved overlap, unavailable policy and
censored lower bounds remain distinct states. `duplicateOf` points to an earlier
slot for this same model/target; repeated cards are comparison slots, not new
independent evidence. A guard-only policy has no recurring cap and zero startup
caps; its single-startup-cap variant retains the different finite-average scope.

The primary exact demand change is inside quality minus `d*mu`, outside quality
fixed. The deployed nominal guard, physical cap, public clock and original
absolute target stay fixed. The chart must not lower the target or recalculate
the old finite game's rewards under its former certificate. Robust-period rows
are separately calculated timing choices for a **known bound** on calibration
error, not adaptation to observed demand or an optimum over all controllers.
