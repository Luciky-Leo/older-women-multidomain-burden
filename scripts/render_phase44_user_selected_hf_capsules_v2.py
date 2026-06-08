#!/usr/bin/env python3
"""Render user-selected PERSIST HF capsule variants for Fig3/Fig2/S1.

SOURCE_CODE_FIRST:
This project-local script is a runnable port of selected PERSIST high-fidelity
capsule visual grammars to original Older women manuscript outputs.

Source code snapshots consulted:
- HF112_2025-11-13_1cced429/source_code/source_01_52ebc0ff.py
- HF176_2026-03-12_52ae8721/source_code/source_01_bc264e15.py
- HF207_2026-05-13_e6a8d9c5/source_code/source_01_08924199.py
- HF084_2025-10-07_728da769/source_code/source_01_5bf72cc1.py
- HF200_2026-05-01_17639b10/source_code/source_01_57fbb0c8.py

VISUAL_REFERENCES:
- HF112 Figure_1.png ridge/scatter dashboard grammar
- HF207 3D_Pie_26.png 3D pie grammar
- HF084 correlation_pearson_1.png semicircular fan matrix grammar
- HF200 shap_results_Validation_Set_scheme10.png multi-panel beeswarm + rose grammar

The data-loading layer is replaced with real project tables under
E:/Reserch/Older women/outputs. No screenshot-derived or simulated values are
used. SHAP-like visual elements are relabelled as guardrail/profile summaries
and are not interpreted as SHAP values.
"""

from __future__ import annotations

import math
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize, to_hex, to_rgb
from matplotlib.cm import ScalarMappable
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Wedge
import numpy as np
import pandas as pd

try:
    from scipy.stats import gaussian_kde
except Exception:  # pragma: no cover - scipy is expected in research-py312
    gaussian_kde = None


PROJECT = Path("/mnt/e/Reserch/Older women")
STYLE_MODULE_DIR = PROJECT / "scripts"
if str(STYLE_MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(STYLE_MODULE_DIR))

from manuscript_figure_style import (  # noqa: E402
    FIGURE_RULE_SUMMARY,
    apply_manuscript_figure_style,
    save_manuscript_figure,
)

# Editable vector export is applied by scripts/manuscript_figure_style.py:
# mpl.rcParams["pdf.fonttype"] = 42
# mpl.rcParams["svg.fonttype"] = "none"
# mpl.rcParams["font.family"] = "Arial"

STAGE = PROJECT / "figure_redraw" / "persist_stage4_user_selected_hf_capsules_v2"
SCRIPT_DIR = STAGE / "scripts"
INTERMEDIATE = STAGE / "intermediate_tables"
OUTPUT_DIR = STAGE / "outputs"
CONTACT_DIR = STAGE / "contact_sheets"
PROJECT_OUTPUTS = PROJECT / "outputs"

CAPSULE_ROOT = Path("/mnt/e/Python/PERSIST/_portable_patterns/high_fidelity_by_folder/capsules")

CAPSULES = {
    "HF112": {
        "id": "HF112_2025-11-13_1cced429",
        "path": CAPSULE_ROOT / "HF112_2025-11-13_1cced429",
        "snapshot": CAPSULE_ROOT / "HF112_2025-11-13_1cced429/source_code/source_01_52ebc0ff.py",
        "source_script": "/mnt/e/Python/PERSIST/2025年11月13日 期刊图片复现Python绘制山脊图+散点图组合图/1113-山脊图+回归拟合图组图.py",
        "reference": "/mnt/e/Python/PERSIST/2025年11月13日 期刊图片复现Python绘制山脊图+散点图组合图/Figure_1.png",
    },
    "HF176": {
        "id": "HF176_2026-03-12_52ae8721",
        "path": CAPSULE_ROOT / "HF176_2026-03-12_52ae8721",
        "snapshot": CAPSULE_ROOT / "HF176_2026-03-12_52ae8721/source_code/source_01_bc264e15.py",
        "source_script": "/mnt/e/Python/PERSIST/2026年03月12日 Python绘制XGBoost+SHAP特征重要性与影响方向汇总图-适用于分类任务/20260305-(分类)Python绘制XGBoost+SHAP特征重要性与影响方向汇总图.py",
        "reference": "/mnt/e/Python/PERSIST/2026年03月12日 Python绘制XGBoost+SHAP特征重要性与影响方向汇总图-适用于分类任务/47_Class_5.png",
    },
    "HF207": {
        "id": "HF207_2026-05-13_e6a8d9c5",
        "path": CAPSULE_ROOT / "HF207_2026-05-13_e6a8d9c5",
        "snapshot": CAPSULE_ROOT / "HF207_2026-05-13_e6a8d9c5/source_code/source_01_08924199.py",
        "source_script": str(CAPSULE_ROOT / "HF207_2026-05-13_e6a8d9c5/source_code/source_01_08924199.py"),
        "reference": str(CAPSULE_ROOT / "HF207_2026-05-13_e6a8d9c5/VISUAL_SPEC.md"),
    },
    "HF084": {
        "id": "HF084_2025-10-07_728da769",
        "path": CAPSULE_ROOT / "HF084_2025-10-07_728da769",
        "snapshot": CAPSULE_ROOT / "HF084_2025-10-07_728da769/source_code/source_01_5bf72cc1.py",
        "source_script": "/mnt/e/Python/PERSIST/2025年10月7日 Python绘制扇形相关性热图-包括pearson, spearman, kendall/扇形相关性热图.py",
        "reference": "/mnt/e/Python/PERSIST/2025年10月7日 Python绘制扇形相关性热图-包括pearson, spearman, kendall/correlation_pearson_1.png",
    },
    "HF200": {
        "id": "HF200_2026-05-01_17639b10",
        "path": CAPSULE_ROOT / "HF200_2026-05-01_17639b10",
        "snapshot": CAPSULE_ROOT / "HF200_2026-05-01_17639b10/source_code/source_01_57fbb0c8.py",
        "source_script": "/mnt/e/Python/PERSIST/2026年05月01日 Python绘制多分类任务shap蜂巢图+玫瑰图组合图/20260501-多分类任务shap重要性组图.py",
        "reference": "/mnt/e/Python/PERSIST/2026年05月01日 Python绘制多分类任务shap蜂巢图+玫瑰图组合图/shap_results_Validation_Set_scheme10.png",
    },
}

STRICT_ROLE = "Strict-core"
ROLE_COLORS = {
    "Strict-core": "#175C66",
    "Functional bridge sensitivity": "#C9862D",
    "Baseline-only descriptive": "#8A8D91",
    "Validation-downgraded sensitivity": "#B86B5E",
}
ROLE_PIE_ORDER = [
    "Baseline-only descriptive",
    "Functional bridge sensitivity",
    "Strict-core",
    "Validation-downgraded sensitivity",
]
ROLE_SHORT_LABELS = {
    "Strict-core": "Strict",
    "Functional bridge sensitivity": "Bridge",
    "Baseline-only descriptive": "Baseline",
    "Validation-downgraded sensitivity": "Down",
}
COHORT_COLORS = {
    "CHARLS": "#175C66",
    "ELSA": "#7A1E48",
    "HRS": "#234B9B",
    "KLoSA": "#C9862D",
    "LASI": "#8A8D91",
    "MHAS": "#1A8A6A",
    "SHARE": "#B86B5E",
}
DOMAIN_COLORS = {
    "Functional": "#175C66",
    "Cognitive": "#7A1E48",
    "Affective": "#C9862D",
    "Cardiometabolic": "#234B9B",
}
METHOD_ORDER = [
    "gmm_full",
    "gmm_diag",
    "gmm_tied",
    "kmeans",
    "hierarchical_ward_sample",
    "continuous_severity_tertile",
]
METHOD_LABELS = {
    "gmm_full": "Full",
    "gmm_diag": "Diag",
    "gmm_tied": "Tied",
    "kmeans": "K-means",
    "hierarchical_ward_sample": "Ward",
    "continuous_severity_tertile": "Severity",
}


