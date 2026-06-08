# Panel Final Selection

| Panel | Selected option | Candidate ID | Candidate level | Selected output | Final selection reason | Rejected alternatives | Known tradeoff |
|---|---|---|---|---|---|---|---|
| Fig1 | tierheatmap | native_enhanced_alluvial_tierheatmap | native_workflow | outputs/figure1_enhanced_alluvial_tierheatmap_phase50.svg | Makes denominator loss, LFO availability, evidence tier and tier membership visible in one figure. | Card-style claim boundary panel | Uses ASCII plus signs because Arial lacks a checkmark glyph in the WSL render device. |
| Fig1 | upset | native_enhanced_alluvial_upset | native_workflow | outputs/figure1_enhanced_alluvial_upset_phase50.svg | Provides a formal UpSet representation of tier intersections. | Card-style claim boundary panel | More abstract than heatmap; likely better as supplement or optional main variant. |
| Fig2 | enhanced | native_complexheatmap_radial_decision | native_workflow | outputs/figure2_enhanced_complexheatmap_radial_decision_phase49.svg | Adds a pure ComplexHeatmap method-agreement heatmap, radial covariance guardrail, and direct stability decision quadrant. | Previous normalized ternary evidence-balance panel | Four panels are information-rich and need a clear legend. |
| Fig3 | enhanced | native_clinical_forest_quadrant | native_workflow | outputs/figure3_enhanced_clinical_forest_quadrant_phase49.svg | Presents clinical effect, absolute risk, event burden and lack of Delta AUC gain together. | Phase48 forest plus ellipse | Compact table omits CI text to preserve readability. |
