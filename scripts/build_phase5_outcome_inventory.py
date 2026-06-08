from __future__ import annotations

import argparse
import re
from pathlib import Path

import numpy as np
import pandas as pd

from build_phase3_domain_scores import COHORT_CONFIG, find_clean_csv, read_header_map


DOMAIN_COLUMNS = [
    "functional_score",
    "cognitive_score",
    "affective_score",
    "cardiometabolic_chronic_score",
]

DOMAIN_OUTCOME_PREFIXES = {
    "functional_score": "functional_deterioration",
    "cognitive_score": "cognitive_worsening",
    "affective_score": "affective_worsening",
    "cardiometabolic_chronic_score": "cardiometabolic_worsening",
}

DIRECT_MORTALITY_PATTERN = re.compile(
    r"(death|dead|died|mort|vital|alive|exit|^iwstat$|iwstat$|^radyear$|^radmonth$|dyear|dmonth)",
    re.IGNORECASE,
)
BROAD_STATUS_PATTERN = re.compile(
    r"(death|dead|died|mort|vital|alive|exit|status|^iwstat$|iwstat$|^radyear$|^radmonth$|dyear|dmonth)",
    re.IGNORECASE,
)
FOLLOWUP_WAVE_PATTERN = re.compile(r"(wave|iwy|iwendy|iwindy|year|date|interview)", re.IGNORECASE)
DETERIORATION_THRESHOLD = 0.5
DETERIORATION_LABEL = str(DETERIORATION_THRESHOLD).replace(".", "_")


def safe_pct(numerator: int | float, denominator: int | float) -> float:
    if denominator == 0 or pd.isna(denominator):
        return np.nan
    return round(float(numerator) / float(denominator) * 100, 2)


def join_hits(values: list[str], limit: int = 60) -> str:
    if not values:
        return ""
    return ";".join(values[:limit])


def build_variable_inventory(data_root: Path) -> pd.DataFrame:
    rows = []
    for cohort, config in COHORT_CONFIG.items():
        path = find_clean_csv(data_root, str(config["file"]))
        header_map = read_header_map(path)
        variables = sorted(header_map)
        direct_mortality = [var for var in variables if DIRECT_MORTALITY_PATTERN.search(var)]
        broad_status = [var for var in variables if BROAD_STATUS_PATTERN.search(var)]
        wave_date = [var for var in variables if FOLLOWUP_WAVE_PATTERN.search(var)]
        domains = config["domains"]
        domain_variables = {}
        for domain_name, domain in domains.items():
            used = []
            for group in domain.groups:
                for spec in group:
                    if spec.name in header_map and spec.name not in used:
                        used.append(spec.name)
            domain_variables[domain_name] = used
        rows.append(
            {
                "cohort": cohort,
                "clean_csv": str(path),
                "n_columns": len(variables),
                "direct_mortality_candidate_n": len(direct_mortality),
                "direct_mortality_candidates": join_hits(direct_mortality),
                "broad_status_candidate_n": len(broad_status),
                "broad_status_candidates": join_hits(broad_status),
                "mortality_ready_from_clean_csv": int(len(direct_mortality) > 0),
                "wave_date_candidates": join_hits(wave_date),
                "functional_variables": join_hits(domain_variables["functional"]),
                "cognitive_variables": join_hits(domain_variables["cognitive"]),
                "affective_variables": join_hits(domain_variables["affective"]),
                "cardiometabolic_chronic_variables": join_hits(domain_variables["cardiometabolic_chronic"]),
            }
        )
    return pd.DataFrame(rows)


