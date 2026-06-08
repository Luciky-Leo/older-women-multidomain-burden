# Phase 7 Manuscript Review Assets

This phase consolidates class profiles, event rates, endotype ORs/HRs, and model-comparator deltas for manuscript triage.

## Highest Mortality Classes

| analysis_set | cohort | class | profile_label | death_pct | mortality_hr_formatted |
| --- | --- | --- | --- | --- | --- |
| strict_earliest_primary | HRS | 5 | high_burden_high_functional_spared_cognitive | 79.75 | 2.88 (2.59-3.19) |
| strict_earliest_primary | HRS | 3 | intermediate_severity_aligned | 73.92 | 2.22 (2.02-2.45) |
| strict_earliest_primary | SHARE | 4 | high_burden_high_functional_spared_affective_cardiometabolic_chronic | 68.99 | 2.75 (2.45-3.09) |
| strict_earliest_primary | HRS | 4 | high_burden_high_affective_spared_cardiometabolic_chronic | 68.1 | 2.14 (1.92-2.38) |
| strict_earliest_primary | HRS | 2 | intermediate_high_cardiometabolic_chronic_spared_functional | 61.53 | 1.64 (1.54-1.76) |
| strict_earliest_primary | MHAS | 4 | high_burden_high_functional_spared_cardiometabolic_chronic | 58.81 | 2.13 (1.84-2.47) |
| strict_earliest_primary | MHAS | 5 | high_burden_high_functional_spared_cognitive | 55.51 | 1.95 (1.69-2.26) |
| strict_earliest_primary | MHAS | 3 | high_burden_high_cardiometabolic_chronic_spared_functional_cognitive | 50.55 | 2.41 (2.12-2.75) |
| strict_earliest_primary | SHARE | 3 | intermediate_severity_aligned | 41.26 | 1.67 (1.50-1.86) |
| functional_bridge_earliest_sensitivity | KLoSA | 3 | high_burden_severity_aligned | 39.72 | 1.32 (1.10-1.58) |

## Highest Functional-Deterioration Classes

| analysis_set | cohort | class | profile_label | functional_deterioration_ge_0_5sd_event_pct | functional_or_formatted |
| --- | --- | --- | --- | --- | --- |
| strict_earliest_primary | SHARE | 4 | high_burden_high_functional_spared_affective_cardiometabolic_chronic | 75.9 | 114.29 (88.05-148.35) |
| strict_earliest_primary | SHARE | 3 | intermediate_severity_aligned | 52.31 | 33.04 (27.39-39.86) |
| strict_earliest_primary | HRS | 3 | intermediate_severity_aligned | 49.67 | 1.92 (1.62-2.27) |
| strict_earliest_primary | HRS | 4 | high_burden_high_affective_spared_cardiometabolic_chronic | 45.9 | 1.85 (1.53-2.23) |
| strict_earliest_primary | ELSA | 4 | intermediate_high_cardiometabolic_chronic_spared_functional_affective | 43.89 | 2.12 (1.68-2.67) |
| strict_earliest_primary | HRS | 2 | intermediate_high_cardiometabolic_chronic_spared_functional | 42.76 | 1.67 (1.51-1.85) |
| strict_earliest_primary | HRS | 5 | high_burden_high_functional_spared_cognitive | 42.62 | 1.42 (1.16-1.72) |
| strict_earliest_primary | ELSA | 3 | intermediate_severity_aligned | 37.5 | 1.48 (1.17-1.86) |
| strict_earliest_primary | MHAS | 3 | high_burden_high_cardiometabolic_chronic_spared_functional_cognitive | 37.14 | 2.18 (1.79-2.67) |
| functional_bridge_earliest_sensitivity | KLoSA | 2 | intermediate_high_cardiometabolic_chronic | 35.69 | 1.39 (1.19-1.62) |

## Delta AIC Versus Severity Tertile

| endpoint | CHARLS | ELSA | HRS | KLoSA | MHAS | SHARE |
| --- | --- | --- | --- | --- | --- | --- |
| Chronic progression | 0.864 | -1.175 | -32.375 | 8.225 | 193.734 | 71.859 |
| Functional deterioration | -15.197 | -37.319 | -83.331 | 7.042 | 23.256 | 3087.292 |
| Mortality | -17.848 | -4.91 | -266.065 | -38.391 | 67.695 | 83.369 |

## Delta AIC Versus Four-Domain Scores

| endpoint | CHARLS | ELSA | HRS | KLoSA | MHAS | SHARE |
| --- | --- | --- | --- | --- | --- | --- |
| Chronic progression | -15.221 | -3.683 | -177.694 | -11.628 | -46.964 | -178.95 |
| Functional deterioration | -302.89 | -83.155 | -164.904 | -566.555 | -61.994 | 347.262 |
| Mortality | -45.545 | -40.203 | -574.972 | -64.255 | -86.499 | -111.211 |

## Figure Files

- `outputs/figures/phase7_aic_delta_vs_severity_tertile.png` and `.svg`
- `outputs/figures/phase7_aic_delta_vs_four_domain_scores.png` and `.svg`
- `outputs/figures/phase7_endotype_profiles_with_outcomes.png` and `.svg`

## Interpretation Guardrails

- Positive delta AIC means the endotype-only model improves on the named comparator.
- Negative delta AIC versus four-domain scores means continuous domain scores outperform endotype-only classes.
- The class review table is for clinical labeling and triage, not final causal interpretation.
