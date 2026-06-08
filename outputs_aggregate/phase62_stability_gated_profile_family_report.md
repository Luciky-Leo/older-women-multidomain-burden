# Phase 62 Stability-Gated Profile Family Analysis

Date: 2026-06-08

## Decision

Model-based alternative algorithms passed the pre-specified descriptive stability gate in 2 cohorts. Severity-strata-only fallback passed in 5 cohorts.

Even where a model-based alternative passes the numerical gate, the result remains a descriptive sensitivity profile because the analysis does not add independent biological mechanism, survey-weighted transportability, or independent hard-endpoint validation.

Endotype language remains disallowed for all cohorts in this package.

## Cohort decisions

| cohort | phase62_decision | best_available_method | best_p10_ari | best_median_ari | best_ari_vs_selected_full_gmm | endotype_claim_allowed | recommended_claim |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CHARLS | only_severity_strata_pass_stability_gate | severity_quantile_k | 1 | 1 | 0.1227 | no | descriptive sensitivity only; continuous domain scores remain primary for modelling |
| ELSA | only_severity_strata_pass_stability_gate | severity_quantile_k | 1 | 1 | 0.1787 | no | descriptive sensitivity only; continuous domain scores remain primary for modelling |
| HRS | only_severity_strata_pass_stability_gate | severity_quantile_k | 1 | 1 | 0.1488 | no | descriptive sensitivity only; continuous domain scores remain primary for modelling |
| KLoSA | only_severity_strata_pass_stability_gate | severity_quantile_k | 1 | 1 | 0.2175 | no | descriptive sensitivity only; continuous domain scores remain primary for modelling |
| LASI | model_based_profile_family_supported_as_descriptive_sensitivity | kmeans | 0.8199 | 0.959 | 0.6175 | no | descriptive sensitivity only; continuous domain scores remain primary for modelling |
| MHAS | only_severity_strata_pass_stability_gate | severity_quantile_k | 1 | 1 | 0.1436 | no | descriptive sensitivity only; continuous domain scores remain primary for modelling |
| SHARE | model_based_profile_family_supported_as_descriptive_sensitivity | kmeans | 0.9343 | 0.9707 | 0.2156 | no | descriptive sensitivity only; continuous domain scores remain primary for modelling |

## Gate thresholds

- median bootstrap ARI >= 0.9
- 10th percentile bootstrap ARI >= 0.75
- minimum class percentage >= 5.0%
- no covariance guardrail flag for model-based GMM alternatives
- at least 95% bootstrap convergence

## Gate summary

