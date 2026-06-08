# Implementation Log

## 2026-05-31

Implemented the research-plan scaffold for the women-only multidomain aging endotype project.

## Final Novelty Check

Exact direct-collision search:

`older women multidomain aging endotypes latent class CHARLS HRS ELSA SHARE KLoSA MHAS LASI`

Result: no direct same-topic hit in first-pass web search. Adjacent literature remains strong around harmonized frailty index, sex disparities in health transitions, frailty/depression/CVD, AnthropoAge, and reproductive factors with frailty.

Decision: proceed only with a multidomain endotype framing, not a generic frailty, sex-difference, biological-age, or reproductive-factor frailty framing.

## Local Variable Audit

Command run:

```powershell
python 'E:\Reserch\Older women\scripts\build_variable_inventory.py' --data-root 'E:\Database\七大老年健康数据库数据\csv 版本 清洗后' --output-dir 'E:\Reserch\Older women\outputs'
```

Generated outputs:

- `outputs/cohort_summary.csv`
- `outputs/domain_variable_inventory.csv`
- `outputs/key_variable_matrix.csv`
- `outputs/variable_availability_report.md`

## Feasibility Findings

- Total cleaned person-wave records across the seven CSVs: 916,824.
- Functional variables are widely available but differ by cohort.
- Cardiometabolic/chronic disease variables are widely available.
- Cognitive variables are usable in CHARLS, ELSA, HRS, KLoSA, LASI, and partly SHARE; MHAS cleaned file has limited cognitive candidates in the current key list.
- Affective variables are strongest in CHARLS, ELSA, HRS, KLoSA, LASI, and limited in MHAS/SHARE.
- Inflammaging is not a shared seven-cohort domain. The cleaned files currently support it mainly in CHARLS through `bl_crp` and `bl_wbc`.
- LASI appears to lack a standard `wave` variable in the cleaned CSV, so it should be treated as cross-sectional or baseline validation unless a longitudinal LASI file is found.

## Coding Caution

The variable `ragender` appears to use `0` and `1`, with `0` likely representing women in several cohorts based on female-specific variable availability. This must be confirmed against the source codebooks before final sex filtering.

## Next Analysis Step

Create the first analysis notebook/script to:

1. Confirm sex coding from codebooks or variable labels.
2. Build a cohort-specific women-only baseline table.
3. Harmonize a minimal four-domain variable set.
4. Test whether the derived classes are more informative than a simple low/medium/high frailty gradient.

## 2026-05-31 Move To Project Root

The project was moved from `E:\Reserch\Idea\female_multidomain_aging_endotypes` to `E:\Reserch\Older women` and should now be run from that directory.

## 2026-05-31 Phase 1 Start

Validation and feasibility scripts were run from the new project root through WSL `research-py312`, following `E:\Reserch\AGENTS.md`.

Commands run:

```powershell
wsl.exe -d Ubuntu -- bash -lc "cd '/mnt/e/Reserch/Older women' && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python -m py_compile scripts/build_variable_inventory.py scripts/build_phase1_feasibility.py && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python scripts/build_variable_inventory.py --data-root '/mnt/e/Database/七大老年健康数据库数据/csv 版本 清洗后' --output-dir outputs && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python scripts/build_phase1_feasibility.py --data-root '/mnt/e/Database/七大老年健康数据库数据/csv 版本 清洗后' --output-dir outputs"
```

Phase 1 outputs:

- `outputs/phase1_baseline_feasibility.csv`
- `outputs/phase1_feasibility_report.md`

Initial women aged 50+ baseline counts:

- CHARLS: 6,878
- ELSA: 6,292
- HRS: 11,005
- KLoSA: 4,344
- LASI: 28,165
- MHAS: 7,440
- SHARE: 15,814

The sex coding remains a codebook confirmation item before formal analysis.

## 2026-05-31 Phase 2 Sex Coding And Harmonization

Added and ran `scripts/build_phase2_harmonization.py` through WSL `research-py312`.

Command run:

```powershell
wsl.exe -d Ubuntu -- bash -lc "cd '/mnt/e/Reserch/Older women' && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python -m py_compile scripts/build_phase2_harmonization.py && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python scripts/build_phase2_harmonization.py --database-root '/mnt/e/Database/七大老年健康数据库数据' --output-dir outputs"
```

Generated outputs:

- `outputs/sex_coding_confirmation.csv`
- `outputs/four_domain_harmonization_candidates.csv`
- `outputs/four_domain_readiness_summary.csv`
- `outputs/four_domain_wave_readiness.csv`
- `outputs/phase2_harmonization_report.md`

Sex coding is now confirmed from Working_data Stata value labels and local merge do-files:

- `ragender == 0`: women
- `ragender == 1`: men

Earliest-wave four-primary-domain cohorts are CHARLS and HRS. Practical earliest-wave modeling can include KLoSA with a performance/frailty functional bridge. Wave-adjusted four-primary-domain cohorts are CHARLS, ELSA, and HRS; practical wave-adjusted modeling can include KLoSA. LASI needs chronic disease extraction beyond BMI/BP, while MHAS and SHARE need targeted cognition/depression-score extraction before four-domain primary modeling.

## 2026-05-31 Phase 2 Targeted Variable Expansion

Expanded the Phase 2 harmonization candidate specification after inspecting LASI, MHAS, and SHARE Working_data/Harmonized DTA variable names and labels.

Resolved variables:

- LASI cardiometabolic/chronic primary variables: `r1hibpe`, `r1diabe`, `r1hearte`, `r1stroke`, `r1hchole`, `r1cancre`.
- MHAS cognition and affective primary variables: `imrc8`, `dlrc8`, `ser7`, `orient_m`, `cesd_m`.
- SHARE cognition and affective primary variables: `imrc`, `dlrc`, `ser7`, `orient`, `numer_s`, `eurod`.

After rerunning Phase 2, strict earliest-wave four-primary-domain cohorts are CHARLS, ELSA, HRS, LASI, and MHAS. KLoSA remains practical with a functional performance bridge. SHARE becomes practical in wave-adjusted sensitivity analyses, but not strict primary, because its functional domain still depends on frailty/grip bridge variables rather than ADL/IADL.

## 2026-05-31 Phase 3 Domain Scores

Added and ran `scripts/build_phase3_domain_scores.py` through WSL `research-py312`.

Command run:

```powershell
wsl.exe -d Ubuntu -- bash -lc "cd '/mnt/e/Reserch/Older women' && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python -m py_compile scripts/build_phase3_domain_scores.py && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python scripts/build_phase3_domain_scores.py --data-root '/mnt/e/Database/七大老年健康数据库数据/csv 版本 清洗后' --output-dir outputs"
```

Generated outputs:

- `outputs/phase3_domain_scores_long.csv`
- `outputs/phase3_domain_scores.csv`
- `outputs/phase3_domain_missingness.csv`
- `outputs/phase3_domain_score_distribution.csv`
- `outputs/phase3_domain_correlations.csv`
- `outputs/phase3_domain_score_qc.md`

Age derivation in Phase 3 now follows the Phase 1 logic: use the selected age variable first, then derive age from interview year minus birth year where needed. This is necessary for MHAS wave 1 and wave 2.

Strict earliest-wave primary cohorts and complete four-domain counts:

- CHARLS wave 1: 6,019 / 6,878 complete.
- ELSA wave 1: 6,104 / 6,292 complete.
- HRS wave 5: 10,202 / 11,005 complete.
- LASI all rows: 27,433 / 28,165 complete.
- MHAS wave 1: 6,733 / 7,440 complete.

Sensitivity cohorts:

- KLoSA wave 3 functional-bridge sensitivity: 4,081 / 4,344 complete.
- SHARE wave 6 functional-bridge wave-adjusted sensitivity: 36,006 / 37,539 complete.

No selected analysis set had an absolute pairwise domain correlation >= 0.70, so the current scores do not immediately collapse into a single severity gradient at the pairwise-correlation screen.

## 2026-06-01 Phase 4 Endotype Screen

Added and ran `scripts/build_phase4_endotype_models.py` through WSL `research-py312`.

Command run:

```powershell
wsl.exe -d Ubuntu -- bash -lc "cd '/mnt/e/Reserch/Older women' && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python -m py_compile scripts/build_phase4_endotype_models.py && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python scripts/build_phase4_endotype_models.py --scores outputs/phase3_domain_scores.csv --output-dir outputs --random-state 20260601 --n-init 5"
```

Generated outputs:

- `outputs/phase4_gmm_model_metrics.csv`
- `outputs/phase4_gmm_class_profiles.csv`
- `outputs/phase4_best_model_summary.csv`
- `outputs/phase4_best_model_assignments.csv`
- `outputs/phase4_severity_comparator_profiles.csv`
- `outputs/phase4_endotype_screen_report.md`

Model selection uses the lowest BIC among converged Gaussian mixture models with minimum class size >= 5%. The BIC-only winner is retained in the CSV outputs for transparency.

