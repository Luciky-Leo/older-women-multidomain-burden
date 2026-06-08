from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "manuscript" / "bmc_geriatrics_submission_burden_profiles_rescue"
REPORT = PKG / "MANUSCRIPT_WORKFLOW_QC_REPORT.md"
QA_DIR = PKG / "qa_workflow_submission_qc"

MAIN_TEX = PKG / "bmc_geriatrics_main.tex"
MAIN_PDF = PKG / "bmc_geriatrics_main.pdf"
REFS = PKG / "bmc_geriatrics_refs.bib"
CLAUDE_REVIEW_REQUEST = PKG / "CLAUDE_TRUE_SIMULATED_PEER_REVIEW_REQUEST_20260605.md"

SOURCE_ZIP = PKG / "bmc_geriatrics_submission_claude_revised_source_only.zip"
PDF_ZIP = PKG / "bmc_geriatrics_submission_claude_revised_pdf_ready.zip"


MAIN_FIGURES = [
    "figure1_cohort_flow_main",
    "figure2_profile_stability_guardrails_main",
    "figure3_lfo_functional_change_main",
    "figure4_harmonization_risk_matrix_main",
]

SUPPLEMENTARY_FIGURES = [
    "supplementary_figure_s1_workflow_schematic",
    "supplementary_figure_s2_cohort_denominator_validation_dashboard",
    "supplementary_figure_s3_strict_core_profile_heatmap",
    "supplementary_figure_s4_full_descriptive_profile_heatmap",
    "supplementary_figure_s5_validation_stability_guardrail_dashboard",
]

REQUIRED_ADDITIONAL_PATTERNS = {
    "26": "additional_file_26_*.csv",
    "27": "additional_file_27_*.csv",
    "27b": "additional_file_27b_*.csv",
    "28": "additional_file_28_*.csv",
    "28b": "additional_file_28b_*.csv",
    "29": "additional_file_29_*.csv",
    "29b": "additional_file_29b_*.csv",
    "30": "additional_file_30_*.csv",
    "30b": "additional_file_30b_*.csv",
    "31": "additional_file_31_*.csv",
    "32": "additional_file_32_*.csv",
}

PLACEHOLDER_PATTERNS = [
    r"\[AUTHOR INPUT REQUIRED\]",
    r"First Author",
    r"Second Author",
    r"repository URL",
    r"affiliation here",
]

AUTHOR_REQUIRED = [
    "Feifan",
    "Lu",
    "luff94@163.com",
    "Rui",
    "Guan",
    "cngreen785@163.com",
    "Changhai Hospital",
    "Naval Medical University",
]

CAPTION_REQUIRED = [
    "Panel A summarizes bootstrap ARI stability",
    "Panel B shows cross-method ARI",
    "Panel C shows log-scaled covariance condition numbers",
    "Secondary all-cause mortality Cox guardrail models",
    "Random-effects heterogeneity",
    "Additional file 32",
    "approved, downloaded, de-identified cohort datasets",
    "Supplementary Figure S1",
    "Supplementary Figure S2",
    "Supplementary Figure S3",
    "Supplementary Figure S4",
    "Supplementary Figure S5",
    "Workflow schematic showing the analysis chain",
]

STALE_ZIP_PATTERNS = [
    "_phase37",
    "_phase38",
    "_phase39",
    "figure1_cohort_tier_lock",
    "figure2_descriptive_profile_heatmap",
    "figure3_validation_and_stability_guardrails",
    "supplementary_figure_s1_profile_heatmap",
    "supplementary_figure_s2_full_descriptive_heatmap",
    "supplementary_figure_s3_validation_stability_dashboard",
    "supplementary_figure_s4_denominator_dashboard",
    "supplementary_figure_s5_workflow_schematic",
]

FORBIDDEN_ZIP_ENTRIES = [
    "CLAUDE_TRUE_SIMULATED_PEER_REVIEW_REQUEST_20260605.md",
    "CLAUDE_RE_REVIEW_REQUEST_20260605_AFTER_PHASE46.md",
    "CLAUDE_DESKTOP_STRICT_REVIEW_REQUEST.md",
    "README_BMC_Geriatrics_burden_profiles_rescue.md",
    "MANUSCRIPT_WORKFLOW.md",
    "MANUSCRIPT_WORKFLOW_QC_REPORT.md",
]


