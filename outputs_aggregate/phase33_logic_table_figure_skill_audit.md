# Phase 33 Skill-Based Manuscript Logic, Table, and Figure Audit

Date: 2026-06-02

Applied skills/assets:

| Rank | Score | Recommendation | Skill or asset | Path | Best use | Limits |
|---:|---:|---|---|---|---|---|
| 1 | 94 | Primary | biomed-figure-redraw / PERSIST protocols | E:/Reserch/Skills/02_callable_skills/figure_publishing/biomed-figure-redraw/SKILL.md | Decide which additional manuscript figures are scientifically needed and how to source-code-first redraw them | This audit does not render new Fig4/Supp figures yet |
| 2 | 86 | Supporting | Documents review workflow | C:/Users/luff9/.codex/plugins/cache/openai-primary-runtime/documents/26.601.10930/skills/documents | Full-text logic and layout/reading-flow review | Current manuscript is LaTeX/PDF, not DOCX |
| 3 | 84 | Supporting | Spreadsheets scientific-research guidance | C:/Users/luff9/.codex/plugins/cache/openai-primary-runtime/spreadsheets/26.601.10930/skills/spreadsheets | Table architecture, machine-readable supplementary tables and reproducible table shells | Final journal LaTeX table styling still needs TeX implementation |

## Executive Verdict

The current BMC rescue manuscript is scientifically safer than the prior endotype draft, but it is too skeletal for a reviewer-ready clinical paper. The central statistical caution is now honest, but the paper has not yet rebuilt a positive clinical storyline around that caution.

Current source facts: 79,938 source-screen women 50+, 76,293 selected profile assignments, 37,923 strict-primary validation rows with 9,590 strict-primary events. Continuous three-domain scores fit functional deterioration better than profile classes in 5 strict validation cohorts. All seven selected cohort solutions have near-singular covariance downgrade flags (7/7).

The manuscript should therefore be framed as: a transparent, women-only, seven-cohort map of multidomain burden profiles plus a validation/stability guardrail showing why the profiles are descriptive clinical strata rather than stable latent endotypes or prediction tools.

## Full-Text Logic Audit

| Manuscript part | Current issue | Required revision | Priority |
|---|---|---|---|
| Title | The title is now conservative and no longer says endotype, which is correct. It still reads as a purely descriptive mapping paper and does not tell readers that the paper contains a major guardrail/comparator result. | Consider adding 'with validation and stability guardrails' only if title length permits; otherwise keep title and make abstract conclusion stronger. | Medium |
| Abstract | It reports the negative comparator result, but the positive clinical contribution is weak: what the profiles reveal clinically is not summarized. | Add one sentence naming the recurrent clinical patterns, e.g. cardiometabolic/chronic-high function-spared profiles and functional-dominant high-burden profiles, while preserving the no-superiority conclusion. | High |
| Background | The women-only rationale is thin. It says older women may have domain-specific burden, but does not explain why women-only cross-cohort mapping is clinically or epidemiologically justified. | Add a paragraph on sex-specific aging burden, longevity/disability burden, affective symptoms, multimorbidity, and why pooled-sex profiles could hide women-specific heterogeneity. | High |
| Final introduction paragraph | Aim is appropriately modest but not operational enough. | State three aims: profile construction; harmonization audit; validation/stability guardrails against overclaiming. | High |
| Methods: cohorts | Missing exact selected wave logic and follow-up interval details in the main text. | Add a compact methods table or paragraph with cohort wave, baseline year/wave, follow-up endpoint window if available, and why LASI lacks validation. | High |
| Methods: domain construction | Current text gives domain names but not enough reproducibility in main text. | Add score construction details: item aggregation, missingness rule, z-standardization, orientation, and handling of cohort-specific global cognitive scores. | High |
| Methods: GMM | Model-selection rule is present, but selected class counts and candidate 2-5 class diagnostics are hidden. | Keep concise main methods but ensure Supplementary Table S2 is cited. Add why GMM is descriptive, not discovery of latent diseases. | High |
| Methods: validation | Decoupled validation is scientifically crucial but still hard to understand. | Add a short schematic sentence: four-domain profiles describe baseline; leave-functional-domain-out profiles test whether non-functional domains predict later function; continuous three-domain scores are the comparator. | High |
| Results order | Harmonization appears before showing the clinical profile families. This makes the paper feel like an audit report before the reader sees the clinical object. | Reorder Results: denominators -> clinical profile families/Fig2 -> harmonization risks -> validation/stability guardrails. | High |
| Results: profile interpretation | There is no main table translating Fig2 rows into clinical families. | Add new Table 2 from phase33_profile_family_summary.csv and cite it before Fig2. | Critical |
| Results: validation | Table 3 and Fig3 now align, but table status text is too long and not visually clinical. | Redesign Table 3 around grouped performance/stability/claim columns with short claim labels. | Critical |
| Discussion | Discussion correctly avoids overclaiming, but reads mostly negative. | First paragraph should say what descriptive mapping adds despite no prediction superiority: interpretable heterogeneity map, harmonization audit, and transparent non-superiority. | High |
| Limitations | No dedicated limitations section; limitations are embedded in discussion. | Add a separate 'Strengths and limitations' or 'Limitations' paragraph/section with endpoint coupling, harmonization non-equivalence, complete-case selection, within-cohort validation, GMM degeneracy, no clinical actionability. | Critical |
| Declarations | Placeholders are acceptable now, but final submission needs author completion. | Leave placeholders until author data are available; do not fabricate. | Submission gate |

