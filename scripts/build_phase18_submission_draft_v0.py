from __future__ import annotations

import argparse
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont


RUN_DATE = "2026-06-01"
COHORT_ORDER = ["CHARLS", "ELSA", "HRS", "MHAS", "KLoSA", "SHARE", "LASI"]
MAIN_VALIDATION_COHORTS = ["CHARLS", "ELSA", "HRS", "MHAS"]
SEVEN_COHORT_DISPLAY = ["CHARLS", "ELSA", "HRS", "MHAS", "KLoSA", "SHARE", "LASI"]
DOMAIN_COLUMNS = ["functional_score", "cognitive_score", "affective_score", "cardiometabolic_chronic_score"]
DOMAIN_LABELS = ["Functional", "Cognitive", "Affective", "Cardiometabolic"]
ENDPOINT_ORDER = ["Functional deterioration >= 0.5 SD", "Chronic progression >= 1 condition", "All-cause mortality"]


def read_csv(output_dir: Path, name: str) -> pd.DataFrame:
    path = output_dir / name
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path, low_memory=False)


def fmt_int(value: object) -> str:
    if pd.isna(value):
        return "0"
    return f"{int(round(float(value))):,}"


def fmt_pct(value: object) -> str:
    if pd.isna(value):
        return "NA"
    return f"{float(value):.1f}%"


def fmt_num(value: object, digits: int = 1) -> str:
    if pd.isna(value):
        return "NA"
    return f"{float(value):.{digits}f}"


def clean_cell(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).replace("\n", " ").replace("|", "/").strip()


def markdown_table(frame: pd.DataFrame, columns: list[str]) -> str:
    if frame.empty:
        return "_No rows._"
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for _, row in frame.iterrows():
        lines.append("| " + " | ".join(clean_cell(row.get(column, "")) for column in columns) + " |")
    return "\n".join(lines)


def class_number(class_id: str) -> int:
    try:
        return int(str(class_id).split("_C", 1)[1])
    except (IndexError, ValueError):
        return 999


