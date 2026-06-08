# Phase 6 Mortality Cox Models

This is a first-pass Cox proportional hazards screen for all-cause mortality.
Positive delta partial AIC values favor endotype over the named comparator.

## Model Comparison

| analysis_set | cohort | events_endotype | event_pct_endotype | median_followup_time_years_endotype | partial_aic_endotype | partial_aic_severity_tertile | partial_aic_severity_score | partial_aic_four_domain_scores | delta_partial_aic_severity_tertile_minus_endotype | delta_partial_aic_severity_score_minus_endotype | delta_partial_aic_four_domain_scores_minus_endotype | delta_partial_aic_four_domains_minus_endotype_plus_domains |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| functional_bridge_earliest_sensitivity | KLoSA | 726 | 18.2 | 10.0 | 10272.233 | 10233.842 | 10208.392 | 10207.978 | -38.391 | -63.841 | -64.255 | 3.833 |
| strict_earliest_primary | CHARLS | 704 | 11.99 | 9.0 | 11233.636 | 11215.788 | 11189.764 | 11188.091 | -17.848 | -43.872 | -45.545 | -3.968 |
| strict_earliest_primary | ELSA | 353 | 6.74 | 12.0 | 5359.717 | 5354.807 | 5329.097 | 5319.514 | -4.91 | -30.62 | -40.203 | -4.119 |
| strict_earliest_primary | HRS | 5569 | 55.45 | 15.88 | 91458.612 | 91192.547 | 91076.516 | 90883.64 | -266.065 | -382.096 | -574.972 | 11.465 |
| strict_earliest_primary | MHAS | 2236 | 34.47 | 17.0 | 35318.537 | 35386.232 | 35273.441 | 35232.038 | 67.695 | -45.096 | -86.499 | 7.09 |
| strict_earliest_primary | SHARE | 3201 | 24.7 | 11.0 | 50832.149 | 50915.518 | 50767.708 | 50720.938 | 83.369 | -64.441 | -111.211 |  |

## Skipped Fits

| analysis_set | cohort | model_type | n | events | skip_reason |
| --- | --- | --- | --- | --- | --- |
| strict_earliest_primary | LASI | severity_tertile | 0 | 0 | no_available_rows |
| strict_earliest_primary | LASI | severity_score | 0 | 0 | no_available_rows |
| strict_earliest_primary | LASI | four_domain_scores | 0 | 0 | no_available_rows |
| strict_earliest_primary | LASI | endotype | 0 | 0 | no_available_rows |
| strict_earliest_primary | LASI | endotype_plus_four_domains | 0 | 0 | no_available_rows |

## Interpretation Guardrails

- These models use derived death year/month from cleaned files after DTA-label confirmation.
- Partial AIC is based on Cox partial likelihood and should be interpreted within cohort and endpoint only.
- Proportional hazards assumptions and mortality coding should be checked before manuscript use.
