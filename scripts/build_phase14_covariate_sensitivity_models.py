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
from statsmodels.duration.hazard_regression import PHReg


FUNCTIONAL_OUTCOME = {
    "outcome": "functional_deterioration_ge_0_5sd",
    "available": "functional_deterioration_available",
    "label": "Functional deterioration >= 0.5 SD",
    "priority": "primary",
}

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

CATEGORICAL_COVARIATES = [
    "cov_education_raw",
    "cov_marital_status_raw",
    "cov_smoking_raw",
    "cov_drinking_raw",
    "cov_rural_region_raw",
    "cov_physical_activity_raw",
]

ADJUSTMENT_SPECS = [
    {
        "adjustment": "minimal_core",
        "description": "Age + education + marital status + smoking + drinking",
        "readiness_column": "minimal_core_ready",
        "categorical": ["cov_education_raw", "cov_marital_status_raw", "cov_smoking_raw", "cov_drinking_raw"],
        "numeric": [],
    },
    {
        "adjustment": "expanded_core",
        "description": "Minimal core + rural/region + physical activity",
        "readiness_column": "expanded_core_ready",
        "categorical": [
            "cov_education_raw",
            "cov_marital_status_raw",
            "cov_smoking_raw",
            "cov_drinking_raw",
            "cov_rural_region_raw",
            "cov_physical_activity_raw",
        ],
        "numeric": [],
    },
    {
        "adjustment": "minimal_plus_bmi",
        "description": "Minimal core + BMI",
        "readiness_column": "optional_bmi_ready",
        "categorical": ["cov_education_raw", "cov_marital_status_raw", "cov_smoking_raw", "cov_drinking_raw"],
        "numeric": ["cov_bmi"],
    },
]

KEYS = ["analysis_set", "analysis_tier", "cohort", "participant_id", "wave"]


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


def normalize_wave(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]
    return text


def read_covariates(path: Path) -> pd.DataFrame:
    covariates = pd.read_csv(path, dtype={"participant_id": str, "wave": str}, low_memory=False)
    covariates["wave"] = covariates["wave"].map(normalize_wave)
    covariates = covariates.drop_duplicates(KEYS)
    for column in CATEGORICAL_COVARIATES:
        if column in covariates.columns:
            covariates[column] = covariates[column].astype("string").str.strip()
            covariates[column] = covariates[column].mask(covariates[column].isin(["", "nan", "NaN", "<NA>"]))
    covariates["cov_bmi"] = pd.to_numeric(covariates.get("cov_bmi_raw"), errors="coerce")
    covariates["cov_bmi"] = covariates["cov_bmi"].where((covariates["cov_bmi"] >= 10) & (covariates["cov_bmi"] <= 80))
    keep = [*KEYS, *CATEGORICAL_COVARIATES, "cov_bmi"]
    return covariates[[column for column in keep if column in covariates.columns]]


def read_functional_screen(path: Path, covariates: pd.DataFrame) -> pd.DataFrame:
    screen = pd.read_csv(path, dtype={"participant_id": str, "wave": str, "baseline_wave": str}, low_memory=False)
    screen["wave"] = screen["wave"].map(normalize_wave)
    for column in [
        "age",
        "severity_score",
        "functional_deterioration_ge_0_5sd",
        "functional_deterioration_available",
        "endotype_posterior",
    ]:
        if column in screen.columns:
            screen[column] = pd.to_numeric(screen[column], errors="coerce")
    screen["endotype_class"] = screen["endotype_class"].astype(str)
    screen["severity_tertile"] = pd.Categorical(screen["severity_tertile"].astype(str), categories=["low", "middle", "high"])
    return screen.merge(covariates, on=KEYS, how="left")


def read_mortality_screen(path: Path, covariates: pd.DataFrame) -> pd.DataFrame:
    screen = pd.read_csv(path, dtype={"participant_id": str, "wave": str}, low_memory=False)
    screen["wave"] = screen["wave"].map(normalize_wave)
    for column in [
        "age",
        "followup_time_years",
        "death_event",
        "mortality_followup_available",
        "severity_score",
        "endotype_posterior",
    ]:
        if column in screen.columns:
            screen[column] = pd.to_numeric(screen[column], errors="coerce")
    screen["endotype_class"] = screen["endotype_class"].astype(str)
    screen["severity_tertile"] = pd.Categorical(screen["severity_tertile"].astype(str), categories=["low", "middle", "high"])
    return screen.merge(covariates, on=KEYS, how="left")


