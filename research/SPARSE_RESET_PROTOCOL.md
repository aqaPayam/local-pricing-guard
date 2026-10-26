# Prospective study: repeat the same physical cap, change its timing

Status: proposed before new controller calculations. Requires independent
implementation review, synthetic tests and a source/input freeze before cases.
The previous continuous/refinement study and its package remain immutable.

## Problem and primary comparison

Can recurring activations of the SAME inherited physical price cap restore a
fixed customer-surplus target that finite initialization cannot guarantee in
the continuous guard? How infrequently can that cap activate within this one
fixed-period family? A result requiring activation every round is retained.

Use all eight inherited labels and both effective/nominal exact-real continuum
models, with the same binary64-import semantics as the closed continuous audit.
The effective model is primary; nominal tolerance is the declared sensitivity.
Reuse each independently validated continuous N, q_star, C_star and rho enclosure
after verifying its exact audit/source/input links. Do not change the market.

The cap ceiling p_cap is the EXACT imported price of the ORIGINAL finite
competitive cap, found independently in the old cap case and old initializer
results. Validate their index/price/economy identities. It is NOT silently moved
to continuous Nash or rounded to a new grid point. Thus the intervention's
physical strength is held fixed while recurrence changes. Every cap execution
allows the full common interval[p_lo,p_cap] for both sellers, independently of
previous prices; it REPLACES the lagged profit guard on that round. Intersecting
the two rules is a different controller and is outside this protocol.

The first future execution at activation is an actual cap round, earns its
actual reward, and supplies public price history. The guard runs for K-1 rounds,
then the cap repeats. The public phase clock is part of this new controller.
This ongoing controller is not a finite initializer under a new name.

## Conditional theorem and numerical calculations

Let A=(p_cap-c)/mu and U be the same continuous upper allowed-price map. Validate
ell<=A<q_star with directed enclosures; retain failure as an unmet condition,
not as a numerical success. Then U(A)>A by contraction. Define a_0=A,
a_(j+1)=U(a_j) and r_j=C(a_j,a_j). The prices increase to q_star and rewards
decrease to C_star. Under the reviewed order comparison, the exact worst average
under period K is G_K=(r_0+...+r_(K-1))/K from every initial public pair.

The same maximum-allowed-price policy attains every future reward minimum.
For T=mK+s executions from immediate cap activation, its exact cumulative reward
is m*sum(r_0...r_(K-1))+sum(r_0...r_(s-1)). Descending rewards imply every finite
activation-average is at least G_K, as is the long-run average. Individual rounds
need only exceed r_(K-1), which can be smaller than G_K. Arbitrary initial phase
has only a long-run guarantee unless its uncontrolled prefix is separately bounded.

All computations use directed interval arithmetic with at least80 decimal digits
and independently checked monotone endpoint root enclosures. Do not reuse an
unvalidated special-function result. Primary calculation code may reuse the
frozen primary interval kernel/model with explicit hashed dependencies; the
independent auditor must use separate arithmetic/model calculation functions.
Disclose a shared standard Decimal backend rather than calling it formal or
fully arithmetic-library-independent verification.

Compute the first J=64 reward terms and a_J using sign-certified upper-map roots
with normalized brackets no wider than1e-25. Keep endpoint clipping explicit.
For K>J, enclose the remaining reward sum using

  (K-J)*C_star <= remaining sum
  <= (K-J)*C_star + B*mu*(q_star-a_J)*(1-rho^(K-J))/(1-rho).

Use outward upper bounds for positive factors and validated distances. Repeated
interval uncertainty is retained. No fabricated exact tail or large simulated
sample is inferred from this analytic enclosure. Record the fixed period
frontier K in[1,2,4,8,16,32,64,128], as derived values from one orbit per model.

## Targets and largest certified period

Keep all40 original requested targets and their exact imported ACTUAL F-delta
thresholds, read directly from the independently audited initializer results.
There are80 model/target labels across effective/nominal, not80 independent
experiments. The thresholds remain fixed and are not redefined as a new fraction
of a different benchmark.

For each actual threshold F:

- If C_star.lower>=F, label 'no recurring cap needed for the long-run target'.
  A no-intervention guard has this long-run floor but does not automatically
  inherit a finite-activation-average guarantee from arbitrary old prices.
  A single immediate inherited cap, followed by the unchanged guard forever,
  does provide the finite-horizon bound under A<q_star. Keep these two zero
  asymptotic-frequency policies distinct and report their startup cap counts.
