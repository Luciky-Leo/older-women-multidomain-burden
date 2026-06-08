# Phase 11 Manuscript Tables And Figure Draft

This phase converts the analysis outputs into manuscript-facing draft tables.

## Readiness Snapshot

- Phase 1 earliest-baseline women aged 50+ across seven cohorts: 79,938.
- Selected complete four-domain endotype sample, including wave-adjusted SHARE sensitivity: 76,293.
- Cohorts with functional deterioration validation in current CSV pass: 6.
- Cohorts with mortality validation in current CSV pass: 6.
- SHARE uses a wave-adjusted sensitivity denominator, so its selected endotype N is not the same denominator as the Phase 1 earliest-baseline N.
- LASI remains baseline-profile only for follow-up validation in the current cleaned CSV pass.

## Draft Table 1: Cohort Readiness

| cohort | analysis_tier | manuscript_role | baseline_women_age50plus_n | domain_score_baseline_n | complete_four_domain_n | complete_four_domain_pct | selected_endotype_n | n_classes | functional_deterioration_ge_0_5sd_available_n | mortality_followup_available_n | death_n |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CHARLS | strict_primary | primary_validation | 6878 | 6878 | 6019 | 87.51 | 6019 | 3 | 5691 | 5872 | 704 |
| ELSA | strict_primary | primary_validation | 6292 | 6292 | 6104 | 97.01 | 6104 | 5 | 5153 | 5237 | 353 |
| HRS | strict_primary | primary_validation | 11005 | 11005 | 10202 | 92.70 | 10202 | 5 | 9431 | 10044 | 5569 |
| LASI | strict_primary | baseline_profile_only_current_csv | 28165 | 28165 | 27433 | 97.40 | 27433 | 3 | 0 | 0 | 0 |
| MHAS | strict_primary | primary_validation | 7440 | 7440 | 6733 | 90.50 | 6733 | 5 | 5443 | 6487 | 2236 |
| KLoSA | bridge_sensitivity | bridge_sensitivity_validation | 4344 | 4344 | 4081 | 93.95 | 4081 | 3 | 3834 | 3990 | 726 |
| SHARE | strict_primary | primary_validation | 15814 | 15814 | 15721 | 99.41 | 15721 | 4 | 12205 | 12960 | 3201 |

## Draft Table 2: Class Profiles And Labels

