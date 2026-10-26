# Independent hostile review of the finite-game cycle audit

Status: prospective review, executed numerical audit and mathematical scope
review completed below. This is a separate AI-agent methods review, not human peer review,
official grading or evidence that learning agents spontaneously coordinated.
The reviewer owns only this review, a separate auditor and its targeted tests.

## The question worth answering

Earlier tabular-learning experiments sample a particular learning procedure.
They cannot by themselves establish what a price guard permits under other
strategies. A complete finite-state control graph can ask a different, useful
question: what long-run consumer and seller outcomes remain feasible when two
sellers pre-coordinate their choices while respecting that same lagged guard?
This is a worst-case capacity audit. It is not an empirical discovery of
collusion, an equilibrium test, or a new learning algorithm.

## Requirements before substantive freeze/run

1. State is the previous public executed pair (i,j). A simultaneous edge to
   (a,b) exists exactly when a is permitted against j and b against i. Both
   choices may follow an agreed public-state rule, without access to the rival's
   current sealed proposal. A returned prefix/cycle must be implementable with
   that information. Repeated vertices must not require inconsistent stationary
   actions unless additional public history/phase is explicitly allowed.
2. Separate minimum consumer surplus and maximum joint seller profit. A
   consumer-harming cycle need not maximize profit or benefit either seller.
   Report each seller's mean profit, every finite-grid Nash reference, and the
   continuous reference. Joint profit alone cannot establish individual
   rationality, profitable collusion or resistance to unilateral deviations.
3. Separate all-state results, each cyclic strongly connected component, and
   reachable results from named starts. Include nearest-continuous-price and
   high/high anchors plus the actual saved checkpoint starting pairs. These
   use checkpoint observations only: replacing the learned policy with an
   adversarial controller is not a test of how that learned policy behaves.
4. Certify complete graph coverage, reachable components and extracted paths.
   A favorable but unreachable cycle cannot be substituted for a checkpoint's
   reachable result. Acyclic components still matter as possible prefixes.
5. Use numerical primal/dual evidence: an explicitly feasible cycle supplies a
   primal mean; a potential h gives a lower bound through every eligible edge,
   w(u,v)+h(u)-h(v)>=L. Report the minimum residual and primal-minus-dual gap.
   Apply the sign change correctly for maximum joint profit. Check every edge,
   not just witness edges or sampled states. Floating-point residual tolerances
   do not establish an exact real-arithmetic theorem about logit payoffs.
6. The guarantee concerns long-run average outcomes. Along a finite T-step
   path the same potential yields sum(w)>=T*L+h(last)-h(start); a transient
   path can fall below the asymptotic cycle value. Do not call a minimum cycle
   mean a per-round safety bound or an unqualified finite-horizon guarantee.
7. Freeze protocol, game/solver/analysis sources, tests and checkpoint hashes
   before the main matrix. Preserve all old results, reports and packages.
   Record duplicate games/calibrations as dependence, not fresh replications.

## Provisional design assessment

The proposed 24 games (eight existing configurations times guard/cap/no-control)
are a coherent finite-family audit. The controlled cap/no-control structures
provide valuable analytical checks on a generic cycle solver. Small-graph
simple-cycle enumeration, periodic components, unreachable attractive cycles,
negative weights and tied optima are consequential tests. More random seeds
are not the main need for this deterministic graph question.

Minimum-mean-cycle optimization, graph reachability and Bellman-Ford potentials
are established techniques. Meaningful incremental value would be a correctly
bounded economic audit that exposes feasible behavior missed by the sampled
learners, or verifies where the guard actually rules out harmful cycles.
Constructing a coordinated policy is expected in a worst-case audit; presenting
it as emergent AI behavior would be a serious overclaim. Whether any witness is
both profitable and strategically sustainable remains a separate question.

## Next consequential question after a verified result

Test unilateral deviation gains and continuation incentives for economically
interesting feasible witnesses, then connect those findings to actual learner
behavior. A unilateral best-response or exploitability audit is more informative
than merely generating additional coordinated low-welfare animations. It must
respect the same information boundary and clearly specify the opponent policy,
guard, horizon/discounting and off-path behavior. No new agent API is needed.

## Pre-outcome review and freeze

The reviewer inspected the graph/solver, runner, protocol, methods, theory,
structural diagnostic and tests before the main run. Requested changes included
actual saved-terminal starts, all finite-grid Nash references, explicit objective
separation, passing declared tolerances to the solver, a strict coordinate-
monotonicity flag and correctly scoped finite-horizon guarantees. The reviewer
approved the stationary-ceiling proof and finite-deficit DAG corollary before
outcomes, and independently reran 14 tests: eight solver tests (including fifty
small-graph brute-force comparisons), three structural tests and three separate
auditor tests. The main matrix was not run before approval.

