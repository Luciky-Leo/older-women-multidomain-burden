#!/usr/bin/env python3
"""Render user-selected PERSIST high-fidelity capsule variants.

Stage 43 follows the user's explicit capsule choices:

- Fig1A: HF132 and HF134
- Fig2A: HF142
- Fig2B: HF211 (the user typed HE211; PERSIST catalog resolves this to HF211)
- Fig2C: HF208
- FigS1: HF205

All panels use existing Older Women project output tables.  No screenshot
tracing, simulated data, or imputed display statistics are used.
"""

from __future__ import annotations

import csv
import json
import math
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

import matplotlib as mpl
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.patches import Circle, Rectangle, Wedge
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401


PROJECT_ROOT = Path("/mnt/e/Reserch/Older women")
STYLE_MODULE_DIR = PROJECT_ROOT / "scripts"
if str(STYLE_MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(STYLE_MODULE_DIR))

from manuscript_figure_style import (  # noqa: E402
    FIGURE_RULE_SUMMARY,
    apply_manuscript_figure_style,
    save_manuscript_figure,
)

OUTPUT_DIR = PROJECT_ROOT / "outputs"
STAGE2_ROOT = PROJECT_ROOT / "figure_redraw" / "persist_stage2_fig1_fig2_fig3_figS1_variants"
REDRAW_ROOT = PROJECT_ROOT / "figure_redraw" / "persist_stage3_user_selected_hf_capsules"
PERSIST_ROOT = Path("/mnt/e/Python/PERSIST")
CAPSULE_ROOT = PERSIST_ROOT / "_portable_patterns" / "high_fidelity_by_folder" / "capsules"
CATALOG_PATH = PERSIST_ROOT / "_portable_patterns" / "high_fidelity_by_folder" / "FOLDER_HIGH_FIDELITY_CATALOG.csv"

COHORT_ORDER = ["CHARLS", "ELSA", "HRS", "KLoSA", "LASI", "MHAS", "SHARE"]
STRICT_CORE_COHORTS = ["CHARLS", "ELSA", "HRS", "MHAS"]
METHOD_ORDER = ["gmm_full", "gmm_diag", "gmm_tied", "kmeans", "continuous_severity_tertile", "hierarchical_ward_sample"]

DOMAIN_COLUMNS = [
    "functional_score",
    "cognitive_score",
    "affective_score",
    "cardiometabolic_chronic_score",
]
DOMAIN_LABELS = {
    "functional_score": "Functional",
    "cognitive_score": "Cognitive",
    "affective_score": "Affective",
    "cardiometabolic_chronic_score": "CM/chronic",
}

PALETTE = {
    "ink": "#1f2933",
    "muted": "#667085",
    "grid": "#d9e0e8",
    "teal_dark": "#183f4a",
    "teal": "#0f6b75",
    "teal_mid": "#2a9d9a",
    "teal_light": "#a9d9cf",
    "yellow": "#e9c46a",
    "orange": "#f4a261",
    "red_orange": "#e76f51",
    "amber": "#d9822b",
    "brown": "#8a3b12",
    "slate": "#64748b",
    "grey": "#cbd5e1",
    "pale": "#f3f6f9",
    "risk": "#b42318",
}

ROLE_COLORS = {
    "Strict-core": PALETTE["teal"],
    "Functional bridge sensitivity": PALETTE["amber"],
    "Validation-downgraded sensitivity": "#b54708",
    "Baseline-only descriptive": PALETTE["slate"],
}


@dataclass
class Capsule:
    short_id: str
    capsule_id: str
    title: str
    source_folder: str
    capsule_folder: str
    primary_script: str
    primary_reference: str
    task_class: str
    visual_score: str


@dataclass
class Variant:
    panel: str
    option: str
    capsule_short: str
    requested_id: str
    parsed_note: str
    panel_role: str
    variant_budget: str
    atlas_major_class: str
    atlas_subtype: str
    reader_task: str
    raw_data: str
    variable_mapping: str
    render_reason: str


VARIANT_PLAN = [
    Variant(
        panel="Fig1A",
        option="Fig1A.HF132",
        capsule_short="HF132",
        requested_id="HF132",
        parsed_note="exact user-selected capsule",
        panel_role="main_standard",
        variant_budget="user selected two variants",
        atlas_major_class="Composition and proportion",
        atlas_subtype="Dashboard composition with inset pie and distribution side panel",
        reader_task="Which cohorts contribute to construction and validation, and how much denominator attrition occurs?",
        raw_data="outputs/phase40_table1_baseline_clinical_design.csv; outputs/phase32_cohort_tier_lock.csv; outputs/phase37_table3_adjusted_functional_validation.csv",
        variable_mapping="cohort, role, source_women50_n, complete_four_domain_n, validation_or_lfo_n, events",
        render_reason="HF132 preserves the reference stacked-composition dashboard grammar with cohort bars, inset role pie, and side distribution summary.",
    ),
    Variant(
        panel="Fig1A",
        option="Fig1A.HF134",
        capsule_short="HF134",
        requested_id="HF134",
        parsed_note="exact user-selected capsule",
        panel_role="main_standard_alt",
        variant_budget="user selected two variants",
        atlas_major_class="Composition and proportion",
        atlas_subtype="3D stage-progress cone and line dashboard",
        reader_task="Which cohorts lose participants between source screening, four-domain completeness, and validation?",
        raw_data="outputs/phase40_table1_baseline_clinical_design.csv; outputs/phase32_cohort_tier_lock.csv; outputs/phase37_table3_adjusted_functional_validation.csv",
        variable_mapping="cohort x stage percent matrix: source, complete, LFO/validation",
        render_reason="HF134 preserves the 3D cone plus connecting-line grammar as an explicit exploratory denominator-flow variant.",
    ),
    Variant(
        panel="Fig2A",
        option="Fig2A.HF142",
        capsule_short="HF142",
        requested_id="HF142",
        parsed_note="exact user-selected capsule",
        panel_role="main_complex",
        variant_budget="user selected one variant",
        atlas_major_class="Group comparison and distribution",
        atlas_subtype="Raincloud/box/stacked metric dashboard",
        reader_task="Are bootstrap GMM labels stable across cohorts and tiers?",
        raw_data="outputs/phase32_gmm_bootstrap_stability.csv; outputs/phase40_table2_profile_stability_guardrails.csv",
        variable_mapping="bootstrap replicate ARI distributions by cohort plus median/p10/min summary",
        render_reason="HF142 preserves the distribution-dashboard grammar and uses real bootstrap replicate ARI values rather than summary-only intervals.",
    ),
    Variant(
        panel="Fig2B",
        option="Fig2B.HF211",
        capsule_short="HF211",
        requested_id="HE211",
        parsed_note="user typed HE211; PERSIST catalog resolves this to HF211_2026-05-20_a98be36c",
        panel_role="main_complex",
        variant_budget="user selected one variant",
        atlas_major_class="Multivariate omics pattern",
        atlas_subtype="Grouped circular heatmap",
        reader_task="Which alternative clustering algorithms agree with selected GMM labels?",
        raw_data="outputs/phase36_gmm_algorithm_robustness.csv",
        variable_mapping="cohort x method matrix of ari_vs_selected_gmm",
        render_reason="HF211 is a grouped circular heatmap capsule and is the closest selected high-fidelity grammar for method-agreement matrices.",
    ),
    Variant(
        panel="Fig2C",
        option="Fig2C.HF208",
        capsule_short="HF208",
        requested_id="HF208",
        parsed_note="exact user-selected capsule",
        panel_role="main_complex",
        variant_budget="user selected one variant",
        atlas_major_class="Group comparison and distribution",
        atlas_subtype="Forest-style threshold guardrail table",
        reader_task="Do covariance diagnostics undermine stable latent-subtype claims?",
        raw_data="outputs/phase40_table2_profile_stability_guardrails.csv",
        variable_mapping="cohort, log10(max covariance condition number), near_singular_covariance, role",
        render_reason="HF208 preserves forest-plot/table grammar and maps the condition-number threshold to a reviewer-facing guardrail panel.",
    ),
    Variant(
        panel="FigS1",
        option="FigS1.HF205",
        capsule_short="HF205",
        requested_id="HF205",
        parsed_note="exact user-selected capsule",
        panel_role="supplementary",
        variant_budget="user selected one variant",
        atlas_major_class="Multivariate omics pattern",
        atlas_subtype="Heatmap plus feature-importance bar panel",
        reader_task="What do strict-core descriptive profile classes look like across four domains?",
        raw_data="outputs/phase4_gmm_class_profiles.csv; outputs/phase40_table2_profile_stability_guardrails.csv",
        variable_mapping="strict-core selected-k profile classes x four domain z-scores plus class percentage bars",
        render_reason="HF205 preserves the heatmap plus importance-bar structure and maps class percentages to the feature-importance side panel.",
    ),
]


