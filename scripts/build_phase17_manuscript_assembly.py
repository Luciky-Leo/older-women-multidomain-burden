from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


RUN_DATE = "2026-06-01"

MAIN_VALIDATION_COHORTS = ["CHARLS", "ELSA", "HRS", "MHAS"]
COHORT_ORDER = ["CHARLS", "ELSA", "HRS", "MHAS", "KLoSA", "SHARE", "LASI"]


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


def fmt_num(value: object, digits: int = 2) -> str:
    if pd.isna(value):
        return "NA"
    return f"{float(value):.{digits}f}"


def clean_cell(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).replace("\n", " ").replace("|", "/").strip()


def markdown_table(frame: pd.DataFrame, columns: list[str], rename: dict[str, str] | None = None) -> str:
    rename = rename or {}
    if frame.empty:
        return "_No rows._"
    header = [rename.get(column, column) for column in columns]
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for _, row in frame.iterrows():
        lines.append("| " + " | ".join(clean_cell(row.get(column, "")) for column in columns) + " |")
    return "\n".join(lines)


def format_table1(table1: pd.DataFrame) -> pd.DataFrame:
    out = table1.copy()
    for column in [
        "baseline_women_age50plus_n",
        "complete_four_domain_n",
        "selected_endotype_n",
        "functional_deterioration_ge_0_5sd_available_n",
        "functional_deterioration_ge_0_5sd_event_n",
        "mortality_followup_available_n",
        "death_n",
    ]:
        if column in out.columns:
            out[column] = out[column].map(fmt_int)
    for column in [
        "complete_four_domain_pct",
        "functional_deterioration_ge_0_5sd_event_pct",
        "mortality_followup_available_pct",
        "death_pct",
    ]:
        if column in out.columns:
            out[column] = out[column].map(fmt_pct)
    out["cohort_order"] = out["cohort"].map({cohort: i for i, cohort in enumerate(COHORT_ORDER)}).fillna(99)
    return out.sort_values("cohort_order").drop(columns=["cohort_order"])


def format_table2(table2: pd.DataFrame) -> pd.DataFrame:
    out = table2.copy()
    for column in [
        "severity_mean",
        "functional_score",
        "cognitive_score",
        "affective_score",
        "cardiometabolic_chronic_score",
    ]:
        out[column] = out[column].map(lambda value: fmt_num(value, 2))
    out["class_pct"] = out["class_pct"].map(fmt_pct)
    out["cohort_order"] = out["cohort"].map({cohort: i for i, cohort in enumerate(COHORT_ORDER)}).fillna(99)
    return out.sort_values(["cohort_order", "class"]).drop(columns=["cohort_order"])


def format_table3(table3: pd.DataFrame) -> pd.DataFrame:
    out = table3.copy()
    out["n_endotype"] = out["n_endotype"].map(fmt_int)
    out["events_endotype"] = out["events_endotype"].map(fmt_int)
    out["event_pct"] = out["event_pct"].map(fmt_pct)
    for column in [
        "delta_aic_severity_tertile_minus_endotype",
        "delta_aic_four_domain_scores_minus_endotype",
    ]:
        out[column] = out[column].map(lambda value: fmt_num(value, 1))
    out["cohort_order"] = out["cohort"].map({cohort: i for i, cohort in enumerate(COHORT_ORDER)}).fillna(99)
    endpoint_order = {
        "Functional deterioration >= 0.5 SD": 1,
        "Chronic progression >= 1 condition": 2,
        "All-cause mortality": 3,
    }
    out["endpoint_order"] = out["endpoint"].map(endpoint_order).fillna(99)
    return out.sort_values(["cohort_order", "endpoint_order"]).drop(columns=["cohort_order", "endpoint_order"])


def conservative_label_suggestion(row: pd.Series) -> str:
    label = str(row.get("label_en_final", ""))
    reason = str(row.get("phase15_review_reason", ""))
    if row.get("phase16_label_status") == "baseline_only_hold":
        return f"{label} [baseline-profile only]"
    if "generic severity-aligned" in reason:
        if "intermediate" in label:
            return "broad intermediate-burden profile"
        if "elevated" in label:
            return "broad elevated-burden profile"
        return "broad burden-profile label"
    if "mortality HR drift" in reason and "Phase 14" in reason:
        return f"{label} [domain-profile label; avoid mortality-driven interpretation]"
    if "Phase 14" in reason:
        return f"{label} [requires sensitivity caveat]"
    if "bridge" in reason.lower():
        return f"{label} [bridge-sensitivity label]"
    return label


