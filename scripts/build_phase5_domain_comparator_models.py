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


DOMAIN_COLUMNS = [
    "functional_score",
    "cognitive_score",
    "affective_score",
    "cardiometabolic_chronic_score",
]

OUTCOME_SPECS = [
    {
        "outcome": "functional_deterioration_ge_0_5sd",
        "available": "functional_deterioration_available",
        "label": "Functional deterioration >= 0.5 SD",
        "matched_domain": "functional_score",
        "priority": "primary",
    },
    {
        "outcome": "chronic_progression_ge_1_condition",
        "available": "chronic_progression_available",
        "label": "Chronic progression >= 1 condition",
        "matched_domain": "cardiometabolic_chronic_score",
        "priority": "secondary",
    },
]

MODEL_SPECS = [
    {
        "model_type": "severity_tertile",
        "rhs": "C(severity_tertile, Treatment(reference='low')) + age",
        "description": "Age + severity tertile",
        "main_comparator": 1,
    },
    {
        "model_type": "severity_score",
        "rhs": "severity_score + age",
        "description": "Age + continuous mean severity score",
        "main_comparator": 1,
    },
    {
        "model_type": "matched_domain_score",
        "rhs": "{matched_domain} + age",
        "description": "Age + outcome-matched baseline domain score",
        "main_comparator": 1,
    },
    {
        "model_type": "four_domain_scores",
        "rhs": "functional_score + cognitive_score + affective_score + cardiometabolic_chronic_score + age",
        "description": "Age + all four baseline domain scores",
        "main_comparator": 1,
    },
    {
        "model_type": "endotype",
        "rhs": "C(endotype_class, Treatment(reference='1')) + age",
        "description": "Age + endotype class",
        "main_comparator": 1,
    },
    {
        "model_type": "endotype_plus_matched_domain",
        "rhs": "C(endotype_class, Treatment(reference='1')) + {matched_domain} + age",
        "description": "Age + endotype class + outcome-matched baseline domain score",
        "main_comparator": 0,
    },
    {
        "model_type": "endotype_plus_four_domains",
        "rhs": "C(endotype_class, Treatment(reference='1')) + functional_score + cognitive_score + affective_score + cardiometabolic_chronic_score + age",
        "description": "Age + endotype class + all four baseline domain scores",
        "main_comparator": 0,
    },
]


def safe_exp(value: float) -> float:
    if pd.isna(value):
        return np.nan
    if value > 700:
        return math.inf
    if value < -700:
        return 0.0
    return float(math.exp(value))


def clean_term(term: str) -> str:
    if term == "Intercept":
        return "Intercept"
    match = re.search(r"\[T\.(.+)\]", term)
    if match:
        return match.group(1)
    return term


def read_screen(path: Path) -> pd.DataFrame:
    screen = pd.read_csv(path, dtype={"participant_id": str, "wave": str, "baseline_wave": str}, low_memory=False)
    numeric_columns = [
        "age",
        "severity_score",
        "endotype_posterior",
        *DOMAIN_COLUMNS,
        "functional_deterioration_ge_0_5sd",
        "functional_deterioration_available",
        "chronic_progression_ge_1_condition",
        "chronic_progression_available",
    ]
    for column in numeric_columns:
        if column in screen.columns:
            screen[column] = pd.to_numeric(screen[column], errors="coerce")
    screen["endotype_class"] = screen["endotype_class"].astype(str)
    screen["severity_tertile"] = screen["severity_tertile"].astype(str)
    return screen


def formula_variables(rhs: str) -> list[str]:
    variables = {"age"}
    for column in ["severity_score", "severity_tertile", "endotype_class", *DOMAIN_COLUMNS]:
        if column in rhs:
            variables.add(column)
    return sorted(variables)


def build_model_frame(screen: pd.DataFrame, outcome_spec: dict[str, str], rhs: str) -> pd.DataFrame:
    outcome = outcome_spec["outcome"]
    available = outcome_spec["available"]
    variables = formula_variables(rhs)
    keep = ["analysis_set", "analysis_tier", "cohort", outcome, available, *variables]
    data = screen[keep].copy()
    data = data[data[available] == 1].copy()
    data = data.dropna(subset=[outcome, *variables])
    data[outcome] = data[outcome].astype(int)
    return data


def fit_glm(data: pd.DataFrame, outcome: str, rhs: str):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return smf.glm(formula=f"{outcome} ~ {rhs}", data=data, family=sm.families.Binomial()).fit()