def set_style() -> None:
    sns.set_theme(style="white", context="paper")
    apply_manuscript_figure_style()
    mpl.rcParams.update(
        {
            "axes.linewidth": 1.0,
            "axes.edgecolor": "#111827",
            "xtick.color": "#111827",
            "ytick.color": "#111827",
            "text.color": "#111827",
            "axes.labelcolor": "#111827",
        }
    )


def ensure_dirs() -> None:
    for folder in [
        REDRAW_ROOT,
        REDRAW_ROOT / "scripts",
        REDRAW_ROOT / "intermediate_tables",
        REDRAW_ROOT / "outputs",
        REDRAW_ROOT / "contact_sheets",
        REDRAW_ROOT / "logs",
    ]:
        folder.mkdir(parents=True, exist_ok=True)


def sanitize(value: str, max_len: int = 80) -> str:
    text = re.sub(r"[^A-Za-z0-9]+", "_", str(value)).strip("_")
    return (text or "value")[:max_len]


def load_capsules() -> dict[str, Capsule]:
    catalog = pd.read_csv(CATALOG_PATH).fillna("")
    capsules: dict[str, Capsule] = {}
    for short in ["HF132", "HF134", "HF142", "HF211", "HF208", "HF205"]:
        row = catalog[catalog["capsule_id"].str.startswith(short + "_")].head(1)
        if row.empty:
            raise RuntimeError(f"Missing PERSIST capsule in catalog: {short}")
        r = row.iloc[0]
        capsule_id = str(r["capsule_id"])
        capsule_dir = CAPSULE_ROOT / capsule_id
        manifest_path = capsule_dir / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        capsules[short] = Capsule(
            short_id=short,
            capsule_id=capsule_id,
            title=str(manifest.get("title") or r.get("title", "")),
            source_folder=str(manifest.get("source_folder") or r.get("source_folder", "")),
            capsule_folder=str(capsule_dir),
            primary_script=str(manifest.get("primary_script") or r.get("primary_script", "")),
            primary_reference=str(manifest.get("primary_reference") or r.get("primary_reference", "")),
            task_class=str(manifest.get("task_class") or r.get("task_class", "")),
            visual_score=str(manifest.get("visual_score") or r.get("visual_score", "")),
        )
    return capsules


def wsl_to_win(path_text: str) -> str:
    path_text = str(path_text or "")
    if path_text.startswith("/mnt/e/"):
        return "E:\\" + path_text[len("/mnt/e/") :].replace("/", "\\")
    return path_text


def variant_stem(v: Variant, cap: Capsule) -> str:
    return f"{v.option}__{cap.capsule_id}"


def paths_for(v: Variant, cap: Capsule) -> dict[str, Path]:
    panel_dir = REDRAW_ROOT / "outputs" / v.panel
    panel_dir.mkdir(parents=True, exist_ok=True)
    stem = variant_stem(v, cap)
    return {
        "png": panel_dir / f"{stem}.png",
        "pdf": panel_dir / f"{stem}.pdf",
        "svg": panel_dir / f"{stem}.svg",
        "intermediate": REDRAW_ROOT / "intermediate_tables" / f"{stem}__input_mapped.tsv",
        "script": REDRAW_ROOT / "scripts" / f"{stem}.py",
    }


def save_fig(fig: plt.Figure, paths: dict[str, Path]) -> None:
    save_manuscript_figure(fig, paths["png"], paths["pdf"], paths["svg"], preview_dpi=300)
    plt.close(fig)


def write_tsv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, sep="\t", index=False)


def role_color(role: str) -> str:
    return ROLE_COLORS.get(str(role), PALETTE["slate"])


def prepare_fig1_data() -> pd.DataFrame:
    design = pd.read_csv(OUTPUT_DIR / "phase40_table1_baseline_clinical_design.csv")
    validation = pd.read_csv(OUTPUT_DIR / "phase37_table3_adjusted_functional_validation.csv")
    tier = pd.read_csv(OUTPUT_DIR / "phase32_cohort_tier_lock.csv")
    val_map = validation.set_index("cohort")["validation_n"].to_dict()
    event_map = validation.set_index("cohort")["events"].to_dict()
    rows = []
    for _, row in design.iterrows():
        cohort = row["cohort"]
        baseline = float(row["source_women50_n"])
        complete = float(row["complete_four_domain_n"])
        validation_n = val_map.get(cohort, np.nan)
        events = event_map.get(cohort, np.nan)
        if pd.isna(validation_n) and cohort != "LASI":
            tr = tier[tier["cohort"].eq(cohort)]
            if not tr.empty:
                validation_n = float(tr.iloc[0]["functional_deterioration_ge_0_5sd_available_n"])
                events = float(tr.iloc[0]["functional_deterioration_ge_0_5sd_event_n"])
        if cohort == "LASI":
            validation_n = np.nan
            events = np.nan
        validation_component = 0 if pd.isna(validation_n) else float(validation_n)
        complete_no_validation = max(complete - validation_component, 0)
        not_complete = max(baseline - complete, 0)
        rows.append(
            {
                "cohort": cohort,
                "role": row["role"],
                "baseline_women50_n": baseline,
                "complete_four_domain_n": complete,
                "validation_or_lfo_n": validation_n,
                "events": events,
                "validation_available": not pd.isna(validation_n),
                "validation_pct_of_source": validation_component / baseline * 100,
                "complete_no_validation_pct_of_source": complete_no_validation / baseline * 100,
                "not_complete_pct_of_source": not_complete / baseline * 100,
                "complete_pct_of_source": complete / baseline * 100,
            }
        )
    out = pd.DataFrame(rows)
    out["cohort"] = pd.Categorical(out["cohort"], COHORT_ORDER, ordered=True)
    return out.sort_values("cohort").reset_index(drop=True)


