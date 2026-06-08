# Phase 4 Endotype Screen

This is a first-pass Gaussian mixture screen on complete four-domain baseline scores.
All four domain scores are standardized and oriented so higher means worse health.

## Best Models By BIC

Model selection uses the lowest BIC among converged models with minimum class size >= 5%. The BIC-only winner is retained in the CSV outputs.

| Analysis set | Cohort | N | Best classes | BIC | Min class % | Entropy separation | Mean max posterior | Interpretation |
|---|---|---:|---:|---:|---:|---:|---:|---|
| functional_bridge_earliest_sensitivity | KLoSA | 4081 | 3 | 16792.03 | 16.34 | 0.9236 | 0.9668 | domain_specific |
| strict_earliest_primary | CHARLS | 6019 | 3 | 219.45 | 11.41 | 0.9997 | 1.0 | domain_specific |
| strict_earliest_primary | ELSA | 6104 | 5 | -58676.83 | 8.99 | 0.9998 | 1.0 | domain_specific |
| strict_earliest_primary | HRS | 10202 | 5 | -59579.5 | 6.36 | 0.9554 | 0.9714 | domain_specific |
| strict_earliest_primary | LASI | 27433 | 3 | 31419.95 | 20.56 | 0.8367 | 0.9187 | domain_specific |
| strict_earliest_primary | MHAS | 6733 | 5 | -71351.93 | 6.94 | 0.9984 | 0.9992 | domain_specific |
| strict_earliest_primary | SHARE | 15721 | 4 | -11357.53 | 7.24 | 0.9332 | 0.9737 | domain_specific |

BIC-only winners rejected for small class size:

- KLoSA: BIC-only 5 classes (min class 1.13%) -> selected 3 classes.
- LASI: BIC-only 5 classes (min class 1.65%) -> selected 3 classes.

## Best-Model Class Profiles

