from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont


COHORT_ORDER = {
    "CHARLS": 1,
    "ELSA": 2,
    "HRS": 3,
    "LASI": 4,
    "MHAS": 5,
    "KLoSA": 6,
    "SHARE": 7,
}

OUTPUT_ROLE = {
    "strict_primary": "primary",
    "bridge_sensitivity": "bridge_sensitivity",
}


def read_csv(output_dir: Path, name: str) -> pd.DataFrame:
    return pd.read_csv(output_dir / name, low_memory=False)


def cohort_sort_key(df: pd.DataFrame) -> pd.Series:
    return df["cohort"].map(COHORT_ORDER).fillna(99)


def round_numeric(df: pd.DataFrame, digits: int = 2) -> pd.DataFrame:
    out = df.copy()
    float_cols = out.select_dtypes(include=["float"]).columns
    out[float_cols] = out[float_cols].round(digits)
    return out


def build_table1(output_dir: Path) -> pd.DataFrame:
    phase1 = read_csv(output_dir, "phase1_baseline_feasibility.csv")
    missing = read_csv(output_dir, "phase3_domain_missingness.csv").rename(
        columns={"n": "domain_score_baseline_n"}
    )
    best = read_csv(output_dir, "phase4_best_model_summary.csv").rename(
        columns={"n": "selected_endotype_n"}
    )
    follow = read_csv(output_dir, "phase5_followup_outcome_inventory.csv")
    mortality = read_csv(output_dir, "phase6_mortality_summary.csv")

    follow_overall = follow[follow["group_type"] == "overall"].copy()
    mortality_overall = mortality[mortality["group_type"] == "overall"].copy()

    table = missing.merge(
        phase1[["cohort", "female_age50plus_rows"]],
        on="cohort",
        how="left",
    )
    table = table.merge(
        best[
            [
                "analysis_set",
                "analysis_tier",
                "cohort",
                "selected_endotype_n",
                "n_classes",
                "min_class_n",
                "min_class_pct",
                "mean_max_posterior",
                "entropy_separation",
                "selection_rule",
            ]
        ],
        on=["analysis_set", "analysis_tier", "cohort"],
        how="left",
    )
    table = table.merge(
        follow_overall[
            [
                "analysis_set",
                "analysis_tier",
                "cohort",
                "baseline_n",
                "any_followup_n",
                "any_followup_pct",
                "median_followup_year_span",
                "functional_deterioration_ge_0_5sd_available_n",
                "functional_deterioration_ge_0_5sd_event_n",
                "functional_deterioration_ge_0_5sd_event_pct",
                "chronic_progression_ge_1_condition_available_n",
                "chronic_progression_ge_1_condition_event_n",
                "chronic_progression_ge_1_condition_event_pct",
            ]
        ],
        on=["analysis_set", "analysis_tier", "cohort"],
        how="left",
    )
    table = table.merge(
        mortality_overall[
            [
                "analysis_set",
                "analysis_tier",
                "cohort",
                "mortality_followup_available_n",
                "mortality_followup_available_pct",
                "death_n",
                "death_pct",
                "median_followup_time_years",
                "max_followup_time_years",
            ]
        ],
        on=["analysis_set", "analysis_tier", "cohort"],
        how="left",
    )

    table = table.rename(
        columns={
            "female_age50plus_rows": "baseline_women_age50plus_n",
            "baseline_n": "followup_inventory_baseline_n",
            "median_followup_year_span": "median_nonmortality_followup_year_span",
            "median_followup_time_years": "median_mortality_followup_years",
            "max_followup_time_years": "max_mortality_followup_years",
        }
    )

    def role(row: pd.Series) -> str:
        if row["cohort"] == "LASI":
            return "baseline_profile_only_current_csv"
        if row["analysis_tier"] == "bridge_sensitivity":
            return "bridge_sensitivity_validation"
        return "primary_validation"

    table["manuscript_role"] = table.apply(role, axis=1)
    table["cohort_order"] = cohort_sort_key(table)
    ordered = [
        "analysis_set",
        "analysis_tier",
        "manuscript_role",
        "cohort",
        "wave",
        "baseline_women_age50plus_n",
        "domain_score_baseline_n",
        "complete_four_domain_n",
        "complete_four_domain_pct",
        "selected_endotype_n",
        "n_classes",
        "min_class_n",
        "min_class_pct",
        "mean_max_posterior",
        "entropy_separation",
        "any_followup_n",
        "any_followup_pct",
        "median_nonmortality_followup_year_span",
        "functional_deterioration_ge_0_5sd_available_n",
        "functional_deterioration_ge_0_5sd_event_n",
        "functional_deterioration_ge_0_5sd_event_pct",
        "chronic_progression_ge_1_condition_available_n",
        "chronic_progression_ge_1_condition_event_n",
        "chronic_progression_ge_1_condition_event_pct",
        "mortality_followup_available_n",
        "mortality_followup_available_pct",
        "death_n",
        "death_pct",
        "median_mortality_followup_years",
        "max_mortality_followup_years",
        "selection_rule",
    ]
    out = table[[column for column in ordered if column in table.columns]].copy()
    out["cohort_order"] = cohort_sort_key(out)
    return out.sort_values(["cohort_order"]).drop(columns=["cohort_order"]).reset_index(drop=True)


