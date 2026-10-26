# Prospective independent review: learned-opponent incentives

Status: prospective source/test review complete, ready for root's administrative
preflight and source freeze. This is not numerical GO. The V10 report, UI and scientific evidence
remain unchanged. No inherited Q checkpoint, new MDP response or strategic
outcome has been read or calculated by this referee for this stage. This file
is not a source freeze, goal closure or numerical GO.

## Question and selected matrix

The proposed 48-label matrix is a useful targeted follow-up: one original
tolerance/economic calibration with zero Q initialization,12 saved market
seeds, startup-only versus the original selected95 controller, and both focal
sellers. The selected95 controller is the actual saved K=4 clock; the later
finite best-fixed K=5 and mixed calendar are different objects. Evaluation
continues from each final2M checkpoint's actual completed prices and NEXT
phase. It does not execute a fresh cap or award already-earned training profit.

Both sellers of a seed are dependent counterfactuals. Twelve whole-market
seeds, rather than24 seller rows, are the units for paired controller summaries.
The source-only analysis contract's descriptive signs/ranges/medians and12
seed-level seller averages are appropriate. No extra bootstrap, significance
test or general-market inference is justified by these exact policy audits.
The follow-up is selected after the old welfare findings but before inspecting
its strategic-response outcomes; it is not preregistration of the whole project.

Forty-eight labels are sufficient for this first, narrowly scoped question.
Expanding to192 after observing gains would weaken that prospective design.
A later separately frozen multi-stratum study remains possible if the
question, rather than a favorable outcome, motivates it.

The cross-controller gain contrast compares separately trained policy pairs
with different original clocks, legal experiences and phase-table capacity.
It is not a clock-only intervention on one frozen pair, an isolated causal
cap-frequency effect or an unrestricted capability control. Within one
checkpoint, baseline versus proposed response holds the opponent and game
fixed; that narrower unilateral policy replacement is the valid direct test.

## Independent mathematical checks

The world state is (phase, previousA, previousB). Both current legal supports
come from this completed state. The saved opponent chooses its masked greedy
action at this state before observing the focal seller's simultaneous action.
Periodic caps preserve both old prices in the Q observation. Startup-only
uses the complete two-phase graph, phase0 -> phase1 -> phase1, including
phase0 in the global residual even when the actual terminal is in phase1.

For seller B, the Q observation row transposes own/rival history. The accepted
profitB table is already indexed in WORLD executed-pair order A*n+B; it must
not be transposed again. Exact Q ties choose the smallest original legal quote
index. Proposed response actions and candidate values are world-state indexed.

The original focal greedy policy is a legal baseline in this same MDP.
A legal stationary response produces a deterministic trajectory with transient
h and cycle c in the FULL world state. Its infinite discounted value is the
exact transient sum plus gamma^h times the exact discounted cycle divided by
1-gamma^c. The first reward belongs to the next execution. A cycle mean,
truncated replay, phase-only closure or cap-block reset cannot replace this.
The mathematical audit discount19/20 differs from binary64 training gamma.

Let saved rewards and the quantized candidate vector share a power-of-two
denominator L, with rewards R/L and values Z/L. For gamma=p/q compute, over
EVERY state and legal action,

    M = max [q*R + p*Z(next) - q*Z(state)].

Then the all-state upper value is

    U(state) = ((q-p)*Z(state) + M) / ((q-p)*L).

M may be negative. This is a one-sided Bellman supersolution bound, not an
absolute-residual norm or a new theorem. The exact remaining gap U(start)
minus the attained response value must be nonnegative. U must also bound the
legal baseline. An exact one-step greedy response against final quantized Z,
using all legal actions and lowest-original-index ties, avoids float argmax
ambiguity. It still requires the independent upper-gap certificate.

Retain raw achieved gain even when negative. The best possible gain lies
between max(0, achieved gain) and U minus baseline because the baseline itself
is feasible. This argument does not silently replace a poor proposed response
with a successful optimized result. Relative gains need a strictly positive
baseline. The exact1e-6 absolute profit-PV gap target classifies a tight versus
loose certificate; it does not turn a finite approximation into an exact optimum.

## Numerical and runtime requirements before GO

Approximate value iteration is proposal generation: at most600 sweeps, final
candidate values quantized to2^-32, followed by exact all-action proposal and
residual checks. Save all candidate values and response actions, their encoding,
lengths, common denominator and hashes. A float residual or unchanged float
vector is not acceptance. Quantization must be specified deterministically.