def review_question(row: pd.Series) -> str:
    status = row.get("phase16_label_status")
    reason = str(row.get("phase15_review_reason", ""))
    if status == "baseline_only_hold":
        return "Should this baseline-only label be shown only in descriptive tables until LASI follow-up is added?"
    if "generic severity-aligned" in reason:
        return "Is a domain-neutral burden label preferable to a generic severity-aligned name?"
    if "mortality HR drift" in reason:
        return "Should the final label avoid mortality language and rely only on the baseline domain profile?"
    if "Phase 14" in reason:
        return "Does covariate sensitivity change the clinical interpretation enough to rename the class?"
    if "bridge" in reason.lower():
        return "Should this bridge-sensitivity class stay out of main-panel final labeling?"
    return "Confirm whether the draft label is clinically interpretable and non-overclaiming."


def build_label_review_packet(dictionary: pd.DataFrame, table2: pd.DataFrame) -> pd.DataFrame:
    evidence_cols = [
        "cohort",
        "class_id",
        "class_n",
        "class_pct",
        "severity_mean",
        "functional_score",
        "cognitive_score",
        "affective_score",
        "cardiometabolic_chronic_score",
        "functional_or_formatted",
        "mortality_hr_formatted",
        "mortality_drift_flag",
    ]
    evidence = table2[[column for column in evidence_cols if column in table2.columns]].copy()
    packet = dictionary.merge(evidence, on=["cohort", "class_id"], how="left")
    packet = packet[packet["phase16_label_status"].ne("locked_for_draft")].copy()
    packet["suggested_conservative_label"] = packet.apply(conservative_label_suggestion, axis=1)
    packet["human_review_question"] = packet.apply(review_question, axis=1)
    packet["recommended_phase17_action"] = packet["phase16_label_status"].map(
        {
            "review_required_not_locked": "manual_review_before_final_tables",
            "baseline_only_hold": "hold_outcome_validated_label",
        }
    )
    keep = [
        "cohort",
        "class_id",
        "phase16_label_status",
        "label_en_final",
        "suggested_conservative_label",
        "phase15_review_reason",
        "human_review_question",
        "recommended_phase17_action",
        "class_n",
        "class_pct",
        "severity_mean",
        "functional_score",
        "cognitive_score",
        "affective_score",
        "cardiometabolic_chronic_score",
        "functional_or_formatted",
        "mortality_hr_formatted",
        "mortality_drift_flag",
        "phase14_stability_flag_count",
        "phase14_flag_reasons",
    ]
    return packet[[column for column in keep if column in packet.columns]]


def table_md_outputs(
    output_dir: Path,
    manuscript_dir: Path,
    table1: pd.DataFrame,
    table2: pd.DataFrame,
    table3: pd.DataFrame,
) -> None:
    t1 = format_table1(table1)
    t2 = format_table2(table2)
    t3 = format_table3(table3)

    t1_cols = [
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
    ]
    t2_cols = [
        "cohort",
        "class_id",
        "class_n",
        "class_pct",
        "label_en_display",
        "phase16_label_status",
        "functional_score",
        "cognitive_score",
        "affective_score",
        "cardiometabolic_chronic_score",
        "functional_or_formatted",
        "mortality_hr_formatted",
    ]
    t3_cols = [
        "cohort",
        "endpoint",
        "n_endotype",
        "events_endotype",
        "event_pct",
        "delta_aic_severity_tertile_minus_endotype",
        "endotype_vs_severity_tertile",
        "delta_aic_four_domain_scores_minus_endotype",
        "endotype_vs_four_domain_scores",
        "validation_note",
    ]

    text = [
        "# Manuscript Tables 1-3 Draft",
        "",
        "Labels marked `[review]` or `[baseline-only]` are not final clinical labels.",
        "",
        "## Table 1. Cohort readiness and analytic denominators",
        "",
        markdown_table(t1, [column for column in t1_cols if column in t1.columns]),
        "",
        "## Table 2. Cohort-specific endotype profiles and draft labels",
        "",
        markdown_table(t2, [column for column in t2_cols if column in t2.columns]),
        "",
        "## Table 3. Outcome validation and comparator guardrails",
        "",
        markdown_table(t3, [column for column in t3_cols if column in t3.columns]),
    ]
    for path in [output_dir / "phase17_tables_1_3_manuscript.md", manuscript_dir / "tables_1_3_draft.md"]:
        path.write_text("\n".join(text) + "\n", encoding="utf-8")


