from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


DOMAIN_COLUMNS = [
    "functional_score",
    "cognitive_score",
    "affective_score",
    "cardiometabolic_chronic_score",
]

DOMAIN_LABELS = ["Functional", "Cognitive", "Affective", "Cardiometabolic"]

ENDPOINT_LABELS = {
    "functional_deterioration_ge_0_5sd": "Functional deterioration",
    "chronic_progression_ge_1_condition": "Chronic progression",
    "all_cause_mortality": "Mortality",
}

COHORT_ORDER = ["CHARLS", "ELSA", "HRS", "KLoSA", "MHAS", "SHARE", "LASI"]


def read_best_profiles(output_dir: Path) -> pd.DataFrame:
    profiles = pd.read_csv(output_dir / "phase4_gmm_class_profiles.csv", low_memory=False)
    best = pd.read_csv(output_dir / "phase4_best_model_summary.csv", low_memory=False)
    keys = best[["analysis_set", "cohort", "n_classes"]].drop_duplicates()
    out = profiles.merge(keys, on=["analysis_set", "cohort", "n_classes"], how="inner")
    out["class"] = out["class"].astype(int)
    return out.sort_values(["analysis_set", "cohort", "class"])


def class_event_summaries(output_dir: Path) -> pd.DataFrame:
    follow = pd.read_csv(output_dir / "phase5_followup_outcome_inventory.csv", low_memory=False)
    follow = follow[follow["group_type"] == "endotype_class"].copy()
    follow["class"] = pd.to_numeric(follow["group_value"], errors="coerce").astype("Int64")
    keep_follow = [
        "analysis_set",
        "cohort",
        "class",
        "functional_deterioration_ge_0_5sd_available_n",
        "functional_deterioration_ge_0_5sd_event_n",
        "functional_deterioration_ge_0_5sd_event_pct",
        "chronic_progression_ge_1_condition_available_n",
        "chronic_progression_ge_1_condition_event_n",
        "chronic_progression_ge_1_condition_event_pct",
    ]
    follow = follow[[column for column in keep_follow if column in follow.columns]]

    mortality = pd.read_csv(output_dir / "phase6_mortality_summary.csv", low_memory=False)
    mortality = mortality[mortality["group_type"] == "endotype_class"].copy()
    mortality["class"] = pd.to_numeric(mortality["group_value"], errors="coerce").astype("Int64")
    keep_mortality = [
        "analysis_set",
        "cohort",
        "class",
        "mortality_followup_available_n",
        "death_n",
        "death_pct",
        "median_followup_time_years",
    ]
    mortality = mortality[[column for column in keep_mortality if column in mortality.columns]]
    return follow.merge(mortality, on=["analysis_set", "cohort", "class"], how="outer")


def add_reference_rows(effects: pd.DataFrame, profiles: pd.DataFrame, value_columns: list[str], model_kind: str) -> pd.DataFrame:
    refs = profiles[["analysis_set", "analysis_tier", "cohort", "class"]].copy()
    refs = refs[refs["class"] == 1].copy()
    if model_kind == "or":
        refs["effect_measure"] = "OR"
        refs["or"] = 1.0
        refs["or_ci_low"] = 1.0
        refs["or_ci_high"] = 1.0
    else:
        refs["effect_measure"] = "HR"
        refs["hr"] = 1.0
        refs["hr_ci_low"] = 1.0
        refs["hr_ci_high"] = 1.0
    refs["p_value"] = np.nan
    refs["outcome"] = ""
    refs["outcome_label"] = ""
    return pd.concat([effects, refs], ignore_index=True, sort=False)


