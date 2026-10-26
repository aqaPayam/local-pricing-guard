# Prospective continuous-price and mesh-refinement study

Status: protocol proposed before new numerical scenario evaluation. The reviewer
must approve the implementation and a source/input-hashed manifest must be saved
before executing the primary cases. This is a new stage; Goal 1/2 remain frozen.

## Question and discriminating outcomes

Does the finite-grid handover protection persist when sellers can choose any
price in the same interval? Can the continuous worst long-run customer benefit
be established from every starting state, and how do discrete worst outcomes
change as the grid is refined?

An initialized finite grid can genuinely satisfy its own certificate while
failing to approximate a continuous guarantee. We will retain either result.
We will not describe a deliberate adversarial path as learned collusion,
incentive compatibility, or evidence that real firms follow that path.

## Fixed inputs and comparisons

Use all eight scenario labels from the frozen cycle guard cases. Import their
economic parameters, tolerance epsilon and first/last prices without changing
their original data. Preserve all labels, including economically equivalent
cases and grid-size variants; do not call these independent economies.

The continuous domain is the closed interval between those saved endpoint
prices. Economic constants, endpoints, epsilon, and saved comparison thresholds
are interpreted as the exact values of their imported binary64 numbers, using
exact integer-ratio/Decimal.from_float conversion in validated arithmetic.
Record both the original decimal serialization and the exact conversion.

Primary continuum: effective payoff tolerance epsilon + 1e-12, with the addition
performed as exact real addition of the imported constants. This carries the
existing implementation's declared comparison allowance into the comparison
model. Record exact epsilon, the exact binary64 literal allowance1e-12, their
exact-real sum and the separately rounded JavaScript fl(epsilon+1e-12). This
continuum is a declared mathematical comparison, not a literal replay of
floating profit, subtraction or comparison operations.
Also evaluate the nominal epsilon continuum as a declared sensitivity
check, never silently replacing one by the other. Neither continuum claims to
reproduce every floating operation of the old engine.

For each scenario compare both continuous floors against all five old requested
targets and their stored actual F-delta thresholds directly from the independently
audited handover results.json records (not an unchecked derived summary):
90%, 95%, 99%, 100% of that scenario's permanent cap
floor and its near-Nash-anchor floor. These old numeric targets remain fixed;
they are not recomputed at a new price resolution. Report requested and actual
threshold separately. Also report continuous Nash surplus and the new
continuum's Nash-to-worst surplus gap.

## Primary mathematics and validated numeric method

Use CONTINUOUS_REFINEMENT_THEORY.md. Validate over the entire interval, not a
derivative sample: interior best responses via the two endpoint best responses;
positive threshold t<m; and its conservative sufficient small-tolerance
condition using m=w(ell). Obtain a rigorous upper bound rho<1. If any required
condition fails or cannot be enclosed, mark that scenario unresolved by this
theorem and retain it. Do not substitute a sampled monotonicity assertion.

For every eligible continuum enclose the unique upper-map fixed price q_star,
Nash price, their consumer surpluses, stationary individual/joint profits and
stationary unilateral deviation gain. A boundary-clipped fixed point is allowed
but must be explicitly detected. The global minimum-CS point is not assumed to
maximize profit or benefit either seller.

Use directed interval arithmetic with at least 80 decimal digits, safe
transcendental enclosures and sign-certified bisection. Positive Lambert-W
values can be enclosed by bisection of w*exp(w)-z; no unvalidated special-function
call is a certificate. Decimal exp/ln are correctly rounded HALF_EVEN regardless
of the context's arithmetic direction: enclose each monotone endpoint result
with next_minus/next_plus at the explicit working precision. Arithmetic
operations use directed endpoint contexts; tests must verify their containment
against independent higher-precision evaluations. Every returned root enclosure must have sign-verified
endpoints and width at most 1e-25 normalized price units. An unresolved sign or
root bracket is a retained failure, not an approximate success.

For an actual threshold F-delta: classify 'all-start failing continuation' only
when the upper CS enclosure is strictly below it; 'already guaranteed' only
when the lower enclosure is at least it; otherwise 'unresolved'. The all-start
conclusion depends on the validated theorem assumptions. Classify nominal and
effective continuums separately. Preserve enclosure endpoints as strings.

The result concerns infinite-run/liminf averages. A continuous top-choice path
may converge to its stationary limit asymptotically. No finite-time exact jump
to that limit is required or implied. A finite initialization period cannot
change the infimum long-run value after returning to the unchanged guard.

## Declared discrete refinement diagnostics

For each of the eight scenario labels use uniform grids of sizes
11, 15, 31, 61, 121, 241, 481, 961 and 1921 on its saved endpoints: 72 labels.
The best-profit benchmark is computed on each grid. Allowed quotes obey the
same epsilon + 1e-12 payoff allowance. New grids use binary64 endpoint linear
interpolation, recorded explicitly; this is a deterministic numerical diagnostic,
not an exact-real interval certificate for every quote.

Find each rival price's upper allowed index using unimodality and a discrete
best-response search, recording its maximizing index and boundary comparisons.
Verify nonempty support and upper-map monotonicity for every rival price. Only
when the discrete upper map is nondecreasing, use the order-envelope lemma to
compute every index's eventual fixed point, all-start minimum/maximum reachable
worst CS, nearest-continuous-Nash-anchor outcome, and the worst continuation over
the full one-round competitive-cap rectangle. Derive a pair's tail from the
two one-dimensional fixed points, including swapping two-cycles. If monotonicity
fails, retain the map and mark these optimality outputs unresolved rather than
running an unplanned replacement optimizer.

Report number of fixed points and spread of all-start worst welfare at each
mesh. No finite-grid unique-basin conclusion is assumed. Do not treat the largest
tested grid as proof of the limit. Continuous convergence follows only from the
reviewed theorem under its assumptions; no numerical K, width threshold or
explicit mesh error rate is claimed unless separately derived and validated.

Compare all tested meshes with the fixed original thresholds, and separately
show their own nearest-Nash permanent-cap floors. These are different questions.
Check all matching 11/15/31 inherited cases against their frozen graph bounds;
retain tiny interpolation/roundoff differences rather than editing old evidence.

## Independent checks, resources and reporting

An independent auditor must recompute primary root signs, global sufficient
conditions, interval welfare arithmetic and all threshold classifications without
importing the primary study's calculation functions. It may share standard
arithmetic libraries, with shared-library limits disclosed. Negative controls
must reject corrupted root, condition, target classification and mesh map data.

For every one of the 72 mesh labels, independently stream-enumerate every
price-profit pair and recover the maximum and highest allowed quote without
importing the primary market code or using its binary search. This is roughly
40 million pairs across the fixed matrix; no full state graph or stored dense
profit matrix is required. Also check the reported neighboring/boundary values,
recompute fixed points and pair tails independently, and crosscheck the matching
old graph certificates. If floating rounding puts a comparison near its decision
boundary, retain and flag that ambiguity explicitly. A runtime or memory overrun
does not authorize skipping the larger meshes, altering the protocol, or dropping
a failed label.

Synthetic tests cover interval outwardness, brackets, clipped roots, rejected
assumptions and malformed evidence before the freeze. Tests must not merely
compare the implementation to itself. Save source/input hashes, execution logs,
runtime, sampled memory and all failures. Target primary runtime under10minutes
and sampled RSS under250MB; an exceeded target is reported, never a reason to
drop a case. No training, model game players, APIs or paid services are used.

Deliver a reviewed research note, readable convergence figure, reproducible
numeric evidence and a graphical explanation distinguishing the valid finite
result from any continuous limitation. A negative result must be equally visible.
