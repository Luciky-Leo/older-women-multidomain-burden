# Manuscript Assembly Draft

Working title: Multidomain aging endotypes among older women across seven international aging cohorts.

Draft status: Phase 17 assembly. Labels marked `[review]`, `*`, or `[baseline-only]` are not final clinical labels.

# Introduction Draft

Population aging is commonly summarized using frailty indices, intrinsic-capacity measures, or single-domain functional transitions. These approaches are useful, but they can compress heterogeneous aging processes into a single severity scale. For older women, this is a particular limitation because functional, cognitive, affective, and cardiometabolic burdens may combine in clinically different ways even when overall burden appears similar.

Recent work has examined multidimensional aging trajectories, intrinsic capacity, symptom clusters, and predeath changes in function, memory, and mood [N1-N6]. This literature makes the broad space crowded, so the present manuscript should not be framed as the first study of multidimensional aging or as a new frailty index. The more defensible gap is narrower: few studies have focused on women-only multidomain aging endotypes across harmonized international aging cohorts while carrying explicit comparator and sensitivity guardrails.

We therefore used cleaned data from seven international aging cohorts to construct cohort-specific women-only multidomain profiles spanning functional, cognitive, affective, and cardiometabolic/chronic disease domains. We evaluated whether these profiles were clinically interpretable, whether they were associated with functional deterioration and all-cause mortality, and whether their evidence remained robust when compared with simpler severity tertiles and continuous four-domain score models.

## Sources for background positioning

- [N1] Interrelated Multidimensional Trajectories of Aging: Evidence From the Health and Retirement Study. https://pubmed.ncbi.nlm.nih.gov/36479143/
- [N2] Sex Differences in Intrinsic Capacity Domains and Their Associations With Adverse Health Outcomes Across Four Aging Cohorts. https://pmc.ncbi.nlm.nih.gov/articles/PMC12317657/
- [N3] Trajectories of intrinsic capacity and their associations with adverse outcomes. https://pmc.ncbi.nlm.nih.gov/articles/PMC11625515/
- [N4] Symptom clusters, disability and health-related quality of life in community-dwelling older adults. https://pmc.ncbi.nlm.nih.gov/articles/PMC12434884/
- [N5] Trajectories of Depressive Symptoms, Memory Function, and Mobility Before Death. https://pmc.ncbi.nlm.nih.gov/articles/PMC11356518/
- [N6] Measurement of Healthy Ageing. https://pmc.ncbi.nlm.nih.gov/articles/PMC11298082/
- [N7] Lifecourse systemic inflammation and healthy ageing: a five-cohort study. https://www.medrxiv.org/content/10.1101/2025.10.22.25338202v1

# Results Draft

This draft uses Phase 16 locked-for-draft labels where available and keeps review-required labels visibly marked.

## Study Sample

The seven cleaned aging cohorts included 79,938 women aged 50 years or older at the eligible baseline screen. Strict-primary endotype construction contributed 56,491 selected class assignments, including 29,058 assignments in the four main validation cohorts (CHARLS, ELSA, HRS, and MHAS). KLoSA and SHARE contributed 40,087 bridge-sensitivity assignments, while LASI remained baseline-profile only because longitudinal outcome validation is not available in the current cleaned CSV pass.

Table callout: Table 1.

## Endotype Structure And Label Status

The selected cohort-specific solutions yielded 29 classes. Phase 16 marks 16 labels as locked for draft use, 10 labels as requiring manual review, and 3 LASI labels as baseline-only holds.

The profiles were not reducible to a single low-to-high severity gradient. Draft labels include functional-dominant, cardiometabolic-dominant, affective-dominant, spared-cardiometabolic, and severity-aligned patterns. Labels marked with an asterisk in Figure 1 require manual review before they should be used as final clinical names.

Table/Figure callout: Table 2 and Figure 1A.

## Functional Deterioration

Functional deterioration validation was available in 6 cohorts, with 50,084 participants and 12,336 events. In the four main validation cohorts, the corresponding analytic set included 25,718 participants and 8,065 events.