The source/input/checkpoint manifest was frozen at
2026-10-25T22:07:06.907Z, SHA-256
`176c7c0b226fea52ad80982896cdfdb650c46064aa37dae9a7b7575eceaa4b0b`.
It includes nine source/test/theory files, saved robustness inputs and all 256
training-endpoint hashes. Previous frozen reports and packages were preserved.

## Independent numerical verification

The separate auditor imports no game, market or search implementation. It
rebuilds the economic grid, rewards, controller sets, projection maps and full
public-state transition graph. Its iterative Kosaraju decomposition is separate
from the solver's Tarjan implementation. Search optimality is checked through
feasible primal cycles and all internal-edge potential inequalities, not by
trusting the reported Karp answer. Closed-form cap/no-control certificates are
also checked over their transient graph edges. The known pitfall in extracting
a witness from Karp's value formula is described in the primary paper
[Chaturvedi and McConnell, 2017](https://www.cs.colostate.edu/~rmm/minCycleMean.pdf);
the implementation instead extracts a shifted negative cycle and verifies it.

The final audit passed all 24 games and 48 objectives: 7,296 parameterized state
instances and 1,275,565 implicit graph edges. Every initial-state reachable
envelope, prefix, cycle, individual seller profit, Nash/joint reference,
checkpoint provenance and objective sign conversion was checked. All 24
structural cases satisfy the finite-map assumptions. The independent DAG
recurrence and global all-edge potential also reproduce every finite-horizon
bound. Maximum economic recomputation discrepancy is zero and the largest
reported cycle primal/dual gap is 2.186965275541297e-8. Five in-memory
corruptions of actual output were rejected: witness action, economic reward,
cycle bound, reachable prefix and finite-horizon bound. Original evidence was
not altered for those negative controls.

The numeric certificate is `research/cycle-results/independent-audit.json`.
Check counts include deliberately rejected corruption trials; state/edge counts
are graph coverage, not independent empirical replications. Arithmetic remains
floating point on computed logit weights, without interval enclosures of the
transcendental economic formulas. Do not call this an exact real-number proof.

Runtime was about 2.683 seconds with no failed/dropped primary cases. Observed
post-case process RSS reached approximately 238.5 MB, above the 100 MB target;
that overrun is disclosed. The runner samples memory after cases rather than
continuously, and heap usage at the largest-RSS sample is not an independent
measurement of peak heap/core-graph storage.

## What the result means, and what it does not

This fills a meaningful logical gap in the earlier learning study: a sampled
learner's performance and the complete feasible-policy envelope are different
objects. The finite-map stationary-ceiling lemma explains why no more harmful
repeating cycle exists in these cases. A one-node self-loop attains each global
minimum-CS bound; complicated cycling is not required. The finite-deficit
corollary additionally controls transients for all feasible policies through a
separately verified all-edge certificate. These are useful bounded mathematical
results, rather than another plot of a programmed rival's chosen behavior.

Reachability changes interpretation materially. In base 15-price guard .1,
the all-state minimum CS is 68.477352 at (2,2), while the near-continuous-Nash
anchor and protected-training endpoints at (1,1) can attain no worse than
72.119040 asymptotically. The worse self-loop is reachable from high initial
states and saved unguarded-training endpoints, not from every checkpoint.
Never substitute the global envelope for a particular starting-state result.

The most important hostile qualification is economic: three of the eight
guard minima are already finite-grid one-period Nash pairs. These are base
15-price tolerance factors 1 and .5, and low-cost 15-price; all use (2,2).
Their unilateral one-period gain is zero. They must not be advertised as a
new collusion or guard-exploitation discovery; finite-grid equilibrium
multiplicity partly explains them. The other five numerical cells (including
the affine-equivalent pair) have positive immediate unilateral gains: .076595,
.038297, .095492, .059069 and .161331 respectively for scale-.5, lower-quality,
base-11, base-31 and doubled tolerance. Those numbers are derived from the
independently reconstructed payoff table after the main run; they are an
interpretation diagnostic, not a new prespecified primary endpoint.

Minimum CS and maximum joint profit happen to share guard/cap witnesses in
this selected matrix. They differ without control, so conflating the two
objectives would be wrong even in the current data. Each seller's profit is
reported; mutual profitability does not establish incentive stability. The
existence of a deliberately chosen feasible policy says nothing about how
often independent Q learners or language models find it. No LLM experiment,
real-market validation or legal collusion certificate has been performed.

## Verdict and next gate

Accept this as a numerically verified, limited coordinated-policy capacity
audit with a reviewed structural explanation. Do not claim a new minimum-
cycle algorithm, general continuous-price safety theorem, credible collusion,
or a ranking prediction. Its value is the precise boundary between observed
learning, feasible coordinated outcomes, initial-state basins and transient
guarantees. The incremental novelty assessment remains modest.

The next consequential goal is now an independently checked discounted
unilateral-best-response audit against fully specified public off-path
policies. A candidate is each seller choosing the highest permitted price
against the previous rival quote; its credibility must be tested over all
states, not just on its desirable self-loop. Fix discount/horizon and opponent
responses before outcomes, solve each firm's best-response MDP, and report
policy versus optimal-deviation values with Bellman residual error bounds.
Failure to support that particular policy is informative and should not be
hidden by searching for an attractive witness afterward. More graphical
replays alone cannot close this strategic-incentive gap.

## Post-primary descriptive summary and an alternative next goal

The reviewer separately crosschecked the post-primary descriptive summary
against the already audited cases and preserved learner summaries: 3,047
checks covered all 256 terminal counterfactual rows, all 256 prior finite-20k
consistency checks, the copied eight-cell learner summaries, three exact-Nash
and five above-all-finite-Nash classifications, and all 64 unprotected-training
starts reaching the global guard minimum. This check performed no new
optimization or bootstrap and does not retroactively freeze the derived
interpretation. The primary audit certificate remains unchanged. Resource
wording in the descriptive report was corrected to sampled post-case RSS.

A handover initializer is another consequential next goal: one explicit
competitive-cap round followed by the unchanged guard, tested against every
cap-permitted first execution and all original starts. This is an all-policy
defense question, so it can be meaningful without assuming sellers' incentives.
Predeclare requested welfare floors and retain failures or empty safe sets;
an initializer cannot repair a floor no starting state can enforce. The first
round must actually execute, with its costs and consumer outcomes reported,
rather than silently editing the public previous-price state.

At a higher start-specific floor, do not automatically reuse the global
stationary-ceiling positive-deficit formula. A qualifying SCC can have some
below-floor states whose rewards are compensated elsewhere on its cycles.
Its accumulated positive deficits need not be bounded. A finite-horizon claim
then requires a correctly scoped all-edge potential on the reachable post-
initializer domain, including cross-SCC edges, or another separately verified
argument. Long-run component eligibility alone does not supply that finite
guarantee. Unilateral incentive stability remains a separate gate for any
future claim that the permitted outcome constitutes credible collusion.

## Graphical replay source review

The reviewer read the Stress Lab HTML, rendering/controller source and its
saved-data exporter. The display distinguishes deliberate coordination of both
shops from independent learning, excludes the initial historical state's reward,
checks allowed simultaneous moves, and identifies constant witnesses as constant.
The global-envelope selection explicitly chooses its own starting state rather
than implying that the loop is reachable from an unrelated anchor. Both sellers'
profits, customer benefit, finite-grid Nash membership and guard acceptance are
separate quantities. The guard's lagged profit comparison is distinguished from
the actual simultaneous payoff. The finite bound uses the global certificate,
not an unverified higher start-specific deficit argument.

Requested precision fixes were applied: the badge says numerical bounds, interval
endpoints round outward, finite lower bounds round downward, and coincident Shop B
lines are dashed. Source inspection found no remaining scientific-label blocker.
The implementation agent reports a DOM-adapter path/interaction smoke test; this
reviewer has not independently rerun that adapter. No enabled browser surface was
available to this reviewer, so this is source review rather than independent live
browser layout or usability validation. No human study is claimed.

The root developer subsequently restored a browser surface and performed actual
desktop interactions plus first-move clicks in 390px and 320px CSS iframe
viewports. The reviewer independently inspected the resulting desktop and narrow
screenshots: shop graphics, separate payoffs and lagged-rule cards are readable,
and the screenshots show no visible horizontal clipping. This is not an exact
DOM-width measurement or a human comprehension study. Root's recorded developer
checks include replay, keyboard/play-pause, manual asymmetric quotes and undo;
the reviewer did not personally repeat those live interactions. The root reports
an empty direct-page log and one unresolved MutationObserver error in the narrow
preview wrapper; it should not be summarized as universally error-free browser QA.

## Final actual PDF closure

Accepted report: `output/pdf/price-guard-study-v3.pdf`, SHA-256
`2c13cd18f85ce1e3dd42f2b93480d6b9a3412d564d16ac2102a581ca14fa5857`.
The reviewer extracted text from the actual PDF and inspected all eight rendered
pages of its initial version. The only subsequent textual change was page 2's
explicit grid endpoints, tolerance scaling and numerical tie/feasibility rules;
the reviewer freshly rendered and inspected that changed page. The final document
has eight pages, six body pages, a 188-word abstract and 392,562 bytes. Text and
figures are readable with no observed overflow, missing text or replacement glyphs.

The paper distinguishes coordinated capacity from emergence and incentive
stability, reports the three finite-grid Nash counterexamples to a collusion
interpretation, preserves the separate objective and reachability meanings, and
describes numerical rather than exact floating-point proof. Its developer-browser
wording is now supported by the root's actual checks described above. Accept the
report as a clear account of this limited contribution; its honest limitations
and verified execution do not elevate the established algorithms into a major
novel methodological advance. This review and its auditor sources are closed for
Goal 1 packaging; any later substantive report change requires a new hash review.