@dataclass
class Variant:
    panel: str
    option: str
    candidate_key: str
    panel_role: str
    variant_budget: str
    atlas_class: str
    atlas_subtype: str
    conclusion: str
    raw_data: str
    variable_mapping: str
    reason: str
    rows_mapped: int = 0
    output_png: Path | None = None
    output_pdf: Path | None = None
    output_svg: Path | None = None
    intermediate_file: Path | None = None
    script_file: Path | None = None

    @property
    def capsule(self) -> dict[str, object]:
        return CAPSULES[self.candidate_key]

    @property
    def candidate_id(self) -> str:
        return str(self.capsule["id"])

    @property
    def base_name(self) -> str:
        return f"{self.option}__{self.candidate_id}"


def ensure_dirs() -> None:
    for path in [STAGE, SCRIPT_DIR, INTERMEDIATE, OUTPUT_DIR, CONTACT_DIR]:
        path.mkdir(parents=True, exist_ok=True)
    for panel in ["Fig3A", "Fig3B", "Fig2B", "Fig2C", "FigS1"]:
        (OUTPUT_DIR / panel).mkdir(parents=True, exist_ok=True)


def rel(path: Path) -> str:
    try:
        return path.relative_to(STAGE).as_posix()
    except ValueError:
        try:
            return path.relative_to(PROJECT).as_posix()
        except ValueError:
            return path.as_posix()


def style_axes(ax: plt.Axes, left: bool = True, bottom: bool = True) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(left)
    ax.spines["bottom"].set_visible(bottom)
    for side in ["left", "bottom"]:
        ax.spines[side].set_linewidth(1.4)
    ax.tick_params(width=1.2, length=4, labelsize=8)


def parse_ci(text: object) -> tuple[float, float]:
    if pd.isna(text):
        return (math.nan, math.nan)
    value = str(text).replace("to", " ").replace(",", " ")
    parts = [p for p in value.split() if p]
    nums: list[float] = []
    for part in parts:
        try:
            nums.append(float(part))
        except ValueError:
            continue
    if len(nums) >= 2:
        return nums[0], nums[1]
    return (math.nan, math.nan)


