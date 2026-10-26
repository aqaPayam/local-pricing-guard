# Coordinated cycle audit: closest work and contribution boundary

Prepared 26 October 2026. This is a targeted primary-source audit for the new
finite-grid stress-test program, not an exhaustive priority search. Eight
sources are retained below. Bibliographic metadata and the specifically relevant
sections were checked; no claim is made that every page of each long paper was
reviewed. No source establishes that our planned comparison is original.

The version-2 paper, archive, source snapshots and numerical evidence remain
immutable. This document proposes a separate follow-up and does not reinterpret
a deliberately optimized joint seller policy as an independently learned one.

## What the new question can be

**Under the exact price filter used in our simulator, what is the lowest
long-run customer benefit that any coordinated sequence of permitted prices
can attain, and how does that bound compare with a price cap, no intervention,
and the behavior of our previously trained sellers?**

The word **coordinated** is essential: an optimizer chooses both sellers'
actions. A witness is an existence result in a specified model. It does not show
that independent learners discover the pattern, that either seller wants to
follow it, or that no seller would profit from deviating.

The established ingredients are graph optimization, action shielding,
worst-case supervisory control, dynamic price cycles and welfare-oriented
platform intervention. A potentially useful incremental contribution is a
checkable economic stress-test comparison for this particular lagged
profit-tolerance rule, with a clear contrast between learned observations and
all-permitted-behavior bounds.

## Eight retained primary sources

