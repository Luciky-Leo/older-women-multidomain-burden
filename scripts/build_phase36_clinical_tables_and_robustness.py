from __future__ import annotations

import math
import re
import shutil
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import statsmodels.api as sm
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.metrics import adjusted_mutual_info_score, adjusted_rand_score, roc_auc_score, silhouette_score
from sklearn.mixture import GaussianMixture


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
PKG = ROOT / "manuscript" / "bmc_geriatrics_submission_burden_profiles_rescue"
TEX = PKG / "bmc_geriatrics_main.tex"

COHORT_ORDER = ["CHARLS", "ELSA", "HRS", "KLoSA", "LASI", "MHAS", "SHARE"]
STRICT_VALIDATION_ORDER = ["CHARLS", "ELSA", "HRS", "MHAS", "SHARE", "KLoSA"]
DOMAIN_COLS = [
    "functional_score",
    "cognitive_score",
    "affective_score",
    "cardiometabolic_chronic_score",
]


def read_csv(name: str, **kwargs) -> pd.DataFrame:
    return pd.read_csv(OUT / name, low_memory=False, **kwargs)


def keyify(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in ["participant_id", "wave"]:
        if col in out.columns:
            out[col] = out[col].astype(str)
    return out


def fmt_int(x: object) -> str:
    if pd.isna(x):
        return "NA"
    return f"{int(round(float(x))):,}"


def fmt_num(x: object, digits: int = 1) -> str:
    if pd.isna(x) or x == "":
        return "NA"
    return f"{float(x):.{digits}f}"


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


def coerce_numeric(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = df.copy()
    for col in cols:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def safe_pct(num: float, den: float) -> float:
    if not den or pd.isna(den):
        return np.nan
    return float(num) / float(den) * 100.0


def build_baseline_characteristics() -> pd.DataFrame:
    assignments = keyify(read_csv("phase4_best_model_assignments.csv", dtype={"participant_id": str, "wave": str}))
    scores = keyify(read_csv("phase3_domain_scores.csv", dtype={"participant_id": str, "wave": str}))
    covars = keyify(read_csv("phase13_covariate_participant_screen.csv", dtype={"participant_id": str, "wave": str}))

    scores_keep = scores[
        [
            "cohort",
            "participant_id",
            "wave",
            "cardiometabolic_chronic_count",
            "cardiometabolic_chronic_prop",
            "complete_four_domain",
        ]
    ].copy()
    cov_keep = covars[
        [
            "cohort",
            "participant_id",
            "wave",
            "cov_bmi_raw",
            "cov_smoking_raw",
            "cov_drinking_raw",
            "cov_marital_status_raw",
            "cov_rural_region_raw",
        ]
    ].copy()
    df = assignments.merge(scores_keep, on=["cohort", "participant_id", "wave"], how="left")
    df = df.merge(cov_keep, on=["cohort", "participant_id", "wave"], how="left")
    df = coerce_numeric(
        df,
        [
            "age",
            "cov_bmi_raw",
            "cov_smoking_raw",
            "cov_drinking_raw",
            "cov_marital_status_raw",
            "cov_rural_region_raw",
            "cardiometabolic_chronic_count",
            *DOMAIN_COLS,
        ],
    )

    rows: list[dict[str, object]] = []
    for cohort in COHORT_ORDER:
        g = df[df["cohort"].eq(cohort)].copy()
        if g.empty:
            continue
        chronic = g["cardiometabolic_chronic_count"]
        plausible_bmi = g["cov_bmi_raw"].where(g["cov_bmi_raw"].between(10, 80))
        row = {
            "cohort": cohort,
            "analytic_profile_n": len(g),
            "age_mean": g["age"].mean(),
            "age_sd": g["age"].std(ddof=1),
            "bmi_n": plausible_bmi.notna().sum(),
            "bmi_pct_nonmissing": safe_pct(plausible_bmi.notna().sum(), len(g)),
            "bmi_implausible_excluded_n": int(g["cov_bmi_raw"].notna().sum() - plausible_bmi.notna().sum()),
            "bmi_mean": plausible_bmi.mean(),
            "bmi_sd": plausible_bmi.std(ddof=1),
            "chronic_count_mean": chronic.mean(),
            "chronic_count_sd": chronic.std(ddof=1),
            "chronic_ge2_pct": safe_pct((chronic >= 2).sum(), chronic.notna().sum()),
            "functional_z_mean": g["functional_score"].mean(),
            "functional_z_sd": g["functional_score"].std(ddof=1),
            "cognitive_z_mean": g["cognitive_score"].mean(),
            "cognitive_z_sd": g["cognitive_score"].std(ddof=1),
            "affective_z_mean": g["affective_score"].mean(),
            "affective_z_sd": g["affective_score"].std(ddof=1),
            "cardiometabolic_chronic_z_mean": g["cardiometabolic_chronic_score"].mean(),
            "cardiometabolic_chronic_z_sd": g["cardiometabolic_chronic_score"].std(ddof=1),
            "smoking_raw_positive_pct": safe_pct((g["cov_smoking_raw"] > 0).sum(), g["cov_smoking_raw"].notna().sum()),
            "drinking_raw_positive_pct": safe_pct((g["cov_drinking_raw"] > 0).sum(), g["cov_drinking_raw"].notna().sum()),
            "marital_raw_one_pct": safe_pct((g["cov_marital_status_raw"] == 1).sum(), g["cov_marital_status_raw"].notna().sum()),
            "rural_raw_one_pct": safe_pct((g["cov_rural_region_raw"] == 1).sum(), g["cov_rural_region_raw"].notna().sum()),
        }
        row["domain_z_signature"] = (
            f"{row['functional_z_mean']:.2f}/"
            f"{row['cognitive_z_mean']:.2f}/"
            f"{row['affective_z_mean']:.2f}/"
            f"{row['cardiometabolic_chronic_z_mean']:.2f}"
        )
        rows.append(row)

    out = pd.DataFrame(rows)
    out.to_csv(OUT / "phase36_baseline_clinical_characteristics.csv", index=False)
    return out


def build_missingness_table() -> pd.DataFrame:
    scores = read_csv("phase3_domain_scores.csv", dtype={"participant_id": str, "wave": str})
    tier = read_csv("phase32_cohort_tier_lock.csv")
    val_lookup = tier.set_index("cohort")
    rows = []
    for cohort in COHORT_ORDER:
        g = scores[scores["cohort"].eq(cohort)].copy()
        if g.empty:
            continue
        complete = g["complete_four_domain"].fillna(0).astype(int).eq(1)
        excluded = ~complete
        row = {
            "cohort": cohort,
            "source_women50_n": len(g),
            "complete_four_domain_n": int(complete.sum()),
            "excluded_incomplete_domain_n": int(excluded.sum()),
            "complete_four_domain_pct": safe_pct(complete.sum(), len(g)),
            "age_mean_complete": g.loc[complete, "age"].mean(),
            "age_mean_excluded": g.loc[excluded, "age"].mean(),
            "age_difference_excluded_minus_complete": g.loc[excluded, "age"].mean() - g.loc[complete, "age"].mean(),
            "functional_missing_pct": safe_pct(g["functional_score"].isna().sum(), len(g)),
            "cognitive_missing_pct": safe_pct(g["cognitive_score"].isna().sum(), len(g)),
            "affective_missing_pct": safe_pct(g["affective_score"].isna().sum(), len(g)),
            "cardiometabolic_chronic_missing_pct": safe_pct(g["cardiometabolic_chronic_score"].isna().sum(), len(g)),
            "validation_available_n": val_lookup.loc[cohort, "functional_deterioration_ge_0_5sd_available_n"]
            if cohort in val_lookup.index
            else np.nan,
            "validation_event_n": val_lookup.loc[cohort, "functional_deterioration_ge_0_5sd_event_n"]
            if cohort in val_lookup.index
            else np.nan,
        }
        rows.append(row)
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "phase36_missingness_included_excluded.csv", index=False)
    return out


def model_frame_for_lfo() -> pd.DataFrame:
    lfo = keyify(read_csv("phase32_decoupled_lfo_participant_screen.csv", dtype={"participant_id": str, "wave": str}))
    cov = keyify(read_csv("phase13_covariate_participant_screen.csv", dtype={"participant_id": str, "wave": str}))
    cov_keep = cov[
        [
            "cohort",
            "participant_id",
            "wave",
            "cov_education_raw",
            "cov_marital_status_raw",
            "cov_smoking_raw",
            "cov_drinking_raw",
        ]
    ].copy()
    df = lfo.merge(cov_keep, on=["cohort", "participant_id", "wave"], how="left")
    df = coerce_numeric(
        df,
        [
            "age",
            "functional_deterioration_ge_0_5sd",
            "functional_deterioration_available",
            "lfo_assignment_available",
            "lfo_profile_class",
            "cognitive_score",
            "affective_score",
            "cardiometabolic_chronic_score",
            "cov_education_raw",
            "cov_marital_status_raw",
            "cov_smoking_raw",
            "cov_drinking_raw",
        ],
    )
    df = df[
        df["functional_deterioration_available"].eq(1)
        & df["lfo_assignment_available"].eq(1)
        & df["cohort"].isin(STRICT_VALIDATION_ORDER)
    ].copy()
    df["lfo_profile_class"] = df["lfo_profile_class"].astype("Int64")
    return df


def parse_class_from_term(term: str) -> int | None:
    match = re.search(r"\[T\.?([0-9]+)\]", str(term))
    if match:
        return int(match.group(1))
    return None


def fit_glm(formula: str, df: pd.DataFrame):
    return smf.glm(formula, data=df, family=sm.families.Binomial()).fit()


def build_functional_association_tables() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df = model_frame_for_lfo()
    cov_cols = ["age", "cov_education_raw", "cov_marital_status_raw", "cov_smoking_raw", "cov_drinking_raw"]
    class_rows = []
    model_rows = []
    main_rows = []
    tier = read_csv("phase32_cohort_tier_lock.csv").set_index("cohort")

    for cohort in STRICT_VALIDATION_ORDER:
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
        if model_df.empty or model_df["functional_deterioration_ge_0_5sd"].nunique() < 2:
            continue

        model_df["lfo_profile_class"] = model_df["lfo_profile_class"].astype(int)
        profile_formula = (
            "functional_deterioration_ge_0_5sd ~ age + cov_education_raw + cov_marital_status_raw "
            "+ cov_smoking_raw + cov_drinking_raw + C(lfo_profile_class, Treatment(reference=1))"
        )
        cont_formula = (
            "functional_deterioration_ge_0_5sd ~ age + cov_education_raw + cov_marital_status_raw "
            "+ cov_smoking_raw + cov_drinking_raw + cognitive_score + affective_score + cardiometabolic_chronic_score"
        )
        profile_res = fit_glm(profile_formula, model_df)
        cont_res = fit_glm(cont_formula, model_df)
        y = model_df["functional_deterioration_ge_0_5sd"].astype(int)
        profile_pred = profile_res.predict(model_df)
        cont_pred = cont_res.predict(model_df)
        profile_auc = roc_auc_score(y, profile_pred)
        cont_auc = roc_auc_score(y, cont_pred)

        # Per-class crude absolute risk.
        class_stats = (
            model_df.groupby("lfo_profile_class", dropna=False)
            .agg(
                n=("functional_deterioration_ge_0_5sd", "size"),
                events=("functional_deterioration_ge_0_5sd", "sum"),
                age_mean=("age", "mean"),
                cognitive_z_mean=("cognitive_score", "mean"),
                affective_z_mean=("affective_score", "mean"),
                cardiometabolic_chronic_z_mean=("cardiometabolic_chronic_score", "mean"),
            )
            .reset_index()
        )
        class_stats["event_pct"] = class_stats["events"] / class_stats["n"] * 100.0

        or_lookup: dict[int, dict[str, float]] = {1: {"or": 1.0, "ci_low": 1.0, "ci_high": 1.0, "p_value": np.nan}}
        conf = profile_res.conf_int()
        for term, coef in profile_res.params.items():
            cls = parse_class_from_term(term)
            if cls is None:
                continue
            low, high = conf.loc[term]
            or_lookup[cls] = {
                "or": float(np.exp(coef)),
                "ci_low": float(np.exp(low)),
                "ci_high": float(np.exp(high)),
                "p_value": float(profile_res.pvalues[term]),
            }

        for _, r in class_stats.iterrows():
            cls = int(r["lfo_profile_class"])
            est = or_lookup.get(cls, {"or": np.nan, "ci_low": np.nan, "ci_high": np.nan, "p_value": np.nan})
            class_rows.append(
                {
                    "cohort": cohort,
                    "analysis_tier": tier.loc[cohort, "analysis_tier"] if cohort in tier.index else "",
                    "lfo_profile_class": cls,
                    "n": int(r["n"]),
                    "events": int(r["events"]),
                    "event_pct": float(r["event_pct"]),
                    "age_mean": float(r["age_mean"]),
                    "cognitive_z_mean": float(r["cognitive_z_mean"]),
                    "affective_z_mean": float(r["affective_z_mean"]),
                    "cardiometabolic_chronic_z_mean": float(r["cardiometabolic_chronic_z_mean"]),
                    "adjusted_or_vs_class1": est["or"],
                    "ci_low": est["ci_low"],
                    "ci_high": est["ci_high"],
                    "p_value": est["p_value"],
                }
            )

        ref = class_stats[class_stats["lfo_profile_class"].eq(1)]
        ref_risk = float(ref["event_pct"].iloc[0]) if not ref.empty else np.nan
        highest = class_stats.sort_values(["event_pct", "n"], ascending=[False, False]).iloc[0]
        highest_cls = int(highest["lfo_profile_class"])
        highest_est = or_lookup.get(highest_cls, {"or": np.nan, "ci_low": np.nan, "ci_high": np.nan, "p_value": np.nan})
        valn = int(model_df.shape[0])
        events = int(y.sum())
        model_rows.extend(
            [
                {
                    "cohort": cohort,
                    "model": "lfo_profile_minimal_core",
                    "n": valn,
                    "events": events,
                    "aic": float(profile_res.aic),
                    "auc": float(profile_auc),
                    "formula": profile_formula,
                },
                {
                    "cohort": cohort,
                    "model": "continuous_three_domain_minimal_core",
                    "n": valn,
                    "events": events,
                    "aic": float(cont_res.aic),
                    "auc": float(cont_auc),
                    "formula": cont_formula,
                },
            ]
        )
        claim = "bridge sensitivity" if cohort == "KLoSA" else "validation downgraded" if cohort == "SHARE" else "within-cohort association"
        main_rows.append(
            {
                "cohort": cohort,
                "tier": "Bridge" if cohort == "KLoSA" else "Strict",
                "validation_n": valn,
                "events": events,
                "event_pct": events / valn * 100.0,
                "reference_class": 1,
                "reference_event_pct": ref_risk,
                "highest_risk_class": highest_cls,
                "highest_risk_event_pct": float(highest["event_pct"]),
                "absolute_risk_difference_pct": float(highest["event_pct"]) - ref_risk,
                "adjusted_or_highest_vs_class1": highest_est["or"],
                "ci_low": highest_est["ci_low"],
                "ci_high": highest_est["ci_high"],
                "p_value": highest_est["p_value"],
                "profile_auc": float(profile_auc),
                "continuous_three_domain_auc": float(cont_auc),
                "delta_auc_profile_minus_continuous": float(profile_auc - cont_auc),
                "delta_aic_continuous_minus_profile_per_1000": float((cont_res.aic - profile_res.aic) / valn * 1000.0),
                "claim_status": claim,
            }
        )

    class_out = pd.DataFrame(class_rows)
    model_out = pd.DataFrame(model_rows)
    main_out = pd.DataFrame(main_rows)
    class_out.to_csv(OUT / "phase36_functional_association_class_risks.csv", index=False)
    model_out.to_csv(OUT / "phase36_functional_association_model_metrics.csv", index=False)
    main_out.to_csv(OUT / "phase36_functional_association_main.csv", index=False)
    return main_out, class_out, model_out


def sample_indices(n: int, max_n: int, rng: np.random.Generator) -> np.ndarray:
    if n <= max_n:
        return np.arange(n)
    return np.sort(rng.choice(n, size=max_n, replace=False))


def covariance_flags(model: GaussianMixture) -> tuple[float, float, int]:
    mins = []
    conds = []
    cov = model.covariances_
    if model.covariance_type == "full":
        iterable = cov
        for c in iterable:
            eig = np.linalg.eigvalsh(c)
            mins.append(float(np.min(eig)))
            conds.append(float(np.max(eig) / max(np.min(eig), 1e-12)))
    elif model.covariance_type == "tied":
        eig = np.linalg.eigvalsh(cov)
        mins.append(float(np.min(eig)))
        conds.append(float(np.max(eig) / max(np.min(eig), 1e-12)))
    elif model.covariance_type == "diag":
        mins.extend(np.min(cov, axis=1).astype(float).tolist())
        conds.extend((np.max(cov, axis=1) / np.maximum(np.min(cov, axis=1), 1e-12)).astype(float).tolist())
    else:
        mins.extend(np.asarray(cov).astype(float).ravel().tolist())
        conds.extend([1.0] * len(mins))
    min_var = float(np.min(mins)) if mins else np.nan
    max_cond = float(np.max(conds)) if conds else np.nan
    flagged = int((not pd.isna(min_var) and min_var < 1e-4) or (not pd.isna(max_cond) and max_cond > 1e6))
    return min_var, max_cond, flagged


def class_metrics(labels: np.ndarray) -> tuple[int, float, float]:
    counts = pd.Series(labels).value_counts()
    n = len(labels)
    return int(counts.size), float(counts.min() / n * 100.0), float(counts.max() / n * 100.0)


def safe_silhouette(x: np.ndarray, labels: np.ndarray, rng: np.random.Generator) -> float:
    if len(np.unique(labels)) < 2 or len(labels) < 10:
        return np.nan
    idx = sample_indices(len(labels), 5000, rng)
    if len(np.unique(labels[idx])) < 2:
        return np.nan
    return float(silhouette_score(x[idx], labels[idx]))


def build_algorithm_robustness() -> tuple[pd.DataFrame, pd.DataFrame]:
    assignments = keyify(read_csv("phase4_best_model_assignments.csv", dtype={"participant_id": str, "wave": str}))
    rng = np.random.default_rng(20260602)
    rows = []
    summary_rows = []

    for cohort in COHORT_ORDER:
        g = assignments[assignments["cohort"].eq(cohort)].copy()
        g = g.dropna(subset=DOMAIN_COLS + ["endotype_class"])
        if g.empty:
            continue
        x = g[DOMAIN_COLS].astype(float).to_numpy()
        selected = g["endotype_class"].astype(int).to_numpy()
        k = int(g["n_classes"].iloc[0])

        method_results: list[dict[str, object]] = []
        for cov_type in ["full", "diag", "tied"]:
            model = GaussianMixture(
                n_components=k,
                covariance_type=cov_type,
                random_state=20260602,
                n_init=10,
                reg_covar=1e-6,
                max_iter=500,
            )
            labels = model.fit_predict(x)
            n_classes, min_pct, max_pct = class_metrics(labels)
            min_var, max_cond, cov_flag = covariance_flags(model)
            method_results.append(
                {
                    "cohort": cohort,
                    "method": f"gmm_{cov_type}",
                    "n": len(g),
                    "sample_n": len(g),
                    "target_classes": k,
                    "observed_classes": n_classes,
                    "min_class_pct": min_pct,
                    "max_class_pct": max_pct,
                    "bic": float(model.bic(x)),
                    "aic": float(model.aic(x)),
                    "silhouette": safe_silhouette(x, labels, rng),
                    "ari_vs_selected_gmm": float(adjusted_rand_score(selected, labels)),
                    "ami_vs_selected_gmm": float(adjusted_mutual_info_score(selected, labels)),
                    "covariance_min_eigen_or_variance": min_var,
                    "covariance_max_condition": max_cond,
                    "near_singular_flag": cov_flag,
                    "converged": int(model.converged_),
                    "note": "full sample",
                }
            )

        km = KMeans(n_clusters=k, random_state=20260602, n_init=50)
        km_labels = km.fit_predict(x)
        n_classes, min_pct, max_pct = class_metrics(km_labels)
        method_results.append(
            {
                "cohort": cohort,
                "method": "kmeans",
                "n": len(g),
                "sample_n": len(g),
                "target_classes": k,
                "observed_classes": n_classes,
                "min_class_pct": min_pct,
                "max_class_pct": max_pct,
                "bic": np.nan,
                "aic": np.nan,
                "silhouette": safe_silhouette(x, km_labels, rng),
                "ari_vs_selected_gmm": float(adjusted_rand_score(selected, km_labels)),
                "ami_vs_selected_gmm": float(adjusted_mutual_info_score(selected, km_labels)),
                "covariance_min_eigen_or_variance": np.nan,
                "covariance_max_condition": np.nan,
                "near_singular_flag": np.nan,
                "converged": 1,
                "note": "full sample",
            }
        )

        idx = sample_indices(len(g), 5000, rng)
        h = AgglomerativeClustering(n_clusters=k, linkage="ward")
        h_labels = h.fit_predict(x[idx])
        n_classes, min_pct, max_pct = class_metrics(h_labels)
        method_results.append(
            {
                "cohort": cohort,
                "method": "hierarchical_ward_sample",
                "n": len(g),
                "sample_n": len(idx),
                "target_classes": k,
                "observed_classes": n_classes,
                "min_class_pct": min_pct,
                "max_class_pct": max_pct,
                "bic": np.nan,
                "aic": np.nan,
                "silhouette": safe_silhouette(x[idx], h_labels, rng),
                "ari_vs_selected_gmm": float(adjusted_rand_score(selected[idx], h_labels)),
                "ami_vs_selected_gmm": float(adjusted_mutual_info_score(selected[idx], h_labels)),
                "covariance_min_eigen_or_variance": np.nan,
                "covariance_max_condition": np.nan,
                "near_singular_flag": np.nan,
                "converged": 1,
                "note": "sampled to max 5,000 participants for scalability",
            }
        )

        severity = g[DOMAIN_COLS].mean(axis=1)
        try:
            sev_labels = pd.qcut(severity, q=3, labels=False, duplicates="drop").to_numpy()
        except ValueError:
            sev_labels = pd.Series(pd.cut(severity, bins=3, labels=False)).fillna(0).astype(int).to_numpy()
        n_classes, min_pct, max_pct = class_metrics(sev_labels)
        method_results.append(
            {
                "cohort": cohort,
                "method": "continuous_severity_tertile",
                "n": len(g),
                "sample_n": len(g),
                "target_classes": 3,
                "observed_classes": n_classes,
                "min_class_pct": min_pct,
                "max_class_pct": max_pct,
                "bic": np.nan,
                "aic": np.nan,
                "silhouette": safe_silhouette(x, sev_labels, rng),
                "ari_vs_selected_gmm": float(adjusted_rand_score(selected, sev_labels)),
                "ami_vs_selected_gmm": float(adjusted_mutual_info_score(selected, sev_labels)),
                "covariance_min_eigen_or_variance": np.nan,
                "covariance_max_condition": np.nan,
                "near_singular_flag": np.nan,
                "converged": 1,
                "note": "continuous-domain comparator discretized into tertiles for ARI only",
            }
        )

        rows.extend(method_results)
        res = pd.DataFrame(method_results).set_index("method")
        non_full_ari = res.drop(index="gmm_full")["ari_vs_selected_gmm"].astype(float)
        non_gmm_methods = ["kmeans", "hierarchical_ward_sample", "continuous_severity_tertile"]
        best_non_full_method = non_full_ari.idxmax()
        best_non_full_ari = non_full_ari.max()
        best_non_gmm_ari = res.loc[non_gmm_methods, "ari_vs_selected_gmm"].astype(float).max()
        diag_ari = float(res.loc["gmm_diag", "ari_vs_selected_gmm"])
        if diag_ari >= 0.75 and best_non_gmm_ari >= 0.75:
            interpretation = "broadly_robust"
        elif diag_ari >= 0.75:
            interpretation = "diagonal_gmm_consistent_but_non_gmm_limited"
        else:
            interpretation = "limited"
        summary_rows.append(
            {
                "cohort": cohort,
                "n": len(g),
                "selected_classes": k,
                "diag_gmm_ari": diag_ari,
                "tied_gmm_ari": res.loc["gmm_tied", "ari_vs_selected_gmm"],
                "kmeans_ari": res.loc["kmeans", "ari_vs_selected_gmm"],
                "hierarchical_sample_ari": res.loc["hierarchical_ward_sample", "ari_vs_selected_gmm"],
                "severity_tertile_ari": res.loc["continuous_severity_tertile", "ari_vs_selected_gmm"],
                "best_non_full_method": best_non_full_method,
                "best_non_full_ari": best_non_full_ari,
                "best_non_gmm_ari": best_non_gmm_ari,
                "full_gmm_near_singular_flag": res.loc["gmm_full", "near_singular_flag"],
                "robustness_interpretation": interpretation,
            }
        )

    out = pd.DataFrame(rows)
    summary = pd.DataFrame(summary_rows)
    out.to_csv(OUT / "phase36_gmm_algorithm_robustness.csv", index=False)
    summary.to_csv(OUT / "phase36_gmm_algorithm_robustness_summary.csv", index=False)
    return out, summary


def selected_class_counts() -> pd.DataFrame:
    selected = read_csv("phase28_gmm_selection_table.csv")
    return selected.loc[selected["selected_model"].eq(1), ["cohort", "n_classes"]]


def clean_tier(tier: str, role: str) -> str:
    if role == "baseline_profile_only":
        return "Baseline only"
    if tier == "bridge_sensitivity":
        return "Bridge sensitivity"
    return "Strict construction"


def ensure_table_style_preamble() -> None:
    text = TEX.read_text(encoding="utf-8")
    if r"\usepackage[table]{xcolor}" not in text:
        text = text.replace(
            r"\usepackage{array}",
            r"\usepackage{array}" + "\n" + r"\usepackage[table]{xcolor}",
        )
    if r"\usepackage{placeins}" not in text:
        text = text.replace(
            r"\usepackage[table]{xcolor}",
            r"\usepackage[table]{xcolor}" + "\n" + r"\usepackage{placeins}",
        )
    if r"\definecolor{tablehead}" not in text:
        text = text.replace(
            r"\usepackage{placeins}",
            r"\usepackage{placeins}"
            + "\n\n"
            + r"\definecolor{tablehead}{HTML}{E9ECEF}"
            + "\n"
            + r"\definecolor{tablegray}{HTML}{F5F6F7}",
        )
    elif r"\definecolor{tablegray}" not in text:
        text = text.replace(
            r"\definecolor{tablehead}{HTML}{E9ECEF}",
            r"\definecolor{tablehead}{HTML}{E9ECEF}"
            + "\n"
            + r"\definecolor{tablegray}{HTML}{F5F6F7}",
        )
    TEX.write_text(text, encoding="utf-8")


def table1_tex() -> str:
    cohort = read_csv("phase32_cohort_tier_lock.csv").merge(selected_class_counts(), on="cohort", how="left")
    cohort = cohort.set_index("cohort").loc[COHORT_ORDER].reset_index()
    lines = [
        r"\begin{table}[!htbp]",
        r"\caption{Cohort roles, denominator locks and validation availability}\label{tab:tier-lock}",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{2pt}",
        r"\rowcolors{2}{tablegray}{white}",
        r"\begin{tabular}{@{}>{\raggedright\arraybackslash}p{0.11\textwidth}>{\raggedright\arraybackslash}p{0.14\textwidth}>{\raggedright\arraybackslash}p{0.22\textwidth}>{\raggedright\arraybackslash}p{0.18\textwidth}>{\raggedright\arraybackslash}p{0.31\textwidth}@{}}",
        r"\toprule",
        r"\rowcolor{tablehead}",
        r"Cohort & Role/tier & Construction denominator & Validation denominator/events & Claim status\\",
        r"\midrule",
    ]
    for _, r in cohort.iterrows():
        source = r["baseline_women_age50plus_n"]
        complete = r["complete_four_domain_n"]
        profile = r["selected_endotype_n"]
        val = r["functional_deterioration_ge_0_5sd_available_n"]
        events = r["functional_deterioration_ge_0_5sd_event_n"]
        role = "baseline_profile_only" if r["cohort"] == "LASI" else r["analysis_tier"]
        if val == 0:
            validation = "NA; no follow-up validation"
        else:
            validation = f"{fmt_int(val)}; events {fmt_int(events)} ({float(events) / float(val) * 100:.1f}%)"
        if r["cohort"] == "LASI":
            claim = "Baseline profile construction only; excluded from validation denominator."
        elif r["cohort"] == "KLoSA":
            claim = "Bridge-sensitivity construction only; not pooled as strict primary evidence."
        elif r["cohort"] == "SHARE":
            claim = "Descriptive construction allowed; functional validation downgraded."
        else:
            claim = "Descriptive construction and within-cohort gradients only; no prediction-superiority claim."
        lines.append(
            " & ".join(
                [
                    tex_escape(r["cohort"]),
                    tex_escape(clean_tier(str(r["analysis_tier"]), role)),
                    tex_escape(
                        f"source {fmt_int(source)}; complete {fmt_int(complete)} "
                        f"({float(complete) / float(source) * 100:.1f}%); "
                        f"profile {fmt_int(profile)}, {int(r['n_classes'])} classes"
                    ),
                    tex_escape(validation),
                    tex_escape(claim),
                ]
            )
            + r"\\"
        )
    lines += [
        r"\botrule",
        r"\end{tabular}",
        r"\rowcolors{2}{white}{white}",
        r"\footnotetext{Source-screen, complete-domain, profile-construction and validation denominators are intentionally separated. LASI had no follow-up validation denominator in the current cleaned-data pass and is not counted as zero events.}",
        r"\end{table}",
    ]
    return "\n".join(lines)


def table2_baseline_tex(baseline: pd.DataFrame) -> str:
    lines = [
        r"\begin{table}[!htbp]",
        r"\caption{Baseline clinical characteristics of the profile-construction sample}\label{tab:baseline-clinical}",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{3pt}",
        r"\rowcolors{2}{tablegray}{white}",
        r"\begin{tabular}{@{}>{\raggedright\arraybackslash}p{0.10\textwidth}r>{\raggedright\arraybackslash}p{0.12\textwidth}>{\raggedright\arraybackslash}p{0.15\textwidth}>{\raggedright\arraybackslash}p{0.13\textwidth}>{\raggedright\arraybackslash}p{0.11\textwidth}>{\raggedright\arraybackslash}p{0.18\textwidth}@{}}",
        r"\toprule",
        r"\rowcolor{tablehead}",
        r"Cohort & N & Age & BMI & Chronic count & $\geq$2 chronic & Domain z F/Cog/Aff/CM\\",
        r"\midrule",
    ]
    for _, r in baseline.set_index("cohort").loc[COHORT_ORDER].reset_index().iterrows():
        bmi = "NA" if pd.isna(r["bmi_mean"]) else f"{fmt_mean_sd(r['bmi_mean'], r['bmi_sd'])}; {r['bmi_pct_nonmissing']:.0f}% observed"
        lines.append(
            " & ".join(
                [
                    tex_escape(r["cohort"]),
                    fmt_int(r["analytic_profile_n"]),
                    tex_escape(fmt_mean_sd(r["age_mean"], r["age_sd"])),
                    tex_escape(bmi),
                    tex_escape(fmt_mean_sd(r["chronic_count_mean"], r["chronic_count_sd"])),
                    tex_escape(f"{r['chronic_ge2_pct']:.1f}%"),
                    tex_escape(r["domain_z_signature"]),
                ]
            )
            + r"\\"
        )
    lines += [
        r"\botrule",
        r"\end{tabular}",
        r"\rowcolors{2}{white}{white}",
        r"\footnotetext{BMI and covariate fields are baseline harmonized candidates from the cleaned files; BMI missingness is shown in-cell, and BMI values outside 10--80 kg/m$^2$ were excluded from BMI summaries as implausible. Domain z columns are cohort-standardized burden scores, ordered as functional/cognitive/affective/cardiometabolic-chronic, with higher values indicating worse burden. Full raw candidate covariate summaries are provided in Additional file 11.}",
        r"\end{table}",
    ]
    return "\n".join(lines)


def family_label(label: str) -> str:
    mapping = {
        "Intermediate burden, cardiometabolic/chronic spared": "Intermediate, CM spared",
        "Intermediate burden, severity aligned": "Intermediate, severity aligned",
        "Intermediate burden, cardiometabolic/chronic high with function spared": "Intermediate, CM high/function spared",
        "Intermediate burden, cardiometabolic/chronic high": "Intermediate, CM high",
        "High burden, functional dominant with cardiometabolic/chronic spared": "High burden, functional dominant/CM spared",
        "High burden, functional dominant with cognition relatively spared": "High burden, functional dominant/cognition spared",
        "Cohort-specific high-burden variants": "Cohort-specific high-burden variants",
    }
    return mapping.get(label, label)


def family_reading(label: str) -> str:
    if "functional dominant" in label:
        return "Functional limitation is the main signal."
    if "severity aligned" in label:
        return "Domains move together as a severity gradient."
    if "cardiometabolic/chronic high" in label:
        return "Chronic disease burden dominates while function is relatively preserved."
    if "cardiometabolic/chronic spared" in label:
        return "CM/chronic burden is relatively low despite intermediate burden."
    return "Heterogeneous cohort-specific pattern; inspect full dictionary."


def evidence_tier(cohorts: str) -> str:
    items = {c.strip() for c in str(cohorts).split(",")}
    flags = []
    if "KLoSA" in items:
        flags.append("bridge-supported")
    if "LASI" in items:
        flags.append("baseline-only included")
    if "SHARE" in items:
        flags.append("SHARE validation-downgraded")
    return "; ".join(flags) if flags else "strict recurrent"


def table3_profile_tex() -> str:
    fam = read_csv("phase33_profile_family_summary.csv")
    recurrent = fam[fam["main_table_group"].eq("recurrent family")]
    specific = fam[fam["main_table_group"].eq("cohort-specific family")]
    if not specific.empty:
        row = {
            "clinical_family": "Cohort-specific high-burden variants",
            "main_table_group": "cohort-specific variants",
            "selected_classes": int(specific["selected_classes"].sum()),
            "represented_cohorts": ", ".join(sorted(set(", ".join(specific["represented_cohorts"]).split(", ")))),
            "participants": int(specific["participants"].sum()),
            "participant_pct_of_selected_profiles": specific["participants"].sum() / fam["participants"].sum() * 100,
            "mean_functional_z": specific["mean_functional_z"].mean(),
            "mean_cognitive_z": specific["mean_cognitive_z"].mean(),
            "mean_affective_z": specific["mean_affective_z"].mean(),
            "mean_cardiometabolic_chronic_z": specific["mean_cardiometabolic_chronic_z"].mean(),
        }
        display = pd.concat([recurrent, pd.DataFrame([row])], ignore_index=True)
    else:
        display = recurrent.copy()
    lines = [
        r"\begin{table}[!htbp]",
        r"\caption{Clinical burden-profile families among selected Gaussian mixture classes}\label{tab:profile-families}",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{2pt}",
        r"\rowcolors{2}{tablegray}{white}",
        r"\begin{tabular}{@{}>{\raggedright\arraybackslash}p{0.19\textwidth}>{\raggedright\arraybackslash}p{0.19\textwidth}>{\raggedright\arraybackslash}p{0.22\textwidth}>{\raggedright\arraybackslash}p{0.11\textwidth}>{\raggedright\arraybackslash}p{0.25\textwidth}@{}}",
        r"\toprule",
        r"\rowcolor{tablehead}",
        r"Clinical family & Evidence tier & Cross-cohort evidence & N (\%) & Conservative interpretation\\",
        r"\midrule",
    ]
    for _, r in display.iterrows():
        signature = (
            f"{float(r['mean_functional_z']):.2f}/"
            f"{float(r['mean_cognitive_z']):.2f}/"
            f"{float(r['mean_affective_z']):.2f}/"
            f"{float(r['mean_cardiometabolic_chronic_z']):.2f}"
        )
        participant = f"{int(r['participants']):,} ({float(r['participant_pct_of_selected_profiles']):.1f}%)"
        interpretation = f"{family_reading(str(r['clinical_family']))} Mean z F/Cog/Aff/CM = {signature}."
        lines.append(
            " & ".join(
                [
                    tex_escape(family_label(str(r["clinical_family"]))),
                    tex_escape(evidence_tier(str(r["represented_cohorts"]))),
                    tex_escape(f"{int(r['selected_classes'])} classes; {r['represented_cohorts']}"),
                    tex_escape(participant),
                    tex_escape(interpretation),
                ]
            )
            + r"\\"
        )
    lines += [
        r"\botrule",
        r"\end{tabular}",
        r"\rowcolors{2}{white}{white}",
        r"\footnotetext{Evidence tiers describe measurement and validation constraints, not data quality. F = functional, Cog = cognitive, Aff = affective symptoms and CM = cardiometabolic/chronic disease burden. Full class-level details are provided in Additional file 7.}",
        r"\end{table}",
    ]
    return "\n".join(lines)


def table4_functional_assoc_tex(assoc: pd.DataFrame) -> str:
    lines = [
        r"\begin{table}[!htbp]",
        r"\caption{Functional deterioration associations and comparator guardrails}\label{tab:functional-association}",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{2pt}",
        r"\rowcolors{2}{tablegray}{white}",
        r"\begin{tabular}{@{}>{\raggedright\arraybackslash}p{0.24\textwidth}>{\raggedright\arraybackslash}p{0.27\textwidth}>{\raggedright\arraybackslash}p{0.21\textwidth}>{\raggedright\arraybackslash}p{0.25\textwidth}@{}}",
        r"\toprule",
        r"\rowcolor{tablehead}",
        r"Cohort, tier and N/events & Absolute-risk gradient & Adjusted association & Comparator and claim\\",
        r"\midrule",
    ]
    for _, r in assoc.set_index("cohort").loc[STRICT_VALIDATION_ORDER].reset_index().iterrows():
        or_cell = "1.00 (reference)" if r["highest_risk_class"] == r["reference_class"] else (
            f"OR {r['adjusted_or_highest_vs_class1']:.2f} ({r['ci_low']:.2f}-{r['ci_high']:.2f}); {fmt_p(r['p_value'])}"
        )
        risk_gradient = (
            f"C{int(r['reference_class'])}: {r['reference_event_pct']:.1f}% to "
            f"C{int(r['highest_risk_class'])}: {r['highest_risk_event_pct']:.1f}%; "
            f"+{r['absolute_risk_difference_pct']:.1f} pp"
        )
        comparator = (
            f"Delta AUC {r['delta_auc_profile_minus_continuous']:.3f}; "
            f"{'continuous favored' if float(r['delta_auc_profile_minus_continuous']) < 0 else 'profile favored'}; "
            f"{r['claim_status']}"
        )
        lines.append(
            " & ".join(
                [
                    tex_escape(f"{r['cohort']}; {r['tier']}; {fmt_int(r['validation_n'])}; {fmt_int(r['events'])} events"),
                    tex_escape(risk_gradient),
                    tex_escape(or_cell),
                    tex_escape(comparator),
                ]
            )
            + r"\\"
        )
    lines += [
        r"\botrule",
        r"\end{tabular}",
        r"\rowcolors{2}{white}{white}",
        r"\footnotetext{Associations use leave-functional-domain-out profile classes and minimal-core covariate adjustment (age, education, marital status, smoking and drinking) to reduce endpoint leakage. Absolute-risk values are crude event percentages for class 1 and the highest-risk class; pp = percentage points. Delta AUC is profile-model AUC minus continuous three-domain model AUC using the same covariate-adjusted analytic set; negative values favor continuous scores. These are within-cohort associations and guardrails, not transportable prediction models. Full class-level risks, AIC values and model metrics are provided in Additional files 13 and 14.}",
        r"\end{table}",
    ]
    return "\n".join(lines)


def replace_results_block(baseline: pd.DataFrame, assoc: pd.DataFrame) -> None:
    text = TEX.read_text(encoding="utf-8")
    start = text.index(r"\section{Results}")
    end = text.index(r"\section{Discussion}")
    new = r"""\section{Results}\label{sec:results}

\subsection{Cohort roles and denominators}

The source screen included 79,938 women aged 50 years or older, with 76,293 complete four-domain profile assignments. These denominators are not interchangeable. Six cohorts had functional follow-up rows for the decoupled validation guardrail, whereas LASI contributed baseline profile construction only. KLoSA remained bridge-sensitivity evidence. Table~\ref{tab:tier-lock} and Figure~\ref{fig:tier-lock} show the locked cohort roles, construction denominators, validation denominators and allowed claims.

""" + table1_tex() + r"""

\subsection{Baseline clinical characteristics and missingness}

The complete four-domain profile-construction sample varied clinically across cohorts in age, BMI availability, chronic-disease count and domain burden signatures (Table~\ref{tab:baseline-clinical}). Complete-case selection was also non-neutral: the included-versus-excluded audit separated source-screen, complete-domain and validation denominators and quantified domain-specific missingness (Additional file 12). These descriptive rows should be interpreted as analytic-sample characteristics, not population prevalence estimates.

""" + table2_baseline_tex(baseline) + r"""

\subsection{Clinical burden-profile families}

Across the selected cohort-specific Gaussian mixture solutions, 28 classes were summarized into recurrent or cohort-specific clinical burden-profile families (Table~\ref{tab:profile-families}; Figure~\ref{fig:profile-heatmap}). The largest recurrent family was an intermediate-burden pattern with relatively spared cardiometabolic/chronic disease burden, represented in six cohorts and 33,498 participants. A second recurrent pattern showed cardiometabolic/chronic disease burden with relative functional sparing. Smaller recurrent high-burden patterns were dominated by functional limitation. These families are descriptive clinical strata rather than diagnoses or risk tools.

""" + table3_profile_tex() + r"""

\FloatBarrier

\subsection{Functional deterioration associations and model guardrails}

In the leakage-control leave-functional-domain-out analysis, the highest-risk profile class showed higher crude functional-deterioration risk than the reference class in most validation cohorts, but continuous three-domain scores generally retained equal or better discrimination (Table~\ref{tab:functional-association}; Figure~\ref{fig:guardrails}). SHARE remained validation-downgraded, and KLoSA remained bridge-sensitivity evidence. These results support within-cohort descriptive association, not prediction superiority.

""" + table4_functional_assoc_tex(assoc) + r"""

\FloatBarrier

\subsection{Harmonization and robustness guardrails}

The item-level crosswalk included 97 rows and exposed the main comparability risks (Figure~\ref{fig:harmonization-risk}; Additional file 9). Functional-domain strictness differed across cohorts: CHARLS used IADL-only information, HRS used ADL-only information, KLoSA used a bridge proxy based on grip and falls, and SHARE used ADL/IADL variables but remained validation-downgraded. Cognitive batteries were not item-identical, SHARE used EURO-D for affective symptoms, and lipid/cholesterol indicators were not available in all cardiometabolic/chronic disease counts. Algorithm sensitivity analyses comparing unconstrained GMMs, constrained GMMs, k-means, sampled hierarchical clustering and continuous severity tertiles are provided in Additional file 14.

\FloatBarrier

\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth,height=0.72\textheight,keepaspectratio]{figure1_cohort_tier_lock-re.pdf}
\caption{Cohort denominators and locked manuscript roles. Source-screen, complete-domain profile construction and functional follow-up validation denominators are shown separately.}
\label{fig:tier-lock}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth,height=0.86\textheight,keepaspectratio]{figure2_descriptive_profile_heatmap-re.pdf}
\caption{Clinically annotated multidomain burden profiles. The left panel shows within-cohort class size, the central matrix shows four-domain z-scored burden profiles, and the right panel shows the clinical family, functional deterioration event percentage where available, and the locked construction or validation tier. Higher z-scores indicate worse burden. Rows marked as bridge, baseline-only, or validation-downgraded are retained for profile construction or descriptive comparison but are not interpreted as equivalent primary validation strata.}
\label{fig:profile-heatmap}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth,height=0.76\textheight,keepaspectratio]{figure3_validation_and_stability_guardrails-re.pdf}
\caption{Validation and model-stability guardrails. The left panel compares leave-functional-domain-out profile classes with continuous three-domain scores using delta AIC per 1,000 validation participants; negative values favor continuous scores. The middle panel shows bootstrap median and 10th percentile adjusted Rand index values with stability thresholds. The right table reports validation denominators, raw delta AIC/delta AUC, ARI p50/p10 and the locked claim status. Tier codes are S = strict validation-gradient evidence, D = validation downgraded, B = bridge sensitivity and N = no follow-up validation. All selected Gaussian mixture models triggered near-singular covariance downgrade diagnostics.}
\label{fig:guardrails}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth,height=0.78\textheight,keepaspectratio]{figure4_harmonization_risk_matrix-re.pdf}
\caption{Cohort-domain harmonization risk matrix. Cells show source tier, non-missing percentage and the principal construct used for each burden domain. The matrix makes the main measurement guardrails visible: KLoSA contributes a bridge functional proxy, CHARLS and HRS use partial functional information, SHARE uses EURO-D for affective symptoms, and cognitive batteries are cohort-specific or partial across several cohorts.}
\label{fig:harmonization-risk}
\end{figure}

\FloatBarrier

"""
    TEX.write_text(text[:start] + new + text[end:], encoding="utf-8")


def update_discussion() -> None:
    text = TEX.read_text(encoding="utf-8")
    start = text.index(r"\section{Discussion}")
    end = text.index(r"\section{Conclusions}")
    new = r"""\section{Discussion}\label{sec:discussion}

This revised analysis supports a descriptive burden-profile atlas with explicit clinical and methodological guardrails. Its contribution is a cross-cohort map of how functional, cognitive, affective and cardiometabolic/chronic burdens combine among older women, paired with denominator, missingness, harmonization, outcome-association and algorithm-robustness checks. The profile families provide a compact clinical vocabulary for heterogeneity that a single severity score can hide, especially for patterns in which cardiometabolic/chronic disease burden and functional limitation do not move together.

The negative and cautionary findings remain central. Functional deterioration is vulnerable to endpoint leakage when baseline functional score is used in profile construction. In the leave-functional-domain-out analysis, profile classes showed within-cohort absolute-risk gradients, but continuous three-domain scores generally retained equal or better discrimination. In addition, selected GMM covariance matrices were near-singular and algorithm sensitivity did not uniformly reproduce the selected classes. High posterior separation should therefore not be mistaken for robust latent subtype discovery.

These findings define the proper clinical interpretation. Burden-profile labels may be useful for communication, subgroup description and hypothesis generation. They should not be used as diagnoses, treatment assignments, transportable risk tools or evidence that categorical profiles outperform continuous domain measures. Mortality should remain secondary and guarded because previous proportional-hazards and piecewise diagnostics raised time-stability concerns.

\section{Strengths and limitations}\label{sec:limitations}

Strengths include the women-only focus across seven international aging cohorts, explicit denominator locking, baseline clinical characterization, included-versus-excluded missingness auditing, item-level harmonization review, decoupled functional-association analysis and model-stability diagnostics. The main limitations are also central to interpretation. First, baseline and follow-up functional information can be coupled when functional scores are used both for profile construction and outcome definition; the leave-functional-domain-out analysis was therefore treated as the main validation guardrail. Second, domain measures were harmonized by orientation and within-cohort standardization but were not instrument-identical across cohorts. Third, validation remained within-cohort association rather than transport validation, and LASI lacked a follow-up validation denominator in the current cleaned-data pass. Fourth, complete four-domain profiles may represent selected participants with sufficient data. Fifth, all selected GMM solutions triggered near-singular covariance diagnostics, and algorithm robustness was limited in several cohorts, so the classes should be interpreted as descriptive strata rather than stable latent disease entities.

"""
    TEX.write_text(text[:start] + new + text[end:], encoding="utf-8")


def update_additional_files_text() -> None:
    text = TEX.read_text(encoding="utf-8")
    old = (
        "Additional file 10: Clinical and epidemiology skill-search report.\\\\\n"
        "Supplementary Figure S1: Cohort validation dashboard.\\\\\n"
    )
    new = (
        "Additional file 10: Clinical and epidemiology skill-search report.\\\\\n"
        "Additional file 11: Baseline clinical characteristics.\\\\\n"
        "Additional file 12: Included-versus-excluded missingness audit.\\\\\n"
        "Additional file 13: Functional deterioration class-level risks and adjusted associations.\\\\\n"
        "Additional file 14: GMM algorithm robustness sensitivity.\\\\\n"
        "Supplementary Figure S1: Cohort validation dashboard.\\\\\n"
    )
    if old in text:
        text = text.replace(old, new)
    TEX.write_text(text, encoding="utf-8")


def write_additional_files() -> None:
    mapping = {
        "additional_file_11_baseline_clinical_characteristics.csv": OUT / "phase36_baseline_clinical_characteristics.csv",
        "additional_file_12_missingness_included_excluded.csv": OUT / "phase36_missingness_included_excluded.csv",
        "additional_file_13_functional_association_class_risks.csv": OUT / "phase36_functional_association_class_risks.csv",
        "additional_file_14_gmm_algorithm_robustness.csv": OUT / "phase36_gmm_algorithm_robustness.csv",
    }
    for name, src in mapping.items():
        shutil.copyfile(src, PKG / name)


def update_readme() -> None:
    readme = PKG / "README_BMC_Geriatrics_burden_profiles_rescue.md"
    text = readme.read_text(encoding="utf-8") if readme.exists() else "# BMC Geriatrics burden profile rescue package\n"
    add = """

## Phase 36 clinical-table upgrade

- Added baseline clinical characteristics and included-versus-excluded missingness audit.
- Replaced the main validation table with functional-deterioration absolute-risk and adjusted-association guardrails.
- Added GMM algorithm robustness sensitivity comparing unconstrained GMM, constrained GMM, k-means, sampled hierarchical clustering and continuous severity tertiles.
- Harmonization matrix remains available as Figure 4 and Additional file 9 rather than a crowded main table.
"""
    if "## Phase 36 clinical-table upgrade" not in text:
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
        "figure1_cohort_tier_lock.png",
        "figure1_cohort_tier_lock.pdf",
        "figure1_cohort_tier_lock.svg",
        "figure1_cohort_tier_lock-re.pdf",
        "figure2_descriptive_profile_heatmap.png",
        "figure2_descriptive_profile_heatmap.pdf",
        "figure2_descriptive_profile_heatmap.svg",
        "figure2_descriptive_profile_heatmap-re.pdf",
        "figure3_validation_and_stability_guardrails.png",
        "figure3_validation_and_stability_guardrails.pdf",
        "figure3_validation_and_stability_guardrails.svg",
        "figure3_validation_and_stability_guardrails-re.pdf",
        "figure4_harmonization_risk_matrix.png",
        "figure4_harmonization_risk_matrix.pdf",
        "figure4_harmonization_risk_matrix.svg",
        "figure4_harmonization_risk_matrix-re.pdf",
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
    baseline = build_baseline_characteristics()
    missing = build_missingness_table()
    assoc, class_risks, model_metrics = build_functional_association_tables()
    robustness, robustness_summary = build_algorithm_robustness()
    ensure_table_style_preamble()
    replace_results_block(baseline, assoc)
    update_discussion()
    update_additional_files_text()
    write_additional_files()
    update_readme()
    # Zips are rebuilt after LaTeX compilation by a separate call if needed.
    print(OUT / "phase36_baseline_clinical_characteristics.csv")
    print(OUT / "phase36_missingness_included_excluded.csv")
    print(OUT / "phase36_functional_association_main.csv")
    print(OUT / "phase36_gmm_algorithm_robustness_summary.csv")
    print(TEX)


if __name__ == "__main__":
    main()
