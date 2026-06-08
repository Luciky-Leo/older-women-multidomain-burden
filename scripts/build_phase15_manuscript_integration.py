from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


REFRESH_DATE = "2026-06-01"

NOVELTY_QUERIES = [
    "PubMed older women multidomain aging endotypes latent class CHARLS HRS ELSA SHARE KLoSA MHAS LASI",
    '"multidomain aging" endotypes older women latent class',
    '"older women" "endotypes" aging latent class cohorts',
    '"CHARLS" "HRS" "ELSA" "SHARE" multidomain aging latent class women',
]

NOVELTY_SOURCES = [
    {
        "source_id": "N1",
        "title": "Interrelated Multidimensional Trajectories of Aging: Evidence From the Health and Retirement Study",
        "url": "https://pubmed.ncbi.nlm.nih.gov/36479143/",
        "relation_to_current_study": "Adjacent HRS multidimensional aging trajectory work",
        "collision_risk": "adjacent_not_direct",
        "positioning_implication": "Avoid claiming novelty for multidimensional trajectories in HRS alone; emphasize women-only, seven-cohort endotype comparison.",
    },
    {
        "source_id": "N2",
        "title": "Sex Differences in Intrinsic Capacity Domains and Their Associations With Adverse Health Outcomes Across Four Aging Cohorts",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC12317657/",
        "relation_to_current_study": "Adjacent sex-stratified intrinsic-capacity analysis across aging cohorts",
        "collision_risk": "moderate_adjacent",
        "positioning_implication": "Do not frame the paper as a generic sex-difference or intrinsic-capacity paper.",
    },
    {
        "source_id": "N3",
        "title": "Trajectories of intrinsic capacity and their associations with adverse outcomes",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC11625515/",
        "relation_to_current_study": "Adjacent multidomain intrinsic-capacity trajectory literature",
        "collision_risk": "moderate_adjacent",
        "positioning_implication": "Keep the contribution on endotype profile structure and cohort-specific validation, not on intrinsic capacity trajectories per se.",
    },
    {
        "source_id": "N4",
        "title": "Symptom clusters, disability and health-related quality of life in community-dwelling older adults",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC12434884/",
        "relation_to_current_study": "Adjacent symptom-cluster work using international aging cohorts",
        "collision_risk": "moderate_adjacent",
        "positioning_implication": "Distinguish multidomain aging endotypes from symptom-cluster-only phenotyping.",
    },
    {
        "source_id": "N5",
        "title": "Trajectories of Depressive Symptoms, Memory Function, and Mobility Before Death",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC11356518/",
        "relation_to_current_study": "Adjacent predeath trajectory work in aging cohorts",
        "collision_risk": "adjacent_not_direct",
        "positioning_implication": "Avoid overclaiming novelty for linked depression, memory, mobility trajectories.",
    },
    {
        "source_id": "N6",
        "title": "Measurement of Healthy Ageing",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC11298082/",
        "relation_to_current_study": "Background measurement framework for healthy aging",
        "collision_risk": "background",
        "positioning_implication": "Use as framework context only; keep the empirical novelty claim narrower.",
    },
    {
        "source_id": "N7",
        "title": "Lifecourse systemic inflammation and healthy ageing: a five-cohort study",
        "url": "https://www.medrxiv.org/content/10.1101/2025.10.22.25338202v1",
        "relation_to_current_study": "Adjacent preprint on healthy-aging outcomes across cohorts",
        "collision_risk": "background_adjacent",
        "positioning_implication": "Do not pivot the main manuscript to inflammaging unless biomarker harmonization is expanded.",
    },
]


def read_csv(output_dir: Path, name: str) -> pd.DataFrame:
    path = output_dir / name
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path, low_memory=False)


def fmt_int(value: object) -> str:
    if pd.isna(value):
        return "0"
    return f"{int(round(float(value))):,}"


def fmt_num(value: object, digits: int = 2) -> str:
    if pd.isna(value):
        return "NA"
    return f"{float(value):.{digits}f}"