| Source and inspected scope | Relevant established result | Boundary for our follow-up |
|---|---|---|
| **Richard M. Karp (1978).** *A characterization of the minimum cycle mean in a digraph.* Discrete Mathematics 23(3), 309–311. [Publisher/DOI](https://doi.org/10.1016/0012-365X(78)90011-0); [author's 1977 Berkeley technical report, UCB/ERL M77/47](https://www2.eecs.berkeley.edu/Pubs/TechRpts/1977/Archive/ERL-m-77-47.pdf). Definition, characterization, dynamic program and component decomposition inspected. | Computes the smallest average edge weight on directed cycles using established finite-graph optimization. | Implementing this algorithm, changing the edge weight to consumer surplus, or enumerating finite market states is not a new optimization method. Reachability and witness certification still require care. |
| **Mmanu Chaturvedi and Ross M. McConnell (2017).** *A note on finding minimum mean cycle.* Information Processing Letters 127, 21–22. [DOI](https://doi.org/10.1016/j.ipl.2017.06.007); [author-hosted manuscript](https://www.cs.colostate.edu/~rmm/minCycleMean.pdf). Counterexample and Lemma 1 inspected. | Karp's value computation is correct, but the proposed fixed-length extraction shortcut is not. Their corrected construction reconstructs an optimal length-n walk ending at a minimizer and extracts a repeated-vertex cycle. | A numerical value alone is not a usable economic counterexample. Independently check the actual witness's closure, legal transitions, mean weight and reachability. Do not claim our witness extraction is new. |
| **Mohammed Alshiekh, Roderick Bloem, Ruediger Ehlers, Bettina Könighofer, Scott Niekum and Ufuk Topcu (AAAI 2018; preprint 2017).** *Safe Reinforcement Learning via Shielding.* [Primary full text](https://arxiv.org/html/1708.08611), especially sections 5 and 6. | Synthesizes action restrictions or corrections from safety games and analyzes correctness and minimal interference. Rewards credited to overridden proposals can sustain those proposals. | We must not rediscover pre/post shielding, proposal aliasing, safety-game construction or minimal interference. Our filter's own-profit test is not automatically a temporal consumer-welfare specification. |
| **Bettina Könighofer, Roderick Bloem, Nils Jansen, Sebastian Junges and Stefan Pranger (2025).** *Shields for Safe Reinforcement Learning.* Communications of the ACM 68(11), 80–90; published 20 October 2025. [DOI](https://doi.org/10.1145/3715958); [institution-hosted accepted manuscript](https://tugraz.elsevierpure.com/ws/portalfiles/portal/93576031/Shields_for_Safe_Reinforcement_Learning.pdf), sections 3–4 inspected. | Explains adversarial future behavior, invariant winning regions and permissiveness; distinguishes several probabilistic notions that need not compose under repeated action choices. | A local test and a long-run guarantee answer different questions. Our result would concern this economic rule and objective, not the first observation that future behavior matters or a refutation of correctly specified shields. |
| **Yiding Ji, Xiang Yin and Stéphane Lafortune (2021).** *Optimal supervisory control with mean payoff objectives and under partial observation.* Automatica 123, article 109359. [DOI](https://doi.org/10.1016/j.automatica.2020.109359); [author-hosted full text](https://xiangyin.sjtu.edu.cn/Paper/21AutomaticaOptimal.pdf), introduction, problem formulations and game construction inspected. | Studies worst-case long-run average objectives for weighted systems, including partial observation, using a supervisor/environment game and minimax synthesis. | General mean-payoff control and adversarial guarantees are established. A later welfare-preserving price-filter synthesis must cite this broader field and state the narrower economic design and information assumptions. |
| **Gianluca Brero, Eric Mibuari, Nicolas Lepore and David C. Parkes (2022).** *Learning to Mitigate AI Collusion on Economic Platforms.* NeurIPS 35. [Official proceedings PDF](https://papers.neurips.cc/paper_files/paper/2022/file/f746974abd33c0015ca583a267dac1fd-Paper-Conference.pdf), sections 1–5 inspected. | Uses a Stackelberg POMDP to optimize platform rules against Q-learning sellers, measuring consumer surplus and robustness; its discussion already includes price cycles. | Consumer-oriented anti-collusion platform design and robustness testing are prior work. Our graph certificate covers permitted policies in a fixed price-filter model, unlike their learned display rule and behavioral response model; superiority is not established by this difference. |
| **Jason D. Hartline, Chang Wang and Chenhao Zhang (2025).** *Regulation of Algorithmic Collusion, Refined: Testing Pessimistic Calibrated Regret.* arXiv:2501.09740, submitted 16 January 2025. [Primary full text](https://arxiv.org/html/2501.09740), sections 1, 3–6 inspected. | Develops an audit based on worst compatible calibrated regret, demonstrates weaknesses of external regret and examines uncertain costs. | Our lagged modeled one-step profit loss is neither their calibrated regret nor a legal compliance certificate. Checking it on a jointly designed path does not show that their audit accepts that path. |
| **Eric Maskin and Jean Tirole (1988).** *A Theory of Dynamic Oligopoly, II: Price Competition, Kinked Demand Curves, and Edgeworth Cycles.* Econometrica 56(3), 571–599. [Author-hosted original article](https://maskin.scholars.harvard.edu/sites/g/files/omnuum10606/files/maskin/files/a_theory_of_dynamic_oligopoly_ii_price_competition_kinked_demand_curves_and_edgeworth_cycles.pdf), introduction and equilibrium framing inspected. | Gives equilibrium foundations for price cycles in alternating-move oligopoly with short-run commitment. | A cycle is not itself a novel economic mechanism. Our simultaneous, jointly optimized witness does not inherit their timing assumptions, strategic equilibrium or incentive compatibility. |

The primary texts support the middle column. The right column is our assessment
of their relationship to the proposed work. Search snippets without an
accessible primary publication are not treated as verified prior-art evidence.

## What is established and what still needs a result

| Proposed component | Status |
|---|---|
| Encode the previous price pair as a finite graph state | Standard modeling construction; explain it rather than claiming invention. |
| Find a minimum-average-weight recurrent pattern | Established graph optimization. |
| Enforce a safety property while preserving allowable actions | Established shielding/supervisory-control program. The exact property matters. |
| Compare the existing lagged profit filter with a simple cap under coordinated stress | Potentially useful model-specific empirical/formal comparison; outcome not yet known. |
| Quantify the gap between learned outcomes and an all-policy welfare bound | Potentially useful evaluation result, provided objectives, reachability, grid and uncertainty are explicit. |
| Demonstrate a profitable, stable cartel | Not established by a minimum-CS witness or a sum-of-profits objective. |
| Show a new LLM or emergent-learning phenomenon | Outside this coordinated graph audit; no account-backed or paid inference is authorized. |

## Mathematical checks that make the comparison credible

These are proposed checks and elementary model reasoning, not claims of new
optimization theory or completed experiments.

1. **Define the quantifier.** For a declared initial state, search only states
   and recurrent components reachable through permitted actions. Label a
   separate global search over all starting states as such.
2. **Certify both directions.** An attainable closed witness gives an upper
   bound on the minimum welfare value. A graph potential satisfying the
   corresponding edge inequalities gives a lower bound. The two should agree
   within the reported numerical tolerance. Recompute economics independently.
3. **Keep transient harm visible.** A path into the eventual loop can have a
   different average. Report its length and finite-horizon welfare separately;
   do not hide it inside an asymptotic statement.
4. **Use simple controls.** With no intervention, monotonicity of logit consumer
   surplus makes the highest-price constant pair a worst-CS control. With a
   fixed cap, the highest executable capped pair gives the analogous control.
   Verify this against the actual price grid and cap rounding.
5. **Do not demand a nontrivial cycle.** A one-state self-loop is a valid
   optimizer. Check whether monotonicity of the guard's upper feasible-price
   map permits a stronger all-cycle fixed-point bound. Treat this as a question
   to prove or falsify, not an assumed fact.
6. **Distinguish objective functions.** A minimum-CS witness may harm sellers.
   Separately compute a maximum-joint-profit witness and show each seller's
   profit against its benchmark. A sum can hide one seller losing. A profitable
   path still need not be a strategic equilibrium.
7. **Avoid an incorrect constrained extension.** Adding long-run individual
   profit constraints can make occupation measures or mixtures of cycles
   relevant; searching only individually feasible simple cycles need not solve
   that larger problem.

## Stronger next goals, in priority order

**First: close the existing filter's actual guarantee gap.** Produce all-cell
graph certificates and reachable witnesses; compare these with the frozen
learned-policy results. A clean negative finding is useful if it establishes
that the apparent protection came from the tested learners rather than the
permitted behavior set. A positive finite-model bound is also useful, provided
it remains explicitly finite-model and model-relative.

**Second: explain a structural boundary.** Test whether a simple order or
fixed-point argument determines the worst welfare for this logit filter. If
it does, give the economic condition and an independent enumerative check. If
it fails, identify a concrete parameter/grid cell and explain why. Replacing a
large search with an interpretable condition can improve the contribution
without pretending the graph algorithm is new.

**Third: compare welfare with retained economic choice.** For a declared welfare
floor, compare a cap and a state-dependent filter using feasible cardinality,
price span and both profits, at matched guarantees. Do not call a controller
maximally permissive merely because it beats one cap. Safety-preserving
permissiveness and minimum intervention are established concepts, and the
precise ordering of allowed policies must be stated.

**Fourth: test robustness of a certificate, not just more seeds.** A finite-grid
certificate is exact only for that grid, payoff model and timing. Investigate
whether a conservative error margin extends a bound to finer grids or bounded
model misspecification. A discrete numerical sweep alone is not a continuous
proof, and data-derived payoffs would require an additional uncertainty model.

**Fifth: add incentive or discovery evidence only as a separate study.** Test
unilateral deviation profitability or whether independently trained local
learners find the witness. Neither is needed to establish the coordinated
existence bound; both are needed before stronger cartel/emergence language.
Do not add LLM players without separate authorization.

## Recommended claim wording

Before results: "We will audit the long-run welfare permitted by a specified
price filter using established cycle optimization and independently checked
witnesses."

After a certified result: "For the stated finite grid, model and reachable
states, the lowest permitted recurrent mean customer benefit is [value]. A
coordinated policy attains it, and an independent bound certifies optimality to
[tolerance]." Add each seller's profit and any transient qualification.

Avoid "we discovered cycle attacks," "all shields fail," "the agents learned
this cartel," "the minimum-CS optimizer is an equilibrium," "100% accepted
proves safety," and "the most permissive safe market rule" unless the exact
additional claim is independently established. No originality or prize outcome
is guaranteed by this literature audit.