def short_label(label: object, max_len: int = 32) -> str:
    text = str(label)
    replacements = {
        "intermediate-burden": "intermediate",
        "elevated-burden": "elevated",
        "high-burden": "high",
        "low-burden": "low",
        "cardiometabolic-dominant": "cardiomet",
        "functional-dominant": "functional",
        "affective-dominant": "affective",
        "functional/cognitive-dominant": "func/cog",
        "functional/cardiometabolic-dominant": "func/cardio",
        "with spared cardiometabolic": "spared cardiomet",
        "with spared functional": "spared functional",
        "profile": "profile",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = " ".join(text.split())
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "..."


def conservative_auto_label(row: pd.Series) -> tuple[str, str, str, str]:
    original = str(row.get("label_en_final", ""))
    status = str(row.get("phase16_label_status", ""))
    reason = str(row.get("phase15_review_reason", ""))

    if status == "locked_for_draft":
        return original, "accepted_from_phase16", "none", "No Phase 17 review flag."
    if status == "baseline_only_hold":
        return original, "baseline_only_hold", "hold", "LASI lacks follow-up validation in the current cleaned CSV pass."
    if "generic severity-aligned" in reason:
        if "intermediate" in original:
            return "broad intermediate-burden profile", "auto_renamed_conservative", "signoff", "Generic severity-aligned label replaced with domain-neutral burden-profile label."
        if "elevated" in original:
            return "broad elevated-burden profile", "auto_renamed_conservative", "signoff", "Generic severity-aligned label replaced with domain-neutral burden-profile label."
        return "broad burden-profile label", "auto_renamed_conservative", "signoff", "Generic severity-aligned label replaced with domain-neutral burden-profile label."
    if "mortality HR drift" in reason or "Phase 14" in reason or "bridge" in reason.lower():
        return original, "locked_with_caveat_auto_v0", "caveat", "Keep baseline domain-profile name; avoid mortality-driven interpretation and report sensitivity caveat."
    return original, "auto_v0_needs_signoff", "signoff", "No deterministic rename rule; human signoff still required."


def build_label_decisions(dictionary: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for _, row in dictionary.iterrows():
        label, decision, marker, rationale = conservative_auto_label(row)
        rows.append(
            {
                "cohort": row["cohort"],
                "class_id": row["class_id"],
                "class": class_number(row["class_id"]),
                "phase16_label_status": row.get("phase16_label_status", ""),
                "phase18_label_en_v0": label,
                "phase18_decision_v0": decision,
                "phase18_marker": marker,
                "phase18_rationale": rationale,
                "human_signoff_required": int(decision != "accepted_from_phase16"),
                "phase16_label_en": row.get("label_en_final", ""),
                "phase15_review_reason": row.get("phase15_review_reason", ""),
                "phase14_stability_flag_count": row.get("phase14_stability_flag_count", 0),
                "phase14_flag_reasons": row.get("phase14_flag_reasons", ""),
            }
        )
    out = pd.DataFrame(rows)
    out["cohort_order"] = out["cohort"].map({cohort: i for i, cohort in enumerate(COHORT_ORDER)}).fillna(99)
    return out.sort_values(["cohort_order", "class"]).drop(columns=["cohort_order"]).reset_index(drop=True)


def build_final_dictionary(dictionary: pd.DataFrame, decisions: pd.DataFrame) -> pd.DataFrame:
    out = dictionary.merge(
        decisions[
            [
                "cohort",
                "class_id",
                "phase18_label_en_v0",
                "phase18_decision_v0",
                "phase18_marker",
                "phase18_rationale",
                "human_signoff_required",
            ]
        ],
        on=["cohort", "class_id"],
        how="left",
    )
    labels = []
    figure_labels = []
    for _, row in out.iterrows():
        label = str(row["phase18_label_en_v0"])
        marker = str(row.get("phase18_marker", ""))
        display = label
        fig = f"C{class_number(row['class_id'])}: {short_label(label)}"
        if marker == "caveat":
            display += " [caveat]"
            fig += " [cav]"
        elif marker == "hold":
            display += " [baseline-only]"
            fig += " [hold]"
        elif marker == "signoff":
            display += " [signoff]"
            fig += " [signoff]"
        labels.append(display)
        figure_labels.append(fig)
    out["phase18_label_en_display_v0"] = labels
    out["phase18_figure_label_short_v0"] = figure_labels
    out["phase18_dictionary_status"] = "auto_v0_human_signoff_required"
    out["cohort_order"] = out["cohort"].map({cohort: i for i, cohort in enumerate(COHORT_ORDER)}).fillna(99)
    return out.sort_values(["cohort_order", "class"]).drop(columns=["cohort_order"]).reset_index(drop=True)


def build_table2(table2: pd.DataFrame, final_dict: pd.DataFrame) -> pd.DataFrame:
    keep = [
        "cohort",
        "class_id",
        "phase18_label_en_v0",
        "phase18_label_en_display_v0",
        "phase18_decision_v0",
        "phase18_marker",
        "phase18_rationale",
        "human_signoff_required",
        "phase18_figure_label_short_v0",
    ]
    out = table2.drop(
        columns=[column for column in table2.columns if column.startswith("phase18_")],
        errors="ignore",
    ).merge(final_dict[keep], on=["cohort", "class_id"], how="left")
    out["cohort_order"] = out["cohort"].map({cohort: i for i, cohort in enumerate(COHORT_ORDER)}).fillna(99)
    return out.sort_values(["cohort_order", "class"]).drop(columns=["cohort_order"]).reset_index(drop=True)


def build_figure_map(table2: pd.DataFrame) -> pd.DataFrame:
    out = table2[
        [
            "cohort",
            "class_id",
            "class",
            "phase18_figure_label_short_v0",
            "phase18_label_en_display_v0",
            "phase18_decision_v0",
            "human_signoff_required",
            "functional_deterioration_ge_0_5sd_event_pct",
            "death_pct",
        ]
    ].copy()
    out["phase18_figure1_main_use"] = out["cohort"].isin(MAIN_VALIDATION_COHORTS).astype(int)
    out["phase18_figure1_sensitivity_use"] = out["cohort"].isin(SEVEN_COHORT_DISPLAY).astype(int)
    return out


def plot_profiles(table2: pd.DataFrame, cohorts: list[str], title: str, output_base: Path) -> Path:
    subset = table2[table2["cohort"].isin(cohorts)].copy()
    subset["cohort_order"] = subset["cohort"].map({cohort: i for i, cohort in enumerate(cohorts)}).fillna(99)
    subset = subset.sort_values(["cohort_order", "class"])
    ncols = 2
    nrows = int(math.ceil(len(cohorts) / ncols))
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(13, 3.7 * nrows), sharey=True)
    axes = np.asarray(axes).reshape(-1)
    x = np.arange(len(DOMAIN_COLUMNS))
    colors = plt.cm.tab10(np.linspace(0, 1, 10))

    for ax, cohort in zip(axes, cohorts):
        cdata = subset[subset["cohort"].eq(cohort)].sort_values("class")
        for idx, row in enumerate(cdata.to_dict("records")):
            values = [row.get(column, np.nan) for column in DOMAIN_COLUMNS]
            label = str(row.get("phase18_figure_label_short_v0", f"C{row.get('class', '')}"))
            pct = row.get("class_pct", np.nan)
            if pd.notna(pct):
                label += f" ({float(pct):.0f}%)"
            func = row.get("functional_deterioration_ge_0_5sd_event_pct", np.nan)
            death = row.get("death_pct", np.nan)
            if pd.notna(func):
                label += f" F{float(func):.0f}%"
            if pd.notna(death):
                label += f" M{float(death):.0f}%"
            ax.plot(x, values, marker="o", linewidth=1.8, color=colors[idx % len(colors)], label=label)
        ax.axhline(0, color="#666666", linewidth=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels(DOMAIN_LABELS, rotation=20, ha="right")
        ax.set_title(cohort)
        ax.set_ylabel("Standardized burden")
        ax.grid(axis="y", alpha=0.25)
        ax.legend(fontsize=6.3, frameon=False, loc="best")

    for ax in axes[len(cohorts) :]:
        ax.axis("off")
    fig.suptitle(title, y=0.995)
    fig.text(
        0.01,
        0.005,
        "[cav] sensitivity caveat; [hold] baseline-only class; [signoff] label needs human signoff. F/M are event percentages.",
        fontsize=8,
    )
    fig.tight_layout(rect=(0, 0.02, 1, 0.985))
    png_path = output_base.with_suffix(".png")
    pdf_path = output_base.with_suffix(".pdf")
    fig.savefig(png_path, dpi=240)
    fig.savefig(pdf_path)
    plt.close(fig)
    return png_path


def plot_heatmap(table3: pd.DataFrame, cohorts: list[str], metric: str, title: str, output_base: Path) -> Path:
    frame = table3[table3["cohort"].isin(cohorts)].copy()
    matrix = frame.pivot_table(index="endpoint", columns="cohort", values=metric, aggfunc="first").reindex(
        index=ENDPOINT_ORDER, columns=cohorts
    )
    values = matrix.to_numpy(dtype=float)
    max_abs = np.nanmax(np.abs(values)) if np.isfinite(values).any() else 1.0
    max_abs = max(10.0, min(float(max_abs), 220.0))
    fig, ax = plt.subplots(figsize=(max(7.0, 1.1 * len(cohorts) + 2.8), 3.5))
    im = ax.imshow(values, cmap="RdBu_r", vmin=-max_abs, vmax=max_abs, aspect="auto")
    ax.set_xticks(range(len(cohorts)))
    ax.set_xticklabels(cohorts, rotation=30, ha="right")
    ax.set_yticks(range(len(ENDPOINT_ORDER)))
    ax.set_yticklabels(["Functional", "Chronic", "Mortality"])
    ax.set_title(title)
    for i in range(len(ENDPOINT_ORDER)):
        for j in range(len(cohorts)):
            value = matrix.iloc[i, j]
            label = "NA" if pd.isna(value) else f"{float(value):.1f}"
            ax.text(j, i, label, ha="center", va="center", fontsize=8, color="black")
    cbar = fig.colorbar(im, ax=ax, shrink=0.82)
    cbar.set_label("Delta AIC: comparator minus endotype")
    fig.tight_layout()
    png_path = output_base.with_suffix(".png")
    pdf_path = output_base.with_suffix(".pdf")
    fig.savefig(png_path, dpi=240)
    fig.savefig(pdf_path)
    plt.close(fig)
    return png_path


def load_font(size: int = 42) -> ImageFont.ImageFont:
    for path in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    ]:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def paste_panel(canvas: Image.Image, image: Image.Image, y: int, label: str, common_width: int, margin: int, label_height: int) -> int:
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, y), label, fill=(0, 0, 0), font=load_font())
    y += label_height
    if image.width != common_width:
        height = int(round(image.height * common_width / image.width))
        image = image.resize((common_width, height), Image.Resampling.LANCZOS)
    canvas.paste(image, (margin, y))
    return y + image.height + margin