Against severity tertiles, the functional model-comparison pattern was endotype_favored: 3, severity_tertile_favored: 3. Four-domain continuous-score models were favored in four_domain_scores_favored: 6, so functional results support endpoint-specific clinical heterogeneity rather than universal endotype prediction superiority.

Table/Figure callout: Table 3 and Figure 1B-C.

## Chronic Progression

Chronic progression validation included 6 cohorts and 22,423 events. The endotype-versus-severity pattern was endotype_favored: 3, severity_tertile_favored: 1, similar_by_aic: 2, but four-domain continuous scores remained favored in four_domain_scores_favored: 6.

## Mortality

Mortality validation included 6 cohorts and 12,649 deaths. Against severity tertiles, the mortality comparison pattern was endotype_favored: 2, severity_tertile_favored: 4.

Mortality should remain a secondary validation endpoint. Prior PH diagnostics and piecewise sensitivity identified time-drift for selected class terms, and Phase 14 covariate sensitivity added further review flags for ELSA_C5, HRS_C3, HRS_C4, HRS_C5, KLoSA_C2, SHARE_C4, SHARE_C5.

## Covariate Sensitivity And Display Guardrails

Phase 14 covariate-sensitivity models are best reported as robustness checks. They support transparent label review and sensitivity reporting, but they should not replace the age-adjusted primary validation screen. Figure 1 should default to the main validation cohorts, with KLoSA and SHARE in sensitivity or supplement display unless bridge-sensitivity footnotes are explicit.

## Comparator Guardrail

The central claim should remain conservative: endotype classes provide compact, interpretable, cohort-specific multidomain profiles with endpoint-specific validation signals. The manuscript should not claim that endotype membership is a universally superior prediction variable compared with the continuous source-domain scores.

# Discussion Draft

## Principal Findings

In this women-only analysis of seven cleaned aging cohorts, the eligible baseline screen included 79,938 women aged 50 years or older. Cohort-specific endotype modeling yielded 96,578 selected assignments overall, including 56,491 strict-primary assignments and 40,087 bridge-sensitivity assignments.

The selected models produced 29 cohort-specific classes. Phase 16 marked 16 labels as locked for draft use, 10 as requiring manual review, and 3 LASI labels as baseline-only holds. This label status is important: review-required labels should remain visibly marked until clinical review is complete.

Functional deterioration validation was available in 6 cohorts, with 50,084 participants and 12,336 events. Mortality validation was available in 6 cohorts, with 54,362 participants and 12,649 deaths.

## Interpretation

The endotype profiles show multidomain heterogeneity that is not fully captured by a single severity gradient. Some classes were dominated by functional burden, others by cardiometabolic/chronic disease burden, affective symptoms, or relative sparing of specific domains. This supports the manuscript's core descriptive claim: among older women, clinically interpretable multidomain aging patterns can be constructed across several cohort systems.

The prediction claim should be more restrained. Across the tested endpoint-cohort rows, continuous four-domain score models generally outperformed endotype-only models. The manuscript should therefore state that endotypes improve interpretability and profile-level summarization, not that class membership is a universally superior standalone predictor.

## Relation to Existing Work

The findings are adjacent to prior studies of multidimensional aging trajectories, intrinsic capacity, symptom clusters, and predeath trajectories [N1-N6]. The distinction is not that multidomain aging has been ignored, but that this analysis uses a women-focused endotype framing across seven international aging cohorts and explicitly benchmarks the classes against severity tertiles and four-domain continuous scores.

## Strengths

Strengths include the women-only analytic frame, harmonized four-domain construction, cohort-specific profile modeling rather than forced pooling, functional and mortality validation, proportional-hazards and piecewise mortality sensitivity checks, covariate-sensitivity screens, and explicit display rules for bridge-sensitivity and baseline-only cohorts.

## Limitations

Limitations include reliance on cleaned CSV variables rather than a full raw-file harmonization pass, cohort differences in domain measurement, bridge definitions for KLoSA and SHARE, missing LASI follow-up validation in the current pass, incomplete expanded-core covariate coverage in several cohorts, and mortality proportional-hazards/time-drift concerns for selected class terms.

## Implications

The most defensible next step is not to overstate prediction superiority, but to refine the clinical naming and cross-cohort alignment of the profiles. If manual label review confirms the current domain interpretations, the study can support a manuscript centered on women-specific multidomain aging heterogeneity and endpoint-specific validation.

