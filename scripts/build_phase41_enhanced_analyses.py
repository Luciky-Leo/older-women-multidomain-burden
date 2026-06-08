from __future__ import annotations

import argparse
import math
import re
import shutil
import sys
import warnings
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from sklearn.metrics import roc_auc_score


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
PKG = ROOT / "manuscript" / "bmc_geriatrics_submission_burden_profiles_rescue"
TEX = PKG / "bmc_geriatrics_main.tex"

sys.path.insert(0, str(ROOT / "scripts"))
from build_phase3_domain_scores import (  # noqa: E402
    ANALYSIS_SELECTIONS,
    COHORT_CONFIG,
    DOMAIN_NAMES,
    find_clean_csv,
    read_header_map,
    score_cohort,
    to_numeric,
)
from build_phase36_clinical_tables_and_robustness import (  # noqa: E402
    model_frame_for_lfo,
)
from build_phase38_unresolved_guardrail_package import (  # noqa: E402
    read_all_sex_cohort_frame,
)


COHORT_ORDER = ["CHARLS", "ELSA", "HRS", "KLoSA", "LASI", "MHAS", "SHARE"]
STRICT_CORE = ["CHARLS", "ELSA", "HRS", "MHAS"]
SENSITIVITY = ["KLoSA", "LASI", "SHARE"]
PROFILE_DOMAIN_COLUMNS = [
    "cognitive_score",
    "affective_score",
    "cardiometabolic_chronic_score",
]
ALL_DOMAIN_COLUMNS = [
    "functional_score",
    *PROFILE_DOMAIN_COLUMNS,
]
LFO_OUTCOME = "functional_deterioration_ge_0_5sd"
LFO_AVAILABLE = "functional_deterioration_available"
SURVEY_PATTERNS = {
    "weight": [
        r"\b(weight|weights|wgt|wgts|pweight|iweight|hhweight|raked)\b",
        r"\b(wtresp|wtperson|indwt|hhwt|xwgt|chwgt|wght)\b",
        r"(sample|sampling|survey|cross[- ]?sectional|longitudinal).{0,40}\b(weight|wgt|wt)\b",
    ],
    "psu": [
        r"\bpsu\b",
        r"\bcluster\b",
        r"primary.{0,25}sampling",
        r"sampling.{0,25}unit",
    ],
    "strata": [
        r"\bstrata\b",
        r"\bstratum\b",
        r"\bstratification\b",
        r"\bstrat\b",
    ],
}
SURVEY_RE = {
    concept: [re.compile(pattern, re.I) for pattern in patterns]
    for concept, patterns in SURVEY_PATTERNS.items()
}
BODY_WEIGHT_RE = re.compile(
    r"(self[- ]?reported.{0,20}weight|body.{0,20}weight|weight.{0,10}kg|kg\))",
    re.I,
)
TEXT_SUFFIXES = {".do", ".txt", ".md", ".sas", ".sps", ".r", ".html", ".htm"}


def read_csv(name: str, **kwargs) -> pd.DataFrame:
    return pd.read_csv(OUT / name, low_memory=False, **kwargs)


