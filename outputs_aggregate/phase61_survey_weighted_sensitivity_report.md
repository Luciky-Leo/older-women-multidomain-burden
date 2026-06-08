# Phase 61 Survey-Weight Sensitivity

Date: 2026-06-08

## Decision

The corrected cleaned-file audit did not identify a full weight/PSU/strata triplet in the current model frame. Therefore Phase 61 does not support a seven-cohort survey-weighted prevalence or pooled survey-weighted association claim.

Weight-only sensitivity models were run for: HRS. These models use normalized cleaned weights without PSU/strata and are sensitivity checks only.

## Weight-only model metrics

| cohort | model_type | weighting | weight_variable | n | events | event_pct_unweighted | event_pct_weighted | auc | aic_or_pseudo_aic | weight_mean | weight_p01 | weight_p99 | design_note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| HRS | lfo_profile | unweighted | wtresp | 9081 | 3478 | 38.3 | 38.3 | 0.6933 | 1.115e+04 | 3467 | 834.8 | 1.057e+04 | weight-only normalized GLM; no cleaned PSU/strata available in current model frame |
| HRS | lfo_profile | weight_only_norm | wtresp | 9081 | 3478 | 38.3 | 36.54 | 0.7054 | 1.087e+04 | 3467 | 834.8 | 1.057e+04 | weight-only normalized GLM; no cleaned PSU/strata available in current model frame |
| HRS | lfo_profile | weight_only_trim99 | wtresp | 9081 | 3478 | 38.3 | 36.58 | 0.7056 | 1.087e+04 | 3467 | 834.8 | 1.057e+04 | weight-only normalized GLM; no cleaned PSU/strata available in current model frame |
| HRS | continuous_three_domain | unweighted | wtresp | 9081 | 3478 | 38.3 | 38.3 | 0.7014 | 1.108e+04 | 3467 | 834.8 | 1.057e+04 | weight-only normalized GLM; no cleaned PSU/strata available in current model frame |
| HRS | continuous_three_domain | weight_only_norm | wtresp | 9081 | 3478 | 38.3 | 36.54 | 0.7128 | 1.081e+04 | 3467 | 834.8 | 1.057e+04 | weight-only normalized GLM; no cleaned PSU/strata available in current model frame |
| HRS | continuous_three_domain | weight_only_trim99 | wtresp | 9081 | 3478 | 38.3 | 36.58 | 0.7129 | 1.081e+04 | 3467 | 834.8 | 1.057e+04 | weight-only normalized GLM; no cleaned PSU/strata available in current model frame |

## Corrected status

| cohort | weight_cleaned_variable_count | weight_cleaned_variables | weight_metadata_nonempty_mentions | weight_metadata_evidence | psu_cleaned_variable_count | psu_cleaned_variables | psu_metadata_nonempty_mentions | psu_metadata_evidence | strata_cleaned_variable_count | strata_cleaned_variables | strata_metadata_nonempty_mentions | strata_metadata_evidence | full_cleaned_triplet_available | full_metadata_triplet_available | phase61_analysis_decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CHARLS | 0 |  | 188 | 1 | 0 |  | 32 | 1 | 0 |  | 0 | 0 | 0 | 0 | not_modelable_from_current_cleaned_files |
| ELSA | 0 |  | 178 | 1 | 0 |  | 0 | 0 | 0 |  | 13 | 1 | 0 | 0 | not_modelable_from_current_cleaned_files |
| HRS | 1 | wtresp | 722 | 1 | 0 |  | 3 | 1 | 0 |  | 32 | 1 | 0 | 1 | weight_only_sensitivity_modelable_no_psu_or_strata |
| KLoSA | 0 |  | 40 | 1 | 0 |  | 1 | 1 | 0 |  | 4 | 1 | 0 | 1 | metadata_mentions_only_no_cleaned_design_variables |
| LASI | 0 |  | 99 | 1 | 0 |  | 7 | 1 | 0 |  | 19 | 1 | 0 | 1 | metadata_mentions_only_no_cleaned_design_variables |
| MHAS | 0 |  | 95 | 1 | 0 |  | 0 | 0 | 0 |  | 0 | 0 | 0 | 0 | not_modelable_from_current_cleaned_files |
| SHARE | 0 |  | 217 | 1 | 0 |  | 59 | 1 | 0 |  | 36 | 1 | 0 | 1 | metadata_mentions_only_no_cleaned_design_variables |

## Skipped cohorts

| cohort | reason | phase61_analysis_decision |
| --- | --- | --- |
| CHARLS | no cleaned weight variable available for model frame | not_modelable_from_current_cleaned_files |
| ELSA | no cleaned weight variable available for model frame | not_modelable_from_current_cleaned_files |
| KLoSA | no cleaned weight variable available for model frame | metadata_mentions_only_no_cleaned_design_variables |
| LASI | no cleaned weight variable available for model frame | metadata_mentions_only_no_cleaned_design_variables |
| MHAS | no cleaned weight variable available for model frame | not_modelable_from_current_cleaned_files |
| SHARE | no cleaned weight variable available for model frame | metadata_mentions_only_no_cleaned_design_variables |