# Tables

# Manuscript Tables 1-3 Draft

Labels marked `[review]` or `[baseline-only]` are not final clinical labels.

## Table 1. Cohort readiness and analytic denominators

| cohort | analysis_tier | manuscript_role | baseline_women_age50plus_n | complete_four_domain_n | selected_endotype_n | n_classes | functional_deterioration_ge_0_5sd_available_n | functional_deterioration_ge_0_5sd_event_n | death_n |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CHARLS | strict_primary | primary_validation | 6,878 | 6,019 | 6,019 | 3 | 5,691 | 1,766 | 704 |
| ELSA | strict_primary | primary_validation | 6,292 | 6,104 | 6,104 | 5 | 5,153 | 1,316 | 353 |
| HRS | strict_primary | primary_validation | 11,005 | 10,202 | 10,202 | 5 | 9,431 | 3,546 | 5,569 |
| MHAS | strict_primary | primary_validation | 7,440 | 6,733 | 6,733 | 5 | 5,443 | 1,437 | 2,236 |
| KLoSA | bridge_sensitivity | bridge_sensitivity_validation | 4,344 | 4,081 | 4,081 | 3 | 3,834 | 1,144 | 726 |
| SHARE | bridge_sensitivity | bridge_sensitivity_validation | 15,814 | 36,006 | 36,006 | 5 | 20,532 | 3,127 | 3,061 |
| LASI | strict_primary | baseline_profile_only_current_csv | 28,165 | 27,433 | 27,433 | 3 | 0 | 0 | 0 |

## Table 2. Cohort-specific endotype profiles and draft labels

