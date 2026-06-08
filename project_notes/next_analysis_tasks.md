# Next Analysis Tasks

## Minimum Viable Analysis

1. Confirm `ragender` coding in all seven cohorts. Done: `0 = women`, `1 = men`.
2. Define one stable baseline wave per cohort. Partly done: see `outputs/four_domain_wave_readiness.csv`.
3. Restrict primary analysis to women aged 50 or older.
4. Create domain scores:
   - functional domain;
   - cognitive domain;
   - affective domain;
   - cardiometabolic/chronic disease domain.
5. Run descriptive missingness and score distributions by cohort.
6. Test 2-5 latent/endotype classes per cohort. Done for the first-pass Gaussian mixture screen.
7. Reject class solutions that only reproduce low/medium/high generic frailty. First-pass automated screen done; manual profile review still needed.
8. Estimate mortality and functional deterioration associations within each cohort.
9. Meta-analyze cohort-specific estimates.
10. Prepare the novelty-safe introduction around women-only multidomain aging endotypes.

## First Table Shell

Table 1: Cohort and participant characteristics among women aged 50+.

Table 2: Domain-variable availability and missingness by cohort.

Table 3: Multidomain aging endotype profiles.

Table 4: Associations between endotypes and adverse health transitions.

## First Figure Shell

Figure 1: Study positioning and novelty boundary.

Figure 2: Variable availability heatmap across seven cohorts.

Figure 3: Multidomain endotype profile radar/line plot.

Figure 4: Longitudinal trajectories by endotype.

Figure 5: Random-effects forest plot for mortality and functional deterioration.

## Go / No-Go Rules

Go:

- At least four cohorts support three or more aging domains.
- Endotypes are clinically interpretable and not a simple severity gradient.
- Mortality or functional deterioration events are sufficient in at least four cohorts.

No-go or pivot:

- Classes collapse into only low/medium/high frailty.
- Cognitive and affective domains cannot be harmonized.
- Sex coding cannot be verified.
- Another direct women-only multidomain endotype paper appears in the final literature check.

## Immediate Phase 3 Tasks

1. Decide whether the first modeling run should be earliest-wave only or wave-adjusted.
2. For a conservative strict-primary first pass, model CHARLS, ELSA, HRS, LASI, and MHAS.
3. Include KLoSA as functional-bridge sensitivity because its functional domain currently relies on grip/fall variables rather than ADL/IADL.
4. Include SHARE only in a wave-adjusted practical sensitivity because cognition/depressive symptoms are now available but functional readiness still depends on frailty/grip bridge variables.
5. Build `scripts/build_phase3_domain_scores.py` to create women 50+ analytic domain scores with all domains oriented so higher means worse health. Done.

## Phase 2 Targeted Extraction Status

- LASI chronic disease gap resolved from existing cleaned variables: `r1hibpe`, `r1diabe`, `r1hearte`, `r1stroke`, `r1hchole`, `r1cancre`.
- MHAS cognition/depressive symptom gap resolved from existing cleaned variables: `imrc8`, `dlrc8`, `ser7`, `orient_m`, `cesd_m`.
- SHARE cognition/depressive symptom gap resolved from existing cleaned variables: `imrc`, `dlrc`, `ser7`, `orient`, `numer_s`, `eurod`.
- No raw-data merge is needed for this pass; the needed variables were already present in the cleaned Working_data/CSV files but missing from the earlier candidate specification.

## Phase 3 Domain Score Status

- Strict primary score table is ready in `outputs/phase3_domain_scores.csv`.
- Long women 50+ domain-score table is ready in `outputs/phase3_domain_scores_long.csv`.
- QC report is ready in `outputs/phase3_domain_score_qc.md`.
- Strict earliest-wave primary cohorts: CHARLS, ELSA, HRS, LASI, MHAS.
- Functional-bridge sensitivity cohorts: KLoSA and SHARE.
- No selected analysis set has absolute pairwise domain correlation >= 0.70.

## Phase 4 Endotype Screen Status

- `scripts/build_phase4_endotype_models.py` is built and run.
- First-pass Gaussian mixture models are complete for strict primary cohorts: CHARLS, ELSA, HRS, LASI, and MHAS.
- Functional-bridge sensitivity models are complete for KLoSA and SHARE.
- Model outputs are ready in `outputs/phase4_gmm_model_metrics.csv`, `outputs/phase4_gmm_class_profiles.csv`, `outputs/phase4_best_model_summary.csv`, and `outputs/phase4_best_model_assignments.csv`.
- The simple severity comparator is ready in `outputs/phase4_severity_comparator_profiles.csv`.
- The screening report is ready in `outputs/phase4_endotype_screen_report.md`.
- Selected models use the lowest BIC among converged solutions with minimum class size >= 5%.
- BIC-only 5-class solutions were rejected for KLoSA and LASI because they produced very small classes.

## Immediate Phase 5 Tasks

