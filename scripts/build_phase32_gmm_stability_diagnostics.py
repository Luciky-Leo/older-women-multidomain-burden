from __future__ import annotations

import argparse
from itertools import permutations
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import adjusted_rand_score
from sklearn.mixture import GaussianMixture


DOMAIN_COLUMNS = [
    "functional_score",
    "cognitive_score",
    "affective_score",
    "cardiometabolic_chronic_score",
]

MIN_EIGENVALUE_THRESHOLD = 1e-5
MAX_CONDITION_THRESHOLD = 1e6
MIN_DETERMINANT_THRESHOLD = 1e-10
STABLE_MEDIAN_ARI = 0.75
STABLE_P10_ARI = 0.60


def read_scores(path: Path) -> pd.DataFrame:
    scores = pd.read_csv(path, dtype={"participant_id": str, "wave": str}, low_memory=False)
    for column in DOMAIN_COLUMNS:
        scores[column] = pd.to_numeric(scores[column], errors="coerce")
    scores["complete_four_domain"] = pd.to_numeric(scores["complete_four_domain"], errors="coerce").fillna(0).astype(int)
    scores = scores[scores["complete_four_domain"] == 1].copy()
    scores["severity_score"] = scores[DOMAIN_COLUMNS].mean(axis=1)
    return scores


def fit_gmm(x: np.ndarray, n_classes: int, random_state: int, n_init: int) -> GaussianMixture:
    model = GaussianMixture(
        n_components=n_classes,
        covariance_type="full",
        reg_covar=1e-6,
        n_init=n_init,
        max_iter=500,
        random_state=random_state,
    )
    model.fit(x)
    return model


def ordered_component_indices(model: GaussianMixture) -> list[int]:
    severity = model.means_.mean(axis=1)
    return [int(idx) for idx in np.argsort(severity)]


def ordered_means(model: GaussianMixture) -> np.ndarray:
    order = ordered_component_indices(model)
    return model.means_[order]


def covariance_diagnostics(
    model: GaussianMixture,
    metadata: dict[str, object],
) -> list[dict[str, object]]:
    rows = []
    order = ordered_component_indices(model)
    for ordered_class, raw_index in enumerate(order, start=1):
        covariance = model.covariances_[raw_index]
        eigenvalues = np.linalg.eigvalsh(covariance)
        min_eigen = float(np.min(eigenvalues))
        max_eigen = float(np.max(eigenvalues))
        determinant = float(np.linalg.det(covariance))
        condition_number = float(max_eigen / min_eigen) if min_eigen > 0 else np.inf
        row = {
            **metadata,
            "ordered_class": ordered_class,
            "raw_component": int(raw_index),
            "component_weight": round(float(model.weights_[raw_index]), 6),
            "min_covariance_eigenvalue": min_eigen,
            "max_covariance_eigenvalue": max_eigen,
            "covariance_condition_number": condition_number,
            "covariance_determinant": determinant,
            "near_singular_covariance_flag": int(
                (min_eigen < MIN_EIGENVALUE_THRESHOLD)
                or (condition_number > MAX_CONDITION_THRESHOLD)
                or (determinant < MIN_DETERMINANT_THRESHOLD)
            ),
        }
        for idx, column in enumerate(DOMAIN_COLUMNS):
            row[f"mean_{column}"] = round(float(model.means_[raw_index, idx]), 4)
        rows.append(row)
    return rows


def best_centroid_distance(reference: np.ndarray, replicate: np.ndarray) -> tuple[float, float, str]:
    n_classes = reference.shape[0]
    best_perm: tuple[int, ...] | None = None
    best_mean = np.inf
    best_max = np.inf
    for perm in permutations(range(n_classes)):
        distances = np.linalg.norm(reference - replicate[list(perm), :], axis=1)
        mean_distance = float(np.mean(distances))
        max_distance = float(np.max(distances))
        if (mean_distance < best_mean) or (mean_distance == best_mean and max_distance < best_max):
            best_mean = mean_distance
            best_max = max_distance
            best_perm = perm
    mapping = ",".join(str(item + 1) for item in best_perm) if best_perm is not None else ""
    return best_mean, best_max, mapping


def normalized_entropy(probabilities: np.ndarray) -> float:
    clipped = np.clip(probabilities, 1e-12, 1.0)
    entropy = -np.mean(np.sum(clipped * np.log(clipped), axis=1))
    return float(1.0 - entropy / np.log(probabilities.shape[1]))