def supplement_md_outputs(output_dir: Path, manuscript_dir: Path, supplement: pd.DataFrame) -> None:
    s1 = supplement[supplement["table_id"].isin(["S1a", "S1b"])].copy()
    s2 = supplement[supplement["table_id"].eq("S2")].copy()
    s3 = supplement[supplement["table_id"].eq("S3")].copy()
    for frame in [s1, s2, s3]:
        for column in ["comparison_value", "secondary_value"]:
            if column in frame.columns:
                frame[column] = frame[column].map(lambda value: fmt_num(value, 3) if pd.notna(pd.to_numeric(value, errors="coerce")) else clean_cell(value))

    text = [
        "# Supplementary Tables S1-S3 Draft",
        "",
        "## Supplementary Table S1. Covariate-sensitivity model comparisons",
        "",
        markdown_table(
            s1,
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
                "secondary_metric",
                "secondary_value",
            ],
        ),
        "",
        "## Supplementary Table S2. Effect-stability flags",
        "",
        markdown_table(
            s2,
            [
                "endpoint",
                "cohort",
                "analysis_tier",
                "class_id",
                "adjustment",
                "comparison_metric",
                "comparison_value",
                "secondary_value",
                "interpretation_note",
            ],
        ),
        "",
        "## Supplementary Table S3. Non-estimable or skipped sensitivity fits",
        "",
        markdown_table(
            s3,
            [
                "endpoint",
                "cohort",
                "analysis_tier",
                "adjustment",
                "comparison_metric",
                "secondary_metric",
                "secondary_value",
                "interpretation_note",
            ],
        ),
    ]
    for path in [output_dir / "phase17_supplement_s1_s3.md", manuscript_dir / "supplement_s1_s3_draft.md"]:
        path.write_text("\n".join(text) + "\n", encoding="utf-8")


def source_link_list(sources: pd.DataFrame) -> str:
    lines = []
    for _, row in sources.iterrows():
        lines.append(f"- [{row['source_id']}] {row['title']}. {row['url']}")
    return "\n".join(lines)


def endpoint_counts(table3: pd.DataFrame, endpoint: str) -> tuple[int, int, int]:
    subset = table3[table3["endpoint"].eq(endpoint)]
    return subset["cohort"].nunique(), int(subset["n_endotype"].fillna(0).sum()), int(subset["events_endotype"].fillna(0).sum())