def read_scores(path: Path) -> pd.DataFrame:
    wanted = [
        "cohort",
        "participant_id",
        "wave",
        "age",
        *DOMAIN_COLUMNS,
        "complete_four_domain",
        "cardiometabolic_chronic_count",
        "cardiometabolic_chronic_prop",
    ]
    scores = pd.read_csv(path, usecols=lambda col: col in wanted, dtype={"participant_id": str, "wave": str}, low_memory=False)
    for column in DOMAIN_COLUMNS + ["age", "cardiometabolic_chronic_count", "cardiometabolic_chronic_prop"]:
        if column in scores.columns:
            scores[column] = pd.to_numeric(scores[column], errors="coerce")
    scores["wave"] = scores["wave"].astype("string")
    scores["wave_num"] = pd.to_numeric(scores["wave"], errors="coerce")
    return scores


def read_assignments(path: Path) -> pd.DataFrame:
    assignments = pd.read_csv(path, dtype={"participant_id": str, "wave": str}, low_memory=False)
    for column in ["age", "severity_score", "endotype_posterior", *DOMAIN_COLUMNS]:
        assignments[column] = pd.to_numeric(assignments[column], errors="coerce")
    assignments["wave"] = assignments["wave"].astype("string")
    assignments["baseline_wave"] = assignments["wave"]
    assignments["baseline_wave_num"] = pd.to_numeric(assignments["baseline_wave"], errors="coerce")
    assignments["endotype_class"] = assignments["endotype_class"].astype(str)
    assignments["severity_tertile"] = (
        assignments.groupby(["analysis_set", "cohort"], group_keys=False)["severity_score"]
        .apply(lambda values: pd.qcut(values.rank(method="first"), q=3, labels=["low", "middle", "high"]).astype(str))
        .reindex(assignments.index)
    )
    return assignments


def attach_baseline_chronic_count(assignments: pd.DataFrame, scores: pd.DataFrame) -> pd.DataFrame:
    baseline = scores[
        ["cohort", "participant_id", "wave", "cardiometabolic_chronic_count", "cardiometabolic_chronic_prop"]
    ].drop_duplicates(["cohort", "participant_id", "wave"])
    baseline = baseline.rename(
        columns={
            "wave": "baseline_wave",
            "cardiometabolic_chronic_count": "baseline_cardiometabolic_chronic_count",
            "cardiometabolic_chronic_prop": "baseline_cardiometabolic_chronic_prop",
        }
    )
    return assignments.merge(baseline, on=["cohort", "participant_id", "baseline_wave"], how="left")


