from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from build_phase3_domain_scores import COHORT_CONFIG, find_clean_csv, read_header_map


INTERVIEW_YEAR_CANDIDATES = ("iwy", "iwendy", "iwindy", "r1iwy")
MORTALITY_CANDIDATES = ("iwstat", "radyear", "radmonth")


def to_numeric(series: pd.Series) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce")
    return values.mask(values < 0)


def clean_year(series: pd.Series) -> pd.Series:
    values = to_numeric(series)
    return values.where((values >= 1900) & (values <= 2100))


def clean_month(series: pd.Series) -> pd.Series:
    values = to_numeric(series)
    return values.where((values >= 1) & (values <= 12))


def read_labels(database_root: Path, cohort: str) -> dict[str, str]:
    file_name = str(COHORT_CONFIG[cohort]["file"]).replace(".csv", ".dta")
    matches = [path for path in database_root.rglob(file_name) if "Working_data" in str(path)]
    if not matches:
        return {}
    try:
        reader = pd.read_stata(str(matches[0]), iterator=True)
        return reader.variable_labels()
    except Exception:
        return {}


def build_variable_inventory(data_root: Path, database_root: Path) -> pd.DataFrame:
    rows = []
    for cohort, config in COHORT_CONFIG.items():
        csv_path = find_clean_csv(data_root, str(config["file"]))
        header_map = read_header_map(csv_path)
        labels = read_labels(database_root, cohort)
        present = [var for var in MORTALITY_CANDIDATES if var in header_map]
        for var in present:
            rows.append(
                {
                    "cohort": cohort,
                    "clean_csv": str(csv_path),
                    "variable": var,
                    "label_from_working_dta": labels.get(var, ""),
                    "role": "death_status" if var == "iwstat" else "death_year" if var == "radyear" else "death_month",
                    "usable_for_mortality_screen": int(var in {"radyear", "radmonth", "iwstat"}),
                }
            )
        if not present:
            rows.append(
                {
                    "cohort": cohort,
                    "clean_csv": str(csv_path),
                    "variable": "",
                    "label_from_working_dta": "",
                    "role": "",
                    "usable_for_mortality_screen": 0,
                }
            )
    return pd.DataFrame(rows)


def read_cohort_mortality_frame(data_root: Path, cohort: str) -> pd.DataFrame:
    config = COHORT_CONFIG[cohort]
    csv_path = find_clean_csv(data_root, str(config["file"]))
    header_map = read_header_map(csv_path)
    wanted = {str(config["id"])}
    if config["wave"]:
        wanted.add(str(config["wave"]))
    wanted.update(INTERVIEW_YEAR_CANDIDATES)
    wanted.update(MORTALITY_CANDIDATES)
    available = {var: header_map[var] for var in wanted if var in header_map}
    if str(config["id"]) not in available:
        raise KeyError(f"{cohort} missing id variable {config['id']}")
    frame = pd.read_csv(
        csv_path,
        usecols=list(available.values()),
        dtype=str,
        encoding="utf-8-sig",
        low_memory=False,
    ).rename(columns={raw: var for var, raw in available.items()})
    frame["cohort"] = cohort
    frame["participant_id"] = frame[str(config["id"])].astype("string")
    if config["wave"] and str(config["wave"]) in frame.columns:
        frame["wave"] = frame[str(config["wave"])].astype("string")
    else:
        frame["wave"] = "all_rows_no_wave"

    interview_year = pd.Series(np.nan, index=frame.index, dtype="float")
    for candidate in INTERVIEW_YEAR_CANDIDATES:
        if candidate in frame.columns:
            interview_year = interview_year.fillna(clean_year(frame[candidate]))
    frame["interview_year"] = interview_year
    frame["wave_num"] = pd.to_numeric(frame["wave"], errors="coerce")
    frame["death_year"] = clean_year(frame["radyear"]) if "radyear" in frame.columns else np.nan
    frame["death_month"] = clean_month(frame["radmonth"]) if "radmonth" in frame.columns else np.nan
    frame["iwstat_numeric"] = to_numeric(frame["iwstat"]) if "iwstat" in frame.columns else np.nan
    return frame[["cohort", "participant_id", "wave", "wave_num", "interview_year", "death_year", "death_month", "iwstat_numeric"]]