| cohort | class_id | class_n | class_pct | label_en_display | phase16_label_status | functional_score | cognitive_score | affective_score | cardiometabolic_chronic_score | functional_or_formatted | mortality_hr_formatted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CHARLS | CHARLS_C1 | 4419 | 73.4% | intermediate-burden severity-aligned [review] | review_required_not_locked | -0.52 | -0.15 | -0.20 | -0.06 | 1.00 (1.00-1.00) | 1.00 (1.00-1.00) |
| CHARLS | CHARLS_C2 | 687 | 11.4% | elevated-burden severity-aligned [review] | review_required_not_locked | 0.27 | 0.30 | 0.22 | 0.09 | 0.77 (0.64-0.92) | 1.23 (0.97-1.54) |
| CHARLS | CHARLS_C3 | 913 | 15.2% | functional-dominant high-burden | locked_for_draft | 1.84 | 0.59 | 0.70 | 0.24 | 0.45 (0.37-0.54) | 1.84 (1.55-2.18) |
| ELSA | ELSA_C1 | 2604 | 42.7% | intermediate-burden with spared cardiometabolic | locked_for_draft | -0.42 | -0.20 | -0.20 | -0.84 | 1.00 (1.00-1.00) | 1.00 (1.00-1.00) |
| ELSA | ELSA_C2 | 1668 | 27.3% | cardiometabolic-dominant intermediate-burden | locked_for_draft | -0.42 | -0.06 | -0.14 | 0.38 | 1.18 (1.00-1.40) | 1.47 (1.06-2.03) |
| ELSA | ELSA_C3 | 624 | 10.2% | elevated-burden severity-aligned [review] | review_required_not_locked | 0.57 | 0.30 | 0.31 | 0.30 | 1.48 (1.17-1.86) | 2.10 (1.47-3.01) |
| ELSA | ELSA_C4 | 549 | 9.0% | cardiometabolic-dominant elevated-burden | locked_for_draft | -0.42 | 0.20 | 0.03 | 1.83 | 2.12 (1.68-2.67) | 2.53 (1.77-3.62) |
| ELSA | ELSA_C5 | 659 | 10.8% | functional-dominant high-burden [review] | review_required_not_locked | 2.48 | 0.39 | 0.82 | 0.48 | 0.94 (0.74-1.19) | 3.01 (2.16-4.20) |
| HRS | HRS_C1 | 3596 | 35.2% | low-burden with spared cardiometabolic | locked_for_draft | -0.41 | -0.30 | -0.27 | -0.99 | 1.00 (1.00-1.00) | 1.00 (1.00-1.00) |
| HRS | HRS_C2 | 4428 | 43.4% | cardiometabolic-dominant intermediate-burden | locked_for_draft | -0.41 | -0.01 | -0.21 | 0.51 | 1.67 (1.51-1.85) | 1.64 (1.54-1.76) |
| HRS | HRS_C3 | 870 | 8.5% | elevated-burden severity-aligned [review] | review_required_not_locked | 0.40 | 0.39 | 0.35 | 0.46 | 1.92 (1.62-2.27) | 2.22 (2.02-2.45) |
| HRS | HRS_C4 | 659 | 6.5% | affective-dominant elevated-burden [review] | review_required_not_locked | 0.77 | 0.49 | 1.50 | 0.01 | 1.85 (1.53-2.23) | 2.14 (1.92-2.38) |
| HRS | HRS_C5 | 649 | 6.4% | functional-dominant high-burden [review] | review_required_not_locked | 2.12 | 0.65 | 0.93 | 0.86 | 1.42 (1.16-1.72) | 2.88 (2.59-3.19) |
| MHAS | MHAS_C1 | 2719 | 40.4% | intermediate-burden with spared cardiometabolic | locked_for_draft | -0.32 | -0.10 | -0.26 | -0.96 | 1.00 (1.00-1.00) | 1.00 (1.00-1.00) |
| MHAS | MHAS_C2 | 2267 | 33.7% | cardiometabolic-dominant intermediate-burden | locked_for_draft | -0.32 | -0.06 | -0.02 | 0.42 | 1.60 (1.38-1.85) | 1.36 (1.22-1.52) |
| MHAS | MHAS_C3 | 760 | 11.3% | cardiometabolic-dominant elevated-burden | locked_for_draft | -0.02 | 0.07 | 0.29 | 1.80 | 2.18 (1.79-2.67) | 2.41 (2.12-2.75) |
| MHAS | MHAS_C4 | 467 | 6.9% | functional-dominant elevated-burden | locked_for_draft | 1.82 | 0.37 | 0.51 | -0.00 | 1.21 (0.92-1.60) | 2.13 (1.84-2.47) |
| MHAS | MHAS_C5 | 520 | 7.7% | functional-dominant elevated-burden | locked_for_draft | 1.54 | 0.28 | 0.62 | 0.42 | 1.49 (1.16-1.90) | 1.95 (1.69-2.26) |
| KLoSA | KLoSA_C1 | 1986 | 48.7% | intermediate-burden with spared cardiometabolic | locked_for_draft | -0.19 | -0.18 | -0.18 | -0.86 | 1.00 (1.00-1.00) | 1.00 (1.00-1.00) |
| KLoSA | KLoSA_C2 | 1428 | 35.0% | cardiometabolic-dominant intermediate-burden [review] | review_required_not_locked | -0.30 | -0.21 | -0.15 | 0.58 | 1.39 (1.19-1.62) | 0.96 (0.80-1.15) |
| KLoSA | KLoSA_C3 | 667 | 16.3% | functional/cardiometabolic-dominant high-burden | locked_for_draft | 1.12 | 0.96 | 0.72 | 1.25 | 0.73 (0.59-0.92) | 1.32 (1.10-1.58) |
| SHARE | SHARE_C1 | 11272 | 31.3% | low-burden with spared cardiometabolic | locked_for_draft | -0.69 | -0.41 | -0.65 | -0.75 | 1.00 (1.00-1.00) | 1.00 (1.00-1.00) |
| SHARE | SHARE_C2 | 7860 | 21.8% | cardiometabolic-dominant intermediate-burden | locked_for_draft | -0.31 | -0.28 | -0.59 | 0.47 | 1.37 (1.22-1.55) | 1.48 (1.27-1.73) |
| SHARE | SHARE_C3 | 7032 | 19.5% | affective-dominant intermediate-burden | locked_for_draft | -0.18 | -0.29 | 0.73 | -0.44 | 1.64 (1.45-1.85) | 1.67 (1.42-1.96) |
| SHARE | SHARE_C4 | 6774 | 18.8% | elevated-burden with spared functional [review] | review_required_not_locked | 0.32 | 0.84 | 0.66 | 0.86 | 2.51 (2.22-2.84) | 2.55 (2.21-2.95) |
| SHARE | SHARE_C5 | 3068 | 8.5% | functional/cognitive-dominant high-burden [review] | review_required_not_locked | 2.23 | 1.02 | 0.64 | 0.40 | 1.21 (1.01-1.45) | 3.64 (3.13-4.24) |
| LASI | LASI_C1 | 15915 | 58.0% | intermediate-burden with spared cardiometabolic [baseline-only] | baseline_only_hold | -0.10 | 0.09 | -0.02 | -0.73 | 1.00 (1.00-1.00) |  |
| LASI | LASI_C2 | 5641 | 20.6% | cardiometabolic-dominant intermediate-burden [baseline-only] | baseline_only_hold | -0.61 | -0.38 | -0.13 | 0.95 |  |  |
| LASI | LASI_C3 | 5877 | 21.4% | cardiometabolic-dominant elevated-burden [baseline-only] | baseline_only_hold | 0.72 | 0.13 | 0.17 | 1.04 |  |  |