| cohort | class_id | class_pct | label_en | label_confidence | severity_mean | functional_score | cognitive_score | affective_score | cardiometabolic_chronic_score | functional_or_formatted | mortality_hr_formatted | mortality_drift_flag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CHARLS | CHARLS_C1 | 73.42 | intermediate-burden severity-aligned | low | -0.23 | -0.52 | -0.15 | -0.20 | -0.06 | 1.00 (1.00-1.00) | 1.00 (1.00-1.00) | 0 |
| CHARLS | CHARLS_C2 | 11.41 | elevated-burden severity-aligned | low | 0.22 | 0.27 | 0.30 | 0.22 | 0.09 | 0.77 (0.64-0.92) | 1.23 (0.97-1.54) | 0 |
| CHARLS | CHARLS_C3 | 15.17 | functional-dominant high-burden | high | 0.84 | 1.84 | 0.59 | 0.70 | 0.24 | 0.45 (0.37-0.54) | 1.84 (1.55-2.18) | 0 |
| ELSA | ELSA_C1 | 42.66 | intermediate-burden with spared cardiometabolic | moderate | -0.41 | -0.42 | -0.20 | -0.20 | -0.84 | 1.00 (1.00-1.00) | 1.00 (1.00-1.00) | 0 |
| ELSA | ELSA_C2 | 27.33 | cardiometabolic-dominant intermediate-burden | high | -0.06 | -0.42 | -0.06 | -0.14 | 0.38 | 1.18 (1.00-1.40) | 1.47 (1.06-2.03) | 0 |
| ELSA | ELSA_C3 | 10.22 | elevated-burden severity-aligned | low | 0.37 | 0.57 | 0.30 | 0.31 | 0.30 | 1.48 (1.17-1.86) | 2.10 (1.47-3.01) | 0 |
| ELSA | ELSA_C4 | 8.99 | cardiometabolic-dominant elevated-burden | high | 0.41 | -0.42 | 0.20 | 0.03 | 1.83 | 2.12 (1.68-2.67) | 2.53 (1.77-3.62) | 0 |
| ELSA | ELSA_C5 | 10.80 | functional-dominant high-burden | high | 1.04 | 2.48 | 0.39 | 0.82 | 0.48 | 0.94 (0.74-1.19) | 3.01 (2.16-4.20) | 0 |
| HRS | HRS_C1 | 35.25 | low-burden with spared cardiometabolic | moderate | -0.49 | -0.41 | -0.30 | -0.27 | -0.99 | 1.00 (1.00-1.00) | 1.00 (1.00-1.00) | 0 |
| HRS | HRS_C2 | 43.40 | cardiometabolic-dominant intermediate-burden | high | -0.03 | -0.41 | -0.01 | -0.21 | 0.51 | 1.67 (1.51-1.85) | 1.64 (1.54-1.76) | 0 |
| HRS | HRS_C3 | 8.53 | elevated-burden severity-aligned | provisional | 0.40 | 0.40 | 0.39 | 0.35 | 0.46 | 1.92 (1.62-2.27) | 2.22 (2.02-2.45) | 1 |
| HRS | HRS_C4 | 6.46 | affective-dominant elevated-burden | provisional | 0.69 | 0.77 | 0.49 | 1.50 | 0.01 | 1.85 (1.53-2.23) | 2.14 (1.92-2.38) | 1 |
| HRS | HRS_C5 | 6.36 | functional-dominant high-burden | provisional | 1.14 | 2.12 | 0.65 | 0.93 | 0.86 | 1.42 (1.16-1.72) | 2.88 (2.59-3.19) | 1 |
| LASI | LASI_C1 | 58.01 | intermediate-burden with spared cardiometabolic | moderate | -0.19 | -0.10 | 0.09 | -0.02 | -0.73 | 1.00 (1.00-1.00) |  | 0 |
| LASI | LASI_C2 | 20.56 | cardiometabolic-dominant intermediate-burden | high | -0.04 | -0.61 | -0.38 | -0.13 | 0.95 |  |  | 0 |
| LASI | LASI_C3 | 21.42 | cardiometabolic-dominant elevated-burden | high | 0.51 | 0.72 | 0.13 | 0.17 | 1.04 |  |  | 0 |
| MHAS | MHAS_C1 | 40.38 | intermediate-burden with spared cardiometabolic | moderate | -0.41 | -0.32 | -0.10 | -0.26 | -0.96 | 1.00 (1.00-1.00) | 1.00 (1.00-1.00) | 0 |
| MHAS | MHAS_C2 | 33.67 | cardiometabolic-dominant intermediate-burden | high | 0.00 | -0.32 | -0.06 | -0.02 | 0.42 | 1.60 (1.38-1.85) | 1.36 (1.22-1.52) | 0 |
| MHAS | MHAS_C3 | 11.29 | cardiometabolic-dominant elevated-burden | high | 0.54 | -0.02 | 0.07 | 0.29 | 1.80 | 2.18 (1.79-2.67) | 2.41 (2.12-2.75) | 0 |
| MHAS | MHAS_C4 | 6.94 | functional-dominant elevated-burden | moderate | 0.68 | 1.82 | 0.37 | 0.51 | -0.00 | 1.21 (0.92-1.60) | 2.13 (1.84-2.47) | 0 |
| MHAS | MHAS_C5 | 7.72 | functional-dominant elevated-burden | moderate | 0.72 | 1.54 | 0.28 | 0.62 | 0.42 | 1.49 (1.16-1.90) | 1.95 (1.69-2.26) | 0 |
| KLoSA | KLoSA_C1 | 48.66 | intermediate-burden with spared cardiometabolic | moderate | -0.35 | -0.19 | -0.18 | -0.18 | -0.86 | 1.00 (1.00-1.00) | 1.00 (1.00-1.00) | 0 |
| KLoSA | KLoSA_C2 | 34.99 | cardiometabolic-dominant intermediate-burden | provisional | -0.02 | -0.30 | -0.21 | -0.15 | 0.58 | 1.39 (1.19-1.62) | 0.96 (0.80-1.15) | 1 |
| KLoSA | KLoSA_C3 | 16.34 | functional/cardiometabolic-dominant high-burden | high | 1.01 | 1.12 | 0.96 | 0.72 | 1.25 | 0.73 (0.59-0.92) | 1.32 (1.10-1.58) | 0 |
| SHARE | SHARE_C1 | 42.48 | intermediate-burden with spared cardiometabolic | moderate | -0.42 | -0.32 | -0.26 | -0.25 | -0.87 | 1.00 (1.00-1.00) | 1.00 (1.00-1.00) | 0 |
| SHARE | SHARE_C2 | 37.50 | cardiometabolic-dominant intermediate-burden | high | 0.02 | -0.37 | -0.12 | -0.08 | 0.65 | 0.00 (0.00-inf) | 1.24 (1.13-1.36) | 0 |
| SHARE | SHARE_C3 | 12.78 | elevated-burden severity-aligned | low | 0.44 | 0.44 | 0.24 | 0.48 | 0.59 | 33.04 (27.39-39.86) | 1.67 (1.50-1.86) | 0 |
| SHARE | SHARE_C4 | 7.24 | functional/cognitive/affective-dominant high-burden | moderate | 1.60 | 2.94 | 1.69 | 1.03 | 0.72 | 114.29 (88.05-148.35) | 2.75 (2.45-3.09) | 0 |

## Draft Table 3: Outcome Validation Summary

