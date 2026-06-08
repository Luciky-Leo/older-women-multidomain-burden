# Phase 2 Sex Coding and Four-Domain Harmonization Report

## Sex Coding Confirmation

The cleaned project files use `ragender == 0` for women and `ragender == 1` for men in all seven cohorts.
This is confirmed from the Working_data Stata value labels and the local merge do-files.

| Cohort | DTA value mapping | Female code | Male code | Status |
|---|---|---:|---:|---|
| CHARLS | 0=女性; 1=男性 | 0 | 1 | confirmed |
| ELSA | 0=女性; 1=男性 | 0 | 1 | confirmed |
| HRS | 0=女性; 1=男性 | 0 | 1 | confirmed |
| KLoSA | 0=女性; 1=男性 | 0 | 1 | confirmed |
| LASI | 0=女性; 1=男性 | 0 | 1 | confirmed |
| MHAS | 0=女性; 1=男性 | 0 | 1 | confirmed |
| SHARE | 0=女性; 1=男性 | 0 | 1 | confirmed |

## Four-Domain Readiness

| Cohort | Women 50+ baseline | Functional | Cognitive | Affective | Cardiometabolic/chronic |
|---|---:|---|---|---|---|
| CHARLS | 6878 | ready_primary | ready_primary | ready_primary | ready_primary |
| ELSA | 6292 | ready_primary | ready_primary | ready_primary | ready_primary |
| HRS | 11005 | ready_primary | ready_primary | ready_primary | ready_primary |
| KLoSA | 4344 | limited_performance_ready | ready_primary | ready_primary | ready_primary |
| LASI | 28165 | ready_primary | ready_primary | ready_primary | ready_primary |
| MHAS | 7440 | ready_primary | ready_primary | ready_primary | ready_primary |
| SHARE | 15814 | limited_supporting_only | ready_primary | ready_primary | ready_primary |

## Interpretation

- Strict earliest-wave four-primary-domain cohorts: CHARLS, ELSA, HRS, LASI, MHAS.
- Practical earliest-wave endotype modeling cohorts: CHARLS, ELSA, HRS, KLoSA, LASI, MHAS
- Strict wave-adjusted four-primary-domain cohorts: CHARLS, ELSA, HRS, LASI, MHAS
- Practical wave-adjusted endotype modeling cohorts: CHARLS, ELSA, HRS, KLoSA, LASI, MHAS, SHARE
- Targeted variable expansion resolved the LASI chronic-disease gap and the MHAS/SHARE cognition and depressive-symptom gaps from existing cleaned Working_data/CSV variables.
- SHARE still does not have a strict ADL/IADL functional primary variable under the current candidate rule; it is practical only with a performance/frailty functional bridge.
- The baseline table above uses the earliest available wave, matching Phase 1. SHARE needs a later wave for the practical four-domain bridge because earliest-wave functional coverage is too thin.

## Wave-Level Baseline Check

The selected wave below maximizes ready/limited domain count, then women 50+ sample size. It is a feasibility choice, not yet the final longitudinal baseline.

| Cohort | Best current wave | Women 50+ rows | Ready/limited domains | Functional | Cognitive | Affective | Cardiometabolic/chronic |
|---|---|---:|---:|---|---|---|---|
| CHARLS | 5 | 9539 | 4 | primary:iadl | primary:total_cognition;memory_z;orient_z;tcog_z_z;ser7;imrc;dlrc;orient | primary:cesd10 | primary:hibpe;diabe;hearte;stroke;dyslipe;cancre |
| ELSA | 1 | 6292 | 4 | primary:adltot6 | primary:imrc;dlrc;orient | primary:cesd | primary:hibpe;diabe;hearte;stroke;cancre |
| HRS | 10 | 12058 | 4 | primary:adl6a | primary:cogtot;cog27;memory_z;orient_z;tcog_z_z;ser7;imrc;dlrc;orient | primary:cesd;depressive | primary:hibpe;diabe;hearte;stroke;cancre |
| KLoSA | 3 | 4344 | 4 | limited:gripsum;gripcomp;fall | primary:cog_total;ser7 | primary:cesd10a | primary:hibpe;diabe;hearte;stroke;cancre |
| LASI | all_rows_no_wave | 28165 | 4 | primary:r1adltot6;r1iadltot_l | primary:r1cog_total | primary:r1cesd10 | primary:r1hibpe;r1diabe;r1hearte;r1stroke;r1hchole;r1cancre |
| MHAS | 5 | 8969 | 4 | primary:adltot6;iadlfour | primary:imrc8;dlrc8;ser7 | primary:cesd_m | primary:hibpe;diabe;hearte;stroke;cancre |
| SHARE | 6 | 37539 | 4 | limited:frailtyb;gripcomp | primary:ser7;imrc;dlrc;orient | primary:eurod | primary:hibpe;diabe;hearte;stroke;hchole;cancre |

## Minimal Harmonization Rule For The Next Script

- Use `ragender == 0` and baseline age >= 50 for the primary women-only cohort.
- Build domain scores within cohort/wave and orient every domain so higher means worse health.
- Functional: ADL/IADL when available; otherwise keep performance/frailty variables as a sensitivity bridge.
- Cognitive: require a continuous/global cognition score for primary modeling; dementia indicators are supporting variables only.
- Affective: require CES-D/depressive symptoms for primary modeling; `psyche` and `satlifez` need label/range checks before secondary use.
- Cardiometabolic/chronic: use a count or proportion of available chronic disease indicators, with BMI/BP as secondary severity components.