Selected strict-primary models:

- CHARLS: 3 classes, N = 6,019.
- ELSA: 5 classes, N = 6,104.
- HRS: 5 classes, N = 10,202.
- LASI: 3 classes, N = 27,433.
- MHAS: 5 classes, N = 6,733.

Sensitivity models:

- KLoSA functional-bridge earliest sensitivity: 3 classes, N = 4,081.
- SHARE functional-bridge wave-adjusted sensitivity: 5 classes, N = 36,006.

BIC-only 5-class solutions were rejected for KLoSA and LASI because their smallest classes were 1.13% and 1.65%, respectively. All selected best-model profiles were flagged as domain-specific by the automated screening rule, but manual profile review remains required before manuscript claims.

## 2026-06-01 Phase 5 Outcome Inventory

Added and ran `scripts/build_phase5_outcome_inventory.py` through WSL `research-py312`.

Command run:

```powershell
wsl.exe -d Ubuntu -- bash -lc "cd '/mnt/e/Reserch/Older women' && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python -m py_compile scripts/build_phase5_outcome_inventory.py && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python scripts/build_phase5_outcome_inventory.py --data-root '/mnt/e/Database/七大老年健康数据库数据/csv 版本 清洗后' --scores-long outputs/phase3_domain_scores_long.csv --assignments outputs/phase4_best_model_assignments.csv --output-dir outputs"
```

Generated outputs:

- `outputs/phase5_outcome_variable_inventory.csv`
- `outputs/phase5_participant_outcome_screen.csv`
- `outputs/phase5_followup_outcome_inventory.csv`
- `outputs/phase5_outcome_inventory_report.md`

Key screening findings:

- No direct mortality candidate variable was found in the cleaned seven-cohort CSV files.
- CHARLS has a broad status-like hit, `cog_status`, but this is not a direct mortality variable.
- Mortality validation needs targeted extraction from harmonized tracker, end-of-life, exit, or raw mortality files.
- Functional deterioration and chronic progression can be screened from the cleaned longitudinal CSV files for CHARLS, ELSA, HRS, KLoSA, MHAS, and SHARE.
- LASI currently contributes baseline endotypes but no cleaned longitudinal follow-up in this CSV pass.

Overall follow-up availability among Phase 4 assigned participants:

- CHARLS: 5,724 / 6,019 with later follow-up.
- ELSA: 5,155 / 6,104 with later follow-up.
- HRS: 9,476 / 10,202 with later follow-up.
- KLoSA: 3,834 / 4,081 with later follow-up.
- MHAS: 6,285 / 6,733 with later follow-up.
- SHARE: 20,532 / 36,006 with later follow-up.
- LASI: 0 / 27,433 with later follow-up.

Next modeling priority is functional deterioration, with chronic progression as a secondary validation outcome. Mortality should be added after direct mortality variables are extracted from non-cleaned harmonized/raw sources.

## 2026-06-01 Phase 5 Outcome Models

Added and ran `scripts/build_phase5_outcome_models.py` through WSL `research-py312`.

Command run:

```powershell
wsl.exe -d Ubuntu -- bash -lc "cd '/mnt/e/Reserch/Older women' && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python -m py_compile scripts/build_phase5_outcome_models.py && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python scripts/build_phase5_outcome_models.py --participant-screen outputs/phase5_participant_outcome_screen.csv --output-dir outputs --min-events 20"
```

Generated outputs:

- `outputs/phase5_outcome_model_metrics.csv`
- `outputs/phase5_outcome_model_terms.csv`
- `outputs/phase5_outcome_model_comparison.csv`
- `outputs/phase5_outcome_model_skipped.csv`
- `outputs/phase5_outcome_model_report.md`

Primary functional-deterioration validation compared age-adjusted endotype-class models against age-adjusted severity-tertile models. Positive delta AIC favors endotype over severity tertile.

Functional deterioration results:

- KLoSA: delta AIC +7.04, delta AUC +0.0052, favoring endotype weakly.
- SHARE: delta AIC +64.92, delta AUC +0.0035, favoring endotype weakly by AUC and clearly by AIC.
- CHARLS: delta AIC -15.20, delta AUC -0.0067, favoring severity tertile.
- ELSA: delta AIC -37.32, delta AUC -0.0074, favoring severity tertile.
- HRS: delta AIC -83.33, delta AUC -0.0088, favoring severity tertile.
- MHAS: delta AIC +23.26, delta AUC +0.0060, favoring endotype weakly.

Secondary chronic-progression results:

- KLoSA, SHARE, CHARLS, and MHAS favored endotype by AIC.
- ELSA and HRS favored severity tertile by AIC.
- MHAS showed the largest endotype advantage for chronic progression, with delta AIC +193.73 and delta AUC +0.0382.

Interpretation: Phase 5 does not support a simple claim that endotypes universally outperform severity gradients. A more defensible framing is that endotypes reveal cohort-specific domain-pattern heterogeneity and add outcome information in selected cohorts, while some cohorts are adequately captured by overall severity.

## 2026-06-01 Phase 5 Domain Comparator Refinement

Added and ran `scripts/build_phase5_domain_comparator_models.py` through WSL `research-py312`.

Command run:

```powershell
wsl.exe -d Ubuntu -- bash -lc "cd '/mnt/e/Reserch/Older women' && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python -m py_compile scripts/build_phase5_domain_comparator_models.py && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python scripts/build_phase5_domain_comparator_models.py --participant-screen outputs/phase5_participant_outcome_screen.csv --output-dir outputs --min-events 20"
```

Generated outputs:

- `outputs/phase5_domain_comparator_metrics.csv`
- `outputs/phase5_domain_comparator_terms.csv`
- `outputs/phase5_domain_comparator_comparison.csv`
- `outputs/phase5_domain_comparator_skipped.csv`
- `outputs/phase5_domain_comparator_report.md`
- `outputs/phase5_refinement_interpretation_memo.md`

Key refinement finding:

- For functional deterioration, the age-adjusted four-domain continuous-score model had lower AIC and higher AUC than the endotype-only model in every cohort with follow-up.
- This argues against a manuscript claim that endotype classes are a universally superior standalone prediction model.
- Endotype class still added AIC improvement after four-domain scores in selected overadjustment-style diagnostics, especially SHARE, CHARLS, ELSA, and HRS for functional deterioration.
- The recommended framing is now heterogeneity mapping plus clinically interpretable profiles, with outcome relevance that is cohort- and endpoint-dependent.

## 2026-06-01 Phase 5 Mortality Readiness Correction

The initial Phase 5 outcome inventory used variable-name pattern matching and missed `radyear`, `radmonth`, and `iwstat` as mortality variables because their names do not contain `death` or `mortality`.

Working_data DTA label inspection confirmed:

- `radyear`: death year.
- `radmonth`: death month.
- `iwstat`: death or survival/interview status, depending on cohort label.

The Phase 5 outcome-inventory pattern was updated and rerun. Direct mortality candidates are now correctly detected in CHARLS, ELSA, HRS, KLoSA, MHAS, and SHARE cleaned CSV files. LASI still lacks mortality variables in the current cleaned CSV pass.

## 2026-06-01 Phase 6 Mortality Screen

Added and ran `scripts/build_phase6_mortality_screen.py` through WSL `research-py312`.

Command run:

```powershell
wsl.exe -d Ubuntu -- bash -lc "cd '/mnt/e/Reserch/Older women' && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python -m py_compile scripts/build_phase6_mortality_screen.py && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python scripts/build_phase6_mortality_screen.py --data-root '/mnt/e/Database/七大老年健康数据库数据/csv 版本 清洗后' --database-root '/mnt/e/Database/七大老年健康数据库数据' --assignments outputs/phase4_best_model_assignments.csv --output-dir outputs"
```

Generated outputs:

- `outputs/phase6_mortality_variable_inventory.csv`
- `outputs/phase6_mortality_participant_screen.csv`
- `outputs/phase6_mortality_summary.csv`
- `outputs/phase6_mortality_screen_report.md`

Mortality follow-up availability and deaths among Phase 4 assigned participants:

- CHARLS: 5,872 / 6,019 available; 704 deaths.
- ELSA: 5,237 / 6,104 available; 353 deaths.
- HRS: 10,044 / 10,202 available; 5,569 deaths.
- KLoSA: 3,990 / 4,081 available; 726 deaths.
- MHAS: 6,487 / 6,733 available; 2,236 deaths.
- SHARE: 22,732 / 36,006 available; 3,061 deaths.
- LASI: 0 / 27,433 available in the current cleaned CSV pass.

## 2026-06-01 Phase 6 Mortality Cox Models

Added and ran `scripts/build_phase6_mortality_models.py` through WSL `research-py312`.

Command run:

