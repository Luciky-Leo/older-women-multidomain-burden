from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


RUN_DATE = "2026-06-01"
DOMAIN_NAMES = ("functional", "cognitive", "affective", "cardiometabolic_chronic")


def read_csv(output_dir: Path, name: str) -> pd.DataFrame:
    path = output_dir / name
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path, low_memory=False)


def numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def build_domain_dictionary(output_dir: Path) -> pd.DataFrame:
    missing = read_csv(output_dir, "phase3_domain_missingness.csv")
    table1 = read_csv(output_dir, "phase11_table1_cohort_readiness.csv")[
        ["analysis_set", "analysis_tier", "cohort", "manuscript_role", "baseline_women_age50plus_n"]
    ]
    missing = missing.merge(table1, on=["analysis_set", "analysis_tier", "cohort"], how="left")
    rows = []
    for _, row in missing.iterrows():
        for domain in DOMAIN_NAMES:
            rows.append(
                {
                    "analysis_set": row["analysis_set"],
                    "analysis_tier": row["analysis_tier"],
                    "manuscript_role": row["manuscript_role"],
                    "cohort": row["cohort"],
                    "wave": row["wave"],
                    "domain": domain,
                    "source_tier": row[f"{domain}_source"],
                    "variables": row[f"{domain}_variables"],
                    "nonmissing_n": row[f"{domain}_nonmissing_n"],
                    "nonmissing_pct": row[f"{domain}_nonmissing_pct"],
                    "complete_four_domain_n": row["complete_four_domain_n"],
                    "baseline_women_age50plus_n": row["baseline_women_age50plus_n"],
                }
            )
    return pd.DataFrame(rows)


def build_gmm_selection_table(output_dir: Path) -> pd.DataFrame:
    metrics = read_csv(output_dir, "phase4_gmm_model_metrics.csv")
    selected = read_csv(output_dir, "phase4_best_model_summary.csv")[
        ["analysis_set", "analysis_tier", "cohort", "wave", "n_classes", "selection_rule"]
    ].rename(columns={"n_classes": "selected_n_classes"})
    out = metrics.merge(selected, on=["analysis_set", "analysis_tier", "cohort", "wave"], how="left")
    out["selected_model"] = (numeric(out["n_classes"]) == numeric(out["selected_n_classes"])).astype(int)
    columns = [
        "analysis_set",
        "analysis_tier",
        "cohort",
        "wave",
        "n",
        "n_classes",
        "selected_model",
        "bic",
        "aic",
        "converged",
        "n_iter",
        "entropy_separation",
        "mean_max_posterior",
        "min_class_n",
        "min_class_pct",
        "profile_interpretation",
        "max_domain_deviation_from_severity",
        "monotonic_domain_count",
        "selection_rule",
    ]
    return out[[column for column in columns if column in out.columns]].sort_values(
        ["analysis_tier", "cohort", "n_classes"]
    )


