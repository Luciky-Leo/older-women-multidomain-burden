from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd


RUN_DATE = "2026-06-01"


GUIDELINE_ROWS = [
    {
        "journal": "Age and Ageing",
        "publisher": "Oxford Academic / British Geriatrics Society",
        "guideline_status": "official_page_checked",
        "official_url": "https://academic.oup.com/ageing/pages/general_instructions",
        "article_type": "Research Papers",
        "word_limit": "3000",
        "word_limit_scope": "Article category table; keep main research paper concise.",
        "abstract_limit": "Abstract required; no separate numeric research-paper abstract cap captured in the checked lines.",
        "tables_figures_limit": "5",
        "references_limit": "No formal limit; recommends no more than 50.",
        "reporting_or_style": "Clinical geriatric medicine readership; strong clinical implication required; anonymized manuscript file required.",
        "data_code_policy": "Use supplementary material for additional detail; complete final policy check after target selection.",
        "current_fit_note": "Best first target if the paper is tightened around clinical gerontology and immediate implications for functional decline in older women.",
        "main_risk": "Tight 3000-word and 5-data-element ceiling; pure epidemiologic heterogeneity mapping may be rejected if clinical implications are weak.",
        "phase20_action": "Working first target after label signoff, provided the manuscript is compressed and the main figure/table set is limited.",
    },
    {
        "journal": "The Journals of Gerontology: Series A, Medical Sciences",
        "publisher": "Oxford Academic / Gerontological Society of America",
        "guideline_status": "official_page_checked",
        "official_url": "https://academic.oup.com/biomedgerontology/pages/general_instructions_2",
        "article_type": "Research Article",
        "word_limit": "5200",
        "word_limit_scope": "Includes title page, abstract, and main text; tables and figures do not count.",
        "abstract_limit": "250 words; guideline states this limit is not negotiable.",
        "tables_figures_limit": "5 data elements",
        "references_limit": "50",
        "reporting_or_style": "EQUATOR guidance recommended; AMA 11th reference style; 3-5 keywords not in the title.",
        "data_code_policy": "Strongly encourages data/software availability where ethically feasible; public datasets should be cited.",
        "current_fit_note": "Strong scientific fit for medical gerontology, multimorbidity, disability, global aging, and diverse population outcomes.",
        "main_risk": "Guidelines emphasize contemporary data and novelty; older cohort waves need a clear rationale in the cover letter.",
        "phase20_action": "Best scientific-fit target if the manuscript emphasizes medical gerontology, functional outcomes, and methodological innovation.",
    },
    {
        "journal": "BMC Geriatrics",
        "publisher": "Springer Nature / BMC",
        "guideline_status": "official_page_checked",
        "official_url": "https://bmcgeriatr.biomedcentral.com/submission-guidelines",
        "article_type": "Research article",
        "word_limit": "not_fixed_in_checked_page",
        "word_limit_scope": "Specific research-article limits were not captured from the checked page; BMC generally emphasizes completeness and article-type formatting.",
        "abstract_limit": "Structured abstract expected for research articles; final section labels require live article-type check.",
        "tables_figures_limit": "not_fixed_in_checked_page",
        "references_limit": "not_fixed_in_checked_page",
        "reporting_or_style": "Double-line spacing, line/page numbering, editable source files, data availability section, and cover letter content are specified.",
        "data_code_policy": "Data availability statement required; links and URLs should be reference-list items rather than inline text.",
        "current_fit_note": "Good fallback for transparent multi-cohort observational geriatric epidemiology with extensive supplements.",
        "main_risk": "APC/open-access requirement and lower selectivity fit compared with the top specialist targets.",
        "phase20_action": "Use as fallback if target-journal compression for Age and Ageing or JGMS would damage the methods/results.",
    },
    {
        "journal": "Journal of the American Geriatrics Society",
        "publisher": "Wiley / American Geriatrics Society",
        "guideline_status": "not_verified_tool_403",
        "official_url": "https://agsjournals.onlinelibrary.wiley.com/journal/15325415",
        "article_type": "Original investigation or equivalent",
        "word_limit": "manual_check_required",
        "word_limit_scope": "Wiley page was not accessible through the current tool session.",
        "abstract_limit": "manual_check_required",
        "tables_figures_limit": "manual_check_required",
        "references_limit": "manual_check_required",
        "reporting_or_style": "Manual browser check required before any formatting claim.",
        "data_code_policy": "Manual browser check required.",
        "current_fit_note": "Potentially attractive clinical geriatrics target, but current guideline details were not verified.",
        "main_risk": "Cannot be selected as formatted target until current instructions are checked outside the 403-blocked tool path.",
        "phase20_action": "Hold for manual guideline verification.",
    },
]