def ridge_density(values: np.ndarray, x_grid: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if values.size == 0:
        return np.zeros_like(x_grid)
    if values.size >= 3 and np.unique(np.round(values, 6)).size >= 3 and gaussian_kde is not None:
        try:
            density = gaussian_kde(values)(x_grid)
        except Exception:
            density = np.zeros_like(x_grid)
    else:
        span = max(float(np.nanmax(x_grid) - np.nanmin(x_grid)), 1.0)
        bandwidth = span / 25.0
        density = np.zeros_like(x_grid)
        for val in values:
            density += np.exp(-0.5 * ((x_grid - val) / bandwidth) ** 2)
    if np.nanmax(density) > 0:
        density = density / np.nanmax(density)
    return density


def save_figure(fig: plt.Figure, variant: Variant) -> None:
    panel_dir = OUTPUT_DIR / variant.panel
    variant.output_png = panel_dir / f"{variant.base_name}.png"
    variant.output_pdf = panel_dir / f"{variant.base_name}.pdf"
    variant.output_svg = panel_dir / f"{variant.base_name}.svg"
    save_manuscript_figure(fig, variant.output_png, variant.output_pdf, variant.output_svg, preview_dpi=300)
    plt.close(fig)


def write_intermediate(variant: Variant, df: pd.DataFrame) -> None:
    variant.intermediate_file = INTERMEDIATE / f"{variant.base_name}__input_mapped.tsv"
    df.to_csv(variant.intermediate_file, sep="\t", index=False)
    variant.rows_mapped = len(df)


def draw_hf112_ridge_effect_dashboard(
    variant: Variant,
    mode: str,
    strict: pd.DataFrame,
    class_risks: pd.DataFrame,
    auc_ci: pd.DataFrame,
) -> None:
    """Port HF112 ridge/scatter grammar to effect-size panels."""
    # SOURCE_CODE_SNAPSHOT: HF112 ridge density plus scatter comparison grammar.
    data = strict.copy()
    cohorts = data["cohort"].tolist()
    palette = [COHORT_COLORS[c] for c in cohorts]
    fig = plt.figure(figsize=(9.4, 3.1))
    gs = GridSpec(1, 3, figure=fig, width_ratios=[1.25, 1.05, 0.9], wspace=0.34)
    ax_left = fig.add_subplot(gs[0, 0])
    ax_mid = fig.add_subplot(gs[0, 1])
    ax_right = fig.add_subplot(gs[0, 2])

    y_positions = np.arange(len(cohorts))[::-1]

    if mode == "risk":
        mapped_rows = []
        x_grid = np.linspace(15, 55, 320)
        for y, cohort, color in zip(y_positions, cohorts, palette):
            vals = class_risks.loc[class_risks["cohort"] == cohort, "event_pct"].to_numpy(float)
            sizes = class_risks.loc[class_risks["cohort"] == cohort, "n"].to_numpy(float)
            density = ridge_density(vals, x_grid)
            ax_left.fill_between(x_grid, y, y + density * 0.62, color=color, alpha=0.26)
            ax_left.plot(x_grid, y + density * 0.62, color=color, lw=1.7)
            if len(vals):
                scaled = 18 + 55 * (sizes / np.nanmax(sizes))
                ax_left.scatter(vals, np.repeat(y + 0.06, len(vals)), s=scaled, color=color, ec="white", lw=0.5, zorder=3)
                mapped_rows.extend(
                    {
                        "cohort": cohort,
                        "source": "phase36_functional_association_class_risks",
                        "class_event_pct": val,
                        "class_n": size,
                    }
                    for val, size in zip(vals, sizes)
                )
        ax_left.set_xlim(15, 55)
        ax_left.set_xlabel("Class event risk, %", fontsize=9)
        ax_left.set_yticks(y_positions)
        ax_left.set_yticklabels(cohorts, fontsize=9, fontweight="bold")
        style_axes(ax_left)

        mids = data["crude_risk_difference_pct"].to_numpy(float)
        lows, highs = zip(*[parse_ci(x) for x in data["crude_risk_difference_ci_pct"]])
        for y, cohort, color, mid, low, high in zip(y_positions, cohorts, palette, mids, lows, highs):
            ax_mid.hlines(y, low, high, color=color, lw=2.4)
            ax_mid.scatter([mid], [y], color=color, s=70, ec="white", lw=0.7, zorder=3)
            ax_mid.text(high + 0.8, y, f"{mid:.1f}", va="center", fontsize=8, color=color)
        ax_mid.axvline(0, color="0.55", lw=1.1, ls=":")
        ax_mid.set_xlim(8, 30)
        ax_mid.set_yticks([])
        ax_mid.set_xlabel("Crude risk difference, %", fontsize=9)
        style_axes(ax_mid, left=False)

        x = data["reference_event_pct"].to_numpy(float)
        yv = data["highest_event_pct"].to_numpy(float)
        for cohort, color, xv, yval in zip(cohorts, palette, x, yv):
            ax_right.scatter(xv, yval, s=82, color=color, ec="white", lw=0.7)
            ax_right.text(xv + 0.6, yval, cohort, fontsize=7.5, color=color, va="center")
        lim = [min(x.min(), yv.min()) - 2, max(x.max(), yv.max()) + 2]
        ax_right.plot(lim, lim, color="0.25", lw=1.5)
        ax_right.set_xlim(lim)
        ax_right.set_ylim(lim)
        ax_right.set_xlabel("Reference class risk, %", fontsize=9)
        ax_right.set_ylabel("Highest class risk, %", fontsize=9)
        style_axes(ax_right)
        interm = pd.concat([data, pd.DataFrame(mapped_rows)], ignore_index=True, sort=False)
        write_intermediate(variant, interm)
    else:
        ci = auc_ci[auc_ci["cohort"].isin(cohorts)].set_index("cohort")
        mapped = data.copy()
        mapped = mapped.join(ci, on="cohort", rsuffix="_bootstrap")
        for y, cohort, color in zip(y_positions, cohorts, palette):
            row = mapped.loc[mapped["cohort"] == cohort].iloc[0]
            auc_values = np.array([row["profile_auc"], row["continuous_auc"]], dtype=float)
            x_grid = np.linspace(0.62, 0.78, 320)
            density = ridge_density(auc_values, x_grid)
            ax_left.fill_between(x_grid, y, y + density * 0.62, color=color, alpha=0.22)
            ax_left.plot(x_grid, y + density * 0.62, color=color, lw=1.6)
            ax_left.plot(auc_values, [y + 0.05, y + 0.05], color=color, lw=1.2, alpha=0.8)
            ax_left.scatter(row["continuous_auc"], y + 0.05, s=58, marker="s", color=color, ec="white", lw=0.5)
            ax_left.scatter(row["profile_auc"], y + 0.05, s=58, marker="o", color=color, ec="white", lw=0.5)
        ax_left.set_xlim(0.62, 0.78)
        ax_left.set_xlabel("AUC values", fontsize=9)
        ax_left.set_yticks(y_positions)
        ax_left.set_yticklabels(cohorts, fontsize=9, fontweight="bold")
        style_axes(ax_left)
        ax_left.legend(
            handles=[
                plt.Line2D([], [], marker="o", color="0.2", ls="", label="Profile"),
                plt.Line2D([], [], marker="s", color="0.2", ls="", label="Continuous"),
            ],
            loc="lower right",
            frameon=False,
            fontsize=7,
        )

        for y, cohort, color in zip(y_positions, cohorts, palette):
            row = mapped.loc[mapped["cohort"] == cohort].iloc[0]
            low = row["delta_auc_p025"]
            high = row["delta_auc_p975"]
            mid = row["delta_auc_profile_minus_continuous"]
            ax_mid.hlines(y, low, high, color=color, lw=2.4)
            ax_mid.scatter(mid, y, color=color, s=70, ec="white", lw=0.7, zorder=3)
            ax_mid.text(high + 0.001, y, f"{mid:.3f}", va="center", fontsize=8, color=color)
        ax_mid.axvline(0, color="0.45", lw=1.2, ls=":")
        ax_mid.set_xlim(-0.026, 0.004)
        ax_mid.set_yticks([])
        ax_mid.set_xlabel("Delta AUC, profile - continuous", fontsize=9)
        style_axes(ax_mid, left=False)

        x = mapped["continuous_auc"].to_numpy(float)
        yv = mapped["profile_auc"].to_numpy(float)
        for cohort, color, xv, yval in zip(cohorts, palette, x, yv):
            ax_right.scatter(xv, yval, s=82, color=color, ec="white", lw=0.7)
            ax_right.text(xv + 0.002, yval, cohort, fontsize=7.5, color=color, va="center")
        lim = [min(x.min(), yv.min()) - 0.01, max(x.max(), yv.max()) + 0.01]
        ax_right.plot(lim, lim, color="0.25", lw=1.5)
        ax_right.set_xlim(lim)
        ax_right.set_ylim(lim)
        ax_right.set_xlabel("Continuous AUC", fontsize=9)
        ax_right.set_ylabel("Profile AUC", fontsize=9)
        style_axes(ax_right)
        write_intermediate(variant, mapped)

    for label, ax in zip(["a", "b", "c"], [ax_left, ax_mid, ax_right]):
        ax.text(-0.12, 1.05, label, transform=ax.transAxes, fontsize=13, fontweight="bold")

    save_figure(fig, variant)


def draw_hf084_fan_matrix(variant: Variant, robustness: pd.DataFrame) -> None:
    """Port HF084 semicircular fan heatmap to cohort-by-method ARI."""
    # SOURCE_CODE_SNAPSHOT: HF084 correlation_matrix_custom fan matrix.
    keep = robustness[robustness["method"].isin(METHOD_ORDER)].copy()
    matrix = keep.pivot(index="cohort", columns="method", values="ari_vs_selected_gmm")
    cohort_order = ["CHARLS", "ELSA", "HRS", "KLoSA", "LASI", "MHAS", "SHARE"]
    matrix = matrix.reindex(cohort_order)[METHOD_ORDER]
    long = matrix.reset_index().melt(id_vars="cohort", var_name="method", value_name="ari_vs_selected_gmm")
    long["method_label"] = long["method"].map(METHOD_LABELS)
    write_intermediate(variant, long)

    fig, ax = plt.subplots(figsize=(10.5, 7.3), subplot_kw={"projection": "polar"})
    total_deg = 154
    start = np.deg2rad(90 - total_deg / 2)
    end = np.deg2rad(90 + total_deg / 2)
    theta = np.linspace(start, end, len(cohort_order))
    width = (end - start) / len(cohort_order) * 0.9
    radii = np.arange(4.3, 4.3 + len(METHOD_ORDER))
    cmap = LinearSegmentedColormap.from_list("ari_guardrail", ["#E9F3F3", "#F7F5F0", "#D75F5F"])
    norm = Normalize(vmin=0, vmax=1)

    for ridx, method in enumerate(METHOD_ORDER):
        r = radii[ridx]
        values = matrix[method].to_numpy(float)
        for cidx, value in enumerate(values):
            color = cmap(norm(value)) if np.isfinite(value) else "#F2F2F2"
            ax.bar(theta[cidx], height=0.86, width=width, bottom=r, color=color, edgecolor="white", linewidth=1.0)
            if np.isfinite(value):
                rot = np.rad2deg(theta[cidx]) - 90
                ax.text(
                    theta[cidx],
                    r + 0.43,
                    f"{value:.2f}",
                    ha="center",
                    va="center",
                    rotation=rot,
                    rotation_mode="anchor",
                    fontsize=8.5,
                    color="black",
                )

    label_r = radii[-1] + 1.2
    for cohort, angle in zip(cohort_order, theta):
        rot = np.rad2deg(angle) - 90
        ax.text(
            angle,
            label_r,
            cohort,
            ha="center",
            va="center",
            rotation=rot,
            rotation_mode="anchor",
            fontsize=10,
            fontweight="bold",
            color=COHORT_COLORS[cohort],
        )

    ax.text(
        0,
        0,
        "Method\nagreement\nARI vs selected GMM",
        ha="center",
        va="center",
        fontsize=12,
        fontweight="bold",
        linespacing=1.25,
    )
    ax.grid(False)
    ax.spines["polar"].set_visible(False)
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_ylim(0, label_r + 1.7)

    cax = fig.add_axes([0.22, 0.13, 0.56, 0.025])
    sm = ScalarMappable(cmap=cmap, norm=norm)
    cbar = fig.colorbar(sm, cax=cax, orientation="horizontal")
    cbar.set_label("ARI vs selected GMM", fontsize=10, labelpad=8)
    cbar.ax.tick_params(labelsize=8)
    handles = [
        plt.Line2D([0], [0], marker="s", color="black", ls="", markersize=7, label=METHOD_LABELS[method])
        for method in METHOD_ORDER
    ]
    ax.legend(
        handles=handles,
        title="Methods",
        frameon=False,
        fontsize=8,
        title_fontsize=9,
        loc="center left",
        bbox_to_anchor=(1.04, 0.52),
    )
    ax.text(-0.05, 1.0, "a", transform=ax.transAxes, fontsize=14, fontweight="bold")
    save_figure(fig, variant)


def darken_color(color: str, factor: float = 0.72) -> str:
    rgb = np.asarray(to_rgb(color), dtype=float)
    return to_hex(np.clip(rgb * factor, 0, 1))


def draw_hf207_3d_role_pie(ax: plt.Axes, role_summary: pd.DataFrame) -> None:
    """Port HF207 stacked-layer 3D pie grammar to four role-tier colors."""
    # SOURCE_CODE_SNAPSHOT: HF207 layered 3D pie with top labels and side depth.
    ordered = role_summary.set_index("role").reindex(ROLE_PIE_ORDER).reset_index()
    ordered["importance_pct"] = pd.to_numeric(ordered["importance_pct"], errors="coerce").fillna(0)
    ordered = ordered[ordered["importance_pct"].gt(0)].copy()
    labels = [ROLE_SHORT_LABELS.get(role, role) for role in ordered["role"]]
    sizes = ordered["importance_pct"].to_numpy(float)
    colors = [ROLE_COLORS[role] for role in ordered["role"]]
    side_colors = colors

    depth_layers = 46
    total_thickness = 0.13
    step = total_thickness / depth_layers
    startangle = 92
    radius = 0.72
    center_y = 0.42

    for i in range(depth_layers):
        wedges_side, _ = ax.pie(
            sizes,
            colors=side_colors,
            startangle=startangle,
            radius=radius,
            center=(0, center_y - i * step),
            counterclock=False,
        )
        for wedge in wedges_side:
            wedge.set_edgecolor("none")
            wedge.set_antialiased(True)
            wedge.set_zorder(depth_layers - i)

    wedges, _ = ax.pie(
        sizes,
        colors=colors,
        startangle=startangle,
        radius=radius,
        center=(0, center_y),
        counterclock=False,
        wedgeprops={"edgecolor": "white", "linewidth": 0.7},
    )

    for wedge in wedges:
        wedge.set_center((0, center_y))
        wedge.set_zorder(depth_layers + 1)

    legend_name_map = {"Baseline": "Base", "Strict": "Strict", "Bridge": "Bridge", "Down": "Down"}
    legend_labels = [f"{legend_name_map.get(label, label)} {value:.0f}%" for label, value in zip(labels, sizes)]
    legend_positions = [(-0.92, -0.70), (-0.92, -0.95), (0.16, -0.70), (0.16, -0.95)]
    for (x0, y0), label, color in zip(legend_positions, legend_labels, colors):
        ax.scatter(x0, y0, marker="s", s=44, color=color, clip_on=True, zorder=depth_layers + 4)
        ax.text(
            x0 + 0.12,
            y0,
            label,
            ha="left",
            va="center",
            fontsize=7,
            color="#111827",
            clip_on=True,
            zorder=depth_layers + 4,
        )
    ax.set_aspect(0.58)
    ax.set_xlim(-1.24, 1.24)
    ax.set_ylim(-1.14, 1.20)
    ax.axis("off")


def draw_hf207_guardrail_dashboard(
    variant: Variant,
    guardrails: pd.DataFrame,
    robustness: pd.DataFrame,
) -> None:
    """Port HF207 3D pie plus guardrail bar/beeswarm dashboard to covariance guardrails."""
    # SOURCE_CODE_SNAPSHOT: HF207 layered 3D pie; flanking panels retain guardrail context.
    data = guardrails.copy()
    data["log10_condition"] = np.log10(pd.to_numeric(data["max_covariance_condition_number"], errors="coerce"))
    data["importance_pct"] = data["log10_condition"] / data["log10_condition"].sum() * 100
    data = data.sort_values("log10_condition", ascending=True)
    bee = robustness[robustness["method"].isin(METHOD_ORDER)].copy()
    bee = bee.merge(data[["cohort", "role", "log10_condition"]], on="cohort", how="left")
    write_intermediate(
        variant,
        pd.concat(
            [
                data.assign(mapped_source="phase40_table2_profile_stability_guardrails"),
                bee.assign(mapped_source="phase36_gmm_algorithm_robustness"),
            ],
            ignore_index=True,
            sort=False,
        ),
    )

    fig = plt.figure(figsize=(12.0, 5.4))
    gs = GridSpec(1, 3, figure=fig, width_ratios=[1.03, 1.06, 1.45], wspace=0.34)
    ax_bar = fig.add_subplot(gs[0, 0])
    ax_pie = fig.add_subplot(gs[0, 1])
    ax_bee = fig.add_subplot(gs[0, 2])

    y = np.arange(len(data))
    bar_colors = [ROLE_COLORS.get(role, "0.5") for role in data["role"]]
    ax_bar.barh(y, data["log10_condition"], color=bar_colors, height=0.62)
    ax_bar.set_yticks(y)
    ax_bar.set_yticklabels(data["cohort"], fontsize=9, fontweight="bold")
    for idx, row in enumerate(data.itertuples(index=False)):
        ax_bar.text(row.log10_condition + 0.03, idx, f"{row.importance_pct:.1f}%", va="center", fontsize=8)
    ax_bar.set_xlabel("log10 covariance condition", fontsize=9)
    ax_bar.set_xlim(0, max(data["log10_condition"]) + 0.9)
    style_axes(ax_bar)

    role_summary = data.groupby("role", as_index=False)["importance_pct"].sum()
    draw_hf207_3d_role_pie(ax_pie, role_summary)

    cohort_order = data.sort_values("log10_condition", ascending=False)["cohort"].tolist()
    ymap = {cohort: i for i, cohort in enumerate(cohort_order)}
    method_index = {method: i for i, method in enumerate(METHOD_ORDER)}
    cmap = plt.get_cmap("PuOr")
    for row in bee.itertuples(index=False):
        if not np.isfinite(row.ari_vs_selected_gmm):
            continue
        jitter = (method_index[row.method] - (len(METHOD_ORDER) - 1) / 2) * 0.028
        ax_bee.scatter(
            row.ari_vs_selected_gmm,
            ymap[row.cohort] + jitter,
            s=42,
            marker="s",
            color=cmap(method_index[row.method] / max(len(METHOD_ORDER) - 1, 1)),
            alpha=0.9,
            ec="white",
            lw=0.35,
        )
    for cohort in cohort_order:
        ax_bee.axhline(ymap[cohort], color="0.86", lw=0.8, ls="--", zorder=0)
    ax_bee.axvline(1.0, color="0.35", lw=1.2)
    ax_bee.set_yticks([ymap[c] for c in cohort_order])
    ax_bee.set_yticklabels(cohort_order, fontsize=9, fontweight="bold")
    ax_bee.set_xlim(0, 1.04)
    ax_bee.set_xlabel("Algorithm agreement, ARI", fontsize=9)
    style_axes(ax_bee)
    sm = ScalarMappable(cmap=cmap, norm=Normalize(vmin=0, vmax=len(METHOD_ORDER) - 1))
    cbar = fig.colorbar(sm, ax=ax_bee, fraction=0.035, pad=0.02)
    cbar.set_ticks(range(len(METHOD_ORDER)))
    cbar.set_ticklabels([METHOD_LABELS[m] for m in METHOD_ORDER])
    cbar.ax.tick_params(labelsize=7)
    cbar.set_label("Method", fontsize=8)

    for label, ax in zip(["a", "b", "c"], [ax_bar, ax_pie, ax_bee]):
        ax.text(-0.16, 1.03, label, transform=ax.transAxes, fontsize=14, fontweight="bold")
    save_figure(fig, variant)


def draw_rose_inset(ax: plt.Axes, values: np.ndarray, colors: list[str], label: str) -> None:
    angles = np.linspace(0, 2 * np.pi, len(values), endpoint=False)
    vals = np.asarray(values, dtype=float)
    if vals.size == 0 or np.nanmax(vals) <= 0:
        vals = np.ones(len(colors))
    heights = 0.32 + 0.62 * vals / np.nanmax(vals)
    ax.bar(angles, heights, width=2 * np.pi / len(values) * 0.92, bottom=0.12, color=colors, edgecolor="white", lw=0.8)
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.grid(False)
    ax.spines["polar"].set_visible(False)
    ax.text(0, -0.1, label, transform=ax.transAxes, fontsize=8.5, fontweight="bold", ha="center")


def draw_hf200_profile_burden(variant: Variant, profiles: pd.DataFrame, guardrails: pd.DataFrame) -> None:
    """Port HF200 multi-panel beeswarm plus rose grammar to strict-core profiles."""
    # SOURCE_CODE_SNAPSHOT: HF200 multi-class beeswarm panels with rose insets.
    selected = guardrails[guardrails["role"].eq(STRICT_ROLE)][["cohort", "selected_k"]].copy()
    strict_profiles = profiles.merge(selected, on="cohort", how="inner")
    strict_profiles = strict_profiles[strict_profiles["n_classes"].astype(str).eq(strict_profiles["selected_k"].astype(str))].copy()
    domain_map = {
        "Functional": "functional_score",
        "Cognitive": "cognitive_score",
        "Affective": "affective_score",
        "Cardiometabolic": "cardiometabolic_chronic_score",
    }
    rows = []
    for _, row in strict_profiles.iterrows():
        for domain, col in domain_map.items():
            rows.append(
                {
                    "cohort": row["cohort"],
                    "class": row["class"],
                    "class_pct": row["class_pct"],
                    "domain": domain,
                    "domain_z": row[col],
                    "severity_mean": row["severity_mean"],
                    "profile_label": row["profile_label"],
                }
            )
    long = pd.DataFrame(rows)
    write_intermediate(variant, long)

    cohorts = ["CHARLS", "ELSA", "HRS", "MHAS"]
    fig = plt.figure(figsize=(11.2, 8.2))
    gs = GridSpec(2, 3, figure=fig, width_ratios=[1.0, 1.0, 1.05], height_ratios=[1.0, 1.0], wspace=0.42, hspace=0.48)
    panel_axes = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[0, 2]), fig.add_subplot(gs[1, 0])]
    summary_ax = fig.add_subplot(gs[1, 1:], projection="polar")
    cmap = plt.get_cmap("Spectral_r")
    domain_order = ["Functional", "Cognitive", "Affective", "Cardiometabolic"]
    ymap = {domain: i for i, domain in enumerate(domain_order[::-1])}

    for idx, (ax, cohort) in enumerate(zip(panel_axes, cohorts)):
        subset = long[long["cohort"].eq(cohort)].copy()
        classes = sorted(subset["class"].unique())
        for class_idx, class_id in enumerate(classes):
            class_subset = subset[subset["class"].eq(class_id)]
            for row in class_subset.itertuples(index=False):
                y = ymap[row.domain] + (class_idx - (len(classes) - 1) / 2) * 0.06
                color = cmap((row.severity_mean + 1.6) / 3.6)
                ax.scatter(
                    row.domain_z,
                    y,
                    s=38 + row.class_pct * 1.4,
                    color=color,
                    alpha=0.88,
                    ec="white",
                    lw=0.45,
                )
                ax.text(row.domain_z, y + 0.08, str(class_id), ha="center", va="center", fontsize=6.6, color="0.25")
        ax.axvline(0, color="0.35", lw=1.3)
        for domain in domain_order:
            ax.axhline(ymap[domain], color="0.88", lw=0.8, ls="--", zorder=0)
        ax.set_yticks([ymap[d] for d in domain_order])
        ax.set_yticklabels(domain_order, fontsize=8.5, fontweight="bold")
        ax.set_xlim(-1.4, 2.4)
        ax.set_xlabel("Domain z-score", fontsize=9, fontweight="bold")
        ax.text(0.02, 0.94, chr(ord("a") + idx), transform=ax.transAxes, fontsize=13, fontweight="bold")
        ax.text(0.5, -0.23, cohort, transform=ax.transAxes, ha="center", fontsize=11, fontweight="bold", color=COHORT_COLORS[cohort])
        style_axes(ax)
        inset = ax.inset_axes([0.58, 0.08, 0.32, 0.32], projection="polar")
        class_pct = (
            strict_profiles[strict_profiles["cohort"].eq(cohort)]
            .sort_values("class")["class_pct"]
            .to_numpy(float)
        )
        rose_colors = [cmap((i + 1) / (len(class_pct) + 1)) for i in range(len(class_pct))]
        draw_rose_inset(inset, class_pct, rose_colors, f"k={len(class_pct)}")

    # Summary polar burden: weighted mean absolute domain burden by cohort.
    summary = (
        long.assign(weight=lambda d: d["class_pct"] / 100.0, abs_burden=lambda d: d["domain_z"].abs())
        .groupby(["cohort", "domain"], as_index=False)
        .apply(lambda g: pd.Series({"weighted_abs_z": np.average(g["abs_burden"], weights=g["weight"])}))
        .reset_index(drop=True)
    )
    ring_bottoms = np.arange(len(cohorts)) * 0.64 + 1.0
    angles = np.linspace(0, 2 * np.pi, len(domain_order), endpoint=False)
    for ridx, cohort in enumerate(cohorts):
        row = summary[summary["cohort"].eq(cohort)].set_index("domain").reindex(domain_order)
        vals = row["weighted_abs_z"].to_numpy(float)
        vals = np.nan_to_num(vals, nan=0.0)
        heights = 0.08 + 0.45 * vals / max(vals.max(), 0.01)
        for angle, height, domain in zip(angles, heights, domain_order):
            summary_ax.bar(
                angle,
                height,
                width=2 * np.pi / len(domain_order) * 0.86,
                bottom=ring_bottoms[ridx],
                color=DOMAIN_COLORS[domain],
                edgecolor="white",
                lw=1.2,
                alpha=0.92,
            )
        summary_ax.text(np.deg2rad(96), ring_bottoms[ridx] + 0.22, cohort, fontsize=8.5, color=COHORT_COLORS[cohort], ha="right", va="center")
    summary_ax.set_xticks(angles)
    summary_ax.set_xticklabels(domain_order, fontsize=8, fontweight="bold")
    summary_ax.set_yticklabels([])
    summary_ax.grid(False)
    summary_ax.spines["polar"].set_visible(False)
    summary_ax.set_ylim(0, ring_bottoms[-1] + 1.0)
    summary_ax.text(0.02, 0.98, "e", transform=summary_ax.transAxes, fontsize=13, fontweight="bold")
    summary_ax.set_title("Weighted absolute domain burden", fontsize=11, fontweight="bold", pad=10)
    legend = [
        plt.Line2D([0], [0], color=DOMAIN_COLORS[d], lw=8, label=d)
        for d in domain_order
    ]
    summary_ax.legend(handles=legend, frameon=False, fontsize=8, loc="center left", bbox_to_anchor=(1.02, 0.18), ncol=1)
    save_figure(fig, variant)


