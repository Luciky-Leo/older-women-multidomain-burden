from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


MISSING_VALUES = {"", "NA", "NAN", "NULL", "."}
AGE_FALLBACK_VARIABLES = ("rabyear", "iwy", "iwendy", "iwindy", "r1iwy")


@dataclass(frozen=True)
class VarSpec:
    name: str
    direction: str


@dataclass(frozen=True)
class DomainSpec:
    groups: tuple[tuple[VarSpec, ...], ...]
    source: str


COHORT_CONFIG = {
    "CHARLS": {
        "file": "charls.csv",
        "id": "ID",
        "wave": "wave",
        "age": "age",
        "domains": {
            "functional": DomainSpec(((VarSpec("iadl", "higher_worse"),),), "primary"),
            "cognitive": DomainSpec(
                (
                    (VarSpec("total_cognition", "higher_better"),),
                    (
                        VarSpec("memory_z", "higher_better"),
                        VarSpec("orient_z", "higher_better"),
                        VarSpec("imrc", "higher_better"),
                        VarSpec("dlrc", "higher_better"),
                        VarSpec("ser7", "higher_better"),
                    ),
                ),
                "primary",
            ),
            "affective": DomainSpec(((VarSpec("cesd10", "higher_worse"),),), "primary"),
            "cardiometabolic_chronic": DomainSpec(
                (
                    (
                        VarSpec("hibpe", "higher_worse"),
                        VarSpec("diabe", "higher_worse"),
                        VarSpec("hearte", "higher_worse"),
                        VarSpec("stroke", "higher_worse"),
                        VarSpec("dyslipe", "higher_worse"),
                        VarSpec("cancre", "higher_worse"),
                    ),
                ),
                "primary",
            ),
        },
    },
    "ELSA": {
        "file": "elsa.csv",
        "id": "idauniqc",
        "wave": "wave",
        "age": "agey",
        "domains": {
            "functional": DomainSpec(
                (
                    (VarSpec("adltot6", "higher_worse"), VarSpec("iadltot2_e", "higher_worse")),
                    (VarSpec("adltot6", "higher_worse"),),
                ),
                "primary",
            ),
            "cognitive": DomainSpec(
                (
                    (
                        VarSpec("memory_z", "higher_better"),
                        VarSpec("orient_z", "higher_better"),
                        VarSpec("tcog_z_z", "higher_better"),
                    ),
                    (
                        VarSpec("imrc", "higher_better"),
                        VarSpec("dlrc", "higher_better"),
                        VarSpec("orient", "higher_better"),
                    ),
                ),
                "primary",
            ),
            "affective": DomainSpec(((VarSpec("cesd", "higher_worse"),),), "primary"),
            "cardiometabolic_chronic": DomainSpec(
                (
                    (
                        VarSpec("hibpe", "higher_worse"),
                        VarSpec("diabe", "higher_worse"),
                        VarSpec("hearte", "higher_worse"),
                        VarSpec("stroke", "higher_worse"),
                        VarSpec("hchole", "higher_worse"),
                        VarSpec("cancre", "higher_worse"),
                    ),
                ),
                "primary",
            ),
        },
    },
    "HRS": {
        "file": "hrs.csv",
        "id": "hhidpn",
        "wave": "wave",
        "age": "ragey_b",
        "domains": {
            "functional": DomainSpec(((VarSpec("adl6a", "higher_worse"),),), "primary"),
            "cognitive": DomainSpec(
                (
                    (VarSpec("cog27", "higher_better"),),
                    (VarSpec("cogtot", "higher_better"),),
                    (
                        VarSpec("memory_z", "higher_better"),
                        VarSpec("orient_z", "higher_better"),
                        VarSpec("imrc", "higher_better"),
                        VarSpec("dlrc", "higher_better"),
                        VarSpec("ser7", "higher_better"),
                    ),
                ),
                "primary",
            ),
            "affective": DomainSpec(((VarSpec("cesd", "higher_worse"),),), "primary"),
            "cardiometabolic_chronic": DomainSpec(
                (
                    (
                        VarSpec("hibpe", "higher_worse"),
                        VarSpec("diabe", "higher_worse"),
                        VarSpec("hearte", "higher_worse"),
                        VarSpec("stroke", "higher_worse"),
                        VarSpec("hchole", "higher_worse"),
                        VarSpec("cancre", "higher_worse"),
                    ),
                ),
                "primary",
            ),
        },
    },
    "KLoSA": {
        "file": "klosa.csv",
        "id": "pid",
        "wave": "wave",
        "age": "agey",
        "domains": {
            "functional": DomainSpec(
                (
                    (
                        VarSpec("gripsum", "higher_better"),
                        VarSpec("gripcomp", "higher_better"),
                        VarSpec("fall", "higher_worse"),
                    ),
                ),
                "bridge",
            ),
            "cognitive": DomainSpec(((VarSpec("cog_total", "higher_better"),),), "primary"),
            "affective": DomainSpec(((VarSpec("cesd10a", "higher_worse"),),), "primary"),
            "cardiometabolic_chronic": DomainSpec(
                (
                    (
                        VarSpec("hibpe", "higher_worse"),
                        VarSpec("diabe", "higher_worse"),
                        VarSpec("hearte", "higher_worse"),
                        VarSpec("stroke", "higher_worse"),
                        VarSpec("cancre", "higher_worse"),
                    ),
                ),
                "primary",
            ),
        },
    },
    "LASI": {
        "file": "lasi.csv",
        "id": "prim_key",
        "wave": "",
        "age": "r1agey",
        "domains": {
            "functional": DomainSpec(
                ((VarSpec("r1adltot6", "higher_worse"), VarSpec("r1iadltot_l", "higher_worse")),),
                "primary",
            ),
            "cognitive": DomainSpec(((VarSpec("r1cog_total", "higher_better"),),), "primary"),
            "affective": DomainSpec(((VarSpec("r1cesd10", "higher_worse"),),), "primary"),
            "cardiometabolic_chronic": DomainSpec(
                (
                    (
                        VarSpec("r1hibpe", "higher_worse"),
                        VarSpec("r1diabe", "higher_worse"),
                        VarSpec("r1hearte", "higher_worse"),
                        VarSpec("r1stroke", "higher_worse"),
                        VarSpec("r1hchole", "higher_worse"),
                        VarSpec("r1cancre", "higher_worse"),
                    ),
                ),
                "primary",
            ),
        },
    },
    "MHAS": {
        "file": "mhas.csv",
        "id": "rahhidnp",
        "wave": "wave",
        "age": "agey",
        "domains": {
            "functional": DomainSpec(
                ((VarSpec("adltot6", "higher_worse"), VarSpec("iadlfour", "higher_worse")),),
                "primary",
            ),
            "cognitive": DomainSpec(
                (
                    (
                        VarSpec("imrc8", "higher_better"),
                        VarSpec("dlrc8", "higher_better"),
                        VarSpec("ser7", "higher_better"),
                        VarSpec("orient_m", "higher_better"),
                    ),
                    (VarSpec("imrc8", "higher_better"), VarSpec("dlrc8", "higher_better")),
                ),
                "primary",
            ),
            "affective": DomainSpec(((VarSpec("cesd_m", "higher_worse"),),), "primary"),
            "cardiometabolic_chronic": DomainSpec(
                (
                    (
                        VarSpec("hibpe", "higher_worse"),
                        VarSpec("diabe", "higher_worse"),
                        VarSpec("hearte", "higher_worse"),
                        VarSpec("stroke", "higher_worse"),
                        VarSpec("cancre", "higher_worse"),
                    ),
                ),
                "primary",
            ),
        },
    },
    "SHARE": {
        "file": "share.csv",
        "id": "mergeid",
        "wave": "wave",
        "age": "agey",
        "domains": {
            "functional": DomainSpec(
                (
                    (VarSpec("adl", "higher_worse"), VarSpec("iadl", "higher_worse")),
                ),
                "primary",
            ),
            "cognitive": DomainSpec(
                (
                    (
                        VarSpec("imrc", "higher_better"),
                        VarSpec("dlrc", "higher_better"),
                        VarSpec("orient", "higher_better"),
                        VarSpec("ser7", "higher_better"),
                        VarSpec("numer_s", "higher_better"),
                    ),
                    (
                        VarSpec("imrc", "higher_better"),
                        VarSpec("dlrc", "higher_better"),
                        VarSpec("orient", "higher_better"),
                        VarSpec("numer_s", "higher_better"),
                    ),
                ),
                "primary",
            ),
            "affective": DomainSpec(((VarSpec("eurod", "higher_worse"),),), "primary"),
            "cardiometabolic_chronic": DomainSpec(
                (
                    (
                        VarSpec("hibpe", "higher_worse"),
                        VarSpec("diabe", "higher_worse"),
                        VarSpec("hearte", "higher_worse"),
                        VarSpec("stroke", "higher_worse"),
                        VarSpec("hchole", "higher_worse"),
                        VarSpec("cancre", "higher_worse"),
                    ),
                ),
                "primary",
            ),
        },
    },
}