```powershell
wsl.exe -d Ubuntu -- bash -lc "cd '/mnt/e/Reserch/Older women' && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python -m py_compile scripts/build_phase6_mortality_models.py && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python scripts/build_phase6_mortality_models.py --mortality-screen outputs/phase6_mortality_participant_screen.csv --output-dir outputs --min-events 20"
```

Generated outputs:

- `outputs/phase6_mortality_model_metrics.csv`
- `outputs/phase6_mortality_model_terms.csv`
- `outputs/phase6_mortality_model_comparison.csv`
- `outputs/phase6_mortality_model_skipped.csv`
- `outputs/phase6_mortality_model_report.md`

Mortality model interpretation:

- Endotype-only Cox models beat severity tertiles by partial AIC in SHARE and MHAS.
- Severity tertiles beat endotype-only models in KLoSA, CHARLS, ELSA, and HRS.
- Four-domain continuous-score Cox models beat endotype-only models in all six mortality-ready cohorts.
- Endotype-plus-four-domain diagnostic models improved over four-domain scores in KLoSA, SHARE, HRS, and MHAS, but not CHARLS or ELSA.
- This reinforces the current framing: endotypes are useful for interpretable heterogeneity mapping and selected incremental diagnostics, but not as universally superior standalone predictors.

## 2026-06-01 Phase 7 Manuscript Review Assets

Added and ran `scripts/build_phase7_manuscript_review_assets.py` through WSL `research-py312`.

Command run:

```powershell
wsl.exe -d Ubuntu -- bash -lc "cd '/mnt/e/Reserch/Older women' && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python -m py_compile scripts/build_phase7_manuscript_review_assets.py && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python scripts/build_phase7_manuscript_review_assets.py --output-dir outputs"
```

Generated outputs:

- `outputs/phase7_class_outcome_review.csv`
- `outputs/phase7_aic_delta_vs_severity_tertile.csv`
- `outputs/phase7_aic_delta_vs_four_domain_scores.csv`
- `outputs/phase7_manuscript_review_report.md`
- `outputs/figures/phase7_aic_delta_vs_severity_tertile.png`
- `outputs/figures/phase7_aic_delta_vs_severity_tertile.svg`
- `outputs/figures/phase7_aic_delta_vs_four_domain_scores.png`
- `outputs/figures/phase7_aic_delta_vs_four_domain_scores.svg`
- `outputs/figures/phase7_endotype_profiles_with_outcomes.png`
- `outputs/figures/phase7_endotype_profiles_with_outcomes.svg`

The class review table combines selected Phase 4 class profiles with functional-deterioration event rates and age-adjusted ORs, chronic-progression event rates and age-adjusted ORs, and mortality event rates and age-adjusted Cox HRs. The AIC delta heatmaps confirm visually that endotype-only models sometimes improve on severity tertiles, but consistently underperform four-domain continuous-score models.

## 2026-06-01 Phase 8 Mortality PH Diagnostics

Added and ran `scripts/build_phase8_mortality_ph_diagnostics.py` through WSL `research-py312`.

Command run:

```powershell
wsl.exe -d Ubuntu -- bash -lc "cd '/mnt/e/Reserch/Older women' && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python -m py_compile scripts/build_phase8_mortality_ph_diagnostics.py && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python scripts/build_phase8_mortality_ph_diagnostics.py --mortality-screen outputs/phase6_mortality_participant_screen.csv --output-dir outputs --min-events 20"
```

Generated outputs:

- `outputs/phase8_mortality_ph_diagnostics.csv`
- `outputs/phase8_mortality_ph_diagnostic_summary.csv`
- `outputs/phase8_mortality_ph_diagnostic_skipped.csv`
- `outputs/phase8_mortality_ph_diagnostic_report.md`

PH screen findings for the age-adjusted endotype Cox model:

- CHARLS: no flagged terms.
- MHAS: no flagged terms.
- KLoSA: 1 flagged term.
- ELSA: 1 flagged term.
- HRS: 2 flagged terms.
- SHARE: 4 flagged terms.
- LASI: skipped because mortality follow-up is unavailable in the current cleaned CSV pass.

Interpretation: mortality HRs should not be used as final manuscript estimates without sensitivity checks. SHARE, HRS, ELSA, and KLoSA need time-interaction or stratified Cox sensitivity analyses if mortality is retained as a key outcome.

## 2026-06-01 Phase 9 Mortality Piecewise Cox Sensitivity

Added and ran `scripts/build_phase9_mortality_piecewise_sensitivity.py` through WSL `research-py312`.

Command run:

```powershell
wsl.exe -d Ubuntu -- bash -lc "cd '/mnt/e/Reserch/Older women' && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python -m py_compile scripts/build_phase9_mortality_piecewise_sensitivity.py && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python scripts/build_phase9_mortality_piecewise_sensitivity.py --mortality-screen outputs/phase6_mortality_participant_screen.csv --output-dir outputs --min-events 20"
```

Generated outputs:

- `outputs/phase9_mortality_piecewise_metrics.csv`
- `outputs/phase9_mortality_piecewise_terms.csv`
- `outputs/phase9_mortality_piecewise_stability.csv`
- `outputs/phase9_mortality_piecewise_skipped.csv`
- `outputs/phase9_mortality_piecewise_report.md`

The piecewise sensitivity splits each cohort at its median observed death time and compares early-period and late-period endotype HRs.

Drift flags:

- KLoSA class 2: early HR 0.67, late HR 1.38, direction change and large drift.
- SHARE class 5: early HR 4.81, late HR 2.52, large drift.
- HRS class 3: early HR 2.85, late HR 1.83, large drift.
- HRS class 4: early HR 2.92, late HR 1.62, large drift.
- HRS class 5: early HR 3.83, late HR 2.21, large drift.

Interpretation: mortality remains usable as a secondary validation outcome, but full-follow-up mortality HRs for drift-flagged classes should not be interpreted as single constant effects. Functional deterioration remains the cleaner first validation endpoint.

## 2026-06-01 Phase 10 Class Label Candidates

Added and ran `scripts/build_phase10_class_label_candidates.py` through WSL `research-py312`.

Command run:

```powershell
wsl.exe -d Ubuntu -- bash -lc "cd '/mnt/e/Reserch/Older women' && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python -m py_compile scripts/build_phase10_class_label_candidates.py && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python scripts/build_phase10_class_label_candidates.py --output-dir outputs"
```

Generated outputs:

- `outputs/phase10_class_label_candidates.csv`
- `outputs/phase10_class_label_candidates_report.md`

The label table provides deterministic English and Chinese candidate labels using class burden level, dominant/spared domains, outcome signals, and Phase 9 mortality-drift flags. Labels are marked `provisional` when mortality HRs show early/late drift. These labels are ready for manual manuscript triage, but should not be treated as final labels without clinical review.

## 2026-06-01 Phase 11 Manuscript Tables And Figure Draft

Added and ran `scripts/build_phase11_manuscript_tables.py` through WSL `research-py312`.

Command run:

```powershell
wsl.exe -d Ubuntu -- bash -lc "cd '/mnt/e/Reserch/Older women' && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python -m py_compile scripts/build_phase11_manuscript_tables.py && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python scripts/build_phase11_manuscript_tables.py --output-dir outputs"
```

Generated outputs:

- `outputs/phase11_table1_cohort_readiness.csv`
- `outputs/phase11_table2_class_profiles_labels.csv`
- `outputs/phase11_table3_outcome_validation_summary.csv`
- `outputs/phase11_manuscript_tables_report.md`
- `outputs/figures/phase11_figure1_manuscript_draft.png`
- `outputs/figures/phase11_figure1_manuscript_draft.pdf`

Key manuscript-readiness points:

- Table 1 summarizes selected cohort denominators, complete four-domain samples, selected class-model samples, functional deterioration follow-up, and mortality follow-up.
- Table 2 combines class profiles, candidate English/Chinese labels, outcome signals, and mortality drift flags.
- Table 3 summarizes endpoint-specific validation against severity tertiles and four-domain continuous-score comparators.
- Figure 1 combines the endotype profile plot with AIC delta heatmaps versus severity tertiles and versus four-domain continuous scores.
- SHARE uses a wave-adjusted sensitivity denominator, so its selected endotype N should not be interpreted as the same denominator as Phase 1 earliest baseline.
- LASI remains baseline-profile only for follow-up outcome validation in the current cleaned CSV pass.
- Mortality is retained as secondary validation because PH diagnostics and piecewise sensitivity flagged selected cohort-class terms.

## 2026-06-01 Phase 12 Results Skeleton And Label Dictionary

Added and ran `scripts/build_phase12_results_skeleton.py` through WSL `research-py312`.

Command run:

```powershell
wsl.exe -d Ubuntu -- bash -lc "cd '/mnt/e/Reserch/Older women' && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python -m py_compile scripts/build_phase12_results_skeleton.py && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python scripts/build_phase12_results_skeleton.py --output-dir outputs"
```

Generated outputs:

- `outputs/phase12_label_dictionary_draft.csv`
- `outputs/phase12_results_claims.csv`
- `outputs/phase12_results_skeleton.md`
- `outputs/phase12_internal_zh_summary.md`
- `outputs/phase12_results_skeleton_report.md`
- `manuscript/results_skeleton.md`
- `manuscript/internal_zh_summary.md`

Key manuscript-writing points:

- Results skeleton is organized around sample readiness, cohort-specific endotype structure, functional deterioration, chronic progression, mortality, and the comparator guardrail.
- The label review queue contains 18 labels ready for manual lock, 5 labels requiring manual review because of mortality drift, 3 generic severity-aligned labels requiring review, and 3 LASI baseline-only candidates.
- Functional deterioration validation includes 6 cohorts, 50,084 participants, and 12,336 events.
- Chronic progression validation includes 6 cohorts and 22,423 events.
- Mortality validation includes 6 cohorts and 12,649 deaths, but remains secondary because PH/piecewise sensitivity flagged selected terms.
- The draft text explicitly states that four-domain continuous scores outperform endotype-only classes across tested endpoint-cohort rows; the defensible manuscript framing is interpretable heterogeneity mapping rather than universal prediction superiority.

## 2026-06-01 Phase 13 Covariate Inventory And Display Policy

Added and ran `scripts/build_phase13_covariate_inventory.py` through WSL `research-py312`.

Command run:

```powershell
wsl.exe -d Ubuntu -- bash -lc "cd '/mnt/e/Reserch/Older women' && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python -m py_compile scripts/build_phase13_covariate_inventory.py && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python scripts/build_phase13_covariate_inventory.py --data-root '/mnt/e/Database/七大老年健康数据库数据/csv 版本 清洗后' --output-dir outputs"
```

Generated outputs:

- `outputs/phase13_covariate_candidate_inventory.csv`
- `outputs/phase13_covariate_readiness_summary.csv`
- `outputs/phase13_covariate_participant_screen.csv`
- `outputs/phase13_label_display_policy.csv`
- `outputs/phase13_covariate_inventory_report.md`
- `manuscript/covariate_sensitivity_plan.md`

Key covariate-readiness findings:

- Minimal core covariates are ready in all seven cohorts: education, marital status, smoking, and drinking.
- Expanded core covariates are ready in ELSA, LASI, and SHARE.
- Physical activity is the main limiting field for expanded-core modeling in CHARLS, HRS, MHAS, and KLoSA under the strict candidate rule.
- Optional BMI is ready in CHARLS, HRS, LASI, KLoSA, and SHARE.
- The recommended Phase 14 model is age plus minimal core covariates for functional deterioration and mortality, with expanded-core and BMI sensitivity reported separately.

Label/display policy findings:

- 18 labels are lock candidates.
- 8 labels require manual review before lock.
- 3 LASI labels should remain baseline-profile-only hold candidates until follow-up validation is available.
- KLoSA and SHARE remain sensitivity or supplement display candidates unless the main figure includes explicit bridge-sensitivity footnotes.

## 2026-06-01 Phase 14 Covariate Sensitivity Models

Fixed and reran the Phase 13 participant-level covariate screen after identifying an index-alignment issue that wrote covariate values as missing for several strict-primary cohorts. The rerun confirmed nonmissing minimal-core covariates in CHARLS, ELSA, HRS, KLoSA, LASI, MHAS, and SHARE.

Added and ran `scripts/build_phase14_covariate_sensitivity_models.py` through WSL `research-py312`.

Command run:

```powershell
wsl.exe -d Ubuntu -- bash -lc "cd '/mnt/e/Reserch/Older women' && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python -m py_compile scripts/build_phase13_covariate_inventory.py scripts/build_phase14_covariate_sensitivity_models.py && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python scripts/build_phase13_covariate_inventory.py --data-root '/mnt/e/Database/七大老年健康数据库数据/csv 版本 清洗后' --output-dir outputs && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python scripts/build_phase14_covariate_sensitivity_models.py --output-dir outputs --min-events 20"
```

Generated outputs:

- `outputs/phase14_functional_covariate_model_metrics.csv`
- `outputs/phase14_functional_covariate_model_terms.csv`
- `outputs/phase14_functional_covariate_model_comparison.csv`
- `outputs/phase14_mortality_covariate_model_metrics.csv`
- `outputs/phase14_mortality_covariate_model_terms.csv`
- `outputs/phase14_mortality_covariate_model_comparison.csv`
- `outputs/phase14_covariate_model_skipped.csv`
- `outputs/phase14_endotype_effect_stability.csv`
- `outputs/phase14_covariate_sensitivity_report.md`
- `manuscript/covariate_sensitivity_results.md`

Key covariate-sensitivity findings:

- Functional deterioration minimal-core sensitivity was fit for CHARLS, ELSA, HRS, KLoSA, MHAS, and SHARE.
- Mortality minimal-core sensitivity was fit for CHARLS, ELSA, HRS, KLoSA, MHAS, and SHARE.
- LASI remains unavailable for follow-up functional and mortality validation in the current cleaned CSV pass.
- HRS mortality severity-tertile minimal Cox returned a nonfinite result and is explicitly recorded in skipped fits.
- Covariate sensitivity stability flags mainly involve SHARE functional classes 4-5, HRS functional classes 3-5 in BMI/minimal sensitivity, ELSA functional class 5 in expanded sensitivity, and KLoSA mortality class 2 in BMI sensitivity.
- Phase 14 supports using covariate sensitivity as robustness evidence, not as a replacement for the age-adjusted primary validation screen.

## 2026-06-01 Phase 15 Manuscript Integration And Novelty Refresh

Added and ran `scripts/build_phase15_manuscript_integration.py` through WSL `research-py312`.

Command run:

```powershell
wsl.exe -d Ubuntu -- bash -lc "cd '/mnt/e/Reserch/Older women' && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python -m py_compile scripts/build_phase15_manuscript_integration.py && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python scripts/build_phase15_manuscript_integration.py --output-dir outputs --manuscript-dir manuscript"
```

Generated outputs:

- `outputs/phase15_results_skeleton_integrated.md`
- `manuscript/results_skeleton.md`
- `outputs/phase15_supplement_table_shell.csv`
- `manuscript/supplement_table_shell.md`
- `outputs/phase15_label_lock_queue.csv`
- `outputs/phase15_display_policy_recommendation.csv`
- `outputs/phase15_novelty_refresh_sources.csv`
- `outputs/phase15_novelty_refresh_report.md`
- `outputs/phase15_manuscript_integration_report.md`

Key Phase 15 findings:

- Functional and mortality covariate-sensitivity comparison tables each contain 12 rows.
- Phase 14 stability flags block automatic label locking for 7 class labels: ELSA_C5, HRS_C3, HRS_C4, HRS_C5, KLoSA_C2, SHARE_C4, and SHARE_C5.
- Updated label queue status: 16 labels ready for manual lock, 10 requiring manual review, and 3 LASI baseline-only hold labels.
- Default display policy keeps CHARLS, ELSA, HRS, and MHAS in main validation panels, KLoSA and SHARE in sensitivity/supplement display, and LASI as baseline-profile only.
- Targeted novelty refresh did not identify a direct same-topic collision, but adjacent multidimensional aging, intrinsic-capacity, symptom-cluster, and predeath-trajectory literature requires conservative novelty claims.

## 2026-06-01 Phase 16 Label Lock And Manuscript Draft

Added and ran `scripts/build_phase16_label_lock_and_manuscript_draft.py` through WSL `research-py312`.

Command run:

```powershell
wsl.exe -d Ubuntu -- bash -lc "cd '/mnt/e/Reserch/Older women' && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python -m py_compile scripts/build_phase16_label_lock_and_manuscript_draft.py && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python scripts/build_phase16_label_lock_and_manuscript_draft.py --output-dir outputs --manuscript-dir manuscript"
```

Generated outputs:

- `outputs/phase16_locked_label_dictionary.csv`
- `outputs/phase16_table2_locked_labels.csv`
- `outputs/phase16_figure1_label_map.csv`
- `outputs/phase16_results_draft.md`
- `manuscript/results_draft.md`
- `outputs/phase16_label_lock_and_manuscript_report.md`
- `outputs/figures/phase16_figure1_main_validation.png`
- `outputs/figures/phase16_figure1_main_validation.pdf`
- `outputs/figures/phase16_figure1_seven_cohort_sensitivity.png`
- `outputs/figures/phase16_figure1_seven_cohort_sensitivity.pdf`

Key Phase 16 findings:

- Label status is 16 locked-for-draft, 10 review-required/not locked, and 3 baseline-only holds.
- Review-required labels are visibly marked with `*` in figure labels.
- LASI baseline-only labels are visibly marked with `[hold]` in the seven-cohort sensitivity figure.
- Main validation Figure 1 uses CHARLS, ELSA, HRS, and MHAS.
- Seven-cohort sensitivity Figure 1 includes KLoSA, SHARE, and LASI, with outcome heatmaps showing LASI as unavailable.
- `manuscript/results_draft.md` now gives a tighter Results section with table/figure callouts and comparator guardrails.

