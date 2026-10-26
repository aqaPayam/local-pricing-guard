# Independent prospective review and audit plan: mixed cap timing

Status: implementation and artificial-test design accepted conditionally; no
inherited-market numerical execution is authorized. This file is outside the
frozen Goal7/V9 payload. No accepted scientific source, report, audit or archive
was changed for this review. The referee read the new protocol and theory in
full, and read only source code of the closed arithmetic auditors to assess
reuse feasibility. No new inherited-market record was opened or calculated.

The earlier `MIXED_TIMING_CONCEPT_REVIEW.md` supplies the independent proof and
clearly artificial examples. This review checks the proposed numerical study
against that proof; it is not a claim that the implementation already passes.

## Verdict and one required clarification

The proposed 40 finite plus 80 continuous labels, inherited absolute targets,
fixed physical caps and complete exceptional-status inventory are appropriate
for a bounded follow-up. The largest-safe/strict-next-failing frontier, partial
final gap in Jensen's argument, attained causal upper-price response, and exact
funded calendar resolve the main conceptual risks. The theory establishes a
restricted minimax frequency result under a strong every-realization promise;
it does not establish a generic new scheduling algorithm or new behavior.

Before source freeze, distinguish exact rational rate endpoints from outward
decimal displays. Treat aL/aU/bL/bU as exact rational values and compute

    lower = 1/(K+p(aU,bU)), upper = 1/(K+p(aL,bL))

as exact rational expressions. The lower-credit calendar has rate exactly
`upper`; its outward-rounded decimal upper display may be strictly larger.
Do not assert exact equality to that rounded display. Store both exact rational
endpoints and outward decimal displays, or state the weaker display inequality
unambiguously. This is a numerical representation clarification, not a change
to the minimax proof. A synthetic test must exercise strict outward rounding.

## Proof audit

The restricted family announces cap or full guard before prices, cap A is
attainable, and guard supports attain a nondecreasing maximum U. Together with
coordinate-decreasing customer benefit, this makes the repeated upper-price
response causal and simultaneously adverse at every age after each cap. Its
nonincreasing rewards r_j make the piecewise-linear sum S concave. A controller
depending on observed history or randomization still faces this same feasible
response along each realized sequence of announced modes.

At any horizon T, m executed caps partition T into exactly m positive gap
lengths, including the last partial gap and its executed cap. Thus protection
and Jensen imply F*T <= m*S(T/m). For C_star<F<=r0, the largest nonnegative
crossing K+p bounds T/m. This gives a finite-horizon rate lower bound on that
one adverse path, hence the necessary worst-path limsup lower bound. It does
not require the same cap frequency on cooperative paths.

For the constructive calendar, bounded rational credit B chooses a long gap
only when its entire endpoint debt is funded. The actual within-block excess
is concave in the executed prefix length, so its minimum lies at an endpoint.
Funding the negative endpoint protects every interior prefix as well. Bounded
credit then identifies the asymptotic long-block fraction without an ergodic
assumption or enumerating a potentially enormous rational repeat period.

The result is asymptotic frequency optimality, not a smallest-cap-count theorem
at every finite horizon. Its guarantee is measured from the actual activation
cap, not each sliding window, individual execution or restarted block. The
adverse response need not be profit-optimal or incentive compatible.

The interval rate direction is correct: p increases with both a and b on the
declared sign domain, while the rate decreases with p. Conservative lower
credits produce a feasible calendar and an upper bound on the unknown optimum.
A nonzero enclosure width must not be presented as exact continuous optimality.

## Novelty and useful outcome