def build_participant_screen(assignments: pd.DataFrame, scores: pd.DataFrame) -> pd.DataFrame:
    keys = ["analysis_set", "analysis_tier", "cohort", "participant_id"]
    base_keys = assignments[keys + ["baseline_wave", "baseline_wave_num"]].copy()
    follow = scores[
        [
            "cohort",
            "participant_id",
            "wave",
            "wave_num",
            "age",
            *DOMAIN_COLUMNS,
            "complete_four_domain",
            "cardiometabolic_chronic_count",
            "cardiometabolic_chronic_prop",
        ]
    ].rename(
        columns={
            "wave": "followup_wave",
            "wave_num": "followup_wave_num",
            "age": "followup_age",
            "complete_four_domain": "followup_complete_four_domain",
            "cardiometabolic_chronic_count": "followup_cardiometabolic_chronic_count",
            "cardiometabolic_chronic_prop": "followup_cardiometabolic_chronic_prop",
            **{column: f"followup_{column}" for column in DOMAIN_COLUMNS},
        }
    )
    candidates = base_keys.merge(follow, on=["cohort", "participant_id"], how="left")
    candidates = candidates[candidates["followup_wave_num"] > candidates["baseline_wave_num"]].copy()

    followup_counts = (
        candidates.groupby(keys, dropna=False)
        .agg(
            followup_rows=("followup_wave", "size"),
            last_followup_wave_num=("followup_wave_num", "max"),
            max_followup_age=("followup_age", "max"),
        )
        .reset_index()
    )
    last_followup = (
        candidates.sort_values(keys + ["followup_wave_num"])
        .drop_duplicates(keys, keep="last")
        .drop(columns=["baseline_wave", "baseline_wave_num"])
    )

    screen = assignments.merge(followup_counts, on=keys, how="left")
    screen = screen.merge(last_followup, on=keys, how="left", suffixes=("", "_last"))
    screen["followup_rows"] = screen["followup_rows"].fillna(0).astype(int)
    screen["any_followup"] = (screen["followup_rows"] > 0).astype(int)
    screen["followup_year_span"] = screen["max_followup_age"] - screen["age"]

    for column, prefix in DOMAIN_OUTCOME_PREFIXES.items():
        follow_col = f"followup_{column}"
        change_col = f"{prefix}_change"
        available_col = f"{prefix}_available"
        event_col = f"{prefix}_ge_{DETERIORATION_LABEL}sd"
        screen[change_col] = screen[follow_col] - screen[column]
        available = screen[column].notna() & screen[follow_col].notna()
        screen[available_col] = available.astype(int)
        screen[event_col] = pd.Series(pd.NA, index=screen.index, dtype="Float64")
        screen.loc[available, event_col] = (screen.loc[available, change_col] >= DETERIORATION_THRESHOLD).astype(int)

    chronic_available = screen["baseline_cardiometabolic_chronic_count"].notna() & screen[
        "followup_cardiometabolic_chronic_count"
    ].notna()
    screen["chronic_count_change"] = (
        screen["followup_cardiometabolic_chronic_count"] - screen["baseline_cardiometabolic_chronic_count"]
    )
    screen["chronic_progression_available"] = chronic_available.astype(int)
    screen["chronic_progression_ge_1_condition"] = pd.Series(pd.NA, index=screen.index, dtype="Float64")
    screen.loc[chronic_available, "chronic_progression_ge_1_condition"] = (
        screen.loc[chronic_available, "chronic_count_change"] >= 1
    ).astype(int)
    return screen


def summarize_groups(screen: pd.DataFrame) -> pd.DataFrame:
    group_specs = [
        ("overall", "overall_group"),
        ("endotype_class", "endotype_class"),
        ("severity_tertile", "severity_tertile"),
    ]
    temp = screen.copy()
    temp["overall_group"] = "all"
    outcome_specs = [
        ("functional_deterioration_ge_0_5sd", "functional_deterioration_available", "functional_deterioration_ge_0_5sd"),
        ("cognitive_worsening_ge_0_5sd", "cognitive_worsening_available", "cognitive_worsening_ge_0_5sd"),
        ("affective_worsening_ge_0_5sd", "affective_worsening_available", "affective_worsening_ge_0_5sd"),
        (
            "cardiometabolic_worsening_ge_0_5sd",
            "cardiometabolic_worsening_available",
            "cardiometabolic_worsening_ge_0_5sd",
        ),
        ("chronic_progression_ge_1_condition", "chronic_progression_available", "chronic_progression_ge_1_condition"),
    ]
    rows = []
    base_cols = ["analysis_set", "analysis_tier", "cohort"]
    for group_type, group_col in group_specs:
        for keys, group in temp.groupby(base_cols + [group_col], dropna=False):
            analysis_set, analysis_tier, cohort, group_value = keys
            baseline_n = len(group)
            any_followup_n = int(group["any_followup"].sum())
            row = {
                "analysis_set": analysis_set,
                "analysis_tier": analysis_tier,
                "cohort": cohort,
                "group_type": group_type,
                "group_value": str(group_value),
                "baseline_n": baseline_n,
                "any_followup_n": any_followup_n,
                "any_followup_pct": safe_pct(any_followup_n, baseline_n),
                "median_followup_rows": round(float(group["followup_rows"].median()), 2),
                "max_followup_wave": group["last_followup_wave_num"].max(),
                "median_followup_year_span": round(float(group["followup_year_span"].median()), 2)
                if group["followup_year_span"].notna().any()
                else np.nan,
            }
            for event_col, available_col, prefix in outcome_specs:
                available_n = int(group[available_col].sum())
                event_n = int(group[event_col].fillna(0).sum())
                row[f"{prefix}_available_n"] = available_n
                row[f"{prefix}_event_n"] = event_n
                row[f"{prefix}_event_pct"] = safe_pct(event_n, available_n)
            rows.append(row)
    return pd.DataFrame(rows).sort_values(["analysis_set", "cohort", "group_type", "group_value"])


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