def read_or_effects(output_dir: Path, profiles: pd.DataFrame) -> pd.DataFrame:
    terms = pd.read_csv(output_dir / "phase5_outcome_model_terms.csv", low_memory=False)
    terms = terms[
        (terms["model_type"] == "endotype")
        & (terms["adjustment"] == "age_adjusted")
        & (terms["term_label"] != "Intercept")
        & (terms["term_label"] != "age")
    ].copy()
    terms["class"] = pd.to_numeric(terms["term_label"], errors="coerce").astype("Int64")
    terms = terms.rename(columns={"ci_low": "or_ci_low", "ci_high": "or_ci_high"})
    terms["effect_measure"] = "OR"
    keep = [
        "analysis_set",
        "analysis_tier",
        "cohort",
        "outcome",
        "outcome_label",
        "class",
        "effect_measure",
        "or",
        "or_ci_low",
        "or_ci_high",
        "p_value",
    ]
    terms = terms[keep]
    references = []
    for outcome, outcome_label in terms[["outcome", "outcome_label"]].drop_duplicates().itertuples(index=False):
        ref = profiles[["analysis_set", "analysis_tier", "cohort", "class"]].copy()
        ref = ref[ref["class"] == 1].copy()
        ref["outcome"] = outcome
        ref["outcome_label"] = outcome_label
        ref["effect_measure"] = "OR"
        ref["or"] = 1.0
        ref["or_ci_low"] = 1.0
        ref["or_ci_high"] = 1.0
        ref["p_value"] = np.nan
        references.append(ref)
    if references:
        terms = pd.concat([terms, *references], ignore_index=True, sort=False)
    return terms


def read_hr_effects(output_dir: Path, profiles: pd.DataFrame) -> pd.DataFrame:
    terms = pd.read_csv(output_dir / "phase6_mortality_model_terms.csv", low_memory=False)
    terms = terms[
        (terms["model_type"] == "endotype")
        & (terms["term_label"] != "age")
    ].copy()
    terms["class"] = pd.to_numeric(terms["term_label"], errors="coerce").astype("Int64")
    terms = terms.rename(columns={"ci_low": "hr_ci_low", "ci_high": "hr_ci_high"})
    terms["outcome_label"] = "All-cause mortality"
    terms["effect_measure"] = "HR"
    keep = [
        "analysis_set",
        "analysis_tier",
        "cohort",
        "outcome",
        "outcome_label",
        "class",
        "effect_measure",
        "hr",
        "hr_ci_low",
        "hr_ci_high",
        "p_value",
    ]
    terms = terms[keep]
    ref = profiles[["analysis_set", "analysis_tier", "cohort", "class"]].copy()
    ref = ref[ref["class"] == 1].copy()
    ref = ref[ref["cohort"] != "LASI"].copy()
    ref["outcome"] = "all_cause_mortality"
    ref["outcome_label"] = "All-cause mortality"
    ref["effect_measure"] = "HR"
    ref["hr"] = 1.0
    ref["hr_ci_low"] = 1.0
    ref["hr_ci_high"] = 1.0
    ref["p_value"] = np.nan
    return pd.concat([terms, ref], ignore_index=True, sort=False)


def effect_pivot(effects: pd.DataFrame, outcome: str, prefix: str) -> pd.DataFrame:
    subset = effects[effects["outcome"] == outcome].copy()
    if subset.empty:
        return pd.DataFrame(columns=["analysis_set", "cohort", "class"])
    measure = "or" if prefix.endswith("or") else "hr"
    low = f"{measure}_ci_low"
    high = f"{measure}_ci_high"
    subset[f"{prefix}_formatted"] = subset.apply(
        lambda row: format_effect(row[measure], row[low], row[high]),
        axis=1,
    )
    rename = {
        measure: prefix,
        low: f"{prefix}_ci_low",
        high: f"{prefix}_ci_high",
        "p_value": f"{prefix}_p_value",
        f"{prefix}_formatted": f"{prefix}_formatted",
    }
    return subset[["analysis_set", "cohort", "class", measure, low, high, "p_value", f"{prefix}_formatted"]].rename(columns=rename)


def format_effect(value: float, low: float, high: float) -> str:
    if pd.isna(value):
        return ""
    return f"{value:.2f} ({low:.2f}-{high:.2f})"


