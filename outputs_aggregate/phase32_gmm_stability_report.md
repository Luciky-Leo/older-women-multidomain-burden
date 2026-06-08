# Phase 32D GMM Stability And Covariance Diagnostics

Date: 2026-06-02

## Decision Rule

- Near-singular covariance flag: min eigenvalue < 1e-05, condition number > 1e+06, or determinant < 1e-10.
- Stable bootstrap rule: median ARI >= 0.75 and 10th percentile ARI >= 0.6, with >=95% convergence.

## Stability Summary

| cohort | n_classes | bootstrap_converged_pct | median_ari_vs_reference | p10_ari_vs_reference | min_ari_vs_reference | median_mean_centroid_distance | max_centroid_distance | any_near_singular_covariance | phase32d_stability_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| KLoSA | 3 | 100.0 | 0.9751 | 0.2322 | 0.225 | 0.0751 | 0.945 | 1 | downgrade_near_singular_covariance |
| CHARLS | 3 | 100.0 | 1.0 | 0.9274 | 0.43 | 0.0491 | 1.5099 | 1 | downgrade_near_singular_covariance |
| ELSA | 5 | 100.0 | 0.9461 | 0.8214 | 0.3461 | 0.1035 | 2.9853 | 1 | downgrade_near_singular_covariance |
| HRS | 5 | 100.0 | 0.9859 | 0.2828 | 0.2818 | 0.5141 | 4.3132 | 1 | downgrade_near_singular_covariance |
| LASI | 3 | 100.0 | 0.9781 | 0.977 | 0.9643 | 0.0995 | 0.2807 | 1 | downgrade_near_singular_covariance |
| MHAS | 5 | 100.0 | 0.9783 | 0.835 | 0.36 | 0.2992 | 2.0518 | 1 | downgrade_near_singular_covariance |
| SHARE | 4 | 100.0 | 0.3679 | 0.3661 | 0.3618 | 0.5048 | 1.1155 | 1 | downgrade_near_singular_covariance |

## Covariance Flags

| cohort | ordered_class | component_weight | min_covariance_eigenvalue | covariance_condition_number | covariance_determinant |
| --- | --- | --- | --- | --- | --- |
| KLoSA | 1 | 0.4863 | 0.0 | 1364626.5392 | 0.0 |
| CHARLS | 1 | 0.7342 | 0.0 | 1102114.681 | 0.0 |
| CHARLS | 2 | 0.1141 | 0.0 | 1199523.9855 | 0.0 |
| ELSA | 1 | 0.4266 | 0.0 | 849515.6319 | 0.0 |
| ELSA | 2 | 0.2733 | 0.0 | 956137.6175 | 0.0 |
| ELSA | 3 | 0.1022 | 0.0 | 1354678.3652 | 0.0 |
| ELSA | 4 | 0.0899 | 0.0 | 1270861.7191 | 0.0 |
| HRS | 1 | 0.3524 | 0.0 | 857692.3223 | 0.0 |
| HRS | 2 | 0.4622 | 0.0 | 1091449.5246 | 0.0 |
| HRS | 3 | 0.0924 | 0.0 | 1518608.7265 | 0.0 |
| HRS | 4 | 0.0405 | 0.0 | 1443966.1112 | 0.0 |
| LASI | 1 | 0.539 | 0.0 | 1194111.5547 | 0.0 |
| LASI | 2 | 0.2392 | 0.0 | 1078032.5244 | 0.0 |
| MHAS | 1 | 0.4038 | 0.0 | 1066338.5819 | 0.0 |
| MHAS | 2 | 0.4052 | 0.0 | 1019094.5307 | 0.0 |
| MHAS | 4 | 0.1012 | 0.0 | 2533332.3976 | 0.0 |
| SHARE | 1 | 0.4127 | 0.0 | 823544.1881 | 0.0 |
| SHARE | 2 | 0.3862 | 0.0 | 927580.0212 | 0.0 |

## Manuscript Rule

Profiles marked stable_by_bootstrap_ari can remain in descriptive profile construction tables.
Profiles marked with any downgrade status must be explicitly labeled as unstable or downgraded to sensitivity/descriptive-only evidence.