ANALYSIS_SELECTIONS = [
    {"analysis_set": "strict_earliest_primary", "cohort": "CHARLS", "wave": "1", "tier": "strict_primary"},
    {"analysis_set": "strict_earliest_primary", "cohort": "ELSA", "wave": "1", "tier": "strict_primary"},
    {"analysis_set": "strict_earliest_primary", "cohort": "HRS", "wave": "5", "tier": "strict_primary"},
    {"analysis_set": "strict_earliest_primary", "cohort": "LASI", "wave": "all_rows_no_wave", "tier": "strict_primary"},
    {"analysis_set": "strict_earliest_primary", "cohort": "MHAS", "wave": "1", "tier": "strict_primary"},
    {"analysis_set": "strict_earliest_primary", "cohort": "SHARE", "wave": "1", "tier": "strict_primary"},
    {"analysis_set": "functional_bridge_earliest_sensitivity", "cohort": "KLoSA", "wave": "3", "tier": "bridge_sensitivity"},
]

DOMAIN_NAMES = ("functional", "cognitive", "affective", "cardiometabolic_chronic")
CORE_OUTPUT_COLUMNS = [
    "cohort",
    "participant_id",
    "wave",
    "age",
    "functional_score",
    "cognitive_score",
    "affective_score",
    "cardiometabolic_chronic_score",
    "functional_n_components",
    "cognitive_n_components",
    "affective_n_components",
    "cardiometabolic_chronic_n_components",
    "functional_source",
    "cognitive_source",
    "affective_source",
    "cardiometabolic_chronic_source",
    "complete_four_domain",
]


