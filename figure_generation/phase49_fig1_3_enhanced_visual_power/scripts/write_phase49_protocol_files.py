"""Write Phase49 PERSIST-compatible redraw protocol files.

SOURCE_CODE_FIRST records for the enhanced Fig1-Fig3 redraw package.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
REDRAW = ROOT / "figure_redraw" / "phase49_fig1_3_enhanced_visual_power"
OUT = REDRAW / "outputs"


def win(path: str) -> str:
    return path.replace("/", "\\").replace("\\mnt\\e", "E:")


def write_tsv(path: Path, rows: list[list[object]], columns: list[str]) -> None:
    pd.DataFrame(rows, columns=columns).to_csv(path, sep="\t", index=False)


def main() -> None:
    render_py = r"E:\Reserch\Older women\figure_redraw\phase49_fig1_3_enhanced_visual_power\scripts\render_phase49_fig1_fig3_enhanced.py"
    render_r = r"E:\Reserch\Older women\figure_redraw\phase49_fig1_3_enhanced_visual_power\scripts\render_phase49_fig2_complexheatmap_hf147.R"

    candidates_cols = [
        "panel", "option", "panel role", "variant budget", "candidate id", "candidate level",
        "candidate maturity", "hf capsule id", "persist source id", "generic template path",
        "native workflow", "candidate source", "candidate kind", "persist atlas major class",
        "persist atlas subtype", "data fit gate", "data fit notes", "visual fit gate",
        "visual fit notes", "task fit score", "data fit score", "visual grammar score",
        "source-code readiness score", "readability score", "total score", "render decision",
        "runtime", "env", "capsule path", "reference visual", "source script",
        "source code snapshot", "why it fits", "risk",
    ]
    write_tsv(
        REDRAW / "panel_template_candidates.tsv",
        [
            ["Fig1", "tierheatmap", "cohort denominator, attrition flow, and tier membership", "two Fig1B variants", "native_enhanced_alluvial_tierheatmap", "native_workflow", "production_ready", "NA", "NA", "NA", "native alluvial plus tier-membership heatmap workflow", "project native", "native cohort-flow", "flow + membership heatmap", "alluvial attrition + tier membership matrix", "pass", "source, complete-domain, LFO model denominators and role labels available", "pass", "membership heatmap answers reviewer denominator and claim-scope concerns with minimal space", 30, 20, 18, 14, 18, 100, "render_recommended", "Python", "research-py312", "NA", "Phase48 alluvial plus user-requested tier membership heatmap", render_py, render_py, "Directly encodes cohort-level participant loss, analysis eligibility and analysis-tier membership", "Plus sign is used instead of a checkmark for Arial-safe editable output"],
            ["Fig1", "upset", "cohort denominator, attrition flow, and tier intersections", "two Fig1B variants", "native_enhanced_alluvial_upset", "native_workflow", "production_ready", "NA", "NA", "NA", "native alluvial plus UpSet workflow", "project native", "native cohort-flow", "flow + UpSet", "alluvial attrition + UpSet intersections", "pass", "source, complete-domain, LFO model denominators and role labels available", "pass", "UpSet panel precisely shows tier intersections as a Venn alternative", 30, 20, 17, 14, 17, 98, "render_optional", "Python", "research-py312", "NA", "Phase48 alluvial plus user-requested UpSet variant", render_py, render_py, "Directly encodes intersections across construction, strict LFO, sensitivity and baseline-only tiers", "More abstract than the heatmap and needs a clear caption"],
            ["Fig2", "enhanced", "stability evidence plus decision quadrant", "single final render", "native_complexheatmap_radial_decision", "native_workflow", "production_ready", "NA", "NA", "NA", "ComplexHeatmap plus R grid decision workflow", "R-native ComplexHeatmap and decision quadrant", "dashboard", "stability dashboard", "raincloud + ComplexHeatmap + radial lollipop + decision quadrant", "pass", "bootstrap replicates, method ARI, condition number and complete-domain N available", "pass", "adds threshold bands, ComplexHeatmap matrix, radial condition guardrail and direct stability decision quadrant", 30, 20, 17, 14, 18, 99, "render_recommended", "R", "research-r45", "NA", "R-native grid/ComplexHeatmap", render_r, render_r, "Decision quadrant uses original p10 ARI and covariance condition rather than normalized ternary components", "Caption must define quadrant thresholds and point-size encoding"],
            ["Fig3", "enhanced", "clinical impact forest and decision quadrant", "single final render", "native_clinical_forest_quadrant", "native_workflow", "production_ready", "NA", "NA", "NA", "native clinical forest and bivariate decision plot", "project native", "clinical forest", "clinical association", "forest table + risk difference by Delta AUC", "pass", "RR, absolute risks, event counts, risk difference and Delta AUC are available", "pass", "clinical table and quadrant background make the profile-versus-continuous conclusion visible", 30, 20, 15, 14, 18, 97, "render_recommended", "Python", "research-py312", "NA", "Phase48 forest plus reviewer-requested clinical impact enhancement", render_py, render_py, "Shows association strength and lack of AUC gain in one figure", "Compact table uses point estimates; CIs remain encoded in forest/scatter intervals"],
        ],
        candidates_cols,
    )

    variants_cols = [
        "panel", "option", "panel role", "variant budget", "candidate id", "candidate level",
        "candidate maturity", "data fit gate", "visual fit gate", "runtime", "env",
        "rendered", "render script", "intermediate file", "output png", "output pdf/svg",
        "figure layout spec", "figure output spec", "validation status", "reason",
    ]
    write_tsv(
        REDRAW / "panel_render_variants.tsv",
        [
            ["Fig1", "tierheatmap", "cohort denominator, attrition flow, and tier membership", "two Fig1B variants", "native_enhanced_alluvial_tierheatmap", "native_workflow", "production_ready", "pass", "pass", "Python", "research-py312", "yes", render_py, "intermediate_tables/fig1_enhanced_alluvial_attrition_input_mapped.tsv; intermediate_tables/fig1B_claim_boundary_lock_input_mapped.tsv; intermediate_tables/fig1B_tier_membership_matrix_input_mapped.tsv", "outputs/figure1_enhanced_alluvial_tierheatmap_phase50.png", "outputs/figure1_enhanced_alluvial_tierheatmap_phase50.svg; outputs/figure1_enhanced_alluvial_tierheatmap_phase50.pdf", "figure_layout_spec.tsv", "figure_output_spec.md", "pass", "Enhanced denominator alluvial plus tier-membership heatmap rendered at final size and copied to legacy Fig1 path"],
            ["Fig1", "upset", "cohort denominator, attrition flow, and tier intersections", "two Fig1B variants", "native_enhanced_alluvial_upset", "native_workflow", "production_ready", "pass", "pass", "Python", "research-py312", "yes", render_py, "intermediate_tables/fig1_enhanced_alluvial_attrition_input_mapped.tsv; intermediate_tables/fig1B_claim_boundary_lock_input_mapped.tsv; intermediate_tables/fig1B_tier_membership_matrix_input_mapped.tsv", "outputs/figure1_enhanced_alluvial_upset_phase50.png", "outputs/figure1_enhanced_alluvial_upset_phase50.svg; outputs/figure1_enhanced_alluvial_upset_phase50.pdf", "figure_layout_spec.tsv", "figure_output_spec.md", "pass", "Enhanced denominator alluvial plus UpSet intersection variant rendered at final size"],
            ["Fig2", "enhanced", "stability evidence plus decision quadrant", "single final render", "native_complexheatmap_radial_decision", "native_workflow", "production_ready", "pass", "pass", "R", "research-r45", "yes", render_r, "intermediate_tables/fig2A_raincloud_bootstrap_input_mapped.tsv; intermediate_tables/fig2B_complexheatmap_method_ari_input_mapped.tsv; intermediate_tables/fig2C_radial_lollipop_condition_input_mapped.tsv; intermediate_tables/fig2D_stability_decision_quadrant_input_mapped.tsv", "outputs/figure2_enhanced_complexheatmap_radial_decision_phase49.png", "outputs/figure2_enhanced_complexheatmap_radial_decision_phase49.svg; outputs/figure2_enhanced_complexheatmap_radial_decision_phase49.pdf", "figure_layout_spec.tsv", "figure_output_spec.md", "pass", "R ComplexHeatmap plus stability decision quadrant rendered at final size"],
            ["Fig3", "enhanced", "clinical impact forest and decision quadrant", "single final render", "native_clinical_forest_quadrant", "native_workflow", "production_ready", "pass", "pass", "Python", "research-py312", "yes", render_py, "intermediate_tables/fig3_enhanced_clinical_impact_input_mapped.tsv", "outputs/figure3_enhanced_clinical_forest_quadrant_phase49.png", "outputs/figure3_enhanced_clinical_forest_quadrant_phase49.svg; outputs/figure3_enhanced_clinical_forest_quadrant_phase49.pdf", "figure_layout_spec.tsv", "figure_output_spec.md", "pass", "Enhanced clinical forest/quadrant rendered at final size"],
        ],
        variants_cols,
    )

    layout_cols = [
        "figure", "panel", "panel role", "final x mm", "final y mm", "final width mm",
        "final height mm", "render width mm", "render height mm", "scale in assembly",
        "panel label x mm", "panel label y mm", "font target", "line width target",
        "output pdf/svg", "output png", "reason",
    ]
    write_tsv(
        REDRAW / "figure_layout_spec.tsv",
        [
            ["Fig1", "A-B tierheatmap", "enhanced alluvial attrition flow and tier membership heatmap", 0, 0, 180, 160, 180, 160, "100%", 4, 4, "Arial 7-8 pt", "0.75-1.6 pt emphasis lines", "figure1_enhanced_alluvial_tierheatmap_phase50.svg", "figure1_enhanced_alluvial_tierheatmap_phase50.png", "default final-size render"],
            ["Fig1", "A-B UpSet", "enhanced alluvial attrition flow and UpSet intersections", 0, 0, 180, 160, 180, 160, "100%", 4, 4, "Arial 7-8 pt", "0.75-1.6 pt emphasis lines", "figure1_enhanced_alluvial_upset_phase50.svg", "figure1_enhanced_alluvial_upset_phase50.png", "alternative final-size render"],
            ["Fig2", "A-D", "raincloud, ComplexHeatmap, radial lollipop, decision quadrant", 0, 0, 180, 160, 180, 160, "100%", 4, 4, "Arial/Helvetica 7-8 pt", "0.75-2.1 pt emphasis lines", "figure2_enhanced_complexheatmap_radial_decision_phase49.svg", "figure2_enhanced_complexheatmap_radial_decision_phase49.png", "final-size R grid render"],
            ["Fig3", "A-B", "clinical forest table and quadrant scatter", 0, 0, 180, 142, 180, 142, "100%", 4, 4, "Arial 7-8 pt", "0.70-1.55 pt emphasis lines", "figure3_enhanced_clinical_forest_quadrant_phase49.svg", "figure3_enhanced_clinical_forest_quadrant_phase49.png", "final-size render"],
        ],
        layout_cols,
    )

    mapping = f"""
