from __future__ import annotations

import argparse
import csv
import re
import shutil
import sys
import textwrap
import zipfile
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
PKG = ROOT / "manuscript" / "bmc_geriatrics_submission_burden_profiles_rescue"
TEX = PKG / "bmc_geriatrics_main.tex"

sys.path.insert(0, str(ROOT / "scripts"))
from build_phase3_domain_scores import (  # noqa: E402
    AGE_FALLBACK_VARIABLES,
    ANALYSIS_SELECTIONS,
    COHORT_CONFIG,
    DOMAIN_NAMES,
    augment_share_strict_functional,
    find_clean_csv,
    read_header_map,
    score_cohort,
    to_numeric,
    variables_for_config,
)


COHORT_ORDER = ["CHARLS", "ELSA", "HRS", "KLoSA", "LASI", "MHAS", "SHARE"]

SURVEY_PATTERNS = {
    "weight": [
        r"\b(weight|weights|wgt|wgts|pweight|iweight|hhweight|raked)\b",
        r"\b(wtresp|wtperson|indwt|hhwt|xwgt|chwgt|wght)\b",
        r"(sample|sampling|survey|cross[- ]?sectional|longitudinal).{0,35}\b(weight|wgt|wt)\b",
        r"\b(weight|wgt|wt)\b.{0,35}(sample|sampling|survey|cross[- ]?sectional|longitudinal)",
    ],
    "psu": [
        r"\bpsu\b",
        r"\bcluster\b",
        r"primary.{0,20}sampling",
        r"sampling.{0,20}unit",
    ],
    "strata": [
        r"\bstrata\b",
        r"\bstratum\b",
        r"\bstratification\b",
        r"\bstrat\b",
    ],
}

HARD_OUTCOME_PATTERNS = {
    "hospitalization": [
        r"\bhosp",
        r"hospital",
        r"inpatient",
        r"admission",
        r"admitted",
        r"overnight.{0,20}(hospital|stay)",
    ],
    "institutionalization": [
        r"nursing.{0,20}home",
        r"care.{0,20}home",
        r"residential.{0,20}care",
        r"institution",
        r"long[- ]?term.{0,20}care",
        r"\bltc\b",
    ],
    "care_dependence": [
        r"caregiv",
        r"caregiver",
        r"formal.{0,20}care",
        r"informal.{0,20}care",
        r"home.{0,20}care",
        r"receive.{0,20}help",
        r"paid.{0,20}help",
        r"unpaid.{0,20}help",
        r"care.{0,20}depend",
    ],
}


def compile_regex(patterns: dict[str, list[str]]) -> dict[str, list[re.Pattern[str]]]:
    return {name: [re.compile(pattern, re.I) for pattern in values] for name, values in patterns.items()}


SURVEY_RE = compile_regex(SURVEY_PATTERNS)
HARD_RE = compile_regex(HARD_OUTCOME_PATTERNS)
BODY_WEIGHT_RE = re.compile(r"(self[- ]?reported.{0,20}weight|body.{0,20}weight|weight.{0,10}kg|kg\)|自报体重|体重)", re.I)


def var_id(header: str) -> str:
    return header.strip().strip('"').split(" ", 1)[0].strip()


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


def fmt_num(value: object, digits: int = 2) -> str:
    if pd.isna(value) or value == "":
        return "NA"
    return f"{float(value):.{digits}f}"


def first_examples(series: pd.Series, n: int = 8) -> str:
    cleaned = series.astype("string").str.strip()
    cleaned = cleaned[(cleaned.notna()) & (cleaned != "")]
    values = cleaned.drop_duplicates().head(n).tolist()
    return "|".join(str(value) for value in values)


def matches_any(text: str, patterns: list[re.Pattern[str]]) -> bool:
    return any(pattern.search(text) for pattern in patterns)


def candidate_variables(
    header_map: dict[str, str], patterns: dict[str, list[re.Pattern[str]]]
) -> dict[str, list[tuple[str, str]]]:
    by_concept: dict[str, list[tuple[str, str]]] = {name: [] for name in patterns}
    for variable, raw_header in header_map.items():
        haystack = f"{variable} {raw_header}".lower()
        for concept, compiled in patterns.items():
            if matches_any(haystack, compiled):
                by_concept[concept].append((variable, raw_header))
    return by_concept


