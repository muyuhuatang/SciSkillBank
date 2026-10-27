#!/usr/bin/env python3
"""
Figure 2 -- UMAP landscape of the 11,613 validly summarized candidate repositories.

    python3 figures/fig2_umap.py          # writes the figure PDFs into figures/
    python3 figures/fig2_umap.py --png    # also writes the two panel PNGs used in the paper

Reads only dataset/sciskillbank_umap_all_candidates.csv. No network, GPU or API
calls. The UMAP coordinates are precomputed from the text-embedding-3-large embeddings
of the repository summaries (cosine distance, 15 neighbors, minimum distance 0.1); this
script only draws them. Every count behind the figure is printed to stdout.

Left panel: every repository as a light-grey point, research and data-science
repositories in color, and a label at the density peak of each broad domain with at
least 150 repositories.

Right panel: the 2,199 research-relevant repositories (broad domain research or data
science) that have an embedding, colored by primary workflow stage. The three most
frequent primary stages get the three colors, the other twelve stages are dark grey,
and repositories outside the corpus stay light grey. Stages with at least 40
repositories are labeled.

Why the design looks like this: a scatter plot can put any two categories next to each
other, so every pair of hues must stay distinguishable, and ten or fifteen hues cannot.
Category identity therefore comes from a label placed on the point cloud rather than a
legend swatch, and hue is spent on at most three categories per panel. The three hues
are the first three slots of a categorical palette chosen so that every pair stays
distinguishable, including under simulated colour-vision deficiency.

The axes carry no ticks because UMAP axes and distances have no quantitative meaning.
"""
import argparse
import collections
import csv
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import patheffects

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "dataset", "sciskillbank_umap_all_candidates.csv")
OUTDIR = os.path.join(ROOT, "figures")

# categorical slots 1-3 (all-pairs safe on a scatter), plus greys
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
GREY_PT   = "#d6d5d0"     # backdrop points, left panel
GREY_BG   = "#eceae4"     # backdrop points, right panel
GREY_DARK = "#8a8983"     # the twelve smaller stages, right panel
INK       = "#0b0b0b"
INK_2     = "#52514e"

# The ten broad domains on the categorization menu. The CSV stores the raw model string,
# so 21 rows carry an off-menu value (game_dev, productivity, ...), which the paper merges
# into "other". Off-menu rows are never labeled, and "other" (75 rows) is below the
# 150-point label threshold, so both appear only in the grey backdrop either way.
DOMAIN_CANON = ["devops", "general_coding", "data_science", "web_dev", "industry",
                "education", "research", "mobile", "design", "other"]
DOMAIN_NICE = {"devops": "DevOps", "general_coding": "General coding",
               "data_science": "Data science", "web_dev": "Web dev",
               "industry": "Industry", "education": "Education",
               "research": "Research", "mobile": "Mobile", "design": "Design",
               "other": "Other"}
RESEARCH_CORPUS = ("research", "data_science")
# Short display names for the 15 workflow stages. Kept short on purpose: these are drawn
# ON the cloud, so a long string cannot be placed without overrunning its neighbours.
STAGE_NICE = {"ideation_formulation": "Ideation", "study_design": "Study design",
              "literature_review": "Literature review",
              "data_collection_preparation": "Data collection", "exploratory_data_analysis": "EDA",
              "data_analysis": "Data analysis", "visualization": "Visualization",
              "writing_documentation": "Writing", "submission_peer_review": "Peer review",
              "replication_reproducibility": "Replication", "quality_assurance": "Quality assurance",
              "citation_management": "Citation mgmt",
              "collaboration_project_management": "Project mgmt",
              "communication_dissemination": "Communication", "ethics_safety": "Ethics"}

PANEL_SIZE = (3.5, 3.3)   # inches, one panel; the paper places two side by side

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 7.5, "axes.labelsize": 8.5, "axes.titlesize": 9,
    "axes.linewidth": 0.6, "xtick.labelsize": 7, "ytick.labelsize": 7,
    "figure.dpi": 400, "savefig.dpi": 400,
    "pdf.fonttype": 42,   # TrueType, not Type 3, for the axis titles (haloed labels become outlines)
})