| analysis_set | analysis_tier | cohort | wave | method | target_classes | n | observed_classes | min_class_pct | ari_vs_selected_full_gmm | silhouette_sample | bootstrap_replicates | bootstrap_converged_pct | median_ari_vs_full_fit | p10_ari_vs_full_fit | min_ari_vs_full_fit | median_replicate_min_class_pct | covariance_guardrail_flag | phase62_gate_pass | phase62_gate_conclusion |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| functional_bridge_earliest_sensitivity | bridge_sensitivity | KLoSA | 3 | gmm_diag | 3 | 4081 | 3 | 20.56 | 0.913 | 0.1949 | 100 | 100 | 0.2346 | 0.2047 | 0.1949 | 21.01 | 1 | 0 | fails_covariance_guardrail |
| functional_bridge_earliest_sensitivity | bridge_sensitivity | KLoSA | 3 | kmeans | 3 | 4081 | 3 | 22.45 | 0.6878 | 0.2565 | 100 | 100 | 0.5092 | 0.4525 | 0.4051 | 19.41 | 0 | 0 | fails_bootstrap_ari_gate |
| functional_bridge_earliest_sensitivity | bridge_sensitivity | KLoSA | 3 | severity_quantile_k | 3 | 4081 | 3 | 33.33 | 0.2175 | 0.1386 | 100 | 100 | 1 | 1 | 1 | 33.33 | 0 | 1 | stable_severity_strata_not_latent_profile |
| strict_earliest_primary | strict_primary | CHARLS | 1 | gmm_diag | 3 | 6019 | 3 | 11.41 | 1 | 0.1166 | 100 | 100 | 1 | 0.9275 | 0.6373 | 11.41 | 1 | 0 | fails_covariance_guardrail |
| strict_earliest_primary | strict_primary | CHARLS | 1 | kmeans | 3 | 6019 | 3 | 15.67 | 0.207 | 0.2879 | 100 | 100 | 0.8903 | 0.2706 | 0.2528 | 15.46 | 0 | 0 | fails_bootstrap_ari_gate |
| strict_earliest_primary | strict_primary | CHARLS | 1 | severity_quantile_k | 3 | 6019 | 3 | 33.33 | 0.1227 | 0.1274 | 100 | 100 | 1 | 1 | 1 | 33.33 | 0 | 1 | stable_severity_strata_not_latent_profile |
| strict_earliest_primary | strict_primary | ELSA | 1 | gmm_diag | 5 | 6104 | 5 | 8.994 | 1 | 0.2033 | 100 | 100 | 0.8845 | 0.3421 | 0.2803 | 5.349 | 1 | 0 | fails_covariance_guardrail |
| strict_earliest_primary | strict_primary | ELSA | 1 | kmeans | 5 | 6104 | 5 | 7.913 | 0.2429 | 0.2916 | 100 | 100 | 0.888 | 0.4307 | 0.4118 | 7.847 | 0 | 0 | fails_bootstrap_ari_gate |
| strict_earliest_primary | strict_primary | ELSA | 1 | severity_quantile_k | 5 | 6104 | 5 | 19.99 | 0.1787 | 0.05734 | 100 | 100 | 1 | 1 | 1 | 19.99 | 0 | 1 | stable_severity_strata_not_latent_profile |
| strict_earliest_primary | strict_primary | HRS | 5 | gmm_diag | 5 | 10202 | 4 | 2.999 | 0.3571 | -0.02872 | 100 | 100 | 0.9811 | 0.4021 | 0.3586 | 0.4362 | 1 | 0 | fails_covariance_guardrail |
| strict_earliest_primary | strict_primary | HRS | 5 | kmeans | 5 | 10202 | 5 | 6.126 | 0.1712 | 0.2873 | 100 | 100 | 0.8868 | 0.7905 | 0.697 | 6.156 | 0 | 0 | fails_stability_gate |
| strict_earliest_primary | strict_primary | HRS | 5 | severity_quantile_k | 5 | 10202 | 5 | 20 | 0.1488 | 0.07132 | 100 | 100 | 1 | 1 | 1 | 20 | 0 | 1 | stable_severity_strata_not_latent_profile |
| strict_earliest_primary | strict_primary | LASI | all_rows_no_wave | gmm_diag | 3 | 27433 | 3 | 21.42 | 0.9551 | 0.1784 | 100 | 100 | 0.9837 | 0.1961 | 0.1603 | 21.42 | 1 | 0 | fails_covariance_guardrail |
| strict_earliest_primary | strict_primary | LASI | all_rows_no_wave | kmeans | 3 | 27433 | 3 | 17.59 | 0.6175 | 0.2433 | 100 | 100 | 0.959 | 0.8199 | 0.2418 | 17.58 | 0 | 1 | passes_phase62_model_based_stability_gate |
| strict_earliest_primary | strict_primary | LASI | all_rows_no_wave | severity_quantile_k | 3 | 27433 | 3 | 33.33 | 0.09024 | 0.09469 | 100 | 100 | 1 | 1 | 1 | 33.33 | 0 | 1 | stable_severity_strata_not_latent_profile |
| strict_earliest_primary | strict_primary | MHAS | 1 | gmm_diag | 5 | 6733 | 5 | 7.218 | 0.9513 | 0.1792 | 100 | 100 | 0.8366 | 0.2907 | 0.2351 | 3.527 | 1 | 0 | fails_covariance_guardrail |
| strict_earliest_primary | strict_primary | MHAS | 1 | kmeans | 5 | 6733 | 5 | 4.589 | 0.1945 | 0.2813 | 100 | 100 | 0.9224 | 0.4688 | 0.446 | 4.604 | 0 | 0 | fails_min_class_gate |
| strict_earliest_primary | strict_primary | MHAS | 1 | severity_quantile_k | 5 | 6733 | 5 | 19.99 | 0.1436 | 0.0588 | 100 | 100 | 1 | 1 | 1 | 19.99 | 0 | 1 | stable_severity_strata_not_latent_profile |
| strict_earliest_primary | strict_primary | SHARE | 1 | gmm_diag | 4 | 15721 | 4 | 7.29 | 0.3666 | 0.1096 | 100 | 100 | 0.9644 | 0.9626 | 0.3668 | 6.806 | 1 | 0 | fails_covariance_guardrail |
| strict_earliest_primary | strict_primary | SHARE | 1 | kmeans | 4 | 15721 | 4 | 5.025 | 0.2156 | 0.3164 | 100 | 100 | 0.9707 | 0.9343 | 0.8901 | 4.984 | 0 | 1 | passes_phase62_model_based_stability_gate |
| strict_earliest_primary | strict_primary | SHARE | 1 | severity_quantile_k | 4 | 15721 | 4 | 25 | 0.1755 | 0.08066 | 100 | 100 | 0.9995 | 0.9995 | 0.9995 | 25 | 0 | 1 | stable_severity_strata_not_latent_profile |
