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

DOMAIN_PATTERNS = {
    "id_time_death": re.compile(
        r"^(id|hhid|pid|mergeid|prim|wave|inw|iw|rad|rage|age|r1age|r1iw|iwy|iwm|rabyear|rabmonth)",
        re.I,
    ),
    "female_specific": re.compile(
        r"(mammog|papsm|hyster|preg|birth|child|breast|cerv|uter|ovary|ooph|menop|menar|reproductive)",
        re.I,
    ),
    "functional": re.compile(
        r"(adl|iadl|walk|dress|bath|eat|bed|toil|chair|clim|stoop|lift|grip|gait|frail|fall|balance|hearing)",
        re.I,
    ),
    "cognitive": re.compile(
        r"(cog|mem|recall|orient|word|serial|demen|alzh|memory)",
        re.I,
    ),
    "affective": re.compile(
        r"(cesd|depress|psyche|psych|sleep|lonel|happy|satlife|lifein)",
        re.I,
    ),
    "cardiometabolic_chronic": re.compile(
        r"(hibp|hyper|diab|heart|stroke|chole|dyslip|bmi|height|weight|waist|bp|systo|diasto|pulse|chol|hdl|ldl|glucose|tyg)",
        re.I,
    ),
    "lifestyle_covariate": re.compile(
        r"(smok|drink|alco|act|vgact|mdact|ltact|educ|rural|urban|income|wealth|water)",
        re.I,
    ),
    "inflammaging": re.compile(
        r"(crp|wbc|lymph|neut|plate|hemoglobin|albumin|bun|creat)",
        re.I,
    ),
    "cancer_secondary": re.compile(r"(cancr|cancer)", re.I),
}