The300-second per-case hard limit needs enforceable supervision of the actual
solver process, not a timer that cannot interrupt synchronous BigInt
work. Retain partial journals/artifacts and every planned identity on a kill or
error. The2-hour global runtime,512MB sampled RSS and250MB output limits are
soft and must be reported honestly if exceeded. No seed/sweep extension,
discount change or outcome-selected rerun is authorized. Resource sampling
must not be described as a continuously observed peak.

Execution success and scientific availability are orthogonal. A timed-out
worker remains a visible execution failure but may supply scientific values
only if its COMPLETE hashed f64/dyadic/policy/full-path/all-edge-certificate
bundle was received and checked before termination. A partial value vector
cannot be salvaged into a new primary certificate after timeout. Independent
checks cover every available bundle; summaries include scientifically
available values with their execution status intact, and require both sellers
for a seed mean. Source/event traces support the recorded receipt sequence;
they are not an independently authenticated wall-clock measurement.

Exact scalar hexadecimal numerator/denominator strings avoid Python's default
decimal integer-string ceiling. The full N-state path bound remains mandatory;
large exact cycles must not be shortened, silently truncated or represented
only by a hash. Budgets must cover writing/verifying those exact certificates.
Every baseline/response path's opponent coverage comes from original saved
counts with validated overflow reconstruction. Unvisited/off-path behavior is
a property of the frozen lookup table, not a prediction after resumed learning.
Keep unweighted full-transient-plus-one-cycle counts separate from exact
normalized discounted exposure, (1-gamma)*sum gamma^t*indicator, for each
firm's unvisited source state and never-tried executed action. The latter
lies in[0,1] and distinguishes unsupported far-future behavior from immediate
economic exposure; neither quantity is a causal attribution of the gain.

## Independent implementation and synthetic evidence so far

New files `research/audit-learned-opponent.py` and
`tests/test_learned_opponent_audit.py` contain an independent numerical core.
They import no primary MDP, optimizer, graph or exact-value helper. The closed
finite mask/reward tables may be reused through their accepted immutable audit
and hash bindings, with dimensions/legality rechecked; this referee does not
claim a new independent economic re-enumeration. New Q argmax policies,
world-state transitions, all-edge residuals and exact paths are recomputed.

Eighteen artificial-only core tests currently pass. They include signed/subnormal
binary64 conversion, large hexadecimal rationals, Q ties and cap-history
dependence, seller-B observation versus reward orientation, startup absorption,
exact transient/cycle values checked against separately solved dense rational
linear systems, every stationary policy of a small MDP below the certified
upper value, valid negative one-sided residual, a non-proposed action with
the maximum residual, wrong upper-bound-factor controls, retained negative
achieved gain, count-overflow/coverage checks and illegal off-path actions.
Discounted-exposure fixtures separately check a first-step unsupported
transient, a far-future absorbing unsupported cycle and alternating cycle
flags against closed-form rational values.
They also check exact signed ties-to-even proposal quantization, an exact cycle
whose rational denominator exceeds4,300 decimal digits, and secondary cycle
customer-benefit means excluding the transient and discount weights. Final
unquantized f64LE proposals will be retained so every actual quantization can
be checked without claiming to replay all value-iteration sweeps.
The endpoint fixture checks K=4 after1,2 and4 executions, including above-cap
last-completed quotes when NEXT phase is0, plus absorbing startup behavior and
rejection of wrong clocks/cap counts or out-of-envelope actual histories.

Two additional complete-file/process cross-audit tests, in
`tests/test_learned_opponent_cross_audit.py`, invoke the actual primary kernel
for both firms on an entirely artificial old-format checkpoint fixture. The
independent input loader and full-record comparator accept its saved f64,
dyadic, policy, full-path and Bellman artifacts. Sixteen scientific mutations
are rejected, including artifact edits with freshly recomputed artificial
hashes. Neither fixture generation nor audit reads inherited numerical data.
Production audit code imports no primary numerical helpers; the synthetic
generator deliberately calls the primary kernel to test interoperability.
The actual isolated-process path also passes for both focal sellers; a complete
scientific bundle followed by an artificial busy loop remains available while
execution correctly fails its shorter artificial deadline. Receipt ordering
uses strict event order and elapsed<=termination, allowing genuine clock ties.

The complete study-level adapter is now implemented. The two full-inventory
tests in `tests/test_learned_opponent_inventory_audit.py` pass:48 actual isolated
Node processes consume24 entirely artificial old-format checkpoint fixtures,
then the independent checker reconstructs all48 new records, full paths,
960 toy state-action edges, runtime/event/task chronology, record/index/journal/
completion bindings and exact seed summaries. Nineteen inventory/scientific
negative controls reject altered claims. Only the inherited-old-study premise
gate is mocked in this fixture; no NEW numerical or process helper is mocked.
This does not pretend to reproduce the old study's training or its audit.

