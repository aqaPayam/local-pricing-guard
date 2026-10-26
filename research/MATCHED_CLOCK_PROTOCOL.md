# Prospective matched-clock learning protocol

Status: REVIEWED PROSPECTIVE PROTOCOL, 26 October 2026, Goal10, outside closed
V11. Root and independent source review accept the scientific choices below.
Source-only implementation and wholly artificial checks are authorized. Actual
matched-study training remains unauthorized until the final source-bound maximal
benchmark, source/input/runtime snapshot, independent administrative closure and
separate root numerical GO all pass. No new real matched-study Q or outcome was
read to define this protocol. Freeze these agreed choices before the first step.

## Problem and estimand

The earlier adaptive study compares complete enforcement/representation
packages: startup-only has an absorbing guard label, whereas recurring control
has a cyclic phase-indexed learner. This new comparison holds the observed
clock, allocated Q dimensions, initialization and training budget fixed. It asks
whether ongoing caps change learned-and-enforced outcomes under that common
architecture. It does not retrospectively identify why the old result occurred.

Use the one unchanged, original-tolerance finite game historically labelled
`base-g15-t1`: the accepted training game has **62 original quote indices**,
including its inherited physical cap. The historical label is not a 15-price
grid. Bind the exact old record, sparse-display index/manifest, both finite
audits and their live source/input closure before execution; import the saved
prices, masks and reward tables without new economic enumeration. No tolerance,
physical cap, reward, target or price grid changes are permitted.

Exactly 24 new training runs are planned: two arms times the twelve ordered seed
IDs 907001 through 907012. Both firms start at zero Q. Each run has 2,000,000
simultaneous rounds and checkpoints at 1,000,000 and 2,000,000. These are the same
seed namespaces used earlier, intentionally reused for a matched follow-up;
they are not fresh independent market samples or independent of the previous
study. The new architecture/run identity distinguishes this evidence from all
old compact checkpoints. Do not replace seeds, failures or negative results.
This is a staged follow-up designed after earlier project findings. Its source
freeze and display defaults precede the NEW matched-study training/outcomes,
not all prior project results; no public preregistration is claimed.

For each seed, the primary outcome is the recurring-minus-startup difference in
the final frozen-policy eventual-cycle customer-benefit mean, continuing from
each run's **actual final completed history and NEXT clock**. The primary summary
is the arithmetic mean of all twelve paired differences. Retain all twelve rows.
No confidence interval, significance test or bootstrap is planned initially. If
any required endpoint is unavailable, the planned twelve-pair mean is null,
with an explicit reason; any complete-pair description is secondary and labelled
with its numerator and denominator, never substituted for the primary estimate.

This is the total effect of the recurring-enforcement package with matched
clock/allocation: enforcement changes both learning experiences and constraints
during frozen continuation. It does not isolate policy formation from ongoing
execution control. Different masks, rewards, histories and visits induced by
the treatment are mechanisms of the comparison, not variables to equalize after
seeing outcomes. There is no unrestricted arm, equilibrium or collusion-formation
test, convergence assertion, model player, paid inference or new incentive audit.

## Common Markov clock and legal actions

Both arms expose exactly five public phase labels, with transitions

    0 -> 1 -> 2 -> 3 -> 4 -> 1 -> ... .

Phase 0 occurs once. In both arms it executes the actual inherited cap. In the
recurring arm, phase 4 also executes that same cap; in startup-only all phases
1, 2, 3 and 4 execute the original guard. Thus recurring cap executions are
1, 5, 9, ...; startup-only has one cap execution. The cap replaces the guard,
and permits original quote indices 0 through the inherited cap index. Guard
support is the original saved set S(previous rival index). Actual cap choices
can depend on the complete previous pair; no state-independent price reset is
assumed. Every original permitted quote remains a separate action.

At elapsed main-training step t, NEXT phase is 0 if t=0 and otherwise
`1 + ((t-1) mod 4)`. Both declared checkpoints therefore have NEXT phase **4**.
This label denotes a cap only in the recurring arm. Neither primary evaluation
gets a fresh phase 0 or a new history. Initial old memory is the highest original
pair `[n-1,n-1]`, earning no reward; execution 1 is the first reward-bearing cap.