Current structure audit: approx 2,028 TeX tokens/words, 3 main tables, 3 main figures, no dedicated limitations section flag = 0.

## Main Table Upgrade Plan

### Table 1: Cohort roles, denominator locks, and validation availability

- Placement/action: Main; Revise current Table 1.
- Reader question: Which cohorts support construction, validation, bridge sensitivity, or baseline-only description?
- Core columns: Cohort; selected wave; role/tier; source women 50+; complete four-domain n (% of source); selected profile n/classes; validation n (% of profile); events (%); functional source tier; allowed claim
- Data source: `outputs/phase32_cohort_tier_lock.csv; outputs/phase28_gmm_selection_table.csv`
- Design upgrade: Use grouped headers for construction, validation, and claim status; right-align numbers; replace LASI 0 events with NA/not available; remove long raw variable strings from body and move to footnote.
- Status: `must_add_or_revise`

### Table 2: Clinical burden-profile families among selected GMM classes

- Placement/action: Main; Add new clinical core table.
- Reader question: What clinical patterns did the profiles actually identify?
- Core columns: Clinical family; recurrent/cohort-specific; selected classes; cohorts represented; participants (%); class-size range; four-domain signature; conservative clinical interpretation; caveat
- Data source: `outputs/phase33_profile_family_summary.csv; outputs/phase33_selected_class_dictionary.csv`
- Design upgrade: Collapse 28 selected classes into 5-7 readable family rows; keep full 28-row dictionary in supplement; use short domain chips such as F, Cog, Aff, CM rather than long prose in every cell.
- Status: `must_add`

### Table 3: Decoupled validation performance and model-stability guardrails

- Placement/action: Main; Revise current Table 3.
- Reader question: Do profiles add validation value beyond continuous domain scores, and are models stable enough to trust?
- Core columns: Cohort; tier; validation n/events/%; profile AUC; continuous three-domain AUC; delta AUC; delta AIC/1,000; ARI median/p10; covariance downgrade; locked interpretation
- Data source: `outputs/phase32_decoupled_validation_comparison.csv; outputs/phase32_gmm_stability_summary.csv`
- Design upgrade: Use comparator columns, not a single status sentence; normalize delta AIC by 1,000 participants; mark negative deltas as continuous-favored; no underscores in status text.
- Status: `must_revise`

### Table 4: Domain harmonization and comparability risk matrix

- Placement/action: Main or supplement depending on final page budget; Replace current Table 2 or move current Table 2 to supplement.
- Reader question: Are functional, cognitive, affective, and cardiometabolic/chronic domains comparable enough for interpretation?
- Core columns: Cohort; functional tier/items/nonmissing; cognitive tier/items/nonmissing; affective tier/items/nonmissing; cardiometabolic/chronic tier/items/nonmissing; reviewer-risk note
- Data source: `outputs/phase32_item_level_harmonization_crosswalk.csv; outputs/phase28_domain_harmonization_dictionary.csv`
- Design upgrade: Use a 7 by 4 cohort-domain matrix instead of comparability flag counts; show tier and nonmissing percent in each cell; use footnotes for CHARLS IADL-only, HRS ADL-only, KLoSA bridge, SHARE EURO-D.
- Status: `must_have_either_main_table_or_main_figure`