def intro_discussion_outputs(
    output_dir: Path,
    manuscript_dir: Path,
    table1: pd.DataFrame,
    table2: pd.DataFrame,
    table3: pd.DataFrame,
    dictionary: pd.DataFrame,
    sources: pd.DataFrame,
) -> None:
    baseline_total = int(table1["baseline_women_age50plus_n"].fillna(0).sum())
    selected_total = int(table1["selected_endotype_n"].fillna(0).sum())
    strict_total = int(table1.loc[table1["analysis_tier"].eq("strict_primary"), "selected_endotype_n"].fillna(0).sum())
    bridge_total = int(table1.loc[table1["analysis_tier"].eq("bridge_sensitivity"), "selected_endotype_n"].fillna(0).sum())
    functional_cohorts, functional_n, functional_events = endpoint_counts(table3, "Functional deterioration >= 0.5 SD")
    mortality_cohorts, mortality_n, mortality_events = endpoint_counts(table3, "All-cause mortality")
    label_counts = dictionary["phase16_label_status"].value_counts().to_dict()

    introduction = [
        "# Introduction Draft",
        "",
        (
            "Population aging is commonly summarized using frailty indices, intrinsic-capacity measures, or "
            "single-domain functional transitions. These approaches are useful, but they can compress heterogeneous "
            "aging processes into a single severity scale. For older women, this is a particular limitation because "
            "functional, cognitive, affective, and cardiometabolic burdens may combine in clinically different ways "
            "even when overall burden appears similar."
        ),
        "",
        (
            "Recent work has examined multidimensional aging trajectories, intrinsic capacity, symptom clusters, "
            "and predeath changes in function, memory, and mood [N1-N6]. This literature makes the broad space "
            "crowded, so the present manuscript should not be framed as the first study of multidimensional aging "
            "or as a new frailty index. The more defensible gap is narrower: few studies have focused on women-only "
            "multidomain aging endotypes across harmonized international aging cohorts while carrying explicit "
            "comparator and sensitivity guardrails."
        ),
        "",
        (
            "We therefore used cleaned data from seven international aging cohorts to construct cohort-specific "
            "women-only multidomain profiles spanning functional, cognitive, affective, and cardiometabolic/chronic "
            "disease domains. We evaluated whether these profiles were clinically interpretable, whether they were "
            "associated with functional deterioration and all-cause mortality, and whether their evidence remained "
            "robust when compared with simpler severity tertiles and continuous four-domain score models."
        ),
        "",
        "## Sources for background positioning",
        "",
        source_link_list(sources),
    ]

    discussion = [
        "# Discussion Draft",
        "",
        "## Principal Findings",
        "",
        (
            f"In this women-only analysis of seven cleaned aging cohorts, the eligible baseline screen included "
            f"{fmt_int(baseline_total)} women aged 50 years or older. Cohort-specific endotype modeling yielded "
            f"{fmt_int(selected_total)} selected assignments overall, including {fmt_int(strict_total)} strict-primary "
            f"assignments and {fmt_int(bridge_total)} bridge-sensitivity assignments."
        ),
        "",
        (
            f"The selected models produced {len(table2)} cohort-specific classes. Phase 16 marked "
            f"{int(label_counts.get('locked_for_draft', 0))} labels as locked for draft use, "
            f"{int(label_counts.get('review_required_not_locked', 0))} as requiring manual review, and "
            f"{int(label_counts.get('baseline_only_hold', 0))} LASI labels as baseline-only holds. This label status "
            "is important: review-required labels should remain visibly marked until clinical review is complete."
        ),
        "",
        (
            f"Functional deterioration validation was available in {functional_cohorts} cohorts, with "
            f"{fmt_int(functional_n)} participants and {fmt_int(functional_events)} events. Mortality validation was "
            f"available in {mortality_cohorts} cohorts, with {fmt_int(mortality_n)} participants and "
            f"{fmt_int(mortality_events)} deaths."
        ),
        "",
        "## Interpretation",
        "",
        (
            "The endotype profiles show multidomain heterogeneity that is not fully captured by a single severity "
            "gradient. Some classes were dominated by functional burden, others by cardiometabolic/chronic disease "
            "burden, affective symptoms, or relative sparing of specific domains. This supports the manuscript's "
            "core descriptive claim: among older women, clinically interpretable multidomain aging patterns can be "
            "constructed across several cohort systems."
        ),
        "",
        (
            "The prediction claim should be more restrained. Across the tested endpoint-cohort rows, continuous "
            "four-domain score models generally outperformed endotype-only models. The manuscript should therefore "
            "state that endotypes improve interpretability and profile-level summarization, not that class membership "
            "is a universally superior standalone predictor."
        ),
        "",
        "## Relation to Existing Work",
        "",
        (
            "The findings are adjacent to prior studies of multidimensional aging trajectories, intrinsic capacity, "
            "symptom clusters, and predeath trajectories [N1-N6]. The distinction is not that multidomain aging has "
            "been ignored, but that this analysis uses a women-focused endotype framing across seven international "
            "aging cohorts and explicitly benchmarks the classes against severity tertiles and four-domain continuous "
            "scores."
        ),
        "",
        "## Strengths",
        "",
        (
            "Strengths include the women-only analytic frame, harmonized four-domain construction, cohort-specific "
            "profile modeling rather than forced pooling, functional and mortality validation, proportional-hazards "
            "and piecewise mortality sensitivity checks, covariate-sensitivity screens, and explicit display rules "
            "for bridge-sensitivity and baseline-only cohorts."
        ),
        "",
        "## Limitations",
        "",
        (
            "Limitations include reliance on cleaned CSV variables rather than a full raw-file harmonization pass, "
            "cohort differences in domain measurement, bridge definitions for KLoSA and SHARE, missing LASI follow-up "
            "validation in the current pass, incomplete expanded-core covariate coverage in several cohorts, and "
            "mortality proportional-hazards/time-drift concerns for selected class terms."
        ),
        "",
        "## Implications",
        "",
        (
            "The most defensible next step is not to overstate prediction superiority, but to refine the clinical "
            "naming and cross-cohort alignment of the profiles. If manual label review confirms the current domain "
            "interpretations, the study can support a manuscript centered on women-specific multidomain aging "
            "heterogeneity and endpoint-specific validation."
        ),
    ]

    intro_path = manuscript_dir / "introduction_draft.md"
    discussion_path = manuscript_dir / "discussion_draft.md"
    combined_path = output_dir / "phase17_intro_discussion_draft.md"
    intro_path.write_text("\n".join(introduction) + "\n", encoding="utf-8")
    discussion_path.write_text("\n".join(discussion) + "\n", encoding="utf-8")
    combined_path.write_text("\n\n".join(["\n".join(introduction), "\n".join(discussion)]) + "\n", encoding="utf-8")


