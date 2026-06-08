from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd
from pandas.io.stata import StataReader


COHORTS = {
    "CHARLS": {"csv": "charls.csv", "dta": "charls.dta", "aliases": ["CHARLS"]},
    "ELSA": {"csv": "elsa.csv", "dta": "elsa.dta", "aliases": ["ELSA"]},
    "HRS": {"csv": "hrs.csv", "dta": "hrs.dta", "aliases": ["HRS"]},
    "KLoSA": {"csv": "klosa.csv", "dta": "klosa.dta", "aliases": ["KLoSA"]},
    "LASI": {"csv": "lasi.csv", "dta": "lasi.dta", "aliases": ["LASI"]},
    "MHAS": {"csv": "mhas.csv", "dta": "mhas.dta", "aliases": ["MHAS"]},
    "SHARE": {"csv": "share.csv", "dta": "share.dta", "aliases": ["SHARE"]},
}

AGE_CANDIDATES = ["age", "agey", "r1agey", "ragey_b", "ragey_e", "ragey_m"]
MISSING_VALUES = {"", "NA", "NAN", "NULL", "."}

EVIDENCE_PATTERNS = [
    re.compile(r"\breplace\s+ragender\b", re.I),
    re.compile(r"\brecode\s+ragender\b", re.I),
    re.compile(r"\blabel\s+define\s+(?:ragender_|gender_|gender)\b", re.I),
    re.compile(r"\blabel\s+values?\s+ragender\b", re.I),
    re.compile(r"\blabel\s+var(?:iable)?\s+ragender\b", re.I),
]


@dataclass(frozen=True)
class CandidateSpec:
    domain: str
    construct: str
    variables: tuple[str, ...]
    role: str
    direction: str
    harmonization_action: str


DOMAIN_SPECS = [
    CandidateSpec(
        "functional",
        "adl_limitations",
        ("adltot6", "adl6a", "r1adltot6"),
        "primary",
        "higher_worse",
        "Use as functional limitation count; standardize within cohort/wave.",
    ),
    CandidateSpec(
        "functional",
        "iadl_limitations",
        ("iadl", "iadlfour", "iadltot2_e", "r1iadltot_l"),
        "primary",
        "higher_worse",
        "Use as instrumental limitation count; standardize within cohort/wave.",
    ),
    CandidateSpec(
        "functional",
        "frailty_or_performance",
        ("frailty", "frailtya", "frailtyb", "gripsum", "gripcomp", "walkcomp", "fall", "fall_down"),
        "supporting",
        "mixed_check_labels",
        "Use for sensitivity or performance-anchored functional score after label/range checks.",
    ),
    CandidateSpec(
        "cognitive",
        "global_cognition",
        ("total_cognition", "cog_total", "cogtot", "cog27", "r1cog_total"),
        "primary",
        "higher_better",
        "Reverse standardized score so higher harmonized domain score means worse cognition.",
    ),
    CandidateSpec(
        "cognitive",
        "memory_orientation",
        (
            "memory_z",
            "orient_z",
            "tcog_z_z",
            "imrc8",
            "dlrc8",
            "ser7",
            "orient_m",
            "imrc",
            "dlrc",
            "orient",
            "numer_s",
        ),
        "primary",
        "higher_better",
        "Reverse standardized memory/orientation/numeracy scores; combine only after confirming comparable construction.",
    ),
    CandidateSpec(
        "cognitive",
        "dementia_indicator",
        ("dementia", "demene", "alzdeme"),
        "supporting",
        "higher_worse",
        "Do not use as a direct substitute for continuous cognition in the primary class model.",
    ),
    CandidateSpec(
        "affective",
        "depressive_symptoms",
        ("cesd", "cesd10", "cesd10a", "cesd10b", "r1cesd10", "cesd_m", "eurod", "depressive"),
        "primary",
        "higher_worse",
        "Use depressive symptom score or indicator; standardize within cohort/wave.",
    ),
    CandidateSpec(
        "affective",
        "psychological_or_life_satisfaction",
        ("psyche", "r1psyche", "satlifez"),
        "supporting",
        "label_check_required",
        "Use only after label/range checks; not a direct replacement for CES-D in primary models.",
    ),
    CandidateSpec(
        "cardiometabolic_chronic",
        "chronic_disease_indicators",
        (
            "hibpe",
            "diabe",
            "hearte",
            "stroke",
            "hchole",
            "dyslipe",
            "cancre",
            "r1hibpe",
            "r1diabe",
            "r1hearte",
            "r1stroke",
            "r1hchole",
            "r1cancre",
        ),
        "primary",
        "higher_worse",
        "Create count/proportion of available chronic cardiometabolic conditions.",
    ),
    CandidateSpec(
        "cardiometabolic_chronic",
        "anthropometry_blood_pressure",
        ("bmi", "mbmi", "r1mbmi", "systo", "diasto", "r1systo", "r1diasto"),
        "supporting",
        "continuous_risk_check",
        "Use as secondary cardiometabolic severity components after cohort-specific range checks.",
    ),
]