def markdown_table(rows: list[dict[str, object]], columns: list[str]) -> str:
    if not rows:
        return "_No rows._"
    header = "| " + " | ".join(columns) + " |"
    divider = "| " + " | ".join(["---"] * len(columns)) + " |"
    body = []
    for row in rows:
        values = [str(row.get(column, "")).replace("\n", " ") for column in columns]
        body.append("| " + " | ".join(values) + " |")
    return "\n".join([header, divider, *body])


def stable_unique(values: pd.Series) -> str:
    clean = [str(value) for value in values.dropna().tolist() if str(value).strip()]
    return "; ".join(sorted(set(clean)))


def change_reason(row: pd.Series) -> str:
    reasons = []
    if int(row.get("direction_change", 0) or 0) == 1:
        reasons.append("direction_change")
    if int(row.get("significance_change", 0) or 0) == 1:
        reasons.append("significance_change")
    if int(row.get("material_log_change", 0) or 0) == 1:
        reasons.append("material_log_change")
    return "+".join(reasons) if reasons else "stability_flag"


def build_stability_flag_summary(stability: pd.DataFrame) -> pd.DataFrame:
    flags = stability[pd.to_numeric(stability["stability_flag"], errors="coerce").fillna(0).eq(1)].copy()
    if flags.empty:
        return pd.DataFrame(
            columns=[
                "cohort",
                "class_id",
                "phase14_stability_flag_count",
                "phase14_flagged_outcomes",
                "phase14_flagged_adjustments",
                "phase14_flag_reasons",
                "phase14_effect_ratio_min",
                "phase14_effect_ratio_max",
            ]
        )
    flags["term_label"] = flags["term_label"].astype(int).astype(str)
    flags["class_id"] = flags["cohort"].astype(str) + "_C" + flags["term_label"]
    flags["flag_reason"] = flags.apply(change_reason, axis=1)
    grouped = (
        flags.groupby(["cohort", "class_id"], as_index=False)
        .agg(
            phase14_stability_flag_count=("stability_flag", "sum"),
            phase14_flagged_outcomes=("outcome", stable_unique),
            phase14_flagged_adjustments=("adjustment", stable_unique),
            phase14_flag_reasons=("flag_reason", stable_unique),
            phase14_effect_ratio_min=("effect_ratio_sensitivity_vs_age", "min"),
            phase14_effect_ratio_max=("effect_ratio_sensitivity_vs_age", "max"),
        )
        .sort_values(["cohort", "class_id"])
    )
    return grouped


def combine_reasons(*parts: object) -> str:
    out: list[str] = []
    for part in parts:
        if pd.isna(part):
            continue
        text = str(part).strip()
        if text and text.lower() != "nan":
            for item in text.split(";"):
                item = item.strip()
                if item and item not in out:
                    out.append(item)
    return "; ".join(out)