1. Manually review the Phase 4 class profiles and lock a clinically interpretable class-label rule.
2. Inventory mortality, ADL/IADL deterioration, cognitive decline, depressive-symptom worsening, and multimorbidity progression outcomes by cohort and wave. Done for cleaned CSV follow-up outcomes.
3. Build `scripts/build_phase5_outcome_inventory.py` to quantify available follow-up, events, and loss to follow-up by selected Phase 4 class. Done.
4. Fit cohort-specific outcome models comparing endotype classes with the severity-tertile comparator.
5. Prioritize functional deterioration first, because it is immediately available from cleaned longitudinal CSVs.
6. Add mortality after candidate confirmation from labels. Done in Phase 6 using `radyear`, `radmonth`, and `iwstat`.
7. Move to longitudinal trajectory or latent class mixed models only if outcome validation shows that baseline endotypes add information beyond simple severity tertiles.

## Phase 5 Outcome Inventory Status

- `scripts/build_phase5_outcome_inventory.py` is built and run.
- Participant-level outcome screen is ready in `outputs/phase5_participant_outcome_screen.csv`.
- Grouped follow-up and event counts are ready in `outputs/phase5_followup_outcome_inventory.csv`.
- Variable readiness inventory is ready in `outputs/phase5_outcome_variable_inventory.csv`.
- Markdown report is ready in `outputs/phase5_outcome_inventory_report.md`.
- Direct mortality candidates were missed by the first name-only screen but are now confirmed from Working_data DTA labels and cleaned CSV headers: `radyear`, `radmonth`, and `iwstat`.
- Functional deterioration and chronic progression are available for CHARLS, ELSA, HRS, KLoSA, MHAS, and SHARE.
- LASI has baseline endotypes but no cleaned longitudinal follow-up in this CSV pass.

## Immediate Outcome Modeling Tasks

1. Build `scripts/build_phase5_outcome_models.py`. Done.
2. Model functional deterioration as the first validation endpoint among cohorts with follow-up. Done.
3. Compare endotype classes against the severity-tertile comparator within each cohort. Done.
4. Report minimally adjusted and age-adjusted models first. Done for the initial validation screen.
5. Keep LASI in baseline-profile tables but exclude it from follow-up outcome validation until longitudinal LASI data are added. Done in current model outputs.

## Phase 5 Outcome Model Status

- First-pass outcome model outputs are ready in `outputs/phase5_outcome_model_metrics.csv`, `outputs/phase5_outcome_model_terms.csv`, `outputs/phase5_outcome_model_comparison.csv`, and `outputs/phase5_outcome_model_report.md`.
- Functional deterioration supports a weak endotype advantage in KLoSA, SHARE, and MHAS.
- Functional deterioration favors the severity-tertile comparator in CHARLS, ELSA, and HRS.
- Chronic progression favors endotype in KLoSA, SHARE, CHARLS, and MHAS, but favors severity tertile in ELSA and HRS.
- The manuscript should not claim universal superiority of endotypes over severity gradients.

## Immediate Refinement Tasks

1. Manually inspect endotype class profiles and outcome ORs to identify clinically meaningful labels.
2. Run sensitivity models with baseline age plus baseline wave-specific covariates if available.
3. Consider domain-specific comparator models, not only severity tertiles, because some outcome signal may be driven by the baseline functional domain. Done for severity score, matched-domain score, four-domain score, and endotype-plus-domain diagnostics.
4. Extract mortality variables from harmonized tracker, end-of-life, exit, or raw mortality files. Current cleaned CSV pass now has mortality for CHARLS, ELSA, HRS, KLoSA, MHAS, and SHARE; LASI remains unavailable.
5. Decide whether the main paper should frame endotypes as cross-cohort heterogeneity mapping rather than as a uniformly superior prediction tool.

## Phase 5 Domain Comparator Status

- `scripts/build_phase5_domain_comparator_models.py` is built and run.
- Outputs are ready in `outputs/phase5_domain_comparator_metrics.csv`, `outputs/phase5_domain_comparator_terms.csv`, `outputs/phase5_domain_comparator_comparison.csv`, and `outputs/phase5_domain_comparator_report.md`.
- Interpretation memo is ready in `outputs/phase5_refinement_interpretation_memo.md`.
- For functional deterioration, four-domain continuous-score models outperform endotype-only models in every follow-up cohort by AIC and AUC.
- Endotype classes still add information after four-domain scores in selected diagnostic models, but this should be framed cautiously because the classes are derived from the domain scores.
- The paper should now emphasize clinically interpretable heterogeneity and cross-cohort profile structure, not universal prediction superiority.

## Immediate Mortality Extraction Tasks

