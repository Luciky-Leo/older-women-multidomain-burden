# Phase 14 Covariate Sensitivity Models

This phase refits functional deterioration and mortality validation models with baseline covariates from Phase 13.

## Functional Deterioration Model Comparison

| cohort | adjustment | n_endotype | events_endotype | event_pct_endotype | aic_endotype | aic_severity_tertile | delta_aic_severity_tertile_minus_endotype | auc_endotype | auc_severity_tertile |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| KLoSA | minimal_core | 3834 | 1144 | 29.84 | 4616.415 | 4623.505 | 7.09 | 0.5865 | 0.5851 |
| KLoSA | minimal_plus_bmi | 3717 | 1098 | 29.54 | 4460.874 | 4463.409 | 2.535 | 0.5871 | 0.5889 |
| CHARLS | minimal_core | 5687 | 1765 | 31.04 | 6691.605 | 6696.854 | 5.249 | 0.6515 | 0.6531 |
| CHARLS | minimal_plus_bmi | 4871 | 1543 | 31.68 | 5800.289 | 5796.768 | -3.521 | 0.646 | 0.6494 |
| ELSA | expanded_core | 4561 | 1180 | 25.87 | 4516.579 | 4507.637 | -8.942 | 0.7556 | 0.7571 |
| ELSA | minimal_core | 4562 | 1180 | 25.87 | 4537.703 | 4519.876 | -17.827 | 0.7517 | 0.7544 |
| HRS | minimal_core | 9430 | 3546 | 37.6 | 11409.599 | 11381.615 | -27.984 | 0.702 | 0.7059 |
| HRS | minimal_plus_bmi | 9229 | 3459 | 37.48 | 11035.709 | 11022.471 | -13.238 | 0.7112 | 0.7139 |
| MHAS | minimal_core | 5434 | 1434 | 26.39 | 5932.388 | 5959.351 | 26.963 | 0.6766 | 0.6691 |
| SHARE | expanded_core | 11743 | 1467 | 12.49 | 4407.217 | 7329.44 | 2922.223 | 0.9355 | 0.7969 |
| SHARE | minimal_core | 12198 | 1523 | 12.49 | 4587.489 | 7670.8 | 3083.311 | 0.935 | 0.7886 |
| SHARE | minimal_plus_bmi | 11922 | 1446 | 12.13 | 4422.7 | 7344.633 | 2921.933 | 0.9355 | 0.7923 |

## Mortality Model Comparison

| cohort | adjustment | n_endotype | events_endotype | event_pct_endotype | partial_aic_endotype | partial_aic_severity_tertile | delta_partial_aic_severity_tertile_minus_endotype |
| --- | --- | --- | --- | --- | --- | --- | --- |
| KLoSA | minimal_core | 3990.0 | 726.0 | 18.2 | 10258.628 | 10226.914 | -31.714 |
| KLoSA | minimal_plus_bmi | 3868.0 | 674.0 | 17.43 | 9466.623 | 9436.581 | -30.042 |
| CHARLS | minimal_core | 5868.0 | 703.0 | 11.98 | 11213.547 | 11198.58 | -14.967 |
| CHARLS | minimal_plus_bmi | 5008.0 | 573.0 | 11.44 | 8996.54 | 8973.585 | -22.955 |
| ELSA | expanded_core | 4638.0 | 317.0 | 6.83 | 4716.837 | 4717.423 | 0.586 |
| ELSA | minimal_core | 4639.0 | 317.0 | 6.83 | 4722.708 | 4724.621 | 1.913 |
| HRS | minimal_core | 10043.0 | 5569.0 | 55.45 | 90994.079 |  |  |
| HRS | minimal_plus_bmi | 9832.0 | 5458.0 | 55.51 | 88943.161 | 88757.975 | -185.186 |
| MHAS | minimal_core | 6477.0 | 2231.0 | 34.44 | 35223.671 | 35298.684 | 75.013 |
| SHARE | expanded_core | 12444.0 | 3056.0 | 24.56 | 48225.501 | 48285.484 | 59.983 |
| SHARE | minimal_core | 12952.0 | 3198.0 | 24.69 | 50667.415 | 50749.459 | 82.044 |
| SHARE | minimal_plus_bmi | 12613.0 | 3051.0 | 24.19 | 48151.47 | 48233.531 | 82.061 |

## Endotype Effect Stability Flags

| outcome | cohort | term_label | adjustment | age_adjusted_effect | sensitivity_effect | effect_ratio_sensitivity_vs_age | direction_change | significance_change | material_log_change |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| functional_deterioration_ge_0_5sd | ELSA | 5 | expanded_core | 0.9378 | 0.7721 | 0.8233 | 0 | 1 | 0 |
| functional_deterioration_ge_0_5sd | HRS | 3 | minimal_plus_bmi | 1.9187 | 1.4882 | 0.7756 | 0 | 0 | 1 |
| functional_deterioration_ge_0_5sd | HRS | 4 | minimal_plus_bmi | 1.8485 | 1.3991 | 0.7569 | 0 | 0 | 1 |
| functional_deterioration_ge_0_5sd | HRS | 5 | minimal_core | 1.415 | 1.1849 | 0.8374 | 0 | 1 | 0 |
| functional_deterioration_ge_0_5sd | HRS | 5 | minimal_plus_bmi | 1.415 | 0.9482 | 0.6701 | 1 | 1 | 1 |
| all_cause_mortality | KLoSA | 2 | minimal_plus_bmi | 0.9571 | 1.0321 | 1.0783 | 1 | 0 | 0 |