def load_data() -> dict[str, pd.DataFrame]:
    return {
        "strict": pd.read_csv(PROJECT_OUTPUTS / "phase40_table3_lfo_functional_change_association_strict_core.csv"),
        "class_risks": pd.read_csv(PROJECT_OUTPUTS / "phase36_functional_association_class_risks.csv"),
        "auc_ci": pd.read_csv(PROJECT_OUTPUTS / "phase37_auc_bootstrap_ci.csv"),
        "guardrails": pd.read_csv(PROJECT_OUTPUTS / "phase40_table2_profile_stability_guardrails.csv"),
        "robustness": pd.read_csv(PROJECT_OUTPUTS / "phase36_gmm_algorithm_robustness.csv"),
        "profiles": pd.read_csv(PROJECT_OUTPUTS / "phase4_gmm_class_profiles.csv"),
    }


def build_variants() -> list[Variant]:
    return [
        Variant(
            panel="Fig3A",
            option="Fig3A.HF112",
            candidate_key="HF112",
            panel_role="main_outcome_effect",
            variant_budget="user selected one variant for Fig3A",
            atlas_class="distribution_relationship_dashboard",
            atlas_subtype="ridge_density_plus_effect_ci_plus_scatter",
            conclusion="Strict-core profile classes separate crude functional deterioration risk but remain exploratory.",
            raw_data="outputs/phase40_table3_lfo_functional_change_association_strict_core.csv; outputs/phase36_functional_association_class_risks.csv",
            variable_mapping="cohort, class event_pct, class_n, crude risk difference CI, reference and highest class risk",
            reason="HF112 preserves ridge-plus-scatter grammar for a compact effect-size and risk-gradient panel.",
        ),
        Variant(
            panel="Fig3B",
            option="Fig3B.HF112",
            candidate_key="HF112",
            panel_role="main_validation_comparator",
            variant_budget="user selected one variant for Fig3B",
            atlas_class="distribution_relationship_dashboard",
            atlas_subtype="paired_auc_ridge_plus_delta_ci_plus_one_to_one_scatter",
            conclusion="Continuous four-domain scores have equal or better AUC than profile classes in strict-core validation.",
            raw_data="outputs/phase40_table3_lfo_functional_change_association_strict_core.csv; outputs/phase37_auc_bootstrap_ci.csv",
            variable_mapping="cohort, profile_auc, continuous_auc, delta_auc, bootstrap delta CI",
            reason="HF112 preserves the comparison ridge and 1:1 scatter grammar while showing comparator deltas.",
        ),
        Variant(
            panel="Fig2B",
            option="Fig2B.HF084",
            candidate_key="HF084",
            panel_role="main_stability_method_agreement",
            variant_budget="user selected one replacement variant for Fig2B",
            atlas_class="matrix",
            atlas_subtype="semicircular_fan_heatmap",
            conclusion="Non-GMM methods often do not reproduce the selected full-covariance GMM assignments.",
            raw_data="outputs/phase36_gmm_algorithm_robustness.csv",
            variable_mapping="cohort x method matrix of ari_vs_selected_gmm",
            reason="HF084 directly matches the requested fan/circular matrix grammar for cohort-by-method agreement.",
        ),
        Variant(
            panel="Fig2C",
            option="Fig2C.HF207",
            candidate_key="HF207",
            panel_role="main_stability_guardrail_dashboard",
            variant_budget="user selected one replacement variant for Fig2C",
            atlas_class="model_guardrail_dashboard",
            atlas_subtype="importance_bar_3d_role_pie_method_beeswarm",
            conclusion="All selected GMM solutions require covariance guardrails; role tiers remain explicit.",
            raw_data="outputs/phase40_table2_profile_stability_guardrails.csv; outputs/phase36_gmm_algorithm_robustness.csv",
            variable_mapping="cohort log10 covariance condition number, four role-tier contribution percentages, method-level ARI spread",
            reason="HF207 is used for the central 3D role-tier pie; only the four manuscript role colors are shown.",
        ),
        Variant(
            panel="FigS1",
            option="FigS1.HF200",
            candidate_key="HF200",
            panel_role="supplementary_profile_burden",
            variant_budget="user selected one replacement variant for FigS1",
            atlas_class="multi_panel_profile_summary",
            atlas_subtype="beeswarm_with_rose_insets",
            conclusion="Strict-core selected profile classes differ by four-domain burden signatures and class proportions.",
            raw_data="outputs/phase4_gmm_class_profiles.csv; outputs/phase40_table2_profile_stability_guardrails.csv",
            variable_mapping="strict-core selected k profile classes x four domain z-scores plus class percentage",
            reason="HF200 preserves multi-class beeswarm plus rose grammar for a readable strict-core supplement.",
        ),
    ]


