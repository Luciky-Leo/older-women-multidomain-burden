from __future__ import annotations

import argparse
import math
import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
REDRAW = ROOT / "figure_redraw" / "persist_stage1_fig1_fig2_fig3_figS1"
PERSIST = Path("/mnt/e/Python/PERSIST")


PANEL_SPECS = [
    {
        "panel": "Fig1A",
        "existing_figure": "figure1_cohort_flow_main.pdf",
        "current_visual_type": "Horizontal denominator bars with cohort role/tier labels",
        "panel_role": "main_standard",
        "variant_budget": "top 2-3 variants",
        "atlas_major_class": "Composition and proportion",
        "atlas_subtype": "Percent stacked/progress bar; denominator flow",
        "one_sentence_conclusion": "Source, complete-domain and LFO model denominators differ by cohort and tier.",
        "data_type": "cohort-level denominator table",
        "cognitive_task": "composition",
        "raw_data_file": "outputs/phase40_table1_baseline_clinical_design.csv; outputs/phase32_cohort_tier_lock.csv; outputs/phase37_table3_adjusted_functional_validation.csv",
        "required_columns_statistics": "cohort, source_women50_n, complete_four_domain_n, LFO/model denominator, role/tier, validation availability",
        "manuscript_role": "Denominator lock and cohort-tier guardrail",
        "reader_question_answered": "Which cohorts contribute to construction and validation, and how much denominator attrition occurs?",
        "guardrail_or_annotation_needed": "LASI baseline-only; SHARE validation-downgraded; KLoSA bridge; source vs complete vs model denominators must not be conflated.",
        "recommended_color_series_direction": "restrained clinical categorical tier colors plus neutral denominator greys",
        "recommended_analysis_runtime": "Python",
        "recommended_render_runtime": "Python / PERSIST matplotlib",
        "native_or_persist_candidate": "PERSIST composition templates with project-specific guardrail labels",
        "reason": "Panel is primarily a denominator-composition reading task rather than a biological result.",
        "query_terms": "percent stacked horizontal stacked bar denominator flow tier cohort construction validation composition progress bullet",
        "preferred_patterns": "percent_stacked_bar; composition_dashboard; horizontal_stacked; bullet; dumbbell",
        "avoid_terms": "SHAP spatial raster ROC calibration scatter regression radial 环形 玫瑰",
    },
    {
        "panel": "Fig2A",
        "existing_figure": "figure2_profile_stability_guardrails_main.pdf",
        "current_visual_type": "Bootstrap ARI dot/error display",
        "panel_role": "main_complex",
        "variant_budget": "top 2-3 variants",
        "atlas_major_class": "Group comparison and distribution",
        "atlas_subtype": "Forest/dot-interval uncertainty plot",
        "one_sentence_conclusion": "Bootstrap label stability varies by cohort and is poor in some sensitivity tiers.",
        "data_type": "cohort-level stability estimates with interval summary",
        "cognitive_task": "comparison",
        "raw_data_file": "outputs/phase32_gmm_stability_summary.csv; outputs/phase40_table2_profile_stability_guardrails.csv",
        "required_columns_statistics": "cohort, median_ari_vs_reference, p10_ari_vs_reference, min_ari_vs_reference, role/tier",
        "manuscript_role": "Model-stability guardrail",
        "reader_question_answered": "Are the selected GMM partitions stable enough to interpret?",
        "guardrail_or_annotation_needed": "Do not imply validation; label ARI thresholds and sensitivity tiers.",
        "recommended_color_series_direction": "ordered stability colors from stable teal to caution orange/red",
        "recommended_analysis_runtime": "Python",
        "recommended_render_runtime": "Python / PERSIST matplotlib",
        "native_or_persist_candidate": "PERSIST forest/errorbar or horizontal metric panel",
        "reason": "Effect-interval grammar is clearer than decorative dashboards for reviewer-facing stability.",
        "query_terms": "forest errorbar dot interval bootstrap ARI stability cohort uncertainty horizontal bar",
        "preferred_patterns": "forest_plot; errorbar; horizontal_bar; model_performance_scatter",
        "avoid_terms": "SHAP ROC raster map composition pie violin 小提琴 raincloud 云雨 density 密度",
    },
    {
        "panel": "Fig2B",
        "existing_figure": "figure2_profile_stability_guardrails_main.pdf",
        "current_visual_type": "Cross-method ARI heatmap",
        "panel_role": "main_complex",
        "variant_budget": "top 2-3 variants",
        "atlas_major_class": "Multivariate omics pattern",
        "atlas_subtype": "Matrix heatmap; method agreement matrix",
        "one_sentence_conclusion": "Alternative clustering methods reproduce the selected GMM labels unevenly across cohorts.",
        "data_type": "cohort by method numeric agreement matrix",
        "cognitive_task": "matrix",
        "raw_data_file": "outputs/phase36_gmm_algorithm_robustness.csv",
        "required_columns_statistics": "cohort, method, ari_vs_selected_gmm, selected_classes, near_singular_flag",
        "manuscript_role": "Algorithmic robustness guardrail",
        "reader_question_answered": "Which alternative algorithms agree with the selected GMM labels?",
        "guardrail_or_annotation_needed": "Label ARI scale; mark near-singular full-GMM solutions; avoid biological subtype wording.",
        "recommended_color_series_direction": "single sequential ARI heat scale with tier side annotation",
        "recommended_analysis_runtime": "Python",
        "recommended_render_runtime": "Python / PERSIST matplotlib",
        "native_or_persist_candidate": "PERSIST matrix heatmap or grouped heatmap templates",
        "reason": "The raw object is a small numeric matrix and must preserve exact ARI values.",
        "query_terms": "heatmap matrix correlation ARI method agreement cohort clustered heatmap rectangular heatmap",
        "preferred_patterns": "correlation_heatmap; matrix_heatmap; grouped_heatmap; triangular_heatmap",
        "avoid_terms": "SHAP ROC spatial raincloud scatter 散点 PCA Mantel network 网络",
    },
    {
        "panel": "Fig2C",
        "existing_figure": "figure2_profile_stability_guardrails_main.pdf",
        "current_visual_type": "Covariance condition-number horizontal bar",
        "panel_role": "main_complex",
        "variant_budget": "top 1-2 variants",
        "atlas_major_class": "Group comparison and distribution",
        "atlas_subtype": "Thresholded ranking bar/dot plot",
        "one_sentence_conclusion": "Full-covariance GMM solutions trigger near-singular covariance diagnostics.",
        "data_type": "cohort-level scalar diagnostic",
        "cognitive_task": "ranking",
        "raw_data_file": "outputs/phase32_gmm_stability_summary.csv; outputs/phase40_table2_profile_stability_guardrails.csv",
        "required_columns_statistics": "cohort, max_covariance_condition_number, near_singular_covariance, threshold line",
        "manuscript_role": "Model-stability guardrail",
        "reader_question_answered": "Do covariance diagnostics undermine stable latent-subtype claims?",
        "guardrail_or_annotation_needed": "Show log10 condition number and threshold reference.",
        "recommended_color_series_direction": "caution red/orange for near-singular diagnostics with neutral axis",
        "recommended_analysis_runtime": "Python",
        "recommended_render_runtime": "Python / PERSIST matplotlib",
        "native_or_persist_candidate": "PERSIST horizontal bar/errorbar or compact threshold metric panel",
        "reason": "Ranking with threshold is reviewer-friendly and avoids over-designed visuals.",
        "query_terms": "bar horizontal threshold condition number ranking errorbar cohort guardrail",
        "preferred_patterns": "forest_plot; horizontal_bar; lollipop; gradient_bar",
        "avoid_terms": "ROC SHAP spatial heatmap network 3D scatter 散点 regression 回归",
    },
    {
        "panel": "Fig3A",
        "existing_figure": "figure3_lfo_functional_change_main.pdf",
        "current_visual_type": "Crude risk-difference forest plot",
        "panel_role": "main_high_impact",
        "variant_budget": "top 2-3 variants",
        "atlas_major_class": "Group comparison and distribution",
        "atlas_subtype": "Clinical forest plot; effect size with CI",
        "one_sentence_conclusion": "Highest-risk LFO classes show within-cohort functional-change risk gradients.",
        "data_type": "cohort-level risk difference and confidence interval",
        "cognitive_task": "comparison",
        "raw_data_file": "outputs/phase40_table3_lfo_functional_change_association_strict_core.csv; outputs/phase36_functional_association_class_risks.csv",
        "required_columns_statistics": "cohort, crude_risk_difference_pct, crude_risk_difference_ci_pct, adjusted_risk_ratio, adjusted_risk_ratio_ci, event counts",
        "manuscript_role": "Exploratory strict-core functional-change association",
        "reader_question_answered": "How large are the absolute functional deterioration gradients within strict-core cohorts?",
        "guardrail_or_annotation_needed": "State LFO classes are not four-domain descriptive profiles; show strict-core only.",
        "recommended_color_series_direction": "clinical forest palette with absolute-risk emphasis; avoid subtype colors implying biology",
        "recommended_analysis_runtime": "Python or R",
        "recommended_render_runtime": "Python / PERSIST or R forest if statistical trust boundary needed",
        "native_or_persist_candidate": "PERSIST forest/errorbar variants plus optional native forest workflow",
        "reason": "Clinical reviewers expect effect estimates with CIs and denominators.",
        "query_terms": "forest plot risk difference confidence interval errorbar clinical effect size cohort",
        "preferred_patterns": "forest_plot; errorbar; dumbbell; lollipop; grouped_bar_error",
        "avoid_terms": "SHAP ROC heatmap spatial violin 小提琴 raincloud 云雨 box 箱线 density 密度",
    },
    {
        "panel": "Fig3B",
        "existing_figure": "figure3_lfo_functional_change_main.pdf",
        "current_visual_type": "Delta AUC forest plot",
        "panel_role": "main_high_impact",
        "variant_budget": "top 2-3 variants",
        "atlas_major_class": "Clinical prediction evaluation",
        "atlas_subtype": "Discrimination delta / model comparison interval",
        "one_sentence_conclusion": "Continuous three-domain scores match or outperform categorical LFO profiles for discrimination.",
        "data_type": "cohort-level delta AUC and bootstrap interval",
        "cognitive_task": "clinical_prediction",
        "raw_data_file": "outputs/phase40_table3_lfo_functional_change_association_strict_core.csv; outputs/phase37_auc_bootstrap_ci.csv; outputs/phase41_calibration_metrics.csv; outputs/phase41_decision_curve_summary.csv",
        "required_columns_statistics": "cohort, delta_auc_profile_minus_continuous, delta_auc_ci, profile_auc, continuous_auc, optional DCA/calibration",
        "manuscript_role": "Prediction-overclaim guardrail",
        "reader_question_answered": "Does categorical LFO profiling improve discrimination over continuous scores?",
        "guardrail_or_annotation_needed": "Zero line; negative values favor continuous scores; no prediction superiority claim.",
        "recommended_color_series_direction": "diverging clinical comparator palette centered at zero",
        "recommended_analysis_runtime": "Python",
        "recommended_render_runtime": "Python / PERSIST clinical prediction or forest template",
        "native_or_persist_candidate": "PERSIST forest plot, clinical prediction comparator, or DCA/calibration supplement variant",
        "reason": "The panel is a model-comparison guardrail, not a standard ROC curve.",
        "query_terms": "AUC delta model comparison clinical prediction forest interval ROC calibration DCA",
        "preferred_patterns": "forest_plot; roc_curve; calibration_curve; dca_curve; model_performance",
        "avoid_terms": "SHAP spatial composition pie ROC 曲线 校准 DCA raincloud 云雨 scatter 散点",
    },
    {
        "panel": "FigS1",
        "existing_figure": "supplementary_figure_s1_profile_heatmap.pdf",
        "current_visual_type": "Strict-core descriptive profile heatmap",
        "panel_role": "supplementary",
        "variant_budget": "top 2 variants if useful",
        "atlas_major_class": "Multivariate omics pattern",
        "atlas_subtype": "Clustered/grouped heatmap; profile signature matrix",
        "one_sentence_conclusion": "Strict-core profile classes are mostly severity gradients with cohort-specific domain deviations.",
        "data_type": "profile-class by burden-domain matrix with class size and cohort labels",
        "cognitive_task": "matrix",
        "raw_data_file": "outputs/phase37_table2_strict_core_profile_families.csv; outputs/phase4_gmm_class_profiles.csv; outputs/phase33_profile_family_summary.csv",
        "required_columns_statistics": "cohort, class/profile, class_n/pct, functional/cognitive/affective/cardiometabolic z means, family label",
        "manuscript_role": "Supplementary descriptive profile signature",
        "reader_question_answered": "What do the strict-core descriptive profile classes look like across four domains?",
        "guardrail_or_annotation_needed": "Show descriptive, not validated subtype; strict-core only; retain domain labels and class size.",
        "recommended_color_series_direction": "diverging burden z-score palette with class-size side annotation",
        "recommended_analysis_runtime": "Python",
        "recommended_render_runtime": "Python / PERSIST heatmap capsule",
        "native_or_persist_candidate": "PERSIST grouped heatmap/correlation heatmap or multi-omics matrix template",
        "reason": "A matrix heatmap best preserves domain-pattern interpretation.",
        "query_terms": "heatmap matrix profile class domain z score clustered grouped rectangular heatmap multiomics",
        "preferred_patterns": "correlation_heatmap; pca_heatmap; grouped_heatmap; circular_heatmap",
        "avoid_terms": "ROC SHAP spatial bar only scatter 散点 PCA Mantel network 网络 玫瑰 雷达",
    },
]


