from __future__ import annotations

import argparse
import re
import shutil
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
PKG = ROOT / "manuscript" / "bmc_geriatrics_submission_burden_profiles_rescue"
TEX = PKG / "bmc_geriatrics_main.tex"

COHORT_ORDER = ["CHARLS", "ELSA", "HRS", "KLoSA", "LASI", "MHAS", "SHARE"]
STRICT_CORE = ["CHARLS", "ELSA", "HRS", "MHAS"]
SENSITIVITY = ["SHARE", "KLoSA", "LASI"]
DOMAIN_COLS = [
    "functional_score",
    "cognitive_score",
    "affective_score",
    "cardiometabolic_chronic_score",
]


def read_csv(name: str, **kwargs) -> pd.DataFrame:
    return pd.read_csv(OUT / name, low_memory=False, **kwargs)


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


def fmt_int(value: object) -> str:
    if pd.isna(value) or value == "":
        return "NA"
    return f"{int(round(float(value))):,}"


def fmt_num(value: object, digits: int = 1) -> str:
    if pd.isna(value) or value == "":
        return "NA"
    return f"{float(value):.{digits}f}"


def fmt_mean_sd(mean: object, sd: object, digits: int = 1) -> str:
    if pd.isna(mean):
        return "NA"
    if pd.isna(sd):
        return fmt_num(mean, digits)
    return f"{fmt_num(mean, digits)} ({fmt_num(sd, digits)})"


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


def family_interpretation(family: str) -> str:
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


def weighted_mean(df: pd.DataFrame, col: str) -> float:
    if df.empty or df["class_n"].sum() == 0:
        return float("nan")
    return float(np.average(pd.to_numeric(df[col], errors="coerce"), weights=df["class_n"].astype(float)))


def education_distribution(covars: pd.DataFrame, cohort: str) -> str:
    g = covars[covars["cohort"].eq(cohort)].copy()
    if g.empty or "cov_education_raw" not in g.columns:
        return "education raw 1/2/3 NA"
    values = pd.to_numeric(g["cov_education_raw"], errors="coerce")
    values = values.dropna()
    if values.empty:
        return "education raw 1/2/3 NA"
    den = float(values.size)
    parts = []
    for code in [1, 2, 3]:
        parts.append(f"{(values.eq(code).sum() / den * 100.0):.1f}")
    other = (~values.isin([1, 2, 3])).sum() / den * 100.0
    suffix = f"; other {other:.1f}%" if other >= 0.1 else ""
    return f"education raw 1/2/3 {'/'.join(parts)}%{suffix}"


