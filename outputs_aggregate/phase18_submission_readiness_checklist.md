# Phase 18 Submission Readiness Checklist

## Blocking Before Submission

- Resolve 13 labels with `human_signoff_required == 1` in `outputs/phase18_final_label_dictionary_v0.csv`.
- Confirm target journal and adapt word count, table count, and supplement format.
- Replace URL-style references with formal citations and a reference list.
- Decide whether the main figure uses the four main validation cohorts only or the seven-cohort sensitivity display.
- Confirm whether LASI remains in Table 1/Table 2 only or is moved entirely to supplement.

## Label Signoff Rows

| cohort | class_id | phase18_label_en_display_v0 | phase18_decision_v0 | phase18_rationale |
| --- | --- | --- | --- | --- |
| CHARLS | CHARLS_C1 | broad intermediate-burden profile [signoff] | auto_renamed_conservative | Generic severity-aligned label replaced with domain-neutral burden-profile label. |
| CHARLS | CHARLS_C2 | broad elevated-burden profile [signoff] | auto_renamed_conservative | Generic severity-aligned label replaced with domain-neutral burden-profile label. |
| ELSA | ELSA_C3 | broad elevated-burden profile [signoff] | auto_renamed_conservative | Generic severity-aligned label replaced with domain-neutral burden-profile label. |
| ELSA | ELSA_C5 | functional-dominant high-burden [caveat] | locked_with_caveat_auto_v0 | Keep baseline domain-profile name; avoid mortality-driven interpretation and report sensitivity caveat. |
| HRS | HRS_C3 | elevated-burden severity-aligned [caveat] | locked_with_caveat_auto_v0 | Keep baseline domain-profile name; avoid mortality-driven interpretation and report sensitivity caveat. |
| HRS | HRS_C4 | affective-dominant elevated-burden [caveat] | locked_with_caveat_auto_v0 | Keep baseline domain-profile name; avoid mortality-driven interpretation and report sensitivity caveat. |
| HRS | HRS_C5 | functional-dominant high-burden [caveat] | locked_with_caveat_auto_v0 | Keep baseline domain-profile name; avoid mortality-driven interpretation and report sensitivity caveat. |
| KLoSA | KLoSA_C2 | cardiometabolic-dominant intermediate-burden [caveat] | locked_with_caveat_auto_v0 | Keep baseline domain-profile name; avoid mortality-driven interpretation and report sensitivity caveat. |
| SHARE | SHARE_C4 | elevated-burden with spared functional [caveat] | locked_with_caveat_auto_v0 | Keep baseline domain-profile name; avoid mortality-driven interpretation and report sensitivity caveat. |
| SHARE | SHARE_C5 | functional/cognitive-dominant high-burden [caveat] | locked_with_caveat_auto_v0 | Keep baseline domain-profile name; avoid mortality-driven interpretation and report sensitivity caveat. |
| LASI | LASI_C1 | intermediate-burden with spared cardiometabolic [baseline-only] | baseline_only_hold | LASI lacks follow-up validation in the current cleaned CSV pass. |
| LASI | LASI_C2 | cardiometabolic-dominant intermediate-burden [baseline-only] | baseline_only_hold | LASI lacks follow-up validation in the current cleaned CSV pass. |
| LASI | LASI_C3 | cardiometabolic-dominant elevated-burden [baseline-only] | baseline_only_hold | LASI lacks follow-up validation in the current cleaned CSV pass. |

## Reference Formatting Queue

| source_id | title | url | collision_risk |
| --- | --- | --- | --- |
| N1 | Interrelated Multidimensional Trajectories of Aging: Evidence From the Health and Retirement Study | https://pubmed.ncbi.nlm.nih.gov/36479143/ | adjacent_not_direct |
| N2 | Sex Differences in Intrinsic Capacity Domains and Their Associations With Adverse Health Outcomes Across Four Aging Cohorts | https://pmc.ncbi.nlm.nih.gov/articles/PMC12317657/ | moderate_adjacent |
| N3 | Trajectories of intrinsic capacity and their associations with adverse outcomes | https://pmc.ncbi.nlm.nih.gov/articles/PMC11625515/ | moderate_adjacent |
| N4 | Symptom clusters, disability and health-related quality of life in community-dwelling older adults | https://pmc.ncbi.nlm.nih.gov/articles/PMC12434884/ | moderate_adjacent |
| N5 | Trajectories of Depressive Symptoms, Memory Function, and Mobility Before Death | https://pmc.ncbi.nlm.nih.gov/articles/PMC11356518/ | adjacent_not_direct |
| N6 | Measurement of Healthy Ageing | https://pmc.ncbi.nlm.nih.gov/articles/PMC11298082/ | background |
| N7 | Lifecourse systemic inflammation and healthy ageing: a five-cohort study | https://www.medrxiv.org/content/10.1101/2025.10.22.25338202v1 | background_adjacent |