def readiness_lookup(path: Path) -> dict[str, dict[str, int]]:
    summary = pd.read_csv(path, low_memory=False)
    out: dict[str, dict[str, int]] = {}
    for _, row in summary.iterrows():
        out[row["cohort"]] = {
            "minimal_core_ready": int(row.get("minimal_core_ready", 0)),
            "expanded_core_ready": int(row.get("expanded_core_ready", 0)),
            "optional_bmi_ready": int(row.get("optional_bmi_ready", 0)),
        }
    return out


def collapse_rare_categories(data: pd.DataFrame, columns: list[str], min_count: int = 20) -> pd.DataFrame:
    out = data.copy()
    for column in columns:
        if column not in out.columns:
            continue
        text = out[column].astype("string").str.strip()
        counts = text.value_counts(dropna=True)
        rare = set(counts[counts < min_count].index.astype(str))
        out[column] = text.map(lambda value: "rare_or_sparse" if pd.notna(value) and str(value) in rare else value)
    return out


def covariate_terms(adjustment_spec: dict[str, object]) -> list[str]:
    categorical = [f"C({column})" for column in adjustment_spec["categorical"]]  # type: ignore[index]
    numeric = list(adjustment_spec["numeric"])  # type: ignore[index]
    return ["age", *categorical, *numeric]


def logistic_model_frame(
    screen: pd.DataFrame,
    model_spec: dict[str, str],
    adjustment_spec: dict[str, object],
) -> pd.DataFrame:
    outcome = FUNCTIONAL_OUTCOME["outcome"]
    available = FUNCTIONAL_OUTCOME["available"]
    categorical = list(adjustment_spec["categorical"])  # type: ignore[index]
    numeric = list(adjustment_spec["numeric"])  # type: ignore[index]
    required = [
        "analysis_set",
        "analysis_tier",
        "cohort",
        outcome,
        available,
        model_spec["group_var"],
        "age",
        *categorical,
        *numeric,
    ]
    data = screen[[column for column in required if column in screen.columns]].copy()
    data = data[data[available] == 1].copy()
    data = data.dropna(subset=[outcome, model_spec["group_var"], "age", *categorical, *numeric])
    data = collapse_rare_categories(data, categorical)
    data[outcome] = data[outcome].astype(int)
    return data


def fit_logistic(data: pd.DataFrame, model_spec: dict[str, str], adjustment_spec: dict[str, object]):
    rhs = model_spec["formula_group"] + " + " + " + ".join(covariate_terms(adjustment_spec))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return smf.glm(formula=f"{FUNCTIONAL_OUTCOME['outcome']} ~ {rhs}", data=data, family=sm.families.Binomial()).fit()


