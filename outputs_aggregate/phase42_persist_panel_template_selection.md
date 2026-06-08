# Phase 42 PERSIST Panel Selection Audit

No rendering was performed. This is Stage 1 classification, full-catalog candidate recall, gate scoring, and variant planning for Fig1, Fig2, Fig3, and Fig S1.

Search surfaces used:

- `E:/Python/PERSIST/_portable_patterns/high_fidelity_by_folder/FOLDER_HIGH_FIDELITY_CATALOG.csv`
- `E:/Python/PERSIST/_index/PERSIST_plot_code_index.csv`
- `E:/Python/PERSIST/_portable_patterns/SOURCE_TO_PATTERN_MAPPING.csv`
- `E:/Python/PERSIST/_portable_patterns/TEMPLATE_CATALOG.csv`
- `E:/Python/PERSIST/_portable_patterns/high_fidelity_by_folder/capsules` via HF catalog rows
- `E:/Python/PERSIST/_atlas/PERSIST_atlas_index.csv` and original source folders via indexed source paths

## Panel Inventory

| Panel | Current visual type | Panel role | Variant budget | PERSIST atlas major class | PERSIST atlas subtype | One-sentence conclusion | Data type | Data source status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Fig1A | Horizontal denominator bars with cohort role/tier labels | main_standard | top 2-3 variants | Composition and proportion | Percent stacked/progress bar; denominator flow | Source, complete-domain and LFO model denominators differ by cohort and tier. | cohort-level denominator table | available from project outputs; original cohort data not needed for plotted aggregate statistics |
| Fig2A | Bootstrap ARI dot/error display | main_complex | top 2-3 variants | Group comparison and distribution | Forest/dot-interval uncertainty plot | Bootstrap label stability varies by cohort and is poor in some sensitivity tiers. | cohort-level stability estimates with interval summary | available from project outputs; original cohort data not needed for plotted aggregate statistics |
| Fig2B | Cross-method ARI heatmap | main_complex | top 2-3 variants | Multivariate omics pattern | Matrix heatmap; method agreement matrix | Alternative clustering methods reproduce the selected GMM labels unevenly across cohorts. | cohort by method numeric agreement matrix | available from project outputs; original cohort data not needed for plotted aggregate statistics |
| Fig2C | Covariance condition-number horizontal bar | main_complex | top 1-2 variants | Group comparison and distribution | Thresholded ranking bar/dot plot | Full-covariance GMM solutions trigger near-singular covariance diagnostics. | cohort-level scalar diagnostic | available from project outputs; original cohort data not needed for plotted aggregate statistics |
| Fig3A | Crude risk-difference forest plot | main_high_impact | top 2-3 variants | Group comparison and distribution | Clinical forest plot; effect size with CI | Highest-risk LFO classes show within-cohort functional-change risk gradients. | cohort-level risk difference and confidence interval | available from project outputs; original cohort data not needed for plotted aggregate statistics |
| Fig3B | Delta AUC forest plot | main_high_impact | top 2-3 variants | Clinical prediction evaluation | Discrimination delta / model comparison interval | Continuous three-domain scores match or outperform categorical LFO profiles for discrimination. | cohort-level delta AUC and bootstrap interval | available from project outputs; original cohort data not needed for plotted aggregate statistics |
| FigS1 | Strict-core descriptive profile heatmap | supplementary | top 2 variants if useful | Multivariate omics pattern | Clustered/grouped heatmap; profile signature matrix | Strict-core profile classes are mostly severity gradients with cohort-specific domain deviations. | profile-class by burden-domain matrix with class size and cohort labels | available from project outputs; original cohort data not needed for plotted aggregate statistics |

## Candidate Shortlist

