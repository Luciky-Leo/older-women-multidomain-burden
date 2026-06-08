# Statistical Analysis Plan

## Objective

Identify multidomain aging endotypes among women aged 50 years or older across seven international aging cohorts and estimate their associations with adverse health transitions.

## Data

Primary datasets are cleaned cohort CSV files:

- CHARLS
- ELSA
- HRS
- KLoSA
- LASI
- MHAS
- SHARE

Source data must remain read-only. Derived tables should be written under `outputs/`.

## Study Population

Main analysis:

- Female participants.
- Age 50 years or older at cohort-specific baseline.
- At least two observations for trajectory modeling when longitudinal models are used.

Sensitivity analysis:

- Include male participants only to test whether the women-derived endotypes are sex-specific or general aging patterns.

## Exposure / Phenotype Construction

Do not use a single frailty index as the main exposure. Build domain scores separately.

Functional domain:

- ADL and IADL limitations.
- Walking difficulty or walking test where available.
- Grip strength or grip completion where available.
- Falls where available.

Cognitive domain:

- Total cognition or cohort-specific comparable cognitive score.
- Memory and orientation z-scores where available.
- Dementia or Alzheimer variables only as severe-state indicators.

Affective domain:

- CESD or CESD-10.
- Depressive symptom indicators.
- Sleep and loneliness variables may be secondary if harmonization is reliable.

Cardiometabolic / chronic disease domain:

- Hypertension, diabetes, heart disease, stroke.
- BMI and blood pressure measurements.
- Dyslipidemia or cholesterol where available.
- Cancer should be secondary because incident cancer coding may be inconsistent.

Exploratory inflammaging domain:

- CHARLS only unless other cohorts have comparable markers in the cleaned files.
- Candidate variables: CRP and WBC.

## Primary Modeling

1. Build cohort-specific domain scores with direction standardized so higher values mean worse aging status.
2. Standardize continuous domain scores within cohort and wave.
3. Use women-only longitudinal data to estimate endotypes using one of:
   - group-based multi-trajectory modeling;
   - latent class mixed models;
   - joint latent class models if event outcomes are modeled jointly.
4. Choose class number using BIC, entropy, minimum class size, clinical interpretability, and cross-cohort reproducibility.
5. Align endotypes across cohorts by domain-profile similarity rather than forcing identical class labels.
6. Estimate associations between baseline or time-updated endotype and outcomes within each cohort.
7. Compare endotype models against severity-tertile, continuous severity-score, outcome-matched domain-score, and four-domain-score comparator models.
8. Pool cohort-specific estimates with random-effects meta-analysis only after the comparator screen supports a coherent cross-cohort estimand.

## Outcomes

Primary:

- All-cause mortality where death year/month or interview status supports follow-up.
- Functional deterioration: incident or worsening ADL/IADL limitation.

Secondary:

- Cognitive decline.
- Depressive symptom progression.
- Incident multimorbidity or increase in chronic disease count.

## Covariates

Core adjustment set:

- Age.
- Education.
- Marital status.
- Rural/urban or country/region where available.
- Smoking.
- Drinking.
- Physical activity.
- BMI, unless BMI is part of the exposure domain in that specific model.

Avoid overadjustment:

- Do not adjust for variables that are components of the endotype when estimating total endotype-outcome associations.
- Use endotype-plus-domain-score models only as diagnostic comparators, not as the primary total-effect model.

## Missing Data

First feasibility pass:

- Report missingness by cohort, wave, sex, and domain.
- Drop variables with severe missingness or inconsistent coding before modeling.

Analysis phase:

- Prefer complete-case domain construction only when missingness is limited.
- Use multiple imputation or full-information likelihood only after verifying that variable coding is harmonized.

## Main Figures

1. Novelty-positioning figure: what this study avoids and what it adds.
2. Cohort-variable heatmap: availability of domain variables across seven cohorts.
3. Endotype profile plot: standardized domain scores by class and cohort, annotated with functional-deterioration and mortality event rates.
4. Model-comparator heatmaps: endotype-only delta AIC versus severity tertiles and versus four-domain continuous scores.
5. Forest plot: endotype associations with mortality and functional deterioration, using mortality as secondary or sensitivity-supported if PH diagnostics are flagged.

## Current Manuscript Draft Assets