def build_table2(output_dir: Path) -> pd.DataFrame:
    labels = read_csv(output_dir, "phase10_class_label_candidates.csv")
    labels["class"] = pd.to_numeric(labels["class"], errors="coerce").astype("Int64")
    labels["class_id"] = labels["cohort"] + "_C" + labels["class"].astype(str)
    ordered = [
        "analysis_set",
        "analysis_tier",
        "cohort",
        "class_id",
        "class",
        "class_n",
        "class_pct",
        "label_en",
        "label_zh",
        "label_confidence",
        "high_domains",
        "spared_domains",
        "outcome_flags",
        "severity_mean",
        "functional_score",
        "cognitive_score",
        "affective_score",
        "cardiometabolic_chronic_score",
        "functional_deterioration_ge_0_5sd_event_pct",
        "functional_or_formatted",
        "chronic_progression_ge_1_condition_event_pct",
        "chronic_or_formatted",
        "death_pct",
        "mortality_hr_formatted",
        "mortality_drift_flag",
        "profile_label",
    ]
    out = labels[[column for column in ordered if column in labels.columns]].copy()
    out["cohort_order"] = cohort_sort_key(out)
    out = out.sort_values(["cohort_order", "class"]).drop(columns=["cohort_order"])
    return out.reset_index(drop=True)


def comparator_label(delta: float | int | None, better: str, comparator: str) -> str:
    if pd.isna(delta):
        return "not_available"
    if delta > 2:
        return f"{better}_favored"
    if delta < -2:
        return f"{comparator}_favored"
    return "similar_by_aic"


def add_after_label(delta: float | int | None) -> str:
    if pd.isna(delta):
        return "not_available"
    if delta > 2:
        return "endotype_adds_after_four_domains"
    if delta < -2:
        return "four_domains_only_favored"
    return "similar_after_four_domains"


def build_functional_chronic_validation(output_dir: Path) -> pd.DataFrame:
    comp = read_csv(output_dir, "phase5_domain_comparator_comparison.csv")
    rows = []
    for _, row in comp.iterrows():
        rows.append(
            {
                "analysis_set": row["analysis_set"],
                "analysis_tier": row["analysis_tier"],
                "cohort": row["cohort"],
                "endpoint": row["outcome_label"],
                "endpoint_role": row["outcome_priority"],
                "n_endotype": row["n_endotype"],
                "events_endotype": row["events_endotype"],
                "event_pct": row["event_pct_endotype"],
                "median_followup_years": pd.NA,
                "delta_aic_severity_tertile_minus_endotype": row["delta_aic_severity_tertile_minus_endotype"],
                "delta_auc_endotype_minus_severity_tertile": row["delta_auc_endotype_minus_severity_tertile"],
                "delta_aic_four_domain_scores_minus_endotype": row["delta_aic_four_domain_scores_minus_endotype"],
                "delta_auc_endotype_minus_four_domain_scores": row["delta_auc_endotype_minus_four_domain_scores"],
                "delta_aic_four_domains_minus_endotype_plus_domains": row["delta_aic_four_domains_minus_endotype_plus_domains"],
                "endotype_vs_severity_tertile": comparator_label(
                    row["delta_aic_severity_tertile_minus_endotype"],
                    "endotype",
                    "severity_tertile",
                ),
                "endotype_vs_four_domain_scores": comparator_label(
                    row["delta_aic_four_domain_scores_minus_endotype"],
                    "endotype",
                    "four_domain_scores",
                ),
                "endotype_plus_four_domain_note": add_after_label(
                    row["delta_aic_four_domains_minus_endotype_plus_domains"]
                ),
                "ph_screen_flag": pd.NA,
                "mortality_drift_flagged_classes": "",
                "validation_note": "logistic_age_adjusted_domain_comparator",
            }
        )
    return pd.DataFrame(rows)


