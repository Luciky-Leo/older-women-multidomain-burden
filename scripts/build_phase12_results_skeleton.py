from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


ENDPOINT_ORDER = {
    "Functional deterioration >= 0.5 SD": 1,
    "Chronic progression >= 1 condition": 2,
    "All-cause mortality": 3,
}


def read_csv(output_dir: Path, name: str) -> pd.DataFrame:
    return pd.read_csv(output_dir / name, low_memory=False)


def fmt_int(value: float | int | None) -> str:
    if pd.isna(value):
        return "0"
    return f"{int(round(float(value))):,}"


def fmt_pct(value: float | int | None) -> str:
    if pd.isna(value):
        return "NA"
    return f"{float(value):.1f}%"


def fmt_num(value: float | int | None, digits: int = 1) -> str:
    if pd.isna(value):
        return "NA"
    return f"{float(value):.{digits}f}"


def build_label_dictionary(table2: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in table2.iterrows():
        reasons = []
        if row.get("label_confidence") == "provisional":
            reasons.append("mortality HR drift")
        if row.get("label_confidence") == "low":
            reasons.append("generic severity-aligned label")
        if row.get("cohort") == "LASI":
            reasons.append("baseline profile only in current CSV pass")
        if row.get("analysis_tier") == "bridge_sensitivity":
            reasons.append("bridge sensitivity cohort")

        if row.get("label_confidence") == "provisional":
            status = "requires_manual_review"
        elif row.get("label_confidence") == "low":
            status = "review_generic_label"
        elif row.get("cohort") == "LASI":
            status = "baseline_only_candidate"
        else:
            status = "ready_for_manual_lock"

        rows.append(
            {
                "analysis_set": row["analysis_set"],
                "analysis_tier": row["analysis_tier"],
                "cohort": row["cohort"],
                "class_id": row["class_id"],
                "class": row["class"],
                "class_pct": row["class_pct"],
                "label_en_current": row["label_en"],
                "label_zh_current": row.get("label_zh", ""),
                "label_confidence": row["label_confidence"],
                "suggested_label_status": status,
                "manual_review_reason": "; ".join(reasons),
                "profile_label": row.get("profile_label", ""),
                "severity_mean": row.get("severity_mean", pd.NA),
                "functional_score": row.get("functional_score", pd.NA),
                "cognitive_score": row.get("cognitive_score", pd.NA),
                "affective_score": row.get("affective_score", pd.NA),
                "cardiometabolic_chronic_score": row.get("cardiometabolic_chronic_score", pd.NA),
                "functional_or_formatted": row.get("functional_or_formatted", ""),
                "mortality_hr_formatted": row.get("mortality_hr_formatted", ""),
                "mortality_drift_flag": row.get("mortality_drift_flag", 0),
            }
        )
    return pd.DataFrame(rows)


def summarize_table1(table1: pd.DataFrame) -> dict[str, object]:
    strict = table1[table1["analysis_tier"] == "strict_primary"].copy()
    bridge = table1[table1["analysis_tier"] == "bridge_sensitivity"].copy()
    validation_ready = table1[
        (table1["functional_deterioration_ge_0_5sd_available_n"].fillna(0) > 0)
        | (table1["mortality_followup_available_n"].fillna(0) > 0)
    ].copy()

    return {
        "phase1_baseline_total": table1["baseline_women_age50plus_n"].sum(),
        "strict_primary_cohorts": strict["cohort"].nunique(),
        "strict_primary_endotype_n": strict["selected_endotype_n"].sum(),
        "bridge_cohorts": bridge["cohort"].nunique(),
        "bridge_endotype_n": bridge["selected_endotype_n"].sum(),
        "all_selected_endotype_n": table1["selected_endotype_n"].sum(),
        "functional_validation_cohorts": table1[
            table1["functional_deterioration_ge_0_5sd_available_n"].fillna(0) > 0
        ]["cohort"].nunique(),
        "mortality_validation_cohorts": table1[
            table1["mortality_followup_available_n"].fillna(0) > 0
        ]["cohort"].nunique(),
        "validation_ready_cohorts": validation_ready["cohort"].nunique(),
        "total_functional_events": table1["functional_deterioration_ge_0_5sd_event_n"].fillna(0).sum(),
        "total_deaths": table1["death_n"].fillna(0).sum(),
        "baseline_only_cohorts": "; ".join(
            table1.loc[table1["manuscript_role"] == "baseline_profile_only_current_csv", "cohort"]
        ),
    }


def summarize_labels(table2: pd.DataFrame) -> dict[str, object]:
    counts_by_confidence = table2["label_confidence"].value_counts().to_dict()
    classes_by_cohort = (
        table2.groupby("cohort")["class_id"]
        .count()
        .reset_index(name="n_classes")
        .to_dict("records")
    )
    provisional = table2.loc[table2["label_confidence"] == "provisional", "class_id"].tolist()
    high_confidence = table2.loc[table2["label_confidence"] == "high", "class_id"].tolist()
    return {
        "total_classes": len(table2),
        "counts_by_confidence": counts_by_confidence,
        "classes_by_cohort": classes_by_cohort,
        "provisional_classes": provisional,
        "high_confidence_classes": high_confidence,
    }


def endpoint_summary(table3: pd.DataFrame, endpoint: str) -> dict[str, object]:
    subset = table3[table3["endpoint"] == endpoint].copy()
    if subset.empty:
        return {
            "endpoint": endpoint,
            "n_cohorts": 0,
            "n_participants": 0,
            "n_events": 0,
            "endotype_vs_severity": {},
            "endotype_vs_four_domain_scores": {},
            "endotype_plus_four_domain_note": {},
            "ph_flags": 0,
            "drift_classes": [],
        }
    return {
        "endpoint": endpoint,
        "n_cohorts": subset["cohort"].nunique(),
        "n_participants": subset["n_endotype"].sum(),
        "n_events": subset["events_endotype"].sum(),
        "endotype_vs_severity": subset["endotype_vs_severity_tertile"].value_counts().to_dict(),
        "endotype_vs_four_domain_scores": subset["endotype_vs_four_domain_scores"].value_counts().to_dict(),
        "endotype_plus_four_domain_note": subset["endotype_plus_four_domain_note"].value_counts().to_dict(),
        "ph_flags": int(pd.to_numeric(subset.get("ph_screen_flag", 0), errors="coerce").fillna(0).sum()),
        "drift_classes": sorted(
            {
                item
                for value in subset["mortality_drift_flagged_classes"].fillna("")
                for item in str(value).split(";")
                if item
            }
        ),
    }


def build_claims(
    sample: dict[str, object],
    labels: dict[str, object],
    endpoint_summaries: dict[str, dict[str, object]],
) -> pd.DataFrame:
    functional = endpoint_summaries["Functional deterioration >= 0.5 SD"]
    chronic = endpoint_summaries["Chronic progression >= 1 condition"]
    mortality = endpoint_summaries["All-cause mortality"]

    claims = [
        {
            "claim_id": "C1",
            "manuscript_section": "Sample and readiness",
            "claim": (
                f"The current analysis identifies endotype profiles in {sample['strict_primary_cohorts']} "
                f"strict-primary cohorts plus {sample['bridge_cohorts']} bridge-sensitivity cohorts."
            ),
            "supporting_assets": "Table 1",
            "caveat": (
                "SHARE uses a wave-adjusted sensitivity denominator; LASI is baseline-profile only for follow-up validation."
            ),
        },
        {
            "claim_id": "C2",
            "manuscript_section": "Endotype structure",
            "claim": (
                f"Selected models produced {labels['total_classes']} cohort-specific classes, with "
                f"{len(labels['high_confidence_classes'])} high-confidence domain-dominant labels and "
                f"{len(labels['provisional_classes'])} provisional labels."
            ),
            "supporting_assets": "Table 2; Figure 1A",
            "caveat": "Provisional labels require manual clinical review before final tables.",
        },
        {
            "claim_id": "C3",
            "manuscript_section": "Functional validation",
            "claim": (
                f"Functional deterioration validation included {functional['n_cohorts']} cohorts, "
                f"{fmt_int(functional['n_participants'])} participants, and {fmt_int(functional['n_events'])} events."
            ),
            "supporting_assets": "Table 3; Figure 1B-C",
            "caveat": "Endotype-only models did not uniformly outperform severity tertiles across cohorts.",
        },
        {
            "claim_id": "C4",
            "manuscript_section": "Secondary outcomes",
            "claim": (
                f"Chronic progression validation included {chronic['n_cohorts']} cohorts and "
                f"{fmt_int(chronic['n_events'])} events."
            ),
            "supporting_assets": "Table 3; Figure 1B-C",
            "caveat": "Chronic progression is useful as secondary validation because definitions remain broad across cohorts.",
        },
        {
            "claim_id": "C5",
            "manuscript_section": "Mortality",
            "claim": (
                f"Mortality validation included {mortality['n_cohorts']} cohorts and "
                f"{fmt_int(mortality['n_events'])} deaths."
            ),
            "supporting_assets": "Table 3; Phase 8-9 diagnostics",
            "caveat": "Mortality should be reported as secondary because PH diagnostics and piecewise sensitivity flagged selected terms.",
        },
        {
            "claim_id": "C6",
            "manuscript_section": "Comparator guardrail",
            "claim": "Four-domain continuous-score models outperformed endotype-only models for every tested endpoint-cohort row.",
            "supporting_assets": "Table 3; Figure 1C",
            "caveat": "Frame the study as clinically interpretable heterogeneity mapping, not universal prediction superiority.",
        },
    ]
    return pd.DataFrame(claims)


def dict_counts_text(counts: dict[str, int]) -> str:
    if not counts:
        return "no rows"
    return ", ".join(f"{key}: {value}" for key, value in sorted(counts.items()))


def write_results_skeleton(
    path: Path,
    sample: dict[str, object],
    labels: dict[str, object],
    endpoint_summaries: dict[str, dict[str, object]],
) -> None:
    functional = endpoint_summaries["Functional deterioration >= 0.5 SD"]
    chronic = endpoint_summaries["Chronic progression >= 1 condition"]
    mortality = endpoint_summaries["All-cause mortality"]

    provisional = ", ".join(labels["provisional_classes"]) or "none"
    confidence_text = dict_counts_text(labels["counts_by_confidence"])
    functional_severity = dict_counts_text(functional["endotype_vs_severity"])
    chronic_severity = dict_counts_text(chronic["endotype_vs_severity"])
    mortality_severity = dict_counts_text(mortality["endotype_vs_severity"])
    four_domain_all = dict_counts_text(functional["endotype_vs_four_domain_scores"])

    lines = [
        "# Results Skeleton",
        "",
        "This is a manuscript-facing draft. It is intentionally conservative and should be edited after manual label review.",
        "",
        "## Study Sample And Cohort Readiness",
        "",
        (
            f"Across the seven cleaned aging cohorts, the Phase 1 earliest-baseline screen identified "
            f"{fmt_int(sample['phase1_baseline_total'])} women aged 50 years or older. The strict-primary "
            f"analysis included {sample['strict_primary_cohorts']} cohorts and {fmt_int(sample['strict_primary_endotype_n'])} "
            "participants with complete four-domain endotype inputs. Two additional bridge-sensitivity cohorts "
            f"contributed {fmt_int(sample['bridge_endotype_n'])} selected endotype assignments, giving "
            f"{fmt_int(sample['all_selected_endotype_n'])} selected assignments across strict and sensitivity analyses."
        ),
        "",
        (
            f"Functional deterioration validation was available in {sample['functional_validation_cohorts']} cohorts, "
            f"and mortality validation was available in {sample['mortality_validation_cohorts']} cohorts. "
            f"{sample['baseline_only_cohorts']} remained baseline-profile only in the current cleaned CSV pass."
        ),
        "",
        "Draft table callout: Table 1.",
        "",
        "## Cohort-Specific Endotype Structure",
        "",
        (
            f"The selected cohort-specific solutions yielded {labels['total_classes']} classes. Label confidence distribution was "
            f"{confidence_text}. Provisional labels were assigned to {provisional}, primarily because mortality HRs varied across "
            "early and late follow-up periods."
        ),
        "",
        (
            "The dominant patterns were not restricted to a single low-to-high severity gradient. Several classes showed "
            "domain-specific elevations, including cardiometabolic-dominant, functional-dominant, affective-dominant, "
            "and spared-cardiometabolic profiles. These labels should be finalized by manual review before being used "
            "as definitive clinical names."
        ),
        "",
        "Draft table/figure callout: Table 2 and Figure 1A.",
        "",
        "## Functional Deterioration",
        "",
        (
            f"Functional deterioration models included {functional['n_cohorts']} cohorts, "
            f"{fmt_int(functional['n_participants'])} participants, and {fmt_int(functional['n_events'])} events. "
            f"Against severity tertiles, the endotype model comparison pattern was {functional_severity}."
        ),
        "",
        (
            "However, four-domain continuous-score models fit better than endotype-only models in all functional "
            "deterioration comparisons, indicating that class membership should not be presented as a universally "
            "superior standalone prediction model."
        ),
        "",
        "Draft table/figure callout: Table 3 and Figure 1B-C.",
        "",
        "## Chronic Progression",
        "",
        (
            f"Chronic progression models included {chronic['n_cohorts']} cohorts, "
            f"{fmt_int(chronic['n_participants'])} participants, and {fmt_int(chronic['n_events'])} events. "
            f"Against severity tertiles, the comparison pattern was {chronic_severity}."
        ),
        "",
        (
            "As with functional deterioration, the four-domain continuous-score comparator outperformed the endotype-only "
            "model across chronic progression comparisons. Chronic progression is therefore best used as secondary evidence "
            "that the identified profiles carry clinically interpretable risk differences."
        ),
        "",
        "## Mortality",
        "",
        (
            f"Mortality models included {mortality['n_cohorts']} cohorts, "
            f"{fmt_int(mortality['n_participants'])} participants, and {fmt_int(mortality['n_events'])} deaths. "
            f"Against severity tertiles, the mortality comparison pattern was {mortality_severity}."
        ),
        "",
        (
            "Mortality estimates should remain secondary in the current manuscript draft. The PH screen flagged selected "
            "cohorts, and piecewise sensitivity flagged KLoSA C2, SHARE C5, and HRS C3-C5 as time-drift terms."
        ),
        "",
        "## Comparator Guardrail",
        "",
        (
            f"Across endpoint-cohort comparisons, the four-domain score result pattern was {four_domain_all} for functional "
            "deterioration and similarly favored four-domain scores for chronic progression and mortality. This should be "
            "stated directly: the manuscript claim is not that endotype classes beat their source continuous measures as "
            "prediction variables. The defensible claim is that the classes provide compact, interpretable, cohort-specific "
            "multidomain profiles with endpoint-specific validation signals."
        ),
        "",
        "## Results Paragraph Order",
        "",
        "1. Cohort readiness and selected denominators.",
        "2. Endotype solution sizes and profile diversity.",
        "3. Functional deterioration as the primary validation endpoint.",
        "4. Chronic progression as secondary validation.",
        "5. Mortality as secondary validation with PH/piecewise sensitivity caveat.",
        "6. Comparator guardrail and final interpretation.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")


def write_internal_zh_summary(path: Path, sample: dict[str, object], labels: dict[str, object]) -> None:
    provisional = "、".join(labels["provisional_classes"]) or "无"
    lines = [
        "# Phase 12 中文内部摘要",
        "",
        "当前结果适合写成“多域衰老异质性/亚型图谱”，不适合写成“分型模型全面优于连续评分预测模型”。",
        "",
        f"- Phase 1 earliest-baseline 女性 50+ 总数：{fmt_int(sample['phase1_baseline_total'])}。",
        f"- strict-primary 完整四域 endotype 样本：{fmt_int(sample['strict_primary_endotype_n'])}。",
        f"- bridge sensitivity endotype 样本：{fmt_int(sample['bridge_endotype_n'])}。",
        f"- 功能恶化验证可用队列：{sample['functional_validation_cohorts']} 个；死亡验证可用队列：{sample['mortality_validation_cohorts']} 个。",
        f"- 需要人工复核的 provisional 标签：{provisional}。",
        "- LASI 当前只能放 baseline profile；SHARE 使用 wave-adjusted sensitivity 分母。",
        "- 主结果优先写功能恶化；死亡作为 secondary validation，并注明 PH/piecewise sensitivity。",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")


def write_report(
    path: Path,
    label_dictionary: pd.DataFrame,
    claims: pd.DataFrame,
    endpoint_summaries: dict[str, dict[str, object]],
) -> None:
    lines = [
        "# Phase 12 Results Skeleton And Label Dictionary",
        "",
        "Generated outputs:",
        "",
        "- `outputs/phase12_label_dictionary_draft.csv`",
        "- `outputs/phase12_results_claims.csv`",
        "- `outputs/phase12_results_skeleton.md`",
        "- `outputs/phase12_internal_zh_summary.md`",
        "",
        "## Label Review Queue",
        "",
    ]
    status_counts = label_dictionary["suggested_label_status"].value_counts().reset_index()
    status_counts.columns = ["suggested_label_status", "n"]
    lines.extend(markdown_table(status_counts, ["suggested_label_status", "n"]))
    lines.extend(["", "## Claims", ""])
    lines.extend(markdown_table(claims, ["claim_id", "manuscript_section", "claim", "caveat"]))
    lines.extend(["", "## Endpoint Summaries", ""])
    endpoint_rows = []
    for endpoint in sorted(endpoint_summaries, key=lambda x: ENDPOINT_ORDER.get(x, 99)):
        item = endpoint_summaries[endpoint]
        endpoint_rows.append(
            {
                "endpoint": endpoint,
                "cohorts": item["n_cohorts"],
                "n": item["n_participants"],
                "events": item["n_events"],
                "severity_comparison": dict_counts_text(item["endotype_vs_severity"]),
                "four_domain_comparison": dict_counts_text(item["endotype_vs_four_domain_scores"]),
            }
        )
    lines.extend(markdown_table(pd.DataFrame(endpoint_rows), list(endpoint_rows[0].keys())))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")


def markdown_table(df: pd.DataFrame, columns: list[str]) -> list[str]:
    if df.empty:
        return ["No rows."]
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in df[columns].to_dict("records"):
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
    return lines


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--manuscript-dir", type=Path, default=None)
    args = parser.parse_args()

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    manuscript_dir = args.manuscript_dir or (output_dir.parent / "manuscript")
    manuscript_dir.mkdir(parents=True, exist_ok=True)

    table1 = read_csv(output_dir, "phase11_table1_cohort_readiness.csv")
    table2 = read_csv(output_dir, "phase11_table2_class_profiles_labels.csv")
    table3 = read_csv(output_dir, "phase11_table3_outcome_validation_summary.csv")

    label_dictionary = build_label_dictionary(table2)
    sample = summarize_table1(table1)
    label_summary = summarize_labels(table2)
    endpoint_summaries = {
        endpoint: endpoint_summary(table3, endpoint)
        for endpoint in sorted(table3["endpoint"].dropna().unique(), key=lambda x: ENDPOINT_ORDER.get(x, 99))
    }
    claims = build_claims(sample, label_summary, endpoint_summaries)

    label_dictionary.to_csv(output_dir / "phase12_label_dictionary_draft.csv", index=False, encoding="utf-8-sig")
    claims.to_csv(output_dir / "phase12_results_claims.csv", index=False, encoding="utf-8-sig")
    write_results_skeleton(output_dir / "phase12_results_skeleton.md", sample, label_summary, endpoint_summaries)
    write_internal_zh_summary(output_dir / "phase12_internal_zh_summary.md", sample, label_summary)
    write_report(output_dir / "phase12_results_skeleton_report.md", label_dictionary, claims, endpoint_summaries)
    write_results_skeleton(manuscript_dir / "results_skeleton.md", sample, label_summary, endpoint_summaries)
    write_internal_zh_summary(manuscript_dir / "internal_zh_summary.md", sample, label_summary)


if __name__ == "__main__":
    main()
