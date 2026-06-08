from __future__ import annotations

import argparse
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont


RUN_DATE = "2026-06-01"

COHORT_ORDER = ["CHARLS", "ELSA", "HRS", "MHAS", "KLoSA", "SHARE", "LASI"]
MAIN_VALIDATION_COHORTS = ["CHARLS", "ELSA", "HRS", "MHAS"]
SEVEN_COHORT_DISPLAY = ["CHARLS", "ELSA", "HRS", "MHAS", "KLoSA", "SHARE", "LASI"]

DOMAIN_COLUMNS = [
    "functional_score",
    "cognitive_score",
    "affective_score",
    "cardiometabolic_chronic_score",
]
DOMAIN_LABELS = ["Functional", "Cognitive", "Affective", "Cardiometabolic"]

ENDPOINT_ORDER = [
    "Functional deterioration >= 0.5 SD",
    "Chronic progression >= 1 condition",
    "All-cause mortality",
]


def read_csv(output_dir: Path, name: str) -> pd.DataFrame:
    path = output_dir / name
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path, low_memory=False)


def fmt_int(value: object) -> str:
    if pd.isna(value):
        return "0"
    return f"{int(round(float(value))):,}"


def fmt_num(value: object, digits: int = 1) -> str:
    if pd.isna(value):
        return "NA"
    return f"{float(value):.{digits}f}"


def markdown_table(rows: list[dict[str, object]], columns: list[str]) -> str:
    if not rows:
        return "_No rows._"
    header = "| " + " | ".join(columns) + " |"
    divider = "| " + " | ".join(["---"] * len(columns)) + " |"
    body = []
    for row in rows:
        values = [str(row.get(column, "")).replace("\n", " ") for column in columns]
        body.append("| " + " | ".join(values) + " |")
    return "\n".join([header, divider, *body])


def class_number(class_id: str) -> int:
    try:
        return int(str(class_id).split("_C", 1)[1])
    except (IndexError, ValueError):
        return 999