def build_candidate_audit(
    data_root: Path,
    patterns: dict[str, list[re.Pattern[str]]],
    audit_type: str,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for cohort in COHORT_ORDER:
        path = find_clean_csv(data_root, str(COHORT_CONFIG[cohort]["file"]))
        header_map = read_header_map(path)
        candidates = candidate_variables(header_map, patterns)
        all_vars = sorted({variable for values in candidates.values() for variable, _ in values})
        candidate_frame = pd.DataFrame()
        if all_vars:
            raw_cols = [header_map[variable] for variable in all_vars]
            candidate_frame = pd.read_csv(
                path,
                usecols=raw_cols,
                dtype=str,
                encoding="utf-8-sig",
                low_memory=False,
            ).rename(columns={header_map[variable]: variable for variable in all_vars})

        for concept in patterns:
            values = candidates[concept]
            if audit_type == "survey_design" and concept == "weight":
                values = [
                    (variable, raw_header)
                    for variable, raw_header in values
                    if not BODY_WEIGHT_RE.search(f"{variable} {raw_header}")
                ]
            if not values:
                rows.append(
                    {
                        "audit_type": audit_type,
                        "cohort": cohort,
                        "concept": concept,
                        "variable": "",
                        "raw_header": "",
                        "source_file": str(path),
                        "nonmissing_n": 0,
                        "nonmissing_pct": 0.0,
                        "sample_values": "",
                        "harmonization_status": "no_cleaned_candidate",
                        "decision": "not available for current harmonized analysis",
                    }
                )
                continue
            for variable, raw_header in values:
                series = candidate_frame[variable] if variable in candidate_frame.columns else pd.Series(dtype=str)
                nonmissing = int(series.astype("string").str.strip().replace("", pd.NA).notna().sum())
                total = int(len(series)) if len(series) else 0
                rows.append(
                    {
                        "audit_type": audit_type,
                        "cohort": cohort,
                        "concept": concept,
                        "variable": variable,
                        "raw_header": raw_header,
                        "source_file": str(path),
                        "nonmissing_n": nonmissing,
                        "nonmissing_pct": round(nonmissing / total * 100, 2) if total else 0.0,
                        "sample_values": first_examples(series),
                        "harmonization_status": "candidate_header_only",
                        "decision": "requires cohort codebook mapping before analysis use",
                    }
                )
    return pd.DataFrame(rows)


def read_all_sex_cohort_frame(data_root: Path, database_root: Path | None, cohort: str) -> pd.DataFrame:
    config = COHORT_CONFIG[cohort]
    path = find_clean_csv(data_root, str(config["file"]))
    header_map = read_header_map(path)
    wanted = set(variables_for_config(config))
    wanted.add("ragender")
    wanted.add(str(config["age"]))
    wanted.update(AGE_FALLBACK_VARIABLES)
    available = {var: header_map[var] for var in wanted if var in header_map}
    missing_required = [var for var in ["ragender", str(config["age"])] if var not in available]
    if missing_required:
        raise KeyError(f"{cohort} missing required variables: {missing_required}")

    frame = pd.read_csv(
        path,
        usecols=list(available.values()),
        dtype=str,
        encoding="utf-8-sig",
        low_memory=False,
    ).rename(columns={raw: var for var, raw in available.items()})

    if cohort == "SHARE":
        frame = augment_share_strict_functional(frame, database_root)

    if config["id"] and str(config["id"]) in frame.columns:
        frame["participant_id"] = frame[str(config["id"])].astype("string")
    else:
        frame["participant_id"] = [f"{cohort}_{idx}" for idx in range(len(frame))]

    if config["wave"] and str(config["wave"]) in frame.columns:
        frame["wave"] = frame[str(config["wave"])].astype("string").fillna("")
    else:
        frame["wave"] = "all_rows_no_wave"

    frame["cohort"] = cohort
    frame["age"] = to_numeric(frame[str(config["age"])])
    birth_year = to_numeric(frame["rabyear"]) if "rabyear" in frame.columns else pd.Series(pd.NA, index=frame.index)
    for interview_year_var in ("iwy", "iwendy", "iwindy", "r1iwy"):
        if interview_year_var not in frame.columns:
            continue
        derived_age = to_numeric(frame[interview_year_var]) - birth_year
        derived_age = derived_age.where((derived_age >= 0) & (derived_age <= 120))
        frame["age"] = frame["age"].fillna(derived_age)
    frame["ragender"] = frame["ragender"].astype("string").str.strip()
    frame = frame[(frame["ragender"].isin(["0", "1"])) & (frame["age"] >= 50)].copy()
    return frame


def build_all_sex_scores(data_root: Path, database_root: Path | None) -> pd.DataFrame:
    frames = []
    for cohort in COHORT_ORDER:
        raw = read_all_sex_cohort_frame(data_root, database_root, cohort)
        scored = score_cohort(raw.copy(), cohort)
        scored["ragender"] = raw.loc[scored.index, "ragender"].astype("string").to_numpy()
        scored["sex"] = scored["ragender"].map({"0": "female", "1": "male"})
        frames.append(scored)
    long_scores = pd.concat(frames, ignore_index=True)

    selected_frames = []
    for selection in ANALYSIS_SELECTIONS:
        subset = long_scores[
            (long_scores["cohort"] == selection["cohort"])
            & (long_scores["wave"].astype(str) == str(selection["wave"]))
        ].copy()
        subset.insert(0, "analysis_set", selection["analysis_set"])
        subset.insert(1, "analysis_tier", selection["tier"])
        selected_frames.append(subset)
    return pd.concat(selected_frames, ignore_index=True)


def summarize_sex_comparator(selected: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict[str, object]] = []
    for (analysis_set, analysis_tier, cohort, sex), group in selected.groupby(
        ["analysis_set", "analysis_tier", "cohort", "sex"], dropna=False
    ):
        complete = group[group["complete_four_domain"] == 1]
        row: dict[str, object] = {
            "analysis_set": analysis_set,
            "analysis_tier": analysis_tier,
            "cohort": cohort,
            "sex": sex,
            "baseline_age50plus_n": int(len(group)),
            "complete_four_domain_n": int(len(complete)),
            "complete_four_domain_pct": round(len(complete) / len(group) * 100, 2) if len(group) else 0.0,
            "age_mean": round(float(group["age"].mean()), 2) if len(group) else "",
            "age_sd": round(float(group["age"].std()), 2) if len(group) > 1 else "",
        }
        for domain in DOMAIN_NAMES:
            series = pd.to_numeric(complete[f"{domain}_score"], errors="coerce")
            row[f"{domain}_mean_z"] = round(float(series.mean()), 3) if series.notna().any() else ""
        rows.append(row)

    summary = pd.DataFrame(rows).sort_values(["cohort", "sex"])
    contrast_rows = []
    for cohort, group in summary.groupby("cohort"):
        by_sex = {row["sex"]: row for row in group.to_dict("records")}
        if "female" not in by_sex or "male" not in by_sex:
            contrast_rows.append({"cohort": cohort, "status": "missing one sex"})
            continue
        row = {
            "cohort": cohort,
            "female_complete_n": by_sex["female"]["complete_four_domain_n"],
            "male_complete_n": by_sex["male"]["complete_four_domain_n"],
            "female_minus_male_age_mean": round(
                float(by_sex["female"]["age_mean"]) - float(by_sex["male"]["age_mean"]), 2
            ),
            "status": "baseline_comparator_only",
        }
        for domain in DOMAIN_NAMES:
            left = by_sex["female"].get(f"{domain}_mean_z", "")
            right = by_sex["male"].get(f"{domain}_mean_z", "")
            row[f"female_minus_male_{domain}_mean_z"] = (
                round(float(left) - float(right), 3) if left != "" and right != "" else ""
            )
        contrast_rows.append(row)
    contrasts = pd.DataFrame(contrast_rows).sort_values("cohort")
    return summary, contrasts


def build_mortality_guardrail() -> pd.DataFrame:
    summary_path = OUT / "phase6_mortality_summary.csv"
    guardrail_path = OUT / "phase28_mortality_sensitivity_guardrails.csv"
    if not summary_path.exists() or not guardrail_path.exists():
        return pd.DataFrame(
            [
                {
                    "cohort": "",
                    "status": "mortality guardrail source files missing",
                }
            ]
        )

    summary = pd.read_csv(summary_path)
    guardrail = pd.read_csv(guardrail_path)
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
    merged["phase38_decision"] = merged["mortality_interpretation"].fillna("unavailable").map(
        {
            "secondary_no_major_ph_or_piecewise_flag": "secondary guardrail only; no primary hard-outcome claim",
            "secondary_with_guardrail": "secondary guardrail with PH or time-drift caveat",
            "unavailable": "unavailable in current cleaned pass",
        }
    )
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
        "phase38_decision",
    ]
    return merged[keep].sort_values(["analysis_set", "cohort"])