def build_enhanced_table1() -> pd.DataFrame:
    base = read_csv("phase36_baseline_clinical_characteristics.csv")
    miss = read_csv("phase36_missingness_included_excluded.csv")
    covars = read_csv("phase13_covariate_participant_screen.csv", dtype={"participant_id": str, "wave": str})
    rows = []
    for cohort in COHORT_ORDER:
        b = base[base["cohort"].eq(cohort)].iloc[0]
        m = miss[miss["cohort"].eq(cohort)].iloc[0]
        bmi = "NA" if pd.isna(b.get("bmi_mean")) else (
            f"{fmt_mean_sd(b['bmi_mean'], b['bmi_sd'])}; {fmt_num(b['bmi_pct_nonmissing'], 0)}% observed"
        )
        covariates = (
            f"BMI {bmi}; chronic count {fmt_mean_sd(b['chronic_count_mean'], b['chronic_count_sd'])}; "
            f"2+ chronic {fmt_num(b['chronic_ge2_pct'], 1)}%; {education_distribution(covars, cohort)}; "
            f"marital raw=1 {fmt_num(b['marital_raw_one_pct'], 1)}%; rural/region raw=1 {fmt_num(b['rural_raw_one_pct'], 1)}%; "
            f"smoking {fmt_num(b['smoking_raw_positive_pct'], 1)}%; drinking {fmt_num(b['drinking_raw_positive_pct'], 1)}%"
        )
        selection = (
            f"Complete {fmt_int(m['complete_four_domain_n'])}/{fmt_int(m['source_women50_n'])} "
            f"({fmt_num(m['complete_four_domain_pct'], 1)}%); excluded age delta "
            f"{fmt_num(m['age_difference_excluded_minus_complete'], 1)} y"
        )
        if int(m["validation_available_n"]) == 0:
            validation = "endpoint availability unavailable in current cleaned pass"
            validation_n = ""
            validation_events = ""
        else:
            validation = (
                f"endpoint availability {fmt_int(m['validation_available_n'])}; events {fmt_int(m['validation_event_n'])} "
                f"({fmt_num(float(m['validation_event_n']) / float(m['validation_available_n']) * 100.0, 1)}%)"
            )
            validation_n = int(m["validation_available_n"])
            validation_events = int(m["validation_event_n"])
        rows.append(
            {
                "cohort": cohort,
                "primary_role": role_for(cohort),
                "source_women50_n": int(m["source_women50_n"]),
                "complete_four_domain_n": int(m["complete_four_domain_n"]),
                "complete_four_domain_pct": float(m["complete_four_domain_pct"]),
                "age_mean_sd": fmt_mean_sd(b["age_mean"], b["age_sd"]),
                "baseline_clinical_covariate_summary": covariates,
                "complete_case_selection": selection,
                "endpoint_availability_summary": validation,
                "endpoint_availability_n": validation_n,
                "endpoint_event_n": validation_events,
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "phase39_table1_baseline_clinical_covariates.csv", index=False, encoding="utf-8-sig")
    return out


def build_table2_outputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    classes = read_csv("phase33_selected_class_dictionary.csv")
    classes["family"] = classes["profile_label"].map(plain_family)
    strict = classes[classes["cohort"].isin(STRICT_CORE)].copy()
    sens = classes[classes["cohort"].isin(SENSITIVITY)].copy()
    strict_total = int(strict["class_n"].sum())
    main_rows = []
    for family, g in strict.groupby("family", sort=False):
        main_rows.append(
            {
                "clinical_family": family,
                "strict_core_classes": int(g.shape[0]),
                "strict_core_cohorts": ", ".join(sorted(g["cohort"].unique())),
                "strict_core_n": int(g["class_n"].sum()),
                "strict_core_pct": float(g["class_n"].sum() / strict_total * 100.0),
                "mean_functional_z": weighted_mean(g, "functional_score"),
                "mean_cognitive_z": weighted_mean(g, "cognitive_score"),
                "mean_affective_z": weighted_mean(g, "affective_score"),
                "mean_cardiometabolic_chronic_z": weighted_mean(g, "cardiometabolic_chronic_score"),
                "conservative_interpretation": family_interpretation(family),
            }
        )

    sens_rows = []
    for family, g in sens.groupby("family", sort=False):
        sens_rows.append(
            {
                "clinical_family": family,
                "sensitivity_classes": int(g.shape[0]),
                "sensitivity_cohorts": ", ".join(sorted(g["cohort"].unique())),
                "sensitivity_n": int(g["class_n"].sum()),
                "mean_functional_z": weighted_mean(g, "functional_score"),
                "mean_cognitive_z": weighted_mean(g, "cognitive_score"),
                "mean_affective_z": weighted_mean(g, "affective_score"),
                "mean_cardiometabolic_chronic_z": weighted_mean(g, "cardiometabolic_chronic_score"),
                "use_in_main_claim": "no; sensitivity/descriptive support only",
            }
        )
    main = pd.DataFrame(main_rows).sort_values(["strict_core_n", "clinical_family"], ascending=[False, True])
    sensitivity = pd.DataFrame(sens_rows).sort_values(["sensitivity_n", "clinical_family"], ascending=[False, True])
    main.to_csv(OUT / "phase39_table2_strict_core_profile_families_main.csv", index=False, encoding="utf-8-sig")
    sensitivity.to_csv(OUT / "phase39_profile_family_sensitivity_support.csv", index=False, encoding="utf-8-sig")
    return main, sensitivity


def build_mortality_guardrail() -> pd.DataFrame:
    summary = read_csv("phase6_mortality_summary.csv")
    guardrail = read_csv("phase28_mortality_sensitivity_guardrails.csv")
    overall = summary[summary["group_type"].eq("overall")].copy()
    merged = overall.merge(
        guardrail[
            [
                "analysis_set",
                "analysis_tier",
                "cohort",
                "ph_screen_flag",
                "large_time_drift_terms",
                "direction_change_terms",
                "mortality_interpretation",
            ]
        ],
        on=["analysis_set", "analysis_tier", "cohort"],
        how="left",
    )
    merged["phase39_decision"] = merged["mortality_interpretation"].fillna("unavailable").map(
        {
            "secondary_no_major_ph_or_piecewise_flag": "secondary guardrail only; no primary hard-outcome claim",
            "secondary_with_guardrail": "secondary guardrail with PH or time-drift caveat",
            "unavailable": "unavailable in current cleaned pass",
        }
    )
    unavailable = pd.to_numeric(merged["mortality_followup_available_n"], errors="coerce").fillna(0).eq(0)
    unavailable_cols = [
        "mortality_followup_available_n",
        "mortality_followup_available_pct",
        "death_n",
        "death_pct",
        "median_followup_time_years",
        "max_followup_time_years",
        "ph_screen_flag",
        "large_time_drift_terms",
        "direction_change_terms",
        "mortality_interpretation",
    ]
    for col in unavailable_cols:
        merged[col] = merged[col].astype("object")
    for col in unavailable_cols:
        merged.loc[unavailable, col] = "unavailable" if col in {"mortality_followup_available_n", "death_n", "mortality_interpretation"} else "NA"
    merged.loc[unavailable, "phase39_decision"] = "unavailable in current cleaned pass"
    keep = [
        "analysis_set",
        "analysis_tier",
        "cohort",
        "baseline_n",
        "mortality_followup_available_n",
        "mortality_followup_available_pct",
        "death_n",
        "death_pct",
        "median_followup_time_years",
        "max_followup_time_years",
        "ph_screen_flag",
        "large_time_drift_terms",
        "direction_change_terms",
        "mortality_interpretation",
        "phase39_decision",
    ]
    out = merged[keep].sort_values(["analysis_set", "cohort"])
    out.to_csv(OUT / "phase39_mortality_secondary_guardrail_table.csv", index=False, encoding="utf-8-sig")
    return out


def build_issue_matrix() -> pd.DataFrame:
    rows = [
        {
            "issue": "duplicate Phase38 manuscript insertion",
            "phase39_action": "Section-level TeX replacement now keeps one methods paragraph for cohort guardrails and one for hard-outcome/mortality guardrails.",
            "status": "fixed",
        },
        {
            "issue": "LASI mortality unavailable represented as zero events",
            "phase39_action": "LASI mortality follow-up and death fields are written as unavailable/NA in the mortality guardrail table.",
            "status": "fixed",
        },
        {
            "issue": "Table 1 versus Table 3 denominator mismatch",
            "phase39_action": "Table 1 now labels endpoint availability before covariate-complete LFO model restrictions; Table 3 footnote states its denominator is the covariate-complete LFO model set.",
            "status": "fixed",
        },
        {
            "issue": "survey-weight and male-comparator wording",
            "phase39_action": "Survey design wording is limited to cleaned-file header audit; male comparator is described as a separately standardized all-sex baseline scale.",
            "status": "fixed",
        },
        {
            "issue": "baseline covariate table gap",
            "phase39_action": "Table 1 adds education raw-category distribution plus marital and rural/region raw=1 proportions.",
            "status": "fixed with raw-code caveat",
        },
        {
            "issue": "Table 2 sensitivity support weakens strict-core claim",
            "phase39_action": "Main Table 2 is strict-core only; sensitivity support moved to Additional file 25.",
            "status": "fixed",
        },
        {
            "issue": "GMM reproducibility details insufficient",
            "phase39_action": "Methods now report covariance type, regularization, n_init, max_iter, random states, class-selection rule, bootstrap counts and software families.",
            "status": "fixed",
        },
    ]
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "phase39_submission_cleanup_issue_matrix.csv", index=False, encoding="utf-8-sig")
    return out