def short_label(label: object, max_len: int = 34) -> str:
    text = str(label)
    replacements = {
        "intermediate-burden": "intermediate",
        "elevated-burden": "elevated",
        "high-burden": "high",
        "low-burden": "low",
        "cardiometabolic-dominant": "cardiomet",
        "functional-dominant": "functional",
        "affective-dominant": "affective",
        "with spared cardiometabolic": "spared cardiomet",
        "severity-aligned": "severity",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = " ".join(text.split())
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "..."


def status_from_phase15(row: pd.Series) -> tuple[str, str, str]:
    status = str(row.get("phase15_lock_status", "")).strip()
    if status == "ready_for_manual_lock":
        return "locked_for_draft", "", "Can be used in draft tables/figures after final human sign-off."
    if status == "hold_baseline_only":
        return "baseline_only_hold", "hold", "Baseline-profile-only class; do not use as outcome-validated label."
    return "review_required_not_locked", "asterisk", "Requires manual review before final label lock."


def build_locked_dictionary(queue: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for _, row in queue.iterrows():
        final_status, marker_type, rule = status_from_phase15(row)
        marker = "*" if marker_type == "asterisk" else ("hold" if marker_type == "hold" else "")
        display_suffix = ""
        if final_status == "review_required_not_locked":
            display_suffix = " [review]"
        elif final_status == "baseline_only_hold":
            display_suffix = " [baseline-only]"

        label_en = row.get("label_en_current", "")
        label_zh = row.get("label_zh_current", "")
        cls = class_number(row["class_id"])
        figure_short = f"C{cls}: {short_label(label_en)}"
        if marker == "*":
            figure_short += "*"
        elif marker == "hold":
            figure_short += " [hold]"

        rows.append(
            {
                "cohort": row["cohort"],
                "class_id": row["class_id"],
                "class": cls,
                "label_en_final": label_en,
                "label_zh_final": label_zh,
                "label_en_display": f"{label_en}{display_suffix}",
                "label_zh_display": f"{label_zh}{display_suffix}",
                "figure_label_short": figure_short,
                "phase16_label_status": final_status,
                "phase16_marker": marker,
                "phase16_lock_rule": rule,
                "phase15_review_reason": row.get("phase15_review_reason", ""),
                "phase14_stability_flag_count": row.get("phase14_stability_flag_count", 0),
                "phase14_flagged_outcomes": row.get("phase14_flagged_outcomes", ""),
                "phase14_flagged_adjustments": row.get("phase14_flagged_adjustments", ""),
                "phase14_flag_reasons": row.get("phase14_flag_reasons", ""),
            }
        )
    out = pd.DataFrame(rows)
    out["cohort_order"] = out["cohort"].map({cohort: i for i, cohort in enumerate(COHORT_ORDER)}).fillna(99)
    return out.sort_values(["cohort_order", "class"]).drop(columns=["cohort_order"]).reset_index(drop=True)


def build_table2_locked(table2: pd.DataFrame, dictionary: pd.DataFrame) -> pd.DataFrame:
    merged = table2.merge(
        dictionary[
            [
                "cohort",
                "class_id",
                "label_en_final",
                "label_zh_final",
                "label_en_display",
                "label_zh_display",
                "figure_label_short",
                "phase16_label_status",
                "phase16_marker",
                "phase16_lock_rule",
                "phase15_review_reason",
                "phase14_stability_flag_count",
            ]
        ],
        on=["cohort", "class_id"],
        how="left",
    )
    first_cols = [
        "analysis_set",
        "analysis_tier",
        "cohort",
        "class_id",
        "class",
        "class_n",
        "class_pct",
        "label_en_final",
        "label_zh_final",
        "label_en_display",
        "label_zh_display",
        "phase16_label_status",
        "phase15_review_reason",
        "label_confidence",
        "high_domains",
        "spared_domains",
        "outcome_flags",
    ]
    remaining = [column for column in merged.columns if column not in first_cols]
    return merged[[column for column in first_cols if column in merged.columns] + remaining]


def build_figure_label_map(table2_locked: pd.DataFrame, display: pd.DataFrame) -> pd.DataFrame:
    policy = display[["cohort", "phase15_display_recommendation", "figure1_policy", "condition_for_main_display"]]
    rows = table2_locked.merge(policy, on="cohort", how="left")
    rows["phase16_figure1_main_use"] = rows["cohort"].isin(MAIN_VALIDATION_COHORTS).astype(int)
    rows["phase16_figure1_sensitivity_use"] = rows["cohort"].isin(SEVEN_COHORT_DISPLAY).astype(int)
    keep = [
        "cohort",
        "class_id",
        "class",
        "figure_label_short",
        "label_en_display",
        "phase16_label_status",
        "phase16_marker",
        "phase15_display_recommendation",
        "figure1_policy",
        "phase16_figure1_main_use",
        "phase16_figure1_sensitivity_use",
        "functional_deterioration_ge_0_5sd_event_pct",
        "death_pct",
    ]
    return rows[[column for column in keep if column in rows.columns]]


def plot_profiles(table2_locked: pd.DataFrame, cohorts: list[str], title: str, output_base: Path) -> tuple[Path, Path]:
    subset = table2_locked[table2_locked["cohort"].isin(cohorts)].copy()
    subset["cohort_order"] = subset["cohort"].map({cohort: i for i, cohort in enumerate(cohorts)}).fillna(99)
    subset = subset.sort_values(["cohort_order", "class"])
    ncols = 2
    nrows = int(math.ceil(len(cohorts) / ncols))
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(13, 3.7 * nrows), sharey=True)
    axes = np.asarray(axes).reshape(-1)
    x = np.arange(len(DOMAIN_COLUMNS))
    colors = plt.cm.tab10(np.linspace(0, 1, 10))

    for ax, cohort in zip(axes, cohorts):
        cdata = subset[subset["cohort"] == cohort].sort_values("class")
        for idx, row in enumerate(cdata.to_dict("records")):
            values = [row.get(column, np.nan) for column in DOMAIN_COLUMNS]
            label = str(row.get("figure_label_short", f"C{row.get('class', '')}"))
            pct = row.get("class_pct", np.nan)
            if pd.notna(pct):
                label += f" ({float(pct):.0f}%)"
            func = row.get("functional_deterioration_ge_0_5sd_event_pct", np.nan)
            death = row.get("death_pct", np.nan)
            if pd.notna(func):
                label += f" F{float(func):.0f}%"
            if pd.notna(death):
                label += f" M{float(death):.0f}%"
            ax.plot(x, values, marker="o", linewidth=1.8, color=colors[idx % len(colors)], label=label)
        ax.axhline(0, color="#666666", linewidth=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels(DOMAIN_LABELS, rotation=20, ha="right")
        ax.set_title(cohort)
        ax.set_ylabel("Standardized burden")
        ax.grid(axis="y", alpha=0.25)
        ax.legend(fontsize=6.3, frameon=False, loc="best")

    for ax in axes[len(cohorts) :]:
        ax.axis("off")

    fig.suptitle(title, y=0.995)
    fig.text(
        0.01,
        0.005,
        "* review before final label lock; [hold] baseline-only class. F/M are functional deterioration and mortality event percentages.",
        fontsize=8,
    )
    fig.tight_layout(rect=(0, 0.02, 1, 0.985))
    png_path = output_base.with_suffix(".png")
    pdf_path = output_base.with_suffix(".pdf")
    fig.savefig(png_path, dpi=240)
    fig.savefig(pdf_path)
    plt.close(fig)
    return png_path, pdf_path


def plot_heatmap(table3: pd.DataFrame, cohorts: list[str], metric: str, title: str, output_base: Path) -> tuple[Path, Path]:
    frame = table3[table3["cohort"].isin(cohorts)].copy()
    matrix = (
        frame.pivot_table(index="endpoint", columns="cohort", values=metric, aggfunc="first")
        .reindex(index=ENDPOINT_ORDER, columns=cohorts)
    )
    values = matrix.to_numpy(dtype=float)
    max_abs = np.nanmax(np.abs(values)) if np.isfinite(values).any() else 1.0
    max_abs = max(10.0, min(float(max_abs), 220.0))

    fig, ax = plt.subplots(figsize=(max(7.0, 1.1 * len(cohorts) + 2.8), 3.5))
    im = ax.imshow(values, cmap="RdBu_r", vmin=-max_abs, vmax=max_abs, aspect="auto")
    ax.set_xticks(range(len(cohorts)))
    ax.set_xticklabels(cohorts, rotation=30, ha="right")
    ax.set_yticks(range(len(ENDPOINT_ORDER)))
    ax.set_yticklabels(["Functional", "Chronic", "Mortality"])
    ax.set_title(title)
    for i in range(len(ENDPOINT_ORDER)):
        for j in range(len(cohorts)):
            value = matrix.iloc[i, j]
            label = "NA" if pd.isna(value) else f"{float(value):.1f}"
            ax.text(j, i, label, ha="center", va="center", fontsize=8, color="black")
    cbar = fig.colorbar(im, ax=ax, shrink=0.82)
    cbar.set_label("Delta AIC: comparator minus endotype")
    fig.tight_layout()
    png_path = output_base.with_suffix(".png")
    pdf_path = output_base.with_suffix(".pdf")
    fig.savefig(png_path, dpi=240)
    fig.savefig(pdf_path)
    plt.close(fig)
    return png_path, pdf_path


def load_font(size: int = 42) -> ImageFont.ImageFont:
    for path in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    ]:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def paste_panel(
    canvas: Image.Image,
    image: Image.Image,
    y: int,
    label: str,
    common_width: int,
    margin: int,
    label_height: int,
) -> int:
    draw = ImageDraw.Draw(canvas)
    font = load_font()
    draw.text((margin, y), label, fill=(0, 0, 0), font=font)
    y += label_height
    if image.width != common_width:
        height = int(round(image.height * common_width / image.width))
        image = image.resize((common_width, height), Image.Resampling.LANCZOS)
    canvas.paste(image, (margin, y))
    return y + image.height + margin


def combine_figure(profile_png: Path, severity_png: Path, domains_png: Path, output_base: Path) -> tuple[Path, Path]:
    images = [Image.open(path).convert("RGB") for path in [profile_png, severity_png, domains_png]]
    common_width = max(image.width for image in images)
    margin = 72
    label_height = 62
    scaled_heights = [
        image.height if image.width == common_width else int(round(image.height * common_width / image.width))
        for image in images
    ]
    canvas = Image.new("RGB", (common_width + margin * 2, margin + sum(h + label_height + margin for h in scaled_heights)), "white")
    y = margin
    for label, image in zip(
        [
            "A. Endotype profiles with Phase 16 label status",
            "B. Delta AIC versus severity tertiles",
            "C. Delta AIC versus four-domain continuous scores",
        ],
        images,
    ):
        y = paste_panel(canvas, image, y, label, common_width, margin, label_height)
    png_path = output_base.with_suffix(".png")
    pdf_path = output_base.with_suffix(".pdf")
    canvas.save(png_path, dpi=(300, 300))
    canvas.save(pdf_path, "PDF", resolution=300.0)
    return png_path, pdf_path


def endpoint_summary(table3: pd.DataFrame, endpoint: str, cohorts: list[str] | None = None) -> dict[str, object]:
    subset = table3[table3["endpoint"].eq(endpoint)].copy()
    if cohorts is not None:
        subset = subset[subset["cohort"].isin(cohorts)]
    return {
        "cohorts": subset["cohort"].nunique(),
        "participants": subset["n_endotype"].fillna(0).sum(),
        "events": subset["events_endotype"].fillna(0).sum(),
        "severity_pattern": subset["endotype_vs_severity_tertile"].value_counts().to_dict(),
        "domain_pattern": subset["endotype_vs_four_domain_scores"].value_counts().to_dict(),
    }


def counts_text(counts: dict[str, int]) -> str:
    if not counts:
        return "no rows"
    return ", ".join(f"{key}: {value}" for key, value in sorted(counts.items()))


def write_results_draft(
    path: Path,
    table1: pd.DataFrame,
    table2_locked: pd.DataFrame,
    table3: pd.DataFrame,
    dictionary: pd.DataFrame,
    supplement: pd.DataFrame,
) -> None:
    baseline_total = table1["baseline_women_age50plus_n"].fillna(0).sum()
    strict_endotype_n = table1.loc[table1["analysis_tier"].eq("strict_primary"), "selected_endotype_n"].fillna(0).sum()
    main_endotype_n = table1.loc[table1["cohort"].isin(MAIN_VALIDATION_COHORTS), "selected_endotype_n"].fillna(0).sum()
    bridge_endotype_n = table1.loc[table1["analysis_tier"].eq("bridge_sensitivity"), "selected_endotype_n"].fillna(0).sum()

    label_counts = dictionary["phase16_label_status"].value_counts().to_dict()
    functional = endpoint_summary(table3, "Functional deterioration >= 0.5 SD")
    functional_main = endpoint_summary(table3, "Functional deterioration >= 0.5 SD", MAIN_VALIDATION_COHORTS)
    chronic = endpoint_summary(table3, "Chronic progression >= 1 condition")
    mortality = endpoint_summary(table3, "All-cause mortality")

    s2_flags = supplement[supplement["table_id"].eq("S2")]
    flagged_classes = ", ".join(sorted(s2_flags["class_id"].dropna().unique())) if not s2_flags.empty else "none"

    text = [
        "# Results Draft",
        "",
        "This draft uses Phase 16 locked-for-draft labels where available and keeps review-required labels visibly marked.",
        "",
        "## Study Sample",
        "",
        (
            f"The seven cleaned aging cohorts included {fmt_int(baseline_total)} women aged 50 years or older at the "
            f"eligible baseline screen. Strict-primary endotype construction contributed {fmt_int(strict_endotype_n)} "
            f"selected class assignments, including {fmt_int(main_endotype_n)} assignments in the four main validation "
            "cohorts (CHARLS, ELSA, HRS, and MHAS). KLoSA and SHARE contributed "
            f"{fmt_int(bridge_endotype_n)} bridge-sensitivity assignments, while LASI remained baseline-profile only "
            "because longitudinal outcome validation is not available in the current cleaned CSV pass."
        ),
        "",
        "Table callout: Table 1.",
        "",
        "## Endotype Structure And Label Status",
        "",
        (
            f"The selected cohort-specific solutions yielded {len(table2_locked)} classes. Phase 16 marks "
            f"{int(label_counts.get('locked_for_draft', 0))} labels as locked for draft use, "
            f"{int(label_counts.get('review_required_not_locked', 0))} labels as requiring manual review, and "
            f"{int(label_counts.get('baseline_only_hold', 0))} LASI labels as baseline-only holds."
        ),
        "",
        (
            "The profiles were not reducible to a single low-to-high severity gradient. Draft labels include "
            "functional-dominant, cardiometabolic-dominant, affective-dominant, spared-cardiometabolic, and "
            "severity-aligned patterns. Labels marked with an asterisk in Figure 1 require manual review before "
            "they should be used as final clinical names."
        ),
        "",
        "Table/Figure callout: Table 2 and Figure 1A.",
        "",
        "## Functional Deterioration",
        "",
        (
            f"Functional deterioration validation was available in {int(functional['cohorts'])} cohorts, with "
            f"{fmt_int(functional['participants'])} participants and {fmt_int(functional['events'])} events. In the "
            f"four main validation cohorts, the corresponding analytic set included {fmt_int(functional_main['participants'])} "
            f"participants and {fmt_int(functional_main['events'])} events."
        ),
        "",
        (
            f"Against severity tertiles, the functional model-comparison pattern was "
            f"{counts_text(functional['severity_pattern'])}. Four-domain continuous-score models were favored in "
            f"{counts_text(functional['domain_pattern'])}, so functional results support endpoint-specific clinical "
            "heterogeneity rather than universal endotype prediction superiority."
        ),
        "",
        "Table/Figure callout: Table 3 and Figure 1B-C.",
        "",
        "## Chronic Progression",
        "",
        (
            f"Chronic progression validation included {int(chronic['cohorts'])} cohorts and "
            f"{fmt_int(chronic['events'])} events. The endotype-versus-severity pattern was "
            f"{counts_text(chronic['severity_pattern'])}, but four-domain continuous scores remained favored in "
            f"{counts_text(chronic['domain_pattern'])}."
        ),
        "",
        "## Mortality",
        "",
        (
            f"Mortality validation included {int(mortality['cohorts'])} cohorts and {fmt_int(mortality['events'])} deaths. "
            f"Against severity tertiles, the mortality comparison pattern was {counts_text(mortality['severity_pattern'])}."
        ),
        "",
        (
            "Mortality should remain a secondary validation endpoint. Prior PH diagnostics and piecewise sensitivity "
            "identified time-drift for selected class terms, and Phase 14 covariate sensitivity added further review "
            f"flags for {flagged_classes}."
        ),
        "",
        "## Covariate Sensitivity And Display Guardrails",
        "",
        (
            "Phase 14 covariate-sensitivity models are best reported as robustness checks. They support transparent "
            "label review and sensitivity reporting, but they should not replace the age-adjusted primary validation "
            "screen. Figure 1 should default to the main validation cohorts, with KLoSA and SHARE in sensitivity or "
            "supplement display unless bridge-sensitivity footnotes are explicit."
        ),
        "",
        "## Comparator Guardrail",
        "",
        (
            "The central claim should remain conservative: endotype classes provide compact, interpretable, "
            "cohort-specific multidomain profiles with endpoint-specific validation signals. The manuscript should "
            "not claim that endotype membership is a universally superior prediction variable compared with the "
            "continuous source-domain scores."
        ),
    ]
    path.write_text("\n".join(text) + "\n", encoding="utf-8")


def write_report(
    path: Path,
    dictionary: pd.DataFrame,
    table2_locked: pd.DataFrame,
    label_map: pd.DataFrame,
    main_figure: tuple[Path, Path],
    sensitivity_figure: tuple[Path, Path],
) -> None:
    counts = dictionary["phase16_label_status"].value_counts().to_dict()
    review = dictionary[dictionary["phase16_label_status"].eq("review_required_not_locked")]
    hold = dictionary[dictionary["phase16_label_status"].eq("baseline_only_hold")]
    text = [
        "# Phase 16 Label Lock And Manuscript Draft Report",
        "",
        f"Run date: {RUN_DATE}.",
        "",
        "## Outputs",
        "",
        "- `outputs/phase16_locked_label_dictionary.csv`",
        "- `outputs/phase16_table2_locked_labels.csv`",
        "- `outputs/phase16_figure1_label_map.csv`",
        "- `outputs/phase16_results_draft.md`",
        "- `manuscript/results_draft.md`",
        "- `outputs/figures/phase16_figure1_main_validation.png` and `.pdf`",
        "- `outputs/figures/phase16_figure1_seven_cohort_sensitivity.png` and `.pdf`",
        "",
        "## Label Status",
        "",
        f"- Locked for draft: {int(counts.get('locked_for_draft', 0))}.",
        f"- Review required, not locked: {int(counts.get('review_required_not_locked', 0))}.",
        f"- Baseline-only hold: {int(counts.get('baseline_only_hold', 0))}.",
        "",
        "## Review-Required Labels",
        "",
        markdown_table(
            review[
                [
                    "cohort",
                    "class_id",
                    "label_en_final",
                    "phase15_review_reason",
                    "phase14_stability_flag_count",
                ]
            ].to_dict("records"),
            ["cohort", "class_id", "label_en_final", "phase15_review_reason", "phase14_stability_flag_count"],
        ),
        "",
        "## Baseline-Only Hold Labels",
        "",
        markdown_table(
            hold[["cohort", "class_id", "label_en_final", "phase16_lock_rule"]].to_dict("records"),
            ["cohort", "class_id", "label_en_final", "phase16_lock_rule"],
        ),
        "",
        "## Figure Files",
        "",
        f"- Main validation Figure 1: `{main_figure[0].as_posix()}` and `{main_figure[1].as_posix()}`",
        f"- Seven-cohort sensitivity Figure 1: `{sensitivity_figure[0].as_posix()}` and `{sensitivity_figure[1].as_posix()}`",
        "",
        "## Guardrail",
        "",
        "Rows marked `review_required_not_locked` are deliberately carried forward with visible markers. They still need human review before final manuscript submission.",
    ]
    path.write_text("\n".join(text) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    parser.add_argument("--manuscript-dir", type=Path, default=Path("manuscript"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir: Path = args.output_dir
    manuscript_dir: Path = args.manuscript_dir
    figures_dir = output_dir / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)
    manuscript_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    table1 = read_csv(output_dir, "phase11_table1_cohort_readiness.csv")
    table2 = read_csv(output_dir, "phase11_table2_class_profiles_labels.csv")
    table3 = read_csv(output_dir, "phase11_table3_outcome_validation_summary.csv")
    queue = read_csv(output_dir, "phase15_label_lock_queue.csv")
    display = read_csv(output_dir, "phase15_display_policy_recommendation.csv")
    supplement = read_csv(output_dir, "phase15_supplement_table_shell.csv")

    dictionary = build_locked_dictionary(queue)
    table2_locked = build_table2_locked(table2, dictionary)
    label_map = build_figure_label_map(table2_locked, display)

    dictionary.to_csv(output_dir / "phase16_locked_label_dictionary.csv", index=False)
    table2_locked.to_csv(output_dir / "phase16_table2_locked_labels.csv", index=False)
    label_map.to_csv(output_dir / "phase16_figure1_label_map.csv", index=False)

    main_profile, _ = plot_profiles(
        table2_locked,
        MAIN_VALIDATION_COHORTS,
        "Main Validation Cohorts: Endotype Profiles With Phase 16 Labels",
        figures_dir / "phase16_profile_main_validation",
    )
    main_severity, _ = plot_heatmap(
        table3,
        MAIN_VALIDATION_COHORTS,
        "delta_aic_severity_tertile_minus_endotype",
        "Main Validation Cohorts: Endotype vs Severity Tertiles",
        figures_dir / "phase16_heatmap_main_vs_severity",
    )
    main_domains, _ = plot_heatmap(
        table3,
        MAIN_VALIDATION_COHORTS,
        "delta_aic_four_domain_scores_minus_endotype",
        "Main Validation Cohorts: Endotype vs Four-Domain Scores",
        figures_dir / "phase16_heatmap_main_vs_four_domain_scores",
    )
    main_figure = combine_figure(
        main_profile,
        main_severity,
        main_domains,
        figures_dir / "phase16_figure1_main_validation",
    )

    sensitivity_profile, _ = plot_profiles(
        table2_locked,
        SEVEN_COHORT_DISPLAY,
        "Seven-Cohort Sensitivity Display: Endotype Profiles With Phase 16 Labels",
        figures_dir / "phase16_profile_seven_cohort_sensitivity",
    )
    sensitivity_severity, _ = plot_heatmap(
        table3,
        SEVEN_COHORT_DISPLAY,
        "delta_aic_severity_tertile_minus_endotype",
        "Seven-Cohort Display: Endotype vs Severity Tertiles",
        figures_dir / "phase16_heatmap_seven_vs_severity",
    )
    sensitivity_domains, _ = plot_heatmap(
        table3,
        SEVEN_COHORT_DISPLAY,
        "delta_aic_four_domain_scores_minus_endotype",
        "Seven-Cohort Display: Endotype vs Four-Domain Scores",
        figures_dir / "phase16_heatmap_seven_vs_four_domain_scores",
    )
    sensitivity_figure = combine_figure(
        sensitivity_profile,
        sensitivity_severity,
        sensitivity_domains,
        figures_dir / "phase16_figure1_seven_cohort_sensitivity",
    )

    write_results_draft(output_dir / "phase16_results_draft.md", table1, table2_locked, table3, dictionary, supplement)
    write_results_draft(manuscript_dir / "results_draft.md", table1, table2_locked, table3, dictionary, supplement)
    write_report(
        output_dir / "phase16_label_lock_and_manuscript_report.md",
        dictionary,
        table2_locked,
        label_map,
        main_figure,
        sensitivity_figure,
    )


if __name__ == "__main__":
    main()
