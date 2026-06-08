from __future__ import annotations

import math
import re
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from sklearn.metrics import roc_auc_score


RUN_DATE = "2026-06-02"
OUTCOME = "functional_deterioration_ge_0_5sd"
AVAILABLE = "functional_deterioration_available"


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


def read_csv(output_dir: Path, name: str) -> pd.DataFrame:
    return pd.read_csv(output_dir / name, encoding="utf-8-sig", low_memory=False)


def build_reference_map(output_dir: Path) -> pd.DataFrame:
    labels = read_csv(output_dir, "phase11_table2_class_profiles_labels.csv")
    rows = []
    for keys, group in labels.groupby(["analysis_set", "analysis_tier", "cohort"], dropna=False):
        analysis_set, analysis_tier, cohort = keys
        group = group.copy()
        group["severity_mean"] = pd.to_numeric(group["severity_mean"], errors="coerce")
        ref = group.sort_values(["severity_mean", "class"]).iloc[0]
        true_low = bool(ref["severity_mean"] <= -0.25 and ref["functional_score"] <= 0 and ref["cognitive_score"] <= 0)
        rows.append(
            {
                "analysis_set": analysis_set,
                "analysis_tier": analysis_tier,
                "cohort": cohort,
                "lowest_burden_reference_class": str(ref["class"]),
                "reference_class_id": ref["class_id"],
                "reference_label": ref["label_en"],
                "reference_severity_mean": ref["severity_mean"],
                "reference_functional_score": ref["functional_score"],
                "reference_cognitive_score": ref["cognitive_score"],
                "reference_affective_score": ref["affective_score"],
                "reference_cardiometabolic_score": ref["cardiometabolic_chronic_score"],
                "true_low_burden_reference_flag": int(true_low),
                "reference_caution": "true_low_burden_reference"
                if true_low
                else "lowest_available_reference_not_strict_low_burden",
            }
        )
    return pd.DataFrame(rows).sort_values(["analysis_tier", "cohort"])


def model_frame(screen: pd.DataFrame, cohort: str) -> pd.DataFrame:
    data = screen[screen["cohort"].eq(cohort)].copy()
    data = data[data[AVAILABLE].eq(1)].copy()
    data = data.dropna(subset=[OUTCOME, "endotype_class", "age"])
    data[OUTCOME] = pd.to_numeric(data[OUTCOME], errors="coerce")
    data = data.dropna(subset=[OUTCOME])
    data[OUTCOME] = data[OUTCOME].astype(int)
    data["endotype_class"] = data["endotype_class"].astype(str)
    return data


def fit_cohort(data: pd.DataFrame, reference: str):
    formula = f"{OUTCOME} ~ C(endotype_class, Treatment(reference='{reference}')) + age"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return smf.glm(formula=formula, data=data, family=sm.families.Binomial()).fit()


def summarize_fit(fit, data: pd.DataFrame, reference: str) -> tuple[dict[str, object], pd.DataFrame]:
    predicted = fit.predict(data)
    auc = np.nan
    if data[OUTCOME].nunique() == 2:
        auc = float(roc_auc_score(data[OUTCOME], predicted))
    metrics = {
        "analysis_set": data["analysis_set"].iloc[0],
        "analysis_tier": data["analysis_tier"].iloc[0],
        "cohort": data["cohort"].iloc[0],
        "outcome": OUTCOME,
        "model_type": "endotype_lowest_burden_reference",
        "adjustment": "age_adjusted",
        "reference": reference,
        "n": int(len(data)),
        "events": int(data[OUTCOME].sum()),
        "event_pct": round(float(data[OUTCOME].mean()) * 100, 2),
        "aic": round(float(fit.aic), 3),
        "bic_llf": round(float(getattr(fit, "bic_llf", np.nan)), 3),
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
                "model_type": metrics["model_type"],
                "adjustment": metrics["adjustment"],
                "term": term,
                "term_label": clean_term(term),
                "reference": reference,
                "log_or": round(float(estimate), 6),
                "or": round(safe_exp(float(estimate)), 4),
                "ci_low": round(safe_exp(float(lower)), 4),
                "ci_high": round(safe_exp(float(upper)), 4),
                "p_value": round(float(fit.pvalues[term]), 6),
            }
        )
    return metrics, pd.DataFrame(rows)


