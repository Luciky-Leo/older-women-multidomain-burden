# Phase49 Visual Reviewer Audit After Optimization

Date: 2026-06-05

## Pass Checks

- Fig1-3 were regenerated from project CSVs through reproducible Python/R scripts; no simulated data were introduced.
- Line weights and endpoint markers were increased across the alluvial, Fig1B tier-membership heatmap/UpSet variants, raincloud, pure ComplexHeatmap heatmap, radial lollipop, decision quadrant, forest plot, and quadrant scatter.
- Fig1 node markers were converted to rounded boxes, improving the alluvial smoothness without changing denominators; Fig1B is now available as a tier-membership heatmap default and an UpSet tier-intersection alternative.
- Fig2B uses R ComplexHeatmap as a pure method-agreement heatmap, with short method-family headers, a row evidence-tier strip, a boxed selected GMM reference column, and dashed low-agreement cells; Fig2C uses radial lollipop; Fig2D now uses a direct stability decision quadrant instead of the prior normalized ternary display.
- Fig3 table/scatter collision was reduced by widening the table slot and moving the y-axis definition inside the scatter panel as a short label.
- PERSIST source-code-first validation remains pass after the updated documentation is regenerated.

## Remaining Reviewer-Level Caveats

- Fig1A is still a row-aligned alluvial rather than a fully crossed Sankey. This is acceptable for readability, but the legend/caption should call it an alluvial-style cohort flow rather than overclaiming a formal Sankey if strict terminology matters. Fig1B heatmap is the clearer main-text option; UpSet is a stronger formal set-intersection alternative if space/caption length allows.
- Fig2 is information-rich. The four-panel structure is visually stronger, but the figure legend must explicitly define all four evidence chains, including Fig2B's GMM/Cluster/Score headers and low-agreement dashed boxes.
- Fig2D thresholds are reviewer-facing guardrails, not formal decision rules. The caption should define bootstrap p10 ARI, log10 covariance condition, point-size encoding, and the algorithm-agreement outer ring.
- Fig3 compact table reports point estimates for space. The forest plot and scatter encode interval uncertainty, but the table itself should not be described as a full model-results table.
- R PDF output uses a Helvetica-family fallback because the WSL R PostScript device does not register Arial; SVG text remains editable and can be converted to Arial in vector editing or through a journal production workflow.

## Recommendation

Use the optimized Phase49 SVGs as the current editable figure masters. Before final manuscript insertion, adjust figure legends to match the more information-dense panels and avoid implying that the quadrant shading is inferential.