KEY_VARIABLES = {
    "time": ["wave", "iwstat", "radyear", "radmonth", "age", "agey", "r1agey", "ragey_b", "ragey_e"],
    "sex": ["ragender"],
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
        "sleep_night",
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
    "female_specific": [
        "mammog",
        "r1mammog",
        "papsm",
        "r1papsm",
        "hystere",
        "r1hystere",
        "oophos1y",
        "oophos",
        "child",
        "hchild",
        "r1child",
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


def infer_gender_mapping(rows: list[dict[str, str]], variables: list[str]) -> str:
    if "ragender" not in variables:
        return "unknown_no_ragender"
    female_markers = [
        v
        for v in variables
        if re.search(r"(mammog|papsm|hyster|ooph|breast|r1mammog|r1papsm|r1hystere)", v, re.I)
    ]
    if not female_markers:
        return "unknown_no_marker"
    marker_counts: dict[str, int] = defaultdict(int)
    row_counts: dict[str, int] = defaultdict(int)
    for row in rows:
        g = clean_value(row.get("ragender"))
        if not g:
            continue
        row_counts[g] += 1
        if any(is_nonmissing(row.get(v)) for v in female_markers):
            marker_counts[g] += 1
    if not marker_counts:
        return "unknown_markers_empty"
    ranked = sorted(marker_counts.items(), key=lambda kv: (kv[1], row_counts.get(kv[0], 0)), reverse=True)
    return f"likely_female={ranked[0][0]}; marker_nonmissing=" + ";".join(
        f"{k}:{v}/{row_counts.get(k, 0)}" for k, v in sorted(marker_counts.items())
    )


def read_csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
        reader = csv.reader(handle)
        header_raw = next(reader)
        variables = [var_id(h) for h in header_raw]
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


def summarize_cohort(cohort: str, variables: list[str], rows: list[dict[str, str]], file_name: str) -> dict[str, object]:
    waves = sorted({clean_value(r.get("wave")) for r in rows if clean_value(r.get("wave"))}, key=lambda x: (len(x), x))
    gender_counts = Counter(clean_value(r.get("ragender")) for r in rows if clean_value(r.get("ragender")))
    age_candidates = [v for v in ["age", "agey", "r1agey", "ragey_b", "ragey_e"] if v in variables]
    age_nonmissing = {v: sum(is_nonmissing(r.get(v)) for r in rows) for v in age_candidates}
    return {
        "cohort": cohort,
        "file": file_name,
        "rows": len(rows),
        "columns": len(variables),
        "waves": ";".join(waves[:30]),
        "ragender_counts": ";".join(f"{k}:{v}" for k, v in sorted(gender_counts.items())),
        "gender_mapping_inference": infer_gender_mapping(rows, variables),
        "age_variables_nonmissing": ";".join(f"{k}:{v}" for k, v in age_nonmissing.items()),
    }


def domain_inventory(cohort: str, variables: list[str], rows: list[dict[str, str]]) -> list[dict[str, object]]:
    out = []
    for variable in variables:
        matched = [name for name, pattern in DOMAIN_PATTERNS.items() if pattern.search(variable)]
        if not matched:
            continue
        nonmissing = sum(is_nonmissing(r.get(variable)) for r in rows)
        unique_values = []
        seen = set()
        for row in rows:
            value = clean_value(row.get(variable))
            if is_nonmissing(value) and value not in seen:
                seen.add(value)
                unique_values.append(value)
            if len(unique_values) >= 8:
                break
        for domain in matched:
            out.append(
                {
                    "cohort": cohort,
                    "domain": domain,
                    "variable": variable,
                    "nonmissing": nonmissing,
                    "nonmissing_pct": round(nonmissing / max(len(rows), 1) * 100, 2),
                    "sample_values": "|".join(unique_values),
                }
            )
    return out


def key_matrix(cohort: str, variables: list[str], rows: list[dict[str, str]]) -> list[dict[str, object]]:
    variable_set = set(variables)
    out = []
    for domain, candidates in KEY_VARIABLES.items():
        for variable in candidates:
            present = variable in variable_set
            nonmissing = sum(is_nonmissing(r.get(variable)) for r in rows) if present else 0
            out.append(
                {
                    "cohort": cohort,
                    "domain": domain,
                    "variable": variable,
                    "present": int(present),
                    "nonmissing": nonmissing,
                    "nonmissing_pct": round(nonmissing / max(len(rows), 1) * 100, 2),
                }
            )
    return out


def write_markdown_report(output_dir: Path, cohort_rows: list[dict[str, object]], key_rows: list[dict[str, object]]) -> None:
    domains = ["functional", "cognitive", "affective", "cardiometabolic_chronic", "female_specific", "inflammaging"]
    by_cohort_domain: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in key_rows:
        if row["present"]:
            by_cohort_domain[(str(row["cohort"]), str(row["domain"]))].append(row)

    lines = [
        "# Variable Availability Report",
        "",
        "Generated from cleaned CSV headers and nonmissing counts. Source data were not modified.",
        "",
        "## Cohort Summary",
        "",
        "| Cohort | Rows | Columns | Waves | Gender mapping inference |",
        "|---|---:|---:|---|---|",
    ]
    for row in cohort_rows:
        lines.append(
            f"| {row['cohort']} | {row['rows']} | {row['columns']} | {row['waves']} | {row['gender_mapping_inference']} |"
        )
    lines.extend(["", "## Key Domain Availability", ""])
    for cohort in [row["cohort"] for row in cohort_rows]:
        lines.append(f"### {cohort}")
        lines.append("")
        lines.append("| Domain | Available key variables |")
        lines.append("|---|---|")
        for domain in domains:
            items = by_cohort_domain.get((str(cohort), domain), [])
            label = ", ".join(f"{r['variable']} ({r['nonmissing_pct']}%)" for r in items) if items else "None in candidate list"
            lines.append(f"| {domain} | {label} |")
        lines.append("")

    lines.extend(
        [
            "## Immediate Interpretation",
            "",
            "- The shared-data strength is longitudinal aging phenotype analysis, not molecular multiomics.",
            "- Functional and cardiometabolic variables are broadly available.",
            "- Cognitive and affective variables are available in several cohorts but need harmonization checks before modeling.",
            "- Inflammaging is not a seven-cohort common domain in the cleaned CSVs; treat it as a CHARLS exploratory module unless more biomarker variables are found.",
            "- Female-specific variables are uneven and should be secondary descriptors, not the central exposure.",
        ]
    )
    (output_dir / "variable_availability_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    cohort_rows: list[dict[str, object]] = []
    domain_rows: list[dict[str, object]] = []
    key_rows: list[dict[str, object]] = []

    for cohort, file_name in COHORT_FILES.items():
        path = args.data_root / file_name
        if not path.exists():
            raise FileNotFoundError(f"Missing expected cohort file: {path}")
        variables, rows = read_csv_rows(path)
        cohort_rows.append(summarize_cohort(cohort, variables, rows, file_name))
        domain_rows.extend(domain_inventory(cohort, variables, rows))
        key_rows.extend(key_matrix(cohort, variables, rows))

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(
        args.output_dir / "cohort_summary.csv",
        cohort_rows,
        ["cohort", "file", "rows", "columns", "waves", "ragender_counts", "gender_mapping_inference", "age_variables_nonmissing"],
    )
    write_csv(
        args.output_dir / "domain_variable_inventory.csv",
        domain_rows,
        ["cohort", "domain", "variable", "nonmissing", "nonmissing_pct", "sample_values"],
    )
    write_csv(
        args.output_dir / "key_variable_matrix.csv",
        key_rows,
        ["cohort", "domain", "variable", "present", "nonmissing", "nonmissing_pct"],
    )
    write_markdown_report(args.output_dir, cohort_rows, key_rows)


if __name__ == "__main__":
    main()