| cohort | endpoint | endpoint_role | n_endotype | events_endotype | event_pct | delta_aic_severity_tertile_minus_endotype | endotype_vs_severity_tertile | delta_aic_four_domain_scores_minus_endotype | endotype_vs_four_domain_scores | endotype_plus_four_domain_note | ph_screen_flag | mortality_drift_flagged_classes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CHARLS | Functional deterioration >= 0.5 SD | primary | 5691 | 1766 | 31.03 | -15.20 | severity_tertile_favored | -302.89 | four_domain_scores_favored | endotype_adds_after_four_domains |  |  |
| CHARLS | Chronic progression >= 1 condition | secondary | 5724 | 2769 | 48.38 | 0.86 | similar_by_aic | -15.22 | four_domain_scores_favored | four_domains_only_favored |  |  |
| CHARLS | All-cause mortality | secondary | 5872 | 704 | 11.99 | -17.85 | severity_tertile_favored | -45.55 | four_domain_scores_favored | four_domains_only_favored | 0 |  |
| ELSA | Functional deterioration >= 0.5 SD | primary | 5153 | 1316 | 25.54 | -37.32 | severity_tertile_favored | -83.15 | four_domain_scores_favored | endotype_adds_after_four_domains |  |  |
| ELSA | Chronic progression >= 1 condition | secondary | 5155 | 3245 | 62.95 | -1.18 | similar_by_aic | -3.68 | four_domain_scores_favored | endotype_adds_after_four_domains |  |  |
| ELSA | All-cause mortality | secondary | 5237 | 353 | 6.74 | -4.91 | severity_tertile_favored | -40.20 | four_domain_scores_favored | four_domains_only_favored | 1 |  |
| HRS | Functional deterioration >= 0.5 SD | primary | 9431 | 3546 | 37.60 | -83.33 | severity_tertile_favored | -164.90 | four_domain_scores_favored | endotype_adds_after_four_domains |  |  |
| HRS | Chronic progression >= 1 condition | secondary | 9476 | 6629 | 69.96 | -32.38 | severity_tertile_favored | -177.69 | four_domain_scores_favored | endotype_adds_after_four_domains |  |  |
| HRS | All-cause mortality | secondary | 10044 | 5569 | 55.45 | -266.06 | severity_tertile_favored | -574.97 | four_domain_scores_favored | endotype_adds_after_four_domains | 1 | C3;C4;C5 |
| MHAS | Functional deterioration >= 0.5 SD | primary | 5443 | 1437 | 26.40 | 23.26 | endotype_favored | -61.99 | four_domain_scores_favored | endotype_adds_after_four_domains |  |  |
| MHAS | Chronic progression >= 1 condition | secondary | 6285 | 3035 | 48.29 | 193.73 | endotype_favored | -46.96 | four_domain_scores_favored | similar_after_four_domains |  |  |
| MHAS | All-cause mortality | secondary | 6487 | 2236 | 34.47 | 67.70 | endotype_favored | -86.50 | four_domain_scores_favored | endotype_adds_after_four_domains | 0 |  |
| KLoSA | Functional deterioration >= 0.5 SD | primary | 3834 | 1144 | 29.84 | 7.04 | endotype_favored | -566.56 | four_domain_scores_favored | similar_after_four_domains |  |  |
| KLoSA | Chronic progression >= 1 condition | secondary | 3834 | 1136 | 29.63 | 8.22 | endotype_favored | -11.63 | four_domain_scores_favored | similar_after_four_domains |  |  |
| KLoSA | All-cause mortality | secondary | 3990 | 726 | 18.20 | -38.39 | severity_tertile_favored | -64.26 | four_domain_scores_favored | endotype_adds_after_four_domains | 1 | C2 |
| SHARE | Functional deterioration >= 0.5 SD | primary | 12205 | 1525 | 12.49 | 3087.29 | endotype_favored | 347.26 | endotype_favored | endotype_adds_after_four_domains |  |  |
| SHARE | Chronic progression >= 1 condition | secondary | 12205 | 5893 | 48.28 | 71.86 | endotype_favored | -178.95 | four_domain_scores_favored | endotype_adds_after_four_domains |  |  |
| SHARE | All-cause mortality | secondary | 12960 | 3201 | 24.70 | 83.37 | endotype_favored | -111.21 | four_domain_scores_favored | not_available | 1 |  |

## Draft Figure 1

- PNG: `outputs/figures/phase11_figure1_manuscript_draft.png`
- PDF: `outputs/figures/phase11_figure1_manuscript_draft.pdf`

Figure 1 draft combines:

- Panel A: endotype domain profiles annotated with functional deterioration and mortality rates.
- Panel B: delta AIC versus severity tertiles.
- Panel C: delta AIC versus four-domain continuous scores.

## Interpretation Guardrails

- Positive delta AIC means the endotype-only model improves on the named comparator.
- Negative delta AIC versus four-domain scores means continuous domain scores fit better than endotype-only classes.
- Mortality is retained as a secondary validation endpoint because PH diagnostics and piecewise sensitivity flagged selected cohort-class terms.
- The manuscript should emphasize interpretable multidomain heterogeneity, not universal prediction superiority.