def summarize_logistic_fit(
    fit,
    data: pd.DataFrame,
    model_spec: dict[str, str],
    adjustment_spec: dict[str, object],
) -> tuple[dict[str, object], pd.DataFrame]:
    outcome = FUNCTIONAL_OUTCOME["outcome"]
    predicted = fit.predict(data)
    auc = np.nan
    if data[outcome].nunique() == 2:
        auc = float(roc_auc_score(data[outcome], predicted))
    bic = getattr(fit, "bic_llf", np.nan)
    if not np.isfinite(float(fit.aic)):
        raise ValueError("nonfinite_aic")
    metrics = {
        "analysis_set": data["analysis_set"].iloc[0],
        "analysis_tier": data["analysis_tier"].iloc[0],
        "cohort": data["cohort"].iloc[0],
        "outcome": outcome,
        "outcome_label": FUNCTIONAL_OUTCOME["label"],
        "outcome_priority": FUNCTIONAL_OUTCOME["priority"],
        "model_type": model_spec["model_type"],
        "adjustment": adjustment_spec["adjustment"],
        "adjustment_description": adjustment_spec["description"],
        "n": int(len(data)),
        "events": int(data[outcome].sum()),
        "event_pct": round(float(data[outcome].mean()) * 100, 2),
        "aic": round(float(fit.aic), 3),
        "bic_llf": round(float(bic), 3) if not pd.isna(bic) else np.nan,
        "auc": round(float(auc), 4) if not pd.isna(auc) else np.nan,
        "converged": int(bool(getattr(fit, "converged", True))),
        "reference": model_spec["reference"],
        "covariates": ";".join(["age", *adjustment_spec["categorical"], *adjustment_spec["numeric"]]),  # type: ignore[index]
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
                "outcome_label": FUNCTIONAL_OUTCOME["label"],
                "model_type": model_spec["model_type"],
                "adjustment": adjustment_spec["adjustment"],
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


def cox_model_frame(
    screen: pd.DataFrame,
    model_spec: dict[str, str],
    adjustment_spec: dict[str, object],
) -> pd.DataFrame:
    categorical = list(adjustment_spec["categorical"])  # type: ignore[index]
    numeric = list(adjustment_spec["numeric"])  # type: ignore[index]
    required = [
        "analysis_set",
        "analysis_tier",
        "cohort",
        "followup_time_years",
        "death_event",
        "mortality_followup_available",
        model_spec["group_var"],
        "age",
        *categorical,
        *numeric,
    ]
    data = screen[[column for column in required if column in screen.columns]].copy()
    data = data[data["mortality_followup_available"] == 1].copy()
    data = data.dropna(subset=["followup_time_years", "death_event", model_spec["group_var"], "age", *categorical, *numeric])
    data = data[data["followup_time_years"] > 0].copy()
    data = collapse_rare_categories(data, categorical)
    data["death_event"] = data["death_event"].astype(int)
    return data


def fit_cox(data: pd.DataFrame, model_spec: dict[str, str], adjustment_spec: dict[str, object]):
    rhs = model_spec["formula_group"] + " + " + " + ".join(covariate_terms(adjustment_spec))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = PHReg.from_formula(f"followup_time_years ~ {rhs}", status=data["death_event"], data=data)
        return model.fit(disp=0)


def summarize_cox_fit(
    result,
    data: pd.DataFrame,
    model_spec: dict[str, str],
    adjustment_spec: dict[str, object],
) -> tuple[dict[str, object], pd.DataFrame]:
    params = np.asarray(result.params)
    conf = np.asarray(result.conf_int())
    pvalues = np.asarray(result.pvalues)
    names = result.model.exog_names
    k = len(params)
    n = len(data)
    events = int(data["death_event"].sum())
    if not np.isfinite(float(result.llf)) or not np.isfinite(params).all():
        raise ValueError("nonfinite_cox_result")
    partial_aic = -2.0 * float(result.llf) + 2.0 * k
    partial_bic = -2.0 * float(result.llf) + math.log(max(n, 1)) * k
    metrics = {
        "analysis_set": data["analysis_set"].iloc[0],
        "analysis_tier": data["analysis_tier"].iloc[0],
        "cohort": data["cohort"].iloc[0],
        "outcome": "all_cause_mortality",
        "outcome_label": "All-cause mortality",
        "model_type": model_spec["model_type"],
        "adjustment": adjustment_spec["adjustment"],
        "adjustment_description": adjustment_spec["description"],
        "n": n,
        "events": events,
        "event_pct": round(events / n * 100, 2),
        "median_followup_time_years": round(float(data["followup_time_years"].median()), 2),
        "max_followup_time_years": round(float(data["followup_time_years"].max()), 2),
        "log_likelihood": round(float(result.llf), 6),
        "partial_aic": round(partial_aic, 3),
        "partial_bic": round(partial_bic, 3),
        "reference": model_spec["reference"],
        "covariates": ";".join(["age", *adjustment_spec["categorical"], *adjustment_spec["numeric"]]),  # type: ignore[index]
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
                "outcome_label": "All-cause mortality",
                "model_type": model_spec["model_type"],
                "adjustment": adjustment_spec["adjustment"],
                "term": term,
                "term_label": clean_term(term),
                "reference": model_spec["reference"],
                "log_hr": round(float(params[idx]), 6),
                "hr": round(safe_exp(float(params[idx])), 4),
                "ci_low": round(safe_exp(float(lower)), 4),
                "ci_high": round(safe_exp(float(upper)), 4),
                "p_value": round(float(pvalues[idx]), 6),
            }
        )
    return metrics, pd.DataFrame(rows)