def build_issue_matrix(
    survey: pd.DataFrame,
    hard: pd.DataFrame,
    sex_summary: pd.DataFrame,
    mortality: pd.DataFrame,
) -> pd.DataFrame:
    complete_design = []
    for cohort, group in survey.groupby("cohort"):
        concepts = {
            row["concept"]
            for row in group.to_dict("records")
            if row["harmonization_status"] == "candidate_header_only"
        }
        if {"weight", "psu", "strata"}.issubset(concepts):
            complete_design.append(cohort)
    hard_ready = hard[
        (hard["harmonization_status"] == "candidate_header_only")
        & (hard["concept"].isin(["hospitalization", "institutionalization", "care_dependence"]))
    ]["cohort"].nunique()
    sex_cohorts = sex_summary[sex_summary["complete_four_domain_n"] > 0]["cohort"].nunique()
    mortality_available = int((pd.to_numeric(mortality.get("mortality_followup_available_n"), errors="coerce") > 0).sum())

    rows = [
        {
            "issue": "survey weights/PSU/strata",
            "phase38_action": f"Cleaned-header survey-design audit generated; complete candidate triplets found in {len(complete_design)} cohorts: {', '.join(complete_design) if complete_design else 'none'}.",
            "manuscript_decision": "No survey-weighted or population-prevalence claim; survey-design modeling deferred until codebook-confirmed harmonized weight, PSU and strata variables exist.",
            "output": "phase38_survey_design_variable_audit.csv",
        },
        {
            "issue": "male comparator/sex interaction",
            "phase38_action": f"All-sex baseline domain comparator generated with the Phase3 domain rules for {sex_cohorts} cohorts.",
            "manuscript_decision": "Baseline male comparator is supplementary only; no longitudinal sex-interaction validation claim is made without rebuilding all-sex profile and outcome models.",
            "output": "phase38_sex_comparator_domain_summary.csv; phase38_sex_comparator_domain_contrasts.csv",
        },
        {
            "issue": "hospitalization/institutionalization/care-dependence",
            "phase38_action": f"Cleaned-header candidate audit generated; candidate hard-outcome headers found in {hard_ready} cohorts but remain header-only and non-harmonized.",
            "manuscript_decision": "These endpoints are not used as current hard-outcome validation and are not replaced by functional deterioration.",
            "output": "phase38_hard_outcome_candidate_audit.csv",
        },
        {
            "issue": "mortality",
            "phase38_action": f"Mortality guardrail table generated for {mortality_available} cohort rows with follow-up.",
            "manuscript_decision": "Mortality stays secondary guardrail because PH/time-drift diagnostics are cohort-dependent and LASI remains unavailable.",
            "output": "phase38_mortality_secondary_guardrail_table.csv",
        },
        {
            "issue": "previous figures",
            "phase38_action": "Original Fig1-4 assets moved into a post-reference Supplementary figures section.",
            "manuscript_decision": "Main text retains the newer STROBE flow, strict-core heatmap and functional-validation forest; harmonization matrix is treated as supplementary measurement evidence.",
            "output": "bmc_geriatrics_main.tex",
        },
    ]
    return pd.DataFrame(rows)


