from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path

import pandas as pd
from pandas.io.stata import StataReader


RUN_DATE = "2026-06-01"
STRICT_NAME_PATTERN = re.compile(r"^(adl|iadl)$", re.IGNORECASE)
STRICT_LABEL_PATTERN = re.compile(
    r"(activities of daily living|instrumental activities of daily living|\bADL\b|\bIADL\b)",
    re.IGNORECASE,
)
FUNCTIONAL_LABEL_PATTERN = re.compile(
    r"(adl|iadl|activities of daily living|instrumental activities|dressing|bathing|toilet|"
    r"eating|shopping|meal|housework|mobility|walking|walk|limitations? with activities)",
    re.IGNORECASE,
)
BRIDGE_ONLY_PATTERN = re.compile(r"(grip|frailty|walkcomp|chair|fall|performance)", re.IGNORECASE)


def var_id(header: str) -> str:
    return header.strip().strip('"').split(" ", 1)[0].strip()


def clean_value(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def source_layer(path: Path) -> str:
    text = str(path).lower()
    if "csv " in text or "csv" in path.parent.name.lower():
        return "cleaned_csv"
    if "working_data" in text:
        return "working_data"
    if "temp_data" in text:
        return "temp_data"
    if "harmonized share" in text:
        return "raw_harmonized_share"
    if "easyshare" in text:
        return "raw_easyshare"
    if "raw_data" in text:
        return "raw_share_release"
    if "dofile" in text:
        return "dofile"
    return "other"


def wave_from_path(path: Path) -> str:
    text = str(path)
    patterns = [
        r"share_wave(\d+)",
        r"sharew(\d+)_",
        r"Wave\s+(\d+)",
        r"wave(\d+)",
        r"_r(\d+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return ""


def classify_candidate(name: str, label: str) -> tuple[str, int]:
    text = f"{name} {label}"
    if STRICT_NAME_PATTERN.search(name) or STRICT_LABEL_PATTERN.search(text):
        return "strict_adl_iadl", 1
    if FUNCTIONAL_LABEL_PATTERN.search(text) and not BRIDGE_ONLY_PATTERN.search(text):
        return "strict_like_functional_limitation", 0
    if BRIDGE_ONLY_PATTERN.search(text):
        return "bridge_performance_or_frailty", 0
    return "not_functional", 0


def read_csv_header(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
        return [var_id(column) for column in next(csv.reader(handle))]


def summarize_values(path: Path, variables: list[str]) -> dict[str, tuple[int, str]]:
    if not variables:
        return {}
    try:
        if path.suffix.lower() == ".csv":
            frame = pd.read_csv(path, usecols=variables, dtype=str, encoding="utf-8-sig", low_memory=False)
        else:
            frame = pd.read_stata(str(path), columns=variables, convert_categoricals=False)
    except Exception:
        return {variable: (0, "") for variable in variables}
    out: dict[str, tuple[int, str]] = {}
    for variable in variables:
        if variable not in frame.columns:
            out[variable] = (0, "")
            continue
        series = frame[variable]
        nonmissing = int(series.notna().sum())
        samples = []
        for value in series.dropna().astype(str).head(50):
            cleaned = value.strip()
            if cleaned and cleaned not in samples:
                samples.append(cleaned)
            if len(samples) >= 8:
                break
        out[variable] = (nonmissing, "|".join(samples))
    return out


def inspect_stata_file(path: Path) -> list[dict[str, object]]:
    try:
        with StataReader(str(path)) as reader:
            labels = reader.variable_labels()
    except Exception:
        return []
    candidates = []
    candidate_names = []
    for name, label in labels.items():
        category, qualifies = classify_candidate(name, label)
        if category == "not_functional":
            continue
        candidate_names.append(name)
        candidates.append(
            {
                "source_path": str(path),
                "source_layer": source_layer(path),
                "wave_hint": wave_from_path(path),
                "file_type": "dta",
                "variable": name,
                "variable_label": label,
                "candidate_category": category,
                "qualifies_for_strict_functional": qualifies,
                "nonmissing": "",
                "sample_values": "",
                "has_mergeid": int("mergeid" in labels),
            }
        )
    strict_candidate_names = [
        str(row["variable"])
        for row in candidates
        if str(row["candidate_category"]) == "strict_adl_iadl"
    ]
    value_summary = summarize_values(path, strict_candidate_names)
    for row in candidates:
        nonmissing, samples = value_summary.get(str(row["variable"]), (0, ""))
        row["nonmissing"] = nonmissing
        row["sample_values"] = samples
    return candidates


def inspect_csv_file(path: Path) -> list[dict[str, object]]:
    try:
        variables = read_csv_header(path)
    except Exception:
        return []
    candidates = []
    for name in variables:
        category, qualifies = classify_candidate(name, "")
        if category == "not_functional":
            continue
        candidates.append(
            {
                "source_path": str(path),
                "source_layer": source_layer(path),
                "wave_hint": wave_from_path(path),
                "file_type": "csv",
                "variable": name,
                "variable_label": "",
                "candidate_category": category,
                "qualifies_for_strict_functional": qualifies,
                "nonmissing": "",
                "sample_values": "",
                "has_mergeid": int("mergeid" in variables),
            }
        )
    value_summary = summarize_values(path, [str(row["variable"]) for row in candidates])
    for row in candidates:
        nonmissing, samples = value_summary.get(str(row["variable"]), (0, ""))
        row["nonmissing"] = nonmissing
        row["sample_values"] = samples
    return candidates


def inspect_dofile(path: Path) -> list[dict[str, object]]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []
    rows = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        if not FUNCTIONAL_LABEL_PATTERN.search(line):
            continue
        category, qualifies = classify_candidate(line, line)
        rows.append(
            {
                "source_path": f"{path}:{line_no}",
                "source_layer": "dofile",
                "wave_hint": wave_from_path(path),
                "file_type": "do",
                "variable": "",
                "variable_label": line.strip()[:500],
                "candidate_category": category,
                "qualifies_for_strict_functional": qualifies,
                "nonmissing": "",
                "sample_values": "",
                "has_mergeid": "",
            }
        )
    return rows


def relevant_dta_paths(share_root: Path) -> list[Path]:
    paths: list[Path] = []
    preferred_dirs = [
        "Working_data",
        "Temp_data",
        "Raw_data/Harmonized SHARE",
        "Raw_data/easySHARE Release 9.0.0",
        "Raw_data/Wave 1 Release 9.0.0",
    ]
    for relative in preferred_dirs:
        folder = share_root / relative
        if folder.exists():
            paths.extend(sorted(folder.rglob("*.dta")))
    if not paths:
        paths = sorted(share_root.rglob("*.dta"))
    seen = set()
    unique = []
    for path in paths:
        key = str(path)
        if key in seen:
            continue
        seen.add(key)
        unique.append(path)
    return unique


def find_share_root(database_root: Path) -> Path:
    candidates = [
        path
        for path in database_root.rglob("*")
        if path.is_dir() and "share" in path.name.lower() and any(child.name.lower() == "working_data" for child in path.iterdir())
    ]
    if candidates:
        return sorted(candidates, key=lambda path: (len(path.parts), str(path)))[0]
    matches = [path for path in database_root.rglob("*SHARE*") if path.is_dir()]
    if not matches:
        raise FileNotFoundError(f"Could not locate SHARE root under {database_root}")
    return sorted(matches, key=lambda path: (len(path.parts), str(path)))[0]


def collect_candidates(database_root: Path, data_root: Path) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    share_root = find_share_root(database_root)
    cleaned_matches = list(data_root.rglob("share.csv"))
    for path in cleaned_matches:
        rows.extend(inspect_csv_file(path))
    for path in relevant_dta_paths(share_root):
        rows.extend(inspect_stata_file(path))
    for path in share_root.rglob("*.do"):
        rows.extend(inspect_dofile(path))
    if not rows:
        return pd.DataFrame()
    frame = pd.DataFrame(rows)
    frame["strict_wave1_evidence"] = (
        frame["wave_hint"].astype(str).eq("1")
        & frame["candidate_category"].astype(str).eq("strict_adl_iadl")
        & pd.to_numeric(frame["nonmissing"], errors="coerce").fillna(0).gt(0)
    ).astype(int)
    return frame.sort_values(
        ["qualifies_for_strict_functional", "strict_wave1_evidence", "source_layer", "source_path", "variable"],
        ascending=[False, False, True, True, True],
    ).reset_index(drop=True)


def build_decision(candidates: pd.DataFrame) -> dict[str, object]:
    if candidates.empty:
        return {
            "phase27_status": "failed_no_functional_candidates",
            "recommended_action": "keep_share_bridge_sensitivity",
            "evidence_path": "",
            "evidence_variables": "",
        }
    strict = candidates[
        candidates["strict_wave1_evidence"].eq(1)
        & candidates["has_mergeid"].astype(str).isin(["1", "1.0", "True", "true"])
    ].copy()
    layer_rank = {
        "temp_data": 0,
        "working_data": 1,
        "raw_harmonized_share": 2,
        "raw_easyshare": 3,
        "raw_share_release": 4,
    }
    grouped: dict[str, set[str]] = defaultdict(set)
    path_layer: dict[str, str] = {}
    for _, row in strict.iterrows():
        source_path = str(row["source_path"])
        grouped[source_path].add(str(row["variable"]).lower())
        path_layer[source_path] = str(row["source_layer"])
    candidate_paths = sorted(grouped, key=lambda item: (layer_rank.get(path_layer.get(item, ""), 99), item))
    for path in candidate_paths:
        variables = grouped[path]
        if {"adl", "iadl"}.issubset(variables):
            return {
                "phase27_status": "passed_strict_share_wave1_functional_available",
                "recommended_action": "promote_share_wave1_to_strict_primary_after_merge",
                "evidence_path": path,
                "evidence_variables": "adl;iadl",
            }
    return {
        "phase27_status": "failed_no_wave1_adl_iadl_pair",
        "recommended_action": "keep_share_bridge_sensitivity",
        "evidence_path": "",
        "evidence_variables": "",
    }


def write_report(path: Path, candidates: pd.DataFrame, decision: dict[str, object]) -> None:
    lines = [
        "# Phase 27 SHARE Strict Baseline Functional Domain Audit",
        "",
        f"Date: {RUN_DATE}",
        "",
        "## Decision",
        "",
        f"- Status: `{decision['phase27_status']}`",
        f"- Recommended action: `{decision['recommended_action']}`",
        f"- Evidence path: `{decision['evidence_path']}`",
        f"- Evidence variables: `{decision['evidence_variables']}`",
        "",
        "## Interpretation",
        "",
    ]
    if decision["phase27_status"] == "passed_strict_share_wave1_functional_available":
        lines.extend(
            [
                "SHARE can be upgraded from the current wave-6 bridge-only functional-domain construction to a strict wave-1 functional-domain construction, because a local SHARE wave-1 Stata file contains both `adl` and `iadl` with explicit ADL/IADL limitation labels and a mergeable `mergeid` key.",
                "",
                "Implementation rule: merge `adl` and `iadl` from the evidence file into the cleaned SHARE rows by `mergeid`, restrict the strict SHARE analysis selection to wave 1, and use `adl + iadl` as the SHARE functional score source.",
            ]
        )
    else:
        lines.extend(
            [
                "SHARE should remain bridge-sensitivity/wave-adjusted. No local wave-1 ADL/IADL pair with a mergeable key was found in the scanned cleaned, Working_data, Temp_data, raw/harmonized, and do-file sources.",
            ]
        )
    lines.extend(
        [
            "",
            "## Top Candidate Evidence",
            "",
            "| Source layer | Wave | Variable | Category | Strict | Nonmissing | Label | Source |",
            "|---|---|---|---|---:|---:|---|---|",
        ]
    )
    if candidates.empty:
        lines.append("|  |  |  |  |  |  |  |  |")
    else:
        top = candidates.head(40).fillna("")
        for row in top.to_dict("records"):
            label = str(row["variable_label"]).replace("|", "/")[:140]
            source = str(row["source_path"]).replace("|", "/")
            lines.append(
                f"| {row['source_layer']} | {row['wave_hint']} | `{row['variable']}` | "
                f"{row['candidate_category']} | {row['qualifies_for_strict_functional']} | "
                f"{row['nonmissing']} | {label} | {source} |"
            )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit SHARE strict baseline ADL/IADL functional-domain availability.")
    parser.add_argument("--database-root", required=True, type=Path)
    parser.add_argument("--data-root", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    candidates = collect_candidates(args.database_root, args.data_root)
    decision = build_decision(candidates)
    if candidates.empty:
        candidates = pd.DataFrame(
            columns=[
                "source_path",
                "source_layer",
                "wave_hint",
                "file_type",
                "variable",
                "variable_label",
                "candidate_category",
                "qualifies_for_strict_functional",
                "nonmissing",
                "sample_values",
                "has_mergeid",
                "strict_wave1_evidence",
            ]
        )
    candidates.to_csv(args.output_dir / "phase27_share_strict_functional_audit.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame([decision]).to_csv(args.output_dir / "phase27_share_strict_functional_decision.csv", index=False, encoding="utf-8-sig")
    write_report(args.output_dir / "phase27_share_strict_functional_audit.md", candidates, decision)
    print(f"Phase 27 status: {decision['phase27_status']}")
    print(f"Recommended action: {decision['recommended_action']}")


if __name__ == "__main__":
    main()