MANUAL_BOOSTS = {
    "Fig1A": {
        "percent_stacked_bar_template.py": 28,
        "hf_composition_dashboard_template.py": 20,
        "横轴百分比堆叠图": 35,
        "百分比堆叠图": 30,
        "带悬浮效果的条形堆叠图": 18,
        "双向子弹图": 25,
    },
    "Fig2A": {
        "forest_plot_template.py": 30,
        "森林图": 32,
        "误差": 22,
        "多面板多重坐标轴的水平柱状图": 24,
        "数据在100次随机划分": 16,
    },
    "Fig2B": {
        "correlation_heatmap_template.py": 25,
        "矩阵": 24,
        "热图": 28,
        "相关性": 15,
        "六边形": 8,
    },
    "Fig2C": {
        "forest_plot_template.py": 20,
        "横向条形图": 22,
        "渐变颜色": 10,
        "棒棒糖": 18,
        "误差": 10,
    },
    "Fig3A": {
        "forest_plot_template.py": 36,
        "森林图": 40,
        "误差": 22,
        "哑铃": 20,
        "棒棒糖": 16,
        "带误差线": 26,
    },
    "Fig3B": {
        "forest_plot_template.py": 30,
        "ROC": 12,
        "AUC": 12,
        "校准": 5,
        "DCA": 5,
        "森林图": 28,
        "误差": 20,
    },
    "FigS1": {
        "correlation_heatmap_template.py": 28,
        "pca_heatmap_template.py": 15,
        "热图": 30,
        "矩阵": 24,
        "相关性矩阵": 15,
        "多组学验证环形热图": 12,
    },
}


