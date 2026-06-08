# Multidomain Aging Endotypes Among Older Women

## Working Title

Multidomain aging endotypes among older women across seven international aging cohorts: functional, cognitive, affective, and cardiometabolic trajectories and adverse health transitions.

中文题目：七大国际老年队列中老年女性多域衰老亚型及不良健康转归：功能、认知、心理与心代谢轨迹研究。

## Current Decision

Use the seven cleaned aging cohorts as the primary evidence base:

- CHARLS
- ELSA
- HRS
- KLoSA
- LASI
- MHAS
- SHARE

The main paper should not claim novelty from building a generic frailty index, ADL/IADL transition model, sex-difference comparison, reproductive-factor frailty association, or anthropometric biological age score. Those spaces already have close published work.

## Core Hypothesis

Older women follow distinct multidomain aging endotypes defined by longitudinal changes across functional, cognitive, affective, and cardiometabolic domains. These endotypes have different risks of mortality, functional decline, cognitive decline, and multimorbidity progression, and their structure can be compared across countries or cohort systems.

## Main Design

- Population: women aged 50 years or older.
- Main analysis: cohort-specific multidomain trajectory/endotype modeling followed by cross-cohort alignment and meta-analysis.
- Male participants: optional sensitivity or contrast analysis only, not the main framing.
- CHARLS inflammaging module: exploratory subanalysis using CRP/WBC if variable completeness is acceptable.

## Local Data

Expected cleaned CSV root:

`E:\Database\七大老年健康数据库数据\csv 版本 清洗后`

The scripts in `scripts/` are read-only with respect to the source data and write outputs to `outputs/`.

## Files

- `novelty_matrix.md`: collision-risk matrix and positioning rules.
- `statistical_analysis_plan.md`: first-pass analytic specification.
- `scripts/build_variable_inventory.py`: variable availability audit for the seven cleaned CSV files.
- `scripts/build_phase1_feasibility.py`: baseline women 50+ feasibility counts.
- `scripts/build_phase2_harmonization.py`: sex coding confirmation and four-domain harmonization readiness.
- `scripts/build_phase3_domain_scores.py`: women 50+ four-domain score construction and QC.
- `scripts/build_phase4_endotype_models.py`: first-pass Gaussian mixture endotype screen and severity comparator.
- `scripts/build_phase5_outcome_inventory.py`: follow-up outcome availability screen after endotype assignment.
- `scripts/build_phase5_outcome_models.py`: first-pass outcome validation models for endotype classes versus severity tertiles.
- `scripts/build_phase5_domain_comparator_models.py`: stricter outcome validation against continuous severity and domain-score comparators.
- `scripts/build_phase6_mortality_screen.py`: DTA-label-confirmed mortality variable screen and participant-level mortality follow-up construction.
- `scripts/build_phase6_mortality_models.py`: first-pass Cox proportional hazards mortality validation models.
- `scripts/build_phase7_manuscript_review_assets.py`: class-level outcome review tables and manuscript triage figures.
- `scripts/build_phase8_mortality_ph_diagnostics.py`: lightweight Schoenfeld-residual proportional-hazards screen for mortality Cox models.
- `scripts/build_phase9_mortality_piecewise_sensitivity.py`: early/late piecewise Cox sensitivity for mortality HR stability.
- `scripts/build_phase10_class_label_candidates.py`: deterministic English and Chinese class-label candidates for manuscript triage.
- `scripts/build_phase11_manuscript_tables.py`: manuscript-facing draft tables and combined Figure 1 draft.
- `scripts/build_phase12_results_skeleton.py`: conservative Results skeleton, manuscript claims table, and label review queue.
- `scripts/build_phase13_covariate_inventory.py`: baseline covariate coverage screen, participant-level covariate screen, and label/display policy.
- `scripts/build_phase14_covariate_sensitivity_models.py`: functional deterioration and mortality covariate-sensitivity models.
- `scripts/build_phase15_manuscript_integration.py`: integrated Results skeleton update, supplement table shell, label-lock queue, display policy, and novelty refresh log.
- `scripts/build_phase16_label_lock_and_manuscript_draft.py`: locked-for-draft label dictionary, Table 2 label backfill, Figure 1 label maps, and Results draft.
- `scripts/build_phase17_manuscript_assembly.py`: label-review packet, Introduction/Discussion draft, Table 1-3 draft, Supplement S1-S3 draft, claim guardrails, and manuscript assembly draft.
- `scripts/build_phase18_submission_draft_v0.py`: conservative auto-v0 label decisions, submission-style manuscript draft, final Table/Figure v0 assets, and submission readiness checklist.
- `scripts/build_phase19_clean_submission_package.py`: clean target-neutral manuscript package, verified reference queue, reference-correction memo, label signoff sheet, target-journal decision matrix, title page draft, and cover letter skeleton.
- `scripts/build_phase20_target_and_signoff_assets.py`: human label-signoff decision template, official target-journal guideline snapshot, manuscript format gap check, and working target memo.
- `scripts/build_phase21_bmc_geriatrics_template_package.py`: BMC Geriatrics package generated from the local Springer Nature LaTeX template.
- `scripts/build_phase22_bmc_review_ready_package.py`: BMC Geriatrics review-ready package with conservative label proposal, cleaned additional files, and internal signoff worksheet removed from the zip.
- `scripts/build_phase23_bmc_declarations_completion_pack.py`: BMC declarations/data-availability completion pack with cohort data portal URLs, author metadata template, and AI-disclosure decision note.
- `outputs/`: generated feasibility tables and variable maps.
- `manuscript/`: generated manuscript-facing text drafts.