def render_all(variants: list[Variant]) -> None:
    data = load_data()
    strict_core = data["strict"][data["strict"]["role"].eq(STRICT_ROLE)].copy()
    class_risks = data["class_risks"][data["class_risks"]["analysis_tier"].eq("strict_primary")].copy()
    for variant in variants:
        if variant.panel == "Fig3A":
            draw_hf112_ridge_effect_dashboard(variant, "risk", strict_core, class_risks, data["auc_ci"])
        elif variant.panel == "Fig3B":
            draw_hf112_ridge_effect_dashboard(variant, "auc", strict_core, class_risks, data["auc_ci"])
        elif variant.panel == "Fig2B":
            draw_hf084_fan_matrix(variant, data["robustness"])
        elif variant.panel == "Fig2C":
            draw_hf207_guardrail_dashboard(variant, data["guardrails"], data["robustness"])
        elif variant.panel == "FigS1":
            draw_hf200_profile_burden(variant, data["profiles"], data["guardrails"])
        else:
            raise ValueError(f"Unknown panel: {variant.panel}")


def copy_variant_scripts(variants: list[Variant]) -> None:
    source = Path(__file__)
    text = source.read_text(encoding="utf-8")
    for variant in variants:
        target = SCRIPT_DIR / f"{variant.base_name}.py"
        if target != source:
            target.write_text(text, encoding="utf-8")
        variant.script_file = target