def run_logistic_models(
    screen: pd.DataFrame,
    readiness: dict[str, dict[str, int]],
    min_events: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    metric_rows = []
    term_frames = []
    skipped_rows = []
    for model_spec in MODEL_SPECS:
        for adjustment_spec in ADJUSTMENT_SPECS:
            for _, cohort_frame in screen.groupby(["analysis_set", "analysis_tier", "cohort"], dropna=False):
                cohort = cohort_frame["cohort"].iloc[0]
                readiness_column = str(adjustment_spec["readiness_column"])
                if readiness.get(cohort, {}).get(readiness_column, 0) != 1:
                    skipped_rows.append(skip_row(cohort_frame, "functional", model_spec, adjustment_spec, 0, 0, "covariate_set_not_ready"))
                    continue
                data = logistic_model_frame(cohort_frame, model_spec, adjustment_spec)
                reason = check_binary_model_data(data, FUNCTIONAL_OUTCOME["outcome"], model_spec["group_var"], min_events)
                if reason:
                    skipped_rows.append(
                        skip_row(cohort_frame, "functional", model_spec, adjustment_spec, len(data), int(data[FUNCTIONAL_OUTCOME["outcome"]].sum()) if not data.empty else 0, reason)
                    )
                    continue
                try:
                    fit = fit_logistic(data, model_spec, adjustment_spec)
                    metrics, terms = summarize_logistic_fit(fit, data, model_spec, adjustment_spec)
                    metric_rows.append(metrics)
                    term_frames.append(terms)
                except Exception as exc:  # pragma: no cover
                    skipped_rows.append(
                        skip_row(
                            cohort_frame,
                            "functional",
                            model_spec,
                            adjustment_spec,
                            len(data),
                            int(data[FUNCTIONAL_OUTCOME["outcome"]].sum()),
                            f"fit_failed: {type(exc).__name__}: {exc}",
                        )
                    )
    return frames(metric_rows, term_frames, skipped_rows)


def run_cox_models(
    screen: pd.DataFrame,
    readiness: dict[str, dict[str, int]],
    min_events: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    metric_rows = []
    term_frames = []
    skipped_rows = []
    for model_spec in MODEL_SPECS:
        for adjustment_spec in ADJUSTMENT_SPECS:
            for _, cohort_frame in screen.groupby(["analysis_set", "analysis_tier", "cohort"], dropna=False):
                cohort = cohort_frame["cohort"].iloc[0]
                readiness_column = str(adjustment_spec["readiness_column"])
                if readiness.get(cohort, {}).get(readiness_column, 0) != 1:
                    skipped_rows.append(skip_row(cohort_frame, "mortality", model_spec, adjustment_spec, 0, 0, "covariate_set_not_ready"))
                    continue
                data = cox_model_frame(cohort_frame, model_spec, adjustment_spec)
                reason = check_binary_model_data(data, "death_event", model_spec["group_var"], min_events)
                if not reason and not data.empty and (data["followup_time_years"] <= 0).any():
                    reason = "invalid_followup_time"
                if reason:
                    skipped_rows.append(
                        skip_row(cohort_frame, "mortality", model_spec, adjustment_spec, len(data), int(data["death_event"].sum()) if not data.empty else 0, reason)
                    )
                    continue
                try:
                    result = fit_cox(data, model_spec, adjustment_spec)
                    metrics, terms = summarize_cox_fit(result, data, model_spec, adjustment_spec)
                    metric_rows.append(metrics)
                    term_frames.append(terms)
                except Exception as exc:  # pragma: no cover
                    skipped_rows.append(
                        skip_row(
                            cohort_frame,
                            "mortality",
                            model_spec,
                            adjustment_spec,
                            len(data),
                            int(data["death_event"].sum()) if not data.empty else 0,
                            f"fit_failed: {type(exc).__name__}: {exc}",
                        )
                    )
    return frames(metric_rows, term_frames, skipped_rows)


def check_binary_model_data(data: pd.DataFrame, outcome: str, group_var: str, min_events: int) -> str:
    if data.empty:
        return "no_available_rows"
    events = int(data[outcome].sum())
    if events < min_events:
        return "too_few_events"
    if (len(data) - events) < min_events:
        return "too_few_nonevents_or_censored"
    if data[group_var].nunique(dropna=True) < 2:
        return "group_has_less_than_two_levels"
    return ""


def skip_row(
    cohort_frame: pd.DataFrame,
    outcome_family: str,
    model_spec: dict[str, str],
    adjustment_spec: dict[str, object],
    n: int,
    events: int,
    reason: str,
) -> dict[str, object]:
    return {
        "analysis_set": cohort_frame["analysis_set"].iloc[0],
        "analysis_tier": cohort_frame["analysis_tier"].iloc[0],
        "cohort": cohort_frame["cohort"].iloc[0],
        "outcome_family": outcome_family,
        "model_type": model_spec["model_type"],
        "adjustment": adjustment_spec["adjustment"],
        "n": n,
        "events": events,
        "skip_reason": reason,
    }


def frames(metric_rows: list[dict[str, object]], term_frames: list[pd.DataFrame], skipped_rows: list[dict[str, object]]):
    metrics = pd.DataFrame(metric_rows)
    terms = pd.concat(term_frames, ignore_index=True) if term_frames else pd.DataFrame()
    skipped = pd.DataFrame(skipped_rows)
    return metrics, terms, skipped


def build_logistic_comparison(metrics: pd.DataFrame) -> pd.DataFrame:
    if metrics.empty:
        return pd.DataFrame()
    wide = metrics.pivot_table(
        index=["analysis_set", "analysis_tier", "cohort", "outcome", "outcome_label", "adjustment"],
        columns="model_type",
        values=["n", "events", "event_pct", "aic", "bic_llf", "auc"],
        aggfunc="first",
    )
    wide.columns = [f"{metric}_{model_type}" for metric, model_type in wide.columns]
    wide = wide.reset_index()
    if "aic_severity_tertile" in wide.columns and "aic_endotype" in wide.columns:
        wide["delta_aic_severity_tertile_minus_endotype"] = wide["aic_severity_tertile"] - wide["aic_endotype"]
    if "auc_severity_tertile" in wide.columns and "auc_endotype" in wide.columns:
        wide["delta_auc_endotype_minus_severity"] = wide["auc_endotype"] - wide["auc_severity_tertile"]
    return wide


def build_cox_comparison(metrics: pd.DataFrame) -> pd.DataFrame:
    if metrics.empty:
        return pd.DataFrame()
    wide = metrics.pivot_table(
        index=["analysis_set", "analysis_tier", "cohort", "outcome", "outcome_label", "adjustment"],
        columns="model_type",
        values=["n", "events", "event_pct", "partial_aic", "partial_bic", "median_followup_time_years"],
        aggfunc="first",
    )
    wide.columns = [f"{metric}_{model_type}" for metric, model_type in wide.columns]
    wide = wide.reset_index()
    if "partial_aic_severity_tertile" in wide.columns and "partial_aic_endotype" in wide.columns:
        wide["delta_partial_aic_severity_tertile_minus_endotype"] = (
            wide["partial_aic_severity_tertile"] - wide["partial_aic_endotype"]
        )
    return wide


def class_terms_only(terms: pd.DataFrame, effect_name: str) -> pd.DataFrame:
    if terms.empty:
        return pd.DataFrame()
    subset = terms[(terms["model_type"] == "endotype") & terms["term_label"].astype(str).str.fullmatch(r"\d+")].copy()
    if subset.empty:
        return subset
    subset = subset.rename(
        columns={
            effect_name: "sensitivity_effect",
            f"log_{'or' if effect_name == 'or' else 'hr'}": "sensitivity_log_effect",
            "ci_low": "sensitivity_ci_low",
            "ci_high": "sensitivity_ci_high",
            "p_value": "sensitivity_p_value",
        }
    )
    return subset


def build_effect_stability(output_dir: Path, logistic_terms: pd.DataFrame, cox_terms: pd.DataFrame) -> pd.DataFrame:
    rows = []
    functional_age = pd.read_csv(output_dir / "phase5_outcome_model_terms.csv", low_memory=False)
    functional_age = functional_age[
        (functional_age["outcome"] == FUNCTIONAL_OUTCOME["outcome"])
        & (functional_age["model_type"] == "endotype")
        & (functional_age["adjustment"] == "age_adjusted")
        & (functional_age["term_label"].astype(str).str.fullmatch(r"\d+"))
    ].copy()
    functional_age = functional_age.rename(
        columns={
            "or": "age_adjusted_effect",
            "log_or": "age_adjusted_log_effect",
            "ci_low": "age_adjusted_ci_low",
            "ci_high": "age_adjusted_ci_high",
            "p_value": "age_adjusted_p_value",
        }
    )
    functional_sens = class_terms_only(logistic_terms, "or")
    if not functional_sens.empty:
        rows.append(
            merge_stability(
                functional_age,
                functional_sens,
                "functional_deterioration_ge_0_5sd",
                "OR",
                "age_adjusted_log_effect",
                "sensitivity_log_effect",
            )
        )

    mortality_age = pd.read_csv(output_dir / "phase6_mortality_model_terms.csv", low_memory=False)
    mortality_age = mortality_age[
        (mortality_age["model_type"] == "endotype")
        & (mortality_age["term_label"].astype(str).str.fullmatch(r"\d+"))
    ].copy()
    mortality_age = mortality_age.rename(
        columns={
            "hr": "age_adjusted_effect",
            "log_hr": "age_adjusted_log_effect",
            "ci_low": "age_adjusted_ci_low",
            "ci_high": "age_adjusted_ci_high",
            "p_value": "age_adjusted_p_value",
        }
    )
    mortality_sens = class_terms_only(cox_terms, "hr")
    if not mortality_sens.empty:
        rows.append(
            merge_stability(
                mortality_age,
                mortality_sens,
                "all_cause_mortality",
                "HR",
                "age_adjusted_log_effect",
                "sensitivity_log_effect",
            )
        )
    return pd.concat(rows, ignore_index=True, sort=False) if rows else pd.DataFrame()


def merge_stability(
    age_terms: pd.DataFrame,
    sensitivity_terms: pd.DataFrame,
    outcome: str,
    effect_measure: str,
    age_log_column: str,
    sensitivity_log_column: str,
) -> pd.DataFrame:
    keys = ["analysis_set", "analysis_tier", "cohort", "term_label"]
    keep_age = [
        *keys,
        "age_adjusted_effect",
        age_log_column,
        "age_adjusted_ci_low",
        "age_adjusted_ci_high",
        "age_adjusted_p_value",
    ]
    keep_sens = [
        *keys,
        "adjustment",
        "sensitivity_effect",
        sensitivity_log_column,
        "sensitivity_ci_low",
        "sensitivity_ci_high",
        "sensitivity_p_value",
    ]
    merged = age_terms[keep_age].merge(sensitivity_terms[keep_sens], on=keys, how="inner")
    merged["outcome"] = outcome
    merged["effect_measure"] = effect_measure
    merged["effect_ratio_sensitivity_vs_age"] = np.exp(
        pd.to_numeric(merged[sensitivity_log_column], errors="coerce")
        - pd.to_numeric(merged[age_log_column], errors="coerce")
    )
    merged["age_excludes_null"] = (
        (pd.to_numeric(merged["age_adjusted_ci_low"], errors="coerce") > 1)
        | (pd.to_numeric(merged["age_adjusted_ci_high"], errors="coerce") < 1)
    ).astype(int)
    merged["sensitivity_excludes_null"] = (
        (pd.to_numeric(merged["sensitivity_ci_low"], errors="coerce") > 1)
        | (pd.to_numeric(merged["sensitivity_ci_high"], errors="coerce") < 1)
    ).astype(int)
    merged["direction_change"] = (
        (
            (pd.to_numeric(merged["age_adjusted_effect"], errors="coerce") > 1)
            & (pd.to_numeric(merged["sensitivity_effect"], errors="coerce") < 1)
        )
        | (
            (pd.to_numeric(merged["age_adjusted_effect"], errors="coerce") < 1)
            & (pd.to_numeric(merged["sensitivity_effect"], errors="coerce") > 1)
        )
    ).astype(int)
    merged["significance_change"] = (merged["age_excludes_null"] != merged["sensitivity_excludes_null"]).astype(int)
    merged["material_log_change"] = (
        np.abs(np.log(pd.to_numeric(merged["effect_ratio_sensitivity_vs_age"], errors="coerce"))) >= math.log(1.25)
    ).astype(int)
    merged["stability_flag"] = (
        (merged["direction_change"] == 1)
        | (merged["significance_change"] == 1)
        | (merged["material_log_change"] == 1)
    ).astype(int)
    ordered = [
        "outcome",
        "effect_measure",
        "analysis_set",
        "analysis_tier",
        "cohort",
        "term_label",
        "adjustment",
        "age_adjusted_effect",
        "age_adjusted_ci_low",
        "age_adjusted_ci_high",
        "age_adjusted_p_value",
        "sensitivity_effect",
        "sensitivity_ci_low",
        "sensitivity_ci_high",
        "sensitivity_p_value",
        "effect_ratio_sensitivity_vs_age",
        "direction_change",
        "significance_change",
        "material_log_change",
        "stability_flag",
    ]
    out = merged[ordered].copy()
    for column in ["age_adjusted_effect", "sensitivity_effect", "effect_ratio_sensitivity_vs_age"]:
        out[column] = pd.to_numeric(out[column], errors="coerce").round(4)
    return out


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


def write_report(
    output_dir: Path,
    logistic_comparison: pd.DataFrame,
    cox_comparison: pd.DataFrame,
    stability: pd.DataFrame,
    skipped: pd.DataFrame,
) -> None:
    lines = [
        "# Phase 14 Covariate Sensitivity Models",
        "",
        "This phase refits functional deterioration and mortality validation models with baseline covariates from Phase 13.",
        "",
        "## Functional Deterioration Model Comparison",
        "",
    ]
    func_cols = [
        "cohort",
        "adjustment",
        "n_endotype",
        "events_endotype",
        "event_pct_endotype",
        "aic_endotype",
        "aic_severity_tertile",
        "delta_aic_severity_tertile_minus_endotype",
        "auc_endotype",
        "auc_severity_tertile",
    ]
    if not logistic_comparison.empty:
        lines.extend(markdown_table(logistic_comparison, [column for column in func_cols if column in logistic_comparison.columns]))
    else:
        lines.append("No functional models fit.")
    lines.extend(["", "## Mortality Model Comparison", ""])
    mort_cols = [
        "cohort",
        "adjustment",
        "n_endotype",
        "events_endotype",
        "event_pct_endotype",
        "partial_aic_endotype",
        "partial_aic_severity_tertile",
        "delta_partial_aic_severity_tertile_minus_endotype",
    ]
    if not cox_comparison.empty:
        lines.extend(markdown_table(cox_comparison, [column for column in mort_cols if column in cox_comparison.columns]))
    else:
        lines.append("No mortality models fit.")
    lines.extend(["", "## Endotype Effect Stability Flags", ""])
    flagged = stability[stability["stability_flag"] == 1].copy() if not stability.empty else pd.DataFrame()
    if not flagged.empty:
        lines.extend(
            markdown_table(
                flagged,
                [
                    "outcome",
                    "cohort",
                    "term_label",
                    "adjustment",
                    "age_adjusted_effect",
                    "sensitivity_effect",
                    "effect_ratio_sensitivity_vs_age",
                    "direction_change",
                    "significance_change",
                    "material_log_change",
                ],
            )
        )
    else:
        lines.append("No class-level endotype terms crossed the current stability-flag rule.")
    lines.extend(["", "## Skipped Fits", ""])
    if not skipped.empty:
        lines.extend(markdown_table(skipped, ["cohort", "outcome_family", "model_type", "adjustment", "n", "events", "skip_reason"]))
    else:
        lines.append("No skipped fits.")
    lines.extend(
        [
            "",
            "## Interpretation Guardrails",
            "",
            "- Minimal-core sensitivity uses age, education, marital status, smoking, and drinking.",
            "- Expanded-core sensitivity is only attempted when Phase 13 marked rural/region and physical activity as ready.",
            "- BMI sensitivity is reported separately because BMI is close to the cardiometabolic construct.",
            "- Stability flags are screening flags, not final decisions; they indicate direction change, null-exclusion change, or a >=25% relative change in OR/HR.",
        ]
    )
    (output_dir / "phase14_covariate_sensitivity_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8-sig")


def write_manuscript_summary(manuscript_dir: Path, stability: pd.DataFrame) -> None:
    flags = stability[stability["stability_flag"] == 1].copy() if not stability.empty else pd.DataFrame()
    lines = [
        "# Covariate Sensitivity Results Draft",
        "",
        "Phase 14 reran functional deterioration and mortality validation models with Phase 13 baseline covariates.",
        "",
        "## Draft Interpretation",
        "",
        "Minimal-core covariate sensitivity should be treated as the first robustness check after the age-adjusted models. Expanded-core and BMI models are sensitivity-only because coverage and construct overlap differ by cohort.",
        "",
        "## Stability Flags",
        "",
    ]
    if flags.empty:
        lines.append("No stability flags under the current rule.")
    else:
        lines.extend(
            markdown_table(
                flags,
                [
                    "outcome",
                    "cohort",
                    "term_label",
                    "adjustment",
                    "age_adjusted_effect",
                    "sensitivity_effect",
                    "effect_ratio_sensitivity_vs_age",
                    "direction_change",
                    "significance_change",
                    "material_log_change",
                ],
            )
        )
    lines.extend(
        [
            "",
            "## Manuscript Use",
            "",
            "- Report the age-adjusted models as the main validation screen.",
            "- Use minimal-core sensitivity to show whether endotype-outcome signals persist after sociodemographic and lifestyle adjustment.",
            "- Do not use expanded-core or BMI sensitivity to redefine class labels without manual review.",
        ]
    )
    manuscript_dir.mkdir(parents=True, exist_ok=True)
    (manuscript_dir / "covariate_sensitivity_results.md").write_text("\n".join(lines) + "\n", encoding="utf-8-sig")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--manuscript-dir", type=Path, default=None)
    parser.add_argument("--min-events", type=int, default=20)
    args = parser.parse_args()

    output_dir = args.output_dir
    manuscript_dir = args.manuscript_dir or (output_dir.parent / "manuscript")
    output_dir.mkdir(parents=True, exist_ok=True)
    manuscript_dir.mkdir(parents=True, exist_ok=True)

    covariates = read_covariates(output_dir / "phase13_covariate_participant_screen.csv")
    readiness = readiness_lookup(output_dir / "phase13_covariate_readiness_summary.csv")
    functional_screen = read_functional_screen(output_dir / "phase5_participant_outcome_screen.csv", covariates)
    mortality_screen = read_mortality_screen(output_dir / "phase6_mortality_participant_screen.csv", covariates)

    logistic_metrics, logistic_terms, logistic_skipped = run_logistic_models(functional_screen, readiness, args.min_events)
    cox_metrics, cox_terms, cox_skipped = run_cox_models(mortality_screen, readiness, args.min_events)
    logistic_comparison = build_logistic_comparison(logistic_metrics)
    cox_comparison = build_cox_comparison(cox_metrics)
    stability = build_effect_stability(output_dir, logistic_terms, cox_terms)
    skipped = pd.concat([logistic_skipped, cox_skipped], ignore_index=True, sort=False)

    logistic_metrics.to_csv(output_dir / "phase14_functional_covariate_model_metrics.csv", index=False, encoding="utf-8-sig")
    logistic_terms.to_csv(output_dir / "phase14_functional_covariate_model_terms.csv", index=False, encoding="utf-8-sig")
    logistic_comparison.to_csv(output_dir / "phase14_functional_covariate_model_comparison.csv", index=False, encoding="utf-8-sig")
    cox_metrics.to_csv(output_dir / "phase14_mortality_covariate_model_metrics.csv", index=False, encoding="utf-8-sig")
    cox_terms.to_csv(output_dir / "phase14_mortality_covariate_model_terms.csv", index=False, encoding="utf-8-sig")
    cox_comparison.to_csv(output_dir / "phase14_mortality_covariate_model_comparison.csv", index=False, encoding="utf-8-sig")
    skipped.to_csv(output_dir / "phase14_covariate_model_skipped.csv", index=False, encoding="utf-8-sig")
    stability.to_csv(output_dir / "phase14_endotype_effect_stability.csv", index=False, encoding="utf-8-sig")
    write_report(output_dir, logistic_comparison, cox_comparison, stability, skipped)
    write_manuscript_summary(manuscript_dir, stability)


if __name__ == "__main__":
    main()
