"""Independent saved-Q / frozen-profile auditor; no primary learner imports.

Prospective core is tested on synthetic graphs before real-case execution.
Exact rational statements concern saved numerical weights, not real markets.
"""
from array import array
from fractions import Fraction
from pathlib import Path
import hashlib
import math
import struct
import sys
import json
import argparse
import copy
import time
from datetime import datetime, timezone
from functools import lru_cache

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def exact_float(value):
    value = float(value)
    require(math.isfinite(value), 'Finite saved binary64 value')
    return Fraction(*value.as_integer_ratio())


def canonical_cycle(states):
    require(states and len(set(states)) == len(states), 'Nonempty simple functional-graph cycle')
    at = states.index(min(states))
    return tuple(states[at:]+states[:at])


def decompose(next_state):
    """Independent functional graph decomposition, with arbitrary transient starts."""
    count = len(next_state)
    require(count and all(isinstance(v, int) and 0 <= v < count for v in next_state), 'Complete functional graph')
    assigned = [None]*count
    cycles = {}
    distance = [0]*count
    for start in range(count):
        if assigned[start] is not None:
            continue
        path, position, at = [], {}, start
        while assigned[at] is None and at not in position:
            position[at] = len(path)
            path.append(at)
            at = next_state[at]
        if assigned[at] is None:
            first = position[at]
            key = canonical_cycle(path[first:])
            cycles[key] = {'states': key, 'basinStates': 0}
            for state in path[first:]:
                assigned[state] = key
            tail = path[:first]
        else:
            key, tail = assigned[at], path
        for state in reversed(tail):
            assigned[state] = key
            distance[state] = distance[next_state[state]]+1
    for key in assigned:
        cycles[key]['basinStates'] += 1
    require(sum(row['basinStates'] for row in cycles.values()) == count, 'Every state assigned to one cycle')
    return {'cycles': cycles, 'cycleByState': assigned, 'distance': distance}


def trace(next_state, start):
    require(isinstance(start, int) and 0 <= start < len(next_state), 'Valid public initial state')
    path, seen, at = [], {}, start
    while at not in seen:
        seen[at] = len(path)
        path.append(at)
        at = next_state[at]
    split = seen[at]
    return {'transient': path[:split], 'cycle': path[split:],
            'canonicalCycle': canonical_cycle(path[split:])}


def phase_count(controller):
    return 2 if controller['kind'] == 'startup-only' else controller['period']


def next_phase(controller, phase):
    return 1 if controller['kind'] == 'startup-only' else (phase+1) % controller['period']


def compact_rows(game, controller):
    n = len(game['prices'])
    rows, offsets = [], [0]
    for phase in range(phase_count(controller)):
        for own in range(n):
            for rival in range(n):
                actions = list(range(game['capIndex']+1)) if phase == 0 else game['sets'][rival]
                require(actions and actions == sorted(set(actions)), 'Ascending original legal action indices')
                rows.append(actions)
                offsets.append(offsets[-1]+len(actions))
    return rows, offsets


def masked_greedy(values, rows, offsets):
    require(len(values) == offsets[-1], 'Every compact legal Q cell present')
    policy = bytearray(len(rows))
    for row, actions in enumerate(rows):
        at = offsets[row]
        best, choice = None, None
        for local, action in enumerate(actions):
            value = values[at+local]
            require(math.isfinite(value), 'Finite every saved Q value')
            if best is None or value > best:
                best, choice = value, action
        policy[row] = choice
    return bytes(policy)


def read_le_array(content, kind):
    code, size = {'f64': ('d', 8), 'u16': ('H', 2)}[kind]
    require(len(content) % size == 0, 'Complete little-endian array cells')
    result = array(code)
    require(result.itemsize == size, 'Supported native scalar width')
    result.frombytes(content)
    if sys.byteorder != 'little':
        result.byteswap()
    return result


def exact_counts(base, overflow, expected_steps):
    """Decode saturated u16 counts, retaining literal65535 versus overflow."""
    previous, table = -1, {}
    for entry in overflow:
        cell, count = (entry['cell'], entry['count']) if isinstance(entry, dict) else entry
        require(isinstance(cell, int) and previous < cell < len(base) and cell >= 0,
                'Sorted unique overflow cells')
        require(base[cell] == 65535 and isinstance(count, int) and 65535 < count <= expected_steps,
                'Saturated exact action-count overflow')
        table[cell], previous = count, cell
    total = sum(base)+sum(count-65535 for count in table.values())
    require(total == expected_steps, 'Exactly one own action update per training round')
    return table


def visit_support(base, overflow, rows, offsets, policy):
    states, actions = bytearray(len(rows)), bytearray(len(rows))
    for row, support in enumerate(rows):
        lo, hi = offsets[row:row+2]
        states[row] = any(base[cell] or cell in overflow for cell in range(lo, hi))
        selected = lo+support.index(policy[row])
        actions[row] = bool(base[selected] or selected in overflow)
    return bytes(states), bytes(actions)


def visit_values(base, overflow, rows, offsets, policy):
    totals, selected = [], []
    for row, support in enumerate(rows):
        lo, hi = offsets[row:row+2]
        totals.append(sum(overflow.get(cell, base[cell]) for cell in range(lo, hi)))
        cell = lo+support.index(policy[row])
        selected.append(overflow.get(cell, base[cell]))
    return totals, selected


def public_graph(game, controller, focal_policies):
    n = len(game['prices'])
    states = phase_count(controller)*n*n
    require(all(len(policy) == states for policy in focal_policies), 'Both full focal policy tables')
    destination, actions = [0]*states, bytearray(2*states)
    for phase in range(phase_count(controller)):
        for a_prev in range(n):
            for b_prev in range(n):
                state = phase*n*n+a_prev*n+b_prev
                a = focal_policies[0][state]
                b = focal_policies[1][phase*n*n+b_prev*n+a_prev]
                allowed_a = list(range(game['capIndex']+1)) if phase == 0 else game['sets'][b_prev]
                allowed_b = list(range(game['capIndex']+1)) if phase == 0 else game['sets'][a_prev]
                require(a in allowed_a and b in allowed_b, 'Full-state phase/focal mask feasibility')
                destination[state] = next_phase(controller, phase)*n*n+a*n+b
                actions[2*state:2*state+2] = bytes([a, b])
    return destination, bytes(actions)


def cycle_means(game, states, actions):
    n = len(game['prices'])
    totals = {name: Fraction(0) for name in ['consumerSurplus', 'profitA', 'profitB', 'priceA', 'priceB']}
    for state in states:
        a, b = actions[2*state:2*state+2]
        for name in ['consumerSurplus', 'profitA', 'profitB']:
            totals[name] += exact_float(game['rewards'][name][a*n+b])
        totals['priceA'] += exact_float(game['prices'][a])
        totals['priceB'] += exact_float(game['prices'][b])
    return {name: value/len(states) for name, value in totals.items()}


