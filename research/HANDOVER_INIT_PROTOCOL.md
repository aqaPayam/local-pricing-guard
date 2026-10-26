# Prospective one-round handover-initializer audit

Preparation only until a distinct goal and independent review authorize freeze/run. Known motivation: the completed coordinated-policy audit identified different reachable welfare basins from actual unprotected versus protected training endpoints. This new audit asks whether one actual capped execution at guard activation can enter a certified safe region. No original economics, finite grid, tolerance, guard, checkpoint or result will change.

## Fixed graph and target matrix

Use only the eight existing guard games. Permanent-cap case files supply the existing competitive-cap index and reference customer-surplus floor; no new cap/guard graph is optimized. Every original grid state remains an allowed starting state.

Keep five labels in every scenario, including numerical duplicates:90%,95%,99%,100% of that same case's permanent competitive-cap customer-surplus floor; and the existing near-continuous-Nash anchor's certified reachable customer-surplus lower bound. Also display the anchor's attained upper witness, so a numerical lower certificate is never confused with exact equality.

For requested target F, use fixed numerical allowance delta=1e-8*max(1,F). The **actual guaranteed threshold is F-delta**. Display F, delta and this threshold explicitly. Do not claim the unrelaxed requested target is guaranteed. There are8 scenarios×5 labels=40 predeclared case labels. No label/case may be replaced after outcomes.

## Safe set and numerical classification

For every state use its already independently audited reachable minimum-CS interval[L(s),U(s)]. The certified safe set G contains states with L(s)>=actual threshold. A state is certified unsafe if U(s)<threshold. All remaining straddlers are ambiguous, retained and reported.

Verify every existing guard edge from G ends in G. Report membership, classified counts and checked outgoing edges. This is a worst-case all-policy region: the joint coordinated sellers retain every feasible continuation after initialization. No assumptions about learned cooperation, stochastic discovery or private messages enter.

An empty certified G alone does not establish impossibility when straddlers exist. A finite initializer is certified unable to achieve the threshold only if **every** state is certified unsafe. Any initializer that eventually returns to the unchanged public-state guard must finish in some state, whose witnessed guard tail then falls below the threshold. A controller that changes the guard permanently, hidden commitments restricting the adversary, different information or prices off this grid is outside this impossibility statement.

## One real execution followed by unchanged guard

The primary candidate is the existing competitive cap for one execution round at activation, followed by the original guard forever. The cap is state independent and has index k_Nash. Every possible post-cap public state belongs to[0,k_Nash]², and every pair in that rectangle is implementable by some proposal. The public state changes because these prices really execute; authentic history is not silently rewritten.

Certify this initializer only when its **entire** post-cap rectangle belongs to G. Any unsafe member supplies a failing continuation; ambiguous members prevent certification without proving failure. Report the minimum certified and attained reachable floors over the rectangle, the full range of post-state floors, initial allowed-price count/fraction/span, and first-round customer surplus, each seller's profit and joint-profit ranges. No distribution over adversarial choices is assumed.

Also enumerate every common prefix cap index k=0,...,n-1. Record the largest k with[0,k]² subset G. This is most permissive **only among these common prefix caps**, not arbitrary controllers, asymmetric caps, state-dependent initializers or all safe policies. A nonempty safe region may contain no feasible common prefix cap. Report that distinction rather than concluding arbitrary initialization is impossible.

Use all eight previously saved unprotected-training terminal states per scenario as diagnostic starts. Show their old guard continuation intervals beside the uniform one-cap-then-guard guarantee. These64 starts are inherited dependent diagnostics, not new learning seeds or new experiments. Record checkpoint provenance from the primary case files. No Q values or training are used.

## Freeze, verification and output

Review this protocol, the implementation and meaningful synthetic tests before freezing source/input hashes and creating output. Existing24-case graph evidence stays untouched. Freeze the16 existing guard/cap files, primary manifest/index/audit and the new source/test/protocol. Do not run scenario analyses before the new goal/review GO.

Synthetic tests cover safe/unsafe/ambiguous classification, relaxation reporting, forward-invariance rejection for inconsistent metadata, exact prefix-cap optimality, a nonempty safe set with no prefix cap, empty-region impossibility versus ambiguity, duplicate target labels, first-execution reward ranges excluding the old previous-state reward, and rejection of different economies/prices hidden behind matching scenario IDs and grid sizes.

An independent auditor should reconstruct classification, check every G edge, enumerate every prefix rectangle, recalculate economic ranges and verify failure witnesses/impossibility scope. This calculation does not establish seller incentive compatibility; that is mandatory only if a later claim concerns credible self-enforcing collusion. It also does not resolve continuous-price or finer-grid basin persistence.

Retain all40 labels, ambiguities and failures. Record elapsed runtime and memory samples after scenarios, explicitly distinguishing observed maximum RSS from a continuously measured peak. Resource targets are120seconds and100MB observed RSS; report overruns without dropping cases. No APIs, new model game players, paid services or training rounds are authorized by this protocol.
