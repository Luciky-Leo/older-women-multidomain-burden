# Phase 16 Label Lock And Manuscript Draft Report

Run date: 2026-06-01.

## Outputs

- `outputs/phase16_locked_label_dictionary.csv`
- `outputs/phase16_table2_locked_labels.csv`
- `outputs/phase16_figure1_label_map.csv`
- `outputs/phase16_results_draft.md`
- `manuscript/results_draft.md`
- `outputs/figures/phase16_figure1_main_validation.png` and `.pdf`
- `outputs/figures/phase16_figure1_seven_cohort_sensitivity.png` and `.pdf`

## Label Status

- Locked for draft: 16.
- Review required, not locked: 10.
- Baseline-only hold: 3.

## Review-Required Labels

| cohort | class_id | label_en_final | phase15_review_reason | phase14_stability_flag_count |
| --- | --- | --- | --- | --- |
| CHARLS | CHARLS_C1 | intermediate-burden severity-aligned | generic severity-aligned label | 0 |
| CHARLS | CHARLS_C2 | elevated-burden severity-aligned | generic severity-aligned label | 0 |
| ELSA | ELSA_C3 | elevated-burden severity-aligned | generic severity-aligned label | 0 |
| ELSA | ELSA_C5 | functional-dominant high-burden | Phase 14 covariate sensitivity stability flag | 1 |
| HRS | HRS_C3 | elevated-burden severity-aligned | mortality HR drift; Phase 14 covariate sensitivity stability flag | 1 |
| HRS | HRS_C4 | affective-dominant elevated-burden | mortality HR drift; Phase 14 covariate sensitivity stability flag | 1 |
| HRS | HRS_C5 | functional-dominant high-burden | mortality HR drift; Phase 14 covariate sensitivity stability flag | 2 |
| KLoSA | KLoSA_C2 | cardiometabolic-dominant intermediate-burden | mortality HR drift; bridge sensitivity cohort; Phase 14 covariate sensitivity stability flag; Bridge-sensitivity cohort display needs explicit footnote | 1 |
| SHARE | SHARE_C4 | elevated-burden with spared functional | bridge sensitivity cohort; Phase 14 covariate sensitivity stability flag; Bridge-sensitivity cohort display needs explicit footnote | 2 |
| SHARE | SHARE_C5 | functional/cognitive-dominant high-burden | mortality HR drift; bridge sensitivity cohort; Phase 14 covariate sensitivity stability flag; Bridge-sensitivity cohort display needs explicit footnote | 3 |

## Baseline-Only Hold Labels

| cohort | class_id | label_en_final | phase16_lock_rule |
| --- | --- | --- | --- |
| LASI | LASI_C1 | intermediate-burden with spared cardiometabolic | Baseline-profile-only class; do not use as outcome-validated label. |
| LASI | LASI_C2 | cardiometabolic-dominant intermediate-burden | Baseline-profile-only class; do not use as outcome-validated label. |
| LASI | LASI_C3 | cardiometabolic-dominant elevated-burden | Baseline-profile-only class; do not use as outcome-validated label. |

## Figure Files

- Main validation Figure 1: `outputs/figures/phase16_figure1_main_validation.png` and `outputs/figures/phase16_figure1_main_validation.pdf`
- Seven-cohort sensitivity Figure 1: `outputs/figures/phase16_figure1_seven_cohort_sensitivity.png` and `outputs/figures/phase16_figure1_seven_cohort_sensitivity.pdf`

## Guardrail

Rows marked `review_required_not_locked` are deliberately carried forward with visible markers. They still need human review before final manuscript submission.