def run_models(output_dir: Path, ref_map: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    screen = read_csv(output_dir, "phase5_participant_outcome_screen.csv")
    metric_rows = []
    term_frames = []
    skipped = []
    for _, ref in ref_map.iterrows():
        cohort = ref["cohort"]
        data = model_frame(screen, cohort)
        reference = str(ref["lowest_burden_reference_class"])
        if data.empty:
            skipped.append({"cohort": cohort, "reference": reference, "skip_reason": "no_available_data", "n": 0, "events": 0})
            continue
        if reference not in set(data["endotype_class"].astype(str)):
            skipped.append(
                {
                    "cohort": cohort,
                    "reference": reference,
                    "skip_reason": "reference_not_present_in_model_frame",
                    "n": len(data),
                    "events": int(data[OUTCOME].sum()),
                }
            )
            continue
        if data[OUTCOME].sum() < 20 or (len(data) - data[OUTCOME].sum()) < 20:
            skipped.append(
                {"cohort": cohort, "reference": reference, "skip_reason": "too_few_events_or_nonevents", "n": len(data), "events": int(data[OUTCOME].sum())}
            )
            continue
        try:
            fit = fit_cohort(data, reference)
            metrics, terms = summarize_fit(fit, data, reference)
            metric_rows.append(metrics)
            term_frames.append(terms)
        except Exception as exc:
            skipped.append(
                {
                    "cohort": cohort,
                    "reference": reference,
                    "skip_reason": f"fit_failed: {type(exc).__name__}: {exc}",
                    "n": len(data),
                    "events": int(data[OUTCOME].sum()),
                }
            )
    metrics = pd.DataFrame(metric_rows)
    terms = pd.concat(term_frames, ignore_index=True) if term_frames else pd.DataFrame()
    skipped_df = pd.DataFrame(skipped)
    return metrics, terms, skipped_df


def compare_with_original(output_dir: Path, uniform_terms: pd.DataFrame, ref_map: pd.DataFrame) -> pd.DataFrame:
    original = read_csv(output_dir, "phase14_functional_covariate_model_terms.csv")
    original = original[
        original["outcome"].eq(OUTCOME)
        & original["model_type"].eq("endotype")
        & original["adjustment"].eq("minimal_core")
        & original["term"].str.contains("endotype_class", regex=False)
    ].copy()
    keep = uniform_terms[uniform_terms["term"].str.contains("endotype_class", regex=False)].copy()
    keep = keep.rename(columns={"or": "uniform_reference_or", "ci_low": "uniform_reference_ci_low", "ci_high": "uniform_reference_ci_high"})
    original = original.rename(columns={"or": "original_c1_reference_or", "ci_low": "original_c1_reference_ci_low", "ci_high": "original_c1_reference_ci_high"})
    merged = keep.merge(
        original[["cohort", "term_label", "original_c1_reference_or", "original_c1_reference_ci_low", "original_c1_reference_ci_high"]],
        on=["cohort", "term_label"],
        how="left",
    )
    merged = merged.merge(ref_map[["cohort", "reference_class_id", "reference_caution"]], on="cohort", how="left")
    merged["direction_changed_vs_original"] = (
        (pd.to_numeric(merged["uniform_reference_or"], errors="coerce") - 1)
        * (pd.to_numeric(merged["original_c1_reference_or"], errors="coerce") - 1)
        < 0
    ).astype("Int64")
    columns = [
        "cohort",
        "term_label",
        "reference",
        "reference_class_id",
        "reference_caution",
        "uniform_reference_or",
        "uniform_reference_ci_low",
        "uniform_reference_ci_high",
        "original_c1_reference_or",
        "original_c1_reference_ci_low",
        "original_c1_reference_ci_high",
        "direction_changed_vs_original",
    ]
    return merged[[column for column in columns if column in merged.columns]]


def write_report(path: Path, ref_map: pd.DataFrame, metrics: pd.DataFrame, terms: pd.DataFrame, comparison: pd.DataFrame, skipped: pd.DataFrame) -> None:
    lines = [
        "# Phase 32C Uniform Reference-Class Reanalysis",
        "",
        f"Date: {RUN_DATE}",
        "",
        "## Decision",
        "",
        "All functional endotype ORs should use the cohort-specific lowest-burden available class as reference. Fixed C1 references are not comparable across cohorts.",
        "",
        "## Reference Map",
        "",
        "| Cohort | Reference class | Label | Severity | Caution |",
        "|---|---|---|---:|---|",
    ]
    for _, row in ref_map.iterrows():
        lines.append(
            f"| {row['cohort']} | {row['reference_class_id']} | {row['reference_label']} | "
            f"{row['reference_severity_mean']:.3f} | {row['reference_caution']} |"
        )
    lines.extend(["", "## Model Metrics", ""])
    if metrics.empty:
        lines.append("No models were fit.")
    else:
        lines.append("| Cohort | Reference | N | Events | AIC | AUC |")
        lines.append("|---|---|---:|---:|---:|---:|")
        for _, row in metrics.iterrows():
            lines.append(f"| {row['cohort']} | {row['reference']} | {row['n']} | {row['events']} | {row['aic']} | {row['auc']} |")
    changed = comparison[comparison.get("direction_changed_vs_original", pd.Series(dtype=int)).eq(1)] if not comparison.empty else pd.DataFrame()
    lines.extend(["", "## Direction Changes", ""])
    if changed.empty:
        lines.append("No direction changes detected among matched original C1-reference terms.")
    else:
        lines.append("| Cohort | Class | Uniform OR | Original OR |")
        lines.append("|---|---|---:|---:|")
        for _, row in changed.iterrows():
            lines.append(
                f"| {row['cohort']} | {row['term_label']} | {row['uniform_reference_or']} | {row['original_c1_reference_or']} |"
            )
    if not skipped.empty:
        lines.extend(["", "## Skipped", ""])
        lines.append("| Cohort | Reason |")
        lines.append("|---|---|")
        for _, row in skipped.iterrows():
            lines.append(f"| {row['cohort']} | {row['skip_reason']} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    root = Path.cwd()
    output_dir = root / "outputs"
    ref_map = build_reference_map(output_dir)
    metrics, terms, skipped = run_models(output_dir, ref_map)
    comparison = compare_with_original(output_dir, terms, ref_map) if not terms.empty else pd.DataFrame()
    ref_map.to_csv(output_dir / "phase32_lowest_burden_reference_map.csv", index=False, encoding="utf-8-sig")
    metrics.to_csv(output_dir / "phase32_uniform_reference_functional_metrics.csv", index=False, encoding="utf-8-sig")
    terms.to_csv(output_dir / "phase32_uniform_reference_functional_terms.csv", index=False, encoding="utf-8-sig")
    skipped.to_csv(output_dir / "phase32_uniform_reference_skipped.csv", index=False, encoding="utf-8-sig")
    comparison.to_csv(output_dir / "phase32_uniform_reference_vs_original.csv", index=False, encoding="utf-8-sig")
    write_report(output_dir / "phase32_uniform_reference_report.md", ref_map, metrics, terms, comparison, skipped)
    print("Phase 32C uniform reference reanalysis complete.")
    print(ref_map[["cohort", "reference_class_id", "reference_caution"]].to_string(index=False))


if __name__ == "__main__":
    main()
