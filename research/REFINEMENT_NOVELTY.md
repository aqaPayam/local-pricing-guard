# Closest prior work for the continuous/refinement question

Reviewed 26 October 2026. This is a targeted primary-source comparison, not an exhaustive systematic review or a guarantee of originality. It reads the prospective `CONTINUOUS_REFINEMENT_PROTOCOL.md` and conditional `CONTINUOUS_REFINEMENT_THEORY.md`; it does not evaluate new scenarios, run a mesh, inspect prospective outcomes, train agents or alter frozen Goal 1/2 evidence.

## What the question actually adds

The strongest candidate contribution is **certificate transfer for a particular economic action restriction**: whether a long-run consumer-surplus guarantee obtained by one real capped execution on a finite price grid survives when the same price interval becomes continuous, and how the worst permitted continuation values approach their continuous counterpart.

Several broader claims are already prior work: price-grid sensitivity, initialization/exploration sensitivity, frozen-policy attractor audits, the inadequacy of high prices alone to establish collusion, action shielding, and approximation guarantees for continuous systems. We should not present any of those as discoveries of this project.

Keep three different meanings of “basin” separate:

1. A learning process's outcome as Q initialization, random seed or exploration changes.
2. Attractors of a **fixed learned policy pair**, as the initial public price state changes.
3. Reachability and worst long-run welfare under **all permitted policies** of a fixed guard, as the public starting state or a finite initializer changes.

The prospective theorem concerns the third object. The first two can motivate it but do not establish it.

## Eight focused primary sources

### 1. Baseline logit learning model