def build_validation_metrics(output_dir: Path) -> pd.DataFrame:
    comp = read_csv(output_dir, "phase5_domain_comparator_comparison.csv")
    comp = comp[comp["outcome"].isin(["functional_deterioration_ge_0_5sd", "chronic_progression_ge_1_condition"])].copy()
    comp_rows = []
    for _, row in comp.iterrows():
        comp_rows.append(
            {
                "analysis_set": row["analysis_set"],
                "analysis_tier": row["analysis_tier"],
                "cohort": row["cohort"],
                "endpoint": row["outcome_label"],
                "endpoint_role": row["outcome_priority"],
                "model_family": "logistic_regression",
                "n": row["n_endotype"],
                "events": row["events_endotype"],
                "event_pct": row["event_pct_endotype"],
                "median_followup_years": "",
                "fit_metric_name": "AIC",
                "endotype_fit": row["aic_endotype"],
                "four_domain_fit": row["aic_four_domain_scores"],
                "severity_tertile_fit": row["aic_severity_tertile"],
                "endotype_auc": row["auc_endotype"],
                "four_domain_auc": row["auc_four_domain_scores"],
                "severity_tertile_auc": row["auc_severity_tertile"],
                "delta_fit_severity_tertile_minus_endotype": row["delta_aic_severity_tertile_minus_endotype"],
                "delta_fit_four_domain_minus_endotype": row["delta_aic_four_domain_scores_minus_endotype"],
                "delta_auc_endotype_minus_severity_tertile": row["delta_auc_endotype_minus_severity_tertile"],
                "delta_auc_endotype_minus_four_domain": row["delta_auc_endotype_minus_four_domain_scores"],
            }
        )

    mortality = read_csv(output_dir, "phase6_mortality_model_comparison.csv")
    mortality_rows = []
    for _, row in mortality.iterrows():
        mortality_rows.append(
            {
                "analysis_set": row["analysis_set"],
                "analysis_tier": row["analysis_tier"],
                "cohort": row["cohort"],
                "endpoint": "All-cause mortality",
                "endpoint_role": "secondary",
                "model_family": "cox_proportional_hazards",
                "n": row["n_endotype"],
                "events": row["events_endotype"],
                "event_pct": row["event_pct_endotype"],
                "median_followup_years": row["median_followup_time_years_endotype"],
                "fit_metric_name": "partial_AIC",
                "endotype_fit": row["partial_aic_endotype"],
                "four_domain_fit": row["partial_aic_four_domain_scores"],
                "severity_tertile_fit": row["partial_aic_severity_tertile"],
                "endotype_auc": "",
                "four_domain_auc": "",
                "severity_tertile_auc": "",
                "delta_fit_severity_tertile_minus_endotype": row["delta_partial_aic_severity_tertile_minus_endotype"],
                "delta_fit_four_domain_minus_endotype": row["delta_partial_aic_four_domain_scores_minus_endotype"],
                "delta_auc_endotype_minus_severity_tertile": "",
                "delta_auc_endotype_minus_four_domain": "",
            }
        )
    out = pd.DataFrame(comp_rows + mortality_rows)
    return out.sort_values(["endpoint_role", "endpoint", "analysis_tier", "cohort"]).reset_index(drop=True)


def build_outcome_specification() -> pd.DataFrame:
    rows = [
        {
            "endpoint": "Functional deterioration >= 0.5 SD",
            "endpoint_role": "primary",
            "model_family": "logistic_regression",
            "time_origin": "cohort-specific endotype construction wave",
            "availability_rule": "participant has a later wave with comparable functional-domain score",
            "event_definition": "follow-up functional score minus baseline functional score >= 0.5 SD",
            "main_comparators": "severity tertile; continuous severity; matched functional score; four-domain scores",
        },
        {
            "endpoint": "Chronic progression >= 1 condition",
            "endpoint_role": "secondary",
            "model_family": "logistic_regression",
            "time_origin": "cohort-specific endotype construction wave",
            "availability_rule": "participant has baseline and later chronic-condition counts",
            "event_definition": "follow-up chronic-condition count minus baseline count >= 1",
            "main_comparators": "severity tertile; continuous severity; matched chronic score; four-domain scores",
        },
        {
            "endpoint": "All-cause mortality",
            "endpoint_role": "secondary",
            "model_family": "cox_proportional_hazards",
            "time_origin": "cohort-specific endotype construction wave/interview year",
            "availability_rule": "participant has baseline interview year and death or censoring follow-up",
            "event_definition": "death year at or after baseline interview year; otherwise censored at last interview year",
            "main_comparators": "severity tertile; continuous severity; four-domain scores",
        },
    ]
    return pd.DataFrame(rows)


