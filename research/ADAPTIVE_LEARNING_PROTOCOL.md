# Prospective adaptive masked-pricing study

Status: prepared before implementation and substantive learning. Goal 7 is a
distinct authorized research goal, but this document does not authorize training.
Primary code, synthetic tests/benchmark, this protocol, the analysis contract and
all inherited inputs require root/referee review and a source/input freeze before
any real case starts. Earlier science, reports, games and archives are immutable.

## Question and reporting boundary

How do independently adapting masked tabular-Q sellers behave under different
timings of the same external physical cap? Earlier studies established adverse
permitted paths and audited one seller against a fixed upper-price opponent.
Here both sellers learn their own profit policies independently. The fixed upper
script is not a training player, teacher, reward or initialization instruction.

Q-learning, masked actions and deterministic-policy graph evaluation are
established methods. This is a controlled behavioral study of these saved finite
games, not a new learning algorithm, a reproduction of a published formation
experiment, an equilibrium proof or evidence of emergent intent. There is no
unrestricted/no-guard arm, so this study cannot establish that these learners
discover collusion or that the controller prevents it relative to unconstrained
learning. Positive/zero/unfavorable outcomes are retained without reseeding.

The learner's public phase representation changes size with the period. Equal
training rounds do not mean equal visits per Q row or equal representational
complexity. Report state/action coverage and this limitation before attributing
differences solely to cap frequency. Neither initialization nor a fixed horizon
guarantees competence or convergence of two adapting learners.

## Fixed matrix and inherited game identities

Use only `base-g15-t1` and `base-g15-t0.5` from the separately audited
`sparse-display-results` finite games. Each currently has 62 original quote
indices, including its exactly retained physical cap. No economy, payoff,
tolerance, comparison allowance, quote grid or numerical action mask changes.
The suffixes are historical scenario labels, not new 15-quote training grids.

Each market has four controller conditions:

1. **Startup only:** phase 0 executes the actual physical cap once, then phase 1
   executes the original guard forever. Phase 1 never returns to phase 0.
2. **Permanent:** K = 1, an actual cap at every execution.
3. **Inherited selected period:** the already closed EFFECTIVE continuous
   `cap-95pct` period identity, currently K = 4 for base and K = 10 for half
   tolerance. Import by scenario and exact original target identity. This is
   a period identity, not a transferred finite-game protection guarantee.
4. **Fixed looser period:** K = 16.

Periodic phase 0 executes the cap instead of intersecting it with the guard;
other phases execute the original guard. Phase advances modulo K. All conditions
start at phase 0 with the same unearned highest original-price history
`[n-1,n-1]`. The first real cap execution counts as round 1 and earns rewards;
old history earns none. A cap resets the permitted sets, **not necessarily the
executed pair**: a learned cap choice can depend on the full previous pair.
Consequently Goal 6's fixed-script block-reset value reduction does not apply.

Use 12 fresh paired seed IDs `907001..907012`, two Q initializations (zero and
optimistic), two markets and four conditions: exactly **192 retained runs**.
No seed may be replaced for unattractive behavior. The same seed identifies a
paired market/initialization/controller family, not independent observations
within that family. Both sellers and checkpoints do not increase independent n.
The rejected initial candidate 7001..7012 overlaps an older cohort and is not
used. A retained read-only inventory of 16 prior manifests and 17 closed protocol
files found no candidate 907001..907012 collisions
(`.local/adaptive-seed-inventory.json`, SHA256
`00e4ea5d05b2da0da2a27bfec87ac709734acc0e079ad1cc70a5ade9043157bb`).
Final actor namespace/state mapping is source-frozen; no empirical outcomes
influence this administrative check.

## Learner and simultaneous information boundary

Each firm has a private Q table and a separate private pseudorandom stream.
Its state is `(public phase, own previous executed index, rival previous
executed index)`. Seller B uses the transposed completed-price coordinates.
Keep the complete previous pair at cap phases; do not merge cap histories or
introduce the fixed-script assumption that they are economically identical.