def build_label_lock_queue(policy: pd.DataFrame, flag_summary: pd.DataFrame) -> pd.DataFrame:
    queue = policy.merge(flag_summary, on=["cohort", "class_id"], how="left")
    queue["phase14_stability_flag_count"] = (
        pd.to_numeric(queue["phase14_stability_flag_count"], errors="coerce").fillna(0).astype(int)
    )

    actions = []
    statuses = []
    reasons = []
    for _, row in queue.iterrows():
        current = str(row.get("label_action", "")).strip()
        action = current
        reason = row.get("manual_review_reason", "")

        if row["phase14_stability_flag_count"] > 0:
            if current == "lock_candidate":
                action = "manual_review_before_lock"
            elif current == "hold_until_followup_available":
                action = "hold_until_followup_available"
            else:
                action = "manual_review_before_lock"
            reason = combine_reasons(reason, "Phase 14 covariate sensitivity stability flag")

        if row.get("cohort") in {"KLoSA", "SHARE"}:
            reason = combine_reasons(reason, "Bridge-sensitivity cohort display needs explicit footnote")
        if row.get("cohort") == "LASI":
            reason = combine_reasons(reason, "Baseline-profile only until follow-up validation is available")

        if action == "lock_candidate":
            status = "ready_for_manual_lock"
        elif action == "manual_review_before_lock":
            status = "manual_review_required"
        elif action == "hold_until_followup_available":
            status = "hold_baseline_only"
        else:
            status = "manual_review_required"

        actions.append(action)
        statuses.append(status)
        reasons.append(reason)

    queue["phase15_label_action"] = actions
    queue["phase15_lock_status"] = statuses
    queue["phase15_review_reason"] = reasons
    keep = [
        "cohort",
        "class_id",
        "analysis_tier",
        "manuscript_role",
        "display_policy",
        "label_action",
        "phase15_label_action",
        "phase15_lock_status",
        "label_en_current",
        "label_zh_current",
        "label_confidence",
        "manual_review_reason",
        "phase15_review_reason",
        "phase14_stability_flag_count",
        "phase14_flagged_outcomes",
        "phase14_flagged_adjustments",
        "phase14_flag_reasons",
        "phase14_effect_ratio_min",
        "phase14_effect_ratio_max",
    ]
    return queue[[column for column in keep if column in queue.columns]].sort_values(["cohort", "class_id"])


