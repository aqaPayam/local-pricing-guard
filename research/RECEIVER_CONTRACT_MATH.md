# A receiver contract for the calibrated market

This is a proposed mathematical intervention, not a result about learned agents. No model was run to derive it. A receiver contract means an external action validator that enforces a stated property even if a predecessor note or a proposed action requests something else. It changes the feasible action set explicitly; it does not pretend that deleting text makes an agent competitive.

## Market and timing

Two firms simultaneously choose prices in `[0,3]`. Cost is `c=1`, product quality is `a=2`, the outside option has quality zero, logit scale is `mu=1/4`, and there are `M=100` buyers. Define

\[
 s_i(p_i,p_j)=\frac{e^{(2-p_i)/\mu}}{1+e^{(2-p_i)/\mu}+e^{(2-p_j)/\mu}},\qquad
 \pi_i=100(p_i-1)s_i.
\]

At time `t`, the validator sees an authenticated, completed previous-round rival price `p_j(t-1)` and an arbitrary proposed own price. It cannot observe the simultaneous current rival price. Both agents, their notes, and their proposal-generation methods may be arbitrary. Exact knowledge of this demand equation and cost, and correct enforcement outside the proposal generator, are essential assumptions.

## Exact best response and its derivative

For any rival price in `[0,3]`, the unique profit maximum is interior and above cost. Nonpositive margins cannot maximize profit. For positive margins the log of profit is strictly concave, so there is at most one stationary maximum. Write `s` for own share and `t` for rival share at that maximum. The first-order condition is

\[
 F(p_i,p_j)=1-\frac{(p_i-1)(1-s)}\mu=0.
\]

With `r=exp((2-p_j)/mu)`, the best response can be written using the positive real Lambert W function:

\[
 w=W\!\left(\frac{e^3}{1+r}\right),\qquad
 b(p_j)=1+\mu(1+w),\qquad s=\frac{w}{1+w}.
\]

Since `0<w<3`, this also proves `1.25<b(p_j)<2`, so the solution is inside the allowed interval. The share derivatives are `ds/dp_i=-s(1-s)/mu` and `ds/dp_j=st/mu`. At the first-order condition,

\[
 F_{p_i}=-1/\mu,\qquad
 F_{p_j}=\frac{st}{\mu(1-s)},\qquad
 b'(p_j)=\frac{st}{1-s}=s\frac{r}{1+r}.
\]

The simple share bound first gives `0<b'(p_j)<3/4`: `w<3` implies `s<3/4`, and `r/(1+r)<1`. The stronger derivative argument below yields the constant used throughout the subsequent results.

An elementary stronger bound is available: **`L=1/2` is valid globally**. Substituting `r/(1+r)=1-w*exp(w-3)` gives

\[
 b'=\frac{w}{1+w}\bigl(1-w e^{w-3}\bigr).
\]

For `0<w<=1`, this is strictly below `1/2`. For `w>1`, the inequality `b'<1/2` is equivalent to `w-1<2w^2 exp(w-3)`. Its right side is at least `2w^2/e^2` because `w>1`. The quadratic `2w^2-e^2*w+e^2` is strictly positive for all real `w`: its leading coefficient is positive and its discriminant is `e^2(e^2-8)<0`. Thus the stronger bound holds without a numerical search. We use `L=1/2` below.

## Bilateral exact enforcement

For epsilon zero, a shield ignores any proposal and outputs `b(previous rival price)`. If **both** sellers use it, realized prices satisfy

\[
 P_t=T(P_{t-1}),\quad T(x,y)=(b(y),b(x)),\qquad
 \|T(P)-T(Q)\|_\infty\le L\|P-Q\|_\infty,\quad L=1/2.
\]

The price square maps into itself, so the contraction theorem yields one fixed point and global geometric convergence. Symmetry forces the fixed point to have equal prices. It is the unique static Nash equilibrium, approximately `1.472927` per seller. If the first shielded round is `t0`,

\[
 \|P_{t0+k}-P^*\|_\infty\le L^{k+1}\|P_{t0-1}-P^*\|_\infty.
\]

This covers arbitrary initial last prices and arbitrary inherited notes/proposals: the validator reads neither instructions nor hidden controller memory when constructing the feasible action. It does not establish convergence under missing observations, fake price records, demand drift, asynchronous timing, or only one participating seller.

## Epsilon best-response projection

For a nonnegative profit tolerance epsilon, define the permitted set

\[
 A_\epsilon(q)=\{p\in[0,3]:\pi(p,q)\ge\pi(b(q),q)-\epsilon\}.
\]

