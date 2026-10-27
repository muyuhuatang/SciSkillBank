#!/usr/bin/env python3
"""Figure: measurement instability of the released annotation dimensions.

Three panels:

  (a) autonomy-level shares under four counterbalanced orderings of the option list
  (b) position effect: each level's share when it leads the list against when it does not
  (c) methodology x autonomy association under four elicitation structures

Every number is recomputed from the per-repository label tables written by
code/instability/02_option_order.py and code/instability/01_decoupled_annotation.py. Nothing is
hardcoded. Point estimates are deterministic and must reproduce the archived reports
exactly; bootstrap intervals are recomputed under the seed below and printed for audit.

    python3 fig4_measurement_instability.py
"""

import csv
import math
import random
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

import vizstyle as vs

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "dataset" / "instability"
OUT = HERE / "fig4_measurement_instability.pdf"

BOOT_SEED = 20260923
BOOT_B = 5000

ORDERS = ["forward", "reverse", "mid_collab", "mid_deleg"]
ORDER_LABEL = {
    "forward": "forward",
    "reverse": "reverse",
    "mid_collab": "collab-\nfirst",
    "mid_deleg": "deleg-\nfirst",
}
# Which level is presented first in each ordering, from the run's prompt definitions.
LEADS = {
    "forward": "assistive",
    "reverse": "autonomous",
    "mid_collab": "collaborative",
    "mid_deleg": "delegated",
}
LEVELS = ["assistive", "collaborative", "delegated", "autonomous"]
# Ordered categories -> one hue light to dark (vizstyle RAMP4), never a categorical cycle.
LEVEL_COLOR = dict(zip(LEVELS, vs.RAMP4))

CONDITIONS = [
    ("released_meth", "released_aut", "released", "as released"),
    ("joint_meth", "joint_aut", "joint", "joint re-run"),
    ("decoupled_v2_meth", "decoupled_v2_aut", "decoupled_v2", "separate calls"),
    ("decoupled_meth", "decoupled_aut", "decoupled", "separate, stages dropped"),
]


def read(path):
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def cramers_v(pairs):
    """Cramer's V for a 2 x 4 contingency table given (methodology, autonomy) pairs."""
    rows = sorted({a for a, _ in pairs})
    cols = sorted({b for _, b in pairs})
    n = len(pairs)
    if n == 0 or len(rows) < 2 or len(cols) < 2:
        return float("nan")
    obs = Counter(pairs)
    rtot = Counter(a for a, _ in pairs)
    ctot = Counter(b for _, b in pairs)
    chi2 = 0.0
    for r in rows:
        for c in cols:
            exp = rtot[r] * ctot[c] / n
            if exp > 0:
                chi2 += (obs.get((r, c), 0) - exp) ** 2 / exp
    return math.sqrt(chi2 / (n * min(len(rows) - 1, len(cols) - 1)))


def boot_ci(pairs, b=BOOT_B, seed=BOOT_SEED):
    rng = random.Random(seed)
    n = len(pairs)
    vals = []
    for _ in range(b):
        vals.append(cramers_v([pairs[rng.randrange(n)] for _ in range(n)]))
    vals = sorted(v for v in vals if not math.isnan(v))
    return vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals))]


