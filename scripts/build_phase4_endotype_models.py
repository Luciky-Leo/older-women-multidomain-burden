from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture


DOMAIN_COLUMNS = [
    "functional_score",
    "cognitive_score",
    "affective_score",
    "cardiometabolic_chronic_score",
]

DOMAIN_LABELS = {
    "functional_score": "functional",
    "cognitive_score": "cognitive",
    "affective_score": "affective",
    "cardiometabolic_chronic_score": "cardiometabolic_chronic",
}

MIN_CLASS_PCT = 5.0


@dataclass(frozen=True)
class FitResult:
    model: GaussianMixture
    metrics: dict[str, object]
    profiles: pd.DataFrame
    assignments: pd.DataFrame
    summary: dict[str, object]


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
    severity = float(row["severity_mean"])
    deviations = {}
    for column in DOMAIN_COLUMNS:
        domain = DOMAIN_LABELS[column]
        deviations[domain] = float(row[column]) - severity
    high_domains = [name for name, value in deviations.items() if value >= 0.35]
    spared_domains = [name for name, value in deviations.items() if value <= -0.35]
    if high_domains or spared_domains:
        label = severity_label(severity)
        if high_domains:
            label += "_high_" + "_".join(high_domains)
        if spared_domains:
            label += "_spared_" + "_".join(spared_domains)
        return label, ";".join(high_domains), ";".join(spared_domains)
    return severity_label(severity) + "_severity_aligned", "", ""


def monotonic_domain_count(profiles: pd.DataFrame) -> int:
    count = 0
    for column in DOMAIN_COLUMNS:
        values = profiles[column].to_numpy(dtype=float)
        if np.all(np.diff(values) >= -0.10) or np.all(np.diff(values) <= 0.10):
            count += 1
    return count


def profile_interpretation(profiles: pd.DataFrame) -> dict[str, object]:
    deviations = profiles[DOMAIN_COLUMNS].subtract(profiles["severity_mean"], axis=0).abs()
    max_deviation = float(deviations.max().max())
    monotonic_count = monotonic_domain_count(profiles)
    if max_deviation >= 0.50:
        interpretation = "domain_specific"
    elif monotonic_count >= 3:
        interpretation = "mostly_severity_gradient"
    else:
        interpretation = "mixed_profile"
    return {
        "profile_interpretation": interpretation,
        "max_domain_deviation_from_severity": round(max_deviation, 4),
        "monotonic_domain_count": monotonic_count,
    }


def order_classes(labels: np.ndarray, probabilities: np.ndarray, data: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, dict[int, int]]:
    temp = data.copy()
    temp["raw_class"] = labels
    severity_by_raw = temp.groupby("raw_class")["severity_score"].mean().sort_values()
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
    profile_frame["class"] = ordered_labels
    rows = []
    total_n = len(profile_frame)
    for class_id, group in profile_frame.groupby("class"):
        posterior = ordered_probabilities[ordered_labels == class_id, class_id - 1]
        row = {
            **metadata,
            "class": int(class_id),
            "class_n": int(len(group)),
            "class_pct": round(len(group) / total_n * 100, 2),
            "mean_posterior": round(float(np.mean(posterior)), 4),
            "severity_mean": round(float(group["severity_score"].mean()), 4),
            "severity_sd": round(float(group["severity_score"].std()), 4),
        }
        for column in DOMAIN_COLUMNS:
            row[column] = round(float(group[column].mean()), 4)
        label, high_domains, spared_domains = class_profile_label(pd.Series(row))
        row["profile_label"] = label
        row["high_domains_vs_class_severity"] = high_domains
        row["spared_domains_vs_class_severity"] = spared_domains
        rows.append(row)
    return pd.DataFrame(rows).sort_values("class")


def fit_one_model(data: pd.DataFrame, n_components: int, metadata: dict[str, object], random_state: int, n_init: int) -> FitResult:
    x = data[DOMAIN_COLUMNS].to_numpy(dtype=float)
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
    interpretation = profile_interpretation(profiles)
    min_class_n = int(profiles["class_n"].min())
    min_class_pct = float(profiles["class_pct"].min())
    metrics = {
        **metadata,
        "n": len(data),
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
        **interpretation,
    }
    assignment_frame = data[
        ["analysis_set", "analysis_tier", "cohort", "participant_id", "wave", "age", "severity_score", *DOMAIN_COLUMNS]
    ].copy()
    assignment_frame["n_classes"] = n_components
    assignment_frame["endotype_class"] = ordered_labels
    assignment_frame["endotype_posterior"] = ordered_probabilities.max(axis=1)
    return FitResult(model=model, metrics=metrics, profiles=profiles, assignments=assignment_frame, summary=metrics)