def ratio(field, wanted, label):
    wanted = Fraction(wanted)
    require(field['numerator'] == str(wanted.numerator) and field['denominator'] == str(wanted.denominator),
            label+' exact reduced saved-weight rational')
    if field.get('approximate') is not None:
        require(math.isclose(field['approximate'], float(wanted), rel_tol=3e-14, abs_tol=1e-14), label+' approximate display')


def path_metrics(game, controller, nodes, actions):
    if not nodes:
        return None
    result = cycle_means(game, nodes, actions)
    n, total = len(game['prices']), len(nodes)
    result.update({name: [Fraction(0), Fraction(0)] for name in ['maxAllowedUsage', 'maskCount', 'maskFraction', 'maskSpan']})
    caps = 0
    for node in nodes:
        phase, i, j = node//(n*n), node//n % n, node % n
        cap = phase == 0
        caps += cap
        for focal, rival in [(0, j), (1, i)]:
            support = list(range(game['capIndex']+1)) if cap else game['sets'][rival]
            result['maxAllowedUsage'][focal] += actions[2*node+focal] == support[-1]
            result['maskCount'][focal] += len(support)
            result['maskFraction'][focal] += Fraction(len(support), n)
            result['maskSpan'][focal] += exact_float(game['prices'][support[-1]])-exact_float(game['prices'][support[0]])
    for name in ['maxAllowedUsage', 'maskCount', 'maskFraction', 'maskSpan']:
        result[name] = [value/total for value in result[name]]
    result['capRuleFrequency'] = Fraction(caps, total)
    return result


def check_metrics(field, game, controller, nodes, actions):
    wanted = path_metrics(game, controller, nodes, actions)
    if wanted is None:
        require(field is None, 'No reward assigned to an empty transient')
        return
    require(field['rounds'] == len(nodes), 'Exactly one new reward per traversed source node')
    ratio(field['consumerSurplus'], wanted['consumerSurplus'], 'Cycle/path customer benefit')
    for name, keys in [('profits', ('profitA', 'profitB')), ('prices', ('priceA', 'priceB'))]:
        for seller, key in zip(('A', 'B'), keys):
            ratio(field[name][seller], wanted[key], 'Individual cycle/path '+key)
    for name in ['maxAllowedUsage', 'maskCount', 'maskFraction', 'maskSpan']:
        for focal, seller in enumerate(('A', 'B')):
            ratio(field[name][seller], wanted[name][focal], 'Conditional '+name)
    ratio(field['capRuleFrequency'], wanted['capRuleFrequency'], 'Actual cap-rule execution frequency')


def own_floor(raw, controller):
    game = raw['finite']
    n, upper = len(game['prices']), [max(s) for s in game['sets']]
    require(all(upper[i] <= upper[i+1] for i in range(n-1)), 'Finite upper map monotone')
    cs = game['rewards']['consumerSurplus']
    for i in range(n):
        for j in range(n):
            require((i+1 == n or cs[(i+1)*n+j] <= cs[i*n+j]) and
                    (j+1 == n or cs[i*n+j+1] <= cs[i*n+j]), 'Coordinate-decreasing numerical customer benefit')
    at, orbit = game['capIndex'], [game['capIndex']]
    if controller['kind'] == 'startup-only':
        while upper[at] != at:
            require(upper[at] > at and len(orbit) <= n, 'Cap-start increasing finite upper orbit')
            at = upper[at]
            orbit.append(at)
        return {'kind': 'startup-cap-first', 'upperOrbit': orbit, 'fixedPointIndex': at,
                'floor': exact_float(cs[at*n+at]), 'mean': exact_float(cs[at*n+at])}
    period, total, floor = controller['period'], Fraction(0), None
    for t in range(period):
        total += exact_float(cs[at*n+at])
        mean = total/(t+1)
        floor = mean if floor is None else min(floor, mean)
        at = upper[at]
    return {'kind': 'periodic', 'floor': floor, 'mean': total/period}


def check_floor(field, raw, controller):
    wanted = own_floor(raw, controller)
    require(field['kind'] == wanted['kind'], 'Correct finite controller floor family')
    ratio(field['activationFloor'], wanted['floor'], 'Exact same-game cap-first activation floor')
    ratio(field['cycleMean'], wanted['mean'], 'Exact same-game long-run floor')
    if wanted['kind'] == 'startup-cap-first':
        require(field['upperOrbit'] == wanted['upperOrbit'] and field['fixedPointIndex'] == wanted['fixedPointIndex'],
                'Explicit startup upper-map invariant ceiling')
    targets = raw.get('originalTargets', [])
    require(len(field['targetComparisons']) == len(targets), 'All fixed prior targets retained')
    for target, row in zip(targets, field['targetComparisons']):
        actual = exact_float(target['actualGuaranteedThreshold'])
        require(row['label'] == target['label'] and row['activationFloorMeetsTarget'] == (wanted['floor'] >= actual),
                'Same finite floor/old target exact classification')
        ratio(row['actualThreshold'], actual, 'Original relaxed target')
    return wanted