def var_id(header: str) -> str:
    return header.strip().strip('"').split(" ", 1)[0].strip()


def read_header_map(path: Path) -> dict[str, str]:
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
        raw_header = next(csv.reader(handle))
    return {var_id(raw): raw for raw in raw_header}


def to_numeric(series: pd.Series) -> pd.Series:
    out = pd.to_numeric(series.replace(list(MISSING_VALUES), pd.NA), errors="coerce")
    return out.mask(out < 0)


def zscore(series: pd.Series, group: pd.Series) -> pd.Series:
    mean = series.groupby(group).transform("mean")
    std = series.groupby(group).transform("std")
    return (series - mean) / std.mask(std == 0)


def orient(series: pd.Series, direction: str) -> pd.Series:
    numeric = to_numeric(series)
    if direction == "higher_better":
        return -numeric
    if direction == "higher_worse":
        return numeric
    raise ValueError(f"Unknown direction: {direction}")


def find_clean_csv(data_root: Path, file_name: str) -> Path:
    direct = data_root / file_name
    if direct.exists():
        return direct
    matches = list(data_root.rglob(file_name))
    if not matches:
        raise FileNotFoundError(f"Could not find {file_name} under {data_root}")
    return sorted(matches, key=lambda path: (len(path.parts), str(path)))[0]


def find_share_wave1_functional_dta(database_root: Path) -> Path:
    preferred = [
        path
        for path in database_root.rglob("share_wave1.dta")
        if "share" in str(path).lower() and "temp_data" in str(path).lower()
    ]
    if preferred:
        return sorted(preferred, key=lambda path: (len(path.parts), str(path)))[0]
    candidates = [
        path
        for path in database_root.rglob("*.dta")
        if "share" in str(path).lower() and "wave1" in str(path).lower()
    ]
    if not candidates:
        raise FileNotFoundError("Could not find SHARE wave-1 functional DTA under database root")
    return sorted(candidates, key=lambda path: (len(path.parts), str(path)))[0]


