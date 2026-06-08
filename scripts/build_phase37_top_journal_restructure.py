from __future__ import annotations

import argparse
import math
import os
import re
import shutil
import sys
import textwrap
import warnings
import zipfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from matplotlib import patches
from sklearn.metrics import roc_auc_score


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
PKG = ROOT / "manuscript" / "bmc_geriatrics_submission_burden_profiles_rescue"
TEX = PKG / "bmc_geriatrics_main.tex"
FIG_ROOT = ROOT / "figure_redraw" / "phase37_top_journal_restructure"
FIG_OUT = FIG_ROOT / "outputs"
INTERMEDIATE = FIG_ROOT / "intermediate_tables"

COHORT_ORDER = ["CHARLS", "ELSA", "HRS", "KLoSA", "LASI", "MHAS", "SHARE"]
STRICT_CORE = ["CHARLS", "ELSA", "HRS", "MHAS"]
SENSITIVITY = ["SHARE", "KLoSA", "LASI"]
VALIDATION_ORDER = ["CHARLS", "ELSA", "HRS", "MHAS", "SHARE", "KLoSA"]
DOMAIN_COLS = [
    "functional_score",
    "cognitive_score",
    "affective_score",
    "cardiometabolic_chronic_score",
]
DOMAIN_LABELS = ["Functional", "Cognitive", "Affective", "CM/chronic"]


def read_csv(name: str, **kwargs) -> pd.DataFrame:
    return pd.read_csv(OUT / name, low_memory=False, **kwargs)


def ensure_dirs() -> None:
    FIG_OUT.mkdir(parents=True, exist_ok=True)
    INTERMEDIATE.mkdir(parents=True, exist_ok=True)


def fmt_int(x: object) -> str:
    if pd.isna(x):
        return "NA"
    return f"{int(round(float(x))):,}"


def fmt_num(x: object, digits: int = 1) -> str:
    if pd.isna(x) or x == "":
        return "NA"
    return f"{float(x):.{digits}f}"


def fmt_pct(x: object, digits: int = 1) -> str:
    if pd.isna(x) or x == "":
        return "NA"
    return f"{float(x):.{digits}f}\\%"


def fmt_mean_sd(mean: object, sd: object, digits: int = 1) -> str:
    if pd.isna(mean):
        return "NA"
    if pd.isna(sd):
        return fmt_num(mean, digits)
    return f"{fmt_num(mean, digits)} ({fmt_num(sd, digits)})"


def fmt_p(value: object) -> str:
    if pd.isna(value):
        return "p=NA"
    p = float(value)
    if p < 0.001:
        return "p<0.001"
    return f"p={p:.3f}"


def tex_escape(value: object) -> str:
    if pd.isna(value):
        return "NA"
    text = str(value)
    repl = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(repl.get(ch, ch) for ch in text)


def plain_family(label: object) -> str:
    label = str(label)
    if "high_functional" in label and "spared_cardiometabolic_chronic" in label:
        return "Functional-dominant, CM-spared high burden"
    if "spared_cardiometabolic_chronic" in label:
        return "Intermediate burden, CM spared"
    if "high_cardiometabolic_chronic" in label and "spared_functional" in label:
        return "CM/chronic-high, function-spared"
    if "high_cardiometabolic_chronic" in label:
        return "CM/chronic-high mixed"
    if "high_affective" in label:
        return "Affective-dominant high burden"
    if "high_functional" in label:
        return "Functional-dominant high burden"
    if "severity_aligned" in label:
        return "Severity-aligned burden"
    return "Cohort-specific mixed"


def role_for(cohort: str) -> str:
    if cohort in STRICT_CORE:
        return "Strict-core primary"
    if cohort == "SHARE":
        return "Sensitivity: validation downgraded"
    if cohort == "KLoSA":
        return "Sensitivity: functional bridge"
    if cohort == "LASI":
        return "Sensitivity: baseline only"
    return "Sensitivity"


def plural(n: int, singular: str, plural_word: str | None = None) -> str:
    if n == 1:
        return f"{n} {singular}"
    return f"{n} {plural_word or singular + 's'}"


def family_interpretation(family: str, row: pd.Series | None = None) -> str:
    mapping = {
        "Intermediate burden, CM spared": "Lower cardiometabolic/chronic burden relative to other domains.",
        "CM/chronic-high, function-spared": "Chronic disease burden is prominent while functional limitation is relatively preserved.",
        "CM/chronic-high mixed": "CM/chronic burden is prominent without a stable function-spared pattern.",
        "Functional-dominant, CM-spared high burden": "Functional limitation dominates with relative cardiometabolic/chronic sparing.",
        "Functional-dominant high burden": "Functional limitation dominates the profile.",
        "Affective-dominant high burden": "Affective symptoms are the most prominent domain signal.",
        "Severity-aligned burden": "Domains move together as a general severity gradient.",
        "Cohort-specific mixed": "Cohort-specific pattern; do not pool as a recurrent clinical family.",
    }
    return mapping.get(family, "Descriptive family; inspect full class dictionary.")