# Panel Visual Mapping

| Panel | Panel role | Variant budget | Atlas major class | Atlas subtype | Candidate ID | Candidate level | Candidate maturity | Data fit gate | Visual fit gate | Runtime | Env | Selected option | Template/capsule | Capsule path | Reference visual | Source script | Source code snapshot | Raw data | Variable mapping | Intermediate file | Ported script | Visual match notes | Validation report | Output | Reason |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Fig1 | Cohort denominator, attrition flow, and tier membership | two Fig1B variants | flow + matrix | enhanced alluvial attrition + tier membership heatmap | native_enhanced_alluvial_tierheatmap | native_workflow | production_ready | pass | pass | Python | research-py312 | tierheatmap default | native matplotlib alluvial and membership matrix workflow | NA | Phase48 alluvial plus user-requested tier membership heatmap | {render_py} | {render_py} | E:\\Reserch\\Older women\\manuscript\\bmc_geriatrics_submission_burden_profiles_rescue\\additional_file_12_baseline_clinical_design_covariate_availability.csv | source, complete four-domain, LFO model n, events, evidence role, tier membership | intermediate_tables/fig1_enhanced_alluvial_attrition_input_mapped.tsv; intermediate_tables/fig1B_claim_boundary_lock_input_mapped.tsv; intermediate_tables/fig1B_tier_membership_matrix_input_mapped.tsv | scripts/render_phase49_fig1_fig3_enhanced.py | visual_match_notes.md#fig1 | persist_source_code_first_validation.md | outputs/figure1_enhanced_alluvial_tierheatmap_phase50.svg | Adds pale attrition streams, retention labels, event chips and a tier membership heatmap. |
| Fig1 | Cohort denominator, attrition flow, and tier intersections | two Fig1B variants | flow + UpSet | enhanced alluvial attrition + UpSet intersections | native_enhanced_alluvial_upset | native_workflow | production_ready | pass | pass | Python | research-py312 | upset alternative | native matplotlib alluvial and UpSet workflow | NA | Phase48 alluvial plus user-requested UpSet variant | {render_py} | {render_py} | E:\\Reserch\\Older women\\manuscript\\bmc_geriatrics_submission_burden_profiles_rescue\\additional_file_12_baseline_clinical_design_covariate_availability.csv | source, complete four-domain, LFO model n, events, evidence role, tier intersection | intermediate_tables/fig1_enhanced_alluvial_attrition_input_mapped.tsv; intermediate_tables/fig1B_claim_boundary_lock_input_mapped.tsv; intermediate_tables/fig1B_tier_membership_matrix_input_mapped.tsv | scripts/render_phase49_fig1_fig3_enhanced.py | visual_match_notes.md#fig1 | persist_source_code_first_validation.md | outputs/figure1_enhanced_alluvial_upset_phase50.svg | Adds pale attrition streams, retention labels, event chips and an UpSet tier-intersection panel. |
| Fig2 | Stability evidence dashboard | single final render | dashboard | raincloud + ComplexHeatmap + radial lollipop + decision quadrant | native_complexheatmap_radial_decision | native_workflow | production_ready | pass | pass | R | research-r45 | enhanced | R-native ComplexHeatmap plus grid decision grammar | NA | R-native stability dashboard | {render_r} | {render_r} | E:\\Reserch\\Older women\\outputs\\phase32_gmm_bootstrap_stability.csv; E:\\Reserch\\Older women\\manuscript\\bmc_geriatrics_submission_burden_profiles_rescue\\additional_file_17_gmm_algorithm_robustness.csv; E:\\Reserch\\Older women\\manuscript\\bmc_geriatrics_submission_burden_profiles_rescue\\additional_file_13_profile_stability_guardrails.csv | bootstrap ARI, method ARI matrix, log10 covariance condition, complete-domain N, decision region | intermediate_tables/fig2A_raincloud_bootstrap_input_mapped.tsv; intermediate_tables/fig2B_complexheatmap_method_ari_input_mapped.tsv; intermediate_tables/fig2C_radial_lollipop_condition_input_mapped.tsv; intermediate_tables/fig2D_stability_decision_quadrant_input_mapped.tsv | scripts/render_phase49_fig2_complexheatmap_hf147.R | visual_match_notes.md#fig2 | persist_source_code_first_validation.md | outputs/figure2_enhanced_complexheatmap_radial_decision_phase49.svg | Uses ComplexHeatmap for method matrix and a direct p10 ARI by covariance decision quadrant. |
| Fig3 | Clinical impact and comparator loss | single final render | clinical forest | forest table + decision quadrant | native_clinical_forest_quadrant | native_workflow | production_ready | pass | pass | Python | research-py312 | enhanced | native clinical forest workflow | NA | Phase48 forest plus reviewer enhancement | {render_py} | {render_py} | E:\\Reserch\\Older women\\manuscript\\bmc_geriatrics_submission_burden_profiles_rescue\\additional_file_14_strict_core_lfo_functional_change_association.csv | adjusted RR, absolute risk, event counts, risk difference, Delta AUC | intermediate_tables/fig3_enhanced_clinical_impact_input_mapped.tsv | scripts/render_phase49_fig1_fig3_enhanced.py | visual_match_notes.md#fig3 | persist_source_code_first_validation.md | outputs/figure3_enhanced_clinical_forest_quadrant_phase49.svg | Adds absolute-risk table and quadrant interpretation for no AUC gain. |
"""
    (REDRAW / "panel_visual_mapping.md").write_text(mapping.strip() + "\n", encoding="utf-8")

    (REDRAW / "panel_template_selection.md").write_text(
        """# Panel Template Selection

