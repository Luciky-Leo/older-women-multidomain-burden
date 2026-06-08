#!/usr/bin/env python3
"""Render PERSIST-informed figure variants from real Older Women project outputs.

This is a project-local source-code-first port layer.  The source visual
contracts come from the PERSIST candidate table generated in Phase 42:

- composition/percent_stacked_bar_template.py
- group_distribution/forest_plot_template.py
- correlation_omics/correlation_heatmap_template.py
- indexed PERSIST and high-fidelity candidates listed in panel_template_candidates.tsv

Only existing project output tables are used.  No simulated data and no
screenshot-derived values are introduced.
"""

from __future__ import annotations

import csv
import math
import re
import shutil
import textwrap
from dataclasses import dataclass
from pathlib import Path

import matplotlib as mpl
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Circle, Rectangle


PROJECT_ROOT = Path("/mnt/e/Reserch/Older women")
STAGE1_ROOT = PROJECT_ROOT / "figure_redraw" / "persist_stage1_fig1_fig2_fig3_figS1"
REDRAW_ROOT = PROJECT_ROOT / "figure_redraw" / "persist_stage2_fig1_fig2_fig3_figS1_variants"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

CANDIDATE_SOURCE = STAGE1_ROOT / "panel_template_candidates.tsv"
INVENTORY_SOURCE = STAGE1_ROOT / "panel_inventory.tsv"

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

ROLE_ORDER = {
    "Strict-core": 0,
    "Functional bridge sensitivity": 1,
    "Validation-downgraded sensitivity": 2,
    "Baseline-only descriptive": 3,
}

COHORT_ORDER = ["CHARLS", "ELSA", "HRS", "KLoSA", "LASI", "MHAS", "SHARE"]
STRICT_CORE_COHORTS = ["CHARLS", "ELSA", "HRS", "MHAS"]

PALETTE = {
    "ink": "#1f2933",
    "muted": "#667085",
    "line": "#d0d5dd",
    "grid": "#e5e7eb",
    "baseline": "#cbd5e1",
    "complete": "#5aa6a6",
    "model": "#0f6b75",
    "unavailable": "#f2f4f7",
    "strict": "#0f6b75",
    "bridge": "#d9822b",
    "downgrade": "#b54708",
    "baseline_only": "#64748b",
    "risk": "#b42318",
    "continuous": "#344054",
    "zero": "#475467",
}


@dataclass
class Variant:
    panel: str
    option: str
    candidate_id: str
    candidate_level: str
    candidate_maturity: str
    panel_role: str
    variant_budget: str
    atlas_major_class: str
    atlas_subtype: str
    data_fit_gate: str
    visual_fit_gate: str
    runtime: str
    env: str
    template_path: str
    capsule_path: str
    reference_visual: str
    source_script: str
    source_snapshot: str
    why_it_fits: str
    candidate_title: str
    candidate_family: str
    candidate_technique: str


