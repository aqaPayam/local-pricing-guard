"""Independent finite frozen-opponent audit core.

Importing performs no evidence IO. Actual case auditing requires the separate
frozen-source/root authorization gate. No primary MDP, value-iteration, graph
or rational helpers are imported. The closed finite reward/mask game is reused
through its accepted immutable audit/hash binding; new Q, transitions, paths
and Bellman inequalities are recomputed here.
"""
from __future__ import annotations

import hashlib
import copy
import argparse
import json
import math
import struct
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable, Sequence

MAX_INTEGER_BITS = 1_000_000
V10_RECEIPT = "e2915ad87588a781abf3c925209b8bf450ba4fab13cc49dcffac4b9b1aa2979e"
V10_ARCHIVE = "5b494614af0efabe6a416814604a4914fb8e5492d6d78fb106d5a09b8497bdcf"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_digest(path: Path) -> str:
    value = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def safe_path(root: Path, relative: str) -> Path:
    require(isinstance(relative, str) and relative and "\\" not in relative
            and not Path(relative).is_absolute() and ":" not in relative,
            "Artifact reference must be portable and relative")
    resolved_root = Path(root).resolve()
    result = (resolved_root/relative).resolve()
    require(result.is_relative_to(resolved_root), "Artifact escapes declared root")
    return result


def read_reference(root: Path, reference: dict, declared_hashes: dict | None = None) -> bytes:
    require(isinstance(reference, dict) and isinstance(reference.get("sha256"), str)
            and type(reference.get("bytes")) is int and reference["bytes"] >= 0,
            "Malformed bound artifact reference")
    if declared_hashes is not None:
        require(declared_hashes.get(reference["file"]) == reference["sha256"],
                "Consumed input is absent from the frozen input map")
    data = safe_path(root, reference["file"]).read_bytes()
    require(len(data) == reference["bytes"] and digest(data) == reference["sha256"],
            "Artifact bytes/hash differ")
    return data


def json_value(data: bytes):
    def unique(items):
        result = {}
        for key, value in items:
            require(key not in result, "Duplicate JSON key")
            result[key] = value
        return result
    def invalid_constant(value):
        raise ValueError("Nonfinite JSON constant: "+value)
    return json.loads(data.decode("utf-8"), object_pairs_hook=unique,
                      parse_constant=invalid_constant)


def strict_equal(actual, expected, label: str) -> None:
    # In particular, Python's True==1 must not accept a fake numeric edge count.
    require(type(actual) is type(expected), "Scientific claim type differs: "+label)
    if isinstance(expected, dict):
        require(actual.keys() == expected.keys(), "Scientific keys differ: "+label)
        for key in expected:
            strict_equal(actual[key], expected[key], label+"."+key)
    elif isinstance(expected, (list, tuple)):
        require(len(actual) == len(expected), "Scientific array length differs: "+label)
        for index, (value, reference) in enumerate(zip(actual, expected)):
            strict_equal(value, reference, f"{label}[{index}]")
    else:
        require(actual == expected, "Scientific claim differs: "+label)


def exact_hex(value: Fraction) -> dict:
    value = Fraction(value)
    require(abs(value.numerator).bit_length() <= MAX_INTEGER_BITS
            and value.denominator.bit_length() <= MAX_INTEGER_BITS,
            "Exact scalar exceeds prospective integer bit budget")
    return {"numeratorHex": hex(value.numerator),
            "denominatorHex": hex(value.denominator)}


def parse_hex(value: dict) -> Fraction:
    require(isinstance(value, dict), "Exact scalar is not an object")
    a, b = value.get("numeratorHex"), value.get("denominatorHex")
    require(isinstance(a, str) and isinstance(b, str), "Missing hexadecimal scalar")
    require(len(a) <= (MAX_INTEGER_BITS+3)//4+3
            and len(b) <= (MAX_INTEGER_BITS+3)//4+3,
            "Encoded scalar exceeds prospective integer bit budget")
    try:
        numerator, denominator = int(a, 16), int(b, 16)
    except ValueError as error:
        raise ValueError("Malformed hexadecimal scalar") from error
    require(denominator > 0, "Nonpositive exact denominator")
    require(abs(numerator).bit_length() <= MAX_INTEGER_BITS
            and denominator.bit_length() <= MAX_INTEGER_BITS,
            "Exact scalar exceeds prospective integer bit budget")
    result = Fraction(numerator, denominator)
    require(exact_hex(result) == value, "Noncanonical hexadecimal rational")
    return result