def build_supplement_shell(
    functional: pd.DataFrame,
    mortality: pd.DataFrame,
    stability: pd.DataFrame,
    skipped: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []

    for _, row in functional.iterrows():
        rows.append(
            {
                "table_id": "S1a",
                "table_title": "Functional deterioration covariate-sensitivity model comparison",
                "row_type": "model_comparison",
                "endpoint": row.get("outcome_label", "Functional deterioration >= 0.5 SD"),
                "cohort": row["cohort"],
                "analysis_tier": row["analysis_tier"],
                "class_id": "",
                "adjustment": row["adjustment"],
                "n_endotype": row.get("n_endotype", ""),
                "events_endotype": row.get("events_endotype", ""),
                "comparison_metric": "delta_aic_severity_tertile_minus_endotype",
                "comparison_value": row.get("delta_aic_severity_tertile_minus_endotype", ""),
                "secondary_metric": "delta_auc_endotype_minus_severity",
                "secondary_value": row.get("delta_auc_endotype_minus_severity", ""),
                "interpretation_note": "Positive delta AIC favors the endotype model over the severity-tertile comparator.",
            }
        )

    for _, row in mortality.iterrows():
        rows.append(
            {
                "table_id": "S1b",
                "table_title": "Mortality covariate-sensitivity model comparison",
                "row_type": "model_comparison",
                "endpoint": row.get("outcome_label", "All-cause mortality"),
                "cohort": row["cohort"],
                "analysis_tier": row["analysis_tier"],
                "class_id": "",
                "adjustment": row["adjustment"],
                "n_endotype": row.get("n_endotype", ""),
                "events_endotype": row.get("events_endotype", ""),
                "comparison_metric": "delta_partial_aic_severity_tertile_minus_endotype",
                "comparison_value": row.get("delta_partial_aic_severity_tertile_minus_endotype", ""),
                "secondary_metric": "median_followup_time_years_endotype",
                "secondary_value": row.get("median_followup_time_years_endotype", ""),
                "interpretation_note": "Positive delta partial AIC favors the endotype Cox model over the severity-tertile comparator.",
            }
        )

    flags = stability[pd.to_numeric(stability["stability_flag"], errors="coerce").fillna(0).eq(1)].copy()
    if not flags.empty:
        flags["term_label"] = flags["term_label"].astype(int).astype(str)
        flags["class_id"] = flags["cohort"].astype(str) + "_C" + flags["term_label"]
        flags["flag_reason"] = flags.apply(change_reason, axis=1)
        for _, row in flags.iterrows():
            rows.append(
                {
                    "table_id": "S2",
                    "table_title": "Endotype effect-stability flags under covariate sensitivity",
                    "row_type": "effect_stability_flag",
                    "endpoint": row.get("outcome", ""),
                    "cohort": row["cohort"],
                    "analysis_tier": row["analysis_tier"],
                    "class_id": row["class_id"],
                    "adjustment": row["adjustment"],
                    "n_endotype": "",
                    "events_endotype": "",
                    "comparison_metric": "effect_ratio_sensitivity_vs_age",
                    "comparison_value": row.get("effect_ratio_sensitivity_vs_age", ""),
                    "secondary_metric": "flag_reason",
                    "secondary_value": row["flag_reason"],
                    "interpretation_note": "Requires manual label/outcome interpretation review before final lock.",
                }
            )

    nonfinite = skipped[skipped["skip_reason"].astype(str).str.contains("nonfinite", case=False, na=False)].copy()
    for _, row in nonfinite.iterrows():
        rows.append(
            {
                "table_id": "S3",
                "table_title": "Skipped or non-estimable sensitivity fits",
                "row_type": "skipped_fit",
                "endpoint": row.get("outcome_family", ""),
                "cohort": row.get("cohort", ""),
                "analysis_tier": row.get("analysis_tier", ""),
                "class_id": "",
                "adjustment": row.get("adjustment", ""),
                "n_endotype": row.get("n", ""),
                "events_endotype": row.get("events", ""),
                "comparison_metric": row.get("model_type", ""),
                "comparison_value": "",
                "secondary_metric": "skip_reason",
                "secondary_value": row.get("skip_reason", ""),
                "interpretation_note": "Document in supplement if the corresponding comparator is discussed.",
            }
        )

    return pd.DataFrame(rows)


def build_display_policy(table1: pd.DataFrame, label_queue: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    cohort_order = ["CHARLS", "ELSA", "HRS", "MHAS", "KLoSA", "SHARE", "LASI"]
    queue_counts = (
        label_queue.groupby(["cohort", "phase15_lock_status"]).size().unstack(fill_value=0).reset_index()
        if not label_queue.empty
        else pd.DataFrame()
    )
    for cohort in cohort_order:
        t1 = table1[table1["cohort"] == cohort]
        if t1.empty:
            continue
        row = t1.iloc[0]
        qrow = queue_counts[queue_counts["cohort"] == cohort]
        qdata = qrow.iloc[0].to_dict() if not qrow.empty else {}

        if cohort in {"CHARLS", "ELSA", "HRS", "MHAS"}:
            recommendation = "main_results"
            figure_policy = "main_panel"
            condition = "Use in main Results and main Figure 1 with standard strict-primary denominators."
        elif cohort == "LASI":
            recommendation = "baseline_profile_table_only"
            figure_policy = "table_or_supplement_profile_only"
            condition = "Do not use in outcome-validation panels until follow-up validation is available."
        else:
            recommendation = "sensitivity_or_supplement_default"
            figure_policy = "sensitivity_panel_default"
            condition = "May appear in the main figure only with an explicit bridge-sensitivity or wave-adjusted denominator footnote."

        rows.append(
            {
                "cohort": cohort,
                "analysis_tier": row.get("analysis_tier", ""),
                "manuscript_role": row.get("manuscript_role", ""),
                "baseline_women_age50plus_n": row.get("baseline_women_age50plus_n", ""),
                "selected_endotype_n": row.get("selected_endotype_n", ""),
                "functional_followup_n": row.get("functional_deterioration_ge_0_5sd_available_n", ""),
                "mortality_followup_n": row.get("mortality_followup_available_n", ""),
                "phase15_display_recommendation": recommendation,
                "figure1_policy": figure_policy,
                "condition_for_main_display": condition,
                "ready_for_manual_lock_n": qdata.get("ready_for_manual_lock", 0),
                "manual_review_required_n": qdata.get("manual_review_required", 0),
                "hold_baseline_only_n": qdata.get("hold_baseline_only", 0),
            }
        )
    return pd.DataFrame(rows)


def source_table() -> pd.DataFrame:
    return pd.DataFrame(NOVELTY_SOURCES)


def write_novelty_report(path: Path, sources: pd.DataFrame) -> None:
    rows = sources[
        [
            "source_id",
            "title",
            "collision_risk",
            "relation_to_current_study",
            "url",
        ]
    ].to_dict("records")
    text = [
        "# Phase 15 Novelty Refresh",
        "",
        f"Refresh date: {REFRESH_DATE}.",
        "",
        "## Targeted Queries",
        "",
        *[f"- `{query}`" for query in NOVELTY_QUERIES],
        "",
        "## Direct-Collision Read",
        "",
        (
            "Targeted refresh did not identify a direct same-topic collision for a women-only, "
            "seven-international-cohort, four-domain aging endotype study with functional and "
            "mortality validation."
        ),
        "",
        (
            "The adjacent literature is active. The Introduction and Discussion should therefore avoid "
            "claims that the paper is the first multidimensional aging, intrinsic-capacity, symptom-cluster, "
            "or sex-difference study. The safer claim is that few studies have focused on women-only "
            "multidomain endotypes across harmonized international cohorts while retaining explicit "
            "comparator guardrails."
        ),
        "",
        "## Sources Logged",
        "",
        markdown_table(rows, ["source_id", "title", "collision_risk", "relation_to_current_study", "url"]),
        "",
        "## Positioning Rules",
        "",
        "- Keep the main novelty claim narrow: women-only multidomain endotype structure across seven aging cohorts.",
        "- State that continuous four-domain scores remain stronger prediction variables in the current screens.",
        "- Treat KLoSA and SHARE as bridge-sensitivity cohorts unless the figure footnote makes the denominator difference explicit.",
        "- Keep LASI as baseline-profile-only until longitudinal follow-up files are added.",
    ]
    path.write_text("\n".join(text) + "\n", encoding="utf-8")


def write_supplement_markdown(path: Path, supplement: pd.DataFrame, display: pd.DataFrame) -> None:
    s1 = supplement[supplement["table_id"].isin(["S1a", "S1b"])]
    s2 = supplement[supplement["table_id"].eq("S2")]
    s3 = supplement[supplement["table_id"].eq("S3")]
    text = [
        "# Supplement Table Shell",
        "",
        "## Supplementary Table S1",
        "",
        (
            "Covariate-sensitivity model comparisons for functional deterioration and all-cause mortality. "
            "Positive AIC or partial-AIC deltas favor the endotype model over the severity-tertile comparator."
        ),
        "",
        markdown_table(
            s1.head(12).to_dict("records"),
            [
                "table_id",
                "endpoint",
                "cohort",
                "analysis_tier",
                "adjustment",
                "n_endotype",
                "events_endotype",
                "comparison_metric",
                "comparison_value",
            ],
        ),
        "",
        "## Supplementary Table S2",
        "",
        "Endotype effect-stability flags that should block automatic label locking.",
        "",
        markdown_table(
            s2.to_dict("records"),
            ["endpoint", "cohort", "analysis_tier", "class_id", "adjustment", "comparison_value", "secondary_value"],
        ),
        "",
        "## Supplementary Table S3",
        "",
        "Non-estimable or skipped sensitivity fits that need transparent reporting if the relevant model is discussed.",
        "",
        markdown_table(
            s3.to_dict("records"),
            ["endpoint", "cohort", "analysis_tier", "adjustment", "comparison_metric", "secondary_value"],
        ),
        "",
        "## Display Policy Table",
        "",
        markdown_table(
            display.to_dict("records"),
            [
                "cohort",
                "analysis_tier",
                "phase15_display_recommendation",
                "figure1_policy",
                "manual_review_required_n",
                "hold_baseline_only_n",
            ],
        ),
    ]
    path.write_text("\n".join(text) + "\n", encoding="utf-8")


def write_results_skeleton(
    path: Path,
    base_text: str,
    functional: pd.DataFrame,
    mortality: pd.DataFrame,
    flag_summary: pd.DataFrame,
    label_queue: pd.DataFrame,
    display: pd.DataFrame,
) -> None:
    functional_minimal = functional[functional["adjustment"].eq("minimal_core")]
    mortality_minimal = mortality[mortality["adjustment"].eq("minimal_core")]
    functional_cohorts = ", ".join(sorted(functional_minimal["cohort"].unique()))
    mortality_cohorts = ", ".join(sorted(mortality_minimal["cohort"].unique()))
    flagged_classes = ", ".join(flag_summary["class_id"].tolist()) if not flag_summary.empty else "none"
    label_counts = label_queue["phase15_lock_status"].value_counts().to_dict()
    display_rows = display[["cohort", "phase15_display_recommendation"]].to_dict("records")

    appendix = [
        "",
        "## Phase 15 Integrated Sensitivity Update",
        "",
        "### Covariate Sensitivity",
        "",
        (
            f"Phase 14 added {len(functional)} functional-deterioration and {len(mortality)} mortality "
            "covariate-sensitivity comparison rows. Minimal-core functional sensitivity was estimable in "
            f"{functional_minimal['cohort'].nunique()} cohorts ({functional_cohorts}), and minimal-core "
            f"mortality sensitivity was estimable in {mortality_minimal['cohort'].nunique()} cohorts "
            f"({mortality_cohorts}). LASI remains baseline-profile only in the current cleaned CSV pass."
        ),
        "",
        (
            f"Effect-stability screening flagged {len(flag_summary)} class labels for manual review before "
            f"final lock: {flagged_classes}. These flags should be described as robustness caveats, not as "
            "replacement primary estimates."
        ),
        "",
        "Draft table callout: Supplementary Table S1-S2.",
        "",
        "### Label Lock Queue",
        "",
        (
            "After incorporating Phase 14 stability flags, the Phase 15 label queue contains "
            f"{int(label_counts.get('ready_for_manual_lock', 0))} labels ready for manual lock, "
            f"{int(label_counts.get('manual_review_required', 0))} labels requiring manual review, and "
            f"{int(label_counts.get('hold_baseline_only', 0))} baseline-only hold labels."
        ),
        "",
        "Classes blocked from automatic locking are those with generic severity-aligned labels, mortality time-drift, "
        "Phase 14 covariate-sensitivity instability, bridge-sensitivity display caveats, or missing follow-up validation.",
        "",
        "### Display Policy",
        "",
        markdown_table(display_rows, ["cohort", "phase15_display_recommendation"]),
        "",
        (
            "Default manuscript display should keep CHARLS, ELSA, HRS, and MHAS in the main validation panels. "
            "KLoSA and SHARE should default to sensitivity or supplement display because they use bridge-sensitivity "
            "definitions; they may appear in the main figure only with explicit bridge or wave-adjusted denominator "
            "footnotes. LASI should remain a baseline-profile table row until longitudinal follow-up validation is added."
        ),
        "",
        "### Novelty Refresh",
        "",
        (
            "The 2026-06-01 targeted refresh did not identify a direct same-topic collision for a women-only, "
            "seven-cohort, four-domain endotype study with functional and mortality validation. Adjacent work on "
            "multidimensional aging trajectories, intrinsic capacity, symptom clusters, and predeath trajectories "
            "means the manuscript should keep novelty claims narrow and comparator-aware."
        ),
        "",
        "Draft table callout: Supplementary Table S3 or a short novelty-positioning appendix.",
        "",
        "## Updated Results Paragraph Order",
        "",
        "1. Cohort readiness and selected denominators.",
        "2. Endotype solution sizes and profile diversity.",
        "3. Functional deterioration as the primary validation endpoint.",
        "4. Chronic progression as secondary validation.",
        "5. Mortality as secondary validation with PH, piecewise, and covariate-sensitivity caveats.",
        "6. Comparator guardrail and final interpretation.",
        "7. Novelty-positioning statement for Discussion rather than Results.",
    ]
    path.write_text(base_text.rstrip() + "\n" + "\n".join(appendix) + "\n", encoding="utf-8")


def write_report(
    path: Path,
    functional: pd.DataFrame,
    mortality: pd.DataFrame,
    flag_summary: pd.DataFrame,
    label_queue: pd.DataFrame,
    display: pd.DataFrame,
    sources: pd.DataFrame,
) -> None:
    action_counts = label_queue["phase15_lock_status"].value_counts().to_dict()
    text = [
        "# Phase 15 Manuscript Integration Report",
        "",
        f"Run date: {REFRESH_DATE}.",
        "",
        "## Outputs",
        "",
        "- `outputs/phase15_results_skeleton_integrated.md`",
        "- `manuscript/results_skeleton.md`",
        "- `outputs/phase15_supplement_table_shell.csv`",
        "- `manuscript/supplement_table_shell.md`",
        "- `outputs/phase15_label_lock_queue.csv`",
        "- `outputs/phase15_display_policy_recommendation.csv`",
        "- `outputs/phase15_novelty_refresh_sources.csv`",
        "- `outputs/phase15_novelty_refresh_report.md`",
        "",
        "## Key Results",
        "",
        f"- Functional covariate-sensitivity comparison rows: {len(functional)}.",
        f"- Mortality covariate-sensitivity comparison rows: {len(mortality)}.",
        f"- Phase 14 stability-flagged class labels: {len(flag_summary)}.",
        f"- Label queue status counts: {action_counts}.",
        f"- Novelty refresh sources logged: {len(sources)}.",
        "",
        "## Display Decision",
        "",
        markdown_table(
            display.to_dict("records"),
            [
                "cohort",
                "analysis_tier",
                "phase15_display_recommendation",
                "figure1_policy",
                "condition_for_main_display",
            ],
        ),
    ]
    path.write_text("\n".join(text) + "\n", encoding="utf-8")


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

    table1 = read_csv(output_dir, "phase11_table1_cohort_readiness.csv")
    policy = read_csv(output_dir, "phase13_label_display_policy.csv")
    functional = read_csv(output_dir, "phase14_functional_covariate_model_comparison.csv")
    mortality = read_csv(output_dir, "phase14_mortality_covariate_model_comparison.csv")
    stability = read_csv(output_dir, "phase14_endotype_effect_stability.csv")
    skipped = read_csv(output_dir, "phase14_covariate_model_skipped.csv")

    flag_summary = build_stability_flag_summary(stability)
    label_queue = build_label_lock_queue(policy, flag_summary)
    supplement = build_supplement_shell(functional, mortality, stability, skipped)
    display = build_display_policy(table1, label_queue)
    sources = source_table()

    base_path = output_dir / "phase12_results_skeleton.md"
    base_text = base_path.read_text(encoding="utf-8") if base_path.exists() else ""

    label_queue.to_csv(output_dir / "phase15_label_lock_queue.csv", index=False)
    supplement.to_csv(output_dir / "phase15_supplement_table_shell.csv", index=False)
    display.to_csv(output_dir / "phase15_display_policy_recommendation.csv", index=False)
    sources.to_csv(output_dir / "phase15_novelty_refresh_sources.csv", index=False)

    integrated_path = output_dir / "phase15_results_skeleton_integrated.md"
    write_results_skeleton(integrated_path, base_text, functional, mortality, flag_summary, label_queue, display)
    write_results_skeleton(manuscript_dir / "results_skeleton.md", base_text, functional, mortality, flag_summary, label_queue, display)
    write_supplement_markdown(manuscript_dir / "supplement_table_shell.md", supplement, display)
    write_novelty_report(output_dir / "phase15_novelty_refresh_report.md", sources)
    write_report(
        output_dir / "phase15_manuscript_integration_report.md",
        functional,
        mortality,
        flag_summary,
        label_queue,
        display,
        sources,
    )


if __name__ == "__main__":
    main()