| Analysis set | Cohort | Class | N | % | Severity mean | Functional | Cognitive | Affective | Cardiometabolic | Label |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| functional_bridge_earliest_sensitivity | KLoSA | 1 | 1986 | 48.66 | -0.3526 | -0.1896 | -0.181 | -0.1797 | -0.8603 | intermediate_spared_cardiometabolic_chronic |
| functional_bridge_earliest_sensitivity | KLoSA | 2 | 1428 | 34.99 | -0.0178 | -0.3015 | -0.2065 | -0.1477 | 0.5847 | intermediate_high_cardiometabolic_chronic |
| functional_bridge_earliest_sensitivity | KLoSA | 3 | 667 | 16.34 | 1.011 | 1.1217 | 0.9561 | 0.72 | 1.2461 | high_burden_severity_aligned |
| strict_earliest_primary | CHARLS | 1 | 4419 | 73.42 | -0.2315 | -0.5196 | -0.1505 | -0.1997 | -0.056 | intermediate_severity_aligned |
| strict_earliest_primary | CHARLS | 2 | 687 | 11.41 | 0.2213 | 0.2715 | 0.2962 | 0.2228 | 0.0946 | intermediate_severity_aligned |
| strict_earliest_primary | CHARLS | 3 | 913 | 15.17 | 0.8407 | 1.8374 | 0.5856 | 0.7004 | 0.2395 | high_burden_high_functional_spared_cardiometabolic_chronic |
| strict_earliest_primary | ELSA | 1 | 2604 | 42.66 | -0.4149 | -0.4212 | -0.1999 | -0.1985 | -0.8399 | intermediate_spared_cardiometabolic_chronic |
| strict_earliest_primary | ELSA | 2 | 1668 | 27.33 | -0.0601 | -0.4212 | -0.0594 | -0.1414 | 0.3817 | intermediate_high_cardiometabolic_chronic_spared_functional |
| strict_earliest_primary | ELSA | 3 | 624 | 10.22 | 0.3703 | 0.5706 | 0.301 | 0.3121 | 0.2975 | intermediate_severity_aligned |
| strict_earliest_primary | ELSA | 4 | 549 | 8.99 | 0.4103 | -0.4212 | 0.2046 | 0.0297 | 1.828 | intermediate_high_cardiometabolic_chronic_spared_functional_affective |
| strict_earliest_primary | ELSA | 5 | 659 | 10.8 | 1.0426 | 2.4804 | 0.3863 | 0.825 | 0.4785 | high_burden_high_functional_spared_cognitive_cardiometabolic_chronic |
| strict_earliest_primary | HRS | 1 | 3596 | 35.25 | -0.4924 | -0.4133 | -0.2965 | -0.2705 | -0.9894 | intermediate_spared_cardiometabolic_chronic |
| strict_earliest_primary | HRS | 2 | 4428 | 43.4 | -0.0303 | -0.4133 | -0.0053 | -0.2097 | 0.5071 | intermediate_high_cardiometabolic_chronic_spared_functional |
| strict_earliest_primary | HRS | 3 | 870 | 8.53 | 0.397 | 0.3953 | 0.3903 | 0.347 | 0.4554 | intermediate_severity_aligned |
| strict_earliest_primary | HRS | 4 | 659 | 6.46 | 0.6935 | 0.7683 | 0.49 | 1.5036 | 0.0122 | high_burden_high_affective_spared_cardiometabolic_chronic |
| strict_earliest_primary | HRS | 5 | 649 | 6.36 | 1.1369 | 2.1171 | 0.6453 | 0.9257 | 0.8595 | high_burden_high_functional_spared_cognitive |
| strict_earliest_primary | LASI | 1 | 15915 | 58.01 | -0.1877 | -0.0969 | 0.0875 | -0.0156 | -0.7258 | intermediate_spared_cardiometabolic_chronic |
| strict_earliest_primary | LASI | 2 | 5641 | 20.56 | -0.0429 | -0.6137 | -0.3776 | -0.1293 | 0.9491 | intermediate_high_cardiometabolic_chronic_spared_functional |
| strict_earliest_primary | LASI | 3 | 5877 | 21.42 | 0.5127 | 0.7158 | 0.1264 | 0.1667 | 1.0421 | high_burden_high_cardiometabolic_chronic_spared_cognitive |
| strict_earliest_primary | MHAS | 1 | 2719 | 40.38 | -0.4101 | -0.323 | -0.101 | -0.2616 | -0.955 | intermediate_spared_cardiometabolic_chronic |
| strict_earliest_primary | MHAS | 2 | 2267 | 33.67 | 0.0043 | -0.323 | -0.0613 | -0.0205 | 0.4219 | intermediate_high_cardiometabolic_chronic |
| strict_earliest_primary | MHAS | 3 | 760 | 11.29 | 0.5351 | -0.0191 | 0.0665 | 0.2944 | 1.7987 | high_burden_high_cardiometabolic_chronic_spared_functional_cognitive |
| strict_earliest_primary | MHAS | 4 | 467 | 6.94 | 0.6752 | 1.8217 | 0.3702 | 0.5134 | -0.0047 | high_burden_high_functional_spared_cardiometabolic_chronic |
| strict_earliest_primary | MHAS | 5 | 520 | 7.72 | 0.7182 | 1.5444 | 0.2831 | 0.6233 | 0.4219 | high_burden_high_functional_spared_cognitive |
| strict_earliest_primary | SHARE | 1 | 6678 | 42.48 | -0.4235 | -0.3175 | -0.2591 | -0.2476 | -0.8698 | intermediate_spared_cardiometabolic_chronic |
| strict_earliest_primary | SHARE | 2 | 5896 | 37.5 | 0.0195 | -0.366 | -0.1176 | -0.084 | 0.6455 | intermediate_high_cardiometabolic_chronic_spared_functional |
| strict_earliest_primary | SHARE | 3 | 2009 | 12.78 | 0.439 | 0.4449 | 0.2444 | 0.4764 | 0.5903 | intermediate_severity_aligned |
| strict_earliest_primary | SHARE | 4 | 1138 | 7.24 | 1.5971 | 2.941 | 1.6908 | 1.0327 | 0.7241 | high_burden_high_functional_spared_affective_cardiometabolic_chronic |

## Severity Comparator

A simple comparator was created by tertiling the mean of the four domain scores. Use this as the null model for low/middle/high severity.

## Proceeding Decision

- Domain-specific best-model profiles: KLoSA, CHARLS, ELSA, HRS, LASI, MHAS, SHARE.
- Mostly severity-gradient best-model profiles: none by the current automated rule.
- Manual inspection of the best-model class profiles is required before moving to manuscript claims.
- Phase 5 should connect these classes to mortality and functional deterioration, and compare them against the severity tertile comparator.