1. Scan harmonized and raw Stata files for direct death, vital status, exit interview, and death-date variables. Done for Working_data DTA labels and cleaned CSV mortality variables.
2. Prioritize HRS, ELSA, SHARE, CHARLS, KLoSA, and MHAS because they have follow-up-ready endotype assignments in the current pipeline.
3. Build a mortality variable inventory with candidate variable names, labels, value labels, file paths, and usable IDs. Done for current cleaned CSV and Working_data DTA labels.
4. Only after candidate confirmation, merge mortality status/time into `outputs/phase5_participant_outcome_screen.csv`. Done as a separate Phase 6 mortality participant screen.

## Phase 6 Mortality Status

- `scripts/build_phase6_mortality_screen.py` is built and run.
- Mortality variables are confirmed from Working_data DTA labels: `radyear`, `radmonth`, and `iwstat`.
- Mortality participant screen is ready in `outputs/phase6_mortality_participant_screen.csv`.
- Mortality summary is ready in `outputs/phase6_mortality_summary.csv`.
- Mortality screen report is ready in `outputs/phase6_mortality_screen_report.md`.
- `scripts/build_phase6_mortality_models.py` is built and run.
- Cox model outputs are ready in `outputs/phase6_mortality_model_metrics.csv`, `outputs/phase6_mortality_model_terms.csv`, `outputs/phase6_mortality_model_comparison.csv`, and `outputs/phase6_mortality_model_report.md`.
- Mortality is ready for CHARLS, ELSA, HRS, KLoSA, MHAS, and SHARE.
- LASI remains unavailable for mortality in the current cleaned CSV pass.
- Four-domain continuous-score Cox models outperform endotype-only Cox models in all mortality-ready cohorts.
- Endotype-only mortality models outperform severity tertiles only in SHARE and MHAS.

## Immediate Manuscript-Readiness Tasks

1. Build a class-profile plus mortality/function HR/OR review table. Done in Phase 7.
2. Generate AIC delta heatmaps for functional deterioration, chronic progression, and mortality. Done in Phase 7.
3. Generate endotype profile plots annotated by mortality and functional deterioration risk. Done in Phase 7.
4. Check Cox proportional hazards assumptions before using mortality HRs in manuscript tables.
5. Decide whether LASI should remain baseline-profile-only or be excluded from the main outcome-validation manuscript.

## Phase 7 Manuscript Review Asset Status

- Class-level review table is ready in `outputs/phase7_class_outcome_review.csv`.
- Manuscript triage report is ready in `outputs/phase7_manuscript_review_report.md`.
- AIC delta heatmap inputs are ready in `outputs/phase7_aic_delta_vs_severity_tertile.csv` and `outputs/phase7_aic_delta_vs_four_domain_scores.csv`.
- Figures are ready under `outputs/figures/`.
- The main visual message is now stable: endotype-only models improve on severity tertiles in selected cohort-endpoint combinations, but four-domain continuous scores outperform endotype-only models across functional deterioration, chronic progression, and mortality.

## Immediate PH-Assumption Tasks

1. Build a Cox PH diagnostic script for the endotype mortality model. Done in Phase 8.
2. Test Schoenfeld-residual time trends by cohort where the diagnostic API is available. Done in Phase 8.
3. Flag models requiring time-interaction sensitivity or stratified reporting. Done in Phase 8.

## Phase 8 Mortality PH Diagnostic Status

- PH diagnostic outputs are ready in `outputs/phase8_mortality_ph_diagnostics.csv`, `outputs/phase8_mortality_ph_diagnostic_summary.csv`, and `outputs/phase8_mortality_ph_diagnostic_report.md`.
- CHARLS and MHAS had no flagged terms in the lightweight Schoenfeld-residual screen.
- KLoSA, SHARE, ELSA, and HRS had at least one flagged term.
- SHARE had the strongest PH concern, with four flagged terms.
- Mortality HRs require time-interaction or stratified Cox sensitivity before manuscript use.

## Immediate Sensitivity Tasks

1. Build time-interaction Cox models for flagged cohorts. Done as pragmatic early/late piecewise Cox sensitivity in Phase 9.
2. Compare baseline endotype HRs with endotype-by-log-time interaction models. Done as early/late HR stability comparison in Phase 9; a full time-varying coefficient model remains optional.
3. Consider reporting mortality as a secondary validation outcome if PH sensitivity is unstable. Current result supports mortality as secondary.
4. Finalize clinical class-label candidates from `outputs/phase7_class_outcome_review.csv`.

## Phase 9 Mortality Sensitivity Status

- Piecewise Cox outputs are ready in `outputs/phase9_mortality_piecewise_metrics.csv`, `outputs/phase9_mortality_piecewise_terms.csv`, `outputs/phase9_mortality_piecewise_stability.csv`, and `outputs/phase9_mortality_piecewise_report.md`.
- Drift-flagged mortality class terms: KLoSA class 2, SHARE class 5, HRS classes 3, 4, and 5.
- CHARLS, ELSA, and MHAS had no large early/late endotype HR drift by the current rule.
- Mortality should be reported as secondary or sensitivity-supported, not the sole primary validation endpoint.

