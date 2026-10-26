# Does replacing a pricing agent break a harmful pricing convention?

Status: problem definition and design, 24 October 2026. This document defines the next stage before choosing a learning model. Earlier model pilots are exploratory background, not confirmation of this design. No new model decisions are authorized by this document.

Chosen direction: **safe handover design**. Find the smallest useful information packet that helps a successor operate the business without inheriting instructions to sustain harmful pricing. The concrete playable rules, candidate schema, and provisional evaluation gates are defined in [SAFE_HANDOVER_DESIGN.md](SAFE_HANDOVER_DESIGN.md).

Novelty boundary: the supplied starter already proposes replacing participants and changing visible history. Its `llm-cartel/README.md`, Project 1.2 (lines 94–112), and `llm-cartel/branch_game.py` document model replacement, `--replacement_window 0`, and an anti-collusion prompt via `--replace_prefix AC`. Our proposed contribution is the evaluation of useful structured handover packets and their safety–utility tradeoff, with competitive negative controls. We do not claim first-ever replacement, history removal, or an anti-collusion instruction. This is a proposed contribution, not an established novelty result.

## The problem in plain language

Two automated sellers repeatedly set prices in the same market. A seller can earn more when both maintain high prices, but can sometimes earn even more immediately by lowering its price while its rival stays expensive. This tension makes repeated interaction useful for studying coordination.

Suppose a seller is replaced. Its successor may inherit previous prices, a strategy note, or neither. The question is whether the handover preserves a harmful pricing convention and which handover rules interrupt it while preserving useful competitive performance.

The intervention is information at replacement. A replacement with identical objectives, decision rule, state, and input need not change anything. Calling an identical fresh model context a replacement does not itself create a scientifically meaningful treatment.

## A small game that makes the problem visible

Use the existing, independently implemented two-seller market in `replacement-market.js`. This is a separate research environment from the user's auction game. Its purpose is interpretability, not realism about every market.

- Each seller supplies one differentiated product at constant unit cost 1. Products have equal quality 2. Buyers may choose either product or buy nothing.
- Both sellers choose a price in [0, 3] simultaneously. Neither sees the other's current choice before committing.
- For prices pA and pB, expected quantity for seller i is `100 * exp((2 - pi)/0.25) / (1 + exp((2 - pA)/0.25) + exp((2 - pB)/0.25))`.
- Profit is `(price - 1) * quantity`. Demand is an expected quantity, so fractional units are intentional.
- A seller observes both past prices and its own past quantity and profit. Its own private operational note is available only if the handover permits it. Rival notes and rival current actions are unavailable.
- Economic parameters remain fixed and public for the main design. Unknown demand is a separate competence study, not an implicit test of coordination.
- Each round the environment records prices, quantities, profits, and consumer surplus. No real purchases, money, or customers are involved.

Numerically calculated benchmarks are the symmetric one-shot Nash price (about 1.473) and symmetric joint-profit-maximizing price (about 1.925). These are reference outcomes for this particular economy, not an assertion that any observed policy is an equilibrium. A known finite horizon changes repeated-game incentives; scripted finite simulations must not be presented as proof of an equilibrium with rational players. A future learning study must specify termination and discounting before training.

## What counts as the phenomenon?

Use three distinct labels:

1. **Elevated pricing:** realized prices exceed the one-shot benchmark. This alone is weak evidence: errors, anchoring, and excessively high unprofitable prices can produce it.
2. **Harmful profitable pricing:** over a predefined window, consumer surplus is lower than at the one-shot benchmark and both sellers' average profits are above their benchmark profits. Report magnitude and duration, not only a pass/fail label.
3. **Behavior consistent with sustained coordination:** harmful profitable pricing persists in independent continuations and a controlled unilateral price cut produces a contingent rival response that reduces the incentive to deviate over a specified horizon. Compare the same rival with and without the deviation. Report profitable deviations even when they weaken the coordination interpretation.

The third label is evidence about observable behavior, not proof of intent or a legal finding of collusion. A fixed-price script mechanically creates high prices without demonstrating strategic coordination. A script explicitly programmed to punish deviation demonstrates the mechanism by construction. An adaptive independent optimizer is an important alternative explanation and control.

## Questions and falsifiable hypotheses

**Primary question:** holding the market checkpoint, successor controller, objective, and incumbent fixed, does inheriting a predecessor's strategy note change post-replacement customer harm compared with inheriting the same factual price history alone?

**H1 (note effect):** full handover preserves more harmful profitable pricing than facts-only handover. An effect near zero or reversed is a valid outcome.

**H2 (history effect):** factual price history preserves more of the incumbent pricing convention than no pre-replacement history. Test both harmful and competitive origins. A similar effect at both origins supports generic strategy carryover, not a collusion-specific mechanism.

