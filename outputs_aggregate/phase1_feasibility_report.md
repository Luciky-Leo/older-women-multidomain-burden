# Phase 1 Feasibility Report

This report starts the women-only multidomain aging endotype project from the moved project root.

## Baseline Feasibility

| Cohort | Baseline wave | Age variable | Likely female code | Baseline rows | Women 50+ rows | Domains with candidates |
|---|---|---|---|---:|---:|---|
| CHARLS | 1 | age | 0 | 17708 | 6878 | functional(7); cognitive(4); affective(3); cardiometabolic_chronic(9); inflammaging(2) |
| ELSA | 1 | agey | 0 | 12099 | 6292 | functional(3); cognitive(1); affective(2); cardiometabolic_chronic(5) |
| HRS | 5 | ragey_b | 0 | 19578 | 11005 | functional(3); cognitive(6); affective(3); cardiometabolic_chronic(6) |
| KLoSA | 3 | agey | 0 | 7920 | 4344 | functional(3); cognitive(2); affective(2); cardiometabolic_chronic(6) |
| LASI | all_rows_no_wave | r1agey | 0 | 73408 | 28165 | functional(2); cognitive(1); affective(2); cardiometabolic_chronic(3) |
| MHAS | 1 | agey | 0 | 15186 | 7440 | functional(3); cardiometabolic_chronic(6) |
| SHARE | 1 | agey | 0 | 30416 | 15814 | functional(2); cardiometabolic_chronic(7) |

## Notes

- `likely_female_code` is inferred from female-specific screening/surgery variables and must be confirmed against cohort codebooks.
- Female coding is inferred from all waves, not only baseline, because some female-specific variables are wave-specific.
- Age is read from the selected age variable when possible; if missing, the script derives age from interview year minus birth year.
- LASI currently lacks a standard `wave` field in the cleaned CSV and is treated as `all_rows_no_wave`.
- Domains are counted from candidate variables with any nonmissing values in the baseline subset.
- This is a feasibility start, not the final analytic cohort definition.
