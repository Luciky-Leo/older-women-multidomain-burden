# Phase 32B Decoupled Leave-Functional-Domain-Out Validation

Date: 2026-06-02

## Design

Profiles were rebuilt using only cognitive, affective and cardiometabolic/chronic disease baseline domains.
Baseline functional score was not used in profile construction. Functional deterioration was then evaluated as a follow-up outcome.

This design is a leakage-control sensitivity, not a full external validation design.

## LFO Profile Model Selection

| analysis_set | cohort | n | n_classes | bic | min_class_pct | entropy_separation | mean_max_posterior | profile_interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| functional_bridge_earliest_sensitivity | KLoSA | 4081 | 3 | -8425.05 | 17.45 | 0.9999 | 1.0 | domain_specific |
| strict_earliest_primary | CHARLS | 6019 | 4 | -10335.86 | 9.54 | 0.9511 | 0.9705 | domain_specific |
| strict_earliest_primary | ELSA | 6105 | 5 | -15611.4 | 5.68 | 0.9109 | 0.9393 | domain_specific |
| strict_earliest_primary | HRS | 10210 | 4 | -29806.29 | 7.78 | 1.0 | 1.0 | domain_specific |
| strict_earliest_primary | LASI | 27438 | 3 | -70697.97 | 13.53 | 0.9999 | 1.0 | domain_specific |
| strict_earliest_primary | MHAS | 6741 | 3 | -17709.71 | 13.26 | 1.0 | 1.0 | domain_specific |
| strict_earliest_primary | SHARE | 15721 | 4 | -49788.57 | 6.67 | 1.0 | 1.0 | domain_specific |

## Functional Validation Comparison

| cohort | validation_n | validation_events | aic_lfo_profile_age | auc_lfo_profile_age | aic_three_domain_scores_age | auc_three_domain_scores_age | delta_aic_three_domain_scores_minus_lfo_profile | delta_auc_lfo_profile_minus_three_domain_scores | max_lfo_profile_or | phase32b_evidence_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| KLoSA | 3834 | 1144.0 | 4645.739 | 0.5604 | 4636.58 | 0.5722 | -9.159 | -0.0118 | 1.3301 | bridge_sensitivity_only |
| CHARLS | 5691 | 1766.0 | 6744.133 | 0.6409 | 6682.224 | 0.6584 | -61.909 | -0.0175 | 2.1196 | three_domain_scores_fit_better_than_profiles |
| ELSA | 5153 | 1316.0 | 5148.332 | 0.7405 | 5097.587 | 0.7505 | -50.745 | -0.01 | 1.7432 | three_domain_scores_fit_better_than_profiles |
| HRS | 9431 | 3546.0 | 11518.56 | 0.6925 | 11397.243 | 0.7058 | -121.317 | -0.0133 | 1.9023 | three_domain_scores_fit_better_than_profiles |
| MHAS | 5443 | 1437.0 | 5966.819 | 0.67 | 5951.143 | 0.6727 | -15.676 | -0.0027 | 2.1044 | three_domain_scores_fit_better_than_profiles |
| SHARE | 12205 | 1525.0 | 8674.965 | 0.6736 | 8005.592 | 0.748 | -669.373 | -0.0744 | 3.3074 | three_domain_scores_fit_better_than_profiles |

## Interpretation

- three_domain_scores_fit_better_than_profiles: 5
- bridge_sensitivity_only: 1

## Manuscript Rule

Only cohorts marked candidate_decoupled_profile_signal can be used as primary decoupled functional-validation evidence.
Cohorts marked three_domain_scores_fit_better_than_profiles should be described as continuous-domain comparator evidence against profile superiority.
KLoSA remains bridge-sensitivity and LASI remains excluded from follow-up validation.

## Skipped Models

| cohort | model_type | n | events | skip_reason |
| --- | --- | --- | --- | --- |
| LASI | lfo_profile_age | 0 | 0 | no_available_rows |
| LASI | lfo_profile_age_baseline_functional | 0 | 0 | no_available_rows |
| LASI | lfo_severity_score_age | 0 | 0 | no_available_rows |
| LASI | lfo_severity_tertile_age | 0 | 0 | no_available_rows |
| LASI | three_domain_scores_age | 0 | 0 | no_available_rows |
| LASI | baseline_functional_age_diagnostic | 0 | 0 | no_available_rows |
