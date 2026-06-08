from __future__ import annotations

import argparse
import math
import re
import warnings
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from sklearn.metrics import roc_auc_score
from sklearn.mixture import GaussianMixture


PROFILE_DOMAIN_COLUMNS = [
    "cognitive_score",
    "affective_score",
    "cardiometabolic_chronic_score",
]

ALL_DOMAIN_COLUMNS = [
    "functional_score",
    *PROFILE_DOMAIN_COLUMNS,
]

PROFILE_DOMAIN_LABELS = {
    "cognitive_score": "cognitive",
    "affective_score": "affective",
    "cardiometabolic_chronic_score": "cardiometabolic_chronic",
}

OUTCOME = "functional_deterioration_ge_0_5sd"
AVAILABLE = "functional_deterioration_available"
MIN_CLASS_PCT = 5.0
MIN_EVENTS = 20


@dataclass(frozen=True)
class FitResult:
    model: GaussianMixture
    metrics: dict[str, object]
    profiles: pd.DataFrame
    assignments: pd.DataFrame


def safe_exp(value: float) -> float:
    if pd.isna(value):
        return np.nan
    if value > 700:
        return math.inf
    if value < -700:
        return 0.0
    return float(math.exp(value))


def normalized_entropy(probabilities: np.ndarray) -> float:
    clipped = np.clip(probabilities, 1e-12, 1.0)
    entropy = -np.mean(np.sum(clipped * np.log(clipped), axis=1))
    return float(1.0 - entropy / np.log(probabilities.shape[1]))


def severity_label(value: float) -> str:
    if value <= -0.5:
        return "low_burden"
    if value >= 0.5:
        return "high_burden"
    return "intermediate"


def class_profile_label(row: pd.Series) -> tuple[str, str, str]:
    severity = float(row["lfo_severity_score"])
    deviations = {}
    for column in PROFILE_DOMAIN_COLUMNS:
        deviations[PROFILE_DOMAIN_LABELS[column]] = float(row[column]) - severity
    high_domains = [name for name, value in deviations.items() if value >= 0.35]
    spared_domains = [name for name, value in deviations.items() if value <= -0.35]
    label = severity_label(severity)
    if high_domains:
        label += "_high_" + "_".join(high_domains)
    if spared_domains:
        label += "_spared_" + "_".join(spared_domains)
    if not high_domains and not spared_domains:
        label += "_severity_aligned"
    return label, ";".join(high_domains), ";".join(spared_domains)


def clean_term(term: str) -> str:
    if term == "Intercept":
        return "Intercept"
    match = re.search(r"\[T\.(.+)\]", term)
    if match:
        return match.group(1)
    return term


def read_scores(path: Path) -> pd.DataFrame:
    scores = pd.read_csv(path, dtype={"participant_id": str, "wave": str}, low_memory=False)
    for column in ["age", *ALL_DOMAIN_COLUMNS, "cardiometabolic_chronic_count", "cardiometabolic_chronic_prop"]:
        if column in scores.columns:
            scores[column] = pd.to_numeric(scores[column], errors="coerce")
    scores["wave"] = scores["wave"].astype("string")
    scores["wave_num"] = pd.to_numeric(scores["wave"], errors="coerce")
    scores["complete_lfo_three_domain"] = scores[PROFILE_DOMAIN_COLUMNS].notna().all(axis=1).astype(int)
    scores["lfo_severity_score"] = scores[PROFILE_DOMAIN_COLUMNS].mean(axis=1)
    return scores


def order_classes(labels: np.ndarray, probabilities: np.ndarray, data: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, dict[int, int]]:
    temp = data.copy()
    temp["raw_class"] = labels
    severity_by_raw = temp.groupby("raw_class")["lfo_severity_score"].mean().sort_values()
    mapping = {int(raw): idx + 1 for idx, raw in enumerate(severity_by_raw.index)}
    ordered_labels = np.array([mapping[int(label)] for label in labels])
    ordered_probabilities = np.zeros_like(probabilities)
    for raw, ordered in mapping.items():
        ordered_probabilities[:, ordered - 1] = probabilities[:, raw]
    return ordered_labels, ordered_probabilities, mapping


