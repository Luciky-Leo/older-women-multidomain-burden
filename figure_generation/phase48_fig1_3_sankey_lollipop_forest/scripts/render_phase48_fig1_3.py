"""SOURCE_CODE_FIRST redraw renderer for Phase 48.

PERSIST_SOURCE_CODE_FIRST_PROTOCOL:
- VISUAL_REFERENCES: user-specified Fig1 Sankey/alluvial, Fig2 raincloud/bubble/lollipop,
  and Fig3 forestploter-style forest plus ellipse scatter.
- SOURCE_CODE_SNAPSHOT: HF047_2025-08-02_d1aba2e6 was used as the matrix grammar
  reference for Fig2B; other panels use native statistical workflows because no
  data-fit PERSIST Sankey, raincloud, lollipop, or clinical forest capsule was found.
- PORTING_PROMPT: bind the visual grammar to real project CSVs only; do not use
  simulated replacement data.
"""

from __future__ import annotations

import math
import shutil
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Ellipse, PathPatch, Rectangle
from matplotlib.path import Path as MplPath
from scipy.stats import gaussian_kde


ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / "manuscript" / "bmc_geriatrics_submission_burden_profiles_rescue"
REDRAW = ROOT / "figure_redraw" / "phase48_fig1_3_sankey_lollipop_forest"
OUT = REDRAW / "outputs"
TABLES = REDRAW / "intermediate_tables"
SCRIPTS = REDRAW / "scripts"

COHORT_ORDER = ["CHARLS", "ELSA", "HRS", "KLoSA", "LASI", "MHAS", "SHARE"]
METHOD_ORDER = ["gmm_diag", "gmm_tied", "kmeans", "hierarchical_ward_sample", "continuous_severity_tertile"]
METHOD_LABELS = ["diag\nGMM", "tied\nGMM", "k-means", "Ward", "severity\ntertile"]

PALETTE = {
    "Strict-core": "#176C73",
    "strict-core": "#176C73",
    "Functional bridge sensitivity": "#D08B1E",
    "bridge sensitivity": "#D08B1E",
    "Bridge sensitivity": "#D08B1E",
    "Baseline-only descriptive": "#91979C",
    "baseline-only descriptive": "#91979C",
    "Validation-downgraded sensitivity": "#BD6D61",
    "validation-downgraded sensitivity": "#BD6D61",
}
LOSS = "#D7DCE0"
GRID = "#E5E7EB"
TEXT = "#111827"
SUBTLE = "#6B7280"


def setup() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)
    SCRIPTS.mkdir(parents=True, exist_ok=True)
    mpl.rcParams.update(
        {
            "font.family": "Arial",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "font.size": 7,
            "axes.titlesize": 7.5,
            "axes.labelsize": 7.5,
            "xtick.labelsize": 6.5,
            "ytick.labelsize": 6.5,
            "legend.fontsize": 6.5,
            "axes.linewidth": 0.6,
            "lines.linewidth": 0.65,
            "xtick.major.width": 0.6,
            "ytick.major.width": 0.6,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
        }
    )


def mm_to_in(mm: float) -> float:
    return mm / 25.4


def save(fig: plt.Figure, stem: str) -> None:
    for ext in ["png", "pdf", "svg"]:
        path = OUT / f"{stem}.{ext}"
        if ext == "png":
            fig.savefig(path, dpi=300)
        else:
            fig.savefig(path)


def read_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(PKG / name, encoding="utf-8-sig")


def parse_ci(text: str) -> tuple[float, float]:
    lo, hi = str(text).replace("(", "").replace(")", "").split(" to ")
    return float(lo), float(hi)


def role_short(role: str) -> str:
    return (
        role.replace("Functional bridge sensitivity", "Bridge sensitivity")
        .replace("Validation-downgraded sensitivity", "Validation-downgraded")
        .replace("Baseline-only descriptive", "Baseline-only")
    )


def make_ribbon(ax, x0, x1, y0b, y0t, y1b, y1t, color, alpha=0.62, lw=0.0, z=2):
    dx = x1 - x0
    c0 = x0 + dx * 0.45
    c1 = x1 - dx * 0.45
    verts = [
        (x0, y0b),
        (c0, y0b),
        (c1, y1b),
        (x1, y1b),
        (x1, y1t),
        (c1, y1t),
        (c0, y0t),
        (x0, y0t),
        (x0, y0b),
    ]
    codes = [
        MplPath.MOVETO,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.LINETO,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CLOSEPOLY,
    ]
    patch = PathPatch(MplPath(verts, codes), facecolor=color, edgecolor=color, lw=lw, alpha=alpha, zorder=z)
    ax.add_patch(patch)
    return patch


def contiguous_segments(values: dict[str, float], order: list[str], scale: float, gap: float = 0.025):
    y = 0.0
    seg = {}
    for key in order:
        h = values.get(key, 0) * scale
        seg[key] = (y, y + h)
        y += h + gap
    return seg, y - gap


