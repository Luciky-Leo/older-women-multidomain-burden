# Phase 8 Mortality PH Diagnostics

This is a lightweight proportional-hazards screen for the age-adjusted endotype Cox model.
Each model term's Schoenfeld residuals are correlated with log follow-up time.
A term is flagged when Pearson p < 0.01 and absolute Pearson r >= 0.05.

## Cohort Summary

| analysis_set | cohort | n | events | tested_terms | flagged_terms | min_pearson_p | max_abs_pearson_r | ph_screen_flag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| functional_bridge_earliest_sensitivity | KLoSA | 3990 | 726 | 3 | 1 | 0.00014 | 0.14091 | 1 |
| strict_earliest_primary | CHARLS | 5872 | 704 | 3 | 0 | 0.45026 | 0.0285 | 0 |
| strict_earliest_primary | ELSA | 5237 | 353 | 5 | 1 | 0.0077 | 0.14162 | 1 |
| strict_earliest_primary | HRS | 10044 | 5569 | 5 | 2 | 0.0 | 0.06379 | 1 |
| strict_earliest_primary | MHAS | 6487 | 2236 | 5 | 0 | 0.12896 | 0.03212 | 0 |
| strict_earliest_primary | SHARE | 12960 | 3201 | 4 | 1 | 0.0 | 0.08323 | 1 |

## Flagged Terms

| analysis_set | cohort | term | events | pearson_r_with_log_time | pearson_p | spearman_r_with_log_time | spearman_p |
| --- | --- | --- | --- | --- | --- | --- | --- |
| functional_bridge_earliest_sensitivity | KLoSA | C(endotype_class, Treatment(reference='1'))[T.2] | 726 | 0.14091 | 0.00014 | -0.15595 | 2e-05 |
| strict_earliest_primary | ELSA | C(endotype_class, Treatment(reference='1'))[T.5] | 353 | -0.14162 | 0.0077 | 0.51647 | 0.0 |
| strict_earliest_primary | HRS | C(endotype_class, Treatment(reference='1'))[T.5] | 5569 | -0.05892 | 1e-05 | 0.69549 | 0.0 |
| strict_earliest_primary | HRS | age | 5569 | 0.06379 | 0.0 | 0.02638 | 0.049 |
| strict_earliest_primary | SHARE | C(endotype_class, Treatment(reference='1'))[T.4] | 3201 | -0.08323 | 0.0 | 0.43922 | 0.0 |

## Skipped Cohorts

| analysis_set | cohort | n | events | skip_reason |
| --- | --- | --- | --- | --- |
| strict_earliest_primary | LASI | 0 | 0 | no_available_rows |

## Interpretation Guardrails

- This is a screen, not a final PH-assumption proof.
- Large cohorts can produce small p-values for weak time trends; the correlation threshold is included to reduce trivial flags.
- Flagged models should get a time-interaction or stratified sensitivity before manuscript use.
