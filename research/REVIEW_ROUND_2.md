# Independent research review — round 2

Decision: **accept the calibrated mathematical argument as a conditional benchmark; require revised contribution claims and additional quantitative evidence before accepting a substantive research result.** This is stronger than the original scripted filtering null, but it is not a newly discovered best-response theorem, a general anti-collusion defense, or a demonstrated result about AI agents. Agreement is not the acceptance criterion.

Reviewed `RECEIVER_CONTRACT_MATH.md` and the draft `receiver-contract.js`. Ran a few local numerical diagnostics only; no game-model inference or paid resources. New diagnostics are not frozen confirmatory experiments and must be frozen/reproduced in the new study if used as results. The previous matrix remains unchanged background.

## Mathematical review

The Lambert-W best-response expression is correct for the stated homogeneous two-firm calibration. With `r=exp((2-q)/mu)`, the argument is `exp(3)/(1+r)`, the best price is `1+mu*(1+w)`, and the optimum share is `w/(1+w)`. The bound `0<w<3` implies an interior price in `(1.25,2)`.

The first-order-condition derivatives at the optimum are also correct: `F_own=-1/mu`, `F_rival=s*t/[mu*(1-s)]`, so `b'(q)=s*t/(1-s)`. The uniform `k=0.75` bound follows from `s<0.75` and `r/(1+r)<1`. This is conservative but analytical. The map sends the full price square into itself, and simultaneous bilateral best responses are a contraction in the maximum norm. The stated activation-round exponent is correct. The unique fixed point is symmetric and is the static Nash point.

The positive-epsilon argument is valid under its stated restrictions:

- Choosing own price 1.25 gives the uniform lower bound `P0=25*exp(3)/(1+exp(3)+exp(8))=0.1672655373` on optimal profit over all rival prices in `[0,3]`.
- For `epsilon<P0`, every allowed action has strictly positive profit and therefore lies strictly above cost.
- On `(1,3]`, the log-profit curvature is at most `-1/4`, so the squared distance from the optimum is at most eight times the log-profit gap.
- The log ratio `log(P/(P-epsilon))` decreases with P, giving the proposed uniform displacement bound and the standard perturbed-contraction radius `4*delta`.
- After the first guarded step, rival prices lie in `(1,3]`. The larger floor `P1=25*exp(3)/(1+exp(3)+exp(4))=6.6346982193` is then valid for later updates.

**Bootstrap restriction:** an arbitrary-initial-state theorem still needs `epsilon<P0` to justify entry above cost. It cannot simply replace that assumption with `epsilon<P1`. If both initial rival quotes are already at least 1, the stronger floor can instead be used immediately with its separate initial-condition assumption. State which theorem each numerical case invokes.

For an explicit two-stage statement, let the first-step bound use `delta0` from P0, and subsequent steps use `delta1` from P1. If `e1 <= k*e0+delta0`, then for `m>=1`, `em <= k^(m-1)*e1 + delta1*(1-k^(m-1))/(1-k)`. The eventual radius is `delta1/(1-k)`, not the much worse all-domain radius. This improves the sufficient bound without extending the permitted global epsilon range.

The certificate remains loose. The bootstrap asymptotic radii are approximately 0.04392 at epsilon 0.0001, 0.13890 at 0.001, 0.43940 at 0.01, and 1.39425 at 0.1. Report these honestly: a valid inequality that permits nearly the whole price range is not a practically useful welfare guarantee. Numerical convergence can be much better without improving the theorem.

## Algorithm review and remaining checks

For the current profit function, the epsilon-superlevel set is a closed interval: profit is strictly increasing below its unique maximum and strictly decreasing above it. The draft's bisection and clipping implement the appropriate one-dimensional projection. Epsilon zero is exactly the unique best-response price, independent of proposal. This is a complete loss of pricing autonomy, not merely removal of harmful inherited instructions.

The code's timing reads only `previous`, computes both corrected quotes, and settles them together. Believed cost affects the constraint model; `outcome` settles at true cost 1. These are appropriate choices for testing the stated guarantee and a controlled model-error counterexample. Distinguish forecast regret against the previous rival quote from regret against the current realized rival price. Do not rename either one 'legal collusion'.

Before accepting executed results, independently check: optimum versus a separate numerical oracle; epsilon endpoints over a broad model/quote domain; permitted-action pass-through; projected-regret residual; exact epsilon-zero proposal invariance; one-sided versus bilateral coverage; inclusive release timing; true versus believed settlement fields; reproducible streams; and exact case accounting. Numerical bisection in floating point is not a formal machine-checked certificate. Either provide an implementation-error allowance justified analytically or label the theorem exact-arithmetic and the implementation numerically verified to a stated tolerance. Ninety iterations alone do not prove floating-point feasibility.

## Substantive assessment

The following are meaningful but limited results:

1. A **proposal-agnostic conditional recovery statement** separates the untrusted proposal generator from a trusted economic enforcement layer. This is qualitatively stronger than testing whether a few programmed scripts behave well.
2. Explicit **necessary-assumption failures** clarify why packet filtering, one-sided adoption, and temporary onboarding are weaker interventions than permanent bilateral enforcement.
3. A numerical **autonomy–harm frontier** could show precisely when allowing economically near-optimal proposals reintroduces a harmful fixed point.

The first result remains an application of known contraction and shielding ideas. The second is largely expected from the changed assumptions; its value is in precise quantification, not novelty by surprise. To earn more than an educational replication contribution, the third should expose a quantitative boundary that is not obvious from a generic best-response baseline. Do not count a larger scripted matrix as the missing scientific advance.