## Immediate Class-Label Tasks

1. Build deterministic class-label candidates in English and Chinese. Done in Phase 10.
2. Use `outputs/phase7_class_outcome_review.csv` as the input table. Done.
3. Mark labels as provisional when mortality drift is flagged. Done.

## Phase 10 Class Label Status

- Label candidates are ready in `outputs/phase10_class_label_candidates.csv`.
- Label triage report is ready in `outputs/phase10_class_label_candidates_report.md`.
- English labels can be used as figure/table draft labels.
- Chinese labels can be used for internal review and project discussion.
- Provisional labels require manual review because their mortality HRs are unstable across follow-up periods.

## Immediate Manuscript Drafting Tasks

1. Create draft Table 1: selected cohorts, baseline N, complete-domain N, mortality/function follow-up N. Done in Phase 11.
2. Create draft Table 2: class profiles and candidate labels. Done in Phase 11.
3. Create draft Table 3: outcome validation summary with endotype vs severity and four-domain comparator deltas. Done in Phase 11.
4. Create draft Figure 1: endotype profile plot plus AIC delta heatmaps. Done in Phase 11.
5. Keep mortality as secondary validation unless PH sensitivity is explicitly described. Current Phase 11 table does this.

## Phase 11 Manuscript Draft Asset Status

- Draft Table 1 is ready in `outputs/phase11_table1_cohort_readiness.csv`.
- Draft Table 2 is ready in `outputs/phase11_table2_class_profiles_labels.csv`.
- Draft Table 3 is ready in `outputs/phase11_table3_outcome_validation_summary.csv`.
- Draft report is ready in `outputs/phase11_manuscript_tables_report.md`.
- Combined Figure 1 draft is ready in `outputs/figures/phase11_figure1_manuscript_draft.png` and `.pdf`.
- SHARE uses a wave-adjusted sensitivity denominator, so its selected endotype N is not the same denominator as the Phase 1 earliest-baseline N.
- LASI remains baseline-profile only for follow-up validation in the current cleaned CSV pass.

## Immediate Manuscript Text Tasks

1. Draft the Results skeleton around three claims: cross-cohort endotype structure, endpoint-specific validation, and comparator guardrail. Done in Phase 12.
2. Convert provisional labels into a manually approved label dictionary before final tables. Draft queue created in Phase 12; manual lock still needed.
3. Decide whether bridge sensitivity cohorts KLoSA and SHARE stay in the main display or move to sensitivity panels.
4. Add covariate-expanded sensitivity models if education, marital status, region, smoking, drinking, BMI, and physical activity harmonization is acceptable.
5. Run a final novelty screen before writing the Introduction as publication-ready text.

## Phase 12 Results Skeleton Status

- Results skeleton is ready in `outputs/phase12_results_skeleton.md` and `manuscript/results_skeleton.md`.
- Internal Chinese summary is ready in `outputs/phase12_internal_zh_summary.md` and `manuscript/internal_zh_summary.md`.
- Claim table is ready in `outputs/phase12_results_claims.csv`.
- Label dictionary draft is ready in `outputs/phase12_label_dictionary_draft.csv`.
- Label queue counts: 18 ready for manual lock, 5 require manual review because of mortality drift, 3 generic severity-aligned labels need review, and 3 LASI labels are baseline-only candidates.
- Results skeleton keeps the core guardrail explicit: four-domain continuous scores outperform endotype-only classes across tested endpoint-cohort rows, so the paper should claim interpretable heterogeneity rather than universal prediction superiority.

## Immediate Phase 13 Tasks

1. Lock a final label dictionary by manually reviewing `outputs/phase12_label_dictionary_draft.csv`. Display policy created in Phase 13; manual lock still needed.
2. Decide the main-display policy for KLoSA and SHARE: keep as bridge-sensitivity panels or include in main seven-cohort figure with clear footnotes. Draft display policy created in Phase 13.
3. Build a covariate inventory for education, marital status, region, smoking, drinking, physical activity, and BMI. Done in Phase 13.
4. If covariate coverage is acceptable, run age-plus-core-covariate sensitivity models for functional deterioration and mortality. Ready for Phase 14.
5. Refresh novelty screening before writing Introduction and Discussion as publication-ready text.

## Phase 13 Covariate And Display Policy Status