PREFERRED_LEVEL = {
    "hf": "hf_capsule",
    "index": "persist_indexed_code",
    "mapping": "persist_indexed_code",
    "template": "generic_portable_template",
    "atlas": "hf_capsule",
}


def safe_read(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, low_memory=False)


def normalize_text(value: object) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return ""
    return str(value)


def row_text(row: pd.Series) -> str:
    return " ".join(normalize_text(value) for value in row.to_dict().values())


def text_score(text: str, terms: str) -> int:
    lower = text.lower()
    score = 0
    for term in re.split(r"[\s,;/|]+", terms):
        term = term.strip().lower()
        if not term:
            continue
        if term in lower:
            score += 8
    return score


def manual_boost(panel: str, text: str) -> int:
    lower = text.lower()
    score = 0
    for key, boost in MANUAL_BOOSTS.get(panel, {}).items():
        if key.lower() in lower:
            score += boost
    return score


def avoid_penalty(spec: dict[str, str], text: str) -> int:
    lower = text.lower()
    penalty = 0
    for term in spec["avoid_terms"].split():
        if term.lower() in lower:
            penalty += 12
    return penalty


def source_ready_score(row: dict[str, object], level: str) -> int:
    score = 0
    for key in ["source_script", "source_code_snapshot", "primary_script"]:
        if normalize_text(row.get(key)):
            score += 5
    for key in ["reference_visual", "primary_reference", "selected_file"]:
        if normalize_text(row.get(key)):
            score += 5
    if level == "generic_portable_template":
        score += 10
    return min(score, 15)


