# Results Skeleton

This is a manuscript-facing draft. It is intentionally conservative and should be edited after manual label review.

## Study Sample And Cohort Readiness

Across the seven cleaned aging cohorts, the Phase 1 earliest-baseline screen identified 79,938 women aged 50 years or older. The strict-primary analysis included 5 cohorts and 56,491 participants with complete four-domain endotype inputs. Two additional bridge-sensitivity cohorts contributed 40,087 selected endotype assignments, giving 96,578 selected assignments across strict and sensitivity analyses.

Functional deterioration validation was available in 6 cohorts, and mortality validation was available in 6 cohorts. LASI remained baseline-profile only in the current cleaned CSV pass.

Draft table callout: Table 1.

## Cohort-Specific Endotype Structure

The selected cohort-specific solutions yielded 29 classes. Label confidence distribution was high: 12, low: 3, moderate: 9, provisional: 5. Provisional labels were assigned to HRS_C3, HRS_C4, HRS_C5, KLoSA_C2, SHARE_C5, primarily because mortality HRs varied across early and late follow-up periods.

The dominant patterns were not restricted to a single low-to-high severity gradient. Several classes showed domain-specific elevations, including cardiometabolic-dominant, functional-dominant, affective-dominant, and spared-cardiometabolic profiles. These labels should be finalized by manual review before being used as definitive clinical names.

Draft table/figure callout: Table 2 and Figure 1A.

## Functional Deterioration

Functional deterioration models included 6 cohorts, 50,084 participants, and 12,336 events. Against severity tertiles, the endotype model comparison pattern was endotype_favored: 3, severity_tertile_favored: 3.

However, four-domain continuous-score models fit better than endotype-only models in all functional deterioration comparisons, indicating that class membership should not be presented as a universally superior standalone prediction model.

Draft table/figure callout: Table 3 and Figure 1B-C.

## Chronic Progression

Chronic progression models included 6 cohorts, 51,006 participants, and 22,423 events. Against severity tertiles, the comparison pattern was endotype_favored: 3, severity_tertile_favored: 1, similar_by_aic: 2.

As with functional deterioration, the four-domain continuous-score comparator outperformed the endotype-only model across chronic progression comparisons. Chronic progression is therefore best used as secondary evidence that the identified profiles carry clinically interpretable risk differences.

## Mortality

Mortality models included 6 cohorts, 54,362 participants, and 12,649 deaths. Against severity tertiles, the mortality comparison pattern was endotype_favored: 2, severity_tertile_favored: 4.

Mortality estimates should remain secondary in the current manuscript draft. The PH screen flagged selected cohorts, and piecewise sensitivity flagged KLoSA C2, SHARE C5, and HRS C3-C5 as time-drift terms.

## Comparator Guardrail

Across endpoint-cohort comparisons, the four-domain score result pattern was four_domain_scores_favored: 6 for functional deterioration and similarly favored four-domain scores for chronic progression and mortality. This should be stated directly: the manuscript claim is not that endotype classes beat their source continuous measures as prediction variables. The defensible claim is that the classes provide compact, interpretable, cohort-specific multidomain profiles with endpoint-specific validation signals.

## Results Paragraph Order

1. Cohort readiness and selected denominators.
2. Endotype solution sizes and profile diversity.
3. Functional deterioration as the primary validation endpoint.
4. Chronic progression as secondary validation.
5. Mortality as secondary validation with PH/piecewise sensitivity caveat.
6. Comparator guardrail and final interpretation.

## Phase 15 Integrated Sensitivity Update

### Covariate Sensitivity

Phase 14 added 12 functional-deterioration and 12 mortality covariate-sensitivity comparison rows. Minimal-core functional sensitivity was estimable in 6 cohorts (CHARLS, ELSA, HRS, KLoSA, MHAS, SHARE), and minimal-core mortality sensitivity was estimable in 6 cohorts (CHARLS, ELSA, HRS, KLoSA, MHAS, SHARE). LASI remains baseline-profile only in the current cleaned CSV pass.

Effect-stability screening flagged 7 class labels for manual review before final lock: ELSA_C5, HRS_C3, HRS_C4, HRS_C5, KLoSA_C2, SHARE_C4, SHARE_C5. These flags should be described as robustness caveats, not as replacement primary estimates.

Draft table callout: Supplementary Table S1-S2.

### Label Lock Queue

After incorporating Phase 14 stability flags, the Phase 15 label queue contains 16 labels ready for manual lock, 10 labels requiring manual review, and 3 baseline-only hold labels.

Classes blocked from automatic locking are those with generic severity-aligned labels, mortality time-drift, Phase 14 covariate-sensitivity instability, bridge-sensitivity display caveats, or missing follow-up validation.

### Display Policy

| cohort | phase15_display_recommendation |
| --- | --- |
| CHARLS | main_results |
| ELSA | main_results |
| HRS | main_results |
| MHAS | main_results |
| KLoSA | sensitivity_or_supplement_default |
| SHARE | sensitivity_or_supplement_default |
| LASI | baseline_profile_table_only |

Default manuscript display should keep CHARLS, ELSA, HRS, and MHAS in the main validation panels. KLoSA and SHARE should default to sensitivity or supplement display because they use bridge-sensitivity definitions; they may appear in the main figure only with explicit bridge or wave-adjusted denominator footnotes. LASI should remain a baseline-profile table row until longitudinal follow-up validation is added.

### Novelty Refresh

The 2026-06-01 targeted refresh did not identify a direct same-topic collision for a women-only, seven-cohort, four-domain endotype study with functional and mortality validation. Adjacent work on multidimensional aging trajectories, intrinsic capacity, symptom clusters, and predeath trajectories means the manuscript should keep novelty claims narrow and comparator-aware.

Draft table callout: Supplementary Table S3 or a short novelty-positioning appendix.

## Updated Results Paragraph Order

1. Cohort readiness and selected denominators.
2. Endotype solution sizes and profile diversity.
3. Functional deterioration as the primary validation endpoint.
4. Chronic progression as secondary validation.
5. Mortality as secondary validation with PH, piecewise, and covariate-sensitivity caveats.
6. Comparator guardrail and final interpretation.
7. Novelty-positioning statement for Discussion rather than Results.