def var_id(header: str) -> str:
    return header.strip().strip('"').split(" ", 1)[0].strip()


def clean_value(value: object | None) -> str:
    if value is None:
        return ""
    return str(value).strip().strip('"')


def is_nonmissing(value: object | None) -> bool:
    value_clean = clean_value(value)
    return bool(value_clean) and value_clean.upper() not in MISSING_VALUES


def to_float(value: object | None) -> float | None:
    value_clean = clean_value(value)
    if not is_nonmissing(value_clean):
        return None
    try:
        return float(value_clean)
    except ValueError:
        return None


def numeric_sort_key(value: str) -> tuple[int, float | str]:
    try:
        return (0, float(value))
    except ValueError:
        return (1, value)


def format_code(value: object) -> str:
    if pd.isna(value):
        return ""
    try:
        value_float = float(value)
        if value_float.is_integer():
            return str(int(value_float))
    except (TypeError, ValueError):
        pass
    return str(value)


def read_csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
        reader = csv.reader(handle)
        variables = [var_id(h) for h in next(reader)]
        rows = []
        for raw in reader:
            if len(raw) < len(variables):
                raw = raw + [""] * (len(variables) - len(raw))
            rows.append(dict(zip(variables, raw)))
    return variables, rows


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def find_clean_csv(database_root: Path, file_name: str) -> Path:
    matches = [p for p in database_root.rglob(file_name) if "csv" in p.parent.name.lower()]
    if not matches:
        matches = list(database_root.rglob(file_name))
    if not matches:
        raise FileNotFoundError(f"Could not find {file_name} under {database_root}")
    return sorted(matches, key=lambda p: (len(p.parts), str(p)))[0]


def find_working_dta(database_root: Path, file_name: str) -> Path:
    matches = [p for p in database_root.rglob(file_name) if p.parent.name.lower() == "working_data"]
    if not matches:
        matches = list(database_root.rglob(file_name))
    if not matches:
        raise FileNotFoundError(f"Could not find {file_name} under {database_root}")
    return sorted(matches, key=lambda p: (0 if p.parent.name.lower() == "working_data" else 1, len(p.parts), str(p)))[0]