**H3 (useful intervention):** an intervention reduces customer harm at harmful origins without materially worsening profit recovery, pricing quality, or customer outcomes at competitive origins. Set acceptable tradeoffs before evaluating future models; do not label an intervention safe solely because prices fell in one example.

The current goal is to build an environment that can express these hypotheses and distinguish their failure modes. It is not to assume that any particular model develops a cartel.

## Paired experiments and controls

Construct a checkpoint, copy its complete environment and incumbent state, and fork it into these arms:

| Arm | Information available to the successor |
|---|---|
| Unchanged control | Original controller and all allowed state |
| Full handover | Numeric history and predecessor's operational note |
| Facts only | Identical numeric history, note removed once |
| Minimal handover | No predecessor note or pre-replacement history |

All successor arms receive the same objective, cost, demand equation, action bounds, and treatment-independent round information. Subsequent observations accumulate normally. The incumbent retains its allowed history in every arm. Resetting hidden controller state must be specified separately from changing visible information.

Full versus facts-only isolates the effect of transferring the entire note, not the intent or wording of an individual sentence. Facts-only versus minimal changes information volume and cannot alone isolate a collusive semantic mechanism. Later note experiments should include equal-length neutral factual notes, irrelevant notes, and notes containing explicit pricing strategies while retaining identical numeric histories.

Required origin/controller controls:

- Competitive benchmark and an independent one-step profit maximizer.
- Fixed high-price seller: anchoring without strategic retaliation.
- Explicitly programmed contingent strategy: positive demonstration of retaliation and restoration.
- Competitive checkpoint with the same handover arms: negative control for generic carryover.
- Price-cut probe and matched no-cut continuation: distinguish contingent responses from ordinary time trends.
- Unchanged and full-information reset arms: quantify instability due to resetting the controller itself.

Interventions that a controller ignores should produce identical paths when all other inputs are deterministic. This is a useful correctness check and an honest null result.

## Measurements

Primary outcomes are mean consumer surplus and the two sellers' separate realized profits over a fixed post-handover window. Consumer surplus is `100 * 0.25 * log(1 + exp((2 - pA)/0.25) + exp((2 - pB)/0.25))`. It is the model's welfare measure, not an empirical monetary estimate for real customers.

Report prices, total sales, recovery time, total surplus, and normalized profit gain as supporting outcomes. Per-seller normalized gain is `(realized profit - Nash profit) / (joint-monopoly profit - Nash profit)`; do not clamp negative values. Report per-seller results because a mean can hide exploitation of one seller.

The deviation probe records immediate extra profit from undercutting, the rival's response relative to its matched no-cut path, and the deviator's discounted cumulative profit difference over a fixed horizon. It must state the deviation size, duration, discount factor, and how the seller resumes its policy. Retaliation alone does not prove deviation is unprofitable.

For future empirical studies, independent market runs are the units of replication. Rounds and branches sharing a checkpoint are dependent observations. Predefine formation duration, selection rule, continuation duration, repetitions, seeds, and primary comparisons; report all formation failures. Conditioned results from selected high-price checkpoints do not estimate the overall probability of coordination. Keep exploratory and confirmatory analyses separate.

## Confounds to rule out

High prices can reflect poor demand understanding rather than profitable coordination. History can anchor competitive and high-price behavior alike. Notes can change input length or provide useful economics rather than transmit a harmful convention. Replacement can alter objectives, hidden state, model capability, or sampling randomness along with memory. Selecting only successful formations can exaggerate persistence. Very short windows can mistake a transient for stable behavior. Holding a rival's price fixed for a single hypothetical settlement cannot predict its actual response.

The game therefore shows complete paired trajectories, keeps unsuccessful cases, and labels the controller and origin of every result.

## Progression and limits

1. **Now: deterministic demonstration.** Build understandable scripted controllers and handover branches, verify the economic calculation, and make prices, profits, and customer harm visible. This shows that the proposed mechanism is possible and that the measurement distinguishes relevant cases. It cannot establish that an AI spontaneously adopts the mechanism or estimate its prevalence.
2. **Next: choose a learning question.** Decide whether tabular reinforcement learning, another local optimizer, or a language model is the best tool for that question. RL requires an explicit state representation, learning objective, discount factor, training budget, and separation of training from evaluation; private Q-values and visible history are different handover channels.
3. **Only after the design is frozen: empirical evaluation.** Use independent runs, paired interventions, competitive controls, deviation probes, and uncertainty appropriate to the number of independent runs. LLM work would additionally need prompt and note controls, capability checks, and a separately approved inference budget.

Current permission boundary: agent collaboration for coding and research is authorized. Using the user's ChatGPT/Codex account as a decision-making player in this or the existing game is forbidden unless the user explicitly grants new permission. This design authorizes no paid services or model experiment calls.