def main():
    order_rows = read(DATA / "option_order_labels.csv")
    dec_rows = read(DATA / "decoupled_labels.csv")
    n_order, n_dec = len(order_rows), len(dec_rows)

    # ---- panel (a): marginal share of each level under each ordering ----
    shares = {}
    for o in ORDERS:
        c = Counter(r[o] for r in order_rows)
        shares[o] = {lv: 100.0 * c[lv] / n_order for lv in LEVELS}

    # ---- panel (b): position effect (leading vs not leading), same level both sides ----
    lift = {}
    for lv in LEVELS:
        lead_orders = [o for o in ORDERS if LEADS[o] == lv]
        rest_orders = [o for o in ORDERS if LEADS[o] != lv]
        lead = sum(shares[o][lv] for o in lead_orders) / len(lead_orders)
        rest = sum(shares[o][lv] for o in rest_orders) / len(rest_orders)
        lift[lv] = (lead, rest, lead - rest)

    # ---- unanimity across all four orderings ----
    unanimous = sum(1 for r in order_rows if len({r[o] for o in ORDERS}) == 1)

    # ---- panel (c): association under each elicitation structure ----
    assoc = []
    for mcol, acol, key, label in CONDITIONS:
        pairs = [(r[mcol], r[acol]) for r in dec_rows if r[mcol] and r[acol]]
        v = cramers_v(pairs)
        lo, hi = boot_ci(pairs)
        assoc.append((key, label, v, lo, hi, len(pairs)))

    # ---------------- audit print ----------------
    print(f"option-order table: n={n_order}   decoupling table: n={n_dec}")
    print(f"\n(a) autonomy share (%) by ordering  [leading level in brackets]")
    print("    " + "".join(f"{o:>13}" for o in ORDERS))
    for lv in LEVELS:
        print(f"    {lv:<14}" + "".join(f"{shares[o][lv]:12.1f}" for o in ORDERS))
    print("    leads:        " + "".join(f"{LEADS[o]:>13}" for o in ORDERS))
    print(f"\n(b) position effect: share leading / not leading / lift (pp)")
    for lv in LEVELS:
        a, b_, d = lift[lv]
        print(f"    {lv:<14} {a:6.1f} {b_:6.1f} {d:+7.1f}")
    print(f"    mean |lift| = {sum(abs(lift[lv][2]) for lv in LEVELS) / len(LEVELS):.1f} pp")
    print(f"\n    all four orderings agree: {unanimous} of {n_order} "
          f"({100.0 * unanimous / n_order:.1f}%)")
    print(f"\n(c) methodology x autonomy association "
          f"(bootstrap B={BOOT_B}, seed={BOOT_SEED})")
    for key, label, v, lo, hi, n in assoc:
        print(f"    {key:<14} V={v:.3f}  [{lo:.3f}, {hi:.3f}]  n={n}")

    # ---------------- figure ----------------
    vs.apply_rc()
    # Venues reject Type 3; force TrueType so figure text stays editable vector text.
    plt.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42})
    fig = plt.figure(figsize=(5.5, 3.42))
    gs = fig.add_gridspec(
        2, 2, height_ratios=[1.0, 0.66], width_ratios=[1.40, 1.0],
        hspace=0.44, wspace=0.40,
        left=0.105, right=0.985, top=0.94, bottom=0.085,
    )
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[1, :])

    # (a) slopegraph across the four orderings
    xs = list(range(len(ORDERS)))
    for lv in LEVELS:
        ys = [shares[o][lv] for o in ORDERS]
        ax_a.plot(xs, ys, "-o", color=LEVEL_COLOR[lv], lw=1.5, ms=3.4,
                  mec="white", mew=0.6, zorder=3, clip_on=False)
    # End labels collide when two levels finish close together (autonomous 8.0 vs
    # collaborative 5.8), so push them apart vertically before drawing.
    ends = sorted(((shares[ORDERS[-1]][lv], lv) for lv in LEVELS))
    placed, min_gap = [], 5.0
    for y, lv in ends:
        if placed and y - placed[-1][0] < min_gap:
            y = placed[-1][0] + min_gap
        placed.append((y, lv))
    for y_text, lv in placed:
        ax_a.text(xs[-1] + 0.10, y_text, lv, va="center", ha="left",
                  fontsize=6.1, color=LEVEL_COLOR[lv], clip_on=False)
    ax_a.set_xticks(xs)
    ax_a.set_xticklabels([ORDER_LABEL[o] for o in ORDERS])
    ax_a.set_ylabel("repositories (%)")
    ax_a.set_xlabel("option order presented to the model")
    ax_a.set_xlim(-0.18, len(ORDERS) - 1 + 1.62)
    ax_a.set_ylim(0, 80)
    vs.frame(ax_a, xgrid=False, ygrid=True)

    # (b) dumbbell: leading vs not leading, per level
    ys = list(range(len(LEVELS)))[::-1]
    LIFT_X = 84.0   # fixed column for the lift values, so they align and cannot collide
    for y, lv in zip(ys, LEVELS):
        lead, rest, d = lift[lv]
        ax_b.plot([rest, lead], [y, y], "-", color=vs.TRACK, lw=2.6,
                  solid_capstyle="round", zorder=1)
        ax_b.plot([rest], [y], "o", color=vs.MUTED, ms=4.0, zorder=3,
                  mec="white", mew=0.6)
        ax_b.plot([lead], [y], "o", color=vs.FILL_DARK, ms=4.8, zorder=3,
                  mec="white", mew=0.6)
        ax_b.text(LIFT_X, y, f"{d:+.1f}", va="center", ha="right",
                  fontsize=6.2, color=vs.INK_2)
    ax_b.set_yticks(ys)
    ax_b.set_yticklabels(LEVELS)
    ax_b.set_xlabel("share of repositories (%)")
    ax_b.set_xticks([0, 20, 40, 60])
    ax_b.set_xlim(0, 88)
    ax_b.set_ylim(-0.6, len(LEVELS) + 0.25)
    vs.frame(ax_b, xgrid=True, ygrid=False)
    ax_b.text(LIFT_X, len(LEVELS) - 0.55, "lift", va="center", ha="right",
              fontsize=6.2, color=vs.MUTED)
    ax_b.legend(
        handles=[
            Line2D([], [], marker="o", ls="", color=vs.MUTED, ms=4.0,
                   label="does not lead"),
            Line2D([], [], marker="o", ls="", color=vs.FILL_DARK, ms=4.8,
                   label="leads the list"),
        ],
        loc="upper center", bbox_to_anchor=(0.42, 1.20), ncol=2, frameon=False,
        handletextpad=0.3, borderpad=0.0, columnspacing=0.9,
    )

    # (c) association point-range across elicitation structures
    yc = list(range(len(assoc)))[::-1]
    for y, (key, label, v, lo, hi, _n) in zip(yc, assoc):
        # red = the structure under test; blue = the released/control structure
        col = vs.BLUE if key in ("released", "joint") else vs.RED
        ax_c.plot([lo, hi], [y, y], "-", color=col, lw=1.5,
                  solid_capstyle="round", alpha=0.55, zorder=2)
        ax_c.plot([v], [y], "o", color=col, ms=4.6, zorder=3,
                  mec="white", mew=0.7)
        ax_c.annotate(f"{v:.2f}", (hi, y), xytext=(5, 0),
                      textcoords="offset points", ha="left", va="center",
                      fontsize=6.2, color=vs.INK_2)
    ax_c.set_yticks(yc)
    ax_c.set_yticklabels([lab for _k, lab, *_ in assoc])
    ax_c.set_xlabel("Cramér's $V$, methodology encoding $\\times$ autonomy level")
    ax_c.set_xlim(0, 1.0)
    ax_c.set_ylim(-0.6, len(assoc) - 0.4)
    vs.frame(ax_c, xgrid=True, ygrid=False)

    for ax, tag in ((ax_a, "a"), (ax_b, "b"), (ax_c, "c")):
        ax.text(-0.10, 1.10, tag, transform=ax.transAxes, fontsize=8.4,
                fontweight="bold", va="top", ha="right", color=vs.INK_1)

    fig.savefig(OUT, bbox_inches="tight", pad_inches=0.02)
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