def severity_comparator(scores: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for keys, group in scores.groupby(["analysis_set", "analysis_tier", "cohort", "wave"], dropna=False):
        analysis_set, analysis_tier, cohort, wave = keys
        labels = pd.qcut(group["severity_score"], q=3, labels=["low", "middle", "high"], duplicates="drop")
        temp = group.copy()
        temp["severity_group"] = labels.astype(str)
        for severity_group, subgroup in temp.groupby("severity_group"):
            row = {
                "analysis_set": analysis_set,
                "analysis_tier": analysis_tier,
                "cohort": cohort,
                "wave": wave,
                "severity_group": severity_group,
                "n": len(subgroup),
                "pct": round(len(subgroup) / len(group) * 100, 2),
                "severity_mean": round(float(subgroup["severity_score"].mean()), 4),
            }
            for column in DOMAIN_COLUMNS:
                row[column] = round(float(subgroup[column].mean()), 4)
            rows.append(row)
    return pd.DataFrame(rows)


def load_scores(path: Path) -> pd.DataFrame:
    scores = pd.read_csv(path, dtype={"participant_id": str, "wave": str}, low_memory=False)
    for column in DOMAIN_COLUMNS:
        scores[column] = pd.to_numeric(scores[column], errors="coerce")
    scores["complete_four_domain"] = pd.to_numeric(scores["complete_four_domain"], errors="coerce").fillna(0).astype(int)
    scores = scores[scores["complete_four_domain"] == 1].copy()
    scores["severity_score"] = scores[DOMAIN_COLUMNS].mean(axis=1)
    return scores


def run_models(scores: pd.DataFrame, random_state: int, n_init: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    metric_rows = []
    profile_frames = []
    assignment_frames = []
    best_rows = []

    grouped = scores.groupby(["analysis_set", "analysis_tier", "cohort", "wave"], dropna=False)
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
        best_summary = dict(best.summary)
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
        pd.concat(profile_frames, ignore_index=True),
        pd.DataFrame(best_rows),
        pd.concat(assignment_frames, ignore_index=True),
    )


def write_report(
    path: Path,
    metrics: pd.DataFrame,
    best: pd.DataFrame,
    profiles: pd.DataFrame,
    severity_profiles: pd.DataFrame,
) -> None:
    lines = [
        "# Phase 4 Endotype Screen",
        "",
        "This is a first-pass Gaussian mixture screen on complete four-domain baseline scores.",
        "All four domain scores are standardized and oriented so higher means worse health.",
        "",
        "## Best Models By BIC",
        "",
        f"Model selection uses the lowest BIC among converged models with minimum class size >= {MIN_CLASS_PCT:g}%. The BIC-only winner is retained in the CSV outputs.",
        "",
        "| Analysis set | Cohort | N | Best classes | BIC | Min class % | Entropy separation | Mean max posterior | Interpretation |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in best.sort_values(["analysis_set", "cohort"]).to_dict("records"):
        lines.append(
            f"| {row['analysis_set']} | {row['cohort']} | {row['n']} | {row['n_classes']} | {row['bic']} | "
            f"{row['min_class_pct']} | {row['entropy_separation']} | {row['mean_max_posterior']} | "
            f"{row['profile_interpretation']} |"
        )

    differs = best[pd.to_numeric(best["selected_differs_from_bic_winner"], errors="coerce") == 1]
    if not differs.empty:
        lines.extend(["", "BIC-only winners rejected for small class size:", ""])
        for row in differs.sort_values(["analysis_set", "cohort"]).to_dict("records"):
            lines.append(
                f"- {row['cohort']}: BIC-only {row['bic_winner_n_classes']} classes "
                f"(min class {row['bic_winner_min_class_pct']}%) -> selected {row['n_classes']} classes."
            )

    lines.extend(["", "## Best-Model Class Profiles", ""])
    lines.append("| Analysis set | Cohort | Class | N | % | Severity mean | Functional | Cognitive | Affective | Cardiometabolic | Label |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|")
    best_keys = set(
        tuple(row)
        for row in best[["analysis_set", "cohort", "n_classes"]].itertuples(index=False, name=None)
    )
    best_profiles = profiles[
        profiles.apply(lambda row: (row["analysis_set"], row["cohort"], row["n_classes"]) in best_keys, axis=1)
    ]
    for row in best_profiles.sort_values(["analysis_set", "cohort", "class"]).to_dict("records"):
        lines.append(
            f"| {row['analysis_set']} | {row['cohort']} | {row['class']} | {row['class_n']} | {row['class_pct']} | "
            f"{row['severity_mean']} | {row['functional_score']} | {row['cognitive_score']} | "
            f"{row['affective_score']} | {row['cardiometabolic_chronic_score']} | {row['profile_label']} |"
        )

    severity_like = best[best["profile_interpretation"] == "mostly_severity_gradient"]
    domain_specific = best[best["profile_interpretation"] == "domain_specific"]
    lines.extend(
        [
            "",
        "## Severity Comparator",
            "",
            "A simple comparator was created by tertiling the mean of the four domain scores. Use this as the null model for low/middle/high severity.",
            "",
            "## Proceeding Decision",
            "",
            f"- Domain-specific best-model profiles: {', '.join(domain_specific['cohort'].astype(str)) if not domain_specific.empty else 'none by the current automated rule'}.",
            f"- Mostly severity-gradient best-model profiles: {', '.join(severity_like['cohort'].astype(str)) if not severity_like.empty else 'none by the current automated rule'}.",
            "- Manual inspection of the best-model class profiles is required before moving to manuscript claims.",
            "- Phase 5 should connect these classes to mortality and functional deterioration, and compare them against the severity tertile comparator.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scores", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--random-state", type=int, default=20260601)
    parser.add_argument("--n-init", type=int, default=5)
    args = parser.parse_args()

    scores = load_scores(args.scores)
    metrics, profiles, best, assignments = run_models(scores, args.random_state, args.n_init)
    severity_profiles = severity_comparator(scores)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(args.output_dir / "phase4_gmm_model_metrics.csv", index=False, encoding="utf-8-sig")
    profiles.to_csv(args.output_dir / "phase4_gmm_class_profiles.csv", index=False, encoding="utf-8-sig")
    best.to_csv(args.output_dir / "phase4_best_model_summary.csv", index=False, encoding="utf-8-sig")
    assignments.to_csv(args.output_dir / "phase4_best_model_assignments.csv", index=False, encoding="utf-8-sig")
    severity_profiles.to_csv(args.output_dir / "phase4_severity_comparator_profiles.csv", index=False, encoding="utf-8-sig")
    write_report(args.output_dir / "phase4_endotype_screen_report.md", metrics, best, profiles, severity_profiles)


if __name__ == "__main__":
    main()
