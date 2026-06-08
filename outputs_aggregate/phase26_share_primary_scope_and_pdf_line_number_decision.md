# Phase 26 SHARE Primary Scope And PDF Line Number Decision

Date: 2026-06-01

## Recommendation

Keep SHARE out of the primary pooled baseline interpretation for the current BMC draft.

Use this hierarchy:

1. Primary manuscript claim: strict-primary cohorts only for baseline-denominator language and main inferential framing.
2. SHARE: retain as bridge-sensitivity / wave-adjusted analysis-wave evidence, with explicit footnotes and no pooled baseline wording.
3. Next data work: attempt a targeted SHARE raw/harmonized extraction only if the project needs SHARE in the primary analysis.

## Rationale

The current SHARE entry-screen women 50+ denominator is 15,814, while the usable four-domain endotype denominator is 36,006 at a later analysis wave. Treating those as the same baseline denominator would be a design error, even if the LaTeX compiles correctly.

For BMC Geriatrics, the safer and cleaner story is a conservative multi-cohort women-only endotype paper with SHARE presented as sensitivity evidence rather than as part of the same baseline pooled denominator.

## Decision Rule

Promote SHARE to primary only if all of the following are confirmed:

- A strict baseline functional domain can be constructed at the entry wave, or a prespecified wave-adjusted estimand is explicitly defended.
- `ragender` coding and wave-specific denominators are codebook-confirmed.
- The Table 1 denominator fields do not mix entry-screen people with later-wave assignments.
- Main text, figure captions and supplements use the same denominator language.

## PDF Line Number Decision

Side line numbers were removed by dropping the `lineno` class option from the Springer Nature document class:

```tex
\documentclass[referee,pdflatex,sn-vancouver-num]{sn-jnl}
```

This keeps referee formatting but avoids side line-number display in the generated PDF.

## Verification

- Current source class line: `\documentclass[referee,pdflatex,sn-vancouver-num]{sn-jnl}`
- Current PDF: `manuscript/bmc_geriatrics_submission_declarations_ready/bmc_geriatrics_main.pdf`
- Current PDF pages: 10
- Current PDF bytes: 1,387,943
- Source-only zip: `manuscript/bmc_geriatrics_declarations_ready_package.zip`
- PDF-ready zip: `manuscript/bmc_geriatrics_declarations_ready_pdf_ready_package.zip`
