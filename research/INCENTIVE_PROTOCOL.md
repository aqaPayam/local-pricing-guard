# Prospective Goal6 protocol: individual incentives under recurring caps

Status: prospective. No substantive case execution is authorized by this file.
The root must verify V7 delivery, activate a distinct goal and obtain independent
source-review GO before source/input freeze and any primary run. Earlier reports,
archives, games and their frozen evidence remain unchanged.

## Discriminating question and complete matrix

Does the public maximum-permitted-price script, which attains the lowest
customer benefit allowed by the masks, maximize either firm's own discounted
profit when the other firm remains that same public script? A profitable
deviation would separate worst-case safety from individual script stability.
It would not demonstrate learned collusion or undermine an all-policy floor.
The elementary last-guard one-shot screen is primary qualitative context,
not suppressed in favor of a more elaborate dynamic program.

Use all eight closed sparse-display finite numerical games, with their exact
61/62 quote arrays, original numerical masks, saved binary64 reward tables,
physical cap indices and epsilon-plus-comparison-allowance semantics. No new
mesh, tolerance, economy, reward recalibration or actual-demand shift is added.

Retain three named period slots per game:

1. Permanent activation, K=1.
2. The already closed EFFECTIVE continuous policy's old cap-95pct selected K,
   imported by matching the original scenario and target identity.
3. A prospectively fixed looser clock, K=16.

Retain duplicated K slots explicitly; do not treat them as independent evidence.
For each slot retain both focal sellers A and B and both discounts 19/20 and 0.
This is exactly 8*3*2*2 = 96 retained comparison labels. There is no random seed,
training, model player, statistical hypothesis test or external API. Effective
continuous K is a source of period identity only, not a transferred guarantee
for the separate numerical finite game. Preserve all five original target
identities and compare the new finite floor to them without retuning targets.

## Fixed decision model and exact calculations

Use the phase/state definitions and recursions in INCENTIVE_THEORY.md. The first
real execution is the cap and its reward counts as execution 1. Old initial
history has no reward. Cap replaces the guard; it does not intersect with it.
The opponent remains its public deterministic upper script after deviations.
No current hidden quote, internal state or policy adaptation is supplied.

Store all states in row-major focal-coordinate order index=i*n+j. On guard
phases opponent quote is U(i), focal support S(j), next state (a,U(i)). On cap
phases opponent quote is capIndex and focal support all indices <=capIndex.
Seller B rewards must be obtained from the original seller-B table with original
coordinates (rival,focal). Do not assume symmetry as a shortcut.

Convert the saved binary64 profit weights to exact integers with the minimal
common power-of-two denominator for that focal game. Discounts are exact
rationals, including 0/1. Evaluate every permitted action at every state/guard
phase. Tie-breaking is the smallest original quote index among exact maxima.
Retain all exact baseline feasibility and gain>=0 checks. No tolerance may turn
a negative gain into zero. No floating value iteration or finite approximation
of an infinite discounted value is used.

Compute optimal and prescribed-baseline finite layers, cap values, and infinite
values using their separate next-cycle constants. Retain a compact optimal
policy for every state/guard phase and the state-independent cap action. Replay
that policy from cap activation through one full block; its weighted payoff
must equal the exact block optimum. Repeat the block logically through the
reset formula, not a rollout-based infinite approximation.

The both-upper baseline cycle supplies one public prior state at each guard
phase. Store optimal and baseline finite/infinite values, exact gains, immediate
best-response gain and prescribed/optimal actions for every baseline-path phase,
including the cap. Gamma=0 thus retains later-phase incentives. Compute the
last-guard one-shot screen for every K>1 and the cap one-shot analogue for K=1;
save feasible maximizing action, exact gain and next-cap reset justification.
Retain zero gains and all tie cases. A positive screen can explain a positive
DP result, not be claimed as a separate novel mechanism.

For each distinct game/K reconstruct the both-upper quote cycle and save exact
binary64-weight customer-benefit cycle and minimum-prefix rational certificates,
with their inherited-target comparisons. Also retain baseline per-firm profit
cycle means. This avoids asserting that continuous-selected K protects 95% on
this numerical finite mesh. Discounted individual profit and undiscounted
customer-benefit averages are separate quantities.

## Evidence schema, hashes and prospective resources

