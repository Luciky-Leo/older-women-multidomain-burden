# Phase 13 Covariate Inventory And Display Policy

This phase screens baseline covariates for sensitivity modeling and converts the Phase 12 label queue into a display policy.

## Covariate Readiness

- Minimal core covariate readiness: 7 cohorts.
- Expanded core covariate readiness: 3 cohorts.
- Optional BMI readiness: 5 cohorts.

| cohort | minimal_core_ready | expanded_core_ready | optional_bmi_ready | education_variable | marital_status_variable | rural_region_variable | smoking_variable | drinking_variable | physical_activity_variable | bmi_variable | recommendation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CHARLS | 1 | 0 | 1 | raeducl | marry | hrural | smoken | drinkev | vgact_c | bmi | minimal_core_ready_physical_or_region_limited |
| ELSA | 1 | 1 | 0 | raeducl | mstath | rabcountry | smoken | drink | vgactx_e | mbmi | expanded_core_covariate_sensitivity_ready |
| HRS | 1 | 0 | 1 | raeducl | mstath | rural | smoken | drink | vgactx | bmi | minimal_core_ready_physical_or_region_limited |
| LASI | 1 | 1 | 1 | raeducl | r1mstath | hh1rural | r1smoken | r1drink3m | r1vgactx | r1mbmi | expanded_core_covariate_sensitivity_ready |
| MHAS | 1 | 0 | 0 | raeducl | mstath | rural | smoken | drink |  | bmi | minimal_core_ready_physical_or_region_limited |
| KLoSA | 1 | 0 | 1 | raeducl | mstath | rural | smoken | drink |  | bmi | minimal_core_ready_physical_or_region_limited |
| SHARE | 1 | 1 | 1 | raeducl | mstath | rural | smoken | drink3m | vgactx | bmi | expanded_core_covariate_sensitivity_ready |

## Label And Display Policy

- Label lock candidates: 18.
- Labels requiring manual review before lock: 8.
- Baseline-only labels held until follow-up is available: 3.

| display_policy | label_action | n |
| --- | --- | --- |
| baseline_profile_table_only | hold_until_followup_available | 3 |
| main_results | lock_candidate | 16 |
| main_results | manual_review_before_lock | 7 |
| sensitivity_or_supplement | lock_candidate | 2 |
| sensitivity_or_supplement | manual_review_before_lock | 1 |

## Recommended Next Step

- Run covariate-expanded sensitivity first with age plus minimal core covariates.
- Add rural/region and physical activity only where expanded-core coverage is ready.
- Keep BMI as an optional sensitivity covariate because it is close to the cardiometabolic domain, even though the current cardiometabolic score is chronic-disease based.
- Do not final-lock labels marked `manual_review_before_lock` without manual clinical review.