def build_profiles(
    data: pd.DataFrame,
    ordered_labels: np.ndarray,
    ordered_probabilities: np.ndarray,
    metadata: dict[str, object],
) -> pd.DataFrame:
    profile_frame = data.copy()
    profile_frame["lfo_profile_class"] = ordered_labels
    rows = []
    total_n = len(profile_frame)
    for class_id, group in profile_frame.groupby("lfo_profile_class"):
        posterior = ordered_probabilities[ordered_labels == class_id, class_id - 1]
        row = {
            **metadata,
            "lfo_profile_class": int(class_id),
            "class_n": int(len(group)),
            "class_pct": round(len(group) / total_n * 100, 2),
            "mean_posterior": round(float(np.mean(posterior)), 4),
            "lfo_severity_score": round(float(group["lfo_severity_score"].mean()), 4),
            "lfo_severity_sd": round(float(group["lfo_severity_score"].std()), 4),
            "baseline_functional_score_mean": round(float(group["functional_score"].mean()), 4)
            if group["functional_score"].notna().any()
            else np.nan,
        }
        for column in PROFILE_DOMAIN_COLUMNS:
            row[column] = round(float(group[column].mean()), 4)
        label, high_domains, spared_domains = class_profile_label(pd.Series(row))
        row["profile_label"] = label
        row["high_domains_vs_class_severity"] = high_domains
        row["spared_domains_vs_class_severity"] = spared_domains
        rows.append(row)
    return pd.DataFrame(rows).sort_values("lfo_profile_class")


def profile_interpretation(profiles: pd.DataFrame) -> dict[str, object]:
    deviations = profiles[PROFILE_DOMAIN_COLUMNS].subtract(profiles["lfo_severity_score"], axis=0).abs()
    max_deviation = float(deviations.max().max())
    return {
        "profile_interpretation": "domain_specific" if max_deviation >= 0.50 else "mostly_severity_gradient",
        "max_domain_deviation_from_lfo_severity": round(max_deviation, 4),
    }


def fit_one_model(data: pd.DataFrame, n_components: int, metadata: dict[str, object], random_state: int, n_init: int) -> FitResult:
    x = data[PROFILE_DOMAIN_COLUMNS].to_numpy(dtype=float)
    model = GaussianMixture(
        n_components=n_components,
        covariance_type="full",
        reg_covar=1e-6,
        n_init=n_init,
        max_iter=500,
        random_state=random_state,
    )
    model.fit(x)
    raw_labels = model.predict(x)
    probabilities = model.predict_proba(x)
    ordered_labels, ordered_probabilities, _ = order_classes(raw_labels, probabilities, data)
    profiles = build_profiles(data, ordered_labels, ordered_probabilities, metadata | {"n_classes": n_components})
    min_class_n = int(profiles["class_n"].min())
    min_class_pct = float(profiles["class_pct"].min())
    metrics = {
        **metadata,
        "profile_design": "leave_functional_domain_out",
        "profile_domains": "+".join(PROFILE_DOMAIN_COLUMNS),
        "n": int(len(data)),
        "n_classes": n_components,
        "bic": round(float(model.bic(x)), 2),
        "aic": round(float(model.aic(x)), 2),
        "lower_bound": round(float(model.lower_bound_), 6),
        "converged": int(model.converged_),
        "n_iter": int(model.n_iter_),
        "entropy_separation": round(normalized_entropy(ordered_probabilities), 4),
        "mean_max_posterior": round(float(ordered_probabilities.max(axis=1).mean()), 4),
        "min_class_n": min_class_n,
        "min_class_pct": round(min_class_pct, 2),
        **profile_interpretation(profiles),
    }
    assignment_frame = data[
        [
            "analysis_set",
            "analysis_tier",
            "cohort",
            "participant_id",
            "wave",
            "wave_num",
            "age",
            "functional_score",
            "lfo_severity_score",
            *PROFILE_DOMAIN_COLUMNS,
        ]
    ].copy()
    assignment_frame["n_classes"] = n_components
    assignment_frame["lfo_profile_class"] = ordered_labels
    assignment_frame["lfo_profile_posterior"] = ordered_probabilities.max(axis=1)
    return FitResult(model=model, metrics=metrics, profiles=profiles, assignments=assignment_frame)