def bootstrap_stability(
    data: pd.DataFrame,
    reference_model: GaussianMixture,
    metadata: dict[str, object],
    replicates: int,
    n_init: int,
    seed: int,
) -> list[dict[str, object]]:
    x_full = data[DOMAIN_COLUMNS].to_numpy(dtype=float)
    reference_labels = reference_model.predict(x_full)
    reference_means = ordered_means(reference_model)
    rng = np.random.default_rng(seed)
    rows = []
    for replicate_id in range(1, replicates + 1):
        indices = rng.integers(0, len(data), size=len(data))
        x_sample = x_full[indices]
        try:
            model = fit_gmm(x_sample, int(metadata["n_classes"]), seed + replicate_id, n_init)
            replicate_labels = model.predict(x_full)
            ari = float(adjusted_rand_score(reference_labels, replicate_labels))
            replicate_probs = model.predict_proba(x_full)
            min_class_pct = float(np.min(np.bincount(replicate_labels, minlength=int(metadata["n_classes"])) / len(data) * 100))
            mean_distance, max_distance, mapping = best_centroid_distance(reference_means, ordered_means(model))
            converged = int(model.converged_)
            entropy = normalized_entropy(replicate_probs)
            skip_reason = ""
        except Exception as exc:  # pragma: no cover - diagnostic path
            ari = np.nan
            min_class_pct = np.nan
            mean_distance = np.nan
            max_distance = np.nan
            mapping = ""
            converged = 0
            entropy = np.nan
            skip_reason = f"fit_failed: {type(exc).__name__}: {exc}"
        rows.append(
            {
                **metadata,
                "replicate_id": replicate_id,
                "resample_design": "nonparametric_bootstrap",
                "adjusted_rand_index_vs_reference": round(ari, 4) if not pd.isna(ari) else np.nan,
                "mean_centroid_distance_vs_reference": round(mean_distance, 4) if not pd.isna(mean_distance) else np.nan,
                "max_centroid_distance_vs_reference": round(max_distance, 4) if not pd.isna(max_distance) else np.nan,
                "aligned_component_order": mapping,
                "replicate_min_class_pct_on_full_data": round(min_class_pct, 2) if not pd.isna(min_class_pct) else np.nan,
                "replicate_entropy_separation_on_full_data": round(entropy, 4) if not pd.isna(entropy) else np.nan,
                "replicate_converged": converged,
                "skip_reason": skip_reason,
            }
        )
    return rows


def summarize_stability(covariance: pd.DataFrame, bootstrap: pd.DataFrame) -> pd.DataFrame:
    if bootstrap.empty:
        return pd.DataFrame()
    rows = []
    group_cols = ["analysis_set", "analysis_tier", "cohort", "wave", "n_classes"]
    cov_summary = (
        covariance.groupby(group_cols, dropna=False)
        .agg(
            any_near_singular_covariance=("near_singular_covariance_flag", "max"),
            min_covariance_eigenvalue=("min_covariance_eigenvalue", "min"),
            max_covariance_condition_number=("covariance_condition_number", "max"),
        )
        .reset_index()
    )
    for keys, group in bootstrap.groupby(group_cols, dropna=False):
        analysis_set, analysis_tier, cohort, wave, n_classes = keys
        ari = pd.to_numeric(group["adjusted_rand_index_vs_reference"], errors="coerce")
        converged_pct = float(pd.to_numeric(group["replicate_converged"], errors="coerce").mean() * 100)
        row = {
            "analysis_set": analysis_set,
            "analysis_tier": analysis_tier,
            "cohort": cohort,
            "wave": wave,
            "n_classes": n_classes,
            "bootstrap_replicates": int(len(group)),
            "bootstrap_converged_pct": round(converged_pct, 2),
            "median_ari_vs_reference": round(float(ari.median()), 4) if ari.notna().any() else np.nan,
            "p10_ari_vs_reference": round(float(ari.quantile(0.10)), 4) if ari.notna().any() else np.nan,
            "min_ari_vs_reference": round(float(ari.min()), 4) if ari.notna().any() else np.nan,
            "median_mean_centroid_distance": round(float(group["mean_centroid_distance_vs_reference"].median()), 4),
            "max_centroid_distance": round(float(group["max_centroid_distance_vs_reference"].max()), 4),
            "median_replicate_min_class_pct": round(float(group["replicate_min_class_pct_on_full_data"].median()), 2),
        }
        rows.append(row)
    summary = pd.DataFrame(rows)
    summary = summary.merge(cov_summary, on=group_cols, how="left")
    summary["phase32d_stability_status"] = summary.apply(stability_status, axis=1)
    return summary


def stability_status(row: pd.Series) -> str:
    if int(row.get("any_near_singular_covariance", 0)) == 1:
        return "downgrade_near_singular_covariance"
    if float(row.get("bootstrap_converged_pct", 0)) < 95:
        return "downgrade_bootstrap_nonconvergence"
    if pd.isna(row.get("median_ari_vs_reference")):
        return "downgrade_no_bootstrap_evidence"
    if float(row["median_ari_vs_reference"]) >= STABLE_MEDIAN_ARI and float(row["p10_ari_vs_reference"]) >= STABLE_P10_ARI:
        return "stable_by_bootstrap_ari"
    return "downgrade_unstable_bootstrap_ari"


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