## Table 3. Outcome validation and comparator guardrails

| cohort | endpoint | n_endotype | events_endotype | event_pct | delta_aic_severity_tertile_minus_endotype | endotype_vs_severity_tertile | delta_aic_four_domain_scores_minus_endotype | endotype_vs_four_domain_scores | validation_note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CHARLS | Functional deterioration >= 0.5 SD | 5,691 | 1,766 | 31.0% | -15.2 | severity_tertile_favored | -302.9 | four_domain_scores_favored | logistic_age_adjusted_domain_comparator |
| CHARLS | Chronic progression >= 1 condition | 5,724 | 2,769 | 48.4% | 0.9 | similar_by_aic | -15.2 | four_domain_scores_favored | logistic_age_adjusted_domain_comparator |
| CHARLS | All-cause mortality | 5,872 | 704 | 12.0% | -17.9 | severity_tertile_favored | -45.5 | four_domain_scores_favored | cox_age_adjusted_secondary |
| ELSA | Functional deterioration >= 0.5 SD | 5,153 | 1,316 | 25.5% | -37.3 | severity_tertile_favored | -83.2 | four_domain_scores_favored | logistic_age_adjusted_domain_comparator |
| ELSA | Chronic progression >= 1 condition | 5,155 | 3,245 | 63.0% | -1.2 | similar_by_aic | -3.7 | four_domain_scores_favored | logistic_age_adjusted_domain_comparator |
| ELSA | All-cause mortality | 5,237 | 353 | 6.7% | -4.9 | severity_tertile_favored | -40.2 | four_domain_scores_favored | cox_secondary_with_ph_or_piecewise_sensitivity |
| HRS | Functional deterioration >= 0.5 SD | 9,431 | 3,546 | 37.6% | -83.3 | severity_tertile_favored | -164.9 | four_domain_scores_favored | logistic_age_adjusted_domain_comparator |
| HRS | Chronic progression >= 1 condition | 9,476 | 6,629 | 70.0% | -32.4 | severity_tertile_favored | -177.7 | four_domain_scores_favored | logistic_age_adjusted_domain_comparator |
| HRS | All-cause mortality | 10,044 | 5,569 | 55.5% | -266.1 | severity_tertile_favored | -575.0 | four_domain_scores_favored | cox_secondary_with_ph_or_piecewise_sensitivity |
| MHAS | Functional deterioration >= 0.5 SD | 5,443 | 1,437 | 26.4% | 23.3 | endotype_favored | -62.0 | four_domain_scores_favored | logistic_age_adjusted_domain_comparator |
| MHAS | Chronic progression >= 1 condition | 6,285 | 3,035 | 48.3% | 193.7 | endotype_favored | -47.0 | four_domain_scores_favored | logistic_age_adjusted_domain_comparator |
| MHAS | All-cause mortality | 6,487 | 2,236 | 34.5% | 67.7 | endotype_favored | -86.5 | four_domain_scores_favored | cox_age_adjusted_secondary |
| KLoSA | Functional deterioration >= 0.5 SD | 3,834 | 1,144 | 29.8% | 7.0 | endotype_favored | -566.6 | four_domain_scores_favored | logistic_age_adjusted_domain_comparator |
| KLoSA | Chronic progression >= 1 condition | 3,834 | 1,136 | 29.6% | 8.2 | endotype_favored | -11.6 | four_domain_scores_favored | logistic_age_adjusted_domain_comparator |
| KLoSA | All-cause mortality | 3,990 | 726 | 18.2% | -38.4 | severity_tertile_favored | -64.3 | four_domain_scores_favored | cox_secondary_with_ph_or_piecewise_sensitivity |
| SHARE | Functional deterioration >= 0.5 SD | 20,532 | 3,127 | 15.2% | 64.9 | endotype_favored | -142.0 | four_domain_scores_favored | logistic_age_adjusted_domain_comparator |
| SHARE | Chronic progression >= 1 condition | 20,532 | 5,609 | 27.3% | 70.7 | endotype_favored | -251.6 | four_domain_scores_favored | logistic_age_adjusted_domain_comparator |
| SHARE | All-cause mortality | 22,732 | 3,061 | 13.5% | 93.2 | endotype_favored | -58.0 | four_domain_scores_favored | cox_secondary_with_ph_or_piecewise_sensitivity |


