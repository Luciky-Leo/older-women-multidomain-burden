# Introduction Draft

Population aging is commonly summarized using frailty indices, intrinsic-capacity measures, or single-domain functional transitions. These approaches are useful, but they can compress heterogeneous aging processes into a single severity scale. For older women, this is a particular limitation because functional, cognitive, affective, and cardiometabolic burdens may combine in clinically different ways even when overall burden appears similar.

Recent work has examined multidimensional aging trajectories, intrinsic capacity, symptom clusters, and predeath changes in function, memory, and mood [N1-N6]. This literature makes the broad space crowded, so the present manuscript should not be framed as the first study of multidimensional aging or as a new frailty index. The more defensible gap is narrower: few studies have focused on women-only multidomain aging endotypes across harmonized international aging cohorts while carrying explicit comparator and sensitivity guardrails.

We therefore used cleaned data from seven international aging cohorts to construct cohort-specific women-only multidomain profiles spanning functional, cognitive, affective, and cardiometabolic/chronic disease domains. We evaluated whether these profiles were clinically interpretable, whether they were associated with functional deterioration and all-cause mortality, and whether their evidence remained robust when compared with simpler severity tertiles and continuous four-domain score models.

## Sources for background positioning

- [N1] Interrelated Multidimensional Trajectories of Aging: Evidence From the Health and Retirement Study. https://pubmed.ncbi.nlm.nih.gov/36479143/
- [N2] Sex Differences in Intrinsic Capacity Domains and Their Associations With Adverse Health Outcomes Across Four Aging Cohorts. https://pmc.ncbi.nlm.nih.gov/articles/PMC12317657/
- [N3] Trajectories of intrinsic capacity and their associations with adverse outcomes. https://pmc.ncbi.nlm.nih.gov/articles/PMC11625515/
- [N4] Symptom clusters, disability and health-related quality of life in community-dwelling older adults. https://pmc.ncbi.nlm.nih.gov/articles/PMC12434884/
- [N5] Trajectories of Depressive Symptoms, Memory Function, and Mobility Before Death. https://pmc.ncbi.nlm.nih.gov/articles/PMC11356518/
- [N6] Measurement of Healthy Ageing. https://pmc.ncbi.nlm.nih.gov/articles/PMC11298082/
- [N7] Lifecourse systemic inflammation and healthy ageing: a five-cohort study. https://www.medrxiv.org/content/10.1101/2025.10.22.25338202v1

# Discussion Draft

## Principal Findings

In this women-only analysis of seven cleaned aging cohorts, the eligible baseline screen included 79,938 women aged 50 years or older. Cohort-specific endotype modeling yielded 96,578 selected assignments overall, including 56,491 strict-primary assignments and 40,087 bridge-sensitivity assignments.

The selected models produced 29 cohort-specific classes. Phase 16 marked 16 labels as locked for draft use, 10 as requiring manual review, and 3 LASI labels as baseline-only holds. This label status is important: review-required labels should remain visibly marked until clinical review is complete.

Functional deterioration validation was available in 6 cohorts, with 50,084 participants and 12,336 events. Mortality validation was available in 6 cohorts, with 54,362 participants and 12,649 deaths.

## Interpretation

The endotype profiles show multidomain heterogeneity that is not fully captured by a single severity gradient. Some classes were dominated by functional burden, others by cardiometabolic/chronic disease burden, affective symptoms, or relative sparing of specific domains. This supports the manuscript's core descriptive claim: among older women, clinically interpretable multidomain aging patterns can be constructed across several cohort systems.

The prediction claim should be more restrained. Across the tested endpoint-cohort rows, continuous four-domain score models generally outperformed endotype-only models. The manuscript should therefore state that endotypes improve interpretability and profile-level summarization, not that class membership is a universally superior standalone predictor.

## Relation to Existing Work

The findings are adjacent to prior studies of multidimensional aging trajectories, intrinsic capacity, symptom clusters, and predeath trajectories [N1-N6]. The distinction is not that multidomain aging has been ignored, but that this analysis uses a women-focused endotype framing across seven international aging cohorts and explicitly benchmarks the classes against severity tertiles and four-domain continuous scores.

## Strengths

Strengths include the women-only analytic frame, harmonized four-domain construction, cohort-specific profile modeling rather than forced pooling, functional and mortality validation, proportional-hazards and piecewise mortality sensitivity checks, covariate-sensitivity screens, and explicit display rules for bridge-sensitivity and baseline-only cohorts.

## Limitations

Limitations include reliance on cleaned CSV variables rather than a full raw-file harmonization pass, cohort differences in domain measurement, bridge definitions for KLoSA and SHARE, missing LASI follow-up validation in the current pass, incomplete expanded-core covariate coverage in several cohorts, and mortality proportional-hazards/time-drift concerns for selected class terms.

## Implications

The most defensible next step is not to overstate prediction superiority, but to refine the clinical naming and cross-cohort alignment of the profiles. If manual label review confirms the current domain interpretations, the study can support a manuscript centered on women-specific multidomain aging heterogeneity and endpoint-specific validation.
