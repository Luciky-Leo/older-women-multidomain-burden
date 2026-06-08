from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from build_phase3_domain_scores import COHORT_CONFIG, find_clean_csv, read_header_map


MISSING_STRINGS = {"", "NA", "NAN", "NULL", ".", "-9", "-8", "-7", "-1"}


@dataclass(frozen=True)
class CovariateSpec:
    concept: str
    role: str
    preferred: tuple[str, ...]
    pattern: re.Pattern[str]
    min_nonmissing_pct: float = 70.0


COVARIATE_SPECS = [
    CovariateSpec(
        concept="education",
        role="minimal_core",
        preferred=("raeducl", "r1raeducl", "raedyrs", "r1raedyrs", "education", "raeduc_c", "raeduc_e", "raeduc_k", "raeduc_l"),
        pattern=re.compile(r"(educ|educl|edyrs|school|schl|raeduc)", re.IGNORECASE),
    ),
    CovariateSpec(
        concept="marital_status",
        role="minimal_core",
        preferred=("mstath", "r1mstath", "marry"),
        pattern=re.compile(r"(marit|marry|mstat|partner|spouse|couple)", re.IGNORECASE),
    ),
    CovariateSpec(
        concept="rural_region",
        role="expanded_core",
        preferred=("rural", "hrural", "hh1rural", "rural2", "region", "region_k", "province", "country", "rabcountry", "hukou", "r1city"),
        pattern=re.compile(r"(rural|urban|region|province|city|country|area|resid|hukou|rabcountry)", re.IGNORECASE),
    ),
    CovariateSpec(
        concept="smoking",
        role="minimal_core",
        preferred=("smoken", "r1smoken", "smokef", "r1smokef", "smokev", "r1smokev"),
        pattern=re.compile(r"(smok|smoke|cigar|tobac)", re.IGNORECASE),
    ),
    CovariateSpec(
        concept="drinking",
        role="minimal_core",
        preferred=("drink", "r1drink3m", "drink3m", "drinkev", "r1drinkev", "drinkl", "drinkb", "r1drinkb", "drinkd", "drinkn"),
        pattern=re.compile(r"(drink|alco|beer|wine|liquor)", re.IGNORECASE),
    ),
    CovariateSpec(
        concept="physical_activity",
        role="expanded_core",
        preferred=(
            "vgactx",
            "mdactx",
            "ltactx",
            "r1vgactx",
            "r1mdactx",
            "r1ltactx",
            "vgact_c",
            "mdact_c",
            "ltact_c",
            "vgactx_c",
            "mdactx_c",
            "ltactx_c",
            "vgactx_e",
            "mdactx_e",
            "ltactx_e",
        ),
        pattern=re.compile(r"(vgact|mdact|ltact|physical|exercise|sport|activ)", re.IGNORECASE),
    ),
    CovariateSpec(
        concept="bmi",
        role="optional_biometric",
        preferred=("mbmi", "r1mbmi", "bmi", "pmbmi"),
        pattern=re.compile(r"(^bmi$|mbmi|pmbmi)", re.IGNORECASE),
    ),
]

CORE_MINIMAL = {"education", "marital_status", "smoking", "drinking"}
CORE_EXPANDED = CORE_MINIMAL | {"rural_region", "physical_activity"}


def normalize_wave(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]
    return text


def normalize_missing(series: pd.Series) -> pd.Series:
    text = series.astype("string").str.strip()
    return text.mask(text.str.upper().isin(MISSING_STRINGS))


def safe_pct(numerator: int | float, denominator: int | float) -> float:
    if denominator == 0 or pd.isna(denominator):
        return float("nan")
    return round(float(numerator) / float(denominator) * 100, 2)


def join_values(values: list[str], limit: int = 40) -> str:
    return ";".join(values[:limit])