def read_text_lossy(path: Path) -> str:
    for encoding in ("utf-8-sig", "utf-8", "gb18030", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def find_dofile(database_root: Path, aliases: Iterable[str]) -> Path | None:
    candidates = []
    alias_lower = [a.lower() for a in aliases]
    for path in database_root.rglob("*.do"):
        path_lower = str(path).lower()
        if not any(alias in path_lower for alias in alias_lower):
            continue
        text = read_text_lossy(path)
        if "ragender" not in text:
            continue
        score = sum(len(pattern.findall(text)) for pattern in EVIDENCE_PATTERNS)
        if score:
            dofiles_preference = 0 if "dofiles" in path_lower else 1
            explicit_zero_female = 0 if re.search(r'0\s+"(?:女性|female)"', text, re.I) else 1
            candidates.append((dofiles_preference, explicit_zero_female, -score, len(path.parts), str(path), path))
    if not candidates:
        return None
    return sorted(candidates, key=lambda item: item[:-1])[0][-1]


def extract_dofile_evidence(path: Path | None) -> list[str]:
    if path is None:
        return []
    evidence = []
    lines = read_text_lossy(path).splitlines()
    for line_no, line in enumerate(lines, start=1):
        if any(pattern.search(line) for pattern in EVIDENCE_PATTERNS):
            evidence.append(f"{path}:{line_no}: {line.strip()}")
    return evidence[:10]


def inspect_gender_coding(dta_path: Path) -> dict[str, object]:
    with StataReader(str(dta_path)) as reader:
        variable_labels = reader.variable_labels()
        variable_label = variable_labels.get("ragender", "")

    raw = pd.read_stata(str(dta_path), columns=["ragender"], convert_categoricals=False)["ragender"]
    labeled = pd.read_stata(str(dta_path), columns=["ragender"], convert_categoricals=True)["ragender"]
    pairs = pd.DataFrame({"code": raw, "label": labeled.astype("string")}).dropna()
    mapping = {}
    for _, row in pairs.drop_duplicates().sort_values("code").iterrows():
        mapping[format_code(row["code"])] = str(row["label"])

    female_code = ""
    male_code = ""
    for code, label in mapping.items():
        label_lower = label.lower()
        if "女" in label or "female" in label_lower:
            female_code = code
        if "男" in label or "male" in label_lower:
            male_code = code

    raw_counts = "; ".join(
        f"{format_code(code)}:{int(count)}"
        for code, count in raw.value_counts(dropna=False).sort_index().items()
        if format_code(code)
    )
    labeled_counts = "; ".join(f"{label}:{int(count)}" for label, count in labeled.value_counts(dropna=False).items())
    status = "confirmed" if female_code == "0" and male_code == "1" else "check_required"
    return {
        "variable_label": variable_label,
        "value_mapping": "; ".join(f"{code}={label}" for code, label in mapping.items()),
        "female_code": female_code,
        "male_code": male_code,
        "raw_counts": raw_counts,
        "labeled_counts": labeled_counts,
        "confirmation_status": status,
    }


def infer_baseline_wave(rows: list[dict[str, str]], variables: list[str]) -> str:
    if "wave" not in variables:
        return "all_rows_no_wave"
    waves = sorted({clean_value(r.get("wave")) for r in rows if clean_value(r.get("wave"))}, key=numeric_sort_key)
    return waves[0] if waves else "unknown"


def choose_age_variable(rows: list[dict[str, str]], variables: list[str]) -> str:
    candidates = [v for v in AGE_CANDIDATES if v in variables]
    if not candidates:
        return ""
    counts = {v: sum(to_float(r.get(v)) is not None for r in rows) for v in candidates}
    return max(candidates, key=lambda v: counts[v])


def derive_age(row: dict[str, str], age_variable: str) -> float | None:
    age = to_float(row.get(age_variable))
    if age is not None:
        return age

    birth_year = to_float(row.get("rabyear"))
    if birth_year is None:
        return None

    for interview_year_var in ["iwy", "iwendy", "iwindy", "r1iwy"]:
        interview_year = to_float(row.get(interview_year_var))
        if interview_year is None:
            continue
        derived = interview_year - birth_year
        if 0 <= derived <= 120:
            return derived
    return None


def baseline_rows(rows: list[dict[str, str]], baseline_wave: str) -> list[dict[str, str]]:
    if baseline_wave == "all_rows_no_wave":
        return rows
    return [r for r in rows if clean_value(r.get("wave")) == baseline_wave]


def sample_values(rows: list[dict[str, str]], variable: str, limit: int = 8) -> str:
    seen = set()
    values = []
    for row in rows:
        value = clean_value(row.get(variable))
        if not is_nonmissing(value) or value in seen:
            continue
        seen.add(value)
        values.append(value)
        if len(values) >= limit:
            break
    return "|".join(values)


def dta_variable_labels(dta_path: Path) -> dict[str, str]:
    with StataReader(str(dta_path)) as reader:
        return reader.variable_labels()


def present_specs_for_variable(variable: str) -> list[CandidateSpec]:
    return [spec for spec in DOMAIN_SPECS if variable in spec.variables]


def build_candidate_rows(
    cohort: str,
    variables: list[str],
    women_rows: list[dict[str, str]],
    labels: dict[str, str],
) -> list[dict[str, object]]:
    out = []
    variable_set = set(variables)
    total = len(women_rows)
    for spec in DOMAIN_SPECS:
        for variable in spec.variables:
            if variable not in variable_set:
                continue
            nonmissing = sum(is_nonmissing(row.get(variable)) for row in women_rows)
            out.append(
                {
                    "cohort": cohort,
                    "domain": spec.domain,
                    "construct": spec.construct,
                    "variable": variable,
                    "role": spec.role,
                    "direction": spec.direction,
                    "harmonization_action": spec.harmonization_action,
                    "baseline_women50_rows": total,
                    "nonmissing": nonmissing,
                    "nonmissing_pct": round(nonmissing / max(total, 1) * 100, 2),
                    "sample_values": sample_values(women_rows, variable),
                    "variable_label": labels.get(variable, ""),
                }
            )
    return out


def readiness_for_domain(cohort: str, domain: str, rows: list[dict[str, object]], n: int) -> dict[str, object]:
    domain_rows = [r for r in rows if r["cohort"] == cohort and r["domain"] == domain and int(r["nonmissing"]) > 0]
    primary = [r for r in domain_rows if r["role"] == "primary" and float(r["nonmissing_pct"]) >= 50]
    supporting = [r for r in domain_rows if r["role"] == "supporting" and float(r["nonmissing_pct"]) >= 50]
    if primary:
        readiness = "ready_primary"
        note = "At least one primary harmonization variable has >=50% nonmissing."
    elif domain == "functional" and len(supporting) >= 2:
        readiness = "limited_performance_ready"
        note = "Functional domain can be approximated with performance/frailty variables, but construct differs from ADL/IADL."
    elif supporting:
        readiness = "limited_supporting_only"
        note = "Only supporting variables pass the missingness threshold; avoid primary class modeling without additional extraction."
    else:
        readiness = "not_ready"
        note = "No suitable candidate passes the current threshold."

    return {
        "cohort": cohort,
        "domain": domain,
        "baseline_women50_rows": n,
        "readiness": readiness,
        "primary_variables": "; ".join(f"{r['variable']}({r['nonmissing_pct']}%)" for r in primary),
        "supporting_variables": "; ".join(f"{r['variable']}({r['nonmissing_pct']}%)" for r in supporting),
        "note": note,
    }


def build_report(
    path: Path,
    sex_rows: list[dict[str, object]],
    readiness_rows: list[dict[str, object]],
    wave_readiness_rows: list[dict[str, object]],
    cohort_counts: dict[str, int],
) -> None:
    domains = ["functional", "cognitive", "affective", "cardiometabolic_chronic"]
    readiness_map = {(r["cohort"], r["domain"]): r["readiness"] for r in readiness_rows}

    lines = [
        "# Phase 2 Sex Coding and Four-Domain Harmonization Report",
        "",
        "## Sex Coding Confirmation",
        "",
        "The cleaned project files use `ragender == 0` for women and `ragender == 1` for men in all seven cohorts.",
        "This is confirmed from the Working_data Stata value labels and the local merge do-files.",
        "",
        "| Cohort | DTA value mapping | Female code | Male code | Status |",
        "|---|---|---:|---:|---|",
    ]
    for row in sex_rows:
        lines.append(
            f"| {row['cohort']} | {row['value_mapping']} | {row['female_code']} | {row['male_code']} | "
            f"{row['confirmation_status']} |"
        )

    lines.extend(
        [
            "",
            "## Four-Domain Readiness",
            "",
            "| Cohort | Women 50+ baseline | Functional | Cognitive | Affective | Cardiometabolic/chronic |",
            "|---|---:|---|---|---|---|",
        ]
    )
    for cohort in COHORTS:
        lines.append(
            f"| {cohort} | {cohort_counts[cohort]} | "
            f"{readiness_map[(cohort, 'functional')]} | "
            f"{readiness_map[(cohort, 'cognitive')]} | "
            f"{readiness_map[(cohort, 'affective')]} | "
            f"{readiness_map[(cohort, 'cardiometabolic_chronic')]} |"
        )

    selected_wave = {}
    for cohort in COHORTS:
        rows = [r for r in wave_readiness_rows if r["cohort"] == cohort]
        best = sorted(rows, key=lambda r: (-int(r["ready_or_limited_domains"]), -int(r["women50_rows"]), str(r["wave"])))[0]
        selected_wave[cohort] = best

    ready_primary_4 = [
        cohort
        for cohort in COHORTS
        if all(readiness_map[(cohort, domain)] == "ready_primary" for domain in domains)
    ]
    usable_primary_or_functional_limited = [
        cohort
        for cohort in COHORTS
        if readiness_map[(cohort, "functional")] in {"ready_primary", "limited_performance_ready"}
        and readiness_map[(cohort, "cognitive")] == "ready_primary"
        and readiness_map[(cohort, "affective")] == "ready_primary"
        and readiness_map[(cohort, "cardiometabolic_chronic")] == "ready_primary"
    ]
    wave_strict_primary_4 = sorted(
        {
            str(row["cohort"])
            for row in wave_readiness_rows
            if all(str(row[domain]).startswith("primary:") for domain in domains)
        }
    )
    wave_practical = sorted(
        {
            str(row["cohort"])
            for row in wave_readiness_rows
            if str(row["functional"]).startswith(("primary:", "limited:"))
            and str(row["cognitive"]).startswith("primary:")
            and str(row["affective"]).startswith("primary:")
            and str(row["cardiometabolic_chronic"]).startswith("primary:")
        }
    )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"- Strict earliest-wave four-primary-domain cohorts: {', '.join(ready_primary_4) if ready_primary_4 else 'none under the current rule'}.",
            "- Practical earliest-wave endotype modeling cohorts: "
            + (", ".join(usable_primary_or_functional_limited) if usable_primary_or_functional_limited else "none"),
            "- Strict wave-adjusted four-primary-domain cohorts: "
            + (", ".join(wave_strict_primary_4) if wave_strict_primary_4 else "none under the current rule"),
            "- Practical wave-adjusted endotype modeling cohorts: "
            + (", ".join(wave_practical) if wave_practical else "none"),
            "- Targeted variable expansion resolved the LASI chronic-disease gap and the MHAS/SHARE cognition and depressive-symptom gaps from existing cleaned Working_data/CSV variables.",
            "- SHARE still does not have a strict ADL/IADL functional primary variable under the current candidate rule; it is practical only with a performance/frailty functional bridge.",
            "- The baseline table above uses the earliest available wave, matching Phase 1. SHARE needs a later wave for the practical four-domain bridge because earliest-wave functional coverage is too thin.",
            "",
            "## Wave-Level Baseline Check",
            "",
            "The selected wave below maximizes ready/limited domain count, then women 50+ sample size. It is a feasibility choice, not yet the final longitudinal baseline.",
            "",
            "| Cohort | Best current wave | Women 50+ rows | Ready/limited domains | Functional | Cognitive | Affective | Cardiometabolic/chronic |",
            "|---|---|---:|---:|---|---|---|---|",
        ]
    )
    for cohort in COHORTS:
        row = selected_wave[cohort]
        lines.append(
            f"| {cohort} | {row['wave']} | {row['women50_rows']} | {row['ready_or_limited_domains']} | "
            f"{row['functional']} | {row['cognitive']} | {row['affective']} | {row['cardiometabolic_chronic']} |"
        )

    lines.extend(
        [
            "",
            "## Minimal Harmonization Rule For The Next Script",
            "",
            "- Use `ragender == 0` and baseline age >= 50 for the primary women-only cohort.",
            "- Build domain scores within cohort/wave and orient every domain so higher means worse health.",
            "- Functional: ADL/IADL when available; otherwise keep performance/frailty variables as a sensitivity bridge.",
            "- Cognitive: require a continuous/global cognition score for primary modeling; dementia indicators are supporting variables only.",
            "- Affective: require CES-D/depressive symptoms for primary modeling; `psyche` and `satlifez` need label/range checks before secondary use.",
            "- Cardiometabolic/chronic: use a count or proportion of available chronic disease indicators, with BMI/BP as secondary severity components.",
        ]
    )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")