def summarize_person_mortality(long_frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for keys, group in long_frame.groupby(["cohort", "participant_id"], dropna=False):
        cohort, participant_id = keys
        death_years = group["death_year"].dropna()
        death_year = float(death_years.min()) if not death_years.empty else np.nan
        death_month = np.nan
        if not pd.isna(death_year):
            month_candidates = group.loc[group["death_year"] == death_year, "death_month"].dropna()
            if not month_candidates.empty:
                death_month = float(month_candidates.min())
        rows.append(
            {
                "cohort": cohort,
                "participant_id": participant_id,
                "death_year": death_year,
                "death_month": death_month,
                "any_iwstat_death": int((group["iwstat_numeric"] == 1).any()),
                "last_interview_year": group["interview_year"].max(),
                "last_observed_wave": group["wave_num"].max(),
            }
        )
    return pd.DataFrame(rows)


def baseline_frame(long_frame: pd.DataFrame, assignments: pd.DataFrame) -> pd.DataFrame:
    base = long_frame[["cohort", "participant_id", "wave", "interview_year"]].dropna(subset=["interview_year"]).copy()
    base = base.rename(columns={"wave": "baseline_wave", "interview_year": "baseline_interview_year"})
    base = base.drop_duplicates(["cohort", "participant_id", "baseline_wave"])
    out = assignments.merge(base, on=["cohort", "participant_id", "baseline_wave"], how="left")
    return out


def read_assignments(path: Path) -> pd.DataFrame:
    assignments = pd.read_csv(path, dtype={"participant_id": str, "wave": str}, low_memory=False)
    assignments["baseline_wave"] = assignments["wave"].astype("string")
    assignments["endotype_class"] = assignments["endotype_class"].astype(str)
    for column in [
        "age",
        "severity_score",
        "functional_score",
        "cognitive_score",
        "affective_score",
        "cardiometabolic_chronic_score",
    ]:
        assignments[column] = pd.to_numeric(assignments[column], errors="coerce")
    assignments["severity_tertile"] = (
        assignments.groupby(["analysis_set", "cohort"], group_keys=False)["severity_score"]
        .apply(lambda values: pd.qcut(values.rank(method="first"), q=3, labels=["low", "middle", "high"]).astype(str))
        .reindex(assignments.index)
    )
    return assignments


def build_mortality_screen(assignments: pd.DataFrame, long_frame: pd.DataFrame, person_mortality: pd.DataFrame) -> pd.DataFrame:
    screen = baseline_frame(long_frame, assignments)
    screen = screen.merge(person_mortality, on=["cohort", "participant_id"], how="left")
    screen["death_event"] = 0
    valid_death = screen["death_year"].notna() & screen["baseline_interview_year"].notna()
    screen.loc[valid_death, "death_event"] = (
        screen.loc[valid_death, "death_year"] >= screen.loc[valid_death, "baseline_interview_year"]
    ).astype(int)
    screen["death_time_years"] = (
        screen["death_year"] + ((screen["death_month"].fillna(6.0) - 0.5) / 12.0) - screen["baseline_interview_year"]
    )
    screen.loc[screen["death_event"] != 1, "death_time_years"] = np.nan
    screen["censor_year"] = screen["last_interview_year"]
    screen["followup_time_years"] = screen["censor_year"] - screen["baseline_interview_year"]
    screen.loc[screen["death_event"] == 1, "followup_time_years"] = screen.loc[screen["death_event"] == 1, "death_time_years"]
    screen["mortality_followup_available"] = (
        screen["baseline_interview_year"].notna()
        & (screen["death_event"].eq(1) | screen["censor_year"].notna())
        & screen["followup_time_years"].notna()
        & (screen["followup_time_years"] > 0)
    ).astype(int)
    return screen


def safe_pct(numerator: int | float, denominator: int | float) -> float:
    if denominator == 0 or pd.isna(denominator):
        return np.nan
    return round(float(numerator) / float(denominator) * 100, 2)


def summarize_groups(screen: pd.DataFrame) -> pd.DataFrame:
    temp = screen.copy()
    temp["overall_group"] = "all"
    rows = []
    for group_type, group_col in [
        ("overall", "overall_group"),
        ("endotype_class", "endotype_class"),
        ("severity_tertile", "severity_tertile"),
    ]:
        for keys, group in temp.groupby(["analysis_set", "analysis_tier", "cohort", group_col], dropna=False):
            analysis_set, analysis_tier, cohort, group_value = keys
            available = group[group["mortality_followup_available"] == 1]
            deaths = int(available["death_event"].sum()) if not available.empty else 0
            rows.append(
                {
                    "analysis_set": analysis_set,
                    "analysis_tier": analysis_tier,
                    "cohort": cohort,
                    "group_type": group_type,
                    "group_value": str(group_value),
                    "baseline_n": int(len(group)),
                    "mortality_followup_available_n": int(len(available)),
                    "mortality_followup_available_pct": safe_pct(len(available), len(group)),
                    "death_n": deaths,
                    "death_pct": safe_pct(deaths, len(available)),
                    "median_followup_time_years": round(float(available["followup_time_years"].median()), 2)
                    if not available.empty
                    else np.nan,
                    "max_followup_time_years": round(float(available["followup_time_years"].max()), 2)
                    if not available.empty
                    else np.nan,
                }
            )
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


def write_report(path: Path, inventory: pd.DataFrame, summary: pd.DataFrame) -> None:
    overall = summary[summary["group_type"] == "overall"].copy()
    columns = [
        "analysis_set",
        "cohort",
        "baseline_n",
        "mortality_followup_available_n",
        "mortality_followup_available_pct",
        "death_n",
        "death_pct",
        "median_followup_time_years",
        "max_followup_time_years",
    ]
    lines = [
        "# Phase 6 Mortality Screen",
        "",
        "Mortality was derived from cleaned CSV variables whose Working_data DTA labels identify `radyear`, `radmonth`, and `iwstat` as death-year, death-month, or death-status fields.",
        "",
        "## Mortality Variables",
        "",
    ]
    variable_cols = ["cohort", "variable", "label_from_working_dta", "role", "usable_for_mortality_screen"]
    lines.extend(markdown_table(inventory, variable_cols))
    lines.extend(["", "## Mortality Follow-Up Summary", ""])
    lines.extend(markdown_table(overall, columns))
    lines.extend(
        [
            "",
            "## Interpretation Guardrails",
            "",
            "- `radyear` and `radmonth` are now treated as direct mortality candidates after DTA-label confirmation.",
            "- `iwstat` was mostly zero in the cleaned Working_data files and should be used as a supporting status field, not the only death indicator.",
            "- Survival models should use `followup_time_years` and `death_event`, not a simple death-ever logistic model, because follow-up time differs by cohort.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", required=True, type=Path)
    parser.add_argument("--database-root", required=True, type=Path)
    parser.add_argument("--assignments", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    assignments = read_assignments(args.assignments)
    inventory = build_variable_inventory(args.data_root, args.database_root)
    frames = [read_cohort_mortality_frame(args.data_root, cohort) for cohort in COHORT_CONFIG]
    long_frame = pd.concat(frames, ignore_index=True)
    person_mortality = summarize_person_mortality(long_frame)
    screen = build_mortality_screen(assignments, long_frame, person_mortality)
    summary = summarize_groups(screen)

    inventory.to_csv(args.output_dir / "phase6_mortality_variable_inventory.csv", index=False, encoding="utf-8-sig")
    screen.to_csv(args.output_dir / "phase6_mortality_participant_screen.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(args.output_dir / "phase6_mortality_summary.csv", index=False, encoding="utf-8-sig")
    write_report(args.output_dir / "phase6_mortality_screen_report.md", inventory, summary)


if __name__ == "__main__":
    main()
