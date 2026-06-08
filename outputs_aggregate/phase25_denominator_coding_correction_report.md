# Phase 25 Denominator Coding Correction Report

Date: 2026-06-01

## Issue

The previous BMC PDF compiled correctly, but Table 1 and the surrounding text could be misread as using one pooled baseline denominator. This was a source denominator-coding problem, not a LaTeX-template problem.

The clearest risk was SHARE: the Phase 1 source-screen denominator is 15,814 women aged 50+ at the entry screen, while the endotype analysis uses a later wave-adjusted bridge-sensitivity denominator of 36,006 assignments. These two numbers must not be presented as the same baseline denominator.

## SHARE row now protected

| cohort | analysis_tier | wave | baseline_women_age50plus_n | complete_four_domain_n | selected_endotype_n |
| --- | --- | --- | --- | --- | --- |
| SHARE | bridge_sensitivity | 6 | 15814 | 36006 | 36006 |

## Corrections made

- Updated scripts/build_phase21_bmc_geriatrics_template_package.py so future BMC package generation preserves the denominator distinction.
- Updated scripts/build_phase23_bmc_declarations_completion_pack.py so rebuilt source packages are clean and exclude generated PDF/aux/log files.
- Reworded the abstract Results sentence to call strict/bridge counts analysis-wave assignments, not a pooled baseline denominator.
- Reworded the Results opening paragraph to state that SHARE uses a later analysis wave.
- Renamed Table 1 columns from baseline-style wording to denominator-safe wording:
  - Source-screen women 50+
  - Analysis-wave complete domains
  - Endotype assignments
- Expanded the Table 1 footnote to state that SHARE's 36,006 assignments are not part of the 15,814 earliest-wave source-screen denominator.
- Kept the minimal TeX source fixes needed for compilation: `amsmath` and escaped `Event \%`.

## Verification

- Current TeX contains denominator-safe SHARE wording: yes.
- Current PDF was regenerated: manuscript/bmc_geriatrics_submission_declarations_ready/bmc_geriatrics_main.pdf.
- Current PDF pages: 10.
- Current PDF bytes after Phase 26 line-number removal: 1387943.
- Source-only zip after Phase 26 rebuild: manuscript/bmc_geriatrics_declarations_ready_package.zip, 2433578 bytes, excludes PDF.
- PDF-ready zip after Phase 26 rebuild: manuscript/bmc_geriatrics_declarations_ready_pdf_ready_package.zip, 3715481 bytes, includes PDF.
- Phase 26 removed the `lineno` document-class option; see `outputs/phase26_share_primary_scope_and_pdf_line_number_decision.md`.

## Remaining data decision

This correction makes the manuscript honest about denominator coding. It does not resolve the deeper analysis decision: SHARE should remain bridge-sensitivity unless the raw/harmonized extraction can construct a strict baseline functional domain at the entry wave or a defensible prespecified wave-adjusted estimand.