def candidate_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    hf = safe_read(PERSIST / "_portable_patterns/high_fidelity_by_folder/FOLDER_HIGH_FIDELITY_CATALOG.csv")
    for _, r in hf.iterrows():
        rows.append(
            {
                "source": "FOLDER_HIGH_FIDELITY_CATALOG",
                "source_kind": "high_fidelity_capsule",
                "candidate_id": r.get("capsule_id", ""),
                "level": "hf_capsule",
                "title": r.get("title", ""),
                "family": r.get("task_class", ""),
                "technique": r.get("feature_labels", ""),
                "capsule_path": r.get("capsule_folder", ""),
                "reference_visual": r.get("primary_reference", ""),
                "source_script": r.get("primary_script", ""),
                "source_code_snapshot": "",
                "generic_template_path": "",
                "native_workflow": "",
                "visual_score_raw": r.get("visual_score", ""),
                "raw_text": row_text(r),
            }
        )
    idx = safe_read(PERSIST / "_index/PERSIST_plot_code_index.csv")
    for _, r in idx.iterrows():
        rel = normalize_text(r.get("relative_path"))
        rows.append(
            {
                "source": "PERSIST_plot_code_index",
                "source_kind": "indexed_source_code",
                "candidate_id": r.get("id", ""),
                "level": "persist_indexed_code",
                "title": r.get("item_title", ""),
                "family": r.get("primary_family", ""),
                "technique": r.get("technique_tags", ""),
                "capsule_path": "",
                "reference_visual": "",
                "source_script": str(PERSIST / rel) if rel else "",
                "source_code_snapshot": "",
                "generic_template_path": "",
                "native_workflow": "",
                "visual_score_raw": r.get("figure_file_count_in_folder", ""),
                "raw_text": row_text(r),
            }
        )
    templates = safe_read(PERSIST / "_portable_patterns/TEMPLATE_CATALOG.csv")
    for _, r in templates.iterrows():
        rel = normalize_text(r.get("pattern_path"))
        rows.append(
            {
                "source": "TEMPLATE_CATALOG",
                "source_kind": "portable_template",
                "candidate_id": f"generic_portable_template:{rel}",
                "level": "generic_portable_template",
                "title": r.get("plot_task", rel),
                "family": r.get("source_family", ""),
                "technique": r.get("plot_task", ""),
                "capsule_path": "",
                "reference_visual": "",
                "source_script": str(PERSIST / "_portable_patterns/patterns" / rel) if rel else "",
                "source_code_snapshot": "",
                "generic_template_path": str(PERSIST / "_portable_patterns/patterns" / rel) if rel else "",
                "native_workflow": "",
                "visual_score_raw": "",
                "raw_text": row_text(r),
            }
        )
    mapping = safe_read(PERSIST / "_portable_patterns/SOURCE_TO_PATTERN_MAPPING.csv")
    for i, r in mapping.iterrows():
        source_rel = normalize_text(r.get("source_relative_path"))
        suggested = normalize_text(r.get("suggested_pattern"))
        rows.append(
            {
                "source": "SOURCE_TO_PATTERN_MAPPING",
                "source_kind": "source_to_pattern_mapping",
                "candidate_id": f"mapping:{i:04d}:{suggested}",
                "level": "persist_indexed_code",
                "title": source_rel,
                "family": r.get("primary_family", ""),
                "technique": suggested,
                "capsule_path": "",
                "reference_visual": "",
                "source_script": str(PERSIST / source_rel) if source_rel else "",
                "source_code_snapshot": "",
                "generic_template_path": str(PERSIST / "_portable_patterns/patterns" / suggested) if suggested else "",
                "native_workflow": "",
                "visual_score_raw": "",
                "raw_text": row_text(r),
            }
        )
    atlas = safe_read(PERSIST / "_atlas/PERSIST_atlas_index.csv")
    for _, r in atlas.iterrows():
        folder = normalize_text(r.get("folder_name"))
        rows.append(
            {
                "source": "PERSIST_atlas_index",
                "source_kind": "atlas_reference",
                "candidate_id": f"atlas:{int(r.get('number', 0)):03d}:{folder}",
                "level": "hf_capsule",
                "title": r.get("chart_label", folder),
                "family": "atlas_reference",
                "technique": r.get("chart_label", ""),
                "capsule_path": "",
                "reference_visual": r.get("selected_file", ""),
                "source_script": "",
                "source_code_snapshot": "",
                "generic_template_path": "",
                "native_workflow": "",
                "visual_score_raw": "",
                "raw_text": row_text(r),
            }
        )
    return rows