The checkpoint cap count must equal 1 for startup-only and `ceil(t/4)` for
recurring, for t>0. With the accepted monotone upper map U and cap index A,
the actual completed pair is bounded by U^(t-1)(A) in startup-only and by
U^((t-1) mod 4)(A) in recurring; stop iterating once a fixed point is reached.
This validates the actual endpoint, not arbitrary old-history graph states.
The inherited cap-first floor may be reported only with its correct same-game
clock/history premises. No new guarantee follows merely from a learner outcome.

## Identical dense capacity and information boundary

Each firm allocates a Float64Array with **5*n*n*n** cells, indexed by
`(((phase*n + ownPrevious)*n + rivalPrevious)*n + originalAction)`.
At n=62 this is 1,191,640 cells per firm. Allocate an identically shaped Uint32
action-count array for each firm. All Q bits and counts initially equal positive
zero. Both arms allocate every cell, including actions forbidden in some rows;
neither arm uses a compact representation during training. Record allocation
counts/bytes and the mask identity in every checkpoint.

Selection, ties, next-state bootstrap and cache reconstruction enumerate only
that arm's legal support in ascending original-index order. Forbidden cells must
never be read for these operations and must never be updated or counted. Their
saved Q bits remain positive zero and counts zero. Their existence gives equal
allocated capacity, not equal usable support or equal effective training visits.
Do not interpret 100% accepted legal actions as strategic freedom; report mask
count/span and actual usage separately.

Each seller observes `(phase, own previous quote, rival previous quote)` and its
own deterministic saved expected profit. Seller B transposes completed-price
coordinates for its private rows; environment rewards retain original WORLD
order `profitB[a*n+b]`. Both current actions are selected before either update;
neither seller sees its rival's hidden current action, Q, random draw or internal
learning state. No communication, common profit reward, highest-price script,
sampled customers or stochastic reward noise is supplied.

The common clock is a Markov description of the external scheduling rule, not
a claim that each learning seller faces a stationary fully observed MDP.
Its observation omits the other learner's evolving Q table/internal state, so
the partner's behavior is nonstationary during joint learning. Matching the
finite clock does not justify Q-learning convergence. The deterministic joint
graph after both policies are frozen, and a separate known-fixed-opponent MDP,
are different mathematical objects from this simultaneous adaptive process.

## Binary64 update and paired random streams

Preserve the earlier scientific update and arithmetic order:

    target = ownReward + gamma * nextLegalMaximum
    newQ = oldQ + alpha * (target - oldQ)

where alpha is binary64 .1 and gamma is binary64 `19/20` (.95). Both next maxima
are evaluated on pre-update Q at the actual next clock/history and its legal
support. Caps are continuing transitions, never terminal resets. Ties choose
the smallest legal original action index. Caches are an optimization only and
require exact parity against a reference scan before freeze, including decreases,
ties, self-loops and changes in next support.

The source-level reference is `research/adaptive-learning.js`, current SHA256
`05fbcb4fe7c3b1993fdee40000a15b584f46662b227d9b46e097a8b0f5a2c535`.
This binds an expression/PRNG reference, not permission to mutate or reuse its
old compact learner as the independent new replay implementation.

At round index t=0..T-1, exploration is exactly 1 at t=0, .01 at t=T-1, and
`Math.exp(-Math.log(100)*t/(T-1))` otherwise, evaluated in that order. A cached
schedule is allowed only if its complete binary64 vector is independently
regenerated and bitwise equal. Freeze the Node executable hash, Node/V8 versions,
platform/architecture, OS release, expression order and execution flags. Node
executable path is provenance, not an equality requirement. Also freeze the
actual supervising Python executable hash, version/implementation and zlib
compile/runtime versions, without absolute-path equality. This does not formally
pin the complete OS or standard library. Same-runtime replay
does not imply cross-runtime/libm bitwise portability; mismatches are retained.

