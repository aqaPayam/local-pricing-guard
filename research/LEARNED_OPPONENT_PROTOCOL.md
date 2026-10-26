# Prospective audit of responses to frozen learned opponents

Draft preparation only, outside the immutable V10 payload. This document does
not authorize a new inherited-market MDP calculation, source freeze or run.
Root has closed Goal 8 and activated Goal 9. It must still accept primary and
independent source/tests and give explicit execution authorization. New source
imports and artificial tests must not read inherited numerical evidence.

## Question, population and prior work

From the saved final training state, can one seller increase its discounted
private expected profit by changing its policy while its original learned
opponent stays frozen? The original guard, physical cap, legal prices, payoff
tables and controller clock remain unchanged. This is a known finite-MDP
response audit, not another learning run, intent test, equilibrium claim or
new optimization algorithm. Frozen-policy pricing responses are prior work;
the mandatory `LEARNED_OPPONENT_CONCEPT_REVIEW.md` and root's prospective
`LEARNED_OPPONENT_ANALYSIS_CONTRACT.md` govern the interpretation and citations.

The fixed targeted matrix is **48 retained labels**:

- One saved game: `base-g15-t1`, the original tolerance.
- One initialization: zero Q values in the closed training study.
- Twelve original whole-market seeds: `907001..907012`.
- Two original controllers: `startup-only` and `selected95`.
- Both focal sellers: A and B.
- One original checkpoint: final 2,000,000 main training rounds.
- One mathematical audit discount: gamma = 19/20.

Use stable seed, controller (`startup-only`, `selected95`), then focal-seller
(A, B) order. Preserve duplicates and all unavailable/budget/loose results.
The selected95 controller is the actual saved **K=4** controller inherited from
the earlier continuous95% identity. It is not the finite K=5 best fixed timing
from Goal 8, and no mixed-credit clock is substituted. Startup-only retains its
two original phases: phase0 transitions to absorbing guard phase1, which never
returns to phase0. Every selected terminal checkpoint is already post-startup.

This stratum was chosen after earlier welfare results were known, before any
new response computation. It is not preregistration before the full project.
The sellers/controllers of one seed are dependent counterfactuals; there are
12 whole-market seed identities, not 48 independent samples. Root's contract
specifies descriptive complete-matrix counts and seed means, with no new CI,
p-value, horizon/seed selection or outcome-dependent matrix expansion.

## Full state, simultaneous decisions and saved policy reconstruction

World state index is `(phase*n + previousA)*n + previousB`. It represents the
completed public state **before the next execution**, with n unchanged original
price indices. Include every phase and previous-price pair, including cap
histories that the actual terminal trajectory will never visit.

At phase0 either seller may choose every original index0..capIndex; this cap
replaces the guard. At a guard phase a seller's support is exactly the saved
set S(previous rival). No proposal clipping, extra action, new tolerance or
changed numerical comparison is introduced. All saved finite game weights and
supports are reused through their accepted audit/index hashes; this stage does
not re-enumerate the economic formulas.

Reconstruct both firms' masked greedy actions directly from the original saved
binary64 Q files. Compact Q rows are focal `(phase, ownPrevious, rivalPrevious)`;
legal cells are in ascending original action index. A lookup uses the world
row directly for A and transposes previous A/B for B. Choose the smallest legal
original index on exact binary64 Q ties. Reject nonfinite cells, bad lengths,
incorrect offsets or malformed count-overflow identities. Saved greedy bytes
can be cross-checked but cannot replace reconstruction from Q.

The opponent chooses its reconstructed greedy quote from this completed state.
It does not observe the focal seller's current simultaneous action. For each
permitted focal action, form the original executed pair (a,b), earn the focal
reward from `profitA[a*n+b]` or `profitB[a*n+b]`, and advance the original phase
and full pair. Seller B's reward lookup is already in world orientation; do
not transpose it a second time. A cap can change the price constraints without
resetting the learned opponent's history-dependent policy or continuation.

The baseline is both original masked greedy policies in this same MDP. Start
baseline and proposed response at the exact stored terminal history and NEXT
execution phase. Verify the closed step/phase and cap-first endpoint invariant.
No fresh cap, preceding training reward, reset value, Q update, exploration or
message is introduced. The first audited reward is the next actual executed
pair. The old full training trajectory remains not independently replayed.

