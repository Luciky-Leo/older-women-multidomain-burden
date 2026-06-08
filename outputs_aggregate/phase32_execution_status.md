# Phase 32 Execution Status

Date: 2026-06-02

## Completed

### Phase 32A Functional Endpoint Leakage Audit

Artifacts:

- `outputs/phase32_functional_endpoint_leakage_audit.csv`
- `outputs/phase32_functional_endpoint_leakage_audit.md`

Decision:

- The current functional validation endpoint is a same-domain score-change endpoint: follow-up functional score minus baseline functional score >= 0.5 SD.
- Baseline functional score is also one of the four profile-construction domains.
- Therefore, these models cannot be described as independent clinical prediction.

Status by cohort:

- CHARLS, ELSA, HRS, MHAS: usable only as coupled within-cohort association evidence.
- KLoSA: bridge-sensitivity only.
- LASI: excluded from follow-up validation because follow-up outcome is unavailable in the current validation screen.
- SHARE: exclude or redefine until the endpoint is decoupled; current model shows implausible/separation-like OR behavior.

### Phase 32C Uniform Reference-Class Reanalysis

Artifacts:

- `outputs/phase32_lowest_burden_reference_map.csv`
- `outputs/phase32_uniform_reference_functional_metrics.csv`
- `outputs/phase32_uniform_reference_functional_terms.csv`
- `outputs/phase32_uniform_reference_skipped.csv`
- `outputs/phase32_uniform_reference_vs_original.csv`
- `outputs/phase32_uniform_reference_report.md`

Decision:

- Current C1 references are already the cohort-specific lowest available burden class in all modeled cohorts.
- CHARLS and LASI C1 are lowest available references but not strict low-burden profiles by the severity threshold.
- LASI remains skipped for functional validation because it lacks available follow-up outcome data.

### Phase 32B Decoupled Leave-Functional-Domain-Out Validation

Artifacts:

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

Decision:

- Leave-functional-domain-out profiles were rebuilt from cognitive, affective and cardiometabolic/chronic disease domains.
- The decoupled profile model did not outperform continuous three-domain scores in any strict validation cohort.
- CHARLS, ELSA, HRS, MHAS and SHARE are all marked `three_domain_scores_fit_better_than_profiles`.
- KLoSA remains `bridge_sensitivity_only`.
- LASI remains `exclude_no_followup_validation`.

Manuscript consequence:

- Do not claim profile prediction superiority.
- Reframe the manuscript as descriptive burden-profile mapping with transparent comparator inferiority.
- Use the current validation only to show outcome gradients and comparator diagnostics, not independent clinical utility.

### Phase 32D GMM Stability And Covariance Diagnostics

Artifacts:

- `outputs/phase32_gmm_covariance_diagnostics.csv`
- `outputs/phase32_gmm_bootstrap_stability.csv`
- `outputs/phase32_gmm_stability_summary.csv`
- `outputs/phase32_gmm_stability_report.md`

Decision:

- All selected four-domain GMM models triggered near-singular covariance diagnostics.
- SHARE also showed poor bootstrap stability: median ARI approximately 0.37 against the reference solution.
- KLoSA and HRS had low 10th percentile bootstrap ARI despite high median ARI, reinforcing sensitivity-only handling.
- No cohort should be described as having a robustly discovered latent GMM structure without this caveat.

Manuscript consequence:

- Profiles can remain as descriptive burden-profile strata only.
- Main claims must avoid "latent endotype discovery", "stable subtypes", or mechanistic subtype language.
- SHARE should not be used as strong validation evidence; it can remain in construction/descriptive sensitivity only if the caveat is explicit.

### Phase 32E Item-Level Harmonization Crosswalk And Tier Lock

Artifacts:

- `outputs/phase32_item_level_harmonization_crosswalk.csv`
- `outputs/phase32_cohort_tier_lock.csv`
- `outputs/phase32_item_level_harmonization_report.md`

Decision:

- The item-level crosswalk now exposes functional, cognitive, affective and cardiometabolic/chronic variable non-equivalence.
- KLoSA is locked as `bridge_sensitivity_descriptive_only`.
- LASI is locked as `baseline_profile_construction_only_no_followup_validation`.
- SHARE is locked as `strict_construction_but_validation_downgraded`.
- CHARLS, ELSA, HRS and MHAS are locked as `strict_construction_within_cohort_gradient_only`.

Manuscript consequence:

- Table 1 and Figure 1 must use `outputs/phase32_cohort_tier_lock.csv` rather than older qualitative tier wording.
- The additional-file variable dictionary should use `outputs/phase32_item_level_harmonization_crosswalk.csv`, not the older domain-only dictionary.

## Blocking Manuscript Rule

The Phase 30 clinical-upgrade manuscript must not be submitted as written. Functional validation must be rewritten as coupled within-cohort association evidence unless Phase 32B produces a non-circular endpoint or a leave-functional-domain-out validation design.

## Next Required Work

1. Phase 32F: rewrite the BMC manuscript as a descriptive/cautionary multidomain burden-profile paper using the locked Phase 32 evidence.
2. Phase 32G: rebuild the BMC package and PDF with no side line numbers after the rewrite.