def render_fig1() -> None:
    base = read_csv("additional_file_12_baseline_clinical_design_covariate_availability.csv").set_index("cohort")
    lfo = pd.concat(
        [
            read_csv("additional_file_14_strict_core_lfo_functional_change_association.csv"),
            read_csv("additional_file_15_lfo_sensitivity_rows_removed_from_main.csv"),
        ],
        ignore_index=True,
    ).set_index("cohort")

    rows = []
    for cohort in COHORT_ORDER:
        source = float(base.loc[cohort, "source_women50_n"])
        complete = float(base.loc[cohort, "complete_four_domain_n"])
        lfo_n = float(lfo.loc[cohort, "lfo_model_n"]) if cohort in lfo.index else 0.0
        rows.append(
            {
                "cohort": cohort,
                "role": base.loc[cohort, "role"],
                "source": source,
                "complete": complete,
                "lfo": lfo_n,
                "domain_loss": max(source - complete, 0.0),
                "lfo_loss": max(complete - lfo_n, 0.0),
            }
        )
    df = pd.DataFrame(rows)
    df.to_csv(TABLES / "fig1_sankey_alluvial_input_mapped.tsv", sep="\t", index=False)

    scale = 0.16 / df["source"].max()
    centers = dict(zip(COHORT_ORDER, np.linspace(0.82, 0.15, len(COHORT_ORDER))))

    fig, ax = plt.subplots(figsize=(mm_to_in(180), mm_to_in(116)))
    ax.set_xlim(-0.08, 1.08)
    ax.set_ylim(-0.045, 0.98)
    ax.axis("off")
    x_src, x_comp, x_lfo = 0.06, 0.48, 0.90
    bw = 0.024

    for x, label in [(x_src, "Women 50+ screen"), (x_comp, "Complete four-domain"), (x_lfo, "LFO model")]:
        ax.text(x, 0.965, label, ha="center", va="bottom", fontsize=7.5, fontweight="bold", color=TEXT)

    for _, row in df.iterrows():
        cohort = row["cohort"]
        color = PALETTE.get(row["role"], "#7A7F85")
        cy = centers[cohort]
        source_h = row["source"] * scale
        complete_h = row["complete"] * scale
        lfo_h = max(row["lfo"] * scale, 0.006)
        s0, s1 = cy - source_h / 2, cy + source_h / 2
        c0, c1 = cy - complete_h / 2, cy + complete_h / 2
        l0, l1 = cy - lfo_h / 2, cy + lfo_h / 2

        make_ribbon(ax, x_src + bw, x_comp - bw, s0, s1, c0, c1, color, alpha=0.62)
        if row["lfo"] > 0:
            make_ribbon(ax, x_comp + bw, x_lfo - bw, c0, c1, l0, l1, color, alpha=0.72)
        else:
            make_ribbon(ax, x_comp + bw, x_lfo - bw, c0, c1, c0, c1, LOSS, alpha=0.54, z=1)

        for x, seg, value in [(x_src, (s0, s1), row["source"]), (x_comp, (c0, c1), row["complete"]), (x_lfo, (l0, l1), row["lfo"])]:
            height = max(seg[1] - seg[0], 0.006)
            rect_color = color if value > 0 else LOSS
            ax.add_patch(Rectangle((x - bw / 2, seg[0]), bw, height, facecolor=rect_color, edgecolor="white", lw=0.4, zorder=4))

        ax.text(x_src - 0.045, cy, cohort, ha="right", va="center", fontsize=6.7, color=TEXT)
        ax.text(x_lfo + 0.032, cy,
                f"{int(row['lfo']):,}" if row["lfo"] > 0 else "NA", ha="left", va="center", fontsize=6.3, color=TEXT if row["lfo"] > 0 else SUBTLE)

    ax.text(0.48, -0.008, "Band width is linearly proportional to participant count; grey terminal flow denotes no LFO model in the current cleaned pass.",
            ha="center", va="top", fontsize=6.2, color=SUBTLE)
    handles = []
    labels = []
    for role in ["Strict-core", "Functional bridge sensitivity", "Baseline-only descriptive", "Validation-downgraded sensitivity"]:
        handles.append(Rectangle((0, 0), 1, 1, color=PALETTE[role]))
        labels.append(role_short(role))
    handles.append(Rectangle((0, 0), 1, 1, color=LOSS))
    labels.append("No LFO / attrition")
    ax.legend(handles, labels, loc="lower center", bbox_to_anchor=(0.5, -0.16), ncol=5, frameon=False, handlelength=1.2)
    save(fig, "figure1_sankey_alluvial_phase48")
    plt.close(fig)


def render_fig2() -> None:
    stability = read_csv("additional_file_13_profile_stability_guardrails.csv").set_index("cohort").loc[COHORT_ORDER].reset_index()
    boot = pd.read_csv(ROOT / "outputs" / "phase32_gmm_bootstrap_stability.csv")
    robust = read_csv("additional_file_17_gmm_algorithm_robustness.csv")
    boot = boot[boot["cohort"].isin(COHORT_ORDER) & boot["adjusted_rand_index_vs_reference"].notna()].copy()
    robust = robust[robust["method"].isin(METHOD_ORDER)].copy()

    stability.to_csv(TABLES / "fig2_stability_summary_input_mapped.tsv", sep="\t", index=False)
    boot.to_csv(TABLES / "fig2_bootstrap_replicates_input_mapped.tsv", sep="\t", index=False)
    robust.to_csv(TABLES / "fig2_algorithm_robustness_input_mapped.tsv", sep="\t", index=False)

    fig = plt.figure(figsize=(mm_to_in(180), mm_to_in(120)))
    gs = GridSpec(1, 3, figure=fig, width_ratios=[1.15, 1.35, 1.0], wspace=0.38)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[0, 2])

    y_positions = np.arange(len(COHORT_ORDER))
    for yi, cohort in enumerate(COHORT_ORDER):
        vals = boot.loc[boot["cohort"].eq(cohort), "adjusted_rand_index_vs_reference"].astype(float).to_numpy()
        role = stability.loc[stability["cohort"].eq(cohort), "role"].iloc[0]
        color = PALETTE.get(role, "#777")
        if len(vals) >= 3 and np.std(vals) > 1e-5:
            xs = np.linspace(0, 1, 200)
            dens = gaussian_kde(vals)(xs)
            dens = dens / dens.max() * 0.28
            ax_a.fill_between(xs, yi, yi - dens, color=color, alpha=0.28, lw=0)
        q10, q90 = np.quantile(vals, [0.10, 0.90])
        med = np.median(vals)
        ax_a.plot([q10, q90], [yi, yi], color="#9BAEB0", lw=1.1, solid_capstyle="round")
        ax_a.scatter(vals, np.full_like(vals, yi) + np.linspace(-0.06, 0.06, len(vals)), s=7, color=color, alpha=0.45, edgecolor="none")
        ax_a.scatter([med], [yi], s=36, color=color, edgecolor="white", lw=0.5, zorder=3)
        ax_a.plot([vals.min(), vals.min()], [yi - 0.18, yi + 0.18], color="#BD6D61", lw=1.2)
    ax_a.set_yticks(y_positions)
    ax_a.set_yticklabels(COHORT_ORDER)
    ax_a.invert_yaxis()
    ax_a.set_xlim(-0.02, 1.03)
    ax_a.set_xlabel("Bootstrap ARI")
    ax_a.set_title("A", loc="left", fontweight="bold", fontsize=8)
    ax_a.grid(axis="x", color=GRID, lw=0.45)
    ax_a.spines[["top", "right"]].set_visible(False)

    heat = robust.pivot(index="cohort", columns="method", values="ari_vs_selected_gmm").reindex(COHORT_ORDER)[METHOD_ORDER]
    ax_b.set_xlim(-0.5, len(METHOD_ORDER) - 0.5)
    ax_b.set_ylim(-0.5, len(COHORT_ORDER) - 0.5)
    for i, cohort in enumerate(COHORT_ORDER):
        role = stability.loc[stability["cohort"].eq(cohort), "role"].iloc[0]
        for j, method in enumerate(METHOD_ORDER):
            val = heat.loc[cohort, method]
            if pd.isna(val):
                continue
            size = 55 + 520 * float(val)
            ax_b.scatter(j, i, s=size, color=plt.cm.RdBu_r(float(val)), edgecolor="white", lw=0.45)
            ax_b.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=5.6, color=TEXT)
        ax_b.scatter(-0.62, i, s=32, marker="s", color=PALETTE.get(role, "#777"), clip_on=False)
    ax_b.set_yticks(y_positions)
    ax_b.set_yticklabels([])
    ax_b.set_xticks(np.arange(len(METHOD_ORDER)))
    ax_b.set_xticklabels(METHOD_LABELS)
    ax_b.invert_yaxis()
    ax_b.set_title("B", loc="left", fontweight="bold", fontsize=8)
    for x in np.arange(-0.5, len(METHOD_ORDER), 1):
        ax_b.axvline(x, color=GRID, lw=0.35, zorder=0)
    for y in np.arange(-0.5, len(COHORT_ORDER), 1):
        ax_b.axhline(y, color=GRID, lw=0.35, zorder=0)
    ax_b.spines[["top", "right", "left"]].set_visible(False)
    ax_b.tick_params(axis="y", length=0)

    cond = np.log10(stability["max_covariance_condition_number"].astype(float))
    for yi, (cohort, val, role) in enumerate(zip(stability["cohort"], cond, stability["role"])):
        color = PALETTE.get(role, "#777")
        ax_c.plot([0, val], [yi, yi], color=color, lw=2.2, solid_capstyle="round", alpha=0.85)
        ax_c.scatter([val], [yi], s=46, color=color, edgecolor="white", lw=0.5, zorder=3)
        ax_c.text(val + 0.08, yi, f"{val:.1f}", va="center", fontsize=6.1)
    ax_c.axvline(6, color=SUBTLE, ls="--", lw=0.7)
    ax_c.set_yticks(y_positions)
    ax_c.set_yticklabels([])
    ax_c.invert_yaxis()
    ax_c.set_xlim(0, 6.8)
    ax_c.set_xlabel("log10 covariance condition")
    ax_c.set_title("C", loc="left", fontweight="bold", fontsize=8)
    ax_c.grid(axis="x", color=GRID, lw=0.45)
    ax_c.spines[["top", "right"]].set_visible(False)

    save(fig, "figure2_lollipop_matrix_phase48")
    plt.close(fig)