| Panel | Selected option | Candidate ID | Candidate level | Selected output | Selection reason |
|---|---|---|---|---|---|
| Fig1 | tierheatmap | native_enhanced_alluvial_tierheatmap | native_workflow | outputs/figure1_enhanced_alluvial_tierheatmap_phase50.svg | Enhances denominator logic with attrition streams and adds a tier membership heatmap. |
| Fig1 | upset | native_enhanced_alluvial_upset | native_workflow | outputs/figure1_enhanced_alluvial_upset_phase50.svg | Alternative UpSet representation of tier intersections. |
| Fig2 | enhanced | native_complexheatmap_radial_decision | native_workflow | outputs/figure2_enhanced_complexheatmap_radial_decision_phase49.svg | Keeps the requested ComplexHeatmap and radial lollipop panels while replacing the ternary panel with a direct stability decision quadrant. |
| Fig3 | enhanced | native_clinical_forest_quadrant | native_workflow | outputs/figure3_enhanced_clinical_forest_quadrant_phase49.svg | Shows adjusted association, absolute risk, sample size, and profile-versus-continuous Delta AUC in one clinical figure. |
""",
        encoding="utf-8",
    )
    (REDRAW / "visual_match_notes.md").write_text(
        """# Visual Match Notes

## Fig1