# Supplement

# Supplementary Tables S1-S3 Draft

## Supplementary Table S1. Covariate-sensitivity model comparisons

| table_id | endpoint | cohort | analysis_tier | adjustment | n_endotype | events_endotype | comparison_metric | comparison_value | secondary_metric | secondary_value |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S1a | Functional deterioration >= 0.5 SD | KLoSA | bridge_sensitivity | minimal_core | 3834.0 | 1144.0 | delta_aic_severity_tertile_minus_endotype | 7.090 | delta_auc_endotype_minus_severity | 0.001 |
| S1a | Functional deterioration >= 0.5 SD | KLoSA | bridge_sensitivity | minimal_plus_bmi | 3717.0 | 1098.0 | delta_aic_severity_tertile_minus_endotype | 2.535 | delta_auc_endotype_minus_severity | -0.002 |
| S1a | Functional deterioration >= 0.5 SD | SHARE | bridge_sensitivity | expanded_core | 19337.0 | 2922.0 | delta_aic_severity_tertile_minus_endotype | 75.369 | delta_auc_endotype_minus_severity | 0.005 |
| S1a | Functional deterioration >= 0.5 SD | SHARE | bridge_sensitivity | minimal_core | 20243.0 | 3083.0 | delta_aic_severity_tertile_minus_endotype | 72.937 | delta_auc_endotype_minus_severity | 0.004 |
| S1a | Functional deterioration >= 0.5 SD | SHARE | bridge_sensitivity | minimal_plus_bmi | 19753.0 | 2944.0 | delta_aic_severity_tertile_minus_endotype | 60.732 | delta_auc_endotype_minus_severity | 0.004 |
| S1a | Functional deterioration >= 0.5 SD | CHARLS | strict_primary | minimal_core | 5687.0 | 1765.0 | delta_aic_severity_tertile_minus_endotype | 5.249 | delta_auc_endotype_minus_severity | -0.002 |
| S1a | Functional deterioration >= 0.5 SD | CHARLS | strict_primary | minimal_plus_bmi | 4871.0 | 1543.0 | delta_aic_severity_tertile_minus_endotype | -3.521 | delta_auc_endotype_minus_severity | -0.003 |
| S1a | Functional deterioration >= 0.5 SD | ELSA | strict_primary | expanded_core | 4561.0 | 1180.0 | delta_aic_severity_tertile_minus_endotype | -8.942 | delta_auc_endotype_minus_severity | -0.001 |
| S1a | Functional deterioration >= 0.5 SD | ELSA | strict_primary | minimal_core | 4562.0 | 1180.0 | delta_aic_severity_tertile_minus_endotype | -17.827 | delta_auc_endotype_minus_severity | -0.003 |
| S1a | Functional deterioration >= 0.5 SD | HRS | strict_primary | minimal_core | 9430.0 | 3546.0 | delta_aic_severity_tertile_minus_endotype | -27.984 | delta_auc_endotype_minus_severity | -0.004 |
| S1a | Functional deterioration >= 0.5 SD | HRS | strict_primary | minimal_plus_bmi | 9229.0 | 3459.0 | delta_aic_severity_tertile_minus_endotype | -13.238 | delta_auc_endotype_minus_severity | -0.003 |
| S1a | Functional deterioration >= 0.5 SD | MHAS | strict_primary | minimal_core | 5434.0 | 1434.0 | delta_aic_severity_tertile_minus_endotype | 26.963 | delta_auc_endotype_minus_severity | 0.007 |
| S1b | All-cause mortality | KLoSA | bridge_sensitivity | minimal_core | 3990.0 | 726.0 | delta_partial_aic_severity_tertile_minus_endotype | -31.714 | median_followup_time_years_endotype | 10.000 |
| S1b | All-cause mortality | KLoSA | bridge_sensitivity | minimal_plus_bmi | 3868.0 | 674.0 | delta_partial_aic_severity_tertile_minus_endotype | -30.042 | median_followup_time_years_endotype | 10.000 |
| S1b | All-cause mortality | SHARE | bridge_sensitivity | expanded_core | 21395.0 | 2864.0 | delta_partial_aic_severity_tertile_minus_endotype | 68.472 | median_followup_time_years_endotype | 4.000 |
| S1b | All-cause mortality | SHARE | bridge_sensitivity | minimal_core | 22413.0 | 3014.0 | delta_partial_aic_severity_tertile_minus_endotype | 89.450 | median_followup_time_years_endotype | 4.000 |
| S1b | All-cause mortality | SHARE | bridge_sensitivity | minimal_plus_bmi | 21755.0 | 2785.0 | delta_partial_aic_severity_tertile_minus_endotype | 62.133 | median_followup_time_years_endotype | 4.000 |
| S1b | All-cause mortality | CHARLS | strict_primary | minimal_core | 5868.0 | 703.0 | delta_partial_aic_severity_tertile_minus_endotype | -14.967 | median_followup_time_years_endotype | 9.000 |
| S1b | All-cause mortality | CHARLS | strict_primary | minimal_plus_bmi | 5008.0 | 573.0 | delta_partial_aic_severity_tertile_minus_endotype | -22.955 | median_followup_time_years_endotype | 9.000 |
| S1b | All-cause mortality | ELSA | strict_primary | expanded_core | 4638.0 | 317.0 | delta_partial_aic_severity_tertile_minus_endotype | 0.586 | median_followup_time_years_endotype | 12.000 |
| S1b | All-cause mortality | ELSA | strict_primary | minimal_core | 4639.0 | 317.0 | delta_partial_aic_severity_tertile_minus_endotype | 1.913 | median_followup_time_years_endotype | 12.000 |
| S1b | All-cause mortality | HRS | strict_primary | minimal_core | 10043.0 | 5569.0 | delta_partial_aic_severity_tertile_minus_endotype |  | median_followup_time_years_endotype | 15.880 |
| S1b | All-cause mortality | HRS | strict_primary | minimal_plus_bmi | 9832.0 | 5458.0 | delta_partial_aic_severity_tertile_minus_endotype | -185.186 | median_followup_time_years_endotype | 15.880 |
| S1b | All-cause mortality | MHAS | strict_primary | minimal_core | 6477.0 | 2231.0 | delta_partial_aic_severity_tertile_minus_endotype | 75.013 | median_followup_time_years_endotype | 17.000 |

