from __future__ import annotations

import argparse
import math
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.duration.hazard_regression import PHReg


PH_P_THRESHOLD = 0.01
PH_ABS_CORR_THRESHOLD = 0.05


def read_screen(path: Path) -> pd.DataFrame:
    screen = pd.read_csv(path, dtype={"participant_id": str}, low_memory=False)
    for column in [
        "age",
        "followup_time_years",
        "death_event",
        "mortality_followup_available",
        "severity_score",
        "functional_score",
        "cognitive_score",
        "affective_score",
        "cardiometabolic_chronic_score",
    ]:
        if column in screen.columns:
            screen[column] = pd.to_numeric(screen[column], errors="coerce")
    screen["endotype_class"] = screen["endotype_class"].astype(str)
    return screen


def model_frame(screen: pd.DataFrame) -> pd.DataFrame:
    keep = [
        "analysis_set",
        "analysis_tier",
        "cohort",
        "followup_time_years",
        "death_event",
        "mortality_followup_available",
        "endotype_class",
        "age",
    ]
    data = screen[keep].copy()
    data = data[data["mortality_followup_available"] == 1].copy()
    data = data.dropna(subset=["followup_time_years", "death_event", "endotype_class", "age"])
    data = data[data["followup_time_years"] > 0].copy()
    data["death_event"] = data["death_event"].astype(int)
    return data


def fit_endotype_cox(data: pd.DataFrame):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return PHReg.from_formula(
            "followup_time_years ~ C(endotype_class, Treatment(reference='1')) + age",
            status=data["death_event"],
            data=data,
        ).fit(disp=0)


def safe_corr(x: np.ndarray, y: np.ndarray) -> tuple[float, float, float, float]:
    if len(x) < 5 or np.nanstd(x) == 0 or np.nanstd(y) == 0:
        return np.nan, np.nan, np.nan, np.nan
    pearson = stats.pearsonr(x, y)
    spearman = stats.spearmanr(x, y)
    return float(pearson.statistic), float(pearson.pvalue), float(spearman.statistic), float(spearman.pvalue)