## New Clinical Profile Family Table Evidence

The following rows are generated from selected GMM classes only. They should drive the new main Table 2, with the full 28-class dictionary placed in the supplement.

| Clinical family | Group | Classes | Cohorts | Participants | Participant % | Class % range | Mean F/Cog/Aff/CM z |
|---|---|---:|---|---:|---:|---|---|
| Intermediate burden, cardiometabolic/chronic spared | recurrent family | 6 | ELSA, HRS, KLoSA, LASI, MHAS, SHARE | 33,498 | 43.91 | 35.25-58.01 | -0.29/-0.16/-0.20/-0.87 |
| Intermediate burden, severity aligned | recurrent family | 5 | CHARLS, ELSA, HRS, SHARE | 8,609 | 11.28 | 8.53-73.42 | 0.23/0.22/0.23/0.28 |
| Intermediate burden, cardiometabolic/chronic high with function spared | recurrent family | 4 | ELSA, HRS, LASI, SHARE | 17,633 | 23.11 | 20.56-43.40 | -0.45/-0.14/-0.14/0.62 |
| Intermediate burden, cardiometabolic/chronic high | recurrent family | 2 | KLoSA, MHAS | 3,695 | 4.84 | 33.67-34.99 | -0.31/-0.13/-0.08/0.50 |
| High burden, functional dominant with cardiometabolic/chronic spared | recurrent family | 2 | CHARLS, MHAS | 1,380 | 1.81 | 6.94-15.17 | 1.83/0.48/0.61/0.12 |
| High burden, functional dominant with cognition relatively spared | recurrent family | 2 | HRS, MHAS | 1,169 | 1.53 | 6.36-7.72 | 1.83/0.46/0.77/0.64 |
| High burden, cardiometabolic/chronic dominant with cognition spared | cohort-specific family | 1 | LASI | 5,877 | 7.70 | 21.42-21.42 | 0.72/0.13/0.17/1.04 |
| High burden, functional/cognitive dominant with affective and cardiometabolic/chronic partly spared | cohort-specific family | 1 | SHARE | 1,138 | 1.49 | 7.24-7.24 | 2.94/1.69/1.03/0.72 |
| High burden, cardiometabolic/chronic dominant with function and cognition spared | cohort-specific family | 1 | MHAS | 760 | 1.00 | 11.29-11.29 | -0.02/0.07/0.29/1.80 |
| High burden, severity aligned | cohort-specific family | 1 | KLoSA | 667 | 0.87 | 16.34-16.34 | 1.12/0.96/0.72/1.25 |
| High burden, affective dominant with cardiometabolic/chronic spared | cohort-specific family | 1 | HRS | 659 | 0.86 | 6.46-6.46 | 0.77/0.49/1.50/0.01 |
| High burden, functional dominant with cognition and cardiometabolic/chronic spared | cohort-specific family | 1 | ELSA | 659 | 0.86 | 10.80-10.80 | 2.48/0.39/0.82/0.48 |
| Intermediate burden, cardiometabolic/chronic high with function and affective symptoms spared | cohort-specific family | 1 | ELSA | 549 | 0.72 | 8.99-8.99 | -0.42/0.20/0.03/1.83 |

Table 2 should not overinterpret these families as diagnoses or actionable treatment groups. The safest wording is 'clinical burden-profile families' or 'descriptive profile families'.

## Supplementary Table Upgrade Plan

