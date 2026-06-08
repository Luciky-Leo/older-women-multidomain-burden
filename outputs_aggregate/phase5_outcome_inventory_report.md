# Phase 5 Outcome Inventory

This is a screening inventory for outcome validation after the Phase 4 endotype screen.
Domain-score deterioration is defined as a >= 0.5 SD increase in the worse-health direction from baseline to the last observed later wave.
Chronic progression is defined as an increase of >= 1 cardiometabolic/chronic condition from baseline to the last observed later wave.

## Mortality Readiness

- Direct mortality candidates were found in these cleaned CSV files:
  - CHARLS: iwstat;radmonth;radyear
  - ELSA: iwstat;radyear
  - HRS: iwstat;radmonth;radyear
  - KLoSA: iwstat;radmonth;radyear
  - MHAS: iwstat;radmonth;radyear
  - SHARE: iwstat;radmonth;radyear

Broad status-like hits that need manual interpretation:
- CHARLS: cog_status;iwstat;radmonth;radyear
- ELSA: iwstat;radyear
- HRS: iwstat;radmonth;radyear
- KLoSA: iwstat;radmonth;radyear
- MHAS: iwstat;radmonth;radyear
- SHARE: iwstat;radmonth;radyear

## Follow-Up Outcome Screen

| analysis_set | cohort | baseline_n | any_followup_n | any_followup_pct | max_followup_wave | functional_deterioration_ge_0_5sd_available_n | functional_deterioration_ge_0_5sd_event_n | chronic_progression_ge_1_condition_available_n | chronic_progression_ge_1_condition_event_n |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| functional_bridge_earliest_sensitivity | KLoSA | 4081 | 3834 | 93.95 | 8 | 3834 | 1144 | 3834 | 1136 |
| strict_earliest_primary | CHARLS | 6019 | 5724 | 95.1 | 5 | 5691 | 1766 | 5724 | 2769 |
| strict_earliest_primary | ELSA | 6104 | 5155 | 84.45 | 9 | 5153 | 1316 | 5155 | 3245 |
| strict_earliest_primary | HRS | 10202 | 9476 | 92.88 | 15 | 9431 | 3546 | 9476 | 6629 |
| strict_earliest_primary | LASI | 27433 | 0 | 0.0 |  | 0 | 0 | 0 | 0 |
| strict_earliest_primary | MHAS | 6733 | 6285 | 93.35 | 5 | 5443 | 1437 | 6285 | 3035 |
| strict_earliest_primary | SHARE | 15721 | 12205 | 77.64 | 8 | 12205 | 1525 | 12205 | 5893 |

## Proceeding Decision

- Functional deterioration and chronic progression can be screened from the cleaned longitudinal CSV files for all multi-wave cohorts.
- LASI currently contributes baseline endotypes but no cleaned longitudinal follow-up in this CSV pass.
- Mortality should be handled through the DTA-label-confirmed `radyear`, `radmonth`, and `iwstat` fields rather than name-only screening.
