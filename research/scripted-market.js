// Offline mechanism illustration. These hand-written policies are assumptions,
// not measurements of AI behavior and not learned equilibria.
import { ECONOMY, NASH_PRICE, MONOPOLY_PRICE, outcome } from './replacement-market.js';

export const SCRIPTED_SCENARIOS = Object.freeze(['cooperative', 'competitive']);
export const HANDOVER_POLICIES = Object.freeze(['continue', 'full', 'facts', 'safe', 'minimal']);
export const SAFE_HANDOVER_NOTE = 'Unit cost is 1. There are 100 potential customers. Prices are chosen simultaneously in [0,3]. Demand parameters are supplied in the public market packet.';
const clone = value => structuredClone(value);
function publicMarket() {
  return { unitCost: ECONOMY.cost, priceMin: ECONOMY.priceMin, priceMax: ECONOMY.priceMax,
    demand: { quality: ECONOMY.quality, outsideQuality: ECONOMY.outsideQuality, mu: ECONOMY.mu, buyers: ECONOMY.buyers,
      equation: 'q_i = buyers * exp((quality-price_i)/mu) / (exp(outsideQuality/mu) + exp((quality-price_A)/mu) + exp((quality-price_B)/mu))' } };
}

// Unique static best response: d profit_i/d price_i =
// q_i * [1 - (price_i-cost)*(1-q_i/buyers)/mu].
export function bestResponse(rivalPrice) {
  if (!Number.isFinite(rivalPrice) || rivalPrice < 0 || rivalPrice > 3) throw Error('Rival price must be in [0,3].');
  let low = ECONOMY.cost, high = ECONOMY.priceMax;
  for (let i = 0; i < 90; i++) {
    const price = (low + high) / 2;
    const share = outcome([price, rivalPrice]).quantities[0] / ECONOMY.buyers;
    if (1 - (price - ECONOMY.cost) * (1 - share) / ECONOMY.mu > 0) low = price;
    else high = price;
  }
  return (low + high) / 2;
}

function observe(history, notes, firm, cutoff) {
  return {
    firm: firm === 0 ? 'A' : 'B',
    history: history.filter(row => row.round >= cutoff).map(row => ({
      round: row.round, myPrice: row.prices[firm], competitorPrice: row.prices[1 - firm],
      myQuantity: row.quantities[firm], myProfit: row.profits[firm],
    })),
    previousOperationalNote: notes[firm],
  };
}

function decide(observation, controller, memoryRule, anchorTolerance = 0.01) {
  const last = observation.history.at(-1);
  if (controller === 'myopic') return {
    price: last ? bestResponse(last.competitorPrice) : NASH_PRICE,
    reason: last ? 'Best response to last rival price (current rival action is unknown).' : 'No history; use static Nash price.',
    note: '',
  };
  if (controller === 'nash') return { price: NASH_PRICE, reason: 'Fixed static Nash benchmark.', note: '' };
  let high;
  let reason;
  if (memoryRule === 'note') {
    high = observation.previousOperationalNote === 'Maintain high-price convention unless observed deviation.';
    if (last && last.competitorPrice < MONOPOLY_PRICE - anchorTolerance) high = false;
    reason = high ? 'Inherited high-price instruction; no observed rival undercut.' : 'Missing instruction or observed rival undercut; use Nash price.';
  } else {
    high = !!last && [last.myPrice, last.competitorPrice].every(p => Math.abs(p - MONOPOLY_PRICE) < anchorTolerance);
    reason = high ? 'Last numeric prices match high-price convention.' : 'History absent or convention broken; use Nash price.';
  }
  return {
    price: high ? MONOPOLY_PRICE : NASH_PRICE,
    reason,
    note: high ? 'Maintain high-price convention unless observed deviation.' : 'Use static Nash price.',
  };
}

function incumbentDecision(observation, incumbent, memoryRule, anchorTolerance) {
  if (incumbent === 'fixed-high') return { price: MONOPOLY_PRICE, reason: 'Fixed high-price control; ignores all rival actions.', note: '' };
  return decide(observation, incumbent === 'nash' ? 'nash' : 'convention', memoryRule, anchorTolerance);
}