Freeze the new primary source/tests, this protocol, theory, each of the eight
raw finite games and closed source/input manifests, passed finite numeric and
rational audit receipts plus their live auditor hashes, and the recurring
results/journals/audit dependencies supplying the effective 95% period. Verify
closed identities and all live transitive dependencies before freeze and again
after execution. Bind a verified V7 delivery receipt before numerical GO.

Use rolling BigInt value arrays. Store one phase record per complete optimal
and baseline layer: phase, state count, scale denominator, SHA256 of the row-major
integer numerators encoded as base10 strings, one per line WITH a final newline.
This encoding includes exactly n*n numerators with no JSON whitespace dependence.
Store argmax policies as n*n unsigned bytes (n<=62), row-major, with both file
hash and length; the cap action is a separate integer. Store all cap and on-path
values as reduced numerator/denominator decimal strings, with approximate fields
explicitly for display only. Document original versus focal reward coordinates.

Retain 96 result identities even if duplicated or failed. A failure keeps its
scenario, period slot/source, focal seller, discount, status and diagnostic,
with started/finished journals. Any existing execution journal, record, result,
completion or run-start blocks destructive rerunning. A freeze manifest alone
does not erase failure evidence. Catch and retain pre-case identity failures.

Soft resource targets are 60 seconds, 250 MB observed process RSS and 10 MB new
outputs, excluding inherited inputs. Report elapsed time and measurement scope,
including overruns, without selective horizon/slot removal. These are targets,
not permission to omit results. If a practical failure requires a new algorithm
or smaller matrix, retain the failed run and freeze a prospective amendment;
do not silently change a running protocol. No giant duplicate value-array dump
is required, but lack of raw layers is never a substitute for independent
recomputation of every Bellman maximum.

## Independent review and falsification

Before primary freeze, synthetic tests must discriminate rival-index orientation,
seller B rewards, nontrivial ties, unavailable actions, cap replacement, reset
timing, K=1, gamma=0 later-phase behavior, and separate infinite continuation
constants. Compare exact DP with exhaustive short-block policy enumeration on
tiny asymmetric games. Check exact integers against separate rational arithmetic.
Include a case where a late profitable deviation is invisible to gamma=0 at cap.

After freeze/run, an independent implementation imports no primary search or
reward-conversion functions. It independently converts every saved payoff,
rebuilds legal supports/upper maps and exact fractions, recomputes all state/
phase maxima and baseline layers, rechecks all hashes/argmax bytes, and verifies
the chosen policy's complete block replay and infinite reset formula. It checks
every on-path phase gain, last-guard screen, per-firm orientation, duplicate-slot
identity, finite customer-benefit prefix/cycle certificate and fixed old target.
Whole-table payoffs/masks remain checked against the inherited audit provenance;
reuse of an inherited arithmetic backend must be declared and source-hashed.

Deliberate in-memory corruptions must include at least a forbidden argmax, a
phase/value hash, seller-coordinate/reward identity, discount/continuation value,
and one-shot or finite-welfare certificate. Rejection tests do not modify frozen
evidence. A passed independent receipt binds exact manifest/results/index,
auditor and any arithmetic backend hashes. Derived analysis/UI/report exports
remain blocked until passed audits, complete journals and final dependency
rechecks; they retain all 96 labels and exact signs.

## Reporting and scope

Report exact signs and display-scale absolute/relative profit gains for each
firm/period, baseline/optimal policy traces, gamma=0 phase findings and the simple
last-guard explanation alongside customer-benefit protection. Relative gain is
unavailable when baseline value is nonpositive; no percentage benefit is inferred
by dividing by zero or a negative baseline.
Do not count duplicate slots, firms, states or phases as independent trials.
No significance test or convergence claim is planned. Zero gains at recorded
states are scoped observations, not a general equilibrium assertion.

Exact unilateral MDP/DP audits, periodic-control decomposition and renewal
arithmetic are established methods. Cite the close prior work already retained
in REFINEMENT_NOVELTY.md (arXiv:2610.21867v2) rather than claiming a new algorithm.
The contribution is the connection between a particular externally enforced
all-policy safety controller and its adverse script's individual incentives.
No behavioral emergence, stability of learned agents, human playtest, empirical
market or all-collusion equilibrium conclusion follows from this experiment.