## 2026-06-01 Phase 17 Manuscript Assembly Draft

Added and ran `scripts/build_phase17_manuscript_assembly.py` through WSL `research-py312`.

Command run:

```powershell
wsl.exe -d Ubuntu -- bash -lc "cd '/mnt/e/Reserch/Older women' && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python -m py_compile scripts/build_phase17_manuscript_assembly.py && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python scripts/build_phase17_manuscript_assembly.py --output-dir outputs --manuscript-dir manuscript"
```

Generated outputs:

- `outputs/phase17_label_review_packet.csv`
- `outputs/phase17_tables_1_3_manuscript.md`
- `outputs/phase17_supplement_s1_s3.md`
- `outputs/phase17_intro_discussion_draft.md`
- `outputs/phase17_claim_to_evidence_map.csv`
- `outputs/phase17_manuscript_assembly_draft.md`
- `outputs/phase17_manuscript_assembly_report.md`
- `manuscript/introduction_draft.md`
- `manuscript/discussion_draft.md`
- `manuscript/tables_1_3_draft.md`
- `manuscript/supplement_s1_s3_draft.md`
- `manuscript/manuscript_assembly_draft.md`

Key Phase 17 findings:

- The label-review packet contains 13 rows: 10 review-required/not locked labels and 3 LASI baseline-only hold labels.
- Generic severity-aligned review labels are given conservative domain-neutral alternatives such as broad intermediate- or elevated-burden profiles.
- Mortality-drift and Phase 14 stability-flagged labels are kept as domain-profile labels with explicit sensitivity caveats.
- Introduction and Discussion drafts use the Phase 15 novelty refresh and avoid first/novelty overclaims.
- The claim-to-evidence map keeps mortality as secondary validation and keeps endotype classes framed as interpretable heterogeneity summaries, not universally superior prediction models.

## 2026-06-01 Phase 18 Submission Draft v0

Added and ran `scripts/build_phase18_submission_draft_v0.py` through WSL `research-py312`.

Command run:

```powershell
wsl.exe -d Ubuntu -- bash -lc "cd '/mnt/e/Reserch/Older women' && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python -m py_compile scripts/build_phase18_submission_draft_v0.py && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python scripts/build_phase18_submission_draft_v0.py --output-dir outputs --manuscript-dir manuscript"
```

Generated outputs:

- `outputs/phase18_label_decisions_auto_v0.csv`
- `outputs/phase18_final_label_dictionary_v0.csv`
- `outputs/phase18_table2_final_labels_v0.csv`
- `outputs/phase18_figure1_label_map_v0.csv`
- `outputs/phase18_tables_1_3_v0.md`
- `outputs/phase18_journal_style_manuscript_v0.md`
- `outputs/phase18_submission_readiness_checklist.md`
- `outputs/phase18_submission_draft_v0_report.md`
- `manuscript/journal_style_manuscript_v0.md`
- `manuscript/submission_readiness_checklist.md`
- `manuscript/tables_1_3_phase18_v0.md`
- `outputs/figures/phase18_figure1_main_validation_v0.png`
- `outputs/figures/phase18_figure1_main_validation_v0.pdf`
- `outputs/figures/phase18_figure1_seven_cohort_sensitivity_v0.png`
- `outputs/figures/phase18_figure1_seven_cohort_sensitivity_v0.pdf`

Key Phase 18 findings:

- Phase 18 accepted 16 labels from Phase 16, retained 7 labels with explicit sensitivity caveats, conservatively renamed 3 generic severity-aligned labels, and kept 3 LASI labels as baseline-only.
- Human signoff remains required for 13 labels before submission.
- The main validation Figure 1 v0 renders CHARLS, ELSA, HRS, and MHAS with `[signoff]` and `[cav]` markers.
- The journal-style manuscript v0 includes Abstract, Introduction, Methods, Results, Discussion, and a references-to-format queue.
- The submission-readiness checklist lists the remaining blocking tasks: label signoff, target-journal formatting, formal citations, Figure 1 display decision, and LASI display decision.

## 2026-06-01 Phase 19 Clean Submission Package

Added and ran `scripts/build_phase19_clean_submission_package.py` through WSL `research-py312`.

Command run:

```powershell
wsl.exe -d Ubuntu -- bash -lc "cd '/mnt/e/Reserch/Older women' && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python -m py_compile scripts/build_phase19_clean_submission_package.py && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python scripts/build_phase19_clean_submission_package.py --output-dir outputs --manuscript-dir manuscript"
```

Generated outputs:

- `outputs/phase19_verified_reference_queue.csv`
- `outputs/phase19_reference_corrections.md`
- `outputs/phase19_label_signoff_sheet.csv`
- `outputs/phase19_clean_manuscript_target_neutral.md`
- `outputs/phase19_target_journal_decision_matrix.csv`
- `outputs/phase19_submission_package_index.md`
- `outputs/phase19_clean_submission_package_report.md`
- `manuscript/clean_manuscript_target_neutral.md`
- `manuscript/references_verified_v0.md`
- `manuscript/title_page_draft.md`
- `manuscript/cover_letter_skeleton.md`

Key Phase 19 findings:

- The clean manuscript cites only verified references and removes the old Phase 18 `References To Format` queue from the manuscript body.
- Phase 15 N1 was verified as PMID 36479143; corrected/replacement references were added for N4 and N5 as PMID 41258422 and PMID 41916958.
- Old Phase 15 N2, N3, N4, N5, and N6 PMCID rows are held out of the clean draft because they were unrelated or replaced during Phase 19 checking.
- The reference queue contains 9 rows: 3 verified references, 5 held PMCID rows, and 1 optional preprint row.
- The label signoff sheet contains 29 class rows, with 13 rows still requiring signoff, caveat approval, or baseline-only hold approval.
- The target-journal matrix is target-neutral and explicitly requires a live author-guideline check after the journal is chosen.

## 2026-06-01 Phase 20 Target-Journal And Signoff Assets

Added and ran `scripts/build_phase20_target_and_signoff_assets.py` through WSL `research-py312`.

Command run:

```powershell
wsl.exe -d Ubuntu -- bash -lc "cd '/mnt/e/Reserch/Older women' && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python -m py_compile scripts/build_phase20_target_and_signoff_assets.py && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python scripts/build_phase20_target_and_signoff_assets.py --output-dir outputs --manuscript-dir manuscript"
```

Generated outputs:

- `outputs/phase20_label_signoff_decision_template.csv`
- `outputs/phase20_label_signoff_review_packet.md`
- `outputs/phase20_target_guideline_snapshot.csv`
- `outputs/phase20_manuscript_format_gap_check.csv`
- `outputs/phase20_target_selection_memo.md`
- `outputs/phase20_guideline_sources.md`
- `outputs/phase20_target_and_signoff_report.md`
- `manuscript/phase20_working_target_plan.md`

Key Phase 20 findings:

- The 13 remaining label decisions are split into 7 caveat approvals, 3 conservative rename signoffs, and 3 LASI baseline-only hold approvals.
- Official guideline pages were checked for Age and Ageing, The Journals of Gerontology: Series A Medical Sciences, and BMC Geriatrics.
- Age and Ageing is the working first target if the story is tightened around clinical geriatric implications and stays within the 3000-word, 5-data-element research-paper format.
- The Journals of Gerontology: Series A Medical Sciences is the strongest scientific-fit alternative, with a 5200-word research-article limit, 250-word abstract limit, 50-reference limit, and 5-data-element limit.
- BMC Geriatrics remains the pragmatic fallback when extensive methods and supplements are prioritized.
- Journal of the American Geriatrics Society remains on hold because the Wiley author-guideline page was not accessible through the current tool session.
- The current clean draft has 1,228 counted words, a 245-word abstract, and 3 references before adding final target-specific declarations and table/figure packages.

## 2026-06-01 Phase 21 BMC Geriatrics Springer Nature Template Package

Per user instruction, changed the active target to BMC Geriatrics and used the local Springer Nature template at `E:\Reserch\Temp\_tmp_springer_nature_template_inspect_20260524`.

Added and ran `scripts/build_phase21_bmc_geriatrics_template_package.py` through WSL `research-py312`.

Command run:

```powershell
wsl.exe -d Ubuntu -- bash -lc "cd '/mnt/e/Reserch/Older women' && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python -m py_compile scripts/build_phase21_bmc_geriatrics_template_package.py && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python scripts/build_phase21_bmc_geriatrics_template_package.py --template-dir '/mnt/e/Reserch/Temp/_tmp_springer_nature_template_inspect_20260524' --output-dir outputs --manuscript-dir manuscript"
```