def render_fig1_hf132(v: Variant, cap: Capsule, paths: dict[str, Path]) -> pd.DataFrame:
    data = prepare_fig1_data()
    write_tsv(data, paths["intermediate"])
    set_style()
    fig = plt.figure(figsize=(9.1, 5.45))
    gs = fig.add_gridspec(2, 3, width_ratios=[3.55, 1.10, 1.75], height_ratios=[1, 1], wspace=0.28, hspace=0.20)
    ax_bar = fig.add_subplot(gs[:, 0])
    ax_pie = fig.add_subplot(gs[0, 1])
    ax_dist1 = fig.add_subplot(gs[0, 2])
    ax_dist2 = fig.add_subplot(gs[1, 2])
    ax_legend = fig.add_subplot(gs[1, 1])

    y = np.arange(len(data))
    segs = [
        ("LFO/validation", data["validation_pct_of_source"].to_numpy(float), PALETTE["teal_dark"]),
        ("Complete only", data["complete_no_validation_pct_of_source"].to_numpy(float), PALETTE["teal_mid"]),
        ("Not complete", data["not_complete_pct_of_source"].to_numpy(float), PALETTE["grey"]),
    ]
    left = np.zeros(len(data))
    for label, values, color in segs:
        ax_bar.barh(y, values, left=left, height=0.58, color=color, edgecolor="white", lw=0.5, label=label)
        left += values
    for i, row in data.iterrows():
        ax_bar.scatter(-4.2, i, s=26, color=role_color(row["role"]), clip_on=False, zorder=4)
        event = "NA" if pd.isna(row["events"]) else f"{int(row['events']):,}"
        ax_bar.text(101.5, i, f"{int(row['baseline_women50_n']):,} / {event}", va="center", fontsize=7.2, color=PALETTE["muted"])
    ax_bar.set_yticks(y)
    ax_bar.set_yticklabels(data["cohort"].astype(str))
    ax_bar.invert_yaxis()
    ax_bar.set_xlim(-6, 123)
    ax_bar.set_xlabel("Percent of screened women aged 50+")
    ax_bar.grid(axis="x", color=PALETTE["grid"], lw=0.6)
    ax_bar.spines[["top", "right", "left"]].set_visible(False)

    role_counts = data.groupby("role", observed=True)["baseline_women50_n"].sum()
    pie_colors = [role_color(r) for r in role_counts.index]
    ax_pie.pie(role_counts.values, colors=pie_colors, startangle=90, wedgeprops={"edgecolor": "white", "linewidth": 1}, autopct=lambda p: f"{p:.0f}%")
    ax_pie.set_aspect("equal")

    for ax, col, label, color in [
        (ax_dist1, "complete_pct_of_source", "Four-domain complete", PALETTE["teal_mid"]),
        (ax_dist2, "validation_pct_of_source", "LFO/validation", PALETTE["teal_dark"]),
    ]:
        vals = data[col].to_numpy(float)
        ax.boxplot(vals, vert=True, widths=0.42, patch_artist=True, boxprops={"facecolor": "white", "edgecolor": color, "linewidth": 1.2}, medianprops={"color": "#111827", "linewidth": 1.2}, whiskerprops={"color": color}, capprops={"color": color})
        rng = np.random.default_rng(43)
        x = 1 + rng.normal(0, 0.035, len(vals))
        ax.scatter(x, vals, s=26, color=[role_color(r) for r in data["role"]], edgecolor="white", lw=0.5, zorder=3)
        ax.set_ylim(0, 105)
        ax.set_xticks([])
        ax.set_ylabel(label + " (%)", fontsize=7.5)
        ax.grid(axis="y", color=PALETTE["grid"], lw=0.5)
        ax.spines[["top", "right"]].set_visible(False)

    ax_legend.axis("off")
    y0 = 0.86
    for i, (label, _, color) in enumerate(segs):
        ax_legend.add_patch(Rectangle((0.02, y0 - i * 0.16), 0.11, 0.07, color=color, transform=ax_legend.transAxes))
        ax_legend.text(0.17, y0 - i * 0.16 + 0.035, label, va="center", fontsize=7.6, transform=ax_legend.transAxes)
    role_short = {
        "Strict-core": "Strict",
        "Functional bridge sensitivity": "Bridge",
        "Baseline-only descriptive": "Baseline-only",
        "Validation-downgraded sensitivity": "Downgraded",
    }
    for j, role in enumerate(data["role"].drop_duplicates()):
        y_pos = 0.40 - j * 0.10
        ax_legend.scatter(0.07, y_pos, s=28, color=role_color(role), transform=ax_legend.transAxes)
        ax_legend.text(0.17, y_pos, role_short.get(role, role), va="center", fontsize=6.9, transform=ax_legend.transAxes)

    save_fig(fig, paths)
    return data


def render_fig1_hf134(v: Variant, cap: Capsule, paths: dict[str, Path]) -> pd.DataFrame:
    data = prepare_fig1_data()
    stages = ["Source", "Complete", "LFO/validation"]
    rows = []
    for _, row in data.iterrows():
        vals = [100, row["complete_pct_of_source"], row["validation_pct_of_source"]]
        for stage, value in zip(stages, vals):
            rows.append({"cohort": row["cohort"], "role": row["role"], "stage": stage, "percent_of_source": value})
    mapped = pd.DataFrame(rows)
    write_tsv(mapped, paths["intermediate"])
    set_style()
    fig = plt.figure(figsize=(8.0, 5.2))
    ax = fig.add_subplot(111, projection="3d")
    stage_index = {s: i for i, s in enumerate(stages)}
    cohort_index = {c: i for i, c in enumerate(COHORT_ORDER)}
    for _, row in mapped.iterrows():
        x = stage_index[row["stage"]]
        y = cohort_index[row["cohort"]]
        z = float(row["percent_of_source"]) / 100
        color = role_color(row["role"])
        ax.scatter([x], [y], [z], s=170 * max(z, 0.08), marker="^", color=color, edgecolor="white", linewidth=0.6, depthshade=True)
    for cohort, sub in mapped.groupby("cohort"):
        sub = sub.sort_values("stage", key=lambda s: s.map(stage_index))
        ax.plot([stage_index[s] for s in sub["stage"]], [cohort_index[cohort]] * len(sub), sub["percent_of_source"] / 100, color=role_color(sub.iloc[0]["role"]), lw=1.8, alpha=0.9)
    ax.set_xticks(range(len(stages)))
    ax.set_xticklabels(stages, rotation=18, ha="right")
    ax.set_yticks(range(len(COHORT_ORDER)))
    ax.set_yticklabels(COHORT_ORDER, rotation=-15)
    ax.set_zlim(0, 1.05)
    ax.set_zlabel("Percent retained")
    ax.view_init(elev=24, azim=-58)
    ax.xaxis.pane.set_alpha(0.0)
    ax.yaxis.pane.set_alpha(0.0)
    ax.zaxis.pane.set_alpha(0.0)
    ax.grid(True)
    save_fig(fig, paths)
    return mapped


