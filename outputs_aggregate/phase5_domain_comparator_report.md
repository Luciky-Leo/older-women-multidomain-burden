# Phase 5 Domain Comparator Models

This refinement asks whether endotype classes add information beyond simpler baseline domain-score comparators.
Positive delta AIC values favor the endotype-containing model named in the column.

## Primary Functional Deterioration

| analysis_set | cohort | events_endotype | event_pct_endotype | aic_endotype | aic_severity_score | aic_matched_domain_score | aic_four_domain_scores | aic_endotype_plus_matched_domain | delta_aic_four_domain_scores_minus_endotype | delta_aic_matched_domain_minus_endotype_plus_domain | delta_aic_four_domains_minus_endotype_plus_domains | auc_endotype | auc_four_domain_scores | incremental_value_flag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| functional_bridge_earliest_sensitivity | KLoSA | 1144 | 29.84 | 4615.966 | 4580.093 | 4094.248 | 4049.411 | 4064.119 | -566.555 | 30.129 | -1.53 | 0.58 | 0.7494 | four_domain_scores_beat_endotype |
| strict_earliest_primary | CHARLS | 1766 | 31.03 | 6721.782 | 6779.579 | 6676.153 | 6418.892 | 6656.989 | -302.89 | 19.164 | 11.537 | 0.6423 | 0.7012 | four_domain_scores_beat_endotype_but_endotype_adds_after_four_domains |
| strict_earliest_primary | ELSA | 1316 | 25.54 | 5144.713 | 5148.367 | 5178.797 | 5061.558 | 5130.037 | -83.155 | 48.76 | 12.945 | 0.7394 | 0.7543 | four_domain_scores_beat_endotype_but_endotype_adds_after_four_domains |
| strict_earliest_primary | HRS | 3546 | 37.6 | 11506.008 | 11476.543 | 11624.274 | 11341.104 | 11461.953 | -164.904 | 162.321 | 32.551 | 0.6924 | 0.7071 | four_domain_scores_beat_endotype_but_endotype_adds_after_four_domains |
| strict_earliest_primary | MHAS | 1437 | 26.4 | 5972.038 | 6010.301 | 6021.128 | 5910.044 | 5930.577 | -61.994 | 90.551 | 5.409 | 0.6687 | 0.6783 | four_domain_scores_beat_endotype |
| strict_earliest_primary | SHARE | 1525 | 12.49 | 4604.766 | 6907.775 | 4963.76 | 4952.028 | 3935.551 | 347.262 | 1028.209 | 1025.939 | 0.9294 | 0.9705 | endotype_beats_four_domain_scores |

## Secondary Chronic Progression

| analysis_set | cohort | events_endotype | event_pct_endotype | aic_endotype | aic_severity_score | aic_matched_domain_score | aic_four_domain_scores | aic_endotype_plus_matched_domain | delta_aic_four_domain_scores_minus_endotype | delta_aic_matched_domain_minus_endotype_plus_domain | delta_aic_four_domains_minus_endotype_plus_domains | auc_endotype | auc_four_domain_scores | incremental_value_flag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| functional_bridge_earliest_sensitivity | KLoSA | 1136 | 29.63 | 4633.997 | 4640.231 | 4622.826 | 4622.369 | 4622.6 | -11.628 | 0.226 | -1.992 | 0.5641 | 0.5701 | four_domain_scores_beat_endotype |
| strict_earliest_primary | CHARLS | 2769 | 48.38 | 7927.155 | 7926.421 | 7923.398 | 7911.934 | 7923.9 | -15.221 | -0.502 | -2.998 | 0.5164 | 0.5377 | four_domain_scores_beat_endotype |
| strict_earliest_primary | ELSA | 3245 | 62.95 | 6780.52 | 6787.803 | 6789.239 | 6776.837 | 6777.946 | -3.683 | 11.293 | 11.383 | 0.5362 | 0.5398 | endotype_adds_beyond_matched_domain |
| strict_earliest_primary | HRS | 6629 | 69.96 | 11075.774 | 11031.791 | 10895.929 | 10898.08 | 10875.596 | -177.694 | 20.333 | 18.464 | 0.6399 | 0.6542 | four_domain_scores_beat_endotype_but_endotype_adds_after_four_domains |
| strict_earliest_primary | MHAS | 3035 | 48.29 | 8191.593 | 8366.739 | 8146.318 | 8144.629 | 8150.902 | -46.964 | -4.584 | -0.956 | 0.6609 | 0.6673 | four_domain_scores_beat_endotype |
| strict_earliest_primary | SHARE | 5893 | 48.28 | 16817.297 | 16884.935 | 16703.31 | 16638.347 | 16680.28 | -178.95 | 23.03 | 17.379 | 0.5556 | 0.5829 | four_domain_scores_beat_endotype_but_endotype_adds_after_four_domains |

## Skipped Fits

| analysis_set | cohort | outcome | model_type | n | events | skip_reason |
| --- | --- | --- | --- | --- | --- | --- |
| strict_earliest_primary | LASI | functional_deterioration_ge_0_5sd | severity_tertile | 0 | 0 | no_available_rows |
| strict_earliest_primary | LASI | functional_deterioration_ge_0_5sd | severity_score | 0 | 0 | no_available_rows |
| strict_earliest_primary | LASI | functional_deterioration_ge_0_5sd | matched_domain_score | 0 | 0 | no_available_rows |
| strict_earliest_primary | LASI | functional_deterioration_ge_0_5sd | four_domain_scores | 0 | 0 | no_available_rows |
| strict_earliest_primary | LASI | functional_deterioration_ge_0_5sd | endotype | 0 | 0 | no_available_rows |
| strict_earliest_primary | LASI | functional_deterioration_ge_0_5sd | endotype_plus_matched_domain | 0 | 0 | no_available_rows |
| strict_earliest_primary | LASI | functional_deterioration_ge_0_5sd | endotype_plus_four_domains | 0 | 0 | no_available_rows |
| strict_earliest_primary | LASI | chronic_progression_ge_1_condition | severity_tertile | 0 | 0 | no_available_rows |
| strict_earliest_primary | LASI | chronic_progression_ge_1_condition | severity_score | 0 | 0 | no_available_rows |
| strict_earliest_primary | LASI | chronic_progression_ge_1_condition | matched_domain_score | 0 | 0 | no_available_rows |
| strict_earliest_primary | LASI | chronic_progression_ge_1_condition | four_domain_scores | 0 | 0 | no_available_rows |
| strict_earliest_primary | LASI | chronic_progression_ge_1_condition | endotype | 0 | 0 | no_available_rows |
| strict_earliest_primary | LASI | chronic_progression_ge_1_condition | endotype_plus_matched_domain | 0 | 0 | no_available_rows |
| strict_earliest_primary | LASI | chronic_progression_ge_1_condition | endotype_plus_four_domains | 0 | 0 | no_available_rows |

## Interpretation Guardrails

- The four-domain-score model is not a manuscript replacement for endotypes; it is a diagnostic comparator for whether classes carry pattern information beyond their source scores.
- Endotype-plus-domain and endotype-plus-four-domain models are overadjustment-style diagnostics because endotypes are derived from the same domain scores.
- A consistent endotype advantage should appear against severity score, outcome-matched domain score, and four-domain-score comparators before making strong prediction claims.
