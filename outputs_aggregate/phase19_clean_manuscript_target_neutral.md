# Multidomain Aging Endotypes Among Older Women Across Seven International Aging Cohorts

## Abstract

### Background

Aging phenotypes among older women are often represented by single severity or frailty scales, although functional, cognitive, affective, and cardiometabolic burdens may combine in clinically distinct patterns. We evaluated whether multidomain endotype profiles can summarize this heterogeneity across international aging cohort systems.

### Methods

We analyzed cleaned data from seven aging cohorts: CHARLS, ELSA, HRS, KLoSA, LASI, MHAS, and SHARE. Women aged 50 years or older were screened at cohort-specific baseline. Four domain scores were constructed for functional, cognitive, affective, and cardiometabolic/chronic disease burden, with higher scores indicating worse burden. Cohort-specific Gaussian mixture models were used to derive multidomain endotype profiles. Functional deterioration was treated as the primary validation endpoint. Mortality was analyzed as a secondary endpoint because proportional-hazards and time-stability diagnostics flagged selected class terms. Endotype models were compared with severity-tertile and continuous four-domain score comparators.

### Results

The baseline screen included 79,938 women aged 50 years or older. The selected endotype construction contributed 56,491 strict-primary assignments and 40,087 bridge-sensitivity assignments. The final Phase 18 auto-v0 dictionary contained 29 cohort-specific classes. Functional deterioration validation included 6 cohort rows, 50,084 participants, and 12,336 events. Mortality validation included 6 cohort rows, 54,362 participants, and 12,649 deaths. Endotype profiles showed interpretable multidomain heterogeneity, but continuous four-domain score models generally outperformed endotype-only models.

### Conclusions

Women-only multidomain endotypes can summarize clinically interpretable aging heterogeneity across international cohorts. The current evidence supports an interpretability and heterogeneity-mapping contribution rather than a universal prediction-superiority claim.

## Introduction

Frailty indices, intrinsic-capacity frameworks, and single-domain functional transitions are useful for studying aging, but they can compress heterogeneous aging processes into a single severity continuum. This compression is a particular limitation when studying older women, for whom functional, cognitive, affective, and cardiometabolic burdens may cluster in clinically different ways even when overall burden appears similar.

Recent studies have examined multidimensional aging trajectories, multimodal symptom clusters, and predeath trajectories in older-adult cohorts [1] [2] [3]. These studies reduce the room for broad novelty claims about multidomain aging analysis in general. The present study therefore uses a narrower claim: a women-focused, seven-cohort analysis of multidomain aging endotypes with explicit comparator and sensitivity guardrails.

## Methods

### Study Design And Cohorts

We used cleaned cohort CSV files from CHARLS, ELSA, HRS, KLoSA, LASI, MHAS, and SHARE. The primary population was women aged 50 years or older at the cohort-specific baseline or selected analysis wave. Source data were treated as read-only, and all derived artifacts were written to the project `outputs/` and `manuscript/` directories.

### Domain Construction

Four domain scores were constructed: functional burden, cognitive burden, affective burden, and cardiometabolic/chronic disease burden. Scores were oriented so that higher values represented worse burden. Domain construction used the cleaned harmonized variables available in each cohort, with bridge rules retained for KLoSA and SHARE where the strict functional-domain definition was not fully available. LASI contributed baseline endotype profiles but remains excluded from follow-up validation in the current cleaned CSV pass.

### Endotype Modeling

Cohort-specific Gaussian mixture models were fit to the multidomain scores. Model selection used convergence, Bayesian information criterion, minimum class-size rules, and clinical interpretability. The selected classes were labeled using conservative domain-profile language. Labels with mortality drift, covariate-sensitivity flags, or baseline-only status retained explicit caveat or hold markers until human signoff.

### Outcome Validation

Functional deterioration was the primary validation endpoint. Chronic disease progression and all-cause mortality were secondary validation endpoints. Mortality estimates were interpreted cautiously because proportional-hazards diagnostics and early/late piecewise sensitivity flagged selected cohort-class terms. Comparator models included severity tertiles, continuous severity scores, outcome-matched domain scores, continuous four-domain score models, and diagnostic endotype-plus-domain models.

## Results