def table1_tex(table1: pd.DataFrame) -> str:
    lines = [
        r"\begin{table}[!htbp]",
        r"\caption{Baseline clinical characteristics, covariate profile, complete-case selection and endpoint availability}\label{tab:baseline-clinical}",
        r"\tiny",
        r"\setlength{\tabcolsep}{1pt}",
        r"\rowcolors{2}{tablegray}{white}",
        r"\begin{tabular}{@{}>{\raggedright\arraybackslash}p{0.08\textwidth}>{\raggedright\arraybackslash}p{0.13\textwidth}>{\raggedright\arraybackslash}p{0.13\textwidth}>{\raggedright\arraybackslash}p{0.33\textwidth}>{\raggedright\arraybackslash}p{0.23\textwidth}@{}}",
        r"\toprule",
        r"\rowcolor{tablehead}",
        r"Cohort & Analysis role & Construction denominator & Baseline clinical and covariate profile & Selection and endpoint availability\\",
        r"\midrule",
    ]
    for row in table1.to_dict("records"):
        baseline_text = f"Age {row['age_mean_sd']}; {row['baseline_clinical_covariate_summary']}"
        lines.append(
            f"{tex_escape(row['cohort'])} & {tex_escape(row['primary_role'])} & "
            f"{fmt_int(row['source_women50_n'])} source; {fmt_int(row['complete_four_domain_n'])} complete "
            f"({fmt_num(row['complete_four_domain_pct'], 1)}\\%) & "
            f"{tex_escape(baseline_text)} & "
            f"{tex_escape(row['complete_case_selection'])}; {tex_escape(row['endpoint_availability_summary'])}\\\\"
        )
    lines.extend(
        [
            r"\botrule",
            r"\end{tabular}",
            r"\rowcolors{2}{white}{white}",
            r"\footnotetext{This table separates source-screen, complete four-domain construction and endpoint-availability denominators. Endpoint availability is counted before the covariate-complete leave-functional-domain-out model restrictions used in Table~\ref{tab:functional-association}. Education, marital and rural/region summaries use cohort harmonized raw codes and should not be interpreted as instrument-identical social categories. Validation events are functional deterioration events, not hard clinical endpoints.}",
            r"\end{table}",
            "",
        ]
    )
    return "\n".join(lines)