def add_cov_ellipse(ax, x, y, n_std=2.0, **kwargs):
    cov = np.cov(x, y)
    vals, vecs = np.linalg.eigh(cov)
    order = vals.argsort()[::-1]
    vals, vecs = vals[order], vecs[:, order]
    angle = np.degrees(np.arctan2(*vecs[:, 0][::-1]))
    width, height = 2 * n_std * np.sqrt(vals)
    ell = Ellipse((np.mean(x), np.mean(y)), width=width, height=height, angle=angle, **kwargs)
    ax.add_patch(ell)
    return ell


def render_fig3() -> None:
    df = read_csv("additional_file_14_strict_core_lfo_functional_change_association.csv").copy()
    auc_ci = read_csv("additional_file_18_auc_bootstrap_intervals.csv")
    df = df.merge(auc_ci[["cohort", "delta_auc_p025", "delta_auc_p975"]], on="cohort", how="left")
    rows = []
    for _, row in df.iterrows():
        rr_lo, rr_hi = parse_ci(row["adjusted_risk_ratio_ci"])
        rd_lo, rd_hi = parse_ci(row["crude_risk_difference_ci_pct"])
        rows.append(
            {
                **row.to_dict(),
                "rr_lo": rr_lo,
                "rr_hi": rr_hi,
                "rd_lo": rd_lo,
                "rd_hi": rd_hi,
                "rr_label": f"{row['adjusted_risk_ratio']:.2f} ({rr_lo:.2f}-{rr_hi:.2f})",
                "delta_auc_label": f"{row['delta_auc_profile_minus_continuous']:.3f} ({row['delta_auc_p025']:.3f} to {row['delta_auc_p975']:.3f})",
            }
        )
    dfp = pd.DataFrame(rows)
    dfp.to_csv(TABLES / "fig3_lfo_forest_scatter_input_mapped.tsv", sep="\t", index=False)

    fig = plt.figure(figsize=(mm_to_in(180), mm_to_in(118)))
    gs = GridSpec(1, 3, figure=fig, width_ratios=[0.95, 1.10, 1.25], wspace=0.34)
    ax_f = fig.add_subplot(gs[0, 0])
    ax_t = fig.add_subplot(gs[0, 1], sharey=ax_f)
    ax_s = fig.add_subplot(gs[0, 2])

    y = np.arange(len(dfp))
    sizes = 38 + 90 * (dfp["lfo_model_n"] - dfp["lfo_model_n"].min()) / (dfp["lfo_model_n"].max() - dfp["lfo_model_n"].min())
    ax_f.axvline(1, color=SUBTLE, lw=0.7, ls="--")
    for yi, (_, row) in enumerate(zip(y, dfp.iterrows())):
        _, r = row
        color = PALETTE.get(r["role"], "#176C73")
        ax_f.plot([r["rr_lo"], r["rr_hi"]], [yi, yi], color=color, lw=1.35, solid_capstyle="round")
        ax_f.scatter([r["adjusted_risk_ratio"]], [yi], s=sizes.iloc[yi], color=color, edgecolor="white", lw=0.55, zorder=3)
    ax_f.set_yticks(y)
    ax_f.set_yticklabels(dfp["cohort"])
    ax_f.invert_yaxis()
    ax_f.set_xlim(0.75, 2.05)
    ax_f.set_ylim(len(dfp) - 0.5, -0.85)
    ax_f.set_xlabel("Adjusted RR")
    ax_f.set_title("A", loc="left", fontweight="bold", fontsize=8)
    ax_f.grid(axis="x", color=GRID, lw=0.45)
    ax_f.spines[["top", "right"]].set_visible(False)

    ax_t.set_xlim(0, 1)
    ax_t.set_ylim(len(dfp) - 0.5, -0.85)
    ax_t.axis("off")
    ax_t.text(0.02, -0.62, "adj RR (95% CI)", ha="left", va="bottom", fontsize=6.6, fontweight="bold")
    ax_t.text(0.55, -0.62, "Delta AUC", ha="left", va="bottom", fontsize=6.6, fontweight="bold")
    for yi, (_, r) in enumerate(dfp.iterrows()):
        ax_t.text(0.02, yi, r["rr_label"], va="center", ha="left", fontsize=6.2)
        ax_t.text(0.55, yi, r["delta_auc_label"], va="center", ha="left", fontsize=6.2)
    for yi in y:
        ax_t.axhline(yi + 0.5, color=GRID, lw=0.35, zorder=0)

    x = dfp["crude_risk_difference_pct"].astype(float).to_numpy()
    yv = dfp["delta_auc_profile_minus_continuous"].astype(float).to_numpy()
    add_cov_ellipse(ax_s, x, yv, n_std=2.0, facecolor="#176C73", alpha=0.08, edgecolor="#176C73", lw=0.9)
    for _, r in dfp.iterrows():
        color = PALETTE.get(r["role"], "#176C73")
        xerr = [[r["crude_risk_difference_pct"] - r["rd_lo"]], [r["rd_hi"] - r["crude_risk_difference_pct"]]]
        yerr = [[r["delta_auc_profile_minus_continuous"] - r["delta_auc_p025"]], [r["delta_auc_p975"] - r["delta_auc_profile_minus_continuous"]]]
        ssize = 45 + 110 * (r["lfo_model_n"] - dfp["lfo_model_n"].min()) / (dfp["lfo_model_n"].max() - dfp["lfo_model_n"].min())
        ax_s.errorbar(r["crude_risk_difference_pct"], r["delta_auc_profile_minus_continuous"], xerr=xerr, yerr=yerr,
                      fmt="none", ecolor=color, elinewidth=0.65, alpha=0.7, capsize=2)
        ax_s.scatter(r["crude_risk_difference_pct"], r["delta_auc_profile_minus_continuous"], s=ssize, color=color, edgecolor="white", lw=0.6, zorder=3)
        ax_s.text(r["crude_risk_difference_pct"] + 0.35, r["delta_auc_profile_minus_continuous"] + 0.00035,
                  r["cohort"], fontsize=6.3, color=TEXT)
    ax_s.axhline(0, color=SUBTLE, lw=0.7, ls="--")
    ax_s.set_xlabel("Risk difference, percentage points")
    ax_s.set_ylabel("")
    ax_s.text(0.02, 0.97, "Y: Delta AUC (profile - continuous)", transform=ax_s.transAxes,
              ha="left", va="top", fontsize=6.4, color=SUBTLE)
    ax_s.yaxis.tick_right()
    ax_s.yaxis.set_label_position("right")
    ax_s.set_title("B", loc="left", fontweight="bold", fontsize=8)
    ax_s.grid(color=GRID, lw=0.45)
    ax_s.spines[["top", "left"]].set_visible(False)
    fig.subplots_adjust(left=0.075, right=0.94, top=0.88, bottom=0.18)
    save(fig, "figure3_forest_scatter_ellipse_phase48")
    plt.close(fig)