def claim_map_outputs(output_dir: Path, table3: pd.DataFrame, dictionary: pd.DataFrame) -> pd.DataFrame:
    label_counts = dictionary["phase16_label_status"].value_counts().to_dict()
    claims = [
        {
            "claim_id": "P17-C1",
            "claim": "Women-only multidomain endotype profiles are available across seven cleaned aging cohorts.",
            "evidence_assets": "phase11_table1_cohort_readiness.csv; phase16_table2_locked_labels.csv",
            "allowed_strength": "descriptive",
            "required_caveat": "KLoSA and SHARE are bridge-sensitivity cohorts; LASI is baseline-profile only.",
        },
        {
            "claim_id": "P17-C2",
            "claim": f"{int(label_counts.get('locked_for_draft', 0))} labels are draft-locked, but {int(label_counts.get('review_required_not_locked', 0))} still need review.",
            "evidence_assets": "phase16_locked_label_dictionary.csv; phase17_label_review_packet.csv",
            "allowed_strength": "process_guardrail",
            "required_caveat": "Do not treat review-required labels as final clinical labels.",
        },
        {
            "claim_id": "P17-C3",
            "claim": "Functional deterioration is the primary validation endpoint in the current manuscript draft.",
            "evidence_assets": "phase11_table3_outcome_validation_summary.csv; phase16_results_draft.md",
            "allowed_strength": "primary_validation",
            "required_caveat": "Comparator results are endpoint- and cohort-specific.",
        },
        {
            "claim_id": "P17-C4",
            "claim": "Mortality is secondary validation.",
            "evidence_assets": "phase8_mortality_ph_diagnostics.csv; phase9_mortality_piecewise_stability.csv; phase14_endotype_effect_stability.csv",
            "allowed_strength": "secondary_validation",
            "required_caveat": "PH, piecewise, and covariate-sensitivity flags require caveated interpretation.",
        },
        {
            "claim_id": "P17-C5",
            "claim": "Endotypes should be framed as interpretable heterogeneity summaries, not universally superior prediction models.",
            "evidence_assets": "phase11_table3_outcome_validation_summary.csv",
            "allowed_strength": "main_guardrail",
            "required_caveat": "Four-domain continuous-score models generally outperform endotype-only models.",
        },
    ]
    out = pd.DataFrame(claims)
    out.to_csv(output_dir / "phase17_claim_to_evidence_map.csv", index=False)
    return out