def table2_tex(table2: pd.DataFrame) -> str:
    lines = [
        r"\begin{table}[!htbp]",
        r"\caption{Strict-core clinical burden-profile families}\label{tab:profile-families}",
        r"\tiny",
        r"\setlength{\tabcolsep}{1pt}",
        r"\rowcolors{2}{tablegray}{white}",
        r"\begin{tabular}{@{}>{\raggedright\arraybackslash}p{0.19\textwidth}>{\raggedright\arraybackslash}p{0.18\textwidth}>{\raggedright\arraybackslash}p{0.11\textwidth}>{\raggedright\arraybackslash}p{0.20\textwidth}>{\raggedright\arraybackslash}p{0.26\textwidth}@{}}",
        r"\toprule",
        r"\rowcolor{tablehead}",
        r"Clinical family & Strict-core evidence & Strict-core N & Class-size weighted domain z profile & Conservative interpretation\\",
        r"\midrule",
    ]
    for row in table2.to_dict("records"):
        class_count = int(row["strict_core_classes"])
        class_word = "class" if class_count == 1 else "classes"
        evidence = f"{class_count} {class_word} in {row['strict_core_cohorts']}"
        profile = (
            f"F {float(row['mean_functional_z']):.2f}; Cog {float(row['mean_cognitive_z']):.2f}; "
            f"Aff {float(row['mean_affective_z']):.2f}; CM {float(row['mean_cardiometabolic_chronic_z']):.2f}"
        )
        n = f"{fmt_int(row['strict_core_n'])} ({fmt_num(row['strict_core_pct'], 1)}\\%)"
        lines.append(
            f"{tex_escape(row['clinical_family'])} & {tex_escape(evidence)} & {n} & "
            f"{tex_escape(profile)} & {tex_escape(row['conservative_interpretation'])}\\\\"
        )
    lines.extend(
        [
            r"\botrule",
            r"\end{tabular}",
            r"\rowcolors{2}{white}{white}",
            r"\footnotetext{Strict-core evidence is restricted to CHARLS, ELSA, HRS and MHAS. SHARE, KLoSA and LASI sensitivity support is moved to Additional file 25 and is not used to define the main profile families. F = functional, Cog = cognitive, Aff = affective symptoms and CM = cardiometabolic/chronic disease burden. Higher z-scores indicate worse burden; class-size weighting is not survey weighting.}",
            r"\end{table}",
            "",
        ]
    )
    return "\n".join(lines)