At phase 0 the legal support is every original index `0..capIndex`. At a guard
phase the support is exactly `S(previous rival index)` from the saved numerical
game. Exploration and greedy selection both choose only within that support.
There is no outside proposal, projection or alias-credit mechanism. Acceptance
is therefore 100% by construction and is not a measure of strategic freedom.
Report permitted count/span and actual action use instead. A price-correction
rate is unavailable without a separately specified unconstrained proposal.

Both firms observe the same completed public state, independently choose and
commit their current actions, then settle simultaneously. Each receives only
its own deterministic saved **expected profit** and the next completed public
state. There are no sampled buyers or stochastic reward noise. Neither reads the
other's Q table, current hidden choice, internal random draw, reward or learning
state before commitment. No messages, cooperative reward, monopoly instruction,
scripted retaliation, joint optimizer or experimental model call is supplied.
Trusted payoff-table lookup is environment implementation, not counterfactual
reward feedback to the acting learner.

For its selected and executed action a, update only the firm's own cell:

`Q(s,a) <- Q(s,a) + .1 * [own profit + .95 * max_legal Q(s_next,.) - Q(s,a)]`.

The bootstrap maximum is over the **next phase's legal support**, including cap
replacement. The update is continuing across cap rounds: do not terminate,
truncate or reset a return at a cap. Both actions, rewards and next-state maxima
use pre-update state/tables. Greedy exact numerical ties choose the smallest
original permitted quote index. Arithmetic is explicitly binary64 Q arithmetic;
the mathematical discount is 19/20, represented by its binary64 nearest value.
This is not exact rational learning or a Bellman convergence certificate.

Zero initialization sets every stored legal Q cell to zero. Optimistic
initialization sets every such cell to the constant `20 * Rmax`, with Rmax the
largest own-profit entry in that market's saved table. This public-model upper
bound is disclosed preprocessing, not per-action profit hints or a cooperative
objective. Illegal action cells are absent and cannot enter an argmax.