- Covariate candidate inventory is ready in `outputs/phase13_covariate_candidate_inventory.csv`.
- Cohort-level covariate readiness summary is ready in `outputs/phase13_covariate_readiness_summary.csv`.
- Participant-level covariate screen is ready in `outputs/phase13_covariate_participant_screen.csv`.
- Label/display policy is ready in `outputs/phase13_label_display_policy.csv`.
- Covariate report is ready in `outputs/phase13_covariate_inventory_report.md`.
- Manuscript-facing covariate sensitivity plan is ready in `manuscript/covariate_sensitivity_plan.md`.
- Minimal core covariates are ready in all seven cohorts: education, marital status, smoking, and drinking.
- Expanded core covariates are ready in ELSA, LASI, and SHARE; physical activity is the main limiting field in CHARLS, HRS, MHAS, and KLoSA under the current strict candidate rule.
- Optional BMI is ready in CHARLS, HRS, LASI, KLoSA, and SHARE.
- Label/display policy marks 18 labels as lock candidates, 8 labels as manual-review-before-lock, and 3 LASI labels as baseline-profile-only hold candidates.

## Immediate Phase 14 Tasks

1. Build covariate-expanded sensitivity models for functional deterioration using age plus minimal core covariates. Done in Phase 14.
2. Build covariate-expanded Cox sensitivity models for mortality using the same minimal core covariates. Done in Phase 14.
3. Add expanded-core models only for ELSA, LASI, and SHARE where rural/region and physical activity coverage is ready; LASI will still be baseline-only for outcomes until follow-up is available. Done where outcome data were available.
4. Report optional BMI sensitivity separately because BMI is close to the cardiometabolic construct. Done in Phase 14.
5. Compare sensitivity estimates against the current age-adjusted models and flag class labels whose outcome interpretation changes materially. Done in Phase 14.

## Phase 14 Covariate Sensitivity Status

- Functional covariate model metrics are ready in `outputs/phase14_functional_covariate_model_metrics.csv`.
- Functional model comparison is ready in `outputs/phase14_functional_covariate_model_comparison.csv`.
- Mortality covariate model metrics are ready in `outputs/phase14_mortality_covariate_model_metrics.csv`.
- Mortality model comparison is ready in `outputs/phase14_mortality_covariate_model_comparison.csv`.
- Endotype effect stability screen is ready in `outputs/phase14_endotype_effect_stability.csv`.
- Skipped-fit diagnostics are ready in `outputs/phase14_covariate_model_skipped.csv`.
- Report is ready in `outputs/phase14_covariate_sensitivity_report.md`.
- Manuscript-facing sensitivity summary is ready in `manuscript/covariate_sensitivity_results.md`.
- Functional deterioration minimal-core sensitivity was fit for CHARLS, ELSA, HRS, KLoSA, MHAS, and SHARE; LASI remains unavailable for follow-up validation.
- Mortality minimal-core sensitivity was fit for CHARLS, ELSA, HRS, KLoSA, MHAS, and SHARE; HRS severity-tertile minimal Cox returned a nonfinite result and is flagged in skipped fits.
- Stability flags mainly involve SHARE functional classes 4-5, HRS functional classes 3-5 in BMI/minimal sensitivity, ELSA functional class 5 in expanded sensitivity, and KLoSA mortality class 2 in BMI sensitivity.

## Immediate Phase 15 Tasks

1. Update `manuscript/results_skeleton.md` with the Phase 14 covariate sensitivity paragraph.
2. Add a supplementary table shell for Phase 14 sensitivity model comparisons and effect-stability flags.
3. Use Phase 14 flags to revise the final class-label lock queue.
4. Refresh novelty screening before writing Introduction and Discussion.
5. Decide whether Figure 1 should keep KLoSA/SHARE in the main panel or move them to sensitivity/supplement display.

## Phase 15 Manuscript Integration Status

- `scripts/build_phase15_manuscript_integration.py` is built and run.
- Integrated Results skeleton is ready in `outputs/phase15_results_skeleton_integrated.md` and `manuscript/results_skeleton.md`.
- Supplement table shell is ready in `outputs/phase15_supplement_table_shell.csv` and `manuscript/supplement_table_shell.md`.
- Phase 15 label-lock queue is ready in `outputs/phase15_label_lock_queue.csv`.
- Display policy recommendation is ready in `outputs/phase15_display_policy_recommendation.csv`.
- Novelty refresh sources and report are ready in `outputs/phase15_novelty_refresh_sources.csv` and `outputs/phase15_novelty_refresh_report.md`.
- Phase 15 label queue status: 16 ready for manual lock, 10 requiring manual review, and 3 baseline-only hold labels.
- Phase 14 stability flags block automatic locking for ELSA_C5, HRS_C3, HRS_C4, HRS_C5, KLoSA_C2, SHARE_C4, and SHARE_C5.
- Default display policy: CHARLS, ELSA, HRS, and MHAS in main validation panels; KLoSA and SHARE as sensitivity/supplement by default; LASI baseline-profile only.
- Targeted novelty refresh found no direct same-topic collision, but adjacent multidimensional aging, intrinsic-capacity, symptom-cluster, and predeath-trajectory literature requires conservative novelty claims.

## Immediate Phase 16 Tasks