def replace_section_paragraph(text: str, subsection: str, next_subsection: str, paragraph: str) -> str:
    pattern = re.compile(
        rf"(\\subsection\{{{re.escape(subsection)}\}}\n\n)(.*?)(\n\n\\subsection\{{{re.escape(next_subsection)}\}})",
        re.S,
    )
    return pattern.sub(lambda match: match.group(1) + paragraph + match.group(3), text, count=1)


def replace_subsection_to_section(text: str, subsection: str, next_section: str, paragraph: str) -> str:
    pattern = re.compile(
        rf"(\\subsection\{{{re.escape(subsection)}\}}\n\n)(.*?)(\n\n\\section\{{{re.escape(next_section)}\}})",
        re.S,
    )
    return pattern.sub(lambda match: match.group(1) + paragraph + match.group(3), text, count=1)


def replace_subsection_to_floatbarrier(text: str, subsection: str, paragraph: str) -> str:
    pattern = re.compile(
        rf"(\\subsection\{{{re.escape(subsection)}\}}\n\n)(.*?)(\n\n\\FloatBarrier)",
        re.S,
    )
    return pattern.sub(lambda match: match.group(1) + paragraph + match.group(3), text, count=1)


def replace_table(text: str, label: str, replacement: str) -> str:
    label_token = rf"\label{{{label}}}"
    label_pos = text.find(label_token)
    if label_pos < 0:
        return text
    start = text.rfind(r"\begin{table}", 0, label_pos)
    end = text.find(r"\end{table}", label_pos)
    if start < 0 or end < 0:
        return text
    end += len(r"\end{table}")
    return text[:start] + replacement.rstrip() + text[end:]


def insert_after_once(text: str, needle: str, insertion: str) -> str:
    pos = text.find(needle)
    if pos < 0:
        return text
    pos += len(needle)
    return text[:pos] + "\n\n" + insertion.rstrip() + "\n" + text[pos:]


def supplementary_figure_block() -> str:
    return r"""
\clearpage
\section*{Supplementary figures}

\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth,height=0.76\textheight,keepaspectratio]{figure1_cohort_tier_lock-re.pdf}
{\small\noindent\textbf{Supplementary Figure S1.} Original denominator and cohort-tier dashboard. This earlier display is retained as supplementary measurement context after the revised STROBE-style main flow replaced it.\par}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth,height=0.76\textheight,keepaspectratio]{figure2_descriptive_profile_heatmap-re.pdf}
{\small\noindent\textbf{Supplementary Figure S2.} Original full descriptive profile heatmap. This broader profile display is retained as supplementary context because the main text now emphasizes strict-core profile families.\par}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth,height=0.76\textheight,keepaspectratio]{figure3_validation_and_stability_guardrails-re.pdf}
{\small\noindent\textbf{Supplementary Figure S3.} Original validation and model-stability guardrail dashboard. This compact dashboard is retained as supplementary context after the main validation figure was simplified to adjusted functional-deterioration associations.\par}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth,height=0.78\textheight,keepaspectratio]{figure4_harmonization_risk_matrix-re.pdf}
{\small\noindent\textbf{Supplementary Figure S4.} Cohort-domain harmonization risk matrix. The matrix is retained after the references as measurement-risk evidence rather than a primary biological result.\par}
\end{figure}

\FloatBarrier
"""