def load():
    """The 11,613 rows of the all-candidate UMAP table, with float coordinates."""
    with open(SRC, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 11613:
        raise RuntimeError("expected 11,613 rows in %s, found %d" % (SRC, len(rows)))
    for r in rows:
        r["x"] = float(r["umap_x"]); r["y"] = float(r["umap_y"])
    return rows


def frame(ax, xlab="UMAP 1", ylab="UMAP 2"):
    """A quiet frame: no ticks (the axes carry no units), thin spines, ample air."""
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#c9c8c2"); ax.spines[s].set_linewidth(0.6)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_xlabel(xlab, color=INK_2, labelpad=3)
    ax.set_ylabel(ylab, color=INK_2, labelpad=3)
    ax.set_facecolor("white")


def label(ax, x, y, text, color=INK, size=7.2, weight="medium"):
    """Direct label with a white halo so it stays legible over dense points."""
    t = ax.text(x, y, text, fontsize=size, color=color, ha="center", va="center",
                fontweight=weight, zorder=60)
    t.set_path_effects([patheffects.withStroke(linewidth=2.6, foreground="white")])
    return t


def peak(pts, grid=64):
    """Where the category is DENSEST, not where its coordinates average out.

    A median centroid drags every label toward the middle of the map, because a
    UMAP cloud is rarely convex; several categories then land on the same spot.
    Binning and taking the modal cell puts each label inside its own mass.
    """
    a = np.array(pts)
    if len(a) < 12:
        return float(np.median(a[:, 0])), float(np.median(a[:, 1]))
    H, xe, ye = np.histogram2d(a[:, 0], a[:, 1], bins=grid)
    # light smoothing so a single lucky bin does not win
    K = np.array([[1, 2, 1], [2, 4, 2], [1, 2, 1]], float); K /= K.sum()
    P = np.pad(H, 1, mode="edge")
    S = sum(K[i, j] * P[i:i + H.shape[0], j:j + H.shape[1]]
            for i in range(3) for j in range(3))
    i, j = np.unravel_index(np.argmax(S), S.shape)
    return float((xe[i] + xe[i + 1]) / 2), float((ye[j] + ye[j + 1]) / 2)


def place(cands, unit_dx, min_dy, bounds):
    # unit_dx = (data span in x, axes width in inches)
    """Greedy, largest-first label placement with collision resolution.

    cands: (n_points, x, y, text, colour, weight, size). Two refinements matter:

      * clearance scales with the LABEL'S OWN WIDTH. A fixed threshold lets long
        strings ("Literature review") overlap while short ones are pushed apart
        more than they need to be.
      * placements are clamped inside the axes, so a label near the edge is not
        half-cut by the frame.

    A label with no free spot is dropped rather than drawn on top of another, and
    main() reports it.
    """
    (x0, x1, y0, y1) = bounds
    placed, out = [], []
    for n, x, y, text, col, wt, sz in sorted(cands, key=lambda c: -c[0]):
        # half-width in DATA units, from the glyph size actually used:
        #   width_inches = n_chars * pt_size * avg_glyph_ratio / 72
        # An estimate that is too small is what lets long labels overrun short
        # ones, so the ratio is set for a wide sans face and rounded up.
        half = (len(text) * sz * .60 / 72.0) / unit_dx[1] * unit_dx[0] * .5
        px, py = x, y
        ok = False
        for _ in range(40):
            px = min(max(px, x0 + half), x1 - half)
            py = min(max(py, y0 + min_dy), y1 - min_dy)
            hit = None
            for qx, qy, qhalf in placed:
                if abs(px - qx) < (half + qhalf) and abs(py - qy) < min_dy:
                    hit = (qx, qy); break
            if hit is None:
                ok = True; break
            dx, dy = px - hit[0], py - hit[1]
            if abs(dx) < 1e-9 and abs(dy) < 1e-9:
                dx, dy = 1.0, 0.6
            norm = (dx * dx + dy * dy) ** .5
            px += (dx / norm) * half * .55
            py += (dy / norm) * min_dy * .85
        if ok:
            placed.append((px, py, half)); out.append((px, py, text, col, wt, sz))
    return out


def label_peaks(ax, X, groups, min_n, nice, colors, sizes):
    """Label every group of at least min_n points at its density peak.

    Returns (labels drawn, labels dropped for lack of space)."""
    span_x = X[:, 0].max() - X[:, 0].min(); span_y = X[:, 1].max() - X[:, 1].min()
    cands = []
    for cat, pts in groups.items():
        if len(pts) < min_n:
            continue
        cx, cy = peak(pts)
        cands.append((len(pts), cx, cy, nice[cat], colors.get(cat, INK_2),
                      "bold" if cat in colors else "normal",
                      sizes[0] if cat in colors else sizes[1]))
    b = (X[:, 0].min(), X[:, 0].max(), X[:, 1].min(), X[:, 1].max())
    drawn = place(cands, (span_x, PANEL_SIZE[0] * 0.80), span_y * .045, b)
    for px, py, text, col, wt, sz in drawn:
        label(ax, px, py, text, color=col, weight=wt, size=sz)
    shown = [d[2] for d in drawn]
    return shown, [c[3] for c in cands if c[3] not in shown]


def draw_domains(ax, rows):
    """Left panel: the full landscape, research and data science highlighted."""
    X = np.array([[r["x"], r["y"]] for r in rows])
    ax.scatter(X[:, 0], X[:, 1], s=1.6, c=GREY_PT, lw=0, alpha=.55, zorder=1,
               rasterized=True)

    hi = {"research": BLUE, "data_science": ORANGE}
    for cat, col in hi.items():
        P = np.array([[r["x"], r["y"]] for r in rows if r["broad_domain"] == cat])
        ax.scatter(P[:, 0], P[:, 1], s=2.6, c=col, lw=0, alpha=.85, zorder=3,
                   rasterized=True)

    # No outline is drawn around the research points; the paper interprets the
    # projection only qualitatively.
    by = collections.defaultdict(list)
    for r in rows:
        if r["broad_domain"] in DOMAIN_CANON:
            by[r["broad_domain"]].append((r["x"], r["y"]))
    shown, dropped = label_peaks(ax, X, by, 150, DOMAIN_NICE, hi, (7.4, 6.9))
    frame(ax)
    return {"counts": collections.Counter(r["broad_domain"] for r in rows),
            "labels": shown, "dropped": dropped}


def draw_stages(ax, rows):
    """Right panel: the research-relevant corpus colored by primary workflow stage."""
    res = [r for r in rows if r["broad_domain"] in RESEARCH_CORPUS]
    # Backdrop is the FULL corpus, so no repository is hidden -- the foreground layers
    # simply redraw the subset each one is about, on top.
    X = np.array([[r["x"], r["y"]] for r in rows])
    ax.scatter(X[:, 0], X[:, 1], s=1.4, c=GREY_BG, lw=0, alpha=.7, zorder=1,
               rasterized=True)

    cnt = collections.Counter(r["primary_stage"] for r in res
                              if r["primary_stage"] in STAGE_NICE)
    top3 = [k for k, _ in cnt.most_common(3)]
    cols = dict(zip(top3, (BLUE, ORANGE, AQUA)))

    # The dark-grey layer is the twelve smaller workflow stages. A repository without a
    # primary stage remains in the light-grey backdrop rather than being presented as a
    # labelled stage.
    rest = [r for r in res if r["primary_stage"] in STAGE_NICE and r["primary_stage"] not in top3]
    if rest:
        P = np.array([[r["x"], r["y"]] for r in rest])
        ax.scatter(P[:, 0], P[:, 1], s=2.0, c=GREY_DARK, lw=0, alpha=.6, zorder=2,
                   rasterized=True)
    for cat in top3:
        P = np.array([[r["x"], r["y"]] for r in res if r["primary_stage"] == cat])
        ax.scatter(P[:, 0], P[:, 1], s=3.0, c=cols[cat], lw=0, alpha=.85, zorder=3,
                   rasterized=True)

    by = collections.defaultdict(list)
    for r in res:
        if r["primary_stage"] in STAGE_NICE:
            by[r["primary_stage"]].append((r["x"], r["y"]))
    shown, dropped = label_peaks(ax, X, by, 40, STAGE_NICE, cols, (7.2, 6.7))
    frame(ax)
    return {"n": len(res), "counts": cnt, "top3": top3,
            "no_stage": sum(1 for r in res if r["primary_stage"] not in STAGE_NICE),
            "labels": shown, "dropped": dropped}


def save(fig, path):
    fig.tight_layout(pad=0.3)
    kw = {"metadata": {"CreationDate": None}} if path.endswith(".pdf") else {}
    fig.savefig(path, bbox_inches="tight", facecolor="white", **kw)
    plt.close(fig)
    print("  wrote %s" % os.path.relpath(path, ROOT))


def report(a, b):
    print("\nLeft panel: %d repositories" % sum(a["counts"].values()))
    for cat in DOMAIN_CANON:
        print("  %-15s %5d" % (cat, a["counts"][cat]))
    off = {k: v for k, v in a["counts"].items() if k not in DOMAIN_CANON}
    print("  off-menu        %5d  %s" % (sum(off.values()), dict(sorted(off.items()))))
    print("  labels drawn:   %s" % ", ".join(a["labels"]))
    print("  labels dropped: %s" % (", ".join(a["dropped"]) or "none"))

    print("\nRight panel: %d research-relevant repositories with an embedding" % b["n"])
    for cat, n in b["counts"].most_common():
        mark = "  <- colored" if cat in b["top3"] else ""
        print("  %-34s %5d%s" % (cat, n, mark))
    print("  no primary stage (backdrop)        %5d" % b["no_stage"])
    print("  labels drawn:   %s" % ", ".join(b["labels"]))
    print("  labels dropped: %s" % (", ".join(b["dropped"]) or "none"))


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("--png", action="store_true",
                    help="also write the two panel PNGs at 400 dpi, as embedded in the paper")
    args = ap.parse_args()

    rows = load()
    os.makedirs(OUTDIR, exist_ok=True)
    exts = ["pdf", "png"] if args.png else ["pdf"]

    # Each panel on its own, at the size the paper uses.
    info = {}
    for name, draw in (("left", draw_domains), ("right", draw_stages)):
        stem = {"left": "fig2_left_all_domains", "right": "fig2_right_research_stages"}[name]
        for ext in exts:
            fig, ax = plt.subplots(figsize=PANEL_SIZE)
            info[name] = draw(ax, rows)
            save(fig, os.path.join(OUTDIR, "%s.%s" % (stem, ext)))

    # Both panels side by side, as Figure 2 appears in the paper.
    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(2 * PANEL_SIZE[0], PANEL_SIZE[1]))
    draw_domains(ax_a, rows)
    draw_stages(ax_b, rows)
    save(fig, os.path.join(OUTDIR, "fig2_umap.pdf"))

    report(info["left"], info["right"])


if __name__ == "__main__":
    main()
