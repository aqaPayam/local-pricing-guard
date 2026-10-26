// Independent action constraint experiment. No learned agents, inference or network.
import { outcome, NASH_PRICE, MONOPOLY_PRICE } from './replacement-market.js';

const DEFAULT_MODEL = Object.freeze({ quality: 2, cost: 1, mu: 0.25, buyers: 100, outsideQuality: 0, priceMin: 0, priceMax: 3 });
function modelOptions(input = {}) {
  if (!input || typeof input !== 'object' || Array.isArray(input) || Object.keys(input).some(key => !Object.hasOwn(DEFAULT_MODEL, key))) throw Error('Unknown model option.');
  const model = { ...DEFAULT_MODEL, ...input };
  if (Object.values(model).some(value => !Number.isFinite(value)) || model.mu <= 0 || model.buyers <= 0 || model.priceMin >= model.priceMax || model.cost < model.priceMin || model.cost >= model.priceMax) throw Error('Invalid public market model.');
  return model;
}
function validPrice(price, model) {
  if (!Number.isFinite(price) || price < model.priceMin || price > model.priceMax) throw Error('Price outside model limits.');
}
function share(price, rivalPrice, model) {
  const a = (model.quality - price) / model.mu;
  const b = (model.quality - rivalPrice) / model.mu;
  const c = model.outsideQuality / model.mu;
  const offset = Math.max(a, b, c);
  return Math.exp(a - offset) / (Math.exp(a - offset) + Math.exp(b - offset) + Math.exp(c - offset));
}
function profit(price, rivalPrice, model) { return model.buyers * (price - model.cost) * share(price, rivalPrice, model); }
function optimum(rivalPrice, model) {
  let low = model.cost, high = model.priceMax;
  const derivative = price => 1 - (price - model.cost) * (1 - share(price, rivalPrice, model)) / model.mu;
  if (derivative(high) >= 0) return high;
  for (let iteration = 0; iteration < 90; iteration++) {
    const middle = (low + high) / 2;
    if (derivative(middle) > 0) low = middle; else high = middle;
  }
  return (low + high) / 2;
}

export function brInterval(rivalPrice, { epsilon = 0, model: input = {} } = {}) {
  const model = modelOptions(input);
  validPrice(rivalPrice, model);
  if (!Number.isFinite(epsilon) || epsilon < 0) throw Error('Epsilon must be finite and nonnegative.');
  const bestPrice = optimum(rivalPrice, model);
  const bestProfit = profit(bestPrice, rivalPrice, model);
  const target = bestProfit - epsilon;
  let lower = bestPrice, upper = bestPrice;
  if (epsilon > 0) {
    if (profit(model.priceMin, rivalPrice, model) >= target) lower = model.priceMin;
    else {
      let lo = model.priceMin, hi = bestPrice;
      for (let i = 0; i < 90; i++) {
        const mid = (lo + hi) / 2;
        if (profit(mid, rivalPrice, model) < target) lo = mid; else hi = mid;
      }
      lower = hi;
    }
    if (profit(model.priceMax, rivalPrice, model) >= target) upper = model.priceMax;
    else {
      let lo = bestPrice, hi = model.priceMax;
      for (let i = 0; i < 90; i++) {
        const mid = (lo + hi) / 2;
        if (profit(mid, rivalPrice, model) >= target) lo = mid; else hi = mid;
      }
      upper = lo;
    }
  }
  return { lower, upper, bestPrice, bestProfit, epsilon, model };
}

export function projectQuote(proposal, rivalPrice, options = {}) {
  const interval = brInterval(rivalPrice, options);
  validPrice(proposal, interval.model);
  const price = Math.max(interval.lower, Math.min(interval.upper, proposal));
  return { ...interval, price, proposal, projectionSize: Math.abs(price - proposal),
    regret: Math.max(0, interval.bestProfit - profit(price, rivalPrice, interval.model)) };
}

// PCG RXS-M-XS permutation on a 32-bit LCG; deterministic common random stream.
function randomGenerator(seed) {
  let state = seed >>> 0;
  return () => {
    state = (Math.imul(state, 747796405) + 2891336453) >>> 0;
    const word = Math.imul(((state >>> ((state >>> 28) + 4)) ^ state) >>> 0, 277803737) >>> 0;
    return ((word >>> 22) ^ word) >>> 0;
  };
}

