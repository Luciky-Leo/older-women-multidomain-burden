# Phase 33 Revised Main Table Shells

These shells are data-driven drafts for the next manuscript rewrite. They are not final LaTeX styling. Convert to `threeparttable`/`tabularx`, avoid `\tiny` where possible, and keep the explanatory footnotes.

## Revised Table 1. Cohort roles, denominator locks, and validation availability

| Cohort | Role/tier | Source women 50+ | Complete four-domain | Selected profiles/classes | Functional validation | Functional events | Functional source | Allowed main claim |
|---|---|---:|---:|---:|---:|---:|---|---|
| KLoSA | bridge_sensitivity | 4,344 | 4,081 (93.9%) | 4,081 / 3 | 3,834 (93.9%) | 1,144 (29.8%) | bridge | Sensitivity construction only; do not pool as strict primary evidence. |
| ELSA | strict_primary | 6,292 | 6,104 (97.0%) | 6,104 / 5 | 5,153 (84.4%) | 1,316 (25.5%) | primary | Descriptive construction and within-cohort outcome gradients only; no prediction-superiority claim. |
| CHARLS | strict_primary | 6,878 | 6,019 (87.5%) | 6,019 / 3 | 5,691 (94.6%) | 1,766 (31.0%) | primary | Descriptive construction and within-cohort outcome gradients only; no prediction-superiority claim. |
| MHAS | strict_primary | 7,440 | 6,733 (90.5%) | 6,733 / 5 | 5,443 (80.8%) | 1,437 (26.4%) | primary | Descriptive construction and within-cohort outcome gradients only; no prediction-superiority claim. |
| HRS | strict_primary | 11,005 | 10,202 (92.7%) | 10,202 / 5 | 9,431 (92.4%) | 3,546 (37.6%) | primary | Descriptive construction and within-cohort outcome gradients only; no prediction-superiority claim. |
| SHARE | strict_primary | 15,814 | 15,721 (99.4%) | 15,721 / 4 | 12,205 (77.6%) | 1,525 (12.5%) | primary | Descriptive construction allowed; functional validation downgraded by endpoint/model diagnostics. |
| LASI | strict_primary | 28,165 | 27,433 (97.4%) | 27,433 / 3 | NA; not available | NA | primary | Baseline profile construction only; no follow-up validation denominator. |

Footnote: Source, complete-domain, selected-profile and validation denominators are not interchangeable. LASI validation is unavailable in the current cleaned-data pass and must not be reported as zero events.

## New Table 2. Clinical burden-profile families among selected GMM classes

| Clinical family | Group | Classes | Cohorts | Participants | Class-size range | Mean domain z signature F/Cog/Aff/CM | Conservative reading |
|---|---|---:|---|---:|---|---|---|
| Intermediate burden, cardiometabolic/chronic spared | recurrent family | 6 | ELSA, HRS, KLoSA, LASI, MHAS, SHARE | 33,498 (43.9%) | 35.2-58.0% | -0.29/-0.16/-0.20/-0.87 | Lower cardiometabolic/chronic burden despite intermediate overall burden. |
| Intermediate burden, severity aligned | recurrent family | 5 | CHARLS, ELSA, HRS, SHARE | 8,609 (11.3%) | 8.5-73.4% | 0.23/0.22/0.23/0.28 | Domains move together as a general severity gradient. |
| Intermediate burden, cardiometabolic/chronic high with function spared | recurrent family | 4 | ELSA, HRS, LASI, SHARE | 17,633 (23.1%) | 20.6-43.4% | -0.45/-0.14/-0.14/0.62 | Chronic disease burden dominates while function is relatively preserved. |
| Intermediate burden, cardiometabolic/chronic high | recurrent family | 2 | KLoSA, MHAS | 3,695 (4.8%) | 33.7-35.0% | -0.31/-0.13/-0.08/0.50 | Chronic disease burden dominates while function is relatively preserved. |
| High burden, functional dominant with cardiometabolic/chronic spared | recurrent family | 2 | CHARLS, MHAS | 1,380 (1.8%) | 6.9-15.2% | 1.83/0.48/0.61/0.12 | Functional limitation is the main clinical signal. |
| High burden, functional dominant with cognition relatively spared | recurrent family | 2 | HRS, MHAS | 1,169 (1.5%) | 6.4-7.7% | 1.83/0.46/0.77/0.64 | Functional limitation is the main clinical signal. |
| Cohort-specific high-burden variants | collapsed cohort-specific families | 7 | ELSA, HRS, KLoSA, LASI, MHAS, SHARE | 10,309 (13.5%) | 6.5-21.4% | 1.08/0.56/0.65/1.02 | Heterogeneous cohort-specific pattern; inspect full class dictionary. |