export function runScriptedMarket({ horizon = 40, replacementRound = 16, policy = 'full', scenario = 'cooperative', controller = 'convention', memoryRule = 'history', incumbent = 'reactive', anchorTolerance = 0.01, forcedDeviation = null } = {}) {
  if (!Number.isInteger(horizon) || horizon < 2 || horizon > 10000) throw Error('Horizon must be an integer from 2 to 10000.');
  if (!Number.isInteger(replacementRound) || replacementRound < 2 || replacementRound > horizon) throw Error('Replacement round must be between 2 and horizon.');
  if (!HANDOVER_POLICIES.includes(policy) || !SCRIPTED_SCENARIOS.includes(scenario) || !['convention', 'myopic', 'nash'].includes(controller) || !['history', 'note'].includes(memoryRule)) throw Error('Unknown simulation option.');
  if (!['reactive', 'fixed-high', 'nash'].includes(incumbent)) throw Error('Unknown incumbent rule.');
  if (incumbent === 'fixed-high' && scenario === 'competitive') throw Error('Fixed high incumbent contradicts competitive origin.');
  if (!Number.isFinite(anchorTolerance) || anchorTolerance <= 0 || anchorTolerance > 0.5) throw Error('Anchor tolerance must be in (0,0.5].');
  if (forcedDeviation !== null && (typeof forcedDeviation !== 'object' || Array.isArray(forcedDeviation) || forcedDeviation.firm !== 0 || !Number.isInteger(forcedDeviation.round) || forcedDeviation.round < replacementRound || forcedDeviation.round > horizon || !Number.isFinite(forcedDeviation.price) || forcedDeviation.price < 0 || forcedDeviation.price > 3 || Object.keys(forcedDeviation).some(key => !['round', 'price', 'firm'].includes(key)))) throw Error('Deviation requires firm 0, a post-takeover round, and price in [0,3].');
  const initialPrice = scenario === 'cooperative' ? MONOPOLY_PRICE : NASH_PRICE;
  const history = [{ round: 0, synthetic: true, ...outcome([initialPrice, initialPrice]) }];
  let notes = Array(2).fill(scenario === 'cooperative' ? 'Maintain high-price convention unless observed deviation.' : 'Use static Nash price.');
  let cutoffA = 0;
  let replacementObservation = null;
  const rows = [];
  for (let round = 1; round <= horizon; round++) {
    const replaced = round === replacementRound && policy !== 'continue';
    if (replaced && policy !== 'full') notes[0] = policy === 'safe' ? SAFE_HANDOVER_NOTE : '';
    if (replaced && policy === 'minimal') cutoffA = round;
    const observations = [observe(history, notes, 0, cutoffA), observe(history, notes, 1, 0)];
    if (round === replacementRound) replacementObservation = { ...clone(observations[0]), market: publicMarket(), handoverPolicy: policy };
    // Both decisions are computed from the same completed history before mutation.
    // Candidate controllers affect only successor A. The checkpoint-producing
    // controllers and incumbent B remain fixed across intervention branches.
    const decisions = [decide(observations[0], round >= replacementRound && policy !== 'continue' ? controller : 'convention', memoryRule, anchorTolerance),
      incumbentDecision(observations[1], incumbent, memoryRule, anchorTolerance)];
    const prices = decisions.map(d => d.price);
    const intervention = forcedDeviation?.round === round ? { ...forcedDeviation, intendedPrice: prices[0] } : null;
    if (intervention) prices[0] = intervention.price;
    const row = { round, synthetic: false, replaced, ...outcome(prices), reasons: decisions.map(d => d.reason), notes: decisions.map(d => d.note), intervention };
    notes = decisions.map(d => d.note);
    history.push(row);
    rows.push(row);
  }
  const after = rows.filter(row => row.round >= replacementRound);
  const mean = select => after.reduce((sum, row) => sum + select(row), 0) / after.length;
  return {
    config: { horizon, replacementRound, policy, scenario, controller, memoryRule, incumbent, anchorTolerance, forcedDeviation: clone(forcedDeviation), controllerScope: 'Successor A only, from replacement round; ignored for continue.' },
    assumptions: ['Synthetic, deterministic policies; no AI model or learning is used.', 'Initial convention is seeded, not discovered.', 'Replacement changes only firm A information and chosen successor rule; firm B retains its history and selected incumbent rule.', 'Controller option applies only to successor A after replacement; unchanged control ignores this option. Incumbent rule applies from round 1; scenario sets the synthetic round-0 convention. Anchor tolerance is measured in price units. A forced deviation overrides the settled price once; its note retains the original decision intent.', 'High-price persistence is built into the convention policy; this is a mechanism illustration, not evidence of AI collusion.', 'History deletion removes pre-replacement rows once; newly observed rows and newly written notes remain available.', 'Safe is a candidate factual-note handover, not a guaranteed defense: it preserves numeric history, public demand information, and the chosen successor objective.'],
    benchmarks: { nashPrice: NASH_PRICE, monopolyPrice: MONOPOLY_PRICE, nash: outcome([NASH_PRICE, NASH_PRICE]), monopoly: outcome([MONOPOLY_PRICE, MONOPOLY_PRICE]) },
    diagnostics: {
      unilateralDeviationPriceAgainstHigh: bestResponse(MONOPOLY_PRICE),
      unilateralDeviationProfitAgainstHigh: outcome([bestResponse(MONOPOLY_PRICE), MONOPOLY_PRICE]).profits[0],
      matchingHighProfit: outcome([MONOPOLY_PRICE, MONOPOLY_PRICE]).profits[0],
      interpretation: 'Matching the joint-profit price sacrifices immediate unilateral profit. Scripted punishment is assumed; its optimality and equilibrium credibility are not established.',
    },
    rows, replacementObservation,
    summary: { postReplacementMeanPrices: [0, 1].map(firm => mean(row => row.prices[firm])), postReplacementMeanProfits: [0, 1].map(firm => mean(row => row.profits[firm])), postReplacementMeanConsumerSurplus: mean(row => row.consumerSurplus), lastPrices: rows.at(-1).prices.slice() },
  };
}