def write_report(path: Path, variable_inventory: pd.DataFrame, summary: pd.DataFrame) -> None:
    mortality_ready = variable_inventory[variable_inventory["mortality_ready_from_clean_csv"] == 1]
    broad_status = variable_inventory[variable_inventory["broad_status_candidate_n"] > 0]
    overall = summary[summary["group_type"] == "overall"].copy()
    overall_columns = [
        "analysis_set",
        "cohort",
        "baseline_n",
        "any_followup_n",
        "any_followup_pct",
        "max_followup_wave",
        "functional_deterioration_ge_0_5sd_available_n",
        "functional_deterioration_ge_0_5sd_event_n",
        "chronic_progression_ge_1_condition_available_n",
        "chronic_progression_ge_1_condition_event_n",
    ]
    lines = [
        "# Phase 5 Outcome Inventory",
        "",
        "This is a screening inventory for outcome validation after the Phase 4 endotype screen.",
        "Domain-score deterioration is defined as a >= 0.5 SD increase in the worse-health direction from baseline to the last observed later wave.",
        "Chronic progression is defined as an increase of >= 1 cardiometabolic/chronic condition from baseline to the last observed later wave.",
        "",
        "## Mortality Readiness",
        "",
    ]
    if mortality_ready.empty:
        lines.append("- No direct mortality candidate variables were found in the cleaned seven-cohort CSV files.")
        lines.append("- Mortality validation therefore needs targeted extraction from harmonized tracker, end-of-life, exit, or raw mortality files.")
    else:
        lines.append("- Direct mortality candidates were found in these cleaned CSV files:")
        for row in mortality_ready.to_dict("records"):
            lines.append(f"  - {row['cohort']}: {row['direct_mortality_candidates']}")
    if not broad_status.empty:
        lines.extend(["", "Broad status-like hits that need manual interpretation:"])
        for row in broad_status.to_dict("records"):
            lines.append(f"- {row['cohort']}: {row['broad_status_candidates']}")

    lines.extend(["", "## Follow-Up Outcome Screen", ""])
    lines.extend(markdown_table(overall, overall_columns))
    lines.extend(
        [
            "",
            "## Proceeding Decision",
            "",
            "- Functional deterioration and chronic progression can be screened from the cleaned longitudinal CSV files for all multi-wave cohorts.",
            "- LASI currently contributes baseline endotypes but no cleaned longitudinal follow-up in this CSV pass.",
            "- Mortality should be handled through the DTA-label-confirmed `radyear`, `radmonth`, and `iwstat` fields rather than name-only screening.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", required=True, type=Path)
    parser.add_argument("--scores-long", required=True, type=Path)
    parser.add_argument("--assignments", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    variable_inventory = build_variable_inventory(args.data_root)
    scores = read_scores(args.scores_long)
    assignments = read_assignments(args.assignments)
    assignments = attach_baseline_chronic_count(assignments, scores)
    screen = build_participant_screen(assignments, scores)
    summary = summarize_groups(screen)

    variable_inventory.to_csv(args.output_dir / "phase5_outcome_variable_inventory.csv", index=False, encoding="utf-8-sig")
    screen.to_csv(args.output_dir / "phase5_participant_outcome_screen.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(args.output_dir / "phase5_followup_outcome_inventory.csv", index=False, encoding="utf-8-sig")
    write_report(args.output_dir / "phase5_outcome_inventory_report.md", variable_inventory, summary)


if __name__ == "__main__":
    main()
