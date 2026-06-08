# Phase 32C Uniform Reference-Class Reanalysis

Date: 2026-06-02

## Decision

All functional endotype ORs should use the cohort-specific lowest-burden available class as reference. Fixed C1 references are not comparable across cohorts.

## Reference Map

| Cohort | Reference class | Label | Severity | Caution |
|---|---|---|---:|---|
| KLoSA | KLoSA_C1 | intermediate-burden with spared cardiometabolic | -0.350 | true_low_burden_reference |
| CHARLS | CHARLS_C1 | intermediate-burden severity-aligned | -0.230 | lowest_available_reference_not_strict_low_burden |
| ELSA | ELSA_C1 | intermediate-burden with spared cardiometabolic | -0.410 | true_low_burden_reference |
| HRS | HRS_C1 | low-burden with spared cardiometabolic | -0.490 | true_low_burden_reference |
| LASI | LASI_C1 | intermediate-burden with spared cardiometabolic | -0.190 | lowest_available_reference_not_strict_low_burden |
| MHAS | MHAS_C1 | intermediate-burden with spared cardiometabolic | -0.410 | true_low_burden_reference |
| SHARE | SHARE_C1 | intermediate-burden with spared cardiometabolic | -0.420 | true_low_burden_reference |

## Model Metrics

| Cohort | Reference | N | Events | AIC | AUC |
|---|---|---:|---:|---:|---:|
| KLoSA | 1 | 3834 | 1144 | 4615.966 | 0.58 |
| CHARLS | 1 | 5691 | 1766 | 6721.782 | 0.6423 |
| ELSA | 1 | 5153 | 1316 | 5144.713 | 0.7394 |
| HRS | 1 | 9431 | 3546 | 11506.008 | 0.6924 |
| MHAS | 1 | 5443 | 1437 | 5972.038 | 0.6687 |
| SHARE | 1 | 12205 | 1525 | 4604.766 | 0.9294 |

## Direction Changes

No direction changes detected among matched original C1-reference terms.

## Skipped

| Cohort | Reason |
|---|---|
| LASI | no_available_data |