@dataclass
class CheckResult:
    severity: str
    item: str
    detail: str


class Recorder:
    def __init__(self) -> None:
        self.results: list[CheckResult] = []

    def pass_(self, item: str, detail: str) -> None:
        self.results.append(CheckResult("PASS", item, detail))

    def warn(self, item: str, detail: str) -> None:
        self.results.append(CheckResult("WARN", item, detail))

    def fail(self, item: str, detail: str) -> None:
        self.results.append(CheckResult("FAIL", item, detail))

    @property
    def has_failures(self) -> bool:
        return any(r.severity == "FAIL" for r in self.results)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def file_size(path: Path) -> str:
    return f"{path.stat().st_size:,} bytes"


def check_exists(rec: Recorder, path: Path, item: str) -> bool:
    if path.exists() and path.stat().st_size > 0:
        rec.pass_(item, f"{path.name} exists ({file_size(path)})")
        return True
    rec.fail(item, f"Missing or empty: {path}")
    return False


def check_sources(rec: Recorder) -> None:
    required = [
        MAIN_TEX,
        REFS,
        PKG / "sn-jnl.cls",
        PKG / "sn-vancouver-num.bst",
        PKG / "README_BMC_Geriatrics_burden_profiles_rescue.md",
        PKG / "MANUSCRIPT_WORKFLOW.md",
    ]
    for path in required:
        check_exists(rec, path, "Source file")


def check_tex_content(rec: Recorder) -> None:
    if not MAIN_TEX.exists():
        rec.fail("TeX content", "Main TeX file is missing")
        return
    text = read_text(MAIN_TEX)
    for pattern in PLACEHOLDER_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            rec.fail("Placeholder scan", f"Found unresolved placeholder pattern: {pattern}")
        else:
            rec.pass_("Placeholder scan", f"Absent: {pattern}")
    for phrase in AUTHOR_REQUIRED:
        if phrase in text:
            rec.pass_("Author metadata", f"Present: {phrase}")
        else:
            rec.fail("Author metadata", f"Missing: {phrase}")
    for phrase in CAPTION_REQUIRED:
        if phrase in text:
            rec.pass_("Caption text", f"Present: {phrase}")
        else:
            rec.fail("Caption text", f"Missing: {phrase}")
    for label in REQUIRED_ADDITIONAL_PATTERNS:
        if f"Additional file {label}" in text:
            rec.pass_("Additional-file list", f"TeX lists Additional file {label}")
        else:
            rec.fail("Additional-file list", f"TeX does not list Additional file {label}")


def iter_includegraphics(text: str) -> Iterable[str]:
    pattern = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")
    for match in pattern.finditer(text):
        yield match.group(1)


def check_graphics(rec: Recorder) -> None:
    if not MAIN_TEX.exists():
        return
    text = read_text(MAIN_TEX)
    included = sorted(set(iter_includegraphics(text)))
    if not included:
        rec.fail("Graphics include scan", "No includegraphics targets found")
    for name in included:
        path = PKG / name
        if path.suffix:
            check_exists(rec, path, "Graphics include")
        else:
            candidates = [path.with_suffix(ext) for ext in [".pdf", ".png", ".svg"]]
            if any(p.exists() and p.stat().st_size > 0 for p in candidates):
                found = [p.name for p in candidates if p.exists() and p.stat().st_size > 0]
                rec.pass_("Graphics include", f"{name} resolved to {', '.join(found)}")
            else:
                rec.fail("Graphics include", f"Could not resolve {name}")

    for stem in [*MAIN_FIGURES, *SUPPLEMENTARY_FIGURES]:
        check_exists(rec, PKG / f"{stem}.pdf", "Figure PDF")
        preview = PKG / f"{stem}.png"
        if preview.exists() and preview.stat().st_size > 0:
            rec.pass_("Figure PNG preview", f"{preview.name} exists ({file_size(preview)})")
        else:
            rec.warn("Figure PNG preview", f"Missing preview: {preview.name}")


def check_additional_files(rec: Recorder) -> None:
    for label, pattern in REQUIRED_ADDITIONAL_PATTERNS.items():
        matches = sorted(PKG.glob(pattern))
        if matches:
            rec.pass_("Additional file", f"{label}: {', '.join(p.name for p in matches)}")
        else:
            rec.fail("Additional file", f"No file matches {pattern}")