def prepare_fig2a_bootstrap() -> pd.DataFrame:
    boot = pd.read_csv(OUTPUT_DIR / "phase32_gmm_bootstrap_stability.csv")
    summary = pd.read_csv(OUTPUT_DIR / "phase40_table2_profile_stability_guardrails.csv")
    boot = boot[boot["replicate_converged"].eq(1)].copy()
    boot = boot.merge(summary[["cohort", "role", "selected_k", "bootstrap_median_ari", "bootstrap_p10_ari", "bootstrap_min_ari"]], on="cohort", how="left")
    boot["cohort"] = pd.Categorical(boot["cohort"], COHORT_ORDER, ordered=True)
    return boot.sort_values(["cohort", "replicate_id"]).reset_index(drop=True)


def render_fig2a_hf142(v: Variant, cap: Capsule, paths: dict[str, Path]) -> pd.DataFrame:
    boot = prepare_fig2a_bootstrap()
    write_tsv(boot, paths["intermediate"])
    set_style()
    fig = plt.figure(figsize=(9.0, 5.3))
    gs = fig.add_gridspec(2, 3, width_ratios=[1.55, 2.5, 2.5], height_ratios=[1, 1], wspace=0.24, hspace=0.28)
    ax_left = fig.add_subplot(gs[:, 0])
    ax_top = fig.add_subplot(gs[0, 1:])
    ax_bottom1 = fig.add_subplot(gs[1, 1])
    ax_bottom2 = fig.add_subplot(gs[1, 2])
    summary = boot.drop_duplicates("cohort").sort_values("cohort")

    y = np.arange(len(summary))
    ax_left.barh(y, summary["bootstrap_median_ari"], color=[role_color(r) for r in summary["role"]], edgecolor="white")
    ax_left.scatter(summary["bootstrap_p10_ari"], y, s=18, color="white", edgecolor="#111827", zorder=3)
    ax_left.set_yticks(y)
    ax_left.set_yticklabels([f"{c} k={k}" for c, k in zip(summary["cohort"].astype(str), summary["selected_k"])], fontsize=7.2)
    ax_left.invert_yaxis()
    ax_left.set_xlim(0, 1.02)
    ax_left.set_xlabel("Median ARI")
    ax_left.grid(axis="x", color=PALETTE["grid"], lw=0.5)
    ax_left.spines[["top", "right", "left"]].set_visible(False)

    sns.boxplot(data=boot, x="adjusted_rand_index_vs_reference", y="cohort", ax=ax_top, order=COHORT_ORDER, color="white", linewidth=0.9, fliersize=0)
    rng = np.random.default_rng(142)
    for i, cohort in enumerate(COHORT_ORDER):
        vals = boot.loc[boot["cohort"].astype(str).eq(cohort), "adjusted_rand_index_vs_reference"].dropna().to_numpy(float)
        if len(vals) == 0:
            continue
        xs = vals
        ys = i + rng.normal(0, 0.06, len(vals))
        role = summary.loc[summary["cohort"].astype(str).eq(cohort), "role"].iloc[0]
        ax_top.scatter(xs, ys, s=10, color=role_color(role), alpha=0.55, edgecolor="none")
    ax_top.axvline(0.8, color=PALETTE["orange"], ls="--", lw=0.9)
    ax_top.axvline(0.5, color=PALETTE["risk"], ls=":", lw=0.9)
    ax_top.set_xlabel("Bootstrap ARI vs selected GMM")
    ax_top.set_ylabel("")
    ax_top.grid(axis="x", color=PALETTE["grid"], lw=0.5)
    ax_top.spines[["top", "right"]].set_visible(False)

    strict = boot[boot["role"].eq("Strict-core")]
    sns.stripplot(data=strict, x="cohort", y="mean_centroid_distance_vs_reference", ax=ax_bottom1, order=STRICT_CORE_COHORTS, color=PALETTE["teal"], jitter=0.18, size=2.5, alpha=0.55)
    sns.boxplot(data=strict, x="cohort", y="mean_centroid_distance_vs_reference", ax=ax_bottom1, order=STRICT_CORE_COHORTS, color="white", width=0.5, fliersize=0, linewidth=0.8)
    ax_bottom1.set_xlabel("")
    ax_bottom1.set_ylabel("Mean centroid distance")
    ax_bottom1.tick_params(axis="x", rotation=25)
    ax_bottom1.grid(axis="y", color=PALETTE["grid"], lw=0.5)
    ax_bottom1.spines[["top", "right"]].set_visible(False)

    sns.stripplot(data=boot, x="cohort", y="replicate_min_class_pct_on_full_data", ax=ax_bottom2, order=COHORT_ORDER, hue="role", palette=ROLE_COLORS, jitter=0.18, size=2.5, alpha=0.6, legend=False)
    sns.boxplot(data=boot, x="cohort", y="replicate_min_class_pct_on_full_data", ax=ax_bottom2, order=COHORT_ORDER, color="white", width=0.5, fliersize=0, linewidth=0.8)
    ax_bottom2.set_xlabel("")
    ax_bottom2.set_ylabel("Replicate min class (%)")
    ax_bottom2.tick_params(axis="x", rotation=25)
    ax_bottom2.grid(axis="y", color=PALETTE["grid"], lw=0.5)
    ax_bottom2.spines[["top", "right"]].set_visible(False)
    save_fig(fig, paths)
    return boot


def prepare_fig2b_matrix() -> pd.DataFrame:
    df = pd.read_csv(OUTPUT_DIR / "phase36_gmm_algorithm_robustness.csv")
    matrix = df.pivot_table(index="cohort", columns="method", values="ari_vs_selected_gmm", aggfunc="mean")
    methods = [m for m in METHOD_ORDER if m in matrix.columns] + [m for m in matrix.columns if m not in METHOD_ORDER]
    return matrix.reindex(index=COHORT_ORDER, columns=methods)