The second fixture preserves all48 unavailable labels, null paired means and
three actual inventory controls, with zero numerical certificates. It also
verifies refusal to overwrite a closed audit receipt. A same-semantics file
edit during auditing is detected by the original-hash final recheck. All
consumed scientific artifacts are re-hashed before acceptance. The default CLI
is read-only stdout; optional --output exclusive-creates a new receipt.

Thus22 independent artificial tests pass across the three test files. The
primary's separate numerical/process and derivative tests remain additional
developer checks. No inherited Q/MDP outcome has been opened by this referee.
The dependency verifier itself is administrative metadata/hash/schema only:
it neither decodes Q nor constructs/solves an MDP. Root will run that actual
upstream-closure check after source freeze and BEFORE numerical GO. Actual
data acceptance will be recorded in a separate LEARNED_OPPONENT_REVIEW.md;
this prospective file must remain unchanged after freezing.

The first real administrative preflight, before source freeze or any numerical
case, rejected the historical boundary manifest: it declares its two source
digests in a legacy `hashes` map rather than modern `sourceHashes`/`inputHashes`.
A subsequent metadata-only recursive schema sweep also identified legacy
`sources` maps on four older manifests. Both the primary inventory and
independent verifier explicitly validate every present recognized map
(`sourceHashes`, `inputHashes`, `hashes`, `sources`) and those legacy
declarations and include their declared source bytes in the hash closure;
they do not accept arbitrary mapless manifests as opaque leaves. An artificial
test checks recognized legacy/modern maps, malformed digests, missing maps
and conflicting declarations. The prior artificial benchmark remains preserved;
a new versioned benchmark will bind the final corrected source identities.
This checks provenance bytes, not old boundary results or training behavior.

During source preparation an artificial worker-thread hard-termination test
produced a native V8 DisposeIsolate crash, despite earlier passing toy runs.
No inherited case had executed. This was treated as a real runtime blocker,
not cleared by repeating until one pass. Root approved a Python parent
supervising one isolated Node PROCESS per case instead. Only that Popen-owned
PID may be terminated. The reviewed final process tests cover busy/crashed
children, next-case continuation, normal exit0 versus a mere done marker,
closed stdout followed by a stall, duplicate certificates, partial progress
and late validation. The unsafe thread-based production run is disabled;
the real entry point is `research/run-learned-opponent.py`. The deadline uses
perf_counter, with elapsed/termination overhead retained. Windows parent
working-set and child-reported RSS form explicitly approximate paired samples;
they are neither simultaneous physical usage nor a continuous peak, and
unavailable readings have null values/reasons rather than invented zeros.

An artificial-only performance probe used15,376 states and62 legal actions at
every state,953,312 edges total. The independent complete exact Bellman pass
took5.57 seconds on this machine. These were synthetic weights/policies with
no inherited checkpoint or market input. This bounds neither the eventual
primary solver nor every exact-path cost; it is a feasibility check for the
planned independent audit, not a real-case result.

## Meaning and novelty

This is more consequential than another favorable fixed-grid sweep because
it tests the missing unilateral strategic property of the saved learners.
A positive exact attained gain rejects optimality against that specific frozen
opponent. A tight small best-gain upper bound supports only corresponding
terminal-state approximate optimality. Neither result establishes mutual
adaptation, every-state equilibrium, intent, deterrence or general prevention
of collusion.

The response audit is white-box/full-information: it knows the frozen rival
policy, complete payoff table and masks. It does not show that a competing
seller could discover the same response from a few observations. Any manual
display must retain the predetermined default and actual terminal clock,
separate finite executed profit from infinite values, and lock unavailable
benchmarks. If both responses for a checkpoint are unavailable, this new
receipt does not claim to have independently reconstructed that checkpoint's
Q/counts numerically; the current planned manual display locks it.

The separately declared secondary customer-benefit diagnostic is useful:
compute each already-certified baseline/response cycle's mean from the
unchanged saved consumer-surplus table and show their signed difference.
Exclude transient rewards and do not label this a discounted welfare value,
prefix guarantee or effect of learning. It must never select the response,
its ties or the displayed seed; differing baseline/response cycle lengths
are retained rather than matched by a convenient horizon.

Frozen-partner optimal policy deviations are already explicit in Lopes de
Moraes and De Losso, *Algorithmic Collusion Without Deterrence*, arXiv
2610.21867v2, Sections3.2(iv) and4.5. The accepted analysis contract cites this
close prior. Any addition here is the guarded phase-aware application and
independently checkable achieved-value/upper-gap evidence, not invention of
frozen-opponent MDP auditing or dynamic programming.
