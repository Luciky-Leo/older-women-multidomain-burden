"""SOURCE_CODE_FIRST renderer for Phase 49 enhanced Fig1 and Fig3.

PERSIST_SOURCE_CODE_FIRST_PROTOCOL:
- VISUAL_REFERENCES: enhanced cohort alluvial attrition figure and clinical
  impact forest/quadrant figure requested after Phase48 review.
- SOURCE_CODE_SNAPSHOT: Phase48 project renderer plus native statistical
  matplotlib workflows; no simulated data are used.
- PORTING_PROMPT: bind the visual grammar to current manuscript CSVs and keep
  PDF/SVG text editable.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import to_rgb
from matplotlib.gridspec import GridSpec
from matplotlib.patches import FancyBboxPatch, PathPatch, Rectangle
from matplotlib.path import Path as MplPath


ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / "manuscript" / "bmc_geriatrics_submission_ready_20260605"
LEGACY_PKG = ROOT / "manuscript" / "bmc_geriatrics_submission_burden_profiles_rescue"
REDRAW = ROOT / "figure_redraw" / "phase49_fig1_3_enhanced_visual_power"
OUT = REDRAW / "outputs"
TABLES = REDRAW / "intermediate_tables"

COHORT_ORDER = ["CHARLS", "ELSA", "HRS", "KLoSA", "LASI", "MHAS", "SHARE"]
PALETTE = {
    "Strict-core": "#176C73",
    "Functional bridge sensitivity": "#D08B1E",
    "Baseline-only descriptive": "#91979C",
    "Validation-downgraded sensitivity": "#BD6D61",
}
LOSS = "#D7DCE0"
LOSS_DARK = "#9AA1A7"
GRID = "#E5E7EB"
TEXT = "#111827"
SUBTLE = "#6B7280"

TABLE_SOURCE_MAP = {
    "additional_file_12_baseline_clinical_design_covariate_availability.csv": (
        "additional_file_1_harmonization_and_cohort_construction.xlsx",
        "baseline_covariates",
    ),
    "additional_file_14_strict_core_lfo_functional_change_association.csv": (
        "additional_file_3_lfo_functional_change_associations.xlsx",
        "strict_core_lfo",
    ),
    "additional_file_15_lfo_sensitivity_rows_removed_from_main.csv": (
        "additional_file_3_lfo_functional_change_associations.xlsx",
        "lfo_sensitivity",
    ),
    "additional_file_18_auc_bootstrap_intervals.csv": (
        "additional_file_3_lfo_functional_change_associations.xlsx",
        "auc_bootstrap",
    ),
}


def setup() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)
    mpl.rcParams.update(
        {
            "font.family": "Arial",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "font.size": 7,
            "axes.linewidth": 0.75,
            "axes.edgecolor": TEXT,
            "xtick.major.width": 0.55,
            "ytick.major.width": 0.55,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
        }
    )


def mm_to_in(width_mm: float, height_mm: float) -> tuple[float, float]:
    return width_mm / 25.4, height_mm / 25.4


def read_csv(name: str) -> pd.DataFrame:
    if name in TABLE_SOURCE_MAP:
        xlsx_name, sheet = TABLE_SOURCE_MAP[name]
        xlsx_path = PKG / xlsx_name
        if xlsx_path.exists():
            return pd.read_excel(xlsx_path, sheet_name=sheet)
    csv_path = PKG / name
    if csv_path.exists():
        return pd.read_csv(csv_path)
    legacy_csv_path = LEGACY_PKG / name
    if legacy_csv_path.exists():
        return pd.read_csv(legacy_csv_path)
    raise FileNotFoundError(f"Could not locate {name} in {PKG} or {LEGACY_PKG}")


def role_color(role: str) -> str:
    return PALETTE.get(role, "#176C73")


def parse_ci(text: str) -> tuple[float, float]:
    nums = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", str(text))]
    if len(nums) >= 2:
        return nums[0], nums[1]
    return (math.nan, math.nan)


def band(ax, x0, x1, y0b, y0t, y1b, y1t, color, alpha=1.0, zorder=1, ec="none"):
    dx = (x1 - x0) * 0.48
    verts = [
        (x0, y0b),
        (x0 + dx, y0b),
        (x1 - dx, y1b),
        (x1, y1b),
        (x1, y1t),
        (x1 - dx, y1t),
        (x0 + dx, y0t),
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
    ax.add_patch(
        PathPatch(
            MplPath(verts, codes),
            facecolor=color,
            edgecolor=ec,
            linewidth=0.35,
            alpha=alpha,
            zorder=zorder,
        )
    )


def lighten(color: str, amount: float = 0.76) -> tuple[float, float, float]:
    base = np.array(to_rgb(color))
    white = np.array([1.0, 1.0, 1.0])
    return tuple(base * (1 - amount) + white * amount)


def fmt_n(value: float | int) -> str:
    return f"{int(round(float(value))):,}"


def draw_chip(ax, x: float, y: float, text: str, face: str = "white", edge: str = GRID, color: str = TEXT, size: float = 5.4) -> None:
    ax.text(
        x,
        y,
        text,
        ha="center",
        va="center",
        fontsize=size,
        color=color,
        zorder=9,
        bbox={"boxstyle": "round,pad=0.16", "facecolor": face, "edgecolor": edge, "linewidth": 0.45},
    )


def draw_stage_header(ax, x: float, title: str, total: int, width: float = 0.18) -> None:
    ax.add_patch(
        FancyBboxPatch(
            (x - width / 2, 0.905),
            width,
            0.056,
            boxstyle="round,pad=0.004,rounding_size=0.012",
            facecolor="#FFFFFF",
            edgecolor="#E6E9EE",
            lw=0.75,
            zorder=8,
        )
    )
    ax.text(x, 0.942, title, ha="center", va="center", fontsize=7.4, fontweight="bold", color=TEXT, zorder=9)
    ax.text(x, 0.918, f"n={fmt_n(total)}", ha="center", va="center", fontsize=5.7, color=SUBTLE, zorder=9)


def draw_node(ax, x: float, y: float, h: float, color: str, width: float = 0.024, zorder: int = 6) -> None:
    ax.add_patch(
        FancyBboxPatch(
            (x - width / 2 + 0.002, y - h / 2 - 0.002),
            width,
            h,
            boxstyle="round,pad=0,rounding_size=0.006",
            facecolor="#000000",
            edgecolor="none",
            alpha=0.08,
            zorder=zorder - 1,
        )
    )
    ax.add_patch(
        FancyBboxPatch(
            (x - width / 2, y - h / 2),
            width,
            h,
            boxstyle="round,pad=0,rounding_size=0.006",
            facecolor=color,
            edgecolor="white",
            lw=0.85,
            zorder=zorder,
        )
    )


def build_flow_table() -> pd.DataFrame:
    base = read_csv("additional_file_12_baseline_clinical_design_covariate_availability.csv")
    main = read_csv("additional_file_14_strict_core_lfo_functional_change_association.csv")
    sens = read_csv("additional_file_15_lfo_sensitivity_rows_removed_from_main.csv")
    lfo = pd.concat([main, sens], ignore_index=True)[["cohort", "lfo_model_n", "events"]]
    df = base.merge(lfo, on="cohort", how="left")
    df["lfo_model_n"] = df["lfo_model_n"].fillna(0).astype(int)
    df["events"] = df["events"].fillna(np.nan)
    df["domain_loss_n"] = (df["source_women50_n"] - df["complete_four_domain_n"]).clip(lower=0)
    df["lfo_loss_n"] = (df["complete_four_domain_n"] - df["lfo_model_n"]).clip(lower=0)
    df["source_to_lfo_pct"] = np.where(df["source_women50_n"] > 0, 100 * df["lfo_model_n"] / df["source_women50_n"], np.nan)
    df["complete_to_lfo_pct"] = np.where(df["complete_four_domain_n"] > 0, 100 * df["lfo_model_n"] / df["complete_four_domain_n"], np.nan)
    df["cohort"] = pd.Categorical(df["cohort"], COHORT_ORDER, ordered=True)
    df = df.sort_values("cohort").reset_index(drop=True)
    df.to_csv(TABLES / "fig1_enhanced_alluvial_attrition_input_mapped.tsv", sep="\t", index=False)
    return df


def build_claim_lock_table(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in df.iterrows():
        role = row["role"]
        lfo_available = int(row["lfo_model_n"]) > 0
        rows.append(
            {
                "cohort": row["cohort"],
                "role": role,
                "construction": "yes",
                "strict_lfo_validation": "yes" if role == "Strict-core" and lfo_available else "no",
                "sensitivity_validation": "yes"
                if role in {"Functional bridge sensitivity", "Validation-downgraded sensitivity"} and lfo_available
                else "no",
                "baseline_only_or_unavailable": "yes" if role == "Baseline-only descriptive" or not lfo_available else "no",
                "claim_boundary": (
                    "strict LFO validation"
                    if role == "Strict-core" and lfo_available
                    else "sensitivity only"
                    if role in {"Functional bridge sensitivity", "Validation-downgraded sensitivity"} and lfo_available
                    else "baseline construction only"
                ),
            }
        )
    claim = pd.DataFrame(rows)
    claim.to_csv(TABLES / "fig1B_claim_boundary_lock_input_mapped.tsv", sep="\t", index=False)
    return claim


def draw_fig1a(ax, df: pd.DataFrame) -> None:
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    x_source, x_complete, x_lfo = 0.18, 0.49, 0.75
    max_n = df["source_women50_n"].max()
    max_h = 0.082
    y_positions = np.linspace(0.80, 0.24, len(df))

    ax.text(0.004, 0.985, "A", ha="left", va="top", fontsize=8, fontweight="bold", color=TEXT, transform=ax.transAxes)
    ax.add_patch(
        FancyBboxPatch(
            (0.030, 0.092),
            0.925,
            0.810,
            boxstyle="round,pad=0.002,rounding_size=0.018",
            facecolor="#FBFCFD",
            edgecolor="#ECEFF3",
            lw=0.70,
            zorder=-6,
        )
    )
    for x in [x_source, x_complete, x_lfo]:
        ax.plot([x, x], [0.165, 0.880], color="#DDE3EA", lw=0.85, zorder=-2, solid_capstyle="round")

    draw_stage_header(ax, x_source, "Women 50+ screen", int(df["source_women50_n"].sum()), width=0.170)
    draw_stage_header(ax, x_complete, "Four-domain complete", int(df["complete_four_domain_n"].sum()), width=0.196)
    draw_stage_header(ax, x_lfo, "LFO model set", int(df["lfo_model_n"].sum()), width=0.158)
    ax.text(0.925, 0.936, "Events", ha="center", va="center", fontsize=7.1, fontweight="bold", color=TEXT, zorder=9)
    ax.text(0.925, 0.914, f"n={fmt_n(df['events'].fillna(0).sum())}", ha="center", va="center", fontsize=5.6, color=SUBTLE, zorder=9)

    for y in y_positions:
        ax.plot([0.070, 0.925], [y, y], color="#EEF1F4", lw=0.75, zorder=-3, solid_capstyle="round")

    for _, row in df.iterrows():
        y = y_positions[int(row.name)]
        col = role_color(row["role"])
        light_col = lighten(col, 0.70)
        source_h = max(row["source_women50_n"] / max_n * max_h, 0.014)
        complete_h = max(row["complete_four_domain_n"] / max_n * max_h, 0.010)
        lfo_h = max(row["lfo_model_n"] / max_n * max_h, 0.006) if row["lfo_model_n"] > 0 else 0

        # The pale under-ribbons carry the starting denominator; colored ribbons show retained analysis sets.
        band(ax, x_source, x_complete, y - source_h / 2, y + source_h / 2, y - source_h / 2, y + source_h / 2, LOSS, 0.58, zorder=1)
        band(
            ax,
            x_source,
            x_complete,
            y - complete_h / 2,
            y + complete_h / 2,
            y - complete_h / 2,
            y + complete_h / 2,
            col,
            0.80,
            zorder=3,
            ec=light_col,
        )
        band(ax, x_complete, x_lfo, y - complete_h / 2, y + complete_h / 2, y - complete_h / 2, y + complete_h / 2, LOSS, 0.52, zorder=1)
        if row["lfo_model_n"] > 0:
            band(
                ax,
                x_complete,
                x_lfo,
                y - lfo_h / 2,
                y + lfo_h / 2,
                y - lfo_h / 2,
                y + lfo_h / 2,
                col,
                0.86,
                zorder=4,
                ec=light_col,
            )

        draw_node(ax, x_source, y, source_h, col, width=0.026, zorder=6)
        draw_node(ax, x_complete, y, complete_h, col, width=0.026, zorder=6)
        if row["lfo_model_n"] > 0:
            draw_node(ax, x_lfo, y, lfo_h, col, width=0.026, zorder=7)
        else:
            ax.plot([x_lfo - 0.017, x_lfo + 0.017], [y, y], color=LOSS_DARK, lw=2.1, zorder=7, solid_capstyle="round")

        ax.text(0.071, y, str(row["cohort"]), ha="right", va="center", fontsize=7.6, color=TEXT, fontweight="bold")
        draw_chip(ax, 0.122, y, fmt_n(row["source_women50_n"]), face="white", edge="#E4E7EC", color=TEXT, size=5.25)
        draw_chip(
            ax,
            x_complete + 0.060,
            y + complete_h / 2 + 0.012,
            f"{row['complete_four_domain_pct']:.1f}%",
            face="#FFFFFF",
            edge="#E4E7EC",
            color=SUBTLE,
            size=5.05,
        )
        if int(row["domain_loss_n"]) > 0:
            draw_chip(
                ax,
                (x_source + x_complete) / 2,
                y + source_h / 2 + 0.014,
                f"-{fmt_n(row['domain_loss_n'])}",
                face="#F3F5F7",
                edge="#E0E4E8",
                color=SUBTLE,
                size=4.75,
            )
        if int(row["lfo_loss_n"]) > 0:
            loss_label = "unavailable" if int(row["lfo_model_n"]) == 0 else f"-{fmt_n(row['lfo_loss_n'])}"
            draw_chip(
                ax,
                (x_complete + x_lfo) / 2,
                y - complete_h / 2 - 0.014,
                loss_label,
                face="#F3F5F7",
                edge="#E0E4E8",
                color=SUBTLE,
                size=4.75,
            )
        if row["lfo_model_n"] > 0:
            ev = int(row["events"]) if not pd.isna(row["events"]) else 0
            label = f"{fmt_n(row['lfo_model_n'])} ({row['source_to_lfo_pct']:.1f}%)\n{fmt_n(ev)} events"
            label_color = TEXT
        else:
            label = "LFO\nunavailable"
            label_color = SUBTLE
        ax.text(x_lfo + 0.032, y, label, ha="left", va="center", fontsize=5.75, color=label_color, linespacing=1.18)

    legend_items = [
        ("Strict-core", PALETTE["Strict-core"]),
        ("Bridge sensitivity", PALETTE["Functional bridge sensitivity"]),
        ("Baseline-only", PALETTE["Baseline-only descriptive"]),
        ("Validation-downgraded", PALETTE["Validation-downgraded sensitivity"]),
        ("Attrition / unavailable", LOSS),
    ]
    lx = 0.166
    for label, color in legend_items:
        ax.add_patch(
            FancyBboxPatch(
                (lx, 0.058),
                0.022,
                0.014,
                boxstyle="round,pad=0,rounding_size=0.004",
                facecolor=color,
                edgecolor="none",
                alpha=0.92,
            )
        )
        ax.text(lx + 0.027, 0.065, label, ha="left", va="center", fontsize=5.75, color=TEXT)
        lx += 0.128 if label != "Validation-downgraded" else 0.176

    ax.text(
        0.50,
        0.024,
        "Ribbon height is proportional to participant count; grey badges mark loss between analytic stages.",
        ha="center",
        va="center",
        fontsize=5.75,
        color=SUBTLE,
    )


def membership_matrix(claim: pd.DataFrame) -> pd.DataFrame:
    mat = pd.DataFrame(
        {
            "Construction": (claim["construction"] == "yes").astype(int),
            "Strict LFO": (claim["strict_lfo_validation"] == "yes").astype(int),
            "Sensitivity": (claim["sensitivity_validation"] == "yes").astype(int),
            "Baseline-only": (claim["baseline_only_or_unavailable"] == "yes").astype(int),
        }
    )
    mat.index = claim["cohort"].astype(str).values
    mat.to_csv(TABLES / "fig1B_tier_membership_matrix_input_mapped.tsv", sep="\t")
    return mat


def draw_fig1b_tier_heatmap(ax, claim: pd.DataFrame) -> None:
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.0, 0.98, "B", ha="left", va="top", fontsize=8, fontweight="bold", color=TEXT)
    ax.text(0.50, 0.94, "Analytic tier membership", ha="center", va="top", fontsize=7.1, fontweight="bold", color=TEXT)

    mat = membership_matrix(claim)
    role_lookup = dict(zip(claim["cohort"].astype(str), claim["role"].astype(str)))
    x0, y_top = 0.34, 0.70
    cell_w, cell_h = 0.125, 0.073
    row_label_x, anno_x = 0.205, 0.270

    ax.text(anno_x + 0.018, 0.805, "Evidence", ha="center", va="bottom", fontsize=5.4, color=SUBTLE)
    for j, col in enumerate(mat.columns):
        x = x0 + j * cell_w
        ax.text(x + cell_w / 2, 0.805, col, ha="center", va="bottom", fontsize=5.7, color=TEXT, fontweight="bold")
        ax.text(x + cell_w / 2, 0.735, f"n={int(mat[col].sum())}", ha="center", va="bottom", fontsize=5.1, color=SUBTLE)

    for i, cohort in enumerate(mat.index):
        y = y_top - i * cell_h
        role = role_lookup[cohort]
        role_col = role_color(role)
        ax.text(row_label_x, y, cohort, ha="right", va="center", fontsize=5.8, color=TEXT)
        ax.add_patch(
            Rectangle(
                (anno_x, y - cell_h * 0.36),
                0.036,
                cell_h * 0.72,
                facecolor=role_col,
                edgecolor="white",
                lw=0.55,
            )
        )
        for j, col in enumerate(mat.columns):
            x = x0 + j * cell_w
            included = int(mat.loc[cohort, col]) == 1
            ax.add_patch(
                Rectangle(
                    (x, y - cell_h * 0.42),
                    cell_w * 0.96,
                    cell_h * 0.84,
                    facecolor=role_col if included else "#F1F3F5",
                    edgecolor="white",
                    lw=1.0,
                )
            )
            if included:
                ax.text(x + cell_w * 0.48, y, "+", ha="center", va="center", fontsize=7.2, color="white", fontweight="bold")

    ax.text(
        0.50,
        0.060,
        "Cells indicate whether each cohort contributes to a given analysis tier; fill color follows evidence tier.",
        ha="center",
        va="center",
        fontsize=5.7,
        color=SUBTLE,
    )


def draw_fig1b_upset(ax, claim: pd.DataFrame) -> None:
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.0, 0.98, "B", ha="left", va="top", fontsize=8, fontweight="bold", color=TEXT)
    ax.text(0.50, 0.94, "Analytic tier intersections", ha="center", va="top", fontsize=7.1, fontweight="bold", color=TEXT)

    mat = membership_matrix(claim)
    intersections = [
        ("Strict LFO", ["Construction", "Strict LFO"], mat.index[(mat["Construction"] == 1) & (mat["Strict LFO"] == 1)].tolist()),
        ("Sensitivity", ["Construction", "Sensitivity"], mat.index[(mat["Construction"] == 1) & (mat["Sensitivity"] == 1)].tolist()),
        ("Baseline-only", ["Construction", "Baseline-only"], mat.index[(mat["Construction"] == 1) & (mat["Baseline-only"] == 1)].tolist()),
    ]
    upset_rows = ["Construction", "Strict LFO", "Sensitivity", "Baseline-only"]
    set_sizes = mat[upset_rows].sum().astype(int).to_dict()

    x_bar0, x_bar1 = 0.105, 0.255
    y_rows = np.linspace(0.44, 0.17, len(upset_rows))
    for row_name, y in zip(upset_rows, y_rows):
        ax.text(0.095, y, row_name, ha="right", va="center", fontsize=5.5, color=TEXT)
        ax.plot([x_bar0, x_bar1], [y, y], color="#EEF0F2", lw=5.0, solid_capstyle="round", zorder=1)
        ax.plot([x_bar0, x_bar0 + (x_bar1 - x_bar0) * set_sizes[row_name] / len(mat)], [y, y], color="#4B5563", lw=5.0, solid_capstyle="round", zorder=2)
        ax.text(x_bar1 + 0.012, y, str(set_sizes[row_name]), ha="left", va="center", fontsize=5.4, color=SUBTLE)
    ax.text((x_bar0 + x_bar1) / 2, 0.56, "Set size", ha="center", va="center", fontsize=5.2, color=SUBTLE)

    x_positions = [0.45, 0.63, 0.81]
    max_count = max(len(cohorts) for _, _, cohorts in intersections)
    for x, (label, members, cohorts) in zip(x_positions, intersections):
        count = len(cohorts)
        bar_h = 0.22 * count / max_count
        ax.add_patch(Rectangle((x - 0.032, 0.58), 0.064, bar_h, facecolor="#176C73", edgecolor="none", alpha=0.95))
        ax.text(x, 0.58 + bar_h + 0.035, str(count), ha="center", va="bottom", fontsize=6.0, color=TEXT, fontweight="bold")
        ax.text(x, 0.525, label, ha="center", va="top", fontsize=5.3, color=TEXT, fontweight="bold")

        filled_rows = [upset_rows.index(member) for member in members]
        if filled_rows:
            y0 = y_rows[min(filled_rows)]
            y1 = y_rows[max(filled_rows)]
            ax.plot([x, x], [y0, y1], color=TEXT, lw=1.25, zorder=3, solid_capstyle="round")
        for k, y in enumerate(y_rows):
            active = upset_rows[k] in members
            ax.scatter(
                [x],
                [y],
                s=42 if active else 22,
                facecolor=TEXT if active else "#D1D5DB",
                edgecolor="white",
                linewidth=0.45,
                zorder=4,
            )
        code = " ".join(c[:2].upper() for c in cohorts)
        ax.text(x, 0.085, code, ha="center", va="center", fontsize=5.2, color=SUBTLE)

    ax.text(
        0.50,
        0.004,
        "UpSet columns show cohort intersections across construction, strict LFO, sensitivity and baseline-only tiers.",
        ha="center",
        va="bottom",
        fontsize=5.5,
        color=SUBTLE,
    )


def render_fig1_variant(df: pd.DataFrame, claim: pd.DataFrame, variant: str, stem: str, write_legacy: bool = False) -> None:
    fig = plt.figure(figsize=mm_to_in(180, 160))
    ax = fig.add_axes([0.02, 0.30, 0.96, 0.67])
    draw_fig1a(ax, df)
    axb = fig.add_axes([0.045, 0.035, 0.91, 0.235])
    if variant == "tierheatmap":
        draw_fig1b_tier_heatmap(axb, claim)
    elif variant == "upset":
        draw_fig1b_upset(axb, claim)
    else:
        raise ValueError(f"Unknown Fig1B variant: {variant}")
    for ext in ["png", "pdf", "svg"]:
        fig.savefig(OUT / f"{stem}.{ext}", dpi=300, bbox_inches="tight")
        if write_legacy:
            fig.savefig(OUT / f"figure1_enhanced_alluvial_attrition_phase49.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)


def render_fig1() -> None:
    df = build_flow_table()
    claim = build_claim_lock_table(df)
    render_fig1_variant(df, claim, "tierheatmap", "figure1_enhanced_alluvial_tierheatmap_phase50", write_legacy=True)
    render_fig1_variant(df, claim, "upset", "figure1_enhanced_alluvial_upset_phase50")


def build_fig3_table() -> pd.DataFrame:
    df = read_csv("additional_file_14_strict_core_lfo_functional_change_association.csv")
    auc = read_csv("additional_file_18_auc_bootstrap_intervals.csv")
    df = df.merge(auc, on="cohort", how="left")
    rows = []
    for _, row in df.iterrows():
        rr_low, rr_high = parse_ci(row["adjusted_risk_ratio_ci"])
        rd_low, rd_high = parse_ci(row["crude_risk_difference_ci_pct"])
        da_low, da_high = parse_ci(row["delta_auc_ci"])
        rows.append(
            {
                **row.to_dict(),
                "rr_low": rr_low,
                "rr_high": rr_high,
                "rd_low": rd_low,
                "rd_high": rd_high,
                "delta_auc_low": da_low,
                "delta_auc_high": da_high,
            }
        )
    out = pd.DataFrame(rows)
    out["cohort"] = pd.Categorical(out["cohort"], ["CHARLS", "ELSA", "HRS", "MHAS"], ordered=True)
    out = out.sort_values("cohort").reset_index(drop=True)
    out.to_csv(TABLES / "fig3_enhanced_clinical_impact_input_mapped.tsv", sep="\t", index=False)
    return out


def size_from_n(values: pd.Series) -> np.ndarray:
    v = values.astype(float)
    return 82 + 270 * (v - v.min()) / max(v.max() - v.min(), 1)


def render_fig3() -> None:
    df = build_fig3_table()
    fig = plt.figure(figsize=mm_to_in(180, 142))
    gs = GridSpec(1, 3, figure=fig, width_ratios=[1.02, 1.68, 1.42], wspace=0.40)
    ax_f = fig.add_subplot(gs[0, 0])
    ax_t = fig.add_subplot(gs[0, 1])
    ax_s = fig.add_subplot(gs[0, 2])

    y = np.arange(len(df))[::-1]
    sizes = size_from_n(df["lfo_model_n"])
    teal = PALETTE["Strict-core"]
    for yi in y:
        ax_f.axhspan(yi - 0.5, yi + 0.5, color="#F8FAFC" if yi % 2 == 0 else "white", zorder=0)
    x = df["adjusted_risk_ratio"].to_numpy()
    lo = df["rr_low"].to_numpy()
    hi = df["rr_high"].to_numpy()
    ax_f.errorbar(x, y, xerr=[x - lo, hi - x], fmt="none", ecolor=teal, elinewidth=1.55, capsize=0, zorder=2)
    ax_f.scatter(x, y, s=sizes, color=teal, edgecolor="white", linewidth=1.05, zorder=3)
    ax_f.axvline(1, color="#6B7280", lw=1.05, ls="--")
    ax_f.set_yticks(y)
    ax_f.set_yticklabels(df["cohort"], fontsize=7.5)
    ax_f.set_xlabel("Adjusted RR", fontsize=8)
    ax_f.set_xlim(0.75, 2.05)
    ax_f.set_ylim(-0.65, len(df) - 0.35)
    ax_f.grid(axis="x", color=GRID, lw=0.70)
    ax_f.text(-0.13, 1.03, "A", transform=ax_f.transAxes, fontsize=8, fontweight="bold")
    ax_f.spines[["top", "right"]].set_visible(False)

    ax_t.set_xlim(0, 1)
    ax_t.set_ylim(-0.65, len(df) - 0.35)
    ax_t.axis("off")
    headers = ["N/events", "Ref %", "High %", "adj RR", "Delta AUC"]
    xs = [0.10, 0.37, 0.54, 0.70, 0.91]
    for xx, h in zip(xs, headers):
        ax_t.text(xx, len(df) - 0.15, h, ha="center", va="bottom", fontsize=5.7, fontweight="bold", color=TEXT)
    for idx, row in df.iterrows():
        yi = y[idx]
        if yi % 2 == 0:
            ax_t.axhspan(yi - 0.5, yi + 0.5, color="#F8FAFC", zorder=0)
        ax_t.plot([0, 1], [yi - 0.5, yi - 0.5], color=GRID, lw=0.60)
        ax_t.text(xs[0], yi, f"{int(row['lfo_model_n'])}/{int(row['events'])}", va="center", ha="center", fontsize=5.7)
        ax_t.text(xs[1], yi, f"{row['reference_event_pct']:.1f}", va="center", ha="center", fontsize=5.7)
        ax_t.text(xs[2], yi, f"{row['highest_event_pct']:.1f}", va="center", ha="center", fontsize=5.7)
        ax_t.text(xs[3], yi, f"{row['adjusted_risk_ratio']:.2f}", va="center", ha="center", fontsize=5.7)
        ax_t.text(xs[4], yi, f"{row['delta_auc_profile_minus_continuous']:.3f}", va="center", ha="center", fontsize=5.7, color="#9B2C2C")

    sx = df["crude_risk_difference_pct"].to_numpy()
    sxlo = df["rd_low"].to_numpy()
    sxhi = df["rd_high"].to_numpy()
    sy = df["delta_auc_profile_minus_continuous"].to_numpy()
    sylo = df["delta_auc_low"].to_numpy()
    syhi = df["delta_auc_high"].to_numpy()
    xmid = np.nanmedian(sx)
    ax_s.axhspan(min(sylo) - 0.004, 0, color="#FEE2E2", alpha=0.28, zorder=0)
    ax_s.axvspan(xmid, max(sxhi) + 2, color="#ECFDF5", alpha=0.35, zorder=0)
    ax_s.axhline(0, color="#6B7280", ls="--", lw=1.05)
    ax_s.axvline(xmid, color="#9CA3AF", ls=":", lw=1.05)
    ax_s.errorbar(sx, sy, xerr=[sx - sxlo, sxhi - sx], yerr=[sy - sylo, syhi - sy], fmt="none", ecolor=teal, elinewidth=1.25, alpha=0.82, zorder=2)
    ax_s.scatter(sx, sy, s=sizes, color=teal, edgecolor="white", linewidth=1.05, zorder=3)
    for _, row in df.iterrows():
        ax_s.text(row["crude_risk_difference_pct"] + 0.30, row["delta_auc_profile_minus_continuous"] + 0.0004, row["cohort"], fontsize=6.4, color=TEXT)
    ax_s.text(0.98, 0.94, "higher risk\nno AUC gain", transform=ax_s.transAxes, ha="right", va="top", fontsize=6.2, color="#9B2C2C")
    ax_s.text(0.02, 0.97, "B", transform=ax_s.transAxes, fontsize=8, fontweight="bold")
    ax_s.set_xlabel("Risk difference, percentage points", fontsize=8)
    ax_s.set_ylabel("")
    ax_s.text(0.03, 0.97, "Delta AUC", transform=ax_s.transAxes, ha="left", va="top", fontsize=6.2, color=SUBTLE)
    ax_s.grid(color=GRID, lw=0.70)
    ax_s.spines[["top"]].set_visible(False)
    ax_s.set_xlim(min(sxlo) - 2, max(sxhi) + 2)
    ax_s.set_ylim(min(sylo) - 0.004, 0.004)

    for ext in ["png", "pdf", "svg"]:
        fig.savefig(OUT / f"figure3_enhanced_clinical_forest_quadrant_phase49.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)


def write_protocol_files() -> None:
    # Fig2 rows are appended/overwritten by the R script after rendering.
    spec = """