def write_report(path: Path, summary: pd.DataFrame, covariance: pd.DataFrame) -> None:
    lines = [
        "# Phase 32D GMM Stability And Covariance Diagnostics",
        "",
        "Date: 2026-06-02",
        "",
        "## Decision Rule",
        "",
        f"- Near-singular covariance flag: min eigenvalue < {MIN_EIGENVALUE_THRESHOLD:g}, condition number > {MAX_CONDITION_THRESHOLD:g}, or determinant < {MIN_DETERMINANT_THRESHOLD:g}.",
        f"- Stable bootstrap rule: median ARI >= {STABLE_MEDIAN_ARI:g} and 10th percentile ARI >= {STABLE_P10_ARI:g}, with >=95% convergence.",
        "",
        "## Stability Summary",
        "",
    ]
    columns = [
        "cohort",
        "n_classes",
        "bootstrap_converged_pct",
        "median_ari_vs_reference",
        "p10_ari_vs_reference",
        "min_ari_vs_reference",
        "median_mean_centroid_distance",
        "max_centroid_distance",
        "any_near_singular_covariance",
        "phase32d_stability_status",
    ]
    lines.extend(markdown_table(summary.sort_values(["analysis_set", "cohort"]), columns))
    lines.extend(["", "## Covariance Flags", ""])
    flagged = covariance[pd.to_numeric(covariance["near_singular_covariance_flag"], errors="coerce") == 1].copy()
    if flagged.empty:
        lines.append("No selected-model components crossed the near-singular covariance threshold.")
    else:
        lines.extend(
            markdown_table(
                flagged.sort_values(["analysis_set", "cohort", "ordered_class"]),
                [
                    "cohort",
                    "ordered_class",
                    "component_weight",
                    "min_covariance_eigenvalue",
                    "covariance_condition_number",
                    "covariance_determinant",
                ],
            )
        )
    lines.extend(
        [
            "",
            "## Manuscript Rule",
            "",
            "Profiles marked stable_by_bootstrap_ari can remain in descriptive profile construction tables.",
            "Profiles marked with any downgrade status must be explicitly labeled as unstable or downgraded to sensitivity/descriptive-only evidence.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scores", type=Path, default=Path("outputs/phase3_domain_scores.csv"))
    parser.add_argument("--best-models", type=Path, default=Path("outputs/phase4_best_model_summary.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    parser.add_argument("--replicates", type=int, default=20)
    parser.add_argument("--random-state", type=int, default=20260602)
    parser.add_argument("--n-init-reference", type=int, default=5)
    parser.add_argument("--n-init-bootstrap", type=int, default=3)
    args = parser.parse_args()

    scores = read_scores(args.scores)
    best_models = pd.read_csv(args.best_models, dtype={"wave": str}, low_memory=False)
    covariance_rows = []
    bootstrap_rows = []
    for best in best_models.sort_values(["analysis_set", "cohort"]).to_dict("records"):
        mask = (
            (scores["analysis_set"] == best["analysis_set"])
            & (scores["analysis_tier"] == best["analysis_tier"])
            & (scores["cohort"] == best["cohort"])
            & (scores["wave"].astype(str) == str(best["wave"]))
        )
        group = scores[mask].copy()
        x = group[DOMAIN_COLUMNS].to_numpy(dtype=float)
        metadata = {
            "analysis_set": best["analysis_set"],
            "analysis_tier": best["analysis_tier"],
            "cohort": best["cohort"],
            "wave": best["wave"],
            "n": int(len(group)),
            "n_classes": int(best["n_classes"]),
            "reference_bic": float(best["bic"]),
            "reference_entropy_separation": float(best["entropy_separation"]),
            "reference_mean_max_posterior": float(best["mean_max_posterior"]),
        }
        reference = fit_gmm(x, int(best["n_classes"]), args.random_state, args.n_init_reference)
        covariance_rows.extend(covariance_diagnostics(reference, metadata))
        bootstrap_rows.extend(
            bootstrap_stability(
                group,
                reference,
                metadata,
                replicates=args.replicates,
                n_init=args.n_init_bootstrap,
                seed=args.random_state + int(len(bootstrap_rows)) + 101,
            )
        )

    covariance = pd.DataFrame(covariance_rows)
    bootstrap = pd.DataFrame(bootstrap_rows)
    summary = summarize_stability(covariance, bootstrap)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    covariance.to_csv(args.output_dir / "phase32_gmm_covariance_diagnostics.csv", index=False, encoding="utf-8-sig")
    bootstrap.to_csv(args.output_dir / "phase32_gmm_bootstrap_stability.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(args.output_dir / "phase32_gmm_stability_summary.csv", index=False, encoding="utf-8-sig")
    write_report(args.output_dir / "phase32_gmm_stability_report.md", summary, covariance)

    print("Phase 32D GMM stability diagnostics complete.")
    print(summary[["cohort", "n_classes", "median_ari_vs_reference", "p10_ari_vs_reference", "phase32d_stability_status"]].to_string(index=False))


if __name__ == "__main__":
    main()
