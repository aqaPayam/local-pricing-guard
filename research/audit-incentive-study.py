"""Independent integer/Fraction audit. No primary incentive-study imports.

Core functions are first exercised on synthetic games only. The real study
adapter is added after prospective primary schema review and source freeze.
"""
from fractions import Fraction
from pathlib import Path
import hashlib
import math
import sys
import argparse
import copy
import json
from datetime import datetime, timezone

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def binary_fraction(value):
    """Python's independent binary64 conversion, not JS bit extraction."""
    value = float(value)
    require(math.isfinite(value), 'Finite saved binary64 reward')
    return Fraction(*value.as_integer_ratio())


def rational_json(value):
    value = Fraction(value)
    return {'numerator': str(value.numerator), 'denominator': str(value.denominator)}


def value_hash(values):
    return hashlib.sha256((''.join(str(v)+'\n' for v in values)).encode('ascii')).hexdigest()


def common_integer_rewards(game, seller):
    n = len(game['prices'])
    require(seller in (0, 1), 'Focal seller A or B')
    table = game['rewards']['profitA' if seller == 0 else 'profitB']
    require(len(table) == n*n, 'Complete individual profit table')
    oriented = [binary_fraction(table[a*n+b] if seller == 0 else table[b*n+a])
                for a in range(n) for b in range(n)]
    denominator = max(v.denominator for v in oriented)
    require(denominator > 0 and denominator & (denominator-1) == 0,
            'Common binary64 reward denominator is a power of two')
    return denominator, [v.numerator*(denominator//v.denominator) for v in oriented]


def finite_welfare(game, period):
    n = len(game['prices'])
    upper = [max(s) for s in game['sets']]
    require(all(upper[i] <= upper[i+1] for i in range(n-1)), 'Monotone inherited upper map')
    cs = game['rewards']['consumerSurplus']
    require(len(cs) == n*n, 'Complete saved customer-benefit table')
    for i in range(n):
        for j in range(n):
            if i+1 < n:
                require(cs[(i+1)*n+j] <= cs[i*n+j], 'Coordinate monotone CS in first price')
            if j+1 < n:
                require(cs[i*n+j+1] <= cs[i*n+j], 'Coordinate monotone CS in second price')
    at = game['capIndex']
    orbit, total, floor, horizon = [], Fraction(0), None, None
    profit_totals = [Fraction(0), Fraction(0)]
    for phase in range(period):
        orbit.append(at)
        total += binary_fraction(cs[at*n+at])
        for seller, name in enumerate(('profitA', 'profitB')):
            profit_totals[seller] += binary_fraction(game['rewards'][name][at*n+at])
        average = total/(phase+1)
        if floor is None or average < floor:
            floor, horizon = average, phase+1
        at = upper[at]
    return {'cycleIndices': orbit, 'cycleAverage': total/period,
            'activationFloor': floor, 'minimizingPrefix': horizon,
            'baselineProfitMeans': [x/period for x in profit_totals]}


def calculate(game, period, seller, discount):
    """Recompute every permitted Bellman maximum with Python integers.

    Rolling layers and retained policy bytes suffice; all baseline-path phase
    values are captured while their complete layers are present.
    """
    require(isinstance(period, int) and 1 <= period <= 65536, 'Valid phase period')
    gamma = Fraction(discount)
    require(0 <= gamma < 1, 'Discount below one')
    p, q = gamma.numerator, gamma.denominator
    n = len(game['prices'])
    require(1 <= n <= 256, 'Byte-representable quotes')
    sets = [sorted(s) for s in game['sets']]
    require(len(sets) == n and all(s and len(s) == len(set(s)) and
            all(isinstance(a, int) and 0 <= a < n for a in s) for s in sets), 'Legal saved supports')
    upper = [s[-1] for s in sets]
    cap = game['capIndex']
    require(isinstance(cap, int) and 0 <= cap < n, 'Physical cap index')
    denominator, rewards = common_integer_rewards(game, seller)
    count = n*n
    powers = [q**h for h in range(period)]
    next_opt, next_base = [0]*count, [0]*count
    layers, on_path = {}, {}
    baseline_orbit = [cap]
    for _ in range(1, period):
        baseline_orbit.append(upper[baseline_orbit[-1]])
    comparisons, tied_states, feasibility_checks = 0, 0, 0
    for phase in range(period-1, 0, -1):
        factor = powers[period-phase-1]
        optimal, baseline, policy = [0]*count, [0]*count, bytearray(count)
        for own in range(n):
            other = upper[own]
            for rival in range(n):
                state = own*n+rival
                best, best_action, ties = None, None, 0
                for action in sets[rival]:
                    after = action*n+other
                    candidate = rewards[after]*factor+p*next_opt[after]
                    comparisons += 1
                    if best is None or candidate > best:
                        best, best_action, ties = candidate, action, 1
                    elif candidate == best:
                        ties += 1
                scripted = upper[rival]
                after_script = scripted*n+other
                optimal[state] = best
                baseline[state] = rewards[after_script]*factor+p*next_base[after_script]
                policy[state] = best_action
                require(optimal[state] >= baseline[state], 'Every state optimal block contains baseline policy')
                feasibility_checks += 1
                tied_states += ties > 1
        layers[phase] = {'phase': phase, 'stateCount': count,
                         'valueScaleDenominator': denominator*factor,
                         'valueNumeratorsHash': value_hash(optimal),
                         'baselineNumeratorsHash': value_hash(baseline),
                         'policy': bytes(policy)}
        prior = baseline_orbit[phase-1]
        at = prior*n+prior
        on_path[phase] = {'previous': [prior, prior], 'optimalNumerator': optimal[at],
                          'baselineNumerator': baseline[at], 'scale': denominator*factor,
                          'optimalAction': policy[at], 'baselineAction': upper[prior],
                          'opponentAction': upper[prior]}
        next_opt, next_base = optimal, baseline
    factor = powers[period-1]
    cap_opt, cap_action, cap_ties = None, None, 0
    for action in range(cap+1):
        after = action*n+cap
        candidate = rewards[after]*factor+p*next_opt[after]
        comparisons += 1
        if cap_opt is None or candidate > cap_opt:
            cap_opt, cap_action, cap_ties = candidate, action, 1
        elif candidate == cap_opt:
            cap_ties += 1
    cap_base = rewards[cap*n+cap]*factor+p*next_base[cap*n+cap]
    require(cap_opt >= cap_base, 'Cap optimum includes prescribed cap')
    feasibility_checks += 1
    tied_states += cap_ties > 1
    on_path[0] = {'previous': None, 'optimalNumerator': cap_opt,
                  'baselineNumerator': cap_base, 'scale': denominator*factor,
                  'optimalAction': cap_action, 'baselineAction': cap,
                  'opponentAction': cap}
    j0 = Fraction(q*cap_opt, denominator*(q**period-p**period))
    h0 = Fraction(q*cap_base, denominator*(q**period-p**period))
    phases = []
    for phase in range(period):
        item = on_path[phase]
        v, b = Fraction(item['optimalNumerator'], item['scale']), Fraction(item['baselineNumerator'], item['scale'])
        optimal_infinite = j0 if phase == 0 else v+gamma**(period-phase)*j0
        baseline_infinite = h0 if phase == 0 else b+gamma**(period-phase)*h0
        require(optimal_infinite >= baseline_infinite, 'Nonnegative exact infinite phase gain')
        prior = item['previous']
        support = list(range(cap+1)) if phase == 0 else sets[prior[1]]
        opponent = item['opponentAction']
        best_reward = max(rewards[a*n+opponent] for a in support)
        immediate_action = next(a for a in support if rewards[a*n+opponent] == best_reward)
        immediate_gain = Fraction(best_reward-rewards[item['baselineAction']*n+opponent], denominator)
        phases.append({**item, 'phase': phase, 'optimalBlockValue': v, 'baselineBlockValue': b,
                       'optimalInfiniteValue': optimal_infinite, 'baselineInfiniteValue': baseline_infinite,
                       'infiniteGain': optimal_infinite-baseline_infinite,
                       'immediateBestAction': immediate_action, 'immediateGain': immediate_gain,
                       'immediateBestTies': sum(rewards[a*n+opponent] == best_reward for a in support)})
    # Follow the computed optimal policy on its own history, not the baseline history.
    trace, block_reward, own, rival = [], Fraction(0), None, None
    for phase in range(period):
        action = cap_action if phase == 0 else layers[phase]['policy'][own*n+rival]
        other = cap if phase == 0 else upper[own]
        require(action in (list(range(cap+1)) if phase == 0 else sets[rival]), 'Replayed optimal action is permitted')
        reward = Fraction(rewards[action*n+other], denominator)
        trace.append({'phase': phase, 'focalAction': action, 'opponentAction': other, 'reward': reward})
        block_reward += gamma**phase*reward
        own, rival = action, other
    require(block_reward == Fraction(cap_opt, denominator*factor), 'Complete optimal block reward matches cap Bellman maximum')
    require(block_reward/(1-gamma**period) == j0, 'Exact infinite reset replay')
    screen_phase = period-1 if period > 1 else 0
    screen = phases[screen_phase]
    return {'denominator': denominator, 'layers': layers, 'phases': phases,
            'capOptimalNumerator': cap_opt, 'capBaselineNumerator': cap_base,
            'capOptimalAction': cap_action, 'capTies': cap_ties, 'optimalBlockTrace': trace,
            'oneShotScreen': {'phase': screen_phase, 'kind': 'last-guard' if period > 1 else 'cap',
                              'action': screen['immediateBestAction'], 'gain': screen['immediateGain']},
            'actionComparisons': comparisons, 'tiedStateMaxima': tied_states,
            'feasibilityChecks': feasibility_checks}


def exact_field(field, expected, label):
    require(isinstance(field, dict), label+' rational object')
    require(field.get('numerator') == str(Fraction(expected).numerator) and
            field.get('denominator') == str(Fraction(expected).denominator), label+' reduced exact rational')
    shown = field.get('approximate')
    if shown is not None:
        require(isinstance(shown, (int, float)) and math.isfinite(shown) and
                math.isclose(shown, float(expected), rel_tol=2e-14, abs_tol=1e-14),
                label+' approximate display agrees with exact value')


def check_record(record, game, policy_loader):
    """Check a complete primary record against recomputed values and bytes."""
    require(record.get('status') == 'completed exact unilateral audit', 'Complete exact result status')
    period = record['period']
    seller = {'A': 0, 'B': 1}[record['focalSeller']]
    gamma = Fraction(int(record['discount']['numerator']), int(record['discount']['denominator']))
    expected = calculate(game, period, seller, gamma)
    n, denominator = len(game['prices']), expected['denominator']
    orientation = 'original profitA[own*n+rival]' if seller == 0 else 'original profitB[rival*n+own]'
    require(record['rewardOrientation'] == orientation, 'Focal reward coordinate orientation')
    require(record['profitCommonDenominator'] == str(denominator), 'Minimal common payoff denominator')
    require(record['statesPerGuardLayer'] == n*n, 'All-state guard inventory')
    require([l['phase'] for l in record['layers']] == list(range(1, period)), 'Every complete guard phase retained once')
    for layer in record['layers']:
        phase = layer['phase']
        wanted = expected['layers'][phase]
        require(layer['states'] == n*n and layer['remainingRewards'] == period-phase, 'Layer phase/state counts')
        require(layer['scaleDenominator'] == str(wanted['valueScaleDenominator']), 'Layer exact integer scaling')
        require(layer['optimalValueSha256'] == wanted['valueNumeratorsHash'] and
                layer['baselineValueSha256'] == wanted['baselineNumeratorsHash'], 'Every recomputed state maximum/baseline hash')
        policy = policy_loader(layer['argmaxFile'])
        require(policy == wanted['policy'], 'Every exact argmax action and smallest-index tie')
        require(layer['argmaxBytes'] == n*n and layer['argmaxSha256'] == hashlib.sha256(policy).hexdigest(), 'Complete policy byte length/hash')
    cap = record['cap']
    require(cap['action'] == expected['capOptimalAction'] and cap['baselineAction'] == game['capIndex'] and
            cap['tiedMaximizers'] == expected['capTies'], 'Cap maximizing action/baseline/ties')
    require(cap['scaleDenominator'] == str(denominator*gamma.denominator**(period-1)) and
            cap['optimalNumerator'] == str(expected['capOptimalNumerator']) and
            cap['baselineNumerator'] == str(expected['capBaselineNumerator']), 'Cap integer numerators/scaling')
    first = expected['phases'][0]
    for name, key in [('finiteOptimal', 'optimalBlockValue'), ('finiteBaseline', 'baselineBlockValue'),
                      ('infiniteOptimal', 'optimalInfiniteValue'), ('infiniteBaseline', 'baselineInfiniteValue'),
                      ('infiniteGain', 'infiniteGain')]:
        exact_field(cap[name], first[key], 'Cap '+name)
    require(len(record['phaseDiagnostics']) == period, 'All baseline-path phases retained')
    for phase, (row, wanted) in enumerate(zip(record['phaseDiagnostics'], expected['phases'])):
        require(row['phase'] == phase and row['priorFocalState'] == wanted['previous'] and
                row['remainingRewards'] == period-phase, 'Baseline phase/previous state/excluded old reward')
        for name in ['optimalAction', 'baselineAction', 'opponentAction', 'immediateBestAction', 'immediateBestTies']:
            require(row[name] == wanted[name], 'On-path '+name)
        values = [('finiteOptimal', 'optimalBlockValue'), ('finiteBaseline', 'baselineBlockValue'),
                  ('infiniteOptimal', 'optimalInfiniteValue'), ('infiniteBaseline', 'baselineInfiniteValue'),
                  ('infiniteGain', 'infiniteGain'), ('immediateBestGain', 'immediateGain')]
        for field, key in values:
            exact_field(row[field], wanted[key], 'Phase '+field)
        factor = gamma**(period-phase)
        exact_field(row['nextCycleOptimalContribution'], factor*first['optimalInfiniteValue'], 'Separate optimal next-cycle constant')
        exact_field(row['nextCycleBaselineContribution'], factor*first['baselineInfiniteValue'], 'Separate baseline next-cycle constant')
        base = wanted['baselineInfiniteValue']
        if base <= 0:
            require(row['relativeGain'] is None and row.get('relativeGainUnavailableReason'), 'No relative benefit from a nonpositive baseline')
        else:
            exact_field(row['relativeGain'], wanted['infiniteGain']/base, 'Exact relative gain')
    require(len(record['optimalBlockReplay']) == period, 'Complete optimum block replay length')
    previous = None
    for row, wanted in zip(record['optimalBlockReplay'], expected['optimalBlockTrace']):
        require(row['phase'] == wanted['phase'] and row['priorFocalState'] == previous,
                'Replay phase and public prior state')
        a, b = wanted['focalAction'], wanted['opponentAction']
        require(row['focalAction'] == a and row['opponentAction'] == b and
                row['originalQuoteIndices'] == ([a, b] if seller == 0 else [b, a]), 'Replay focal/original coordinates')
        exact_field(row['profit'], wanted['reward'], 'Replayed individual reward')
        previous = [a, b]
    exact_field(record['replayDiscountedProfit'], first['optimalBlockValue'], 'Complete exact optimum block weighted reward')
    screen, wanted = record['oneShotScreen'], expected['oneShotScreen']
    last = expected['phases'][wanted['phase']]
    require(screen['phase'] == wanted['phase'] and screen['priorFocalState'] == last['previous'] and
            screen['action'] == wanted['action'] and screen['baselineAction'] == last['baselineAction'] and
            screen['opponentAction'] == last['opponentAction'], 'One-shot final-phase permitted action/history')
    require(screen['kind'] == ('cap one-shot analogue' if period == 1 else 'last guard before the next cap'), 'K1/last-guard distinction')
    exact_field(screen['gain'], wanted['gain'], 'Elementary one-shot gain')
    require(screen['positive'] == (wanted['gain'] > 0), 'Exact one-shot sign')
    exact_field(screen['capActivationLowerGain'], gamma**wanted['phase']*wanted['gain'], 'Activation discount of returning-to-baseline deviation')
    checks = record['checks']
    require(checks['allStateBaselineFeasibility'] is True and checks['completeOptimalBlockReplay'] is True and
            checks['exactNonnegativeFiniteGainChecks'] == expected['feasibilityChecks'] and
            checks['exactNonnegativeOnPathInfiniteGains'] == period and
            checks['tiedStateMaxima'] == expected['tiedStateMaxima'], 'All-state feasibility/maximizer check counts')
    return expected


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def safe_child(directory, relative):
    target = (directory/relative).resolve()
    require(target.is_relative_to(directory.resolve()), 'Evidence-relative path remains within study')
    return target


def check_welfare(record, raw, period, raw_hash):
    game = raw['finite']
    expected = finite_welfare(game, period)
    require(record['scenario'] == raw['scenario']['id'] and record['rawCaseSha256'] == raw_hash and
            record['period'] == period, 'Welfare certificate scenario/game/period identity')
    require(len(record['cycle']) == period, 'All finite welfare cycle executions')
    for phase, (row, at) in enumerate(zip(record['cycle'], expected['cycleIndices'])):
        require(row['phase'] == phase and row['quoteIndices'] == [at, at], 'Both-upper cap-first cycle quotes')
        exact_field(row['customerBenefit'], binary_fraction(game['rewards']['consumerSurplus'][at*len(game['prices'])+at]), 'Saved-weight cycle reward')
    exact_field(record['cycleMean'], expected['cycleAverage'], 'Finite all-policy long-run floor')
    exact_field(record['activationAverageFloor'], expected['activationFloor'], 'Finite all-horizon minimum prefix floor')
    require(record['minimizingPrefixLength'] == expected['minimizingPrefix'], 'Correct minimum-prefix horizon')
    for seller, mean in zip(('A', 'B'), expected['baselineProfitMeans']):
        exact_field(record['baselineProfitCycleMeans'][seller], mean, 'Individual prescribed cycle profit')
    require(len(record['targetComparisons']) == len(raw['originalTargets']), 'Every original fixed target retained')
    for target, comparison in zip(raw['originalTargets'], record['targetComparisons']):
        require(comparison['label'] == target['label'], 'Fixed target label')
        requested, actual = binary_fraction(target['requestedTarget']), binary_fraction(target['actualGuaranteedThreshold'])
        exact_field(comparison['requestedTarget'], requested, 'Original requested target')
        exact_field(comparison['actualThreshold'], actual, 'Original relaxed actual threshold')
        reserve = expected['activationFloor']-actual
        require(comparison['activationFloorMeetsTarget'] == (reserve >= 0), 'Finite-only exact target classification')
        exact_field(comparison['activationFloorReserve'], reserve, 'Finite-only target reserve')
    return expected


def check_saved_masks(game):
    """Rebuild saved numerical row supports; no primary mask functions."""
    n = len(game['prices'])
    require(n in (61, 62) and all(game['prices'][i] < game['prices'][i+1] for i in range(n-1)), 'Inherited 61/62-price numerical game')
    profit = game['rewards']['profitA']
    require(len(profit) == n*n, 'Full saved profit matrix')
    require(game['comparisonAllowance'] == game['epsilon']+1e-12, 'Original rounded numerical comparison allowance')
    for rival in range(n):
        values = [profit[own*n+rival] for own in range(n)]
        best = max(values)
        support = [own for own, value in enumerate(values) if best-value <= game['comparisonAllowance']]
        require(support == game['sets'][rival] and support[-1] == game['upper'][rival], 'Every numerical saved mask/upper action')
        require(best == game['rowBestProfits'][rival], 'Saved numerical best-profit row')
    return n*n


def audit(directory=None):
    directory = (directory or ROOT/'research/incentive-results').resolve()
    auditor_hash = digest(Path(__file__))
    manifest, results, index, completion = [read(directory/(name+'.json')) for name in ('manifest', 'results', 'index', 'completion')]
    manifest_hash, results_hash, index_hash = [digest(directory/(name+'.json')) for name in ('manifest', 'results', 'index')]
    dependencies = 0
    for group in ['sourceHashes', 'inputHashes']:
        for relative, wanted in manifest[group].items():
            require(digest(ROOT/relative) == wanted, 'Live frozen dependency '+relative)
            if group == 'sourceHashes':
                require(digest(safe_child(directory, 'sources/'+relative)) == wanted, 'Frozen source snapshot '+relative)
            dependencies += 1
    require(results['manifestSha256'] == index['manifestSha256'] == manifest_hash, 'Main result/index manifest identity')
    require(completion['manifestSha256'] == manifest_hash and completion['resultsSha256'] == results_hash and
            completion['indexSha256'] == index_hash and completion['finalFrozenDependencyCheck']['passed'], 'Completion frozen output identities')
    require(completion['passed'] is True and completion['records'] == 96 and completion['unresolvedRecords'] == 0, 'Complete retained comparison matrix')
    require(completion['resources']['experimentalModelApiCalls'] == completion['resources']['newTrainingRounds'] == 0, 'No seller model calls or training')
    delivery = manifest['v7Delivery']
    require(delivery['receiptSha256'] == digest(ROOT/delivery['receipt']), 'Closed V7 receipt identity')
    receipt = read(ROOT/delivery['receipt'])
    require(receipt['verification']['passed'] is True and receipt['verification']['payloadHashesAndCRC'] is True and
            receipt['sha256'] == delivery['archiveSha256'], 'Closed verified V7 archive binding')
    archive = ROOT/delivery['archive']
    if archive.exists():
        require(digest(archive) == delivery['archiveSha256'], 'Present closed V7 archive exact identity')
    inherited = read(ROOT/'research/sparse-display-results/index.json')
    require(len(inherited['cases']) == len(manifest['plan']['cases']) == 8, 'All eight inherited finite games')
    require({r['scenario'] for r in inherited['cases']} == {r['scenario'] for r in manifest['plan']['cases']}, 'Inherited game scenario set')
    require(manifest['plan']['periodSlots'] == ['permanent-cap', 'closed-effective-95pct', 'fixed-16'] and
            manifest['plan']['focalSellers'] == ['A', 'B'] and manifest['plan']['discounts'] == [{'p': 19, 'q': 20}, {'p': 0, 'q': 1}] and
            manifest['plan']['retainedRecords'] == 96, 'Frozen predeclared incentive matrix')
    records = results['records']
    require(len(records) == len(index['records']) == 96 and len({r['id'] for r in records}) == 96, 'All 96 distinct retained record identities')
    by_id = {r['id']: r for r in records}
    for entry in index['records']:
        record_path = safe_child(directory, entry['file'])
        require(digest(record_path) == entry['sha256'] and read(record_path) == by_id[entry['id']], 'Every indexed record hash/journal equals collected result')
        require(entry['status'] == by_id[entry['id']]['status'], 'Index result status')
    journal = [json.loads(line) for line in (directory/'journal.jsonl').read_text(encoding='utf-8').splitlines() if line]
    require(len(journal) == 192, 'All started/finished execution journals')
    for record in records:
        require([r['status'] for r in journal if r['id'] == record['id']] == ['started', record['status']], 'Exactly one start and retained finish per label')
    welfare_index = {entry['file']: entry for entry in index['welfareCertificates']}
    checked_welfare, seen, details = {}, set(), []
    action_comparisons = state_checks = guard_layers = phases = masks = duplicates = 0
    fixture = None
    for inherited_entry in inherited['cases']:
        sid = inherited_entry['scenario']
        case_path = ROOT/'research/sparse-display-results'/inherited_entry['file']
        require(digest(case_path) == inherited_entry['sha256'], 'Inherited finite case exact hash')
        raw = read(case_path)
        entry = next(e for e in manifest['plan']['cases'] if e['scenario'] == sid)
        require(entry['rawSha256'] == inherited_entry['sha256'] and digest(ROOT/entry['rawFile']) == inherited_entry['sha256'], 'Frozen raw case input matches inherited index')
        require(raw['scenario']['id'] == sid, 'Original scenario identity')
        masks += check_saved_masks(raw['finite'])
        closed = read(ROOT/'research/recurring-results/records'/f'{sid}-effective.json')
        require(closed['scenario'] == sid and closed['continuum'] == 'effective', 'Selected-period effective semantic identity')
        selection = [row for row in closed['comparisons'] if row['label'] == 'cap-95pct']
        require(len(selection) == 1 and selection[0]['status'] == 'largest certified fixed period', 'Closed effective95 selected period exists')
        selected = selection[0]
        target = next(t for t in raw['originalTargets'] if t['label'] == 'cap-95pct')
        target_import = selected.get('actualThresholdImported', selected.get('thresholdImported'))
        require(Fraction(int(target_import['numerator']), int(target_import['denominator'])) == binary_fraction(target['actualGuaranteedThreshold']), 'Inherited absolute 95 target equality')
        slot_periods = [('permanent-cap', 1), ('closed-effective-95pct', selected['largestPeriod']), ('fixed-16', 16)]
        for slot_index, (slot, period) in enumerate(slot_periods):
            duplicate = next((name for name, prior in slot_periods[:slot_index] if prior == period), None)
            for seller in ['A', 'B']:
                for gamma in [Fraction(19, 20), Fraction(0)]:
                    record_id = f'{sid}--{slot}--{seller}--g{gamma.numerator}-{gamma.denominator}'
                    require(record_id in by_id, 'Predeclared case/period/seller/discount retained')
                    record = by_id[record_id]
                    require(record['scenario'] == sid and record['focalSeller'] == seller and record['discount'] ==
                            {'numerator': str(gamma.numerator), 'denominator': str(gamma.denominator)}, 'Retained label identity')
                    require(record['period'] == record['periodSlot']['period'] == period and record['periodSlot']['id'] == slot and
                            record['periodSlot']['duplicateOf'] == duplicate, 'Period-slot identity and explicit duplicate')
                    if slot == 'closed-effective-95pct':
                        require(record['periodSlot']['inheritedSelectionStatus'] == selected['status'] and
                                record['periodSlot']['inheritedActualTarget'] == target_import and
                                record['periodSlot']['inheritedRequestedTarget'] == selected['requestedImported'], 'Closed source period/target metadata')
                    expected = check_record(record, raw['finite'], lambda relative: safe_child(directory, relative).read_bytes())
                    seen.add(record_id)
                    action_comparisons += expected['actionComparisons']
                    state_checks += expected['feasibilityChecks']
                    guard_layers += len(expected['layers'])
                    phases += period
                    duplicates += duplicate is not None
                    reference = record['welfareCertificate']
                    require(reference['file'] in welfare_index and reference == welfare_index[reference['file']] and
                            digest(safe_child(directory, reference['file'])) == reference['sha256'], 'Every exact finite-welfare reference/index hash')
                    if reference['file'] not in checked_welfare:
                        checked_welfare[reference['file']] = check_welfare(read(safe_child(directory, reference['file'])), raw, period, inherited_entry['sha256'])
                    details.append({'id': record_id, 'infiniteActivationGain': rational_json(expected['phases'][0]['infiniteGain']),
                                    'lastPhaseOneShotGain': rational_json(expected['oneShotScreen']['gain']),
                                    'stateMaxima': expected['feasibilityChecks'], 'actionComparisons': expected['actionComparisons']})
                    if period > 1 and fixture is None:
                        fixture = record, raw['finite']
    require(seen == set(by_id) and set(checked_welfare) == set(welfare_index), 'No missing/extraneous retained records or finite certificates')
    require(fixture is not None, 'Guard-phase actual fixture exists')
    # Corruptions are solely in memory; no frozen policy/output file changes.
    baseline_record, baseline_game = fixture
    def corrupted_policy(relative):
        content = bytearray(safe_child(directory, relative).read_bytes())
        content[0] = 255
        return bytes(content)
    mutations = {
        'forbiddenArgmax': (lambda r: None, corrupted_policy),
        'stateValueHash': (lambda r: r['layers'][0].update(optimalValueSha256='0'*64), None),
        'sellerCoordinateIdentity': (lambda r: r.update(rewardOrientation='original profitA[rival*n+own]'), None),
        'infiniteContinuation': (lambda r: r['phaseDiagnostics'][1]['nextCycleOptimalContribution'].update(numerator='-1'), None),
        'oneShotGain': (lambda r: r['oneShotScreen']['gain'].update(numerator='-1'), None)}
    controls = {}
    for name, (mutate, loader) in mutations.items():
        changed = copy.deepcopy(baseline_record)
        mutate(changed)
        rejected = False
        try:
            check_record(changed, baseline_game, loader or (lambda relative: safe_child(directory, relative).read_bytes()))
        except (ValueError, KeyError):
            rejected = True
        require(rejected, 'Rejected actual incentive evidence corruption '+name)
        controls[name] = True
    reference = baseline_record['welfareCertificate']
    altered = read(safe_child(directory, reference['file']))
    altered['activationAverageFloor']['numerator'] = '-1'
    rejected = False
    try:
        raw = read(ROOT/next(e['rawFile'] for e in manifest['plan']['cases'] if e['scenario'] == baseline_record['scenario']))
        check_welfare(altered, raw, baseline_record['period'], digest(ROOT/next(e['rawFile'] for e in manifest['plan']['cases'] if e['scenario'] == baseline_record['scenario'])))
    except (ValueError, KeyError):
        rejected = True
    require(rejected, 'Rejected finite-welfare certificate corruption')
    controls['finiteWelfareCertificate'] = True
    for group in ['sourceHashes', 'inputHashes']:
        for relative, wanted in manifest[group].items():
            require(digest(ROOT/relative) == wanted, 'Final unchanged frozen dependency '+relative)
    require([digest(directory/(name+'.json')) for name in ('manifest', 'results', 'index')] ==
            [manifest_hash, results_hash, index_hash], 'Primary evidence unchanged throughout independent audit')
    require(digest(Path(__file__)) == auditor_hash, 'Auditor source unchanged throughout execution')
    return {'passed': True, 'completedAt': datetime.now(timezone.utc).isoformat(),
            'studyManifestHash': manifest_hash, 'resultsSha256': results_hash, 'indexSha256': index_hash,
            'auditorSourceHash': auditor_hash, 'arithmeticBackendHash': None,
            'records': 96, 'duplicatePolicyLabels': duplicates, 'guardLayers': guard_layers,
            'baselinePathPhaseDiagnostics': phases, 'stateBellmanMaxima': state_checks,
            'permittedActionComparisons': action_comparisons, 'savedMaskPayoffPairs': masks,
            'finiteWelfareCertificates': len(checked_welfare), 'frozenDependencyFiles': dependencies,
            'corruptionNegativeControls': controls, 'details': details,
            'scope': 'Independent Python integer/Fraction implementation and binary64 as_integer_ratio conversion; every full-state permitted-action maximum, policy byte/tie, individual coordinate, phase continuation, reset replay, one-shot screen and exact saved-weight finite-welfare prefix checked. No primary search/conversion imports or shared numerical backend; not formal verification, a learner or equilibrium evidence.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--directory', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = audit(args.directory)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result))