| Table | Title | Minimum fields | Data source | Purpose |
|---|---|---|---|---|
| Supplementary Table S1 | Item-level harmonization crosswalk | cohort, wave, domain, variable, construct, source tier, raw direction, score orientation, nonmissing n/%, used flag, comparability flag, reviewer-risk note | `outputs/phase32_item_level_harmonization_crosswalk.csv` | Defends domain construction at reviewer audit level. |
| Supplementary Table S2 | GMM two-to-five class model selection and convergence | cohort, classes, n, converged, BIC, AIC, entropy, mean posterior, min class %, selected flag, selection rule | `outputs/phase28_gmm_selection_table.csv` | Prevents black-box class-number criticism. |
| Supplementary Table S3 | Full selected class dictionary | cohort, class, n, %, posterior, four z-scored domains, severity mean, label, high/spared domains | `outputs/phase33_selected_class_dictionary.csv` | Allows readers to inspect every selected class behind Fig2 and main Table 2. |
| Supplementary Table S4 | Full validation model metrics | cohort, endpoint, n, events, event %, all comparator AIC/BIC/AUC columns, delta columns, separation flag | `outputs/phase32_decoupled_validation_comparison.csv; outputs/phase28_validation_metrics_main.csv` | Shows the continuous comparator result transparently. |
| Supplementary Table S5 | Endpoint leakage and coupling audit | cohort, endpoint kind, coupling level, baseline-function/event correlation, change-event correlation, baseline quartile event percentages, evidence status | `outputs/phase32_functional_endpoint_leakage_audit.csv` | Addresses the most serious validation-circularity criticism. |
| Supplementary Table S6 | Covariance degeneracy and bootstrap stability diagnostics | cohort, class, weight, min eigenvalue, determinant, condition number, near-singular flag, ARI median/p10/min | `outputs/phase32_gmm_covariance_diagnostics.csv; outputs/phase32_gmm_stability_summary.csv` | Documents why profiles are descriptive rather than stable latent endotypes. |
| Supplementary Table S7 | Selection and missingness audit | cohort, source women 50+, complete four-domain n/% retained, validation n/% retained, missingness driver by domain, role lock | `outputs/phase32_cohort_tier_lock.csv; outputs/phase32_item_level_harmonization_crosswalk.csv` | Needed because complete-case selection is not yet made visible enough. |
| Supplementary Table S8 | Outcome and model specification dictionary | endpoint, model family, covariates, comparator, fit metric, missingness rule, interpretation limit | `outputs/phase28_outcome_model_specification.csv; scripts` | Gives methods reproducibility without overloading main text. |

## Table Visual Design Rules

- Do not use `\tiny` in main tables unless absolutely unavoidable; use `\small`/`\scriptsize`, `tabularx`, `adjustbox`, or split tables instead.
- Use grouped column headers: `Construction`, `Validation`, `Model stability`, `Allowed claim`.
- Use numbers as numbers: right-align N, events, percentages, AIC/AUC/ARI; keep text columns left-aligned.
- Replace machine labels such as `three_domain_scores_fit_better_than_profiles` with short reader labels such as `continuous favored`.
- Use `NA/not available` for LASI validation rather than `0 events`.
- Move raw variable strings out of main table body when they create line wrapping; retain source tier and cite the full crosswalk.
- Give every table a one-line interpretation footnote, not just definitions.
- Keep color optional and print-safe. If color is used in PDFs, it must be redundant with text/tier codes.

## Figure Upgrade Plan