def combine_figure(profile_png: Path, severity_png: Path, domains_png: Path, output_base: Path) -> tuple[Path, Path]:
    images = [Image.open(path).convert("RGB") for path in [profile_png, severity_png, domains_png]]
    common_width = max(image.width for image in images)
    margin = 72
    label_height = 62
    scaled = [image.height if image.width == common_width else int(round(image.height * common_width / image.width)) for image in images]
    canvas = Image.new("RGB", (common_width + margin * 2, margin + sum(h + label_height + margin for h in scaled)), "white")
    y = margin
    for label, image in zip(
        [
            "A. Endotype profiles with Phase 18 auto-v0 labels",
            "B. Delta AIC versus severity tertiles",
            "C. Delta AIC versus four-domain continuous scores",
        ],
        images,
    ):
        y = paste_panel(canvas, image, y, label, common_width, margin, label_height)
    png_path = output_base.with_suffix(".png")
    pdf_path = output_base.with_suffix(".pdf")
    canvas.save(png_path, dpi=(300, 300))
    canvas.save(pdf_path, "PDF", resolution=300.0)
    return png_path, pdf_path


def build_figures(output_dir: Path, table2: pd.DataFrame, table3: pd.DataFrame) -> tuple[tuple[Path, Path], tuple[Path, Path]]:
    fig_dir = output_dir / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    main_profile = plot_profiles(table2, MAIN_VALIDATION_COHORTS, "Main Validation Cohorts: Phase 18 Auto-v0 Labels", fig_dir / "phase18_profile_main_validation")
    main_severity = plot_heatmap(table3, MAIN_VALIDATION_COHORTS, "delta_aic_severity_tertile_minus_endotype", "Main Validation: Endotype vs Severity Tertiles", fig_dir / "phase18_heatmap_main_vs_severity")
    main_domains = plot_heatmap(table3, MAIN_VALIDATION_COHORTS, "delta_aic_four_domain_scores_minus_endotype", "Main Validation: Endotype vs Four-Domain Scores", fig_dir / "phase18_heatmap_main_vs_four_domain_scores")
    main = combine_figure(main_profile, main_severity, main_domains, fig_dir / "phase18_figure1_main_validation_v0")

    seven_profile = plot_profiles(table2, SEVEN_COHORT_DISPLAY, "Seven-Cohort Sensitivity: Phase 18 Auto-v0 Labels", fig_dir / "phase18_profile_seven_cohort_sensitivity")
    seven_severity = plot_heatmap(table3, SEVEN_COHORT_DISPLAY, "delta_aic_severity_tertile_minus_endotype", "Seven-Cohort Sensitivity: Endotype vs Severity Tertiles", fig_dir / "phase18_heatmap_seven_vs_severity")
    seven_domains = plot_heatmap(table3, SEVEN_COHORT_DISPLAY, "delta_aic_four_domain_scores_minus_endotype", "Seven-Cohort Sensitivity: Endotype vs Four-Domain Scores", fig_dir / "phase18_heatmap_seven_vs_four_domain_scores")
    seven = combine_figure(seven_profile, seven_severity, seven_domains, fig_dir / "phase18_figure1_seven_cohort_sensitivity_v0")
    return main, seven