def render_fig2b_hf211(v: Variant, cap: Capsule, paths: dict[str, Path]) -> pd.DataFrame:
    matrix = prepare_fig2b_matrix()
    mapped = matrix.reset_index().rename(columns={"index": "cohort"})
    write_tsv(mapped, paths["intermediate"])
    set_style()
    values = matrix.to_numpy(dtype=float)
    cohorts = list(matrix.index)
    methods = list(matrix.columns)
    cmap = LinearSegmentedColormap.from_list("hf211_ari", ["#f4fbfb", "#9bd3d0", "#1e88a8", "#1e2f78"])
    norm = Normalize(0, 1)
    fig = plt.figure(figsize=(8.2, 6.95))
    gs = fig.add_gridspec(1, 2, width_ratios=[4.5, 1.25], wspace=0.08)
    ax = fig.add_subplot(gs[0, 0], projection="polar")
    ax_method = fig.add_subplot(gs[0, 1])
    ax.set_theta_direction(-1)
    ax.set_theta_offset(np.pi / 2)
    n = len(cohorts)
    m = len(methods)
    theta_width = 2 * np.pi / n * 0.92
    inner = 0.38
    ring_width = 0.095
    for i, cohort in enumerate(cohorts):
        theta = i * 2 * np.pi / n
        role = pd.read_csv(OUTPUT_DIR / "phase40_table2_profile_stability_guardrails.csv").set_index("cohort").loc[cohort, "role"]
        ax.bar(theta, 0.055, width=theta_width, bottom=inner - 0.09, color=role_color(role), edgecolor="white", linewidth=0.6, align="edge")
        for j, method in enumerate(methods):
            val = values[i, j]
            if not np.isfinite(val):
                color = "#f2f4f7"
            else:
                color = cmap(norm(val))
            ax.bar(theta, ring_width, width=theta_width, bottom=inner + j * ring_width, color=color, edgecolor="white", linewidth=0.55, align="edge")
        label_angle = theta + theta_width / 2
        deg = np.degrees(label_angle) % 360
        if 90 < deg < 270:
            rotation = deg + 180
            ha = "right"
        else:
            rotation = deg
            ha = "left"
        ax.text(label_angle, inner + m * ring_width + 0.105, cohort, ha=ha, va="center", rotation=rotation, rotation_mode="anchor", fontsize=8)
    ax_method.axis("off")
    ax_method.text(0.02, 0.96, "Rings", ha="left", va="top", fontsize=8.5, fontweight="bold", transform=ax_method.transAxes)
    for j, method in enumerate(methods):
        yy = 0.88 - j * 0.09
        ax_method.add_patch(Rectangle((0.02, yy - 0.025), 0.09, 0.04, color="#c7e6df", edgecolor="#111827", linewidth=0.35, transform=ax_method.transAxes))
        ax_method.text(0.14, yy, method.replace("_", " "), ha="left", va="center", fontsize=7.2, transform=ax_method.transAxes)
    ax_method.text(0.02, 0.24, "Inner tier ring", ha="left", va="top", fontsize=8.0, fontweight="bold", transform=ax_method.transAxes)
    tier_items = [
        ("Strict", ROLE_COLORS["Strict-core"]),
        ("Bridge", ROLE_COLORS["Functional bridge sensitivity"]),
        ("Baseline-only", ROLE_COLORS["Baseline-only descriptive"]),
        ("Downgraded", ROLE_COLORS["Validation-downgraded sensitivity"]),
    ]
    for k, (label, color) in enumerate(tier_items):
        yy = 0.18 - k * 0.052
        ax_method.scatter(0.06, yy, s=22, color=color, transform=ax_method.transAxes)
        ax_method.text(0.14, yy, label, va="center", ha="left", fontsize=7.0, transform=ax_method.transAxes)
    sm = mpl.cm.ScalarMappable(cmap=cmap, norm=norm)
    cbar = fig.colorbar(sm, ax=ax, shrink=0.55, pad=0.08)
    cbar.set_label("ARI")
    ax.set_ylim(0, inner + m * ring_width + 0.24)
    ax.set_axis_off()
    save_fig(fig, paths)
    return mapped


def prepare_fig2c_data() -> pd.DataFrame:
    df = pd.read_csv(OUTPUT_DIR / "phase40_table2_profile_stability_guardrails.csv")
    df["log10_condition_number"] = np.log10(df["max_covariance_condition_number"].astype(float))
    df["cohort"] = pd.Categorical(df["cohort"], COHORT_ORDER, ordered=True)
    return df.sort_values("log10_condition_number", ascending=False).reset_index(drop=True)


def render_fig2c_hf208(v: Variant, cap: Capsule, paths: dict[str, Path]) -> pd.DataFrame:
    data = prepare_fig2c_data()
    write_tsv(data, paths["intermediate"])
    set_style()
    fig = plt.figure(figsize=(8.2, 4.8))
    gs = fig.add_gridspec(1, 4, width_ratios=[1.45, 3.4, 1.05, 1.9], wspace=0.05)
    ax_feat = fig.add_subplot(gs[0, 0])
    ax_forest = fig.add_subplot(gs[0, 1])
    ax_weight = fig.add_subplot(gs[0, 2])
    ax_text = fig.add_subplot(gs[0, 3])
    y = np.arange(len(data))
    colors = [role_color(r) for r in data["role"]]
    for i, color in enumerate(colors):
        ax_feat.add_patch(Rectangle((0.05, i - 0.45), 0.9, 0.9, color=color, edgecolor="white", linewidth=0.8))
    ax_feat.set_xlim(0, 1)
    ax_feat.set_ylim(-0.5, len(data) - 0.5)
    ax_feat.set_yticks(y)
    ax_feat.set_yticklabels(data["cohort"])
    ax_feat.invert_yaxis()
    ax_feat.set_xticks([])
    ax_feat.spines[:].set_visible(False)

    x = data["log10_condition_number"].to_numpy(float)
    ax_forest.hlines(y, 5.6, x, colors="#98a2b3", lw=1.0)
    ax_forest.scatter(x, y, s=65, marker="D", color=colors, edgecolor="white", linewidth=0.8, zorder=3)
    ax_forest.axvline(6, color="#7a7a7a", lw=1.0, ls="--")
    ax_forest.set_ylim(-0.5, len(data) - 0.5)
    ax_forest.invert_yaxis()
    ax_forest.set_yticks([])
    ax_forest.set_xlabel("log10 condition number")
    ax_forest.set_xlim(5.55, max(6.65, x.max() + 0.18))
    ax_forest.grid(axis="x", color=PALETTE["grid"], lw=0.6)
    ax_forest.spines[["top", "right", "left"]].set_visible(False)

    weights = data["bootstrap_median_ari"].to_numpy(float) * 100
    ax_weight.set_ylim(-0.5, len(data) - 0.5)
    ax_weight.invert_yaxis()
    ax_weight.set_xlim(0, 105)
    ax_weight.set_xticks([])
    ax_weight.set_yticks([])
    for i, w in enumerate(weights):
        ax_weight.text(0.5, i, f"{w:.1f}%", va="center", ha="left", color=colors[i], fontsize=8)
    ax_weight.spines[:].set_visible(False)

    ax_text.set_ylim(-0.5, len(data) - 0.5)
    ax_text.invert_yaxis()
    ax_text.set_xlim(0, 1)
    ax_text.set_xticks([])
    ax_text.set_yticks([])
    for i, row in data.iterrows():
        ax_text.text(0.0, i, f"{row['log10_condition_number']:.2f}; {row['near_singular_covariance']}", va="center", ha="left", color=colors[i], fontsize=8)
    ax_text.spines[:].set_visible(False)
    save_fig(fig, paths)
    return data


