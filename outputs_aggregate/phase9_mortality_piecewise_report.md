# Phase 9 Mortality Piecewise Cox Sensitivity

This sensitivity splits each cohort at its median observed death time.
Early models censor at the cutpoint; late models condition on being followed beyond the cutpoint and reset time from that point.
This is a pragmatic PH-sensitivity screen, not a full time-varying-coefficient model.

## Period Model Sizes

| analysis_set | cohort | period | cutpoint_years | n | events | event_pct | median_period_time_years |
| --- | --- | --- | --- | --- | --- | --- | --- |
| functional_bridge_earliest_sensitivity | KLoSA | full_followup | 6.875 | 3990 | 726 | 18.2 | 10.0 |
| functional_bridge_earliest_sensitivity | KLoSA | early | 6.875 | 3990 | 371 | 9.3 | 6.875 |
| functional_bridge_earliest_sensitivity | KLoSA | late | 6.875 | 3412 | 355 | 10.4 | 3.125 |
| strict_earliest_primary | CHARLS | full_followup | 5.5417 | 5872 | 704 | 11.99 | 9.0 |
| strict_earliest_primary | CHARLS | early | 5.5417 | 5872 | 488 | 8.31 | 5.5417 |
| strict_earliest_primary | CHARLS | late | 5.5417 | 5143 | 216 | 4.2 | 3.4583 |
| strict_earliest_primary | ELSA | full_followup | 5.4583 | 5237 | 353 | 6.74 | 12.0 |
| strict_earliest_primary | ELSA | early | 5.4583 | 5237 | 203 | 3.88 | 5.4583 |
| strict_earliest_primary | ELSA | late | 5.4583 | 4069 | 150 | 3.69 | 9.5417 |
| strict_earliest_primary | HRS | full_followup | 10.7917 | 10044 | 5569 | 55.45 | 15.875 |
| strict_earliest_primary | HRS | early | 10.7917 | 10044 | 2812 | 28.0 | 10.7917 |
| strict_earliest_primary | HRS | late | 10.7917 | 6788 | 2757 | 40.62 | 8.75 |
| strict_earliest_primary | MHAS | full_followup | 10.2083 | 6487 | 2236 | 34.47 | 17.0 |
| strict_earliest_primary | MHAS | early | 10.2083 | 6487 | 1120 | 17.27 | 10.2083 |
| strict_earliest_primary | MHAS | late | 10.2083 | 4971 | 1116 | 22.45 | 6.7917 |
| strict_earliest_primary | SHARE | full_followup | 8.7917 | 12960 | 3201 | 24.7 | 11.0 |
| strict_earliest_primary | SHARE | early | 8.7917 | 12960 | 1612 | 12.44 | 8.7917 |
| strict_earliest_primary | SHARE | late | 8.7917 | 8511 | 1589 | 18.67 | 4.5 |

## Endotype HR Stability

| analysis_set | cohort | term_label | hr_full_followup | hr_early | hr_late | late_vs_early_hr_ratio | direction_change | large_time_drift |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| functional_bridge_earliest_sensitivity | KLoSA | 2 | 0.9571 | 0.6687 | 1.3778 | 2.0605 | 1 | 1 |
| functional_bridge_earliest_sensitivity | KLoSA | 3 | 1.3164 | 1.2381 | 1.5036 | 1.2144 | 0 | 0 |
| strict_earliest_primary | CHARLS | 2 | 1.225 | 1.242 | 1.1951 | 0.9622 | 0 | 0 |
| strict_earliest_primary | CHARLS | 3 | 1.8402 | 1.8635 | 1.8034 | 0.9677 | 0 | 0 |
| strict_earliest_primary | ELSA | 2 | 1.4704 | 1.4924 | 1.4282 | 0.957 | 0 | 0 |
| strict_earliest_primary | ELSA | 3 | 2.1048 | 2.1535 | 2.0712 | 0.9618 | 0 | 0 |
| strict_earliest_primary | ELSA | 4 | 2.5316 | 2.7432 | 2.2423 | 0.8174 | 0 | 0 |
| strict_earliest_primary | ELSA | 5 | 3.0109 | 3.4376 | 2.4996 | 0.7271 | 0 | 0 |
| strict_earliest_primary | HRS | 2 | 1.6422 | 1.9509 | 1.4938 | 0.7657 | 0 | 0 |
| strict_earliest_primary | HRS | 3 | 2.2213 | 2.8491 | 1.8315 | 0.6428 | 0 | 1 |
| strict_earliest_primary | HRS | 4 | 2.1366 | 2.9195 | 1.6211 | 0.5553 | 0 | 1 |
| strict_earliest_primary | HRS | 5 | 2.8771 | 3.8295 | 2.2051 | 0.5758 | 0 | 1 |
| strict_earliest_primary | MHAS | 2 | 1.3646 | 1.299 | 1.4261 | 1.0978 | 0 | 0 |
| strict_earliest_primary | MHAS | 3 | 2.4136 | 2.6305 | 2.206 | 0.8386 | 0 | 0 |
| strict_earliest_primary | MHAS | 4 | 2.1346 | 2.2711 | 2.0289 | 0.8934 | 0 | 0 |
| strict_earliest_primary | MHAS | 5 | 1.9539 | 2.2789 | 1.6122 | 0.7074 | 0 | 0 |
| strict_earliest_primary | SHARE | 2 | 1.2414 | 1.2732 | 1.2127 | 0.9525 | 0 | 0 |
| strict_earliest_primary | SHARE | 3 | 1.673 | 1.8553 | 1.5313 | 0.8254 | 0 | 0 |
| strict_earliest_primary | SHARE | 4 | 2.7529 | 3.276 | 2.1958 | 0.6703 | 0 | 0 |

## Drift Flags

| analysis_set | cohort | term_label | hr_full_followup | hr_early | hr_late | late_vs_early_hr_ratio | direction_change | large_time_drift |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| functional_bridge_earliest_sensitivity | KLoSA | 2 | 0.9571 | 0.6687 | 1.3778 | 2.0605 | 1 | 1 |
| strict_earliest_primary | HRS | 3 | 2.2213 | 2.8491 | 1.8315 | 0.6428 | 0 | 1 |
| strict_earliest_primary | HRS | 4 | 2.1366 | 2.9195 | 1.6211 | 0.5553 | 0 | 1 |
| strict_earliest_primary | HRS | 5 | 2.8771 | 3.8295 | 2.2051 | 0.5758 | 0 | 1 |

## Skipped Fits

| analysis_set | cohort | period | n | events | skip_reason |
| --- | --- | --- | --- | --- | --- |
| strict_earliest_primary | LASI | all | 0 | 0 | no_available_rows_or_too_few_deaths |

## Interpretation Guardrails

- Direction changes or HR ratios >= 1.5 / <= 0.67 indicate unstable mortality HRs across follow-up periods.
- For flagged cohort-class terms, mortality should be reported as secondary or with explicit time-period sensitivity.
- Functional deterioration remains the cleaner first validation endpoint because it does not depend on PH assumptions.