def score_candidate(spec: dict[str, str], cand: dict[str, object]) -> dict[str, object]:
    text = normalize_text(cand.get("raw_text"))
    panel = spec["panel"]
    base = text_score(text, spec["query_terms"]) + manual_boost(panel, text) - avoid_penalty(spec, text)
    level = normalize_text(cand["level"])
    source_ready = source_ready_score(cand, level)
    task_fit = min(30, max(0, base // 3 + (8 if spec["atlas_major_class"].split()[0].lower() in text.lower() else 0)))
    data_fit = 25
    visual = min(20, max(0, base // 4))
    readiness = source_ready
    readability = 10
    lower_text = text.lower()
    if "radial" in lower_text or "环形" in text or "玫瑰" in text:
        if panel in {"Fig1A", "Fig2B", "FigS1"}:
            readability -= 2
        if panel in {"Fig2A", "Fig2C", "Fig3A", "Fig3B"}:
            readability -= 5
            visual -= 4
    if "shap" in lower_text:
        data_fit -= 12
        visual -= 6
    if "roc" in lower_text and panel != "Fig3B":
        data_fit -= 10
        visual -= 5
    if "spatial" in lower_text or "遥感" in text:
        data_fit -= 15
        visual -= 8
    # Panel-specific hard gates. These panels are aggregate clinical/statistical
    # summaries; attractive but wrong grammars must stay out of render lists.
    if panel in {"Fig2A", "Fig3A"} and any(term in text for term in ["小提琴", "云雨", "山脊", "密度", "箱线"]):
        data_fit -= 12
        visual -= 8
    if (panel == "Fig3B" and any(term in lower_text for term in ["roc", "calibration", "dca"])) or (
        panel == "Fig3B" and any(term in text for term in ["ROC", "校准", "决策曲线", "混淆矩阵"])
    ):
        # Current Fig3B is a delta-AUC interval panel, not a raw prediction
        # curve panel. ROC/calibration/DCA can be separate Phase41 supplement
        # variants only after a different panel definition.
        data_fit -= 18
        visual -= 12
    if panel == "Fig3B" and any(term in lower_text for term in ["confusion", "classification"]):
        data_fit -= 18
        visual -= 12
    if panel == "FigS1" and any(term in text for term in ["散点", "PCoA", "PCA", "Mantel", "网络", "雷达", "玫瑰"]):
        data_fit -= 12
        visual -= 8
    if panel == "Fig2B" and any(term in text for term in ["PCA", "Mantel", "网络", "散点"]):
        data_fit -= 10
        visual -= 7
    if panel in {"Fig2B", "FigS1"} and any(term in lower_text for term in ["feature_importance", "shap", "importance"]):
        data_fit -= 12
        visual -= 8
    if panel == "Fig1A" and any(term in text for term in ["环形百分比堆叠", "径向堆叠", "玫瑰"]):
        visual -= 8
        readability -= 3
    total = task_fit + data_fit + visual + readiness + readability
    if total < 35 or data_fit < 15 or visual < 4:
        data_gate = "fail" if data_fit < 15 else "conditional_pass"
        visual_gate = "fail" if visual < 4 else "conditional_pass"
        decision = "reject"
        maturity = "reject"
    else:
        data_gate = "pass" if data_fit >= 23 else "conditional_pass"
        visual_gate = "pass" if visual >= 14 else "conditional_pass"
        if level == "generic_portable_template":
            maturity = "production_ready"
        elif readiness >= 12:
            maturity = "source_port_ready"
        else:
            maturity = "needs_porting"
        decision = "render_recommended" if total >= 76 and data_gate != "fail" and visual_gate != "fail" else "render_optional" if total >= 60 else "hold_native"
    return {
        "Panel": panel,
        "Panel role": spec["panel_role"],
        "Variant budget": spec["variant_budget"],
        "Candidate ID": cand["candidate_id"],
        "Candidate level": level,
        "Candidate maturity": maturity,
        "HF capsule ID": cand["candidate_id"] if level == "hf_capsule" and normalize_text(cand["candidate_id"]).startswith("HF") else "",
        "PERSIST source ID": cand["candidate_id"] if level == "persist_indexed_code" and normalize_text(cand["candidate_id"]).startswith("PERSIST-") else "",
        "Generic template path": cand["generic_template_path"],
        "Native workflow": "",
        "Candidate source": cand["source"],
        "Candidate kind": cand["source_kind"],
        "PERSIST atlas major class": spec["atlas_major_class"],
        "PERSIST atlas subtype": spec["atlas_subtype"],
        "Data fit gate": data_gate,
        "Data fit notes": "Original project table exists; mapping required but no simulated data needed." if data_gate != "fail" else "Candidate implies unavailable or mismatched data/statistic.",
        "Visual fit gate": visual_gate,
        "Visual fit notes": "Visual grammar matches reader task." if visual_gate == "pass" else "Needs porting/readability check at panel size.",
        "Task fit score": task_fit,
        "Data fit score": data_fit,
        "Visual grammar score": max(0, visual),
        "Source-code readiness score": readiness,
        "Readability score": max(0, readability),
        "Total score": total,
        "Render decision": decision,
        "Runtime": "Python" if "R" not in spec["recommended_render_runtime"] else spec["recommended_render_runtime"],
        "Env": "research-py312",
        "Capsule path": cand["capsule_path"],
        "Reference visual": cand["reference_visual"],
        "Source script": cand["source_script"],
        "Source code snapshot": cand["source_code_snapshot"],
        "Why it fits": f"{cand['title']} -> {spec['reader_question_answered']}",
        "Risk": "Need source-code-first port and exact data binding; reject if reference/source cannot be verified.",
        "Candidate title": cand["title"],
        "Candidate family": cand["family"],
        "Candidate technique": cand["technique"],
    }


def dedupe_and_rank(scored: pd.DataFrame, per_panel: int = 8) -> pd.DataFrame:
    keep_rows = []
    for panel, g in scored.groupby("Panel", sort=False):
        g = g.sort_values("Total score", ascending=False).copy()
        # Keep the best row for each candidate ID.
        g = g.drop_duplicates("Candidate ID", keep="first")
        selected = []
        seen_families: dict[str, int] = {}
        for _, row in g.iterrows():
            if row["Render decision"] == "reject":
                continue
            family_key = str(row["Generic template path"] or row["Candidate family"] or row["Candidate kind"])
            if seen_families.get(family_key, 0) >= 2 and len(selected) >= 4:
                continue
            seen_families[family_key] = seen_families.get(family_key, 0) + 1
            selected.append(row)
            if len(selected) >= per_panel:
                break
        if not selected:
            selected = [g.iloc[0]]
        for i, row in enumerate(selected, start=1):
            d = row.to_dict()
            d["Option"] = f"{panel}.{i}"
            keep_rows.append(d)
    columns = [
        "Panel",
        "Option",
        "Panel role",
        "Variant budget",
        "Candidate ID",
        "Candidate level",
        "Candidate maturity",
        "HF capsule ID",
        "PERSIST source ID",
        "Generic template path",
        "Native workflow",
        "Candidate source",
        "Candidate kind",
        "PERSIST atlas major class",
        "PERSIST atlas subtype",
        "Data fit gate",
        "Data fit notes",
        "Visual fit gate",
        "Visual fit notes",
        "Task fit score",
        "Data fit score",
        "Visual grammar score",
        "Source-code readiness score",
        "Readability score",
        "Total score",
        "Render decision",
        "Runtime",
        "Env",
        "Capsule path",
        "Reference visual",
        "Source script",
        "Source code snapshot",
        "Why it fits",
        "Risk",
        "Candidate title",
        "Candidate family",
        "Candidate technique",
    ]
    return pd.DataFrame(keep_rows)[columns]


def write_markdown(inventory: pd.DataFrame, candidates: pd.DataFrame, out: Path) -> None:
    lines = [
        "# Phase 42 PERSIST Panel Selection Audit",
        "",
        "No rendering was performed. This is Stage 1 classification, full-catalog candidate recall, gate scoring, and variant planning for Fig1, Fig2, Fig3, and Fig S1.",
        "",
        "Search surfaces used:",
        "",
        "- `E:/Python/PERSIST/_portable_patterns/high_fidelity_by_folder/FOLDER_HIGH_FIDELITY_CATALOG.csv`",
        "- `E:/Python/PERSIST/_index/PERSIST_plot_code_index.csv`",
        "- `E:/Python/PERSIST/_portable_patterns/SOURCE_TO_PATTERN_MAPPING.csv`",
        "- `E:/Python/PERSIST/_portable_patterns/TEMPLATE_CATALOG.csv`",
        "- `E:/Python/PERSIST/_portable_patterns/high_fidelity_by_folder/capsules` via HF catalog rows",
        "- `E:/Python/PERSIST/_atlas/PERSIST_atlas_index.csv` and original source folders via indexed source paths",
        "",
        "## Panel Inventory",
        "",
    ]
    inv_cols = [
        "Panel",
        "Current visual type",
        "Panel role",
        "Variant budget",
        "PERSIST atlas major class",
        "PERSIST atlas subtype",
        "One-sentence conclusion",
        "Data type",
        "Data source status",
    ]
    lines.append("| " + " | ".join(inv_cols) + " |")
    lines.append("| " + " | ".join(["---"] * len(inv_cols)) + " |")
    for row in inventory.to_dict("records"):
        vals = [str(row.get(col, "")).replace("|", "/") for col in inv_cols]
        lines.append("| " + " | ".join(vals) + " |")
    lines.extend(["", "## Candidate Shortlist", ""])
    cand_cols = [
        "Panel",
        "Option",
        "Candidate level",
        "Candidate maturity",
        "Data fit gate",
        "Visual fit gate",
        "Total score",
        "Render decision",
        "Candidate ID",
        "Candidate title",
        "Source script",
    ]
    lines.append("| " + " | ".join(cand_cols) + " |")
    lines.append("| " + " | ".join(["---"] * len(cand_cols)) + " |")
    for row in candidates.to_dict("records"):
        vals = [str(row.get(col, "")).replace("|", "/") for col in cand_cols]
        lines.append("| " + " | ".join(vals) + " |")
    lines.extend(
        [
            "",
            "## Rendering Rule For Next Step",
            "",
            "Render only `render_recommended` and user-approved `render_optional` candidates. Each rendered variant must use real project output tables listed in `panel_inventory.tsv`; no screenshots or simulated data are allowed.",
            "",
            "Recommended next action: render all `render_recommended` candidates, plus optional candidates for panels where the top two grammars are meaningfully different.",
        ]
    )
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=REDRAW)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    inventory = pd.DataFrame(PANEL_SPECS)
    inventory_out = inventory.rename(
        columns={
            "panel": "Panel",
            "existing_figure": "Existing figure",
            "current_visual_type": "Current visual type",
            "panel_role": "Panel role",
            "variant_budget": "Variant budget",
            "atlas_major_class": "PERSIST atlas major class",
            "atlas_subtype": "PERSIST atlas subtype",
            "one_sentence_conclusion": "One-sentence conclusion",
            "data_type": "Data type",
            "cognitive_task": "Cognitive task",
            "raw_data_file": "Raw data file",
            "required_columns_statistics": "Required columns/statistics",
            "manuscript_role": "Manuscript role",
            "reader_question_answered": "Reader question answered",
            "guardrail_or_annotation_needed": "Guardrail or annotation needed",
            "recommended_color_series_direction": "Recommended color-series direction",
            "recommended_analysis_runtime": "Recommended analysis runtime",
            "recommended_render_runtime": "Recommended render runtime",
            "native_or_persist_candidate": "Native or PERSIST candidate",
            "reason": "Reason",
        }
    )
    inventory_out["Data source status"] = "available from project outputs; original cohort data not needed for plotted aggregate statistics"
    inventory_out.to_csv(args.output_dir / "panel_inventory.tsv", sep="\t", index=False)

    pool = candidate_rows()
    full_rows = []
    for spec in PANEL_SPECS:
        for cand in pool:
            full_rows.append(score_candidate(spec, cand))
    full = pd.DataFrame(full_rows)
    full.to_csv(args.output_dir / "panel_template_candidates_full_pool_scored.tsv", sep="\t", index=False)
    shortlisted = dedupe_and_rank(full, per_panel=8)
    shortlisted.to_csv(args.output_dir / "panel_template_candidates.tsv", sep="\t", index=False)
    # Also write empty render/final-selection placeholders required by protocol.
    pd.DataFrame(
        columns=[
            "Panel",
            "Option",
            "Panel role",
            "Variant budget",
            "Candidate ID",
            "Candidate level",
            "Candidate maturity",
            "Data fit gate",
            "Visual fit gate",
            "Runtime",
            "Env",
            "Rendered",
            "Render script",
            "Intermediate file",
            "Output PNG",
            "Output PDF/SVG",
            "Validation status",
            "Reason",
        ]
    ).to_csv(args.output_dir / "panel_render_variants.tsv", sep="\t", index=False)
    write_markdown(inventory_out, shortlisted, args.output_dir / "panel_template_selection.md")

    # Copy stage-1 artifacts to outputs for easy discovery.
    inventory_out.to_csv(OUT / "phase42_persist_panel_inventory.tsv", sep="\t", index=False)
    shortlisted.to_csv(OUT / "phase42_persist_panel_template_candidates.tsv", sep="\t", index=False)
    full.to_csv(OUT / "phase42_persist_full_pool_scored.tsv", sep="\t", index=False)
    write_markdown(inventory_out, shortlisted, OUT / "phase42_persist_panel_template_selection.md")
    print(args.output_dir / "panel_inventory.tsv")
    print(args.output_dir / "panel_template_candidates.tsv")
    print(args.output_dir / "panel_template_selection.md")


if __name__ == "__main__":
    main()