- Draft cohort readiness table: `outputs/phase11_table1_cohort_readiness.csv`.
- Draft class profile and label table: `outputs/phase11_table2_class_profiles_labels.csv`.
- Draft outcome validation table: `outputs/phase11_table3_outcome_validation_summary.csv`.
- Draft combined Figure 1: `outputs/figures/phase11_figure1_manuscript_draft.png` and `.pdf`.
- Results skeleton and writing claims: `outputs/phase12_results_skeleton.md`, `outputs/phase12_results_claims.csv`, and `manuscript/results_skeleton.md`.
- Draft label review queue: `outputs/phase12_label_dictionary_draft.csv`.
- Covariate sensitivity plan: `outputs/phase13_covariate_readiness_summary.csv`, `outputs/phase13_covariate_participant_screen.csv`, and `manuscript/covariate_sensitivity_plan.md`.
- Label/display policy: `outputs/phase13_label_display_policy.csv`.
- Covariate sensitivity model outputs: `outputs/phase14_functional_covariate_model_comparison.csv`, `outputs/phase14_mortality_covariate_model_comparison.csv`, and `outputs/phase14_endotype_effect_stability.csv`.
- Covariate sensitivity manuscript note: `manuscript/covariate_sensitivity_results.md`.
- Integrated Phase 15 manuscript assets: `outputs/phase15_results_skeleton_integrated.md`, `outputs/phase15_label_lock_queue.csv`, `outputs/phase15_supplement_table_shell.csv`, `outputs/phase15_display_policy_recommendation.csv`, and `outputs/phase15_novelty_refresh_report.md`.
- Supplement table shell: `manuscript/supplement_table_shell.md`.
- Phase 16 draft assets: `outputs/phase16_locked_label_dictionary.csv`, `outputs/phase16_table2_locked_labels.csv`, `outputs/phase16_figure1_label_map.csv`, `outputs/figures/phase16_figure1_main_validation.png`, `outputs/figures/phase16_figure1_seven_cohort_sensitivity.png`, and `manuscript/results_draft.md`.
- Phase 17 manuscript assembly assets: `outputs/phase17_label_review_packet.csv`, `outputs/phase17_claim_to_evidence_map.csv`, `outputs/phase17_manuscript_assembly_draft.md`, `manuscript/introduction_draft.md`, `manuscript/discussion_draft.md`, `manuscript/tables_1_3_draft.md`, `manuscript/supplement_s1_s3_draft.md`, and `manuscript/manuscript_assembly_draft.md`.
- Phase 18 submission draft assets: `outputs/phase18_label_decisions_auto_v0.csv`, `outputs/phase18_final_label_dictionary_v0.csv`, `outputs/phase18_table2_final_labels_v0.csv`, `outputs/phase18_figure1_label_map_v0.csv`, `outputs/figures/phase18_figure1_main_validation_v0.png`, `outputs/figures/phase18_figure1_seven_cohort_sensitivity_v0.png`, `manuscript/journal_style_manuscript_v0.md`, and `manuscript/submission_readiness_checklist.md`.
- Phase 19 clean submission package assets: `outputs/phase19_clean_manuscript_target_neutral.md`, `manuscript/clean_manuscript_target_neutral.md`, `outputs/phase19_verified_reference_queue.csv`, `outputs/phase19_reference_corrections.md`, `manuscript/references_verified_v0.md`, `outputs/phase19_label_signoff_sheet.csv`, `outputs/phase19_target_journal_decision_matrix.csv`, `manuscript/title_page_draft.md`, `manuscript/cover_letter_skeleton.md`, and `outputs/phase19_submission_package_index.md`.
- Phase 20 target and signoff assets: `outputs/phase20_label_signoff_decision_template.csv`, `outputs/phase20_label_signoff_review_packet.md`, `outputs/phase20_target_guideline_snapshot.csv`, `outputs/phase20_manuscript_format_gap_check.csv`, `outputs/phase20_target_selection_memo.md`, `outputs/phase20_guideline_sources.md`, `outputs/phase20_target_and_signoff_report.md`, and `manuscript/phase20_working_target_plan.md`.
- Phase 21 BMC Geriatrics Springer Nature template package assets: `manuscript/bmc_geriatrics_submission/bmc_geriatrics_main.tex`, `manuscript/bmc_geriatrics_submission/bmc_geriatrics_refs.bib`, `manuscript/bmc_geriatrics_submission/sn-jnl.cls`, `manuscript/bmc_geriatrics_submission/sn-vancouver-num.bst`, `manuscript/bmc_geriatrics_submission/figure1_main_validation.png`, `manuscript/bmc_geriatrics_submission/figure1_seven_cohort_sensitivity.png`, `manuscript/bmc_geriatrics_submission/bmc_geriatrics_cover_letter.md`, `manuscript/bmc_geriatrics_submission_package.zip`, `outputs/phase21_bmc_geriatrics_package_manifest.csv`, `outputs/phase21_bmc_geriatrics_package_summary.csv`, `outputs/phase21_bmc_geriatrics_package_zip.csv`, and `outputs/phase21_latex_compile_check.md`.
- Phase 22 BMC review-ready package assets: `manuscript/bmc_geriatrics_submission_review_ready/bmc_geriatrics_main.tex`, `manuscript/bmc_geriatrics_submission_review_ready/bmc_geriatrics_refs.bib`, `manuscript/bmc_geriatrics_submission_review_ready/additional_file_1_class_profiles.csv`, `manuscript/bmc_geriatrics_submission_review_ready/additional_file_2_outcome_validation.csv`, `manuscript/bmc_geriatrics_review_ready_package.zip`, `outputs/phase22_conservative_label_signoff_proposal.csv`, `outputs/phase22_bmc_class_profiles_review_ready.csv`, `outputs/phase22_bmc_review_ready_manifest.csv`, `outputs/phase22_bmc_review_ready_summary.csv`, `outputs/phase22_bmc_review_ready_report.md`, `outputs/phase22_bmc_remaining_author_items.md`, and `outputs/phase22_latex_source_sanity_check.md`.
- Phase 23 BMC declarations completion assets: `manuscript/bmc_geriatrics_submission_declarations_ready/bmc_geriatrics_main.tex`, `manuscript/bmc_geriatrics_declarations_ready_package.zip`, `outputs/phase23_bmc_declarations_completion_template.csv`, `outputs/phase23_cohort_data_availability_template.csv`, `outputs/phase23_author_metadata_template.csv`, `outputs/phase23_ai_disclosure_decision_note.md`, `outputs/phase23_bmc_completion_precheck.csv`, `outputs/phase23_bmc_declarations_ready_manifest.csv`, `outputs/phase23_bmc_declarations_ready_zip.csv`, and `outputs/phase23_bmc_declarations_ready_report.md`.
- Mortality estimates should remain secondary unless the PH and piecewise sensitivity notes are shown with the estimates.
- SHARE is wave-adjusted in the current sensitivity analysis; LASI is baseline-profile only for follow-up validation in the current cleaned CSV pass.

