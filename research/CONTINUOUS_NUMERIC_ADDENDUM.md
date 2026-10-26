# Continuous primary implementation details, before evaluation

This addendum specifies implementation details under the immutable prospective
protocol and conditional theory. It introduces no scenario evaluations or new
scientific endpoints. The primary arithmetic manifest is separate from the mesh
diagnostic manifest; neither edits Goal 1 or Goal 2 evidence.

The primary source files are `continuous-study.py` and `continuous_interval.py`.
All imported binary64 constants are converted through exact integer ratios and
`Decimal.from_float`, including the binary64 literal `1e-12`. The effective
tolerance is the exact real sum of those imported constants. Its separately
rounded binary64 sum is recorded for comparison only. Fixed old targets come
directly from the independently audited handover `results.json` records, not a
derived display export. Their saved binary64 thresholds are interpreted exactly.

Arithmetic endpoints use 80 decimal digits with floor/ceiling rounding. Each
Decimal `exp`/`ln` endpoint is evaluated under explicit 80-digit HALF_EVEN and
expanded by one `next_minus`/`next_plus`. Exact terminating rational conversions
do not pass through the default Decimal arithmetic context. Nonterminating
normalization is rejected rather than silently treated as exact; every inherited
normalization is checked at execution by this conversion rule.

Positive Lambert-W is enclosed by signed bisection of `w exp(w)-z`, separately
at each argument interval endpoint, with width at most `1e-40` at each endpoint.
Nash and upper fixed prices use signed brackets of width at most `1e-28`, tighter
than the protocol's `1e-25` requirement. A zero-straddling midpoint never supplies
a guessed sign: quarter points must certify progress or the calculation remains
unresolved. Bisection requires a continuous unique root with negative-to-positive
sign orientation. It does not assert that every residual derivative is positive.

The endpoint best responses certify interiority throughout the interval because
the best response is increasing. The saved lower endpoint W interval supplies
the global lower bound used for both sufficient small-tolerance inequalities.
The contraction bound uses the global `W(1/(e k))/(1+W(1/(e k)))` enclosure.
Failure to certify any sufficient hypothesis is retained as unresolved by this
theorem, rather than evidence that the hypothesis is necessary or false.

The interior upper fixed-point bracket begins above the enclosed Nash price.
The residual is `w(q)-t-f(q,q)`, whose unique root on that branch follows from
the reviewed contraction theorem. A strictly negative residual at the upper
domain endpoint certifies that endpoint as an allowed clipped fixed point;
its best-response branch margin is also checked. An unresolved endpoint sign
remains unresolved, including a possible exact boundary equality.

Each of the sixteen planned records is written separately before completion.
Failed assumptions/calculations and all five target labels remain visible.
An execution-start receipt prevents rerunning over partial outputs. Source/input
hashes are rechecked at completion. Resource samples occur after records and
are explicitly not continuously measured peak memory. This implementation does
not evaluate a quantitative mesh-error constant or establish incentive stability.