Actual learned-agent data are **not necessary** for a properly scoped mathematical or worst-case numerical benchmark. They **are necessary** for empirical claims about learned pricing policies, the frequency of AI collusion, or semantic usefulness of inherited text. There is no authorization for new account-based game inference, and this review does not ask for it. If the theory/application claim remains modest, report that limitation rather than implying models were tested.

## Strongest feasible additional offline science

For each candidate symmetric stationary price p, calculate the exact forecast-regret function

`R(p)=profit(bestResponse(p),p)-profit(p,p)`.

If `epsilon>=R(p)`, a constant proposal p passes through the bilateral contract unchanged at `(p,p)`. This supplies an exact self-sustaining harmful-outcome counterexample even when **both** sides enforce permanently and the demand model is correct. It identifies a limit of the contract itself, not just an implementation fault or missing adoption.

At the current joint-profit price, the draft numerics give `R(p)=7.4204391951` profit units. Once epsilon reaches that threshold, constant monopoly-price proposals require no correction at the high-price state. Freeze and independently verify this value before using it as a study result. Map customer harm and retained action freedom along this stationary feasibility frontier; do not assume R is globally monotone without proof. If reporting the largest feasible stationary price for a given epsilon, solve the actual constrained optimization, not a coarse grid falsely presented as exact.

Measure proposal autonomy directly: feasible interval width, percentage of a prespecified proposal grid passed unchanged, correction magnitude, and sensitivity to proposal policy. For safety, measure worst permitted proposals rather than relying on average random draws. Compare analytical envelopes with the observed worst-case stationary boundary so the reader sees certificate conservatism and genuine contract failures separately. A nonstationary adversarial proposal could be worse; the stationary frontier is a lower bound on possible harm, not a complete worst-case theorem.

The three necessary-assumption diagnostics should remain:

- Unilateral exact enforcement against a fixed high rival yields approximately `(1.661695,1.924981)`, not the symmetric competitive pair.
- Releasing enforcement after ten rounds with constant high proposals restores high prices immediately after release; the active period does not sanitize the proposal generator.
- Believing cost 1.2 when true cost remains 1 makes bilateral exact enforcement approach approximately `(1.650471,1.650471)`, above the true-model Nash price. Report true-model welfare and profits, not the validator's imagined outcomes.

These numbers are diagnostic checks of the draft, not evidence that these are the only or maximal failures. The one-step-delay exploitation boundary also remains open.

## Acceptance gate for the next round

Accept a **scoped theory-plus-counterexample result package** if it provides: the corrected explicit bootstrap theorem; exact-versus-floating arithmetic scope; independent endpoint/optimizer and artifact audits; frozen new evaluation; the stationary harmful-feasibility threshold/frontier; autonomy metrics; all unilateral/release/model-error failures; and a literature comparison stating that BR convergence and shielding are established.

The abstract must prominently state permanent bilateral enforcement and trusted known economics, the loss of autonomy at epsilon zero, the positive-epsilon neighborhood rather than exact convergence, and the absence of learned-agent evidence. The architecture is an ongoing action contract, not a one-time safe packet; explain the shift instead of hiding it behind the old title.

Do not accept claims of a novel general anti-collusion algorithm, proof of semantic handover safety, a model-agnostic real-market guarantee, or a strong competition ranking. A careful conditional certificate plus a sharp autonomy/failure boundary could be a useful hackathon result. Whether it is competitive depends on clarity, actual incremental insight, and comparison with existing work; reviewer agreement alone cannot establish that.

## Pre-execution addendum: sharper contraction and runner

The newly appended analytical `k=1/2` proof is valid. Substitution gives `b'=w/(1+w)*(1-w*exp(w-3))`. For `w<=1` this is below 1/2. For `w>1`, the required inequality follows from `2*w^2*exp(w-3) >= 2*w^2/e^2 > w-1`: the last strict inequality is equivalent to positivity of `2*w^2-e^2*w+e^2`, whose discriminant `e^2*(e^2-8)` is negative and leading coefficient positive. This is an analytical bound, not an estimate from a derivative grid.

The runner's exact bound `.5^round*initialError` and two-stage positive-epsilon bound are correctly indexed. Specifically, `e1<=.5*e0+delta(P0)` followed by `et<=.5^(t-1)*e1+2*delta(P1)*(1-.5^(t-1))` holds under the prior global restriction `epsilon<P0`, bilateral permanent coverage, accurate parameters, and authenticated immediate previous prices. Earlier 3/4 constants and 4*delta radii in this review are conservative predecessors; with the sharpened theorem, the limiting 2*delta(P1) radius is half the previously listed bootstrap radius. This improvement does not imply a new best-response-convergence theorem.

Before freezing the new runner: reconcile the protocol's promised maximum price-error metric with the summary schema, which at review time contained only final error and maximum bound residual. Also specify that the 121 stationary probe points sample the segment from Nash to the joint-profit price. They demonstrate permitted harmful stationary outcomes on that segment; they do not identify the globally largest feasible stationary price, exhaust prices above the joint-profit benchmark, or certify worst-case nonstationary harm. A manifest may preserve the precise source sampling formula, but the resulting plot/report must use this limited interpretation.

The runner's 2,160 main nominal configurations, 12 long-horizon supplements, two wrong-mu supplements, and explicit computational tolerance of 1e-7 are coherent with the current protocol. Separate random streams and their phase/seed details are documented in the preserved source; independence is not a statistical claim. The broader theorem is a real-arithmetic statement; the planned floating-point residual checks are numerical verification, not a machine-checked proof. Executed artifacts and optimization endpoints still require independent audit before acceptance.