The one-dimensional profit function is increasing up to its unique maximizer and decreasing thereafter (below cost its derivative is positive). Therefore this superlevel set is a nonempty closed interval. An action shield clips an arbitrary proposal to its two interval endpoints. This is projection onto an explicit economic constraint; it is not a claim that the proposal generator voluntarily chooses a best response. For sufficiently large epsilon, negative-margin prices may be allowed, so the small-epsilon bounds below must not be extrapolated.

Here is a valid but loose analytical robustness bound. For all `p_j` in `[0,3]`, optimal profit is at least the profit obtained by choosing `p_i=1.25` against `p_j=0`:

\[
 P_{\min}=\frac{25e^3}{1+e^3+e^8}\approx0.167266.
\]

Take `0<=epsilon<Pmin`. Every allowed action then has positive profit and hence `p>1`. On `(1,3]`,

\[
 \frac{d^2}{dp^2}\log\pi(p,q)
 =-\frac1{(p-1)^2}-\frac{s(1-s)}{\mu^2}\le-1/4.
\]

Strong concavity about `b(q)` implies

\[
 |p-b(q)|\le\delta(\epsilon)
 :=\sqrt{8\log\!\left(\frac{P_{\min}}{P_{\min}-\epsilon}\right)}.
\]

Indeed the log-profit gap is at least the squared distance divided by eight; epsilon-optimality bounds that gap above by `log(P*/(P*-epsilon))`, which decreases as optimal profit `P*` increases. Under bilateral shielding this gives the perturbed contraction inequality

\[
 e_t\le Le_{t-1}+\delta,
 \qquad e_{t0+k}\le L^{k+1}e_{t0-1}
 +\frac{1-L^{k+1}}{1-L}\delta,
 \qquad\limsup e_t\le2\delta.
\]

This is a neighborhood bound, not convergence to Nash, and it may be too loose to be useful. Once both shielded prices are above cost, rival prices lie in `[1,3]`; the same proof can use the larger lower profit bound `25e^3/(1+e^3+e^4)`, approximately `6.634698`, for subsequent rounds. **For arbitrary initial prices including zero, this bootstrap still requires epsilon below the global bound `Pmin≈0.167266`. Merely taking epsilon below the later bound `6.634698` does not establish entry into or invariance of the above-cost domain.** If initial prices are independently known to exceed cost, the later-domain argument can instead start there. Epsilon is measured in per-round profit units for the 100-buyer market, not price units. Numerical interval endpoints or observed convergence outside these sufficient conditions must be labeled numerical evidence, not an analytic theorem.

## Stationary symmetric-price admissibility frontier

For any constant price `p` in `[Nash price, joint-profit price]`, define the exact one-step regret

\[
 r(p)=\pi(b(p),p)-\pi(p,p).
\]

If both previous prices equal `p`, both proposals equal `p`, and the calibrated bilateral constraint uses `epsilon>=r(p)`, projection preserves both proposals. Induction makes the constant path invariant. Conversely, if `epsilon<r(p)`, price `p` is excluded from each feasible interval and the symmetric constant path cannot persist under enforcement. This is an exact pointwise admissibility frontier, not an assertion of monotonicity of `r`, of maximal harm among arbitrary histories, or of strategic equilibrium credibility. At the calibrated joint-profit price the threshold is approximately `7.420439195` profit units. Thus approximate best-response enforcement can admit the high-price constant path when its tolerance exceeds this threshold. The proposal must actually select that admissible path; permissibility alone does not predict behavior.

## What this does not establish

Unilateral enforcement is insufficient for symmetric Nash recovery. Against a rival fixed at the joint-profit price, an exact receiver chooses `b(fixed high price)`, leaving asymmetric prices indefinitely. A nonparticipating adaptive rival may also exploit the one-round delay. The contract promises myopic optimality relative to the previous quote, not current-round optimality against an unknown simultaneous action or optimal discounted repeated-game profit.

Demand estimation error, unknown costs, strategic data manipulation, nonstationarity, and enforcement bypasses invalidate assumptions and require separate tests. A note sanitizer cannot inherit this mathematical guarantee: the guarantee comes from the external constraint on actual settled actions.

## Novelty assessment

The exact bilateral result is a direct contraction argument for best-response dynamics; epsilon enforcement is a standard approximate-best-response construction. Calling that alone a new collusion discovery would overstate it. Potential research value lies in a carefully specified receiver contract, testing which facts must be authenticated, and quantifying performance/robustness when demand is estimated rather than known. Those contributions remain unproven. This derivation provides a falsifiable benchmark and separates handover information from enforceable behavior; it is not yet a publishable novelty claim or a literature priority claim.
