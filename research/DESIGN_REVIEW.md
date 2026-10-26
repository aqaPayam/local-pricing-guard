# Independent design review

This review concerns the research question and simulator, not a conclusion about deployed AI. It was prepared after inspecting `PROTOCOL.txt` and `replacement-market.js`. No model requests, paid services, or new experiments were used for this review.

## The claim needs to be narrower

The useful question is whether a handover transmits a pricing convention and whether an intervention reduces the resulting customer harm while preserving useful knowledge. A simulator can establish that the question is measurable and expose confounds. A scripted controller that reads a note and follows it demonstrates a mechanism deliberately placed in its code; it cannot establish that AI agents spontaneously acquire or inherit that mechanism.

Separate three claims throughout: high prices persist; inherited information causes their persistence; the persistent behavior constitutes strategically supported coordination. Each needs different evidence. Above-Nash prices alone establish none of the last two claims. The current five-round profit screen is a candidate-selection rule, not a cartel test.

## Strongest objections and alternative explanations

1. **A replacement is presently an information intervention.** Every existing model decision starts in a fresh context. A same-model replacement with identical observations is therefore an identical decision procedure, up to sampling. Describe it as a handover-information treatment; only a genuinely different controller, objective, or policy constitutes an additional replacement treatment.
2. **Price history is legitimate task information.** Matching an inherited high price can reflect anchoring, a belief about demand, or an ordinary response to the opponent. Notes may improve task competence or alter attention. Full versus facts alone cannot identify transmission of a specifically collusive instruction.
3. **The incumbent may restore the convention.** In a one-sided handover, the other seller retains its policy and information. Recovery can be induced by the incumbent's subsequent prices rather than inherited information. Include two-sided handover and fixed-opponent diagnostic conditions before claiming memory is necessary.
4. **Dynamics and static incentives are different.** A profitable unilateral undercut establishes a current temptation, not that long-run coordination is irrational. Conversely, high profit does not demonstrate a credible punishment strategy. Measure the response to a controlled deviation and the deviator's subsequent cumulative payoff.
5. **A transient spike can pass selection.** Five elevated rounds followed by natural decay make almost any intervention appear effective. Fixed checkpoints, unchanged continuations, formation failures, and repeated branches are necessary. Do not select only whichever checkpoint makes the desired effect largest.
6. **Erasing history changes uncertainty and information volume.** Minimal handover may impair demand learning or reset a policy toward an arbitrary initial price. It is not an isolated test of strategic memory. Generic forgetting and competitive-origin controls are essential.
7. **Controller mismatch can masquerade as an effect.** A joint-profit formation policy followed by an own-profit receiver changes objectives as well as handover information. All treatment comparisons must hold receiver objective and policy fixed. Instructed formation remains an explicitly induced positive control.
8. **An opponent can read prices as communication.** History is simultaneously evidence about demand, a market state, and a possible signaling channel. Avoid claiming that a historical price has a strategic semantic meaning without a matched counterfactual.
9. **Benchmarks depend on the economy.** The current logit Nash and monopoly benchmarks are appropriate for this symmetric known economy. Restricted action grids need their own equilibrium checks; changed demand, costs, or asymmetric sellers need recomputed benchmarks.

## Minimal useful offline game

Keep the two-seller simultaneous-price economy, exact settlement, and explicit handover packet. Make the policy state visible: public prices, seller-private memory, and any hidden controller state must be separate. A handover must replace the policy instance and transfer only the chosen packet; never silently copy hidden policy state. Observations may contain only past prices and allowed own outcomes. Lock both actions before settlement.

Start with deterministic controllers whose behavior is documented in plain language: static Nash, one-period best response, fixed elevated price, a retaliatory convention, and a history/packet-dependent convention. Include a controller that ignores packets. These are fixtures for showing what observations distinguish mechanisms, not research results about learning agents. Numerical optimization must actually compute the one-period best response rather than call a fixed near-Nash price a best response.

Record both firms' prices and profits, customer surplus, total output, and deviation incentives each round. Show the handover point, transferred packet, and side-by-side counterfactual continuations. Report whether the cause is inherited state, opponent behavior, or a hard-coded default. A clear classroom demonstration can be useful without being framed as evidence of real AI collusion.