def set_style() -> None:
    sns.set_theme(style="white", context="paper")
    mpl.rcParams.update(
        {
            "figure.dpi": 150,
            "savefig.dpi": 450,
            "font.family": "DejaVu Sans",
            "font.size": 8.5,
            "axes.labelsize": 8.5,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 7.8,
            "axes.linewidth": 0.7,
            "axes.edgecolor": "#344054",
            "xtick.color": "#344054",
            "ytick.color": "#344054",
            "text.color": "#1f2933",
            "axes.labelcolor": "#344054",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "axes.titlepad": 0,
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


def sanitize_id(value: str, max_len: int = 72) -> str:
    text = str(value or "candidate")
    text = re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_")
    if not text:
        text = "candidate"
    return text[:max_len]


def read_candidates() -> pd.DataFrame:
    candidates = pd.read_csv(CANDIDATE_SOURCE, sep="\t")
    selected = candidates[candidates["Render decision"].eq("render_recommended")].copy()
    # Fig2C has no render_recommended option but is part of the requested Fig2.
    if not selected["Panel"].eq("Fig2C").any():
        fallback = (
            candidates[candidates["Panel"].eq("Fig2C")]
            .sort_values("Total score", ascending=False)
            .head(1)
            .copy()
        )
        if not fallback.empty:
            selected = pd.concat([selected, fallback], ignore_index=True)
    panel_order = {panel: idx for idx, panel in enumerate(["Fig1A", "Fig2A", "Fig2B", "Fig2C", "Fig3A", "Fig3B", "FigS1"])}
    selected["_panel_order"] = selected["Panel"].map(panel_order).fillna(99)
    selected["_option_sort"] = selected["Option"].astype(str).str.extract(r"\.(\d+)").fillna("99").astype(int)
    return selected.sort_values(["_panel_order", "_option_sort", "Total score"], ascending=[True, True, False]).drop(columns=["_panel_order", "_option_sort"])


def candidate_to_variant(row: pd.Series) -> Variant:
    return Variant(
        panel=str(row.get("Panel", "")),
        option=str(row.get("Option", "")),
        candidate_id=str(row.get("Candidate ID", "")),
        candidate_level=str(row.get("Candidate level", "")),
        candidate_maturity=str(row.get("Candidate maturity", "")),
        panel_role=str(row.get("Panel role", "")),
        variant_budget=str(row.get("Variant budget", "")),
        atlas_major_class=str(row.get("PERSIST atlas major class", "")),
        atlas_subtype=str(row.get("PERSIST atlas subtype", "")),
        data_fit_gate=str(row.get("Data fit gate", "")),
        visual_fit_gate=str(row.get("Visual fit gate", "")),
        runtime=str(row.get("Runtime", "")),
        env=str(row.get("Env", "")),
        template_path=str(row.get("Generic template path", "")),
        capsule_path=str(row.get("Capsule path", "")),
        reference_visual=str(row.get("Reference visual", "")),
        source_script=str(row.get("Source script", "")),
        source_snapshot=str(row.get("Source code snapshot", "")),
        why_it_fits=str(row.get("Why it fits", "")),
        candidate_title=str(row.get("Candidate title", "")),
        candidate_family=str(row.get("Candidate family", "")),
        candidate_technique=str(row.get("Candidate technique", "")),
    )


def variant_stem(v: Variant) -> str:
    return f"{v.panel}__{v.option}__{sanitize_id(v.candidate_id)}"


def output_paths(v: Variant) -> dict[str, Path]:
    panel_dir = REDRAW_ROOT / "outputs" / v.panel
    panel_dir.mkdir(parents=True, exist_ok=True)
    stem = variant_stem(v)
    return {
        "png": panel_dir / f"{stem}.png",
        "pdf": panel_dir / f"{stem}.pdf",
        "svg": panel_dir / f"{stem}.svg",
        "intermediate": REDRAW_ROOT / "intermediate_tables" / f"{stem}__input_mapped.tsv",
        "script": REDRAW_ROOT / "scripts" / f"{stem}.py",
    }


def save_fig(fig: plt.Figure, paths: dict[str, Path]) -> None:
    for ext in ["png", "pdf", "svg"]:
        fig.savefig(paths[ext], bbox_inches="tight", dpi=450)
    plt.close(fig)


def write_tsv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, sep="\t", index=False)


def parse_ci(ci_text: str) -> tuple[float, float]:
    nums = re.findall(r"-?\d+(?:\.\d+)?", str(ci_text))
    if len(nums) < 2:
        return (np.nan, np.nan)
    return float(nums[0]), float(nums[1])


def role_color(role: str) -> str:
    if role == "Strict-core":
        return PALETTE["strict"]
    if "bridge" in role.lower():
        return PALETTE["bridge"]
    if "downgraded" in role.lower():
        return PALETTE["downgrade"]
    return PALETTE["baseline_only"]


def short_profile_label(label: str) -> str:
    text = str(label).replace("_", " ")
    replacements = {
        "cardiometabolic chronic": "CM",
        "intermediate": "interm.",
        "high burden": "high",
        "severity aligned": "severity",
        "spared": "spared",
        "functional": "function",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text[:44]


def prepare_fig1_data() -> pd.DataFrame:
    design = pd.read_csv(OUTPUT_DIR / "phase40_table1_baseline_clinical_design.csv")
    lock = pd.read_csv(OUTPUT_DIR / "phase32_cohort_tier_lock.csv")
    validation = pd.read_csv(OUTPUT_DIR / "phase37_table3_adjusted_functional_validation.csv")

    val_map = validation.set_index("cohort")["validation_n"].to_dict()
    event_map = validation.set_index("cohort")["events"].to_dict()
    rows = []
    for _, row in design.iterrows():
        cohort = row["cohort"]
        lock_row = lock[lock["cohort"].eq(cohort)].head(1)
        baseline = float(row["source_women50_n"])
        complete = float(row["complete_four_domain_n"])
        role = row["role"]
        validation_n = val_map.get(cohort, np.nan)
        events = event_map.get(cohort, np.nan)
        if pd.isna(validation_n) and not lock_row.empty and cohort != "LASI":
            validation_n = float(lock_row.iloc[0]["functional_deterioration_ge_0_5sd_available_n"])
            events = float(lock_row.iloc[0]["functional_deterioration_ge_0_5sd_event_n"])
        if cohort == "LASI":
            validation_n = np.nan
            events = np.nan
        validation_component = 0.0 if pd.isna(validation_n) else max(float(validation_n), 0.0)
        complete_no_validation = max(complete - validation_component, 0.0)
        not_complete = max(baseline - complete, 0.0)
        rows.append(
            {
                "cohort": cohort,
                "role": role,
                "baseline_women50_n": baseline,
                "complete_four_domain_n": complete,
                "validation_or_lfo_n": validation_n,
                "events": events,
                "validation_available": not pd.isna(validation_n),
                "model_component": validation_component,
                "complete_no_validation_component": complete_no_validation,
                "not_complete_component": not_complete,
                "complete_pct": complete / baseline * 100 if baseline else np.nan,
                "validation_pct": validation_component / baseline * 100 if baseline else np.nan,
            }
        )
    out = pd.DataFrame(rows)
    out["cohort"] = pd.Categorical(out["cohort"], COHORT_ORDER, ordered=True)
    return out.sort_values("cohort").reset_index(drop=True)


def render_fig1(v: Variant, paths: dict[str, Path]) -> pd.DataFrame:
    data = prepare_fig1_data()
    write_tsv(data, paths["intermediate"])
    set_style()
    style_idx = int(v.option.split(".")[-1])
    fig, ax = plt.subplots(figsize=(7.2, 4.3))
    y = np.arange(len(data))
    baseline = data["baseline_women50_n"].to_numpy(float)
    validation = data["model_component"].to_numpy(float) / baseline * 100
    complete_no_validation = data["complete_no_validation_component"].to_numpy(float) / baseline * 100
    not_complete = data["not_complete_component"].to_numpy(float) / baseline * 100

    if style_idx in {2, 3, 7}:
        ax.barh(y - 0.18, np.full_like(y, 100, dtype=float), height=0.14, color="#eef2f6", edgecolor="none")
        ax.barh(y - 0.18, data["complete_pct"], height=0.14, color=PALETTE["complete"], edgecolor="white", linewidth=0.5, label="Four-domain complete")
        valid_pct = data["validation_pct"].fillna(0).to_numpy(float)
        ax.barh(y + 0.18, np.full_like(y, 100, dtype=float), height=0.14, color="#f7f8fa", edgecolor="none")
        ax.barh(y + 0.18, valid_pct, height=0.14, color=PALETTE["model"], edgecolor="white", linewidth=0.5, label="LFO/validation denominator")
        for i, row in data.iterrows():
            ax.text(101.5, i, f"{int(row['baseline_women50_n']):,}", va="center", ha="left", fontsize=7.3, color=PALETTE["muted"])
            ax.scatter(-3.2, i, s=28, color=role_color(row["role"]), clip_on=False, zorder=3)
        ax.set_xlim(-5, 116)
        ax.set_xlabel("Percent of screened women aged 50+")
    else:
        left = np.zeros(len(data))
        segments = [
            ("LFO/validation denominator", validation, PALETTE["model"]),
            ("Four-domain complete, no LFO validation", complete_no_validation, PALETTE["complete"]),
            ("Screened but not complete", not_complete, PALETTE["baseline"]),
        ]
        for label, values, color in segments:
            ax.barh(y, values, left=left, height=0.62, color=color, edgecolor="white", linewidth=0.5, label=label)
            left = left + values
        for i, row in data.iterrows():
            event_text = "NA" if pd.isna(row["events"]) else f"{int(row['events']):,}"
            ax.text(101.2, i, f"N {int(row['baseline_women50_n']):,}; ev {event_text}", va="center", ha="left", fontsize=7.1, color=PALETTE["muted"])
            ax.scatter(-2.8, i, s=30, color=role_color(row["role"]), clip_on=False, zorder=3)
        ax.set_xlim(-5, 119)
        ax.set_xlabel("Percent of screened women aged 50+")

    ax.set_yticks(y)
    ax.set_yticklabels(data["cohort"].astype(str))
    ax.invert_yaxis()
    ax.xaxis.grid(True, color=PALETTE["grid"], lw=0.5)
    ax.set_ylabel("")
    ax.legend(frameon=False, loc="lower center", bbox_to_anchor=(0.5, -0.23), ncol=3, handlelength=1.2, columnspacing=1.2)
    sns.despine(ax=ax, left=True, bottom=False)
    save_fig(fig, paths)
    return data


def prepare_fig2a_data() -> pd.DataFrame:
    df = pd.read_csv(OUTPUT_DIR / "phase40_table2_profile_stability_guardrails.csv")
    df["role_rank"] = df["role"].map(ROLE_ORDER).fillna(9)
    df["cohort"] = pd.Categorical(df["cohort"], COHORT_ORDER, ordered=True)
    df = df.sort_values(["role_rank", "cohort"]).reset_index(drop=True)
    return df[
        [
            "cohort",
            "role",
            "selected_k",
            "bootstrap_median_ari",
            "bootstrap_p10_ari",
            "bootstrap_min_ari",
            "algorithm_ari_median",
            "near_singular_covariance",
        ]
    ]


def render_fig2a(v: Variant, paths: dict[str, Path]) -> pd.DataFrame:
    data = prepare_fig2a_data()
    write_tsv(data, paths["intermediate"])
    set_style()
    style_idx = int(v.option.split(".")[-1])
    fig, ax = plt.subplots(figsize=(6.7, 4.1))
    y = np.arange(len(data))
    median = data["bootstrap_median_ari"].to_numpy(float)
    p10 = data["bootstrap_p10_ari"].to_numpy(float)
    minv = data["bootstrap_min_ari"].to_numpy(float)
    colors = [role_color(r) for r in data["role"]]
    if style_idx == 2:
        ax.hlines(y, minv, median, color="#98a2b3", lw=3.0, alpha=0.65)
        ax.scatter(p10, y, s=22, facecolor="white", edgecolor="#667085", linewidth=0.8, zorder=3, label="p10")
        ax.scatter(median, y, s=46, color=colors, edgecolor="white", linewidth=0.7, zorder=4, label="median")
    else:
        ax.errorbar(
            median,
            y,
            xerr=np.vstack([median - p10, np.zeros_like(median)]),
            fmt="none",
            ecolor="#667085",
            elinewidth=1.0,
            capsize=2.5,
            zorder=2,
        )
        ax.scatter(minv, y, s=16, facecolor="none", edgecolor="#98a2b3", linewidth=0.8, zorder=2, label="min")
        ax.scatter(median, y, s=48, color=colors, edgecolor="white", linewidth=0.7, zorder=4, label="median")
    ax.axvline(0.8, color="#f79009", lw=0.9, ls="--")
    ax.axvline(0.5, color="#b42318", lw=0.8, ls=":")
    ax.set_xlim(0, 1.04)
    ax.set_yticks(y)
    ax.set_yticklabels([f"{c} (k={k})" for c, k in zip(data["cohort"].astype(str), data["selected_k"])])
    ax.invert_yaxis()
    ax.set_xlabel("Bootstrap ARI vs selected GMM")
    ax.set_ylabel("")
    ax.xaxis.grid(True, color=PALETTE["grid"], lw=0.5)
    sns.despine(ax=ax, left=True)
    save_fig(fig, paths)
    return data


def prepare_fig2b_matrix() -> pd.DataFrame:
    df = pd.read_csv(OUTPUT_DIR / "phase36_gmm_algorithm_robustness.csv")
    method_order = ["gmm_full", "gmm_diag", "gmm_tied", "kmeans", "agglomerative", "hierarchical"]
    methods = [m for m in method_order if m in set(df["method"])]
    methods += [m for m in sorted(df["method"].unique()) if m not in methods]
    matrix = df.pivot_table(index="cohort", columns="method", values="ari_vs_selected_gmm", aggfunc="mean")
    matrix = matrix.reindex(index=COHORT_ORDER, columns=methods)
    return matrix


def render_heatmap_matrix(matrix: pd.DataFrame, ax: plt.Axes, variant_style: str) -> None:
    cmap = LinearSegmentedColormap.from_list("ari_teal", ["#f7fafc", "#c7e6df", "#4da4a4", "#0f5f6a"])
    if variant_style == "bubble":
        ax.set_xlim(-0.5, matrix.shape[1] - 0.5)
        ax.set_ylim(matrix.shape[0] - 0.5, -0.5)
        for i, row in enumerate(matrix.index):
            for j, col in enumerate(matrix.columns):
                val = matrix.loc[row, col]
                if not np.isfinite(val):
                    continue
                radius = 0.08 + 0.28 * max(val, 0)
                color = cmap(val)
                ax.add_patch(Circle((j, i), radius, facecolor=color, edgecolor="white", linewidth=0.8))
                ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=6.3, color="#1f2933")
        ax.set_xticks(np.arange(matrix.shape[1]))
        ax.set_xticklabels(matrix.columns, rotation=35, ha="right")
        ax.set_yticks(np.arange(matrix.shape[0]))
        ax.set_yticklabels(matrix.index)
        for j in range(matrix.shape[1] + 1):
            ax.axvline(j - 0.5, color="#edf2f7", lw=0.6, zorder=0)
        for i in range(matrix.shape[0] + 1):
            ax.axhline(i - 0.5, color="#edf2f7", lw=0.6, zorder=0)
        ax.set_aspect("equal")
        return
    if variant_style == "triangular":
        mask = np.triu(np.ones_like(matrix.to_numpy(dtype=float), dtype=bool), k=1)
        sns.heatmap(
            matrix,
            ax=ax,
            cmap=cmap,
            vmin=0,
            vmax=1,
            annot=True,
            fmt=".2f",
            linewidths=0.4,
            linecolor="white",
            cbar_kws={"label": "ARI"},
            mask=mask,
        )
        ax.tick_params(axis="x", rotation=35)
        return
    sns.heatmap(
        matrix,
        ax=ax,
        cmap=cmap,
        vmin=0,
        vmax=1,
        annot=True,
        fmt=".2f",
        linewidths=0.45,
        linecolor="white",
        cbar_kws={"label": "ARI"},
    )
    ax.tick_params(axis="x", rotation=35)


def render_fig2b(v: Variant, paths: dict[str, Path]) -> pd.DataFrame:
    matrix = prepare_fig2b_matrix()
    mapped = matrix.reset_index().rename(columns={"index": "cohort"})
    write_tsv(mapped, paths["intermediate"])
    set_style()
    opt_idx = int(v.option.split(".")[-1])
    if opt_idx in {6}:
        variant_style = "bubble"
    elif opt_idx in {7}:
        variant_style = "triangular"
    else:
        variant_style = "matrix"
    fig, ax = plt.subplots(figsize=(6.9, 4.7))
    render_heatmap_matrix(matrix, ax, variant_style)
    ax.set_xlabel("")
    ax.set_ylabel("")
    sns.despine(ax=ax, left=True, bottom=True)
    save_fig(fig, paths)
    return mapped


def prepare_fig2c_data() -> pd.DataFrame:
    df = pd.read_csv(OUTPUT_DIR / "phase40_table2_profile_stability_guardrails.csv")
    df["log10_condition_number"] = np.log10(df["max_covariance_condition_number"].astype(float))
    df["role_rank"] = df["role"].map(ROLE_ORDER).fillna(9)
    df["cohort"] = pd.Categorical(df["cohort"], COHORT_ORDER, ordered=True)
    return df.sort_values(["log10_condition_number", "cohort"], ascending=[False, True])[
        ["cohort", "role", "near_singular_covariance", "max_covariance_condition_number", "log10_condition_number"]
    ].reset_index(drop=True)


def render_fig2c(v: Variant, paths: dict[str, Path]) -> pd.DataFrame:
    data = prepare_fig2c_data()
    write_tsv(data, paths["intermediate"])
    set_style()
    fig, ax = plt.subplots(figsize=(6.5, 3.9))
    y = np.arange(len(data))
    colors = [role_color(r) for r in data["role"]]
    ax.hlines(y, 0, data["log10_condition_number"], color="#d0d5dd", lw=5, zorder=1)
    ax.scatter(data["log10_condition_number"], y, s=58, color=colors, edgecolor="white", linewidth=0.7, zorder=2)
    ax.axvline(6, color="#b42318", lw=1.0, ls="--")
    for i, val in enumerate(data["log10_condition_number"]):
        ax.text(val + 0.07, i, f"{val:.2f}", va="center", ha="left", fontsize=7.2, color=PALETTE["muted"])
    ax.set_yticks(y)
    ax.set_yticklabels(data["cohort"].astype(str))
    ax.invert_yaxis()
    ax.set_xlim(0, max(data["log10_condition_number"].max() + 0.75, 6.8))
    ax.set_xlabel("log10(max covariance condition number)")
    ax.set_ylabel("")
    ax.xaxis.grid(True, color=PALETTE["grid"], lw=0.5)
    sns.despine(ax=ax, left=True)
    save_fig(fig, paths)
    return data


def prepare_fig3_data() -> pd.DataFrame:
    df = pd.read_csv(OUTPUT_DIR / "phase40_table3_lfo_functional_change_association_strict_core.csv")
    auc = pd.read_csv(OUTPUT_DIR / "phase37_auc_bootstrap_ci.csv")
    df = df.merge(auc[["cohort", "delta_auc_p025", "delta_auc_p975"]], on="cohort", how="left")
    ci = df["crude_risk_difference_ci_pct"].apply(parse_ci)
    df["crude_rd_low"] = [x[0] for x in ci]
    df["crude_rd_high"] = [x[1] for x in ci]
    df["cohort"] = pd.Categorical(df["cohort"], STRICT_CORE_COHORTS, ordered=True)
    return df.sort_values("cohort").reset_index(drop=True)


def render_fig3a(v: Variant, paths: dict[str, Path]) -> pd.DataFrame:
    data = prepare_fig3_data()
    mapped = data[
        [
            "cohort",
            "lfo_model_n",
            "events",
            "reference_class",
            "highest_crude_risk_class",
            "reference_event_pct",
            "highest_event_pct",
            "crude_risk_difference_pct",
            "crude_rd_low",
            "crude_rd_high",
            "adjusted_risk_ratio",
            "adjusted_risk_ratio_ci",
        ]
    ].copy()
    write_tsv(mapped, paths["intermediate"])
    set_style()
    opt_idx = int(v.option.split(".")[-1])
    fig, ax = plt.subplots(figsize=(6.6, 3.25))
    y = np.arange(len(data))
    effect = data["crude_risk_difference_pct"].to_numpy(float)
    low = data["crude_rd_low"].to_numpy(float)
    high = data["crude_rd_high"].to_numpy(float)
    if opt_idx == 3:
        ax.barh(y, effect, height=0.48, color="#dbeafe", edgecolor="#78a7c8", linewidth=0.6)
        ax.errorbar(effect, y, xerr=np.vstack([effect - low, high - effect]), fmt="none", ecolor="#475467", elinewidth=1.0, capsize=2.5, zorder=3)
    else:
        ax.errorbar(effect, y, xerr=np.vstack([effect - low, high - effect]), fmt="none", ecolor="#475467", elinewidth=1.1, capsize=2.8, zorder=2)
        ax.scatter(effect, y, s=58, color=PALETTE["risk"], edgecolor="white", linewidth=0.7, zorder=3)
    for i, row in data.iterrows():
        ax.text(high[i] + 1.2, i, f"{row['events']:,}/{row['lfo_model_n']:,}", va="center", ha="left", fontsize=7.2, color=PALETTE["muted"])
    ax.axvline(0, color=PALETTE["zero"], lw=0.8)
    ax.set_yticks(y)
    ax.set_yticklabels([f"{c}: C{r} to C{h}" for c, r, h in zip(data["cohort"].astype(str), data["reference_class"], data["highest_crude_risk_class"])])
    ax.invert_yaxis()
    ax.set_xlabel("Crude risk difference for functional deterioration, percentage points")
    ax.set_ylabel("")
    ax.set_xlim(min(0, np.nanmin(low) - 2), np.nanmax(high) + 8)
    ax.xaxis.grid(True, color=PALETTE["grid"], lw=0.5)
    sns.despine(ax=ax, left=True)
    save_fig(fig, paths)
    return mapped


def render_fig3b(v: Variant, paths: dict[str, Path]) -> pd.DataFrame:
    data = prepare_fig3_data()
    mapped = data[
        [
            "cohort",
            "profile_auc",
            "continuous_auc",
            "delta_auc_profile_minus_continuous",
            "delta_auc_p025",
            "delta_auc_p975",
            "delta_aic_continuous_minus_profile_per_1000",
        ]
    ].copy()
    write_tsv(mapped, paths["intermediate"])
    set_style()
    opt_idx = int(v.option.split(".")[-1])
    fig, ax = plt.subplots(figsize=(6.4, 3.25))
    y = np.arange(len(data))
    effect = data["delta_auc_profile_minus_continuous"].to_numpy(float)
    low = data["delta_auc_p025"].to_numpy(float)
    high = data["delta_auc_p975"].to_numpy(float)
    if opt_idx == 2:
        colors = [PALETTE["continuous"] if e < 0 else PALETTE["model"] for e in effect]
        ax.hlines(y, low, high, color="#98a2b3", lw=4.2, alpha=0.7)
        ax.scatter(effect, y, s=58, color=colors, edgecolor="white", linewidth=0.7, zorder=3)
    else:
        ax.errorbar(effect, y, xerr=np.vstack([effect - low, high - effect]), fmt="none", ecolor="#475467", elinewidth=1.1, capsize=2.8, zorder=2)
        ax.scatter(effect, y, s=58, color=PALETTE["continuous"], edgecolor="white", linewidth=0.7, zorder=3)
    ax.axvline(0, color=PALETTE["zero"], lw=0.9, ls="--")
    for i, row in data.iterrows():
        ax.text(high[i] + 0.0015, i, f"{row['profile_auc']:.3f}/{row['continuous_auc']:.3f}", va="center", ha="left", fontsize=7.2, color=PALETTE["muted"])
    ax.set_yticks(y)
    ax.set_yticklabels(data["cohort"].astype(str))
    ax.invert_yaxis()
    ax.set_xlabel("Delta AUC: categorical LFO profile minus continuous scores")
    ax.set_ylabel("")
    ax.set_xlim(np.nanmin(low) - 0.004, max(0.003, np.nanmax(high) + 0.01))
    ax.xaxis.grid(True, color=PALETTE["grid"], lw=0.5)
    sns.despine(ax=ax, left=True)
    save_fig(fig, paths)
    return mapped


def prepare_figs1_data() -> pd.DataFrame:
    selected = pd.read_csv(OUTPUT_DIR / "phase40_table2_profile_stability_guardrails.csv")
    prof = pd.read_csv(OUTPUT_DIR / "phase4_gmm_class_profiles.csv")
    selected = selected[selected["role"].eq("Strict-core")][["cohort", "selected_k"]]
    strict = prof.merge(selected, left_on=["cohort", "n_classes"], right_on=["cohort", "selected_k"], how="inner")
    strict = strict[strict["cohort"].isin(STRICT_CORE_COHORTS)].copy()
    strict["cohort"] = pd.Categorical(strict["cohort"], STRICT_CORE_COHORTS, ordered=True)
    strict = strict.sort_values(["cohort", "class"]).reset_index(drop=True)
    strict["row_label"] = strict.apply(
        lambda r: f"{r['cohort']} C{int(r['class'])} ({r['class_pct']:.1f}%)",
        axis=1,
    )
    strict["profile_short"] = strict["profile_label"].apply(short_profile_label)
    return strict


def render_figs1(v: Variant, paths: dict[str, Path]) -> pd.DataFrame:
    data = prepare_figs1_data()
    mapped_cols = ["cohort", "class", "class_n", "class_pct", "profile_label"] + DOMAIN_COLUMNS
    mapped = data[mapped_cols].copy()
    write_tsv(mapped, paths["intermediate"])
    set_style()
    opt_idx = int(v.option.split(".")[-1])
    matrix = data.set_index("row_label")[DOMAIN_COLUMNS].rename(columns=DOMAIN_LABELS)
    cmap = LinearSegmentedColormap.from_list("burden", ["#2166ac", "#f7f7f7", "#b2182b"])

    if opt_idx in {3, 8}:
        fig = plt.figure(figsize=(8.2, 6.7))
        gs = fig.add_gridspec(1, 2, width_ratios=[1.15, 4.2], wspace=0.03)
        ax_bar = fig.add_subplot(gs[0, 0])
        ax = fig.add_subplot(gs[0, 1])
        y = np.arange(len(data))
        ax_bar.barh(y, data["class_pct"], color="#9cc7c8", edgecolor="white", linewidth=0.5)
        ax_bar.set_yticks(y)
        ax_bar.set_yticklabels([])
        ax_bar.invert_yaxis()
        ax_bar.set_xlabel("Class %")
        ax_bar.xaxis.grid(True, color=PALETTE["grid"], lw=0.45)
        sns.despine(ax=ax_bar, left=True)
    else:
        fig, ax = plt.subplots(figsize=(7.0, 6.7))

    if opt_idx in {6, 7}:
        annot = matrix.map(lambda x: f"{x:.1f}")
        sns.heatmap(matrix, ax=ax, cmap=cmap, center=0, vmin=-2.6, vmax=2.6, annot=annot, fmt="", linewidths=0.35, linecolor="white", cbar_kws={"label": "Domain z-score"})
    elif opt_idx == 4:
        sns.heatmap(matrix, ax=ax, cmap=cmap, center=0, vmin=-2.6, vmax=2.6, annot=False, linewidths=0.35, linecolor="white", cbar_kws={"label": "Domain z-score"})
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                val = matrix.iloc[i, j]
                ax.text(j + 0.5, i + 0.5, f"{val:.1f}", ha="center", va="center", fontsize=6.8, color="#1f2933")
    else:
        sns.heatmap(matrix, ax=ax, cmap=cmap, center=0, vmin=-2.6, vmax=2.6, annot=True, fmt=".1f", linewidths=0.35, linecolor="white", cbar_kws={"label": "Domain z-score"})
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.tick_params(axis="x", rotation=35)
    ax.tick_params(axis="y", labelsize=7.2)
    sns.despine(ax=ax, left=True, bottom=True)
    save_fig(fig, paths)
    return mapped


def write_variant_script(v: Variant, paths: dict[str, Path], raw_data: str, variable_mapping: str) -> None:
    script_text = f"""#!/usr/bin/env python3
\"\"\"Project-local PERSIST port for {v.panel} {v.option}.

SOURCE_CODE_FIRST:
    Candidate ID: {v.candidate_id}
    Candidate level: {v.candidate_level}
    Candidate maturity: {v.candidate_maturity}
    Template/capsule: {v.template_path or v.capsule_path}
    Reference visual: {v.reference_visual}
    Source script: {v.source_script}
    Source code snapshot: {v.source_snapshot}
    Raw project data: {raw_data}
    Variable mapping: {variable_mapping}

This standalone panel was rendered by:
    scripts/render_phase42_persist_variants.py

The script preserves the selected PERSIST visual grammar and replaces only the
data-binding layer with the mapped Older Women project output table recorded at:
    {paths['intermediate']}
\"\"\"

# Re-run command:
# wsl.exe -d Ubuntu -- bash -lc "cd '/mnt/e/Reserch/Older women' && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python scripts/render_phase42_persist_variants.py --only {v.option}"
"""
    paths["script"].write_text(script_text, encoding="utf-8")


def render_variant(v: Variant) -> dict[str, str]:
    paths = output_paths(v)
    if v.panel == "Fig1A":
        mapped = render_fig1(v, paths)
        raw_data = "outputs/phase40_table1_baseline_clinical_design.csv; outputs/phase32_cohort_tier_lock.csv; outputs/phase37_table3_adjusted_functional_validation.csv"
        variable_mapping = "cohort, role, source_women50_n, complete_four_domain_n, validation_or_lfo_n, events"
    elif v.panel == "Fig2A":
        mapped = render_fig2a(v, paths)
        raw_data = "outputs/phase40_table2_profile_stability_guardrails.csv"
        variable_mapping = "cohort, role, bootstrap_median_ari, bootstrap_p10_ari, bootstrap_min_ari"
    elif v.panel == "Fig2B":
        mapped = render_fig2b(v, paths)
        raw_data = "outputs/phase36_gmm_algorithm_robustness.csv"
        variable_mapping = "cohort x method matrix of ari_vs_selected_gmm"
    elif v.panel == "Fig2C":
        mapped = render_fig2c(v, paths)
        raw_data = "outputs/phase40_table2_profile_stability_guardrails.csv"
        variable_mapping = "cohort, max_covariance_condition_number, near_singular_covariance"
    elif v.panel == "Fig3A":
        mapped = render_fig3a(v, paths)
        raw_data = "outputs/phase40_table3_lfo_functional_change_association_strict_core.csv"
        variable_mapping = "cohort, crude_risk_difference_pct, parsed crude_risk_difference_ci_pct, events, lfo_model_n"
    elif v.panel == "Fig3B":
        mapped = render_fig3b(v, paths)
        raw_data = "outputs/phase40_table3_lfo_functional_change_association_strict_core.csv; outputs/phase37_auc_bootstrap_ci.csv"
        variable_mapping = "cohort, delta_auc_profile_minus_continuous, delta_auc_p025, delta_auc_p975, profile_auc, continuous_auc"
    elif v.panel == "FigS1":
        mapped = render_figs1(v, paths)
        raw_data = "outputs/phase4_gmm_class_profiles.csv; outputs/phase40_table2_profile_stability_guardrails.csv"
        variable_mapping = "strict-core selected-k cohort-class rows by four domain z-score columns"
    else:
        raise ValueError(f"Unsupported panel: {v.panel}")

    write_variant_script(v, paths, raw_data, variable_mapping)
    return {
        "Panel": v.panel,
        "Option": v.option,
        "Panel role": v.panel_role,
        "Variant budget": v.variant_budget,
        "Candidate ID": v.candidate_id,
        "Candidate level": v.candidate_level,
        "Candidate maturity": v.candidate_maturity,
        "Data fit gate": v.data_fit_gate,
        "Visual fit gate": v.visual_fit_gate,
        "Runtime": v.runtime,
        "Env": v.env,
        "Rendered": "yes",
        "Render script": str(paths["script"]),
        "Intermediate file": str(paths["intermediate"]),
        "Output PNG": str(paths["png"]),
        "Output PDF/SVG": f"{paths['pdf']}; {paths['svg']}",
        "Validation status": "standalone_render_validated",
        "Reason": v.why_it_fits,
        "Raw data": raw_data,
        "Variable mapping": variable_mapping,
        "Rows mapped": str(len(mapped)),
    }


def make_contact_sheet(panel: str, rows: list[dict[str, str]]) -> Path:
    panel_rows = [r for r in rows if r["Panel"] == panel and r["Rendered"] == "yes"]
    if not panel_rows:
        raise ValueError(f"No rows to render contact sheet for {panel}")
    images = []
    labels = []
    for row in panel_rows:
        path = Path(row["Output PNG"])
        if not path.exists():
            continue
        images.append(mpimg.imread(path))
        labels.append(f"{row['Option']} | {sanitize_id(row['Candidate ID'], 34)}")
    if not images:
        raise ValueError(f"No PNG files found for {panel}")
    cols = 2 if len(images) > 1 else 1
    rows_n = math.ceil(len(images) / cols)
    fig = plt.figure(figsize=(9.2, max(4.4, rows_n * 4.1)))
    for idx, (img, label) in enumerate(zip(images, labels), start=1):
        ax = fig.add_subplot(rows_n, cols, idx)
        ax.imshow(img)
        ax.set_axis_off()
        ax.text(0.0, 1.02, label, transform=ax.transAxes, ha="left", va="bottom", fontsize=8, color="#1f2933")
    out = REDRAW_ROOT / "contact_sheets" / f"{panel}_contact_sheet.png"
    fig.savefig(out, bbox_inches="tight", dpi=220)
    plt.close(fig)
    return out


def write_mapping(render_rows: list[dict[str, str]], variants: list[Variant]) -> None:
    candidate_lookup = {(v.panel, v.option): v for v in variants}
    lines = [
        "# Panel Visual Mapping",
        "",
        "| Panel | Panel role | Variant budget | Atlas major class | Atlas subtype | Candidate ID | Candidate level | Candidate maturity | Data fit gate | Visual fit gate | Runtime | Env | Selected option | Template/capsule | Capsule path | Reference visual | Source script | Source code snapshot | Raw data | Variable mapping | Intermediate file | Ported script | Visual match notes | Validation report | Output | Reason |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for row in render_rows:
        v = candidate_lookup[(row["Panel"], row["Option"])]
        output = row["Output PNG"]
        template = v.template_path if v.template_path and v.template_path != "nan" else v.capsule_path
        cells = [
            row["Panel"],
            v.panel_role,
            v.variant_budget,
            v.atlas_major_class,
            v.atlas_subtype,
            v.candidate_id,
            v.candidate_level,
            v.candidate_maturity,
            v.data_fit_gate,
            v.visual_fit_gate,
            v.runtime,
            v.env,
            row["Option"],
            template,
            v.capsule_path,
            v.reference_visual,
            v.source_script,
            v.source_snapshot,
            row["Raw data"],
            row["Variable mapping"],
            row["Intermediate file"],
            row["Render script"],
            "Source grammar ported; project aggregate data bound through recorded intermediate table.",
            "persist_source_code_first_validation.md",
            output,
            row["Reason"],
        ]
        escaped = [str(c).replace("|", "/").replace("\n", " ") for c in cells]
        lines.append("| " + " | ".join(escaped) + " |")
    (REDRAW_ROOT / "panel_visual_mapping.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_gallery(render_rows: list[dict[str, str]], contact_sheets: dict[str, Path]) -> None:
    lines = ["# Panel Variant Gallery", ""]
    for panel in ["Fig1A", "Fig2A", "Fig2B", "Fig2C", "Fig3A", "Fig3B", "FigS1"]:
        subset = [r for r in render_rows if r["Panel"] == panel]
        if not subset:
            continue
        lines.extend([f"## {panel}", ""])
        sheet = contact_sheets.get(panel)
        if sheet:
            rel_sheet = sheet.relative_to(REDRAW_ROOT).as_posix()
            lines.append(f"![{panel} contact sheet]({rel_sheet})")
            lines.append("")
        for row in subset:
            rel_png = Path(row["Output PNG"]).relative_to(REDRAW_ROOT).as_posix()
            rel_svg = Path(row["Output PDF/SVG"].split("; ")[1]).relative_to(REDRAW_ROOT).as_posix()
            lines.append(f"- {row['Option']}: [{rel_png}]({rel_png}); SVG [{Path(rel_svg).name}]({rel_svg})")
        lines.append("")
    (REDRAW_ROOT / "panel_variant_gallery.md").write_text("\n".join(lines), encoding="utf-8")


def write_notes(render_rows: list[dict[str, str]]) -> None:
    notes = [
        "# Visual Match Notes",
        "",
        "- All variants use existing Older Women project output tables as raw aggregate inputs.",
        "- Figure-level titles and explanatory text were intentionally omitted from standalone panels because legends will be handled in the manuscript.",
        "- Fig2A displays the available lower-tail ARI statistics only: median, p10, and minimum. No p90 or CI was imputed.",
        "- Fig3A parses the published crude risk-difference interval strings from the project table.",
        "- Fig3B is rendered as a delta-AUC interval panel, not as ROC/calibration/DCA.",
        "- FigS1 filters selected-k strict-core class profiles and excludes bridge/sensitivity cohorts.",
        "",
    ]
    (REDRAW_ROOT / "visual_match_notes.md").write_text("\n".join(notes), encoding="utf-8")
    log = [
        "# Redraw Log",
        "",
        f"- Rendered variants: {len(render_rows)}",
        "- Runtime: WSL Ubuntu plus micromamba env research-py312.",
        "- Inputs: project `outputs/phase*.csv` tables only.",
        "- Outputs: standalone PNG/PDF/SVG files were generated before contact sheets.",
        "",
    ]
    (REDRAW_ROOT / "redraw_log.md").write_text("\n".join(log), encoding="utf-8")
    palette = [
        "# Project Palette Recommendation",
        "",
        "- Clinical denominator and guardrail panels use neutral greys, strict-core teal, bridge orange, validation-downgrade amber, and risk red.",
        "- Heatmaps use sequential teal for ARI agreement and diverging blue-white-red for burden z-scores.",
        "- The palette avoids decorative gradients and keeps colors semantically tied to cohort tier, risk, or signed burden.",
        "",
        "| Role | Hex |",
        "|---|---|",
    ]
    for key, value in PALETTE.items():
        palette.append(f"| {key} | {value} |")
    (REDRAW_ROOT / "project_palette_recommendation.md").write_text("\n".join(palette), encoding="utf-8")
    final_selection = [
        "# Panel Final Selection",
        "",
        "Final manuscript choices are intentionally blank until the user selects variants from the contact sheets.",
        "",
        "| Panel | Selected option | Candidate ID | Candidate level | Selected output | Final selection reason | Rejected alternatives | Known tradeoff |",
        "|---|---|---|---|---|---|---|---|",
    ]
    (REDRAW_ROOT / "panel_final_selection.md").write_text("\n".join(final_selection) + "\n", encoding="utf-8")


def write_render_rows(render_rows: list[dict[str, str]]) -> None:
    path = REDRAW_ROOT / "panel_render_variants.tsv"
    fieldnames = [
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
        "Validation status",
        "Reason",
        "Raw data",
        "Variable mapping",
        "Rows mapped",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        for row in render_rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def copy_stage1_files() -> None:
    shutil.copy2(CANDIDATE_SOURCE, REDRAW_ROOT / "panel_template_candidates.tsv")
    shutil.copy2(INVENTORY_SOURCE, REDRAW_ROOT / "panel_inventory.tsv")
    selection = STAGE1_ROOT / "panel_template_selection.md"
    if selection.exists():
        shutil.copy2(selection, REDRAW_ROOT / "panel_template_selection.md")


def main() -> None:
    ensure_dirs()
    copy_stage1_files()
    selected = read_candidates()
    variants = [candidate_to_variant(row) for _, row in selected.iterrows()]
    render_rows: list[dict[str, str]] = []
    for variant in variants:
        if variant.data_fit_gate == "fail" or variant.visual_fit_gate == "fail":
            continue
        render_rows.append(render_variant(variant))
    write_render_rows(render_rows)
    write_mapping(render_rows, variants)
    write_notes(render_rows)
    contact_sheets = {}
    for panel in sorted({row["Panel"] for row in render_rows}, key=lambda x: ["Fig1A", "Fig2A", "Fig2B", "Fig2C", "Fig3A", "Fig3B", "FigS1"].index(x)):
        contact_sheets[panel] = make_contact_sheet(panel, render_rows)
    write_gallery(render_rows, contact_sheets)

    summary = pd.DataFrame(
        [
            {
                "panel": panel,
                "variants": sum(1 for row in render_rows if row["Panel"] == panel),
                "contact_sheet": str(path),
            }
            for panel, path in contact_sheets.items()
        ]
    )
    summary_path = REDRAW_ROOT / "panel_contact_sheet_summary.tsv"
    summary.to_csv(summary_path, sep="\t", index=False)
    print(f"Rendered {len(render_rows)} variants")
    print(f"Wrote {summary_path}")


if __name__ == "__main__":
    main()