**Emilio Calvano, Giacomo Calzolari, Vincenzo Denicolò and Sergio Pastorello (2020), “Artificial Intelligence, Algorithmic Pricing, and Collusion,” American Economic Review 110(10), 3267–3297.** [Official article/DOI 10.1257/aer.20190623](https://www.aeaweb.org/articles?id=10.1257/aer.20190623); [institution-hosted December 2019 manuscript](https://www.tse-fr.eu/sites/default/files/TSE/documents/ExEdu/paper_1_calvano.pdf).

Inspected: official bibliographic record and manuscript model/learning specification, baseline price grid, initial Q specification, convergence discussion and rematching discussion. This is established independent-Q-learning evidence in repeated logit price competition. Its baseline uses 15 prices, with Q values initialized using uniform-rival discounted profits and a random initial public state. Our known-economy feasible-path calculation is not a replication of autonomous learning or a replacement test of its repeated-game strategy claims. The inspected manuscript is explicitly an earlier version; do not claim every final-version implementation detail was reverified here.

### 2. Granularity already changes learned pricing patterns

**Timo Klein (2021), “Autonomous algorithmic collusion: Q-learning under sequential pricing,” The RAND Journal of Economics 52(3), 538–558.** [Primary full text/DOI 10.1111/1756-2171.12383](https://onlinelibrary.wiley.com/doi/10.1111/1756-2171.12383).

Inspected: introduction, sequential-pricing model and price-grid comparative statics. Klein already finds that increasing the number of available discrete prices changes learned outcomes from stable high prices toward asymmetric cycling. His homogeneous-good, sequential-move setting differs from the simultaneous lagged logit guard here. Consequently “finer price grids change collusion” is not new. The prospective distinction is a theorem about an action correspondence's all-policy welfare values, rather than a granularity effect on a specified learner.

### 3. Initialization artifacts and a discrete/continuous benchmark distinction

**Calvano, Calzolari, Denicolò and Pastorello (2023), “Algorithmic collusion: Genuine or spurious?,” International Journal of Industrial Organization 90, article 102973.** [Publisher/DOI 10.1016/j.ijindorg.2023.102973](https://www.sciencedirect.com/science/article/pii/S0167718723000541); [institutional accepted manuscript](https://cris.unibo.it/bitstream/11585/952593/4/True_Or_Fake_IJIO_Revision%2Bsubmitted.pdf).

Inspected: exploration definitions and §§2.2–2.3. This paper distinguishes optimistic Q initialization from random exploration and discusses supra-competitive outcomes without the intended strategic mechanism. It also explicitly contrasts continuous-price competition with a one-grid-step-above-cost outcome; footnote 6 reports a finer 100-price check. Thus neither initialization sensitivity nor a discretized benchmark's disappearance under refinement is generically new. Our one-execution public-state initializer is a different operation from initializing a Q table, and must be named accordingly.

### 4. Continuous logit pricing and best responses are established

**Thomas Loots and Arnoud V. den Boer (2023), “Data-driven collusion and competition in a pricing duopoly with multinomial logit demand,” Production and Operations Management 32(4), 1169–1186; first online 15 November 2022.** [Primary full text/DOI 10.1111/poms.13919](https://onlinelibrary.wiley.com/doi/10.1111/poms.13919).

Inspected: §2.1, §2.2 and §3.2.3, particularly equation (21). The Lambert-W logit best-response formula and continuous pricing analysis predate this project. The authors also distinguish joint-revenue optimization from gains for each seller and analyze deliberately designed learning policies. Our cost-shifted normalization and use of W are not new methods. A prospective difference is proving the extremal continuation capacity of this lagged payoff-tolerance guard; existence of a permitted coordinated path does not inherit their policy-learning or incentive conclusions.

### 5. Very close recent basin/graph audit, published as a preprint before this sprint

**Kauê Lopes de Moraes and Rodrigo De Losso (2026), “Algorithmic Collusion Without Deterrence: Auditing the Punishment Mechanism in Q-Learning Pricing Agents,” arXiv:2610.21867v2, 16 October 2026; v1 submitted 15 October.** [Primary full text](https://arxiv.org/html/2610.21867v2); [version metadata](https://arxiv.org/abs/2610.21867).

Inspected: §§3.2, 4.3–4.6 and limitations. It already audits frozen learned policies using state-space basins and dynamic programming, and includes grid refinement at a fixed training budget. It must be cited when discussing basin audits or granularity. Our proposed object is the guard's entire feasible-policy correspondence and its continuous limit, rather than a frozen co-trained pair. The arXiv record lists a forthcoming ICAIF 2026 reference; that metadata is not independently verified publication status here.

### 6. Discrete abstractions do not automatically transfer adversarial guarantees

**Giordano Pola and Paulo Tabuada (2009), “Symbolic Models for Nonlinear Control Systems: Alternating Approximate Bisimulations,” SIAM Journal on Control and Optimization 48(2), 719–733.** [Publisher/DOI 10.1137/070698580](https://epubs.siam.org/doi/10.1137/070698580); [author preprint arXiv:0707.4205](https://arxiv.org/pdf/0707.4205).

Inspected: preprint §§3.2–4, the control/disturbance counterexample and Theorem 4.1. The paper develops approximation relations that preserve the different quantifiers for controller and disturbance choices, under incremental-stability assumptions. Therefore robust transfer between finite abstractions and continuous systems is an established field. Our theory does not establish their alternating approximate bisimulation assumptions for the whole guard: only the extremal upper map contracts, while arbitrary permitted policies need not. The proposed one-sided order argument and welfare comparison are a specialized alternative, not a general new abstraction theory.

### 7. Finite approximations and average-cost convergence have extensive prior theory

**Naci Saldi, Serdar Yüksel and Tamás Linder (2017), “On the Asymptotic Optimality of Finite Approximations to Markov Decision Processes with Borel Spaces,” Mathematics of Operations Research 42(4), 945–978.** [Publisher/DOI 10.1287/moor.2016.0832](https://pubsonline.informs.org/doi/10.1287/moor.2016.0832); [author preprint arXiv:1503.02244v3](https://arxiv.org/pdf/1503.02244).

Inspected: abstract, preprint §2.2/Assumption 2.2/Theorem 2.6 and §5's convergence-rate discussion. Finite approximation, policy-value convergence and average-cost error bounds are not new ideas. Their average-cost argument imposes specific transition/ergodicity conditions. Those are not automatically available for deterministic price updates with multiple basins or periodic paths; distinct deterministic next states need not be close in total variation. We should not invoke that theorem without verifying its hypotheses. Our candidate instead uses a contracting extremal map and a one-sided bound for other policies.

### 8. Action lists, corrections and policy-independent shielding are established

**Mohammed Alshiekh, Roderick Bloem, Rüdiger Ehlers, Bettina Könighofer, Scott Niekum and Ufuk Topcu (AAAI 2018; preprint 2017), “Safe Reinforcement Learning via Shielding.”** [Primary full text](https://arxiv.org/html/1708.08611).

Inspected: §§4–6 and their specification/model assumptions. The paper already separates preemptive action restrictions from post-posed corrections and derives correctness from a specified safety game. Our immediate-profit-tolerance test is not their temporal consumer-welfare specification. A limitation of this economic filter does not refute correctly specified shields, and neither the filter wrapper nor its policy-independent quantifier is a new shielding framework.

The earlier [CYCLE_NOVELTY.md](CYCLE_NOVELTY.md) also records mean-payoff control, calibrated-regret audits and cycle optimization. Those prior distinctions continue to apply; this focused note does not claim to reopen or supersede that review.

## Closest comparisons and defensible contribution boundaries

| Proposed element | Already established | Narrow claim that may remain useful |
|---|---|---|
| Different outcomes on coarse and fine price grids | Learning-based granularity effects and discrete benchmark shifts above | Test the **same guard and fixed old target** as the interval is made continuous; preserve old certificates in their actual finite domains. |
| Dependence on “initialization” | Q initialization, exploration and fixed-policy basins | Distinguish a real one-round public-state intervention from Q initialization; compare all allowed post-intervention continuations. |
| Logit response algebra and approximate best replies | Standard payoff optimization; a guard-feasible constant pair satisfies the underlying bounded game's approximate-Nash inequalities at the tolerance actually used, by definition | Establish stated conditions for this guard's **upper allowance** to be monotone and contractive; preserve the counterexample outside those conditions. |
| Contraction/quantization error propagation | Classical stability and finite-abstraction machinery | Account explicitly for the grid's own best-profit benchmark M_n, including its difference from continuous M, then bound the worst long-run welfare uniformly over public starting states. |
| A lower continuous consumer-surplus floor | Generic adversarial value/control formulations | Identify the extremal feasible path and its limit for this known symmetric lagged rule; do not assume arbitrary low-price policies themselves contract. |
| Initialization becomes unable to guarantee a target | Not a universal consequence of an arbitrary price-grid sweep | Give a **conditional transfer/impossibility criterion** for the old requested and relaxed thresholds, with numeric gaps rigorously enclosed before making a case-level claim. |

The potentially distinctive package is the model-specific link between (i) a valid finite-grid activation certificate, (ii) the guard's continuous all-policy continuation floor, and (iii) a refinement argument explaining whether the certificate transfers. It combines established tools. This search did not establish a prior identical result; that is an absence in this limited search, not evidence of priority.

The cited economic papers differ in models and in how they interpret learned high prices. This note identifies prior questions and methods; it does not resolve those disagreements by accepting one paper's interpretation as settled fact.

## Wording appropriate before and after evaluation

Before new cases are evaluated:

> We study whether finite-grid activation certificates transfer to continuous pricing. For a symmetric logit market with a lagged payoff-tolerance filter, we derive conditional all-start continuation bounds and a refinement argument that accounts for the grid-based best-profit benchmark. A prospective validated study will compare the same inherited targets across resolutions.

If the predeclared assumptions and numerical comparisons later pass:

> For the stated price intervals, tolerances and validated assumptions, we compare audited finite-grid activation guarantees with the continuous guard's worst permitted long-run welfare and the declared refinement diagnostics. The result concerns guarantee transfer under coordinated continuation choices; it does not predict independent learners or establish stable collusion.

Replace “compare” with a concrete outcome only after the independent audit supplies it. Do not insert a case count or conclusion into this literature note from an unfinished run.

Avoid: “first discretization artifact,” “first basin audit,” “first continuous collusion model,” “new shielding algorithm,” “all initialization effects disappear,” “all feasible policies converge,” or “high prices demonstrate collusion.” Uniform convergence of **worst permitted values** is not uniqueness of finite-grid fixed points, convergence of every allowed policy, or a theorem about learned behavior.

## Evidence still required for the proposed distinction

The protocol correctly separates nominal tolerance from the effective allowance carried by the implementation, discrete benchmarking from continuous benchmarking, and old requested targets from their actual relaxed thresholds. These are model definitions and error accounting, not independent novelty claims.

To support the narrower contribution, retain whole-domain assumption validation, independently checked root/welfare enclosures, every failed condition and ambiguous comparison, and matching inherited-grid crosschecks. A large grid is a diagnostic, not a proof of the continuous limit. The theoretical mesh bound additionally needs its stated interval-width and raw-root-slope assumptions before any numerical rate or mesh threshold is advertised. The present protocol does not promise such an evaluated rate, and this note does not manufacture one.
