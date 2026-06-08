# Phase 32A Functional Endpoint Leakage Audit

Date: 2026-06-02

## Decision

The current primary functional endpoint is a same-domain score-change endpoint: follow-up functional score minus baseline functional score >= 0.5 SD. Because baseline functional score is also one of the four profile-construction inputs, this endpoint should not be used to claim independent clinical prediction.

Use current functional models only as coupled within-cohort association evidence unless a decoupled endpoint is rebuilt.

## Status By Cohort

| Cohort | Tier | N | Events | Event % | Functional variables | Max OR | Main evidence status |
|---|---|---:|---:|---:|---|---:|---|
| KLoSA | bridge_sensitivity | 3834 | 1144 | 29.84 | gripsum+gripcomp+fall | 1.3952 | bridge_sensitivity_only |
| CHARLS | strict_primary | 5691 | 1766 | 31.03 | iadl | 0.7353 | usable_only_as_coupled_within_cohort_association |
| ELSA | strict_primary | 5153 | 1316 | 25.54 | adltot6+iadltot2_e | 2.041 | usable_only_as_coupled_within_cohort_association |
| HRS | strict_primary | 9431 | 3546 | 37.6 | adl6a | 1.7122 | usable_only_as_coupled_within_cohort_association |
| LASI | strict_primary | 0 | 0 | nan | r1adltot6+r1iadltot_l | nan | exclude_no_followup_validation |
| MHAS | strict_primary | 5443 | 1437 | 26.4 | adltot6+iadlfour | 2.0886 | usable_only_as_coupled_within_cohort_association |
| SHARE | strict_primary | 12205 | 1525 | 12.49 | adl+iadl | 109.7972 | exclude_or_redefine_until_endpoint_decoupled |

## Flagged Rows

| Cohort | Reason |
|---|---|
| KLoSA | bridge_sensitivity_only |
| LASI | exclude_no_followup_validation |
| SHARE | exclude_or_redefine_until_endpoint_decoupled |

## Required Next Step

Phase 32B should rebuild validation with a non-circular endpoint or a leave-functional-domain-out profile design before the manuscript is rewritten.