def build_table1() -> pd.DataFrame:
    base = read_csv("phase36_baseline_clinical_characteristics.csv")
    miss = read_csv("phase36_missingness_included_excluded.csv")
    rows: list[dict[str, object]] = []
    for cohort in COHORT_ORDER:
        b = base[base["cohort"].eq(cohort)].iloc[0]
        m = miss[miss["cohort"].eq(cohort)].iloc[0]
        bmi = "NA" if pd.isna(b.get("bmi_mean")) else (
            f"{fmt_mean_sd(b['bmi_mean'], b['bmi_sd'])}; {fmt_num(b['bmi_pct_nonmissing'], 0)}% observed"
        )
        covariates = (
            f"BMI {bmi}; chronic count {fmt_mean_sd(b['chronic_count_mean'], b['chronic_count_sd'])}; "
            f"2+ chronic {fmt_num(b['chronic_ge2_pct'], 1)}%; smoking {fmt_num(b['smoking_raw_positive_pct'], 1)}%; "
            f"drinking {fmt_num(b['drinking_raw_positive_pct'], 1)}%"
        )
        selection = (
            f"Complete {fmt_int(m['complete_four_domain_n'])}/{fmt_int(m['source_women50_n'])} "
            f"({fmt_num(m['complete_four_domain_pct'], 1)}%); excluded age delta "
            f"{fmt_num(m['age_difference_excluded_minus_complete'], 1)} y"
        )
        if int(m["validation_available_n"]) == 0:
            validation = "unavailable in current cleaned pass"
        else:
            validation = (
                f"{fmt_int(m['validation_available_n'])}; events {fmt_int(m['validation_event_n'])} "
                f"({fmt_num(float(m['validation_event_n']) / float(m['validation_available_n']) * 100.0, 1)}%)"
            )
        rows.append(
            {
                "cohort": cohort,
                "primary_role": role_for(cohort),
                "source_women50_n": int(m["source_women50_n"]),
                "complete_four_domain_n": int(m["complete_four_domain_n"]),
                "complete_four_domain_pct": float(m["complete_four_domain_pct"]),
                "age_mean_sd": fmt_mean_sd(b["age_mean"], b["age_sd"]),
                "baseline_clinical_summary": covariates,
                "complete_case_selection": selection,
                "validation_summary": validation,
                "validation_available_n": int(m["validation_available_n"]),
                "validation_event_n": int(m["validation_event_n"]),
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "phase37_table1_baseline_clinical_characteristics.csv", index=False)
    out.to_csv(INTERMEDIATE / "phase37_table1_baseline_clinical_characteristics.csv", index=False)
    return out


def weighted_mean(df: pd.DataFrame, col: str) -> float:
    if df.empty or df["class_n"].sum() == 0:
        return float("nan")
    return float(np.average(df[col].astype(float), weights=df["class_n"].astype(float)))


def build_table2() -> pd.DataFrame:
    classes = read_csv("phase33_selected_class_dictionary.csv")
    classes["family"] = classes["profile_label"].map(plain_family)
    strict = classes[classes["cohort"].isin(STRICT_CORE)].copy()
    sens = classes[classes["cohort"].isin(SENSITIVITY)].copy()
    strict_total = int(strict["class_n"].sum())
    rows: list[dict[str, object]] = []
    for family, g in strict.groupby("family", sort=False):
        sens_g = sens[sens["family"].eq(family)]
        strict_cohorts = ", ".join(sorted(g["cohort"].unique()))
        sens_support = "None"
        if not sens_g.empty:
            sens_support = (
                f"{plural(len(sens_g), 'sensitivity class', 'sensitivity classes')} in "
                f"{', '.join(sorted(sens_g['cohort'].unique()))}"
            )
        rows.append(
            {
                "clinical_family": family,
                "strict_core_classes": int(g.shape[0]),
                "strict_core_cohorts": strict_cohorts,
                "strict_core_n": int(g["class_n"].sum()),
                "strict_core_pct": float(g["class_n"].sum() / strict_total * 100.0),
                "mean_functional_z": weighted_mean(g, "functional_score"),
                "mean_cognitive_z": weighted_mean(g, "cognitive_score"),
                "mean_affective_z": weighted_mean(g, "affective_score"),
                "mean_cardiometabolic_chronic_z": weighted_mean(g, "cardiometabolic_chronic_score"),
                "sensitivity_support": sens_support,
                "conservative_interpretation": family_interpretation(family),
            }
        )
    out = pd.DataFrame(rows).sort_values(["strict_core_n", "clinical_family"], ascending=[False, True])
    out.to_csv(OUT / "phase37_table2_strict_core_profile_families.csv", index=False)
    out.to_csv(INTERMEDIATE / "phase37_table2_strict_core_profile_families.csv", index=False)
    return out


def import_phase36():
    sys.path.insert(0, str(ROOT / "scripts"))
    import build_phase36_clinical_tables_and_robustness as phase36

    return phase36


def bootstrap_auc_ci(n_boot: int, seed: int = 3701) -> pd.DataFrame:
    phase36 = import_phase36()
    df = phase36.model_frame_for_lfo()
    cov_cols = ["age", "cov_education_raw", "cov_marital_status_raw", "cov_smoking_raw", "cov_drinking_raw"]
    profile_formula = (
        "functional_deterioration_ge_0_5sd ~ age + cov_education_raw + cov_marital_status_raw "
        "+ cov_smoking_raw + cov_drinking_raw + C(lfo_profile_class, Treatment(reference=1))"
    )
    cont_formula = (
        "functional_deterioration_ge_0_5sd ~ age + cov_education_raw + cov_marital_status_raw "
        "+ cov_smoking_raw + cov_drinking_raw + cognitive_score + affective_score + cardiometabolic_chronic_score"
    )
    rows: list[dict[str, object]] = []
    rng = np.random.default_rng(seed)
    warnings.filterwarnings("ignore", category=RuntimeWarning)

    for cohort in VALIDATION_ORDER:
        g = df[df["cohort"].eq(cohort)].copy()
        model_df = g.dropna(
            subset=[
                "functional_deterioration_ge_0_5sd",
                "lfo_profile_class",
                "cognitive_score",
                "affective_score",
                "cardiometabolic_chronic_score",
                *cov_cols,
            ]
        ).copy()
        if model_df.empty:
            continue
        model_df["lfo_profile_class"] = model_df["lfo_profile_class"].astype(int)
        prof_aucs: list[float] = []
        cont_aucs: list[float] = []
        deltas: list[float] = []
        n = model_df.shape[0]
        for _ in range(n_boot):
            idx = rng.integers(0, n, size=n)
            boot = model_df.iloc[idx].copy()
            y = boot["functional_deterioration_ge_0_5sd"].astype(int)
            if y.nunique() < 2 or boot["lfo_profile_class"].nunique() < 2:
                continue
            try:
                prof = smf.glm(profile_formula, data=boot, family=sm.families.Binomial()).fit(maxiter=80, disp=0)
                cont = smf.glm(cont_formula, data=boot, family=sm.families.Binomial()).fit(maxiter=80, disp=0)
                prof_pred = prof.predict(boot)
                cont_pred = cont.predict(boot)
                prof_auc = float(roc_auc_score(y, prof_pred))
                cont_auc = float(roc_auc_score(y, cont_pred))
            except Exception:
                continue
            if math.isfinite(prof_auc) and math.isfinite(cont_auc):
                prof_aucs.append(prof_auc)
                cont_aucs.append(cont_auc)
                deltas.append(prof_auc - cont_auc)

        def q(values: list[float], prob: float) -> float:
            return float(np.quantile(values, prob)) if values else float("nan")

        rows.append(
            {
                "cohort": cohort,
                "requested_bootstrap_n": n_boot,
                "successful_bootstrap_n": len(deltas),
                "profile_auc_p025": q(prof_aucs, 0.025),
                "profile_auc_p975": q(prof_aucs, 0.975),
                "continuous_auc_p025": q(cont_aucs, 0.025),
                "continuous_auc_p975": q(cont_aucs, 0.975),
                "delta_auc_p025": q(deltas, 0.025),
                "delta_auc_p975": q(deltas, 0.975),
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "phase37_auc_bootstrap_ci.csv", index=False)
    out.to_csv(INTERMEDIATE / "phase37_auc_bootstrap_ci.csv", index=False)
    return out


def build_table3(auc_ci: pd.DataFrame) -> pd.DataFrame:
    main = read_csv("phase36_functional_association_main.csv")
    main = main[main["cohort"].isin(VALIDATION_ORDER)].copy()
    ci = auc_ci.set_index("cohort") if not auc_ci.empty else pd.DataFrame()
    rows: list[dict[str, object]] = []
    for cohort in VALIDATION_ORDER:
        if cohort not in set(main["cohort"]):
            continue
        r = main[main["cohort"].eq(cohort)].iloc[0]
        role = "Strict-core primary" if cohort in STRICT_CORE else (
            "Sensitivity: validation downgraded" if cohort == "SHARE" else "Sensitivity: functional bridge"
        )
        delta_ci = "NA"
        success_n = 0
        if not ci.empty and cohort in ci.index:
            c = ci.loc[cohort]
            success_n = int(c["successful_bootstrap_n"])
            if success_n >= 30:
                delta_ci = f"{float(c['delta_auc_p025']):.3f} to {float(c['delta_auc_p975']):.3f}"
        rows.append(
            {
                "cohort": cohort,
                "analysis_role": role,
                "validation_n": int(r["validation_n"]),
                "events": int(r["events"]),
                "event_pct": float(r["event_pct"]),
                "absolute_risk_gradient": (
                    f"C{int(r['reference_class'])} {float(r['reference_event_pct']):.1f}% to "
                    f"C{int(r['highest_risk_class'])} {float(r['highest_risk_event_pct']):.1f}% "
                    f"(+{float(r['absolute_risk_difference_pct']):.1f} pp)"
                ),
                "adjusted_or_ci": (
                    f"{float(r['adjusted_or_highest_vs_class1']):.2f} "
                    f"({float(r['ci_low']):.2f}-{float(r['ci_high']):.2f}); {fmt_p(r['p_value'])}"
                ),
                "profile_auc": float(r["profile_auc"]),
                "continuous_auc": float(r["continuous_three_domain_auc"]),
                "delta_auc": float(r["delta_auc_profile_minus_continuous"]),
                "delta_auc_ci": delta_ci,
                "delta_aic_continuous_minus_profile_per_1000": float(
                    r["delta_aic_continuous_minus_profile_per_1000"]
                ),
                "successful_auc_bootstrap_n": success_n,
                "claim_status": str(r["claim_status"]),
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "phase37_table3_adjusted_functional_validation.csv", index=False)
    out.to_csv(INTERMEDIATE / "phase37_table3_adjusted_functional_validation.csv", index=False)
    return out


def build_action_audits() -> pd.DataFrame:
    mortality = read_csv("phase28_mortality_sensitivity_guardrails.csv")
    ph_flags = int(mortality["ph_screen_flag"].fillna(0).sum()) if "ph_screen_flag" in mortality.columns else 0
    no_major = int((mortality["mortality_interpretation"] == "secondary_no_major_ph_or_piecewise_flag").sum())
    csv_names = [p.name for p in OUT.glob("*.csv")]
    weight_files = [
        name
        for name in csv_names
        if re.search(r"weight|survey|psu|strat", name, re.I)
        and not name.startswith("phase37_")
        and "audit" not in name.lower()
    ]
    weight_inventory_hits = []
    cov_inventory = OUT / "phase13_covariate_candidate_inventory.csv"
    if cov_inventory.exists():
        text = cov_inventory.read_text(encoding="utf-8", errors="ignore")
        weight_inventory_hits = re.findall(r"[^,\n]*(?:weight|wt|survey|psu|strat)[^,\n]*", text, flags=re.I)

    hard_outcome_inventory = read_csv("phase5_outcome_variable_inventory.csv")
    fall_ready = "fall" in ";".join(hard_outcome_inventory.get("functional_variables", pd.Series(dtype=str)).fillna(""))
    rows = [
        {
            "reviewer_issue": "Clinical contribution overclaimed",
            "phase37_action": "Reframed manuscript as a harmonized descriptive burden-profile atlas with validation guardrails; removed stable endotype and prediction-superiority language.",
            "status": "implemented",
            "manuscript_location": "title, abstract, Background, Results, Discussion",
        },
        {
            "reviewer_issue": "Women-only rationale too weak",
            "phase37_action": "Reframed as a scoped older-women descriptive analysis rather than a sex-difference claim; explicitly says male comparator and sex-interaction analyses were not performed.",
            "status": "partially implemented; male comparison requires new analysis",
            "manuscript_location": "Background; Strengths and limitations",
        },
        {
            "reviewer_issue": "Seven-cohort harmonization not sufficient for common profile-family claim",
            "phase37_action": "Primary evidence now limited to strict-core cohorts (CHARLS, ELSA, HRS, MHAS); SHARE, KLoSA and LASI moved to sensitivity/descriptive tiers.",
            "status": "implemented",
            "manuscript_location": "Methods; Table 1; Table 2; Fig 1",
        },
        {
            "reviewer_issue": "GMM classes unstable and near-singular",
            "phase37_action": "GMM retained only as descriptive clustering; robustness and near-singular covariance are stated as guardrails rather than buried.",
            "status": "implemented for interpretation; more GMM bootstrap still needed for top-journal claim",
            "manuscript_location": "Methods; Discussion; Additional file 17",
        },
        {
            "reviewer_issue": "Functional endpoint leakage",
            "phase37_action": "Leave-functional-domain-out validation promoted to the only validation table and figure; primary profiles are not claimed as validated prediction models.",
            "status": "implemented",
            "manuscript_location": "Methods; Table 3; Fig 3",
        },
        {
            "reviewer_issue": "Lack of independent hard endpoint",
            "phase37_action": f"Mortality outputs found but kept secondary: {no_major} cohorts had no major PH/piecewise flag and {ph_flags} cohorts had PH flags; hospitalization/institutionalization/care-dependence endpoints were not harmonized in current outputs.",
            "status": "data-limited; not forced into primary result",
            "manuscript_location": "Results; Discussion; phase37_hard_outcome_and_weight_audit.csv",
        },
        {
            "reviewer_issue": "No survey weights/design handling",
            "phase37_action": f"No harmonized weight/PSU/strata output files found; candidate inventory hits={len(weight_inventory_hits)}, output files={len(weight_files)}. Marked as not implemented until codebook/raw extraction.",
            "status": "blocked by current harmonized output set",
            "manuscript_location": "Strengths and limitations; phase37_hard_outcome_and_weight_audit.csv",
        },
        {
            "reviewer_issue": "Complete-case selection bias",
            "phase37_action": "Included-vs-excluded age differences and domain missingness were moved into main Table 1 and Additional file 13.",
            "status": "implemented",
            "manuscript_location": "Table 1; Results",
        },
        {
            "reviewer_issue": "ORs for common outcomes can overstate effects",
            "phase37_action": "Table 3 now leads with absolute-risk gradients and treats adjusted ORs as secondary within-cohort associations.",
            "status": "implemented",
            "manuscript_location": "Table 3; Fig 3",
        },
        {
            "reviewer_issue": "AUC delta lacked uncertainty",
            "phase37_action": "Added cohort-specific bootstrap CI for delta AUC using 100 requested resamples per cohort; no prediction-superiority claim is made.",
            "status": "implemented as guardrail uncertainty, not as formal model-validation study",
            "manuscript_location": "Table 3; Additional file 18",
        },
    ]
    audit = pd.DataFrame(rows)
    audit.to_csv(OUT / "phase37_reviewer_issue_action_matrix.csv", index=False)
    audit.to_csv(INTERMEDIATE / "phase37_reviewer_issue_action_matrix.csv", index=False)

    hard_rows = [
        {
            "domain": "Mortality",
            "local_evidence": f"{len(list(OUT.glob('*mortality*.csv')))} mortality CSV outputs; PH flags in {ph_flags} cohort rows; {no_major} rows without major PH/piecewise flag.",
            "phase37_decision": "Keep mortality secondary with guardrails; not a primary hard-outcome validation endpoint.",
        },
        {
            "domain": "Hospitalization/institutionalization/care dependence",
            "local_evidence": "No harmonized phase output found for these endpoints in the current cleaned-data pass.",
            "phase37_decision": "Do not introduce these endpoints without a new raw/codebook extraction.",
        },
        {
            "domain": "Falls",
            "local_evidence": f"Fall variable appears only as a KLoSA bridge functional candidate: {fall_ready}.",
            "phase37_decision": "Do not use as cross-cohort hard endpoint.",
        },
        {
            "domain": "Survey weights/design",
            "local_evidence": f"Output files matching weight/survey/PSU/strata: {len(weight_files)}; candidate inventory hits: {len(weight_inventory_hits)}.",
            "phase37_decision": "Blocked until harmonized weight, strata and PSU variables are confirmed per cohort.",
        },
        {
            "domain": "Male comparator/sex interaction",
            "local_evidence": "Current analysis intentionally filters women 50+ and has no male analytic table.",
            "phase37_decision": "State scope limitation; do not claim women-specific mechanisms.",
        },
    ]
    hard = pd.DataFrame(hard_rows)
    hard.to_csv(OUT / "phase37_hard_outcome_and_weight_audit.csv", index=False)
    hard.to_csv(INTERMEDIATE / "phase37_hard_outcome_and_weight_audit.csv", index=False)
    return audit


def write_panel_mapping() -> None:
    ensure_dirs()
    panels = [
        {
            "figure": "Fig1",
            "panel": "Flow",
            "role": "STROBE-style denominator and tier lock",
            "atlas_major_class": "Multi-panel evidence chain and mechanism",
            "atlas_subtype": "workflow",
            "reader_question": "Which cohorts enter strict-core construction and validation, and which are sensitivity only?",
            "data_type": "cohort-level denominator table",
            "runtime": "Python",
            "env": "research-py312",
            "intermediate_file": "outputs/phase37_table1_baseline_clinical_characteristics.csv",
            "reason": "A flow chart is the clearest guardrail for denominator non-interchangeability.",
        },
        {
            "figure": "Fig2",
            "panel": "Strict-core heatmap",
            "role": "Simplified clinical burden-profile family summary",
            "atlas_major_class": "Multivariate omics pattern",
            "atlas_subtype": "clustered heatmap",
            "reader_question": "What recurrent domain-burden shapes remain in strict-core cohorts?",
            "data_type": "family-level weighted domain z-scores",
            "runtime": "Python",
            "env": "research-py312",
            "intermediate_file": "outputs/phase37_table2_strict_core_profile_families.csv",
            "reason": "The full 28-class heatmap is too dense for the main manuscript; family-level z-scores answer the clinical question.",
        },
        {
            "figure": "Fig3",
            "panel": "Absolute-risk and adjusted OR forest",
            "role": "Functional validation guardrail",
            "atlas_major_class": "Group comparison and distribution",
            "atlas_subtype": "forest plot",
            "reader_question": "Do profile classes show within-cohort functional deterioration gradients, and are they better than continuous scores?",
            "data_type": "cohort-level validation risks, adjusted ORs, AUC deltas",
            "runtime": "Python",
            "env": "research-py312",
            "intermediate_file": "outputs/phase37_table3_adjusted_functional_validation.csv",
            "reason": "A forest/risk display foregrounds clinical effect size and uncertainty instead of crowded model diagnostics.",
        },
        {
            "figure": "Fig4",
            "panel": "Harmonization matrix",
            "role": "Measurement-risk matrix",
            "atlas_major_class": "Multi-panel evidence chain and mechanism",
            "atlas_subtype": "dashboard",
            "reader_question": "Where are domain measures non-equivalent or downgraded?",
            "data_type": "cohort-domain harmonization crosswalk",
            "runtime": "Python",
            "env": "research-py312",
            "intermediate_file": "outputs/phase28_domain_harmonization_dictionary.csv",
            "reason": "Kept as a guardrail figure because measurement risk is central to the claim boundary.",
        },
    ]
    df = pd.DataFrame(panels)
    df.to_csv(FIG_ROOT / "panel_inventory.tsv", sep="\t", index=False)
    df.to_csv(FIG_ROOT / "panel_template_candidates.tsv", sep="\t", index=False)
    mapping_lines = [
        "# Phase 37 Panel Visual Mapping",
        "",
        "Palette: restrained clinical palette with teal for strict-core evidence, amber for sensitivity tiers, gray for unavailable or downgraded evidence, and red only for risk/guardrail emphasis.",
        "",
    ]
    for _, row in df.iterrows():
        mapping_lines.extend(
            [
                f"## {row['figure']} {row['panel']}",
                f"- Manuscript role: {row['role']}",
                f"- Atlas major class: {row['atlas_major_class']}",
                f"- Atlas subtype: {row['atlas_subtype']}",
                f"- Reader question: {row['reader_question']}",
                f"- Data type: {row['data_type']}",
                f"- Runtime: {row['runtime']}",
                f"- Env: {row['env']}",
                f"- Intermediate file: {row['intermediate_file']}",
                f"- Reason: {row['reason']}",
                "",
            ]
        )
    (FIG_ROOT / "panel_visual_mapping.md").write_text("\n".join(mapping_lines), encoding="utf-8")
    (FIG_ROOT / "panel_final_selection.md").write_text(
        "# Phase 37 Panel Final Selection\n\n"
        "Selected main-manuscript route: Fig1 STROBE-style flow, Fig2 strict-core family heatmap, "
        "Fig3 functional validation forest/risk display, Fig4 harmonization risk matrix.\n",
        encoding="utf-8",
    )
    (FIG_ROOT / "redraw_log.md").write_text(
        "# Phase 37 Redraw Log\n\n"
        "Rendered from real project intermediate tables generated by scripts/build_phase37_top_journal_restructure.py.\n",
        encoding="utf-8",
    )


def save_figure(fig: plt.Figure, stem: str) -> None:
    ensure_dirs()
    for suffix in [".pdf", ".svg", ".png"]:
        target = PKG / f"{stem}{suffix}"
        fig.savefig(target, bbox_inches="tight", dpi=300)
        shutil.copyfile(target, FIG_OUT / f"{stem}{suffix}")


def draw_fig1_flow(table1: pd.DataFrame, table3: pd.DataFrame) -> None:
    total_source = int(table1["source_women50_n"].sum())
    total_complete = int(table1["complete_four_domain_n"].sum())
    core_complete = int(table1[table1["cohort"].isin(STRICT_CORE)]["complete_four_domain_n"].sum())
    sens_complete = total_complete - core_complete
    core_val = int(table3[table3["cohort"].isin(STRICT_CORE)]["validation_n"].sum())
    core_events = int(table3[table3["cohort"].isin(STRICT_CORE)]["events"].sum())
    sens_val = int(table3[table3["cohort"].isin(["SHARE", "KLoSA"])]["validation_n"].sum())
    sens_events = int(table3[table3["cohort"].isin(["SHARE", "KLoSA"])]["events"].sum())

    fig, ax = plt.subplots(figsize=(9.4, 7.0))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    colors = {
        "core": "#0F6B6E",
        "sens": "#C9821A",
        "gray": "#6C757D",
        "light": "#F1F3F5",
        "line": "#343A40",
    }

    def wrap_body(body: str, width_chars: int) -> str:
        return "\n".join(textwrap.fill(line, width=width_chars) for line in body.split("\n"))

    def box(x: float, y: float, w: float, h: float, title: str, body: str, color: str, width_chars: int = 48) -> None:
        rect = patches.FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.012,rounding_size=0.012",
            linewidth=1.0,
            edgecolor=color,
            facecolor="#FFFFFF",
        )
        ax.add_patch(rect)
        ax.add_patch(patches.Rectangle((x, y + h - 0.035), w, 0.035, facecolor=color, edgecolor=color))
        ax.text(x + 0.018, y + h - 0.018, title, ha="left", va="center", fontsize=9.5, color="white", fontweight="bold")
        ax.text(
            x + 0.018,
            y + h - 0.065,
            wrap_body(body, width_chars),
            ha="left",
            va="top",
            fontsize=8.2,
            color="#212529",
            linespacing=1.25,
        )

    box(
        0.18,
        0.82,
        0.64,
        0.13,
        "Source screen",
        f"Women aged 50+ across 7 cohorts\nN = {total_source:,}",
        colors["gray"],
        62,
    )
    ax.annotate("", xy=(0.5, 0.78), xytext=(0.5, 0.82), arrowprops=dict(arrowstyle="-|>", lw=1.2, color=colors["line"]))
    box(
        0.18,
        0.64,
        0.64,
        0.13,
        "Complete four-domain construction set",
        f"N = {total_complete:,}; source, complete-domain and validation denominators are separated",
        colors["gray"],
        68,
    )
    ax.annotate("", xy=(0.32, 0.58), xytext=(0.45, 0.64), arrowprops=dict(arrowstyle="-|>", lw=1.2, color=colors["line"]))
    ax.annotate("", xy=(0.68, 0.58), xytext=(0.55, 0.64), arrowprops=dict(arrowstyle="-|>", lw=1.2, color=colors["line"]))

    box(
        0.04,
        0.38,
        0.42,
        0.20,
        "Strict-core primary evidence",
        f"CHARLS, ELSA, HRS, MHAS\nConstruction N = {core_complete:,}\nModel N = {core_val:,}; events = {core_events:,}",
        colors["core"],
        44,
    )
    box(
        0.54,
        0.38,
        0.42,
        0.20,
        "Sensitivity/descriptive evidence",
        f"SHARE validation downgraded; KLoSA bridge; LASI baseline only\nConstruction N = {sens_complete:,}\nModel N = {sens_val:,}; events = {sens_events:,}",
        colors["sens"],
        42,
    )
    ax.annotate("", xy=(0.25, 0.31), xytext=(0.25, 0.38), arrowprops=dict(arrowstyle="-|>", lw=1.2, color=colors["line"]))
    ax.annotate("", xy=(0.75, 0.31), xytext=(0.75, 0.38), arrowprops=dict(arrowstyle="-|>", lw=1.2, color=colors["line"]))
    box(
        0.04,
        0.13,
        0.42,
        0.18,
        "Allowed primary claim",
        "Descriptive burden-profile atlas with within-cohort functional-association guardrails.\nNo stable endotype or prediction-superiority claim.",
        colors["core"],
        38,
    )
    box(
        0.54,
        0.13,
        0.42,
        0.18,
        "Allowed sensitivity claim",
        "Measurement and validation limits are shown explicitly.\nNo pooled strict baseline denominator for downgraded tiers.",
        colors["sens"],
        38,
    )
    ax.text(0.5, 0.045, "Phase 37 denominator lock", ha="center", va="center", fontsize=8.2, color="#495057")
    save_figure(fig, "figure1_strobe_flow_phase37")
    plt.close(fig)


def draw_fig2_heatmap(table2: pd.DataFrame) -> None:
    plot = table2.copy().sort_values("strict_core_n", ascending=True)
    matrix = plot[
        ["mean_functional_z", "mean_cognitive_z", "mean_affective_z", "mean_cardiometabolic_chronic_z"]
    ].astype(float).to_numpy()
    families = plot["clinical_family"].tolist()
    n_pct = [f"N {int(n):,}; {pct:.1f}%" for n, pct in zip(plot["strict_core_n"], plot["strict_core_pct"])]

    fig, ax = plt.subplots(figsize=(9.2, 5.8))
    im = ax.imshow(matrix, aspect="auto", cmap="RdBu_r", vmin=-1.2, vmax=1.2)
    ax.set_xticks(np.arange(len(DOMAIN_LABELS)))
    ax.set_xticklabels(DOMAIN_LABELS, fontsize=9)
    ax.set_yticks(np.arange(len(families)))
    ax.set_yticklabels([textwrap.fill(f, 28) for f in families], fontsize=8.4)
    ax.tick_params(length=0)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ax.text(j, i, f"{matrix[i, j]:.2f}", ha="center", va="center", fontsize=8.2, color="#212529")
    for i, label in enumerate(n_pct):
        ax.text(len(DOMAIN_LABELS) + 0.15, i, label, ha="left", va="center", fontsize=8.4, color="#343A40")
    ax.text(len(DOMAIN_LABELS) + 0.15, len(families) - 0.52, "Strict-core support", ha="left", va="bottom", fontsize=8.8, fontweight="bold")
    ax.set_xlim(-0.5, len(DOMAIN_LABELS) + 2.4)
    cbar = fig.colorbar(im, ax=ax, shrink=0.72, pad=0.03)
    cbar.set_label("Weighted mean burden z-score", fontsize=8.5)
    cbar.ax.tick_params(labelsize=8)
    ax.set_frame_on(False)
    fig.text(0.02, 0.015, "Strict-core cohorts only: CHARLS, ELSA, HRS and MHAS. Higher values indicate worse burden.", fontsize=8.2, color="#495057")
    save_figure(fig, "figure2_strict_core_profile_heatmap_phase37")
    plt.close(fig)


def draw_fig3_forest(table3: pd.DataFrame) -> None:
    plot = table3.copy()
    plot["order"] = plot["cohort"].map({c: i for i, c in enumerate(["KLoSA", "SHARE", "MHAS", "HRS", "ELSA", "CHARLS"])})
    plot = plot.sort_values("order")
    y = np.arange(plot.shape[0])
    colors = ["#0F6B6E" if c in STRICT_CORE else "#C9821A" for c in plot["cohort"]]
    ors = []
    lows = []
    highs = []
    for text in plot["adjusted_or_ci"]:
        m = re.match(r"([0-9.]+) \(([0-9.]+)-([0-9.]+)\)", text)
        ors.append(float(m.group(1)) if m else np.nan)
        lows.append(float(m.group(2)) if m else np.nan)
        highs.append(float(m.group(3)) if m else np.nan)

    fig, ax = plt.subplots(figsize=(9.4, 5.8))
    ax.axvline(1.0, color="#343A40", lw=1.0, ls="--")
    for yi, orv, low, high, color in zip(y, ors, lows, highs, colors):
        ax.plot([low, high], [yi, yi], color=color, lw=1.8)
        ax.scatter(orv, yi, s=56, color=color, edgecolor="white", linewidth=0.8, zorder=3)
    ax.set_xscale("log")
    ax.set_xlim(0.75, 4.4)
    ax.set_xlabel("Adjusted odds ratio for highest-risk vs reference profile class", fontsize=9)
    ax.set_yticks(y)
    ax.set_yticklabels(plot["cohort"].tolist(), fontsize=9)
    ax.grid(axis="x", color="#DEE2E6", lw=0.6)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)

    x_text = 4.65
    for yi, (_, r) in zip(y, plot.iterrows()):
        risk = str(r["absolute_risk_gradient"]).replace(" to ", " -> ")
        delta = f"dAUC {float(r['delta_auc']):.3f}"
        ax.text(x_text, yi + 0.14, risk, ha="left", va="center", fontsize=7.8, color="#212529", clip_on=False)
        ax.text(x_text, yi - 0.14, delta, ha="left", va="center", fontsize=7.8, color="#6C757D", clip_on=False)
    ax.text(x_text, y[-1] + 0.55, "Absolute risk gradient and comparator", ha="left", va="bottom", fontsize=8.4, fontweight="bold", clip_on=False)
    ax.set_ylim(-0.6, y[-1] + 0.85)
    fig.subplots_adjust(right=0.60)
    fig.text(0.02, 0.015, "Teal = strict-core primary; amber = sensitivity/downgraded. dAUC is profile minus continuous three-domain model.", fontsize=8.1, color="#495057")
    save_figure(fig, "figure3_functional_validation_forest_phase37")
    plt.close(fig)


def draw_figures(table1: pd.DataFrame, table2: pd.DataFrame, table3: pd.DataFrame) -> None:
    write_panel_mapping()
    draw_fig1_flow(table1, table3)
    draw_fig2_heatmap(table2)
    draw_fig3_forest(table3)


def tex_table1(table1: pd.DataFrame) -> str:
    rows = []
    for _, r in table1.iterrows():
        rows.append(
            " & ".join(
                [
                    tex_escape(r["cohort"]),
                    tex_escape(r["primary_role"]),
                    tex_escape(f"{fmt_int(r['source_women50_n'])} source; {fmt_int(r['complete_four_domain_n'])} complete ({fmt_num(r['complete_four_domain_pct'], 1)}%)"),
                    tex_escape(f"Age {r['age_mean_sd']}; {r['baseline_clinical_summary']}"),
                    tex_escape(f"{r['complete_case_selection']}; validation {r['validation_summary']}"),
                ]
            )
            + r"\\"
        )
    return r"""\begin{table}[!htbp]
\caption{Baseline clinical characteristics, complete-case selection and validation availability}\label{tab:baseline-clinical}
\tiny
\setlength{\tabcolsep}{1pt}
\rowcolors{2}{tablegray}{white}
\begin{tabular}{@{}>{\raggedright\arraybackslash}p{0.08\textwidth}>{\raggedright\arraybackslash}p{0.14\textwidth}>{\raggedright\arraybackslash}p{0.14\textwidth}>{\raggedright\arraybackslash}p{0.29\textwidth}>{\raggedright\arraybackslash}p{0.23\textwidth}@{}}
\toprule
\rowcolor{tablehead}
Cohort & Analysis role & Construction denominator & Baseline clinical profile & Selection and validation\\
\midrule
""" + "\n".join(rows) + r"""
\botrule
\end{tabular}
\rowcolors{2}{white}{white}
\footnotetext{This table is the main denominator table. Source-screen, complete four-domain construction and validation denominators are not interchangeable. BMI is shown only when available in the cleaned harmonized files. Validation events are functional deterioration events, not hard clinical endpoints.}
\end{table}
"""


def tex_table2(table2: pd.DataFrame) -> str:
    rows = []
    for _, r in table2.iterrows():
        domain = (
            f"F {float(r['mean_functional_z']):.2f}; Cog {float(r['mean_cognitive_z']):.2f}; "
            f"Aff {float(r['mean_affective_z']):.2f}; CM {float(r['mean_cardiometabolic_chronic_z']):.2f}"
        )
        rows.append(
            " & ".join(
                [
                    tex_escape(r["clinical_family"]),
                    tex_escape(f"{plural(int(r['strict_core_classes']), 'class', 'classes')} in {r['strict_core_cohorts']}"),
                    tex_escape(f"{fmt_int(r['strict_core_n'])} ({fmt_num(r['strict_core_pct'], 1)}%)"),
                    tex_escape(domain),
                    tex_escape(r["sensitivity_support"]),
                    tex_escape(r["conservative_interpretation"]),
                ]
            )
            + r"\\"
        )
    return r"""\begin{table}[!htbp]
\caption{Strict-core clinical burden-profile families and sensitivity support}\label{tab:profile-families}
\tiny
\setlength{\tabcolsep}{1pt}
\rowcolors{2}{tablegray}{white}
\begin{tabular}{@{}>{\raggedright\arraybackslash}p{0.15\textwidth}>{\raggedright\arraybackslash}p{0.15\textwidth}>{\raggedright\arraybackslash}p{0.10\textwidth}>{\raggedright\arraybackslash}p{0.16\textwidth}>{\raggedright\arraybackslash}p{0.16\textwidth}>{\raggedright\arraybackslash}p{0.20\textwidth}@{}}
\toprule
\rowcolor{tablehead}
Clinical family & Strict-core evidence & Strict-core N & Weighted domain z profile & Sensitivity support & Conservative interpretation\\
\midrule
""" + "\n".join(rows) + r"""
\botrule
\end{tabular}
\rowcolors{2}{white}{white}
\footnotetext{Strict-core evidence is restricted to CHARLS, ELSA, HRS and MHAS. SHARE, KLoSA and LASI are reported only as sensitivity or descriptive support. F = functional, Cog = cognitive, Aff = affective symptoms and CM = cardiometabolic/chronic disease burden. Higher z-scores indicate worse burden.}
\end{table}
"""


def tex_table3(table3: pd.DataFrame) -> str:
    rows = []
    for _, r in table3.iterrows():
        delta_aic = float(r["delta_aic_continuous_minus_profile_per_1000"])
        comparator = (
            f"Profile AUC {float(r['profile_auc']):.3f}; continuous AUC {float(r['continuous_auc']):.3f}; "
            f"delta AUC {float(r['delta_auc']):.3f} ({r['delta_auc_ci']}); "
            f"delta AIC/1000 {delta_aic:.1f}"
        )
        rows.append(
            " & ".join(
                [
                    tex_escape(f"{r['cohort']}; {r['analysis_role']}"),
                    tex_escape(f"{fmt_int(r['validation_n'])}; {fmt_int(r['events'])} events ({fmt_num(r['event_pct'], 1)}%)"),
                    tex_escape(r["absolute_risk_gradient"]),
                    tex_escape(r["adjusted_or_ci"]),
                    tex_escape(comparator),
                    tex_escape(r["claim_status"]),
                ]
            )
            + r"\\"
        )
    return r"""\begin{table}[!htbp]
\caption{Functional deterioration validation guardrail with absolute risk, adjusted association and continuous-score comparator}\label{tab:functional-association}
\tiny
\setlength{\tabcolsep}{1pt}
\rowcolors{2}{tablegray}{white}
\begin{tabular}{@{}>{\raggedright\arraybackslash}p{0.13\textwidth}>{\raggedright\arraybackslash}p{0.13\textwidth}>{\raggedright\arraybackslash}p{0.16\textwidth}>{\raggedright\arraybackslash}p{0.13\textwidth}>{\raggedright\arraybackslash}p{0.25\textwidth}>{\raggedright\arraybackslash}p{0.12\textwidth}@{}}
\toprule
\rowcolor{tablehead}
Cohort and role & Validation N/events & Absolute-risk gradient & Adjusted OR & Model comparator & Claim status\\
\midrule
""" + "\n".join(rows) + r"""
\botrule
\end{tabular}
\rowcolors{2}{white}{white}
\footnotetext{Profiles in this table were rebuilt after leaving the functional domain out to reduce endpoint leakage. Adjusted ORs compare the highest-risk class with class 1 and adjust for age, education, marital status, smoking and drinking. Delta AUC is profile model minus continuous three-domain model; negative values favor continuous scores. Parentheses show bootstrap 2.5th to 97.5th percentile intervals from 100 requested resamples per cohort when at least 30 bootstrap fits succeeded.}
\end{table}
"""


def update_tex(table1: pd.DataFrame, table2: pd.DataFrame, table3: pd.DataFrame) -> None:
    text = TEX.read_text(encoding="utf-8")
    text = re.sub(
        r"\\title\[[^\]]+\]\{[^{}]+\}",
        r"\\title[Multidomain burden-profile atlas among older women]{Harmonized multidomain burden-profile atlas among older women across seven international aging cohorts: a descriptive validation-guardrail analysis}",
        text,
        count=1,
    )
    abstract = (
        r"\abstract{\textbf{Background:} Multidomain geriatric indicators can identify clinically recognizable patterns of limitation, symptoms and chronic disease, but categorical profiles are easily overinterpreted when denominator selection, harmonization, endpoint leakage and model stability are not explicit. "
        r"\textbf{Methods:} We analyzed women aged 50 years or older in CHARLS, ELSA, HRS, KLoSA, LASI, MHAS and SHARE. Four burden domains were harmonized within cohort and oriented so that higher scores indicated worse burden. After severe-review triage, the primary evidence set was restricted to strict-core cohorts with usable construction and validation evidence (CHARLS, ELSA, HRS and MHAS). SHARE, KLoSA and LASI were retained as sensitivity or descriptive tiers. Gaussian mixture models were used only as descriptive profile-construction tools, with covariance, bootstrap, algorithm-sensitivity, missingness and leave-functional-domain-out validation guardrails. "
        r"\textbf{Results:} The source screen included 79,938 women, of whom 76,293 had complete four-domain profile assignments. Strict-core primary construction included 29,058 women and strict-core functional validation included 25,113 women with 7,925 functional deterioration events. Recurrent strict-core profile families included cardiometabolic/chronic-spared intermediate burden, cardiometabolic/chronic-high function-spared burden and functional-dominant high-burden patterns. In functional validation, profile classes showed within-cohort absolute-risk gradients, but continuous three-domain scores generally retained equal or better discrimination. All selected four-domain Gaussian mixture models had near-singular covariance diagnostics. "
        r"\textbf{Conclusions:} The defensible contribution is a harmonized descriptive atlas of multidomain burden profiles among older women, not evidence for stable latent endotypes or prediction superiority.}"
    )
    start = text.index(r"\abstract{")
    end = text.index(r"\keywords{")
    text = text[:start] + abstract + "\n\n" + text[end:]

    bg_methods = r"""\section{Background}\label{sec:background}

Functional ability, intrinsic capacity and multimorbidity are central to geriatric assessment and health-system planning for ageing populations \cite{who2015worldreport,who2017icope,cesari2018evidence,barnett2012multimorbidity}. Frailty phenotypes and deficit-accumulation indices summarize vulnerability \cite{fried2001frailty,rockwood2007frailty,clegg2013frailty}, but they can compress clinically different domain patterns into a single severity continuum.

This study is intentionally scoped to older women. Women have longer survival, higher late-life disability burden and different patterns of affective symptoms, multimorbidity and care needs \cite{crimmins2011gender}. However, the current analysis does not test sex differences, sex interactions or women-specific mechanisms. The women-only design is therefore framed as a focused descriptive atlas for an older-women population rather than as evidence that the profiles are unique to women.

Recent multidomain trajectory and symptom-cluster studies suggest that functional, cognitive, mood and chronic-disease indicators can evolve jointly \cite{quinones2022multidimensional,zhang2025symptomclusters,jiao2026predeath}. The remaining clinical and epidemiologic problem is whether such profiles can be interpreted without overstating harmonized measurement equivalence, categorical subtype stability or prediction performance. We therefore revised the analysis around a conservative objective: to describe clinically interpretable burden-profile families, make measurement risks visible and test validation guardrails that define what claims are and are not defensible.

\section{Methods}\label{sec:methods}

\subsection{Cohorts and analytic population}

We used cleaned cohort files from CHARLS, ELSA, HRS, KLoSA, LASI, MHAS and SHARE \cite{zhao2014charls,steptoe2013elsa,sonnega2014hrs,keis2026klosa,perianayagam2022lasi,wong2017mhas,borschsupan2013share}. The analytic population was women aged 50 years or older at the cohort-specific selected baseline or analysis wave. Sex coding was confirmed from local Working Data Stata value labels and do-files as \texttt{ragender=0} for women and \texttt{ragender=1} for men. Source-screen, complete-domain, profile-construction and validation denominators were separated in line with observational-study reporting principles \cite{vonelm2007strobe}.

\subsection{Domain construction and harmonization review}

Four domains were constructed: functional limitation, cognitive burden, affective symptoms and cardiometabolic/chronic disease burden. Functional items were anchored to activities of daily living and instrumental activities of daily living constructs where available \cite{katz1963adl,lawton1969iadl}; SHARE affective symptoms used EURO-D information where available \cite{prince1999eurod}. Scores were standardized within cohort and oriented so that higher values indicated worse burden. Retrospective harmonization review treated similar orientation as insufficient evidence for item identity or transportable measurement equivalence \cite{doiron2013bioshare,fortier2017maelstrom}.

\subsection{Primary and sensitivity evidence tiers}

The primary evidence tier was restricted to strict-core cohorts with complete construction and usable functional validation evidence: CHARLS, ELSA, HRS and MHAS. SHARE was retained as strict construction but validation-downgraded sensitivity evidence because functional validation diagnostics remained problematic. KLoSA was retained as bridge sensitivity because the baseline functional domain relied on grip/performance/falls information. LASI was retained for baseline profile construction only because a usable follow-up validation denominator was not available in the current cleaned-data pass. This tiering prevents baseline-only, bridge and downgraded evidence from being pooled as a single strict primary denominator.

\subsection{Profile construction and robustness diagnostics}

Cohort-specific Gaussian mixture models with two to five classes were fit to the four domain scores as model-based descriptive clustering tools \cite{mclachlan2000finite}. The selected model used the lowest BIC among converged models with minimum class size at least 5\%, while recognizing that class enumeration statistics should not be treated as clinical truth without sensitivity checks \cite{nylund2007classes,hennig2015trueclusters}. Component covariance diagnostics, bootstrap stability checks and algorithm sensitivity comparisons were used as guardrails. Profiles were interpreted as descriptive strata, not stable latent disease entities.

\subsection{Functional validation guardrail}

The main follow-up endpoint was functional deterioration of at least 0.5 SD from baseline. Because the original four-domain profile includes baseline function, functional deterioration is vulnerable to endpoint leakage. The primary validation guardrail therefore rebuilt profiles after leaving the functional domain out and compared profile classes with continuous cognitive, affective and cardiometabolic/chronic domain scores. Models used minimal-core covariate adjustment for age, education, marital status, smoking and drinking. Absolute risks were emphasized before adjusted odds ratios because functional deterioration was common.

"""
    start = text.index(r"\section{Background}")
    end = text.index(r"\section{Results}")
    text = text[:start] + bg_methods + text[end:]

    results_discussion = r"""\section{Results}\label{sec:results}

\subsection{Denominator lock, clinical characteristics and complete-case selection}

The source screen included 79,938 women aged 50 years or older, and 76,293 had complete four-domain profile assignments. The strict-core primary construction set comprised 29,058 women from CHARLS, ELSA, HRS and MHAS. The sensitivity/descriptive construction set comprised 47,235 women from SHARE, KLoSA and LASI. Complete-case selection was not neutral: excluded participants were older than included complete-domain participants in every cohort, including HRS (+10.4 years) and ELSA (+6.6 years). Table~\ref{tab:baseline-clinical} and Figure~\ref{fig:strobe-flow} show the denominator lock, baseline clinical characteristics, selection audit and validation availability.

""" + tex_table1(table1) + r"""

\subsection{Strict-core profile families}

In the strict-core cohorts, selected GMM classes were collapsed into clinically readable burden-profile families rather than treated as fixed disease entities. Recurrent strict-core patterns included cardiometabolic/chronic-spared intermediate burden, cardiometabolic/chronic-high function-spared burden, severity-aligned burden and smaller functional-dominant high-burden patterns (Table~\ref{tab:profile-families}; Figure~\ref{fig:profile-heatmap}). Sensitivity support from SHARE, KLoSA and LASI is reported separately and does not convert those cohorts into primary evidence.

""" + tex_table2(table2) + r"""

\FloatBarrier

\subsection{Functional validation guardrail}

Strict-core functional validation included 25,113 women and 7,925 functional deterioration events. Highest-risk leave-functional-domain-out profile classes showed higher crude functional deterioration risk than reference classes in the strict-core cohorts, with absolute risk differences of 16.0 to 23.4 percentage points. However, continuous three-domain scores generally retained equal or better discrimination, and the table is therefore interpreted as within-cohort association evidence rather than prediction superiority (Table~\ref{tab:functional-association}; Figure~\ref{fig:functional-forest}). SHARE and KLoSA are shown only as sensitivity rows.

""" + tex_table3(table3) + r"""

\subsection{Harmonization, hard-outcome and algorithm guardrails}

The harmonization matrix remained central to interpretation (Figure~\ref{fig:harmonization-risk}). Functional-domain strictness differed across cohorts: CHARLS used IADL-only information, HRS used ADL-only information, KLoSA used a bridge proxy and SHARE remained validation-downgraded. Cognitive batteries were cohort-specific, SHARE affective symptoms used EURO-D, and cardiometabolic/chronic disease indicators differed in lipid/cholesterol availability. Mortality analyses were available but were kept secondary because proportional-hazards or piecewise time-drift flags were present in several cohorts. Hospitalization, institutionalization, care dependence and survey-design weights were not harmonized in the current output set and were not introduced into the main claims.

\FloatBarrier

\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth,height=0.72\textheight,keepaspectratio]{figure1_strobe_flow_phase37.pdf}
\caption{STROBE-style denominator lock and cohort-tier flow. Source-screen, complete-domain construction and validation denominators are separated. Model denominators in the lower boxes use the minimal-core functional-validation analytic set. Strict-core primary evidence is restricted to CHARLS, ELSA, HRS and MHAS; SHARE, KLoSA and LASI remain sensitivity or descriptive tiers.}
\label{fig:strobe-flow}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth,height=0.74\textheight,keepaspectratio]{figure2_strict_core_profile_heatmap_phase37.pdf}
\caption{Strict-core burden-profile family heatmap. Rows show weighted mean domain z-scores for profile families observed in CHARLS, ELSA, HRS and MHAS. Higher z-scores indicate worse burden. Sensitivity cohorts are not used to define the primary families.}
\label{fig:profile-heatmap}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth,height=0.72\textheight,keepaspectratio]{figure3_functional_validation_forest_phase37.pdf}
\caption{Functional deterioration validation guardrail. Points and horizontal lines show adjusted odds ratios and 95\% confidence intervals for the highest-risk leave-functional-domain-out profile class compared with class 1. Text annotations show crude absolute-risk gradients and delta AUC for profile versus continuous three-domain models.}
\label{fig:functional-forest}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth,height=0.78\textheight,keepaspectratio]{figure4_harmonization_risk_matrix-re.pdf}
\caption{Cohort-domain harmonization risk matrix. Cells show source tier, non-missing percentage and the principal construct used for each burden domain. The matrix makes the main measurement guardrails visible and should be read as a measurement-risk figure rather than as a biological result figure.}
\label{fig:harmonization-risk}
\end{figure}

\FloatBarrier

\section{Discussion}\label{sec:discussion}

This revision narrows the paper to a defensible clinical and epidemiologic contribution: a harmonized descriptive atlas of multidomain burden profiles among older women, paired with transparent validation and measurement guardrails. The main clinical value is not prediction superiority. It is a structured map showing that similar overall burden can arise through different domain combinations, including cardiometabolic/chronic-dominant patterns with relative functional sparing and functional-dominant high-burden patterns.

The negative findings are part of the main result. Continuous three-domain scores generally matched or outperformed categorical profile classes for functional deterioration discrimination. All selected four-domain Gaussian mixture models triggered near-singular covariance diagnostics, and algorithm sensitivity did not uniformly reproduce the selected class solutions. These findings mean the profiles should not be presented as stable latent endotypes, treatment strata or transportable risk tools.

The women-only scope is also deliberately conservative. The analysis addresses older women as a clinically important population with high late-life disability burden, but it does not establish sex-specific mechanisms. A top-journal version would require male comparator analyses, sex-interaction tests and harmonized women-specific exposures such as reproductive history, menopause-related factors or caregiving burden. Those analyses were outside the current cleaned-output set.

\section{Strengths and limitations}\label{sec:limitations}

Strengths include the seven-cohort scope, codebook-confirmed sex coding, explicit denominator locking, separation of strict-core primary evidence from sensitivity tiers, baseline clinical characterization, included-versus-excluded missingness auditing, item-level harmonization review, leave-functional-domain-out validation and algorithm-robustness diagnostics. Limitations remain substantial. Domain measures were harmonized by orientation and within-cohort standardization but were not instrument-identical across cohorts. Survey weights, strata and primary sampling units were not harmonized in the current output set. Validation remained within-cohort association rather than transport validation. LASI lacked a follow-up validation denominator, SHARE was validation-downgraded and KLoSA used a functional bridge. Mortality was available only as secondary evidence with proportional-hazards and piecewise guardrails. The current study therefore cannot claim population prevalence, stable latent endotypes, independent hard-outcome validation or superiority over continuous domain scores.

\section{Conclusions}\label{sec:conclusions}

Across seven international ageing cohorts, multidomain burden profiles among older women can be described, tiered and audited. The reviewer-ready conclusion is conservative: profiles are descriptive clinical strata with important harmonization and stability caveats, while continuous domain scores remain the stronger functional-validation comparator in the current analyses.

"""
    start = text.index(r"\section{Results}")
    end = text.index(r"\section*{Abbreviations}")
    text = text[:start] + results_discussion + text[end:]

    add_files = r"""\section*{Additional files}

Additional file 1: Item-level harmonization crosswalk.\\
Additional file 2: Cohort tier lock.\\
Additional file 3: Decoupled validation comparison.\\
Additional file 4: GMM stability summary.\\
Additional file 5: GMM covariance diagnostics.\\
Additional file 6: Functional endpoint leakage audit.\\
Additional file 7: Full selected class dictionary.\\
Additional file 8: Clinical burden-profile family summary.\\
Additional file 9: Harmonization risk matrix data.\\
Additional file 10: Clinical and epidemiology skill-search report.\\
Additional file 11: Phase 37 reviewer issue action matrix.\\
Additional file 12: Phase 37 hard-outcome and survey-weight audit.\\
Additional file 13: Phase 37 baseline clinical characteristics and selection table.\\
Additional file 14: Phase 37 strict-core profile-family table.\\
Additional file 15: Phase 37 adjusted functional validation table.\\
Additional file 16: Functional deterioration class-level risks and adjusted associations.\\
Additional file 17: GMM algorithm robustness sensitivity.\\
Additional file 18: Phase 37 AUC bootstrap intervals.\\
Supplementary Figure S1: Original cohort validation dashboard.\\
Supplementary Figure S2: Original compact profile heatmap backup.\\
Supplementary Figure S3: Original compact validation and stability guardrail backup.

"""
    start = text.index(r"\section*{Additional files}")
    end = text.index(r"\bibliography{")
    text = text[:start] + add_files + text[end:]
    TEX.write_text(text, encoding="utf-8")


def copy_additional_files() -> None:
    stale_names = [
        "additional_file_11_baseline_clinical_characteristics.csv",
        "additional_file_12_missingness_included_excluded.csv",
        "additional_file_13_functional_association_class_risks.csv",
        "additional_file_14_gmm_algorithm_robustness.csv",
    ]
    for name in stale_names:
        p = PKG / name
        if p.exists():
            p.unlink()
    mapping = {
        "additional_file_11_phase37_reviewer_issue_action_matrix.csv": OUT / "phase37_reviewer_issue_action_matrix.csv",
        "additional_file_12_phase37_hard_outcome_and_weight_audit.csv": OUT / "phase37_hard_outcome_and_weight_audit.csv",
        "additional_file_13_phase37_table1_baseline_clinical_characteristics.csv": OUT / "phase37_table1_baseline_clinical_characteristics.csv",
        "additional_file_14_phase37_table2_strict_core_profile_families.csv": OUT / "phase37_table2_strict_core_profile_families.csv",
        "additional_file_15_phase37_table3_adjusted_functional_validation.csv": OUT / "phase37_table3_adjusted_functional_validation.csv",
        "additional_file_16_functional_association_class_risks.csv": OUT / "phase36_functional_association_class_risks.csv",
        "additional_file_17_gmm_algorithm_robustness.csv": OUT / "phase36_gmm_algorithm_robustness.csv",
        "additional_file_18_phase37_auc_bootstrap_ci.csv": OUT / "phase37_auc_bootstrap_ci.csv",
    }
    for name, src in mapping.items():
        if src.exists():
            shutil.copyfile(src, PKG / name)


def update_readme() -> None:
    readme = PKG / "README_BMC_Geriatrics_burden_profiles_rescue.md"
    text = readme.read_text(encoding="utf-8") if readme.exists() else "# BMC Geriatrics burden profile rescue package\n"
    add = """

## Phase 37 top-journal severe-review restructure

- Reframed the manuscript as a harmonized descriptive burden-profile atlas with validation guardrails.
- Locked strict-core primary evidence to CHARLS, ELSA, HRS and MHAS.
- Moved SHARE, KLoSA and LASI into validation-downgraded, bridge or baseline-only sensitivity tiers.
- Replaced the audit-style main table with baseline clinical characteristics, complete-case selection and validation availability.
- Rebuilt Table 2 as strict-core profile families with sensitivity support separated.
- Rebuilt Table 3 around absolute functional deterioration risk, adjusted ORs and continuous-score comparator metrics.
- Replaced Fig1-3 with a STROBE-style denominator flow, strict-core burden-family heatmap and functional validation forest/risk plot.
- Added reviewer action and hard-outcome/survey-weight audits as additional files.
"""
    if "## Phase 37 top-journal severe-review restructure" not in text:
        text += add
    readme.write_text(text, encoding="utf-8")


def rebuild_zips() -> None:
    source_zip = PKG / "bmc_geriatrics_submission_burden_profiles_rescue_source_only.zip"
    pdf_zip = PKG / "bmc_geriatrics_submission_burden_profiles_rescue_pdf_ready.zip"
    names = [
        "bmc_geriatrics_main.tex",
        "bmc_geriatrics_refs.bib",
        "sn-jnl.cls",
        "sn-vancouver-num.bst",
        "figure1_strobe_flow_phase37.pdf",
        "figure1_strobe_flow_phase37.svg",
        "figure1_strobe_flow_phase37.png",
        "figure2_strict_core_profile_heatmap_phase37.pdf",
        "figure2_strict_core_profile_heatmap_phase37.svg",
        "figure2_strict_core_profile_heatmap_phase37.png",
        "figure3_functional_validation_forest_phase37.pdf",
        "figure3_functional_validation_forest_phase37.svg",
        "figure3_functional_validation_forest_phase37.png",
        "figure4_harmonization_risk_matrix-re.pdf",
        "figure4_harmonization_risk_matrix.svg",
        "figure4_harmonization_risk_matrix.png",
        "supplementary_figure_s1_cohort_validation_dashboard.png",
        "supplementary_figure_s1_cohort_validation_dashboard.pdf",
        "supplementary_figure_s2_profile_heatmap_backup.png",
        "supplementary_figure_s2_profile_heatmap_backup.pdf",
        "supplementary_figure_s3_validation_stability_backup.png",
        "supplementary_figure_s3_validation_stability_backup.pdf",
        "README_BMC_Geriatrics_burden_profiles_rescue.md",
    ]
    names.extend([p.name for p in sorted(PKG.glob("additional_file_*.csv"))])
    with zipfile.ZipFile(source_zip, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for name in names:
            p = PKG / name
            if p.exists():
                z.write(p, arcname=name)
    with zipfile.ZipFile(pdf_zip, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for name in [*names, "bmc_geriatrics_main.pdf"]:
            p = PKG / name
            if p.exists():
                z.write(p, arcname=name)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip-only", action="store_true")
    parser.add_argument("--bootstrap-n", type=int, default=int(os.environ.get("PHASE37_BOOTSTRAP_N", "100")))
    args = parser.parse_args()
    if args.zip_only:
        rebuild_zips()
        print(PKG / "bmc_geriatrics_submission_burden_profiles_rescue_source_only.zip")
        print(PKG / "bmc_geriatrics_submission_burden_profiles_rescue_pdf_ready.zip")
        return

    ensure_dirs()
    table1 = build_table1()
    table2 = build_table2()
    auc_ci = bootstrap_auc_ci(args.bootstrap_n)
    table3 = build_table3(auc_ci)
    build_action_audits()
    draw_figures(table1, table2, table3)
    update_tex(table1, table2, table3)
    copy_additional_files()
    update_readme()
    print(OUT / "phase37_reviewer_issue_action_matrix.csv")
    print(OUT / "phase37_hard_outcome_and_weight_audit.csv")
    print(OUT / "phase37_table1_baseline_clinical_characteristics.csv")
    print(OUT / "phase37_table2_strict_core_profile_families.csv")
    print(OUT / "phase37_table3_adjusted_functional_validation.csv")
    print(OUT / "phase37_auc_bootstrap_ci.csv")
    print(PKG / "bmc_geriatrics_main.tex")


if __name__ == "__main__":
    main()