## Proposal iteration and deterministic final policy

Use synchronous Jacobi binary64 value iteration, initially v=0 at all world
states, with numerical gamma19/20 evaluated as binary64 for proposal generation
only. Evaluate all legal actions against the fixed opponent. Ascending action
order with strict `>` gives the lowest original index on binary64 score ties.
There is no warm start from a favorable previous response or selected state.

Stop proposal iteration at the first of:

1. A completed sweep with max absolute value change <= 1e-10.
2. 600 completed sweeps.
3. The supervised 300-second per-case hard budget.
4. A retained invalid/nonfinite computation or input failure.

A floating difference or stable vector is not a convergence certificate.
Quantize each final completed binary64 value to the nearest multiple of2^-32,
with exact ties-to-even on its binary64 rational value. Quantization itself
uses integer arithmetic, not a rounded decimal serialization.

The final response is the **exact** one-step greedy policy with respect to
this dyadic vector: maximize q*R+p*Z(next) over every legal action, where rewards
and values share the exact denominator L below, p=19 and q=20. Ties use the
lowest original action index. The exact all-edge pass both selects these
actions and computes the residual. The independent audit must recheck this
all-state argmax claim, not merely legality or the realized path.

Retain a proposed response even if its achieved gain is negative. Do not
silently replace it with the baseline or label a failed proposal optimal.
The baseline is a separate legal lower-bound argument for the best possible
gain; it does not change the proposed response's raw achieved result.

## Exact achieved values and all-edge upper certificate

For each legal deterministic baseline/response, follow the full world state
from the actual terminal node until its first repeated state, at most N states.
Retain the complete transient of length h and one nonempty cycle of length c,
their closing state, source states, both executed indices, next states and
payoff indices. No arbitrary evaluation horizon or shortened cycle is used.

With exact saved binary64 reward rationals and mathematical gamma19/20, value is

    sum(t=0..h-1) gamma^t*r_t
      + gamma^h * sum(j=0..c-1) gamma^j*r_(h+j)/(1-gamma^c).

Implement an integer-polynomial/transient-cycle evaluation rather than
repeated floating summation. Bound paths by the complete N, not by a visually
convenient number of rounds. These are discounted infinite values, not cycle
mean profits or finite preview totals.

Candidate v has dyadic denominator2^32. Let L be the common power-of-two
denominator of all focal saved rewards and candidate values; lift r=R/L and
v=Z/L exactly. Inspect **every legal state/action edge**, including unvisited
and cap states, and save the signed maximum

    M = max_edges [20*R + 19*Z(next) - 20*Z(source)].

M is not clamped to zero. Save an attaining state/action witness and edge count.
For the actual start node s the Bellman supersolution gives

    U(s) = [Z(s)+M]/L >= V_star(s).

This is the standard one-sided Bellman residual bound, not a new theorem.
Independently check the scale, sign, every legal alternative and witness.
The response's gap bound U-V_response must be nonnegative exactly. A negative
value is a retained certificate failure, never a zero after rounding.

The requested gap is **1/1,000,000 absolute discounted-profit units**, checked
by exact rational comparison. A valid but larger gap remains a certified
feasible response with an explicit loose-gap status. A proposal timeout remains
a budget failure even if a separately completed certificate is informative.
Mathematical19/20 in this audit differs from the closed binary64 training
discount; there is no bitwise training-objective replay claim.

For every available case keep baseline value, response value, raw gain, U,
response optimality-gap bound and the possible best improvement interval
`[max(0, raw gain), U-baseline]` separately. Its upper endpoint is nonnegative
because baseline is a legal response. Relative raw gain is available only for
strictly positive exact baseline; otherwise give null and its reason.

One prospective secondary welfare diagnostic uses only those already replayed
paths: exact eventual-cycle customer-benefit means for baseline and response,
and their signed response-minus-baseline difference. Sum the unchanged saved
CS weights over each path's cycle positions h..h+c-1 and divide by its own
cycle length. Retain both exact means even when their cycle lengths differ.
This is a cycle average, not private-profit PV, a finite-prefix guarantee or
a learning effect. It never selects a response, breaks a tie or changes a
solver setting. Unavailable paths retain null and a specific reason.

## Training support and economic exposure