def extract_pdf_text(rec: Recorder) -> tuple[str, int | None]:
    if not check_exists(rec, MAIN_PDF, "Compiled PDF"):
        return "", None
    try:
        import fitz  # type: ignore
    except Exception as exc:
        rec.warn("PDF text extraction", f"PyMuPDF unavailable: {exc}")
        return "", None
    try:
        with fitz.open(MAIN_PDF) as doc:
            text = "\n".join(page.get_text() for page in doc)
            rec.pass_("PDF text extraction", f"Extracted text from {doc.page_count} pages")
            return text, doc.page_count
    except Exception as exc:
        rec.fail("PDF text extraction", f"Could not read PDF: {exc}")
        return "", None


def check_pdf(rec: Recorder) -> None:
    text, page_count = extract_pdf_text(rec)
    if page_count is not None and page_count < 8:
        rec.warn("PDF page count", f"Unexpectedly short PDF: {page_count} pages")
    if text:
        for pattern in PLACEHOLDER_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                rec.fail("PDF placeholder scan", f"Found unresolved PDF text: {pattern}")
            else:
                rec.pass_("PDF placeholder scan", f"Absent in PDF: {pattern}")
    if MAIN_PDF.exists() and MAIN_TEX.exists() and REFS.exists():
        pdf_mtime = MAIN_PDF.stat().st_mtime
        included_figures = [
            PKG / f"{stem}.pdf" for stem in [*MAIN_FIGURES, *SUPPLEMENTARY_FIGURES]
        ]
        existing_figures = [p for p in included_figures if p.exists()]
        newest_source = max(
            [MAIN_TEX.stat().st_mtime, REFS.stat().st_mtime]
            + [p.stat().st_mtime for p in existing_figures]
        )
        if pdf_mtime >= newest_source:
            rec.pass_("PDF freshness", "PDF is newer than TeX, BibTeX and included figure sources")
        else:
            rec.fail(
                "PDF freshness",
                "PDF is older than TeX, BibTeX or included figure sources; recompile before submission",
            )


def check_bibtex_log(rec: Recorder) -> None:
    blg = PKG / "bmc_geriatrics_main.blg"
    if not blg.exists():
        rec.warn("BibTeX log", "No .blg file found; compile once before final QC")
        return
    text = read_text(blg)
    warning_lines = [line.strip() for line in text.splitlines() if "Warning--" in line]
    keis_warnings = [line for line in warning_lines if "keis2026klosa" in line]
    if keis_warnings:
        rec.fail("BibTeX keis2026klosa", "; ".join(keis_warnings))
    else:
        rec.pass_("BibTeX keis2026klosa", "No warning for keis2026klosa")
    if warning_lines:
        rec.warn("BibTeX warnings", "; ".join(warning_lines))
    else:
        rec.pass_("BibTeX warnings", "No BibTeX warnings in .blg")


def zip_names(path: Path) -> set[str]:
    with zipfile.ZipFile(path) as zf:
        return {info.filename for info in zf.infolist()}


def check_zip(rec: Recorder, path: Path, required: list[str]) -> None:
    if not check_exists(rec, path, "Submission zip"):
        return
    try:
        with zipfile.ZipFile(path) as zf:
            names = {info.filename for info in zf.infolist()}
            info_by_name = {info.filename: info for info in zf.infolist()}
    except Exception as exc:
        rec.fail("Submission zip", f"Could not read {path.name}: {exc}")
        return
    for name in required:
        if name in names:
            rec.pass_("Zip content", f"{path.name} contains {name}")
            local = PKG / name
            if local.exists() and info_by_name[name].file_size == local.stat().st_size:
                rec.pass_("Zip freshness", f"{path.name}:{name} size matches current local file")
            elif local.exists():
                rec.fail(
                    "Zip freshness",
                    f"{path.name}:{name} size differs from local file; rebuild zip",
                )
        else:
            rec.fail("Zip content", f"{path.name} is missing {name}")
    stale = sorted(
        name
        for name in names
        if any(pattern in name for pattern in STALE_ZIP_PATTERNS)
    )
    if stale:
        rec.fail("Zip stale assets", f"{path.name} contains stale/duplicate entries: {', '.join(stale)}")
    else:
        rec.pass_("Zip stale assets", f"{path.name} has no stale phase or duplicate figure entries")
    internal = sorted(name for name in names if name in FORBIDDEN_ZIP_ENTRIES)
    if internal:
        rec.fail("Zip internal artifacts", f"{path.name} contains non-submission process files: {', '.join(internal)}")
    else:
        rec.pass_("Zip internal artifacts", f"{path.name} contains no Claude/README/workflow process files")


