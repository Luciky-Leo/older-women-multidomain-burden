# Phase 24 PDF Compile Runtime Diagnosis

Date: 2026-06-01

## Target source

- Main TeX source: `manuscript/bmc_geriatrics_submission_declarations_ready/bmc_geriatrics_main.tex`
- Target journal/template: BMC Geriatrics / Springer Nature `sn-jnl` LaTeX template

## Result

Local PDF compilation is now available in the WSL execution environment.

## Initial detected state

The initial LaTeX doctor check reported:

- `latexmk`: missing
- `pdflatex`: missing
- `kpsewhich`: missing
- `xelatex`: missing
- `lualatex`: missing
- `biber`: missing
- bundled or PATH `tectonic`: missing

Smoke tests were not attempted initially because neither `latexmk` nor `pdflatex` was available.

## Installed runtime

Installed and repaired a Codex-managed TeX runtime under:

- TeX Live root: `/home/luff/.cache/codex-runtimes/codex-texlive/full`
- TeX Live bin: `/home/luff/.cache/codex-runtimes/codex-texlive/full/bin/x86_64-linux`
- Tectonic bin: `/home/luff/.cache/codex-runtimes/tectonic/bin/tectonic`

Verified tools:

- `latexmk`: TeX Live 2026, Latexmk 4.88
- `pdflatex`: TeX Live 2026, pdfTeX 1.40.29
- `kpsewhich`: kpathsea 6.4.2
- `biber`: available
- `lualatex`: available
- `tectonic`: 0.16.9

The TeX Live install was interrupted by a long-running timeout, then repaired by refreshing filename databases, manually generating `pdflatex.fmt`, reinstalling incomplete packages, and installing `collection-latexextra`.

## Compile result

The BMC/Springer Nature LaTeX package was rendered successfully.

- Generated PDF: `manuscript/bmc_geriatrics_submission_declarations_ready/bmc_geriatrics_main.pdf`
- Current no-line-number PDF size after Phase 26 correction: 1,387,943 bytes
- Current no-line-number PDF pages after Phase 26 correction: 10
- Source-only zip rebuilt: `manuscript/bmc_geriatrics_declarations_ready_package.zip`
- PDF-ready zip created: `manuscript/bmc_geriatrics_declarations_ready_pdf_ready_package.zip`

## Source compatibility fixes

Two minimal TeX source fixes were needed:

- Added `\usepackage{amsmath}` because `sn-jnl.cls` calls `\allowdisplaybreaks`.
- Escaped the outcome table header from `Event %` to `Event \%`.

## Remaining warnings

The PDF compiles, but the log still reports layout warnings:

- Overfull table boxes in the two wide tables.
- Main figure float is larger than the page by approximately 81.8 pt.
- Minor font size substitution warnings.

These are layout-quality issues, not runtime blockers.

## Phase 25 note

Phase 25 corrected denominator-coding wording for SHARE. The template/runtime diagnosis in this file remains valid, but the current PDF should be interpreted together with `outputs/phase25_denominator_coding_correction_report.md`.

## Phase 26 note

Phase 26 removed the `lineno` document-class option, so the current PDF should not display side line numbers.

## Recompile command

To recompile:

```bash
cd /mnt/e/Reserch/Older\ women/manuscript/bmc_geriatrics_submission_declarations_ready
PATH=/home/luff/.cache/codex-runtimes/codex-texlive/full/bin/x86_64-linux:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
latexmk -pdf bmc_geriatrics_main.tex
```