1. Manually review `outputs/phase15_label_lock_queue.csv` and write a final locked label dictionary.
2. Update Table 2 labels and Figure 1 labels from the locked dictionary.
3. Convert `manuscript/results_skeleton.md` into a tighter Results section draft with table and figure callouts.
4. Decide whether to create two Figure 1 versions: strict-primary main panel only, and seven-cohort sensitivity version.
5. Draft Introduction and Discussion only after locking the label dictionary and keeping the novelty claims narrow.

## Phase 16 Label Lock And Manuscript Draft Status

- `scripts/build_phase16_label_lock_and_manuscript_draft.py` is built and run.
- Locked-for-draft label dictionary is ready in `outputs/phase16_locked_label_dictionary.csv`.
- Table 2 label-backfill table is ready in `outputs/phase16_table2_locked_labels.csv`.
- Figure 1 label map is ready in `outputs/phase16_figure1_label_map.csv`.
- Results draft is ready in `outputs/phase16_results_draft.md` and `manuscript/results_draft.md`.
- Main validation Figure 1 candidate is ready in `outputs/figures/phase16_figure1_main_validation.png` and `.pdf`.
- Seven-cohort sensitivity Figure 1 candidate is ready in `outputs/figures/phase16_figure1_seven_cohort_sensitivity.png` and `.pdf`.
- Label status remains conservative: 16 labels are locked for draft use, 10 labels remain review-required/not locked, and 3 LASI labels are baseline-only holds.
- Main validation Figure 1 uses CHARLS, ELSA, HRS, and MHAS. Seven-cohort sensitivity Figure 1 includes KLoSA, SHARE, and LASI with `[hold]` markers for LASI baseline-only labels.

## Immediate Phase 17 Tasks

1. Human-review the 10 `review_required_not_locked` labels in `outputs/phase16_locked_label_dictionary.csv`.
2. Decide whether review-required severity-aligned labels should be renamed to domain-neutral terms or collapsed into descriptive burden labels.
3. Use `manuscript/results_draft.md` as the Results base and edit it into journal prose.
4. Draft Introduction and Discussion from the Phase 15 novelty refresh, avoiding first/novelty overclaims.
5. Prepare final Table 1-3 and Supplement S1-S3 shells for manuscript assembly.

## Phase 17 Manuscript Assembly Status

- `scripts/build_phase17_manuscript_assembly.py` is built and run.
- Label-review packet is ready in `outputs/phase17_label_review_packet.csv`.
- Introduction and Discussion drafts are ready in `outputs/phase17_intro_discussion_draft.md`, `manuscript/introduction_draft.md`, and `manuscript/discussion_draft.md`.
- Table 1-3 manuscript draft is ready in `outputs/phase17_tables_1_3_manuscript.md` and `manuscript/tables_1_3_draft.md`.
- Supplement S1-S3 draft is ready in `outputs/phase17_supplement_s1_s3.md` and `manuscript/supplement_s1_s3_draft.md`.
- Claim-to-evidence guardrail map is ready in `outputs/phase17_claim_to_evidence_map.csv`.
- Manuscript assembly draft is ready in `outputs/phase17_manuscript_assembly_draft.md` and `manuscript/manuscript_assembly_draft.md`.
- The Phase 17 review packet contains 13 rows: 10 review-required/not locked labels and 3 LASI baseline-only hold labels.

## Immediate Phase 18 Tasks

1. Resolve the 13-row `outputs/phase17_label_review_packet.csv` with explicit human decisions.
2. Apply accepted label edits to the Phase 16/17 label dictionary and regenerate Table 2/Figure 1.
3. Convert `manuscript/manuscript_assembly_draft.md` into journal-style prose and remove internal draft-status notes.
4. Add formal citations and reference formatting, ideally through Zotero or a manual reference manager export.
5. Decide target journal and adapt word count, table count, and supplement layout to its instructions.

## Phase 18 Submission Draft v0 Status

- `scripts/build_phase18_submission_draft_v0.py` is built and run.
- Conservative auto-v0 label decisions are ready in `outputs/phase18_label_decisions_auto_v0.csv`.
- Phase 18 final label dictionary v0 is ready in `outputs/phase18_final_label_dictionary_v0.csv`.
- Table 2 final-label v0 table is ready in `outputs/phase18_table2_final_labels_v0.csv`.
- Figure 1 label map v0 is ready in `outputs/phase18_figure1_label_map_v0.csv`.
- Tables 1-3 v0 are ready in `outputs/phase18_tables_1_3_v0.md` and `manuscript/tables_1_3_phase18_v0.md`.
- Journal-style manuscript v0 is ready in `outputs/phase18_journal_style_manuscript_v0.md` and `manuscript/journal_style_manuscript_v0.md`.
- Submission-readiness checklist is ready in `outputs/phase18_submission_readiness_checklist.md` and `manuscript/submission_readiness_checklist.md`.
- Main validation Figure 1 v0 is ready in `outputs/figures/phase18_figure1_main_validation_v0.png` and `.pdf`.
- Seven-cohort sensitivity Figure 1 v0 is ready in `outputs/figures/phase18_figure1_seven_cohort_sensitivity_v0.png` and `.pdf`.
- Phase 18 decisions: 16 labels accepted from Phase 16, 7 locked with caveat, 3 auto-renamed conservatively, and 3 LASI baseline-only hold labels.
- Human signoff is still required for 13 labels before submission.