def compact_readiness(domain: str, rows: list[dict[str, object]]) -> str:
    domain_rows = [r for r in rows if r["domain"] == domain and int(r["nonmissing"]) > 0]
    primary = [r for r in domain_rows if r["role"] == "primary" and float(r["nonmissing_pct"]) >= 50]
    supporting = [r for r in domain_rows if r["role"] == "supporting" and float(r["nonmissing_pct"]) >= 50]
    if primary:
        return "primary:" + ";".join(str(r["variable"]) for r in primary)
    if domain == "functional" and len(supporting) >= 2:
        return "limited:" + ";".join(str(r["variable"]) for r in supporting)
    if supporting:
        return "supporting:" + ";".join(str(r["variable"]) for r in supporting)
    return "not_ready"


def build_wave_readiness_rows(
    cohort: str,
    variables: list[str],
    rows: list[dict[str, str]],
    age_variable: str,
    female_code: str,
    labels: dict[str, str],
) -> list[dict[str, object]]:
    if "wave" in variables:
        waves = sorted({clean_value(r.get("wave")) for r in rows if clean_value(r.get("wave"))}, key=numeric_sort_key)
    else:
        waves = ["all_rows_no_wave"]

    out = []
    for wave in waves:
        wave_rows = rows if wave == "all_rows_no_wave" else [r for r in rows if clean_value(r.get("wave")) == wave]
        women_rows = [
            row
            for row in wave_rows
            if derive_age(row, age_variable) is not None
            and derive_age(row, age_variable) >= 50
            and clean_value(row.get("ragender")) == female_code
        ]
        candidate_rows = build_candidate_rows(cohort, variables, women_rows, labels)
        statuses = {domain: compact_readiness(domain, candidate_rows) for domain in ["functional", "cognitive", "affective", "cardiometabolic_chronic"]}
        ready_or_limited = sum(1 for status in statuses.values() if status.startswith(("primary:", "limited:")))
        out.append(
            {
                "cohort": cohort,
                "wave": wave,
                "women50_rows": len(women_rows),
                "ready_or_limited_domains": ready_or_limited,
                "functional": statuses["functional"],
                "cognitive": statuses["cognitive"],
                "affective": statuses["affective"],
                "cardiometabolic_chronic": statuses["cardiometabolic_chronic"],
            }
        )
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database-root", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    sex_rows: list[dict[str, object]] = []
    candidate_rows: list[dict[str, object]] = []
    readiness_rows: list[dict[str, object]] = []
    wave_readiness_rows: list[dict[str, object]] = []
    cohort_counts: dict[str, int] = {}

    for cohort, info in COHORTS.items():
        csv_path = find_clean_csv(args.database_root, str(info["csv"]))
        dta_path = find_working_dta(args.database_root, str(info["dta"]))
        dofile_path = find_dofile(args.database_root, info["aliases"])

        gender = inspect_gender_coding(dta_path)
        evidence = extract_dofile_evidence(dofile_path)
        sex_rows.append(
            {
                "cohort": cohort,
                "dta_source": str(dta_path),
                "dofile_source": str(dofile_path) if dofile_path else "",
                "variable_label": gender["variable_label"],
                "value_mapping": gender["value_mapping"],
                "female_code": gender["female_code"],
                "male_code": gender["male_code"],
                "raw_counts": gender["raw_counts"],
                "labeled_counts": gender["labeled_counts"],
                "confirmation_status": gender["confirmation_status"],
                "dofile_evidence": " || ".join(evidence),
            }
        )

        variables, rows = read_csv_rows(csv_path)
        baseline_wave = infer_baseline_wave(rows, variables)
        base_rows = baseline_rows(rows, baseline_wave)
        age_variable = choose_age_variable(rows, variables)
        female_code = str(gender["female_code"])
        women_rows = [
            row
            for row in base_rows
            if derive_age(row, age_variable) is not None
            and derive_age(row, age_variable) >= 50
            and clean_value(row.get("ragender")) == female_code
        ]
        cohort_counts[cohort] = len(women_rows)

        labels = dta_variable_labels(dta_path)
        rows_for_cohort = build_candidate_rows(cohort, variables, women_rows, labels)
        candidate_rows.extend(rows_for_cohort)
        for domain in ["functional", "cognitive", "affective", "cardiometabolic_chronic"]:
            readiness_rows.append(readiness_for_domain(cohort, domain, rows_for_cohort, len(women_rows)))
        wave_readiness_rows.extend(build_wave_readiness_rows(cohort, variables, rows, age_variable, female_code, labels))

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(
        args.output_dir / "sex_coding_confirmation.csv",
        sex_rows,
        [
            "cohort",
            "dta_source",
            "dofile_source",
            "variable_label",
            "value_mapping",
            "female_code",
            "male_code",
            "raw_counts",
            "labeled_counts",
            "confirmation_status",
            "dofile_evidence",
        ],
    )
    write_csv(
        args.output_dir / "four_domain_harmonization_candidates.csv",
        candidate_rows,
        [
            "cohort",
            "domain",
            "construct",
            "variable",
            "role",
            "direction",
            "harmonization_action",
            "baseline_women50_rows",
            "nonmissing",
            "nonmissing_pct",
            "sample_values",
            "variable_label",
        ],
    )
    write_csv(
        args.output_dir / "four_domain_readiness_summary.csv",
        readiness_rows,
        [
            "cohort",
            "domain",
            "baseline_women50_rows",
            "readiness",
            "primary_variables",
            "supporting_variables",
            "note",
        ],
    )
    write_csv(
        args.output_dir / "four_domain_wave_readiness.csv",
        wave_readiness_rows,
        [
            "cohort",
            "wave",
            "women50_rows",
            "ready_or_limited_domains",
            "functional",
            "cognitive",
            "affective",
            "cardiometabolic_chronic",
        ],
    )
    build_report(
        args.output_dir / "phase2_harmonization_report.md",
        sex_rows,
        readiness_rows,
        wave_readiness_rows,
        cohort_counts,
    )


if __name__ == "__main__":
    main()