def format_table1(table1: pd.DataFrame) -> pd.DataFrame:
    out = table1.copy()
    for column in [
        "baseline_women_age50plus_n",
        "complete_four_domain_n",
        "selected_endotype_n",
        "functional_deterioration_ge_0_5sd_available_n",
        "functional_deterioration_ge_0_5sd_event_n",
        "death_n",
    ]:
        out[column] = out[column].map(fmt_int)
    out["cohort_order"] = out["cohort"].map({cohort: i for i, cohort in enumerate(COHORT_ORDER)}).fillna(99)
    return out.sort_values("cohort_order").drop(columns=["cohort_order"])


def format_table2(table2: pd.DataFrame) -> pd.DataFrame:
    out = table2.copy()
    out["class_pct"] = out["class_pct"].map(fmt_pct)
    for column in DOMAIN_COLUMNS:
        out[column] = out[column].map(lambda value: fmt_num(value, 2))
    out["cohort_order"] = out["cohort"].map({cohort: i for i, cohort in enumerate(COHORT_ORDER)}).fillna(99)
    return out.sort_values(["cohort_order", "class"]).drop(columns=["cohort_order"])


def format_table3(table3: pd.DataFrame) -> pd.DataFrame:
    out = table3.copy()
    for column in ["n_endotype", "events_endotype"]:
        out[column] = out[column].map(fmt_int)
    out["event_pct"] = out["event_pct"].map(fmt_pct)
    for column in ["delta_aic_severity_tertile_minus_endotype", "delta_aic_four_domain_scores_minus_endotype"]:
        out[column] = out[column].map(lambda value: fmt_num(value, 1))
    out["cohort_order"] = out["cohort"].map({cohort: i for i, cohort in enumerate(COHORT_ORDER)}).fillna(99)
    out["endpoint_order"] = out["endpoint"].map({endpoint: i for i, endpoint in enumerate(ENDPOINT_ORDER)}).fillna(99)
    return out.sort_values(["cohort_order", "endpoint_order"]).drop(columns=["cohort_order", "endpoint_order"])


