from __future__ import annotations

import argparse
import math
import re
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.duration.hazard_regression import PHReg


DOMAIN_COLUMNS = [
    "functional_score",
    "cognitive_score",
    "affective_score",
    "cardiometabolic_chronic_score",
]

MODEL_SPECS = [
    {
        "model_type": "severity_tertile",
        "rhs": "C(severity_tertile, Treatment(reference='low')) + age",
        "description": "Age + severity tertile",
    },
    {
        "model_type": "severity_score",
        "rhs": "severity_score + age",
        "description": "Age + continuous mean severity score",
    },
    {
        "model_type": "four_domain_scores",
        "rhs": "functional_score + cognitive_score + affective_score + cardiometabolic_chronic_score + age",
        "description": "Age + four baseline domain scores",
    },
    {
        "model_type": "endotype",
        "rhs": "C(endotype_class, Treatment(reference='1')) + age",
        "description": "Age + endotype class",
    },
    {
        "model_type": "endotype_plus_four_domains",
        "rhs": "C(endotype_class, Treatment(reference='1')) + functional_score + cognitive_score + affective_score + cardiometabolic_chronic_score + age",
        "description": "Age + endotype class + four baseline domain scores",
    },
]


def clean_term(term: str) -> str:
    match = re.search(r"\[T\.(.+)\]", term)
    if match:
        return match.group(1)
    return term


def safe_exp(value: float) -> float:
    if pd.isna(value):
        return np.nan
    if value > 700:
        return math.inf
    if value < -700:
        return 0.0
    return float(math.exp(value))


def read_screen(path: Path) -> pd.DataFrame:
    screen = pd.read_csv(path, dtype={"participant_id": str}, low_memory=False)
    numeric_columns = [
        "age",
        "severity_score",
        "followup_time_years",
        "death_event",
        "mortality_followup_available",
        *DOMAIN_COLUMNS,
    ]
    for column in numeric_columns:
        if column in screen.columns:
            screen[column] = pd.to_numeric(screen[column], errors="coerce")
    screen["endotype_class"] = screen["endotype_class"].astype(str)
    screen["severity_tertile"] = pd.Categorical(screen["severity_tertile"], categories=["low", "middle", "high"])
    return screen


def formula_variables(rhs: str) -> list[str]:
    variables = {"age"}
    for column in ["severity_score", "severity_tertile", "endotype_class", *DOMAIN_COLUMNS]:
        if column in rhs:
            variables.add(column)
    return sorted(variables)


def build_model_frame(screen: pd.DataFrame, rhs: str) -> pd.DataFrame:
    variables = formula_variables(rhs)
    keep = [
        "analysis_set",
        "analysis_tier",
        "cohort",
        "followup_time_years",
        "death_event",
        "mortality_followup_available",
        *variables,
    ]
    data = screen[keep].copy()
    data = data[data["mortality_followup_available"] == 1].copy()
    data = data.dropna(subset=["followup_time_years", "death_event", *variables])
    data = data[data["followup_time_years"] > 0].copy()
    data["death_event"] = data["death_event"].astype(int)
    return data


def fit_cox(data: pd.DataFrame, rhs: str):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = PHReg.from_formula(f"followup_time_years ~ {rhs}", status=data["death_event"], data=data)
        return model.fit(disp=0)