def augment_share_strict_functional(frame: pd.DataFrame, database_root: Path | None) -> pd.DataFrame:
    if database_root is None:
        return frame
    if {"adl", "iadl"}.issubset(frame.columns):
        return frame
    path = find_share_wave1_functional_dta(database_root)
    functional = pd.read_stata(str(path), columns=["mergeid", "adl", "iadl"], convert_categoricals=False)
    functional["mergeid"] = functional["mergeid"].astype("string")
    functional = functional.drop_duplicates("mergeid")
    out = frame.merge(functional, on="mergeid", how="left")
    return out


def variables_for_config(config: dict[str, object]) -> list[str]:
    variables = {"ragender", str(config["age"])}
    variables.update(AGE_FALLBACK_VARIABLES)
    if config["id"]:
        variables.add(str(config["id"]))
    if config["wave"]:
        variables.add(str(config["wave"]))
    domains: dict[str, DomainSpec] = config["domains"]  # type: ignore[assignment]
    for domain in domains.values():
        for group in domain.groups:
            for spec in group:
                variables.add(spec.name)
    return sorted(variables)


def read_cohort_frame(data_root: Path, cohort: str, database_root: Path | None = None) -> pd.DataFrame:
    config = COHORT_CONFIG[cohort]
    path = find_clean_csv(data_root, str(config["file"]))
    header_map = read_header_map(path)
    wanted = variables_for_config(config)
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
    frame = frame[(frame["ragender"] == "0") & (frame["age"] >= 50)].copy()
    return frame


def score_non_chronic_domain(frame: pd.DataFrame, cohort: str, domain_name: str, domain: DomainSpec) -> None:
    group_scores = []
    group_counts = []
    group_labels = []
    for group_index, group in enumerate(domain.groups, start=1):
        z_columns = []
        raw_columns = []
        present_specs = [spec for spec in group if spec.name in frame.columns]
        for spec in present_specs:
            oriented = orient(frame[spec.name], spec.direction)
            raw_name = f"__{domain_name}_{group_index}_{spec.name}_oriented"
            z_name = f"__{domain_name}_{group_index}_{spec.name}_z"
            frame[raw_name] = oriented
            frame[z_name] = zscore(oriented, frame["wave"])
            raw_columns.append(raw_name)
            z_columns.append(z_name)
        if z_columns:
            score = frame[z_columns].mean(axis=1, skipna=True)
            count = frame[z_columns].notna().sum(axis=1)
            score = zscore(score, frame["wave"])
        else:
            score = pd.Series(pd.NA, index=frame.index, dtype="Float64")
            count = pd.Series(0, index=frame.index)
        group_scores.append(score)
        group_counts.append(count)
        group_labels.append("+".join(spec.name for spec in present_specs))

    final_score = pd.Series(pd.NA, index=frame.index, dtype="Float64")
    final_count = pd.Series(0, index=frame.index)
    final_group = pd.Series("", index=frame.index, dtype="string")
    for score, count, label in zip(group_scores, group_counts, group_labels):
        take = final_score.isna() & score.notna()
        final_score.loc[take] = score.loc[take]
        final_count.loc[take] = count.loc[take]
        final_group.loc[take] = label

    frame[f"{domain_name}_score"] = final_score
    frame[f"{domain_name}_n_components"] = final_count.astype(int)
    frame[f"{domain_name}_variables"] = final_group
    frame[f"{domain_name}_source"] = domain.source


def score_chronic_domain(frame: pd.DataFrame, domain_name: str, domain: DomainSpec) -> None:
    group = domain.groups[0]
    columns = []
    for spec in group:
        if spec.name not in frame.columns:
            continue
        numeric = to_numeric(frame[spec.name])
        binary = numeric.where(numeric.isin([0, 1]))
        name = f"__{domain_name}_{spec.name}_binary"
        frame[name] = binary
        columns.append(name)

    if columns:
        frame[f"{domain_name}_count"] = frame[columns].sum(axis=1, skipna=True)
        frame[f"{domain_name}_prop"] = frame[columns].mean(axis=1, skipna=True)
        frame[f"{domain_name}_n_components"] = frame[columns].notna().sum(axis=1).astype(int)
        frame[f"{domain_name}_score"] = zscore(frame[f"{domain_name}_prop"], frame["wave"])
        frame[f"{domain_name}_variables"] = "+".join(spec.name for spec in group if spec.name in frame.columns)
    else:
        frame[f"{domain_name}_count"] = pd.NA
        frame[f"{domain_name}_prop"] = pd.NA
        frame[f"{domain_name}_n_components"] = 0
        frame[f"{domain_name}_score"] = pd.NA
        frame[f"{domain_name}_variables"] = ""
    frame[f"{domain_name}_source"] = domain.source