## Current Covariate Sensitivity Plan

- Minimal sensitivity model: age plus education, marital status, smoking, and drinking.
- Expanded sensitivity model where available: minimal model plus rural/region and physical activity.
- Optional biometric sensitivity: add BMI separately because it is close to the cardiometabolic construct.
- Minimal core covariates are available in all seven cohorts; expanded core coverage is currently ready in ELSA, LASI, and SHARE.
- Physical activity coverage limits expanded-core modeling in CHARLS, HRS, MHAS, and KLoSA under the current strict candidate rule.
- Phase 14 functional and mortality sensitivity models should be used as robustness checks, not as replacement main estimates.
- Class labels with Phase 14 stability flags require manual review before final lock.
- Phase 15 label locking should use `outputs/phase15_label_lock_queue.csv`; any row marked `manual_review_required` should not be silently promoted to a final label.
- Phase 16 labels marked `review_required_not_locked` may be shown in drafts with visible markers but should not be treated as final clinical labels.
- Phase 17 Introduction and Discussion drafts should keep the novelty claim narrow and use `outputs/phase17_claim_to_evidence_map.csv` before strengthening any manuscript statement.
- Phase 18 auto-v0 labels marked `[signoff]`, `[caveat]`, or `[baseline-only]` must be reviewed before final submission; do not remove these markers without an explicit decision.
- Phase 19 clean manuscript should cite only `manuscript/references_verified_v0.md` or an updated verified reference export. Do not reuse the old Phase 15 source list without checking PMIDs, DOIs, and PMCIDs.
- Phase 19 target-journal matrix is a triage aid only; current author instructions must be live-checked after the target journal is selected.
- Phase 20 keeps Age and Ageing as the working clinical target and The Journals of Gerontology: Series A Medical Sciences as the strongest scientific-fit alternative. Do not format for JAGS until the Wiley author-guideline page is manually verified.
- Phase 20 does not complete human signoff. Labels in `outputs/phase20_label_signoff_decision_template.csv` still require reviewer decisions before final submission assets are generated.
- Phase 21 changes the active target to BMC Geriatrics per user instruction and uses the local Springer Nature template at `E:\Reserch\Temp\_tmp_springer_nature_template_inspect_20260524`.
- Phase 21 local PDF compilation is blocked by missing Tectonic/TeX Live. The LaTeX source package remains suitable for Overleaf/Springer submission-system compilation or local compilation after a TeX runtime is available.
- Phase 22 proposes conservative approval for all 13 remaining label decisions but does not treat them as completed human signoff. Use `outputs/phase22_conservative_label_signoff_proposal.csv` for author confirmation.
- Phase 22 removes the internal signoff worksheet from the BMC review-ready zip and keeps caveat/baseline-only information in cleaned explanatory columns of Additional file 1.
- Phase 23 inserts structured BMC declaration placeholders and cohort data-availability URLs into the declaration-ready TeX package. The remaining placeholders are intentionally unresolved because they require author/team decisions.
- Phase 23 data-availability wording is a template only. Confirm exact citation, acknowledgement, and redistribution constraints from each cohort data-use agreement before submission.

## Acceptance Criteria For Proceeding To Manuscript

- At least four cohorts support functional, affective, cardiometabolic, and mortality outcomes.
- At least three cohorts support a meaningful cognitive domain.
- Endotypes are not just "low/medium/high frailty"; they must show domain-specific profiles.
- Outcome validation should show either consistent risk gradients, clinically interpretable heterogeneity, or selected endpoints where endotype profiles add information beyond simple severity.
- Do not claim universal prediction superiority if continuous domain-score models outperform endotype-only models.
- Mortality Cox estimates require proportional-hazards diagnostics and time-interaction or stratified sensitivity if Schoenfeld-residual screens are flagged.
- Novelty screen remains clear of direct same-topic women-only multidomain endotype papers.
