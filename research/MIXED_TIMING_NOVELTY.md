# Prior art and scope: mixed cap timing

Prospective reading note, 26 October 2026. This is outside the frozen V9
payload and reports no new numerical market result. Targeted reading does not
establish priority or an exhaustive literature search.

- [Sun and Cyr, Sampling for Data Freshness Optimization: Non-linear Age
  Functions](https://arxiv.org/html/1812.07241), 2019 version: abstract,
  formulation and Theorems 2 and 4 read. Nonlinear age costs include decreasing
  utility as time since a sample increases. The discrete constrained problem
  can randomize between two threshold times. Adjacent integer timing mixtures
  and the utility/rate tradeoff therefore cannot be claimed as our invention.
  Their queueing/sampling setting and long-run expected constraints differ
  from the particular all-policy, every-activation-prefix promise proposed here.
- [Champati, Skoglund and Gross, Detecting State Transitions of a Markov
  Source: Sampling Frequency and Age Trade-off](https://arxiv.org/abs/2001.10381),
  2020: abstract and initial formulation read. It already optimizes sampling
  frequency under an average age constraint using a Markov decision framework
  and compares periodic sampling. Its update-age reward convention is not
  automatically equivalent to our per-execution pricing reward.
- [Mannor, Tsitsiklis and Yu, Online Learning with Sample Path
  Constraints](https://www.jmlr.org/papers/v10/mannor09a.html), 2009: abstract,
  pathwise asymptotic formulation and relevant convex-hull/algorithm sections
  read. Adversarial constrained reward and pathwise asymptotic constraints are
  established topics. This does not by itself certify our stronger finite
  activation-prefix condition, and our known envelope needs no forecasting.
- [Neely, Fast Learning for Renewal Optimization in Online Task
  Scheduling](https://www.jmlr.org/papers/v22/20-813.html), 2021: renewal reward
  per unit time and mixtures of finite options are established machinery.
  Our deterministic known-model calculation is not a new renewal-learning
  algorithm.
- [Wu, Shariff, Lattimore and Szepesvari, Conservative
  Bandits](https://proceedings.mlr.press/v48/wu16.html), 2016: abstract,
  Sections 2 and 3.1--3.3 read. Keeping cumulative reward above a baseline at
  every time and building a budget before risking a loss are explicit prior
  ideas. Their unknown-reward bandit learning and probabilistic variants differ
  from our known deterministic adverse envelope, but funding safe departures
  from a baseline is not new.
- [Du, Wang and Huang, A One-Size-Fits-All Solution to Conservative Bandit
  Problems](https://ojs.aaai.org/index.php/AAAI/article/view/16891), 2021:
  publisher abstract read only. It expressly addresses sample-path constraints
  on actually received cumulative reward at every time. Therefore even a
  pathwise cumulative budget should not be presented as a generic new concept.

The defensible question is model-specific: does the attained adverse pricing
envelope reduce the existing cap/guard problem to a certified mixed-gap
calendar, how much integer-period frequency penalty remains, and can exact
funded ordering meet every prefix from a real initial cap? The elementary
concavity and credit construction require explicit attribution and independent
checking; novelty beyond this application remains unestablished. Do not claim
new collusion behavior, general regulatory optimality, sliding-window safety,
or behavior of learners trained for the old phase clock.
