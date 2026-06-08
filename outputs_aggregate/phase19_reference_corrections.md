# Phase 19 Reference Corrections

Generated: 2026-06-01.

Phase 15 used a novelty-refresh source log, not a formal reference list. Phase 19 checked the source identifiers before building the clean manuscript package and found that several Phase 15 PMCID rows were wrong or unsuitable for direct citation.

## Verified References Allowed In Clean Draft

| queue_id | phase15_source_id | title | journal | year | doi | pmid | pmcid | url |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R1 | N1 | Multidimensional trajectories of multimorbidity, functional status, cognitive performance, and depressive symptoms among diverse groups of older adults. | Journal of Multimorbidity and Comorbidity | 2022 | 10.1177/26335565221143012 | 36479143 | PMC9720836 | https://pubmed.ncbi.nlm.nih.gov/36479143/ |
| R2 | N4_corrected | Longitudinal associations between multimodal symptom clusters and functional disability in older adults: a comparative cohort analysis using SHARE, ELSA, and KLoSA. | Scientific Reports | 2025 | 10.1038/s41598-025-24623-2 | 41258422 | PMC12630969 | https://pubmed.ncbi.nlm.nih.gov/41258422/ |
| R3 | N5_corrected | Long-term trajectories of memory, depression, and mobility independence before death: a multi-cohort study. | Translational Psychiatry | 2026 | 10.1038/s41398-026-03997-5 | 41916958 | PMC13039425 | https://pubmed.ncbi.nlm.nih.gov/41916958/ |

## Rows Held Out Of The Clean Draft

| queue_id | phase15_source_id | verification_status | url | phase19_action | notes |
| --- | --- | --- | --- | --- | --- |
| N4_old_hold | N4 | old_phase15_url_replaced_do_not_cite | https://pmc.ncbi.nlm.nih.gov/articles/PMC12434884/ | Do not cite until a correct PMID/DOI/PMCID is verified. | The old Phase 15 N4 PMCID/URL should not be cited. Use R2 after final author approval. |
| N5_old_hold | N5 | old_phase15_url_replaced_do_not_cite | https://pmc.ncbi.nlm.nih.gov/articles/PMC11356518/ | Do not cite until a correct PMID/DOI/PMCID is verified. | The old Phase 15 N5 PMCID/URL resolved to an unrelated article during Phase 19 checking. Use R3 after final author approval. |
| N2_hold | N2 | old_phase15_url_unrelated_do_not_cite | https://pmc.ncbi.nlm.nih.gov/articles/PMC12317657/ | Do not cite until a correct PMID/DOI/PMCID is verified. | The PMCID checked during Phase 19 resolved to an unrelated article. Replace before citing. |
| N3_hold | N3 | old_phase15_url_unrelated_do_not_cite | https://pmc.ncbi.nlm.nih.gov/articles/PMC11625515/ | Do not cite until a correct PMID/DOI/PMCID is verified. | The PMCID checked during Phase 19 resolved to an unrelated article. Replace before citing. |
| N6_hold | N6 | old_phase15_url_unrelated_do_not_cite | https://pmc.ncbi.nlm.nih.gov/articles/PMC11298082/ | Do not cite until a correct PMID/DOI/PMCID is verified. | The PMCID checked during Phase 19 resolved to an unrelated article. Replace before citing. |
| N7_optional | N7 | preprint_optional_not_core | https://www.medrxiv.org/content/10.1101/2025.10.22.25338202v1 | Hold out of clean manuscript unless target journal permits and authors decide it is needed. | Do not use as a core novelty comparator unless the target journal permits preprint citations and the record is rechecked. |

## Practical Rule

Do not copy the Phase 15 `References To Format` list into a submission draft. Use `manuscript/references_verified_v0.md` and `outputs/phase19_verified_reference_queue.csv` until a fresh target-journal reference check is completed.