### Cohort Readiness

Across the seven cleaned cohorts, the women aged 50 years or older baseline screen included 79,938 participants. Strict-primary endotype construction contributed 56,491 selected assignments. KLoSA and SHARE contributed 40,087 bridge-sensitivity assignments. LASI remained baseline-profile only for follow-up validation in this cleaned CSV pass.

### Endotype Profile Structure

The selected models produced 29 cohort-specific classes. Phase 18 auto-v0 labeling accepted 16 labels from the Phase 16 dictionary, retained 7 labels with explicit sensitivity caveats, conservatively renamed 3 generic severity-aligned labels, and kept 3 LASI labels as baseline-only profiles. These labels are appropriate for collaborator review but not for submission without final signoff.

### Functional Deterioration

Functional deterioration validation included 6 cohort rows, 50,084 participants, and 12,336 events. The endotype-versus-severity pattern was mixed across cohorts. Continuous four-domain score models generally fit better than endotype-only models for functional deterioration, supporting a heterogeneity-mapping interpretation rather than a prediction-superiority claim.

### Mortality

Mortality validation included 6 cohort rows, 54,362 participants, and 12,649 deaths. Mortality remained secondary because selected class terms showed proportional-hazards, piecewise, or covariate-sensitivity concerns. Mortality-related labels should therefore remain baseline domain-profile labels rather than outcome-driven phenotype names.

### Comparator Guardrail

Across tested endpoint-cohort rows, endotype-only models did not consistently outperform continuous four-domain score models. The defensible manuscript claim is that multidomain endotypes provide an interpretable clinical summary of aging heterogeneity among older women, with endpoint-specific outcome relevance, not that class membership is universally stronger than continuous domain scores.

## Discussion

This women-only analysis identified interpretable multidomain aging profiles across several international cohort systems. Several profiles were not reducible to a single low-to-high severity gradient and instead showed functional, cardiometabolic, affective, cognitive, or spared-domain structure. This supports a descriptive and interpretive contribution: multidomain endotypes can summarize clinically meaningful heterogeneity among older women.

The results should be interpreted with an explicit comparator guardrail. Continuous four-domain score models generally outperformed endotype-only models, indicating that endotype membership should be viewed as a compact clinical summary rather than a universally stronger risk model. This distinction should remain central in the abstract, results, and discussion.

The study has several limitations. First, this analysis used cleaned CSV variables rather than a full raw-file harmonization pass. Second, cohort differences in measurement may influence the shape and interpretation of domain scores. Third, KLoSA and SHARE used bridge definitions for selected domains. Fourth, LASI lacks follow-up validation in the current cleaned CSV pass. Fifth, expanded-core covariate coverage remains incomplete in several cohorts. Finally, selected mortality class terms showed time-drift or proportional-hazards concerns, so mortality should remain secondary unless additional sensitivity analyses support stronger claims.

## Pre-Submission Blockers

This clean draft remains blocked by 13 label signoffs. The target journal has not been selected, so author guidelines, abstract format, word limits, reporting checklist requirements, and reference style still require live checking. The Figure 1 display decision also remains open: main validation only versus seven-cohort sensitivity display. The LASI display decision must remain baseline-profile only unless follow-up data are added.

## References

1. Quinones AR; Nagel CL; Botoseneanu A; Newsom JT; Dorr DA; Kaye J; et al. Multidimensional trajectories of multimorbidity, functional status, cognitive performance, and depressive symptoms among diverse groups of older adults. Journal of Multimorbidity and Comorbidity. 2022;12:26335565221143012. doi:10.1177/26335565221143012.
2. Zhang Q; Liu P; Xu X; Liao H; Yang Y; Xiong Y; et al. Longitudinal associations between multimodal symptom clusters and functional disability in older adults: a comparative cohort analysis using SHARE, ELSA, and KLoSA. Scientific Reports. 2025;15(1):40802. doi:10.1038/s41598-025-24623-2.
3. Jiao J; Guo J; Shen J; Liu S; Zhang L; Sun D; et al. Long-term trajectories of memory, depression, and mobility independence before death: a multi-cohort study. Translational Psychiatry. 2026;16(1). doi:10.1038/s41398-026-03997-5.