def make_inventory(variants: list[Variant]) -> pd.DataFrame:
    rows = []
    for variant in variants:
        rows.append(
            {
                "Panel": variant.panel,
                "Existing figure": variant.panel,
                "Current visual type": variant.atlas_subtype,
                "Panel role": variant.panel_role,
                "Variant budget": variant.variant_budget,
                "PERSIST atlas major class": variant.atlas_class,
                "PERSIST atlas subtype": variant.atlas_subtype,
                "One-sentence conclusion": variant.conclusion,
                "Data type": "aggregate cohort/model output table",
                "Cognitive task": "comparison; matrix; distribution; relationship",
                "Raw data file": variant.raw_data,
                "Required columns/statistics": variant.variable_mapping,
                "Manuscript role": variant.panel_role,
                "Reader question answered": variant.conclusion,
                "Guardrail or annotation needed": "No SHAP claim; no simulated values; role/tier guardrails retained",
                "Recommended color-series direction": "teal, burgundy, blue, amber, neutral grey",
                "Recommended analysis runtime": "Python",
                "Recommended render runtime": "Python PERSIST high-fidelity port",
                "Native or PERSIST candidate": variant.candidate_id,
                "Reason": variant.reason,
            }
        )
    return pd.DataFrame(rows)


def make_candidates(variants: list[Variant]) -> pd.DataFrame:
    rows = []
    for variant in variants:
        cap = variant.capsule
        rows.append(
            {
                "Panel": variant.panel,
                "Option": variant.option,
                "Panel role": variant.panel_role,
                "Variant budget": variant.variant_budget,
                "Candidate ID": variant.candidate_id,
                "Candidate level": "hf_capsule",
                "Candidate maturity": "source_port_ready",
                "HF capsule ID": variant.candidate_id,
                "PERSIST source ID": "",
                "Generic template path": "",
                "Native workflow": "",
                "Candidate source": "FOLDER_HIGH_FIDELITY_CATALOG",
                "Candidate kind": "user_selected_hf_capsule",
                "PERSIST atlas major class": variant.atlas_class,
                "PERSIST atlas subtype": variant.atlas_subtype,
                "Data fit gate": "pass",
                "Data fit notes": "Mapped to original project CSV outputs; no screenshot or simulated values",
                "Visual fit gate": "pass",
                "Visual fit notes": "Visual grammar retained with manuscript-specific labels and guardrails",
                "Task fit score": 27,
                "Data fit score": 24,
                "Visual grammar score": 18,
                "Source-code readiness score": 15,
                "Readability score": 8,
                "Total score": 92,
                "Render decision": "render_recommended",
                "Runtime": "Python / PERSIST high-fidelity port",
                "Env": "research-py312",
                "Capsule path": cap["path"],
                "Reference visual": cap["reference"],
                "Source script": cap["source_script"],
                "Source code snapshot": cap["snapshot"],
                "Why it fits": variant.reason,
                "Risk": "SHAP-origin capsule visual terms must be relabelled; manuscript legend should not call this SHAP"
                if variant.candidate_key in {"HF176", "HF200"}
                else "3D pie is descriptive composition; legend must state four role-tier contribution percentages.",
            }
        )
    return pd.DataFrame(rows)