export function runContractMarket({ rounds = 80, initialPrices = [MONOPOLY_PRICE, MONOPOLY_PRICE], epsilon = 0,
  coverage = 'both', releaseAfter = null, proposal = 'high', seed = 1, believedCost = 1, believedMu = 0.25 } = {}) {
  if (!Number.isInteger(rounds) || rounds < 1 || rounds > 10000 || !['none', 'A', 'both'].includes(coverage) || !['high', 'oscillating', 'random', 'feedback-high'].includes(proposal) || !Number.isInteger(seed) || seed < 0 || seed > 0xffffffff || (releaseAfter !== null && (!Number.isInteger(releaseAfter) || releaseAfter < 0 || releaseAfter > rounds))) throw Error('Invalid simulation configuration.');
  if (!Array.isArray(initialPrices) || initialPrices.length !== 2) throw Error('Two initial prices required.');
  const model = modelOptions({ cost: believedCost, mu: believedMu });
  initialPrices.forEach(price => validPrice(price, model));
  if (!Number.isFinite(epsilon) || epsilon < 0) throw Error('Epsilon must be finite and nonnegative.');
  const randomStreams = [randomGenerator((seed ^ 0xa5a5a5a5) >>> 0), randomGenerator((seed ^ 0x5a5a5a5a) >>> 0)];
  let previous = initialPrices.slice();
  const rows = [];
  for (let round = 1; round <= rounds; round++) {
    const draws = randomStreams.map(random => random() / 4294967296);
    const proposals = [0, 1].map(firm => proposal === 'high' ? MONOPOLY_PRICE : proposal === 'oscillating' ? ((round + firm) % 2 ? 3 : 0) : proposal === 'random' ? 3 * draws[firm] : previous[1 - firm] > NASH_PRICE + 0.05 ? MONOPOLY_PRICE : NASH_PRICE);
    const active = releaseAfter === null || round <= releaseAfter;
    const covered = [active && coverage !== 'none', active && coverage === 'both'];
    const checks = proposals.map((quote, firm) => projectQuote(quote, previous[1 - firm], { epsilon, model }));
    const prices = proposals.map((quote, firm) => covered[firm] ? checks[firm].price : quote);
    const trueChecks = prices.map((quote, firm) => projectQuote(quote, previous[1 - firm], { epsilon: 0 }));
    const realizedRegretTrue = prices.map((quote, firm) => {
      const best = brInterval(prices[1 - firm]);
      return Math.max(0, best.bestProfit - profit(quote, prices[1 - firm], DEFAULT_MODEL));
    });
    const contractModelRegret = prices.map((quote, firm) => Math.max(0, checks[firm].bestProfit - profit(quote, previous[1 - firm], model)));
    rows.push({ round, prices, proposals, observedPrevious: previous.slice(), ...outcome(prices),
      oneStepRegretTrue: trueChecks.map((check, firm) => Math.max(0, check.bestProfit - profit(check.proposal, previous[1 - firm], DEFAULT_MODEL))),
      realizedRegretTrue,
      acceptedIntervals: checks.map(({ lower, upper, bestPrice, bestProfit }) => ({ lower, upper, bestPrice, bestProfit })),
      acceptedIntervalWidths: checks.map(({ lower, upper }) => upper - lower),
      contractModelRegret, projectionSizes: prices.map((price, firm) => Math.abs(price - proposals[firm])), covered,
      calibratedModel: believedCost === 1 && believedMu === 0.25 });
    previous = prices.slice();
  }
  return { config: { rounds, initialPrices: initialPrices.slice(), epsilon, coverage, releaseAfter, proposal, seed, believedCost, believedMu }, rows,
    benchmarks: { nashPrice: NASH_PRICE, monopolyPrice: MONOPOLY_PRICE, highPriceRegret: brInterval(MONOPOLY_PRICE).bestProfit - profit(MONOPOLY_PRICE, MONOPOLY_PRICE, DEFAULT_MODEL) },
    assumptions: ['Synthetic numerical proposals, not trained policies or AI agents.', 'Proposal high is constant joint-profit price; oscillating alternates boundary prices; random uses separate reproducible PCG streams for A and B, initialized with seed XOR 0xa5a5a5a5 and seed XOR 0x5a5a5a5a respectively (separate streams, not a claim of statistical independence); feedback-high matches high only when last rival price exceeds Nash by 0.05.', 'Both prices settle simultaneously; the action constraint uses only previous completed rival price.', 'oneStepRegretTrue is regret versus previous rival quote under the true model; realizedRegretTrue instead evaluates against the actual current rival quote. Accepted intervals are the potential contract sets even for uncovered sellers; they restrict realized actions only where covered is true.', 'Coverage both with epsilon zero is classical delayed best-response dynamics, not an empirical collusion discovery.', 'Believed cost and logit scale affect only constraint evaluation; true settlement cost remains 1 and true scale remains 0.25. Mismatched rows are uncertified relative to true-market convergence and regret.', 'releaseAfter N applies constraints through round N inclusive and removes them thereafter.', 'Feedback proposals can differ across coverage arms because realized histories differ; exogenous proposal streams share identical draws.'] };
}