Use the earlier published xoshiro128** 1.1 transition and 2^64 jump, master state
`[907001,907002,907003,907004]`. Seed 907001+k uses jump segment 2k for A and
2k+1 for B. Save all 24 initial four-word actor states. Each actor consumes
exactly two uint32 words per round: exploration decision and support rank,
including greedy/singleton rounds. Both paired arms start with identical actor
states. Draw consumption cannot depend on mask width, ties or cache behavior.
At each checkpoint both arms' same-firm actor states must be identical and
equal independent 2*t-word advancement. Pairing does not force actions to match.
There are exactly 4,000,000 draws per actor per full run, below jump spacing.

## Checkpoints, counters and exact frozen evaluation

Retain complete dense f64 little-endian Q and uint32 little-endian counts at
both checkpoints, plus step, NEXT clock, completed pair, actor states, cap count,
mask/layout identity, sorted artifact hashes/bytes and software identity. Uint32
is sufficient because a cell count cannot exceed T=2,000,000. Each firm's global
count sum must equal the checkpoint step, with forbidden-cell totals zero.

Canonical artifact hashes cover the **uncompressed full dense byte streams**.
Portable gzip storage may compress those streams, with mtime 0 and saved
compressed hashes/bytes too. Inflation must enforce declared byte ceilings and
produce the canonical hash. Compression does not change live allocation.
Do not omit forbidden cells from the scientific checkpoint identity or introduce
an arm-specific sparse format. Cache files, if retained, have separate hashes;
independent reconstruction must equal them exactly.
Each closed checkpoint also binds both original OWN-coordinate and converted
WORLD-coordinate policy files, plus exact windowMetrics reconstructed from its
joint transition counts. The child emits the closed receipt and waits for the
parent's stdin acknowledgement before continuing; a rejected 1M receipt may
still be followed by a separately valid 2M checkpoint. No acknowledgement is a
substitute for scientific replay acceptance.

Before allocating or inflating, derive each exact raw length from the approved
dense dimensions and element width, and reject a different declared length.
Use bounded streaming decompression, reject extra members/trailing bytes and any
output beyond the exact ceiling, and require the final raw length/hash. A valid
gzip wrapper cannot waive raw little-endian or forbidden-zero checks. Saved gzip
byte hashes identify files; no cross-runtime compressed-byte identity is claimed.

At each checkpoint retain its preceding 100,000-round window: 900k..1M and
1.9M..2M. Save sparse integer joint source-WORLD-state/executed-pair counts,
explicit per-firm largest-permitted-action counters, cap executions and
exploration decisions. Reconstruct window benefit/profit/price and geometry
means from those counts with exact rationals of saved numerical weights.
Also retain fixed 10,000-round summaries, with any floating display sums clearly
labelled. Cap-rule frequency, executed-price changes and largest-action use are
distinct counters. Q=0 alone is never evidence of no training support.

Retain a streamed round-transcript hash for every fixed 10,000-round block.
Each record is exactly 120 bytes, unsigned integers and IEEE754 binary64 floats
all little-endian:

| Byte offset | Field |
| --- | --- |
| 0..3 | One-based main round index, uint32 |
| 4..9 | Six uint8: phase, previous A, previous B, executed A, executed B, exploration flags |
| 10..15 | Six reserved bytes, all zero |
| 16..87 | Nine f64: epsilon, reward A, reward B, old Q A, old Q B, next legal maximum A, next legal maximum B, new Q A, new Q B |
| 88..119 | Eight uint32: post-two-draw actor A's four words, then actor B's four words |

Flag bit0 is A's `u < epsilon` exploration decision and bit1 B's; all other bits
are zero. Include the decision on singleton supports, not merely an action that
differs from greedy. History/phase precede the transition; rewards and new Q
belong to its executed pair. Transcript capture consumes no additional draws.

Use one reused 1,200,000-byte buffer per 10,000-round block. Store SHA256 and
ordered one-based first/last round identities, then reuse the buffer: exactly
200 blocks/run, 4,800 across 24 runs. Keep each run's identity even if hashes
coincide. Checkpoint 1M binds the first 100 hashes; 2M binds all 200. Do not save
the full raw transcript. A failed run's incomplete tail is explicitly partial,
never substituted for a complete block hash. Primary uses Buffer writes and
the independent replay its own DataView encoder. Artificial tests bind a known
byte/hash fixture and reject field/order/flags/padding/block corruptions.
Benchmark all encoding/hash overhead at maximal artificial dimensions before
freeze; resolve infeasibility prospectively, without disabling capture after
seeing market outcomes.

