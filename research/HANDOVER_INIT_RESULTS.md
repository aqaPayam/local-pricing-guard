# One actual capped execution at handover: results

This follow-up uses the eight unchanged finite guard games and five predeclared welfare-target labels per game. A capped quote genuinely executes once, then the original guard resumes. The target-region calculation considers every allowed coordinated continuation; it does not assume the previous learned policy cooperates. All 40 labels were retained, including duplicate numerical targets.

## What one capped round achieves

|Target label|Existing cap certified|Already safe without initialization|Nontrivial uniform repairs|Any finite initializer impossible|Ambiguous scenarios|
|---|---:|---:|---:|---:|---:|
|cap-90pct|8/8|7/8|1/8|0/8|0/8|
|cap-95pct|5/8|0/8|5/8|3/8|0/8|
|cap-99pct|4/8|0/8|4/8|4/8|0/8|
|cap-100pct|4/8|0/8|4/8|4/8|0/8|
|near-Nash-anchor-floor|8/8|2/8|6/8|0/8|0/8|

The distinction between success and repair matters. The 90% cap-reference target succeeds in all eight scenarios, but seven were already safe from every initial state. The near-Nash-anchor target succeeds in all eight, with six genuine repairs and two already-safe, affine-equivalent calibrations. These are exact finite-graph case counts, not independent experimental success probabilities. Four calibrations still represent only three dimensionless demand shapes.

## All 40 target outcomes

Requested target F is relaxed by the frozen allowance delta=1e-8*max(1,F). The actual guarantee is F−delta, shown separately. Membership is certified lower bound ≥ threshold; attained upper bound below threshold is unsafe; numerical straddlers would remain ambiguous. There were no actual straddlers.

|Scenario|Label|Requested target|Actual threshold|Safe states / all|Existing cap|Largest safe prefix k|Initial quotes / seller|Additional quotes / seller|
|---|---|---:|---:|---:|---|---:|---:|---:|
|base-g15-t1|cap-90pct|64.907136376315464|64.907135727244096|225/225|certified|14|15|13|
|base-g15-t1|cap-95pct|68.513088397221878|68.513087712090993|56/225|certified|1|2|0|
|base-g15-t1|cap-99pct|71.397850013947007|71.397849299968513|4/225|certified|1|2|0|
|base-g15-t1|cap-100pct|72.119040418128293|72.119039696937890|4/225|certified|1|2|0|
|base-g15-t1|near-Nash-anchor-floor|72.119040403704474|72.119039682514071|4/225|certified|1|2|0|
|scale0.5-g15-t1|cap-90pct|62.608784189246819|62.608783563158980|225/225|certified|14|15|13|
|scale0.5-g15-t1|cap-95pct|66.087049977538300|66.087049316667802|0/225|impossible|none|none|none|
|scale0.5-g15-t1|cap-99pct|68.869662608171495|68.869661919474865|0/225|impossible|none|none|none|
|scale0.5-g15-t1|cap-100pct|69.565315765829794|69.565315070176638|0/225|impossible|none|none|none|
|scale0.5-g15-t1|near-Nash-anchor-floor|64.653674185582844|64.653673539046096|225/225|certified|14|15|13|
|lower-quality-g15-t1|cap-90pct|31.304392094623395|31.304391781579476|225/225|certified|14|15|13|
|lower-quality-g15-t1|cap-95pct|33.043524988769136|33.043524658333887|0/225|impossible|none|none|none|
|lower-quality-g15-t1|cap-99pct|34.434831304085733|34.434830959737418|0/225|impossible|none|none|none|
|lower-quality-g15-t1|cap-100pct|34.782657882914883|34.782657535088305|0/225|impossible|none|none|none|
|lower-quality-g15-t1|near-Nash-anchor-floor|32.326837092791422|32.326836769523048|225/225|certified|14|15|13|
|lowcost-g15-t1|cap-90pct|98.413374313396403|98.413373329262654|225/225|certified|14|15|13|
|lowcost-g15-t1|cap-95pct|103.88078399747397|103.88078295866613|56/225|certified|1|2|0|
|lowcost-g15-t1|cap-99pct|108.25471174473603|108.25471066218891|4/225|certified|1|2|0|
|lowcost-g15-t1|cap-100pct|109.34819368155155|109.34819258806961|4/225|certified|1|2|0|
|lowcost-g15-t1|near-Nash-anchor-floor|109.34819365968190|109.34819256619996|4/225|certified|1|2|0|
|base-g11-t1|cap-90pct|63.592480199870117|63.592479563945318|121/121|certified|10|11|9|
|base-g11-t1|cap-95pct|67.125395766529564|67.125395095275607|40/121|certified|1|2|0|
|base-g11-t1|cap-99pct|69.951728219857131|69.951727520339844|4/121|certified|1|2|0|
|base-g11-t1|cap-100pct|70.658311333189019|70.658310626605910|4/121|certified|1|2|0|
|base-g11-t1|near-Nash-anchor-floor|70.658311319057347|70.658310612474239|4/121|certified|1|2|0|
|base-g31-t1|cap-90pct|65.126696085103049|65.126695433836090|961/961|certified|30|31|28|
|base-g31-t1|cap-95pct|68.744845867608774|68.744845180160311|25/961|certified|4|5|2|
|base-g31-t1|cap-99pct|71.639365693613357|71.639364977219699|0/961|impossible|none|none|none|
|base-g31-t1|cap-100pct|72.362995650114499|72.362994926484546|0/961|impossible|none|none|none|
|base-g31-t1|near-Nash-anchor-floor|68.960916709352801|68.960916019743635|25/961|certified|4|5|2|
|base-g15-t0.5|cap-90pct|64.907136376315464|64.907135727244096|225/225|certified|14|15|13|
|base-g15-t0.5|cap-95pct|68.513088397221878|68.513087712090993|56/225|certified|1|2|0|
|base-g15-t0.5|cap-99pct|71.397850013947007|71.397849299968513|4/225|certified|1|2|0|
|base-g15-t0.5|cap-100pct|72.119040418128293|72.119039696937890|4/225|certified|1|2|0|
|base-g15-t0.5|near-Nash-anchor-floor|72.119040403704474|72.119039682514071|4/225|certified|1|2|0|
|base-g15-t2|cap-90pct|64.907136376315464|64.907135727244096|81/225|certified|2|3|1|
|base-g15-t2|cap-95pct|68.513088397221878|68.513087712090993|0/225|impossible|none|none|none|
|base-g15-t2|cap-99pct|71.397850013947007|71.397849299968513|0/225|impossible|none|none|none|
|base-g15-t2|cap-100pct|72.119040418128293|72.119039696937890|0/225|impossible|none|none|none|
|base-g15-t2|near-Nash-anchor-floor|68.477351928476267|68.477351243702742|9/225|certified|2|3|1|