The application should cite close prior work prominently. Two-threshold
randomization for discrete rate-constrained monotone-age problems is already
explicit in [Sun and Cyr, Theorem4](https://arxiv.org/html/1812.07241). The
uniform-time baseline constraint also predates this project in
[Wu et al., Conservative Bandits](https://proceedings.mlr.press/v48/wu16.html),
and [Du et al.](https://ojs.aaai.org/index.php/AAAI/article/view/16891) expressly
study sample-path constraints on actually received rewards. No priority claim
for adjacent mixing, renewal optimization or generic funded prefixes is justified.

The plausible addition is the pricing-envelope reduction and a checked,
model-specific frequency comparison with the old physical cap held fixed.
An exact zero or small saving is informative: p/(K+p)<1/(K+1) already limits
how much integer-period rounding alone can explain for large K. The study
should not displace the main report's clearer limitations and learning evidence.

## Required schema and boundary tests

1. Retain all120 planned identities, including duplicated targets, nominal and
   effective records, pre-case errors, and unmet model assumptions. Rates for
   infeasible, unavailable or unresolved records are null, never numerical zero.
2. Preserve exact imported F, requested target/margin, cap price/quote identity,
   and numerical-game versus exact-continuum interpretation. A cap-start orbit
   limit cannot be replaced by a global arbitrary-old guard-cycle floor.
3. Record the bounded frontier's queried lengths. A sentinel test must reject
   any request above65536, including a next-failure request at65537. Censoring
   gives a feasible fixed schedule and outer bound, not an exact optimum.
4. Keep exact equality separate from enclosure overlap. F<=C_star startup-only
   has one actual cap and zero limiting frequency; F>r0 fails at execution1;
   F=r0>C_star uses the whole finite initial plateau. Constant rewards belong
   to the startup-only case. U(A)<A is an unmet premise here.
5. For overlapping signs retain the best certified safe/failing bounds and a
   certified fixed-safe fallback where available. Do not infer an adjacent
   pair or invent an equality. A possible a=0 does not certify positive saving.
6. Store boundary credit separately from within-block cumulative-prefix excess.
   Boundary credit updates at a completed block; partial execution rewards are
   earned immediately. Preview clocks and partial final gaps need explicit tests.
7. Store all64 exact block decisions independently of the limited execution
   preview. A first long gap beyond that preview is legitimate. The preview's
   observed cap ratio is not the analytically proved limiting rate.
8. Test a=0, b=0 rejected as failure, K=1, B=-b choosing long, plateaus, negative
   artificial rewards/targets, very small positive a, huge rational periods,
   interval-rate orientation and strict display rounding. Include unfunded iid
   long-gap and false unweighted per-gap-mean counterexamples.
9. For small legal artificial games, independently enumerate every feasible
   execution prefix over bounded horizons and compare the claimed lower bound.
   Do not relabel artificial examples as inherited economic outcomes.
10. A phase-Q table from the old clock is incompatible with this credit state;
    no saved learner replay or new behavioral claim is part of this study.

## Independent auditor plan

Use a new JavaScript BigInt rational implementation for finite inputs and all
timing, frontier, mixture, exact-credit and preview logic. It must not import
the primary Python timing/search/calendar functions. Binary64-to-rational
conversion must independently handle sign, normal/subnormal exponents, zero
and malformed nonfinite values. Arithmetic tests should include unequal
denominators and tiny positive differences that round to zero in a short display.

For continuous checks, a new Python helper may use the frozen independent
130-digit interval/model backend. It must independently check the saved root
signs, inherited orbit/tail premises, relevant sums and frontier signs rather
than trusting a passed flag. New control and rate logic remain independent of
the primary80-digit code. The shared Decimal transcendental backend and reuse
of accepted model arithmetic must be disclosed; this is not formal verification
or independence of numerical libraries.

The auditor will bind live source/input hashes, model-record identities,
manifest/results/index/completion, all started/finished journals and all120
slots. Finite checks cover full saved payoff/mask support, upper-map monotonicity,
reward-coordinate monotonicity, the cap-start orbit, exact constant tail sums,
frontier and rates. Continuous checks validate signed enclosures and exact
lower-credit construction. Neither a passed inherited receipt alone nor a
finite preview proves the new controller theorem.

The required corruption controls alter a target or cap; substitute an old
global floor; omit a duplicate; move one reward across a partial-gap boundary;
permit an unfunded long gap; change the tie decision; reverse rate bounds;
report a conservative continuous rate as exact optimum; round a tiny positive
saving to zero; or turn censoring into exact optimality. Each rejection must
come from the relevant scientific check, with hashes recomputed where needed
so a superficial hash mismatch is not the sole negative-control mechanism.

Freeze the final auditor and synthetic tests before its first real case read,
and record the actual timing. This review is not that source freeze. The audit
must support read-only verification and an optional output path, preserving
closed original receipts on re-verification. Any primary failure or unresolved
status is retained; a passed audit means the record is honest, not necessarily
that every numerical label resolved.

No numerical GO is given here. After the representation clarification and
synthetic/source review, root must separately confirm the distinct active goal,
accepted V9 archive, source/input freeze and authorization to execute cases.

## Clarification closure before implementation

The primary author applied the requested rational/display distinction and added
the query sentinel, partial-prefix fields and retained-pre-case-failure tests
to the prospective protocol. I inspected these changes in both documents.
The reviewed current protocol SHA256 is
`798cf545b7d87228a2a511c002cf4330cbe8ff142d87d5241fa956df914ba161`;
the theory SHA256 is
`0d5c7f389adae4311ea131c47d15f73fc1268260b46e708f1980c942f2a98b73`.

The representation issue is closed at the specification level. Source code,
synthetic results, complete schema and independent cross-checks are still
required before any numerical execution GO. Approval remains for preparation
only, with no inherited-case calculation or alteration of frozen V9 evidence.

## Final prospective source gate

The primary numerical implementation, runner, complete schema and tests were
subsequently reviewed. The independent implementation is now complete in
`audit-mixed-study.py` (authoritative driver), `audit-mixed-timing.js` and
`audit-mixed-continuous.py`; its four test files are
`mixed-timing-audit.test.js`, `test_mixed_continuous_audit.py`,
`test_mixed_timing_cross_audit.py` and `test_mixed_audit_driver.py`.
The primary source inventory binds all seven files before cases.
The cross-language test treats the primary as an object
under test on artificial sequences; the production auditor does not import
primary timing/search/calendar code.

The final synthetic inventory is44 tests:27 primary Python,10 independent
JavaScript,3 independent interval Python,1 complete-record cross-language
test and3 driver/orchestration/preservation tests.
The cross-language test checks seven artificial complete target records and rejects
scientific mutations of clocks, credits, rates, signs, censoring and interval
exactness. Tests use no inherited model outcomes. Finite tests also exhaust
small legal-game prefixes, and the interval tests verify an analytic contraction
tail rather than treating the last of64 rewards as a constant limit.

Two additional prospective issues were fixed before execution: recursive
dependency closure now supports the old manifest schema with no inputHashes,
and failures retain known target/duplicate identities and failed query attempts.
Declared scientific source/input maps are checked recursively, with conflict
and visited checks. Historical oldCheckpointHashes are administrative references,
not newly required timing-model inputs. Explicit old continuum/initializer audit
bindings establish the accepted global theorem premises. The new helper does
not independently recompute those global premises or q_star/C_star/rho proofs:
it reuses their accepted immutable certificates and independently checks128
scalar-root signs,64 propagated prices/rewards per model and every used sum.
That scope is explicit in its receipt, including
`inheritedPremiseRevalidation:false` and the shared Decimal backend limitation.

Root authorized pre-outcome administrative schema/hash inspection after V9
delivery. The primary owner reported a successful inventory-only check of113
dependency files, with the accepted V9 receipt/archive identity verified. No
envelope, timing sum, new target, calendar or outcome was calculated for that
administrative inspection. This referee's review and tests likewise opened no
inherited numerical-market record. Do not mislabel the inventory inspection
as a new scientific result.

The sandbox rejects Node-to-Python child execution, so the authoritative Python
driver freshly computes continuous checks in-process and invokes the JS
component via stdin. Artificial orchestration verified this direction with128
fresh scalar certificates and complete proposed target records. JS-only output
has passed:false and requiresOrchestrator:true. Only the driver can produce the
full acceptance receipt after both computations; no saved unchecked bridge is
accepted as a substitute. The receipt binds driver/control/helper/backend
sources separately. Default verification is read-only. Optional receipt output
uses exclusive creation and refuses to change an existing closed receipt.

The read-only independent adapter binds all24 models/120 labels, all records,
queries, block decisions, exact/interval rates and ancillary signs, every
preview execution/history/mode/clock/reward, source snapshots and journals. It
distinguishes honest complete failures from successful primary execution, and
checks resource flags without claiming continuously sampled peak memory.
Corruption tests check scientific fields rather than relying solely on hashes.
Its optional output path preserves read-only verification by default.

The analysis/display contract was reviewed, including its separate40/80
populations, strict statuses and prescribed presentation default. Its final
pre-freeze hash is
`d5d95871d4b38182dde8334e25a39de3a62cf6c846095c2aed572e458bc3fae5`.
The first-long diagnostic is valid: for a>0,b<0 the initial short-block count
is n=ceil((-b)/a), and the first long block starts at execution n*K+1. Before
that boundary credit is j*a; minimality follows from (n-1)*a<-b<=n*a. Large
integer times must remain exact strings. This does not authorize old-Q replay.

The specification/source gate is accepted for freeze. Numerical execution
still requires root's explicit GO after the distinct active goal and immutable
source/input manifest are confirmed. This prospective review must itself remain
immutable after that freeze; later results and presentation feedback belong in
a new `MIXED_TIMING_REVIEW.md`.
