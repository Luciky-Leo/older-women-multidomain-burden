# Phase 15 Manuscript Integration Report

Run date: 2026-06-01.

## Outputs

- `outputs/phase15_results_skeleton_integrated.md`
- `manuscript/results_skeleton.md`
- `outputs/phase15_supplement_table_shell.csv`
- `manuscript/supplement_table_shell.md`
- `outputs/phase15_label_lock_queue.csv`
- `outputs/phase15_display_policy_recommendation.csv`
- `outputs/phase15_novelty_refresh_sources.csv`
- `outputs/phase15_novelty_refresh_report.md`

## Key Results

- Functional covariate-sensitivity comparison rows: 12.
- Mortality covariate-sensitivity comparison rows: 12.
- Phase 14 stability-flagged class labels: 7.
- Label queue status counts: {'ready_for_manual_lock': 16, 'manual_review_required': 10, 'hold_baseline_only': 3}.
- Novelty refresh sources logged: 7.

## Display Decision

| cohort | analysis_tier | phase15_display_recommendation | figure1_policy | condition_for_main_display |
| --- | --- | --- | --- | --- |
| CHARLS | strict_primary | main_results | main_panel | Use in main Results and main Figure 1 with standard strict-primary denominators. |
| ELSA | strict_primary | main_results | main_panel | Use in main Results and main Figure 1 with standard strict-primary denominators. |
| HRS | strict_primary | main_results | main_panel | Use in main Results and main Figure 1 with standard strict-primary denominators. |
| MHAS | strict_primary | main_results | main_panel | Use in main Results and main Figure 1 with standard strict-primary denominators. |
| KLoSA | bridge_sensitivity | sensitivity_or_supplement_default | sensitivity_panel_default | May appear in the main figure only with an explicit bridge-sensitivity or wave-adjusted denominator footnote. |
| SHARE | bridge_sensitivity | sensitivity_or_supplement_default | sensitivity_panel_default | May appear in the main figure only with an explicit bridge-sensitivity or wave-adjusted denominator footnote. |
| LASI | strict_primary | baseline_profile_table_only | table_or_supplement_profile_only | Do not use in outcome-validation panels until follow-up validation is available. |