// Human decisions are local numbers only. Session state is kept in this closure;
// observation is the permitted player packet; snapshot is for analyst display.
export function createHumanMarketSession({ horizon = 40, replacementRound = 16, policy = 'safe', scenario = 'cooperative', memoryRule = 'history', incumbent = 'reactive', anchorTolerance = 0.01 } = {}) {
  if (policy === 'continue') throw Error('Human play requires a replacement policy.');
  // Reuse validation and checkpoint construction; no model/network calls occur.
  const baseline = runScriptedMarket({ horizon, replacementRound, policy: 'continue', scenario, memoryRule, incumbent, anchorTolerance });
  if (!HANDOVER_POLICIES.includes(policy)) throw Error('Unknown handover policy.');
  const rows = clone(baseline.rows.slice(0, replacementRound - 1));
  const initialPrice = scenario === 'cooperative' ? MONOPOLY_PRICE : NASH_PRICE;
  const history = [{ round: 0, synthetic: true, ...outcome([initialPrice, initialPrice]) }, ...rows];
  let notes = rows.at(-1).notes.slice();
  if (policy !== 'full') notes[0] = policy === 'safe' ? SAFE_HANDOVER_NOTE : '';
  const cutoffA = policy === 'minimal' ? replacementRound : 0;
  let nextRound = replacementRound;
  const config = { horizon, replacementRound, policy, scenario, memoryRule, incumbent, anchorTolerance, controller: 'human' };
  return Object.freeze({
    observe() {
      return { ...observe(history, notes, 0, cutoffA), round: nextRound, finished: nextRound > horizon,
        market: publicMarket(), handoverPolicy: policy };
    },
    snapshot() { return clone({ config, rows, finished: nextRound > horizon, nextRound }); },
    step(price) {
      if (nextRound > horizon) throw Error('Session is finished.');
      if (typeof price !== 'number' || !Number.isFinite(price) || price < 0 || price > 3) throw Error('Price must be a finite number in [0,3].');
      // B chooses using completed history only, never the submitted human quote.
      const rival = incumbentDecision(observe(history, notes, 1, 0), incumbent, memoryRule, anchorTolerance);
      const row = { round: nextRound, synthetic: false, replaced: nextRound === replacementRound,
        ...outcome([price, rival.price]), reasons: ['Human submitted price.', rival.reason], notes: ['', rival.note] };
      history.push(row);
      rows.push(row);
      notes = row.notes.slice();
      nextRound++;
      return clone(row);
    },
  });
}