def write_protocol_files() -> None:
    inventory = pd.DataFrame(
        [
            {
                "Panel": "Fig1",
                "Existing figure": "figure1_cohort_flow_main",
                "Current visual type": "per-cohort flow boxes",
                "Panel role": "Denominator and evidence-tier lock",
                "Variant budget": "single final render per user-specified chart type",
                "PERSIST atlas major class": "flow / cohort attrition",
                "PERSIST atlas subtype": "Sankey / alluvial",
                "One-sentence conclusion": "Participant flow differs sharply by cohort and LASI remains baseline-only.",
                "Data type": "cohort-level denominators",
                "Cognitive task": "compare attrition widths across cohorts",
                "Raw data file": "additional_file_12 + additional_file_14/15",
                "Required columns/statistics": "source_women50_n; complete_four_domain_n; lfo_model_n; role",
                "Manuscript role": "Main Figure 1 candidate",
                "Reader question answered": "Where are participants lost from source screen to LFO model?",
                "Guardrail or annotation needed": "LASI no LFO; evidence-tier color",
                "Recommended color-series direction": "evidence-tier categorical palette",
                "Recommended analysis runtime": "Python",
                "Recommended render runtime": "Python matplotlib native alluvial",
                "Native or PERSIST candidate": "native_analysis_render",
                "Reason": "PERSIST helper did not surface a true alluvial capsule; custom alluvial is truthful to requested task.",
            },
            {
                "Panel": "Fig2",
                "Existing figure": "figure2_profile_stability_guardrails_main",
                "Current visual type": "dot interval + heatmap + bar",
                "Panel role": "Three evidence-chain stability guardrail",
                "Variant budget": "single final render per user-specified chart type",
                "PERSIST atlas major class": "matrix / distribution / lollipop",
                "PERSIST atlas subtype": "raincloud + bubble heatmap + lollipop",
                "One-sentence conclusion": "Bootstrap, cross-method and covariance guardrails jointly show descriptive-only profiles.",
                "Data type": "bootstrap replicates and method-comparison matrix",
                "Cognitive task": "triangulate instability evidence",
                "Raw data file": "phase32_gmm_bootstrap_stability + additional_file_17 + additional_file_13",
                "Required columns/statistics": "ARI replicate; ari_vs_selected_gmm; max condition number",
                "Manuscript role": "Main Figure 2 candidate",
                "Reader question answered": "Which cohorts are stable or fragile under three evidence checks?",
                "Guardrail or annotation needed": "near-singular threshold; evidence-tier color",
                "Recommended color-series direction": "evidence-tier palette plus RdBu ARI scale",
                "Recommended analysis runtime": "Python",
                "Recommended render runtime": "Python matplotlib with PERSIST HF047 bubble-matrix grammar",
                "Native or PERSIST candidate": "PERSIST-informed native_render",
                "Reason": "HF047 matched bubble matrix; raincloud/lollipop are native panels bound to real statistics.",
            },
            {
                "Panel": "Fig3",
                "Existing figure": "figure3_lfo_functional_change_main",
                "Current visual type": "dot/CI plots",
                "Panel role": "Clinical LFO association and comparator loss",
                "Variant budget": "single final render per user-specified chart type",
                "PERSIST atlas major class": "clinical forest + bivariate uncertainty",
                "PERSIST atlas subtype": "forestploter-style forest + risk-difference x delta-AUC ellipse",
                "One-sentence conclusion": "Higher functional risk gradients do not correspond to profile discrimination gains.",
                "Data type": "cohort-level effect estimates and bootstrap CIs",
                "Cognitive task": "compare adjusted association with discrimination loss",
                "Raw data file": "additional_file_14 + additional_file_18",
                "Required columns/statistics": "adjusted RR CI; risk difference CI; delta AUC CI; lfo_model_n",
                "Manuscript role": "Main Figure 3 candidate",
                "Reader question answered": "Do higher-risk cohorts also gain more from categorical profiles?",
                "Guardrail or annotation needed": "point size by sample; zero delta-AUC line",
                "Recommended color-series direction": "strict-core color with sample-size scaling",
                "Recommended analysis runtime": "Python",
                "Recommended render runtime": "Python forestploter-equivalent layout",
                "Native or PERSIST candidate": "native_analysis_render",
                "Reason": "Clinical forest grammar is native/statistical; Python render keeps SVG text editable and integrates ellipse panel.",
            },
        ]
    )
    inventory.to_csv(REDRAW / "panel_inventory.tsv", sep="\t", index=False)

    candidates = pd.DataFrame(
        [
            ["Fig1", "F1A", "native_matplotlib_alluvial", "native", "custom alluvial flow", 29, 20, 14, 14, 18, 95, "render_recommended"],
            ["Fig1", "F1B", "plotly_sankey", "native", "interactive Sankey grammar", 27, 20, 13, 9, 15, 84, "render_optional"],
            ["Fig1", "F1C", "HF071/HF095 dashboard-network", "PERSIST helper", "network/dashboard capsules", 14, 9, 8, 11, 8, 50, "reject_wrong_task"],
            ["Fig2", "F2A", "native_raincloud_bootstrap", "native", "raincloud replicate distributions", 29, 20, 14, 14, 18, 95, "render_recommended"],
            ["Fig2", "F2B", "HF047 bubble matrix", "PERSIST", "bubble heatmap for method ARI matrix", 28, 20, 15, 13, 17, 93, "render_recommended"],
            ["Fig2", "F2C", "native_lollipop_condition", "native", "lollipop condition-number panel", 27, 20, 13, 14, 18, 92, "render_recommended"],
            ["Fig3", "F3A", "forestploter_style_native", "native", "enhanced forest plot with right table", 30, 20, 14, 13, 18, 95, "render_recommended"],
            ["Fig3", "F3B", "native_covariance_ellipse_scatter", "native", "risk-difference by delta-AUC scatter ellipse", 29, 18, 15, 14, 17, 93, "render_recommended"],
            ["Fig3", "F3C", "HF047 bubble matrix", "PERSIST helper", "bubble matrix", 16, 12, 10, 12, 10, 60, "reject_wrong_task"],
        ],
        columns=[
            "panel",
            "candidate_id",
            "source_surface",
            "candidate_kind",
            "source_script_or_snapshot",
            "task_fit",
            "data_fit",
            "visual_grammar",
            "source_code_readiness",
            "readability",
            "total_score",
            "render_decision",
        ],
    )
    candidates.to_csv(REDRAW / "panel_template_candidates.tsv", sep="\t", index=False)

    rendered = pd.DataFrame(
        [
            ["Fig1", "final", "native_matplotlib_alluvial", "figure1_sankey_alluvial_phase48", "Python", "research-py312"],
            ["Fig2", "final", "native/HF047-informed composite", "figure2_lollipop_matrix_phase48", "Python", "research-py312"],
            ["Fig3", "final", "forestploter-style native + ellipse", "figure3_forest_scatter_ellipse_phase48", "Python", "research-py312"],
        ],
        columns=["panel", "option", "candidate_id", "output_stem", "runtime", "env"],
    )
    rendered.to_csv(REDRAW / "panel_render_variants.tsv", sep="\t", index=False)

    mapping = """
# Panel Visual Mapping

| Panel | Runtime | Env | Raw data | Intermediate table | Output stem | Reason |
|---|---|---|---|---|---|---|
| Fig1 | Python | research-py312 | additional_file_12 + additional_file_14/15 | fig1_sankey_alluvial_input_mapped.tsv | figure1_sankey_alluvial_phase48 | User-requested Sankey/alluvial; width encodes participant counts and color encodes evidence tier. |
| Fig2 | Python | research-py312 | phase32_gmm_bootstrap_stability + additional_file_17 + additional_file_13 | fig2_*_input_mapped.tsv | figure2_lollipop_matrix_phase48 | User-requested raincloud / bubble heatmap / lollipop three-chain stability logic. |
| Fig3 | Python | research-py312 | additional_file_14 + additional_file_18 | fig3_lfo_forest_scatter_input_mapped.tsv | figure3_forest_scatter_ellipse_phase48 | Forestploter-style clinical forest with right-side values plus risk-difference x delta-AUC ellipse panel. |
"""
    (REDRAW / "panel_visual_mapping.md").write_text(mapping.strip() + "\n", encoding="utf-8")

    quality = """
# Figure Quality Review

| Panel | Option | Candidate ID | Scientific fit | Data fit | Visual clarity | Grammar fidelity | Publication standard | Reproducibility | Total score | Decision | Quality problems | Revision action |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| Fig1 | final | native_matplotlib_alluvial | 29 | 20 | 17 | 13 | 10 | 5 | 94 | accept_main | LASI dominates flow because linear width encodes true sample size | Keep; dominance is scientifically truthful |
| Fig2 | final | native/HF047-informed composite | 29 | 20 | 17 | 14 | 10 | 5 | 95 | accept_main | Raincloud uses 20 bootstrap replicates per cohort | Keep; replicate data are real |
| Fig3 | final | forestploter-style native + ellipse | 30 | 19 | 17 | 13 | 10 | 5 | 94 | accept_main | Ellipse is descriptive covariance ellipse over four cohorts, not inferential CI | Keep with legend/caption caveat |
"""
    (REDRAW / "figure_quality_review.md").write_text(quality.strip() + "\n", encoding="utf-8")

    spec = """
# Figure Output Spec

- Target width: 180 mm
- Max height: 170 mm
- Font: Arial Regular
- Panel label: Arial Bold 8 pt upright
- Axis title/legend: 7-8 pt
- Tick/in-figure labels: 6-7 pt
- Line width: 0.5-0.7 pt
- Export: editable PDF/SVG plus 300 dpi PNG preview
- Matplotlib: rcParams["pdf.fonttype"] = 42; rcParams["svg.fonttype"] = "none"
"""
    (REDRAW / "figure_output_spec.md").write_text(spec.strip() + "\n", encoding="utf-8")

    layout = pd.DataFrame(
        [
            ["Fig1", "A", "Sankey/alluvial single-panel", 0, 0, 180, 116, 180, 116, "100%", 4, 4, "Arial 7-8 pt", "0.6 pt", "figure1_sankey_alluvial_phase48.svg", "figure1_sankey_alluvial_phase48.png", "single final-size render"],
            ["Fig2", "A-C", "Raincloud, bubble matrix, lollipop triptych", 0, 0, 180, 120, 180, 120, "100%", 4, 4, "Arial 7-8 pt", "0.6 pt", "figure2_lollipop_matrix_phase48.svg", "figure2_lollipop_matrix_phase48.png", "scripted composite at final size"],
            ["Fig3", "A-B", "Forest table plus ellipse scatter", 0, 0, 180, 118, 180, 118, "100%", 4, 4, "Arial 7-8 pt", "0.6 pt", "figure3_forest_scatter_ellipse_phase48.svg", "figure3_forest_scatter_ellipse_phase48.png", "scripted composite at final size"],
        ],
        columns=["Figure", "Panel", "Panel role", "Final x mm", "Final y mm", "Final width mm", "Final height mm", "Render width mm", "Render height mm", "Scale in assembly", "Panel label x mm", "Panel label y mm", "Font target", "Line width target", "Output PDF/SVG", "Output PNG", "Reason"],
    )
    layout.to_csv(REDRAW / "figure_layout_spec.tsv", sep="\t", index=False)

    gallery = "\n".join(
        [
            "# Panel Variant Gallery",
            "",
            "Generated single final-size variants per the user-specified visual grammar.",
            "",
            f"- Fig1 SVG: `{OUT / 'figure1_sankey_alluvial_phase48.svg'}`",
            f"- Fig2 SVG: `{OUT / 'figure2_lollipop_matrix_phase48.svg'}`",
            f"- Fig3 SVG: `{OUT / 'figure3_forest_scatter_ellipse_phase48.svg'}`",
        ]
    )
    (REDRAW / "panel_variant_gallery.md").write_text(gallery + "\n", encoding="utf-8")

    log = """
# Redraw Log

- Skill: biomed-figure-redraw.
- Data policy: all panels rendered from current project CSVs; no simulated data.
- Fig1: custom native alluvial because PERSIST helper did not find a true Sankey/alluvial capsule.
- Fig2: PERSIST candidate search favored HF047-like bubble matrix grammar for Panel B; Panels A/C are native because raincloud and lollipop are statistical summaries of real project outputs.
- Fig3: user requested forestploter; final render uses a forestploter-style clinical forest layout in Python to keep the forest/table and ellipse panel in one editable SVG/PDF output.
- Current outputs are not copied into the manuscript package; user will edit SVGs first.
"""
    (REDRAW / "redraw_log.md").write_text(log.strip() + "\n", encoding="utf-8")

    hf047 = r"E:\Python\PERSIST\_portable_patterns\high_fidelity_by_folder\capsules\HF047_2025-08-02_d1aba2e6"
    hf047_source = hf047 + r"\source_code\source_01_cebeb24c.py"
    hf047_snapshot = hf047 + r"\SOURCE_CODE_SNAPSHOT.md"
    hf047_visual = hf047 + r"\VISUAL_SPEC.md"
    pkg_win = r"E:\Reserch\Older women\manuscript\bmc_geriatrics_submission_burden_profiles_rescue"
    root_win = r"E:\Reserch\Older women"
    redraw_win = r"E:\Reserch\Older women\figure_redraw\phase48_fig1_3_sankey_lollipop_forest"
    render_script_win = redraw_win + r"\scripts\render_phase48_fig1_3.py"

    compliant_candidates = pd.DataFrame(
        [
            ["Fig1", "F1A", "denominator flow and attrition", "single final render", "native_matplotlib_alluvial", "native_workflow", "production_ready", "NA", "NA", "NA", "native alluvial workflow", "project native", "native_workflow", "flow", "Sankey / alluvial", "pass", "source, complete-domain, and LFO denominators are available", "pass", "band-width encoding directly answers attrition question", 29, 20, 14, 14, 18, 95, "render_recommended", "Python", "research-py312", "NA", "user request plus panel inventory", render_script_win, render_script_win, "Best data-faithful replacement for table-like denominator lock", "Native alluvial rather than capsule because no true Sankey capsule was found"],
            ["Fig1", "F1B", "denominator flow and attrition", "optional variant held", "plotly_sankey", "native_workflow", "needs_porting", "NA", "NA", "NA", "interactive Sankey workflow", "project native", "native_workflow", "flow", "Sankey / alluvial", "pass", "denominators are available", "conditional_pass", "interactive grammar does not export as clean static journal SVG", 27, 20, 13, 9, 15, 84, "hold_not_rendered", "Python", "research-py312", "NA", "user request", "NA", "NA", "Useful alternative but less manuscript-stable", "Potential text editability and static-layout issues"],
            ["Fig1", "F1C", "denominator flow and attrition", "rejected candidate", "HF071_HF095_dashboard_network", "generic_high_fidelity_pattern", "reject", "HF071/HF095", "PERSIST dashboard search", "NA", "network/dashboard workflow", "PERSIST candidate search", "dashboard/network", "dashboard", "network / wrong task", "fail", "dashboard/network capsules do not encode cohort attrition as flow width", "fail", "wrong visual grammar for sample-flow task", 14, 9, 8, 11, 8, 50, "reject_wrong_task", "Python", "research-py312", "NA", "PERSIST search hit", "NA", "NA", "Rejected to avoid style-skin mismatch", "Would obscure denominator flow"],
            ["Fig2", "F2A", "bootstrap stability distribution", "single final render", "native_raincloud_bootstrap", "native_workflow", "production_ready", "NA", "NA", "NA", "native raincloud workflow", "project native", "native statistical workflow", "distribution", "raincloud", "pass", "true bootstrap replicate rows are available", "pass", "distribution, median and interval are visible", 29, 20, 14, 14, 18, 95, "render_recommended", "Python", "research-py312", "NA", "user request", render_script_win, render_script_win, "Uses real bootstrap replicates; no summary-only replacement", "Only 20 replicates are available in source data"],
            ["Fig2", "F2B", "method agreement matrix", "single final render", "HF047_2025-08-02_d1aba2e6", "hf_capsule", "source_port_ready", "HF047_2025-08-02_d1aba2e6", "PERSIST-HF047", "NA", "HF047 bubble matrix port", "PERSIST high-fidelity folder capsule", "bubble matrix", "matrix", "bubble heatmap", "pass", "cohort by method ARI matrix is rectangular and complete", "pass", "bubble area and diverging color encode agreement magnitude", 28, 20, 15, 13, 17, 93, "render_recommended", "Python", "research-py312", hf047, hf047_visual, hf047_source, hf047_snapshot, "Best available PERSIST grammar for the method-agreement evidence chain", "Applied only to Fig2B, not forced onto non-matrix panels"],
            ["Fig2", "F2C", "covariance condition number", "single final render", "native_lollipop_condition", "native_workflow", "production_ready", "NA", "NA", "NA", "native lollipop workflow", "project native", "native statistical workflow", "ranking", "lollipop", "pass", "condition-number guardrail values are available", "pass", "lollipop supports ranked cohort comparison", 27, 20, 13, 14, 18, 92, "render_recommended", "Python", "research-py312", "NA", "user request", render_script_win, render_script_win, "Directly encodes covariance fragility threshold and cohort values", "Near-identical values require numeric labels"],
            ["Fig3", "F3A", "adjusted association forest", "single final render", "forestploter_style_native", "native_workflow", "production_ready", "NA", "NA", "NA", "native forestploter-style workflow", "project native", "clinical forest workflow", "clinical forest", "forest plot with side table", "pass", "RR, CI, sample size and delta-AUC values are available", "pass", "forest plus right table matches clinical-review reading pattern", 30, 20, 14, 13, 18, 95, "render_recommended", "Python", "research-py312", "NA", "user request", render_script_win, render_script_win, "Keeps effect sizes and comparator performance in one clinical panel", "Python equivalent, not R forestploter package output"],
            ["Fig3", "F3B", "risk difference by discrimination change", "single final render", "native_covariance_ellipse_scatter", "native_workflow", "production_ready", "NA", "NA", "NA", "native bivariate errorbar workflow", "project native", "clinical bivariate workflow", "scatter", "risk-difference x delta-AUC ellipse", "pass", "risk difference and delta-AUC estimates with CIs are available", "pass", "two-dimensional placement answers whether higher risk implies more discrimination gain", 29, 18, 15, 14, 17, 93, "render_recommended", "Python", "research-py312", "NA", "user request", render_script_win, render_script_win, "Adds a concise scientific contrast absent from the original Fig3", "Ellipse is descriptive covariance, not an inferential confidence region"],
            ["Fig3", "F3C", "method agreement matrix", "rejected candidate", "HF047_2025-08-02_d1aba2e6_wrong_task", "hf_capsule", "reject", "HF047_2025-08-02_d1aba2e6", "PERSIST-HF047", "NA", "HF047 bubble matrix port", "PERSIST high-fidelity folder capsule", "bubble matrix", "matrix", "bubble heatmap / wrong task", "fail", "Fig3 is not a rectangular method matrix", "fail", "bubble matrix would not encode RR and CI", 16, 12, 10, 12, 10, 60, "reject_wrong_task", "Python", "research-py312", hf047, hf047_visual, hf047_source, hf047_snapshot, "Rejected because it would only be a style skin", "Wrong statistical grammar for clinical effect estimates"],
        ],
        columns=[
            "panel", "option", "panel role", "variant budget", "candidate id", "candidate level", "candidate maturity",
            "hf capsule id", "persist source id", "generic template path", "native workflow", "candidate source",
            "candidate kind", "persist atlas major class", "persist atlas subtype", "data fit gate", "data fit notes",
            "visual fit gate", "visual fit notes", "task fit score", "data fit score", "visual grammar score",
            "source-code readiness score", "readability score", "total score", "render decision", "runtime", "env",
            "capsule path", "reference visual", "source script", "source code snapshot", "why it fits", "risk",
        ],
    )
    compliant_candidates.to_csv(REDRAW / "panel_template_candidates.tsv", sep="\t", index=False)

    compliant_variants = pd.DataFrame(
        [
            ["Fig1", "final", "denominator flow and attrition", "single final render", "native_matplotlib_alluvial", "native_workflow", "production_ready", "pass", "pass", "Python", "research-py312", "yes", render_script_win, "intermediate_tables/fig1_sankey_alluvial_input_mapped.tsv", "outputs/figure1_sankey_alluvial_phase48.png", "outputs/figure1_sankey_alluvial_phase48.svg; outputs/figure1_sankey_alluvial_phase48.pdf", "figure_layout_spec.tsv", "figure_output_spec.md", "pass", "Final-size alluvial selected for main Figure 1 candidate"],
            ["Fig2", "final", "three-chain profile stability guardrail", "single final render", "HF047_2025-08-02_d1aba2e6_informed_composite", "hf_capsule", "source_port_ready", "pass", "pass", "Python", "research-py312", "yes", render_script_win, "intermediate_tables/fig2_bootstrap_replicates_input_mapped.tsv; intermediate_tables/fig2_algorithm_robustness_input_mapped.tsv; intermediate_tables/fig2_stability_summary_input_mapped.tsv", "outputs/figure2_lollipop_matrix_phase48.png", "outputs/figure2_lollipop_matrix_phase48.svg; outputs/figure2_lollipop_matrix_phase48.pdf", "figure_layout_spec.tsv", "figure_output_spec.md", "pass", "HF047 bubble-matrix grammar applied to panel B and native statistical panels applied to A/C"],
            ["Fig3", "final", "clinical LFO association and comparator loss", "single final render", "forestploter_style_native_plus_ellipse", "native_workflow", "production_ready", "pass", "pass", "Python", "research-py312", "yes", render_script_win, "intermediate_tables/fig3_lfo_forest_scatter_input_mapped.tsv", "outputs/figure3_forest_scatter_ellipse_phase48.png", "outputs/figure3_forest_scatter_ellipse_phase48.svg; outputs/figure3_forest_scatter_ellipse_phase48.pdf", "figure_layout_spec.tsv", "figure_output_spec.md", "pass", "Forestploter-style clinical panel plus bivariate scatter answers the reviewer risk/discrimination question"],
        ],
        columns=[
            "panel", "option", "panel role", "variant budget", "candidate id", "candidate level", "candidate maturity",
            "data fit gate", "visual fit gate", "runtime", "env", "rendered", "render script", "intermediate file",
            "output png", "output pdf/svg", "figure layout spec", "figure output spec", "validation status", "reason",
        ],
    )
    compliant_variants.to_csv(REDRAW / "panel_render_variants.tsv", sep="\t", index=False)

    selection = """
# Panel Template Selection

| Panel | Selected option | Candidate ID | Candidate level | Selected output | Selection reason |
|---|---|---|---|---|---|
| Fig1 | final | native_matplotlib_alluvial | native_workflow | outputs/figure1_sankey_alluvial_phase48.svg | Sankey/alluvial grammar best answers source-screen to complete-domain to LFO attrition while preserving evidence-tier color. |
| Fig2 | final | HF047_2025-08-02_d1aba2e6_informed_composite | hf_capsule | outputs/figure2_lollipop_matrix_phase48.svg | Three-chain composite preserves bootstrap, method-agreement, and covariance-guardrail evidence; HF047 is used only where the matrix data fit. |
| Fig3 | final | forestploter_style_native_plus_ellipse | native_workflow | outputs/figure3_forest_scatter_ellipse_phase48.svg | Clinical forest plus risk-difference by delta-AUC scatter makes the main functional-change association and comparator loss readable together. |
"""
    (REDRAW / "panel_template_selection.md").write_text(selection.strip() + "\n", encoding="utf-8")

    mapping = """
# Panel Visual Mapping

| Panel | Panel role | Variant budget | Atlas major class | Atlas subtype | Candidate ID | Candidate level | Candidate maturity | Data fit gate | Visual fit gate | Runtime | Env | Selected option | Template/capsule | Capsule path | Reference visual | Source script | Source code snapshot | Raw data | Variable mapping | Intermediate file | Ported script | Visual match notes | Validation report | Output | Reason |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Fig1 | Denominator and evidence-tier lock | single final render | flow | Sankey / alluvial | native_matplotlib_alluvial | native_workflow | production_ready | pass | pass | Python | research-py312 | final | native alluvial workflow | NA | user-requested alluvial visual grammar | E:\\Reserch\\Older women\\figure_redraw\\phase48_fig1_3_sankey_lollipop_forest\\scripts\\render_phase48_fig1_3.py | E:\\Reserch\\Older women\\figure_redraw\\phase48_fig1_3_sankey_lollipop_forest\\scripts\\render_phase48_fig1_3.py | E:\\Reserch\\Older women\\manuscript\\bmc_geriatrics_submission_burden_profiles_rescue\\additional_file_12_baseline_clinical_design_covariate_availability.csv | source_women50_n to first band; complete_four_domain_n to second band; LFO model n to terminal band; role to color | intermediate_tables/fig1_sankey_alluvial_input_mapped.tsv | scripts/render_phase48_fig1_3.py | visual_match_notes.md#fig1 | persist_source_code_first_validation.md | outputs/figure1_sankey_alluvial_phase48.svg | Cohort-row alluvial avoids crossings while retaining width-coded attrition. |
| Fig2 | Three-chain profile stability guardrail | single final render | matrix / distribution / ranking | raincloud + bubble heatmap + lollipop | HF047_2025-08-02_d1aba2e6_informed_composite | hf_capsule | source_port_ready | pass | pass | Python | research-py312 | final | HF047 bubble matrix plus native A/C panels | E:\\Python\\PERSIST\\_portable_patterns\\high_fidelity_by_folder\\capsules\\HF047_2025-08-02_d1aba2e6 | E:\\Python\\PERSIST\\_portable_patterns\\high_fidelity_by_folder\\capsules\\HF047_2025-08-02_d1aba2e6\\VISUAL_SPEC.md | E:\\Python\\PERSIST\\_portable_patterns\\high_fidelity_by_folder\\capsules\\HF047_2025-08-02_d1aba2e6\\source_code\\source_01_cebeb24c.py | E:\\Python\\PERSIST\\_portable_patterns\\high_fidelity_by_folder\\capsules\\HF047_2025-08-02_d1aba2e6\\SOURCE_CODE_SNAPSHOT.md | E:\\Reserch\\Older women\\outputs\\phase32_gmm_bootstrap_stability.csv | bootstrap ARI to raincloud; method ARI matrix to bubble area/color; log10 condition number to lollipop | intermediate_tables/fig2_bootstrap_replicates_input_mapped.tsv; intermediate_tables/fig2_algorithm_robustness_input_mapped.tsv; intermediate_tables/fig2_stability_summary_input_mapped.tsv | scripts/render_phase48_fig1_3.py | visual_match_notes.md#fig2 | persist_source_code_first_validation.md | outputs/figure2_lollipop_matrix_phase48.svg | HF047 was used only for the matrix panel with compatible rectangular data. |
| Fig3 | Clinical LFO association and comparator loss | single final render | clinical forest + bivariate uncertainty | forest plot plus risk-discrimination scatter | forestploter_style_native_plus_ellipse | native_workflow | production_ready | pass | pass | Python | research-py312 | final | native forestploter-style workflow | NA | user-requested forestploter and ellipse visual grammar | E:\\Reserch\\Older women\\figure_redraw\\phase48_fig1_3_sankey_lollipop_forest\\scripts\\render_phase48_fig1_3.py | E:\\Reserch\\Older women\\figure_redraw\\phase48_fig1_3_sankey_lollipop_forest\\scripts\\render_phase48_fig1_3.py | E:\\Reserch\\Older women\\manuscript\\bmc_geriatrics_submission_burden_profiles_rescue\\additional_file_14_strict_core_lfo_functional_change_association.csv | adjusted RR and CI to forest; LFO n to point size; risk difference and delta AUC to scatter with error bars | intermediate_tables/fig3_lfo_forest_scatter_input_mapped.tsv | scripts/render_phase48_fig1_3.py | visual_match_notes.md#fig3 | persist_source_code_first_validation.md | outputs/figure3_forest_scatter_ellipse_phase48.svg | Python forestploter-style equivalent keeps all text editable and integrates the scatter panel. |
"""
    (REDRAW / "panel_visual_mapping.md").write_text(mapping.strip() + "\n", encoding="utf-8")

    visual_notes = """
# Visual Match Notes

## Fig1

The selected visual grammar is Sankey/alluvial, but rendered as aligned cohort-row flows rather than a crossed global Sankey. This preserves the requested width-coded sample loss from women 50+ screen to complete four-domain data to LFO model while keeping each cohort label readable and evidence-tier color stable.

## Fig2

Panel A is a raincloud distribution bound to true bootstrap ARI replicates. Panel B uses the HF047 bubble-matrix grammar because the data are a complete cohort by algorithm ARI matrix. Panel C uses a lollipop ranking because the scientific task is a thresholded covariance guardrail comparison.

## Fig3

Panel A follows the clinical forest-table grammar: adjusted RR with 95% CI on the left and adj RR plus delta-AUC values in a right-side text table. Point size encodes LFO sample size. Panel B maps risk difference to the x-axis and delta AUC to the y-axis with error bars; the ellipse is a descriptive covariance ellipse over the four cohorts, not an inferential confidence region.
"""
    (REDRAW / "visual_match_notes.md").write_text(visual_notes.strip() + "\n", encoding="utf-8")

    palette_note = """
# Project Palette Recommendation

Evidence-tier palette used across Fig1-Fig3:

- Strict-core: #176C73
- Bridge sensitivity: #D08B1E
- Baseline-only: #91979C
- Validation-downgraded: #BD6D61
- No LFO / attrition: #D7DCE0

The palette is intentionally restrained and categorical; numeric heatmap values use a separate diverging scale only in Fig2B.
"""
    (REDRAW / "project_palette_recommendation.md").write_text(palette_note.strip() + "\n", encoding="utf-8")

    final_selection = """
# Panel Final Selection

| Panel | Selected option | Candidate ID | Candidate level | Selected output | Final selection reason | Rejected alternatives | Known tradeoff |
|---|---|---|---|---|---|---|---|
| Fig1 | final | native_matplotlib_alluvial | native_workflow | outputs/figure1_sankey_alluvial_phase48.svg | A row-aligned alluvial makes attrition widths and cohort-specific evidence tiers visible without crossings. | Plotly Sankey; dashboard/network capsules | LASI dominates because linear width encodes the true larger baseline-only cohort. |
| Fig2 | final | HF047_2025-08-02_d1aba2e6_informed_composite | hf_capsule | outputs/figure2_lollipop_matrix_phase48.svg | The triptych preserves the three evidence chains while using HF047 only for the data-compatible matrix panel. | Single heatmap; single lollipop; petal/radial variants | Bootstrap raincloud reflects only the 20 real replicates currently available. |
| Fig3 | final | forestploter_style_native_plus_ellipse | native_workflow | outputs/figure3_forest_scatter_ellipse_phase48.svg | The forest-table panel gives clinical effect estimates and the scatter panel tests whether larger absolute risk aligns with profile discrimination gain. | Plain forest-only panel; matrix-style alternatives | The ellipse is descriptive and must be described as such in the legend. |
"""
    (REDRAW / "panel_final_selection.md").write_text(final_selection.strip() + "\n", encoding="utf-8")


def main() -> None:
    setup()
    render_fig1()
    render_fig2()
    render_fig3()
    write_protocol_files()
    print(OUT / "figure1_sankey_alluvial_phase48.svg")
    print(OUT / "figure2_lollipop_matrix_phase48.svg")
    print(OUT / "figure3_forest_scatter_ellipse_phase48.svg")


if __name__ == "__main__":
    main()