def build_mortality_guardrails(output_dir: Path) -> pd.DataFrame:
    ph = read_csv(output_dir, "phase8_mortality_ph_diagnostic_summary.csv")
    piecewise = read_csv(output_dir, "phase9_mortality_piecewise_stability.csv")
    drift = (
        piecewise.groupby(["analysis_set", "analysis_tier", "cohort"], dropna=False)
        .agg(
            piecewise_terms_tested=("term_label", "nunique"),
            large_time_drift_terms=("large_time_drift", "sum"),
            direction_change_terms=("direction_change", "sum"),
            max_late_vs_early_hr_ratio=("late_vs_early_hr_ratio", "max"),
        )
        .reset_index()
    )
    out = ph.merge(drift, on=["analysis_set", "analysis_tier", "cohort"], how="left")
    out["large_time_drift_terms"] = numeric(out["large_time_drift_terms"]).fillna(0).astype(int)
    out["direction_change_terms"] = numeric(out["direction_change_terms"]).fillna(0).astype(int)
    out["mortality_interpretation"] = "secondary_with_guardrail"
    out.loc[
        (numeric(out["ph_screen_flag"]).fillna(0).eq(0))
        & (numeric(out["large_time_drift_terms"]).fillna(0).eq(0)),
        "mortality_interpretation",
    ] = "secondary_no_major_ph_or_piecewise_flag"
    return out.sort_values(["analysis_tier", "cohort"]).reset_index(drop=True)


def write_report(output_dir: Path, domain: pd.DataFrame, gmm: pd.DataFrame, validation: pd.DataFrame, guardrails: pd.DataFrame) -> None:
    functional = validation[validation["endpoint"].eq("Functional deterioration >= 0.5 SD")]
    mortality = validation[validation["endpoint"].eq("All-cause mortality")]
    selected = gmm[gmm["selected_model"].eq(1)]
    lines = [
        "# Phase 28 Reviewer-Ready Analytic Assets",
        "",
        f"Date: {RUN_DATE}",
        "",
        "## Generated files",
        "",
        "- `outputs/phase28_domain_harmonization_dictionary.csv`",
        "- `outputs/phase28_gmm_selection_table.csv`",
        "- `outputs/phase28_validation_metrics_main.csv`",
        "- `outputs/phase28_outcome_model_specification.csv`",
        "- `outputs/phase28_mortality_sensitivity_guardrails.csv`",
        "",
        "## Key checks",
        "",
        f"- Domain dictionary rows: {len(domain)}.",
        f"- Selected GMM cohort rows: {len(selected)}.",
        f"- Functional validation rows: {len(functional)}, N={int(numeric(functional['n']).sum())}, events={int(numeric(functional['events']).sum())}.",
        f"- Mortality validation rows: {len(mortality)}, N={int(numeric(mortality['n']).sum())}, deaths={int(numeric(mortality['events']).sum())}.",
        f"- Mortality guardrail rows: {len(guardrails)}.",
        "",
        "## SHARE status",
        "",
        "SHARE is now included as a strict-primary wave-1 endotype-construction cohort using ADL/IADL functional-domain evidence from Phase 27. KLoSA remains bridge-sensitivity because its functional domain is performance/frailty based. LASI remains baseline-profile only for follow-up validation.",
    ]
    (output_dir / "phase28_reviewer_ready_assets_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build reviewer-facing supplementary analytic assets.")
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    domain = build_domain_dictionary(args.output_dir)
    gmm = build_gmm_selection_table(args.output_dir)
    validation = build_validation_metrics(args.output_dir)
    outcome_spec = build_outcome_specification()
    guardrails = build_mortality_guardrails(args.output_dir)

    domain.to_csv(args.output_dir / "phase28_domain_harmonization_dictionary.csv", index=False, encoding="utf-8-sig")
    gmm.to_csv(args.output_dir / "phase28_gmm_selection_table.csv", index=False, encoding="utf-8-sig")
    validation.to_csv(args.output_dir / "phase28_validation_metrics_main.csv", index=False, encoding="utf-8-sig")
    outcome_spec.to_csv(args.output_dir / "phase28_outcome_model_specification.csv", index=False, encoding="utf-8-sig")
    guardrails.to_csv(args.output_dir / "phase28_mortality_sensitivity_guardrails.csv", index=False, encoding="utf-8-sig")
    write_report(args.output_dir, domain, gmm, validation, guardrails)
    print("Phase 28 reviewer-ready analytic assets complete.")


if __name__ == "__main__":
    main()