def build_review_table(output_dir: Path) -> pd.DataFrame:
    profiles = read_best_profiles(output_dir)
    events = class_event_summaries(output_dir)
    or_effects = read_or_effects(output_dir, profiles)
    hr_effects = read_hr_effects(output_dir, profiles)

    review = profiles.merge(events, on=["analysis_set", "cohort", "class"], how="left")
    for outcome, prefix in [
        ("functional_deterioration_ge_0_5sd", "functional_or"),
        ("chronic_progression_ge_1_condition", "chronic_or"),
    ]:
        review = review.merge(effect_pivot(or_effects, outcome, prefix), on=["analysis_set", "cohort", "class"], how="left")
    review = review.merge(
        effect_pivot(hr_effects, "all_cause_mortality", "mortality_hr"),
        on=["analysis_set", "cohort", "class"],
        how="left",
    )

    review["class_outcome_note"] = review.apply(class_note, axis=1)
    ordered = [
        "analysis_set",
        "analysis_tier",
        "cohort",
        "wave",
        "n_classes",
        "class",
        "class_n",
        "class_pct",
        "profile_label",
        "severity_mean",
        "functional_score",
        "cognitive_score",
        "affective_score",
        "cardiometabolic_chronic_score",
        "functional_deterioration_ge_0_5sd_event_pct",
        "functional_or_formatted",
        "chronic_progression_ge_1_condition_event_pct",
        "chronic_or_formatted",
        "death_pct",
        "mortality_hr_formatted",
        "class_outcome_note",
    ]
    return review[[column for column in ordered if column in review.columns]].sort_values(["analysis_set", "cohort", "class"])


def class_note(row: pd.Series) -> str:
    notes = []
    label = str(row.get("profile_label", ""))
    if "high_functional" in label:
        notes.append("functional-heavy")
    if "high_affective" in label:
        notes.append("affective-heavy")
    if "high_cardiometabolic" in label or "high_cardiometabolic_chronic" in label:
        notes.append("cardiometabolic-heavy")
    if "spared_cardiometabolic" in label:
        notes.append("cardiometabolic-spared")
    for column, name in [
        ("functional_or", "functional OR>1.5"),
        ("chronic_or", "chronic OR>1.5"),
        ("mortality_hr", "mortality HR>1.5"),
    ]:
        value = row.get(column)
        if pd.notna(value) and float(value) >= 1.5:
            notes.append(name)
    return "; ".join(notes)


