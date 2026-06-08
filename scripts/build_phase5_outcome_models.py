from __future__ import annotations

import argparse
import math
import re
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from sklearn.metrics import roc_auc_score


OUTCOME_SPECS = [
    {
        "outcome": "functional_deterioration_ge_0_5sd",
        "available": "functional_deterioration_available",
        "label": "Functional deterioration >= 0.5 SD",
        "priority": "primary",
    },
    {
        "outcome": "chronic_progression_ge_1_condition",
        "available": "chronic_progression_available",
        "label": "Chronic progression >= 1 condition",
        "priority": "secondary",
    },
]

MODEL_SPECS = [
    {
        "model_type": "endotype",
        "group_var": "endotype_class",
        "reference": "1",
        "formula_group": "C(endotype_class, Treatment(reference='1'))",
    },
    {
        "model_type": "severity_tertile",
        "group_var": "severity_tertile",
        "reference": "low",
        "formula_group": "C(severity_tertile, Treatment(reference='low'))",
    },
]

ADJUSTMENT_SPECS = [
    {"adjustment": "unadjusted", "covariates": []},
    {"adjustment": "age_adjusted", "covariates": ["age"]},
]


def clean_term(term: str) -> str:
    if term == "Intercept":
        return "Intercept"
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
    screen = pd.read_csv(path, dtype={"participant_id": str, "wave": str, "baseline_wave": str}, low_memory=False)
    for column in [
        "age",
        "severity_score",
        "endotype_posterior",
        "functional_deterioration_ge_0_5sd",
        "functional_deterioration_available",
        "chronic_progression_ge_1_condition",
        "chronic_progression_available",
    ]:
        if column in screen.columns:
            screen[column] = pd.to_numeric(screen[column], errors="coerce")
    screen["endotype_class"] = screen["endotype_class"].astype(str)
    screen["severity_tertile"] = screen["severity_tertile"].astype(str)
    return screen


def model_frame(screen: pd.DataFrame, outcome_spec: dict[str, str], model_spec: dict[str, str], covariates: list[str]) -> pd.DataFrame:
    required = [
        "analysis_set",
        "analysis_tier",
        "cohort",
        outcome_spec["outcome"],
        outcome_spec["available"],
        model_spec["group_var"],
        *covariates,
    ]
    data = screen[required].copy()
    data = data[data[outcome_spec["available"]] == 1].copy()
    data = data.dropna(subset=[outcome_spec["outcome"], model_spec["group_var"], *covariates])
    data[outcome_spec["outcome"]] = data[outcome_spec["outcome"]].astype(int)
    return data


def fit_glm(data: pd.DataFrame, outcome: str, formula_group: str, covariates: list[str]):
    rhs = formula_group
    if covariates:
        rhs += " + " + " + ".join(covariates)
    formula = f"{outcome} ~ {rhs}"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return smf.glm(formula=formula, data=data, family=sm.families.Binomial()).fit()


def summarize_fit(
    fit,
    data: pd.DataFrame,
    outcome_spec: dict[str, str],
    model_spec: dict[str, str],
    adjustment: str,
) -> tuple[dict[str, object], pd.DataFrame]:
    outcome = outcome_spec["outcome"]
    predicted = fit.predict(data)
    auc = np.nan
    if data[outcome].nunique() == 2:
        auc = float(roc_auc_score(data[outcome], predicted))
    bic = getattr(fit, "bic_llf", np.nan)
    metrics = {
        "analysis_set": data["analysis_set"].iloc[0],
        "analysis_tier": data["analysis_tier"].iloc[0],
        "cohort": data["cohort"].iloc[0],
        "outcome": outcome,
        "outcome_label": outcome_spec["label"],
        "outcome_priority": outcome_spec["priority"],
        "model_type": model_spec["model_type"],
        "adjustment": adjustment,
        "n": int(len(data)),
        "events": int(data[outcome].sum()),
        "event_pct": round(float(data[outcome].mean()) * 100, 2),
        "aic": round(float(fit.aic), 3),
        "bic_llf": round(float(bic), 3) if not pd.isna(bic) else np.nan,
        "auc": round(float(auc), 4) if not pd.isna(auc) else np.nan,
        "converged": int(bool(getattr(fit, "converged", True))),
        "reference": model_spec["reference"],
    }

    conf = fit.conf_int()
    rows = []
    for term, estimate in fit.params.items():
        lower, upper = conf.loc[term]
        rows.append(
            {
                **{key: metrics[key] for key in ["analysis_set", "analysis_tier", "cohort", "outcome", "outcome_label"]},
                "model_type": model_spec["model_type"],
                "adjustment": adjustment,
                "term": term,
                "term_label": clean_term(term),
                "reference": model_spec["reference"],
                "log_or": round(float(estimate), 6),
                "or": round(safe_exp(float(estimate)), 4),
                "ci_low": round(safe_exp(float(lower)), 4),
                "ci_high": round(safe_exp(float(upper)), 4),
                "p_value": round(float(fit.pvalues[term]), 6),
            }
        )
    return metrics, pd.DataFrame(rows)