def write_tables(output_dir: Path, manuscript_dir: Path, table1: pd.DataFrame, table2: pd.DataFrame, table3: pd.DataFrame) -> None:
    t1 = format_table1(table1)
    t2 = format_table2(table2)
    t3 = format_table3(table3)
    text = [
        "# Tables 1-3 Draft With Phase 18 Auto-v0 Labels",
        "",
        "Auto-v0 labels still require human signoff where indicated by `[signoff]`, `[caveat]`, or `[baseline-only]`.",
        "",
        "## Table 1. Cohort readiness and analytic denominators",
        "",
        markdown_table(
            t1,
            [
                "cohort",
                "analysis_tier",
                "manuscript_role",
                "baseline_women_age50plus_n",
                "complete_four_domain_n",
                "selected_endotype_n",
                "n_classes",
                "functional_deterioration_ge_0_5sd_available_n",
                "functional_deterioration_ge_0_5sd_event_n",
                "death_n",
            ],
        ),
        "",
        "## Table 2. Endotype profiles and Phase 18 labels",
        "",
        markdown_table(
            t2,
            [
                "cohort",
                "class_id",
                "class_n",
                "class_pct",
                "phase18_label_en_display_v0",
                "phase18_decision_v0",
                "functional_score",
                "cognitive_score",
                "affective_score",
                "cardiometabolic_chronic_score",
                "functional_or_formatted",
                "mortality_hr_formatted",
            ],
        ),
        "",
        "## Table 3. Outcome validation and comparator guardrails",
        "",
        markdown_table(
            t3,
            [
                "cohort",
                "endpoint",
                "n_endotype",
                "events_endotype",
                "event_pct",
                "delta_aic_severity_tertile_minus_endotype",
                "endotype_vs_severity_tertile",
                "delta_aic_four_domain_scores_minus_endotype",
                "endotype_vs_four_domain_scores",
            ],
        ),
    ]
    for path in [output_dir / "phase18_tables_1_3_v0.md", manuscript_dir / "tables_1_3_phase18_v0.md"]:
        path.write_text("\n".join(text) + "\n", encoding="utf-8")


def endpoint_counts(table3: pd.DataFrame, endpoint: str) -> tuple[int, int, int]:
    subset = table3[table3["endpoint"].eq(endpoint)]
    return subset["cohort"].nunique(), int(subset["n_endotype"].fillna(0).sum()), int(subset["events_endotype"].fillna(0).sum())