def read_assignments(path: Path) -> pd.DataFrame:
    usecols = [
        "analysis_set",
        "analysis_tier",
        "cohort",
        "participant_id",
        "wave",
        "age",
        "severity_score",
        "endotype_class",
        "endotype_posterior",
    ]
    assignments = pd.read_csv(path, usecols=lambda col: col in usecols, dtype={"participant_id": str, "wave": str}, low_memory=False)
    assignments["participant_id"] = normalize_missing(assignments["participant_id"])
    assignments["wave"] = assignments["wave"].map(normalize_wave)
    assignments["endotype_class"] = assignments["endotype_class"].astype(str)
    return assignments


def candidate_variables(header_map: dict[str, str], spec: CovariateSpec) -> list[str]:
    variables = sorted(header_map)
    hits = [var for var in variables if spec.pattern.search(var)]
    ordered = [var for var in spec.preferred if var in header_map]
    for var in hits:
        if var not in ordered:
            ordered.append(var)
    return ordered


def read_baseline_covariates(data_root: Path, cohort: str, variables: list[str]) -> pd.DataFrame:
    config = COHORT_CONFIG[cohort]
    path = find_clean_csv(data_root, str(config["file"]))
    header_map = read_header_map(path)
    id_col = str(config["id"])
    wave_col = str(config["wave"])
    wanted = [id_col, *variables]
    if wave_col:
        wanted.append(wave_col)
    available = {var: header_map[var] for var in wanted if var in header_map}
    if id_col not in available:
        raise KeyError(f"{cohort} missing id column {id_col}")
    frame = pd.read_csv(
        path,
        usecols=list(available.values()),
        dtype=str,
        encoding="utf-8-sig",
        low_memory=False,
    ).rename(columns={raw: var for var, raw in available.items()})
    frame = frame.rename(columns={id_col: "participant_id"})
    frame["participant_id"] = normalize_missing(frame["participant_id"])
    if wave_col:
        frame = frame.rename(columns={wave_col: "wave"})
        frame["wave"] = frame["wave"].map(normalize_wave)
    else:
        frame["wave"] = "all_rows_no_wave"
    for column in variables:
        if column in frame.columns:
            frame[column] = normalize_missing(frame[column])
    return frame.drop_duplicates(["participant_id", "wave"])


def concept_stats(merged: pd.DataFrame, variables: list[str], spec: CovariateSpec) -> pd.DataFrame:
    rows = []
    denominator = len(merged)
    for rank, variable in enumerate(variables, start=1):
        if variable not in merged.columns:
            continue
        values = normalize_missing(merged[variable])
        nonmissing = int(values.notna().sum())
        sample_values = [str(value) for value in values.dropna().drop_duplicates().head(8)]
        rows.append(
            {
                "concept": spec.concept,
                "concept_role": spec.role,
                "variable": variable,
                "preference_rank": rank,
                "selected_assignment_n": denominator,
                "nonmissing_n": nonmissing,
                "nonmissing_pct": safe_pct(nonmissing, denominator),
                "sample_values": "|".join(sample_values),
            }
        )
    return pd.DataFrame(rows)


def select_variable(stats: pd.DataFrame, spec: CovariateSpec) -> tuple[str, float, int, str]:
    if stats.empty:
        return "", float("nan"), 0, "no_candidate"
    ready = stats[stats["nonmissing_pct"] >= spec.min_nonmissing_pct].copy()
    if ready.empty:
        best = stats.sort_values(["nonmissing_pct", "preference_rank"], ascending=[False, True]).iloc[0]
        return str(best["variable"]), float(best["nonmissing_pct"]), int(best["nonmissing_n"]), "candidate_below_threshold"
    best = ready.sort_values(["preference_rank", "nonmissing_pct"], ascending=[True, False]).iloc[0]
    return str(best["variable"]), float(best["nonmissing_pct"]), int(best["nonmissing_n"]), "ready"


