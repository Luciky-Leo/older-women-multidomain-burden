# Phase 6 Mortality Screen

Mortality was derived from cleaned CSV variables whose Working_data DTA labels identify `radyear`, `radmonth`, and `iwstat` as death-year, death-month, or death-status fields.

## Mortality Variables

| cohort | variable | label_from_working_dta | role | usable_for_mortality_screen |
| --- | --- | --- | --- | --- |
| CHARLS | iwstat | 本期是否死亡 | death_status | 1 |
| CHARLS | radyear | 死亡年份 | death_year | 1 |
| CHARLS | radmonth | 死亡月份 | death_month | 1 |
| ELSA | iwstat | 是否死亡 | death_status | 1 |
| ELSA | radyear | 死亡年份 | death_year | 1 |
| HRS | iwstat | 是否死亡 | death_status | 1 |
| HRS | radyear | 死亡年份 | death_year | 1 |
| HRS | radmonth | 死亡月份 | death_month | 1 |
| KLoSA | iwstat | 本期是否存活 | death_status | 1 |
| KLoSA | radyear | 死亡年份 | death_year | 1 |
| KLoSA | radmonth | 死亡月份 | death_month | 1 |
| LASI |  |  |  | 0 |
| MHAS | iwstat | 是否死亡 | death_status | 1 |
| MHAS | radyear | 死亡年份 | death_year | 1 |
| MHAS | radmonth | 死亡月份 | death_month | 1 |
| SHARE | iwstat | 是否死亡 | death_status | 1 |
| SHARE | radyear | 死亡年份 | death_year | 1 |
| SHARE | radmonth | 死亡月份 | death_month | 1 |

## Mortality Follow-Up Summary

| analysis_set | cohort | baseline_n | mortality_followup_available_n | mortality_followup_available_pct | death_n | death_pct | median_followup_time_years | max_followup_time_years |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| functional_bridge_earliest_sensitivity | KLoSA | 4081 | 3990 | 97.77 | 726 | 18.2 | 10.0 | 10.88 |
| strict_earliest_primary | CHARLS | 6019 | 5872 | 97.56 | 704 | 11.99 | 9.0 | 9.29 |
| strict_earliest_primary | ELSA | 6104 | 5237 | 85.8 | 353 | 6.74 | 12.0 | 17.0 |
| strict_earliest_primary | HRS | 10202 | 10044 | 98.45 | 5569 | 55.45 | 15.88 | 21.29 |
| strict_earliest_primary | LASI | 27433 | 0 | 0.0 | 0 |  |  |  |
| strict_earliest_primary | MHAS | 6733 | 6487 | 96.35 | 2236 | 34.47 | 17.0 | 18.0 |
| strict_earliest_primary | SHARE | 15721 | 12960 | 82.44 | 3201 | 24.7 | 11.0 | 17.96 |

## Interpretation Guardrails

- `radyear` and `radmonth` are now treated as direct mortality candidates after DTA-label confirmation.
- `iwstat` was mostly zero in the cleaned Working_data files and should be used as a supporting status field, not the only death indicator.
- Survival models should use `followup_time_years` and `death_event`, not a simple death-ever logistic model, because follow-up time differs by cohort.