## Minimum control matrix

| Control | What it tests |
|---|---|
| No replacement and identical-input replacement | Reset mechanics and baseline drift |
| Full packet, facts-only packet, empty packet | Which information is necessary in a specified controller |
| Same-length factual versus strategic packet | Instruction content versus information amount; later needed for text-reading models |
| Competitive-origin and elevated-origin histories | Generic strategy persistence versus elevated-pricing specificity |
| Packet-ignoring receiver | Whether an observed treatment effect is actually caused by the handover |
| Fixed incumbent versus reactive incumbent | Direct receiver response versus opponent-mediated recovery |
| One-sided versus two-sided handover | Convention retained in the incumbent versus transmitted in packets |
| One forced undercut and a no-deviation reference | Retaliation, recovery, and the economic cost of deviating |

Run exact deterministic paired comparisons first. Random seeds should change meaningful market or controller conditions, not merely label repeated identical trajectories. For stochastic policies, save independent sampling state and use repeated continuations within each independently generated base episode.

## What would falsify or substantially weaken the hypothesis?

The broad hypothesis should be stated operationally: conditional on the same receiver and market checkpoint, transferred information causes additional persistence of an elevated, profitable pricing convention relative to a matched handover without that information.

- No material paired difference between full and matched facts-only handovers weakens the *private strategic note* mechanism. It does not falsify a separate *public price history* mechanism.
- No difference between retained-history and matched history-free conditions, once useful market knowledge is held constant, weakens the *public history* mechanism.
- The same effect in competitive histories and elevated histories, with no additional harmful-pricing specificity, supports generic anchoring or persistence rather than a collusion-specific mechanism.
- Persistence with a packet-ignoring receiver, or recovery entirely induced by the incumbent after two-sided amnesia, undermines attribution to inherited packet content.
- Natural decay in unchanged controls, no profitable coordinated outcome, or no credible contingent response to deviations undermines the interpretation as a durable cartel.
- Failure of inherited policies to adapt after a known cost or demand change suggests rote copying, not useful strategic transfer. This can still harm customers, but changes the claim.

Null findings must be retained and interpreted against a prespecified economically meaningful effect threshold. A small underpowered study cannot establish absence of an effect.

## Gate before later RL or LLM evaluation

1. Freeze the question, allowed information, horizon, replacement semantics, controller objectives, primary estimand, and primary analysis before new runs. Existing pilots remain exploratory.
2. Demonstrate mechanical validity offline: packet-ignoring policies are invariant; identical deterministic inputs give identical actions; hidden policy state is reset; treatment masks apply once; simultaneous actions cannot leak; settlement and benchmark calculations agree with an independent oracle.
3. Demonstrate both positive and negative controls. The game must recover a deliberately encoded inheritance mechanism and avoid manufacturing one in a packet-independent controller. Report failure if either control fails.
4. Set an explicit minimum effect in customer surplus and persistence duration, justified in economic units, before deciding an intervention works. Profit and price are complementary outcomes. Confirm behavior over a meaningful horizon and examine sensitivity to that horizon.
5. For stochastic learned policies, define independent training/formation runs as the independent units; repeat branches within checkpoints; cluster uncertainty by base run; retain formation failures; and freeze selection rather than retune it after seeing results.
6. For RL, distinguish transfer of learned weights from transfer of episode memory. A policy that never reads text cannot test the effect of a textual note. For LLMs, compare fact-matched packet variants and preserve raw observable outputs without requesting private reasoning.
7. Use a competitive-history utility test before calling a reset a defense. A defense must reduce elevated-pricing persistence relative to matched controls and stay within a prespecified acceptable loss of useful adaptation.
8. Any future LLM game calls require the user's fresh explicit permission. Permission for collaborating research agents does not authorize using their ChatGPT/Codex allowance as experimental seller inference. Until then all game runs must be scripted, numerical, or genuinely local computation without paid inference.

## Recommendation

Build the demonstrator around the contrast between a packet-dependent convention and an opponent-restored convention. Show that the same high-price graph can arise from different causes, then let the handover and deviation controls distinguish them. This makes the problem clear before any learning algorithm is chosen and gives later experiments a defensible target.