def update_tex(table1: pd.DataFrame, table2: pd.DataFrame) -> None:
    text = TEX.read_text(encoding="utf-8")
    cohort_paragraph = (
        "We used cleaned cohort files from CHARLS, ELSA, HRS, KLoSA, LASI, MHAS and SHARE "
        "\\cite{zhao2014charls,steptoe2013elsa,sonnega2014hrs,keis2026klosa,perianayagam2022lasi,wong2017mhas,borschsupan2013share}. "
        "The analytic population was women aged 50 years or older at the cohort-specific selected baseline or analysis wave. "
        "Sex coding was confirmed from local Working Data Stata value labels and do-files as \\texttt{ragender=0} for women and \\texttt{ragender=1} for men. "
        "Source-screen, complete-domain, profile-construction and validation denominators were separated in line with observational-study reporting principles \\cite{vonelm2007strobe}. "
        "A cleaned-file header audit separately screened survey-design variables, male-comparator feasibility and hard clinical outcome candidates. "
        "Header-only candidate variables were not treated as harmonized analytic variables."
    )
    text = replace_section_paragraph(text, "Cohorts and analytic population", "Domain construction and harmonization review", cohort_paragraph)

    profile_paragraph = (
        "Cohort-specific Gaussian mixture models with two to five classes were fit to the four domain scores as model-based descriptive clustering tools \\cite{mclachlan2000finite}. "
        "Models were implemented with scikit-learn GaussianMixture using full covariance matrices, \\texttt{reg\\_covar=1e-6}, \\texttt{max\\_iter=500}, \\texttt{n\\_init=5} and random state 20260601 for the four-domain baseline models. "
        "Leave-functional-domain-out validation profiles used the same full-covariance regularization, \\texttt{max\\_iter=500}, \\texttt{n\\_init=5} and random state 20260602. "
        "The selected model used the lowest BIC among converged models with minimum class size at least 5\\%, while recognizing that class enumeration statistics should not be treated as clinical truth without sensitivity checks \\cite{nylund2007classes,hennig2015trueclusters}. "
        "Classes were ordered by mean severity score. Component covariance diagnostics, 20-replicate GMM bootstrap stability checks, k-means and hierarchical-clustering algorithm comparisons and 100-requested-resample AUC bootstrap intervals were used as guardrails. "
        "Software families used for analysis included Python, pandas, NumPy, scikit-learn and statsmodels; exact scripts and aggregate outputs are listed in the additional files. Profiles were interpreted as descriptive strata, not stable latent disease entities."
    )
    text = replace_section_paragraph(text, "Profile construction and robustness diagnostics", "Functional validation guardrail", profile_paragraph)

    validation_paragraph = (
        "The main follow-up endpoint was functional deterioration of at least 0.5 SD from baseline. Because the original four-domain profile includes baseline function, functional deterioration is vulnerable to endpoint leakage. "
        "The primary validation guardrail therefore rebuilt profiles after leaving the functional domain out and compared profile classes with continuous cognitive, affective and cardiometabolic/chronic domain scores. "
        "Models used minimal-core covariate adjustment for age, education, marital status, smoking and drinking. Table~\\ref{tab:baseline-clinical} reports endpoint availability before the covariate-complete leave-functional-domain-out model restrictions used in Table~\\ref{tab:functional-association}. "
        "Absolute risks were emphasized before adjusted odds ratios because functional deterioration was common. Hospitalization, institutionalization and care-dependence variables were audited as candidate hard endpoints but were not used unless cohort-level harmonization could be defended. Mortality was handled only as a secondary guardrail endpoint."
    )
    text = replace_subsection_to_section(text, "Functional validation guardrail", "Results", validation_paragraph)

    results_intro_old = (
        "Table~\\ref{tab:baseline-clinical} and Figure~\\ref{fig:strobe-flow} show the denominator lock, baseline clinical characteristics, selection audit and validation availability."
    )
    results_intro_new = (
        "Table~\\ref{tab:baseline-clinical} and Figure~\\ref{fig:strobe-flow} show the denominator lock, baseline clinical and covariate characteristics, selection audit and endpoint availability before model-specific covariate and leave-functional-domain-out restrictions."
    )
    text = text.replace(results_intro_old, results_intro_new)
    table1_block = table1_tex(table1)
    if r"\label{tab:baseline-clinical}" in text:
        text = replace_table(text, "tab:baseline-clinical", table1_block)
    else:
        text = insert_after_once(text, results_intro_new, table1_block)
    text = text.replace(
        "Sensitivity support from SHARE, KLoSA and LASI is reported separately and does not convert those cohorts into primary evidence.",
        "Sensitivity support from SHARE, KLoSA and LASI is reported in Additional file 25 and does not convert those cohorts into primary evidence.",
    )
    text = replace_table(text, "tab:profile-families", table2_tex(table2))
    text = text.replace(
        "Delta AUC is profile model minus continuous three-domain model; negative values favor continuous scores. Parentheses show bootstrap 2.5th to 97.5th percentile intervals from 100 requested resamples per cohort when at least 30 bootstrap fits succeeded.",
        "Table~\\ref{tab:baseline-clinical} reports broader endpoint availability; this table reports the covariate-complete leave-functional-domain-out modeling denominator. Delta AUC is profile model minus continuous three-domain model; negative values favor continuous scores. Parentheses show bootstrap 2.5th to 97.5th percentile intervals from 100 requested resamples per cohort when at least 30 bootstrap fits succeeded.",
    )

    hard_paragraph = (
        "The harmonization matrix remained central to interpretation and is retained as Supplementary Figure S4. Functional-domain strictness differed across cohorts: CHARLS used IADL-only information, HRS used ADL-only information, KLoSA used a bridge proxy and SHARE remained validation-downgraded. "
        "Cognitive batteries were cohort-specific, SHARE affective symptoms used EURO-D, and cardiometabolic/chronic disease indicators differed in lipid/cholesterol availability. A cleaned-file header audit did not identify a harmonized survey-design triplet of analysis weight, primary sampling unit and strata across the seven cleaned files, so no survey-weighted prevalence claim is made. "
        "A baseline male-comparator domain table was generated on a separately standardized all-sex baseline scale using the same domain variable rules, but it was not used for profile construction or validation and no outcome-level sex-interaction model was introduced. "
        "Hospitalization, institutionalization and care-dependence candidates remained non-harmonized header-level evidence. Mortality analyses were available but were kept secondary because proportional-hazards or piecewise time-drift flags were present in several cohorts."
    )
    text = replace_subsection_to_floatbarrier(text, "Harmonization, hard-outcome and algorithm guardrails", hard_paragraph)
    text = re.sub(
        r"\n\\begin\{figure\}\[htbp\]\n\\centering\n\\includegraphics\[width=\\textwidth,height=0\.78\\textheight,keepaspectratio\]\{figure4_harmonization_risk_matrix-re\.pdf\}.*?\\end\{figure\}\n",
        "\n",
        text,
        flags=re.S,
    )
    text = text.replace(
        "Phase 38 adds a supplementary baseline male-comparator audit using the same domain-scoring rules, which helps document feasibility and denominator differences. It still does not provide outcome-level sex-interaction validation or women-specific mechanism testing.",
        "Phase 38 adds a supplementary baseline male-comparator audit on a separately standardized all-sex baseline scale, which helps document feasibility and denominator differences. It is not part of profile construction or validation, and it still does not provide outcome-level sex-interaction validation or women-specific mechanism testing.",
    )
    text = text.replace(
        "Survey weights, strata and primary sampling units were screened but not codebook-confirmed as a common seven-cohort design set, so the analyses are not survey-weighted population estimates.",
        "Survey weights, strata and primary sampling units were screened by cleaned-file headers but were not available as a common seven-cohort design set, so the analyses are not survey-weighted population estimates.",
    )
    text = text.replace(
        "baseline clinical characterization, included-versus-excluded missingness auditing",
        "baseline clinical and covariate characterization, included-versus-excluded missingness auditing",
    )
    text = text.replace(
        "sex-specific mechanisms, independent hard-outcome validation",
        "sex-specific mechanisms, independent hard-outcome validation",
    )

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
Additional file 13: Phase 39 enhanced baseline clinical covariate and endpoint-availability table.\\
Additional file 14: Phase 39 strict-core profile-family table.\\
Additional file 15: Phase 37 adjusted functional validation table.\\
Additional file 16: Functional deterioration class-level risks and adjusted associations.\\
Additional file 17: GMM algorithm robustness sensitivity.\\
Additional file 18: Phase 37 AUC bootstrap intervals.\\
Additional file 19: Phase 38 survey-design variable audit.\\
Additional file 20: Phase 38 baseline male-comparator domain summary.\\
Additional file 21: Phase 38 baseline male-comparator domain contrasts.\\
Additional file 22: Phase 38 hospitalization, institutionalization and care-dependence candidate audit.\\
Additional file 23: Phase 39 mortality secondary guardrail table.\\
Additional file 24: Phase 39 submission cleanup issue matrix.\\
Additional file 25: Phase 39 sensitivity-cohort profile-family support.\\
Supplementary Figures S1-S4: Previous figure set and harmonization-risk matrix, placed after the references.

