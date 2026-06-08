# Phase 62 Stability-Gated Profile Family Analysis

Date: 2026-06-08

## Decision

Model-based alternative algorithms passed the pre-specified descriptive stability gate in 1 cohorts. Severity-strata-only fallback passed in 6 cohorts.

The Phase 62 gate used 20 bounded nonparametric bootstrap refits per bootstrapped method, with each refit drawing up to 3000 original participants with replacement and predicting labels for the full cohort. This is a rapid pre-submission sensitivity analysis, not a definitive external validation study.

Even where a model-based alternative passes the numerical gate, the result remains a descriptive sensitivity profile because the analysis does not add independent biological mechanism, survey-weighted transportability, or independent hard-endpoint validation.

Endotype language remains disallowed for all cohorts in this package.

## Cohort decisions

| cohort | phase62_decision | best_available_method | best_p10_ari | best_median_ari | best_ari_vs_selected_full_gmm | endotype_claim_allowed | recommended_claim |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CHARLS | only_severity_strata_pass_stability_gate | severity_quantile_k | 0.9131 | 0.9538 | 0.1227 | no | descriptive sensitivity only; continuous domain scores remain primary for modelling |
| ELSA | only_severity_strata_pass_stability_gate | severity_quantile_k | 0.878 | 0.9309 | 0.1787 | no | descriptive sensitivity only; continuous domain scores remain primary for modelling |
| HRS | only_severity_strata_pass_stability_gate | severity_quantile_k | 0.8842 | 0.9498 | 0.1488 | no | descriptive sensitivity only; continuous domain scores remain primary for modelling |
| KLoSA | only_severity_strata_pass_stability_gate | severity_quantile_k | 0.916 | 0.9612 | 0.2175 | no | descriptive sensitivity only; continuous domain scores remain primary for modelling |
| LASI | only_severity_strata_pass_stability_gate | severity_quantile_k | 0.9244 | 0.9686 | 0.09024 | no | descriptive sensitivity only; continuous domain scores remain primary for modelling |
| MHAS | only_severity_strata_pass_stability_gate | severity_quantile_k | 0.9074 | 0.9389 | 0.1436 | no | descriptive sensitivity only; continuous domain scores remain primary for modelling |
| SHARE | model_based_profile_family_supported_as_descriptive_sensitivity | kmeans | 0.9125 | 0.9494 | 0.2156 | no | descriptive sensitivity only; continuous domain scores remain primary for modelling |

## Gate thresholds

- median bootstrap ARI >= 0.9
- 10th percentile bootstrap ARI >= 0.75
- minimum class percentage >= 5.0%
- no covariance guardrail flag for model-based GMM alternatives
- at least 95% bootstrap convergence

## Gate summary