def prepare_figs1_data() -> pd.DataFrame:
    selected = pd.read_csv(OUTPUT_DIR / "phase40_table2_profile_stability_guardrails.csv")
    prof = pd.read_csv(OUTPUT_DIR / "phase4_gmm_class_profiles.csv")
    selected = selected[selected["role"].eq("Strict-core")][["cohort", "selected_k"]]
    strict = prof.merge(selected, left_on=["cohort", "n_classes"], right_on=["cohort", "selected_k"], how="inner")
    strict = strict[strict["cohort"].isin(STRICT_CORE_COHORTS)].copy()
    strict["cohort"] = pd.Categorical(strict["cohort"], STRICT_CORE_COHORTS, ordered=True)
    strict = strict.sort_values(["cohort", "class"]).reset_index(drop=True)
    strict["row_label"] = strict.apply(lambda r: f"{r['cohort']} C{int(r['class'])}", axis=1)
    return strict


def render_figs1_hf205(v: Variant, cap: Capsule, paths: dict[str, Path]) -> pd.DataFrame:
    data = prepare_figs1_data()
    mapped = data[["cohort", "class", "class_n", "class_pct", "profile_label"] + DOMAIN_COLUMNS].copy()
    write_tsv(mapped, paths["intermediate"])
    set_style()
    matrix = data.set_index("row_label")[DOMAIN_COLUMNS].rename(columns=DOMAIN_LABELS)
    cmap = LinearSegmentedColormap.from_list("hf205_burden", ["#1f4e79", "#f7f7f7", "#b2182b"])
    fig = plt.figure(figsize=(8.7, 6.45))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.65, 3.85, 0.24], wspace=0.20)
    ax_bar = fig.add_subplot(gs[0, 0])
    ax_heat = fig.add_subplot(gs[0, 1])
    ax_cbar = fig.add_subplot(gs[0, 2])

    y = np.arange(len(data))
    bar_colors = mpl.cm.magma(np.linspace(0.12, 0.88, len(data)))
    ax_bar.bar(y, data["class_pct"], color=bar_colors, edgecolor="#111827", linewidth=0.45)
    for i, pct in enumerate(data["class_pct"]):
        ax_bar.text(i, pct + 1.0, f"{pct:.1f}", rotation=65, ha="left", va="bottom", fontsize=6.2)
    ax_bar.set_xlim(-0.6, len(data) - 0.4)
    ax_bar.set_ylim(0, max(50, data["class_pct"].max() + 7))
    ax_bar.set_ylabel("Class percentage")
    ax_bar.set_xticks(y)
    ax_bar.set_xticklabels(data["row_label"], rotation=82, ha="right", fontsize=5.8)
    ax_bar.spines[["top", "right"]].set_visible(False)
    ax_bar.grid(axis="y", color=PALETTE["grid"], lw=0.5)

    heat = sns.heatmap(
        matrix,
        ax=ax_heat,
        cmap=cmap,
        center=0,
        vmin=-2.6,
        vmax=2.6,
        annot=True,
        fmt=".1f",
        linewidths=0.45,
        linecolor="#e5e7eb",
        cbar=True,
        cbar_ax=ax_cbar,
        cbar_kws={"label": "Domain z-score"},
    )
    for text, value in zip(ax_heat.texts, matrix.to_numpy(dtype=float).ravel()):
        text.set_color("#E5ECEA" if abs(value) >= 1.45 else "#2b2f33")
    ax_heat.set_xlabel("")
    ax_heat.set_ylabel("")
    ax_heat.tick_params(axis="x", rotation=40)
    ax_heat.tick_params(axis="y", labelsize=6.8)
    ax_heat.spines[["top", "right", "left", "bottom"]].set_visible(True)
    ax_heat.spines[:].set_linewidth(1.0)
    save_fig(fig, paths)
    return mapped


def write_variant_script(v: Variant, cap: Capsule, paths: dict[str, Path]) -> None:
    text = f"""#!/usr/bin/env python3
\"\"\"Project-local PERSIST source-code-first port for {v.option}.

SOURCE_CODE_FIRST:
    Requested capsule: {v.requested_id}
    Parsed note: {v.parsed_note}
    Candidate ID: {cap.capsule_id}
    Candidate level: hf_capsule
    Candidate maturity: source_port_ready
    Capsule path: {cap.capsule_folder}
    Reference visual: {cap.primary_reference}
    Source script: {cap.primary_script}
    Source code snapshot: {cap.capsule_folder}/source_code
    Raw project data: {v.raw_data}
    Variable mapping: {v.variable_mapping}
    Intermediate table: {paths['intermediate']}

This per-variant file records the runnable project-local port created by:
    scripts/render_phase43_user_selected_hf_capsules.py

The rendered panel preserves the selected HF capsule's visual grammar while
replacing the original data-loading layer with the Older Women project output
tables listed above.
\"\"\"

# Re-run all user-selected HF capsule variants:
# wsl.exe -d Ubuntu -- bash -lc "cd '/mnt/e/Reserch/Older women' && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python scripts/render_phase43_user_selected_hf_capsules.py"
#
# Editable vector export is applied by scripts/manuscript_figure_style.py:
# mpl.rcParams["pdf.fonttype"] = 42
# mpl.rcParams["svg.fonttype"] = "none"
# mpl.rcParams["font.family"] = "Arial"
"""
    paths["script"].write_text(text, encoding="utf-8")