def build_mortality_validation(output_dir: Path) -> pd.DataFrame:
    comp = read_csv(output_dir, "phase6_mortality_model_comparison.csv")
    ph = read_csv(output_dir, "phase8_mortality_ph_diagnostic_summary.csv")
    drift = read_csv(output_dir, "phase9_mortality_piecewise_stability.csv")
    drift["drift_flag"] = (
        (pd.to_numeric(drift.get("direction_change", 0), errors="coerce").fillna(0) == 1)
        | (pd.to_numeric(drift.get("large_time_drift", 0), errors="coerce").fillna(0) == 1)
    )
    drift_flags = (
        drift[drift["drift_flag"]]
        .assign(term_label=lambda x: "C" + x["term_label"].astype(str))
        .groupby(["analysis_set", "cohort"])["term_label"]
        .apply(lambda x: ";".join(x))
        .reset_index(name="mortality_drift_flagged_classes")
    )
    merged = comp.merge(
        ph[["analysis_set", "cohort", "ph_screen_flag"]],
        on=["analysis_set", "cohort"],
        how="left",
    ).merge(drift_flags, on=["analysis_set", "cohort"], how="left")
    merged["mortality_drift_flagged_classes"] = merged["mortality_drift_flagged_classes"].fillna("")

    rows = []
    for _, row in merged.iterrows():
        note = "cox_age_adjusted_secondary"
        if row.get("ph_screen_flag", 0) == 1 or row["mortality_drift_flagged_classes"]:
            note = "cox_secondary_with_ph_or_piecewise_sensitivity"
        rows.append(
            {
                "analysis_set": row["analysis_set"],
                "analysis_tier": row["analysis_tier"],
                "cohort": row["cohort"],
                "endpoint": "All-cause mortality",
                "endpoint_role": "secondary",
                "n_endotype": row["n_endotype"],
                "events_endotype": row["events_endotype"],
                "event_pct": row["event_pct_endotype"],
                "median_followup_years": row["median_followup_time_years_endotype"],
                "delta_aic_severity_tertile_minus_endotype": row[
                    "delta_partial_aic_severity_tertile_minus_endotype"
                ],
                "delta_auc_endotype_minus_severity_tertile": pd.NA,
                "delta_aic_four_domain_scores_minus_endotype": row[
                    "delta_partial_aic_four_domain_scores_minus_endotype"
                ],
                "delta_auc_endotype_minus_four_domain_scores": pd.NA,
                "delta_aic_four_domains_minus_endotype_plus_domains": row[
                    "delta_partial_aic_four_domains_minus_endotype_plus_domains"
                ],
                "endotype_vs_severity_tertile": comparator_label(
                    row["delta_partial_aic_severity_tertile_minus_endotype"],
                    "endotype",
                    "severity_tertile",
                ),
                "endotype_vs_four_domain_scores": comparator_label(
                    row["delta_partial_aic_four_domain_scores_minus_endotype"],
                    "endotype",
                    "four_domain_scores",
                ),
                "endotype_plus_four_domain_note": add_after_label(
                    row["delta_partial_aic_four_domains_minus_endotype_plus_domains"]
                ),
                "ph_screen_flag": row.get("ph_screen_flag", pd.NA),
                "mortality_drift_flagged_classes": row["mortality_drift_flagged_classes"],
                "validation_note": note,
            }
        )
    return pd.DataFrame(rows)