Use the original saturated uint16 counts plus exact overflow map; do not infer
visits from Q values or the new response path. For each source state in the full
h+one-cycle witness and each firm, retain original state visit count and count
for its newly selected action. This includes the focal response action and the
opponent's reconstructed greedy action. Summary counts distinguish unvisited
source states from never-tried selected actions. A cycle counted once is not
a long-run occupation fraction.

For baseline and response, additionally calculate EACH firm's exact normalized
discounted exposure to unvisited states and never-tried chosen actions:

    (1-gamma) * sum(t>=0) gamma^t * binary_indicator_t.

The deterministic indicators repeat with the same cycle and use the same exact
transient/cycle evaluator with reward denominator1. Save canonical exact hex
rationals and verify each lies in [0,1]. This distinguishes a remote unvisited
state from an economically material early exposure. Do not predict how the
opponent would behave after resuming learning or extrapolate a path's coverage
to competence at every state.

## Prospective storage, budgets and failure retention

Primary output is `research/learned-opponent-results/`. It contains a manifest,
exclusive execution-start receipt, per-case started/finished journal, all48
record identities, indexed files, final aggregate/completion and dependency
recheck. Refuse any partial or completed execution directory. Every planned
label survives per-case metadata/loader/solver/certificate failure with null
unavailable fields, exact error reason and available partial artifacts.

Use one isolated Node process at a time, supervised by the Python outer runner.
The parent enforces a 300-second monotonic wall deadline per case and kills
only its own Popen-created PID if it has not completed. This covers
input load, proposal and exact certification, not just cooperative polling in
the synchronous solver. Record actual measured duration/termination overhead;
never claim exact timer resolution. Artificial busy-loop termination and
next-case continuation must pass in this sandbox before execution GO. A `done`
message is only a marker: execution success also requires natural exit code 0
within the remaining deadline. A post-marker stall or nonzero exit is retained
as an execution failure. Thread termination was rejected before freeze after
two artificial native V8 crashes; their source/log history remains in
`.local/learned-worker-termination-history/`, outside accepted scientific data.

Keep only the latest fully received completed proposal vector in parent memory
for timeout preservation; do not store all intermediate iterations. On timeout,
retain that vector with its actual iteration identity, if available, and all
already written case artifacts, but do not invent a completed certificate.
The child atomically replaces one proposal file at sweep 1, every 25th sweep,
and a stopping/final sweep, then emits a small hash-bound progress message.
It waits for parent acknowledgement before replacing this file. The parent
holds only the latest fully received, hashed proposal bytes; an unacknowledged
file is not a received proposal. A reader thread timestamps each complete line;
the main parent separately records completion of all bound-file validation.
Deadlines are checked at message boundaries and after synchronous validation.
Preserve iteration count, stopping reason and measured times for every label.

Retain orthogonal `executionSucceeded` and `scientificAvailable` flags. A hard
timeout stays `retained hard-budget timeout` and executionSucceeded=false. It
can have scientificAvailable=true ONLY when the complete bound final f64,
dyadic vector, response policy, both complete paths and all-edge certificate
report were already fully received and hashed before termination. The
independent auditor must check that entire report even on a budget-failure
label. The same availability rule applies to a later nonzero exit or process
failure, which remains an execution failure. There is no post-timeout or
post-failure mathematical salvage from a partial vector.
Incomplete work keeps artifacts but null performance fields with reasons.
Count budget/execution failures separately from available certified results;
never relabel a timeout an optimized success. Derived gain summaries retain
all scientifically available labels, with status subgroup counts, and a seed
mean requires both seller values. Artificial tests cover timeout both before
and after receiving a complete certificate.

Soft total targets are two hours, 512MB approximately paired process RSS, and
250MB new primary output. Node reports its own RSS at progress milestones;
Python samples its parent RSS with the standard Windows process-memory API.
Keep both measurements and their approximate paired sum, which is neither a
simultaneous continuous peak nor unique physical memory (shared pages can be
counted twice). Retain explicit missing-measurement reasons if unavailable.
Report overruns. Continue all planned labels without dropping difficult seeds.
Only one case process may be live; the complete loop must continue after a
retained failed/terminated case. No paid process, model inference or training.

Exact integers are bounded prospectively at1,000,000 bits per scalar. With
N<=15,376, gamma19/20, finite binary64 rewards and the declared quantization,
transient/cycle and difference expressions are far below this generous bound;
check it before serialization and retain a failure if exceeded. Do not shorten
paths or change precision to force a pass. Common integer weights and dyadic
candidate vectors remain exact. No fixed-width arithmetic may assume away
overflow of a lifted reward or residual.

