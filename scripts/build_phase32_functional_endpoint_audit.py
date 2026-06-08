from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd


RUN_DATE = "2026-06-02"


def safe_pct(num: float, den: float) -> float:
    if den == 0 or pd.isna(den):
        return np.nan
    return round(float(num) / float(den) * 100, 2)


def safe_corr(a: pd.Series, b: pd.Series) -> float:
    frame = pd.DataFrame({"a": pd.to_numeric(a, errors="coerce"), "b": pd.to_numeric(b, errors="coerce")}).dropna()
    if len(frame) < 3 or frame["a"].nunique() < 2 or frame["b"].nunique() < 2:
        return np.nan
    return round(float(frame["a"].corr(frame["b"])), 4)


def read_csv(output_dir: Path, name: str) -> pd.DataFrame:
    return pd.read_csv(output_dir / name, encoding="utf-8-sig", low_memory=False)


def build_endpoint_audit(output_dir: Path) -> pd.DataFrame:
    screen = read_csv(output_dir, "phase5_participant_outcome_screen.csv")
    domain = read_csv(output_dir, "phase28_domain_harmonization_dictionary.csv")
    table1 = read_csv(output_dir, "phase11_table1_cohort_readiness.csv")
    terms = read_csv(output_dir, "phase14_functional_covariate_model_terms.csv")
    terms = terms[
        terms["outcome"].eq("functional_deterioration_ge_0_5sd")
        & terms["model_type"].eq("endotype")
        & terms["adjustment"].eq("minimal_core")
        & terms["term"].str.contains("endotype_class", regex=False)
    ].copy()

    func_domain = domain[domain["domain"].eq("functional")].copy()
    rows = []
    for keys, group in screen.groupby(["analysis_set", "analysis_tier", "cohort"], dropna=False):
        analysis_set, analysis_tier, cohort = keys
        available = group[group["functional_deterioration_available"].eq(1)].copy()
        available["functional_deterioration_ge_0_5sd"] = pd.to_numeric(
            available["functional_deterioration_ge_0_5sd"], errors="coerce"
        )
        available = available.dropna(subset=["functional_deterioration_ge_0_5sd"])
        fd = func_domain[
            func_domain["analysis_set"].eq(analysis_set)
            & func_domain["cohort"].eq(cohort)
        ]
        t = terms[terms["cohort"].eq(cohort)].copy()
        finite_or = pd.to_numeric(t["or"], errors="coerce").replace([np.inf, -np.inf], np.nan)
        finite_ci_high = pd.to_numeric(t["ci_high"], errors="coerce").replace([np.inf, -np.inf], np.nan)
        max_or = finite_or.max() if not finite_or.dropna().empty else np.nan
        min_or = finite_or.min() if not finite_or.dropna().empty else np.nan
        max_ci_high = finite_ci_high.max() if not finite_ci_high.dropna().empty else np.nan
        implausible_or_flag = int(
            (not pd.isna(max_or) and max_or >= 20)
            or (not pd.isna(min_or) and min_or <= 0.05)
            or (not pd.isna(max_ci_high) and max_ci_high >= 50)
            or t["ci_high"].astype(str).str.contains("inf", case=False, na=False).any()
        )

        if available.empty:
            event_n = 0
            event_pct = np.nan
            base_event_corr = np.nan
            change_event_corr = np.nan
            baseline_mean_event = np.nan
            baseline_mean_nonevent = np.nan
            event_pct_lowest_quartile = np.nan
            event_pct_highest_quartile = np.nan
        else:
            event = available["functional_deterioration_ge_0_5sd"].astype(int)
            event_n = int(event.sum())
            event_pct = safe_pct(event_n, len(available))
            base_event_corr = safe_corr(available["functional_score"], event)
            change_event_corr = safe_corr(available["functional_deterioration_change"], event)
            baseline_mean_event = available.loc[event.eq(1), "functional_score"].mean()
            baseline_mean_nonevent = available.loc[event.eq(0), "functional_score"].mean()
            ranked = available.dropna(subset=["functional_score"]).copy()
            if len(ranked) >= 20 and ranked["functional_score"].nunique() >= 4:
                ranked["baseline_function_quartile"] = pd.qcut(
                    ranked["functional_score"].rank(method="first"), q=4, labels=["Q1_lowest", "Q2", "Q3", "Q4_highest"]
                )
                q = ranked.groupby("baseline_function_quartile", observed=False)["functional_deterioration_ge_0_5sd"].mean()
                event_pct_lowest_quartile = round(float(q.get("Q1_lowest", np.nan)) * 100, 2)
                event_pct_highest_quartile = round(float(q.get("Q4_highest", np.nan)) * 100, 2)
            else:
                event_pct_lowest_quartile = np.nan
                event_pct_highest_quartile = np.nan

        role = table1.loc[table1["cohort"].eq(cohort), "manuscript_role"]
        role_value = role.iloc[0] if not role.empty else ""
        source_tier = fd["source_tier"].iloc[0] if not fd.empty else ""
        variables = fd["variables"].iloc[0] if not fd.empty else ""
        endpoint_kind = "followup_functional_score_minus_baseline_functional_score_ge_0_5sd"
        coupling_level = "same_domain_score_change"
        if str(role_value) == "baseline_profile_only_current_csv":
            main_status = "exclude_no_followup_validation"
        elif str(source_tier) == "bridge":
            main_status = "bridge_sensitivity_only"
        elif implausible_or_flag:
            main_status = "exclude_or_redefine_until_endpoint_decoupled"
        else:
            main_status = "usable_only_as_coupled_within_cohort_association"

        rows.append(
            {
                "analysis_set": analysis_set,
                "analysis_tier": analysis_tier,
                "cohort": cohort,
                "manuscript_role": role_value,
                "functional_source_tier": source_tier,
                "functional_variables": variables,
                "endpoint_kind": endpoint_kind,
                "baseline_profile_input_domain": "functional_score",
                "coupling_level": coupling_level,
                "functional_validation_n": int(len(available)),
                "functional_event_n": event_n,
                "functional_event_pct": event_pct,
                "baseline_function_event_corr": base_event_corr,
                "change_event_corr": change_event_corr,
                "baseline_function_mean_event": round(float(baseline_mean_event), 4) if not pd.isna(baseline_mean_event) else np.nan,
                "baseline_function_mean_nonevent": round(float(baseline_mean_nonevent), 4)
                if not pd.isna(baseline_mean_nonevent)
                else np.nan,
                "event_pct_lowest_baseline_function_quartile": event_pct_lowest_quartile,
                "event_pct_highest_baseline_function_quartile": event_pct_highest_quartile,
                "minimal_core_max_or": round(float(max_or), 4) if not pd.isna(max_or) else np.nan,
                "minimal_core_min_or": round(float(min_or), 4) if not pd.isna(min_or) else np.nan,
                "minimal_core_max_ci_high": round(float(max_ci_high), 4) if not pd.isna(max_ci_high) else np.nan,
                "implausible_or_or_separation_flag": implausible_or_flag,
                "phase32_main_evidence_status": main_status,
            }
        )
    return pd.DataFrame(rows).sort_values(["analysis_tier", "cohort"])