def summarize_fit(result, data: pd.DataFrame, model_spec: dict[str, str]) -> tuple[dict[str, object], pd.DataFrame]:
    params = np.asarray(result.params)
    conf = np.asarray(result.conf_int())
    pvalues = np.asarray(result.pvalues)
    names = result.model.exog_names
    k = len(params)
    n = len(data)
    events = int(data["death_event"].sum())
    partial_aic = -2.0 * float(result.llf) + 2.0 * k
    partial_bic = -2.0 * float(result.llf) + math.log(max(n, 1)) * k
    metrics = {
        "analysis_set": data["analysis_set"].iloc[0],
        "analysis_tier": data["analysis_tier"].iloc[0],
        "cohort": data["cohort"].iloc[0],
        "outcome": "all_cause_mortality",
        "model_type": model_spec["model_type"],
        "model_description": model_spec["description"],
        "n": n,
        "events": events,
        "event_pct": round(events / n * 100, 2),
        "median_followup_time_years": round(float(data["followup_time_years"].median()), 2),
        "max_followup_time_years": round(float(data["followup_time_years"].max()), 2),
        "log_likelihood": round(float(result.llf), 6),
        "partial_aic": round(partial_aic, 3),
        "partial_bic": round(partial_bic, 3),
    }
    rows = []
    for idx, term in enumerate(names):
        lower, upper = conf[idx]
        rows.append(
            {
                "analysis_set": metrics["analysis_set"],
                "analysis_tier": metrics["analysis_tier"],
                "cohort": metrics["cohort"],
                "outcome": "all_cause_mortality",
                "model_type": model_spec["model_type"],
                "term": term,
                "term_label": clean_term(term),
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
    for model_spec in MODEL_SPECS:
        rhs = model_spec["rhs"]
        for _, cohort_frame in screen.groupby(["analysis_set", "analysis_tier", "cohort"], dropna=False):
            data = build_model_frame(cohort_frame, rhs)
            skip_reason = ""
            if data.empty:
                skip_reason = "no_available_rows"
            elif data["death_event"].sum() < min_events:
                skip_reason = "too_few_deaths"
            elif (len(data) - data["death_event"].sum()) < min_events:
                skip_reason = "too_few_censored"
            if skip_reason:
                skipped_rows.append(
                    {
                        "analysis_set": cohort_frame["analysis_set"].iloc[0],
                        "analysis_tier": cohort_frame["analysis_tier"].iloc[0],
                        "cohort": cohort_frame["cohort"].iloc[0],
                        "model_type": model_spec["model_type"],
                        "n": int(len(data)),
                        "events": int(data["death_event"].sum()) if not data.empty else 0,
                        "skip_reason": skip_reason,
                    }
                )
                continue
            try:
                result = fit_cox(data, rhs)
                metrics, terms = summarize_fit(result, data, model_spec)
                metric_rows.append(metrics)
                term_frames.append(terms)
            except Exception as exc:  # pragma: no cover - diagnostic path
                skipped_rows.append(
                    {
                        "analysis_set": cohort_frame["analysis_set"].iloc[0],
                        "analysis_tier": cohort_frame["analysis_tier"].iloc[0],
                        "cohort": cohort_frame["cohort"].iloc[0],
                        "model_type": model_spec["model_type"],
                        "n": int(len(data)),
                        "events": int(data["death_event"].sum()) if not data.empty else 0,
                        "skip_reason": f"fit_failed: {type(exc).__name__}: {exc}",
                    }
                )
    metrics = pd.DataFrame(metric_rows)
    terms = pd.concat(term_frames, ignore_index=True) if term_frames else pd.DataFrame()
    skipped = pd.DataFrame(skipped_rows)
    return metrics, terms, skipped


def build_comparison(metrics: pd.DataFrame) -> pd.DataFrame:
    if metrics.empty:
        return pd.DataFrame()
    wide = metrics.pivot_table(
        index=["analysis_set", "analysis_tier", "cohort", "outcome"],
        columns="model_type",
        values=["n", "events", "event_pct", "partial_aic", "partial_bic", "median_followup_time_years"],
        aggfunc="first",
    )
    wide.columns = [f"{metric}_{model_type}" for metric, model_type in wide.columns]
    wide = wide.reset_index()
    for comparator in ["severity_tertile", "severity_score", "four_domain_scores"]:
        comparator_col = f"partial_aic_{comparator}"
        if comparator_col in wide.columns and "partial_aic_endotype" in wide.columns:
            wide[f"delta_partial_aic_{comparator}_minus_endotype"] = wide[comparator_col] - wide["partial_aic_endotype"]
    if "partial_aic_endotype_plus_four_domains" in wide.columns and "partial_aic_four_domain_scores" in wide.columns:
        wide["delta_partial_aic_four_domains_minus_endotype_plus_domains"] = (
            wide["partial_aic_four_domain_scores"] - wide["partial_aic_endotype_plus_four_domains"]
        )
    return wide


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


def write_report(path: Path, comparison: pd.DataFrame, skipped: pd.DataFrame) -> None:
    columns = [
        "analysis_set",
        "cohort",
        "events_endotype",
        "event_pct_endotype",
        "median_followup_time_years_endotype",
        "partial_aic_endotype",
        "partial_aic_severity_tertile",
        "partial_aic_severity_score",
        "partial_aic_four_domain_scores",
        "delta_partial_aic_severity_tertile_minus_endotype",
        "delta_partial_aic_severity_score_minus_endotype",
        "delta_partial_aic_four_domain_scores_minus_endotype",
        "delta_partial_aic_four_domains_minus_endotype_plus_domains",
    ]
    available_columns = [column for column in columns if column in comparison.columns]
    lines = [
        "# Phase 6 Mortality Cox Models",
        "",
        "This is a first-pass Cox proportional hazards screen for all-cause mortality.",
        "Positive delta partial AIC values favor endotype over the named comparator.",
        "",
        "## Model Comparison",
        "",
    ]
    lines.extend(markdown_table(comparison, available_columns))
    if not skipped.empty:
        lines.extend(["", "## Skipped Fits", ""])
        lines.extend(markdown_table(skipped, ["analysis_set", "cohort", "model_type", "n", "events", "skip_reason"]))
    lines.extend(
        [
            "",
            "## Interpretation Guardrails",
            "",
            "- These models use derived death year/month from cleaned files after DTA-label confirmation.",
            "- Partial AIC is based on Cox partial likelihood and should be interpreted within cohort and endpoint only.",
            "- Proportional hazards assumptions and mortality coding should be checked before manuscript use.",
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
    comparison = build_comparison(metrics)
    metrics.to_csv(args.output_dir / "phase6_mortality_model_metrics.csv", index=False, encoding="utf-8-sig")
    terms.to_csv(args.output_dir / "phase6_mortality_model_terms.csv", index=False, encoding="utf-8-sig")
    comparison.to_csv(args.output_dir / "phase6_mortality_model_comparison.csv", index=False, encoding="utf-8-sig")
    skipped.to_csv(args.output_dir / "phase6_mortality_model_skipped.csv", index=False, encoding="utf-8-sig")
    write_report(args.output_dir / "phase6_mortality_model_report.md", comparison, skipped)


if __name__ == "__main__":
    main()