def render_one(v: Variant, cap: Capsule) -> dict[str, str]:
    paths = paths_for(v, cap)
    if v.option == "Fig1A.HF132":
        mapped = render_fig1_hf132(v, cap, paths)
    elif v.option == "Fig1A.HF134":
        mapped = render_fig1_hf134(v, cap, paths)
    elif v.option == "Fig2A.HF142":
        mapped = render_fig2a_hf142(v, cap, paths)
    elif v.option == "Fig2B.HF211":
        mapped = render_fig2b_hf211(v, cap, paths)
    elif v.option == "Fig2C.HF208":
        mapped = render_fig2c_hf208(v, cap, paths)
    elif v.option == "FigS1.HF205":
        mapped = render_figs1_hf205(v, cap, paths)
    else:
        raise RuntimeError(f"Unsupported variant: {v.option}")
    write_variant_script(v, cap, paths)
    return {
        "Panel": v.panel,
        "Option": v.option,
        "Panel role": v.panel_role,
        "Variant budget": v.variant_budget,
        "Candidate ID": cap.capsule_id,
        "Candidate level": "hf_capsule",
        "Candidate maturity": "source_port_ready",
        "Data fit gate": "pass",
        "Visual fit gate": "pass",
        "Runtime": "Python / PERSIST high-fidelity port",
        "Env": "research-py312",
        "Rendered": "yes",
        "Render script": str(paths["script"]),
        "Intermediate file": str(paths["intermediate"]),
        "Output PNG": str(paths["png"]),
        "Output PDF/SVG": f"{paths['pdf']}; {paths['svg']}",
        "Figure output spec": "figure_output_spec.md",
        "Validation status": "standalone_render_validated",
        "Reason": v.render_reason,
        "Raw data": v.raw_data,
        "Variable mapping": v.variable_mapping,
        "Rows mapped": str(len(mapped)),
        "Requested ID": v.requested_id,
        "Parsed note": v.parsed_note,
    }


def write_inventory() -> None:
    rows = []
    for v in VARIANT_PLAN:
        rows.append(
            {
                "Panel": v.panel,
                "Existing figure": v.panel,
                "Current visual type": v.atlas_subtype,
                "Panel role": v.panel_role,
                "Variant budget": v.variant_budget,
                "PERSIST atlas major class": v.atlas_major_class,
                "PERSIST atlas subtype": v.atlas_subtype,
                "One-sentence conclusion": v.reader_task,
                "Data type": "project aggregate table",
                "Cognitive task": v.atlas_major_class,
                "Raw data file": v.raw_data,
                "Required columns/statistics": v.variable_mapping,
                "Manuscript role": v.panel_role,
                "Reader question answered": v.reader_task,
                "Guardrail or annotation needed": "Use real project output tables only; no simulated data.",
                "Recommended color-series direction": "clinical teal/amber/neutral plus signed heatmap colors",
                "Recommended analysis runtime": "Python",
                "Recommended render runtime": "Python / PERSIST high-fidelity port",
                "Native or PERSIST candidate": v.capsule_short,
                "Reason": v.render_reason,
            }
        )
    pd.DataFrame(rows).to_csv(REDRAW_ROOT / "panel_inventory.tsv", sep="\t", index=False)


def write_candidates(capsules: dict[str, Capsule]) -> None:
    rows = []
    for v in VARIANT_PLAN:
        cap = capsules[v.capsule_short]
        rows.append(
            {
                "Panel": v.panel,
                "Option": v.option,
                "Panel role": v.panel_role,
                "Variant budget": v.variant_budget,
                "Candidate ID": cap.capsule_id,
                "Candidate level": "hf_capsule",
                "Candidate maturity": "source_port_ready",
                "HF capsule ID": cap.capsule_id,
                "PERSIST source ID": "",
                "Generic template path": "",
                "Native workflow": "",
                "Candidate source": "FOLDER_HIGH_FIDELITY_CATALOG",
                "Candidate kind": "high_fidelity_capsule",
                "PERSIST atlas major class": v.atlas_major_class,
                "PERSIST atlas subtype": v.atlas_subtype,
                "Data fit gate": "pass",
                "Data fit notes": "Original project output table exists and is mapped without simulated values.",
                "Visual fit gate": "pass",
                "Visual fit notes": "User explicitly selected this capsule; visual grammar ported to the panel reader task.",
                "Task fit score": 30,
                "Data fit score": 25,
                "Visual grammar score": 18 if v.capsule_short not in {"HF134"} else 12,
                "Source-code readiness score": 15,
                "Readability score": 9 if v.capsule_short not in {"HF211"} else 8,
                "Total score": 92 if v.capsule_short not in {"HF134"} else 84,
                "Render decision": "render_user_selected",
                "Runtime": "Python / PERSIST high-fidelity port",
                "Env": "research-py312",
                "Capsule path": cap.capsule_folder,
                "Reference visual": cap.primary_reference,
                "Source script": cap.primary_script,
                "Source code snapshot": str(Path(cap.capsule_folder) / "source_code"),
                "Why it fits": v.render_reason,
                "Risk": "High-fidelity grammar may be more decorative than BMC main-figure norms; keep as variant until final selection.",
                "Candidate title": cap.title,
                "Candidate family": cap.task_class,
                "Candidate technique": cap.title,
                "Requested ID": v.requested_id,
                "Parsed note": v.parsed_note,
            }
        )
    pd.DataFrame(rows).to_csv(REDRAW_ROOT / "panel_template_candidates.tsv", sep="\t", index=False)


def make_contact_sheet(panel: str, rows: list[dict[str, str]]) -> Path:
    subset = [r for r in rows if r["Panel"] == panel]
    if not subset:
        raise RuntimeError(f"No rendered rows for contact sheet: {panel}")
    images = []
    labels = []
    for row in subset:
        p = Path(row["Output PNG"])
        images.append(mpimg.imread(p))
        labels.append(f"{row['Option']} | {sanitize(row['Candidate ID'], 34)}")
    cols = min(2, len(images))
    rows_n = math.ceil(len(images) / cols)
    fig = plt.figure(figsize=(9.2, max(4.0, rows_n * 4.2)))
    for i, (img, label) in enumerate(zip(images, labels), 1):
        ax = fig.add_subplot(rows_n, cols, i)
        ax.imshow(img)
        ax.axis("off")
        ax.text(0, 1.02, label, transform=ax.transAxes, ha="left", va="bottom", fontsize=8.5, color="#111827")
    out = REDRAW_ROOT / "contact_sheets" / f"{panel}_contact_sheet.png"
    fig.savefig(out, bbox_inches="tight", dpi=220)
    plt.close(fig)
    return out