Derive masked greedy policies directly from each checkpoint, without sampling,
updates or a `learn:false` routine that still explores. Build the complete
functional graph on 5*n*n WORLD states. Phase 0 has outgoing edges but cannot
belong to a recurrent cycle. Retain every cycle, basin/transient distances,
exact saved-weight cycle means (benefit, both profits and both prices), and
unvisited state/chosen-action flags. Identify the actual terminal trajectory
and the first 128 transitions as a truncated preview, not its exact endpoint.
The primary final-cycle mean is undiscounted, separate from Q's discount .95.
Arbitrary-state cycles and common-high-history/fresh-cap replay, if included,
are secondary diagnostics with their reset and reachability scopes explicit.

## Independent full-training replay: prospective acceptance gate

An independently authored JavaScript implementation must replay **all 24 runs,
all 48,000,000 main rounds**, from zero Q using the same frozen Node/V8 runtime.
It must not import the primary learner, phase/mask/update/cache/PRNG functions,
or read saved Q as an initialization. It independently reconstructs supports,
clock, actor streams, simultaneous update order and dense indexing from the
approved protocol and unchanged input tables. It may read recorded hashes for
comparison, not as numerical instructions replacing replay.

Compare every Q bit, count, actor state, actual history/clock, cap count and
window/counter identity at **both** checkpoints. Independently derive every
masked greedy action and complete graph/cycle summaries from the replayed Q.
Require entry/exit hash checks for all consumed inputs and evidence. Endpoint
acceptance is checkpoint-specific; inventory acceptance and the aggregate
complete-replay flag are separate. Never quietly fall back to probe-only
certification or call a same-source rerun independent.

The aggregate flag `fullTrainingReplay:true` requires all 24 planned runs to
reach 2M, all 48 checkpoint bit comparisons and graph checks to pass, and thus
48M main rounds actually replayed. Both aggregate `fullTrainingReplay` and
`replayComplete` are false if any of the 48 checkpoint comparisons is unavailable
or fails, even when every final endpoint is accepted. An honest complete
24-run/48-slot inventory may pass its audit with failed/missing 1M secondary
checkpoints, retaining actual replayed/matched round counts and every status.

A final 2M endpoint is scientifically accepted only if an independent replay
from zero reaches 2M and matches all 200 transcript blocks, final Q/count bits,
actor states, history/clock/counters and full frozen graph. A failed or missing
1M secondary checkpoint does not invalidate that separately accepted final
endpoint. The all-twelve primary mean is available exactly when all 24 final
endpoints are accepted, irrespective of secondary checkpoint availability.
If any final pair is missing, the planned mean remains null; accepted endpoints
may support an explicitly secondary available-pair description. A 1M endpoint
requires its own from-zero 1M replay and first 100 block/checkpoint comparisons.

Also compare all 200 recorded transcript-block hashes per complete run, from
independently encoded bytes. The scope is “all recorded round-transcript block
hashes and all checkpoint bits match.” This detects recorded mid-round changes
that could cancel at checkpoints; it is not externally authenticated per-round
logging, proof of every internal operation, or a replay of old studies. Both
encoders still share SHA256 and the frozen V8 numerical runtime.

This proposed full replay applies only to this new small study. It does not
retroactively certify the old 192-run training trajectories. No trained-state
clone probes are necessary when full replay passes; no extra post-horizon
learning changes the actual stored endpoint.

## Engineering bounds and pre-execution gates

Structural sizing alone, not a pilot outcome: at n=62 the pair of dense Q arrays
is 19,066,240 bytes and the pair of uint32 counts is 9,533,120 bytes. The combined
raw checkpoint is 28,599,360 bytes; 24 runs times two checkpoints is
1,372,769,280 bytes before graphs, counters, metadata and compression. Budget
1.75 GB of new raw-equivalent primary artifacts, excluding inherited inputs.
Record both canonical and actual stored bytes; do not promise a compression ratio.

