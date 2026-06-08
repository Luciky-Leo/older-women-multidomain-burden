# Phase 10 Class Label Candidates

These labels are deterministic candidates for manuscript triage.
They should be manually edited before final tables because cohort-specific clinical context still matters.

## Candidate Labels

| analysis_set | cohort | class | class_pct | label_en | label_zh | label_confidence | outcome_flags | mortality_drift_flag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| functional_bridge_earliest_sensitivity | KLoSA | 1 | 48.66 | intermediate-burden with spared cardiometabolic | 心代谢/慢病相对保留的中等负担 | moderate |  | 0 |
| functional_bridge_earliest_sensitivity | KLoSA | 2 | 34.99 | cardiometabolic-dominant intermediate-burden | 心代谢/慢病主导型中等负担 | provisional |  | 1 |
| functional_bridge_earliest_sensitivity | KLoSA | 3 | 16.34 | functional/cardiometabolic-dominant high-burden | 功能/心代谢/慢病主导型高负担 | high |  | 0 |
| strict_earliest_primary | CHARLS | 1 | 73.42 | intermediate-burden severity-aligned | 中等负担严重度一致型 | low |  | 0 |
| strict_earliest_primary | CHARLS | 2 | 11.41 | elevated-burden severity-aligned | 较高负担严重度一致型 | low |  | 0 |
| strict_earliest_primary | CHARLS | 3 | 15.17 | functional-dominant high-burden | 功能主导型高负担 | high | mortality-risk | 0 |
| strict_earliest_primary | ELSA | 1 | 42.66 | intermediate-burden with spared cardiometabolic | 心代谢/慢病相对保留的中等负担 | moderate |  | 0 |
| strict_earliest_primary | ELSA | 2 | 27.33 | cardiometabolic-dominant intermediate-burden | 心代谢/慢病主导型中等负担 | high |  | 0 |
| strict_earliest_primary | ELSA | 3 | 10.22 | elevated-burden severity-aligned | 较高负担严重度一致型 | low | mortality-risk | 0 |
| strict_earliest_primary | ELSA | 4 | 8.99 | cardiometabolic-dominant elevated-burden | 心代谢/慢病主导型较高负担 | high | functional-risk;mortality-risk | 0 |
| strict_earliest_primary | ELSA | 5 | 10.8 | functional-dominant high-burden | 功能主导型高负担 | high | mortality-risk | 0 |
| strict_earliest_primary | HRS | 1 | 35.25 | low-burden with spared cardiometabolic | 心代谢/慢病相对保留的低负担 | moderate |  | 0 |
| strict_earliest_primary | HRS | 2 | 43.4 | cardiometabolic-dominant intermediate-burden | 心代谢/慢病主导型中等负担 | high | functional-risk;mortality-risk | 0 |
| strict_earliest_primary | HRS | 3 | 8.53 | elevated-burden severity-aligned | 较高负担严重度一致型 | provisional | functional-risk;mortality-risk | 1 |
| strict_earliest_primary | HRS | 4 | 6.46 | affective-dominant elevated-burden | 心理/抑郁主导型较高负担 | provisional | functional-risk;mortality-risk | 1 |
| strict_earliest_primary | HRS | 5 | 6.36 | functional-dominant high-burden | 功能主导型高负担 | provisional | mortality-risk | 1 |
| strict_earliest_primary | LASI | 1 | 58.01 | intermediate-burden with spared cardiometabolic | 心代谢/慢病相对保留的中等负担 | moderate |  | 0 |
| strict_earliest_primary | LASI | 2 | 20.56 | cardiometabolic-dominant intermediate-burden | 心代谢/慢病主导型中等负担 | high |  | 0 |
| strict_earliest_primary | LASI | 3 | 21.42 | cardiometabolic-dominant elevated-burden | 心代谢/慢病主导型较高负担 | high |  | 0 |
| strict_earliest_primary | MHAS | 1 | 40.38 | intermediate-burden with spared cardiometabolic | 心代谢/慢病相对保留的中等负担 | moderate |  | 0 |
| strict_earliest_primary | MHAS | 2 | 33.67 | cardiometabolic-dominant intermediate-burden | 心代谢/慢病主导型中等负担 | high | functional-risk | 0 |
| strict_earliest_primary | MHAS | 3 | 11.29 | cardiometabolic-dominant elevated-burden | 心代谢/慢病主导型较高负担 | high | functional-risk;mortality-risk | 0 |
| strict_earliest_primary | MHAS | 4 | 6.94 | functional-dominant elevated-burden | 功能主导型较高负担 | moderate | mortality-risk | 0 |
| strict_earliest_primary | MHAS | 5 | 7.72 | functional-dominant elevated-burden | 功能主导型较高负担 | moderate | mortality-risk | 0 |
| strict_earliest_primary | SHARE | 1 | 42.48 | intermediate-burden with spared cardiometabolic | 心代谢/慢病相对保留的中等负担 | moderate |  | 0 |
| strict_earliest_primary | SHARE | 2 | 37.5 | cardiometabolic-dominant intermediate-burden | 心代谢/慢病主导型中等负担 | high |  | 0 |
| strict_earliest_primary | SHARE | 3 | 12.78 | elevated-burden severity-aligned | 较高负担严重度一致型 | low | functional-risk;mortality-risk | 0 |
| strict_earliest_primary | SHARE | 4 | 7.24 | functional/cognitive/affective-dominant high-burden | 功能/认知/心理/抑郁主导型高负担 | moderate | functional-risk;mortality-risk | 0 |

## Use Rules

- Use English labels for figure legends and Chinese labels for internal review notes.
- Treat `provisional` labels as requiring manual review, usually because mortality HRs drift across follow-up periods.
- Do not force identical labels across cohorts unless the four-domain profiles and outcome signals are genuinely similar.