## Current Submission Package

Phase 19 creates the current collaborator-review package:

- `manuscript/clean_manuscript_target_neutral.md`
- `manuscript/references_verified_v0.md`
- `manuscript/title_page_draft.md`
- `manuscript/cover_letter_skeleton.md`
- `outputs/phase19_verified_reference_queue.csv`
- `outputs/phase19_reference_corrections.md`
- `outputs/phase19_label_signoff_sheet.csv`
- `outputs/phase19_target_journal_decision_matrix.csv`
- `outputs/phase19_submission_package_index.md`
- `outputs/phase19_clean_submission_package_report.md`

The clean draft cites only verified references. The old Phase 15 `References To Format` list should not be copied into a submission draft because several PMCID rows were found to be unrelated or replaced during Phase 19.

Phase 20 adds the current target and signoff planning layer:

- `outputs/phase20_label_signoff_decision_template.csv`
- `outputs/phase20_label_signoff_review_packet.md`
- `outputs/phase20_target_guideline_snapshot.csv`
- `outputs/phase20_manuscript_format_gap_check.csv`
- `outputs/phase20_target_selection_memo.md`
- `outputs/phase20_guideline_sources.md`
- `outputs/phase20_target_and_signoff_report.md`
- `manuscript/phase20_working_target_plan.md`

The working recommendation is Age and Ageing if the story is tightened around clinical geriatric implications, with The Journals of Gerontology: Series A, Medical Sciences as the strongest scientific-fit alternative. Journal of the American Geriatrics Society is held for manual guideline verification because its Wiley author-guideline page was not accessible in the current tool session.

## BMC Geriatrics Template Package

The current BMC package is under:

- `manuscript/bmc_geriatrics_submission/`
- `manuscript/bmc_geriatrics_submission_package.zip`

It was generated from:

- `E:\Reserch\Temp\_tmp_springer_nature_template_inspect_20260524`

Main files:

- `manuscript/bmc_geriatrics_submission/bmc_geriatrics_main.tex`
- `manuscript/bmc_geriatrics_submission/bmc_geriatrics_refs.bib`
- `manuscript/bmc_geriatrics_submission/sn-jnl.cls`
- `manuscript/bmc_geriatrics_submission/sn-vancouver-num.bst`
- `manuscript/bmc_geriatrics_submission/figure1_main_validation.png`
- `manuscript/bmc_geriatrics_submission/figure1_seven_cohort_sensitivity.png`
- `manuscript/bmc_geriatrics_submission/bmc_geriatrics_cover_letter.md`
- `outputs/phase21_latex_compile_check.md`

Local PDF compilation was not completed because this machine currently has no detected Tectonic or TeX Live runtime. The source package is ready for Overleaf/Springer submission-system compilation or for local compilation after a TeX runtime is made available.

## BMC Review-Ready Package

Phase 22 creates the cleaner BMC review package:

- `manuscript/bmc_geriatrics_submission_review_ready/`
- `manuscript/bmc_geriatrics_review_ready_package.zip`
- `outputs/phase22_conservative_label_signoff_proposal.csv`
- `outputs/phase22_bmc_class_profiles_review_ready.csv`
- `outputs/phase22_bmc_review_ready_manifest.csv`
- `outputs/phase22_bmc_review_ready_summary.csv`
- `outputs/phase22_bmc_review_ready_report.md`
- `outputs/phase22_bmc_remaining_author_items.md`
- `outputs/phase22_latex_source_sanity_check.md`

This package removes the internal label-signoff worksheet from the zip and cleans label display fields in Additional file 1. It is still not submission-final because author confirmation, declarations, and cohort data-use wording remain incomplete.

## BMC Declarations Completion Package

Phase 23 creates the current declaration-ready package:

- `manuscript/bmc_geriatrics_submission_declarations_ready/`
- `manuscript/bmc_geriatrics_declarations_ready_package.zip`
- `outputs/phase23_bmc_declarations_completion_template.csv`
- `outputs/phase23_cohort_data_availability_template.csv`
- `outputs/phase23_author_metadata_template.csv`
- `outputs/phase23_ai_disclosure_decision_note.md`
- `outputs/phase23_bmc_completion_precheck.csv`
- `outputs/phase23_bmc_declarations_ready_report.md`

The TeX now contains structured BMC declarations and data-availability wording with official data portal URLs for CHARLS, ELSA, HRS, KLoSA, LASI, MHAS, and SHARE. It still contains explicit author-input placeholders that must be completed before submission.