def summarize_fit(
    fit,
    data: pd.DataFrame,
    outcome_spec: dict[str, str],
    model_spec: dict[str, object],
    rhs: str,
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
        "matched_domain": outcome_spec["matched_domain"],
        "model_type": model_spec["model_type"],
        "model_description": model_spec["description"],
        "main_comparator": model_spec["main_comparator"],
        "rhs": rhs,
        "n": int(len(data)),
        "events": int(data[outcome].sum()),
        "event_pct": round(float(data[outcome].mean()) * 100, 2),
        "aic": round(float(fit.aic), 3),
        "bic_llf": round(float(bic), 3) if not pd.isna(bic) else np.nan,
        "auc": round(float(auc), 4) if not pd.isna(auc) else np.nan,
        "converged": int(bool(getattr(fit, "converged", True))),
    }
    conf = fit.conf_int()
    rows = []
    for term, estimate in fit.params.items():
        lower, upper = conf.loc[term]
        rows.append(
            {
                "analysis_set": metrics["analysis_set"],
                "analysis_tier": metrics["analysis_tier"],
                "cohort": metrics["cohort"],
                "outcome": outcome,
                "outcome_label": outcome_spec["label"],
                "model_type": model_spec["model_type"],
                "term": term,
                "term_label": clean_term(term),
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
            rhs = str(model_spec["rhs"]).format(matched_domain=outcome_spec["matched_domain"])
            for _, cohort_frame in screen.groupby(["analysis_set", "analysis_tier", "cohort"], dropna=False):
                data = build_model_frame(cohort_frame, outcome_spec, rhs)
                skip_reason = ""
                if data.empty:
                    skip_reason = "no_available_rows"
                elif data[outcome_spec["outcome"]].sum() < min_events:
                    skip_reason = "too_few_events"
                elif (len(data) - data[outcome_spec["outcome"]].sum()) < min_events:
                    skip_reason = "too_few_nonevents"
                if skip_reason:
                    skipped_rows.append(
                        {
                            "analysis_set": cohort_frame["analysis_set"].iloc[0],
                            "analysis_tier": cohort_frame["analysis_tier"].iloc[0],
                            "cohort": cohort_frame["cohort"].iloc[0],
                            "outcome": outcome_spec["outcome"],
                            "model_type": model_spec["model_type"],
                            "n": int(len(data)),
                            "events": int(data[outcome_spec["outcome"]].sum()) if not data.empty else 0,
                            "skip_reason": skip_reason,
                        }
                    )
                    continue
                try:
                    fit = fit_glm(data, outcome_spec["outcome"], rhs)
                    metrics, terms = summarize_fit(fit, data, outcome_spec, model_spec, rhs)
                    metric_rows.append(metrics)
                    term_frames.append(terms)
                except Exception as exc:  # pragma: no cover - diagnostic path
                    skipped_rows.append(
                        {
                            "analysis_set": cohort_frame["analysis_set"].iloc[0],
                            "analysis_tier": cohort_frame["analysis_tier"].iloc[0],
                            "cohort": cohort_frame["cohort"].iloc[0],
                            "outcome": outcome_spec["outcome"],
                            "model_type": model_spec["model_type"],
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
    wide = metrics.pivot_table(
        index=["analysis_set", "analysis_tier", "cohort", "outcome", "outcome_label", "outcome_priority"],
        columns="model_type",
        values=["n", "events", "event_pct", "aic", "bic_llf", "auc"],
        aggfunc="first",
    )
    wide.columns = [f"{metric}_{model_type}" for metric, model_type in wide.columns]
    wide = wide.reset_index()
    for comparator in ["severity_tertile", "severity_score", "matched_domain_score", "four_domain_scores"]:
        aic_col = f"aic_{comparator}"
        auc_col = f"auc_{comparator}"
        if aic_col in wide.columns and "aic_endotype" in wide.columns:
            wide[f"delta_aic_{comparator}_minus_endotype"] = wide[aic_col] - wide["aic_endotype"]
        if auc_col in wide.columns and "auc_endotype" in wide.columns:
            wide[f"delta_auc_endotype_minus_{comparator}"] = wide["auc_endotype"] - wide[auc_col]
    if "aic_endotype_plus_matched_domain" in wide.columns and "aic_matched_domain_score" in wide.columns:
        wide["delta_aic_matched_domain_minus_endotype_plus_domain"] = (
            wide["aic_matched_domain_score"] - wide["aic_endotype_plus_matched_domain"]
        )
    if "aic_endotype_plus_four_domains" in wide.columns and "aic_four_domain_scores" in wide.columns:
        wide["delta_aic_four_domains_minus_endotype_plus_domains"] = (
            wide["aic_four_domain_scores"] - wide["aic_endotype_plus_four_domains"]
        )
    return wide


def classify_incremental_value(row: pd.Series) -> str:
    delta_four = row.get("delta_aic_four_domain_scores_minus_endotype", np.nan)
    delta_domain_plus = row.get("delta_aic_matched_domain_minus_endotype_plus_domain", np.nan)
    delta_four_plus = row.get("delta_aic_four_domains_minus_endotype_plus_domains", np.nan)
    if pd.notna(delta_four) and delta_four <= -6:
        if pd.notna(delta_four_plus) and delta_four_plus >= 6:
            return "four_domain_scores_beat_endotype_but_endotype_adds_after_four_domains"
        return "four_domain_scores_beat_endotype"
    if pd.notna(delta_four) and delta_four >= 6:
        return "endotype_beats_four_domain_scores"
    if pd.notna(delta_domain_plus) and delta_domain_plus >= 6:
        return "endotype_adds_beyond_matched_domain"
    return "no_clear_incremental_endotype_advantage"


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
    report_frame = comparison.copy()
    if not report_frame.empty:
        report_frame["incremental_value_flag"] = report_frame.apply(classify_incremental_value, axis=1)
    focus_columns = [
        "analysis_set",
        "cohort",
        "events_endotype",
        "event_pct_endotype",
        "aic_endotype",
        "aic_severity_score",
        "aic_matched_domain_score",
        "aic_four_domain_scores",
        "aic_endotype_plus_matched_domain",
        "delta_aic_four_domain_scores_minus_endotype",
        "delta_aic_matched_domain_minus_endotype_plus_domain",
        "delta_aic_four_domains_minus_endotype_plus_domains",
        "auc_endotype",
        "auc_four_domain_scores",
        "incremental_value_flag",
    ]
    available_focus = [column for column in focus_columns if column in report_frame.columns]
    primary = report_frame[report_frame["outcome"] == "functional_deterioration_ge_0_5sd"]
    secondary = report_frame[report_frame["outcome"] == "chronic_progression_ge_1_condition"]
    lines = [
        "# Phase 5 Domain Comparator Models",
        "",
        "This refinement asks whether endotype classes add information beyond simpler baseline domain-score comparators.",
        "Positive delta AIC values favor the endotype-containing model named in the column.",
        "",
        "## Primary Functional Deterioration",
        "",
    ]
    lines.extend(markdown_table(primary, available_focus))
    lines.extend(["", "## Secondary Chronic Progression", ""])
    lines.extend(markdown_table(secondary, available_focus))
    if not skipped.empty:
        lines.extend(["", "## Skipped Fits", ""])
        lines.extend(markdown_table(skipped, ["analysis_set", "cohort", "outcome", "model_type", "n", "events", "skip_reason"]))
    lines.extend(
        [
            "",
            "## Interpretation Guardrails",
            "",
            "- The four-domain-score model is not a manuscript replacement for endotypes; it is a diagnostic comparator for whether classes carry pattern information beyond their source scores.",
            "- Endotype-plus-domain and endotype-plus-four-domain models are overadjustment-style diagnostics because endotypes are derived from the same domain scores.",
            "- A consistent endotype advantage should appear against severity score, outcome-matched domain score, and four-domain-score comparators before making strong prediction claims.",
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
    metrics.to_csv(args.output_dir / "phase5_domain_comparator_metrics.csv", index=False, encoding="utf-8-sig")
    terms.to_csv(args.output_dir / "phase5_domain_comparator_terms.csv", index=False, encoding="utf-8-sig")
    comparison.to_csv(args.output_dir / "phase5_domain_comparator_comparison.csv", index=False, encoding="utf-8-sig")
    skipped.to_csv(args.output_dir / "phase5_domain_comparator_skipped.csv", index=False, encoding="utf-8-sig")
    write_report(args.output_dir / "phase5_domain_comparator_report.md", comparison, skipped)


if __name__ == "__main__":
    main()