The Phase48 row-alluvial is now Panel A and was strengthened with pale attrition streams, per-cohort retention labels, and event chips. Panel B is rendered in two source-backed variants: a tier membership heatmap that marks cohort inclusion across Construction, Strict LFO, Sensitivity, and Baseline-only tiers, and an UpSet panel that shows the same tier intersections as a compact Venn alternative. The heatmap variant is copied to the legacy Fig1 output path as the current default.

## Fig2

Panel A adds threshold bands to the true bootstrap ARI raincloud. Panel B uses R ComplexHeatmap as a pure method-agreement heatmap, with short method-family headers, a row evidence-tier strip, a boxed selected diagonal GMM reference column, and dashed inner boxes for low-agreement cells. Panel C converts covariance condition numbers into a radial lollipop guardrail. Panel D replaces the earlier ternary display with a direct stability decision quadrant using bootstrap p10 ARI versus log10 covariance condition; point size encodes complete four-domain N and an outer ring marks algorithm ARI median >=0.50.

## Fig3

Panel A keeps the clinical forest but adds a compact absolute-risk table. Panel B uses shaded quadrants to show that higher absolute-risk gradients do not coincide with positive profile Delta AUC.
""",
        encoding="utf-8",
    )
    (REDRAW / "project_palette_recommendation.md").write_text(
        """# Project Palette Recommendation

