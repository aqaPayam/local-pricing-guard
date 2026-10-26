"""Deterministic twelve-pair figure from accepted evidence; never trains a player."""
from pathlib import Path
from fractions import Fraction
import argparse
import hashlib
import json
import sys
import types

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parent.parent
try:
    import matplotlib
except ImportError:
    sys.path.append(str(Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/python/Lib/site-packages'))
    import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def module():
    path = ROOT/'research/build-matched-clock-web.py'
    value = types.ModuleType('matched_clock_export')
    value.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), value.__dict__)
    return value


def fraction(value):
    return Fraction(int(value['numerator']), int(value['denominator']))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--audit-sha', required=True)
    args = cli.parse_args()
    source = ROOT/'research/matched-clock-results/analysis.json'
    summary = module().load_accepted(source, args.audit_sha)
    rows = summary['pairedRows']
    if [r['seed'] for r in rows] != list(range(907001, 907013)):
        raise ValueError('All twelve rows must remain in prospective seed order')
    output = ROOT/'research/matched-clock-figures'
    output.mkdir(exist_ok=True)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9,
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'svg.hashsalt': 'matched-clock-twelve-pairs-v1',
                         'savefig.facecolor': 'white'})
    fig, ax = plt.subplots(figsize=(8.6, 3.7))
    ax.axvline(0, color='#858178', linewidth=1, zorder=0)
    observed = []
    for index, row in enumerate(rows):
        if row['available']:
            exact = fraction(row['difference'])
            value = float(exact)
            observed.append(value)
            color = '#3c6c50' if exact > 0 else '#9a4b4b' if exact < 0 else '#686052'
            ax.plot([0, value], [index, index], color=color, linewidth=2)
            ax.scatter([value], [index], color=color, marker='o' if exact else 'D', s=25, zorder=3)
        else:
            ax.text(.99, index, 'Unavailable; reason retained in evidence',
                    transform=ax.get_yaxis_transform(), ha='right', va='center',
                    fontsize=7.5, color='#686052')
    primary = summary['primarySummary']
    mean_caption = 'Planned all-twelve mean unavailable'
    if primary['available']:
        mean = float(fraction(primary['meanDifference']))
        observed.append(mean)
        ax.axvline(mean, color='#263b35', linestyle='--', linewidth=1.2)
        mean_caption = f'Dashed line: all-twelve exact mean, displayed approximately {mean:+.4f}'
    lower, upper = min([0, *observed]), max([0, *observed])
    span = max(upper-lower, .1)
    ax.set_xlim(lower-.08*span, upper+.12*span)
    ax.set_yticks(range(12), [str(r['seed']) for r in rows])
    ax.set_ylim(11.8, -.8)
    ax.set_ylabel('Paired whole-market seed')
    ax.set_xlabel('Eventual-cycle customer benefit: repeated limits minus one initial limit')
    ax.set_title('Same five clock labels and allocated memory; all twelve planned pairs\n'+mean_caption,
                 loc='left', fontsize=10)
    ax.grid(axis='x', alpha=.12)
    fig.tight_layout()
    png, svg = output/'matched-clock-paired.png', output/'matched-clock-paired.svg'
    fig.savefig(png, dpi=240, metadata={'Software': 'Market Lab / Matplotlib'})
    fig.savefig(svg, metadata={'Date': None})
    plt.close(fig)
    # Revalidate the complete accepted closure after rendering.
    module().load_accepted(source, args.audit_sha)
    receipt = {'scope': 'Deterministic descriptive plot of all twelve prospective paired rows; no confidence interval, training, or new numerical case',
               'builderSha256': sha(Path(__file__)), 'analysisSha256': sha(source),
               'independentAuditSha256': args.audit_sha,
               'rows': len(rows), 'availablePairs': primary['availablePairs'],
               'plannedMeanAvailable': primary['available'],
               'files': {p.relative_to(ROOT).as_posix(): {'sha256': sha(p), 'bytes': p.stat().st_size} for p in [png, svg]}}
    (output/'figure-receipt.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(receipt))


if __name__ == '__main__':
    main()
