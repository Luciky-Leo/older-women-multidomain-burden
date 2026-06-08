# Multidomain Aging Endotypes Among Older Women Across Seven International Aging Cohorts

Version note: Phase 18 auto-v0 draft generated on 2026-06-01. Labels with caveat/signoff/hold markers require human approval before submission.

## Abstract

### Background

Aging in older women is often summarized using single frailty or functional measures, although functional, cognitive, affective, and cardiometabolic burdens may cluster in distinct patterns.

### Methods

We analyzed cleaned data from seven international aging cohorts. Women aged 50 years or older were used to construct cohort-specific multidomain endotype profiles from functional, cognitive, affective, and cardiometabolic/chronic disease domains. Associations with functional deterioration and all-cause mortality were evaluated within cohorts and benchmarked against severity-tertile and continuous four-domain score comparators.

### Results

The eligible baseline screen included 79,938 women. Endotype modeling yielded 96,578 selected assignments, including 56,491 strict-primary and 40,087 bridge-sensitivity assignments. Phase 18 auto-v0 labeling retained 29 cohort-specific classes; 13 labels still require human signoff or explicit caveat handling. Functional deterioration validation included 6 cohorts, 50,084 participants, and 12,336 events. Mortality validation included 6 cohorts, 54,362 participants, and 12,649 deaths. Endotype profiles showed interpretable multidomain heterogeneity, but continuous four-domain score models generally outperformed endotype-only models.

### Conclusions

Women-only multidomain endotypes can summarize clinically interpretable aging heterogeneity across international cohorts, but the current evidence supports an interpretability and heterogeneity-mapping claim rather than universal prediction superiority.

## Introduction

Population aging is commonly summarized using frailty indices, intrinsic-capacity measures, or single-domain functional transitions. These approaches are useful, but they can compress heterogeneous aging processes into a single severity scale. For older women, this is a limitation because functional, cognitive, affective, and cardiometabolic burdens may combine in clinically different ways even when overall burden appears similar.

Recent studies have examined multidimensional aging trajectories, intrinsic capacity, symptom clusters, and predeath trajectories. The current study is therefore not positioned as the first multidimensional aging analysis or as a new frailty index. Its narrower contribution is a women-focused multidomain endotype analysis across seven international aging cohorts with explicit comparator and sensitivity guardrails.

## Methods

The analysis used cleaned cohort CSV files for CHARLS, ELSA, HRS, KLoSA, LASI, MHAS, and SHARE. The primary population was women aged 50 years or older. Domain scores were constructed so that higher values represented worse burden. Cohort-specific Gaussian mixture models were used for first-pass endotype assignment, with model selection constrained by convergence and minimum class-size rules. Functional deterioration was treated as the primary validation endpoint. Mortality was treated as secondary because proportional-hazards diagnostics, piecewise sensitivity, and covariate-sensitivity screens flagged selected class terms.

## Results

Across the seven cleaned cohorts, the baseline screen included 79,938 women aged 50 years or older. Strict-primary endotype construction contributed 56,491 selected assignments, while KLoSA and SHARE contributed 40,087 bridge-sensitivity assignments. LASI remained baseline-profile only because follow-up validation is unavailable in the current cleaned CSV pass.

The selected models produced 29 cohort-specific classes. Phase 18 auto-v0 labeling accepted 16 labels from the Phase 16 dictionary, retained 7 labels with explicit sensitivity caveats, conservatively renamed 3 generic severity-aligned labels, and kept 3 LASI labels as baseline-only profiles. Mortality-drift and covariate-sensitivity-flagged labels were retained as baseline domain-profile names with explicit caveats.

Functional deterioration validation was available in 6 cohorts, including 50,084 participants and 12,336 events. The endotype-versus-severity pattern was mixed across cohorts, while continuous four-domain score models were favored across the tested functional comparisons.

Mortality validation was available in 6 cohorts, including 54,362 participants and 12,649 deaths. Mortality results should remain secondary because selected class terms showed proportional-hazards, piecewise, or covariate-sensitivity concerns.

Figure 1 main validation file: `outputs/figures/phase18_figure1_main_validation_v0.png`. Seven-cohort sensitivity file: `outputs/figures/phase18_figure1_seven_cohort_sensitivity_v0.png`.

## Discussion

This women-only analysis identified interpretable multidomain aging profiles across several international cohort systems. The profiles were not reducible to a single low-to-high severity gradient; instead, several classes showed functional, cardiometabolic, affective, or spared-domain structure. This supports a descriptive and interpretive contribution: multidomain endotypes can summarize clinically meaningful heterogeneity among older women.

The results do not support an unrestricted prediction-superiority claim. Continuous four-domain score models generally outperformed endotype-only models, indicating that class membership should be viewed as a compact clinical summary rather than a universally stronger risk model. This distinction should remain central in the abstract, results, and discussion.

The study has several limitations: reliance on cleaned CSV variables rather than a full raw-file harmonization pass, cohort differences in measurement, bridge definitions for KLoSA and SHARE, missing LASI follow-up validation, incomplete expanded-core covariate coverage, and mortality time-drift concerns in selected classes. The Phase 18 auto-v0 labels also require human signoff before final submission.

## References To Format

- Interrelated Multidimensional Trajectories of Aging: Evidence From the Health and Retirement Study. https://pubmed.ncbi.nlm.nih.gov/36479143/
- Sex Differences in Intrinsic Capacity Domains and Their Associations With Adverse Health Outcomes Across Four Aging Cohorts. https://pmc.ncbi.nlm.nih.gov/articles/PMC12317657/
- Trajectories of intrinsic capacity and their associations with adverse outcomes. https://pmc.ncbi.nlm.nih.gov/articles/PMC11625515/
- Symptom clusters, disability and health-related quality of life in community-dwelling older adults. https://pmc.ncbi.nlm.nih.gov/articles/PMC12434884/
- Trajectories of Depressive Symptoms, Memory Function, and Mobility Before Death. https://pmc.ncbi.nlm.nih.gov/articles/PMC11356518/
- Measurement of Healthy Ageing. https://pmc.ncbi.nlm.nih.gov/articles/PMC11298082/
- Lifecourse systemic inflammation and healthy ageing: a five-cohort study. https://www.medrxiv.org/content/10.1101/2025.10.22.25338202v1
