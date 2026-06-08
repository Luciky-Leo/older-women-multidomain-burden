from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


DOMAIN_COLUMNS = [
    "functional_score",
    "cognitive_score",
    "affective_score",
    "cardiometabolic_chronic_score",
]

DOMAIN_EN = {
    "functional_score": "functional",
    "cognitive_score": "cognitive",
    "affective_score": "affective",
    "cardiometabolic_chronic_score": "cardiometabolic",
}

DOMAIN_ZH = {
    "functional_score": "功能",
    "cognitive_score": "认知",
    "affective_score": "心理/抑郁",
    "cardiometabolic_chronic_score": "心代谢/慢病",
}


def burden_level(severity: float) -> tuple[str, str]:
    if severity <= -0.45:
        return "low-burden", "低负担"
    if severity <= 0.15:
        return "intermediate-burden", "中等负担"
    if severity <= 0.75:
        return "elevated-burden", "较高负担"
    return "high-burden", "高负担"


def domain_pattern(row: pd.Series) -> tuple[list[str], list[str]]:
    severity = float(row["severity_mean"])
    high = []
    spared = []
    for column in DOMAIN_COLUMNS:
        value = float(row[column])
        if value - severity >= 0.35 or value >= 1.0:
            high.append(column)
        if value - severity <= -0.35 or value <= -0.75:
            spared.append(column)
    return high, spared


def make_label(row: pd.Series) -> dict[str, object]:
    burden_en, burden_zh = burden_level(float(row["severity_mean"]))
    high, spared = domain_pattern(row)

    if high:
        high_en = "/".join(DOMAIN_EN[col] for col in high)
        high_zh = "/".join(DOMAIN_ZH[col] for col in high)
        label_en = f"{high_en}-dominant {burden_en}"
        label_zh = f"{high_zh}主导型{burden_zh}"
    elif spared:
        spared_en = "/".join(DOMAIN_EN[col] for col in spared)
        spared_zh = "/".join(DOMAIN_ZH[col] for col in spared)
        label_en = f"{burden_en} with spared {spared_en}"
        label_zh = f"{spared_zh}相对保留的{burden_zh}"
    else:
        label_en = f"{burden_en} severity-aligned"
        label_zh = f"{burden_zh}严重度一致型"

    outcome_flags = []
    for column, label in [
        ("functional_or_formatted", "functional-risk"),
        ("chronic_or_formatted", "chronic-progression-risk"),
        ("mortality_hr_formatted", "mortality-risk"),
    ]:
        text = str(row.get(column, ""))
        if text and not text.startswith("1.00"):
            try:
                value = float(text.split(" ", 1)[0])
                if value >= 1.5:
                    outcome_flags.append(label)
            except ValueError:
                pass

    confidence = "moderate"
    if not high and not spared:
        confidence = "low"
    if len(high) >= 1 and row.get("class_pct", 0) >= 8:
        confidence = "high"
    if row.get("mortality_drift_flag", 0) == 1:
        confidence = "provisional"

    return {
        "label_en": label_en,
        "label_zh": label_zh,
        "high_domains": ";".join(DOMAIN_EN[col] for col in high),
        "spared_domains": ";".join(DOMAIN_EN[col] for col in spared),
        "outcome_flags": ";".join(outcome_flags),
        "label_confidence": confidence,
    }


def read_drift_flags(output_dir: Path) -> pd.DataFrame:
    path = output_dir / "phase9_mortality_piecewise_stability.csv"
    if not path.exists():
        return pd.DataFrame(columns=["analysis_set", "cohort", "class", "mortality_drift_flag"])
    drift = pd.read_csv(path, low_memory=False)
    if drift.empty:
        return pd.DataFrame(columns=["analysis_set", "cohort", "class", "mortality_drift_flag"])
    drift["class"] = pd.to_numeric(drift["term_label"], errors="coerce").astype("Int64")
    drift["mortality_drift_flag"] = (
        (pd.to_numeric(drift.get("direction_change", 0), errors="coerce").fillna(0) == 1)
        | (pd.to_numeric(drift.get("large_time_drift", 0), errors="coerce").fillna(0) == 1)
    ).astype(int)
    return drift[["analysis_set", "cohort", "class", "mortality_drift_flag"]]


def build_labels(output_dir: Path) -> pd.DataFrame:
    review = pd.read_csv(output_dir / "phase7_class_outcome_review.csv", low_memory=False)
    drift = read_drift_flags(output_dir)
    review["class"] = pd.to_numeric(review["class"], errors="coerce").astype("Int64")
    review = review.merge(drift, on=["analysis_set", "cohort", "class"], how="left")
    review["mortality_drift_flag"] = review["mortality_drift_flag"].fillna(0).astype(int)

    label_rows = []
    for _, row in review.iterrows():
        label_rows.append(make_label(row))
    labels = pd.concat([review.reset_index(drop=True), pd.DataFrame(label_rows)], axis=1)
    ordered = [
        "analysis_set",
        "analysis_tier",
        "cohort",
        "class",
        "class_n",
        "class_pct",
        "label_en",
        "label_zh",
        "label_confidence",
        "high_domains",
        "spared_domains",
        "outcome_flags",
        "profile_label",
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
    ]
    return labels[[column for column in ordered if column in labels.columns]].sort_values(["analysis_set", "cohort", "class"])


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
            elif isinstance(value, float):
                values.append(str(round(value, 3)))
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return lines


def write_report(path: Path, labels: pd.DataFrame) -> None:
    lines = [
        "# Phase 10 Class Label Candidates",
        "",
        "These labels are deterministic candidates for manuscript triage.",
        "They should be manually edited before final tables because cohort-specific clinical context still matters.",
        "",
        "## Candidate Labels",
        "",
    ]
    columns = [
        "analysis_set",
        "cohort",
        "class",
        "class_pct",
        "label_en",
        "label_zh",
        "label_confidence",
        "outcome_flags",
        "mortality_drift_flag",
    ]
    lines.extend(markdown_table(labels, columns))
    lines.extend(
        [
            "",
            "## Use Rules",
            "",
            "- Use English labels for figure legends and Chinese labels for internal review notes.",
            "- Treat `provisional` labels as requiring manual review, usually because mortality HRs drift across follow-up periods.",
            "- Do not force identical labels across cohorts unless the four-domain profiles and outcome signals are genuinely similar.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    labels = build_labels(args.output_dir)
    labels.to_csv(args.output_dir / "phase10_class_label_candidates.csv", index=False, encoding="utf-8-sig")
    write_report(args.output_dir / "phase10_class_label_candidates_report.md", labels)


if __name__ == "__main__":
    main()