"""
    start = text.index(r"\section*{Additional files}")
    end = text.index(r"\bibliography{", start)
    text = text[:start] + add_files + text[end:]
    bib = r"\bibliography{bmc_geriatrics_refs}"
    text = text[: text.index(bib)] + bib + "\n" + supplementary_figure_block() + "\n" + r"\end{document}" + "\n"
    TEX.write_text(text, encoding="utf-8")


def copy_additional_files() -> None:
    stale = [
        "additional_file_13_phase37_table1_baseline_clinical_characteristics.csv",
        "additional_file_14_phase37_table2_strict_core_profile_families.csv",
        "additional_file_23_phase38_mortality_secondary_guardrail_table.csv",
        "additional_file_24_phase38_unresolved_issue_resolution_matrix.csv",
    ]
    for name in stale:
        path = PKG / name
        if path.exists():
            path.unlink()
    mapping = {
        "additional_file_13_phase39_table1_baseline_clinical_covariates.csv": OUT / "phase39_table1_baseline_clinical_covariates.csv",
        "additional_file_14_phase39_table2_strict_core_profile_families_main.csv": OUT / "phase39_table2_strict_core_profile_families_main.csv",
        "additional_file_23_phase39_mortality_secondary_guardrail_table.csv": OUT / "phase39_mortality_secondary_guardrail_table.csv",
        "additional_file_24_phase39_submission_cleanup_issue_matrix.csv": OUT / "phase39_submission_cleanup_issue_matrix.csv",
        "additional_file_25_phase39_profile_family_sensitivity_support.csv": OUT / "phase39_profile_family_sensitivity_support.csv",
    }
    for name, src in mapping.items():
        shutil.copyfile(src, PKG / name)


def update_readme() -> None:
    readme = PKG / "README_BMC_Geriatrics_burden_profiles_rescue.md"
    text = readme.read_text(encoding="utf-8") if readme.exists() else "# BMC Geriatrics burden profile rescue package\n"
    add = """