def score_cohort(frame: pd.DataFrame, cohort: str) -> pd.DataFrame:
    domains: dict[str, DomainSpec] = COHORT_CONFIG[cohort]["domains"]  # type: ignore[assignment]
    for domain_name, domain in domains.items():
        if domain_name == "cardiometabolic_chronic":
            score_chronic_domain(frame, domain_name, domain)
        else:
            score_non_chronic_domain(frame, cohort, domain_name, domain)

    frame["complete_four_domain"] = frame[[f"{domain}_score" for domain in DOMAIN_NAMES]].notna().all(axis=1).astype(int)
    keep = CORE_OUTPUT_COLUMNS + [f"{domain}_variables" for domain in DOMAIN_NAMES]
    keep += ["cardiometabolic_chronic_count", "cardiometabolic_chronic_prop"]
    return frame[[column for column in keep if column in frame.columns]].copy()


def build_selected_scores(long_scores: pd.DataFrame) -> pd.DataFrame:
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


def summarize_missingness(scores: pd.DataFrame) -> pd.DataFrame:
    rows = []
    grouped = scores.groupby(["analysis_set", "analysis_tier", "cohort", "wave"], dropna=False)
    for keys, group in grouped:
        analysis_set, analysis_tier, cohort, wave = keys
        row = {
            "analysis_set": analysis_set,
            "analysis_tier": analysis_tier,
            "cohort": cohort,
            "wave": wave,
            "n": len(group),
            "complete_four_domain_n": int(group["complete_four_domain"].sum()),
            "complete_four_domain_pct": round(group["complete_four_domain"].mean() * 100, 2),
        }
        for domain in DOMAIN_NAMES:
            score_col = f"{domain}_score"
            row[f"{domain}_nonmissing_n"] = int(group[score_col].notna().sum())
            row[f"{domain}_nonmissing_pct"] = round(group[score_col].notna().mean() * 100, 2)
            row[f"{domain}_source"] = group[f"{domain}_source"].dropna().astype(str).iloc[0]
            row[f"{domain}_variables"] = group[f"{domain}_variables"].dropna().astype(str).iloc[0]
        rows.append(row)
    return pd.DataFrame(rows).sort_values(["analysis_set", "cohort"])