def diagnose_one(data: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    result = fit_endotype_cox(data)
    residuals = np.asarray(result.schoenfeld_residuals)
    names = result.model.exog_names
    event_mask = ~np.isnan(residuals).all(axis=1)
    event_times = data.loc[event_mask, "followup_time_years"].to_numpy(dtype=float)
    log_time = np.log(event_times)
    rows = []
    for idx, term in enumerate(names):
        values = residuals[event_mask, idx].astype(float)
        ok = ~np.isnan(values) & ~np.isnan(log_time) & np.isfinite(values) & np.isfinite(log_time)
        pearson_r, pearson_p, spearman_r, spearman_p = safe_corr(values[ok], log_time[ok])
        flag = (
            pd.notna(pearson_p)
            and pearson_p < PH_P_THRESHOLD
            and pd.notna(pearson_r)
            and abs(pearson_r) >= PH_ABS_CORR_THRESHOLD
        )
        rows.append(
            {
                "analysis_set": data["analysis_set"].iloc[0],
                "analysis_tier": data["analysis_tier"].iloc[0],
                "cohort": data["cohort"].iloc[0],
                "term": term,
                "n": int(len(data)),
                "events": int(data["death_event"].sum()),
                "event_residual_n": int(ok.sum()),
                "pearson_r_with_log_time": round(pearson_r, 6) if pd.notna(pearson_r) else np.nan,
                "pearson_p": round(pearson_p, 8) if pd.notna(pearson_p) else np.nan,
                "spearman_r_with_log_time": round(spearman_r, 6) if pd.notna(spearman_r) else np.nan,
                "spearman_p": round(spearman_p, 8) if pd.notna(spearman_p) else np.nan,
                "ph_flag": int(flag),
            }
        )
    summary = {
        "analysis_set": data["analysis_set"].iloc[0],
        "analysis_tier": data["analysis_tier"].iloc[0],
        "cohort": data["cohort"].iloc[0],
        "n": int(len(data)),
        "events": int(data["death_event"].sum()),
        "tested_terms": len(rows),
        "flagged_terms": int(sum(row["ph_flag"] for row in rows)),
        "min_pearson_p": min(row["pearson_p"] for row in rows if pd.notna(row["pearson_p"])),
        "max_abs_pearson_r": max(abs(row["pearson_r_with_log_time"]) for row in rows if pd.notna(row["pearson_r_with_log_time"])),
    }
    summary["ph_screen_flag"] = int(summary["flagged_terms"] > 0)
    return pd.DataFrame(rows), summary


def run_diagnostics(screen: pd.DataFrame, min_events: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rows = []
    summaries = []
    skipped = []
    for _, cohort_frame in screen.groupby(["analysis_set", "analysis_tier", "cohort"], dropna=False):
        data = model_frame(cohort_frame)
        skip_reason = ""
        if data.empty:
            skip_reason = "no_available_rows"
        elif data["death_event"].sum() < min_events:
            skip_reason = "too_few_deaths"
        elif data["endotype_class"].nunique() < 2:
            skip_reason = "less_than_two_endotype_classes"
        if skip_reason:
            skipped.append(
                {
                    "analysis_set": cohort_frame["analysis_set"].iloc[0],
                    "analysis_tier": cohort_frame["analysis_tier"].iloc[0],
                    "cohort": cohort_frame["cohort"].iloc[0],
                    "n": int(len(data)),
                    "events": int(data["death_event"].sum()) if not data.empty else 0,
                    "skip_reason": skip_reason,
                }
            )
            continue
        try:
            detail, summary = diagnose_one(data)
            rows.append(detail)
            summaries.append(summary)
        except Exception as exc:  # pragma: no cover - diagnostic path
            skipped.append(
                {
                    "analysis_set": cohort_frame["analysis_set"].iloc[0],
                    "analysis_tier": cohort_frame["analysis_tier"].iloc[0],
                    "cohort": cohort_frame["cohort"].iloc[0],
                    "n": int(len(data)),
                    "events": int(data["death_event"].sum()) if not data.empty else 0,
                    "skip_reason": f"diagnostic_failed: {type(exc).__name__}: {exc}",
                }
            )
    detail_frame = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()
    summary_frame = pd.DataFrame(summaries)
    skipped_frame = pd.DataFrame(skipped)
    return detail_frame, summary_frame, skipped_frame


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
                values.append(str(round(value, 5)))
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return lines


def write_report(path: Path, detail: pd.DataFrame, summary: pd.DataFrame, skipped: pd.DataFrame) -> None:
    lines = [
        "# Phase 8 Mortality PH Diagnostics",
        "",
        "This is a lightweight proportional-hazards screen for the age-adjusted endotype Cox model.",
        "Each model term's Schoenfeld residuals are correlated with log follow-up time.",
        f"A term is flagged when Pearson p < {PH_P_THRESHOLD} and absolute Pearson r >= {PH_ABS_CORR_THRESHOLD}.",
        "",
        "## Cohort Summary",
        "",
    ]
    summary_cols = ["analysis_set", "cohort", "n", "events", "tested_terms", "flagged_terms", "min_pearson_p", "max_abs_pearson_r", "ph_screen_flag"]
    lines.extend(markdown_table(summary, summary_cols))
    flagged = detail[detail["ph_flag"] == 1].copy() if not detail.empty else pd.DataFrame()
    lines.extend(["", "## Flagged Terms", ""])
    flag_cols = ["analysis_set", "cohort", "term", "events", "pearson_r_with_log_time", "pearson_p", "spearman_r_with_log_time", "spearman_p"]
    lines.extend(markdown_table(flagged, flag_cols))
    if not skipped.empty:
        lines.extend(["", "## Skipped Cohorts", ""])
        lines.extend(markdown_table(skipped, ["analysis_set", "cohort", "n", "events", "skip_reason"]))
    lines.extend(
        [
            "",
            "## Interpretation Guardrails",
            "",
            "- This is a screen, not a final PH-assumption proof.",
            "- Large cohorts can produce small p-values for weak time trends; the correlation threshold is included to reduce trivial flags.",
            "- Flagged models should get a time-interaction or stratified sensitivity before manuscript use.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mortality-screen", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--min-events", type=int, default=20)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    screen = read_screen(args.mortality_screen)
    detail, summary, skipped = run_diagnostics(screen, args.min_events)
    detail.to_csv(args.output_dir / "phase8_mortality_ph_diagnostics.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(args.output_dir / "phase8_mortality_ph_diagnostic_summary.csv", index=False, encoding="utf-8-sig")
    skipped.to_csv(args.output_dir / "phase8_mortality_ph_diagnostic_skipped.csv", index=False, encoding="utf-8-sig")
    write_report(args.output_dir / "phase8_mortality_ph_diagnostic_report.md", detail, summary, skipped)


if __name__ == "__main__":
    main()