Footnote: Higher z-scores indicate worse burden. These families are descriptive clinical strata, not diagnoses or treatment-assignment groups. Full 28-class details should appear in Supplementary Table S3.

## Revised Table 3. Decoupled validation performance and model-stability guardrails

| Cohort | Tier | N/events | Profile AUC | 3-domain AUC | Delta AUC | Delta AIC/1,000 | ARI p50/p10 | Covariance status | Locked interpretation |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| KLoSA | bridge_sensitivity | 3,834 / 1,144 | 0.560 | 0.572 | -0.012 | -2.4 | 0.98/0.23 | downgraded | Bridge only |
| CHARLS | strict_primary | 5,691 / 1,766 | 0.641 | 0.658 | -0.018 | -10.9 | 1.00/0.93 | downgraded | Continuous favored |
| ELSA | strict_primary | 5,153 / 1,316 | 0.741 | 0.750 | -0.010 | -9.8 | 0.95/0.82 | downgraded | Continuous favored |
| HRS | strict_primary | 9,431 / 3,546 | 0.693 | 0.706 | -0.013 | -12.9 | 0.99/0.28 | downgraded | Continuous favored |
| MHAS | strict_primary | 5,443 / 1,437 | 0.670 | 0.673 | -0.003 | -2.9 | 0.98/0.83 | downgraded | Continuous favored |
| SHARE | strict_primary | 12,205 / 1,525 | 0.674 | 0.748 | -0.074 | -54.8 | 0.37/0.37 | downgraded | Validation downgraded; continuous favored |

Footnote: Delta AIC is three-domain continuous score model minus leave-functional-domain-out profile model, scaled per 1,000 validation participants; negative values favor continuous scores. ARI is adjusted Rand index from bootstrap refits.

## Revised Table 4. Domain harmonization and comparability risk matrix

| Cohort | Functional | Cognitive | Affective | Cardiometabolic/chronic | Key reviewer risk |
|---|---|---|---|---|---|
| CHARLS | primary; 99.1%; iadl | primary; 87.6%; total_cognition | primary; 92.8%; cesd10 | primary; 99.3%; hibpe+diabe+hearte+stroke+d... | functional: partial_functional_iadl_only; cognitive: cohort_specific_global_cognitive_score; partial_cognitive_item_battery |
| ELSA | primary; 98.5%; adltot6+iadltot2_e | primary; 97.5%; imrc+dlrc+orient | primary; 97.1%; cesd | primary; 99.9%; hibpe+diabe+hearte+stroke+h... | cognitive: cohort_specific_global_cognitive_score; partial_cognitive_item_battery |
| HRS | primary; 99.8%; adl6a | primary; 92.8%; cog27 | primary; 92.8%; cesd | primary; 100.0%; hibpe+diabe+hearte+stroke+h... | functional: partial_functional_adl_only; cognitive: cohort_specific_global_cognitive_score; partial_cognitive_item_battery |
| KLoSA | bridge; 100.0%; gripsum+gripcomp+fall | primary; 94.7%; source variable not listed | primary; 99.1%; cesd10a | primary; 100.0%; hibpe+diabe+hearte+stroke+c... | functional: bridge_proxy; cognitive: cohort_specific_global_cognitive_score |
| LASI | primary; 99.7%; r1adltot6+r1iadltot_l | primary; 98.8%; r1cog_total | primary; 97.4%; r1cesd10 | primary; 99.8%; r1hibpe+r1diabe+r1hearte+r1... | cognitive: cohort_specific_global_cognitive_score |
| MHAS | primary; 93.9%; adltot6+iadlfour | primary; 92.7%; imrc8+dlrc8+ser7+orient_m | primary; 93.7%; cesd_m | primary; 97.9%; hibpe+diabe+hearte+stroke+c... | cognitive: partial_cognitive_item_battery |
| SHARE | primary; 100.0%; adl+iadl | primary; 99.5%; imrc+dlrc+orient+ser7+numer_s | primary; 100.0%; eurod | primary; 99.5%; hibpe+diabe+hearte+stroke+h... | cognitive: partial_cognitive_item_battery; affective: non_cesd_affective_scale |

Footnote: This table should be visually implemented as a compact cohort-domain matrix. If Fig4 is added as a harmonization heatmap, this table can move to the supplement and remain machine-readable.