## Skipped Fits

| cohort | outcome_family | model_type | adjustment | n | events | skip_reason |
| --- | --- | --- | --- | --- | --- | --- |
| LASI | functional | endotype | minimal_core | 0 | 0 | no_available_rows |
| KLoSA | functional | endotype | expanded_core | 0 | 0 | covariate_set_not_ready |
| CHARLS | functional | endotype | expanded_core | 0 | 0 | covariate_set_not_ready |
| HRS | functional | endotype | expanded_core | 0 | 0 | covariate_set_not_ready |
| LASI | functional | endotype | expanded_core | 0 | 0 | no_available_rows |
| MHAS | functional | endotype | expanded_core | 0 | 0 | covariate_set_not_ready |
| ELSA | functional | endotype | minimal_plus_bmi | 0 | 0 | covariate_set_not_ready |
| LASI | functional | endotype | minimal_plus_bmi | 0 | 0 | no_available_rows |
| MHAS | functional | endotype | minimal_plus_bmi | 0 | 0 | covariate_set_not_ready |
| LASI | functional | severity_tertile | minimal_core | 0 | 0 | no_available_rows |
| KLoSA | functional | severity_tertile | expanded_core | 0 | 0 | covariate_set_not_ready |
| CHARLS | functional | severity_tertile | expanded_core | 0 | 0 | covariate_set_not_ready |
| HRS | functional | severity_tertile | expanded_core | 0 | 0 | covariate_set_not_ready |
| LASI | functional | severity_tertile | expanded_core | 0 | 0 | no_available_rows |
| MHAS | functional | severity_tertile | expanded_core | 0 | 0 | covariate_set_not_ready |
| ELSA | functional | severity_tertile | minimal_plus_bmi | 0 | 0 | covariate_set_not_ready |
| LASI | functional | severity_tertile | minimal_plus_bmi | 0 | 0 | no_available_rows |
| MHAS | functional | severity_tertile | minimal_plus_bmi | 0 | 0 | covariate_set_not_ready |
| LASI | mortality | endotype | minimal_core | 0 | 0 | no_available_rows |
| KLoSA | mortality | endotype | expanded_core | 0 | 0 | covariate_set_not_ready |
| CHARLS | mortality | endotype | expanded_core | 0 | 0 | covariate_set_not_ready |
| HRS | mortality | endotype | expanded_core | 0 | 0 | covariate_set_not_ready |
| LASI | mortality | endotype | expanded_core | 0 | 0 | no_available_rows |
| MHAS | mortality | endotype | expanded_core | 0 | 0 | covariate_set_not_ready |
| ELSA | mortality | endotype | minimal_plus_bmi | 0 | 0 | covariate_set_not_ready |
| LASI | mortality | endotype | minimal_plus_bmi | 0 | 0 | no_available_rows |
| MHAS | mortality | endotype | minimal_plus_bmi | 0 | 0 | covariate_set_not_ready |
| HRS | mortality | severity_tertile | minimal_core | 10043 | 5569 | fit_failed: ValueError: nonfinite_cox_result |
| LASI | mortality | severity_tertile | minimal_core | 0 | 0 | no_available_rows |
| KLoSA | mortality | severity_tertile | expanded_core | 0 | 0 | covariate_set_not_ready |
| CHARLS | mortality | severity_tertile | expanded_core | 0 | 0 | covariate_set_not_ready |
| HRS | mortality | severity_tertile | expanded_core | 0 | 0 | covariate_set_not_ready |
| LASI | mortality | severity_tertile | expanded_core | 0 | 0 | no_available_rows |
| MHAS | mortality | severity_tertile | expanded_core | 0 | 0 | covariate_set_not_ready |
| ELSA | mortality | severity_tertile | minimal_plus_bmi | 0 | 0 | covariate_set_not_ready |
| LASI | mortality | severity_tertile | minimal_plus_bmi | 0 | 0 | no_available_rows |
| MHAS | mortality | severity_tertile | minimal_plus_bmi | 0 | 0 | covariate_set_not_ready |

## Interpretation Guardrails

- Minimal-core sensitivity uses age, education, marital status, smoking, and drinking.
- Expanded-core sensitivity is only attempted when Phase 13 marked rural/region and physical activity as ready.
- BMI sensitivity is reported separately because BMI is close to the cardiometabolic construct.
- Stability flags are screening flags, not final decisions; they indicate direction change, null-exclusion change, or a >=25% relative change in OR/HR.
