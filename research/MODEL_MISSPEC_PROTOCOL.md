# Prospective demand-misspecification study

Status: protocol proposal before any new alternative-demand case calculation.
Requires independent mathematical/code review, a distinct active goal, synthetic
tests and frozen sources/inputs before execution. Older primary sources,
results, reports and archives remain immutable.

## Discriminating question

How much downward error in actual demand quality can the already selected
recurring-cap policies tolerate while maintaining the SAME original absolute
consumer-surplus target? Does a more frequent cap restore a guarantee at
predeclared uncertainty levels, or is the inherited physical cap itself
insufficient? The study can falsify practical calibration robustness. It does
not test autonomous collusion, learn a demand model or invent a new controller.

## Fixed deployed enforcement and alternative demand

Use all eight inherited scenario labels and both effective/nominal exact-real
enforcement semantics, with effective primary and nominal declared sensitivity.
Verify the closed recurring, continuous, finite initializer and independent
audit/source/input bindings before reusing any quantity.

Enforcement remains the original EXTERNAL nominal guard U_hat, the same
physical inherited cap, phase clock, price domain and comparison semantics.
It does not update to the actual demand model. Actual quality minus outside
quality instead falls by d*mu for fixed unknown d>=0: inside product quality is
lower, and outside quality stays fixed so the welfare baseline does not move.
Buyers B, taste scale mu
and all other actual parameters remain unchanged. Report d as a dimensionless
taste-scale displacement, not as a percentage error in total quality or as an
empirically plausible confidence interval.

Use C_d=B*mu*log(1+exp(-d)*S_hat) from MODEL_MISSPEC_THEORY.md.
The old enforced price orbit, q_star, rho and A<q_star premise stay fixed. Refit
neither enforcement nor the cap when varying actual demand. This models an
incorrect demand calibration in a fixed deployed mechanism. Unknown guard
execution, uncertain mu, other demand families or time-varying errors are
outside scope.

Keep all forty original requested targets and exact imported actual F-delta
thresholds. Across sixteen model semantics there are eighty target labels,
not eighty independent experimental markets. Do not lower F along with demand
or redefine it as a fraction of a new actual competitive benchmark.

## Primary robustness-margin comparisons

For EACH of the eighty target/model labels, retain three policy slots:

1. The unchanged nominal guard's worst long-run floor C_star(d), with zero
   startup caps. Also disclose the single-startup-cap variant and its finite
   activation-average meaning; the numerical floor is the same.
2. The policy selected in the CLOSED recurring study: its certified largest
   integer K at d=0, or the zero-recurring-cap policy for an already-met target.
   Do not select a more favorable K after inspecting the new alternative demand.
3. Permanent activation of the exact same physical cap, K=1.

Preserve repeated policy slots when a selected policy equals a baseline; mark
them as duplicates, not additional independent evidence. These are at most240
model/target/policy rows. Retain the originating status if an inherited choice
is censored, unresolved or family-infeasible rather than inventing an optimum.

For each available policy compute a directed enclosure of its nonnegative
break-even downward-error radius d_crit at fixed F. First classify d=0 as
certified safe, already failing, exact zero reserve only when certified, or
unresolved overlap. A failing-at-zero policy has an EMPTY safe nonnegative set,
not an ordinary positive or zero safe radius. Keep all statuses and reasons.

For a positive crossing, require a certified safe lower displacement and a
certified failing upper displacement, with normalized bracket width<=1e-20.
Predeclare displacement search ceiling d=8; no evaluation above8. If the
ceiling remains safe, report a censored lower bound>=8, not an exact radius.
Retain overlap when the inherited price/tail uncertainty prevents the required
signs. Equality is a mathematical boundary, not something to erase by a target
adjustment.

Permanent-cap and guard-floor roots have the stationary closed form in the
theory note; independently cross-check signed welfare evaluations there.
Finite-period roots require independently signed monotone endpoint brackets.
Also report the conservative nominal-reserve/(B*mu) sufficient radius where
positive, so the tight calculation is compared with a simple check.

## Predeclared uncertainty and frequency/reserve comparison

Use EXACT rational dimensionless uncertainty bounds

    d_bar in {0, 1/1000, 1/100, 1/20}.

These four levels are illustrative sensitivity assumptions, not observed error
rates. For unknown actual fixed d in [0,d_bar], evaluate the lower-welfare
endpoint d_bar. For the three fixed policy slots report the surplus enclosure,
reserve G(d_bar)-F, target certification status and cap activation rate/startup
count. Do not call a confidence interval or sample-based risk estimate.

As a separately declared design comparison, compute the largest safe fixed
integer period of the SAME inherited physical cap at each d_bar for all eighty
model/target labels (320 derived comparisons). Use the original period ceiling
65536 and never evaluate65537. A maximal period requires certified safe K and
certified failing K+1; ambiguity retains a certified integer bracket. Keep no-
recurring-cap, K=1, fixed-family-infeasible and censored/unresolved cases.
This compares frequency needed for a KNOWN bound on calibration error. It is
not adaptation to observed actual demand and not a globally optimal controller.
The d_bar=0 rows must reproduce the closed recurring classifications/boundaries.

## Arithmetic, independence and falsification checks

Use directed interval arithmetic at least80 decimal digits. Reuse only hash-
bound certified old price intervals, orbit terms, q_star and rho. Recalculate
actual C_d and all new controller/target logic in new files; no old outcome may
be overwritten. For K>64 retain the validated uniform geometric price tail,
not simulated rewards or an unexplained exact limit replacement.

The independent auditor must implement alternative-demand/selection/radius
logic separately from the primary implementation. It may reuse the frozen
independent130-digit arithmetic/model backend with explicit hash dependencies.
Disclose the shared standard Decimal backend; this is not formal verification
or arithmetic-library independence.

Before freeze, synthetic tests must discriminate: d=0 reproduces nominal
welfare; welfare decreases with d; stationary closed-form crossings agree with
separately evaluated signs; actual rewards stay ordered along the fixed orbit;
finite cap-first prefixes respect their floor; already-failing and boundary
overlap cases remain honest; robust K decreases or becomes unresolved as d_bar
increases; family infeasibility does not imply no other possible controller.
Test tail indexing and retained uncertainty with an exact/simple oracle.

Independent actual-data checks must verify all original target identities,
unchanged enforcement/cap/orbit provenance, every radius sign bracket, all
stationary closed-form checks, every reserve/target row and every safe/next-
failing period pair. Test corruptions of actual-versus-enforcement model identity,
shift sign/units, target scaling, radius bounds and period/frequency claims.

## Reporting and execution discipline

Retain all labels, duplicate policies, unresolved conditions and failures with
exact constants, primary source/input hashes, per-record journals and a final
dependency recheck. Refuse overwriting partial or closed outputs. Resource
targets are30minutes and sampled RSS<250MB; report an overrun without dropping
a case. No model players, new learner training, paid services, API use or
external submission.

Report safe margins and failures together. Near-100% fragility may be mechanical:
the original target already consumes nearly all of the cap's modeled welfare,
and lowering actual demand reduces that welfare. Do not portray this expected
calibration-budget effect as a new emergent mechanism. A useful result is the
verified comparison of inherited sparse timing, always-cap and guard-only
protection, plus an explicit statement of what demand uncertainty is STILL
unaddressed. This is a sensitivity/conditional robustness study, not empirical
validation or a guarantee for arbitrary model misspecification.
