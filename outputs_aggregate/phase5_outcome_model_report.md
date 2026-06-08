# Phase 5 Outcome Models

This first validation pass uses logistic regression by cohort.
The main comparison is age-adjusted endotype class versus age-adjusted severity tertile.
Positive delta AIC means the severity-tertile model has higher AIC, which favors the endotype model.

## Primary Functional Deterioration

| analysis_set | cohort | events_endotype | event_pct_endotype | aic_endotype | aic_severity_tertile | delta_aic_favors_endotype | auc_endotype | auc_severity_tertile | delta_auc_endotype_minus_severity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| functional_bridge_earliest_sensitivity | KLoSA | 1144 | 29.84 | 4615.966 | 4623.008 | 7.042 | 0.58 | 0.5748 | 0.0052 |
| strict_earliest_primary | CHARLS | 1766 | 31.03 | 6721.782 | 6706.585 | -15.197 | 0.6423 | 0.649 | -0.0067 |
| strict_earliest_primary | ELSA | 1316 | 25.54 | 5144.713 | 5107.394 | -37.319 | 0.7394 | 0.7468 | -0.0074 |
| strict_earliest_primary | HRS | 3546 | 37.6 | 11506.008 | 11422.677 | -83.331 | 0.6924 | 0.7012 | -0.0088 |
| strict_earliest_primary | MHAS | 1437 | 26.4 | 5972.038 | 5995.294 | 23.256 | 0.6687 | 0.6627 | 0.006 |
| strict_earliest_primary | SHARE | 1525 | 12.49 | 4604.766 | 7692.058 | 3087.292 | 0.9294 | 0.7837 | 0.1457 |

## Secondary Chronic Progression

| analysis_set | cohort | events_endotype | event_pct_endotype | aic_endotype | aic_severity_tertile | delta_aic_favors_endotype | auc_endotype | auc_severity_tertile | delta_auc_endotype_minus_severity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| functional_bridge_earliest_sensitivity | KLoSA | 1136 | 29.63 | 4633.997 | 4642.222 | 8.225 | 0.5641 | 0.5565 | 0.0076 |
| strict_earliest_primary | CHARLS | 2769 | 48.38 | 7927.155 | 7928.019 | 0.864 | 0.5164 | 0.5157 | 0.0007 |
| strict_earliest_primary | ELSA | 3245 | 62.95 | 6780.52 | 6779.345 | -1.175 | 0.5362 | 0.5404 | -0.0042 |
| strict_earliest_primary | HRS | 6629 | 69.96 | 11075.774 | 11043.399 | -32.375 | 0.6399 | 0.6383 | 0.0016 |
| strict_earliest_primary | MHAS | 3035 | 48.29 | 8191.593 | 8385.327 | 193.734 | 0.6609 | 0.6227 | 0.0382 |
| strict_earliest_primary | SHARE | 5893 | 48.28 | 16817.297 | 16889.156 | 71.859 | 0.5556 | 0.5315 | 0.0241 |

## Skipped Fits

| analysis_set | cohort | outcome | model_type | adjustment | n | events | skip_reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| strict_earliest_primary | LASI | functional_deterioration_ge_0_5sd | endotype | unadjusted | 0 | 0 | no_available_rows |
| strict_earliest_primary | LASI | functional_deterioration_ge_0_5sd | endotype | age_adjusted | 0 | 0 | no_available_rows |
| strict_earliest_primary | LASI | functional_deterioration_ge_0_5sd | severity_tertile | unadjusted | 0 | 0 | no_available_rows |
| strict_earliest_primary | LASI | functional_deterioration_ge_0_5sd | severity_tertile | age_adjusted | 0 | 0 | no_available_rows |
| strict_earliest_primary | LASI | chronic_progression_ge_1_condition | endotype | unadjusted | 0 | 0 | no_available_rows |
| strict_earliest_primary | LASI | chronic_progression_ge_1_condition | endotype | age_adjusted | 0 | 0 | no_available_rows |
| strict_earliest_primary | LASI | chronic_progression_ge_1_condition | severity_tertile | unadjusted | 0 | 0 | no_available_rows |
| strict_earliest_primary | LASI | chronic_progression_ge_1_condition | severity_tertile | age_adjusted | 0 | 0 | no_available_rows |

## Interpretation Guardrails

- These are validation screens, not causal models.
- LASI is absent from follow-up models because the current cleaned CSV has no later-wave follow-up.
- Mortality models remain blocked until direct mortality variables are extracted from harmonized or raw mortality sources.