| Panel | Option | Candidate level | Candidate maturity | Data fit gate | Visual fit gate | Total score | Render decision | Candidate ID | Candidate title | Source script |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Fig1A | Fig1A.1 | generic_portable_template | production_ready | pass | pass | 100 | render_recommended | generic_portable_template:composition/percent_stacked_bar_template.py | 百分比堆叠图 | /mnt/e/Python/PERSIST/_portable_patterns/patterns/composition/percent_stacked_bar_template.py |
| Fig1A | Fig1A.2 | hf_capsule | needs_porting | pass | pass | 93 | render_recommended | HF122_2025-12-01_893fbc2e | 2025年12月1日 Python绘制横轴百分比堆叠图 | E:\Python\PERSIST\2025年12月1日 Python绘制横轴百分比堆叠图\1201-横向堆叠条形图.py |
| Fig1A | Fig1A.3 | persist_indexed_code | needs_porting | pass | pass | 90 | render_recommended | mapping:0058:composition/percent_stacked_bar_template.py | 2025年12月1日 Python绘制横轴百分比堆叠图\1201-横向堆叠条形图.py | /mnt/e/Python/PERSIST/2025年12月1日 Python绘制横轴百分比堆叠图\1201-横向堆叠条形图.py |
| Fig1A | Fig1A.4 | persist_indexed_code | needs_porting | pass | pass | 87 | render_recommended | mapping:0174:composition/percent_stacked_bar_template.py | 2026年02月16日 Python绘制堆叠面积图展示数据分布\20260215-堆叠面积图.py | /mnt/e/Python/PERSIST/2026年02月16日 Python绘制堆叠面积图展示数据分布\20260215-堆叠面积图.py |
| Fig1A | Fig1A.5 | persist_indexed_code | needs_porting | pass | pass | 87 | render_recommended | PERSIST-0973 | composition | /mnt/e/Python/PERSIST/_portable_patterns/patterns/composition/percent_stacked_bar_template.py |
| Fig1A | Fig1A.6 | persist_indexed_code | needs_porting | pass | pass | 77 | render_recommended | PERSIST-0059 | 2025年12月1日 Python绘制横轴百分比堆叠图 | /mnt/e/Python/PERSIST/2025年12月1日 Python绘制横轴百分比堆叠图/1201-横向堆叠条形图.py |
| Fig1A | Fig1A.7 | hf_capsule | needs_porting | pass | pass | 77 | render_recommended | atlas:122:2025年12月1日 Python绘制横轴百分比堆叠图 | 百分比堆叠图 |  |
| Fig1A | Fig1A.8 | hf_capsule | needs_porting | pass | conditional_pass | 69 | render_optional | HF115_2025-11-19_c62ff61d | 2025年11月19日 期刊图片复现Python绘制多组韦恩图 | E:\Python\PERSIST\2025年11月19日 期刊图片复现Python绘制多组韦恩图\1116-韦恩图组合图.py |
| Fig2A | Fig2A.1 | generic_portable_template | production_ready | pass | pass | 97 | render_recommended | generic_portable_template:group_distribution/forest_plot_template.py | 森林图 | /mnt/e/Python/PERSIST/_portable_patterns/patterns/group_distribution/forest_plot_template.py |
| Fig2A | Fig2A.2 | persist_indexed_code | needs_porting | pass | pass | 87 | render_recommended | mapping:0221:group_distribution/forest_plot_template.py | 2026年05月16日 森林图\20260513-森林图.py | /mnt/e/Python/PERSIST/2026年05月16日 森林图\20260513-森林图.py |
| Fig2A | Fig2A.3 | persist_indexed_code | needs_porting | pass | conditional_pass | 72 | render_optional | mapping:0153:group_distribution/box_violin_dot_template.py | 2026年01月07日 Python绘制带有数据标注和误差棒的多面板多重坐标轴的水平柱状图\20260107-Python绘制带有数据标注和误差棒的多面板多重坐标轴的水平柱状图.py | /mnt/e/Python/PERSIST/2026年01月07日 Python绘制带有数据标注和误差棒的多面板多重坐标轴的水平柱状图\20260107-Python绘制带有数据标注和误差棒的多面板多重坐标轴的水平柱状图.py |
| Fig2A | Fig2A.4 | persist_indexed_code | needs_porting | pass | conditional_pass | 69 | render_optional | PERSIST-0981 | group_distribution | /mnt/e/Python/PERSIST/_portable_patterns/patterns/group_distribution/forest_plot_template.py |
| Fig2A | Fig2A.5 | hf_capsule | needs_porting | pass | conditional_pass | 66 | render_optional | atlas:139:2026年01月07日 Python绘制带有数据标注和误差棒的多面板多重坐标轴的水平柱状图 | 带有数据标注和误差棒的多面板多重坐标轴的水平柱状图 |  |
| Fig2A | Fig2A.6 | persist_indexed_code | needs_porting | pass | conditional_pass | 66 | render_optional | PERSIST-0154 | 2026年01月07日 Python绘制带有数据标注和误差棒的多面板多重坐标轴的水平柱状图 | /mnt/e/Python/PERSIST/2026年01月07日 Python绘制带有数据标注和误差棒的多面板多重坐标轴的水平柱状图/20260107-Python绘制带有数据标注和误差棒的多面板多重坐标轴的水平柱状图.py |
| Fig2A | Fig2A.7 | hf_capsule | needs_porting | pass | conditional_pass | 64 | render_optional | HF139_2026-01-07_2cd37105 | 2026年01月07日 Python绘制带有数据标注和误差棒的多面板多重坐标轴的水平柱状图 | E:\Python\PERSIST\2026年01月07日 Python绘制带有数据标注和误差棒的多面板多重坐标轴的水平柱状图\20260107-Python绘制带有数据标注和误差棒的多面板多重坐标轴的水平柱状图.py |
| Fig2A | Fig2A.8 | hf_capsule | needs_porting | pass | conditional_pass | 63 | render_optional | atlas:208:2026年05月16日 森林图 | 森林图 (Forest plot) |  |
| Fig2B | Fig2B.1 | generic_portable_template | production_ready | pass | pass | 100 | render_recommended | generic_portable_template:correlation_omics/correlation_heatmap_template.py | 相关热图+FDR | /mnt/e/Python/PERSIST/_portable_patterns/patterns/correlation_omics/correlation_heatmap_template.py |
| Fig2B | Fig2B.2 | persist_indexed_code | needs_porting | pass | pass | 90 | render_recommended | mapping:0030:correlation_omics/correlation_heatmap_template.py | 2025年10月7日 Python绘制扇形相关性热图-包括pearson, spearman, kendall\扇形相关性热图.py | /mnt/e/Python/PERSIST/2025年10月7日 Python绘制扇形相关性热图-包括pearson, spearman, kendall\扇形相关性热图.py |
| Fig2B | Fig2B.3 | persist_indexed_code | needs_porting | pass | pass | 90 | render_recommended | mapping:0029:correlation_omics/correlation_heatmap_template.py | 2025年10月6日 期刊图片复现Python绘制带有分组区域的环状相关性热图\环状相关性热图-带分组标识.py | /mnt/e/Python/PERSIST/2025年10月6日 期刊图片复现Python绘制带有分组区域的环状相关性热图\环状相关性热图-带分组标识.py |
| Fig2B | Fig2B.4 | persist_indexed_code | needs_porting | pass | pass | 90 | render_recommended | mapping:0031:correlation_omics/correlation_heatmap_template.py | 2025年10月8日 Python绘制花瓣状多组相关性热图\花瓣状相关性热图.py | /mnt/e/Python/PERSIST/2025年10月8日 Python绘制花瓣状多组相关性热图\花瓣状相关性热图.py |
| Fig2B | Fig2B.5 | hf_capsule | needs_porting | pass | pass | 87 | render_recommended | atlas:187:2026年04月09日 Python绘制高颜值相关性矩阵图 | 相关性热图 |  |
| Fig2B | Fig2B.6 | hf_capsule | needs_porting | pass | pass | 83 | render_recommended | atlas:070:2025年9月14日 期刊图片复现python绘制六边形相关性矩阵图 | 相关性热图 |  |
| Fig2B | Fig2B.7 | persist_indexed_code | needs_porting | pass | pass | 82 | render_recommended | mapping:0041:correlation_omics/pca_heatmap_template.py | 2025年11月20日 期刊图片复现Python绘制双变量对角线分割组合三角热图\1120-组合热力图.py | /mnt/e/Python/PERSIST/2025年11月20日 期刊图片复现Python绘制双变量对角线分割组合三角热图\1120-组合热力图.py |
| Fig2B | Fig2B.8 | persist_indexed_code | needs_porting | pass | pass | 78 | render_recommended | PERSIST-0111 | 2025年7月28日 期刊图片复现python绘制地理探测器单因子柱状图+相关性分析热图组合图 | /mnt/e/Python/PERSIST/2025年7月28日 期刊图片复现python绘制地理探测器单因子柱状图+相关性分析热图组合图/横向条形图+矩阵图.py |
| Fig2C | Fig2C.1 | generic_portable_template | production_ready | pass | conditional_pass | 69 | render_optional | generic_portable_template:group_distribution/forest_plot_template.py | 森林图 | /mnt/e/Python/PERSIST/_portable_patterns/patterns/group_distribution/forest_plot_template.py |
| Fig2C | Fig2C.2 | persist_indexed_code | needs_porting | pass | conditional_pass | 59 | hold_native | mapping:0221:group_distribution/forest_plot_template.py | 2026年05月16日 森林图\20260513-森林图.py | /mnt/e/Python/PERSIST/2026年05月16日 森林图\20260513-森林图.py |
| Fig2C | Fig2C.3 | persist_indexed_code | needs_porting | pass | conditional_pass | 59 | hold_native | PERSIST-0981 | group_distribution | /mnt/e/Python/PERSIST/_portable_patterns/patterns/group_distribution/forest_plot_template.py |
| Fig2C | Fig2C.4 | hf_capsule | needs_porting | pass | conditional_pass | 50 | hold_native | atlas:114:2025年11月17日 期刊图片复现Python绘制棒棒糖气泡图 | 相关性气泡图 |  |
| Fig2C | Fig2C.5 | persist_indexed_code | needs_porting | pass | conditional_pass | 50 | hold_native | PERSIST-0038 | 2025年11月17日 期刊图片复现Python绘制棒棒糖气泡图 | /mnt/e/Python/PERSIST/2025年11月17日 期刊图片复现Python绘制棒棒糖气泡图/1115-棒棒糖气泡图.py |
| Fig3A | Fig3A.1 | generic_portable_template | production_ready | pass | pass | 100 | render_recommended | generic_portable_template:group_distribution/forest_plot_template.py | 森林图 | /mnt/e/Python/PERSIST/_portable_patterns/patterns/group_distribution/forest_plot_template.py |
| Fig3A | Fig3A.2 | persist_indexed_code | needs_porting | pass | pass | 90 | render_recommended | mapping:0221:group_distribution/forest_plot_template.py | 2026年05月16日 森林图\20260513-森林图.py | /mnt/e/Python/PERSIST/2026年05月16日 森林图\20260513-森林图.py |
| Fig3A | Fig3A.3 | persist_indexed_code | needs_porting | pass | conditional_pass | 78 | render_recommended | PERSIST-0981 | group_distribution | /mnt/e/Python/PERSIST/_portable_patterns/patterns/group_distribution/forest_plot_template.py |
| Fig3A | Fig3A.4 | hf_capsule | needs_porting | pass | conditional_pass | 73 | render_optional | HF212_2026-05-23_81a66f4d | 2026年05月23日 Python绘制带误差线的多面板柱状图 | E:\Python\PERSIST\2026年05月23日 Python绘制带误差线的多面板柱状图\20260521-多组柱状图.py |
| Fig3A | Fig3A.5 | hf_capsule | needs_porting | pass | pass | 72 | render_optional | atlas:208:2026年05月16日 森林图 | 森林图 (Forest plot) |  |
| Fig3A | Fig3A.6 | persist_indexed_code | needs_porting | pass | pass | 72 | render_optional | PERSIST-0226 | 2026年05月23日 Python绘制带误差线的多面板柱状图 | /mnt/e/Python/PERSIST/2026年05月23日 Python绘制带误差线的多面板柱状图/20260521-多组柱状图.py |
| Fig3A | Fig3A.7 | hf_capsule | needs_porting | pass | conditional_pass | 68 | render_optional | atlas:212:2026年05月23日 Python绘制带误差线的多面板柱状图 | 带误差线的多面板柱状图 |  |
| Fig3A | Fig3A.8 | persist_indexed_code | needs_porting | pass | conditional_pass | 68 | render_optional | PERSIST-0222 | 2026年05月16日 森林图 | /mnt/e/Python/PERSIST/2026年05月16日 森林图/20260513-森林图.py |
| Fig3B | Fig3B.1 | generic_portable_template | production_ready | pass | pass | 88 | render_recommended | generic_portable_template:group_distribution/forest_plot_template.py | 森林图 | /mnt/e/Python/PERSIST/_portable_patterns/patterns/group_distribution/forest_plot_template.py |
| Fig3B | Fig3B.2 | persist_indexed_code | needs_porting | pass | pass | 78 | render_recommended | mapping:0221:group_distribution/forest_plot_template.py | 2026年05月16日 森林图\20260513-森林图.py | /mnt/e/Python/PERSIST/2026年05月16日 森林图\20260513-森林图.py |
| Fig3B | Fig3B.3 | persist_indexed_code | needs_porting | pass | conditional_pass | 61 | render_optional | PERSIST-0981 | group_distribution | /mnt/e/Python/PERSIST/_portable_patterns/patterns/group_distribution/forest_plot_template.py |
| Fig3B | Fig3B.4 | hf_capsule | needs_porting | pass | conditional_pass | 61 | render_optional | atlas:208:2026年05月16日 森林图 | 森林图 (Forest plot) |  |
| Fig3B | Fig3B.5 | hf_capsule | needs_porting | pass | conditional_pass | 59 | hold_native | HF208_2026-05-16_3b690ee7 | 2026年05月16日 森林图 | E:\Python\PERSIST\2026年05月16日 森林图\20260513-森林图.py |
| Fig3B | Fig3B.6 | hf_capsule | needs_porting | pass | conditional_pass | 56 | hold_native | HF212_2026-05-23_81a66f4d | 2026年05月23日 Python绘制带误差线的多面板柱状图 | E:\Python\PERSIST\2026年05月23日 Python绘制带误差线的多面板柱状图\20260521-多组柱状图.py |
| Fig3B | Fig3B.7 | hf_capsule | needs_porting | pass | conditional_pass | 56 | hold_native | HF191_2026-04-18_e0fa957a | 2026年04月18日 Python绘制绝美带误差棒和数值标记3D柱状图 | E:\Python\PERSIST\2026年04月18日 Python绘制绝美带误差棒和数值标记3D柱状图\20260417-3D柱状图.py |
| Fig3B | Fig3B.8 | persist_indexed_code | needs_porting | pass | conditional_pass | 56 | hold_native | PERSIST-0222 | 2026年05月16日 森林图 | /mnt/e/Python/PERSIST/2026年05月16日 森林图/20260513-森林图.py |
| FigS1 | FigS1.1 | generic_portable_template | production_ready | pass | pass | 100 | render_recommended | generic_portable_template:correlation_omics/correlation_heatmap_template.py | 相关热图+FDR | /mnt/e/Python/PERSIST/_portable_patterns/patterns/correlation_omics/correlation_heatmap_template.py |
| FigS1 | FigS1.2 | persist_indexed_code | needs_porting | pass | pass | 90 | render_recommended | mapping:0188:correlation_omics/correlation_heatmap_template.py | 2026年03月11日 Python卡通风格套图(2)：相关性分析热图\20260306-卡通风格相关性分析热图.py | /mnt/e/Python/PERSIST/2026年03月11日 Python卡通风格套图(2)：相关性分析热图\20260306-卡通风格相关性分析热图.py |
| FigS1 | FigS1.3 | persist_indexed_code | needs_porting | pass | pass | 90 | render_recommended | mapping:0110:correlation_omics/correlation_heatmap_template.py | 2025年7月28日 期刊图片复现python绘制地理探测器单因子柱状图+相关性分析热图组合图\横向条形图+矩阵图.py | /mnt/e/Python/PERSIST/2025年7月28日 期刊图片复现python绘制地理探测器单因子柱状图+相关性分析热图组合图\横向条形图+矩阵图.py |
| FigS1 | FigS1.4 | persist_indexed_code | needs_porting | pass | pass | 90 | render_recommended | mapping:0132:correlation_omics/correlation_heatmap_template.py | 2025年8月7日 Python一键绘制惊艳的相关性椭圆图--包括Pearson、Spearman和Kendall相关性分析等三种方法\相关性热图进阶.py | /mnt/e/Python/PERSIST/2025年8月7日 Python一键绘制惊艳的相关性椭圆图--包括Pearson、Spearman和Kendall相关性分析等三种方法\相关性热图进阶.py |
| FigS1 | FigS1.5 | hf_capsule | needs_porting | pass | pass | 84 | render_recommended | atlas:187:2026年04月09日 Python绘制高颜值相关性矩阵图 | 相关性热图 |  |
| FigS1 | FigS1.6 | persist_indexed_code | needs_porting | pass | pass | 82 | render_recommended | mapping:0041:correlation_omics/pca_heatmap_template.py | 2025年11月20日 期刊图片复现Python绘制双变量对角线分割组合三角热图\1120-组合热力图.py | /mnt/e/Python/PERSIST/2025年11月20日 期刊图片复现Python绘制双变量对角线分割组合三角热图\1120-组合热力图.py |
| FigS1 | FigS1.7 | hf_capsule | needs_porting | pass | pass | 80 | render_recommended | atlas:070:2025年9月14日 期刊图片复现python绘制六边形相关性矩阵图 | 相关性热图 |  |
| FigS1 | FigS1.8 | persist_indexed_code | needs_porting | pass | conditional_pass | 71 | render_optional | PERSIST-0111 | 2025年7月28日 期刊图片复现python绘制地理探测器单因子柱状图+相关性分析热图组合图 | /mnt/e/Python/PERSIST/2025年7月28日 期刊图片复现python绘制地理探测器单因子柱状图+相关性分析热图组合图/横向条形图+矩阵图.py |

## Rendering Rule For Next Step

Render only `render_recommended` and user-approved `render_optional` candidates. Each rendered variant must use real project output tables listed in `panel_inventory.tsv`; no screenshots or simulated data are allowed.

Recommended next action: render all `render_recommended` candidates, plus optional candidates for panels where the top two grammars are meaningfully different.