- Strict-core: #176C73
- Functional bridge sensitivity: #D08B1E
- Baseline-only descriptive: #91979C
- Validation-downgraded sensitivity: #BD6D61
- Attrition/unavailable: #D7DCE0

Numeric method agreement in Fig2B uses a separate blue-white-red ComplexHeatmap scale.
""",
        encoding="utf-8",
    )
    (REDRAW / "figure_quality_review.md").write_text(
        """# Figure Quality Review

| Panel | Option | Candidate ID | Scientific fit | Data fit | Visual clarity | Grammar fidelity | Publication standard | Reproducibility | Total score | Decision | Quality problems | Revision action |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| Fig1 | tierheatmap | native_enhanced_alluvial_tierheatmap | 30 | 20 | 18 | 14 | 10 | 5 | 97 | accept_main | Plus sign is used instead of checkmark for Arial-safe output | Current default because it is most compact and least abstract |
| Fig1 | upset | native_enhanced_alluvial_upset | 30 | 20 | 17 | 14 | 10 | 5 | 96 | accept_main | More abstract than heatmap | Use as alternative if the manuscript wants a formal set-intersection visual |
| Fig2 | enhanced | native_complexheatmap_radial_decision | 30 | 20 | 18 | 14 | 10 | 5 | 97 | accept_main | Decision thresholds require caption definition | Caption must define p10 ARI, log10 covariance, point size and outer-ring encoding |
| Fig3 | enhanced | native_clinical_forest_quadrant | 30 | 20 | 17 | 14 | 10 | 5 | 96 | accept_main | Compact table reports point estimates only | Keep CIs encoded in forest/scatter intervals |
""",
        encoding="utf-8",
    )
    (REDRAW / "panel_final_selection.md").write_text(
        """# Panel Final Selection