def aic_delta_tables(output_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    outcome = pd.read_csv(output_dir / "phase5_outcome_model_comparison.csv", low_memory=False)
    domain = pd.read_csv(output_dir / "phase5_domain_comparator_comparison.csv", low_memory=False)
    mortality = pd.read_csv(output_dir / "phase6_mortality_model_comparison.csv", low_memory=False)

    severity_rows = []
    for row in outcome.to_dict("records"):
        severity_rows.append(
            {
                "cohort": row["cohort"],
                "endpoint": ENDPOINT_LABELS.get(row["outcome"], row["outcome"]),
                "delta_aic_favors_endotype": row["delta_aic_favors_endotype"],
                "comparator": "severity_tertile",
            }
        )
    for row in mortality.to_dict("records"):
        severity_rows.append(
            {
                "cohort": row["cohort"],
                "endpoint": "Mortality",
                "delta_aic_favors_endotype": row["delta_partial_aic_severity_tertile_minus_endotype"],
                "comparator": "severity_tertile",
            }
        )

    domain_rows = []
    for row in domain.to_dict("records"):
        domain_rows.append(
            {
                "cohort": row["cohort"],
                "endpoint": ENDPOINT_LABELS.get(row["outcome"], row["outcome"]),
                "delta_aic_favors_endotype": row["delta_aic_four_domain_scores_minus_endotype"],
                "comparator": "four_domain_scores",
            }
        )
    for row in mortality.to_dict("records"):
        domain_rows.append(
            {
                "cohort": row["cohort"],
                "endpoint": "Mortality",
                "delta_aic_favors_endotype": row["delta_partial_aic_four_domain_scores_minus_endotype"],
                "comparator": "four_domain_scores",
            }
        )
    return pd.DataFrame(severity_rows), pd.DataFrame(domain_rows)


def plot_heatmap(frame: pd.DataFrame, output_base: Path, title: str) -> None:
    endpoints = ["Functional deterioration", "Chronic progression", "Mortality"]
    cohorts = [cohort for cohort in COHORT_ORDER if cohort in set(frame["cohort"])]
    matrix = pd.DataFrame(index=endpoints, columns=cohorts, dtype=float)
    for row in frame.to_dict("records"):
        matrix.loc[row["endpoint"], row["cohort"]] = float(row["delta_aic_favors_endotype"])

    max_abs = np.nanmax(np.abs(matrix.to_numpy(dtype=float)))
    max_abs = max(10.0, min(max_abs, 200.0))
    fig, ax = plt.subplots(figsize=(9.5, 3.8))
    im = ax.imshow(matrix.to_numpy(dtype=float), cmap="RdBu_r", vmin=-max_abs, vmax=max_abs, aspect="auto")
    ax.set_xticks(range(len(cohorts)))
    ax.set_xticklabels(cohorts, rotation=30, ha="right")
    ax.set_yticks(range(len(endpoints)))
    ax.set_yticklabels(endpoints)
    ax.set_title(title)
    ax.set_xlabel("Cohort")
    ax.set_ylabel("Endpoint")
    for i, endpoint in enumerate(endpoints):
        for j, cohort in enumerate(cohorts):
            value = matrix.loc[endpoint, cohort]
            if pd.notna(value):
                ax.text(j, i, f"{value:.1f}", ha="center", va="center", fontsize=8, color="black")
    cbar = fig.colorbar(im, ax=ax, shrink=0.82)
    cbar.set_label("Delta AIC: comparator minus endotype")
    fig.tight_layout()
    fig.savefig(output_base.with_suffix(".png"), dpi=220)
    fig.savefig(output_base.with_suffix(".svg"))
    plt.close(fig)


def plot_profiles(review: pd.DataFrame, output_base: Path) -> None:
    cohorts = [cohort for cohort in COHORT_ORDER if cohort in set(review["cohort"])]
    ncols = 2
    nrows = int(np.ceil(len(cohorts) / ncols))
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(11, 3.6 * nrows), sharey=True)
    axes = np.asarray(axes).reshape(-1)
    x = np.arange(len(DOMAIN_COLUMNS))
    for ax, cohort in zip(axes, cohorts):
        subset = review[review["cohort"] == cohort].sort_values("class")
        for row in subset.to_dict("records"):
            values = [row[column] for column in DOMAIN_COLUMNS]
            death = row.get("death_pct", np.nan)
            func = row.get("functional_deterioration_ge_0_5sd_event_pct", np.nan)
            label = f"C{row['class']} ({row['class_pct']:.1f}%)"
            if pd.notna(func):
                label += f" F {func:.0f}%"
            if pd.notna(death):
                label += f" M {death:.0f}%"
            ax.plot(x, values, marker="o", linewidth=1.8, label=label)
        ax.axhline(0, color="#666666", linewidth=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels(DOMAIN_LABELS, rotation=20, ha="right")
        ax.set_title(cohort)
        ax.set_ylabel("Standardized burden")
        ax.grid(axis="y", alpha=0.25)
        ax.legend(fontsize=7, frameon=False, loc="best")
    for ax in axes[len(cohorts) :]:
        ax.axis("off")
    fig.suptitle("Selected Endotype Profiles With Functional (F) And Mortality (M) Event Percent", y=0.995)
    fig.tight_layout()
    fig.savefig(output_base.with_suffix(".png"), dpi=220)
    fig.savefig(output_base.with_suffix(".svg"))
    plt.close(fig)


def markdown_table(df: pd.DataFrame, columns: list[str], limit: int | None = None) -> list[str]:
    if df.empty:
        return ["No rows."]
    if limit is not None:
        df = df.head(limit)
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in df[columns].to_dict("records"):
        values = []
        for column in columns:
            value = row[column]
            if pd.isna(value):
                values.append("")
            elif isinstance(value, float):
                values.append(str(round(value, 3)))
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return lines


def write_report(path: Path, review: pd.DataFrame, severity_delta: pd.DataFrame, domain_delta: pd.DataFrame) -> None:
    high_mortality = review.sort_values("death_pct", ascending=False).head(10)
    high_function = review.sort_values("functional_deterioration_ge_0_5sd_event_pct", ascending=False).head(10)
    severity_wide = severity_delta.pivot_table(index="endpoint", columns="cohort", values="delta_aic_favors_endotype", aggfunc="first")
    domain_wide = domain_delta.pivot_table(index="endpoint", columns="cohort", values="delta_aic_favors_endotype", aggfunc="first")
    lines = [
        "# Phase 7 Manuscript Review Assets",
        "",
        "This phase consolidates class profiles, event rates, endotype ORs/HRs, and model-comparator deltas for manuscript triage.",
        "",
        "## Highest Mortality Classes",
        "",
    ]
    lines.extend(
        markdown_table(
            high_mortality,
            ["analysis_set", "cohort", "class", "profile_label", "death_pct", "mortality_hr_formatted"],
            limit=10,
        )
    )
    lines.extend(["", "## Highest Functional-Deterioration Classes", ""])
    lines.extend(
        markdown_table(
            high_function,
            [
                "analysis_set",
                "cohort",
                "class",
                "profile_label",
                "functional_deterioration_ge_0_5sd_event_pct",
                "functional_or_formatted",
            ],
            limit=10,
        )
    )
    lines.extend(["", "## Delta AIC Versus Severity Tertile", ""])
    severity_wide = severity_wide.reset_index()
    lines.extend(markdown_table(severity_wide, list(severity_wide.columns)))
    lines.extend(["", "## Delta AIC Versus Four-Domain Scores", ""])
    domain_wide = domain_wide.reset_index()
    lines.extend(markdown_table(domain_wide, list(domain_wide.columns)))
    lines.extend(
        [
            "",
            "## Figure Files",
            "",
            "- `outputs/figures/phase7_aic_delta_vs_severity_tertile.png` and `.svg`",
            "- `outputs/figures/phase7_aic_delta_vs_four_domain_scores.png` and `.svg`",
            "- `outputs/figures/phase7_endotype_profiles_with_outcomes.png` and `.svg`",
            "",
            "## Interpretation Guardrails",
            "",
            "- Positive delta AIC means the endotype-only model improves on the named comparator.",
            "- Negative delta AIC versus four-domain scores means continuous domain scores outperform endotype-only classes.",
            "- The class review table is for clinical labeling and triage, not final causal interpretation.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    figures_dir = args.output_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    review = build_review_table(args.output_dir)
    severity_delta, domain_delta = aic_delta_tables(args.output_dir)

    review.to_csv(args.output_dir / "phase7_class_outcome_review.csv", index=False, encoding="utf-8-sig")
    severity_delta.to_csv(args.output_dir / "phase7_aic_delta_vs_severity_tertile.csv", index=False, encoding="utf-8-sig")
    domain_delta.to_csv(args.output_dir / "phase7_aic_delta_vs_four_domain_scores.csv", index=False, encoding="utf-8-sig")

    plot_heatmap(
        severity_delta,
        figures_dir / "phase7_aic_delta_vs_severity_tertile",
        "Endotype Model Delta AIC Versus Severity Tertile",
    )
    plot_heatmap(
        domain_delta,
        figures_dir / "phase7_aic_delta_vs_four_domain_scores",
        "Endotype Model Delta AIC Versus Four-Domain Scores",
    )
    plot_profiles(review, figures_dir / "phase7_endotype_profiles_with_outcomes")
    write_report(args.output_dir / "phase7_manuscript_review_report.md", review, severity_delta, domain_delta)


if __name__ == "__main__":
    main()