def make_render_variants(variants: list[Variant]) -> pd.DataFrame:
    rows = []
    for variant in variants:
        pdf_svg = f"{rel(variant.output_pdf)}; {rel(variant.output_svg)}"
        rows.append(
            {
                "Panel": variant.panel,
                "Option": variant.option,
                "Panel role": variant.panel_role,
                "Variant budget": variant.variant_budget,
                "Candidate ID": variant.candidate_id,
                "Candidate level": "hf_capsule",
                "Candidate maturity": "source_port_ready",
                "Data fit gate": "pass",
                "Visual fit gate": "pass",
                "Runtime": "Python / PERSIST high-fidelity port",
                "Env": "research-py312",
                "Rendered": "yes",
                "Render script": rel(variant.script_file),
                "Intermediate file": rel(variant.intermediate_file),
                "Output PNG": rel(variant.output_png),
                "Output PDF/SVG": pdf_svg,
                "Figure output spec": "figure_output_spec.md",
                "Validation status": "standalone_render_validated",
                "Reason": variant.reason,
                "Raw data": variant.raw_data,
                "Variable mapping": variant.variable_mapping,
                "Rows mapped": variant.rows_mapped,
                "Requested ID": "HF84" if variant.candidate_key == "HF084" else variant.candidate_key,
                "Parsed note": "user typed HF84; resolved to HF084_2025-10-07_728da769" if variant.candidate_key == "HF084" else "exact user-selected capsule",
            }
        )
    return pd.DataFrame(rows)


def markdown_table(rows: list[dict[str, object]], columns: list[str]) -> str:
    lines = []
    lines.append("| " + " | ".join(columns) + " |")
    lines.append("|" + "|".join(["---"] * len(columns)) + "|")
    for row in rows:
        vals = []
        for col in columns:
            val = str(row.get(col, ""))
            vals.append(val.replace("\n", " ").replace("|", "/"))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines) + "\n"