| Panel | Selected option | Candidate ID | Candidate level | Selected output | Final selection reason | Rejected alternatives | Known tradeoff |
|---|---|---|---|---|---|---|---|
| Fig1 | tierheatmap | native_enhanced_alluvial_tierheatmap | native_workflow | outputs/figure1_enhanced_alluvial_tierheatmap_phase50.svg | Makes denominator loss, LFO availability, evidence tier and tier membership visible in one figure. | Card-style claim boundary panel | Uses ASCII plus signs because Arial lacks a checkmark glyph in the WSL render device. |
| Fig1 | upset | native_enhanced_alluvial_upset | native_workflow | outputs/figure1_enhanced_alluvial_upset_phase50.svg | Provides a formal UpSet representation of tier intersections. | Card-style claim boundary panel | More abstract than heatmap; likely better as supplement or optional main variant. |
| Fig2 | enhanced | native_complexheatmap_radial_decision | native_workflow | outputs/figure2_enhanced_complexheatmap_radial_decision_phase49.svg | Adds a pure ComplexHeatmap method-agreement heatmap, radial covariance guardrail, and direct stability decision quadrant. | Previous normalized ternary evidence-balance panel | Four panels are information-rich and need a clear legend. |
| Fig3 | enhanced | native_clinical_forest_quadrant | native_workflow | outputs/figure3_enhanced_clinical_forest_quadrant_phase49.svg | Presents clinical effect, absolute risk, event burden and lack of Delta AUC gain together. | Phase48 forest plus ellipse | Compact table omits CI text to preserve readability. |
""",
        encoding="utf-8",
    )
    (REDRAW / "panel_variant_gallery.md").write_text(
        """# Panel Variant Gallery

Final Phase49 enhanced variants:

- Fig1 SVG default: `outputs/figure1_enhanced_alluvial_tierheatmap_phase50.svg`
- Fig1 SVG UpSet alternative: `outputs/figure1_enhanced_alluvial_upset_phase50.svg`
- Fig1 SVG legacy/default copy: `outputs/figure1_enhanced_alluvial_attrition_phase49.svg`
- Fig2 SVG: `outputs/figure2_enhanced_complexheatmap_radial_decision_phase49.svg`
- Fig3 SVG: `outputs/figure3_enhanced_clinical_forest_quadrant_phase49.svg`
""",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