| analysis_set | analysis_tier | cohort | wave | method | target_classes | n | observed_classes | min_class_pct | ari_vs_selected_full_gmm | silhouette_sample | bootstrap_replicates | bootstrap_converged_pct | median_ari_vs_full_fit | p10_ari_vs_full_fit | min_ari_vs_full_fit | median_replicate_min_class_pct | covariance_guardrail_flag | phase62_gate_pass | phase62_gate_conclusion |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| functional_bridge_earliest_sensitivity | bridge_sensitivity | KLoSA | 3 | gmm_diag | 3 | 4081 | 3 | 20.56 | 0.913 | 0.1949 | 20 | 100 | 0.2434 | 0.2092 | 0.186 | 20.77 | 1 | 0 | fails_covariance_guardrail |
| functional_bridge_earliest_sensitivity | bridge_sensitivity | KLoSA | 3 | kmeans | 3 | 4081 | 3 | 22.45 | 0.6878 | 0.2565 | 20 | 100 | 0.707 | 0.4573 | 0.4062 | 20.12 | 0 | 0 | fails_bootstrap_ari_gate |
| functional_bridge_earliest_sensitivity | bridge_sensitivity | KLoSA | 3 | severity_quantile_k | 3 | 4081 | 3 | 33.33 | 0.2175 | 0.1386 | 20 | 100 | 0.9612 | 0.916 | 0.8993 | 32.41 | 0 | 1 | stable_severity_strata_not_latent_profile |
| strict_earliest_primary | strict_primary | CHARLS | 1 | gmm_diag | 3 | 6019 | 3 | 11.41 | 1 | 0.1166 | 20 | 100 | 1 | 0.9275 | 0.43 | 11.41 | 1 | 0 | fails_covariance_guardrail |
| strict_earliest_primary | strict_primary | CHARLS | 1 | kmeans | 3 | 6019 | 3 | 15.67 | 0.207 | 0.2865 | 20 | 100 | 0.8279 | 0.2671 | 0.2595 | 15.57 | 0 | 0 | fails_bootstrap_ari_gate |
| strict_earliest_primary | strict_primary | CHARLS | 1 | severity_quantile_k | 3 | 6019 | 3 | 33.33 | 0.1227 | 0.1324 | 20 | 100 | 0.9538 | 0.9131 | 0.9064 | 32.26 | 0 | 1 | stable_severity_strata_not_latent_profile |
| strict_earliest_primary | strict_primary | ELSA | 1 | gmm_diag | 5 | 6104 | 5 | 8.994 | 1 | 0.202 | 20 | 100 | 0.684 | 0.2939 | 0.2897 | 3.154 | 1 | 0 | fails_covariance_guardrail |
| strict_earliest_primary | strict_primary | ELSA | 1 | kmeans | 5 | 6104 | 5 | 7.913 | 0.2429 | 0.2932 | 20 | 100 | 0.501 | 0.4259 | 0.4129 | 7.954 | 0 | 0 | fails_bootstrap_ari_gate |
| strict_earliest_primary | strict_primary | ELSA | 1 | severity_quantile_k | 5 | 6104 | 5 | 19.99 | 0.1787 | 0.05757 | 20 | 100 | 0.9309 | 0.878 | 0.8646 | 19.17 | 0 | 1 | stable_severity_strata_not_latent_profile |
| strict_earliest_primary | strict_primary | HRS | 5 | gmm_diag | 5 | 10202 | 4 | 2.999 | 0.3571 | -0.03413 | 20 | 100 | 0.4056 | 0.3962 | 0.3254 | 1.808 | 1 | 0 | fails_covariance_guardrail |
| strict_earliest_primary | strict_primary | HRS | 5 | kmeans | 5 | 10202 | 5 | 6.126 | 0.1712 | 0.288 | 20 | 100 | 0.861 | 0.7076 | 0.7016 | 6.273 | 0 | 0 | fails_bootstrap_ari_gate |
| strict_earliest_primary | strict_primary | HRS | 5 | severity_quantile_k | 5 | 10202 | 5 | 20 | 0.1488 | 0.07165 | 20 | 100 | 0.9498 | 0.8842 | 0.8543 | 19.04 | 0 | 1 | stable_severity_strata_not_latent_profile |
| strict_earliest_primary | strict_primary | LASI | all_rows_no_wave | gmm_diag | 3 | 27433 | 3 | 21.42 | 0.9551 | 0.1777 | 20 | 100 | 0.9333 | 0.1949 | 0.1597 | 20.52 | 1 | 0 | fails_covariance_guardrail |
| strict_earliest_primary | strict_primary | LASI | all_rows_no_wave | kmeans | 3 | 27433 | 3 | 17.59 | 0.6175 | 0.2472 | 20 | 100 | 0.7717 | 0.2339 | 0.1966 | 14.4 | 0 | 0 | fails_bootstrap_ari_gate |
| strict_earliest_primary | strict_primary | LASI | all_rows_no_wave | severity_quantile_k | 3 | 27433 | 3 | 33.33 | 0.09024 | 0.09223 | 20 | 100 | 0.9686 | 0.9244 | 0.8965 | 32.71 | 0 | 1 | stable_severity_strata_not_latent_profile |
| strict_earliest_primary | strict_primary | MHAS | 1 | gmm_diag | 5 | 6733 | 5 | 7.218 | 0.9513 | 0.1804 | 20 | 100 | 0.8361 | 0.2814 | 0.2425 | 3.765 | 1 | 0 | fails_covariance_guardrail |
| strict_earliest_primary | strict_primary | MHAS | 1 | kmeans | 5 | 6733 | 5 | 4.589 | 0.1945 | 0.282 | 20 | 100 | 0.9167 | 0.4483 | 0.4369 | 4.463 | 0 | 0 | fails_min_class_gate |
| strict_earliest_primary | strict_primary | MHAS | 1 | severity_quantile_k | 5 | 6733 | 5 | 19.99 | 0.1436 | 0.05859 | 20 | 100 | 0.9389 | 0.9074 | 0.897 | 19 | 0 | 1 | stable_severity_strata_not_latent_profile |
| strict_earliest_primary | strict_primary | SHARE | 1 | gmm_diag | 4 | 15721 | 4 | 7.29 | 0.3666 | 0.1077 | 20 | 100 | 0.9944 | 0.9631 | 0.3773 | 6.87 | 1 | 0 | fails_covariance_guardrail |
| strict_earliest_primary | strict_primary | SHARE | 1 | kmeans | 4 | 15721 | 4 | 5.025 | 0.2156 | 0.3144 | 20 | 100 | 0.9494 | 0.9125 | 0.9082 | 4.888 | 0 | 1 | passes_phase62_model_based_stability_gate |
| strict_earliest_primary | strict_primary | SHARE | 1 | severity_quantile_k | 4 | 15721 | 4 | 25 | 0.1755 | 0.07697 | 20 | 100 | 0.9411 | 0.8974 | 0.8658 | 23.96 | 0 | 1 | stable_severity_strata_not_latent_profile |