def run_models(screen: pd.DataFrame, min_events: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    metric_rows = []
    term_frames = []
    skipped_rows = []
    for outcome_spec in OUTCOME_SPECS:
        for model_spec in MODEL_SPECS:
            for adjustment_spec in ADJUSTMENT_SPECS:
                covariates = adjustment_spec["covariates"]
                for _, cohort_frame in screen.groupby(["analysis_set", "analysis_tier", "cohort"], dropna=False):
                    data = model_frame(screen=cohort_frame, outcome_spec=outcome_spec, model_spec=model_spec, covariates=covariates)
                    skip_reason = ""
                    if data.empty:
                        skip_reason = "no_available_rows"
                    elif data[outcome_spec["outcome"]].sum() < min_events:
                        skip_reason = "too_few_events"
                    elif (len(data) - data[outcome_spec["outcome"]].sum()) < min_events:
                        skip_reason = "too_few_nonevents"
                    elif data[model_spec["group_var"]].nunique() < 2:
                        skip_reason = "group_has_less_than_two_levels"
                    if skip_reason:
                        skipped_rows.append(
                            {
                                "analysis_set": cohort_frame["analysis_set"].iloc[0],
                                "analysis_tier": cohort_frame["analysis_tier"].iloc[0],
                                "cohort": cohort_frame["cohort"].iloc[0],
                                "outcome": outcome_spec["outcome"],
                                "model_type": model_spec["model_type"],
                                "adjustment": adjustment_spec["adjustment"],
                                "n": int(len(data)),
                                "events": int(data[outcome_spec["outcome"]].sum()) if not data.empty else 0,
                                "skip_reason": skip_reason,
                            }
                        )
                        continue
                    try:
                        fit = fit_glm(data, outcome_spec["outcome"], model_spec["formula_group"], covariates)
                        metrics, terms = summarize_fit(
                            fit=fit,
                            data=data,
                            outcome_spec=outcome_spec,
                            model_spec=model_spec,
                            adjustment=adjustment_spec["adjustment"],
                        )
                        metric_rows.append(metrics)
                        term_frames.append(terms)
                    except Exception as exc:  # pragma: no cover - diagnostic output path
                        skipped_rows.append(
                            {
                                "analysis_set": cohort_frame["analysis_set"].iloc[0],
                                "analysis_tier": cohort_frame["analysis_tier"].iloc[0],
                                "cohort": cohort_frame["cohort"].iloc[0],
                                "outcome": outcome_spec["outcome"],
                                "model_type": model_spec["model_type"],
                                "adjustment": adjustment_spec["adjustment"],
                                "n": int(len(data)),
                                "events": int(data[outcome_spec["outcome"]].sum()),
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
    age = metrics[metrics["adjustment"] == "age_adjusted"].copy()
    wide = age.pivot_table(
        index=["analysis_set", "analysis_tier", "cohort", "outcome", "outcome_label", "outcome_priority"],
        columns="model_type",
        values=["n", "events", "event_pct", "aic", "bic_llf", "auc"],
        aggfunc="first",
    )
    wide.columns = [f"{metric}_{model_type}" for metric, model_type in wide.columns]
    wide = wide.reset_index()
    if "aic_severity_tertile" in wide.columns and "aic_endotype" in wide.columns:
        wide["delta_aic_favors_endotype"] = wide["aic_severity_tertile"] - wide["aic_endotype"]
    if "auc_severity_tertile" in wide.columns and "auc_endotype" in wide.columns:
        wide["delta_auc_endotype_minus_severity"] = wide["auc_endotype"] - wide["auc_severity_tertile"]
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
    primary = comparison[comparison["outcome"] == "functional_deterioration_ge_0_5sd"].copy()
    primary_cols = [
        "analysis_set",
        "cohort",
        "events_endotype",
        "event_pct_endotype",
        "aic_endotype",
        "aic_severity_tertile",
        "delta_aic_favors_endotype",
        "auc_endotype",
        "auc_severity_tertile",
        "delta_auc_endotype_minus_severity",
    ]
    secondary = comparison[comparison["outcome"] == "chronic_progression_ge_1_condition"].copy()
    lines = [
        "# Phase 5 Outcome Models",
        "",
        "This first validation pass uses logistic regression by cohort.",
        "The main comparison is age-adjusted endotype class versus age-adjusted severity tertile.",
        "Positive delta AIC means the severity-tertile model has higher AIC, which favors the endotype model.",
        "",
        "## Primary Functional Deterioration",
        "",
    ]
    lines.extend(markdown_table(primary, primary_cols))
    lines.extend(["", "## Secondary Chronic Progression", ""])
    lines.extend(markdown_table(secondary, primary_cols))
    if not skipped.empty:
        lines.extend(["", "## Skipped Fits", ""])
        skip_cols = ["analysis_set", "cohort", "outcome", "model_type", "adjustment", "n", "events", "skip_reason"]
        lines.extend(markdown_table(skipped, skip_cols))
    lines.extend(
        [
            "",
            "## Interpretation Guardrails",
            "",
            "- These are validation screens, not causal models.",
            "- LASI is absent from follow-up models because the current cleaned CSV has no later-wave follow-up.",
            "- Mortality models remain blocked until direct mortality variables are extracted from harmonized or raw mortality sources.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--participant-screen", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--min-events", type=int, default=20)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    screen = read_screen(args.participant_screen)
    metrics, terms, skipped = run_models(screen, args.min_events)
    comparison = build_comparison(metrics)

    metrics.to_csv(args.output_dir / "phase5_outcome_model_metrics.csv", index=False, encoding="utf-8-sig")
    terms.to_csv(args.output_dir / "phase5_outcome_model_terms.csv", index=False, encoding="utf-8-sig")
    comparison.to_csv(args.output_dir / "phase5_outcome_model_comparison.csv", index=False, encoding="utf-8-sig")
    skipped.to_csv(args.output_dir / "phase5_outcome_model_skipped.csv", index=False, encoding="utf-8-sig")
    write_report(args.output_dir / "phase5_outcome_model_report.md", comparison, skipped)


if __name__ == "__main__":
    main()