A largest prefix of the whole grid is pass-through: no initialization restriction is needed for that label. "Additional quotes" counts only the first execution relative to the existing competitive cap. It does not measure subsequent strategic freedom. The largest certified k is optimal only among common prefix caps [0,k] for both sellers, not arbitrary asymmetric, state-dependent or history-dependent controllers.

## A useful allowance comparison

At the 31-price near-Nash-anchor and 95% targets, the existing competitive cap allows three prices per seller; the largest safe common prefix allows five. With doubled tolerance, the near-Nash target permits three first-round prices rather than two. The full first-round price spans, customer-surplus ranges, each seller’s profit range and joint-profit range are retained for every label in summary.json and results.json. These are feasible ranges over adversarial choices, not expectations under an invented uniform distribution.

## What failures mean

Every unsuccessful actual label had an empty certified safe region and every state was certified unsafe. Thus any finite initializer that eventually returns to this unchanged guard must end at some public grid state from which an allowed coordinated tail falls below the actual threshold. A legal failed-cap prefix and repeatable tail are retained. This is stronger than saying the competitive cap happened to be the wrong initializer.

This impossibility does not cover a permanently changed guard/tolerance, a different price grid or economy, off-grid actions, or additional enforceable commitments that restrict subsequent choices. In general an empty certified set with ambiguous states would be unresolved; synthetic tests explicitly check that distinction. A nonempty safe set with no common prefix cap also does not establish arbitrary-initializer impossibility.

## Inherited starts, verification and scope

All 64 previously saved unprotected-training endpoints were retained as diagnostic starts. Their reuse across five labels creates 320 diagnostic views, not new independent seeds. Forward invariance was checked on every outgoing edge of each certified safe set. Independent reconstruction passed 163,012 checks, 24,841 safe-set edges, all 40 labels, inherited cycle certificates and four actual-output corruption controls. The model/price identity check rejects matching scenario IDs hiding different economic parameters or grids.

The run took 0.104 seconds. The largest observed RSS sample after scenarios was 81.43 MB; it is not a continuously measured peak. Zero failures, API calls and new training rounds were recorded. The source/input freeze manifest is f0e0f41f1ba712a744f87e5dfb15692dab6249c2a5e50c743cb16da5b6090e47.

This goal establishes long-run protection at the displayed relaxed threshold. It does not reuse the previous global transient-deficit formula to assert a higher target over finite horizons, and it makes no equilibrium, credible-collusion, unilateral-incentive or learner-discovery claim. Numerical certificates concern floating computed rewards in a known symmetric deterministic finite duopoly. Continuous-price/finer-grid persistence and incentive stability remain separate research questions.