A conservative size bound can be checked before expensive arithmetic. A
binary64 reward has dyadic denominator at most 2^1074 and a common integer
weight below 2^2098 in magnitude. With h+c<=N and 20^N<2^(5N), the deliberately
loose bound in root's `LEARNED_OPPONENT_THEORY.md` is
`8*N*5 + 8*4096 + 16384 <= 664192` bits at N=15,376, below the 1,000,000-bit
ceiling. Validate matrix/path dimensions first; check conservative operand-size
bounds before each growing product/power. Malformed external certificate
scalars do not gain permission to allocate unbounded intermediate products.

Apply bit budgets when parsing vectors/scalars, before constructing a BigInt
from an overlong hexadecimal token, and before potentially growing powers or
products. Do not wait until serialization to reject oversized input. The
candidate's dyadic numerator additionally has a4096-bit parse limit, generously
above any finite binary64 value scaled by2^32. Check path length before forming
discount powers; check conservative operand-size bounds before products.

Canonical exact scalar schema is
`{numeratorHex:'-0x...' or '0x...', denominatorHex:'0x...'}`: lowercase, reduced,
strictly positive denominator and zero encoded0x0 without negative zero.
These strings avoid Python's decimal-digit conversion ceiling. Parse an
explicit minus sign separately: JavaScript BigInt('-0x1') is not a valid direct
conversion. Approximate
displays are optional and never sign authority. Save the candidate vector as
one canonical signed hex numerator per world state, final newline, denominator
2^32 declared once; also save the final completed unquantized proposal as
IEEE754 f64LE so every ties-to-even quantization can be independently checked.
Save the response policy as original-index uint8 actions. The independent
audit reports `optimizerIterationsReplayed:false`; checking this final vector
and exact certificate is not a full value-iteration replay claim.
Hash all artifacts and retain dimensions/encoding/source identities.

## Input closure and independent acceptance

Bind all selected final Q/count/overflow/metadata artifacts, finite games,
closed adaptive manifest/index/completion/audit and their source/input closure.
Require the accepted V10 archive receipt and verify an available archive by
its exact hash; portable copies need not nest the old ZIP. Before freeze,
administrative schema/hash inspection may identify files but may not solve or
interpret any new MDP. Source imports must not trigger evidence reads.

Freeze primary/protocol/tests, analysis contract, conceptual/prospective review,
complete independent auditor/tests and transitive numerical sources before
the first case. The independent implementation reconstructs masks, Q argmax,
seller orientation, original clock and terminal identity without importing
new primary MDP/solver/path/certificate code. Accepted old numerical payoff
audits are reused through explicit bindings; no new economic enumeration is
required. State that distinction and `fullTrainingReplay:false` accurately.
The authoritative audit defaults to stdout; an optional `--output` must create
a new receipt exclusively and refuse an existing path. It must never overwrite
an accepted receipt in order to make a rerun appear to pass.

The primary completion keeps `inventoryComplete`, `primaryPassed`,
`retainedRecords`, `executionFailures`, `budgetFailures`,
`scientificallyAvailable`, `tightCertificates`, `looseCertificates` and
`finalFrozenDependencyCheck` separately. primaryPassed requires complete
inventory, unchanged dependencies and zero execution failures; independent
acceptance can still validate a complete honestly retained failure record.

Artificial tests must cover full cap-history dependence, B transposition,
simultaneous no-current-action peek, startup absorbing guard, original K=4,
discounted transient/cycle versus a misleading mean, negative rewards/raw gain,
zero/nonpositive baseline, exact negative residual, quantization/ties,
unvisited/never-tried action coverage, late versus early discounted exposure,
partial failure/all48 retention, >4300-decimal-digit exact values, path bound,
process termination and write/refusal safeguards. Corrupt an off-policy edge
that raises the true maximum; checking only proposed actions must fail.

No outcome interpretation, derived export, report or new graphical player is
authorized until complete independent actual-data acceptance. A positive
achieved gain refutes exact unilateral optimality only against that particular
frozen opponent from that terminal state. It does not establish intent,
mutual adaptive stability, subgame perfection or a real-market claim.
