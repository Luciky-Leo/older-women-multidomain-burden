# Phase 12 Results Skeleton And Label Dictionary

Generated outputs:

- `outputs/phase12_label_dictionary_draft.csv`
- `outputs/phase12_results_claims.csv`
- `outputs/phase12_results_skeleton.md`
- `outputs/phase12_internal_zh_summary.md`

## Label Review Queue

| suggested_label_status | n |
| --- | --- |
| ready_for_manual_lock | 18 |
| requires_manual_review | 5 |
| review_generic_label | 3 |
| baseline_only_candidate | 3 |

## Claims

| claim_id | manuscript_section | claim | caveat |
| --- | --- | --- | --- |
| C1 | Sample and readiness | The current analysis identifies endotype profiles in 5 strict-primary cohorts plus 2 bridge-sensitivity cohorts. | SHARE uses a wave-adjusted sensitivity denominator; LASI is baseline-profile only for follow-up validation. |
| C2 | Endotype structure | Selected models produced 29 cohort-specific classes, with 12 high-confidence domain-dominant labels and 5 provisional labels. | Provisional labels require manual clinical review before final tables. |
| C3 | Functional validation | Functional deterioration validation included 6 cohorts, 50,084 participants, and 12,336 events. | Endotype-only models did not uniformly outperform severity tertiles across cohorts. |
| C4 | Secondary outcomes | Chronic progression validation included 6 cohorts and 22,423 events. | Chronic progression is useful as secondary validation because definitions remain broad across cohorts. |
| C5 | Mortality | Mortality validation included 6 cohorts and 12,649 deaths. | Mortality should be reported as secondary because PH diagnostics and piecewise sensitivity flagged selected terms. |
| C6 | Comparator guardrail | Four-domain continuous-score models outperformed endotype-only models for every tested endpoint-cohort row. | Frame the study as clinically interpretable heterogeneity mapping, not universal prediction superiority. |

## Endpoint Summaries

| endpoint | cohorts | n | events | severity_comparison | four_domain_comparison |
| --- | --- | --- | --- | --- | --- |
| Functional deterioration >= 0.5 SD | 6 | 50084 | 12336 | endotype_favored: 3, severity_tertile_favored: 3 | four_domain_scores_favored: 6 |
| Chronic progression >= 1 condition | 6 | 51006 | 22423 | endotype_favored: 3, severity_tertile_favored: 1, similar_by_aic: 2 | four_domain_scores_favored: 6 |
| All-cause mortality | 6 | 54362 | 12649 | endotype_favored: 2, severity_tertile_favored: 4 | four_domain_scores_favored: 6 |