def write_journal_draft(
    output_dir: Path,
    manuscript_dir: Path,
    table1: pd.DataFrame,
    table2: pd.DataFrame,
    table3: pd.DataFrame,
    final_dict: pd.DataFrame,
    sources: pd.DataFrame,
    main_figure: tuple[Path, Path],
    seven_figure: tuple[Path, Path],
) -> None:
    baseline_total = int(table1["baseline_women_age50plus_n"].fillna(0).sum())
    selected_total = int(table1["selected_endotype_n"].fillna(0).sum())
    strict_total = int(table1.loc[table1["analysis_tier"].eq("strict_primary"), "selected_endotype_n"].fillna(0).sum())
    bridge_total = int(table1.loc[table1["analysis_tier"].eq("bridge_sensitivity"), "selected_endotype_n"].fillna(0).sum())
    f_cohorts, f_n, f_events = endpoint_counts(table3, "Functional deterioration >= 0.5 SD")
    m_cohorts, m_n, m_events = endpoint_counts(table3, "All-cause mortality")
    decision_counts = final_dict["phase18_decision_v0"].value_counts().to_dict()
    signoff_n = int(final_dict["human_signoff_required"].fillna(0).sum())
    decision_sentence = (
        f"Phase 18 auto-v0 labeling accepted {int(decision_counts.get('accepted_from_phase16', 0))} labels from the Phase 16 dictionary, "
        f"retained {int(decision_counts.get('locked_with_caveat_auto_v0', 0))} labels with explicit sensitivity caveats, "
        f"conservatively renamed {int(decision_counts.get('auto_renamed_conservative', 0))} generic severity-aligned labels, and "
        f"kept {int(decision_counts.get('baseline_only_hold', 0))} LASI labels as baseline-only profiles."
    )
    source_lines = [f"- {row['title']}. {row['url']}" for _, row in sources.iterrows()]

    text = [
        "# Multidomain Aging Endotypes Among Older Women Across Seven International Aging Cohorts",
        "",
        f"Version note: Phase 18 auto-v0 draft generated on {RUN_DATE}. Labels with caveat/signoff/hold markers require human approval before submission.",
        "",
        "## Abstract",
        "",
        "### Background",
        "",
        "Aging in older women is often summarized using single frailty or functional measures, although functional, cognitive, affective, and cardiometabolic burdens may cluster in distinct patterns.",
        "",
        "### Methods",
        "",
        (
            "We analyzed cleaned data from seven international aging cohorts. Women aged 50 years or older were used to construct cohort-specific multidomain endotype profiles from functional, cognitive, affective, and cardiometabolic/chronic disease domains. "
            "Associations with functional deterioration and all-cause mortality were evaluated within cohorts and benchmarked against severity-tertile and continuous four-domain score comparators."
        ),
        "",
        "### Results",
        "",
        (
            f"The eligible baseline screen included {fmt_int(baseline_total)} women. Endotype modeling yielded {fmt_int(selected_total)} selected assignments, including {fmt_int(strict_total)} strict-primary and {fmt_int(bridge_total)} bridge-sensitivity assignments. "
            f"Phase 18 auto-v0 labeling retained {len(final_dict)} cohort-specific classes; {signoff_n} labels still require human signoff or explicit caveat handling. Functional deterioration validation included {f_cohorts} cohorts, {fmt_int(f_n)} participants, and {fmt_int(f_events)} events. "
            f"Mortality validation included {m_cohorts} cohorts, {fmt_int(m_n)} participants, and {fmt_int(m_events)} deaths. Endotype profiles showed interpretable multidomain heterogeneity, but continuous four-domain score models generally outperformed endotype-only models."
        ),
        "",
        "### Conclusions",
        "",
        "Women-only multidomain endotypes can summarize clinically interpretable aging heterogeneity across international cohorts, but the current evidence supports an interpretability and heterogeneity-mapping claim rather than universal prediction superiority.",
        "",
        "## Introduction",
        "",
        (
            "Population aging is commonly summarized using frailty indices, intrinsic-capacity measures, or single-domain functional transitions. These approaches are useful, but they can compress heterogeneous aging processes into a single severity scale. "
            "For older women, this is a limitation because functional, cognitive, affective, and cardiometabolic burdens may combine in clinically different ways even when overall burden appears similar."
        ),
        "",
        (
            "Recent studies have examined multidimensional aging trajectories, intrinsic capacity, symptom clusters, and predeath trajectories. The current study is therefore not positioned as the first multidimensional aging analysis or as a new frailty index. "
            "Its narrower contribution is a women-focused multidomain endotype analysis across seven international aging cohorts with explicit comparator and sensitivity guardrails."
        ),
        "",
        "## Methods",
        "",
        (
            "The analysis used cleaned cohort CSV files for CHARLS, ELSA, HRS, KLoSA, LASI, MHAS, and SHARE. The primary population was women aged 50 years or older. "
            "Domain scores were constructed so that higher values represented worse burden. Cohort-specific Gaussian mixture models were used for first-pass endotype assignment, with model selection constrained by convergence and minimum class-size rules. "
            "Functional deterioration was treated as the primary validation endpoint. Mortality was treated as secondary because proportional-hazards diagnostics, piecewise sensitivity, and covariate-sensitivity screens flagged selected class terms."
        ),
        "",
        "## Results",
        "",
        (
            f"Across the seven cleaned cohorts, the baseline screen included {fmt_int(baseline_total)} women aged 50 years or older. Strict-primary endotype construction contributed {fmt_int(strict_total)} selected assignments, while KLoSA and SHARE contributed {fmt_int(bridge_total)} bridge-sensitivity assignments. "
            "LASI remained baseline-profile only because follow-up validation is unavailable in the current cleaned CSV pass."
        ),
        "",
        (
            f"The selected models produced {len(final_dict)} cohort-specific classes. {decision_sentence} "
            "Mortality-drift and covariate-sensitivity-flagged labels were retained as baseline domain-profile names with explicit caveats."
        ),
        "",
        (
            f"Functional deterioration validation was available in {f_cohorts} cohorts, including {fmt_int(f_n)} participants and {fmt_int(f_events)} events. "
            "The endotype-versus-severity pattern was mixed across cohorts, while continuous four-domain score models were favored across the tested functional comparisons."
        ),
        "",
        (
            f"Mortality validation was available in {m_cohorts} cohorts, including {fmt_int(m_n)} participants and {fmt_int(m_events)} deaths. "
            "Mortality results should remain secondary because selected class terms showed proportional-hazards, piecewise, or covariate-sensitivity concerns."
        ),
        "",
        f"Figure 1 main validation file: `{main_figure[0].as_posix()}`. Seven-cohort sensitivity file: `{seven_figure[0].as_posix()}`.",
        "",
        "## Discussion",
        "",
        (
            "This women-only analysis identified interpretable multidomain aging profiles across several international cohort systems. The profiles were not reducible to a single low-to-high severity gradient; instead, several classes showed functional, cardiometabolic, affective, or spared-domain structure. "
            "This supports a descriptive and interpretive contribution: multidomain endotypes can summarize clinically meaningful heterogeneity among older women."
        ),
        "",
        (
            "The results do not support an unrestricted prediction-superiority claim. Continuous four-domain score models generally outperformed endotype-only models, indicating that class membership should be viewed as a compact clinical summary rather than a universally stronger risk model. "
            "This distinction should remain central in the abstract, results, and discussion."
        ),
        "",
        (
            "The study has several limitations: reliance on cleaned CSV variables rather than a full raw-file harmonization pass, cohort differences in measurement, bridge definitions for KLoSA and SHARE, missing LASI follow-up validation, incomplete expanded-core covariate coverage, and mortality time-drift concerns in selected classes. "
            "The Phase 18 auto-v0 labels also require human signoff before final submission."
        ),
        "",
        "## References To Format",
        "",
        *source_lines,
    ]
    for path in [output_dir / "phase18_journal_style_manuscript_v0.md", manuscript_dir / "journal_style_manuscript_v0.md"]:
        path.write_text("\n".join(text) + "\n", encoding="utf-8")