def summarize_scores(scores: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (analysis_set, cohort, wave), group in scores.groupby(["analysis_set", "cohort", "wave"], dropna=False):
        for domain in DOMAIN_NAMES:
            series = pd.to_numeric(group[f"{domain}_score"], errors="coerce").dropna()
            if series.empty:
                rows.append(
                    {
                        "analysis_set": analysis_set,
                        "cohort": cohort,
                        "wave": wave,
                        "domain": domain,
                        "n": 0,
                        "mean": "",
                        "sd": "",
                        "min": "",
                        "p25": "",
                        "median": "",
                        "p75": "",
                        "max": "",
                    }
                )
                continue
            rows.append(
                {
                    "analysis_set": analysis_set,
                    "cohort": cohort,
                    "wave": wave,
                    "domain": domain,
                    "n": int(series.size),
                    "mean": round(float(series.mean()), 4),
                    "sd": round(float(series.std()), 4),
                    "min": round(float(series.min()), 4),
                    "p25": round(float(series.quantile(0.25)), 4),
                    "median": round(float(series.median()), 4),
                    "p75": round(float(series.quantile(0.75)), 4),
                    "max": round(float(series.max()), 4),
                }
            )
    return pd.DataFrame(rows)


def summarize_correlations(scores: pd.DataFrame) -> pd.DataFrame:
    rows = []
    score_columns = [f"{domain}_score" for domain in DOMAIN_NAMES]
    for (analysis_set, cohort, wave), group in scores.groupby(["analysis_set", "cohort", "wave"], dropna=False):
        corr = group[score_columns].corr()
        for i, left in enumerate(DOMAIN_NAMES):
            for right in DOMAIN_NAMES[i + 1 :]:
                value = corr.loc[f"{left}_score", f"{right}_score"]
                rows.append(
                    {
                        "analysis_set": analysis_set,
                        "cohort": cohort,
                        "wave": wave,
                        "domain_1": left,
                        "domain_2": right,
                        "correlation": "" if pd.isna(value) else round(float(value), 4),
                    }
                )
    return pd.DataFrame(rows)


def write_report(path: Path, missingness: pd.DataFrame, score_qc: pd.DataFrame, correlations: pd.DataFrame) -> None:
    lines = [
        "# Phase 3 Domain Score QC",
        "",
        "All domain scores are oriented so higher values indicate worse health.",
        "Scores are standardized within cohort and wave before cross-domain modeling.",
        "",
        "## Analysis Sets",
        "",
        "| Analysis set | Cohort | Wave | N | Complete four-domain N | Complete four-domain % | Functional source |",
        "|---|---|---|---:|---:|---:|---|",
    ]
    for row in missingness.to_dict("records"):
        lines.append(
            f"| {row['analysis_set']} | {row['cohort']} | {row['wave']} | {row['n']} | "
            f"{row['complete_four_domain_n']} | {row['complete_four_domain_pct']} | {row['functional_source']} |"
        )

    lines.extend(["", "## Domain Missingness", ""])
    lines.append("| Analysis set | Cohort | Functional % | Cognitive % | Affective % | Cardiometabolic % |")
    lines.append("|---|---|---:|---:|---:|---:|")
    for row in missingness.to_dict("records"):
        lines.append(
            f"| {row['analysis_set']} | {row['cohort']} | {row['functional_nonmissing_pct']} | "
            f"{row['cognitive_nonmissing_pct']} | {row['affective_nonmissing_pct']} | "
            f"{row['cardiometabolic_chronic_nonmissing_pct']} |"
        )

    high_corr = correlations[
        pd.to_numeric(correlations["correlation"], errors="coerce").abs() >= 0.7
    ]
    lines.extend(["", "## Correlation Screen", ""])
    if high_corr.empty:
        lines.append("No absolute pairwise domain correlation >= 0.70 in the selected score sets.")
    else:
        lines.append("| Analysis set | Cohort | Domain 1 | Domain 2 | Correlation |")
        lines.append("|---|---|---|---|---:|")
        for row in high_corr.to_dict("records"):
            lines.append(
                f"| {row['analysis_set']} | {row['cohort']} | {row['domain_1']} | {row['domain_2']} | {row['correlation']} |"
            )

    lines.extend(
        [
            "",
            "## Proceeding Decision",
            "",
            "- Strict primary modeling can start with CHARLS, ELSA, HRS, LASI, MHAS, and SHARE.",
            "- KLoSA should remain a sensitivity cohort because its functional score is a performance bridge.",
            "- SHARE uses a strict wave-1 ADL/IADL functional score merged from the local SHARE wave-1 Stata file.",
            "- Phase 4 should test whether classes are domain-specific rather than a single severity gradient.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", required=True, type=Path)
    parser.add_argument("--database-root", type=Path, default=None)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    long_frames = []
    for cohort in COHORT_CONFIG:
        frame = read_cohort_frame(args.data_root, cohort, args.database_root)
        long_frames.append(score_cohort(frame, cohort))

    long_scores = pd.concat(long_frames, ignore_index=True)
    selected_scores = build_selected_scores(long_scores)
    missingness = summarize_missingness(selected_scores)
    score_qc = summarize_scores(selected_scores)
    correlations = summarize_correlations(selected_scores)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    long_scores.to_csv(args.output_dir / "phase3_domain_scores_long.csv", index=False, encoding="utf-8-sig")
    selected_scores.to_csv(args.output_dir / "phase3_domain_scores.csv", index=False, encoding="utf-8-sig")
    missingness.to_csv(args.output_dir / "phase3_domain_missingness.csv", index=False, encoding="utf-8-sig")
    score_qc.to_csv(args.output_dir / "phase3_domain_score_distribution.csv", index=False, encoding="utf-8-sig")
    correlations.to_csv(args.output_dir / "phase3_domain_correlations.csv", index=False, encoding="utf-8-sig")
    write_report(args.output_dir / "phase3_domain_score_qc.md", missingness, score_qc, correlations)


if __name__ == "__main__":
    main()