# Phase49 Figure Output Spec

- Target width: 180 mm.
- Maximum height used: 160 mm.
- Font: Arial.
- Normal text: 7 pt.
- Panel label: 8 pt bold upright.
- Matplotlib: rcParams["pdf.fonttype"] = 42 and rcParams["svg.fonttype"] = "none".
- Outputs: editable SVG/PDF plus 300 dpi PNG previews.
"""
    (REDRAW / "figure_output_spec.md").write_text(spec.strip() + "\n", encoding="utf-8")
    log = """
# Phase49 Redraw Log

- Skill: biomed-figure-redraw.
- Data policy: all rendered panels use current project CSVs; no simulated data.
- Fig1: enhanced alluvial-style participant flow with pale attrition streams and event/retention annotations; Fig1B is rendered as both tier-membership heatmap and UpSet variants.
- Fig2: rendered separately in R because Panel B is specified as ComplexHeatmap; Panel D uses a direct stability decision quadrant.
- Fig3: enhanced clinical forest plus quadrant decision scatter for risk difference versus Delta AUC.
"""
    (REDRAW / "redraw_log.md").write_text(log.strip() + "\n", encoding="utf-8")


def main() -> None:
    setup()
    render_fig1()
    render_fig3()
    write_protocol_files()
    print(OUT / "figure1_enhanced_alluvial_attrition_phase49.svg")
    print(OUT / "figure1_enhanced_alluvial_tierheatmap_phase50.svg")
    print(OUT / "figure1_enhanced_alluvial_upset_phase50.svg")
    print(OUT / "figure3_enhanced_clinical_forest_quadrant_phase49.svg")


if __name__ == "__main__":
    main()