Use one sequential primary process and subsequently one sequential independent
replay process, not concurrent training. Proposed soft targets are one hour
primary, one hour full replay, 512 MB sampled process RSS, and the above disk
budget. RSS is process-level sampled measurement, not a continuous/private peak.
Any serialization/inflation scratch memory and its samples count. Retain
overruns and failed rows. Do not truncate horizons, drop checkpoints or change
the matrix after outcomes. Record primary and replay elapsed/resource budgets
separately, along with raw-equivalent and actual stored bytes. If a Python parent
and Node child are sampled together, label their sum approximate paired RSS;
neither private RSS nor a continuous simultaneous peak is implied.

Root prospectively chooses one Python parent supervising one isolated Node
PROCESS per primary run and, later, per independent replay run. Each whole case
has a **600-second hard deadline**, including its two checkpoints, graph work and
parent receipt validation. Use structured Popen arguments without a shell. Kill
only the parent's own spawned PID at the deadline, retain its failure/partial
artifacts, and continue the remaining planned labels. A `done` message is not
execution success until natural exit zero within the deadline. Validate this
process/watchdog design in artificial tests and the benchmark before GO; no
native Worker-thread termination or favorable horizon/seed rerun is allowed.

Execution success and scientific checkpoint availability are orthogonal. A
checkpoint is eligible only after its complete closed gzip/raw-length/hash,
metadata, actor states and counters have been fully received and validated by
the parent before deadline/termination. The child closes/hash-binds artifacts
before emitting a receipt. Record monotonic receive/validation/termination times
and event order, checking the deadline again after synchronous validation.
Nothing first discovered or validated after timeout may be adopted as a
checkpoint. Partial vectors/receipts are retained as unavailable, without late
salvage. Before-termination event order is authoritative if coarse measured
timestamps tie; equal elapsed values alone do not reverse recorded event order.

A fully validated predeadline final checkpoint can remain scientifically
available despite a later nonzero exit/stall/timeout, only if independent full
2M replay subsequently passes. Its execution failure remains visible. A valid
1M checkpoint remains a secondary record if 2M is missing. Every planned run,
checkpoint and failure stays in the inventory; the primary all-twelve mean is
null if any final pair lacks accepted endpoints. No new training or extended
horizon is used to repair an incomplete run.

Before numerical GO require independently reviewed source/tests and an
artificial representative-dimension benchmark of the primary plus full replay,
including both checkpoint serialization and exact graph evaluation. Required
tests include dense/compact parity under the same artificial clock/masks,
negative/zero rewards, B orientation, cap full-history dependence, sealed
pre-update maxima, exact ties/decreases, forbidden-cell poison sentinels,
fixed draw consumption, phase0 nonreturn and executions1/5/9 caps, both
checkpoint clocks, portable gzip/restore, resumed-vs-uninterrupted bitwise
identity, count corruption and failure-retention/no-overwrite behavior.

Root must resolve any benchmark resource blocker prospectively. Then freeze
primary, independent replay, tests, protocol, analysis contract, runtime identity,
all transitive numerical inputs, complete 24-run plan and initial actor states
before the first main step. Retain all started/failure/completion journals and
final dependency checks. No source change or selective rerun follows outcomes.

## Approved choices and remaining feasibility gates

1. Accept full same-V8 replay as mandatory acceptance rather than promising
   cross-language bitwise equality; root/referee accept this scoped assurance.
2. Validate the raw-storage and serial primary/replay budgets and the selected
   600-second per-process watchdog on wholly artificial representative workloads.
3. Root/referee approve no CI initially: retain all twelve exact differences and
   their descriptive mean for the narrowly conditional primary comparison.
4. Root/referee approve the null planned mean on any missing final pair, with
   separate labelled available-pair descriptions and retained execution failures.

The scientific distinctions and design rationale are inherited from
`CLOCK_MATCHED_LEARNING_CANDIDATE.md` and
`CLOCK_MATCHED_LEARNING_CONCEPT_REVIEW.md`. The follow-up is an established
learning-method control with stronger execution assurance, not a new Q algorithm
or an originality claim.