## Supplementary Table S2. Effect-stability flags

| endpoint | cohort | analysis_tier | class_id | adjustment | comparison_metric | comparison_value | secondary_value | interpretation_note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| functional_deterioration_ge_0_5sd | SHARE | bridge_sensitivity | SHARE_C4 | expanded_core | effect_ratio_sensitivity_vs_age | 0.780 | material_log_change | Requires manual label/outcome interpretation review before final lock. |
| functional_deterioration_ge_0_5sd | SHARE | bridge_sensitivity | SHARE_C4 | minimal_plus_bmi | effect_ratio_sensitivity_vs_age | 0.779 | material_log_change | Requires manual label/outcome interpretation review before final lock. |
| functional_deterioration_ge_0_5sd | SHARE | bridge_sensitivity | SHARE_C5 | minimal_core | effect_ratio_sensitivity_vs_age | 0.856 | significance_change | Requires manual label/outcome interpretation review before final lock. |
| functional_deterioration_ge_0_5sd | SHARE | bridge_sensitivity | SHARE_C5 | expanded_core | effect_ratio_sensitivity_vs_age | 0.758 | direction_change+significance_change+material_log_change | Requires manual label/outcome interpretation review before final lock. |
| functional_deterioration_ge_0_5sd | SHARE | bridge_sensitivity | SHARE_C5 | minimal_plus_bmi | effect_ratio_sensitivity_vs_age | 0.792 | direction_change+significance_change+material_log_change | Requires manual label/outcome interpretation review before final lock. |
| functional_deterioration_ge_0_5sd | ELSA | strict_primary | ELSA_C5 | expanded_core | effect_ratio_sensitivity_vs_age | 0.823 | significance_change | Requires manual label/outcome interpretation review before final lock. |
| functional_deterioration_ge_0_5sd | HRS | strict_primary | HRS_C3 | minimal_plus_bmi | effect_ratio_sensitivity_vs_age | 0.776 | material_log_change | Requires manual label/outcome interpretation review before final lock. |
| functional_deterioration_ge_0_5sd | HRS | strict_primary | HRS_C4 | minimal_plus_bmi | effect_ratio_sensitivity_vs_age | 0.757 | material_log_change | Requires manual label/outcome interpretation review before final lock. |
| functional_deterioration_ge_0_5sd | HRS | strict_primary | HRS_C5 | minimal_core | effect_ratio_sensitivity_vs_age | 0.837 | significance_change | Requires manual label/outcome interpretation review before final lock. |
| functional_deterioration_ge_0_5sd | HRS | strict_primary | HRS_C5 | minimal_plus_bmi | effect_ratio_sensitivity_vs_age | 0.670 | direction_change+significance_change+material_log_change | Requires manual label/outcome interpretation review before final lock. |
| all_cause_mortality | KLoSA | bridge_sensitivity | KLoSA_C2 | minimal_plus_bmi | effect_ratio_sensitivity_vs_age | 1.078 | direction_change | Requires manual label/outcome interpretation review before final lock. |