def normalize_wave(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if text.endswith(".0"):
        return text[:-2]
    return text


def tex_escape(value: object) -> str:
    if value is None or pd.isna(value):
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


def safe_exp(value: float) -> float:
    if pd.isna(value):
        return np.nan
    if value > 700:
        return math.inf
    if value < -700:
        return 0.0
    return float(math.exp(value))


def safe_pct(num: float, den: float) -> float:
    if not den or pd.isna(den):
        return np.nan
    return float(num) / float(den) * 100.0


def role_for(cohort: str) -> str:
    if cohort in STRICT_CORE:
        return "strict-core"
    if cohort == "KLoSA":
        return "bridge sensitivity"
    if cohort == "LASI":
        return "baseline-only descriptive"
    if cohort == "SHARE":
        return "validation-downgraded sensitivity"
    return "sensitivity"


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


def clean_term(term: str) -> str:
    match = re.search(r"\[T\.?(.+)\]", str(term))
    if match:
        return match.group(1)
    return str(term)


def build_mortality_secondary_table() -> pd.DataFrame:
    comparison = read_csv("phase14_mortality_covariate_model_comparison.csv")
    terms = read_csv("phase14_mortality_covariate_model_terms.csv")
    guardrail = read_csv("phase28_mortality_sensitivity_guardrails.csv")

    adjustment_priority = ["minimal_core", "expanded_core", "minimal_plus_bmi"]
    rows: list[dict[str, object]] = []
    for cohort in COHORT_ORDER:
        cohort_rows = comparison[comparison["cohort"].eq(cohort)].copy()
        if cohort_rows.empty:
            rows.append(
                {
                    "cohort": cohort,
                    "role": role_for(cohort),
                    "analysis_status": "unavailable",
                    "chosen_adjustment": "NA",
                    "n": np.nan,
                    "deaths": np.nan,
                    "event_pct": np.nan,
                    "median_followup_years": np.nan,
                    "endotype_partial_aic": np.nan,
                    "severity_tertile_partial_aic": np.nan,
                    "delta_aic_severity_minus_endotype": np.nan,
                    "aic_favored_model": "NA",
                    "highest_endotype_hr_class": "NA",
                    "highest_endotype_hr": np.nan,
                    "highest_endotype_hr_ci": "NA",
                    "ph_screen_flag": np.nan,
                    "large_time_drift_terms": np.nan,
                    "direction_change_terms": np.nan,
                    "interpretation": "No current mortality follow-up model row; keep outside validation denominator.",
                }
            )
            continue

        chosen = None
        for adjustment in adjustment_priority:
            candidate = cohort_rows[cohort_rows["adjustment"].eq(adjustment)]
            if not candidate.empty:
                chosen = candidate.iloc[0]
                break
        if chosen is None:
            chosen = cohort_rows.iloc[0]
        adjustment = str(chosen["adjustment"])
        term_frame = terms[
            terms["cohort"].eq(cohort)
            & terms["model_type"].eq("endotype")
            & terms["adjustment"].eq(adjustment)
            & terms["term"].astype(str).str.contains("endotype_class", regex=False)
        ].copy()
        highest = None if term_frame.empty else term_frame.sort_values("hr", ascending=False).iloc[0]
        delta = chosen.get("delta_partial_aic_severity_tertile_minus_endotype", np.nan)
        if pd.isna(delta):
            favored = "not comparable"
        elif float(delta) > 2:
            favored = "endotype"
        elif float(delta) < -2:
            favored = "severity tertile"
        else:
            favored = "similar"
        g = guardrail[guardrail["cohort"].eq(cohort)]
        g_row = g.iloc[0] if not g.empty else pd.Series(dtype=object)
        rows.append(
            {
                "cohort": cohort,
                "role": role_for(cohort),
                "analysis_status": "formal secondary Cox model",
                "chosen_adjustment": adjustment,
                "n": chosen.get("n_endotype", np.nan),
                "deaths": chosen.get("events_endotype", np.nan),
                "event_pct": chosen.get("event_pct_endotype", np.nan),
                "median_followup_years": chosen.get("median_followup_time_years_endotype", np.nan),
                "endotype_partial_aic": chosen.get("partial_aic_endotype", np.nan),
                "severity_tertile_partial_aic": chosen.get("partial_aic_severity_tertile", np.nan),
                "delta_aic_severity_minus_endotype": delta,
                "aic_favored_model": favored,
                "highest_endotype_hr_class": clean_term(highest["term"]) if highest is not None else "NA",
                "highest_endotype_hr": highest["hr"] if highest is not None else np.nan,
                "highest_endotype_hr_ci": f"{highest['ci_low']:.2f} to {highest['ci_high']:.2f}"
                if highest is not None
                else "NA",
                "ph_screen_flag": g_row.get("ph_screen_flag", np.nan),
                "large_time_drift_terms": g_row.get("large_time_drift_terms", np.nan),
                "direction_change_terms": g_row.get("direction_change_terms", np.nan),
                "interpretation": "Secondary non-circular endpoint only; not primary validation.",
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "phase41_mortality_secondary_formal_model_table.csv", index=False, encoding="utf-8-sig")
    return out


def read_covariates_for_merge() -> pd.DataFrame:
    cov = read_csv("phase13_covariate_participant_screen.csv", dtype={"participant_id": str, "wave": str})
    cov["wave"] = cov["wave"].map(normalize_wave)
    keep = [
        "analysis_set",
        "analysis_tier",
        "cohort",
        "participant_id",
        "wave",
        "cov_education_raw",
        "cov_marital_status_raw",
        "cov_smoking_raw",
        "cov_drinking_raw",
    ]
    return cov[[column for column in keep if column in cov.columns]].drop_duplicates(
        ["analysis_set", "analysis_tier", "cohort", "participant_id", "wave"]
    )


def preferred_hospitalization_variables(audit: pd.DataFrame, cohort: str) -> list[str]:
    candidates = audit[
        audit["cohort"].eq(cohort)
        & audit["concept"].eq("hospitalization")
        & audit["harmonization_status"].eq("candidate_header_only")
        & audit["variable"].astype(str).ne("")
    ]["variable"].astype(str).tolist()
    priority = ["hospital", "hosp", "hosp1y", "hospital_time"]
    ordered = [var for var in priority if var in candidates]
    ordered.extend([var for var in candidates if var not in ordered])
    return ordered


def read_hospitalization_long(data_root: Path, cohort: str, variables: list[str]) -> pd.DataFrame:
    config = COHORT_CONFIG[cohort]
    if not config["wave"] or not variables:
        return pd.DataFrame()
    path = find_clean_csv(data_root, str(config["file"]))
    header_map = read_header_map(path)
    wanted = {str(config["id"]), str(config["wave"]), *variables}
    available = {var: header_map[var] for var in wanted if var in header_map}
    if str(config["id"]) not in available or str(config["wave"]) not in available:
        return pd.DataFrame()
    frame = pd.read_csv(
        path,
        usecols=list(available.values()),
        dtype=str,
        encoding="utf-8-sig",
        low_memory=False,
    ).rename(columns={raw: var for var, raw in available.items()})
    frame["cohort"] = cohort
    frame["participant_id"] = frame[str(config["id"])].astype("string")
    frame["wave"] = frame[str(config["wave"])].map(normalize_wave)
    frame["wave_num"] = pd.to_numeric(frame["wave"], errors="coerce")
    observed = pd.Series(False, index=frame.index)
    event = pd.Series(False, index=frame.index)
    used_vars = []
    for variable in variables:
        if variable not in frame.columns:
            continue
        values = to_numeric(frame[variable])
        valid = values.notna()
        if variable.endswith("time"):
            var_event = values > 0
        else:
            var_event = values.eq(1)
        observed = observed | valid
        event = event | (valid & var_event)
        used_vars.append(variable)
    if not used_vars:
        return pd.DataFrame()
    frame["hospitalization_observed"] = observed.astype(int)
    frame["hospitalization_event"] = event.astype(int)
    frame["hospitalization_variables_used"] = "+".join(used_vars)
    return frame[
        [
            "cohort",
            "participant_id",
            "wave",
            "wave_num",
            "hospitalization_observed",
            "hospitalization_event",
            "hospitalization_variables_used",
        ]
    ]


def build_hospitalization_candidate_screen(data_root: Path) -> pd.DataFrame:
    assignments = read_csv("phase4_best_model_assignments.csv", dtype={"participant_id": str, "wave": str})
    assignments["wave"] = assignments["wave"].map(normalize_wave)
    assignments["baseline_wave_num"] = pd.to_numeric(assignments["wave"], errors="coerce")
    for col in ["age", "severity_score", *ALL_DOMAIN_COLUMNS]:
        assignments[col] = pd.to_numeric(assignments[col], errors="coerce")
    assignments["endotype_class"] = assignments["endotype_class"].astype(str)
    audit = read_csv("phase38_hard_outcome_candidate_audit.csv")

    screens = []
    status_rows = []
    for cohort in COHORT_ORDER:
        vars_for_cohort = preferred_hospitalization_variables(audit, cohort)
        long = read_hospitalization_long(data_root, cohort, vars_for_cohort)
        base = assignments[assignments["cohort"].eq(cohort)].copy()
        if long.empty or base.empty:
            status_rows.append(
                {
                    "cohort": cohort,
                    "endpoint": "hospitalization",
                    "status": "not modelable in current cleaned pass",
                    "variables_used": "+".join(vars_for_cohort),
                    "reason": "no candidate variable or no wave structure",
                }
            )
            continue
        candidates = base.merge(long, on=["cohort", "participant_id"], how="left", suffixes=("", "_follow"))
        candidates = candidates[candidates["wave_num"] > candidates["baseline_wave_num"]].copy()
        observed = candidates[candidates["hospitalization_observed"].eq(1)].copy()
        if observed.empty:
            status_rows.append(
                {
                    "cohort": cohort,
                    "endpoint": "hospitalization",
                    "status": "not modelable in current cleaned pass",
                    "variables_used": "+".join(vars_for_cohort),
                    "reason": "no post-baseline observed hospitalization rows",
                }
            )
            continue
        grouped = (
            observed.groupby(["analysis_set", "analysis_tier", "cohort", "participant_id"], dropna=False)
            .agg(
                hospitalization_followup_rows=("hospitalization_observed", "sum"),
                hospitalization_event=("hospitalization_event", "max"),
                last_hospitalization_wave_num=("wave_num", "max"),
                hospitalization_variables_used=("hospitalization_variables_used", "first"),
            )
            .reset_index()
        )
        screen = base.merge(
            grouped,
            on=["analysis_set", "analysis_tier", "cohort", "participant_id"],
            how="left",
        )
        screen["hospitalization_followup_rows"] = screen["hospitalization_followup_rows"].fillna(0).astype(int)
        screen["hospitalization_available"] = (screen["hospitalization_followup_rows"] > 0).astype(int)
        screen["hospitalization_event"] = screen["hospitalization_event"].where(
            screen["hospitalization_available"].eq(1)
        )
        screens.append(screen)
        available = screen[screen["hospitalization_available"].eq(1)]
        status_rows.append(
            {
                "cohort": cohort,
                "endpoint": "hospitalization",
                "status": "candidate modelable",
                "variables_used": "+".join(vars_for_cohort),
                "reason": "header-only candidate; codebook confirmation still required",
                "n": len(available),
                "events": int(available["hospitalization_event"].sum()) if not available.empty else 0,
                "event_pct": safe_pct(available["hospitalization_event"].sum(), len(available)) if not available.empty else np.nan,
            }
        )
    screen_out = pd.concat(screens, ignore_index=True) if screens else pd.DataFrame()
    status_out = pd.DataFrame(status_rows)
    screen_out.to_csv(OUT / "phase41_hospitalization_candidate_participant_screen.csv", index=False, encoding="utf-8-sig")
    status_out.to_csv(OUT / "phase41_hospitalization_candidate_status.csv", index=False, encoding="utf-8-sig")
    return screen_out


def fit_candidate_logistic(data: pd.DataFrame, formula: str):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return smf.glm(formula=formula, data=data, family=sm.families.Binomial()).fit(maxiter=200)


def summarize_logistic_fit(fit, data: pd.DataFrame, model_type: str, outcome: str) -> tuple[dict[str, object], pd.DataFrame]:
    pred = fit.predict(data)
    auc = np.nan
    if data[outcome].nunique() == 2:
        auc = float(roc_auc_score(data[outcome], pred))
    metrics = {
        "analysis_set": data["analysis_set"].iloc[0],
        "analysis_tier": data["analysis_tier"].iloc[0],
        "cohort": data["cohort"].iloc[0],
        "outcome": outcome,
        "model_type": model_type,
        "n": int(len(data)),
        "events": int(data[outcome].sum()),
        "event_pct": float(data[outcome].mean() * 100.0),
        "aic": float(fit.aic),
        "auc": auc,
        "converged": int(bool(getattr(fit, "converged", True))),
    }
    conf = fit.conf_int()
    rows = []
    for term, estimate in fit.params.items():
        lo, hi = conf.loc[term]
        rows.append(
            {
                **{k: metrics[k] for k in ["analysis_set", "analysis_tier", "cohort", "outcome", "model_type"]},
                "term": term,
                "term_label": clean_term(term),
                "log_or": float(estimate),
                "or": safe_exp(float(estimate)),
                "ci_low": safe_exp(float(lo)),
                "ci_high": safe_exp(float(hi)),
                "p_value": float(fit.pvalues[term]),
            }
        )
    return metrics, pd.DataFrame(rows)


def run_hospitalization_candidate_models(screen: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if screen.empty:
        empty = pd.DataFrame()
        empty.to_csv(OUT / "phase41_hospitalization_candidate_model_metrics.csv", index=False)
        empty.to_csv(OUT / "phase41_hospitalization_candidate_model_terms.csv", index=False)
        empty.to_csv(OUT / "phase41_hospitalization_candidate_model_comparison.csv", index=False)
        return empty, empty, empty

    model_specs = [
        ("endotype_age", "hospitalization_event ~ C(endotype_class, Treatment(reference='1')) + age"),
        ("severity_score_age", "hospitalization_event ~ severity_score + age"),
        (
            "four_domain_scores_age",
            "hospitalization_event ~ functional_score + cognitive_score + affective_score + cardiometabolic_chronic_score + age",
        ),
    ]
    metrics_rows = []
    term_frames = []
    skipped_rows = []
    for cohort, g in screen.groupby("cohort", dropna=False):
        available = g[g["hospitalization_available"].eq(1)].copy()
        for model_type, formula in model_specs:
            required = ["hospitalization_event", "age"]
            if "severity_score" in formula:
                required.append("severity_score")
            if "endotype_class" in formula:
                required.append("endotype_class")
            for col in ALL_DOMAIN_COLUMNS:
                if col in formula:
                    required.append(col)
            data = available.dropna(subset=required).copy()
            data["hospitalization_event"] = data["hospitalization_event"].astype(int)
            if data.empty or data["hospitalization_event"].sum() < 20 or (len(data) - data["hospitalization_event"].sum()) < 20:
                skipped_rows.append(
                    {
                        "cohort": cohort,
                        "model_type": model_type,
                        "n": len(data),
                        "events": int(data["hospitalization_event"].sum()) if not data.empty else 0,
                        "skip_reason": "too_few_events_or_nonevents",
                    }
                )
                continue
            try:
                fit = fit_candidate_logistic(data, formula)
                metrics, terms = summarize_logistic_fit(fit, data, model_type, "hospitalization_event")
                metrics["candidate_status"] = "header-only; not codebook-confirmed"
                metrics_rows.append(metrics)
                term_frames.append(terms)
            except Exception as exc:  # pragma: no cover
                skipped_rows.append(
                    {
                        "cohort": cohort,
                        "model_type": model_type,
                        "n": len(data),
                        "events": int(data["hospitalization_event"].sum()) if not data.empty else 0,
                        "skip_reason": f"fit_failed: {type(exc).__name__}: {exc}",
                    }
                )
    metrics = pd.DataFrame(metrics_rows)
    terms = pd.concat(term_frames, ignore_index=True) if term_frames else pd.DataFrame()
    if metrics.empty:
        comparison = pd.DataFrame()
    else:
        comparison = metrics.pivot_table(
            index=["analysis_set", "analysis_tier", "cohort"],
            columns="model_type",
            values=["n", "events", "event_pct", "aic", "auc"],
            aggfunc="first",
        )
        comparison.columns = [f"{metric}_{model}" for metric, model in comparison.columns]
        comparison = comparison.reset_index()
        if "aic_endotype_age" in comparison.columns and "aic_severity_score_age" in comparison.columns:
            comparison["delta_aic_severity_minus_endotype"] = (
                comparison["aic_severity_score_age"] - comparison["aic_endotype_age"]
            )
        if "auc_endotype_age" in comparison.columns and "auc_severity_score_age" in comparison.columns:
            comparison["delta_auc_endotype_minus_severity"] = (
                comparison["auc_endotype_age"] - comparison["auc_severity_score_age"]
            )
    skipped = pd.DataFrame(skipped_rows)
    metrics.to_csv(OUT / "phase41_hospitalization_candidate_model_metrics.csv", index=False, encoding="utf-8-sig")
    terms.to_csv(OUT / "phase41_hospitalization_candidate_model_terms.csv", index=False, encoding="utf-8-sig")
    comparison.to_csv(OUT / "phase41_hospitalization_candidate_model_comparison.csv", index=False, encoding="utf-8-sig")
    skipped.to_csv(OUT / "phase41_hospitalization_candidate_model_skipped.csv", index=False, encoding="utf-8-sig")
    return metrics, terms, comparison


def cohort_from_path(path: Path) -> str | None:
    text = str(path).lower()
    aliases = {
        "CHARLS": ["charls"],
        "ELSA": ["elsa"],
        "HRS": ["hrs"],
        "KLoSA": ["klosa"],
        "LASI": ["lasi"],
        "MHAS": ["mhas"],
        "SHARE": ["share"],
    }
    for cohort, names in aliases.items():
        if any(name in text for name in names):
            return cohort
    return None


def survey_concept_for_text(text: str) -> list[str]:
    matches = []
    for concept, patterns in SURVEY_RE.items():
        if any(pattern.search(text) for pattern in patterns):
            matches.append(concept)
    return matches


def build_survey_raw_codebook_audit(database_root: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict[str, object]] = []
    cleaned = read_csv("phase38_survey_design_variable_audit.csv")
    for row in cleaned.to_dict("records"):
        if row.get("variable"):
            rows.append(
                {
                    "cohort": row["cohort"],
                    "concept": row["concept"],
                    "source_type": "cleaned_header",
                    "variable_or_line": row["variable"],
                    "label_or_snippet": row.get("raw_header", ""),
                    "source_file": row.get("source_file", ""),
                    "evidence_status": "cleaned candidate only; requires codebook confirmation",
                }
            )

    # Stata variable labels from prepared working/harmonized data.
    for path in database_root.rglob("*.dta"):
        ptxt = str(path).lower()
        if not any(anchor in ptxt for anchor in ["working_data", "harmonized", "temp_data"]):
            continue
        cohort = cohort_from_path(path)
        if cohort is None:
            continue
        try:
            reader = pd.read_stata(str(path), iterator=True)
            labels = reader.variable_labels()
        except Exception:
            continue
        for variable, label in labels.items():
            haystack = f"{variable} {label}"
            if BODY_WEIGHT_RE.search(haystack):
                continue
            for concept in survey_concept_for_text(haystack):
                rows.append(
                    {
                        "cohort": cohort,
                        "concept": concept,
                        "source_type": "stata_label",
                        "variable_or_line": variable,
                        "label_or_snippet": str(label)[:300],
                        "source_file": str(path),
                        "evidence_status": "metadata mention; manual mapping required",
                    }
                )

    # Dofile/codebook text evidence. Limit snippets per cohort/concept/source type.
    snippet_counts: dict[tuple[str, str], int] = {}
    for path in database_root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        cohort = cohort_from_path(path)
        if cohort is None:
            continue
        try:
            if path.stat().st_size > 5_000_000:
                continue
        except OSError:
            continue
        try:
            handle = path.open("r", encoding="utf-8", errors="ignore")
        except OSError:
            continue
        with handle:
            for line_no, line in enumerate(handle, start=1):
                haystack = line.strip()
                if not haystack or BODY_WEIGHT_RE.search(haystack):
                    continue
                concepts = survey_concept_for_text(haystack)
                for concept in concepts:
                    key = (cohort, concept)
                    if snippet_counts.get(key, 0) >= 40:
                        continue
                    snippet_counts[key] = snippet_counts.get(key, 0) + 1
                    rows.append(
                        {
                            "cohort": cohort,
                            "concept": concept,
                            "source_type": "codebook_or_dofile_text",
                            "variable_or_line": f"line {line_no}",
                            "label_or_snippet": haystack[:300],
                            "source_file": str(path),
                            "evidence_status": "text mention; manual mapping required",
                        }
                    )
    audit = pd.DataFrame(rows).drop_duplicates()
    status_rows = []
    for cohort in COHORT_ORDER:
        g = audit[audit["cohort"].eq(cohort)]
        concept_status = {}
        for concept in ["weight", "psu", "strata"]:
            cg = g[g["concept"].eq(concept)]
            has_cleaned = int(cg["source_type"].eq("cleaned_header").any())
            has_metadata = int(cg["source_type"].isin(["stata_label", "codebook_or_dofile_text"]).any())
            concept_status[f"{concept}_cleaned_candidate"] = has_cleaned
            concept_status[f"{concept}_metadata_evidence"] = has_metadata
        complete = all(
            concept_status[f"{concept}_cleaned_candidate"] and concept_status[f"{concept}_metadata_evidence"]
            for concept in ["weight", "psu", "strata"]
        )
        status_rows.append(
            {
                "cohort": cohort,
                **concept_status,
                "harmonized_triplet_status": "candidate_triplet_needs_manual_confirmation"
                if complete
                else "no_codebook_confirmed_harmonized_triplet",
                "analysis_decision": "survey-weighted model not run in Phase41",
            }
        )
    status = pd.DataFrame(status_rows)
    audit.to_csv(OUT / "phase41_survey_design_raw_codebook_audit.csv", index=False, encoding="utf-8-sig")
    status.to_csv(OUT / "phase41_survey_design_triplet_status.csv", index=False, encoding="utf-8-sig")
    return audit, status


def build_all_sex_long_scores(data_root: Path, database_root: Path | None) -> pd.DataFrame:
    frames = []
    for cohort in COHORT_ORDER:
        raw = read_all_sex_cohort_frame(data_root, database_root, cohort)
        scored = score_cohort(raw.copy(), cohort)
        scored["ragender"] = raw.loc[scored.index, "ragender"].astype("string").to_numpy()
        scored["sex"] = scored["ragender"].map({"0": "female", "1": "male"})
        frames.append(scored)
    out = pd.concat(frames, ignore_index=True)
    for col in ["wave", "participant_id"]:
        out[col] = out[col].astype(str).map(normalize_wave)
    for col in ["age", *ALL_DOMAIN_COLUMNS]:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    out["wave_num"] = pd.to_numeric(out["wave"], errors="coerce")
    out["lfo_severity_score"] = out[PROFILE_DOMAIN_COLUMNS].mean(axis=1)
    out["complete_lfo_three_domain"] = out[PROFILE_DOMAIN_COLUMNS].notna().all(axis=1).astype(int)
    return out


def build_all_sex_lfo_screen(data_root: Path, database_root: Path | None) -> pd.DataFrame:
    scores = build_all_sex_long_scores(data_root, database_root)
    selected_frames = []
    for selection in ANALYSIS_SELECTIONS:
        subset = scores[
            scores["cohort"].eq(selection["cohort"])
            & scores["wave"].astype(str).eq(str(selection["wave"]))
        ].copy()
        subset.insert(0, "analysis_set", selection["analysis_set"])
        subset.insert(1, "analysis_tier", selection["tier"])
        selected_frames.append(subset)
    baseline = pd.concat(selected_frames, ignore_index=True) if selected_frames else pd.DataFrame()
    if baseline.empty:
        return baseline
    baseline = baseline[baseline["complete_lfo_three_domain"].eq(1)].copy()
    baseline = baseline.rename(columns={"wave": "baseline_wave", "wave_num": "baseline_wave_num"})
    follow = scores[
        [
            "cohort",
            "participant_id",
            "wave",
            "wave_num",
            "functional_score",
            "age",
        ]
    ].rename(
        columns={
            "wave": "followup_wave",
            "wave_num": "followup_wave_num",
            "functional_score": "followup_functional_score",
            "age": "followup_age",
        }
    )
    candidates = baseline.merge(follow, on=["cohort", "participant_id"], how="left")
    candidates = candidates[candidates["followup_wave_num"] > candidates["baseline_wave_num"]].copy()
    keys = ["analysis_set", "analysis_tier", "cohort", "participant_id"]
    counts = (
        candidates.groupby(keys, dropna=False)
        .agg(
            followup_rows=("followup_wave", "size"),
            max_followup_age=("followup_age", "max"),
        )
        .reset_index()
    )
    last = candidates.sort_values(keys + ["followup_wave_num"]).drop_duplicates(keys, keep="last")
    last = last[
        [
            *keys,
            "followup_wave",
            "followup_wave_num",
            "followup_functional_score",
            "followup_age",
        ]
    ].copy()
    screen = baseline.merge(counts, on=keys, how="left").merge(last, on=keys, how="left")
    screen["followup_rows"] = screen["followup_rows"].fillna(0).astype(int)
    screen["functional_deterioration_change"] = screen["followup_functional_score"] - screen["functional_score"]
    available = screen["functional_score"].notna() & screen["followup_functional_score"].notna()
    screen[LFO_AVAILABLE] = available.astype(int)
    screen[LFO_OUTCOME] = np.nan
    screen.loc[available, LFO_OUTCOME] = (
        screen.loc[available, "functional_deterioration_change"] >= 0.5
    ).astype(int)
    screen["sex_male"] = screen["sex"].eq("male").astype(int)
    screen.to_csv(OUT / "phase41_all_sex_lfo_longitudinal_screen.csv", index=False, encoding="utf-8-sig")
    return screen


def run_all_sex_sex_interaction(screen: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    term_frames = []
    skipped = []
    for cohort, g in screen.groupby("cohort", dropna=False):
        data = g[g[LFO_AVAILABLE].eq(1)].dropna(
            subset=[LFO_OUTCOME, "sex_male", "lfo_severity_score", "age"]
        ).copy()
        data[LFO_OUTCOME] = data[LFO_OUTCOME].astype(int)
        if (
            data.empty
            or data["sex_male"].nunique() < 2
            or data[LFO_OUTCOME].sum() < 20
            or (len(data) - data[LFO_OUTCOME].sum()) < 20
        ):
            skipped.append(
                {
                    "cohort": cohort,
                    "n": len(data),
                    "events": int(data[LFO_OUTCOME].sum()) if not data.empty else 0,
                    "male_n": int(data["sex_male"].sum()) if not data.empty else 0,
                    "skip_reason": "too_few_events_or_one_sex",
                }
            )
            continue
        formula = f"{LFO_OUTCOME} ~ sex_male + lfo_severity_score + sex_male:lfo_severity_score + age"
        try:
            fit = fit_candidate_logistic(data, formula)
            metrics, terms = summarize_logistic_fit(fit, data, "all_sex_lfo_severity_sex_interaction", LFO_OUTCOME)
            metrics["female_n"] = int((data["sex_male"] == 0).sum())
            metrics["male_n"] = int((data["sex_male"] == 1).sum())
            inter = terms[terms["term"].eq("sex_male:lfo_severity_score")]
            metrics["interaction_or"] = float(inter["or"].iloc[0]) if not inter.empty else np.nan
            metrics["interaction_ci"] = (
                f"{float(inter['ci_low'].iloc[0]):.2f} to {float(inter['ci_high'].iloc[0]):.2f}"
                if not inter.empty
                else "NA"
            )
            metrics["interaction_p_value"] = float(inter["p_value"].iloc[0]) if not inter.empty else np.nan
            metrics["scale_note"] = "all-sex baseline scale; not used for women-only profile construction"
            rows.append(metrics)
            term_frames.append(terms)
        except Exception as exc:  # pragma: no cover
            skipped.append(
                {
                    "cohort": cohort,
                    "n": len(data),
                    "events": int(data[LFO_OUTCOME].sum()) if not data.empty else 0,
                    "male_n": int(data["sex_male"].sum()) if not data.empty else 0,
                    "skip_reason": f"fit_failed: {type(exc).__name__}: {exc}",
                }
            )
    summary = pd.DataFrame(rows)
    terms = pd.concat(term_frames, ignore_index=True) if term_frames else pd.DataFrame()
    pd.DataFrame(skipped).to_csv(OUT / "phase41_all_sex_lfo_sex_interaction_skipped.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(OUT / "phase41_all_sex_lfo_sex_interaction_summary.csv", index=False, encoding="utf-8-sig")
    terms.to_csv(OUT / "phase41_all_sex_lfo_sex_interaction_terms.csv", index=False, encoding="utf-8-sig")
    return summary, terms


def clipped_logit(prob: np.ndarray) -> np.ndarray:
    p = np.clip(prob, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def net_benefit(y: np.ndarray, prob: np.ndarray, threshold: float) -> float:
    predicted = prob >= threshold
    tp = float(np.sum(predicted & (y == 1)))
    fp = float(np.sum(predicted & (y == 0)))
    n = float(len(y))
    return tp / n - fp / n * threshold / (1 - threshold)


def calibration_for_predictions(y: pd.Series, pred: np.ndarray) -> dict[str, float]:
    y_int = y.astype(int).to_numpy()
    out = {
        "observed_event_pct": float(np.mean(y_int) * 100.0),
        "mean_predicted_event_pct": float(np.mean(pred) * 100.0),
        "brier": float(np.mean((pred - y_int) ** 2)),
        "auc": float(roc_auc_score(y_int, pred)) if len(np.unique(y_int)) == 2 else np.nan,
        "calibration_intercept": np.nan,
        "calibration_slope": np.nan,
    }
    try:
        cal = pd.DataFrame({"y": y_int, "lp": clipped_logit(pred)})
        fit = smf.glm("y ~ lp", data=cal, family=sm.families.Binomial()).fit(maxiter=200)
        out["calibration_intercept"] = float(fit.params["Intercept"])
        out["calibration_slope"] = float(fit.params["lp"])
    except Exception:
        pass
    return out


def run_calibration_and_decision_curve() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df = model_frame_for_lfo()
    covars = ["age", "cov_education_raw", "cov_marital_status_raw", "cov_smoking_raw", "cov_drinking_raw"]
    profile_formula = (
        f"{LFO_OUTCOME} ~ age + cov_education_raw + cov_marital_status_raw + "
        "cov_smoking_raw + cov_drinking_raw + C(lfo_profile_class, Treatment(reference='1'))"
    )
    cont_formula = (
        f"{LFO_OUTCOME} ~ age + cov_education_raw + cov_marital_status_raw + "
        "cov_smoking_raw + cov_drinking_raw + cognitive_score + affective_score + cardiometabolic_chronic_score"
    )
    model_defs = [
        ("lfo_profile_adjusted", profile_formula, ["lfo_profile_class", *covars]),
        ("continuous_three_domain_adjusted", cont_formula, [*PROFILE_DOMAIN_COLUMNS, *covars]),
    ]
    thresholds = [0.10, 0.20, 0.30, 0.40, 0.50]
    metric_rows = []
    dca_rows = []
    decile_rows = []
    for cohort, g in df.groupby("cohort", dropna=False):
        for model_type, formula, required in model_defs:
            data = g.dropna(subset=[LFO_OUTCOME, *required]).copy()
            data[LFO_OUTCOME] = data[LFO_OUTCOME].astype(int)
            if "lfo_profile_class" in data.columns:
                data["lfo_profile_class"] = data["lfo_profile_class"].astype(int).astype(str)
            if data.empty or data[LFO_OUTCOME].nunique() < 2:
                continue
            try:
                fit = fit_candidate_logistic(data, formula)
                pred = np.asarray(fit.predict(data))
            except Exception:
                continue
            metrics = calibration_for_predictions(data[LFO_OUTCOME], pred)
            metric_rows.append(
                {
                    "cohort": cohort,
                    "role": role_for(cohort),
                    "model_type": model_type,
                    "n": int(len(data)),
                    "events": int(data[LFO_OUTCOME].sum()),
                    **metrics,
                }
            )
            y = data[LFO_OUTCOME].astype(int).to_numpy()
            for threshold in thresholds:
                event_rate = float(np.mean(y))
                dca_rows.append(
                    {
                        "cohort": cohort,
                        "role": role_for(cohort),
                        "model_type": model_type,
                        "threshold": threshold,
                        "net_benefit": net_benefit(y, pred, threshold),
                        "treat_all_net_benefit": event_rate - (1 - event_rate) * threshold / (1 - threshold),
                        "treat_none_net_benefit": 0.0,
                    }
                )
            decile = pd.DataFrame({"y": y, "pred": pred})
            try:
                decile["risk_decile"] = pd.qcut(decile["pred"].rank(method="first"), q=10, labels=False) + 1
                for dec, dg in decile.groupby("risk_decile"):
                    decile_rows.append(
                        {
                            "cohort": cohort,
                            "model_type": model_type,
                            "risk_decile": int(dec),
                            "n": int(len(dg)),
                            "observed_event_pct": float(dg["y"].mean() * 100.0),
                            "mean_predicted_event_pct": float(dg["pred"].mean() * 100.0),
                        }
                    )
            except Exception:
                pass
    metrics = pd.DataFrame(metric_rows)
    dca = pd.DataFrame(dca_rows)
    deciles = pd.DataFrame(decile_rows)
    if dca.empty:
        dca_summary = pd.DataFrame()
    else:
        wide = dca.pivot_table(
            index=["cohort", "threshold"],
            columns="model_type",
            values="net_benefit",
            aggfunc="first",
        ).reset_index()
        if {"continuous_three_domain_adjusted", "lfo_profile_adjusted"}.issubset(wide.columns):
            wide["continuous_minus_profile_net_benefit"] = (
                wide["continuous_three_domain_adjusted"] - wide["lfo_profile_adjusted"]
            )
        dca_summary = wide
    metrics.to_csv(OUT / "phase41_calibration_metrics.csv", index=False, encoding="utf-8-sig")
    dca.to_csv(OUT / "phase41_decision_curve_net_benefit.csv", index=False, encoding="utf-8-sig")
    dca_summary.to_csv(OUT / "phase41_decision_curve_summary.csv", index=False, encoding="utf-8-sig")
    deciles.to_csv(OUT / "phase41_calibration_deciles.csv", index=False, encoding="utf-8-sig")
    return metrics, dca, dca_summary


def build_phase41_guardrail_summary(
    mortality: pd.DataFrame,
    hosp_comp: pd.DataFrame,
    survey_status: pd.DataFrame,
    sex_summary: pd.DataFrame,
    calib: pd.DataFrame,
    dca_summary: pd.DataFrame,
) -> pd.DataFrame:
    rows = []
    mort_model = mortality[mortality["analysis_status"].eq("formal secondary Cox model")]
    mort_guarded = int(pd.to_numeric(mort_model["ph_screen_flag"], errors="coerce").fillna(0).sum())
    rows.append(
        {
            "domain": "All-cause mortality",
            "cohorts_or_n": f"{len(mort_model)} cohorts modelled; LASI unavailable",
            "phase41_analysis": "Covariate-adjusted Cox models using existing death-year/month screen.",
            "key_result": f"{mort_guarded} modelled cohorts had PH/time-drift guardrail flags; mortality stays secondary.",
            "manuscript_claim": "Secondary non-circular endpoint only; no primary validation claim.",
        }
    )
    hosp_cohorts = sorted(hosp_comp["cohort"].dropna().unique().tolist()) if not hosp_comp.empty else []
    rows.append(
        {
            "domain": "Hospitalization",
            "cohorts_or_n": ", ".join(hosp_cohorts) if hosp_cohorts else "none",
            "phase41_analysis": "Post-baseline candidate hospitalization logistic models where cleaned binary headers existed.",
            "key_result": "Header-only candidate evidence; institutional care and care dependence remained absent.",
            "manuscript_claim": "Sensitivity feasibility only until codebook mapping is completed.",
        }
    )
    complete_triplets = survey_status[
        survey_status["harmonized_triplet_status"].eq("candidate_triplet_needs_manual_confirmation")
    ]["cohort"].tolist()
    common_status = "no seven-cohort confirmed triplet"
    if len(complete_triplets) == len(COHORT_ORDER):
        common_status = "seven-cohort candidate triplet needs manual confirmation"
    rows.append(
        {
            "domain": "Survey design",
            "cohorts_or_n": common_status,
            "phase41_analysis": "Raw/codebook/dofile audit for weight, PSU and strata mentions.",
            "key_result": f"Candidate triplet evidence appeared in {len(complete_triplets)} cohorts, but no codebook-confirmed seven-cohort harmonized weight/PSU/strata triplet was available.",
            "manuscript_claim": "No survey-weighted prevalence or population estimate claim.",
        }
    )
    sex_cohorts = sorted(sex_summary["cohort"].dropna().unique().tolist()) if not sex_summary.empty else []
    sig = int((pd.to_numeric(sex_summary.get("interaction_p_value"), errors="coerce") < 0.05).sum()) if not sex_summary.empty else 0
    sig_text = f"{sig} fitted cohort{'s' if sig != 1 else ''}"
    rows.append(
        {
            "domain": "All-sex sex interaction",
            "cohorts_or_n": ", ".join(sex_cohorts) if sex_cohorts else "none",
            "phase41_analysis": "All-sex LFO severity-by-sex logistic interaction for functional deterioration.",
            "key_result": f"{sig_text} had nominal p<0.05 for the sex interaction on the all-sex scale.",
            "manuscript_claim": "Exploratory scale check; not evidence of women-specific mechanism.",
        }
    )
    strict_cal = calib[calib["cohort"].isin(STRICT_CORE)]
    if not strict_cal.empty:
        profile = strict_cal[strict_cal["model_type"].eq("lfo_profile_adjusted")]
        cont = strict_cal[strict_cal["model_type"].eq("continuous_three_domain_adjusted")]
        auc_text = (
            f"profile mean AUC {profile['auc'].mean():.3f}; continuous mean AUC {cont['auc'].mean():.3f}"
            if not profile.empty and not cont.empty
            else "calibration metrics generated"
        )
    else:
        auc_text = "calibration metrics generated"
    dca_favor_cont = 0
    dca_total = 0
    if not dca_summary.empty and "continuous_minus_profile_net_benefit" in dca_summary.columns:
        strict_dca = dca_summary[dca_summary["cohort"].isin(STRICT_CORE)]
        vals = pd.to_numeric(strict_dca["continuous_minus_profile_net_benefit"], errors="coerce")
        dca_total = int(vals.notna().sum())
        dca_favor_cont = int((vals > 0).sum())
    rows.append(
        {
            "domain": "Calibration and decision curve",
            "cohorts_or_n": "strict-core plus sensitivity rows",
            "phase41_analysis": "Calibration slope/intercept, Brier score and net benefit for profile versus continuous LFO models.",
            "key_result": f"{auc_text}; continuous net benefit exceeded profile in {dca_favor_cont}/{dca_total} strict-core thresholds.",
            "manuscript_claim": "Prediction superiority remains unsupported.",
        }
    )
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "phase41_secondary_endpoint_prediction_guardrail_summary.csv", index=False, encoding="utf-8-sig")
    return out


def table4_tex(summary: pd.DataFrame) -> str:
    lines = [
        r"\begin{table}[!htbp]",
        r"\caption{Phase 41 enhanced non-circular endpoint, survey-design, sex-interaction and prediction guardrails}\label{tab:phase41-guardrails}",
        r"\tiny",
        r"\setlength{\tabcolsep}{1pt}",
        r"\rowcolors{2}{tablegray}{white}",
        r"\begin{tabular}{@{}>{\raggedright\arraybackslash}p{0.11\textwidth}>{\raggedright\arraybackslash}p{0.12\textwidth}>{\raggedright\arraybackslash}p{0.24\textwidth}>{\raggedright\arraybackslash}p{0.24\textwidth}>{\raggedright\arraybackslash}p{0.18\textwidth}@{}}",
        r"\toprule",
        r"\rowcolor{tablehead}",
        r"Guardrail domain & Cohorts or denominator & Phase 41 analysis & Key result & Manuscript claim\\",
        r"\midrule",
    ]
    for row in summary.to_dict("records"):
        lines.append(
            f"{tex_escape(row['domain'])} & {tex_escape(row['cohorts_or_n'])} & "
            f"{tex_escape(row['phase41_analysis'])} & {tex_escape(row['key_result'])} & "
            f"{tex_escape(row['manuscript_claim'])}\\\\"
        )
    lines.extend(
        [
            r"\botrule",
            r"\end{tabular}",
            r"\rowcolors{2}{white}{white}",
            r"\footnotetext{Phase 41 analyses were added to address reviewer concerns directly. Mortality is modelled as a formal secondary non-circular endpoint. Hospitalization models use post-baseline cleaned candidate headers and are therefore feasibility/sensitivity evidence until codebook harmonization is completed. The all-sex sex-interaction screen is fit on a separately standardized all-sex LFO scale and is not used for women-only profile construction. Calibration and decision-curve results are guardrails against prediction overclaiming, not a claim of clinical utility.}",
            r"\end{table}",
            "",
        ]
    )
    return "\n".join(lines)


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        return text
    return text.replace(old, new, 1)


def update_manuscript(summary: pd.DataFrame) -> None:
    text = TEX.read_text(encoding="utf-8")
    text = replace_once(
        text,
        "Hospitalization and mortality audits identified candidate non-circular endpoints, but they were not yet harmonized as primary outcomes.",
        "Phase 41 added formal secondary mortality models, post-baseline hospitalization candidate models, all-sex LFO sex-interaction screens, and calibration/decision-curve guardrails; these analyses remained secondary or sensitivity evidence rather than primary validation.",
    )
    text = replace_once(
        text,
        "The present analysis does not test sex interactions or women-specific mechanisms.",
        "The revised analysis includes an exploratory all-sex LFO sex-interaction screen on a separately standardized all-sex scale, but it does not test women-specific mechanisms.",
    )
    text = replace_once(
        text,
        "Candidate hard endpoints, survey-design variables and male-comparator feasibility were audited but not treated as harmonized primary analyses in the current cleaned-file pass.",
        "Candidate hard endpoints, survey-design variables and male-comparator feasibility were audited. Phase 41 additionally modelled all-cause mortality as a formal secondary Cox endpoint, fit post-baseline hospitalization candidate models where cleaned binary headers existed, ran all-sex LFO sex-interaction screens, and calculated calibration plus decision-curve guardrails. Header-only endpoint and survey-design candidates were not treated as harmonized primary analyses.",
    )
    old_results = (
        "A cleaned-file header audit did not identify a harmonized survey-design triplet of analysis weight, primary sampling unit and strata across the seven cleaned files, so no survey-weighted prevalence claim is made. Mortality and hospitalization audits identified candidate non-circular endpoints, but codebook-level mapping and new endpoint models are required before using them as primary clinical outcomes."
    )
    new_results = (
        "A raw/codebook/dofile Phase 41 audit did not identify a codebook-confirmed harmonized survey-design triplet of analysis weight, primary sampling unit and strata across the seven cohorts, so no survey-weighted prevalence claim is made. Mortality was upgraded from audit-only status to formal secondary Cox modelling, but PH/time-drift guardrail flags kept it secondary. Post-baseline hospitalization candidate models were feasible in cleaned files for selected cohorts, but the variables remained header-only and were not used for primary validation. Table~\\ref{tab:phase41-guardrails} summarizes the enhanced analyses."
    )
    text = replace_once(text, old_results, new_results)
    insertion_marker = r"\begin{figure}[htbp]" + "\n" + r"\centering" + "\n" + r"\includegraphics[width=\textwidth,height=0.76\textheight,keepaspectratio]{figure4_harmonization_risk_matrix_main.pdf}"
    if r"\label{tab:phase41-guardrails}" in text:
        start = text.index(r"\begin{table}[!htbp]", max(0, text.index(r"\label{tab:phase41-guardrails}") - 500))
        end = text.index(r"\end{table}", start) + len(r"\end{table}")
        if end < len(text) and text[end : end + 1] == "\n":
            end += 1
        text = text[:start] + table4_tex(summary) + text[end:]
    elif insertion_marker in text:
        text = text.replace(insertion_marker, table4_tex(summary) + insertion_marker, 1)
    text = replace_once(
        text,
        "This limitation is especially important because hospitalization and mortality audits suggest that more clinically independent endpoints are feasible but not yet harmonized enough for a primary analysis in this package.",
        "This limitation is especially important because Phase 41 showed that clinically more independent endpoints are partly feasible: mortality can be modelled as a secondary endpoint, whereas hospitalization remains a codebook-unconfirmed candidate endpoint and care-dependence outcomes remain unavailable.",
    )
    text = replace_once(
        text,
        "A supplementary baseline male-comparator audit documents feasibility and denominator differences on a separately standardized all-sex scale; it is not part of profile construction or outcome modelling. A stronger women-health paper would require all-sex longitudinal models, formal sex interactions and harmonized women-specific exposures.",
        "A supplementary baseline male-comparator audit documents feasibility and denominator differences on a separately standardized all-sex scale. Phase 41 adds all-sex longitudinal LFO sex-interaction models as an exploratory scale check, but these are not part of women-only profile construction and do not establish women-specific mechanisms. A stronger women-health paper would still require harmonized women-specific exposures.",
    )
    text = replace_once(
        text,
        "Survey weights, strata and primary sampling units were screened by cleaned-file headers but were not available as a common seven-cohort design set, so the analyses are not survey-weighted population estimates. Functional change remained a coupled within-domain endpoint. LASI lacked a follow-up validation denominator, SHARE was validation-downgraded and KLoSA used a functional bridge. Mortality, hospitalization, institutionalization and care-dependence endpoints require codebook-level harmonization and new models before clinical validation claims.",
        "Survey weights, strata and primary sampling units were screened again using cleaned headers, Stata metadata and dofile/codebook text, but no common codebook-confirmed seven-cohort design triplet was available; the analyses are therefore not survey-weighted population estimates. Functional change remained a coupled within-domain endpoint. LASI lacked a follow-up validation denominator, SHARE was validation-downgraded and KLoSA used a functional bridge. Mortality was modelled only as secondary evidence; hospitalization models remain header-only candidate analyses; institutionalization and care-dependence endpoints remain unavailable.",
    )
    text = replace_once(
        text,
        "while continuous domain scores remain the stronger functional-change comparator in the current analyses.",
        "while continuous domain scores remain the stronger functional-change comparator in the current analyses and Phase 41 prediction guardrails do not support clinical prediction-superiority claims.",
    )
    text = replace_once(
        text,
        "AIC, Akaike information criterion; ARI, adjusted Rand index;",
        "AIC, Akaike information criterion; ARI, adjusted Rand index; DCA, decision-curve analysis;",
    )
    add_lines = (
        "Additional file 26: Phase 41 mortality formal secondary model table.\\\\\n"
        "Additional file 27: Phase 41 hospitalization candidate model outputs.\\\\\n"
        "Additional file 28: Phase 41 survey-design raw/codebook audit and triplet status.\\\\\n"
        "Additional file 29: Phase 41 all-sex LFO sex-interaction outputs.\\\\\n"
        "Additional file 30: Phase 41 calibration and decision-curve guardrails.\\\\\n"
        "Additional file 31: Phase 41 enhanced analysis summary matrix.\\\\\n"
    )
    if "Additional file 26: Phase 41 mortality formal secondary model table" not in text:
        text = text.replace(
            "Additional file 25: Sensitivity-cohort descriptive profile support.\\\\\n",
            "Additional file 25: Sensitivity-cohort descriptive profile support.\\\\\n" + add_lines,
            1,
        )
    TEX.write_text(text, encoding="utf-8")


def copy_phase41_additional_files() -> None:
    mapping = {
        "additional_file_26_phase41_mortality_secondary_formal_model_table.csv": OUT / "phase41_mortality_secondary_formal_model_table.csv",
        "additional_file_27_phase41_hospitalization_candidate_model_comparison.csv": OUT / "phase41_hospitalization_candidate_model_comparison.csv",
        "additional_file_27b_phase41_hospitalization_candidate_status.csv": OUT / "phase41_hospitalization_candidate_status.csv",
        "additional_file_28_phase41_survey_design_raw_codebook_audit.csv": OUT / "phase41_survey_design_raw_codebook_audit.csv",
        "additional_file_28b_phase41_survey_design_triplet_status.csv": OUT / "phase41_survey_design_triplet_status.csv",
        "additional_file_29_phase41_all_sex_lfo_sex_interaction_summary.csv": OUT / "phase41_all_sex_lfo_sex_interaction_summary.csv",
        "additional_file_29b_phase41_all_sex_lfo_sex_interaction_terms.csv": OUT / "phase41_all_sex_lfo_sex_interaction_terms.csv",
        "additional_file_30_phase41_calibration_metrics.csv": OUT / "phase41_calibration_metrics.csv",
        "additional_file_30b_phase41_decision_curve_summary.csv": OUT / "phase41_decision_curve_summary.csv",
        "additional_file_31_phase41_secondary_endpoint_prediction_guardrail_summary.csv": OUT / "phase41_secondary_endpoint_prediction_guardrail_summary.csv",
    }
    for dst, src in mapping.items():
        if src.exists():
            shutil.copyfile(src, PKG / dst)


def update_readme() -> None:
    path = PKG / "README_BMC_Geriatrics_burden_profiles_rescue.md"
    text = path.read_text(encoding="utf-8") if path.exists() else "# BMC Geriatrics burden profile rescue package\n"
    block = """

## Phase 41 enhanced analyses

- Added formal secondary all-cause mortality Cox summary from the covariate-adjusted mortality models.
- Added post-baseline candidate hospitalization models where cleaned binary headers existed; these remain header-only sensitivity evidence.
- Added raw/codebook/dofile survey-design audit and triplet-status table; no survey-weighted analysis was run.
- Added all-sex LFO severity-by-sex longitudinal interaction models on a separately standardized all-sex scale.
- Added calibration, Brier score and decision-curve guardrails for profile versus continuous LFO models.
"""
    if "## Phase 41 enhanced analyses" not in text:
        text = text.rstrip() + block + "\n"
    path.write_text(text, encoding="utf-8")


def rebuild_zips() -> None:
    names = [
        "bmc_geriatrics_main.tex",
        "bmc_geriatrics_refs.bib",
        "sn-jnl.cls",
        "sn-vancouver-num.bst",
        "README_BMC_Geriatrics_burden_profiles_rescue.md",
    ]
    names.extend([p.name for p in sorted(PKG.glob("figure*.pdf"))])
    names.extend([p.name for p in sorted(PKG.glob("figure*.png"))])
    names.extend([p.name for p in sorted(PKG.glob("figure*.svg"))])
    names.extend([p.name for p in sorted(PKG.glob("supplementary_figure*.pdf"))])
    names.extend([p.name for p in sorted(PKG.glob("additional_file_*.csv"))])
    names = sorted(set(names))
    for zip_name in [
        "bmc_geriatrics_submission_claude_revised_source_only.zip",
        "bmc_geriatrics_submission_burden_profiles_rescue_source_only.zip",
    ]:
        with zipfile.ZipFile(PKG / zip_name, "w", compression=zipfile.ZIP_DEFLATED) as z:
            for name in names:
                path = PKG / name
                if path.exists():
                    z.write(path, arcname=name)
    pdf_names = [*names]
    if (PKG / "bmc_geriatrics_main.pdf").exists():
        pdf_names.append("bmc_geriatrics_main.pdf")
    for zip_name in [
        "bmc_geriatrics_submission_claude_revised_pdf_ready.zip",
        "bmc_geriatrics_submission_burden_profiles_rescue_pdf_ready.zip",
    ]:
        with zipfile.ZipFile(PKG / zip_name, "w", compression=zipfile.ZIP_DEFLATED) as z:
            for name in sorted(set(pdf_names)):
                path = PKG / name
                if path.exists():
                    z.write(path, arcname=name)


def write_report(summary: pd.DataFrame) -> None:
    lines = [
        "# Phase 41 Enhanced Analyses",
        "",
        "This phase directly addresses the unresolved reviewer issues without upgrading unsupported evidence into primary claims.",
        "",
        "| Domain | Cohorts or denominator | Phase 41 analysis | Key result | Manuscript claim |",
        "|---|---|---|---|---|",
    ]
    for row in summary.to_dict("records"):
        lines.append(
            f"| {row['domain']} | {row['cohorts_or_n']} | {row['phase41_analysis']} | {row['key_result']} | {row['manuscript_claim']} |"
        )
    lines.extend(
        [
            "",
            "Interpretation rule: mortality can be reported as a secondary non-circular endpoint; hospitalization remains header-only candidate evidence; survey-weighted models are not run without a confirmed weight/PSU/strata triplet; all-sex interaction models are exploratory scale checks.",
        ]
    )
    (OUT / "phase41_enhanced_analysis_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", required=True, type=Path)
    parser.add_argument("--database-root", required=True, type=Path)
    parser.add_argument("--update-manuscript", action="store_true")
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    mortality = build_mortality_secondary_table()
    hosp_screen = build_hospitalization_candidate_screen(args.data_root)
    _, _, hosp_comp = run_hospitalization_candidate_models(hosp_screen)
    _, survey_status = build_survey_raw_codebook_audit(args.database_root)
    all_sex_screen = build_all_sex_lfo_screen(args.data_root, args.database_root)
    sex_summary, _ = run_all_sex_sex_interaction(all_sex_screen)
    calib, _, dca_summary = run_calibration_and_decision_curve()
    summary = build_phase41_guardrail_summary(
        mortality=mortality,
        hosp_comp=hosp_comp,
        survey_status=survey_status,
        sex_summary=sex_summary,
        calib=calib,
        dca_summary=dca_summary,
    )
    write_report(summary)
    if args.update_manuscript:
        update_manuscript(summary)
        copy_phase41_additional_files()
        update_readme()
        rebuild_zips()
    print(OUT / "phase41_secondary_endpoint_prediction_guardrail_summary.csv")
    print(OUT / "phase41_enhanced_analysis_report.md")
    if args.update_manuscript:
        print(TEX)


if __name__ == "__main__":
    main()