def assembly_output(output_dir: Path, manuscript_dir: Path, claims: pd.DataFrame) -> None:
    intro = (manuscript_dir / "introduction_draft.md").read_text(encoding="utf-8")
    results = (manuscript_dir / "results_draft.md").read_text(encoding="utf-8")
    discussion = (manuscript_dir / "discussion_draft.md").read_text(encoding="utf-8")
    tables = (manuscript_dir / "tables_1_3_draft.md").read_text(encoding="utf-8")
    supplement = (manuscript_dir / "supplement_s1_s3_draft.md").read_text(encoding="utf-8")

    text = [
        "# Manuscript Assembly Draft",
        "",
        "Working title: Multidomain aging endotypes among older women across seven international aging cohorts.",
        "",
        "Draft status: Phase 17 assembly. Labels marked `[review]`, `*`, or `[baseline-only]` are not final clinical labels.",
        "",
        intro,
        results,
        discussion,
        "# Tables",
        "",
        tables,
        "",
        "# Supplement",
        "",
        supplement,
        "",
        "# Claim Guardrails",
        "",
        markdown_table(claims, ["claim_id", "claim", "allowed_strength", "required_caveat", "evidence_assets"]),
    ]
    for path in [output_dir / "phase17_manuscript_assembly_draft.md", manuscript_dir / "manuscript_assembly_draft.md"]:
        path.write_text("\n".join(text) + "\n", encoding="utf-8")


def write_report(
    output_dir: Path,
    packet: pd.DataFrame,
    claims: pd.DataFrame,
    sources: pd.DataFrame,
) -> None:
    review_counts = packet["phase16_label_status"].value_counts().to_dict()
    text = [
        "# Phase 17 Manuscript Assembly Report",
        "",
        f"Run date: {RUN_DATE}.",
        "",
        "## Outputs",
        "",
        "- `outputs/phase17_label_review_packet.csv`",
        "- `outputs/phase17_tables_1_3_manuscript.md`",
        "- `outputs/phase17_supplement_s1_s3.md`",
        "- `outputs/phase17_intro_discussion_draft.md`",
        "- `outputs/phase17_claim_to_evidence_map.csv`",
        "- `outputs/phase17_manuscript_assembly_draft.md`",
        "- `manuscript/introduction_draft.md`",
        "- `manuscript/discussion_draft.md`",
        "- `manuscript/tables_1_3_draft.md`",
        "- `manuscript/supplement_s1_s3_draft.md`",
        "- `manuscript/manuscript_assembly_draft.md`",
        "",
        "## Label Review Queue",
        "",
        f"- Review-required/not locked labels: {int(review_counts.get('review_required_not_locked', 0))}.",
        f"- Baseline-only hold labels: {int(review_counts.get('baseline_only_hold', 0))}.",
        "",
        "## Claim Guardrails",
        "",
        markdown_table(claims, ["claim_id", "allowed_strength", "required_caveat"]),
        "",
        "## Novelty Sources Reused",
        "",
        markdown_table(sources, ["source_id", "title", "collision_risk", "url"]),
    ]
    (output_dir / "phase17_manuscript_assembly_report.md").write_text("\n".join(text) + "\n", encoding="utf-8")


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
    table2 = read_csv(output_dir, "phase16_table2_locked_labels.csv")
    table3 = read_csv(output_dir, "phase11_table3_outcome_validation_summary.csv")
    dictionary = read_csv(output_dir, "phase16_locked_label_dictionary.csv")
    supplement = read_csv(output_dir, "phase15_supplement_table_shell.csv")
    sources = read_csv(output_dir, "phase15_novelty_refresh_sources.csv")

    packet = build_label_review_packet(dictionary, table2)
    packet.to_csv(output_dir / "phase17_label_review_packet.csv", index=False)

    table_md_outputs(output_dir, manuscript_dir, table1, table2, table3)
    supplement_md_outputs(output_dir, manuscript_dir, supplement)
    intro_discussion_outputs(output_dir, manuscript_dir, table1, table2, table3, dictionary, sources)
    claims = claim_map_outputs(output_dir, table3, dictionary)
    assembly_output(output_dir, manuscript_dir, claims)
    write_report(output_dir, packet, claims, sources)


if __name__ == "__main__":
    main()
