from __future__ import annotations

import argparse
import re
import shutil
import zipfile
from pathlib import Path

import pandas as pd


RUN_DATE = "2026-06-01"
TEMPLATE_FILES = ["sn-jnl.cls", "sn-vancouver-num.bst"]


def read_csv(output_dir: Path, name: str) -> pd.DataFrame:
    path = output_dir / name
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path, low_memory=False)


def clean_text(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def marker_display_note(marker: str) -> str:
    if marker == "caveat":
        return "Sensitivity caveat retained; interpret as a baseline domain-profile label and do not use mortality signal to define the class."
    if marker == "hold":
        return "Baseline-profile only; excluded from follow-up outcome-validation claims in the current cleaned CSV pass."
    return ""


def bmc_display_label(row: pd.Series) -> str:
    label = clean_text(row.get("phase18_label_en_v0", row.get("label_en_final", "")))
    return label


def build_signoff_proposal(signoff: pd.DataFrame) -> pd.DataFrame:
    proposal = signoff.copy()
    proposal["proposed_decision"] = "approve_as_written_conservative_default"
    proposal["proposed_final_label"] = proposal["phase18_label_en_v0"].map(clean_text)
    proposal["proposed_final_marker"] = proposal["phase18_marker"].map(clean_text).replace({"signoff": "none"})
    proposal["author_confirmation_required"] = 1
    proposal["phase22_status"] = "proposal_only_not_human_signoff"
    proposal["phase22_note"] = proposal["phase18_marker"].map(clean_text).map(marker_display_note)
    proposal.loc[proposal["phase18_marker"].eq("signoff"), "phase22_note"] = (
        "Conservative burden-profile rename proposed for approval; no signoff marker would be shown after author confirmation."
    )
    keep = [
        "cohort",
        "class_id",
        "class",
        "phase18_label_en_v0",
        "phase18_marker",
        "phase18_decision_v0",
        "phase18_rationale",
        "phase20_required_decision",
        "default_conservative_option",
        "proposed_decision",
        "proposed_final_label",
        "proposed_final_marker",
        "author_confirmation_required",
        "phase22_status",
        "phase22_note",
    ]
    return proposal[keep].sort_values(["phase18_marker", "cohort", "class_id"])


def build_bmc_class_profiles(table2: pd.DataFrame, proposal: pd.DataFrame) -> pd.DataFrame:
    proposal_short = proposal[
        ["cohort", "class_id", "proposed_final_label", "proposed_final_marker", "phase22_note"]
    ].copy()
    out = table2.merge(proposal_short, on=["cohort", "class_id"], how="left")
    out["bmc_label"] = out.apply(bmc_display_label, axis=1)
    out.loc[out["proposed_final_label"].notna(), "bmc_label"] = out.loc[
        out["proposed_final_label"].notna(), "proposed_final_label"
    ]
    out["bmc_label_status"] = out["proposed_final_marker"].fillna("none").replace("", "none")
    out["bmc_label_note"] = out["phase22_note"].fillna("")
    keep = [
        "analysis_set",
        "analysis_tier",
        "cohort",
        "class_id",
        "class",
        "class_n",
        "class_pct",
        "bmc_label",
        "bmc_label_status",
        "bmc_label_note",
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
        "mortality_drift_flag",
        "phase18_decision_v0",
        "phase18_rationale",
    ]
    existing = [col for col in keep if col in out.columns]
    return out[existing].sort_values(["cohort", "class_id"])


def polish_tex_for_review_ready(tex: str) -> str:
    tex = tex.replace(
        "Labels with mortality drift, covariate-sensitivity flags or baseline-only status require final author signoff before submission.",
        "Class labels were retained using conservative domain-profile language. Classes with sensitivity concerns or baseline-only status are interpreted descriptively and are not used to strengthen mortality-driven claims.",
    )
    tex = tex.replace(
        "The selected classes were labeled using conservative domain-profile language. Class labels were retained using conservative domain-profile language.",
        "The selected classes were labeled using conservative domain-profile language.",
    )
    tex = tex.replace(
        "Final submission should occur only after the remaining label signoff decisions, data-use statements and journal-specific declarations are completed.",
        "Final submission should occur only after data-use statements, declarations and author metadata are completed.",
    )
    tex = tex.replace(
        "Additional file 3: Label signoff decision template. CSV file for pre-submission author review; this file should be removed from the submission package after label decisions are finalized.\n\n",
        "",
    )
    return tex


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def copy_file(src: Path, dst: Path) -> None:
    if not src.exists():
        raise FileNotFoundError(src)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def zip_package(package_dir: Path, zip_path: Path) -> None:
    with zipfile.ZipFile(zip_path, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(package_dir.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(package_dir)
            if "build" in rel.parts:
                continue
            archive.write(path, arcname=str(rel).replace("\\", "/"))


def count_words(text: str) -> int:
    stripped = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{[^{}]*\})?", " ", text)
    return len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?", stripped))


def build_remaining_items() -> str:
    return f"""# Phase 22 BMC Remaining Author Items

Generated: {RUN_DATE}.

## Still Required Before Actual Submission

1. Author confirmation of the conservative label proposal in `outputs/phase22_conservative_label_signoff_proposal.csv`.
2. Complete BMC declarations in `bmc_geriatrics_main.tex`:
   - Ethics approval and consent to participate.
   - Availability of data and materials.
   - Competing interests.
   - Funding.
   - Authors' contributions.
   - Acknowledgements.
3. Confirm source cohort data-use language for CHARLS, ELSA, HRS, KLoSA, LASI, MHAS and SHARE.
4. Decide whether an AI-assisted drafting disclosure is needed under current Springer Nature policy and the author team's actual workflow.
5. Compile the LaTeX source through Overleaf, Springer/BMC submission system, or a local TeX runtime.

## What Changed In Phase 22

- Conservative label decisions were proposed but not treated as human signoff.
- Additional file 3 was removed from the BMC review-ready zip.
- Additional file 1 now uses cleaned BMC label columns and moves caveat/baseline-only information into explanatory note columns.
"""


def build_report(package_dir: Path, zip_path: Path, proposal: pd.DataFrame, tex_word_count: int) -> str:
    marker_counts = proposal["proposed_final_marker"].value_counts().rename_axis("marker").reset_index(name="n")
    lines = [
        "# Phase 22 BMC Review-Ready Package Report",
        "",
        f"Generated: {RUN_DATE}.",
        "",
        "## Package",
        "",
        f"- Review-ready package directory: `{package_dir}`",
        f"- Review-ready zip: `{zip_path}`",
        f"- Approximate TeX word count: {tex_word_count}",
        "",
        "## Conservative Label Proposal",
        "",
        markdown_table(marker_counts, ["marker", "n"]),
        "",
        "## Status",
        "",
        "The package is cleaner than Phase 21 for BMC review: it removes the internal label-signoff template from the zip and uses cleaned label columns in Additional file 1. It is still not submission-final because author confirmation, declarations and data-use wording remain incomplete.",
        "",
    ]
    return "\n".join(lines)


def markdown_table(frame: pd.DataFrame, columns: list[str]) -> str:
    if frame.empty:
        return "_No rows._"
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for _, row in frame.iterrows():
        lines.append("| " + " | ".join(str(row.get(col, "")).replace("|", "/") for col in columns) + " |")
    return "\n".join(lines)


def build_package(output_dir: Path, manuscript_dir: Path) -> None:
    phase21_dir = manuscript_dir / "bmc_geriatrics_submission"
    package_dir = manuscript_dir / "bmc_geriatrics_submission_review_ready"
    package_dir.mkdir(parents=True, exist_ok=True)

    signoff = read_csv(output_dir, "phase20_label_signoff_decision_template.csv")
    table2 = read_csv(output_dir, "phase18_table2_final_labels_v0.csv")
    validation = read_csv(output_dir, "phase11_table3_outcome_validation_summary.csv")

    proposal = build_signoff_proposal(signoff)
    bmc_profiles = build_bmc_class_profiles(table2, proposal)

    source_tex = (phase21_dir / "bmc_geriatrics_main.tex").read_text(encoding="utf-8")
    review_tex = polish_tex_for_review_ready(source_tex)

    for name in TEMPLATE_FILES + [
        "bmc_geriatrics_refs.bib",
        "figure1_main_validation.png",
        "figure1_seven_cohort_sensitivity.png",
        "bmc_geriatrics_cover_letter.md",
    ]:
        copy_file(phase21_dir / name, package_dir / name)

    write_text(package_dir / "bmc_geriatrics_main.tex", review_tex)
    bmc_profiles.to_csv(package_dir / "additional_file_1_class_profiles.csv", index=False, encoding="utf-8-sig")
    validation.to_csv(package_dir / "additional_file_2_outcome_validation.csv", index=False, encoding="utf-8-sig")
    write_text(package_dir / "README_BMC_Geriatrics_review_ready.md", build_remaining_items())

    proposal.to_csv(output_dir / "phase22_conservative_label_signoff_proposal.csv", index=False, encoding="utf-8-sig")
    bmc_profiles.to_csv(output_dir / "phase22_bmc_class_profiles_review_ready.csv", index=False, encoding="utf-8-sig")
    write_text(output_dir / "phase22_bmc_remaining_author_items.md", build_remaining_items())

    zip_path = manuscript_dir / "bmc_geriatrics_review_ready_package.zip"
    zip_package(package_dir, zip_path)

    manifest = pd.DataFrame(
        [
            {"file": path.name, "bytes": path.stat().st_size, "role": file_role(path.name)}
            for path in sorted(package_dir.iterdir())
            if path.is_file()
        ]
    )
    manifest.to_csv(output_dir / "phase22_bmc_review_ready_manifest.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame([{"zip_path": str(zip_path), "bytes": zip_path.stat().st_size}]).to_csv(
        output_dir / "phase22_bmc_review_ready_zip.csv", index=False, encoding="utf-8-sig"
    )
    tex_word_count = count_words(review_tex)
    pd.DataFrame(
        [
            {"metric": "review_ready_tex_word_count_approx", "value": tex_word_count},
            {"metric": "label_proposal_rows", "value": len(proposal)},
            {"metric": "author_confirmation_required_rows", "value": int(proposal["author_confirmation_required"].sum())},
            {"metric": "zip_path", "value": str(zip_path)},
        ]
    ).to_csv(output_dir / "phase22_bmc_review_ready_summary.csv", index=False, encoding="utf-8-sig")
    write_text(output_dir / "phase22_bmc_review_ready_report.md", build_report(package_dir, zip_path, proposal, tex_word_count))

    print("Phase 22 BMC review-ready package complete.")
    print(f"Package directory: {package_dir}")
    print(f"Zip package: {zip_path}")
    print(f"Label proposal rows: {len(proposal)}")
    print(f"Author confirmation required rows: {int(proposal['author_confirmation_required'].sum())}")
    print(f"Approx TeX word count: {tex_word_count}")


def file_role(name: str) -> str:
    if name.endswith(".tex"):
        return "main_latex_manuscript"
    if name.endswith(".bib"):
        return "bibtex_references"
    if name.startswith("sn-"):
        return "springer_nature_template_file"
    if name.startswith("figure"):
        return "figure_file"
    if name.startswith("additional_file"):
        return "additional_file"
    if "cover_letter" in name:
        return "cover_letter"
    if name.startswith("README"):
        return "package_notes"
    return "supporting_file"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build BMC Geriatrics review-ready package after conservative label proposal.")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    parser.add_argument("--manuscript-dir", type=Path, default=Path("manuscript"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    build_package(args.output_dir, args.manuscript_dir)


if __name__ == "__main__":
    main()