def write_checklist(output_dir: Path, manuscript_dir: Path, final_dict: pd.DataFrame, sources: pd.DataFrame) -> None:
    signoff = final_dict[final_dict["human_signoff_required"].fillna(0).eq(1)].copy()
    text = [
        "# Phase 18 Submission Readiness Checklist",
        "",
        "## Blocking Before Submission",
        "",
        f"- Resolve {len(signoff)} labels with `human_signoff_required == 1` in `outputs/phase18_final_label_dictionary_v0.csv`.",
        "- Confirm target journal and adapt word count, table count, and supplement format.",
        "- Replace URL-style references with formal citations and a reference list.",
        "- Decide whether the main figure uses the four main validation cohorts only or the seven-cohort sensitivity display.",
        "- Confirm whether LASI remains in Table 1/Table 2 only or is moved entirely to supplement.",
        "",
        "## Label Signoff Rows",
        "",
        markdown_table(
            signoff[
                [
                    "cohort",
                    "class_id",
                    "phase18_label_en_display_v0",
                    "phase18_decision_v0",
                    "phase18_rationale",
                ]
            ],
            ["cohort", "class_id", "phase18_label_en_display_v0", "phase18_decision_v0", "phase18_rationale"],
        ),
        "",
        "## Reference Formatting Queue",
        "",
        markdown_table(sources, ["source_id", "title", "url", "collision_risk"]),
    ]
    for path in [output_dir / "phase18_submission_readiness_checklist.md", manuscript_dir / "submission_readiness_checklist.md"]:
        path.write_text("\n".join(text) + "\n", encoding="utf-8")