def read_csv(output_dir: Path, name: str) -> pd.DataFrame:
    path = output_dir / name
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path, low_memory=False)


def clean_cell(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).replace("\n", " ").replace("|", "/").strip()


def markdown_table(frame: pd.DataFrame, columns: list[str]) -> str:
    if frame.empty:
        return "_No rows._"
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for _, row in frame.iterrows():
        lines.append("| " + " | ".join(clean_cell(row.get(column, "")) for column in columns) + " |")
    return "\n".join(lines)


def fmt_int(value: object) -> str:
    if pd.isna(value):
        return "0"
    return f"{int(round(float(value))):,}"


def count_words(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?", text))


def section_text(text: str, heading: str) -> str:
    pattern = re.compile(rf"^## {re.escape(heading)}\s*$", flags=re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return ""
    next_match = re.search(r"^##\s+", text[match.end() :], flags=re.MULTILINE)
    if not next_match:
        return text[match.end() :]
    return text[match.end() : match.end() + next_match.start()]


def build_signoff_decision_sheet(signoff_sheet: pd.DataFrame) -> pd.DataFrame:
    required = signoff_sheet[pd.to_numeric(signoff_sheet["human_signoff_required"], errors="coerce").fillna(0).eq(1)].copy()
    required["default_conservative_option"] = required.apply(default_label_option, axis=1)
    required["phase20_required_decision"] = required.apply(required_decision, axis=1)
    required["approve_as_written"] = ""
    required["final_label_override"] = ""
    required["final_marker"] = ""
    required["reviewer_name"] = ""
    required["review_date"] = ""
    required["decision_notes"] = ""
    keep = [
        "cohort",
        "class_id",
        "class",
        "phase18_label_en_v0",
        "phase18_marker",
        "phase18_decision_v0",
        "phase18_rationale",
        "phase15_review_reason",
        "phase14_stability_flag_count",
        "phase14_flag_reasons",
        "phase20_required_decision",
        "default_conservative_option",
        "approve_as_written",
        "final_label_override",
        "final_marker",
        "reviewer_name",
        "review_date",
        "decision_notes",
    ]
    return required[keep].sort_values(["phase18_marker", "cohort", "class_id"])


def default_label_option(row: pd.Series) -> str:
    marker = str(row.get("phase18_marker", ""))
    label = str(row.get("phase18_label_en_v0", ""))
    if marker == "signoff":
        return label
    if marker == "caveat":
        return label + " [keep caveat in table note, not in final class name]"
    if marker == "hold":
        return label + " [baseline-profile only]"
    return label


def required_decision(row: pd.Series) -> str:
    marker = str(row.get("phase18_marker", ""))
    if marker == "signoff":
        return "Approve conservative burden-profile label or replace with a domain-specific clinical label."
    if marker == "caveat":
        return "Approve label with explicit sensitivity caveat; do not convert mortality signal into the class name."
    if marker == "hold":
        return "Approve baseline-only display and exclude from outcome-validation claims."
    return "Confirm label wording."


def build_signoff_packet(decision_sheet: pd.DataFrame) -> str:
    counts = decision_sheet["phase18_marker"].value_counts().rename_axis("marker").reset_index(name="n")
    lines = [
        "# Phase 20 Label Signoff Review Packet",
        "",
        f"Generated: {RUN_DATE}.",
        "",
        "This packet does not perform human signoff. It narrows the review to the labels that still require explicit author or clinical-reviewer decisions.",
        "",
        "## Signoff Counts",
        "",
        markdown_table(counts, ["marker", "n"]),
        "",
    ]
    for marker, title in [
        ("signoff", "Conservative Rename Signoff"),
        ("caveat", "Caveat Approval"),
        ("hold", "Baseline-Only Hold Approval"),
    ]:
        subset = decision_sheet[decision_sheet["phase18_marker"].eq(marker)].copy()
        if subset.empty:
            continue
        lines.extend(
            [
                f"## {title}",
                "",
                markdown_table(
                    subset[
                        [
                            "cohort",
                            "class_id",
                            "phase18_label_en_v0",
                            "phase20_required_decision",
                            "default_conservative_option",
                            "phase18_rationale",
                        ]
                    ],
                    [
                        "cohort",
                        "class_id",
                        "phase18_label_en_v0",
                        "phase20_required_decision",
                        "default_conservative_option",
                        "phase18_rationale",
                    ],
                ),
                "",
            ]
        )
    lines.extend(
        [
            "## How To Complete",
            "",
            "Fill `outputs/phase20_label_signoff_decision_template.csv`. Use `approve_as_written = yes` only when the reviewer accepts the Phase 18 label and marker. Use `final_label_override` only when the reviewer wants a different class name. Do not clear caveat or baseline-only markers unless the corresponding analysis limitation has been resolved.",
            "",
        ]
    )
    return "\n".join(lines)


def build_format_gap(clean_text: str, guideline_frame: pd.DataFrame) -> pd.DataFrame:
    total_words = count_words(clean_text)
    abstract_words = count_words(section_text(clean_text, "Abstract"))
    reference_count = len(re.findall(r"^\d+\.\s", clean_text, flags=re.MULTILINE))
    rows = []
    for row in guideline_frame.to_dict("records"):
        limit_text = row["word_limit"]
        try:
            limit = int(limit_text)
            word_gap = limit - total_words
            word_status = "fits_current_clean_draft" if word_gap >= 0 else "over_limit"
        except ValueError:
            limit = None
            word_gap = ""
            word_status = "manual_limit_check_required"
        rows.append(
            {
                "journal": row["journal"],
                "article_type": row["article_type"],
                "current_clean_draft_word_count": total_words,
                "current_abstract_word_count": abstract_words,
                "current_reference_count": reference_count,
                "word_limit": limit_text,
                "word_gap": word_gap,
                "word_status": word_status,
                "tables_figures_limit": row["tables_figures_limit"],
                "reference_limit": row["references_limit"],
                "format_action": format_action(row, total_words, abstract_words, reference_count),
            }
        )
    return pd.DataFrame(rows)


def format_action(row: dict[str, str], total_words: int, abstract_words: int, reference_count: int) -> str:
    journal = row["journal"]
    if journal == "Age and Ageing":
        return "Keep <=3000 words, <=5 tables/figures, sharpen clinical implications, and prepare anonymized manuscript file."
    if journal.startswith("The Journals of Gerontology"):
        return "Keep abstract <=250 words, main package <=5200 words including title page, <=50 refs, <=5 data elements, AMA references, 3-5 keywords."
    if journal == "BMC Geriatrics":
        return "Add BMC declarations, structured abstract headings, data availability section, line/page numbering, and cover letter policy statements."
    return "Manual guideline check required before formatting."


def build_target_memo(guidelines: pd.DataFrame, gap: pd.DataFrame) -> str:
    display_cols = [
        "journal",
        "guideline_status",
        "article_type",
        "word_limit",
        "tables_figures_limit",
        "references_limit",
        "phase20_action",
    ]
    gap_cols = [
        "journal",
        "current_clean_draft_word_count",
        "current_abstract_word_count",
        "current_reference_count",
        "word_limit",
        "word_status",
        "format_action",
    ]
    lines = [
        "# Phase 20 Target-Journal Guideline And Selection Memo",
        "",
        f"Generated: {RUN_DATE}.",
        "",
        "## Working Recommendation",
        "",
        "Use Age and Ageing as the working first target if the author team wants a clinically oriented geriatric medicine story and accepts a concise 3000-word research-paper format. Use The Journals of Gerontology: Series A, Medical Sciences as the strongest scientific-fit alternative if the team wants more room for methodological detail and a medical-gerontology readership. Keep BMC Geriatrics as the pragmatic fallback when extensive harmonization details and supplements are prioritized over selectivity.",
        "",
        "Do not format for Journal of the American Geriatrics Society yet; the Wiley author-guideline page was not verified in this tool session because it returned a 403 response.",
        "",
        "## Guideline Snapshot",
        "",
        markdown_table(guidelines[display_cols], display_cols),
        "",
        "## Current Clean Draft Gap Check",
        "",
        markdown_table(gap[gap_cols], gap_cols),
        "",
        "## Phase 20 Decision Path",
        "",
        "1. Complete the 13-row label signoff template.",
        "2. If clinical implications can be made concrete, format the next draft for Age and Ageing.",
        "3. If the methods and seven-cohort harmonization need more room, format for The Journals of Gerontology: Series A, Medical Sciences.",
        "4. If neither specialist target is practical after signoff, prepare a BMC Geriatrics version with full declarations and data availability wording.",
        "",
    ]
    return "\n".join(lines)


def build_guideline_sources_md(guidelines: pd.DataFrame) -> str:
    lines = [
        "# Phase 20 Guideline Source Snapshot",
        "",
        f"Generated: {RUN_DATE}.",
        "",
        "This file records the official pages used to build `outputs/phase20_target_guideline_snapshot.csv`. Recheck these pages immediately before submission because author instructions can change.",
        "",
        markdown_table(
            guidelines[
                [
                    "journal",
                    "guideline_status",
                    "official_url",
                    "word_limit",
                    "abstract_limit",
                    "tables_figures_limit",
                    "references_limit",
                    "data_code_policy",
                ]
            ],
            [
                "journal",
                "guideline_status",
                "official_url",
                "word_limit",
                "abstract_limit",
                "tables_figures_limit",
                "references_limit",
                "data_code_policy",
            ],
        ),
        "",
    ]
    return "\n".join(lines)


def build_report(decision_sheet: pd.DataFrame, guidelines: pd.DataFrame, gap: pd.DataFrame) -> str:
    marker_counts = decision_sheet["phase18_marker"].value_counts().rename_axis("marker").reset_index(name="n")
    guideline_counts = guidelines["guideline_status"].value_counts().rename_axis("status").reset_index(name="n")
    lines = [
        "# Phase 20 Target And Signoff Asset Report",
        "",
        f"Generated: {RUN_DATE}.",
        "",
        "## Label Review",
        "",
        markdown_table(marker_counts, ["marker", "n"]),
        "",
        "## Guideline Verification",
        "",
        markdown_table(guideline_counts, ["status", "n"]),
        "",
        "## Current Draft Format Fit",
        "",
        markdown_table(
            gap[["journal", "word_limit", "word_status", "format_action"]],
            ["journal", "word_limit", "word_status", "format_action"],
        ),
        "",
        "## Bottom Line",
        "",
        "Phase 20 creates the human signoff template and target-journal guideline snapshot. It does not finalize labels or submit-ready formatting; those require author decisions.",
        "",
    ]
    return "\n".join(lines)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def build_assets(output_dir: Path, manuscript_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    manuscript_dir.mkdir(parents=True, exist_ok=True)

    signoff = read_csv(output_dir, "phase19_label_signoff_sheet.csv")
    clean_path = manuscript_dir / "clean_manuscript_target_neutral.md"
    if not clean_path.exists():
        raise FileNotFoundError(clean_path)
    clean_text = clean_path.read_text(encoding="utf-8")

    guidelines = pd.DataFrame(GUIDELINE_ROWS)
    decision_sheet = build_signoff_decision_sheet(signoff)
    gap = build_format_gap(clean_text, guidelines)

    decision_sheet.to_csv(output_dir / "phase20_label_signoff_decision_template.csv", index=False, encoding="utf-8-sig")
    guidelines.to_csv(output_dir / "phase20_target_guideline_snapshot.csv", index=False, encoding="utf-8-sig")
    gap.to_csv(output_dir / "phase20_manuscript_format_gap_check.csv", index=False, encoding="utf-8-sig")

    write_text(output_dir / "phase20_label_signoff_review_packet.md", build_signoff_packet(decision_sheet))
    write_text(output_dir / "phase20_target_selection_memo.md", build_target_memo(guidelines, gap))
    write_text(output_dir / "phase20_guideline_sources.md", build_guideline_sources_md(guidelines))
    write_text(output_dir / "phase20_target_and_signoff_report.md", build_report(decision_sheet, guidelines, gap))
    write_text(manuscript_dir / "phase20_working_target_plan.md", build_target_memo(guidelines, gap))

    print("Phase 20 target and signoff assets complete.")
    print(f"Decision rows requiring human review: {len(decision_sheet)}")
    print(f"Official guideline rows checked: {int(guidelines['guideline_status'].eq('official_page_checked').sum())}")
    print(f"Manual guideline rows: {int(guidelines['guideline_status'].ne('official_page_checked').sum())}")
    print(f"Target memo: {output_dir / 'phase20_target_selection_memo.md'}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Phase 20 target-journal and label-signoff assets.")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    parser.add_argument("--manuscript-dir", type=Path, default=Path("manuscript"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    build_assets(args.output_dir, args.manuscript_dir)


if __name__ == "__main__":
    main()
