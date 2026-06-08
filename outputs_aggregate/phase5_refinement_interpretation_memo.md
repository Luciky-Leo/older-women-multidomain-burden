# Phase 5 Refinement Interpretation Memo

## Purpose

This memo interprets the Phase 5 outcome-validation screens after adding baseline domain-score comparators.

The key question is not only whether endotype classes beat severity tertiles. The stricter question is whether endotype classes add information beyond the four baseline domain scores from which they were derived.

## Main Finding

The current evidence does not support a strong prediction claim that endotype classes universally outperform simpler score-based models.

For functional deterioration, the age-adjusted four-domain continuous-score model has lower AIC and higher AUC than the endotype-only model in every cohort with follow-up:

- KLoSA
- SHARE
- CHARLS
- ELSA
- HRS
- MHAS

This means the manuscript should not frame baseline endotype class as the best standalone prediction tool.

## More Nuanced Signal

The endotype classes still have value as an interpretable heterogeneity map.

For functional deterioration, adding endotype class on top of the four baseline domain scores improved AIC in:

- SHARE
- CHARLS
- ELSA
- HRS

The improvement was borderline or absent in:

- KLoSA
- MHAS

For chronic progression, adding endotype class on top of the four domain scores improved AIC in:

- SHARE
- ELSA
- HRS

It did not clearly improve AIC in:

- KLoSA
- CHARLS
- MHAS

These are overadjustment-style diagnostics because endotypes are derived from the same domain scores. They should be described cautiously as evidence that pattern membership may retain some information beyond continuous score levels in selected cohorts, not as causal proof.

## Manuscript Positioning

Recommended primary framing:

Multidomain aging endotypes among older women reveal cross-cohort heterogeneity in how functional, cognitive, affective, and cardiometabolic burden cluster. These profiles are clinically interpretable and have outcome relevance, but their predictive advantage over continuous domain-score models is cohort- and endpoint-dependent.

Avoid this framing:

Endotypes are universally superior predictors of functional deterioration, chronic progression, or mortality.

## Analysis Implications

Keep endotype classes as the main descriptive and interpretive phenotype.

Use severity tertiles and four-domain continuous scores as formal comparator models.

Report both:

- endotype-only associations, for clinical interpretability;
- endotype versus severity and four-domain score comparator performance, for rigor.

Do not claim that classes are not severity gradients solely from pairwise domain correlations or profile labels. The outcome-model comparators show that continuous domain scores can outperform class labels for prediction.

## Next Required Work

1. Build a class-profile plus outcome-OR review table to support clinically meaningful class labels.
2. Use the Phase 6 mortality screen and Cox models to add mortality to outcome validation.
3. Check proportional hazards assumptions before manuscript use of mortality HRs.
4. Add model performance plots:
   - AIC delta heatmap across cohorts and endpoints;
   - AUC delta heatmap across cohorts and endpoints;
   - endotype profile plots annotated by functional-deterioration risk.
5. Decide whether longitudinal trajectory modeling is still necessary or whether baseline endotype plus follow-up validation is sufficient for the first paper.

## Mortality Update

After DTA-label confirmation, `radyear`, `radmonth`, and `iwstat` are available mortality candidates in the cleaned CSV files for CHARLS, ELSA, HRS, KLoSA, MHAS, and SHARE. LASI remains unavailable for mortality in the current cleaned CSV pass.

First-pass Cox models reinforce the same boundary as the functional-deterioration models: endotype-only models do not outperform four-domain continuous-score models as standalone predictors, although selected endotype-plus-domain diagnostics show incremental information.
