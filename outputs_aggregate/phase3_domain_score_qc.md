# Phase 3 Domain Score QC

All domain scores are oriented so higher values indicate worse health.
Scores are standardized within cohort and wave before cross-domain modeling.

## Analysis Sets

| Analysis set | Cohort | Wave | N | Complete four-domain N | Complete four-domain % | Functional source |
|---|---|---|---:|---:|---:|---|
| functional_bridge_earliest_sensitivity | KLoSA | 3 | 4344 | 4081 | 93.95 | bridge |
| strict_earliest_primary | CHARLS | 1 | 6878 | 6019 | 87.51 | primary |
| strict_earliest_primary | ELSA | 1 | 6292 | 6104 | 97.01 | primary |
| strict_earliest_primary | HRS | 5 | 11005 | 10202 | 92.7 | primary |
| strict_earliest_primary | LASI | all_rows_no_wave | 28165 | 27433 | 97.4 | primary |
| strict_earliest_primary | MHAS | 1 | 7440 | 6733 | 90.5 | primary |
| strict_earliest_primary | SHARE | 1 | 15814 | 15721 | 99.41 | primary |

## Domain Missingness

| Analysis set | Cohort | Functional % | Cognitive % | Affective % | Cardiometabolic % |
|---|---|---:|---:|---:|---:|
| functional_bridge_earliest_sensitivity | KLoSA | 100.0 | 94.73 | 99.1 | 100.0 |
| strict_earliest_primary | CHARLS | 99.13 | 87.58 | 92.82 | 99.26 |
| strict_earliest_primary | ELSA | 98.51 | 97.52 | 97.09 | 99.94 |
| strict_earliest_primary | HRS | 99.85 | 92.81 | 92.78 | 100.0 |
| strict_earliest_primary | LASI | 99.69 | 98.76 | 97.43 | 99.82 |
| strict_earliest_primary | MHAS | 93.92 | 92.73 | 93.67 | 97.92 |
| strict_earliest_primary | SHARE | 100.0 | 99.47 | 100.0 | 99.53 |

## Correlation Screen

No absolute pairwise domain correlation >= 0.70 in the selected score sets.

## Proceeding Decision

- Strict primary modeling can start with CHARLS, ELSA, HRS, LASI, MHAS, and SHARE.
- KLoSA should remain a sensitivity cohort because its functional score is a performance bridge.
- SHARE uses a strict wave-1 ADL/IADL functional score merged from the local SHARE wave-1 Stata file.
- Phase 4 should test whether classes are domain-specific rather than a single severity gradient.
