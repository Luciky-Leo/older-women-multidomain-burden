from __future__ import annotations

import argparse
import math
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.duration.hazard_regression import PHReg


FORMULA_RHS = "C(endotype_class, Treatment(reference='1')) + age"


def safe_exp(value: float) -> float:
    if pd.isna(value):
        return np.nan
    if value > 700:
        return math.inf
    if value < -700:
        return 0.0
    return float(math.exp(value))


def clean_term(term: str) -> str:
    if term == "age":
        return "age"
    marker = "[T."
    if marker in term:
        return term.split(marker, 1)[1].rstrip("]")
    return term


def read_screen(path: Path) -> pd.DataFrame:
    screen = pd.read_csv(path, dtype={"participant_id": str}, low_memory=False)
    for column in ["age", "followup_time_years", "death_event", "mortality_followup_available"]:
        screen[column] = pd.to_numeric(screen[column], errors="coerce")
    screen["endotype_class"] = screen["endotype_class"].astype(str)
    return screen


def base_frame(screen: pd.DataFrame) -> pd.DataFrame:
    keep = [
        "analysis_set",
        "analysis_tier",
        "cohort",
        "participant_id",
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


def period_frames(data: pd.DataFrame, cutpoint: float) -> list[tuple[str, pd.DataFrame]]:
    full = data.copy()
    full["period"] = "full_followup"
    full["period_time_years"] = full["followup_time_years"]
    full["period_death_event"] = full["death_event"]

    early = data.copy()
    early["period"] = "early"
    early["period_time_years"] = np.minimum(early["followup_time_years"], cutpoint)
    early["period_death_event"] = (
        (early["death_event"] == 1) & (early["followup_time_years"] <= cutpoint)
    ).astype(int)
    early = early[early["period_time_years"] > 0].copy()

    late = data[data["followup_time_years"] > cutpoint].copy()
    late["period"] = "late"
    late["period_time_years"] = late["followup_time_years"] - cutpoint
    late["period_death_event"] = (
        (late["death_event"] == 1) & (late["followup_time_years"] > cutpoint)
    ).astype(int)
    late = late[late["period_time_years"] > 0].copy()
    return [("full_followup", full), ("early", early), ("late", late)]


def fit_cox(data: pd.DataFrame):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return PHReg.from_formula(
            f"period_time_years ~ {FORMULA_RHS}",
            status=data["period_death_event"],
            data=data,
        ).fit(disp=0)


def summarize_fit(result, data: pd.DataFrame, cutpoint: float) -> tuple[dict[str, object], pd.DataFrame]:
    params = np.asarray(result.params)
    conf = np.asarray(result.conf_int())
    pvalues = np.asarray(result.pvalues)
    names = result.model.exog_names
    n = len(data)
    events = int(data["period_death_event"].sum())
    k = len(params)
    partial_aic = -2.0 * float(result.llf) + 2.0 * k
    metrics = {
        "analysis_set": data["analysis_set"].iloc[0],
        "analysis_tier": data["analysis_tier"].iloc[0],
        "cohort": data["cohort"].iloc[0],
        "period": data["period"].iloc[0],
        "cutpoint_years": round(float(cutpoint), 4),
        "n": n,
        "events": events,
        "event_pct": round(events / n * 100, 2) if n else np.nan,
        "median_period_time_years": round(float(data["period_time_years"].median()), 4),
        "max_period_time_years": round(float(data["period_time_years"].max()), 4),
        "log_likelihood": round(float(result.llf), 6),
        "partial_aic": round(float(partial_aic), 3),
    }
    rows = []
    for idx, term in enumerate(names):
        lower, upper = conf[idx]
        rows.append(
            {
                **{key: metrics[key] for key in ["analysis_set", "analysis_tier", "cohort", "period", "cutpoint_years"]},
                "term": term,
                "term_label": clean_term(term),
                "n": n,
                "events": events,
                "log_hr": round(float(params[idx]), 6),
                "hr": round(safe_exp(float(params[idx])), 4),
                "ci_low": round(safe_exp(float(lower)), 4),
                "ci_high": round(safe_exp(float(upper)), 4),
                "p_value": round(float(pvalues[idx]), 6),
            }
        )
    return metrics, pd.DataFrame(rows)


def run_models(screen: pd.DataFrame, min_events: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    metric_rows = []
    term_frames = []
    skipped_rows = []
    for _, cohort_frame in screen.groupby(["analysis_set", "analysis_tier", "cohort"], dropna=False):
        data = base_frame(cohort_frame)
        if data.empty or data["death_event"].sum() < min_events:
            skipped_rows.append(
                {
                    "analysis_set": cohort_frame["analysis_set"].iloc[0],
                    "analysis_tier": cohort_frame["analysis_tier"].iloc[0],
                    "cohort": cohort_frame["cohort"].iloc[0],
                    "period": "all",
                    "n": int(len(data)),
                    "events": int(data["death_event"].sum()) if not data.empty else 0,
                    "skip_reason": "no_available_rows_or_too_few_deaths",
                }
            )
            continue
        cutpoint = float(data.loc[data["death_event"] == 1, "followup_time_years"].median())
        for period, period_data in period_frames(data, cutpoint):
            period_events = int(period_data["period_death_event"].sum()) if not period_data.empty else 0
            skip_reason = ""
            if period_data.empty:
                skip_reason = "no_period_rows"
            elif period_events < min_events:
                skip_reason = "too_few_period_deaths"
            elif period_data["endotype_class"].nunique() < 2:
                skip_reason = "less_than_two_endotype_classes"
            if skip_reason:
                skipped_rows.append(
                    {
                        "analysis_set": cohort_frame["analysis_set"].iloc[0],
                        "analysis_tier": cohort_frame["analysis_tier"].iloc[0],
                        "cohort": cohort_frame["cohort"].iloc[0],
                        "period": period,
                        "n": int(len(period_data)),
                        "events": period_events,
                        "skip_reason": skip_reason,
                    }
                )
                continue
            try:
                result = fit_cox(period_data)
                metrics, terms = summarize_fit(result, period_data, cutpoint)
                metric_rows.append(metrics)
                term_frames.append(terms)
            except Exception as exc:  # pragma: no cover - diagnostic path
                skipped_rows.append(
                    {
                        "analysis_set": cohort_frame["analysis_set"].iloc[0],
                        "analysis_tier": cohort_frame["analysis_tier"].iloc[0],
                        "cohort": cohort_frame["cohort"].iloc[0],
                        "period": period,
                        "n": int(len(period_data)),
                        "events": period_events,
                        "skip_reason": f"fit_failed: {type(exc).__name__}: {exc}",
                    }
                )
    metrics = pd.DataFrame(metric_rows)
    terms = pd.concat(term_frames, ignore_index=True) if term_frames else pd.DataFrame()
    skipped = pd.DataFrame(skipped_rows)
    return metrics, terms, skipped


def build_stability_table(terms: pd.DataFrame) -> pd.DataFrame:
    if terms.empty:
        return pd.DataFrame()
    effects = terms[(terms["term_label"] != "age")].copy()
    wide = effects.pivot_table(
        index=["analysis_set", "analysis_tier", "cohort", "term_label"],
        columns="period",
        values=["hr", "ci_low", "ci_high", "log_hr"],
        aggfunc="first",
    )
    wide.columns = [f"{metric}_{period}" for metric, period in wide.columns]
    wide = wide.reset_index()
    if "log_hr_early" in wide.columns and "log_hr_late" in wide.columns:
        wide["late_minus_early_log_hr"] = wide["log_hr_late"] - wide["log_hr_early"]
        wide["late_vs_early_hr_ratio"] = np.exp(wide["late_minus_early_log_hr"])
    if "hr_early" in wide.columns and "hr_late" in wide.columns:
        wide["direction_change"] = (
            ((wide["hr_early"] > 1) & (wide["hr_late"] < 1))
            | ((wide["hr_early"] < 1) & (wide["hr_late"] > 1))
        ).astype(int)
        wide["large_time_drift"] = (
            (wide.get("late_vs_early_hr_ratio", pd.Series(np.nan, index=wide.index)) >= 1.5)
            | (wide.get("late_vs_early_hr_ratio", pd.Series(np.nan, index=wide.index)) <= (1 / 1.5))
        ).astype(int)
    return wide.sort_values(["analysis_set", "cohort", "term_label"])


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
                values.append(str(round(value, 4)))
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return lines


def write_report(path: Path, metrics: pd.DataFrame, stability: pd.DataFrame, skipped: pd.DataFrame) -> None:
    metric_cols = ["analysis_set", "cohort", "period", "cutpoint_years", "n", "events", "event_pct", "median_period_time_years"]
    stability_cols = [
        "analysis_set",
        "cohort",
        "term_label",
        "hr_full_followup",
        "hr_early",
        "hr_late",
        "late_vs_early_hr_ratio",
        "direction_change",
        "large_time_drift",
    ]
    stability_cols = [col for col in stability_cols if col in stability.columns]
    flagged = stability[
        (stability.get("direction_change", pd.Series(0, index=stability.index)) == 1)
        | (stability.get("large_time_drift", pd.Series(0, index=stability.index)) == 1)
    ].copy()
    lines = [
        "# Phase 9 Mortality Piecewise Cox Sensitivity",
        "",
        "This sensitivity splits each cohort at its median observed death time.",
        "Early models censor at the cutpoint; late models condition on being followed beyond the cutpoint and reset time from that point.",
        "This is a pragmatic PH-sensitivity screen, not a full time-varying-coefficient model.",
        "",
        "## Period Model Sizes",
        "",
    ]
    lines.extend(markdown_table(metrics, metric_cols))
    lines.extend(["", "## Endotype HR Stability", ""])
    lines.extend(markdown_table(stability, stability_cols))
    lines.extend(["", "## Drift Flags", ""])
    lines.extend(markdown_table(flagged, stability_cols))
    if not skipped.empty:
        lines.extend(["", "## Skipped Fits", ""])
        lines.extend(markdown_table(skipped, ["analysis_set", "cohort", "period", "n", "events", "skip_reason"]))
    lines.extend(
        [
            "",
            "## Interpretation Guardrails",
            "",
            "- Direction changes or HR ratios >= 1.5 / <= 0.67 indicate unstable mortality HRs across follow-up periods.",
            "- For flagged cohort-class terms, mortality should be reported as secondary or with explicit time-period sensitivity.",
            "- Functional deterioration remains the cleaner first validation endpoint because it does not depend on PH assumptions.",
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
    metrics, terms, skipped = run_models(screen, args.min_events)
    stability = build_stability_table(terms)
    metrics.to_csv(args.output_dir / "phase9_mortality_piecewise_metrics.csv", index=False, encoding="utf-8-sig")
    terms.to_csv(args.output_dir / "phase9_mortality_piecewise_terms.csv", index=False, encoding="utf-8-sig")
    stability.to_csv(args.output_dir / "phase9_mortality_piecewise_stability.csv", index=False, encoding="utf-8-sig")
    skipped.to_csv(args.output_dir / "phase9_mortality_piecewise_skipped.csv", index=False, encoding="utf-8-sig")
    write_report(args.output_dir / "phase9_mortality_piecewise_report.md", metrics, stability, skipped)


if __name__ == "__main__":
    main()