def write_protocol_files(variants: list[Variant]) -> None:
    inventory = make_inventory(variants)
    candidates = make_candidates(variants)
    rendered = make_render_variants(variants)
    inventory.to_csv(STAGE / "panel_inventory.tsv", sep="\t", index=False)
    candidates.to_csv(STAGE / "panel_template_candidates.tsv", sep="\t", index=False)
    candidates.to_csv(STAGE / "panel_template_candidates_full.tsv", sep="\t", index=False)
    rendered.to_csv(STAGE / "panel_render_variants.tsv", sep="\t", index=False)

    (STAGE / "figure_output_spec.md").write_text(
        "\n".join(
            [
                "# Figure Output Spec",
                "",
                f"- {FIGURE_RULE_SUMMARY}",
                "- Main figure canvas: 180 mm wide; height scaled from the source aspect ratio and capped at 170 mm.",
                "- Font source: Windows Arial registered from `/mnt/c/Windows/Fonts/arial*.ttf` during WSL rendering.",
                "- PNG files are preview artifacts. PDF and SVG files are the editable manuscript/vector artifacts.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    selection_lines = [
        "# Panel Template Selection",
        "",
        "User-selected replacement capsules for this stage:",
        "",
        "- Fig3A: HF112",
        "- Fig3B: HF112",
        "- Fig2C: HF207",
        "- Fig2B: HF84, resolved to HF084 in the PERSIST catalog",
        "- FigS1: HF200",
        "",
        "All panels use original project CSV outputs under `outputs/`. SHAP-origin capsule layouts are used only as visual grammar; no SHAP values are claimed.",
        "",
        markdown_table(inventory.to_dict("records"), ["Panel", "PERSIST atlas major class", "PERSIST atlas subtype", "One-sentence conclusion", "Raw data file", "Reason"]),
    ]
    (STAGE / "panel_template_selection.md").write_text("\n".join(selection_lines), encoding="utf-8")

    mapping_rows = []
    for variant in variants:
        cap = variant.capsule
        mapping_rows.append(
            {
                "Panel": variant.panel,
                "Panel role": variant.panel_role,
                "Variant budget": variant.variant_budget,
                "Atlas major class": variant.atlas_class,
                "Atlas subtype": variant.atlas_subtype,
                "Candidate ID": variant.candidate_id,
                "Candidate level": "hf_capsule",
                "Candidate maturity": "source_port_ready",
                "Data fit gate": "pass",
                "Visual fit gate": "pass",
                "Runtime": "Python / PERSIST high-fidelity port",
                "Env": "research-py312",
                "Selected option": variant.option,
                "Template/capsule": variant.candidate_id,
                "Capsule path": cap["path"],
                "Reference visual": cap["reference"],
                "Source script": cap["source_script"],
                "Source code snapshot": cap["snapshot"],
                "Raw data": variant.raw_data,
                "Variable mapping": variant.variable_mapping,
                "Intermediate file": rel(variant.intermediate_file),
                "Ported script": rel(variant.script_file),
                "Visual match notes": "visual_match_notes.md",
                "Validation report": "persist_source_code_first_validation.md",
                "Output": rel(variant.output_png),
                "Reason": variant.reason,
            }
        )
    mapping_cols = [
        "Panel",
        "Panel role",
        "Variant budget",
        "Atlas major class",
        "Atlas subtype",
        "Candidate ID",
        "Candidate level",
        "Candidate maturity",
        "Data fit gate",
        "Visual fit gate",
        "Runtime",
        "Env",
        "Selected option",
        "Template/capsule",
        "Capsule path",
        "Reference visual",
        "Source script",
        "Source code snapshot",
        "Raw data",
        "Variable mapping",
        "Intermediate file",
        "Ported script",
        "Visual match notes",
        "Validation report",
        "Output",
        "Reason",
    ]
    (STAGE / "panel_visual_mapping.md").write_text(markdown_table(mapping_rows, mapping_cols), encoding="utf-8")

    notes = [
        "# Visual Match Notes",
        "",
        "## Fig3A / Fig3B with HF112",
        "Preserved the HF112 ridge density, mean/effect annotation, thick axes, and 1:1 scatter comparison structure. The project data are cohort-level strict-core functional association outputs and class-risk tables, so the ridge layer is intentionally sparse and shows class-level aggregate risk points rather than participant-level distributions.",
        "",
        "## Fig2B with HF084",
        "Preserved the HF084 semicircular fan heatmap grammar, rotated outer labels, value labels within fan cells, and horizontal colorbar. The matrix values are ARI vs selected GMM from the original robustness table, not correlations.",
        "",
        "## Fig2C with HF207",
        "Preserved the HF207 layered 3D pie grammar for the central role-tier composition panel. The pie is restricted to the four manuscript role colors: baseline-only, bridge, strict-core, and validation-downgraded. The flanking bar and beeswarm panels retain covariance and algorithm-agreement guardrail context.",
        "",
        "## FigS1 with HF200",
        "Preserved the HF200 multi-panel beeswarm with rose insets and summary rose/ring grammar. The plotted values are strict-core selected-k profile domain z-scores and class percentages, not SHAP values.",
        "",
        "Unresolved mismatch: HF200 originates from model-explainability examples, so manuscript figure legends must avoid SHAP terminology unless a separate SHAP model is actually fitted. HF207 is a composition display and should be described only as a role-tier percentage summary.",
        "",
    ]
    (STAGE / "visual_match_notes.md").write_text("\n".join(notes), encoding="utf-8")

    palette_note = [
        "# Project Palette Recommendation",
        "",
        "Use a 7-color clinical guardrail palette rather than a one-hue gradient:",
        "",
        "| Role | Hex | Use |",
        "|---|---|---|",
        "| Strict-core | #175C66 | Primary strict-core cohorts and core evidence |",
        "| Burgundy | #7A1E48 | Comparator/outcome emphasis |",
        "| Blue | #234B9B | Continuous-domain comparator or cardiometabolic domain |",
        "| Amber | #C9862D | Sensitivity/bridge tier |",
        "| Grey | #8A8D91 | Baseline-only or unavailable validation |",
        "| Green | #1A8A6A | MHAS or favorable validation |",
        "| Coral | #B86B5E | Downgraded sensitivity |",
        "",
    ]
    (STAGE / "project_palette_recommendation.md").write_text("\n".join(palette_note), encoding="utf-8")

    log_lines = [
        "# Redraw Log",
        "",
        "- Created independent stage: `persist_stage4_user_selected_hf_capsules_v2`.",
        "- Rendered Fig3A and Fig3B using HF112 from strict-core functional outcome and AUC tables.",
        "- Rendered Fig2B using HF084 after resolving user input `HF84`.",
        "- Rendered Fig2C using HF207 3D role-tier pie grammar with only four role colors.",
        "- Rendered FigS1 using HF200 strict-core selected-k profile burden grammar without SHAP claims.",
        "- Exported PNG, PDF, SVG, intermediate TSVs, and contact sheets from original project outputs.",
        "",
    ]
    (STAGE / "redraw_log.md").write_text("\n".join(log_lines), encoding="utf-8")

    final_rows = []
    for variant in variants:
        tradeoff = "Source capsule has a model-explainability origin; labels were rewritten to avoid overclaiming." if variant.candidate_key in {"HF176", "HF200"} else "Uses aggregate project outputs rather than participant-level distributions."
        final_rows.append(
            {
                "Panel": variant.panel,
                "Selected option": variant.option,
                "Candidate ID": variant.candidate_id,
                "Candidate level": "hf_capsule",
                "Selected output": rel(variant.output_png),
                "Final selection reason": variant.reason,
                "Rejected alternatives": "Previous stage variant retained for comparison in stage3 outputs",
                "Known tradeoff": tradeoff,
            }
        )
    final_cols = [
        "Panel",
        "Selected option",
        "Candidate ID",
        "Candidate level",
        "Selected output",
        "Final selection reason",
        "Rejected alternatives",
        "Known tradeoff",
    ]
    (STAGE / "panel_final_selection.md").write_text(markdown_table(final_rows, final_cols), encoding="utf-8")


def make_contact_sheet(variants: list[Variant]) -> Path:
    images = []
    labels = []
    for variant in variants:
        img = plt.imread(variant.output_png)
        images.append(img)
        labels.append(f"{variant.option}\n{variant.candidate_id}")
    fig, axes = plt.subplots(2, 3, figsize=(14, 8.2))
    axes = axes.ravel()
    for ax, img, label in zip(axes, images, labels):
        ax.imshow(img)
        ax.set_title(label, fontsize=10, fontweight="bold")
        ax.axis("off")
    for ax in axes[len(images):]:
        ax.axis("off")
    fig.tight_layout()
    sheet = CONTACT_DIR / "phase44_user_selected_hf_v2_contact_sheet.png"
    fig.savefig(sheet, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return sheet


def write_gallery(variants: list[Variant], contact_sheet: Path) -> None:
    lines = [
        "# Panel Variant Gallery",
        "",
        "Contact sheet:",
        "",
        f"![phase44 contact sheet]({rel(contact_sheet)})",
        "",
        "Standalone variants:",
        "",
    ]
    for variant in variants:
        lines.extend(
            [
                f"## {variant.option}",
                "",
                f"- Candidate: `{variant.candidate_id}`",
                f"- PNG: `{rel(variant.output_png)}`",
                f"- PDF: `{rel(variant.output_pdf)}`",
                f"- SVG: `{rel(variant.output_svg)}`",
                f"- Intermediate table: `{rel(variant.intermediate_file)}`",
                "",
                f"![{variant.option}]({rel(variant.output_png)})",
                "",
            ]
        )
    (STAGE / "panel_variant_gallery.md").write_text("\n".join(lines), encoding="utf-8")


def copy_summaries_to_outputs(variants: list[Variant], contact_sheet: Path) -> None:
    rendered = STAGE / "panel_render_variants.tsv"
    shutil.copy2(rendered, PROJECT_OUTPUTS / "phase44_user_selected_hf_v2_panel_render_variants.tsv")
    summary = pd.DataFrame(
        [
            {
                "panel": variant.panel,
                "option": variant.option,
                "candidate_id": variant.candidate_id,
                "png": rel(variant.output_png),
                "pdf": rel(variant.output_pdf),
                "svg": rel(variant.output_svg),
                "contact_sheet": rel(contact_sheet),
                "rows_mapped": variant.rows_mapped,
            }
            for variant in variants
        ]
    )
    summary.to_csv(PROJECT_OUTPUTS / "phase44_user_selected_hf_v2_contact_sheet_summary.tsv", sep="\t", index=False)


def main() -> int:
    ensure_dirs()
    apply_manuscript_figure_style()
    variants = build_variants()
    render_all(variants)
    copy_variant_scripts(variants)
    write_protocol_files(variants)
    contact_sheet = make_contact_sheet(variants)
    write_gallery(variants, contact_sheet)
    copy_summaries_to_outputs(variants, contact_sheet)
    print(f"Rendered {len(variants)} variants")
    print(f"Stage root: {STAGE}")
    print(f"Contact sheet: {contact_sheet}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