| Figure | Placement | Action | Title | Panels | Data source | Why it strengthens the manuscript | Priority |
|---|---|---|---|---|---|---|---|
| Figure 1 | Main | Keep but retitle/reframe | Study architecture and denominator locks | A: source to complete-domain to profile to validation counts; B: cohort role/tier guardrail; C optional: event burden by cohort | `outputs/phase32_cohort_tier_lock.csv` | What is the seven-cohort construction versus six-cohort validation design? Current A1 is appropriate; ensure LASI is shown as no follow-up validation, not 0 events. | must_keep_main |
| Figure 2 | Main | Keep but strengthen annotations | Clinically annotated multidomain burden-profile map | Profile rows with class N/%; four-domain z-score matrix; clinical family; role/tier; event availability | `outputs/phase33_selected_class_dictionary.csv; outputs/phase32_cohort_tier_lock.csv` | What clinical heterogeneity was mapped? Keep B1 main. Add or preserve clinical family labels and avoid implying cross-cohort absolute equivalence of z-scores. | must_keep_main |
| Figure 3 | Main | Keep current G1 | Validation and model-stability guardrails | Decoupled validation delta AIC; bootstrap ARI; numeric guardrail table | `outputs/phase32_decoupled_validation_comparison.csv; outputs/phase32_gmm_stability_summary.csv` | Do profiles outperform continuous scores, and are selected models stable? Current G1 answers the reviewer guardrail. G2 remains Supplementary Figure S3. | must_keep_main |
| Figure 4 | Main if page budget allows; otherwise Supplementary Figure S4 | Add | Cohort-domain harmonization risk matrix | 7 cohorts by 4 domains; cell color = strict/partial/bridge/unavailable; text = variable family and nonmissing % | `outputs/phase32_item_level_harmonization_crosswalk.csv; outputs/phase28_domain_harmonization_dictionary.csv` | How comparable are the four domains across cohorts? This is the strongest additional figure for reviewer confidence because harmonization is the manuscript's main vulnerability. | must_add_main_or_supp |
| Supplementary Figure S4/S5 | Supplement | Add | GMM model-selection and degeneracy diagnostics | BIC delta by class number; min class %; entropy/posterior; covariance condition/eigenvalue; selected model flags | `outputs/phase28_gmm_selection_table.csv; outputs/phase32_gmm_covariance_diagnostics.csv` | Were GMM classes selected transparently and are any numerical artifacts visible? Use heatmap/dot-matrix grammar; do not crowd main text unless reviewers focus on modeling. | should_add_supp |
| Supplementary Figure S5/S6 | Supplement | Add | Functional endpoint coupling and leakage audit | Baseline functional quartile event percentages; baseline-function/event correlation; decoupled endpoint status | `outputs/phase32_functional_endpoint_leakage_audit.csv` | How much of the original validation endpoint was coupled to baseline functional input? This should be supplemental unless the paper is framed mainly as a methodological cautionary study. | should_add_supp |
| Supplementary Figure S6/S7 | Supplement | Add if missingness is challenged | Complete-case and validation-retention funnel | Per-cohort retained % from source to complete-domain and validation sets; domain missingness driver | `outputs/phase32_cohort_tier_lock.csv; outputs/phase32_item_level_harmonization_crosswalk.csv` | Could selection or missingness bias the profile map? Useful if Table 1 is still dense or reviewer asks for a flow diagram beyond denominator bars. | optional_supp |

## Should Additional Figures Be Added?

Yes. The most important added figure is a cohort-domain harmonization risk matrix. The current manuscript says harmonization is a key limitation, but the main visual sequence does not show the measurement non-equivalence that justifies the conservative conclusion. If page budget allows, add it as main Figure 4; otherwise make it Supplementary Figure S4 and cite it prominently in Methods and Results.

A GMM model-selection/stability diagnostic figure should be supplementary. Fig3 already exposes the main stability guardrail; the supplement should show the underlying 2-5 class BIC/min-class/entropy/covariance evidence.

An endpoint leakage/coupling figure should be supplementary unless the manuscript is reframed as a primarily methodological warning. It is valuable because the endpoint-coupling issue was the prior fatal flaw.

## Recommended Revised Main-Text Reading Order

1. Background: clinical need for women-only multidomain burden mapping and risk of overinterpreting profiles.
2. Methods: seven-cohort construction; four domains; GMM descriptive profile construction; harmonization audit; decoupled validation guardrail.
3. Results 1: denominator and role lock (Table 1, Fig1).
4. Results 2: what profiles look like clinically (new Table 2, Fig2).
5. Results 3: harmonization risks that constrain interpretation (Table 4 or Fig4).
6. Results 4: validation/comparator and stability guardrails (revised Table 3, Fig3).
7. Discussion: descriptive value first, then why profiles are not prediction-superior or stable latent endotypes.

## Pass/Fail Gates Before Manuscript Rewrite

- Main Table 2 must exist, or the paper has no clinical interpretation anchor.
- Table 1 must not show LASI as 0 validation events; it must show validation unavailable.
- Table 3 must include delta AUC and delta AIC/1,000 plus ARI p10, not only median ARI.
- A harmonization risk matrix must appear either as main Table 4/main Fig4 or as a prominently cited supplementary figure/table.
- A limitations section must explicitly state endpoint coupling, harmonization non-equivalence, complete-case selection, within-cohort validation, and GMM degeneracy.
- The abstract must name at least one concrete clinical pattern; otherwise the manuscript reads like only a negative methods audit.

## Immediate Implementation Recommendation

Do not add every proposed figure to the main paper. For BMC Geriatrics, the strongest package is four main tables and four main figures if page budget allows: Table 1 denominator lock, Table 2 clinical profile families, Table 3 validation/stability guardrails, Table 4 harmonization risk matrix; Fig1 denominator architecture, Fig2 profile heatmap, Fig3 validation/stability, Fig4 harmonization risk matrix. If this feels heavy, keep Table 4 in supplement and keep Fig4 as main because harmonization is easier to understand visually.