def build_table3(output_dir: Path) -> pd.DataFrame:
    out = pd.concat(
        [
            build_functional_chronic_validation(output_dir),
            build_mortality_validation(output_dir),
        ],
        ignore_index=True,
        sort=False,
    )
    endpoint_order = {
        "Functional deterioration >= 0.5 SD": 1,
        "Chronic progression >= 1 condition": 2,
        "All-cause mortality": 3,
    }
    out["cohort_order"] = cohort_sort_key(out)
    out["endpoint_order"] = out["endpoint"].map(endpoint_order).fillna(99)
    return (
        out.sort_values(["cohort_order", "endpoint_order"])
        .drop(columns=["cohort_order", "endpoint_order"])
        .reset_index(drop=True)
    )


def markdown_table(df: pd.DataFrame, columns: list[str], max_rows: int | None = None) -> list[str]:
    if df.empty:
        return ["No rows."]
    show = df.copy()
    if max_rows is not None:
        show = show.head(max_rows)
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in show[columns].to_dict("records"):
        values = []
        for column in columns:
            value = row[column]
            if pd.isna(value):
                values.append("")
            elif isinstance(value, float):
                values.append(f"{value:.2f}")
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    if max_rows is not None and len(df) > max_rows:
        lines.append(f"| ... | ... | ... | ... | ... | ... |")
    return lines


def save_csv(df: pd.DataFrame, path: Path) -> None:
    round_numeric(df).to_csv(path, index=False, encoding="utf-8-sig")


def paste_panel(
    canvas: Image.Image,
    image: Image.Image,
    y: int,
    panel_label: str,
    common_width: int,
    margin: int,
    label_height: int,
) -> int:
    draw = ImageDraw.Draw(canvas)
    font = load_panel_font()
    draw.text((margin, y), panel_label, fill=(0, 0, 0), font=font)
    y += label_height
    if image.width != common_width:
        height = int(round(image.height * common_width / image.width))
        image = image.resize((common_width, height), Image.Resampling.LANCZOS)
    canvas.paste(image, (margin, y))
    return y + image.height + margin


def load_panel_font() -> ImageFont.ImageFont:
    for path in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
    ]:
        try:
            return ImageFont.truetype(path, 44)
        except OSError:
            continue
    return ImageFont.load_default()


def build_figure1(output_dir: Path) -> tuple[Path, Path]:
    figure_dir = output_dir / "figures"
    panel_paths = [
        figure_dir / "phase7_endotype_profiles_with_outcomes.png",
        figure_dir / "phase7_aic_delta_vs_severity_tertile.png",
        figure_dir / "phase7_aic_delta_vs_four_domain_scores.png",
    ]
    images = [Image.open(path).convert("RGB") for path in panel_paths]
    common_width = images[0].width
    margin = 72
    label_height = 62
    scaled_heights = [
        img.height if img.width == common_width else int(round(img.height * common_width / img.width))
        for img in images
    ]
    canvas_width = common_width + margin * 2
    canvas_height = margin + sum(label_height + height + margin for height in scaled_heights)
    canvas = Image.new("RGB", (canvas_width, canvas_height), "white")
    y = margin
    for label, image in zip(
        [
            "A. Endotype profiles and outcome rates",
            "B. Delta AIC versus severity tertiles",
            "C. Delta AIC versus four-domain continuous scores",
        ],
        images,
    ):
        y = paste_panel(canvas, image, y, label, common_width, margin, label_height)

    png_path = figure_dir / "phase11_figure1_manuscript_draft.png"
    pdf_path = figure_dir / "phase11_figure1_manuscript_draft.pdf"
    canvas.save(png_path, dpi=(300, 300))
    canvas.save(pdf_path, "PDF", resolution=300.0)
    return png_path, pdf_path