## Immediate Phase 19 Tasks

1. Resolve the 13 signoff/caveat/hold labels in `outputs/phase18_final_label_dictionary_v0.csv`.
2. Choose the target journal and apply its abstract, word-count, table, figure, and supplement limits.
3. Replace URL references in `manuscript/journal_style_manuscript_v0.md` with formal formatted citations.
4. Decide whether `phase18_figure1_main_validation_v0` or `phase18_figure1_seven_cohort_sensitivity_v0` is the main Figure 1.
5. Produce a clean submission package with no internal version notes after label signoff.

## Phase 19 Clean Submission Package Status

- `scripts/build_phase19_clean_submission_package.py` is built and run.
- Clean target-neutral manuscript is ready in `manuscript/clean_manuscript_target_neutral.md` and `outputs/phase19_clean_manuscript_target_neutral.md`.
- Verified reference list is ready in `manuscript/references_verified_v0.md`.
- Reference correction memo is ready in `outputs/phase19_reference_corrections.md`.
- Reference queue is ready in `outputs/phase19_verified_reference_queue.csv`.
- Label signoff sheet is ready in `outputs/phase19_label_signoff_sheet.csv`.
- Target-journal decision matrix is ready in `outputs/phase19_target_journal_decision_matrix.csv`.
- Title page and cover letter skeletons are ready in `manuscript/title_page_draft.md` and `manuscript/cover_letter_skeleton.md`.
- Package index and report are ready in `outputs/phase19_submission_package_index.md` and `outputs/phase19_clean_submission_package_report.md`.
- Phase 19 keeps only verified references in the clean manuscript and holds out old Phase 15 PMCID rows that resolved to unrelated or replaced sources.
- The clean package is still not submission-final because 13 labels require signoff, the target journal has not been selected, and author guidelines need live checking.

## Immediate Phase 20 Tasks

1. Complete the 13-row human signoff workflow in `outputs/phase19_label_signoff_sheet.csv`.
2. Choose the target journal from `outputs/phase19_target_journal_decision_matrix.csv`.
3. Live-check the selected journal's current author instructions, including abstract structure, word limits, tables/figures, reporting checklist, reference style, and data-sharing requirements.
4. Decide whether Figure 1 should use the main-validation cohort display or the seven-cohort sensitivity display.
5. Replace or remove all held Phase 15 novelty-source rows before any final submission.

## Phase 20 Target-Journal And Signoff Status

- `scripts/build_phase20_target_and_signoff_assets.py` is built and run.
- Human label-signoff template is ready in `outputs/phase20_label_signoff_decision_template.csv`.
- Label signoff review packet is ready in `outputs/phase20_label_signoff_review_packet.md`.
- Target-journal guideline snapshot is ready in `outputs/phase20_target_guideline_snapshot.csv`.
- Current clean-draft format gap check is ready in `outputs/phase20_manuscript_format_gap_check.csv`.
- Target selection memo is ready in `outputs/phase20_target_selection_memo.md` and `manuscript/phase20_working_target_plan.md`.
- Guideline source snapshot is ready in `outputs/phase20_guideline_sources.md`.
- Phase 20 report is ready in `outputs/phase20_target_and_signoff_report.md`.
- Official pages were checked for Age and Ageing, The Journals of Gerontology: Series A Medical Sciences, and BMC Geriatrics.
- Journal of the American Geriatrics Society remains on hold for manual author-guideline verification because the Wiley page was not accessible through the current tool session.
- Current clean draft word count is 1,228 words with a 245-word abstract and 3 references; it fits the captured Age and Ageing and JGMS Medical Sciences word limits before adding final tables, declarations, and target-specific details.

## Immediate Phase 21 Tasks

1. Fill `outputs/phase20_label_signoff_decision_template.csv` or obtain reviewer decisions for all 13 rows.
2. If no label changes are requested, generate an Age and Ageing working submission draft with <=3000 words, <=5 main data elements, sharpened clinical implications, and anonymized manuscript structure.
3. Generate a JGMS Medical Sciences alternative if the team prioritizes medical-gerontology scope and a 5200-word research article format.
4. Add target-specific declarations, data availability, funding, conflict-of-interest, author contribution, ethics, and reporting-checklist language.
5. Recheck all target-journal author instructions immediately before actual submission.

## Phase 21 BMC Geriatrics Template Package Status