## Supplementary Table S3. Non-estimable or skipped sensitivity fits

| endpoint | cohort | analysis_tier | adjustment | comparison_metric | secondary_metric | secondary_value | interpretation_note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| mortality | HRS | strict_primary | minimal_core | severity_tertile | skip_reason | fit_failed: ValueError: nonfinite_cox_result | Document in supplement if the corresponding comparator is discussed. |


# Claim Guardrails

| claim_id | claim | allowed_strength | required_caveat | evidence_assets |
| --- | --- | --- | --- | --- |
| P17-C1 | Women-only multidomain endotype profiles are available across seven cleaned aging cohorts. | descriptive | KLoSA and SHARE are bridge-sensitivity cohorts; LASI is baseline-profile only. | phase11_table1_cohort_readiness.csv; phase16_table2_locked_labels.csv |
| P17-C2 | 16 labels are draft-locked, but 10 still need review. | process_guardrail | Do not treat review-required labels as final clinical labels. | phase16_locked_label_dictionary.csv; phase17_label_review_packet.csv |
| P17-C3 | Functional deterioration is the primary validation endpoint in the current manuscript draft. | primary_validation | Comparator results are endpoint- and cohort-specific. | phase11_table3_outcome_validation_summary.csv; phase16_results_draft.md |
| P17-C4 | Mortality is secondary validation. | secondary_validation | PH, piecewise, and covariate-sensitivity flags require caveated interpretation. | phase8_mortality_ph_diagnostics.csv; phase9_mortality_piecewise_stability.csv; phase14_endotype_effect_stability.csv |
| P17-C5 | Endotypes should be framed as interpretable heterogeneity summaries, not universally superior prediction models. | main_guardrail | Four-domain continuous-score models generally outperform endotype-only models. | phase11_table3_outcome_validation_summary.csv |
