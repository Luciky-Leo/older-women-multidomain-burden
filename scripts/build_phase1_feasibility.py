from __future__ import annotations

import argparse
import csv
import re
from collections import Counter, defaultdict
from pathlib import Path


COHORT_FILES = {
    "CHARLS": "charls.csv",
    "ELSA": "elsa.csv",
    "HRS": "hrs.csv",
    "KLoSA": "klosa.csv",
    "LASI": "lasi.csv",
    "MHAS": "mhas.csv",
    "SHARE": "share.csv",
}

AGE_CANDIDATES = ["age", "agey", "r1agey", "ragey_b", "ragey_e", "ragey_m"]
FEMALE_MARKER_PATTERN = re.compile(r"(mammog|papsm|hyster|ooph|breast|r1mammog|r1papsm|r1hystere)", re.I)

DOMAIN_CANDIDATES = {
    "functional": [
        "adltot6",
        "adl6a",
        "iadl",
        "iadlfour",
        "iadltot2_e",
        "r1adltot6",
        "r1iadltot_l",
        "frailty",
        "frailtya",
        "frailtyb",
        "gripsum",
        "gripcomp",
        "walkcomp",
        "fall",
        "fall_down",
    ],
    "cognitive": [
        "total_cognition",
        "cog_total",
        "cogtot",
        "cog27",
        "r1cog_total",
        "memory_z",
        "orient_z",
        "tcog_z_z",
        "dementia",
        "demene",
        "alzdeme",
    ],
    "affective": [
        "cesd",
        "cesd10",
        "cesd10a",
        "cesd10b",
        "r1cesd10",
        "depressive",
        "psyche",
        "r1psyche",
        "satlifez",
    ],
    "cardiometabolic_chronic": [
        "hibpe",
        "diabe",
        "hearte",
        "stroke",
        "hchole",
        "dyslipe",
        "bmi",
        "mbmi",
        "r1mbmi",
        "systo",
        "diasto",
        "r1systo",
        "r1diasto",
        "cancre",
    ],
    "inflammaging": ["bl_crp", "bl_wbc", "crp", "wbc"],
}


def var_id(header: str) -> str:
    return header.strip().strip('"').split(" ", 1)[0].strip()


def clean_value(value: str | None) -> str:
    if value is None:
        return ""
    return value.strip().strip('"')


def is_nonmissing(value: str | None) -> bool:
    v = clean_value(value)
    if not v:
        return False
    return v.upper() not in {"NA", "NAN", "NULL", "."}


def to_float(value: str | None) -> float | None:
    v = clean_value(value)
    if not is_nonmissing(v):
        return None
    try:
        return float(v)
    except ValueError:
        return None


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


def numeric_sort_key(value: str) -> tuple[int, float | str]:
    try:
        return (0, float(value))
    except ValueError:
        return (1, value)


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


def infer_female_code(rows: list[dict[str, str]], variables: list[str]) -> str:
    if "ragender" not in variables:
        return ""
    female_markers = [v for v in variables if FEMALE_MARKER_PATTERN.search(v)]
    if not female_markers:
        return ""
    row_counts: dict[str, int] = defaultdict(int)
    marker_counts: dict[str, int] = defaultdict(int)
    for row in rows:
        gender = clean_value(row.get("ragender"))
        if not gender:
            continue
        row_counts[gender] += 1
        if any(is_nonmissing(row.get(marker)) for marker in female_markers):
            marker_counts[gender] += 1
    if not marker_counts:
        return ""
    return max(marker_counts.keys(), key=lambda key: (marker_counts[key], row_counts.get(key, 0)))


def baseline_rows(rows: list[dict[str, str]], baseline_wave: str) -> list[dict[str, str]]:
    if baseline_wave == "all_rows_no_wave":
        return rows
    return [r for r in rows if clean_value(r.get("wave")) == baseline_wave]


def present_domain_variables(variables: list[str], rows: list[dict[str, str]], domain: str) -> list[str]:
    present = []
    variable_set = set(variables)
    for variable in DOMAIN_CANDIDATES[domain]:
        if variable not in variable_set:
            continue
        nonmissing = sum(is_nonmissing(r.get(variable)) for r in rows)
        if nonmissing > 0:
            present.append(f"{variable}:{nonmissing}")
    return present


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_report(path: Path, rows: list[dict[str, object]]) -> None:
    lines = [
        "# Phase 1 Feasibility Report",
        "",
        "This report starts the women-only multidomain aging endotype project from the moved project root.",
        "",
        "## Baseline Feasibility",
        "",
        "| Cohort | Baseline wave | Age variable | Likely female code | Baseline rows | Women 50+ rows | Domains with candidates |",
        "|---|---|---|---|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['cohort']} | {row['baseline_wave']} | {row['age_variable']} | {row['likely_female_code']} | "
            f"{row['baseline_rows']} | {row['female_age50plus_rows']} | {row['domains_with_candidates']} |"
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- `likely_female_code` is inferred from female-specific screening/surgery variables and must be confirmed against cohort codebooks.",
            "- Female coding is inferred from all waves, not only baseline, because some female-specific variables are wave-specific.",
            "- Age is read from the selected age variable when possible; if missing, the script derives age from interview year minus birth year.",
            "- LASI currently lacks a standard `wave` field in the cleaned CSV and is treated as `all_rows_no_wave`.",
            "- Domains are counted from candidate variables with any nonmissing values in the baseline subset.",
            "- This is a feasibility start, not the final analytic cohort definition.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    rows_out: list[dict[str, object]] = []
    for cohort, file_name in COHORT_FILES.items():
        variables, rows = read_csv_rows(args.data_root / file_name)
        baseline_wave = infer_baseline_wave(rows, variables)
        base_rows = baseline_rows(rows, baseline_wave)
        age_variable = choose_age_variable(rows, variables)
        female_code = infer_female_code(rows, variables)

        female_age50plus = []
        if age_variable and female_code:
            for row in base_rows:
                age = derive_age(row, age_variable)
                if age is not None and age >= 50 and clean_value(row.get("ragender")) == female_code:
                    female_age50plus.append(row)

        domain_status = []
        for domain in DOMAIN_CANDIDATES:
            available = present_domain_variables(variables, female_age50plus or base_rows, domain)
            if available:
                domain_status.append(f"{domain}({len(available)})")

        rows_out.append(
            {
                "cohort": cohort,
                "baseline_wave": baseline_wave,
                "age_variable": age_variable,
                "likely_female_code": female_code,
                "baseline_rows": len(base_rows),
                "female_age50plus_rows": len(female_age50plus),
                "domains_with_candidates": "; ".join(domain_status),
            }
        )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(
        args.output_dir / "phase1_baseline_feasibility.csv",
        rows_out,
        [
            "cohort",
            "baseline_wave",
            "age_variable",
            "likely_female_code",
            "baseline_rows",
            "female_age50plus_rows",
            "domains_with_candidates",
        ],
    )
    write_report(args.output_dir / "phase1_feasibility_report.md", rows_out)


if __name__ == "__main__":
    main()