def build_inventory(data_root: Path, output_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    assignments = read_assignments(output_dir / "phase4_best_model_assignments.csv")
    inventory_rows = []
    participant_frames = []

    for cohort, cohort_assignments in assignments.groupby("cohort", sort=False):
        cohort_assignments = cohort_assignments.reset_index(drop=True)
        path = find_clean_csv(data_root, str(COHORT_CONFIG[cohort]["file"]))
        header_map = read_header_map(path)
        concept_to_candidates = {
            spec.concept: candidate_variables(header_map, spec)
            for spec in COVARIATE_SPECS
        }
        all_candidates = sorted({var for variables in concept_to_candidates.values() for var in variables})
        baseline_covariates = read_baseline_covariates(data_root, cohort, all_candidates)
        cohort_merged = cohort_assignments.merge(baseline_covariates, on=["participant_id", "wave"], how="left")

        participant_frame = cohort_assignments.copy()
        participant_frame["covariate_merge_available"] = (
            cohort_merged[all_candidates].notna().any(axis=1).astype(int).to_numpy() if all_candidates else 0
        )

        for spec in COVARIATE_SPECS:
            candidates = concept_to_candidates[spec.concept]
            stats = concept_stats(cohort_merged, candidates, spec)
            if not stats.empty:
                stats["cohort"] = cohort
                stats["clean_csv"] = str(path)
                stats["all_candidates"] = join_values(candidates)
                selected, pct, n, status = select_variable(stats, spec)
            else:
                selected, pct, n, status = "", float("nan"), 0, "no_candidate"
                stats = pd.DataFrame(
                    [
                        {
                            "cohort": cohort,
                            "clean_csv": str(path),
                            "concept": spec.concept,
                            "concept_role": spec.role,
                            "variable": "",
                            "preference_rank": pd.NA,
                            "selected_assignment_n": len(cohort_merged),
                            "nonmissing_n": 0,
                            "nonmissing_pct": float("nan"),
                            "sample_values": "",
                            "all_candidates": "",
                        }
                    ]
                )
            stats["selected_variable"] = selected
            stats["selected_nonmissing_n"] = n
            stats["selected_nonmissing_pct"] = pct
            stats["selected_status"] = status
            inventory_rows.append(stats)

            raw_column = f"cov_{spec.concept}_raw"
            source_column = f"cov_{spec.concept}_source"
            if selected and selected in cohort_merged.columns:
                participant_frame[raw_column] = normalize_missing(cohort_merged[selected]).to_numpy()
                participant_frame[source_column] = selected
            else:
                participant_frame[raw_column] = pd.NA
                participant_frame[source_column] = ""

        participant_frames.append(participant_frame)

    inventory = pd.concat(inventory_rows, ignore_index=True, sort=False)
    participant_screen = pd.concat(participant_frames, ignore_index=True, sort=False)
    summary = build_readiness_summary(inventory)
    return inventory, summary, participant_screen


def build_readiness_summary(inventory: pd.DataFrame) -> pd.DataFrame:
    selected = (
        inventory.sort_values(["cohort", "concept", "selected_status", "preference_rank"])
        .drop_duplicates(["cohort", "concept"])
        .copy()
    )
    rows = []
    for cohort, frame in selected.groupby("cohort", sort=False):
        concept_status = {
            row["concept"]: {
                "status": row["selected_status"],
                "variable": row["selected_variable"],
                "pct": row["selected_nonmissing_pct"],
            }
            for _, row in frame.iterrows()
        }
        minimal_ready = all(concept_status.get(concept, {}).get("status") == "ready" for concept in CORE_MINIMAL)
        expanded_ready = all(concept_status.get(concept, {}).get("status") == "ready" for concept in CORE_EXPANDED)
        optional_bmi_ready = concept_status.get("bmi", {}).get("status") == "ready"
        missing_minimal = [concept for concept in CORE_MINIMAL if concept_status.get(concept, {}).get("status") != "ready"]
        missing_expanded = [concept for concept in CORE_EXPANDED if concept_status.get(concept, {}).get("status") != "ready"]
        if expanded_ready:
            recommendation = "expanded_core_covariate_sensitivity_ready"
        elif minimal_ready:
            recommendation = "minimal_core_ready_physical_or_region_limited"
        else:
            recommendation = "covariate_sensitivity_limited"
        row = {
            "cohort": cohort,
            "minimal_core_ready": int(minimal_ready),
            "expanded_core_ready": int(expanded_ready),
            "optional_bmi_ready": int(optional_bmi_ready),
            "missing_minimal_core": ";".join(missing_minimal),
            "missing_expanded_core": ";".join(missing_expanded),
            "recommendation": recommendation,
        }
        for concept in [spec.concept for spec in COVARIATE_SPECS]:
            row[f"{concept}_variable"] = concept_status.get(concept, {}).get("variable", "")
            row[f"{concept}_pct"] = concept_status.get(concept, {}).get("pct", float("nan"))
            row[f"{concept}_status"] = concept_status.get(concept, {}).get("status", "no_candidate")
        rows.append(row)
    order = {"CHARLS": 1, "ELSA": 2, "HRS": 3, "LASI": 4, "MHAS": 5, "KLoSA": 6, "SHARE": 7}
    out = pd.DataFrame(rows)
    out["cohort_order"] = out["cohort"].map(order).fillna(99)
    return out.sort_values("cohort_order").drop(columns=["cohort_order"]).reset_index(drop=True)


def build_label_display_policy(output_dir: Path) -> pd.DataFrame:
    labels = pd.read_csv(output_dir / "phase12_label_dictionary_draft.csv", low_memory=False)
    table1 = pd.read_csv(output_dir / "phase11_table1_cohort_readiness.csv", low_memory=False)
    role_map = table1.set_index("cohort")["manuscript_role"].to_dict()
    rows = []
    for _, row in labels.iterrows():
        cohort = row["cohort"]
        role = role_map.get(cohort, "")
        if role == "primary_validation":
            display_policy = "main_results"
        elif role == "baseline_profile_only_current_csv":
            display_policy = "baseline_profile_table_only"
        else:
            display_policy = "sensitivity_or_supplement"
        if row["suggested_label_status"] == "ready_for_manual_lock":
            label_action = "lock_candidate"
        elif row["suggested_label_status"] == "baseline_only_candidate":
            label_action = "hold_until_followup_available"
        else:
            label_action = "manual_review_before_lock"
        rows.append(
            {
                "cohort": cohort,
                "class_id": row["class_id"],
                "analysis_tier": row["analysis_tier"],
                "manuscript_role": role,
                "display_policy": display_policy,
                "label_action": label_action,
                "label_en_current": row["label_en_current"],
                "label_zh_current": row["label_zh_current"],
                "label_confidence": row["label_confidence"],
                "manual_review_reason": row.get("manual_review_reason", ""),
            }
        )
    return pd.DataFrame(rows)


def markdown_table(df: pd.DataFrame, columns: list[str]) -> list[str]:
    if df.empty:
        return ["No rows."]
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in df[columns].to_dict("records"):
        values = []
        for column in columns:
            value = row[column]
            if pd.isna(value):
                values.append("")
            elif isinstance(value, float):
                values.append(f"{value:.2f}")
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return lines


def write_report(output_dir: Path, summary: pd.DataFrame, policy: pd.DataFrame) -> None:
    minimal_ready = int(summary["minimal_core_ready"].sum())
    expanded_ready = int(summary["expanded_core_ready"].sum())
    bmi_ready = int(summary["optional_bmi_ready"].sum())
    lock_candidates = int((policy["label_action"] == "lock_candidate").sum())
    manual_review = int((policy["label_action"] == "manual_review_before_lock").sum())
    hold = int((policy["label_action"] == "hold_until_followup_available").sum())

    lines = [
        "# Phase 13 Covariate Inventory And Display Policy",
        "",
        "This phase screens baseline covariates for sensitivity modeling and converts the Phase 12 label queue into a display policy.",
        "",
        "## Covariate Readiness",
        "",
        f"- Minimal core covariate readiness: {minimal_ready} cohorts.",
        f"- Expanded core covariate readiness: {expanded_ready} cohorts.",
        f"- Optional BMI readiness: {bmi_ready} cohorts.",
        "",
    ]
    columns = [
        "cohort",
        "minimal_core_ready",
        "expanded_core_ready",
        "optional_bmi_ready",
        "education_variable",
        "marital_status_variable",
        "rural_region_variable",
        "smoking_variable",
        "drinking_variable",
        "physical_activity_variable",
        "bmi_variable",
        "recommendation",
    ]
    lines.extend(markdown_table(summary, columns))
    lines.extend(
        [
            "",
            "## Label And Display Policy",
            "",
            f"- Label lock candidates: {lock_candidates}.",
            f"- Labels requiring manual review before lock: {manual_review}.",
            f"- Baseline-only labels held until follow-up is available: {hold}.",
            "",
        ]
    )
    policy_counts = policy.groupby(["display_policy", "label_action"]).size().reset_index(name="n")
    lines.extend(markdown_table(policy_counts, ["display_policy", "label_action", "n"]))
    lines.extend(
        [
            "",
            "## Recommended Next Step",
            "",
            "- Run covariate-expanded sensitivity first with age plus minimal core covariates.",
            "- Add rural/region and physical activity only where expanded-core coverage is ready.",
            "- Keep BMI as an optional sensitivity covariate because it is close to the cardiometabolic domain, even though the current cardiometabolic score is chronic-disease based.",
            "- Do not final-lock labels marked `manual_review_before_lock` without manual clinical review.",
        ]
    )
    (output_dir / "phase13_covariate_inventory_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8-sig")


def write_manuscript_plan(manuscript_dir: Path, summary: pd.DataFrame) -> None:
    lines = [
        "# Covariate Sensitivity Plan",
        "",
        "Use this after the main endotype validation results, not as the primary estimand.",
        "",
        "## Recommended Models",
        "",
        "1. Main current model: age-adjusted endotype class model.",
        "2. Minimal sensitivity model: age + education + marital status + smoking + drinking.",
        "3. Expanded sensitivity model where available: minimal model + rural/region + physical activity.",
        "4. Optional biometric sensitivity: expanded or minimal model + BMI, reported separately.",
        "",
        "## Cohort Readiness",
        "",
    ]
    lines.extend(
        markdown_table(
            summary,
            [
                "cohort",
                "minimal_core_ready",
                "expanded_core_ready",
                "optional_bmi_ready",
                "missing_minimal_core",
                "missing_expanded_core",
                "recommendation",
            ],
        )
    )
    lines.extend(
        [
            "",
            "## Guardrails",
            "",
            "- Do not adjust for the four domain scores in the main total association model.",
            "- Treat BMI as optional because it can behave as a cardiometabolic component, even if it is not used in the current chronic-disease domain score.",
            "- Keep KLoSA and SHARE sensitivity status explicit if they are shown in main figures.",
        ]
    )
    manuscript_dir.mkdir(parents=True, exist_ok=True)
    (manuscript_dir / "covariate_sensitivity_plan.md").write_text("\n".join(lines) + "\n", encoding="utf-8-sig")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--manuscript-dir", type=Path, default=None)
    args = parser.parse_args()

    manuscript_dir = args.manuscript_dir or (args.output_dir.parent / "manuscript")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    manuscript_dir.mkdir(parents=True, exist_ok=True)

    inventory, summary, participant_screen = build_inventory(args.data_root, args.output_dir)
    policy = build_label_display_policy(args.output_dir)

    inventory.to_csv(args.output_dir / "phase13_covariate_candidate_inventory.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(args.output_dir / "phase13_covariate_readiness_summary.csv", index=False, encoding="utf-8-sig")
    participant_screen.to_csv(args.output_dir / "phase13_covariate_participant_screen.csv", index=False, encoding="utf-8-sig")
    policy.to_csv(args.output_dir / "phase13_label_display_policy.csv", index=False, encoding="utf-8-sig")
    write_report(args.output_dir, summary, policy)
    write_manuscript_plan(manuscript_dir, summary)


if __name__ == "__main__":
    main()