Use T = 2,000,000 rounds, alpha .1 and discount .95 in every run. At round index
t = 0..T-1 use `exp(-ln(100)*t/(T-1))`, with declared endpoint values 1 and .01.
There is no exploration reset at checkpoints or caps. Each seller consumes two
random numbers every round (explore decision, uniform support rank), even when
greedy or singleton support makes a draw unnecessary. This preserves paired
streams across conditions/initializations without forcing identical actions.
Use the published [xoshiro128** 1.1 transition and 2^64 jump](https://prng.di.unimi.it/xoshiro128starstar.c).
The master four-word state is `[907001,907002,907003,907004]`. Seed family
907001+k uses jump segment 2k for A and 2k+1 for B. Generate all 24 four-word
initial states by repeated published jumps and save them in the manifest. Each
actor consumes at most 4,000,064 draws including a terminal cloned probe, far
less than the 2^64 spacing; different actor segments do not overlap within this
budget. Reusing the same actor segment across controller/market/initialization
conditions is intentional pairing, not a new independent seed. Exact source
tests and independent probes check the transition, jump, 32-bit unsigned
semantics and checkpoint state. This is pseudorandom simulation, not a claim of
physical randomness or statistical independence from a cryptographic generator.

## Storage and prospective engineering budget

Store compact **legal-action** Q rows. Focal row index is
`phase*n*n + ownPrevious*n + rivalPrevious`; enumerate each support in ascending
original quote order. A deterministic prefix-offset layout omits illegal cells
without merging states or actions. Cache maxima only if synthetic reference
tests establish equivalence for increases, decreases, ties, self-loops and next
support changes. No approximation or stale maximum is permitted.

Read-only sizing of the two frozen inputs gives at most 6,752,544 bytes for a
pair of compact Q tables in one run. All 192 final pairs total 445,852,416 bytes;
1M and 2M checkpoints total 891,704,832 bytes before counts/metadata. Dense
phase/state/action cubes would instead require about 4.76 GB per checkpoint.
These are structural storage calculations, not training results.

Use one sequential local worker. Soft targets are one hour of primary elapsed
time, 256 MB observed RSS and 1.5 GB of new primary outputs, excluding inherited
inputs. Record measurement scope and all overruns. Never silently remove seeds,
conditions or checkpoints. Before freeze run only a synthetic engineering
benchmark with artificial rewards/masks and representative dimensions, not a
real-market formation pilot. Confirm feasibility or obtain a prospective uniform
amendment before any real run; after freeze retain any resource failure instead
of changing horizon/algorithm in place. No purchases, installs, remote compute
or paid APIs are authorized by this protocol.

## Checkpoints, support coverage and training records

Save complete 1M and final 2M checkpoints, including both compact Q arrays as
explicit little-endian binary64, current step, controller/phase, exact completed
public index pair, private PRNG states, source layout and file hashes/lengths.
Keep exact legal-cell action visit counts: little-endian uint16 stores
`min(count,65535)` and a sorted `{cell,count}` overflow list supplies the full
integer for counts above 65535. Auditors check total updates, row counts and
seller-coordinate consistency. A zero Q value alone does not establish that
a state/action was unvisited.

At **each** 1M/2M checkpoint retain its own preceding 100,000-round window
(900k..1M and 1.9M..2M); this does not change T or exploration. Retain exact sparse
**joint source-state to executed-pair**
transition counts (uint32 source/destination combined key and uint32 count),
plus fixed 10,000-round learning summaries. Save explicit integer per-seller
largest-permitted-action counters too, and independently rederive them from the
joint counts. Separate source/destination marginals alone are insufficient for
that metric. Report last-window means of
customer benefit, each firm's profit and price, largest-permitted-action use,
permitted count/fraction/span and actual cap-rule frequency. Derive exact saved-
weight terminal-window means from integer counts; label any rounded learning
curve summaries as display values. Cap activation frequency is not price-change
frequency or intervention cost.

Retain the initial update trace, fixed periodic update samples and a contiguous
32-round transition/update probe following each 1M and 2M checkpoint. Each probe
runs on a complete clone, including both Q/count arrays, clock/history and private
random streams, and discards all changes afterward. Its 32 additional diagnostic
steps are counted separately from main training. The final 2M endpoint, window,
Q tables and counts must remain unchanged. A clone at or beyond the terminal
schedule uses exploration .01; a 1M clone retains the original time-indexed
schedule. The saved Q, clock, PRNG state and probe's post-state/Q hashes allow
independent local replay from a real trained state. Synthetic fast/reference and
checkpoint/resume tests
must precede freeze. Unless all rounds are independently replayed, explicitly
state that source/trace/probe review does **not** certify the entire training
history independently. Learning provenance and frozen-policy evaluation have
different audit scopes.

The kernel's `learn:false` option disables updates only and still samples its
time-indexed exploration. Frozen evaluation must derive masked greedy arrays
directly from Q and never use that sampler as a no-exploration evaluation.

## Frozen evaluation: actual continuation is primary

At both checkpoints turn exploration and updating off, derive both complete
masked greedy policy arrays from saved Q and do not change the environment's
clock or completed-price history. The **final 2M actual terminal state** is the
primary evaluation start. In particular startup-only remains in its permanent
guard phase and receives no new cap. Periodic conditions retain their actual
clock; the chosen checkpoints are integer multiples of their specified periods,
which is a predeclared design feature, not a post-outcome phase selection.

A frozen pair forms a deterministic joint functional graph on original-world
states `(phase,previousA,previousB)`. Seller A looks up its focal row directly;
seller B transposes previous A/B. Rewards belong to the newly executed pair,
not the old observed pair. Build every successor, identify every recurrent
cycle, transient distance and basin size, and retain canonical policy/graph
hashes and exact saved-weight cycle means. A complete evaluation uses no
arbitrary finite rollout as a substitute for an eventual recurrent outcome.

The primary outcome is the undiscounted customer-benefit cycle mean reached
from the actual final terminal state. Retain that start's exact step/phase/pair,
full transient/cycle identity and both profit/price means. The 1M equivalent is
secondary and independently audited too. Report each evaluated cycle's state
and chosen-action visit support for both firms, including default/unvisited Q
states or never-tried greedy actions. All-state cycles from rarely trained
states are structural properties of the stored policy, not demonstrated
competence or observed training occupation.

Separately restart each frozen checkpoint at common highest old prices and
phase 0 for a **counterfactual fresh-cap/basin diagnostic**. No Q update or new
training occurs. This may differ from actual continuation, especially for the
startup-only controller. Label the two trajectories separately and never use
the fresh-cap outcome as the primary terminal continuation.

For structural reachability, "policy-cap-reachable" means reachable under this
fixed greedy policy from at least one phase-0 prior-price state. It is not a
claim about every arbitrary guard history or every state reachable during
exploratory training. Keep common-fresh-cap, actual-terminal and this all-cap-
state classification distinct. Startup-only's arbitrary old guard-state cycles
can differ from its cap-start outcomes; do not transfer a post-cap floor to all
those old guard states.

Compare cycle means with the **same finite game's** independently checked
controller floor and the original absolute relaxed 95% target. For the periodic
conditions reuse/recheck the accepted K-specific saved-weight certificates.
For startup-only, derive and independently check the upper-map sequence from
the actual physical cap and its post-cap limit under the saved monotonicity
premises; scope any resulting floor to admissible cap-first histories and their
continuations. If a premise is unresolved, retain an unavailable floor rather
than substituting the periodic or continuous guarantee. No continuous-target
normalization, learned-pair equilibrium or unrestricted-learning guarantee is
inferred from these comparisons.

## Primary paired contrasts and uncertainty

There are four primary strata: two market labels by two initializations. Within
each stratum, for each of the 12 seed IDs subtract startup-only's final actual-
continuation cycle-mean customer benefit from selected95's corresponding mean.
Keep all 12 matched differences, including zeros, reversals and failures. Report
mean, median, range and a whole-seed paired 95% percentile interval using the
pre-generated **5,120 by 12** bootstrap-index matrix, analysis seed 20261026.
Use the same resample-index vectors for all strata; do not resample firms,
rounds, checkpoints, graph states or cycles as independent units.

Freeze `ADAPTIVE_ANALYSIS_CONTRACT.md`, `adaptive-bootstrap.js` and
`adaptive-bootstrap-indices.json` before training. The declared matrix SHA256
is `8fd7455251b3d7faa50ad0125672ab5f0adfa8763a78988d41575a25af05cfbc`.
These are marginal seed-variation intervals, not simultaneous inference,
empirical-market confidence or a guarantee with only 12 seeds. No significance
test, favorable-seed filter or formation-conditioned primary estimate is planned.
Do not pool the four strata as 48 independent markets.

Other controller contrasts, initialization differences, checkpoint changes,
terminal training means, both profits/prices, target/floor gaps, allowed-mask
geometry and all-state cycle distributions are secondary/descriptive. A zero,
small or unfavorable contrast is a valid result. Do not claim convergence from
similar checkpoints, collusion from high prices, or meaningful flexibility from
100% legal masked actions alone. Inspect all reported distributions and visit
coverage before describing practical effects.

If any primary seed is unresolved, retain it and report incomplete primary
coverage; do not silently bootstrap the surviving subset as the planned n = 12.
No outcome-dependent extra training, alternative seeds or hyperparameter search
is part of this protocol.

## Freeze, execution and independent falsification

Freeze new source/tests/protocol/analysis dependencies, both raw finite games,
their masks/reward/cap identities, accepted finite numeric/rational audit
receipts and live auditors, effective recurring period/target journals, all
live transitive source/input hashes, and the verified prior V8 delivery receipt.
Verify an available prior archive against its receipt but do not require a
nested archive inside a portable extracted package. Root must confirm the
delivery identity before numerical GO. No first training step precedes the
accepted source snapshot.

Start/finish journals retain all 192 identities, failures, resources and output
hashes. Any existing execution journal, checkpoint, result, index, completion
or run-start prevents destructive rerunning. Catch pre-run identity/condition
failures inside retained planned records. Verify frozen dependencies again at
completion, preserve errors/overruns, and never edit frozen code or evidence to
make an audit pass.

Synthetic tests must distinguish simultaneous versus sequential settlement,
both seller coordinates, current versus prior rival indexing, current versus
next-phase support, cap replacement, startup-only phase absorption, continuing
Q targets, optimistic/zero initialization, ties, singleton masks, random-draw
pairing, cached maxima, exact count encoding, checkpoint resume and malformed
input/partial-run refusal. Include a known toy stationary competence problem
without representing it as market formation evidence.

An independent Python auditor imports no primary learner/search functions. It
reconstructs every reported checkpoint's masked argmax from binary64 Q, verifies
all policy bytes and visit-count flags, rebuilds the complete joint graph and
every exact saved-weight cycle/trajectory metric, rechecks finite floor/target
comparisons, and independently replays the declared checkpoint probes. Shared
floating-point/PRNG/library limitations must be disclosed. It does not claim a
full independent training replay unless one was actually completed. Independent
corruption tests must reject at least a forbidden policy action, altered Q/
argmax identity, wrong B-state orientation, wrong clock/start, inflated cycle
reward or floor/target comparison, and a changed visit-support/probe record.

Derived analysis, UI, report and packaging remain gated on complete journals,
passed independent exact identity bindings, final dependency checks and honest
scope. No presentation or human experiment is required to be invented in order
to finish this numerical study.


## Portable primary file contract

The read-only `preflight` command validates actual inherited schemas, hash-bound
audit receipts, closed target/period identities, the fresh-seed inventory and
available V8 archive. It neither freezes sources nor trains an inherited game.
Only after prospective source review and numerical GO may `freeze` save the
source/input manifest, then `run` execute its fixed 192 retained identities.

Each `records/<id>.json` retains controller, game, seed, Q initialization, status,
failure, two checkpoint receipts, approximate 10,000-round training curves and
self-contained sampled updates (first 16 and absolute steps divisible by
100,000). These sampled updates and the cloned probes are diagnostic checks,
not a full independent training replay. Failed loading or checkpoint writing
retains the planned identity, actual main round count and completed artifacts.

Each checkpoint folder contains `Q-A/B.f64le`, `counts-A/B.u16le`, masked-greedy
`greedy-A/B.u8`, two source-to-executed-pair `window-0/1.u32le` files,
`graph.json`, `probe.json` and `metadata.json`. Metadata binds every artifact's
relative path, byte count and SHA256, state/layout/actor identities and exact
overflow counts. A uint16 count saturates at 65535; each larger total is retained
as its exact integer in `countOverflow`. Window entries are sorted uint32LE
key/count pairs, with `key = sourceJointState*n*n + executedA*n + executedB`.
The two windows have fixed absolute boundaries; the first window is retained
unchanged at the later checkpoint. The completed current window has exact
saved-weight payoff/price/mask averages and integer max-allowed/cap counters.

Actual endpoints must pass their clock-specific cap-first invariant: at step
zero the highest old history is unearned; after positive step t the phase must
equal t modulo K, and both previous quote indices are at most
`U^((t-1) mod K)(capIndex)`. Startup-only instead has absorbing phase 1 and
bound `U^(t-1)(capIndex)`. The exact number of cap executions is checked too.
An invalid actual endpoint is an error, not an arbitrary-state basin finding.
This does not remove cap-unreachable old guard cycles from the complete graph.

`graph.json` hashes every successor, cycle label and transient-distance array;
cycle IDs are their smallest original joint-state index. Every cycle retains
exact payoff/geometry means, training visit support and applicable floor scope.
Actual-terminal and fresh-cap trajectories remain distinct, including their
finite prefixes and full recurring cycles. A 128-execution preview is explicitly
incomplete. Checkpoint resume verifies the binary/layout identities, rebuilds
masked maxima and matches full saved Q/count/cache/actor/window identities.
Existing run-start, journal, record/checkpoint directory, results, index or
completion prevents rerunning into an evidence directory.