def write_report(
    output_dir: Path,
    table1: pd.DataFrame,
    table2: pd.DataFrame,
    table3: pd.DataFrame,
    figure_png: Path,
    figure_pdf: Path,
) -> None:
    functional_ready = table1["functional_deterioration_ge_0_5sd_available_n"].fillna(0).gt(0).sum()
    mortality_ready = table1["mortality_followup_available_n"].fillna(0).gt(0).sum()
    baseline_total = table1["baseline_women_age50plus_n"].fillna(0).sum()
    selected_total = table1["selected_endotype_n"].fillna(0).sum()

    lines = [
        "# Phase 11 Manuscript Tables And Figure Draft",
        "",
        "This phase converts the analysis outputs into manuscript-facing draft tables.",
        "",
        "## Readiness Snapshot",
        "",
        f"- Phase 1 earliest-baseline women aged 50+ across seven cohorts: {baseline_total:,.0f}.",
        f"- Selected complete four-domain endotype sample, including wave-adjusted SHARE sensitivity: {selected_total:,.0f}.",
        f"- Cohorts with functional deterioration validation in current CSV pass: {functional_ready}.",
        f"- Cohorts with mortality validation in current CSV pass: {mortality_ready}.",
        "- SHARE uses a wave-adjusted sensitivity denominator, so its selected endotype N is not the same denominator as the Phase 1 earliest-baseline N.",
        "- LASI remains baseline-profile only for follow-up validation in the current cleaned CSV pass.",
        "",
        "## Draft Table 1: Cohort Readiness",
        "",
    ]
    table1_cols = [
        "cohort",
        "analysis_tier",
        "manuscript_role",
        "baseline_women_age50plus_n",
        "domain_score_baseline_n",
        "complete_four_domain_n",
        "complete_four_domain_pct",
        "selected_endotype_n",
        "n_classes",
        "functional_deterioration_ge_0_5sd_available_n",
        "mortality_followup_available_n",
        "death_n",
    ]
    lines.extend(markdown_table(round_numeric(table1), table1_cols))
    lines.extend(["", "## Draft Table 2: Class Profiles And Labels", ""])
    table2_cols = [
        "cohort",
        "class_id",
        "class_pct",
        "label_en",
        "label_confidence",
        "severity_mean",
        "functional_score",
        "cognitive_score",
        "affective_score",
        "cardiometabolic_chronic_score",
        "functional_or_formatted",
        "mortality_hr_formatted",
        "mortality_drift_flag",
    ]
    lines.extend(markdown_table(round_numeric(table2), table2_cols))
    lines.extend(["", "## Draft Table 3: Outcome Validation Summary", ""])
    table3_cols = [
        "cohort",
        "endpoint",
        "endpoint_role",
        "n_endotype",
        "events_endotype",
        "event_pct",
        "delta_aic_severity_tertile_minus_endotype",
        "endotype_vs_severity_tertile",
        "delta_aic_four_domain_scores_minus_endotype",
        "endotype_vs_four_domain_scores",
        "endotype_plus_four_domain_note",
        "ph_screen_flag",
        "mortality_drift_flagged_classes",
    ]
    lines.extend(markdown_table(round_numeric(table3), table3_cols))
    lines.extend(
        [
            "",
            "## Draft Figure 1",
            "",
            f"- PNG: `{figure_png.as_posix()}`",
            f"- PDF: `{figure_pdf.as_posix()}`",
            "",
            "Figure 1 draft combines:",
            "",
            "- Panel A: endotype domain profiles annotated with functional deterioration and mortality rates.",
            "- Panel B: delta AIC versus severity tertiles.",
            "- Panel C: delta AIC versus four-domain continuous scores.",
            "",
            "## Interpretation Guardrails",
            "",
            "- Positive delta AIC means the endotype-only model improves on the named comparator.",
            "- Negative delta AIC versus four-domain scores means continuous domain scores fit better than endotype-only classes.",
            "- Mortality is retained as a secondary validation endpoint because PH diagnostics and piecewise sensitivity flagged selected cohort-class terms.",
            "- The manuscript should emphasize interpretable multidomain heterogeneity, not universal prediction superiority.",
        ]
    )
    (output_dir / "phase11_manuscript_tables_report.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8-sig",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    table1 = build_table1(args.output_dir)
    table2 = build_table2(args.output_dir)
    table3 = build_table3(args.output_dir)

    save_csv(table1, args.output_dir / "phase11_table1_cohort_readiness.csv")
    save_csv(table2, args.output_dir / "phase11_table2_class_profiles_labels.csv")
    save_csv(table3, args.output_dir / "phase11_table3_outcome_validation_summary.csv")
    figure_png, figure_pdf = build_figure1(args.output_dir)
    write_report(args.output_dir, table1, table2, table3, figure_png, figure_pdf)


if __name__ == "__main__":
    main()
