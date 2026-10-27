"""Shared chart style for the SciSkillBank figures.

One place for the palette and the small helpers, so Figure 4 and the appendix figures
cannot drift apart. Every colour here has been through `validate_palette.js`; the notes
on each say which gate it passed and under which pairlist, because the answer differs
by chart form:

  * STACKED bars, grouped bars, lines -> segments meet only at ADJACENT pairs, so the
    documented 8-slot order is legal as far as it goes.
  * SCATTER, bubble, map -> any two categories can land side by side, so ALL pairs must
    clear the floors. Only the FIRST THREE slots do. Past three: fold to "Other", facet,
    or carry identity with direct labels instead of hue.
  * ORDERED categories (autonomy levels, tiers) -> not categorical at all. One hue,
    light to dark, validated with --ordinal.

The recurring mistake this file exists to prevent is reaching for a 10-colour cycle
because there are 10 categories.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SURFACE = "#ffffff"
INK_1, INK_2, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID = "#e1e0d9"
TRACK = "#e8e7e1"

# Categorical slots, in fixed order. Never cycled, never reordered per chart.
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
YELLOW, MAGENTA, GREEN, VIOLET, RED = "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"
CAT8 = [BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREEN, VIOLET, RED]
CAT3 = [BLUE, ORANGE, AQUA]          # the only three safe on a scatter

# Sequential blue ramp, for magnitude and for ORDERED categories.
RAMP4 = ["#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]   # steps 250/400/550/700
FILL = "#9ec5f4"                                        # single-series fill (step 200)
FILL_DARK = "#2a78d6"

# Below this many observations a group's summary statistics are noise: one item moves a
# median or a share far enough to invent a pattern. Such rows are drawn back and their
# n is printed, rather than being silently given equal visual weight.
MUTE_BELOW = 30

BASE_RC = {
    "font.size": 7.2, "axes.labelsize": 7.6, "xtick.labelsize": 6.8,
    "ytick.labelsize": 7.2, "legend.fontsize": 6.8,
    "axes.axisbelow": True, "figure.dpi": 600, "savefig.dpi": 600,
}


def apply_rc():
    plt.rcParams.update(BASE_RC)


def frame(ax, xgrid=True, ygrid=False):
    """Recessive chrome: no box, hairline gridlines on the value axis only."""
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(axis="x", length=2, color=GRID, pad=2, labelcolor=MUTED)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x" if xgrid else "y", color=GRID, lw=0.6, alpha=1.0)
    ax.set_axisbelow(True)


def demote(ax, labels, counts, below=MUTE_BELOW):
    """Grey and italicise the tick labels of under-evidenced rows, and return a
    parallel list of alphas for the marks so the whole row recedes together."""
    alphas = []
    for tick, c in zip(ax.get_yticklabels(), counts):
        if c < below:
            tick.set_color(MUTED)
            tick.set_style("italic")
        alphas.append(0.42 if c < below else 1.0)
    return alphas


def ncol(ax, counts, x=1.02, header="n", fmt="{:,}", below=MUTE_BELOW):
    """Print the per-row denominator as a right-hand column in axes coordinates.

    Every figure that summarises groups carries this. Without it a box built from one
    observation is indistinguishable from one built from a thousand.
    """
    for i, c in enumerate(counts):
        ax.text(x, i, fmt.format(c), transform=ax.get_yaxis_transform(),
                va="center", ha="left", fontsize=6.4,
                color=INK_1 if c >= below else MUTED, clip_on=False)
    ax.text(x, 1.0, header, transform=ax.transAxes, va="bottom", ha="left",
            fontsize=6.2, color=MUTED, clip_on=False)


def divider(axes, cut):
    """Hairline separating well-evidenced rows from thin ones."""
    for ax in axes:
        ax.axhline(cut - 0.5, color=GRID, lw=0.7, zorder=1)


# ---------------------------------------------------------------------------------------
# The single research-workflow-stage vocabulary used throughout the paper.
#
# These 15 stages tag 2,199 of 2,200 repositories and are the sole workflow vocabulary
# used in the current figures.
#
# Stages are listed in LIFECYCLE order inside each phase, and the phases in lifecycle
# order, so any figure that iterates this structure is ordered by the research process
# rather than by frequency. "Outputs" is the former "Communication" phase, renamed to
# avoid colliding with the communication_dissemination stage that now sits under
# Research-support.
PHASES = [
    ("Ideation & design", ["ideation_formulation", "study_design", "literature_review"]),
    ("Execution", ["data_collection_preparation", "exploratory_data_analysis", "data_analysis"]),
    ("Outputs", ["visualization", "writing_documentation"]),
    ("Review & QA", ["submission_peer_review", "replication_reproducibility", "quality_assurance"]),
    ("Research-support & infra.", ["citation_management", "collaboration_project_management",
                                   "communication_dissemination"]),
    ("Governance & ethics", ["ethics_safety"]),
]
STAGES = [s for _, ss in PHASES for s in ss]
STAGE_PHASE = {s: p for p, ss in PHASES for s in ss}

STAGE_LABEL = {
    "ideation_formulation": "ideation and formulation",
    "study_design": "study design",
    "literature_review": "literature review",
    "data_collection_preparation": "data collection and preparation",
    "exploratory_data_analysis": "exploratory data analysis",
    "data_analysis": "data analysis",
    "visualization": "visualization",
    "writing_documentation": "writing and documentation",
    "submission_peer_review": "submission and peer review",
    "replication_reproducibility": "replication and reproducibility",
    "quality_assurance": "quality assurance",
    "citation_management": "citation management",
    "collaboration_project_management": "collaboration and project management",
    "communication_dissemination": "communication and dissemination",
    "ethics_safety": "ethics and safety",
}


def stage_tags(row, field="workflow_stages"):
    """Parse the multi-label stage field, keeping only the 15 canonical stages."""
    raw = row.get(field) or ""
    return [t.strip() for t in raw.replace("[", "").replace("]", "").replace("'", "").split(",")
            if t.strip() in STAGE_PHASE]


# Short tags for the rotated in-figure phase brackets. A rotated label needs about 0.5in
# per 10 characters; "Research-support & infra." spans 0.9in against the 0.66in its three
# rows occupy, so the full names collide. Figures use these; captions spell them out.
PHASE_SHORT = {
    "Ideation & design": "Ideation",
    "Execution": "Execution",
    "Outputs": "Outputs",
    "Review & QA": "Review",
    "Research-support & infra.": "Support",
    "Governance & ethics": "Ethics",
}