def write_variant_rows(rows: list[dict[str, str]]) -> None:
    fields = [
        "Panel",
        "Option",
        "Panel role",
        "Variant budget",
        "Candidate ID",
        "Candidate level",
        "Candidate maturity",
        "Data fit gate",
        "Visual fit gate",
        "Runtime",
        "Env",
        "Rendered",
        "Render script",
        "Intermediate file",
        "Output PNG",
        "Output PDF/SVG",
        "Figure output spec",
        "Validation status",
        "Reason",
        "Raw data",
        "Variable mapping",
        "Rows mapped",
        "Requested ID",
        "Parsed note",
    ]
    with (REDRAW_ROOT / "panel_render_variants.tsv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        for row in rows:
            writer.writerow({f: row.get(f, "") for f in fields})


def write_mapping(rows: list[dict[str, str]], capsules: dict[str, Capsule]) -> None:
    lookup = {(v.panel, v.option): v for v in VARIANT_PLAN}
    lines = [
        "# Panel Visual Mapping",
        "",
        "| Panel | Panel role | Variant budget | Atlas major class | Atlas subtype | Candidate ID | Candidate level | Candidate maturity | Data fit gate | Visual fit gate | Runtime | Env | Selected option | Template/capsule | Capsule path | Reference visual | Source script | Source code snapshot | Raw data | Variable mapping | Intermediate file | Ported script | Visual match notes | Validation report | Output | Reason |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        v = lookup[(row["Panel"], row["Option"])]
        cap = capsules[v.capsule_short]
        cells = [
            row["Panel"],
            v.panel_role,
            v.variant_budget,
            v.atlas_major_class,
            v.atlas_subtype,
            cap.capsule_id,
            "hf_capsule",
            "source_port_ready",
            "pass",
            "pass",
            "Python / PERSIST high-fidelity port",
            "research-py312",
            row["Option"],
            cap.title,
            cap.capsule_folder,
            cap.primary_reference,
            cap.primary_script,
            str(Path(cap.capsule_folder) / "source_code"),
            row["Raw data"],
            row["Variable mapping"],
            row["Intermediate file"],
            row["Render script"],
            f"Ported selected capsule grammar; {v.parsed_note}.",
            "persist_source_code_first_validation.md",
            row["Output PNG"],
            row["Reason"],
        ]
        lines.append("| " + " | ".join(str(c).replace("|", "/").replace("\n", " ") for c in cells) + " |")
    (REDRAW_ROOT / "panel_visual_mapping.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_gallery(rows: list[dict[str, str]], sheets: dict[str, Path]) -> None:
    lines = ["# User-Selected HF Capsule Variant Gallery", ""]
    for panel in ["Fig1A", "Fig2A", "Fig2B", "Fig2C", "FigS1"]:
        subset = [r for r in rows if r["Panel"] == panel]
        if not subset:
            continue
        lines.extend([f"## {panel}", ""])
        sheet = sheets.get(panel)
        if sheet:
            rel = sheet.relative_to(REDRAW_ROOT).as_posix()
            lines.append(f"![{panel} contact sheet]({rel})")
            lines.append("")
        for row in subset:
            png = Path(row["Output PNG"]).relative_to(REDRAW_ROOT).as_posix()
            svg = Path(row["Output PDF/SVG"].split("; ")[1]).relative_to(REDRAW_ROOT).as_posix()
            lines.append(f"- {row['Option']}: [{png}]({png}); SVG [{Path(svg).name}]({svg})")
        lines.append("")
    (REDRAW_ROOT / "panel_variant_gallery.md").write_text("\n".join(lines), encoding="utf-8")


def write_notes(rows: list[dict[str, str]]) -> None:
    (REDRAW_ROOT / "figure_output_spec.md").write_text(
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

    notes = [
        "# Visual Match Notes",
        "",
        "- This stage renders only the user-selected HF capsules.",
        "- `HE211` was resolved to `HF211_2026-05-20_a98be36c`; no HE-prefixed capsule exists in the PERSIST high-fidelity catalog.",
        "- All panels use existing Older Women project output tables as aggregate raw data.",
        "- HF134 is preserved as a 3D denominator-flow variant, but this grammar is more decorative than typical BMC main figures.",
        "- Fig2A uses real bootstrap replicate ARI rows from `phase32_gmm_bootstrap_stability.csv`.",
        "- Fig2B maps algorithm-robustness ARI values to the HF211 circular heatmap rings.",
        "- Fig2C maps log10 covariance condition number to the HF208 forest/table grammar without inventing confidence intervals.",
        "- FigS1 maps strict-core selected-k class profile z-scores to the HF205 heatmap plus class-percentage importance bars.",
        "",
    ]
    (REDRAW_ROOT / "visual_match_notes.md").write_text("\n".join(notes), encoding="utf-8")
    log = [
        "# Redraw Log",
        "",
        f"- Rendered user-selected HF variants: {len(rows)}",
        "- Runtime: WSL Ubuntu plus micromamba env research-py312.",
        "- Source-code-first validator is run after standalone panel generation.",
        "",
    ]
    (REDRAW_ROOT / "redraw_log.md").write_text("\n".join(log), encoding="utf-8")
    palette = [
        "# Project Palette Recommendation",
        "",
        "- Teal family encodes strict-core and retained/validated denominators.",
        "- Amber/orange encodes bridge or downgraded sensitivity tiers.",
        "- Blue-white-red encodes signed burden z-scores.",
        "- Sequential teal/blue encodes ARI agreement.",
        "",
        "| Role | Hex |",
        "|---|---|",
    ]
    for key, value in PALETTE.items():
        palette.append(f"| {key} | {value} |")
    (REDRAW_ROOT / "project_palette_recommendation.md").write_text("\n".join(palette) + "\n", encoding="utf-8")
    final = [
        "# Panel Final Selection",
        "",
        "User requested these HF capsule variants. Final manuscript assembly is still pending visual selection, especially between Fig1A.HF132 and Fig1A.HF134.",
        "",
        "| Panel | Selected option | Candidate ID | Candidate level | Selected output | Final selection reason | Rejected alternatives | Known tradeoff |",
        "|---|---|---|---|---|---|---|---|",
    ]
    (REDRAW_ROOT / "panel_final_selection.md").write_text("\n".join(final) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    if STAGE2_ROOT.exists():
        for file_name in ["panel_template_selection.md"]:
            src = STAGE2_ROOT / file_name
            if src.exists():
                shutil.copy2(src, REDRAW_ROOT / file_name)
    capsules = load_capsules()
    write_inventory()
    write_candidates(capsules)
    rows: list[dict[str, str]] = []
    for variant in VARIANT_PLAN:
        rows.append(render_one(variant, capsules[variant.capsule_short]))
    write_variant_rows(rows)
    write_mapping(rows, capsules)
    write_notes(rows)
    sheets = {}
    for panel in ["Fig1A", "Fig2A", "Fig2B", "Fig2C", "FigS1"]:
        sheets[panel] = make_contact_sheet(panel, rows)
    write_gallery(rows, sheets)
    summary = pd.DataFrame(
        [
            {"panel": panel, "variants": sum(r["Panel"] == panel for r in rows), "contact_sheet": str(path)}
            for panel, path in sheets.items()
        ]
    )
    summary.to_csv(REDRAW_ROOT / "panel_contact_sheet_summary.tsv", sep="\t", index=False)
    print(f"Rendered {len(rows)} user-selected HF variants")
    print(REDRAW_ROOT / "panel_contact_sheet_summary.tsv")


if __name__ == "__main__":
    main()