def write_report(
    output_dir: Path,
    decisions: pd.DataFrame,
    main_figure: tuple[Path, Path],
    seven_figure: tuple[Path, Path],
) -> None:
    text = [
        "# Phase 18 Submission Draft v0 Report",
        "",
        f"Run date: {RUN_DATE}.",
        "",
        "## Outputs",
        "",
        "- `outputs/phase18_label_decisions_auto_v0.csv`",
        "- `outputs/phase18_final_label_dictionary_v0.csv`",
        "- `outputs/phase18_table2_final_labels_v0.csv`",
        "- `outputs/phase18_figure1_label_map_v0.csv`",
        "- `outputs/phase18_tables_1_3_v0.md`",
        "- `outputs/phase18_journal_style_manuscript_v0.md`",
        "- `outputs/phase18_submission_readiness_checklist.md`",
        "- `manuscript/journal_style_manuscript_v0.md`",
        "- `manuscript/submission_readiness_checklist.md`",
        "",
        "## Decision Counts",
        "",
        markdown_table(
            decisions["phase18_decision_v0"].value_counts().rename_axis("phase18_decision_v0").reset_index(name="n"),
            ["phase18_decision_v0", "n"],
        ),
        "",
        "## Figure Files",
        "",
        f"- Main validation Figure 1 v0: `{main_figure[0].as_posix()}` and `{main_figure[1].as_posix()}`",
        f"- Seven-cohort sensitivity Figure 1 v0: `{seven_figure[0].as_posix()}` and `{seven_figure[1].as_posix()}`",
    ]
    (output_dir / "phase18_submission_draft_v0_report.md").write_text("\n".join(text) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    parser.add_argument("--manuscript-dir", type=Path, default=Path("manuscript"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir: Path = args.output_dir
    manuscript_dir: Path = args.manuscript_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    manuscript_dir.mkdir(parents=True, exist_ok=True)

    phase16_dict = read_csv(output_dir, "phase16_locked_label_dictionary.csv")
    table1 = read_csv(output_dir, "phase11_table1_cohort_readiness.csv")
    table2 = read_csv(output_dir, "phase16_table2_locked_labels.csv")
    table3 = read_csv(output_dir, "phase11_table3_outcome_validation_summary.csv")
    sources = read_csv(output_dir, "phase15_novelty_refresh_sources.csv")

    decisions = build_label_decisions(phase16_dict)
    final_dict = build_final_dictionary(phase16_dict, decisions)
    table2_final = build_table2(table2, final_dict)
    figure_map = build_figure_map(table2_final)

    decisions.to_csv(output_dir / "phase18_label_decisions_auto_v0.csv", index=False)
    final_dict.to_csv(output_dir / "phase18_final_label_dictionary_v0.csv", index=False)
    table2_final.to_csv(output_dir / "phase18_table2_final_labels_v0.csv", index=False)
    figure_map.to_csv(output_dir / "phase18_figure1_label_map_v0.csv", index=False)

    main_figure, seven_figure = build_figures(output_dir, table2_final, table3)
    write_tables(output_dir, manuscript_dir, table1, table2_final, table3)
    write_journal_draft(output_dir, manuscript_dir, table1, table2_final, table3, final_dict, sources, main_figure, seven_figure)
    write_checklist(output_dir, manuscript_dir, final_dict, sources)
    write_report(output_dir, decisions, main_figure, seven_figure)


if __name__ == "__main__":
    main()