def check_zips(rec: Recorder) -> None:
    source_required = [
        "bmc_geriatrics_main.tex",
        "bmc_geriatrics_refs.bib",
        "sn-jnl.cls",
        "sn-vancouver-num.bst",
    ]
    figure_required = [f"{stem}.pdf" for stem in [*MAIN_FIGURES, *SUPPLEMENTARY_FIGURES]]
    additional_required = []
    for pattern in REQUIRED_ADDITIONAL_PATTERNS.values():
        matches = sorted(PKG.glob(pattern))
        additional_required.extend(p.name for p in matches)
    required_without_pdf = [*source_required, *figure_required, *additional_required]
    check_zip(rec, SOURCE_ZIP, required_without_pdf)
    check_zip(rec, PDF_ZIP, [*required_without_pdf, "bmc_geriatrics_main.pdf"])


def create_contact_sheet(rec: Recorder) -> None:
    if not MAIN_PDF.exists():
        rec.warn("Contact sheet", "Skipped because PDF is missing")
        return
    try:
        import fitz  # type: ignore
        from PIL import Image, ImageDraw
    except Exception as exc:
        rec.warn("Contact sheet", f"Skipped because rendering dependencies are unavailable: {exc}")
        return
    QA_DIR.mkdir(parents=True, exist_ok=True)
    output = QA_DIR / "layout_contact_sheet.png"
    try:
        thumbs = []
        with fitz.open(MAIN_PDF) as doc:
            for i, page in enumerate(doc):
                pix = page.get_pixmap(matrix=fitz.Matrix(0.35, 0.35), alpha=False)
                image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                canvas = Image.new("RGB", (image.width, image.height + 24), "white")
                canvas.paste(image, (0, 24))
                draw = ImageDraw.Draw(canvas)
                draw.text((6, 5), f"Page {i + 1}", fill="black")
                thumbs.append(canvas)
        if not thumbs:
            rec.warn("Contact sheet", "Skipped because PDF has no pages")
            return
        columns = 3
        gap = 16
        width = max(img.width for img in thumbs)
        height = max(img.height for img in thumbs)
        rows = (len(thumbs) + columns - 1) // columns
        sheet = Image.new(
            "RGB",
            (columns * width + (columns + 1) * gap, rows * height + (rows + 1) * gap),
            "white",
        )
        for idx, img in enumerate(thumbs):
            x = gap + (idx % columns) * (width + gap)
            y = gap + (idx // columns) * (height + gap)
            sheet.paste(img, (x, y))
        sheet.save(output, dpi=(180, 180))
        rec.pass_("Contact sheet", f"Wrote {output}")
    except Exception as exc:
        rec.warn("Contact sheet", f"Could not render contact sheet: {exc}")


def write_report(rec: Recorder) -> None:
    status = "FAIL" if rec.has_failures else "PASS"
    lines = [
        "# Manuscript Workflow QC Report",
        "",
        f"- Generated: {dt.datetime.now().isoformat(timespec='seconds')}",
        f"- Project root: `{ROOT}`",
        f"- Package: `{PKG}`",
        f"- Overall status: **{status}**",
        "",
        "| Severity | Item | Detail |",
        "|---|---|---|",
    ]
    for result in rec.results:
        detail = result.detail.replace("|", "\\|")
        lines.append(f"| {result.severity} | {result.item} | {detail} |")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(REPORT)


def run_qc() -> Recorder:
    rec = Recorder()
    check_sources(rec)
    check_tex_content(rec)
    check_graphics(rec)
    check_additional_files(rec)
    check_pdf(rec)
    check_bibtex_log(rec)
    check_zips(rec)
    create_contact_sheet(rec)
    write_report(rec)
    return rec


def main() -> int:
    parser = argparse.ArgumentParser(description="QC the BMC Geriatrics submission package.")
    parser.add_argument(
        "--allow-fail",
        action="store_true",
        help="Always exit 0 after writing the report.",
    )
    args = parser.parse_args()
    rec = run_qc()
    if rec.has_failures and not args.allow_fail:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