## Phase 39 submission cleanup

- Removed duplicate Phase38 methods insertions with section-level TeX replacement.
- Re-coded LASI mortality follow-up as unavailable/NA rather than zero events.
- Clarified Table 1 endpoint availability versus Table 3 covariate-complete LFO model denominators.
- Limited survey-design language to a cleaned-file header audit and clarified the male comparator scale.
- Added education, marital and rural/region covariate summaries to the main baseline table.
- Moved sensitivity-cohort profile-family support out of the main Table 2 into Additional file 25.
- Added GMM reproducibility details to the Methods.
"""
    if "## Phase 39 submission cleanup" not in text:
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
        "figure1_cohort_tier_lock-re.pdf",
        "figure1_cohort_tier_lock.svg",
        "figure1_cohort_tier_lock.png",
        "figure2_descriptive_profile_heatmap-re.pdf",
        "figure2_descriptive_profile_heatmap.svg",
        "figure2_descriptive_profile_heatmap.png",
        "figure3_validation_and_stability_guardrails-re.pdf",
        "figure3_validation_and_stability_guardrails.svg",
        "figure3_validation_and_stability_guardrails.png",
        "figure4_harmonization_risk_matrix-re.pdf",
        "figure4_harmonization_risk_matrix.svg",
        "figure4_harmonization_risk_matrix.png",
        "README_BMC_Geriatrics_burden_profiles_rescue.md",
    ]
    names.extend([p.name for p in sorted(PKG.glob("additional_file_*.csv"))])
    with zipfile.ZipFile(source_zip, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for name in names:
            path = PKG / name
            if path.exists():
                z.write(path, arcname=name)
    with zipfile.ZipFile(pdf_zip, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for name in [*names, "bmc_geriatrics_main.pdf"]:
            path = PKG / name
            if path.exists():
                z.write(path, arcname=name)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip-only", action="store_true")
    args = parser.parse_args()
    if not args.zip_only:
        table1 = build_enhanced_table1()
        table2, _ = build_table2_outputs()
        build_mortality_guardrail()
        build_issue_matrix()
        update_tex(table1, table2)
        copy_additional_files()
        update_readme()
        print(OUT / "phase39_table1_baseline_clinical_covariates.csv")
        print(OUT / "phase39_table2_strict_core_profile_families_main.csv")
        print(OUT / "phase39_profile_family_sensitivity_support.csv")
        print(OUT / "phase39_mortality_secondary_guardrail_table.csv")
        print(OUT / "phase39_submission_cleanup_issue_matrix.csv")
        print(TEX)
    rebuild_zips()
    print(PKG / "bmc_geriatrics_submission_burden_profiles_rescue_source_only.zip")
    print(PKG / "bmc_geriatrics_submission_burden_profiles_rescue_pdf_ready.zip")


if __name__ == "__main__":
    main()