def integer_rewards(values: Sequence[float]) -> tuple[int, tuple[int, ...]]:
    require(values and all(type(x) in (int, float) and math.isfinite(x)
                           for x in values), "Nonfinite/empty reward vector")
    ratios = [float(value).as_integer_ratio() for value in values]
    denominator = max(b for _, b in ratios)
    require(denominator & (denominator - 1) == 0, "Nondyadic binary64 reward")
    return denominator, tuple(a * (denominator // b) for a, b in ratios)


def quantize_binary64(value: float, denominator: int = 2**32) -> int:
    require(type(value) in (int, float) and math.isfinite(value),
            "Nonfinite proposal value")
    require(type(denominator) is int and denominator > 0
            and denominator & (denominator-1) == 0, "Invalid dyadic quantization")
    a, b = float(value).as_integer_ratio()
    quotient, remainder = divmod(abs(a)*denominator, b)
    if 2*remainder > b or (2*remainder == b and quotient % 2):
        quotient += 1
    return -quotient if a < 0 else quotient


def parse_candidate_vector(data: bytes, states: int) -> tuple[int, ...]:
    require(data.endswith(b"\n"), "Candidate vector lacks final newline")
    try:
        lines = data.decode("ascii").splitlines()
    except UnicodeDecodeError as error:
        raise ValueError("Candidate vector is not ASCII") from error
    require(len(lines) == states, "Candidate vector state count differs")
    values = []
    for line in lines:
        require(len(line) <= 4096//4+3, "Candidate numerator exceeds4096-bit budget")
        try:
            value = int(line, 16)
        except ValueError as error:
            raise ValueError("Malformed candidate numerator") from error
        require(line == hex(value) and abs(value).bit_length() <= 4096,
                "Noncanonical/oversized candidate numerator")
        values.append(value)
    return tuple(values)


def check_quantization(data: bytes, candidate: Sequence[int]) -> tuple[float, ...]:
    require(len(data) == len(candidate)*8, "Final binary64 proposal dimensions differ")
    values = tuple(item[0] for item in struct.iter_unpack("<d", data))
    require(tuple(quantize_binary64(value) for value in values) == tuple(candidate),
            "Candidate differs from exact ties-to-even final proposal quantization")
    return values


@dataclass(frozen=True)
class Layout:
    n: int
    phases: int
    cap_index: int
    sets: tuple[tuple[int, ...], ...]
    startup_only: bool

    def __post_init__(self):
        require(type(self.n) is int and 1 <= self.n <= 255, "Invalid quote count")
        require(type(self.phases) is int and self.phases >= 1, "Invalid phase count")
        require(not self.startup_only or self.phases == 2, "Startup must have two phases")
        require(type(self.cap_index) is int and 0 <= self.cap_index < self.n,
                "Invalid cap index")
        require(len(self.sets) == self.n, "Missing rival masks")
        for support in self.sets:
            require(support and all(type(a) is int and 0 <= a < self.n for a in support)
                    and tuple(sorted(set(support))) == tuple(support),
                    "Mask must be nonempty, sorted and unique")

    @property
    def states(self) -> int:
        return self.phases * self.n * self.n

    def decode(self, state: int) -> tuple[int, int, int]:
        require(type(state) is int and 0 <= state < self.states, "Invalid world state")
        phase, pair = divmod(state, self.n * self.n)
        return phase, pair // self.n, pair % self.n

    def support(self, phase: int, rival_previous: int) -> tuple[int, ...]:
        require(0 <= phase < self.phases and 0 <= rival_previous < self.n,
                "Invalid observation")
        return tuple(range(self.cap_index + 1)) if phase == 0 else self.sets[rival_previous]

    def next_phase(self, phase: int) -> int:
        return 1 if self.startup_only else (phase + 1) % self.phases

    def offsets(self) -> tuple[int, ...]:
        offsets = [0]
        for phase in range(self.phases):
            for own in range(self.n):
                for rival in range(self.n):
                    offsets.append(offsets[-1] + len(self.support(phase, rival)))
        return tuple(offsets)


def masked_greedy(layout: Layout, q: Sequence[float]) -> tuple[int, ...]:
    """Focal row=(phase,own previous,rival previous), ascending original action."""
    offsets = layout.offsets()
    require(len(q) == offsets[-1], "Compact Q dimensions differ")
    require(all(math.isfinite(x) for x in q), "Nonfinite saved Q")
    policy = []
    for row in range(layout.states):
        phase = row // (layout.n * layout.n)
        support = layout.support(phase, row % layout.n)
        start = offsets[row]
        # max key favors smallest ORIGINAL quote index, including exact ties.
        policy.append(max(support, key=lambda action:
                          (q[start + support.index(action)], -action)))
    return tuple(policy)


def validate_terminal(layout: Layout, step: int, phase: int,
                      previous: Sequence[int], cap_executions: int) -> int | None:
    """Independent NEXT-clock and last-completed cap-start envelope check."""
    require(type(step) is int and step >= 0, "Invalid completed training step")
    require(type(phase) is int and 0 <= phase < layout.phases,
            "Invalid saved next phase")
    require(len(previous) == 2 and all(type(a) is int and 0 <= a < layout.n for a in previous),
            "Invalid saved completed pair")
    require(type(cap_executions) is int and cap_executions >= 0,
            "Invalid original cap count")
    expected_phase = (0 if step == 0 else 1) if layout.startup_only else step % layout.phases
    expected_caps = (int(step > 0) if layout.startup_only else
                     (step+layout.phases-1)//layout.phases)
    require(phase == expected_phase and cap_executions == expected_caps,
            "Saved NEXT clock/cap count is inconsistent")
    if step == 0:
        require(list(previous) == [layout.n-1, layout.n-1], "Initial history differs")
        return None
    upper = tuple(s[-1] for s in layout.sets)
    require(all(a <= b for a, b in zip(upper, upper[1:]))
            and upper[layout.cap_index] >= layout.cap_index,
            "Accepted cap-start upper-envelope premises differ")
    # Stored phase is NEXT execution. Its completed prices came from exponent
    # (phase-1 mod K), not phase. Startup has already made step-1 guard moves.
    exponent = step-1 if layout.startup_only else (phase+layout.phases-1) % layout.phases
    bound = layout.cap_index
    for _ in range(exponent):
        next_bound = upper[bound]
        if next_bound == bound:
            break
        bound = next_bound
    require(all(a <= bound for a in previous),
            "Actual endpoint lies outside original cap-start invariant")
    return bound


def exact_counts(layout: Layout, saturated: Sequence[int], overflow: Sequence) -> tuple[int, ...]:
    require(len(saturated) == layout.offsets()[-1], "Count dimensions differ")
    require(all(type(c) is int and 0 <= c <= 65535 for c in saturated),
            "Invalid saturated count")
    result = list(saturated)
    previous = -1
    for item in overflow:
        require(isinstance(item, (tuple, list)) and len(item) == 2, "Invalid count overflow")
        cell, count = item
        require(type(cell) is int and type(count) is int and previous < cell < len(result)
                and result[cell] == 65535 and 65535 < count <= 2**53 - 1,
                "Invalid/duplicate overflow count")
        result[cell] = count
        previous = cell
    return tuple(result)


def load_checkpoint_inputs(project: Path, supplied: dict, expected: dict,
                           declared_hashes: dict, adaptive_index: dict) -> dict:
    """No numerical primary imports; no I/O occurs until this is explicitly called."""
    require(supplied.get("inputRoot") == "project", "Wrong input reference root")
    old_id = (f"base-g15-t1--{expected['control']}--zero--s{expected['seed']}")
    require(supplied.get("oldRunID") == old_id and supplied.get("checkpointStep") == 2_000_000,
            "Wrong inherited run/checkpoint selection")
    old = json_value(read_reference(project, supplied["oldRecord"], declared_hashes))
    require(old.get("id") == old_id and old.get("scenario") == "base-g15-t1"
            and old.get("initialization") == "zero" and old.get("seed") == expected["seed"]
            and old.get("status") == "completed frozen-policy evaluation"
            and old.get("actualMainRounds") == 2_000_000,
            "Inherited run identity/completion differs")
    entries = [entry for entry in adaptive_index["records"] if entry["id"] == old_id]
    require(len(entries) == 1, "Inherited indexed run missing/duplicated")
    indexed = entries[0]
    require("research/adaptive-learning-results/"+indexed["file"] == supplied["oldRecord"]["file"]
            and indexed["sha256"] == supplied["oldRecord"]["sha256"],
            "Inherited run is not the accepted indexed record")
    selected = [entry for entry in old["checkpoints"] if entry["step"] == 2_000_000]
    indexed_cp = [entry for entry in indexed["checkpoints"] if entry["step"] == 2_000_000]
    require(len(selected) == len(indexed_cp) == 1, "Final checkpoint missing/duplicated")
    checkpoint, index_checkpoint = selected[0], indexed_cp[0]
    declared = supplied["checkpointEntry"]
    for key in ("step", "file", "sha256"):
        strict_equal(declared.get(key), checkpoint.get(key), "original checkpoint "+key)
        strict_equal(index_checkpoint.get(key), checkpoint.get(key), "indexed checkpoint "+key)
    strict_equal(declared.get("terminal"), checkpoint.get("terminal"), "original terminal")
    require(supplied["metadata"]["file"] == "research/adaptive-learning-results/"+checkpoint["file"]
            and supplied["metadata"]["sha256"] == checkpoint["sha256"],
            "Selected metadata binding differs")
    meta = json_value(read_reference(project, supplied["metadata"], declared_hashes))
    finite_raw = json_value(read_reference(project, supplied["finiteGame"], declared_hashes))
    require(finite_raw["scenario"]["id"] == "base-g15-t1"
            and old["rawFile"] == supplied["finiteGame"]["file"]
            and old["rawSha256"] == supplied["finiteGame"]["sha256"],
            "Original finite-game binding differs")
    finite = finite_raw["finite"]
    prices, n = finite["prices"], len(finite["prices"])
    require(1 <= n <= 62 and all(type(p) in (int, float) and math.isfinite(p) for p in prices)
            and all(a < b for a, b in zip(prices, prices[1:])), "Invalid original price set")
    control = ({"id": "startup-only", "period": None, "phases": 2}
               if expected["control"] == "startup-only" else
               {"id": "selected95", "period": 4, "phases": 4})
    strict_equal(meta["control"], control, "saved actual controller")
    strict_equal(old["control"], control, "run actual controller")
    require(meta["step"] == meta["T"] == 2_000_000 and meta["seed"] == expected["seed"]
            and meta["initialization"] == "zero" and meta["alpha"] == 0.1
            and meta["gamma"] == 19/20, "Original training metadata differs")
    layout = Layout(n, control["phases"], finite["capIndex"],
                    tuple(tuple(mask) for mask in finite["sets"]), control["id"] == "startup-only")
    require(layout.states <= 15_376, "Full state bound exceeded")
    offsets = layout.offsets()
    offset_bytes = b"".join(struct.pack("<I", value) for value in offsets)
    require(meta["layout"]["n"] == n and meta["layout"]["rows"] == layout.states
            and meta["layout"]["cells"] == offsets[-1]
            and meta["layout"]["offsetsSha256"] == digest(offset_bytes),
            "Original compact layout differs")
    validate_terminal(layout, meta["step"], meta["phase"], meta["previousIndices"], meta["capExecutions"])
    strict_equal(declared["terminal"], {"phase": meta["phase"],
                                        "previousIndices": meta["previousIndices"]},
                 "actual next-clock terminal")
    policies, counts = [], []
    require(all(isinstance(supplied.get(kind), list) and len(supplied[kind]) == 2
                for kind in ("q", "counts", "savedPolicies"))
            and isinstance(meta.get("countOverflow"), list) and len(meta["countOverflow"]) == 2,
            "Missing two-firm checkpoint inputs")
    for firm in range(2):
        for kind, meta_key in (("q", "q"), ("counts", "counts"), ("savedPolicies", "policies")):
            source_ref, inherited_ref = supplied[kind][firm], meta["files"][meta_key][firm]
            strict_equal(source_ref, {**inherited_ref, "file": "research/adaptive-learning-results/"+
                                      inherited_ref["file"]}, "original "+kind+" ref")
        q_bytes = read_reference(project, supplied["q"][firm], declared_hashes)
        count_bytes = read_reference(project, supplied["counts"][firm], declared_hashes)
        require(len(q_bytes) == offsets[-1]*8 and len(count_bytes) == offsets[-1]*2,
                "Original compact binary dimensions differ")
        q_values = tuple(value[0] for value in struct.iter_unpack("<d", q_bytes))
        policy = masked_greedy(layout, q_values)
        saturated = tuple(value[0] for value in struct.iter_unpack("<H", count_bytes))
        exact = exact_counts(layout, saturated, meta["countOverflow"][firm])
        require(sum(exact) == 2_000_000, "Original exact action-count total differs")
        saved = read_reference(project, supplied["savedPolicies"][firm], declared_hashes)
        require(saved == bytes(policy), "Saved policy differs from complete Q argmax reconstruction")
        policies.append(policy); counts.append(exact)
    for name in ("profitA", "profitB", "consumerSurplus"):
        require(len(finite["rewards"][name]) == n*n
                and all(type(value) in (int, float) and math.isfinite(value)
                        for value in finite["rewards"][name]),
                "Accepted numerical reward dimensions differ")
    initial = meta["phase"]*n*n+meta["previousIndices"][0]*n+meta["previousIndices"][1]
    return {"layout": layout, "finite": finite, "policies": tuple(policies),
            "counts": tuple(counts), "initial": initial, "metadata": meta}


@dataclass(frozen=True)
class FrozenMDP:
    layout: Layout
    focal: int
    policies: tuple[tuple[int, ...], tuple[int, ...]]
    rewards: tuple[int, ...]  # focal reward, WORLD executed-pair order A*n+B
    denominator: int
    counts: tuple[tuple[int, ...], tuple[int, ...]] | None = None

    def __post_init__(self):
        require(self.focal in (0, 1), "Invalid focal seller")
        require(len(self.rewards) == self.layout.n**2
                and all(type(r) is int for r in self.rewards), "Invalid reward weights")
        require(type(self.denominator) is int and self.denominator > 0,
                "Invalid reward denominator")
        require(len(self.policies) == 2, "Missing seller policies")
        for policy in self.policies:
            require(len(policy) == self.layout.states, "Policy state dimensions differ")
            for row, action in enumerate(policy):
                phase = row // self.layout.n**2
                require(type(action) is int and action in
                        self.layout.support(phase, row % self.layout.n),
                        "Illegal baseline/opponent focal-row policy")
        if self.counts is not None:
            cells = self.layout.offsets()[-1]
            require(len(self.counts) == 2 and all(len(c) == cells for c in self.counts)
                    and all(type(v) is int and v >= 0 for c in self.counts for v in c),
                    "Invalid exact count arrays")

    def rows(self, state: int) -> tuple[int, int]:
        phase, a, b = self.layout.decode(state)
        base = phase * self.layout.n**2
        return base + a*self.layout.n + b, base + b*self.layout.n + a

    def actions(self, state: int) -> tuple[int, ...]:
        phase, a, b = self.layout.decode(state)
        return self.layout.support(phase, b if self.focal == 0 else a)

    def baseline(self) -> tuple[int, ...]:
        return tuple(self.policies[self.focal][self.rows(s)[self.focal]]
                     for s in range(self.layout.states))

    def edge(self, state: int, action: int) -> tuple[int, int, int, tuple[int, int]]:
        phase, _, _ = self.layout.decode(state)
        require(type(action) is int and action in self.actions(state),
                "Illegal proposed focal action")
        other = 1-self.focal
        opponent = self.policies[other][self.rows(state)[other]]
        a, b = (action, opponent) if self.focal == 0 else (opponent, action)
        pair = a*self.layout.n+b
        next_state = self.layout.next_phase(phase)*self.layout.n**2+pair
        return next_state, self.rewards[pair], opponent, (a, b)


def validate_policy(mdp: FrozenMDP, policy: Sequence[int]) -> None:
    require(len(policy) == mdp.layout.states, "Response state dimensions differ")
    for state, action in enumerate(policy):
        require(type(action) is int and action in mdp.actions(state),
                "Illegal response action at a possibly off-path state")


def weighted_numerator(rewards: Sequence[int], p: int, q: int) -> tuple[int, int]:
    """Return sum r_t*(p/q)^t as numerator over q^(len-1), before reward L."""
    if not rewards:
        return 0, 1
    value, qpower = rewards[-1], q
    for reward in reversed(rewards[:-1]):
        value = p*value + reward*qpower
        qpower *= q
    return value, qpower//q


def discounted_path_value(rewards: Sequence[int], transient: int, cycle: int,
                          denominator: int, p: int = 19, q: int = 20) -> Fraction:
    require(type(transient) is int and transient >= 0 and type(cycle) is int
            and cycle >= 1 and len(rewards) == transient+cycle,
            "Invalid full transient/cycle inventory")
    require(type(p) is int and type(q) is int and 0 <= p < q,
            "Invalid rational discount")
    require(type(denominator) is int and denominator > 0
            and all(type(r) is int for r in rewards), "Invalid exact path rewards")
    # Conservative pre-operation bound; covers the cross-multiplied prefix and
    # cycle expression before Fraction cancellation, not only final output.
    bound = (denominator.bit_length()+max((abs(r).bit_length() for r in rewards), default=0)
             + (transient+cycle+2)*q.bit_length()+len(rewards).bit_length()+8)
    require(bound <= MAX_INTEGER_BITS, "Path exceeds prospective integer bit budget")
    pre, pre_denominator = weighted_numerator(rewards[:transient], p, q)
    cyc, _ = weighted_numerator(rewards[transient:], p, q)
    return (Fraction(pre, denominator*pre_denominator)
            + Fraction(p**transient*q*cyc,
                       denominator*q**transient*(q**cycle-p**cycle)))


def normalized_discounted_exposure(flags: Sequence[int], transient: int, cycle: int,
                                  p: int = 19, q: int = 20) -> Fraction:
    require(all(type(flag) is int and flag in (0, 1) for flag in flags),
            "Coverage flag is not a binary indicator")
    value = Fraction(q-p, q)*discounted_path_value(flags, transient, cycle, 1, p, q)
    require(0 <= value <= 1, "Normalized discounted exposure outside [0,1]")
    return value


def cycle_pair_reward_mean(trace: dict, pair_rewards: Sequence[float], n: int) -> Fraction:
    """Secondary eventual-cycle mean; never a private-profit/PV objective."""
    require(type(n) is int and n > 0 and len(pair_rewards) == n*n,
            "Secondary pair-reward table dimensions differ")
    h, c = trace["transientLength"], trace["cycleLength"]
    pairs = trace["executedPairs"]
    require(type(h) is int and h >= 0 and type(c) is int and c > 0
            and len(pairs) == h+c, "Secondary full path inventory differs")
    denominator, weights = integer_rewards(pair_rewards)
    total = 0
    for pair in pairs[h:]:
        require(len(pair) == 2 and all(type(a) is int and 0 <= a < n for a in pair),
                "Invalid secondary cycle pair")
        total += weights[pair[0]*n+pair[1]]
    return Fraction(total, denominator*c)


def trajectory(mdp: FrozenMDP, policy: Sequence[int], initial: int,
               p: int = 19, q: int = 20) -> dict:
    validate_policy(mdp, policy)
    mdp.layout.decode(initial)
    seen, states, actions, other_actions, pairs, rewards, next_states = {}, [], [], [], [], [], []
    state = initial
    while state not in seen:
        require(len(states) < mdp.layout.states, "Exceeded full state path bound")
        seen[state] = len(states)
        action = policy[state]
        next_state, reward, other, pair = mdp.edge(state, action)
        states.append(state); actions.append(action); other_actions.append(other)
        pairs.append(pair); rewards.append(reward)
        next_states.append(next_state)
        state = next_state
    h, c = seen[state], len(states)-seen[state]
    result = {"states": states, "actions": actions, "opponentActions": other_actions,
              "nextStates": next_states,
              "executedPairs": [list(pair) for pair in pairs],
              "transientLength": h, "cycleLength": c, "cycleEntryState": state,
              "value": exact_hex(discounted_path_value(rewards, h, c,
                                                       mdp.denominator, p, q))}
    if mdp.counts is not None:
        offsets = mdp.layout.offsets()
        for firm in range(2):
            state_flags, action_flags = [], []
            state_visits, action_visits = [], []
            for s, pair in zip(states, pairs):
                row = mdp.rows(s)[firm]
                phase = s // mdp.layout.n**2
                rival = row % mdp.layout.n
                support = mdp.layout.support(phase, rival)
                first, last = offsets[row], offsets[row+1]
                state_visits.append(sum(mdp.counts[firm][first:last]))
                action_visits.append(mdp.counts[firm][first+support.index(pair[firm])])
                state_flags.append(int(state_visits[-1] == 0))
                action_flags.append(int(action_visits[-1] == 0))
            result.setdefault("coverage", []).append({
                "firm": firm, "unvisitedStateOccurrences": sum(state_flags),
                "neverTriedActionOccurrences": sum(action_flags),
                "uniqueTrajectoryStates": len(states),
                "stateVisits": state_visits, "chosenActionVisits": action_visits,
                "normalizedDiscountedUnvisitedExposure": exact_hex(
                    normalized_discounted_exposure(state_flags, h, c, p, q)),
                "normalizedDiscountedNeverTriedExposure": exact_hex(
                    normalized_discounted_exposure(action_flags, h, c, p, q)),
                "scope": "counts: full transient plus one cycle; exposure: normalized infinite discount"})
    return result


def bellman_certificate(mdp: FrozenMDP, candidate: Sequence[int],
                        candidate_denominator: int = 2**32,
                        p: int = 19, q: int = 20) -> dict:
    require(len(candidate) == mdp.layout.states and all(type(z) is int for z in candidate),
            "Invalid quantized value vector")
    require(type(candidate_denominator) is int and candidate_denominator > 0
            and candidate_denominator & (candidate_denominator-1) == 0,
            "Candidate denominator must be a positive power of two")
    require(type(p) is int and type(q) is int and 0 <= p < q, "Invalid discount")
    common = math.lcm(mdp.denominator, candidate_denominator)
    require(common.bit_length()+max((abs(z).bit_length() for z in candidate), default=0)
            +q.bit_length()+8 <= MAX_INTEGER_BITS,
            "Bellman vector exceeds prospective integer bit budget")
    z = tuple(value*(common//candidate_denominator) for value in candidate)
    reward_factor = common//mdp.denominator
    maximum, witness, policy, edges = None, None, [], 0
    residual_hash = hashlib.sha256()
    for state in range(mdp.layout.states):
        best_score, winner = None, None
        for action in mdp.actions(state):
            next_state, reward, _, _ = mdp.edge(state, action)
            score = q*reward*reward_factor+p*z[next_state]
            residual = score-q*z[state]
            residual_hash.update((hex(residual)+"\n").encode("ascii"))
            if maximum is None or residual > maximum:
                maximum, witness = residual, [state, action, next_state]
            if best_score is None or score > best_score:
                best_score, winner = score, action
            edges += 1
        policy.append(winner)
    return {"commonDenominatorHex": hex(common), "maxResidualNumeratorHex": hex(maximum),
            "maxResidualWitness": witness, "legalEdges": edges,
            "residualSha256": residual_hash.hexdigest(), "greedyPolicy": policy,
            "upperNumerators": [(q-p)*value+maximum for value in z],
            "upperDenominator": (q-p)*common,
            "oneSidedResidualMayBeNegative": True}


def certify(mdp: FrozenMDP, candidate: Sequence[int], response: Sequence[int], initial: int,
            candidate_denominator: int = 2**32, p: int = 19, q: int = 20) -> dict:
    certificate = bellman_certificate(mdp, candidate, candidate_denominator, p, q)
    require(list(response) == certificate["greedyPolicy"],
            "Response is not the exact all-action greedy proposal")
    baseline = trajectory(mdp, mdp.baseline(), initial, p, q)
    proposed = trajectory(mdp, response, initial, p, q)
    value_baseline, value_response = parse_hex(baseline["value"]), parse_hex(proposed["value"])
    upper = Fraction(certificate["upperNumerators"][initial],
                     certificate["upperDenominator"])
    gap = upper-value_response
    require(gap >= 0, "Negative exact optimality-gap certificate")
    require(upper >= value_baseline, "Upper certificate excludes the legal baseline")
    return {"baseline": baseline, "response": proposed,
            "achievedGain": exact_hex(value_response-value_baseline),
            "optimalityGapUpper": exact_hex(gap),
            "bestGainLower": exact_hex(max(Fraction(0), value_response-value_baseline)),
            "possibleBestGainUpper": exact_hex(upper-value_baseline),
            "upperValue": exact_hex(upper),
            "relativeAchievedGain": exact_hex((value_response-value_baseline)/value_baseline)
                if value_baseline > 0 else None,
            "relativeGainNullReason": None if value_baseline > 0 else "nonpositive baseline",
            "gapTargetMet": gap <= Fraction(1, 1_000_000),
            "certificate": {key: value for key, value in certificate.items()
                            if key not in ("upperNumerators", "upperDenominator", "greedyPolicy")}}


def primary_path_shape(trace: dict, n: int) -> dict:
    pairs = trace["executedPairs"]
    return {"states": trace["states"],
            "executedA": [pair[0] for pair in pairs],
            "executedB": [pair[1] for pair in pairs],
            "nextStates": trace["nextStates"],
            "payoffIndices": [pair[0]*n+pair[1] for pair in pairs],
            "h": trace["transientLength"], "c": trace["cycleLength"],
            "closingState": trace["cycleEntryState"],
            "coverage": {name: {"stateVisits": trace["coverage"][firm]["stateVisits"],
                                "chosenActionVisits": trace["coverage"][firm]["chosenActionVisits"]}
                         for firm, name in enumerate(("A", "B"))}}


def primary_coverage_shape(trace: dict) -> dict:
    result = {}
    for firm, name in enumerate(("A", "B")):
        row = trace["coverage"][firm]
        result[name] = {
            "unweighted": {"states": row["uniqueTrajectoryStates"],
                           "unvisitedStates": row["unvisitedStateOccurrences"],
                           "neverTriedChosenActions": row["neverTriedActionOccurrences"],
                           "minimumStateVisits": min(row["stateVisits"]),
                           "minimumChosenActionVisits": min(row["chosenActionVisits"])},
            "discounted": {"unvisitedStateExposure": row["normalizedDiscountedUnvisitedExposure"],
                           "neverTriedChosenActionExposure": row["normalizedDiscountedNeverTriedExposure"]}}
    return result


def audit_scientific_record(record: dict, loaded: dict, output_root: Path,
                            artifact_reader=None) -> dict:
    """Recheck complete scientific artifacts; execution success is orthogonal."""
    require(record.get("scientificAvailable") is True,
            "Scientific comparator requires an explicitly available complete record")
    read = read_reference if artifact_reader is None else artifact_reader
    focal = {"A": 0, "B": 1}.get(record.get("focal"))
    require(focal is not None, "Invalid proposed focal seller")
    finite, layout = loaded["finite"], loaded["layout"]
    denominator, rewards = integer_rewards(finite["rewards"]["profitA" if focal == 0 else "profitB"])
    mdp = FrozenMDP(layout, focal, loaded["policies"], rewards, denominator, loaded["counts"])
    optimizer = record["optimizer"]
    require(optimizer.get("optimizerIterationsReplayed") is False,
            "False optimizer-replay scope")
    require(type(optimizer.get("completedSweeps")) is int
            and 1 <= optimizer["completedSweeps"] <= 600, "Invalid completed sweep count")
    require(type(optimizer.get("floatDifference")) in (int, float)
            and math.isfinite(optimizer["floatDifference"]) and optimizer["floatDifference"] >= 0,
            "Invalid floating proposal diagnostic")
    strict_equal(optimizer.get("hardBudgetSeconds"), 300, "hard-budget identity")
    strict_equal(optimizer.get("maximumSweeps"), 600, "maximum proposal sweeps")
    strict_equal(optimizer.get("floatStoppingThreshold"), 1e-10, "floating stopping threshold")
    strict_equal(optimizer.get("quantization"),
                 {"denominatorPower": 32, "ties": "nearest-even exact binary64 rational"},
                 "dyadic proposal convention")
    if optimizer.get("stopReason") == "completed floating difference threshold":
        require(optimizer["floatDifference"] <= 1e-10, "False floating stopping threshold")
    else:
        require(optimizer.get("stopReason") == "maximum completed sweeps"
                and optimizer["completedSweeps"] == 600 and optimizer["floatDifference"] > 1e-10,
                "Inconsistent proposal stopping diagnostic")
    candidate = parse_candidate_vector(read(output_root, optimizer["dyadicValues"]),
                                      layout.states)
    check_quantization(read(output_root, optimizer["finalFloat64"]), candidate)
    policy = tuple(read(output_root, optimizer["responsePolicy"]))
    result = certify(mdp, candidate, policy, loaded["initial"])
    initial_phase, previous_a, previous_b = layout.decode(loaded["initial"])
    world_opponent = bytes(loaded["policies"][1-focal][mdp.rows(state)[1-focal]]
                           for state in range(layout.states))
    expected_mdp = {"n": layout.n, "states": layout.states,
                    "edges": result["certificate"]["legalEdges"],
                    "terminal": {"node": loaded["initial"], "phase": initial_phase,
                                 "previousIndices": [previous_a, previous_b]},
                    "coordinateOrder": "World (phase,previousA,previousB), row-major; B Q lookup alone transposes",
                    "focalRewardOrientation": "Original "+("profitA" if focal == 0 else "profitB")+
                                               "[executedA*n+executedB]",
                    "opponentWorldPolicySha256": digest(world_opponent),
                    "baselineWorldPolicySha256": digest(bytes(mdp.baseline()))}
    strict_equal(record["mdp"], expected_mdp, "full MDP metadata")
    means = {}
    for name in ("baseline", "response"):
        claimed, trace = record[name], result[name]
        strict_equal(json_value(read(output_root, claimed["path"])),
                     primary_path_shape(trace, layout.n), name+" full path")
        for key, expected in {"h": trace["transientLength"], "c": trace["cycleLength"],
                              "value": trace["value"], "coverage": primary_coverage_shape(trace)}.items():
            strict_equal(claimed.get(key), expected, name+" "+key)
        means[name] = cycle_pair_reward_mean(trace, finite["rewards"]["consumerSurplus"], layout.n)
        strict_equal(claimed.get("eventualCycleCustomerBenefit"), exact_hex(means[name]),
                     name+" secondary cycle customer benefit")
    witness = result["certificate"]["maxResidualWitness"]
    pair = mdp.edge(witness[0], witness[1])[3]
    expected_certificate = {
        "passed": True,
        "commonDenominatorHex": result["certificate"]["commonDenominatorHex"],
        "maximumResidualNumeratorHex": result["certificate"]["maxResidualNumeratorHex"],
        "maximumWitness": {"sourceState": witness[0], "action": witness[1],
                           "nextState": witness[2], "payoffIndex": pair[0]*layout.n+pair[1]},
        "allEdgesChecked": result["certificate"]["legalEdges"],
        "upperValue": result["upperValue"],
        "responseOptimalityGap": result["optimalityGapUpper"],
        "requestedGap": exact_hex(Fraction(1, 1_000_000)),
        "withinRequestedGap": result["gapTargetMet"]}
    strict_equal(record.get("certificate"), expected_certificate, "all-edge certificate")
    gain = parse_hex(result["achievedGain"])
    expected_performance = {
        "rawGain": result["achievedGain"],
        "rawGainSign": "positive" if gain > 0 else "negative" if gain < 0 else "zero",
        "possibleGain": {"lower": result["bestGainLower"], "upper": result["possibleBestGainUpper"]},
        "relativeGain": result["relativeAchievedGain"],
        "relativeGainReason": None if result["relativeAchievedGain"] is not None else
                              "Exact baseline is zero or negative",
        "cycleCustomerBenefitDifference": exact_hex(means["response"]-means["baseline"])}
    strict_equal(record.get("performance"), expected_performance, "achieved versus possible gain")
    return {"id": record["id"], "scientificAvailable": True,
            "withinRequestedGap": result["gapTargetMet"],
            "baselineValue": result["baseline"]["value"],
            "responseValue": result["response"]["value"],
            "performance": expected_performance, "legalEdges": result["certificate"]["legalEdges"]}


def planned_cases() -> list[dict]:
    rows = []
    for seed in range(907001, 907013):
        for controller in ("startup-only", "selected95"):
            old_id = f"base-g15-t1--{controller}--zero--s{seed}"
            control = ({"id": controller, "period": None, "phases": 2}
                       if controller == "startup-only" else
                       {"id": controller, "period": 4, "phases": 4})
            for focal in ("A", "B"):
                rows.append({"id": old_id+"--focal"+focal, "oldRunID": old_id,
                             "scenario": "base-g15-t1", "seed": seed,
                             "initialization": "zero", "control": control.copy(),
                             "focal": focal, "checkpointStep": 2_000_000})
    return rows


def independent_summaries(records: Sequence[dict]) -> dict:
    require(len(records) == 48, "All48 rows required for descriptive summaries")
    for row, planned in zip(records, planned_cases()):
        for key in ("id", "seed", "control", "focal"):
            strict_equal(row[key], planned[key], "summary identity "+key)
        require(type(row.get("scientificAvailable")) is bool
                and type(row.get("executionSucceeded")) is bool, "Missing orthogonal status flags")
    controllers, seed_means = [], []
    for controller in ("startup-only", "selected95"):
        rows = [row for row in records if row["control"]["id"] == controller]
        available = [row for row in rows if row["scientificAvailable"]]
        gains = sorted(parse_hex(row["performance"]["rawGain"]) for row in available)
        counts = {"positive": sum(value > 0 for value in gains),
                  "zero": sum(value == 0 for value in gains),
                  "negative": sum(value < 0 for value in gains)}
        status_groups = {}
        for row in rows:
            group = status_groups.setdefault(row["status"], {
                "labels": 0, "executionSucceeded": 0, "scientificallyAvailable": 0,
                "rawGainSignCounts": {"positive": 0, "zero": 0, "negative": 0}})
            group["labels"] += 1
            group["executionSucceeded"] += int(row["executionSucceeded"])
            if row["scientificAvailable"]:
                group["scientificallyAvailable"] += 1
                gain = parse_hex(row["performance"]["rawGain"])
                group["rawGainSignCounts"]["positive" if gain > 0 else "negative" if gain < 0 else "zero"] += 1
        median = (gains[len(gains)//2] if len(gains) % 2 else
                  (gains[len(gains)//2-1]+gains[len(gains)//2])/2) if gains else None
        controllers.append({"controller": controller, "plannedSellerLabels": 24,
                            "executionSucceeded": sum(row["executionSucceeded"] for row in rows),
                            "available": len(gains), "unavailable": 24-len(gains),
                            "statusGroups": status_groups, "rawGainSignCounts": counts,
                            "minimum": exact_hex(gains[0]) if gains else None,
                            "median": exact_hex(median) if gains else None,
                            "maximum": exact_hex(gains[-1]) if gains else None,
                            "recordIds": [row["id"] for row in rows]})
        for seed in range(907001, 907013):
            pair = [row for row in rows if row["seed"] == seed]
            ok = all(row["scientificAvailable"] for row in pair)
            mean = sum((parse_hex(row["performance"]["rawGain"]) for row in pair), Fraction(0))/2 if ok else None
            seed_means.append({"seed": seed, "controller": controller,
                               "recordIds": [row["id"] for row in pair],
                               "status": "available" if ok else "unavailable",
                               "meanRawGain": exact_hex(mean) if ok else None,
                               "reason": None if ok else
                               "One or both seller responses unavailable; no zero imputation"})
    differences = []
    for seed in range(907001, 907013):
        a = next(row for row in seed_means if row["seed"] == seed and row["controller"] == "startup-only")
        b = next(row for row in seed_means if row["seed"] == seed and row["controller"] == "selected95")
        ok = a["status"] == b["status"] == "available"
        differences.append({"seed": seed, "comparison": "selected95 minus startup-only",
                            "recordIds": a["recordIds"]+b["recordIds"],
                            "status": "available" if ok else "unavailable",
                            "difference": exact_hex(parse_hex(b["meanRawGain"])-parse_hex(a["meanRawGain"])) if ok else None,
                            "reason": None if ok else
                            "At least one controller seed mean unavailable; paired unit retained"})
    return {"controllerSummaries": controllers, "seedMeans": seed_means,
            "pairedDifferences": differences}


def inherited_manifest_dependencies(parent: dict) -> dict:
    """Recognize declared legacy hashes without accepting arbitrary mapless leaves."""
    require(isinstance(parent, dict), "Inherited manifest is not an object")
    groups = [key for key in ("sourceHashes", "inputHashes", "hashes", "sources") if key in parent]
    require(groups, "Inherited manifest has no recognized scientific dependency map")
    merged = {}
    for key in groups:
        require(isinstance(parent[key], dict), "Inherited dependency map is malformed")
        for child, expected in parent[key].items():
            require(isinstance(child, str) and isinstance(expected, str)
                    and re.fullmatch("[0-9a-f]{64}", expected),
                    "Inherited dependency declaration is malformed")
            require(child not in merged or merged[child] == expected,
                    "Conflicting inherited dependency digests")
            merged[child] = expected
    return merged


def verify_study_dependencies(project: Path, directory: Path) -> dict:
    """Read-only metadata/hash closure; safe for the pre-case administrative gate."""
    manifest_path = safe_path(directory, "manifest.json")
    manifest = json_value(manifest_path.read_bytes())
    for group in ("sourceHashes", "inputHashes"):
        require(isinstance(manifest.get(group), dict) and manifest[group],
                "Missing frozen dependency map: "+group)
        for name, expected in manifest[group].items():
            require(isinstance(expected, str) and re.fullmatch("[0-9a-f]{64}", expected),
                    "Malformed frozen dependency digest")
            require(file_digest(safe_path(project, name)) == expected,
                    "Frozen dependency differs: "+name)
            if group == "sourceHashes":
                require(file_digest(safe_path(directory, "sources/"+name)) == expected,
                        "Frozen source snapshot differs: "+name)
    for required in ("research/audit-learned-opponent.py",
                     "tests/test_learned_opponent_audit.py",
                     "tests/test_learned_opponent_cross_audit.py",
                     "tests/test_learned_opponent_inventory_audit.py",
                     "tests/test_learned_opponent_supervisor.py",
                     "research/run-learned-opponent.py", "research/learned-opponent-case.js",
                     "research/learned-opponent-study.js", "research/LEARNED_OPPONENT_PROTOCOL.md",
                     "research/LEARNED_OPPONENT_THEORY.md",
                     "research/LEARNED_OPPONENT_PROSPECTIVE_REVIEW.md"):
        require(required in manifest["sourceHashes"], "Required source was not frozen: "+required)
    require(manifest["sourceHashes"]["research/audit-learned-opponent.py"] == file_digest(Path(__file__)),
            "Running authoritative auditor is not the frozen auditor source")
    plan = manifest["plan"]
    strict_equal(plan["cases"], planned_cases(), "fixed48-case matrix")
    settings = {"retainedRecords": 48, "discount": {"numerator": 19, "denominator": 20},
                "maximumSweeps": 600, "floatStoppingThreshold": 1e-10,
                "requestedAbsoluteGap": exact_hex(Fraction(1, 1_000_000)),
                "dyadicDenominatorPower": 32, "hardCaseSeconds": 300,
                "maximumStates": 15_376, "maximumScalarBits": 1_000_000,
                "maximumCandidateNumeratorBits": 4096,
                "fullTrainingReplay": False, "optimizerIterationsReplayed": False}
    for key, expected in settings.items():
        strict_equal(plan.get(key), expected, "prospective setting "+key)
    strict_equal(plan.get("softResourceTargets"),
                 {"seconds": 7200, "sampledProcessRSSBytes": 512_000_000,
                  "newOutputBytes": 250_000_000}, "prospective soft budgets")
    old_ids = {row["oldRunID"] for row in planned_cases()}
    require(set(manifest["inputs"]) == old_ids, "All24 inherited checkpoint inputs required")
    inputs = manifest["inputHashes"]
    def old_json(name):
        path = safe_path(project, name)
        require(name in inputs and file_digest(path) == inputs[name],
                "Reused premise file not hash-bound: "+name)
        return json_value(path.read_bytes())
    visited = set()
    def closure(name):
        if name in visited:
            return
        visited.add(name)
        parent = old_json(name)
        for child, expected in inherited_manifest_dependencies(parent).items():
            require(inputs.get(child) == expected, "Inherited dependency closure differs: "+child)
            if child.endswith("/manifest.json"):
                closure(child)
    prefix = "research/adaptive-learning-results/"
    closure(prefix+"manifest.json")
    audit = old_json(prefix+"independent-audit.json")
    index, results, completion = (old_json(prefix+name) for name in
                                  ("index.json", "results.json", "completion.json"))
    require(audit.get("passed") is True and audit.get("fullTrainingReplay") is False,
            "Accepted old learner audit missing/scope differs")
    for field, file in (("studyManifestHash", "manifest.json"), ("resultsSha256", "results.json"),
                        ("indexSha256", "index.json"), ("completionSha256", "completion.json")):
        require(audit.get(field) == inputs[prefix+file], "Accepted learner audit binding differs")
    require(audit.get("auditorSourceHash") == inputs.get("research/audit-adaptive-learning.py"),
            "Reused learner auditor source differs")
    require(completion.get("passed") is True
            and completion.get("finalFrozenDependencyCheck", {}).get("passed") is True
            and completion.get("runs") == 192 and completion.get("checkpoints") == 384
            and completion.get("unresolvedRuns") == 0
            and len(index["records"]) == len(results["records"]) == 192,
            "Accepted learner completion/inventory differs")
    require(completion.get("manifestSha256") == inputs[prefix+"manifest.json"]
            and completion.get("resultsSha256") == inputs[prefix+"results.json"]
            and completion.get("indexSha256") == inputs[prefix+"index.json"],
            "Accepted learner completion hash links differ")
    for aggregate in (index, results):
        require(aggregate.get("manifestSha256") == inputs[prefix+"manifest.json"],
                "Reused learner aggregate manifest differs")
    for old_id, supplied in manifest["inputs"].items():
        original = json_value(read_reference(project, supplied["oldRecord"], inputs))
        matches = [row for row in results["records"] if row["id"] == old_id]
        require(len(matches) == 1, "Reused learner aggregate row missing/duplicate")
        strict_equal(matches[0], original, "accepted original indexed/aggregate record")
    delivery = manifest["v10Delivery"]
    require(delivery.get("receipt") == "output/mixed-timing-package-verification.json"
            and delivery.get("receiptSha256") == V10_RECEIPT
            and delivery.get("archive") == "output/price-guard-mixed-timing-v10.zip"
            and delivery.get("archiveSha256") == V10_ARCHIVE
            and delivery.get("archiveBytes") == 123_232_702,
            "Accepted prior delivery identity differs")
    receipt = old_json(delivery["receipt"])
    require(inputs[delivery["receipt"]] == V10_RECEIPT
            and receipt.get("verification", {}).get("passed") is True
            and receipt.get("verification", {}).get("payloadHashesAndCRC") is True
            and receipt.get("sha256") == V10_ARCHIVE and receipt.get("bytes") == 123_232_702,
            "Accepted prior delivery receipt differs")
    archive = safe_path(project, delivery["archive"])
    if archive.exists():
        require(file_digest(archive) == V10_ARCHIVE and archive.stat().st_size == 123_232_702,
                "Available prior archive differs")
    return {"manifest": manifest, "manifestHash": file_digest(manifest_path),
            "adaptiveIndex": index, "priorArchivePresent": archive.exists()}


def audit_runtime(record: dict, planned: dict, supplied: dict, directory: Path,
                  expected_budget_seconds: int | float = 300) -> dict:
    for key, expected in planned.items():
        strict_equal(record.get(key), expected, "retained case identity "+key)
    strict_equal(record.get("input"), supplied, "retained original input references")
    require(type(record.get("executionSucceeded")) is bool
            and type(record.get("scientificAvailable")) is bool, "Orthogonal flags missing")
    available, succeeded = record["scientificAvailable"], record["executionSucceeded"]
    failure_statuses = {"retained hard-budget timeout", "retained input failure",
                        "retained proposal failure", "retained certificate failure", "retained worker failure"}
    if succeeded:
        require(available and record.get("failure") is None, "Success without complete science")
        expected_status = ("certified response within gap target" if
                           record["certificate"]["withinRequestedGap"] else
                           "certified response with loose gap")
        strict_equal(record.get("status"), expected_status, "success tight/loose status")
    else:
        require(record.get("status") in failure_statuses and isinstance(record.get("failure"), dict)
                and isinstance(record["failure"].get("message"), str)
                and record["failure"]["message"], "Missing retained failure status/reason")
    runtime = record["runtime"]
    events = runtime.get("events")
    require(isinstance(events, list) and type(runtime.get("caseSeconds")) in (int, float)
            and math.isfinite(runtime["caseSeconds"]) and runtime["caseSeconds"] >= 0,
            "Invalid measured case runtime")
    if not events:
        require(not succeeded and not available and record["failure"].get("stage") == "runner",
                "Missing process events outside a retained runner-start failure")
        return {"events": [], "samples": []}
    strict_equal(runtime.get("hardBudgetSeconds"), expected_budget_seconds, "actual hard-budget declaration")
    task = json_value(read_reference(directory, runtime["task"]))
    strict_equal(task, {"plan": planned, "mode": "evidence", "payload": {"input": supplied}},
                 "owned case task")
    prior_elapsed, prior_sweep, samples = -1, 0, []
    for event in events:
        elapsed = event.get("elapsedMilliseconds")
        require(type(elapsed) in (int, float) and math.isfinite(elapsed)
                and elapsed >= prior_elapsed and elapsed >= 0, "Nonmonotone process event clock")
        prior_elapsed = elapsed
        require(isinstance(event.get("at"), str), "Missing event wall-clock label")
        stamp = datetime.fromisoformat(event["at"].replace("Z", "+00:00"))
        require(stamp.tzinfo is not None, "Unqualified event timestamp")
        if event.get("type") == "completed proposal received":
            sweep = event.get("completedSweeps")
            require(type(sweep) is int and prior_sweep < sweep <= 600,
                    "Nonincreasing completed proposal receipt")
            prior_sweep = sweep
            child, parent, paired = (event.get(name) for name in
                                     ("processRSSBytes", "supervisorRSSBytes", "approximatelyPairedRSSBytes"))
            require(child is None or type(child) is int and child >= 0, "Invalid child RSS sample")
            require(parent is None or type(parent) is int and parent >= 0, "Invalid parent RSS sample")
            strict_equal(paired, child+parent if child is not None and parent is not None else None,
                         "approximately paired memory sample")
            if parent is None:
                require(isinstance(event.get("supervisorRSSReason"), str)
                        and event["supervisorRSSReason"], "Missing parent RSS unavailable reason")
            else:
                require(event.get("supervisorRSSReason") is None, "Spurious parent RSS unavailable reason")
            samples.append({"nodeProcessRSSBytes": child, "supervisorRSSBytes": parent,
                            "supervisorRSSReason": event.get("supervisorRSSReason"),
                            "approximatelyPairedRSSBytes": paired})
    stops = [event for event in events if event.get("type") == "termination requested"]
    receipts = [event for event in events if event.get("type") == "complete certificate received"]
    starts = [event for event in events if event.get("type") == "owned process started"]
    require(len(stops) == 1 and events[-1] == stops[0], "Missing/split final termination event")
    stop = stops[0]
    strict_equal(runtime.get("terminationRequestedAt"), stop["at"], "termination timestamp")
    strict_equal(runtime.get("terminationRequestedMilliseconds"), stop["elapsedMilliseconds"], "termination clock")
    require(runtime["caseSeconds"]*1000 >= stop["elapsedMilliseconds"], "Case duration excludes termination")
    reason = "completed" if succeeded else ("timeout" if record["status"] == "retained hard-budget timeout" else "failure")
    strict_equal(stop.get("reason"), reason, "actual process stop reason")
    if starts:
        require(len(starts) == 1 and type(starts[0].get("pid")) is int
                and starts[0]["pid"] > 0 and runtime.get("ownedPID") == starts[0]["pid"],
                "Owned child PID differs")
    else:
        require(not succeeded and not available and runtime.get("ownedPID") is None,
                "Missing owned process start")
    if succeeded:
        strict_equal(runtime.get("workerExitCode"), 0, "natural successful process exit")
    if available:
        require(len(receipts) == 1, "Complete certificate receipt missing/duplicated")
        receipt = receipts[0]
        require(events.index(receipt) < events.index(stop)
                and receipt["elapsedMilliseconds"] <= stop["elapsedMilliseconds"]
                and receipt["elapsedMilliseconds"] < expected_budget_seconds*1000,
                "Scientific bundle not received before deadline/termination")
        require(type(receipt.get("lineReceivedMilliseconds")) in (int, float)
                and 0 <= receipt["lineReceivedMilliseconds"] <= receipt["elapsedMilliseconds"],
                "Line received after full-bundle validation")
        ref = runtime["completeCertificate"]
        strict_equal(receipt.get("sha256"), ref["sha256"], "complete receipt digest")
        strict_equal(runtime.get("receivedCompleteAt"), receipt["at"], "received complete time")
        strict_equal(runtime.get("receivedCompleteMilliseconds"), receipt["elapsedMilliseconds"],
                     "received complete monotonic time")
        complete = json_value(read_reference(directory, ref))
        for key, value in complete.items():
            strict_equal(record.get(key), value, "pre-termination complete report "+key)
        require(prior_sweep == record["optimizer"]["completedSweeps"],
                "Final scientific proposal was not a received completed milestone")
        require(record.get("scientificUnavailableReason") is None,
                "Available science has unavailable reason")
    else:
        require(not receipts and runtime.get("completeCertificate") is None
                and runtime.get("receivedCompleteAt") is None
                and runtime.get("receivedCompleteMilliseconds") is None,
                "Partial/late certificate relabelled unavailable inconsistently")
        for key in ("mdp", "baseline", "response", "certificate", "performance"):
            require(record.get(key) is None, "Unavailable record contains salvaged science: "+key)
        require(isinstance(record.get("scientificUnavailableReason"), str)
                and record["scientificUnavailableReason"], "Unavailable reason missing")
        partial = record.get("optimizer")
        if partial is not None:
            require(type(partial.get("completedSweeps")) is int
                    and partial["completedSweeps"] == prior_sweep and 1 <= prior_sweep <= 600,
                    "Partial proposal sweep identity differs")
            data = read_reference(directory, partial["finalFloat64"])
            require(0 < len(data) <= 15_376*8 and len(data) % 8 == 0
                    and all(math.isfinite(value[0]) for value in struct.iter_unpack("<d", data)),
                    "Invalid retained partial floating proposal")
            require(type(partial.get("difference")) in (int, float)
                    and math.isfinite(partial["difference"]) and partial["difference"] >= 0,
                    "Invalid retained partial floating diagnostic")
    return {"events": events, "samples": samples}


def scientific_negative_controls(record: dict, loaded: dict, directory: Path) -> dict:
    """Read-only in-memory alterations; changed artifacts receive fresh refs."""
    controls = {}
    def rejected(label, mutation, artifact=None):
        altered = copy.deepcopy(record)
        overrides = {}
        mutation(altered)
        if artifact is not None:
            target, key, data = artifact(altered)
            name = "artifacts/"+record["id"]+"/independent-negative-"+label+".bin"
            ref = {"file": name, "bytes": len(data), "sha256": digest(data)}
            target[key] = ref; overrides[name] = data
        def read(root, ref):
            if ref["file"] in overrides:
                value = overrides[ref["file"]]
                require(len(value) == ref["bytes"] and digest(value) == ref["sha256"],
                        "Malformed negative-control reference")
                return value
            return read_reference(root, ref)
        try:
            audit_scientific_record(altered, loaded, directory, artifact_reader=read)
        except ValueError:
            controls[label] = True
        else:
            raise ValueError("Scientific negative control did not reject: "+label)
    rejected("changedResidual", lambda r: r["certificate"].__setitem__(
        "maximumResidualNumeratorHex", hex(int(r["certificate"]["maximumResidualNumeratorHex"], 16)+1)))
    rejected("omittedLegalEdge", lambda r: r["certificate"].__setitem__(
        "allEdgesChecked", r["certificate"]["allEdgesChecked"]-1))
    rejected("wrongBellmanFactor", lambda r: r["certificate"].__setitem__(
        "upperValue", exact_hex(parse_hex(r["certificate"]["upperValue"])*Fraction(19,20)
                                 if parse_hex(r["certificate"]["upperValue"]) else Fraction(1))))
    rejected("wrongWitnessPair", lambda r: r["certificate"]["maximumWitness"].__setitem__(
        "payoffIndex", r["certificate"]["maximumWitness"]["payoffIndex"] ^ 1))
    rejected("resetTerminal", lambda r: r["mdp"]["terminal"].__setitem__(
        "node", r["mdp"]["terminal"]["node"] ^ 1))
    rejected("wrongOpponentWorldMap", lambda r: r["mdp"].__setitem__(
        "opponentWorldPolicySha256", ("0" if r["mdp"]["opponentWorldPolicySha256"][0] != "0" else "1")+
        r["mdp"]["opponentWorldPolicySha256"][1:]))
    rejected("hiddenRawGain", lambda r: r["performance"].__setitem__(
        "rawGain", exact_hex(parse_hex(r["performance"]["rawGain"])+1)))
    rejected("wrongGapTarget", lambda r: r["certificate"].__setitem__(
        "requestedGap", exact_hex(Fraction(1, 500_000))))
    rejected("wrongCoverageExposure", lambda r: r["response"]["coverage"]["B"]["discounted"].__setitem__(
        "unvisitedStateExposure", exact_hex(parse_hex(r["response"]["coverage"]["B"]["discounted"]
                                                       ["unvisitedStateExposure"])+Fraction(1,3))))
    rejected("cycleWelfareAsProfit", lambda r: r["performance"].__setitem__(
        "cycleCustomerBenefitDifference", exact_hex(parse_hex(r["performance"]
                                                               ["cycleCustomerBenefitDifference"])+1)))
    for label, key in (("wrongPathClock", "nextStates"), ("wrongCycleClosure", "closingState"),
                       ("wrongHistoricalVisits", "coverage")):
        def artifact(r, field=key):
            target = r["response"]
            path = json_value(read_reference(directory, target["path"]))
            if field == "closingState": path[field] ^= 1
            elif field == "coverage": path[field]["A"]["stateVisits"][0] += 1
            else: path[field][0] ^= 1
            return target, "path", (json.dumps(path, separators=(",", ":"))+"\n").encode()
        rejected(label, lambda r: None, artifact)
    def changed_proposal(r):
        data = read_reference(directory, r["optimizer"]["finalFloat64"])
        value = struct.unpack("<d", data[:8])[0]
        replacement = 1.0 if quantize_binary64(value) == 0 else -value
        return r["optimizer"], "finalFloat64", struct.pack("<d", replacement)+data[8:]
    rejected("wrongQuantization", lambda r: None, changed_proposal)
    rejected("missingFinalNewline", lambda r: None,
             lambda r: (r["optimizer"], "dyadicValues",
                        read_reference(directory, r["optimizer"]["dyadicValues"])[:-1]))
    rejected("illegalOffPathPolicy", lambda r: None,
             lambda r: (r["optimizer"], "responsePolicy",
                        read_reference(directory, r["optimizer"]["responsePolicy"])[:-1]+bytes([255])))
    return controls


def audit_study(directory: Path, project: Path) -> dict:
    started = time.perf_counter()
    project, directory = Path(project).resolve(), Path(directory).resolve()
    context = verify_study_dependencies(project, directory)
    manifest, manifest_hash = context["manifest"], context["manifestHash"]
    paths = {name: safe_path(directory, name) for name in
             ("results.json", "index.json", "completion.json", "execution-start.json", "journal.jsonl")}
    original_hashes = {name: file_digest(path) for name, path in paths.items()}
    results, index, completion, run_start = (json_value(paths[name].read_bytes()) for name in
                                           ("results.json", "index.json", "completion.json", "execution-start.json"))
    for item in (results, index, completion, run_start):
        require(item.get("manifestSha256") == manifest_hash, "Current output/manifest binding differs")
    require(completion.get("resultsSha256") == file_digest(paths["results.json"])
            and completion.get("indexSha256") == file_digest(paths["index.json"])
            and completion.get("inventoryComplete") is True
            and completion.get("finalFrozenDependencyCheck", {}).get("passed") is True,
            "Current completion/dependency gate differs")
    strict_equal(run_start.get("plannedRecords"), 48, "run-start planned matrix")
    rows, entries, plans = results["records"], index["records"], planned_cases()
    require(len(rows) == len(entries) == 48, "Incomplete48-label raw/index inventory")
    journal_data = paths["journal.jsonl"].read_bytes()
    require(journal_data.endswith(b"\n"), "Journal lacks final newline")
    journal = [json_value(line) for line in journal_data.splitlines()]
    cursor, total_states, total_edges, q_cells, reconstructions = 0, 0, 0, 0, 0
    input_cache_id, input_cache, first_science = None, None, None
    resource_samples, facts = [], []
    for row, entry, plan in zip(rows, entries, plans):
        strict_equal(entry.get("id"), plan["id"], "indexed case order")
        strict_equal(entry.get("file"), "records/"+plan["id"]+".json", "unique indexed case path")
        strict_equal(json_value(read_reference(directory, entry)), row, "indexed/aggregate full record")
        for key in ("status", "executionSucceeded", "scientificAvailable"):
            strict_equal(entry.get(key), row.get(key), "indexed status "+key)
        supplied = manifest["inputs"][plan["oldRunID"]]
        runtime = audit_runtime(row, plan, supplied, directory)
        require(cursor < len(journal) and journal[cursor].get("type") == "case started"
                and journal[cursor].get("id") == plan["id"], "Case-start journal missing/out of order")
        cursor += 1
        for event in runtime["events"]:
            require(cursor < len(journal), "Process journal truncated")
            strict_equal(journal[cursor], {"id": plan["id"], **event}, "runtime/journal event")
            cursor += 1
        require(cursor < len(journal), "Case-retained journal missing")
        retained = journal[cursor]
        for key, expected in {"id": plan["id"], "type": "case retained", "status": row["status"],
                              "executionSucceeded": row["executionSucceeded"],
                              "scientificAvailable": row["scientificAvailable"],
                              "recordSha256": entry["sha256"]}.items():
            strict_equal(retained.get(key), expected, "retained journal "+key)
        cursor += 1
        resource_samples.append({"id": plan["id"], "measurements": runtime["samples"]})
        if row["scientificAvailable"]:
            if input_cache_id != plan["oldRunID"]:
                input_cache = load_checkpoint_inputs(project, supplied,
                    {"seed": plan["seed"], "control": plan["control"]["id"]},
                    manifest["inputHashes"], context["adaptiveIndex"])
                input_cache_id = plan["oldRunID"]
                q_cells += 2*input_cache["layout"].offsets()[-1]; reconstructions += 1
            fact = audit_scientific_record(row, input_cache, directory)
            total_states += row["mdp"]["states"]; total_edges += fact["legalEdges"]
            if first_science is None:
                first_science = row, input_cache
            facts.append({**fact, "executionSucceeded": row["executionSucceeded"], "status": row["status"]})
        else:
            facts.append({"id": row["id"], "scientificAvailable": False,
                          "executionSucceeded": False, "status": row["status"],
                          "reason": row["scientificUnavailableReason"]})
    require(cursor == len(journal), "Unexpected/duplicate trailing journal events")
    available = sum(row["scientificAvailable"] for row in rows)
    failures = sum(not row["executionSucceeded"] for row in rows)
    tight = sum(row["scientificAvailable"] and row["certificate"]["withinRequestedGap"] for row in rows)
    expected_counts = {"retainedRecords": 48, "executionFailures": failures,
                       "budgetFailures": sum(row["status"] == "retained hard-budget timeout" for row in rows),
                       "scientificallyAvailable": available, "tightCertificates": tight,
                       "looseCertificates": available-tight, "primaryPassed": failures == 0}
    for key, expected in expected_counts.items():
        strict_equal(completion.get(key), expected, "primary completion "+key)
    resources = completion["resources"]
    saved_samples = resources["rssSamples"]
    require(len(saved_samples) == 48, "Resource sample inventory differs")
    for row, expected in zip(saved_samples, resource_samples):
        strict_equal(row.get("id"), expected["id"], "RSS case order")
        strict_equal(row.get("measurements"), expected["measurements"], "event/resource samples")
        parent = row["postCaseSupervisorRSS"]
        require((type(parent.get("bytes")) is int and parent["bytes"] >= 0 and parent.get("reason") is None)
                or (parent.get("bytes") is None and isinstance(parent.get("reason"), str)
                    and parent["reason"]), "Invalid post-case parent RSS/unavailable reason")
    samples = [sample for row in resource_samples for sample in row["measurements"]]
    children = [sample["nodeProcessRSSBytes"] for sample in samples if sample["nodeProcessRSSBytes"] is not None]
    paired = [sample["approximatelyPairedRSSBytes"] for sample in samples if sample["approximatelyPairedRSSBytes"] is not None]
    largest_child, largest_paired = max(children) if children else None, max(paired) if paired else None
    strict_equal(resources.get("largestSampledNodeProcessRSSBytes"), largest_child, "sampled child RSS maximum")
    strict_equal(resources.get("largestApproximatelyPairedRSSBytes"), largest_paired, "approximately paired RSS maximum")
    for key, values in (("nodeRSSUnavailableReason", children), ("pairedRSSUnavailableReason", paired)):
        reason = resources.get(key)
        require(reason is None if values else isinstance(reason, str) and bool(reason),
                "Missing/false RSS unavailable reason: "+key)
    seconds = resources.get("seconds")
    require(type(seconds) in (int, float) and math.isfinite(seconds) and seconds >= 0
            and seconds+1e-6 >= sum(row["runtime"]["caseSeconds"] for row in rows),
            "Global runtime excludes retained case time")
    primary_names = ("manifest.json", "sources", "execution-start.json", "journal.jsonl",
                     "records", "tasks", "artifacts", "results.json", "index.json")
    primary_bytes = 0
    for name in primary_names:
        item = safe_path(directory, name)
        if item.is_file(): primary_bytes += item.stat().st_size
        elif item.is_dir(): primary_bytes += sum(path.stat().st_size for path in item.rglob("*") if path.is_file())
    strict_equal(resources.get("newOutputBytesBeforeCompletion"), primary_bytes, "complete primary byte inventory")
    strict_equal(resources.get("softTargetExceeded"), {
        "seconds": seconds > 7200,
        "approximatelyPairedRSS": largest_paired > 512_000_000 if largest_paired is not None else None,
        "newOutputBytes": primary_bytes > 250_000_000}, "retained soft budget overruns")
    strict_equal(resources.get("trainingRounds"), 0, "no new training")
    strict_equal(resources.get("experimentalModelApiCalls"), 0, "no experimental model players")
    controls = {}
    inventory_controls = {"missingRetainedLabel": rows[:-1]}
    changed = copy.deepcopy(rows); changed[0]["focal"] = "B"
    inventory_controls["wrongFocalIdentity"] = changed
    duplicated = list(rows); duplicated[1] = rows[0]
    inventory_controls["duplicatePairedUnit"] = duplicated
    for label, altered in inventory_controls.items():
        try:
            independent_summaries(altered)
        except ValueError:
            controls[label] = True
        else:
            raise ValueError("Inventory negative control did not reject: "+label)
    if first_science:
        controls.update(scientific_negative_controls(first_science[0], first_science[1], directory))
    # Scope-only failure inventories can pass without inventing actual available
    # certificates or claiming that unavailable actual controls were executed.
    summaries = independent_summaries(rows)
    final_context = verify_study_dependencies(project, directory)
    require(final_context["manifestHash"] == manifest_hash, "Manifest changed during independent audit")
    for name in paths:
        require(file_digest(paths[name]) == original_hashes[name], "Output changed during audit")
    consumed = []
    for row, entry in zip(rows, entries):
        consumed.append(entry)
        runtime = row["runtime"]
        if runtime.get("task"): consumed.append(runtime["task"])
        if runtime.get("completeCertificate"): consumed.append(runtime["completeCertificate"])
        if row["optimizer"]:
            consumed.extend(row["optimizer"][key] for key in
                            ("finalFloat64", "dyadicValues", "responsePolicy") if key in row["optimizer"])
        if row["scientificAvailable"]:
            consumed.extend(row[name]["path"] for name in ("baseline", "response"))
    for reference in consumed:
        read_reference(directory, reference)
    return {"passed": True, "checkedAt": datetime.now(timezone.utc).isoformat(),
            "studyManifestHash": manifest_hash, "resultsSha256": original_hashes["results.json"],
            "indexSha256": original_hashes["index.json"], "completionSha256": original_hashes["completion.json"],
            "journalSha256": original_hashes["journal.jsonl"], "runStartSha256": original_hashes["execution-start.json"],
            "auditorSourceHash": file_digest(Path(__file__)), "arithmeticBackendHash": None,
            "labels": 48, "allPlannedLabelsRetained": True,
            "primaryExecutionPassed": completion["primaryPassed"],
            "scientificallyAvailableRecords": available, "certifiedRecords": available,
            "tightRecords": tight, "looseRecords": available-tight, "unavailableRecords": 48-available,
            "executionFailures": failures, "budgetFailures": expected_counts["budgetFailures"],
            "selectedCheckpoints": 24, "checkpointNumericalReconstructions": reconstructions,
            "maskedQCellsReconstructed": q_cells, "worldStatesChecked": total_states,
            "legalStateActionEdgesChecked": total_edges,
            "corruptionNegativeControls": controls, "actualScientificNegativeControlsAvailable": first_science is not None,
            "independentSummaries": summaries, "recordSummaries": facts,
            "fullTrainingReplay": False, "optimizerIterationsReplayed": False,
            "inheritedEconomicReenumeration": False,
            "seconds": time.perf_counter()-started,
            "scope": "Exact saved-weight known-MDP audit; all available states/actions and full paths, no optimizer/training replay. Old finite economics reused through accepted hashes. Process event sequence and recorded counters checked; not independently authenticated wall clocks or continuous peak memory."}


def main(argv=None) -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Read-only independent saved-opponent audit")
    parser.add_argument("--directory", type=Path, default=root/"research/learned-opponent-results")
    parser.add_argument("--project-root", type=Path, default=root)
    parser.add_argument("--output", type=Path, help="Exclusive-create a NEW receipt; default stdout is read-only")
    args = parser.parse_args(argv)
    try:
        if args.output is not None and args.output.exists():
            raise FileExistsError("Existing independent receipt preserved: "+str(args.output))
        receipt = audit_study(args.directory, args.project_root)
        encoded = json.dumps(receipt, separators=(",", ":"), allow_nan=False)+"\n"
        if args.output is not None:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open("x", encoding="utf8", newline="\n") as stream:
                stream.write(encoded)
        print(encoded, end="")
        return 0
    except Exception as error:
        print(json.dumps({"passed": False, "failure": str(error),
                          "errorType": type(error).__name__}, separators=(",", ":")))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
