# Phase 32E Item-Level Harmonization Crosswalk

Date: 2026-06-02

## Generated Files

- `outputs/phase32_item_level_harmonization_crosswalk.csv`
- `outputs/phase32_cohort_tier_lock.csv`
- `outputs/phase32_item_level_harmonization_report.md`

## Comparability Summary

| domain | comparability_flag | item_rows |
| --- | --- | --- |
| affective | cesd_family_affective_scale | 6 |
| affective | non_cesd_affective_scale | 1 |
| cardiometabolic_chronic | core_chronic_condition | 35 |
| cardiometabolic_chronic | optional_lipid_condition | 5 |
| cognitive | cohort_specific_global_cognitive_score | 6 |
| cognitive | partial_cognitive_item_battery | 30 |
| functional | bridge_proxy | 3 |
| functional | partial_functional_adl_only | 1 |
| functional | partial_functional_iadl_only | 1 |
| functional | strict_core_adl_iadl | 9 |

## Cohort Tier Lock

| cohort | functional_source_tier | phase32_main_evidence_status | phase32b_evidence_status | phase32d_stability_status | manuscript_role_lock |
| --- | --- | --- | --- | --- | --- |
| KLoSA | bridge | bridge_sensitivity_only | bridge_sensitivity_only | downgrade_near_singular_covariance | bridge_sensitivity_descriptive_only |
| CHARLS | primary | usable_only_as_coupled_within_cohort_association | three_domain_scores_fit_better_than_profiles | downgrade_near_singular_covariance | strict_construction_within_cohort_gradient_only |
| ELSA | primary | usable_only_as_coupled_within_cohort_association | three_domain_scores_fit_better_than_profiles | downgrade_near_singular_covariance | strict_construction_within_cohort_gradient_only |
| HRS | primary | usable_only_as_coupled_within_cohort_association | three_domain_scores_fit_better_than_profiles | downgrade_near_singular_covariance | strict_construction_within_cohort_gradient_only |
| LASI | primary | exclude_no_followup_validation | exclude_no_followup_validation | downgrade_near_singular_covariance | baseline_profile_construction_only_no_followup_validation |
| MHAS | primary | usable_only_as_coupled_within_cohort_association | three_domain_scores_fit_better_than_profiles | downgrade_near_singular_covariance | strict_construction_within_cohort_gradient_only |
| SHARE | primary | exclude_or_redefine_until_endpoint_decoupled | three_domain_scores_fit_better_than_profiles | downgrade_near_singular_covariance | strict_construction_but_validation_downgraded |

## Manuscript Rule

The manuscript must not describe all seven cohorts as equivalent strict validation cohorts.
Table 1 and all figure legends should use the `manuscript_role_lock` values from `phase32_cohort_tier_lock.csv`.
The harmonization crosswalk should be used as the variable dictionary in the additional files instead of the domain-only Phase 28 dictionary.
