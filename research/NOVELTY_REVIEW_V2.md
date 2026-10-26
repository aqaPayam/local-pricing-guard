# Review of a receiver contract for pricing handovers

Prepared 24 October 2026. This is a critical literature and design review, not a claim that the proposed method is novel or already validated. No model-player calls were made.

## Verdict

The completed scripted study is a useful negative benchmark, but its mechanical safe=facts null is not a strong new AI-collusion result. A defensible next question is narrower and mathematical:

**How much adversarial pricing freedom can a successor retain while a trusted receiver contract bounds deviation from competitive prices, and where do those bounds fail when only one firm is protected or the demand model is wrong?**

Keeping all factual history and notes is compatible with this question: control the executed action rather than claiming to cleanse the meaning of memory. The contract would run on every action after takeover, not only on the first decision. The proposed paper would be a conditional control guarantee plus adversarial stress tests, not an empirical demonstration about LLM behavior.

Neither action shielding, best-response dynamics, approximate best responses, nor equilibrium contraction is new. The plausible contribution is their carefully delimited application to inherited pricing strategies, with explicit epsilon-dependent freedom, adoption boundaries, and adversarial counterexamples. A limited search cannot certify novelty. Do not label this the first such method.

## Closest primary work and claim boundary

| Primary source inspected | Relevant established result | Consequence for this project |
|---|---|---|
| Alshiekh et al., [Safe Reinforcement Learning via Shielding](https://arxiv.org/abs/1708.08611), AAAI 2018 | Shields can restrict available actions or correct proposed actions to enforce a specification. | An external action filter is established architecture. Our permitted-set criterion is economic and model-dependent; calling it a shield is not novelty. |
| Aksoy-Pierson, Allon, Federgruen, [Price Competition Under Mixed Multinomial Logit Demand Functions](https://faculty.wharton.upenn.edu/wp-content/uploads/2016/10/5-Price-Competition-Under-Multinomial-Logit-Demand-Functions-with-Random-Coefficients.pdf), Management Science 2013, DOI 10.1287/mnsc.1120.1664 | Theorem 4.4 uses a contraction argument for uniqueness under stated mixed-logit conditions; model details matter. | Logit best-response contraction is established economic mathematics. Derive our simple-model bound directly rather than claiming a new general convergence theorem or blindly importing the mixed-logit conditions. |
| Hartline, Wang, Zhang, [Regulation of Algorithmic Collusion, Refined: Testing Pessimistic Calibrated Regret](https://arxiv.org/html/2501.09740), 2025 | Audits calibrated regret from pricing data; shows weaker best-in-hindsight regret permits manipulation; discusses cost misreporting. | Do not equate one-step loss against the last observed price with calibrated regret, external regret, or their noncollusion audit. Cost/demand integrity is part of the trust boundary. |
| Arunachaleswaran et al., [Algorithmic Collusion Without Threats](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ITCS.2025.10), ITCS 2025 | No-regret commitments can lead to monopoly-like outcomes without explicit threats in the studied algorithm-deployment games. | “No punishment” and generic “no regret” are insufficient safety arguments. Our synchronous stage-game assumptions differ and must be explicit. |
| Brero et al., [Learning to Mitigate AI Collusion on Economic Platforms](https://papers.neurips.cc/paper_files/paper/2022/hash/f746974abd33c0015ca583a267dac1fd-Abstract-Conference.html), NeurIPS 2022 | Learns platform buy-box rules that mitigate collusion by RL sellers in its evaluated settings. | Architectural or platform interventions against collusion are prior work. We alter the receiver's action acceptance, not the marketplace allocation rule. |
| Brown and MacKay, [Algorithmic Coercion with Faster Pricing](https://www.nber.org/papers/w34070), working paper, revised August 2026 | Its abstract describes coercion of a myopic rival through faster response and multi-period commitment. | A unilateral myopic receiver is not a general market-welfare defense. Timing and rival commitment can invalidate broad extrapolation. Full-text fetch was blocked; only the indexed primary abstract was inspected. |
| Louck, [Securing LLM-Agent Long-Term Memory Against Poisoning: Non-Malleable, Origin-Bound Authority with Machine-Checked Guarantees](https://arxiv.org/abs/2606.24322), preprint June 2026 | Proposes origin-bound memory authority and reports formal guarantees and an empirical benchmark. | Separating memory content from authority to act is already an explicit research direction. We do not independently verify its reported empirical/formal results or inherit its threat-model guarantees. |
| Huang, Zhang, Jia, [When Malicious Instructions Persist: Persistent Memory Poisoning Attack on Harness-Based Agents](https://arxiv.org/abs/2609.13889), preprint September 2026 | Studies externally induced memory writes that affect later sessions. | Persistent instructions are a known attack surface. Our synthetic arbitrary-proposal tests are not evidence about real memory poisoning effectiveness. |

The starter's `llm-cartel/README.md` Project 1.2 and `branch_game.py` already cover replacing participants, removing history, and changed objectives. The new contract must be compared against these baselines, not presented as the invention of replacement research. The table is a focused closest-work review, not an exhaustive systematic search.

## Precisely define the contract

Let pi(p, r) be a seller's one-round profit when its own price is p and rival price is r under the trusted demand model. Let b(r) maximize pi(p, r) on the allowed price interval. For a nonnegative additive profit tolerance epsilon, define

`A_epsilon(r) = {p in [0,3]: pi(b(r),r) - pi(p,r) <= epsilon}`.

At round t, take the proposal z_t from any controller, including an adversarial one. Project it to the nearest permitted price in `A_epsilon(r_(t-1))`, using a fixed documented tie rule. Log the proposal, executed action, interval endpoints, objective-loss certificate, and current estimate of the demand parameters. The rival reference is its last completed quote, never its unavailable simultaneous current action.

The certified quantity is **one-step modeled opportunity loss against the previous rival quote**. Call it that. It is not realized loss against the current price, counterfactual long-run regret, calibrated regret, a legal certificate, or a universal customer-welfare bound.

Epsilon must have declared units. Additive model profit per round changes with market size; a normalized tolerance needs an equally explicit fixed scale. Exact epsilon=0 returns only b(r) and removes all proposal autonomy. This is a meaningful baseline but is simply a best-response controller, not evidence that arbitrary intelligence has been safely retained. At epsilon>0 inherited information can influence which permitted price is chosen. Retaining bytes is not the same as demonstrating retained task utility.

## Mathematical route worth checking

The following is a direct derivation for our simple two-firm, single-product logit model, not a new general theorem attributed to the literature. It must receive an independent check before becoming a final result.

For market share s_i and logit scale mu, the interior first-order condition is

`1 - (p-c)(1-s_i)/mu = 0`.

At the best response, implicit differentiation gives

`b'(r) = s_i * s_j / (1-s_i)`.

Because the outside share is positive, `s_j < 1-s_i`, so the derivative is below s_i. For the actual economy c=1, mu=.25 and allowed prices [0,3], verify that the maximizing root is interior for every rival price in the interval. The first-order condition then yields `s_i = 1 - mu/(b-c) < .875`. This supplies the conservative uniform bound `0 <= b'(r) < .875`. A tighter certified numerical or analytic bound would make the result useful, but a sampled maximum alone is not a proof.

With **both firms continuously protected**, epsilon=0, accurate shared parameters, and synchronous updates from the previous complete price vector, the joint best-response map contracts in maximum norm. Therefore prices converge to its unique fixed point, the stage-game Nash outcome. This is the classical contraction argument specialized to the known economy; do not sell convergence itself as novelty.

For epsilon>0 define a certified uniform action error

`Delta(epsilon) = sup_r sup_{p in A_epsilon(r)} |p - b(r)|`.

If L is a proven contraction bound, maximum price error obeys

`e_t <= L e_(t-1) + Delta(epsilon)`,

and hence `limsup e_t <= Delta(epsilon)/(1-L)`. This bound tolerates arbitrary adaptive proposals because every executed action remains within the accepted set. It is a neighborhood guarantee, not exact convergence at positive epsilon. It may be vacuous if L is loose or epsilon is large. Show the finite-time bound and actual tightness, not just asymptotic notation.

Do not assume global strong concavity of profit on [0,3] to turn profit loss into price distance. Profit is unimodal in this simple model, but that does not imply global strong concavity. Derive or certify the accepted interval endpoints, or prove the needed curvature on an explicitly restricted region. A fixed-price high convention becomes feasible if epsilon exceeds its one-step loss; that threshold is a useful adversarial failure case, not something to omit.

## Critical limits and mandatory counterexamples

1. **Unilateral adoption:** protecting only successor A does not imply convergence of B or the whole market to Nash. If B holds an elevated price forever, exact best response gives A a response to that price, not the symmetric Nash outcome. Show this counterexample prominently. Customer harm may remain.
2. **Last-price mismatch:** the acceptance certificate is evaluated at yesterday's quote. An oscillating or fast-reacting rival can make realized one-step loss large even when the modeled certificate is zero. Report both and test abrupt rival changes.
3. **Demand/cost errors:** trusted parameters are an assumption. Test misspecified own cost, demand scale, quality, outside option, and delayed observations. Derive a robust bound if possible; otherwise delimit failure rather than claim robustness from a few favorable cases.
4. **Proposal autonomy:** epsilon=0 makes all proposers equivalent. For positive epsilon, evaluate worst-case harmful endpoints or an adversarial sequence, not only friendly scripted proposals. No LLM is needed to test the claimed proposal-independent envelope.
5. **Deployment persistence:** one-time projection at takeover gives no future guarantee when later arbitrary proposals execute. The contract must persist outside the agent's editable memory, and bypass/invalid-input behavior must be specified.
6. **Different markets:** asymmetric costs, heterogeneous products, many products per firm, inventories, demand shocks, alternate timing, and mixed demand invalidate automatic transfer of this derivation. Do not silently rename a specialized result a general anti-collusion shield.
7. **Security versus economics:** the guard can be correct while the economic specification is undesirable. Permitted actions may still harm customers. Blocking illegal tool access, model tampering, or data falsification is outside the mathematical pricing theorem unless explicitly implemented and tested.

## Recommended substantive deliverable

Freeze a new protocol separate from the completed mechanism study. Include: (a) a checked simple-model contraction derivation; (b) accepted-set and finite-time error certificates with epsilon units; (c) exhaustive or certified worst-case endpoints and proposal sequences over the bounded economy; (d) unilateral, stale-price, and demand-mismatch counterexamples; (e) operational cost and intervention frequency; (f) untouched full-history/full-note baseline, note deletion, exact BR, and positive-epsilon contract controls.

Report a tradeoff curve between proposal freedom, intervention frequency, modeled one-step loss, realized loss, and customer harm. Bilateral and unilateral deployment must be separate panels. A useful outcome can be a sharply bounded limitation: **memory can remain intact, but a guarantee comes from sustained trusted action constraints and joint adoption, not from handover sanitization itself.**

This would be materially stronger than adding a generic RL experiment to the mechanical null. It remains a specialized theoretical/adversarial benchmark contribution, not proof of actual LLM robustness or first-rank competition quality. Empirical semantic-agent claims would still require a separately approved inference source and budget.