- Active target changed to BMC Geriatrics per user instruction.
- `scripts/build_phase21_bmc_geriatrics_template_package.py` is built and run.
- The local Springer Nature template source is `E:\Reserch\Temp\_tmp_springer_nature_template_inspect_20260524`.
- BMC Geriatrics package directory is ready at `manuscript/bmc_geriatrics_submission/`.
- Zip package is ready at `manuscript/bmc_geriatrics_submission_package.zip`.
- Main TeX manuscript is ready at `manuscript/bmc_geriatrics_submission/bmc_geriatrics_main.tex`.
- BibTeX references are ready at `manuscript/bmc_geriatrics_submission/bmc_geriatrics_refs.bib`.
- Template files copied into the package: `sn-jnl.cls` and `sn-vancouver-num.bst`.
- Figure files copied into the package: `figure1_main_validation.png` and `figure1_seven_cohort_sensitivity.png`.
- Additional files are ready for class profiles, outcome validation, and the pre-submission label signoff template.
- Package manifest, summary, zip record, and report are ready under `outputs/phase21_*`.
- LaTeX source sanity checks passed, but PDF compilation was not completed because no local Tectonic or TeX Live runtime was detected.

## Immediate Phase 22 Tasks

1. Fill or finalize the 13 label decisions in `additional_file_3_label_signoff_decision_template.csv` / `outputs/phase20_label_signoff_decision_template.csv`.
2. Complete BMC declarations: ethics approval and consent, data availability, funding, competing interests, author contributions, and acknowledgements.
3. Decide whether Additional file 3 should be removed before final submission after labels are signed off.
4. Compile the LaTeX package on Overleaf/Springer submission system or install/use a local TeX runtime.
5. Re-export the package zip after label and declaration completion.

## Phase 22 BMC Review-Ready Package Status

- `scripts/build_phase22_bmc_review_ready_package.py` is built and run.
- Conservative label proposal is ready in `outputs/phase22_conservative_label_signoff_proposal.csv`.
- BMC cleaned class-profile additional file is ready in `outputs/phase22_bmc_class_profiles_review_ready.csv`.
- Review-ready package directory is ready at `manuscript/bmc_geriatrics_submission_review_ready/`.
- Review-ready zip is ready at `manuscript/bmc_geriatrics_review_ready_package.zip`.
- Package manifest, summary, report, remaining-author-items note, and LaTeX source sanity check are ready under `outputs/phase22_*`.
- The review-ready zip contains 10 files and no internal label-signoff worksheet.
- Additional file 1 has cleaned `bmc_label`, `bmc_label_status`, and `bmc_label_note` columns; no `bmc_label` contains `[signoff]`, `[caveat]`, or `[baseline-only]` bracket markers.
- TeX sanity checks passed: documentclass, begin/end document, bibliography, figure reference, declarations section, Additional file 3 absence, no duplicate label sentence, and brace balance.

## Immediate Phase 23 Tasks

1. Author-confirm `outputs/phase22_conservative_label_signoff_proposal.csv`; if accepted, record it as the final label decision file.
2. Complete BMC declarations and author metadata in `manuscript/bmc_geriatrics_submission_review_ready/bmc_geriatrics_main.tex`.
3. Replace placeholder author names, affiliations, corresponding author email, funding, author contributions, and acknowledgements.
4. Confirm cohort-specific data availability and ethics wording.
5. Compile via Overleaf/Springer or make a TeX runtime available locally, then regenerate the final zip.

## Phase 23 BMC Declarations Completion Status

- `scripts/build_phase23_bmc_declarations_completion_pack.py` is built and run.
- Declaration-ready package directory is ready at `manuscript/bmc_geriatrics_submission_declarations_ready/`.
- Declaration-ready zip is ready at `manuscript/bmc_geriatrics_declarations_ready_package.zip`.
- Declaration completion template is ready in `outputs/phase23_bmc_declarations_completion_template.csv`.
- Cohort data-availability template is ready in `outputs/phase23_cohort_data_availability_template.csv`.
- Author metadata template is ready in `outputs/phase23_author_metadata_template.csv`.
- AI-disclosure decision note is ready in `outputs/phase23_ai_disclosure_decision_note.md`.
- BMC completion precheck is ready in `outputs/phase23_bmc_completion_precheck.csv`.
- The declaration-ready TeX includes official data portal URLs for CHARLS, ELSA, HRS, KLoSA, LASI, MHAS, and SHARE.
- Precheck status: 10 pass rows, 4 author-input rows, and 1 policy-decision row.

## Immediate Phase 24 Tasks

1. Replace `[AUTHOR INPUT REQUIRED]` sections with final author-approved text.
2. Replace `[repository URL]` or remove the code-sharing clause if no public code repository will be provided.
3. Replace `[Initials]` placeholders in author contributions.
4. Decide whether to keep or remove the `Generative AI and AI-assisted technologies` subsection after reviewing current Springer Nature policy and the actual author workflow.
5. Compile the declaration-ready TeX on Overleaf/Springer/BMC or make a local TeX runtime available.