- If r_0.upper<F, label 'infeasible for this fixed-cap family'. This does not
  prohibit a stricter cap or a different persistent controller.
- Otherwise seek the largest integer K with G_K.lower>=F AND
  G_(K+1).upper<F. Both inequalities are needed for the 'largest' claim.
- Numerical overlap at any relevant boundary is retained as unresolved or a
  certified integer bracket. Do not adjust a target to remove an ambiguity.
- Predeclare search ceiling65,536. Do not evaluate65,537 in this study. If65,536
  meets the target, report a censored lower bound
  on the largest period, never an invented optimum or 'no cap needed'.

Monotonicity of G_K justifies doubling/binary search, with no post-result change
to the intervention family. Record endpoint period bounds and reward-enclosure
strings. Record cap-rule activation frequency1/K; distinguish it from realized
quote-change frequency, seller autonomy or economic intervention cost. Seller
profits on the selected worst-CS periodic path are descriptive, not uniform
profit guarantees or joint-profit optima. Do not combine objectives into an
invented aggregate score.

## Separate finite human-play demonstration

For each original scenario, construct ONE finite display game from its saved
61-choice refinement grid plus the exact inherited p_cap quote. Before sorting,
remove any base quote within1e-12 absolute price units of p_cap and insert p_cap
itself. Preserve that original cap exactly and record every removed quote and
distance; more than one near quote is a retained invalid-grid condition. This
predeclared priority rule prevents almost-coincident binary64 representations
of the same nominal cap from adding artificial display actions and rounding
nonmonotonicity. It is part of the NEW display game, not an edit of old grids.
Sorted exact deduplication then yields61 or62 quotes. The cap therefore
has its actual inherited physical ceiling and an explicitly included maximal
quote. This is a separately declared nonuniform display game, not the uniform
continuous-refinement sequence.

Recompute its full payoff table and original discrete best-profit guard under
the same recorded JavaScript epsilon+1e-12 rule. This saved finite numerical game
uses those binary64 guard masks as its action correspondence. Independently
reproduce the JavaScript comparison arithmetic; do not reinterpret the mask as
an exact-rational profit comparison or transfer a real-logit certificate to it.
Treat the saved binary64 consumer-surplus rewards as exact rational weights for
cycle/prefix certificate arithmetic. Export expected demand for graphical
baskets, explicitly as model demand, not observed customers.
Verify nonempty supports, upper-map monotonicity, coordinate-decreasing surplus
on the ENTIRE stored payoff table, and the cap index. For every declared period, independently
derive the exact finite top-choice cycle and finite activation-prefix floor.
Check U(cap)>=cap before labeling every finite average at least G_K. If that
condition fails, retain it and use the separately checked exact floor
min_{1<=s<=K}(prefixSum(s)/s), which includes the complete-cycle average;
do not transfer the continuous theorem to the display game by analogy.

The UI may let a human choose both shops' legal quotes and compare the cumulative
customer-surplus buffer with this finite game's own audited floor. A scripted
maximum-price benchmark must be explicitly labeled scripted. No Codex account,
API or model may play. A manual path illustrates the policy-independent bound;
it does not replace its independent proof/calculation. All profit and consumer
rewards use newly executed prices; an initial memory pair earns no reward.

## Review, resources and deliverables

Independent review must verify the generalized inherited-cap theorem, all80
target labels, every reported safe/next-failing boundary and the prefix/tail
enclosures. Independently enumerate every finite payoff pair and independently
check all cap outcomes, phase transitions and displayed floors. Inject failures
into cap identity, phase/reward timing, orbit term, period boundary and prefix
certificate, and require their rejection. Synthetic tests precede source freeze.

Save every failed condition/calculation, exact constants, source/input hashes,
per-case execution journal and final dependency recheck. Refuse overwriting
partial or closed outputs. Targets: under30minutes for all primary calculations,
sampled RSS below250MB; report exceeded targets without dropping a case. No new
learning, model players, paid services or external submission is performed.

Deliver an independently reviewed result and period/protection frontier, an
honest comparison with recurring-control prior work, a playable graphical finite
demonstration and a reproducible research checkpoint. The next later question
must be selected by review rather than by adding parameter sweeps for volume.