def check_frozen_graph(graph, raw, controller, values, counts, overflow, state, policy_files=None):
    game = raw['finite']
    n = len(game['prices'])
    bound = check_endpoint(game, controller, state)
    guards = None if state['step'] == 0 else (state['step']-1 if controller['kind'] == 'startup-only' else (state['phase']-1) % controller['period'])
    require(graph['endpointInvariant']['upperBoundIndex'] == bound and
            graph['endpointInvariant']['guardStepsSinceCap'] == guards, 'Declared endpoint envelope uses completed, not next, execution phase')
    rows, offsets = compact_rows(game, controller)
    policy = [masked_greedy(actor, rows, offsets) for actor in values]
    if policy_files is not None:
        require(policy == policy_files, 'Every stored greedy action reconstructed from binary64 Q')
    policies_hash = [hashlib.sha256(actor).hexdigest() for actor in policy]
    require(graph['policySha256'] == policies_hash, 'Complete focal greedy policy hashes')
    edges, actions = public_graph(game, controller, policy)
    decomposition = decompose(edges)
    labels = [key[0] for key in decomposition['cycleByState']]
    require(graph['states'] == len(edges) and graph['successorSha256'] == u32_hash(edges) and
            graph['cycleLabelSha256'] == u32_hash(labels) and
            graph['transientDistanceSha256'] == u32_hash(decomposition['distance']), 'Full original-coordinate graph/labels/distances')
    floor = check_floor(graph['floor'], raw, controller)
    declared = graph['cycles']
    keys = sorted(decomposition['cycles'], key=lambda key: key[0])
    require([cycle['id'] for cycle in declared] == [key[0] for key in keys], 'Every canonical frozen cycle retained once')
    cap_labels = set(labels[:n*n])
    visit_rows = [visit_values(counts[f], overflow[f], rows, offsets, policy[f]) for f in range(2)]
    for cycle, key in zip(declared, keys):
        require(cycle['nodes'] == list(key) and cycle['length'] == len(key) and
                cycle['basinStates'] == decomposition['cycles'][key]['basinStates'], 'Cycle membership/order and all-state basin size')
        check_metrics(cycle['metrics'], game, controller, key, actions)
        require(cycle['policyCapReachable'] == (key[0] in cap_labels), 'Greedy policy-cap reachability separate from arbitrary states')
        maxima = [max(actions[2*node+f] for node in key) for f in range(2)]
        require(cycle['maximumExecutedIndices'] == maxima, 'Actual cycle executed-price ceiling')
        applies = controller['kind'] != 'startup-only' or key[0] in cap_labels or all(i <= floor['fixedPointIndex'] for i in maxima)
        require(cycle['floorApplies'] == applies, 'Startup floor not transferred outside its certified basin/ceiling')
        cs = cycle_means(game, key, actions)['consumerSurplus']
        ratio(cycle['floorGap'], cs-floor['floor'], 'Exact frozen-cycle floor headroom')
        if applies:
            require(cs >= floor['floor'], 'Applicable all-policy welfare floor holds')
        for f, seller in enumerate(('A', 'B')):
            focal_rows = [node if f == 0 else node//(n*n)*n*n+(node % n)*n+(node//n % n) for node in key]
            row_counts, action_counts = visit_rows[f]
            wanted = {'unvisitedStates': sum(row_counts[row] == 0 for row in focal_rows),
                      'neverTriedGreedyActions': sum(action_counts[row] == 0 for row in focal_rows),
                      'minimumStateVisits': min(row_counts[row] for row in focal_rows),
                      'minimumActionVisits': min(action_counts[row] for row in focal_rows)}
            require(cycle['trainingSupport'][seller] == wanted, 'Every cycle state/action visit support and exact minima')
        targets = raw.get('originalTargets', [])
        require(len(cycle['targetComparisons']) == len(targets), 'Every original cycle/target comparison')
        for target, comparison in zip(targets, cycle['targetComparisons']):
            actual = exact_float(target['actualGuaranteedThreshold'])
            require(comparison['label'] == target['label'], 'Preserved target label')
            ratio(comparison['actualThreshold'], actual, 'Original cycle target threshold')
            ratio(comparison['gap'], cs-actual, 'Exact cycle versus fixed old target')
    expected_start = state['phase']*n*n+state['previousIndices'][0]*n+state['previousIndices'][1]
    for name, start in [('actualTerminal', expected_start), ('freshCapCounterfactual', n*n-1)]:
        row, wanted = graph[name], trace(edges, start)
        require(row['startNode'] == start and row['start'] ==
                {'phase': start//(n*n), 'previousIndices': [start//n % n, start % n]}, 'Actual terminal versus separately labeled fresh-cap start')
        require(row['transientNodes'] == wanted['transient'] and row['transientRounds'] == len(wanted['transient']) and
                row['cycleNodesFromStart'] == wanted['cycle'] and row['cycleId'] == wanted['canonicalCycle'][0],
                'Complete reachable trajectory without truncated-rollout substitution')
        check_metrics(row['transientMetrics'], game, controller, wanted['transient'], actions)
        check_metrics(row['cycleMetrics'], game, controller, wanted['cycle'], actions)
        canonical = next(c for c in declared if c['id'] == row['cycleId'])
        for field in ['trainingSupport', 'floorApplies', 'floorGap', 'targetComparisons']:
            require(row[field] == canonical[field], 'Trajectory links its reachable cycle certificate '+field)
    require(graph['step'] == state['step'] and graph['actualTerminal']['floorApplies'], 'Checkpoint absolute time and actual cap-start continuation floor')
    if controller['kind'] == 'startup-only' and state['phase'] != 0:
        require(all(i <= floor['fixedPointIndex'] for i in state['previousIndices']), 'Actual trained cap-start history respects the invariant ceiling')
    return {'states': len(edges), 'qCellsPerActor': offsets[-1], 'cycles': len(keys), 'policy': policy,
            'actualCycleBenefit': cycle_means(game, trace(edges, expected_start)['cycle'], actions)['consumerSurplus']}


def check_endpoint(game, controller, state):
    """Actual training history is constrained more than an arbitrary graph node."""
    step, phase, previous = state['step'], state['phase'], state['previousIndices']
    n = len(game['prices'])
    require(isinstance(step, int) and step >= 0 and len(previous) == 2 and
            all(isinstance(i, int) and 0 <= i < n for i in previous), 'Valid actual training checkpoint')
    clock = (0 if step == 0 else 1) if controller['kind'] == 'startup-only' else step % controller['period']
    require(phase == clock, 'Actual endpoint phase agrees with absolute training clock')
    if step == 0:
        require(previous == [n-1, n-1], 'Initial observation is declared highest old history')
        return n-1
    guards = step-1 if controller['kind'] == 'startup-only' else (phase-1) % controller['period']
    upper = [max(s) for s in game['sets']]
    require(all(upper[i] <= upper[i+1] for i in range(n-1)), 'Endpoint upper-map monotonicity')
    ceiling = game['capIndex']
    # A deterministic monotone orbit can be skipped once it reaches a fixed point.
    for _ in range(guards):
        following = upper[ceiling]
        if following == ceiling:
            break
        ceiling = following
    require(all(i <= ceiling for i in previous), 'Actual trained quotes respect phase-specific cap-start upper envelope')
    return ceiling


def u32_hash(values):
    return hashlib.sha256(b''.join(struct.pack('<I', value) for value in values)).hexdigest()


def mulberry_indices(seed=20261026, repeats=5120, size=12):
    mask, state, draws = 2**32-1, seed, []
    for _ in range(repeats):
        row = []
        for _ in range(size):
            state = (state+0x6D2B79F5) & mask
            value = ((state ^ (state >> 15))*(state | 1)) & mask
            value ^= (value+(((value ^ (value >> 7))*(value | 61)) & mask)) & mask
            row.append((size*((value ^ (value >> 14)) & mask))//2**32)
        draws.append(row)
    return draws


def type7(values, percentile):
    require(values and 0 <= percentile <= 1 and all(math.isfinite(v) for v in values), 'Finite percentile sample')
    ordered = sorted(values)
    at = (len(ordered)-1)*percentile
    lower, upper = math.floor(at), math.ceil(at)
    return ordered[lower]+(ordered[upper]-ordered[lower])*(at-lower)


MASK32 = 2**32-1


def rotl32(value, shift):
    return ((value << shift) | (value >> (32-shift))) & MASK32


def xoshiro_step(state):
    require(len(state) == 4 and any(state) and all(isinstance(x, int) and 0 <= x <= MASK32 for x in state), 'Nonzero unsigned xoshiro128 state')
    a, b, c, d = state
    result = (rotl32((b*5) & MASK32, 7)*9) & MASK32
    shifted = (b << 9) & MASK32
    c ^= a
    d ^= b
    b ^= c
    a ^= d
    c ^= shifted
    d = rotl32(d, 11)
    return result, (a, b, c, d)


def xoshiro_jump(state):
    """Published 2^64 jump; checked against independent GF(2) matrix powering."""
    output = [0, 0, 0, 0]
    state = tuple(state)
    for word in [0x8764000b, 0xf542d2d3, 0x6fa035c3, 0x77f2db5b]:
        for bit in range(32):
            if word & (1 << bit):
                output = [a ^ b for a, b in zip(output, state)]
            _, state = xoshiro_step(state)
    return tuple(output)


def pack_state(state):
    return sum(word << (32*i) for i, word in enumerate(state))


def unpack_state(state):
    return tuple((state >> (32*i)) & MASK32 for i in range(4))


def apply_linear(columns, vector):
    result = 0
    while vector:
        bit = vector & -vector
        result ^= columns[bit.bit_length()-1]
        vector ^= bit
    return result


@lru_cache(None)
def transition_power(power):
    if power == 0:
        return tuple(pack_state(xoshiro_step(unpack_state(1 << bit))[1]) for bit in range(128))
    previous = transition_power(power-1)
    return tuple(apply_linear(previous, column) for column in previous)


def advance_xoshiro(state, steps):
    require(isinstance(steps, int) and steps >= 0, 'Nonnegative PRNG distance')
    vector, power = pack_state(state), 0
    while steps:
        if steps & 1:
            vector = apply_linear(transition_power(power), vector)
        steps >>= 1
        power += 1
    return unpack_state(vector)


def exploration_value(step, horizon):
    if step == 0:
        return 1.
    if step >= horizon-1:
        return .01
    return math.exp(-math.log(100)*step/(horizon-1))


def replay_updates(game, controller, values, rows, offsets, state, witnesses,
                   horizon=2_000_000, alpha=.1, gamma=.95):
    """Replay a declared short probe; this never asserts full-training replay."""
    q = [array('d', actor) for actor in values]
    step, phase, previous = state['step'], state['phase'], list(state['previousIndices'])
    rng = [tuple(actor) for actor in state['actorStates']]
    n = len(game['prices'])
    changed = [set(), set()]
    for witness in witnesses:
        require(witness['step'] == step and witness['phase'] == phase and witness['previous'] == previous,
                'Probe correct absolute clock and completed public history')
        source = [phase*n*n+previous[0]*n+previous[1], phase*n*n+previous[1]*n+previous[0]]
        require(witness['rows'] == source, 'Probe focal-B state transposition')
        epsilon = exploration_value(step, horizon)
        require(math.isclose(witness['exploration'], epsilon, rel_tol=2e-15, abs_tol=2e-16), 'Declared binary64 exponential exploration schedule')
        draws, actions = [], []
        for actor in range(2):
            first, rng[actor] = xoshiro_step(rng[actor])
            second, rng[actor] = xoshiro_step(rng[actor])
            u, v = first/2**32, second/2**32
            draws.append([u, v])
            require(abs(u-epsilon) > 2e-15, 'Probe exploration branch unambiguous across math libraries')
            support, off = rows[source[actor]], offsets[source[actor]]
            current = list(q[actor][off:offsets[source[actor]+1]])
            require(witness['supports'][actor] == support and witness['currentQRows'][actor] == current,
                    'Probe actual compact legal Q row')
            best = max(current)
            choice = support[math.floor(v*len(support))] if u < epsilon else support[current.index(best)]
            actions.append(choice)
        require(witness['draws'] == draws and witness['actions'] == actions, 'Independent PRNG and simultaneous pre-update actions')
        new_phase = next_phase(controller, phase)
        targets, old_values, new_values, max_values = [], [], [], []
        next_rows = [new_phase*n*n+actions[0]*n+actions[1], new_phase*n*n+actions[1]*n+actions[0]]
        require(witness['nextRows'] == next_rows and witness['nextPhase'] == new_phase and
                witness['nextPrevious'] == actions, 'Continuing next-phase cap/guard state')
        # Both bootstrap maxima are read before either private table changes.
        for actor, key in enumerate(['profitA', 'profitB']):
            off, end = offsets[next_rows[actor]:next_rows[actor]+2]
            future_row = list(q[actor][off:end])
            require(witness['nextQRows'][actor] == future_row, 'Next legal support Q row before updates')
            maximum = max(future_row)
            reward = game['rewards'][key][actions[0]*n+actions[1]]
            require(witness['expectedProfits'][actor] == reward, 'Own deterministic expected-profit reward orientation')
            current_off = offsets[source[actor]]
            cell = current_off+rows[source[actor]].index(actions[actor])
            old = q[actor][cell]
            target = reward+gamma*maximum
            value = old+alpha*(target-old)
            targets.append(target)
            old_values.append(old)
            new_values.append(value)
            max_values.append(maximum)
        require(witness['maxNext'] == max_values and witness['oldQ'] == old_values and witness['targets'] == targets and
                witness['newQ'] == new_values, 'Independent binary64 continuing-Q update arithmetic')
        for actor in range(2):
            cell = offsets[source[actor]]+rows[source[actor]].index(actions[actor])
            q[actor][cell] = new_values[actor]
            changed[actor].add(cell)
        require(witness['actorStatesAfter'] == [list(actor) for actor in rng], 'Probe private PRNG endpoint')
        step, phase, previous = step+1, new_phase, actions
    return {'q': q, 'step': step, 'phase': phase, 'previousIndices': previous,
            'actorStates': [list(actor) for actor in rng], 'changedCells': changed}


def digest(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def child(directory, relative):
    candidate, parent = (Path(directory)/relative).resolve(), Path(directory).resolve()
    require(candidate.is_relative_to(parent) and candidate != parent, 'Evidence path stays inside study directory')
    return candidate


def artifact(directory, entry):
    path = child(directory, entry['file'])
    content = path.read_bytes()
    require(len(content) == entry['bytes'] and hashlib.sha256(content).hexdigest() == entry['sha256'],
            'Declared artifact bytes/hash '+entry['file'])
    return content


def normalize(control):
    return {'kind': 'startup-only'} if control['id'] == 'startup-only' else {'kind': 'periodic', 'period': control['period']}


def bytes_hash(values, code):
    return hashlib.sha256(b''.join(struct.pack('<'+code, value) for value in values)).hexdigest()


def counts_after(base, overflow, rows, offsets, traces, actor):
    updated, bigger = array('H', base), dict(overflow)
    for trace_row in traces:
        row = trace_row['rows'][actor]
        cell = offsets[row]+rows[row].index(trace_row['actions'][actor])
        value = bigger.get(cell, updated[cell])+1
        updated[cell] = min(value, 65535)
        if value > 65535:
            bigger[cell] = value
    return updated, bigger


def check_identity(identity, values, counts, overflow, state, rows, offsets, windows, cap_executions):
    for name in ['step', 'phase', 'previousIndices', 'actorStates']:
        require(identity[name] == state[name], 'Checkpoint/probe identity '+name)
    require(identity['capExecutions'] == cap_executions, 'Cap execution count independent of actual quote changes')
    for f in range(2):
        policy = masked_greedy(values[f], rows, offsets)
        maximum = [values[f][offsets[row]+rows[row].index(policy[row])] for row in range(len(rows))]
        require(identity['qSha256'][f] == bytes_hash(values[f], 'd') and
                identity['countSha256'][f] == bytes_hash(counts[f], 'H') and
                identity['countOverflow'][f] == [list(pair) for pair in sorted(overflow[f].items())] and
                identity['bestCacheSha256'][f] == hashlib.sha256(policy).hexdigest() and
                identity['maxCacheSha256'][f] == bytes_hash(maximum, 'd'), 'Full Q/count/cache identity independently rebuilt')
    require(identity['windows'] == windows, 'Cloned diagnostic leaves main training windows unchanged')


def check_windows(entries, contents, raw, controller, step, horizon):
    game, n = raw['finite'], len(raw['finite']['prices'])
    prices = list(map(exact_float, game['prices']))
    reward = {key: list(map(exact_float, game['rewards'][key])) for key in ['consumerSurplus', 'profitA', 'profitB']}
    identities, active = [], None
    for index, (entry, content) in enumerate(zip(entries, contents)):
        end = horizon//2 if index == 0 else horizon
        start = max(0, end-100000)
        rounds = max(0, min(step, end)-start)
        require(entry['startStep'] == start and entry['endStep'] == end and entry['rounds'] == rounds,
                'Training windows have fixed absolute boundaries')
        require(len(content) % 8 == 0, 'Complete sparse joint-window entries')
        sums = {key: Fraction(0) for key in ['consumerSurplus', 'profitA', 'profitB', 'priceA', 'priceB']}
        measures = {key: [Fraction(0), Fraction(0)] for key in ['maxAllowedUsage', 'maskCount', 'maskFraction', 'maskSpan']}
        total, caps, previous_key, number = 0, 0, -1, 0
        for key, count in struct.iter_unpack('<II', content):
            require(key > previous_key and count > 0, 'Strictly sorted positive joint-window counts')
            previous_key, number = key, number+1
            source, pair = divmod(key, n*n)
            phase, rem = divmod(source, n*n)
            i, j = divmod(rem, n)
            a, b = divmod(pair, n)
            require(phase < phase_count(controller), 'Window source phase within controller')
            supports = [list(range(game['capIndex']+1))]*2 if phase == 0 else [game['sets'][j], game['sets'][i]]
            require(a in supports[0] and b in supports[1], 'Window simultaneous actions legal against previous rival')
            total += count
            caps += count*(phase == 0)
            for name in reward:
                sums[name] += reward[name][pair]*count
            sums['priceA'] += prices[a]*count
            sums['priceB'] += prices[b]*count
            for f, action in enumerate((a, b)):
                support = supports[f]
                measures['maxAllowedUsage'][f] += count*(action == support[-1])
                measures['maskCount'][f] += count*len(support)
                measures['maskFraction'][f] += Fraction(count*len(support), n)
                measures['maskSpan'][f] += count*(prices[support[-1]]-prices[support[0]])
        require(total == rounds and entry['maxAllowed'] == [int(v) for v in measures['maxAllowedUsage']], 'Exact joint-window counter reconciliation')
        identities.append({'endStep': end, 'startStep': start, 'rounds': rounds, 'maxAllowed': entry['maxAllowed'],
                           'transitionEntries': number, 'transitionsSha256': hashlib.sha256(content).hexdigest()})
        if end != step:
            continue
        active = {'startStep': start, 'endStep': step, 'rounds': total, 'sums': sums, 'measures': measures, 'caps': caps}
    require(len(identities) == 2 and active is not None, 'Both planned windows retained and checkpoint window available')
    return identities, active


def check_window_metrics(field, wanted, horizon):
    count = wanted['rounds']
    for key in ['startStep', 'endStep', 'rounds']:
        require(field[key] == wanted[key], 'Actual window '+key)
    ratio(field['consumerSurplus'], wanted['sums']['consumerSurplus']/count, 'Actual exploratory window customer benefit')
    for name, keys in [('profits', ('profitA', 'profitB')), ('prices', ('priceA', 'priceB'))]:
        for seller, key in zip(('A', 'B'), keys):
            ratio(field[name][seller], wanted['sums'][key]/count, 'Actual exploratory window '+key)
    for name, values in wanted['measures'].items():
        for f, seller in enumerate(('A', 'B')):
            ratio(field[name][seller], values[f]/count, 'Actual exploratory '+name)
    ratio(field['capRuleFrequency'], Fraction(wanted['caps'], count), 'Actual window cap activation frequency')
    epsilon = sum(exploration_value(t, horizon) for t in range(wanted['startStep'], wanted['endStep']))/count
    require(math.isclose(field['explorationMean'], epsilon, rel_tol=3e-14, abs_tol=2e-15), 'Actual approximate exploration average')


def check_checkpoint(directory, entry, raw, plan, namespace, horizon=2000000):
    metadata_path = child(directory, entry['file'])
    require(digest(metadata_path) == entry['sha256'], 'Checkpoint metadata identity')
    meta = read(metadata_path)
    control, game = normalize(plan['control']), raw['finite']
    step, n = entry['step'], len(game['prices'])
    require(meta['step'] == step and step in (horizon//2, horizon) and meta['control'] == plan['control'] and
            meta['seed'] == plan['seed'] and meta['initialization'] == plan['initialization'] and
            meta['T'] == horizon and meta['alpha'] == .1 and meta['gamma'] == .95, 'Checkpoint algorithm/design identity')
    check_endpoint(game, control, meta)
    require(meta['actorStates'] == [list(advance_xoshiro(tuple(state), 2*step)) for state in namespace], 'Every actor checkpoint RNG independently advanced by GF(2)')
    cap_count = (step > 0) if control['kind'] == 'startup-only' else (step+control['period']-1)//control['period']
    require(meta['capExecutions'] == cap_count, 'Exactly scheduled cap activations')
    initial = [0., 0.] if plan['initialization'] == 'zero' else [20*max(game['rewards'][key]) for key in ['profitA', 'profitB']]
    require(meta['initialValues'] == initial, 'Declared constant Q initializations')
    rows, offsets = compact_rows(game, control)
    require(meta['layout']['n'] == n and meta['layout']['rows'] == len(rows) and meta['layout']['cells'] == offsets[-1] and
            meta['layout']['offsetsSha256'] == u32_hash(offsets), 'Independently reconstructed compact legal layout')
    files = meta['files']
    require(all(len(files[key]) == 2 for key in ['q', 'counts', 'policies', 'windows']), 'Complete both-firm and window artifacts')
    values = [read_le_array(artifact(directory, item), 'f64') for item in files['q']]
    counts = [read_le_array(artifact(directory, item), 'u16') for item in files['counts']]
    require(all(len(a) == offsets[-1] for a in values+counts), 'Every saved legal cell/count present')
    overflow = [exact_counts(counts[f], meta['countOverflow'][f], step) for f in range(2)]
    policy = [artifact(directory, item) for item in files['policies']]
    windows, active = check_windows(files['windows'], [artifact(directory, item) for item in files['windows']], raw, control, step, horizon)
    check_window_metrics(meta['trainingWindow'], active, horizon)
    require(entry['trainingWindow'] == meta['trainingWindow'] and entry['coverage'] == meta['coverage'] and
            entry['terminal'] == {'phase': meta['phase'], 'previousIndices': meta['previousIndices']}, 'Indexed checkpoint duplicated summaries agree')
    check_identity(meta['identity'], values, counts, overflow, meta, rows, offsets, windows, cap_count)
    graph = json.loads(artifact(directory, files['graph']))
    evaluated = check_frozen_graph(graph, raw, control, values, counts, overflow, meta, policy)
    require(entry['graph'] == files['graph'] and entry['actualTerminal'] == graph['actualTerminal'] and
            entry['freshCapCounterfactual'] == graph['freshCapCounterfactual'], 'Checkpoint graph/terminal references exact')
    require(meta['coverage']['statesPerFirm'] == len(rows) and meta['coverage']['legalCellsPerFirm'] == offsets[-1], 'Coverage denominators')
    for f, seller in enumerate(('A', 'B')):
        visits, _ = visit_values(counts[f], overflow[f], rows, offsets, policy[f])
        require(meta['coverage'][seller] == {'visitedStates': sum(v > 0 for v in visits), 'visitedActions': sum(v > 0 for v in counts[f])}, 'Full actual state/action coverage')
    preview, at = graph['terminalPreview128'], meta['phase']*n*n+meta['previousIndices'][0]*n+meta['previousIndices'][1]
    edges, actions = public_graph(game, control, policy)
    require(len(preview) == 128, 'Explicit truncated preview length')
    for number, item in enumerate(preview):
        a, b = actions[2*at:2*at+2]
        require(item['execution'] == number+1 and item['sourceNode'] == at and item['phase'] == at//(n*n) and
                item['previousIndices'] == [at//n % n, at % n] and item['executedIndices'] == [a, b] and
                item['prices'] == [game['prices'][a], game['prices'][b]] and
                item['consumerSurplus'] == game['rewards']['consumerSurplus'][a*n+b] and
                item['profits'] == [game['rewards']['profitA'][a*n+b], game['rewards']['profitB'][a*n+b]],
                'Truncated preview follows exact actual-terminal graph and saved individual rewards')
        at = edges[at]
    probe = json.loads(artifact(directory, files['probe']))
    require(entry['probe'] == files['probe'] and probe['diagnosticSteps'] == len(probe['traces']) == 32 and
            probe['originalUnchanged'] is True and probe['before'] == meta['identity'], 'Cloned short probe from saved main checkpoint')
    replay = replay_updates(game, control, values, rows, offsets, meta, probe['traces'], horizon)
    future_counts, future_overflow = zip(*(counts_after(counts[f], overflow[f], rows, offsets, probe['traces'], f) for f in range(2)))
    future_caps = cap_count+sum(w['phase'] == 0 for w in probe['traces'])
    check_identity(probe['afterClone'], replay['q'], future_counts, future_overflow, replay, rows, offsets, windows, future_caps)
    return {'meta': meta, 'graph': graph, 'values': values, 'counts': counts, 'overflow': overflow,
            'evaluated': evaluated, 'probe': probe, 'qCells': 2*offsets[-1], 'states': len(edges),
            'cycles': evaluated['cycles'], 'endpoint': evaluated['actualCycleBenefit']}


def check_sampled_update(raw, plan, namespace, witness):
    game, control, step = raw['finite'], normalize(plan['control']), witness['step']
    rows, offsets = compact_rows(game, control)
    values = [array('d', [0.])*offsets[-1] for _ in range(2)]
    for f in range(2):
        assigned = {}
        for key, vectors in [('rows', 'currentQRows'), ('nextRows', 'nextQRows')]:
            row, row_values = witness[key][f], witness[vectors][f]
            require(len(row_values) == len(rows[row]), 'Sampled update complete actual legal row')
            require(row not in assigned or assigned[row] == row_values, 'Overlapping sampled current/next rows agree before update')
            assigned[row] = row_values
            values[f][offsets[row]:offsets[row+1]] = array('d', row_values)
    state = {'step': step, 'phase': witness['phase'], 'previousIndices': witness['previous'],
             'actorStates': [list(advance_xoshiro(tuple(actor), 2*step)) for actor in namespace]}
    check_endpoint(game, control, state)
    replay_updates(game, control, values, rows, offsets, state, [witness])


def negative_controls(fixture, raw, plan):
    graph, meta = fixture['graph'], fixture['meta']
    control, game = normalize(plan['control']), raw['finite']
    rows, offsets = compact_rows(game, control)
    def verify_graph(altered=None, state=None, policies=None, values=None):
        return check_frozen_graph(altered or graph, raw, control, values or fixture['values'],
                                  fixture['counts'], fixture['overflow'], state or meta, policies)
    controls = {}
    def reject(name, action):
        rejected = False
        try:
            action()
        except (ValueError, KeyError, IndexError):
            rejected = True
        require(rejected, 'Scientific corruption rejected '+name)
        controls[name] = True
    policies = list(fixture['evaluated']['policy'])
    corrupt = bytearray(policies[0]); corrupt[0] = 255
    reject('forbiddenPolicyByte', lambda: verify_graph(policies=[bytes(corrupt), policies[1]]))
    altered = copy.deepcopy(graph); altered['successorSha256'] = '0'*64
    reject('wrongJointOrSellerBCoordinates', lambda: verify_graph(altered))
    altered = copy.deepcopy(graph); altered['cycles'][0]['metrics']['consumerSurplus']['numerator'] = '-1'
    reject('alteredCycleCustomerBenefit', lambda: verify_graph(altered))
    altered = copy.deepcopy(graph); altered['floor']['activationFloor']['numerator'] = '-1'
    reject('alteredAllPolicyFloor', lambda: verify_graph(altered))
    altered = copy.deepcopy(graph); altered['cycles'][0]['trainingSupport']['B']['minimumStateVisits'] += 1
    reject('alteredTrainingVisitSupport', lambda: verify_graph(altered))
    altered = copy.deepcopy(graph); altered['actualTerminal']['startNode'] = graph['freshCapCounterfactual']['startNode']
    reject('freshCapSubstitutedForActualTerminal', lambda: verify_graph(altered))
    altered_state = {**meta, 'phase': 0 if meta['phase'] else 1}
    reject('wrongActualClock', lambda: verify_graph(state=altered_state))
    ceiling = check_endpoint(game, control, meta)
    require(ceiling+1 < len(game['prices']), 'Actual corruption fixture has an outside-envelope quote')
    altered_state = {**meta, 'previousIndices': [ceiling+1, 0]}
    reject('outOfInvariantActualHistory', lambda: verify_graph(state=altered_state))
    altered = copy.deepcopy(graph); altered['cycles'][0]['targetComparisons'][0]['gap']['numerator'] = '-1'
    reject('alteredFixedTargetGap', lambda: verify_graph(altered))
    altered_values = list(fixture['values']); changed = array('d', altered_values[0]); changed[0] = math.nan; altered_values[0] = changed
    reject('alteredNonfiniteQValue', lambda: verify_graph(values=altered_values))
    probes = copy.deepcopy(fixture['probe']['traces']); probes[0]['newQ'][1] += 1
    reject('alteredPrivateQUpdate', lambda: replay_updates(game, control, fixture['values'], rows, offsets, meta, probes))
    return controls


def audit(directory=None):
    """Read-only complete checkpoint audit; writing a receipt is a separate CLI option."""
    directory = Path(directory or ROOT/'research/adaptive-learning-results').resolve()
    began, auditor_hash = time.perf_counter(), digest(Path(__file__))
    manifest, results, index, completion = [read(directory/(name+'.json')) for name in ['manifest', 'results', 'index', 'completion']]
    manifest_hash, results_hash, index_hash, completion_hash = [digest(directory/(name+'.json')) for name in ['manifest', 'results', 'index', 'completion']]
    for group in ['sourceHashes', 'inputHashes']:
        for relative, wanted in manifest[group].items():
            require(digest(ROOT/relative) == wanted, 'Live frozen dependency '+relative)
            if group == 'sourceHashes':
                require(digest(child(directory, 'sources/'+relative)) == wanted, 'Frozen source snapshot '+relative)
    require(completion['passed'] is True and completion['unresolvedRuns'] == 0 and completion['runs'] == 192 and
            completion['checkpoints'] == 384 and completion['finalFrozenDependencyCheck']['passed'] is True,
            'All predeclared runs/checkpoints complete; no selective successful subset')
    require(results['manifestSha256'] == index['manifestSha256'] == completion['manifestSha256'] == manifest_hash and
            completion['resultsSha256'] == results_hash and completion['indexSha256'] == index_hash, 'All complete evidence identity bindings')
    plan = manifest['plan']
    require(plan['roundsPerRun'] == 2000000 and plan['checkpoints'] == [1000000, 2000000] and
            plan['alpha'] == .1 and plan['gamma'] == .95 and plan['retainedRuns'] == 192, 'Prospective learning design constants')
    namespaces, at = {}, (907001, 907002, 907003, 907004)
    for seed in range(907001, 907013):
        namespaces[seed] = [list(at)]
        at = xoshiro_jump(at)
        namespaces[seed].append(list(at))
        at = xoshiro_jump(at)
    require(manifest['actorNamespaces'] == [{'seed': seed, 'segments': [2*(seed-907001), 2*(seed-907001)+1],
                                            'actors': actors} for seed, actors in namespaces.items()], 'Exact independent jumped actor namespaces')
    cases = plan['cases']
    require([(c['scenario'], c['selectedPeriod']) for c in cases] == [('base-g15-t1', 4), ('base-g15-t0.5', 10)], 'Exactly two inherited mask conditions')
    raw_cases = {}
    for case in cases:
        require(digest(ROOT/case['rawFile']) == case['rawSha256'], 'Unchanged inherited finite game')
        raw = read(ROOT/case['rawFile'])
        require(raw['scenario']['id'] == case['scenario'], 'Finite game case identity')
        raw_cases[case['scenario']] = raw
    expected = []
    for case in cases:
        for initialization in ['zero', 'optimistic']:
            for seed in range(907001, 907013):
                for label, period in [('startup-only', None), ('permanent-cap', 1), ('selected95', case['selectedPeriod']), ('K16', 16)]:
                    expected.append({'id': f"{case['scenario']}--{label}--{initialization}--s{seed}", 'scenario': case['scenario'],
                                     'rawFile': case['rawFile'], 'rawSha256': case['rawSha256'], 'initialization': initialization, 'seed': seed,
                                     'control': {'id': label, 'period': period, 'phases': 2 if period is None else period}})
    require(plan['runs'] == expected and len(results['records']) == len(index['records']) == 192, 'Every fixed seed/game/controller/init identity retained')
    journal = [json.loads(line) for line in (directory/'journal.jsonl').read_text(encoding='utf-8').splitlines() if line]
    require(len(journal) == 4*192, 'Exactly start, two checkpoint, finish events per successful run')
    details, endpoints, counters, controls = [], {}, {'qCells': 0, 'states': 0, 'cycles': 0, 'probes': 0, 'sampledUpdates': 0}, None
    for number, (planned, record, indexed) in enumerate(zip(expected, results['records'], index['records'])):
        require(all(record[key] == value for key, value in planned.items()) and indexed['id'] == record['id'] and
                indexed['status'] == record['status'] == 'completed frozen-policy evaluation' and record['actualMainRounds'] == 2000000,
                'All completed retained planned identities and exact horizon')
        path = child(directory, indexed['file'])
        require(digest(path) == indexed['sha256'] and read(path) == record, 'Indexed record/journal byte identity')
        own_events = journal[number*4:number*4+4]
        require([row['id'] for row in own_events] == [planned['id']]*4 and
                [row['status'] for row in own_events] == ['started', 'checkpoint saved', 'checkpoint saved', 'completed frozen-policy evaluation'] and
                [row['step'] for row in own_events[1:3]] == [1000000, 2000000], 'Complete chronological planned-case execution journal')
        require(len(record['checkpoints']) == 2 and [c['step'] for c in record['checkpoints']] == [1000000, 2000000] and
                indexed['checkpoints'] == [{key: c[key] for key in ['step', 'file', 'sha256']} for c in record['checkpoints']], 'Both actual checkpoints indexed')
        raw, namespace = raw_cases[planned['scenario']], namespaces[planned['seed']]
        for position, checkpoint in enumerate(record['checkpoints']):
            require(own_events[position+1]['metadataSha256'] == checkpoint['sha256'], 'Checkpoint journal identity')
            checked = check_checkpoint(directory, checkpoint, raw, planned, namespace)
            for key in ['qCells', 'states', 'cycles']:
                counters[key] += checked[key]
            counters['probes'] += 32
            if checkpoint['step'] == 2000000:
                endpoints[planned['id']] = float(checked['endpoint'])
            details.append({'id': planned['id'], 'step': checkpoint['step'], 'qCells': checked['qCells'],
                            'jointStates': checked['states'], 'cycles': checked['cycles'],
                            'terminalCycleCS': {'numerator': str(checked['endpoint'].numerator), 'denominator': str(checked['endpoint'].denominator)},
                            'floorApplies': checked['graph']['actualTerminal']['floorApplies']})
            if controls is None and planned['control']['id'] == 'startup-only':
                controls = negative_controls(checked, raw, planned)
        traces = record['sampledUpdateTraces']
        require([w['step'] for w in traces] == list(range(16))+list(range(100000, 2000000, 100000)), 'All declared sampled training update times retained')
        # Initial sixteen rounds really are replayed from the declared constants.
        rows, offsets = compact_rows(raw['finite'], normalize(planned['control']))
        initial = [0., 0.] if planned['initialization'] == 'zero' else [20*max(raw['finite']['rewards'][key]) for key in ['profitA', 'profitB']]
        replay_updates(raw['finite'], normalize(planned['control']), [array('d', [value])*offsets[-1] for value in initial], rows, offsets,
                       {'step': 0, 'phase': 0, 'previousIndices': [len(raw['finite']['prices'])-1]*2, 'actorStates': namespace}, traces[:16])
        for witness in traces[16:]:
            check_sampled_update(raw, planned, namespace, witness)
        counters['sampledUpdates'] += len(traces)
        require(len(record['curves']) == 200 and [(row['startStep'], row['endStep'], row['rounds']) for row in record['curves']] ==
                [(t, t+10000, 10000) for t in range(0, 2000000, 10000)], 'Approximate plot blocks retain complete time coverage')
        print(json.dumps({'auditedRun': number+1, 'of': 192, 'id': planned['id']}), file=sys.stderr, flush=True)
    bootstrap_path = ROOT/'research/adaptive-bootstrap-indices.json'
    require(digest(bootstrap_path) == '8fd7455251b3d7faa50ad0125672ab5f0adfa8763a78988d41575a25af05cfbc', 'Prospective resample hash')
    draws = mulberry_indices()
    require(read(bootstrap_path)['indices'] == draws, 'All independent Mulberry32 resample indices')
    contrasts = []
    for case in cases:
        for initialization in ['zero', 'optimistic']:
            pairs = [endpoints[f"{case['scenario']}--selected95--{initialization}--s{seed}"]-
                     endpoints[f"{case['scenario']}--startup-only--{initialization}--s{seed}"] for seed in range(907001, 907013)]
            means = sorted(sum(pairs[i] for i in row)/12 for row in draws)
            contrasts.append({'scenario': case['scenario'], 'initialization': initialization, 'pairs': pairs, 'n': 12,
                              'mean': sum(pairs)/12, 'median': type7(pairs, .5), 'minimum': min(pairs), 'maximum': max(pairs),
                              'lower': type7(means, .025), 'upper': type7(means, .975), 'bootstrapReplicates': 5120})
    require(completion['resources']['mainTrainingRounds'] == 384000000 and completion['resources']['cloneDiagnosticSteps'] == 12288 and
            completion['resources']['experimentalModelApiCalls'] == 0, 'Declared main/diagnostic computational inventory')
    for group in ['sourceHashes', 'inputHashes']:
        for relative, wanted in manifest[group].items():
            require(digest(ROOT/relative) == wanted, 'Final unchanged dependency '+relative)
    require([digest(directory/(name+'.json')) for name in ['manifest', 'results', 'index', 'completion']] ==
            [manifest_hash, results_hash, index_hash, completion_hash] and digest(Path(__file__)) == auditor_hash, 'Primary evidence/auditor unchanged throughout audit')
    return {'passed': True, 'completedAt': datetime.now(timezone.utc).isoformat(), 'seconds': time.perf_counter()-began,
            'studyManifestHash': manifest_hash, 'resultsSha256': results_hash, 'indexSha256': index_hash, 'completionSha256': completion_hash,
            'auditorSourceHash': auditor_hash, 'arithmeticBackendHash': None, 'runs': 192, 'checkpoints': 384,
            'legalQCells': counters['qCells'], 'jointGraphStates': counters['states'], 'cycles': counters['cycles'],
            'probeUpdateReplays': counters['probes'], 'sampledTrainingUpdates': counters['sampledUpdates'],
            'fullTrainingReplay': False, 'corruptionNegativeControls': controls, 'primaryContrasts': contrasts, 'details': details,
            'scope': 'Separate Python binary64/uint32/Fraction code; all saved Q argmaxes, legal policies/counts, joint functional graphs, exact saved-weight cycles/transients/windows, true terminal ceilings, short cloned updates and sampled updates checked. No primary learner/search imports. Complete training not independently replayed; common IEEE754 arithmetic/libm and deterministic pseudorandom simulation limitations remain. Marginal approximate bootstrap describes conditional whole-seed variation, not market uncertainty/equilibrium or formal verification.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--directory', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    receipt = audit(args.directory)
    if args.output:
        args.output.write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(receipt))