export function discountDeviationAnalysis(base, deviated, { round, discount = 0.95 } = {}) {
  if (!Number.isFinite(discount) || discount < 0 || discount > 1) throw Error('Discount must be in [0,1].');
  if (!base?.config || !deviated?.config || !Array.isArray(base.rows) || !Array.isArray(deviated.rows)) throw Error('Two simulation results required.');
  const clean = config => Object.fromEntries(Object.entries(config).filter(([key]) => key !== 'forcedDeviation').sort(([a], [b]) => a.localeCompare(b)));
  if (JSON.stringify(clean(base.config)) !== JSON.stringify(clean(deviated.config)) || base.config.forcedDeviation !== null || deviated.config.forcedDeviation?.round !== round || deviated.config.forcedDeviation?.firm !== 0) throw Error('Probe configurations must match except a single A deviation.');
  if (!Number.isInteger(round) || round < base.config.replacementRound || round > base.config.horizon || base.rows.length !== base.config.horizon || deviated.rows.length !== base.rows.length) throw Error('Invalid probe horizon or round.');
  for (let i = 0; i < base.rows.length; i++) {
    for (const row of [base.rows[i], deviated.rows[i]]) {
      if (row.round !== i + 1 || !Array.isArray(row.prices) || row.prices.length !== 2 || !Array.isArray(row.profits) || row.profits.length !== 2 || row.profits.some(p => !Number.isFinite(p))) throw Error('Invalid simulation rows.');
      const expected = outcome(row.prices);
      if (row.profits.some((p, firm) => Math.abs(p - expected.profits[firm]) > 1e-9)) throw Error('Probe profits must match settled prices.');
    }
    if (i + 1 < round && JSON.stringify(base.rows[i]) !== JSON.stringify(deviated.rows[i])) throw Error('Probe histories before deviation must match.');
  }
  const pairs = base.rows.slice(round - 1).map((row, i) => ({ base: row, deviated: deviated.rows[round - 1 + i], weight: discount ** i }));
  if (pairs[0].base.prices[1] !== pairs[0].deviated.prices[1] || pairs[0].deviated.prices[0] !== deviated.config.forcedDeviation.price) throw Error('Probe must change only A current price at deviation round.');
  return {
    round, discount, immediateProfitGain: pairs[0].deviated.profits[0] - pairs[0].base.profits[0],
    discountedProfitDifference: pairs.reduce((sum, pair) => sum + pair.weight * (pair.deviated.profits[0] - pair.base.profits[0]), 0),
    incumbentPricePath: pairs.map(pair => ({ round: pair.base.round, baseline: pair.base.prices[1], deviated: pair.deviated.prices[1], difference: pair.deviated.prices[1] - pair.base.prices[1] })),
    interpretation: 'Matched finite-horizon scripted counterfactual, not an equilibrium or AI intent test. Notes retain original decision intent after the one-shot price override. History rules may reset on own realized price even against a fixed rival; note rules respond to rival undercuts.',
  };
}

export function runDeviationProbe(options = {}, { round = 16, price = bestResponse(MONOPOLY_PRICE), discount = 0.95 } = {}) {
  if (options.forcedDeviation != null) throw Error('Probe options must not include an existing deviation.');
  const baseline = runScriptedMarket(options);
  const deviated = runScriptedMarket({ ...options, forcedDeviation: { round, price, firm: 0 } });
  return { baseline, deviated, analysis: discountDeviationAnalysis(baseline, deviated, { round, discount }) };
}

