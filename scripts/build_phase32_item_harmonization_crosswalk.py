from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from build_phase3_domain_scores import (
    ANALYSIS_SELECTIONS,
    COHORT_CONFIG,
    DOMAIN_NAMES,
    MISSING_VALUES,
    DomainSpec,
    read_cohort_frame,
    to_numeric,
)


RUN_DATE = "2026-06-02"


COMMON_CONSTRUCTS = {
    "functional": "functional limitation or performance burden",
    "cognitive": "cognitive impairment burden",
    "affective": "depressive or affective symptom burden",
    "cardiometabolic_chronic": "cardiometabolic and chronic disease burden",
}


def clean_value(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def split_variables(value: object) -> set[str]:
    text = clean_value(value)
    if not text:
        return set()
    return {item.strip() for item in text.split("+") if item.strip()}


def item_family(variable: str) -> str:
    name = variable.lower()
    mapping = [
        (("adl", "iadl"), "adl_iadl_limitation"),
        (("grip", "gripsum", "gripcomp"), "grip_strength_or_performance"),
        (("fall",), "falls"),
        (("cog", "tcog", "total_cognition", "cogtot", "cog27"), "global_cognitive_score"),
        (("imrc", "dlrc", "memory"), "memory_recall"),
        (("orient",), "orientation"),
        (("ser7", "numer"), "serial_subtraction_or_numeracy"),
        (("cesd",), "cesd_depressive_symptoms"),
        (("eurod",), "eurod_depressive_symptoms"),
        (("hibpe",), "hypertension"),
        (("diabe",), "diabetes"),
        (("hearte",), "heart_disease"),
        (("stroke",), "stroke"),
        (("dyslipe", "hchole"), "dyslipidemia_or_high_cholesterol"),
        (("cancre",), "cancer"),
    ]
    for keys, label in mapping:
        if any(key in name for key in keys):
            return label
    return "cohort_specific_item"


def comparability_flag(cohort: str, domain: str, variable: str, source: str) -> tuple[str, str]:
    family = item_family(variable)
    if source == "bridge":
        return "bridge_proxy", "Bridge source; not equivalent to strict ADL/IADL limitation."
    if domain == "functional":
        if cohort in {"ELSA", "LASI", "MHAS", "SHARE"}:
            return "strict_core_adl_iadl", "ADL/IADL or direct limitation variables available."
        if cohort == "CHARLS":
            return "partial_functional_iadl_only", "Functional domain uses IADL only in the current cleaned data."
        if cohort == "HRS":
            return "partial_functional_adl_only", "Functional domain uses ADL only in the current cleaned data."
    if domain == "cognitive":
        if family == "global_cognitive_score":
            return "cohort_specific_global_cognitive_score", "Global cognitive scores are harmonized by orientation/z-scoring but not item-identical."
        return "partial_cognitive_item_battery", "Cognitive item batteries differ by cohort and were standardized within cohort/wave."
    if domain == "affective":
        if family == "eurod_depressive_symptoms":
            return "non_cesd_affective_scale", "SHARE uses EURO-D rather than CES-D."
        return "cesd_family_affective_scale", "CES-D-family depressive symptom scale."
    if domain == "cardiometabolic_chronic":
        if family == "dyslipidemia_or_high_cholesterol":
            return "optional_lipid_condition", "Lipid/high-cholesterol item is present in some but not all cohorts."
        return "core_chronic_condition", "Common chronic-condition indicator used in disease-count domain."
    return "cohort_specific", "Cohort-specific harmonized item."


def selected_wave_frame(frame: pd.DataFrame, wave: str) -> pd.DataFrame:
    if wave == "all_rows_no_wave":
        return frame.copy()
    return frame[frame["wave"].astype(str) == str(wave)].copy()


def nonmissing_stats(frame: pd.DataFrame, variable: str) -> tuple[int, float]:
    if variable not in frame.columns:
        return 0, 0.0
    series = frame[variable].astype("string").map(clean_value)
    series = series.mask(series.str.upper().isin(MISSING_VALUES))
    numeric = to_numeric(series)
    nonmissing = int(numeric.notna().sum())
    pct = round(nonmissing / len(frame) * 100, 2) if len(frame) else 0.0
    return nonmissing, pct


def build_crosswalk(data_root: Path, database_root: Path, output_dir: Path) -> pd.DataFrame:
    domain_dict = pd.read_csv(output_dir / "phase28_domain_harmonization_dictionary.csv", low_memory=False)
    domain_lookup = {
        (row["analysis_set"], row["cohort"], row["domain"]): row
        for row in domain_dict.to_dict("records")
    }
    rows = []
    for selection in ANALYSIS_SELECTIONS:
        cohort = selection["cohort"]
        analysis_set = selection["analysis_set"]
        analysis_tier = selection["tier"]
        wave = str(selection["wave"])
        frame = selected_wave_frame(read_cohort_frame(data_root, cohort, database_root), wave)
        config = COHORT_CONFIG[cohort]
        domains: dict[str, DomainSpec] = config["domains"]  # type: ignore[assignment]
        for domain in DOMAIN_NAMES:
            spec = domains[domain]
            domain_row = domain_lookup.get((analysis_set, cohort, domain), {})
            used_variables = split_variables(domain_row.get("variables", ""))
            for group_index, group in enumerate(spec.groups, start=1):
                group_label = "primary_group" if group_index == 1 else f"fallback_group_{group_index}"
                for item_index, varspec in enumerate(group, start=1):
                    nonmissing_n, nonmissing_pct = nonmissing_stats(frame, varspec.name)
                    comparability, note = comparability_flag(cohort, domain, varspec.name, spec.source)
                    rows.append(
                        {
                            "analysis_set": analysis_set,
                            "analysis_tier": analysis_tier,
                            "cohort": cohort,
                            "wave": wave,
                            "domain": domain,
                            "common_construct": COMMON_CONSTRUCTS[domain],
                            "source_tier": spec.source,
                            "candidate_group_index": group_index,
                            "candidate_group_role": group_label,
                            "item_order_within_group": item_index,
                            "variable": varspec.name,
                            "item_family": item_family(varspec.name),
                            "raw_direction": varspec.direction,
                            "score_orientation": "higher_domain_score_worse_after_orientation",
                            "used_in_selected_domain_score": int(varspec.name in used_variables),
                            "item_nonmissing_n": nonmissing_n,
                            "item_nonmissing_pct": nonmissing_pct,
                            "domain_nonmissing_n": domain_row.get("nonmissing_n", ""),
                            "domain_nonmissing_pct": domain_row.get("nonmissing_pct", ""),
                            "complete_four_domain_n": domain_row.get("complete_four_domain_n", ""),
                            "baseline_women_age50plus_n": domain_row.get("baseline_women_age50plus_n", ""),
                            "comparability_flag": comparability,
                            "comparability_note": note,
                        }
                    )
    return pd.DataFrame(rows)


def build_tier_lock(output_dir: Path) -> pd.DataFrame:
    table1 = pd.read_csv(output_dir / "phase11_table1_cohort_readiness.csv", low_memory=False)
    leakage = pd.read_csv(output_dir / "phase32_functional_endpoint_leakage_audit.csv", low_memory=False)
    decoupled = pd.read_csv(output_dir / "phase32_decoupled_validation_comparison.csv", low_memory=False)
    gmm = pd.read_csv(output_dir / "phase32_gmm_stability_summary.csv", low_memory=False)

    out = table1[
        [
            "analysis_set",
            "analysis_tier",
            "cohort",
            "manuscript_role",
            "baseline_women_age50plus_n",
            "complete_four_domain_n",
            "selected_endotype_n",
            "functional_deterioration_ge_0_5sd_available_n",
            "functional_deterioration_ge_0_5sd_event_n",
        ]
    ].merge(
        leakage[
            [
                "analysis_set",
                "analysis_tier",
                "cohort",
                "functional_source_tier",
                "functional_variables",
                "phase32_main_evidence_status",
            ]
        ],
        on=["analysis_set", "analysis_tier", "cohort"],
        how="left",
    )
    out = out.merge(
        decoupled[["analysis_set", "analysis_tier", "cohort", "phase32b_evidence_status"]],
        on=["analysis_set", "analysis_tier", "cohort"],
        how="left",
    )
    out = out.merge(
        gmm[["analysis_set", "analysis_tier", "cohort", "phase32d_stability_status"]],
        on=["analysis_set", "analysis_tier", "cohort"],
        how="left",
    )
    out["phase32b_evidence_status"] = out["phase32b_evidence_status"].fillna("exclude_no_followup_validation")
    out["manuscript_role_lock"] = out.apply(role_lock, axis=1)
    out["allowed_main_claim"] = out["manuscript_role_lock"].map(allowed_claim)
    return out.sort_values(["analysis_tier", "cohort"]).reset_index(drop=True)


def role_lock(row: pd.Series) -> str:
    cohort = str(row["cohort"])
    if cohort == "KLoSA":
        return "bridge_sensitivity_descriptive_only"
    if cohort == "LASI":
        return "baseline_profile_construction_only_no_followup_validation"
    if cohort == "SHARE":
        return "strict_construction_but_validation_downgraded"
    return "strict_construction_within_cohort_gradient_only"


def allowed_claim(role: str) -> str:
    claims = {
        "bridge_sensitivity_descriptive_only": "Sensitivity construction only; do not pool as strict primary evidence.",
        "baseline_profile_construction_only_no_followup_validation": "Baseline profile construction only; no follow-up validation denominator.",
        "strict_construction_but_validation_downgraded": "Descriptive construction allowed; functional validation downgraded by endpoint/model diagnostics.",
        "strict_construction_within_cohort_gradient_only": "Descriptive construction and within-cohort outcome gradients only; no prediction-superiority claim.",
    }
    return claims.get(role, "Manual review required.")


def markdown_table(df: pd.DataFrame, columns: list[str]) -> list[str]:
    if df.empty:
        return ["No rows."]
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in df[columns].to_dict("records"):
        values = []
        for column in columns:
            value = row[column]
            if pd.isna(value):
                values.append("")
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return lines


def write_report(path: Path, crosswalk: pd.DataFrame, tier_lock: pd.DataFrame) -> None:
    comparability_counts = (
        crosswalk.groupby(["domain", "comparability_flag"], dropna=False)
        .size()
        .reset_index(name="item_rows")
        .sort_values(["domain", "comparability_flag"])
    )
    lines = [
        "# Phase 32E Item-Level Harmonization Crosswalk",
        "",
        f"Date: {RUN_DATE}",
        "",
        "## Generated Files",
        "",
        "- `outputs/phase32_item_level_harmonization_crosswalk.csv`",
        "- `outputs/phase32_cohort_tier_lock.csv`",
        "- `outputs/phase32_item_level_harmonization_report.md`",
        "",
        "## Comparability Summary",
        "",
    ]
    lines.extend(markdown_table(comparability_counts, ["domain", "comparability_flag", "item_rows"]))
    lines.extend(["", "## Cohort Tier Lock", ""])
    lines.extend(
        markdown_table(
            tier_lock,
            [
                "cohort",
                "functional_source_tier",
                "phase32_main_evidence_status",
                "phase32b_evidence_status",
                "phase32d_stability_status",
                "manuscript_role_lock",
            ],
        )
    )
    lines.extend(
        [
            "",
            "## Manuscript Rule",
            "",
            "The manuscript must not describe all seven cohorts as equivalent strict validation cohorts.",
            "Table 1 and all figure legends should use the `manuscript_role_lock` values from `phase32_cohort_tier_lock.csv`.",
            "The harmonization crosswalk should be used as the variable dictionary in the additional files instead of the domain-only Phase 28 dictionary.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", required=True, type=Path)
    parser.add_argument("--database-root", required=True, type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    crosswalk = build_crosswalk(args.data_root, args.database_root, args.output_dir)
    tier_lock = build_tier_lock(args.output_dir)

    crosswalk.to_csv(args.output_dir / "phase32_item_level_harmonization_crosswalk.csv", index=False, encoding="utf-8-sig")
    tier_lock.to_csv(args.output_dir / "phase32_cohort_tier_lock.csv", index=False, encoding="utf-8-sig")
    write_report(args.output_dir / "phase32_item_level_harmonization_report.md", crosswalk, tier_lock)

    print("Phase 32E item-level harmonization crosswalk complete.")
    print(tier_lock[["cohort", "manuscript_role_lock"]].to_string(index=False))


if __name__ == "__main__":
    main()