Generated package:

- `manuscript/bmc_geriatrics_submission/`
- `manuscript/bmc_geriatrics_submission_package.zip`

Generated package files:

- `manuscript/bmc_geriatrics_submission/bmc_geriatrics_main.tex`
- `manuscript/bmc_geriatrics_submission/bmc_geriatrics_refs.bib`
- `manuscript/bmc_geriatrics_submission/sn-jnl.cls`
- `manuscript/bmc_geriatrics_submission/sn-vancouver-num.bst`
- `manuscript/bmc_geriatrics_submission/figure1_main_validation.png`
- `manuscript/bmc_geriatrics_submission/figure1_seven_cohort_sensitivity.png`
- `manuscript/bmc_geriatrics_submission/additional_file_1_class_profiles.csv`
- `manuscript/bmc_geriatrics_submission/additional_file_2_outcome_validation.csv`
- `manuscript/bmc_geriatrics_submission/additional_file_3_label_signoff_decision_template.csv`
- `manuscript/bmc_geriatrics_submission/bmc_geriatrics_cover_letter.md`
- `manuscript/bmc_geriatrics_submission/README_BMC_Geriatrics_package.md`

Generated logs and metadata:

- `outputs/phase21_bmc_geriatrics_template_package_report.md`
- `outputs/phase21_bmc_geriatrics_package_manifest.csv`
- `outputs/phase21_bmc_geriatrics_package_summary.csv`
- `outputs/phase21_bmc_geriatrics_package_zip.csv`
- `outputs/phase21_latex_compile_check.md`

Key Phase 21 findings:

- The BMC package uses `\documentclass[referee,lineno,pdflatex,sn-vancouver-num]{sn-jnl}`.
- Main TeX source uses the Springer Nature class and Vancouver numbered bibliography style from the local template.
- The package contains a structured abstract, Background, Methods, Results, Discussion, Conclusions, Abbreviations, Declarations, Additional files, and BibTeX references.
- Main table values avoid comma thousands separators.
- Approximate TeX word count is 1,387.
- Source sanity checks passed: documentclass, begin/end document, bibliography, figure reference, declarations section, and brace balance.
- PDF compilation was attempted with the LaTeX compile skill but was not completed because no bundled/PATH Tectonic or TeX Live installation was detected. No TeX runtime was installed.
- The package is source-ready but not submission-final because 13 label decisions, BMC declarations, data availability wording, and final author metadata remain incomplete.

## 2026-06-01 Phase 22 BMC Review-Ready Package

Added and ran `scripts/build_phase22_bmc_review_ready_package.py` through WSL `research-py312`.

Command run:

```powershell
wsl.exe -d Ubuntu -- bash -lc "cd '/mnt/e/Reserch/Older women' && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python -m py_compile scripts/build_phase22_bmc_review_ready_package.py && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python scripts/build_phase22_bmc_review_ready_package.py --output-dir outputs --manuscript-dir manuscript"
```

Generated package:

- `manuscript/bmc_geriatrics_submission_review_ready/`
- `manuscript/bmc_geriatrics_review_ready_package.zip`

Generated outputs:

- `outputs/phase22_conservative_label_signoff_proposal.csv`
- `outputs/phase22_bmc_class_profiles_review_ready.csv`
- `outputs/phase22_bmc_review_ready_manifest.csv`
- `outputs/phase22_bmc_review_ready_summary.csv`
- `outputs/phase22_bmc_review_ready_zip.csv`
- `outputs/phase22_bmc_review_ready_report.md`
- `outputs/phase22_bmc_remaining_author_items.md`
- `outputs/phase22_latex_source_sanity_check.md`

Key Phase 22 findings:

- A conservative approval proposal was generated for all 13 remaining label decisions: 7 caveat labels, 3 LASI baseline-only holds, and 3 conservative burden-profile renames.
- The proposal is explicitly marked `proposal_only_not_human_signoff`; author confirmation is still required.
- The review-ready package removes the internal label-signoff worksheet from the zip.
- Additional file 1 now uses cleaned BMC-facing columns: `bmc_label`, `bmc_label_status`, and `bmc_label_note`.
- No `bmc_label` contains `[signoff]`, `[caveat]`, or `[baseline-only]` bracket markers.
- The review-ready zip contains 10 files: main TeX, BibTeX, two additional files, cover letter, two figures, two Springer Nature template files, and package notes.
- TeX sanity checks passed: documentclass, begin/end document, bibliography, figure reference, declarations section, Additional file 3 absence, no duplicate label sentence, and brace balance.
- Approximate TeX word count is 1,359.
- Remaining blockers are now narrowed to author confirmation, BMC declarations, cohort data-use/ethics wording, author metadata, and PDF compilation.

## 2026-06-01 Phase 23 BMC Declarations Completion Pack

Added and ran `scripts/build_phase23_bmc_declarations_completion_pack.py` through WSL `research-py312`.

Command run:

```powershell
wsl.exe -d Ubuntu -- bash -lc "cd '/mnt/e/Reserch/Older women' && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python -m py_compile scripts/build_phase23_bmc_declarations_completion_pack.py && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python scripts/build_phase23_bmc_declarations_completion_pack.py --output-dir outputs --manuscript-dir manuscript"
```

Generated package:

- `manuscript/bmc_geriatrics_submission_declarations_ready/`
- `manuscript/bmc_geriatrics_declarations_ready_package.zip`

Generated outputs:

- `outputs/phase23_bmc_declarations_completion_template.csv`
- `outputs/phase23_cohort_data_availability_template.csv`
- `outputs/phase23_author_metadata_template.csv`
- `outputs/phase23_ai_disclosure_decision_note.md`
- `outputs/phase23_bmc_completion_precheck.csv`
- `outputs/phase23_bmc_declarations_ready_manifest.csv`
- `outputs/phase23_bmc_declarations_ready_zip.csv`
- `outputs/phase23_bmc_declarations_ready_report.md`

Key Phase 23 findings:

- The declaration-ready TeX now contains structured BMC declaration placeholders for ethics/consent, consent for publication, data availability, competing interests, funding, author contributions, acknowledgements, and generative-AI policy decision.
- The data availability section now includes data portal URLs for CHARLS, ELSA, HRS, KLoSA, LASI, MHAS, and SHARE.
- `phase23_cohort_data_availability_template.csv` records one row per cohort with suggested data availability wording and required citation/acknowledgement checks.
- `phase23_author_metadata_template.csv` records author, affiliation, funding, contribution, and repository placeholders.
- Precheck contains 15 rows: 10 pass rows, 4 author-input rows, and 1 policy-decision row.
- Remaining editorial placeholders are `[AUTHOR INPUT REQUIRED]`, `[Confirm that no identifiable participant information is included.]`, `[Initials]`, `[POLICY DECISION REQUIRED]`, and `[repository URL]`.
- This phase does not finalize ethics, funding, author contributions, competing interests, repository URL, or AI disclosure; those require author input.

## 2026-06-01 Phase 27-29 Reviewer-Ready BMC整改包

Added and ran the reviewer-ready整改 layer through WSL `research-py312`.

Commands run:

```powershell
wsl.exe -d Ubuntu -- bash -lc "cd '/mnt/e/Reserch/Older women' && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python -m py_compile scripts/build_phase3_domain_scores.py scripts/build_phase27_share_strict_functional_audit.py scripts/build_phase28_reviewer_ready_assets.py scripts/build_phase29_bmc_reviewer_ready_package.py"
wsl.exe -d Ubuntu -- bash -lc "cd '/mnt/e/Reserch/Older women' && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python scripts/build_phase27_share_strict_functional_audit.py --database-root '/mnt/e/Database/七大老年健康数据库数据' --data-root '/mnt/e/Database/七大老年健康数据库数据/csv 版本 清洗后' --output-dir outputs"
wsl.exe -d Ubuntu -- bash -lc "cd '/mnt/e/Reserch/Older women' && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python scripts/build_phase29_bmc_reviewer_ready_package.py"
```

PDF compile command:

```powershell
wsl.exe -d Ubuntu -- bash -lc "cd '/mnt/e/Reserch/Older women' && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python '/mnt/c/Users/luff9/.codex/plugins/cache/openai-bundled/latex/0.2.2/scripts/compile_latex.py' '/mnt/e/Reserch/Older women/manuscript/bmc_geriatrics_submission_reviewer_ready/bmc_geriatrics_main.tex' --json"
```

Generated scripts:

- `scripts/build_phase27_share_strict_functional_audit.py`
- `scripts/build_phase28_reviewer_ready_assets.py`
- `scripts/build_phase29_bmc_reviewer_ready_package.py`

Updated script:

- `scripts/build_phase3_domain_scores.py`

Generated outputs:

- `outputs/phase27_share_strict_functional_audit.csv`
- `outputs/phase27_share_strict_functional_decision.csv`
- `outputs/phase27_share_strict_functional_audit.md`
- `outputs/phase28_domain_harmonization_dictionary.csv`
- `outputs/phase28_gmm_selection_table.csv`
- `outputs/phase28_validation_metrics_main.csv`
- `outputs/phase28_outcome_model_specification.csv`
- `outputs/phase28_mortality_sensitivity_guardrails.csv`
- `outputs/phase28_reviewer_ready_assets_report.md`
- `outputs/phase29_reviewer_ready_checklist.csv`
- `outputs/phase29_reviewer_ready_checklist.md`
- `outputs/phase29_bmc_reviewer_ready_manifest.csv`
- `outputs/phase29_bmc_reviewer_ready_zip_summary.csv`
- `outputs/phase29_bmc_reviewer_ready_package_report.md`

Generated package:

- `manuscript/bmc_geriatrics_submission_reviewer_ready/`
- `manuscript/bmc_geriatrics_submission_reviewer_ready/bmc_geriatrics_main.pdf`
- `manuscript/bmc_geriatrics_reviewer_ready_source_package.zip`
- `manuscript/bmc_geriatrics_reviewer_ready_pdf_ready_package.zip`

Key Phase 27-29 findings:

- Phase 27 passed: SHARE wave 1 has mergeable strict baseline functional evidence from `/mnt/e/Database/七大老年健康数据库数据/7.SHARE 欧洲/SHARE_欧洲/Temp_data/share_wave1.dta`, using `adl` and `iadl`.
- SHARE was promoted from bridge/wave-adjusted to strict wave-1 primary in `build_phase3_domain_scores.py` and Phase 3-14 outputs were regenerated before the reviewer-ready package was built.
- Updated Phase 3 SHARE readiness: wave 1 baseline women 50+ `15814`, complete four-domain `15721`, functional source `primary`, functional variables `adl+iadl`.
- Table 1 now separates source-screen, complete-domain and endotype-assignment denominators. LASI remains baseline-profile only for follow-up validation and is not represented as a zero-event follow-up cohort.
- The manuscript wording is now `seven-cohort endotype construction; six-cohort validation`.
- The BMC PDF compiles under the Codex-managed TeX Live runtime. The final TeX source contains no `lineno` option and no `resizebox`; the PDF has 10 pages. A minor table overfull warning remained at 13.8 pt but compilation completed successfully.
- The PDF-ready zip includes the compiled PDF; the source-only zip excludes it.
- Remaining submission blockers are author metadata, ethics/funding/contribution/competing-interest completion, repository URL, cohort acknowledgement wording, and the final generative-AI disclosure policy decision.

## 2026-06-02 Phase 30 Clinical Upgrade Package

Added and ran `scripts/build_phase30_clinical_upgrade_package.py` through WSL `research-py312`.

Skill routing used:

- Life Science Research `research-router-skill` for clinical/translational framing.
- Local `biomed-figure-redraw` and PERSIST panel rules for figure-content discipline. This pass generated data-driven clinical figures but did not claim high-fidelity PERSIST capsule matching because no separate capsule-selection confirmation was requested.
- LaTeX `latex-compile` for BMC/Springer Nature PDF compilation.

Commands run:

```powershell
wsl.exe -d Ubuntu -- bash -lc "cd '/mnt/e/Reserch/Older women' && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python -m py_compile scripts/build_phase30_clinical_upgrade_package.py && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python scripts/build_phase30_clinical_upgrade_package.py"
wsl.exe -d Ubuntu -- bash -lc "cd '/mnt/e/Reserch/Older women' && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python '/mnt/c/Users/luff9/.codex/plugins/cache/openai-bundled/latex/0.2.2/scripts/compile_latex.py' '/mnt/e/Reserch/Older women/manuscript/bmc_geriatrics_submission_clinical_upgrade/bmc_geriatrics_main.tex' --json"
wsl.exe -d Ubuntu -- bash -lc "cd '/mnt/e/Reserch/Older women' && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python scripts/build_phase30_clinical_upgrade_package.py"
```

Generated package:

- `manuscript/bmc_geriatrics_submission_clinical_upgrade/`
- `manuscript/bmc_geriatrics_submission_clinical_upgrade/bmc_geriatrics_main.pdf`
- `manuscript/bmc_geriatrics_clinical_upgrade_source_package.zip`
- `manuscript/bmc_geriatrics_clinical_upgrade_pdf_ready_package.zip`

Generated outputs:

- `outputs/phase30_skill_candidate_decision.csv`
- `outputs/phase30_clinical_reference_frame.md`
- `outputs/phase30_table_figure_blueprint.csv`
- `outputs/phase30_clinical_endotype_dictionary.csv`
- `outputs/phase30_clinical_profile_family_summary.csv`
- `outputs/phase30_functional_endotype_or_minimal_core.csv`
- `outputs/phase30_clinical_upgrade_checklist.csv`
- `outputs/phase30_clinical_upgrade_checklist.md`
- `outputs/phase30_clinical_upgrade_manifest.csv`
- `outputs/phase30_clinical_upgrade_zip_summary.csv`
- `outputs/phase30_clinical_upgrade_report.md`

Main clinical table/figure decisions:

- Table 1: cohort denominators and validation availability.
- Table 2: clinical endotype families and interpretation.
- Table 3: functional validation and mortality guardrail metrics.
- Figure 1: clinical study flow and cohort-tier structure.
- Figure 2: four-domain clinical profile heatmap for selected endotypes.
- Figure 3: functional deterioration validation forest and four-domain comparator deltas.
- Additional file 7: full clinical endotype dictionary.
- Additional file 8: table and figure blueprint.

Key Phase 30 results:

- Manuscript now anchors clinical interpretation in functional ability, intrinsic capacity, frailty phenotype and deficit-accumulation framing.
- Endotypes are explicitly described as clinical phenotype families, not diagnoses or treatment assignments.
- Functional deterioration remains the primary clinical validation endpoint.
- Mortality remains secondary with PH/piecewise guardrails.
- The clinical-upgrade PDF compiles to 13 pages with no side line numbers and no float-too-large errors. Final checklist rows pass except author-input and AI-disclosure policy placeholders.

## 2026-06-02 Phase 31-32 Severe External Review Triage

Received Claude severe review from:

- `C:\Users\luff9\Downloads\endotype_manuscript_severe_review.md`

Archived copies:

- `outputs/phase31_claude_severe_review_received.md`
- `manuscript/claude_severe_review_received.md`

Generated triage outputs:

- `outputs/phase32_severe_review_response_plan.md`
- `outputs/phase32_severe_review_action_matrix.csv`

Key decision:

- Freeze the Phase 30 clinical-upgrade manuscript as a reviewed draft, not a submission-ready draft.
- Do not keep polishing the current clinical-upgrade manuscript until Phase 32A-C are addressed.
- The realistic rescue route is BMC Geriatrics as a descriptive/cautionary multidomain burden-profile paper.
- A Nature Communications-level route would require a different study centered on cross-cohort profile replicability, held-out/transport validation, non-circular endpoints, calibration/DCA, and stronger sex-specific justification.

Main severe-review blockers:

- Primary functional validation may be partly coupled to the functional domain used for profile construction.
- Continuous four-domain score models often outperform or match profile-only models.
- Current validation is within-cohort association, not true external validation.
- GMM solutions require degeneracy and stability diagnostics.
- Cross-cohort harmonization and clinical family labels require item-level audit and stricter labeling rules.

Immediate next implementation should start with:

1. `Phase 32A`: functional-endpoint leakage audit.
2. `Phase 32C`: lowest-burden reference reanalysis.
3. `Phase 32D`: GMM covariance/stability diagnostics.
4. `Phase 32E`: item-level harmonization crosswalk.

## 2026-06-02 Phase 32A/C Execution

Added and executed:

- `scripts/build_phase32_functional_endpoint_audit.py`
- `scripts/build_phase32_uniform_reference_models.py`

Generated outputs:

- `outputs/phase32_functional_endpoint_leakage_audit.csv`
- `outputs/phase32_functional_endpoint_leakage_audit.md`
- `outputs/phase32_lowest_burden_reference_map.csv`
- `outputs/phase32_uniform_reference_functional_metrics.csv`
- `outputs/phase32_uniform_reference_functional_terms.csv`
- `outputs/phase32_uniform_reference_skipped.csv`
- `outputs/phase32_uniform_reference_vs_original.csv`
- `outputs/phase32_uniform_reference_report.md`
- `outputs/phase32_execution_status.md`
- `outputs/phase32_next_step_decision.md`

Checks:

- `python -m py_compile scripts/build_phase32_functional_endpoint_audit.py scripts/build_phase32_uniform_reference_models.py` passed under WSL Ubuntu and `research-py312`.

Key Phase 32A decision:

- The current functional endpoint is a same-domain score-change endpoint: follow-up functional score minus baseline functional score >= 0.5 SD.
- Because baseline functional score is also one of the profile-construction domains, current functional outcome models cannot be used as independent clinical prediction evidence.
- CHARLS, ELSA, HRS and MHAS can currently support only coupled within-cohort association.
- KLoSA remains bridge-sensitivity only.
- LASI has no usable follow-up functional validation outcome in the current screen.
- SHARE must be excluded or rebuilt for functional validation because the current model shows implausible/separation-like behavior, including max OR greater than 100.

Key Phase 32C decision:

- The modeled C1 classes are already the cohort-specific lowest available burden references.
- CHARLS and LASI C1 are lowest available but not strict low-burden by the severity threshold, so this caution must remain visible.
- LASI is skipped from functional validation regardless of reference handling because follow-up outcome data are unavailable in the current validation screen.

Immediate next implementation:

1. `Phase 32B`: rebuild validation with a non-circular endpoint or leave-functional-domain-out profile design.
2. `Phase 32D`: run GMM covariance and bootstrap/split-half stability diagnostics.
3. `Phase 32E`: item-level harmonization crosswalk and cohort-tier locking.

## 2026-06-02 Phase 32B Decoupled Validation

Added and executed:

- `scripts/build_phase32_decoupled_lfo_validation.py`

Generated outputs:

- `outputs/phase32_decoupled_lfo_gmm_metrics.csv`
- `outputs/phase32_decoupled_lfo_best_model_summary.csv`
- `outputs/phase32_decoupled_lfo_class_profiles.csv`
- `outputs/phase32_decoupled_lfo_assignments.csv`
- `outputs/phase32_decoupled_lfo_participant_screen.csv`
- `outputs/phase32_decoupled_validation_metrics.csv`
- `outputs/phase32_decoupled_validation_terms.csv`
- `outputs/phase32_decoupled_validation_comparison.csv`
- `outputs/phase32_decoupled_validation_skipped.csv`
- `outputs/phase32_decoupled_validation_report.md`

Checks:

- `python -m py_compile scripts/build_phase32_decoupled_lfo_validation.py` passed under WSL Ubuntu and `research-py312`.

Design:

- Rebuilt Gaussian mixture profiles using cognitive, affective and cardiometabolic/chronic disease domains only.
- Merged leave-functional-domain-out class assignments into the existing Phase 5 participant outcome screen.
- Functional deterioration remained the stored Phase 5 follow-up endpoint, but baseline functional score was not used in profile construction.

Key results:

- KLoSA: bridge-sensitivity only.
- LASI: no follow-up validation rows.
- CHARLS, ELSA, HRS, MHAS and SHARE: `three_domain_scores_fit_better_than_profiles`.
- No strict validation cohort was marked `candidate_decoupled_profile_signal`.

Manuscript consequence:

- Profile prediction superiority is not defensible.
- The rescue manuscript should be rewritten as descriptive/cautionary multidomain burden-profile mapping.
- The main validation table should report profile metrics beside continuous three-domain score comparators and explicitly show that continuous scores fit better.

Immediate next implementation:

1. `Phase 32D`: GMM covariance and bootstrap/split-half stability diagnostics.
2. `Phase 32E`: item-level harmonization crosswalk and cohort-tier locking.

## 2026-06-02 Phase 32D GMM Stability Diagnostics

Added and executed:

- `scripts/build_phase32_gmm_stability_diagnostics.py`

Generated outputs:

- `outputs/phase32_gmm_covariance_diagnostics.csv`
- `outputs/phase32_gmm_bootstrap_stability.csv`
- `outputs/phase32_gmm_stability_summary.csv`
- `outputs/phase32_gmm_stability_report.md`

Checks:

- `python -m py_compile scripts/build_phase32_gmm_stability_diagnostics.py` passed under WSL Ubuntu and `research-py312`.

Design:

- Refit the selected four-domain GMM model for each cohort.
- Computed selected-component covariance eigenvalues, condition numbers and determinants.
- Ran 20 nonparametric bootstrap refits per cohort and compared each solution with the reference using adjusted Rand index and centroid drift.

Key results:

- Every selected four-domain GMM model triggered at least one near-singular covariance flag.
- SHARE showed poor bootstrap stability, with median ARI approximately 0.37.
- KLoSA and HRS had high median ARI but low 10th percentile ARI, supporting sensitivity/downgrade language.
- LASI had strong bootstrap ARI but still triggered near-singular covariance and has no follow-up validation.

Manuscript consequence:

- Do not write "stable latent endotypes" or mechanistic subtype claims.
- Use "descriptive multidomain burden-profile strata" and explicitly report covariance/stability caveats.
- The rescue manuscript should treat the GMM as a data-reduction/profile mapping device, not a discovery model with independent predictive superiority.

Immediate next implementation:

1. `Phase 32E`: item-level harmonization crosswalk and cohort-tier locking.

## 2026-06-02 Phase 32E Item-Level Harmonization And Tier Lock

Added and executed:

- `scripts/build_phase32_item_harmonization_crosswalk.py`

Generated outputs:

- `outputs/phase32_item_level_harmonization_crosswalk.csv`
- `outputs/phase32_cohort_tier_lock.csv`
- `outputs/phase32_item_level_harmonization_report.md`

Checks:

- `python -m py_compile scripts/build_phase32_item_harmonization_crosswalk.py` passed under WSL Ubuntu and `research-py312`.

Design:

- Expanded `COHORT_CONFIG` into item-level rows with variable, domain, source tier, raw direction, selected-score use flag, nonmissing counts and comparability flags.
- Merged Phase 32A, 32B and 32D decisions into a cohort-level tier lock.

Key tier locks:

- KLoSA: `bridge_sensitivity_descriptive_only`.
- LASI: `baseline_profile_construction_only_no_followup_validation`.
- SHARE: `strict_construction_but_validation_downgraded`.
- CHARLS, ELSA, HRS and MHAS: `strict_construction_within_cohort_gradient_only`.

Manuscript consequence:

- Table 1 and figure legends should be driven by `outputs/phase32_cohort_tier_lock.csv`.
- The additional-file variable dictionary should use `outputs/phase32_item_level_harmonization_crosswalk.csv`.
- The manuscript must not describe all seven cohorts as equivalent strict validation cohorts.

Immediate next implementation:

1. `Phase 32F`: rewrite the BMC manuscript as descriptive/cautionary burden-profile mapping.
2. `Phase 32G`: rebuild PDF/package without side line numbers.

## 2026-06-02 Phase 32F/G BMC Burden-Profile Rescue Package

Added and executed:

- `scripts/build_phase32_bmc_rescue_package.py`

Generated package:

- `manuscript/bmc_geriatrics_submission_burden_profiles_rescue/`
- `manuscript/bmc_geriatrics_submission_burden_profiles_rescue/bmc_geriatrics_main.tex`
- `manuscript/bmc_geriatrics_submission_burden_profiles_rescue/bmc_geriatrics_main.pdf`
- `manuscript/bmc_geriatrics_burden_profiles_rescue_source_package.zip`
- `manuscript/bmc_geriatrics_burden_profiles_rescue_pdf_ready_package.zip`

Generated package outputs:

- `outputs/phase32_bmc_rescue_package_manifest.csv`
- `outputs/phase32_bmc_rescue_zip_summary.csv`
- `outputs/phase32_bmc_rescue_package_report.md`

Additional files included in the package:

- `additional_file_1_item_level_harmonization_crosswalk.csv`
- `additional_file_2_cohort_tier_lock.csv`
- `additional_file_3_decoupled_validation_comparison.csv`
- `additional_file_4_gmm_stability_summary.csv`
- `additional_file_5_gmm_covariance_diagnostics.csv`
- `additional_file_6_functional_endpoint_leakage_audit.csv`

Figures included in the package:

- `figure1_cohort_tier_lock.png/.pdf`
- `figure2_descriptive_profile_heatmap.png/.pdf`
- `figure3_validation_and_stability_guardrails.png/.pdf`

Checks:

- `python -m py_compile scripts/build_phase32_bmc_rescue_package.py` passed under WSL Ubuntu and `research-py312`.
- PDF compiled with bundled Tectonic through the LaTeX compile skill.
- PDF text extraction found 8 pages and no unresolved citation placeholders.
- The source uses `\documentclass[pdflatex,sn-vancouver-num]{sn-jnl}` without `referee` or `lineno`, so side line numbers are not enabled.
- PDF-ready zip was rebuilt after compilation and confirmed to include `bmc_geriatrics_main.pdf`.

Manuscript stance:

- Title and abstract now use descriptive multidomain burden profiles rather than mechanistic endotypes.
- The main claim is cross-cohort descriptive mapping.
- The manuscript explicitly reports that continuous three-domain scores fit functional deterioration better than leave-functional-domain-out profile classes in all strict cohorts with follow-up.
- The manuscript explicitly reports near-singular covariance diagnostics for selected GMM models.
- Author, ethics, funding, contribution and AI disclosure placeholders remain intentionally unfilled.