def fit_lfo_profiles(scores: pd.DataFrame, random_state: int, n_init: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    metric_rows = []
    profile_frames = []
    best_rows = []
    assignment_frames = []

    model_scores = scores[scores["complete_lfo_three_domain"] == 1].copy()
    grouped = model_scores.groupby(["analysis_set", "analysis_tier", "cohort", "wave"], dropna=False)
    for keys, group in grouped:
        analysis_set, analysis_tier, cohort, wave = keys
        metadata = {
            "analysis_set": analysis_set,
            "analysis_tier": analysis_tier,
            "cohort": cohort,
            "wave": wave,
        }
        fits = []
        for n_components in range(2, 6):
            fit = fit_one_model(group.reset_index(drop=True), n_components, metadata, random_state, n_init)
            fits.append(fit)
            metric_rows.append(fit.metrics)
            profile_frames.append(fit.profiles)
        bic_winner = min(fits, key=lambda item: item.metrics["bic"])
        admissible = [
            fit
            for fit in fits
            if float(fit.metrics["min_class_pct"]) >= MIN_CLASS_PCT and int(fit.metrics["converged"]) == 1
        ]
        best = min(admissible, key=lambda item: item.metrics["bic"]) if admissible else bic_winner
        best_summary = dict(best.metrics)
        best_summary["selection_rule"] = (
            f"min_bic_among_models_with_min_class_pct_ge_{MIN_CLASS_PCT:g}"
            if admissible
            else "min_bic_no_admissible_model"
        )
        best_summary["bic_winner_n_classes"] = bic_winner.metrics["n_classes"]
        best_summary["bic_winner_min_class_pct"] = bic_winner.metrics["min_class_pct"]
        best_summary["bic_winner_bic"] = bic_winner.metrics["bic"]
        best_summary["selected_differs_from_bic_winner"] = int(best.metrics["n_classes"] != bic_winner.metrics["n_classes"])
        best_rows.append(best_summary)
        assignment_frames.append(best.assignments)

    return (
        pd.DataFrame(metric_rows),
        pd.concat(profile_frames, ignore_index=True) if profile_frames else pd.DataFrame(),
        pd.DataFrame(best_rows),
        pd.concat(assignment_frames, ignore_index=True) if assignment_frames else pd.DataFrame(),
    )


def build_participant_screen(assignments: pd.DataFrame, scores: pd.DataFrame) -> pd.DataFrame:
    keys = ["analysis_set", "analysis_tier", "cohort", "participant_id"]
    assignments = assignments.copy()
    assignments["baseline_wave"] = assignments["wave"]
    assignments["baseline_wave_num"] = pd.to_numeric(assignments["wave_num"], errors="coerce")

    follow = scores[
        [
            "cohort",
            "participant_id",
            "wave",
            "wave_num",
            "age",
            *ALL_DOMAIN_COLUMNS,
        ]
    ].rename(
        columns={
            "wave": "followup_wave",
            "wave_num": "followup_wave_num",
            "age": "followup_age",
            **{column: f"followup_{column}" for column in ALL_DOMAIN_COLUMNS},
        }
    )
    candidates = assignments[keys + ["baseline_wave", "baseline_wave_num"]].merge(
        follow,
        on=["cohort", "participant_id"],
        how="left",
    )
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
    screen = screen.merge(last_followup, on=keys, how="left")
    screen["followup_rows"] = screen["followup_rows"].fillna(0).astype(int)
    screen["any_followup"] = (screen["followup_rows"] > 0).astype(int)
    screen["followup_year_span"] = screen["max_followup_age"] - screen["age"]
    screen["functional_deterioration_change"] = screen["followup_functional_score"] - screen["functional_score"]
    available = screen["functional_score"].notna() & screen["followup_functional_score"].notna()
    screen[AVAILABLE] = available.astype(int)
    screen[OUTCOME] = pd.Series(pd.NA, index=screen.index, dtype="Float64")
    screen.loc[available, OUTCOME] = (screen.loc[available, "functional_deterioration_change"] >= 0.5).astype(int)
    screen["lfo_severity_tertile"] = (
        screen.groupby(["analysis_set", "cohort"], group_keys=False)["lfo_severity_score"]
        .apply(lambda values: pd.qcut(values.rank(method="first"), q=3, labels=["low", "middle", "high"]).astype(str))
        .reindex(screen.index)
    )
    screen["lfo_profile_class"] = screen["lfo_profile_class"].astype(str)
    return screen


def merge_with_existing_outcome_screen(assignments: pd.DataFrame, outcome_screen_path: Path) -> pd.DataFrame:
    outcome = pd.read_csv(
        outcome_screen_path,
        dtype={"participant_id": str, "wave": str, "baseline_wave": str},
        low_memory=False,
    )
    for column in [
        "age",
        OUTCOME,
        AVAILABLE,
        "functional_score",
        *PROFILE_DOMAIN_COLUMNS,
    ]:
        if column in outcome.columns:
            outcome[column] = pd.to_numeric(outcome[column], errors="coerce")
    lfo = assignments[
        [
            "analysis_set",
            "analysis_tier",
            "cohort",
            "participant_id",
            "wave",
            "n_classes",
            "lfo_profile_class",
            "lfo_profile_posterior",
            "lfo_severity_score",
        ]
    ].copy()
    lfo = lfo.rename(columns={"n_classes": "lfo_n_classes"})
    lfo["participant_id"] = lfo["participant_id"].astype(str)
    lfo["wave"] = lfo["wave"].astype(str)
    outcome["participant_id"] = outcome["participant_id"].astype(str)
    outcome["wave"] = outcome["wave"].astype(str)
    merged = outcome.merge(
        lfo,
        on=["analysis_set", "analysis_tier", "cohort", "participant_id", "wave"],
        how="left",
        validate="one_to_one",
    )
    merged["lfo_profile_class"] = merged["lfo_profile_class"].astype("string")
    for column in ["lfo_profile_posterior", "lfo_severity_score"]:
        merged[column] = pd.to_numeric(merged[column], errors="coerce")
    merged["lfo_assignment_available"] = merged["lfo_profile_class"].notna().astype(int)
    merged["lfo_severity_tertile"] = (
        merged.groupby(["analysis_set", "cohort"], group_keys=False)["lfo_severity_score"]
        .apply(lambda values: pd.qcut(values.rank(method="first"), q=3, labels=["low", "middle", "high"]).astype(str))
        .reindex(merged.index)
    )
    return merged


MODEL_SPECS = [
    {
        "model_type": "lfo_profile_age",
        "rhs": "C(lfo_profile_class, Treatment(reference='1')) + age",
        "main_decoupled_candidate": 1,
    },
    {
        "model_type": "lfo_profile_age_baseline_functional",
        "rhs": "C(lfo_profile_class, Treatment(reference='1')) + age + functional_score",
        "main_decoupled_candidate": 0,
    },
    {
        "model_type": "lfo_severity_score_age",
        "rhs": "lfo_severity_score + age",
        "main_decoupled_candidate": 1,
    },
    {
        "model_type": "lfo_severity_tertile_age",
        "rhs": "C(lfo_severity_tertile, Treatment(reference='low')) + age",
        "main_decoupled_candidate": 1,
    },
    {
        "model_type": "three_domain_scores_age",
        "rhs": "cognitive_score + affective_score + cardiometabolic_chronic_score + age",
        "main_decoupled_candidate": 1,
    },
    {
        "model_type": "baseline_functional_age_diagnostic",
        "rhs": "functional_score + age",
        "main_decoupled_candidate": 0,
    },
]


def formula_variables(rhs: str) -> list[str]:
    variables = {"age"}
    for column in [
        "lfo_profile_class",
        "lfo_severity_score",
        "lfo_severity_tertile",
        "functional_score",
        *PROFILE_DOMAIN_COLUMNS,
    ]:
        if column in rhs:
            variables.add(column)
    return sorted(variables)


def model_frame(screen: pd.DataFrame, rhs: str) -> pd.DataFrame:
    variables = formula_variables(rhs)
    keep = [
        "analysis_set",
        "analysis_tier",
        "cohort",
        OUTCOME,
        AVAILABLE,
        *variables,
    ]
    data = screen[keep].copy()
    data = data[data[AVAILABLE] == 1].copy()
    data = data.dropna(subset=[OUTCOME, *variables])
    data[OUTCOME] = data[OUTCOME].astype(int)
    return data


def fit_glm(data: pd.DataFrame, rhs: str):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return smf.glm(formula=f"{OUTCOME} ~ {rhs}", data=data, family=sm.families.Binomial()).fit()


def summarize_fit(fit, data: pd.DataFrame, model_spec: dict[str, object], rhs: str) -> tuple[dict[str, object], pd.DataFrame]:
    predicted = fit.predict(data)
    auc = np.nan
    if data[OUTCOME].nunique() == 2:
        auc = float(roc_auc_score(data[OUTCOME], predicted))
    bic = getattr(fit, "bic_llf", np.nan)
    metrics = {
        "analysis_set": data["analysis_set"].iloc[0],
        "analysis_tier": data["analysis_tier"].iloc[0],
        "cohort": data["cohort"].iloc[0],
        "outcome": OUTCOME,
        "profile_design": "leave_functional_domain_out",
        "model_type": model_spec["model_type"],
        "main_decoupled_candidate": model_spec["main_decoupled_candidate"],
        "rhs": rhs,
        "n": int(len(data)),
        "events": int(data[OUTCOME].sum()),
        "event_pct": round(float(data[OUTCOME].mean()) * 100, 2),
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
                "outcome": OUTCOME,
                "profile_design": metrics["profile_design"],
                "model_type": metrics["model_type"],
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


def run_validation_models(screen: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    metric_rows = []
    term_frames = []
    skipped_rows = []

    for model_spec in MODEL_SPECS:
        rhs = str(model_spec["rhs"])
        for _, cohort_frame in screen.groupby(["analysis_set", "analysis_tier", "cohort"], dropna=False):
            data = model_frame(cohort_frame, rhs)
            skip_reason = ""
            if data.empty:
                skip_reason = "no_available_rows"
            elif data[OUTCOME].sum() < MIN_EVENTS:
                skip_reason = "too_few_events"
            elif (len(data) - data[OUTCOME].sum()) < MIN_EVENTS:
                skip_reason = "too_few_nonevents"
            if skip_reason:
                skipped_rows.append(
                    {
                        "analysis_set": cohort_frame["analysis_set"].iloc[0],
                        "analysis_tier": cohort_frame["analysis_tier"].iloc[0],
                        "cohort": cohort_frame["cohort"].iloc[0],
                        "profile_design": "leave_functional_domain_out",
                        "model_type": model_spec["model_type"],
                        "n": int(len(data)),
                        "events": int(data[OUTCOME].sum()) if not data.empty else 0,
                        "skip_reason": skip_reason,
                    }
                )
                continue
            try:
                fit = fit_glm(data, rhs)
                metrics, terms = summarize_fit(fit, data, model_spec, rhs)
                metric_rows.append(metrics)
                term_frames.append(terms)
            except Exception as exc:  # pragma: no cover - diagnostic path
                skipped_rows.append(
                    {
                        "analysis_set": cohort_frame["analysis_set"].iloc[0],
                        "analysis_tier": cohort_frame["analysis_tier"].iloc[0],
                        "cohort": cohort_frame["cohort"].iloc[0],
                        "profile_design": "leave_functional_domain_out",
                        "model_type": model_spec["model_type"],
                        "n": int(len(data)),
                        "events": int(data[OUTCOME].sum()),
                        "skip_reason": f"fit_failed: {type(exc).__name__}: {exc}",
                    }
                )
    return (
        pd.DataFrame(metric_rows),
        pd.concat(term_frames, ignore_index=True) if term_frames else pd.DataFrame(),
        pd.DataFrame(skipped_rows),
    )


def build_comparison(metrics: pd.DataFrame, terms: pd.DataFrame, screen: pd.DataFrame) -> pd.DataFrame:
    if metrics.empty:
        return pd.DataFrame()
    wide = metrics.pivot_table(
        index=["analysis_set", "analysis_tier", "cohort"],
        columns="model_type",
        values=["n", "events", "event_pct", "aic", "bic_llf", "auc"],
        aggfunc="first",
    )
    wide.columns = [f"{value}_{model}" for value, model in wide.columns]
    wide = wide.reset_index()
    if "aic_three_domain_scores_age" in wide.columns and "aic_lfo_profile_age" in wide.columns:
        wide["delta_aic_three_domain_scores_minus_lfo_profile"] = (
            wide["aic_three_domain_scores_age"] - wide["aic_lfo_profile_age"]
        ).round(3)
    if "auc_lfo_profile_age" in wide.columns and "auc_three_domain_scores_age" in wide.columns:
        wide["delta_auc_lfo_profile_minus_three_domain_scores"] = (
            wide["auc_lfo_profile_age"] - wide["auc_three_domain_scores_age"]
        ).round(4)
    if "auc_baseline_functional_age_diagnostic" in wide.columns and "auc_lfo_profile_age" in wide.columns:
        wide["delta_auc_lfo_profile_minus_baseline_functional_diagnostic"] = (
            wide["auc_lfo_profile_age"] - wide["auc_baseline_functional_age_diagnostic"]
        ).round(4)

    profile_terms = terms[
        (terms["model_type"] == "lfo_profile_age")
        & (terms["term_label"] != "Intercept")
        & terms["term_label"].notna()
    ].copy()
    if profile_terms.empty:
        wide["max_lfo_profile_or"] = np.nan
        wide["min_lfo_profile_or"] = np.nan
        wide["max_lfo_profile_ci_high"] = np.nan
    else:
        term_summary = (
            profile_terms.groupby(["analysis_set", "analysis_tier", "cohort"], dropna=False)
            .agg(
                max_lfo_profile_or=("or", "max"),
                min_lfo_profile_or=("or", "min"),
                max_lfo_profile_ci_high=("ci_high", "max"),
            )
            .reset_index()
        )
        wide = wide.merge(term_summary, on=["analysis_set", "analysis_tier", "cohort"], how="left")

    event_summary = (
        screen[screen[AVAILABLE] == 1]
        .groupby(["analysis_set", "analysis_tier", "cohort"], dropna=False)
        .agg(
            validation_n=(OUTCOME, "size"),
            validation_events=(OUTCOME, "sum"),
            baseline_function_event_corr=("functional_score", lambda values: np.nan),
        )
        .reset_index()
    )
    correlations = []
    for keys, group in screen[screen[AVAILABLE] == 1].groupby(["analysis_set", "analysis_tier", "cohort"], dropna=False):
        analysis_set, analysis_tier, cohort = keys
        correlations.append(
            {
                "analysis_set": analysis_set,
                "analysis_tier": analysis_tier,
                "cohort": cohort,
                "baseline_function_event_corr": round(float(group["functional_score"].corr(group[OUTCOME])), 4)
                if group["functional_score"].notna().sum() >= 3
                else np.nan,
                "lfo_severity_event_corr": round(float(group["lfo_severity_score"].corr(group[OUTCOME])), 4)
                if group["lfo_severity_score"].notna().sum() >= 3
                else np.nan,
            }
        )
    corr = pd.DataFrame(correlations)
    if not event_summary.empty:
        event_summary = event_summary.drop(columns=["baseline_function_event_corr"], errors="ignore")
        event_summary = event_summary.merge(corr, on=["analysis_set", "analysis_tier", "cohort"], how="left")
        wide = wide.merge(event_summary, on=["analysis_set", "analysis_tier", "cohort"], how="left")

    wide["implausible_lfo_or_or_separation_flag"] = (
        (pd.to_numeric(wide.get("max_lfo_profile_or"), errors="coerce") >= 20)
        | (pd.to_numeric(wide.get("min_lfo_profile_or"), errors="coerce") <= 0.05)
        | (pd.to_numeric(wide.get("max_lfo_profile_ci_high"), errors="coerce") >= 50)
    ).astype(int)
    wide["phase32b_evidence_status"] = wide.apply(decide_status, axis=1)
    return wide


def decide_status(row: pd.Series) -> str:
    cohort = str(row["cohort"])
    if cohort == "LASI":
        return "exclude_no_followup_validation"
    if cohort == "KLoSA":
        return "bridge_sensitivity_only"
    if int(row.get("implausible_lfo_or_or_separation_flag", 0)) == 1:
        return "exclude_or_redefine_endpoint"
    delta_aic = row.get("delta_aic_three_domain_scores_minus_lfo_profile", np.nan)
    delta_auc = row.get("delta_auc_lfo_profile_minus_three_domain_scores", np.nan)
    if pd.notna(delta_aic) and pd.notna(delta_auc) and float(delta_aic) >= 2 and float(delta_auc) >= 0:
        return "candidate_decoupled_profile_signal"
    if pd.notna(delta_aic) and float(delta_aic) < 0:
        return "three_domain_scores_fit_better_than_profiles"
    return "decoupled_association_no_profile_advantage"


def markdown_table(df: pd.DataFrame, columns: list[str]) -> list[str]:
    if df.empty:
        return ["No rows."]
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in df[columns].to_dict("records"):
        values = []
        for column in columns:
            value = row.get(column, "")
            if pd.isna(value):
                values.append("")
            elif isinstance(value, float):
                values.append(str(round(value, 4)))
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return lines


def write_report(path: Path, best: pd.DataFrame, comparison: pd.DataFrame, skipped: pd.DataFrame) -> None:
    lines = [
        "# Phase 32B Decoupled Leave-Functional-Domain-Out Validation",
        "",
        "Date: 2026-06-02",
        "",
        "## Design",
        "",
        "Profiles were rebuilt using only cognitive, affective and cardiometabolic/chronic disease baseline domains.",
        "Baseline functional score was not used in profile construction. Functional deterioration was then evaluated as a follow-up outcome.",
        "",
        "This design is a leakage-control sensitivity, not a full external validation design.",
        "",
        "## LFO Profile Model Selection",
        "",
    ]
    lines.extend(
        markdown_table(
            best.sort_values(["analysis_set", "cohort"]),
            [
                "analysis_set",
                "cohort",
                "n",
                "n_classes",
                "bic",
                "min_class_pct",
                "entropy_separation",
                "mean_max_posterior",
                "profile_interpretation",
            ],
        )
    )
    lines.extend(["", "## Functional Validation Comparison", ""])
    display_cols = [
        "cohort",
        "validation_n",
        "validation_events",
        "aic_lfo_profile_age",
        "auc_lfo_profile_age",
        "aic_three_domain_scores_age",
        "auc_three_domain_scores_age",
        "delta_aic_three_domain_scores_minus_lfo_profile",
        "delta_auc_lfo_profile_minus_three_domain_scores",
        "max_lfo_profile_or",
        "phase32b_evidence_status",
    ]
    if comparison.empty or "analysis_set" not in comparison.columns:
        lines.append("No validation models were fit.")
    else:
        lines.extend(markdown_table(comparison.sort_values(["analysis_set", "cohort"]), [col for col in display_cols if col in comparison.columns]))
    lines.extend(["", "## Interpretation", ""])
    statuses = comparison["phase32b_evidence_status"].value_counts().to_dict() if "phase32b_evidence_status" in comparison.columns else {}
    for status, count in statuses.items():
        lines.append(f"- {status}: {count}")
    lines.extend(
        [
            "",
            "## Manuscript Rule",
            "",
            "Only cohorts marked candidate_decoupled_profile_signal can be used as primary decoupled functional-validation evidence.",
            "Cohorts marked three_domain_scores_fit_better_than_profiles should be described as continuous-domain comparator evidence against profile superiority.",
            "KLoSA remains bridge-sensitivity and LASI remains excluded from follow-up validation.",
        ]
    )
    if not skipped.empty:
        lines.extend(["", "## Skipped Models", ""])
        lines.extend(markdown_table(skipped, ["cohort", "model_type", "n", "events", "skip_reason"]))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scores", type=Path, default=Path("outputs/phase3_domain_scores.csv"))
    parser.add_argument("--outcome-screen", type=Path, default=Path("outputs/phase5_participant_outcome_screen.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    parser.add_argument("--random-state", type=int, default=20260602)
    parser.add_argument("--n-init", type=int, default=5)
    args = parser.parse_args()

    scores = read_scores(args.scores)
    metrics, profiles, best, assignments = fit_lfo_profiles(scores, args.random_state, args.n_init)
    screen = merge_with_existing_outcome_screen(assignments, args.outcome_screen)
    validation_metrics, validation_terms, skipped = run_validation_models(screen)
    comparison = build_comparison(validation_metrics, validation_terms, screen)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(args.output_dir / "phase32_decoupled_lfo_gmm_metrics.csv", index=False, encoding="utf-8-sig")
    profiles.to_csv(args.output_dir / "phase32_decoupled_lfo_class_profiles.csv", index=False, encoding="utf-8-sig")
    best.to_csv(args.output_dir / "phase32_decoupled_lfo_best_model_summary.csv", index=False, encoding="utf-8-sig")
    assignments.to_csv(args.output_dir / "phase32_decoupled_lfo_assignments.csv", index=False, encoding="utf-8-sig")
    screen.to_csv(args.output_dir / "phase32_decoupled_lfo_participant_screen.csv", index=False, encoding="utf-8-sig")
    validation_metrics.to_csv(args.output_dir / "phase32_decoupled_validation_metrics.csv", index=False, encoding="utf-8-sig")
    validation_terms.to_csv(args.output_dir / "phase32_decoupled_validation_terms.csv", index=False, encoding="utf-8-sig")
    skipped.to_csv(args.output_dir / "phase32_decoupled_validation_skipped.csv", index=False, encoding="utf-8-sig")
    comparison.to_csv(args.output_dir / "phase32_decoupled_validation_comparison.csv", index=False, encoding="utf-8-sig")
    write_report(args.output_dir / "phase32_decoupled_validation_report.md", best, comparison, skipped)

    print("Phase 32B decoupled LFO validation complete.")
    if not comparison.empty:
        print(comparison[["cohort", "validation_n", "validation_events", "phase32b_evidence_status"]].to_string(index=False))


if __name__ == "__main__":
    main()