def build_report(path: Path, audit: pd.DataFrame) -> None:
    flagged = audit[audit["phase32_main_evidence_status"].ne("usable_only_as_coupled_within_cohort_association")].copy()
    lines = [
        "# Phase 32A Functional Endpoint Leakage Audit",
        "",
        f"Date: {RUN_DATE}",
        "",
        "## Decision",
        "",
        "The current primary functional endpoint is a same-domain score-change endpoint: follow-up functional score minus baseline functional score >= 0.5 SD. Because baseline functional score is also one of the four profile-construction inputs, this endpoint should not be used to claim independent clinical prediction.",
        "",
        "Use current functional models only as coupled within-cohort association evidence unless a decoupled endpoint is rebuilt.",
        "",
        "## Status By Cohort",
        "",
        "| Cohort | Tier | N | Events | Event % | Functional variables | Max OR | Main evidence status |",
        "|---|---|---:|---:|---:|---|---:|---|",
    ]
    for _, row in audit.iterrows():
        lines.append(
            f"| {row['cohort']} | {row['analysis_tier']} | {row['functional_validation_n']} | "
            f"{row['functional_event_n']} | {row['functional_event_pct']} | {row['functional_variables']} | "
            f"{row['minimal_core_max_or']} | {row['phase32_main_evidence_status']} |"
        )
    lines.extend(["", "## Flagged Rows", ""])
    if flagged.empty:
        lines.append("No rows were flagged beyond same-domain coupling.")
    else:
        lines.append("| Cohort | Reason |")
        lines.append("|---|---|")
        for _, row in flagged.iterrows():
            lines.append(f"| {row['cohort']} | {row['phase32_main_evidence_status']} |")
    lines.extend(
        [
            "",
            "## Required Next Step",
            "",
            "Phase 32B should rebuild validation with a non-circular endpoint or a leave-functional-domain-out profile design before the manuscript is rewritten.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    root = Path.cwd()
    output_dir = root / "outputs"
    audit = build_endpoint_audit(output_dir)
    audit.to_csv(output_dir / "phase32_functional_endpoint_leakage_audit.csv", index=False, encoding="utf-8-sig")
    build_report(output_dir / "phase32_functional_endpoint_leakage_audit.md", audit)
    print("Phase 32A functional endpoint audit complete.")
    print(audit[["cohort", "phase32_main_evidence_status"]].to_string(index=False))


if __name__ == "__main__":
    main()