def write_phase38_report(issue_matrix: pd.DataFrame) -> None:
    lines = [
        "# Phase 38 Unresolved Guardrail Package",
        "",
        "This phase addresses the remaining top-journal review vulnerabilities without fabricating unsupported analyses.",
        "",
        "| Issue | Action | Manuscript decision | Output |",
        "|---|---|---|---|",
    ]
    for row in issue_matrix.to_dict("records"):
        lines.append(
            f"| {row['issue']} | {row['phase38_action']} | {row['manuscript_decision']} | {row['output']} |"
        )
    lines.extend(
        [
            "",
            "Interpretation rule: a header-only candidate is not treated as a harmonized analytic variable.",
            "The manuscript therefore avoids survey-weighted prevalence claims, women-specific mechanism claims, independent hard-outcome validation claims and primary mortality claims.",
        ]
    )
    (OUT / "phase38_unresolved_guardrail_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


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


def replace_between(text: str, start_marker: str, end_marker: str, replacement: str) -> str:
    start = text.index(start_marker)
    end = text.index(end_marker, start)
    return text[:start] + replacement + text[end:]


def update_tex(issue_matrix: pd.DataFrame) -> None:
    text = TEX.read_text(encoding="utf-8")

    cohort_paragraph_old = (
        "We used cleaned cohort files from CHARLS, ELSA, HRS, KLoSA, LASI, MHAS and SHARE "
        "\\cite{zhao2014charls,steptoe2013elsa,sonnega2014hrs,keis2026klosa,perianayagam2022lasi,wong2017mhas,borschsupan2013share}. "
        "The analytic population was women aged 50 years or older at the cohort-specific selected baseline or analysis wave. "
        "Sex coding was confirmed from local Working Data Stata value labels and do-files as \\texttt{ragender=0} for women and \\texttt{ragender=1} for men. "
        "Source-screen, complete-domain, profile-construction and validation denominators were separated in line with observational-study reporting principles \\cite{vonelm2007strobe}."
    )
    cohort_paragraph_new = (
        "We used cleaned cohort files from CHARLS, ELSA, HRS, KLoSA, LASI, MHAS and SHARE "
        "\\cite{zhao2014charls,steptoe2013elsa,sonnega2014hrs,keis2026klosa,perianayagam2022lasi,wong2017mhas,borschsupan2013share}. "
        "The analytic population was women aged 50 years or older at the cohort-specific selected baseline or analysis wave. "
        "Sex coding was confirmed from local Working Data Stata value labels and do-files as \\texttt{ragender=0} for women and \\texttt{ragender=1} for men. "
        "Source-screen, complete-domain, profile-construction and validation denominators were separated in line with observational-study reporting principles \\cite{vonelm2007strobe}. "
        "A post-review guardrail audit separately screened survey-design variables, male-comparator feasibility and hard clinical outcome candidates. "
        "Header-only candidate variables were not treated as harmonized analytic variables."
    )
    if cohort_paragraph_old in text:
        text = text.replace(cohort_paragraph_old, cohort_paragraph_new)

    text = text.replace("Weighted domain z profile", "Class-size weighted domain z profile")
    text = text.replace(
        "Rows show weighted mean domain z-scores",
        "Rows show class-size weighted mean domain z-scores",
    )
    text = text.replace(
        "Higher z-scores indicate worse burden. Sensitivity cohorts",
        "Higher z-scores indicate worse burden; class-size weighting is not survey weighting. Sensitivity cohorts",
    )
    text = text.replace(
        "Higher z-scores indicate worse burden.}",
        "Higher z-scores indicate worse burden; class-size weighting is not survey weighting.}",
    )

    validation_old = (
        "The main follow-up endpoint was functional deterioration of at least 0.5 SD from baseline. Because the original four-domain profile includes baseline function, functional deterioration is vulnerable to endpoint leakage. "
        "The primary validation guardrail therefore rebuilt profiles after leaving the functional domain out and compared profile classes with continuous cognitive, affective and cardiometabolic/chronic domain scores. "
        "Models used minimal-core covariate adjustment for age, education, marital status, smoking and drinking. Absolute risks were emphasized before adjusted odds ratios because functional deterioration was common."
    )
    validation_new = (
        "The main follow-up endpoint was functional deterioration of at least 0.5 SD from baseline. Because the original four-domain profile includes baseline function, functional deterioration is vulnerable to endpoint leakage. "
        "The primary validation guardrail therefore rebuilt profiles after leaving the functional domain out and compared profile classes with continuous cognitive, affective and cardiometabolic/chronic domain scores. "
        "Models used minimal-core covariate adjustment for age, education, marital status, smoking and drinking. Absolute risks were emphasized before adjusted odds ratios because functional deterioration was common. "
        "Hospitalization, institutionalization and care-dependence variables were audited as candidate hard endpoints but were not used unless cohort-level harmonization could be defended. "
        "Mortality was handled only as a secondary guardrail endpoint."
    )
    if validation_old in text:
        text = text.replace(validation_old, validation_new)

    hard_old = (
        "The harmonization matrix remained central to interpretation (Figure~\\ref{fig:harmonization-risk}). Functional-domain strictness differed across cohorts: CHARLS used IADL-only information, HRS used ADL-only information, KLoSA used a bridge proxy and SHARE remained validation-downgraded. "
        "Cognitive batteries were cohort-specific, SHARE affective symptoms used EURO-D, and cardiometabolic/chronic disease indicators differed in lipid/cholesterol availability. Mortality analyses were available but were kept secondary because proportional-hazards or piecewise time-drift flags were present in several cohorts. Hospitalization, institutionalization, care dependence and survey-design weights were not harmonized in the current output set and were not introduced into the main claims."
    )
    hard_new = (
        "The harmonization matrix remained central to interpretation and is retained as Supplementary Figure S4. Functional-domain strictness differed across cohorts: CHARLS used IADL-only information, HRS used ADL-only information, KLoSA used a bridge proxy and SHARE remained validation-downgraded. "
        "Cognitive batteries were cohort-specific, SHARE affective symptoms used EURO-D, and cardiometabolic/chronic disease indicators differed in lipid/cholesterol availability. A Phase 38 audit did not identify a codebook-confirmed harmonized survey-design triplet of analysis weight, primary sampling unit and strata across the seven cleaned files, so no survey-weighted prevalence claim is made. "
        "A baseline male-comparator domain table was generated with the same baseline scoring rules, but outcome-level sex-interaction models were not introduced because the longitudinal profile-validation pipeline remains women-only. Hospitalization, institutionalization and care-dependence candidates remained non-harmonized header-level evidence. Mortality analyses were available but were kept secondary because proportional-hazards or piecewise time-drift flags were present in several cohorts."
    )
    if hard_old in text:
        text = text.replace(hard_old, hard_new)
    text = text.replace(
        "Supplementary Figure~\\ref{fig:supp-harmonization-risk}",
        "Supplementary Figure S4",
    )

    fig4_block = r"""
\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth,height=0.78\textheight,keepaspectratio]{figure4_harmonization_risk_matrix-re.pdf}
\caption{Cohort-domain harmonization risk matrix. Cells show source tier, non-missing percentage and the principal construct used for each burden domain. The matrix makes the main measurement guardrails visible and should be read as a measurement-risk figure rather than as a biological result figure.}
\label{fig:harmonization-risk}
\end{figure}
"""
    if fig4_block in text:
        text = text.replace(fig4_block, "")

    women_old = (
        "The women-only scope is also deliberately conservative. The analysis addresses older women as a clinically important population with high late-life disability burden, but it does not establish sex-specific mechanisms. "
        "A top-journal version would require male comparator analyses, sex-interaction tests and harmonized women-specific exposures such as reproductive history, menopause-related factors or caregiving burden. Those analyses were outside the current cleaned-output set."
    )
    women_new = (
        "The women-only scope is also deliberately conservative. The analysis addresses older women as a clinically important population with high late-life disability burden, but it does not establish sex-specific mechanisms. "
        "Phase 38 adds a supplementary baseline male-comparator audit using the same domain-scoring rules, which helps document feasibility and denominator differences. It still does not provide outcome-level sex-interaction validation or women-specific mechanism testing. "
        "A stronger women-health version would require all-sex longitudinal profile models, formal sex interactions and harmonized women-specific exposures such as reproductive history, menopause-related factors or caregiving burden."
    )
    if women_old in text:
        text = text.replace(women_old, women_new)

    limits_old = (
        "Strengths include the seven-cohort scope, codebook-confirmed sex coding, explicit denominator locking, separation of strict-core primary evidence from sensitivity tiers, baseline clinical characterization, included-versus-excluded missingness auditing, item-level harmonization review, leave-functional-domain-out validation and algorithm-robustness diagnostics. Limitations remain substantial. Domain measures were harmonized by orientation and within-cohort standardization but were not instrument-identical across cohorts. Survey weights, strata and primary sampling units were not harmonized in the current output set. Validation remained within-cohort association rather than transport validation. LASI lacked a follow-up validation denominator, SHARE was validation-downgraded and KLoSA used a functional bridge. Mortality was available only as secondary evidence with proportional-hazards and piecewise guardrails. The current study therefore cannot claim population prevalence, stable latent endotypes, independent hard-outcome validation or superiority over continuous domain scores."
    )
    limits_new = (
        "Strengths include the seven-cohort scope, codebook-confirmed sex coding, explicit denominator locking, separation of strict-core primary evidence from sensitivity tiers, baseline clinical characterization, included-versus-excluded missingness auditing, item-level harmonization review, leave-functional-domain-out validation, algorithm-robustness diagnostics and a post-review guardrail audit of unresolved design and outcome issues. Limitations remain substantial. Domain measures were harmonized by orientation and within-cohort standardization but were not instrument-identical across cohorts. Survey weights, strata and primary sampling units were screened but not codebook-confirmed as a common seven-cohort design set, so the analyses are not survey-weighted population estimates. Validation remained within-cohort association rather than transport validation. LASI lacked a follow-up validation denominator, SHARE was validation-downgraded and KLoSA used a functional bridge. Hospitalization, institutionalization and care-dependence endpoints were not currently unified. Mortality was available only as secondary evidence with proportional-hazards and piecewise guardrails. The current study therefore cannot claim population prevalence, stable latent endotypes, sex-specific mechanisms, independent hard-outcome validation or superiority over continuous domain scores."
    )
    if limits_old in text:
        text = text.replace(limits_old, limits_new)

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
Additional file 19: Phase 38 survey-design variable audit.\\
Additional file 20: Phase 38 baseline male-comparator domain summary.\\
Additional file 21: Phase 38 baseline male-comparator domain contrasts.\\
Additional file 22: Phase 38 hospitalization, institutionalization and care-dependence candidate audit.\\
Additional file 23: Phase 38 mortality secondary guardrail table.\\
Additional file 24: Phase 38 unresolved issue resolution matrix.\\
Supplementary Figures S1-S4: Previous figure set and harmonization-risk matrix, placed after the references.

"""
    if r"\section*{Additional files}" in text and r"\bibliography{" in text:
        text = replace_between(text, r"\section*{Additional files}", r"\bibliography{", add_files)

    bib = r"\bibliography{bmc_geriatrics_refs}"
    if bib in text:
        text = text[: text.index(bib)] + bib + "\n" + supplementary_figure_block() + "\n" + r"\end{document}" + "\n"
    TEX.write_text(text, encoding="utf-8")


def copy_additional_files() -> None:
    mapping = {
        "additional_file_19_phase38_survey_design_variable_audit.csv": OUT / "phase38_survey_design_variable_audit.csv",
        "additional_file_20_phase38_sex_comparator_domain_summary.csv": OUT / "phase38_sex_comparator_domain_summary.csv",
        "additional_file_21_phase38_sex_comparator_domain_contrasts.csv": OUT / "phase38_sex_comparator_domain_contrasts.csv",
        "additional_file_22_phase38_hard_outcome_candidate_audit.csv": OUT / "phase38_hard_outcome_candidate_audit.csv",
        "additional_file_23_phase38_mortality_secondary_guardrail_table.csv": OUT / "phase38_mortality_secondary_guardrail_table.csv",
        "additional_file_24_phase38_unresolved_issue_resolution_matrix.csv": OUT / "phase38_unresolved_issue_resolution_matrix.csv",
    }
    for name, src in mapping.items():
        if src.exists():
            shutil.copyfile(src, PKG / name)


def update_readme() -> None:
    readme = PKG / "README_BMC_Geriatrics_burden_profiles_rescue.md"
    text = readme.read_text(encoding="utf-8") if readme.exists() else "# BMC Geriatrics burden profile rescue package\n"
    add = """

## Phase 38 unresolved guardrail package

- Moved the previous Fig1-4 set into the post-reference Supplementary figures section.
- Added a cleaned-header survey-design audit for weights, PSU and strata candidates; no survey-weighted population-prevalence claim is made.
- Added an all-sex baseline domain comparator using the same Phase3 scoring rules; outcome-level sex-interaction validation remains unclaimed.
- Added hospitalization, institutionalization and care-dependence candidate audits; these endpoints remain non-harmonized and are not used as primary validation.
- Added a mortality secondary guardrail table; mortality remains secondary rather than a primary hard endpoint.
"""
    if "## Phase 38 unresolved guardrail package" not in text:
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
    parser.add_argument("--data-root", type=Path)
    parser.add_argument("--database-root", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=OUT)
    parser.add_argument("--zip-only", action="store_true")
    args = parser.parse_args()

    if args.zip_only:
        copy_additional_files()
        update_readme()
        rebuild_zips()
        print(PKG / "bmc_geriatrics_submission_burden_profiles_rescue_source_only.zip")
        print(PKG / "bmc_geriatrics_submission_burden_profiles_rescue_pdf_ready.zip")
        return

    if args.data_root is None:
        raise SystemExit("--data-root is required unless --zip-only is used")

    args.output_dir.mkdir(parents=True, exist_ok=True)

    survey = build_candidate_audit(args.data_root, SURVEY_RE, "survey_design")
    hard = build_candidate_audit(args.data_root, HARD_RE, "hard_outcome")
    all_sex_scores = build_all_sex_scores(args.data_root, args.database_root)
    sex_summary, sex_contrasts = summarize_sex_comparator(all_sex_scores)
    mortality = build_mortality_guardrail()
    issue_matrix = build_issue_matrix(survey, hard, sex_summary, mortality)

    survey.to_csv(args.output_dir / "phase38_survey_design_variable_audit.csv", index=False, encoding="utf-8-sig")
    hard.to_csv(args.output_dir / "phase38_hard_outcome_candidate_audit.csv", index=False, encoding="utf-8-sig")
    all_sex_scores.to_csv(args.output_dir / "phase38_all_sex_selected_domain_scores.csv", index=False, encoding="utf-8-sig")
    sex_summary.to_csv(args.output_dir / "phase38_sex_comparator_domain_summary.csv", index=False, encoding="utf-8-sig")
    sex_contrasts.to_csv(args.output_dir / "phase38_sex_comparator_domain_contrasts.csv", index=False, encoding="utf-8-sig")
    mortality.to_csv(args.output_dir / "phase38_mortality_secondary_guardrail_table.csv", index=False, encoding="utf-8-sig")
    issue_matrix.to_csv(args.output_dir / "phase38_unresolved_issue_resolution_matrix.csv", index=False, encoding="utf-8-sig")
    write_phase38_report(issue_matrix)

    update_tex(issue_matrix)
    copy_additional_files()
    update_readme()
    rebuild_zips()

    print(args.output_dir / "phase38_survey_design_variable_audit.csv")
    print(args.output_dir / "phase38_sex_comparator_domain_summary.csv")
    print(args.output_dir / "phase38_hard_outcome_candidate_audit.csv")
    print(args.output_dir / "phase38_mortality_secondary_guardrail_table.csv")
    print(args.output_dir / "phase38_unresolved_issue_resolution_matrix.csv")
    print(TEX)


if __name__ == "__main__":
    main()
