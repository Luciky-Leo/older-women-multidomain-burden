from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
MANUSCRIPT = ROOT / "manuscript" / "bmc_geriatrics_submission_burden_profiles_rescue" / "bmc_geriatrics_main.tex"


def read_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(OUT / name)


def pct(n: float, d: float) -> str:
    if pd.isna(n) or pd.isna(d) or d == 0:
        return "NA"
    return f"{n:,.0f} ({n / d * 100:.1f}%)"


def build_profile_family_summary() -> pd.DataFrame:
    selection = read_csv("phase28_gmm_selection_table.csv")
    profiles = read_csv("phase4_gmm_class_profiles.csv")
    selected_models = selection.loc[
        selection["selected_model"].eq(1),
        ["analysis_set", "analysis_tier", "cohort", "wave", "n_classes"],
    ]
    selected = profiles.merge(
        selected_models,
        on=["analysis_set", "analysis_tier", "cohort", "wave", "n_classes"],
        how="inner",
    )

    family_name = {
        "intermediate_spared_cardiometabolic_chronic": "Intermediate burden, cardiometabolic/chronic spared",
        "intermediate_high_cardiometabolic_chronic_spared_functional": "Intermediate burden, cardiometabolic/chronic high with function spared",
        "intermediate_severity_aligned": "Intermediate burden, severity aligned",
        "intermediate_high_cardiometabolic_chronic": "Intermediate burden, cardiometabolic/chronic high",
        "high_burden_high_functional_spared_cardiometabolic_chronic": "High burden, functional dominant with cardiometabolic/chronic spared",
        "high_burden_high_functional_spared_cognitive": "High burden, functional dominant with cognition relatively spared",
        "high_burden_high_cardiometabolic_chronic_spared_cognitive": "High burden, cardiometabolic/chronic dominant with cognition spared",
        "high_burden_high_functional_spared_affective_cardiometabolic_chronic": "High burden, functional/cognitive dominant with affective and cardiometabolic/chronic partly spared",
        "high_burden_high_cardiometabolic_chronic_spared_functional_cognitive": "High burden, cardiometabolic/chronic dominant with function and cognition spared",
        "high_burden_severity_aligned": "High burden, severity aligned",
        "high_burden_high_affective_spared_cardiometabolic_chronic": "High burden, affective dominant with cardiometabolic/chronic spared",
        "high_burden_high_functional_spared_cognitive_cardiometabolic_chronic": "High burden, functional dominant with cognition and cardiometabolic/chronic spared",
        "intermediate_high_cardiometabolic_chronic_spared_functional_affective": "Intermediate burden, cardiometabolic/chronic high with function and affective symptoms spared",
    }

    family = (
        selected.groupby("profile_label")
        .agg(
            selected_classes=("profile_label", "size"),
            represented_cohorts=("cohort", lambda x: ", ".join(sorted(set(x)))),
            participants=("class_n", "sum"),
            min_class_pct=("class_pct", "min"),
            max_class_pct=("class_pct", "max"),
            mean_severity_z=("severity_mean", "mean"),
            mean_functional_z=("functional_score", "mean"),
            mean_cognitive_z=("cognitive_score", "mean"),
            mean_affective_z=("affective_score", "mean"),
            mean_cardiometabolic_chronic_z=("cardiometabolic_chronic_score", "mean"),
        )
        .reset_index()
    )
    total = family["participants"].sum()
    family["participant_pct_of_selected_profiles"] = family["participants"] / total * 100
    family["clinical_family"] = family["profile_label"].map(family_name).fillna(family["profile_label"])
    family["main_table_group"] = family.apply(
        lambda r: "recurrent family" if r["selected_classes"] >= 2 else "cohort-specific family",
        axis=1,
    )
    family = family[
        [
            "clinical_family",
            "main_table_group",
            "profile_label",
            "selected_classes",
            "represented_cohorts",
            "participants",
            "participant_pct_of_selected_profiles",
            "min_class_pct",
            "max_class_pct",
            "mean_severity_z",
            "mean_functional_z",
            "mean_cognitive_z",
            "mean_affective_z",
            "mean_cardiometabolic_chronic_z",
        ]
    ].sort_values(["main_table_group", "selected_classes", "participants"], ascending=[False, False, False])
    rounded = family.copy()
    for col in [
        "participant_pct_of_selected_profiles",
        "min_class_pct",
        "max_class_pct",
        "mean_severity_z",
        "mean_functional_z",
        "mean_cognitive_z",
        "mean_affective_z",
        "mean_cardiometabolic_chronic_z",
    ]:
        rounded[col] = rounded[col].round(2)
    rounded.to_csv(OUT / "phase33_profile_family_summary.csv", index=False)
    selected.to_csv(OUT / "phase33_selected_class_dictionary.csv", index=False)
    return rounded


def build_table_blueprints() -> tuple[pd.DataFrame, pd.DataFrame]:
    main_rows = [
        {
            "table": "Table 1",
            "recommended_placement": "Main",
            "action": "Revise current Table 1",
            "title": "Cohort roles, denominator locks, and validation availability",
            "reader_question": "Which cohorts support construction, validation, bridge sensitivity, or baseline-only description?",
            "core_columns": "Cohort; selected wave; role/tier; source women 50+; complete four-domain n (% of source); selected profile n/classes; validation n (% of profile); events (%); functional source tier; allowed claim",
            "data_source": "outputs/phase32_cohort_tier_lock.csv; outputs/phase28_gmm_selection_table.csv",
            "design_upgrade": "Use grouped headers for construction, validation, and claim status; right-align numbers; replace LASI 0 events with NA/not available; remove long raw variable strings from body and move to footnote.",
            "status": "must_add_or_revise",
        },
        {
            "table": "Table 2",
            "recommended_placement": "Main",
            "action": "Add new clinical core table",
            "title": "Clinical burden-profile families among selected GMM classes",
            "reader_question": "What clinical patterns did the profiles actually identify?",
            "core_columns": "Clinical family; recurrent/cohort-specific; selected classes; cohorts represented; participants (%); class-size range; four-domain signature; conservative clinical interpretation; caveat",
            "data_source": "outputs/phase33_profile_family_summary.csv; outputs/phase33_selected_class_dictionary.csv",
            "design_upgrade": "Collapse 28 selected classes into 5-7 readable family rows; keep full 28-row dictionary in supplement; use short domain chips such as F, Cog, Aff, CM rather than long prose in every cell.",
            "status": "must_add",
        },
        {
            "table": "Table 3",
            "recommended_placement": "Main",
            "action": "Revise current Table 3",
            "title": "Decoupled validation performance and model-stability guardrails",
            "reader_question": "Do profiles add validation value beyond continuous domain scores, and are models stable enough to trust?",
            "core_columns": "Cohort; tier; validation n/events/%; profile AUC; continuous three-domain AUC; delta AUC; delta AIC/1,000; ARI median/p10; covariance downgrade; locked interpretation",
            "data_source": "outputs/phase32_decoupled_validation_comparison.csv; outputs/phase32_gmm_stability_summary.csv",
            "design_upgrade": "Use comparator columns, not a single status sentence; normalize delta AIC by 1,000 participants; mark negative deltas as continuous-favored; no underscores in status text.",
            "status": "must_revise",
        },
        {
            "table": "Table 4",
            "recommended_placement": "Main or supplement depending on final page budget",
            "action": "Replace current Table 2 or move current Table 2 to supplement",
            "title": "Domain harmonization and comparability risk matrix",
            "reader_question": "Are functional, cognitive, affective, and cardiometabolic/chronic domains comparable enough for interpretation?",
            "core_columns": "Cohort; functional tier/items/nonmissing; cognitive tier/items/nonmissing; affective tier/items/nonmissing; cardiometabolic/chronic tier/items/nonmissing; reviewer-risk note",
            "data_source": "outputs/phase32_item_level_harmonization_crosswalk.csv; outputs/phase28_domain_harmonization_dictionary.csv",
            "design_upgrade": "Use a 7 by 4 cohort-domain matrix instead of comparability flag counts; show tier and nonmissing percent in each cell; use footnotes for CHARLS IADL-only, HRS ADL-only, KLoSA bridge, SHARE EURO-D.",
            "status": "must_have_either_main_table_or_main_figure",
        },
    ]
    supp_rows = [
        {
            "table": "Supplementary Table S1",
            "title": "Item-level harmonization crosswalk",
            "minimum_fields": "cohort, wave, domain, variable, construct, source tier, raw direction, score orientation, nonmissing n/%, used flag, comparability flag, reviewer-risk note",
            "data_source": "outputs/phase32_item_level_harmonization_crosswalk.csv",
            "purpose": "Defends domain construction at reviewer audit level.",
        },
        {
            "table": "Supplementary Table S2",
            "title": "GMM two-to-five class model selection and convergence",
            "minimum_fields": "cohort, classes, n, converged, BIC, AIC, entropy, mean posterior, min class %, selected flag, selection rule",
            "data_source": "outputs/phase28_gmm_selection_table.csv",
            "purpose": "Prevents black-box class-number criticism.",
        },
        {
            "table": "Supplementary Table S3",
            "title": "Full selected class dictionary",
            "minimum_fields": "cohort, class, n, %, posterior, four z-scored domains, severity mean, label, high/spared domains",
            "data_source": "outputs/phase33_selected_class_dictionary.csv",
            "purpose": "Allows readers to inspect every selected class behind Fig2 and main Table 2.",
        },
        {
            "table": "Supplementary Table S4",
            "title": "Full validation model metrics",
            "minimum_fields": "cohort, endpoint, n, events, event %, all comparator AIC/BIC/AUC columns, delta columns, separation flag",
            "data_source": "outputs/phase32_decoupled_validation_comparison.csv; outputs/phase28_validation_metrics_main.csv",
            "purpose": "Shows the continuous comparator result transparently.",
        },
        {
            "table": "Supplementary Table S5",
            "title": "Endpoint leakage and coupling audit",
            "minimum_fields": "cohort, endpoint kind, coupling level, baseline-function/event correlation, change-event correlation, baseline quartile event percentages, evidence status",
            "data_source": "outputs/phase32_functional_endpoint_leakage_audit.csv",
            "purpose": "Addresses the most serious validation-circularity criticism.",
        },
        {
            "table": "Supplementary Table S6",
            "title": "Covariance degeneracy and bootstrap stability diagnostics",
            "minimum_fields": "cohort, class, weight, min eigenvalue, determinant, condition number, near-singular flag, ARI median/p10/min",
            "data_source": "outputs/phase32_gmm_covariance_diagnostics.csv; outputs/phase32_gmm_stability_summary.csv",
            "purpose": "Documents why profiles are descriptive rather than stable latent endotypes.",
        },
        {
            "table": "Supplementary Table S7",
            "title": "Selection and missingness audit",
            "minimum_fields": "cohort, source women 50+, complete four-domain n/% retained, validation n/% retained, missingness driver by domain, role lock",
            "data_source": "outputs/phase32_cohort_tier_lock.csv; outputs/phase32_item_level_harmonization_crosswalk.csv",
            "purpose": "Needed because complete-case selection is not yet made visible enough.",
        },
        {
            "table": "Supplementary Table S8",
            "title": "Outcome and model specification dictionary",
            "minimum_fields": "endpoint, model family, covariates, comparator, fit metric, missingness rule, interpretation limit",
            "data_source": "outputs/phase28_outcome_model_specification.csv; scripts",
            "purpose": "Gives methods reproducibility without overloading main text.",
        },
    ]
    main = pd.DataFrame(main_rows)
    supp = pd.DataFrame(supp_rows)
    main.to_csv(OUT / "phase33_main_table_upgrade_blueprint.csv", index=False)
    supp.to_csv(OUT / "phase33_supplement_table_upgrade_blueprint.csv", index=False)
    return main, supp


def build_figure_blueprint() -> pd.DataFrame:
    rows = [
        {
            "figure": "Figure 1",
            "recommended_placement": "Main",
            "action": "Keep but retitle/reframe",
            "title": "Study architecture and denominator locks",
            "panels": "A: source to complete-domain to profile to validation counts; B: cohort role/tier guardrail; C optional: event burden by cohort",
            "data_source": "outputs/phase32_cohort_tier_lock.csv",
            "reader_question": "What is the seven-cohort construction versus six-cohort validation design?",
            "design_note": "Current A1 is appropriate; ensure LASI is shown as no follow-up validation, not 0 events.",
            "priority": "must_keep_main",
        },
        {
            "figure": "Figure 2",
            "recommended_placement": "Main",
            "action": "Keep but strengthen annotations",
            "title": "Clinically annotated multidomain burden-profile map",
            "panels": "Profile rows with class N/%; four-domain z-score matrix; clinical family; role/tier; event availability",
            "data_source": "outputs/phase33_selected_class_dictionary.csv; outputs/phase32_cohort_tier_lock.csv",
            "reader_question": "What clinical heterogeneity was mapped?",
            "design_note": "Keep B1 main. Add or preserve clinical family labels and avoid implying cross-cohort absolute equivalence of z-scores.",
            "priority": "must_keep_main",
        },
        {
            "figure": "Figure 3",
            "recommended_placement": "Main",
            "action": "Keep current G1",
            "title": "Validation and model-stability guardrails",
            "panels": "Decoupled validation delta AIC; bootstrap ARI; numeric guardrail table",
            "data_source": "outputs/phase32_decoupled_validation_comparison.csv; outputs/phase32_gmm_stability_summary.csv",
            "reader_question": "Do profiles outperform continuous scores, and are selected models stable?",
            "design_note": "Current G1 answers the reviewer guardrail. G2 remains Supplementary Figure S3.",
            "priority": "must_keep_main",
        },
        {
            "figure": "Figure 4",
            "recommended_placement": "Main if page budget allows; otherwise Supplementary Figure S4",
            "action": "Add",
            "title": "Cohort-domain harmonization risk matrix",
            "panels": "7 cohorts by 4 domains; cell color = strict/partial/bridge/unavailable; text = variable family and nonmissing %",
            "data_source": "outputs/phase32_item_level_harmonization_crosswalk.csv; outputs/phase28_domain_harmonization_dictionary.csv",
            "reader_question": "How comparable are the four domains across cohorts?",
            "design_note": "This is the strongest additional figure for reviewer confidence because harmonization is the manuscript's main vulnerability.",
            "priority": "must_add_main_or_supp",
        },
        {
            "figure": "Supplementary Figure S4/S5",
            "recommended_placement": "Supplement",
            "action": "Add",
            "title": "GMM model-selection and degeneracy diagnostics",
            "panels": "BIC delta by class number; min class %; entropy/posterior; covariance condition/eigenvalue; selected model flags",
            "data_source": "outputs/phase28_gmm_selection_table.csv; outputs/phase32_gmm_covariance_diagnostics.csv",
            "reader_question": "Were GMM classes selected transparently and are any numerical artifacts visible?",
            "design_note": "Use heatmap/dot-matrix grammar; do not crowd main text unless reviewers focus on modeling.",
            "priority": "should_add_supp",
        },
        {
            "figure": "Supplementary Figure S5/S6",
            "recommended_placement": "Supplement",
            "action": "Add",
            "title": "Functional endpoint coupling and leakage audit",
            "panels": "Baseline functional quartile event percentages; baseline-function/event correlation; decoupled endpoint status",
            "data_source": "outputs/phase32_functional_endpoint_leakage_audit.csv",
            "reader_question": "How much of the original validation endpoint was coupled to baseline functional input?",
            "design_note": "This should be supplemental unless the paper is framed mainly as a methodological cautionary study.",
            "priority": "should_add_supp",
        },
        {
            "figure": "Supplementary Figure S6/S7",
            "recommended_placement": "Supplement",
            "action": "Add if missingness is challenged",
            "title": "Complete-case and validation-retention funnel",
            "panels": "Per-cohort retained % from source to complete-domain and validation sets; domain missingness driver",
            "data_source": "outputs/phase32_cohort_tier_lock.csv; outputs/phase32_item_level_harmonization_crosswalk.csv",
            "reader_question": "Could selection or missingness bias the profile map?",
            "design_note": "Useful if Table 1 is still dense or reviewer asks for a flow diagram beyond denominator bars.",
            "priority": "optional_supp",
        },
    ]
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "phase33_figure_upgrade_blueprint.csv", index=False)
    return df


def fmt_int(x: object) -> str:
    if pd.isna(x):
        return "NA"
    return f"{int(round(float(x))):,}"


def fmt_pct(x: object) -> str:
    if pd.isna(x):
        return "NA"
    return f"{float(x):.1f}%"


def build_main_table_shells(family: pd.DataFrame) -> None:
    cohort = read_csv("phase32_cohort_tier_lock.csv")
    selected = read_csv("phase28_gmm_selection_table.csv")
    selected = selected.loc[selected["selected_model"].eq(1), ["cohort", "n_classes"]]
    cohort = cohort.merge(selected, on="cohort", how="left")

    validation = read_csv("phase32_decoupled_validation_comparison.csv")
    stability = read_csv("phase32_gmm_stability_summary.csv")
    t3 = validation.merge(
        stability[
            [
                "cohort",
                "median_ari_vs_reference",
                "p10_ari_vs_reference",
                "any_near_singular_covariance",
            ]
        ],
        on="cohort",
        how="left",
    )

    dictionary = read_csv("phase28_domain_harmonization_dictionary.csv")
    crosswalk = read_csv("phase32_item_level_harmonization_crosswalk.csv")
    risk = (
        crosswalk.groupby(["cohort", "domain"])
        .agg(
            flags=("comparability_flag", lambda x: "; ".join(sorted(set(map(str, x))))),
            notes=("comparability_note", lambda x: " | ".join(sorted(set(map(str, x)))[:2])),
        )
        .reset_index()
    )
    t4 = dictionary.merge(risk, on=["cohort", "domain"], how="left")

    display_family = family.copy()
    recurrent = display_family[display_family["main_table_group"].eq("recurrent family")]
    specific = display_family[display_family["main_table_group"].eq("cohort-specific family")]
    specific_row = {
        "clinical_family": "Cohort-specific high-burden variants",
        "main_table_group": "collapsed cohort-specific families",
        "selected_classes": int(specific["selected_classes"].sum()),
        "represented_cohorts": ", ".join(sorted(set(", ".join(specific["represented_cohorts"]).split(", ")))),
        "participants": int(specific["participants"].sum()),
        "participant_pct_of_selected_profiles": specific["participants"].sum()
        / display_family["participants"].sum()
        * 100,
        "min_class_pct": specific["min_class_pct"].min(),
        "max_class_pct": specific["max_class_pct"].max(),
        "mean_functional_z": specific["mean_functional_z"].mean(),
        "mean_cognitive_z": specific["mean_cognitive_z"].mean(),
        "mean_affective_z": specific["mean_affective_z"].mean(),
        "mean_cardiometabolic_chronic_z": specific["mean_cardiometabolic_chronic_z"].mean(),
    }
    main_family = pd.concat([recurrent, pd.DataFrame([specific_row])], ignore_index=True)

    lines: list[str] = []
    lines.extend(
        [
            "# Phase 33 Revised Main Table Shells",
            "",
            "These shells are data-driven drafts for the next manuscript rewrite. They are not final LaTeX styling. Convert to `threeparttable`/`tabularx`, avoid `\\tiny` where possible, and keep the explanatory footnotes.",
            "",
            "## Revised Table 1. Cohort roles, denominator locks, and validation availability",
            "",
            "| Cohort | Role/tier | Source women 50+ | Complete four-domain | Selected profiles/classes | Functional validation | Functional events | Functional source | Allowed main claim |",
            "|---|---|---:|---:|---:|---:|---:|---|---|",
        ]
    )
    for _, r in cohort.sort_values("baseline_women_age50plus_n").iterrows():
        source = r["baseline_women_age50plus_n"]
        complete = r["complete_four_domain_n"]
        profile = r["selected_endotype_n"]
        val = r["functional_deterioration_ge_0_5sd_available_n"]
        events = r["functional_deterioration_ge_0_5sd_event_n"]
        validation_cell = "NA; not available" if val == 0 else pct(val, profile)
        event_cell = "NA" if val == 0 else f"{fmt_int(events)} ({events / val * 100:.1f}%)"
        lines.append(
            f"| {r['cohort']} | {r['analysis_tier']} | {fmt_int(source)} | {pct(complete, source)} | {fmt_int(profile)} / {int(r['n_classes'])} | {validation_cell} | {event_cell} | {r['functional_source_tier']} | {r['allowed_main_claim']} |"
        )
    lines.extend(
        [
            "",
            "Footnote: Source, complete-domain, selected-profile and validation denominators are not interchangeable. LASI validation is unavailable in the current cleaned-data pass and must not be reported as zero events.",
            "",
            "## New Table 2. Clinical burden-profile families among selected GMM classes",
            "",
            "| Clinical family | Group | Classes | Cohorts | Participants | Class-size range | Mean domain z signature F/Cog/Aff/CM | Conservative reading |",
            "|---|---|---:|---|---:|---|---|---|",
        ]
    )
    for _, r in main_family.iterrows():
        participants = f"{int(r['participants']):,} ({r['participant_pct_of_selected_profiles']:.1f}%)"
        class_range = f"{r['min_class_pct']:.1f}-{r['max_class_pct']:.1f}%"
        signature = (
            f"{r['mean_functional_z']:.2f}/"
            f"{r['mean_cognitive_z']:.2f}/"
            f"{r['mean_affective_z']:.2f}/"
            f"{r['mean_cardiometabolic_chronic_z']:.2f}"
        )
        if "functional dominant" in r["clinical_family"]:
            reading = "Functional limitation is the main clinical signal."
        elif "severity aligned" in r["clinical_family"]:
            reading = "Domains move together as a general severity gradient."
        elif "cardiometabolic/chronic high" in r["clinical_family"]:
            reading = "Chronic disease burden dominates while function is relatively preserved."
        elif "cardiometabolic/chronic spared" in r["clinical_family"]:
            reading = "Lower cardiometabolic/chronic burden despite intermediate overall burden."
        else:
            reading = "Heterogeneous cohort-specific pattern; inspect full class dictionary."
        lines.append(
            f"| {r['clinical_family']} | {r['main_table_group']} | {int(r['selected_classes'])} | {r['represented_cohorts']} | {participants} | {class_range} | {signature} | {reading} |"
        )
    lines.extend(
        [
            "",
            "Footnote: Higher z-scores indicate worse burden. These families are descriptive clinical strata, not diagnoses or treatment-assignment groups. Full 28-class details should appear in Supplementary Table S3.",
            "",
            "## Revised Table 3. Decoupled validation performance and model-stability guardrails",
            "",
            "| Cohort | Tier | N/events | Profile AUC | 3-domain AUC | Delta AUC | Delta AIC/1,000 | ARI p50/p10 | Covariance status | Locked interpretation |",
            "|---|---|---:|---:|---:|---:|---:|---:|---|---|",
        ]
    )
    for _, r in t3.iterrows():
        valn = r["validation_n"]
        events = r["validation_events"]
        delta_aic_1k = r["delta_aic_three_domain_scores_minus_lfo_profile"] / valn * 1000
        cov = "downgraded" if int(r["any_near_singular_covariance"]) else "no downgrade"
        if r["analysis_tier"] == "bridge_sensitivity":
            interp = "Bridge only"
        elif r["cohort"] == "SHARE":
            interp = "Validation downgraded; continuous favored"
        else:
            interp = "Continuous favored"
        lines.append(
            f"| {r['cohort']} | {r['analysis_tier']} | {fmt_int(valn)} / {fmt_int(events)} | {r['auc_lfo_profile_age']:.3f} | {r['auc_three_domain_scores_age']:.3f} | {r['delta_auc_lfo_profile_minus_three_domain_scores']:.3f} | {delta_aic_1k:.1f} | {r['median_ari_vs_reference']:.2f}/{r['p10_ari_vs_reference']:.2f} | {cov} | {interp} |"
        )
    lines.extend(
        [
            "",
            "Footnote: Delta AIC is three-domain continuous score model minus leave-functional-domain-out profile model, scaled per 1,000 validation participants; negative values favor continuous scores. ARI is adjusted Rand index from bootstrap refits.",
            "",
            "## Revised Table 4. Domain harmonization and comparability risk matrix",
            "",
            "| Cohort | Functional | Cognitive | Affective | Cardiometabolic/chronic | Key reviewer risk |",
            "|---|---|---|---|---|---|",
        ]
    )
    domain_order = ["functional", "cognitive", "affective", "cardiometabolic_chronic"]
    for cohort_name in ["CHARLS", "ELSA", "HRS", "KLoSA", "LASI", "MHAS", "SHARE"]:
        row = t4[t4["cohort"].eq(cohort_name)]
        cells: dict[str, str] = {}
        risk_notes: list[str] = []
        for domain in domain_order:
            d = row[row["domain"].eq(domain)]
            if d.empty:
                cells[domain] = "NA"
                continue
            rr = d.iloc[0]
            variables = rr["variables"]
            if pd.isna(variables):
                variables = "source variable not listed"
            variables = str(variables)
            if len(variables) > 30:
                variables = variables[:27] + "..."
            cells[domain] = f"{rr['source_tier']}; {rr['nonmissing_pct']:.1f}%; {variables}"
            flags = str(rr.get("flags", ""))
            if "bridge" in flags or "partial" in flags or "non_cesd" in flags or "cohort_specific" in flags:
                risk_notes.append(f"{domain}: {flags}")
        risk_text = "; ".join(risk_notes[:3]) if risk_notes else "No major main-table flag beyond cohort-specific standardization."
        lines.append(
            f"| {cohort_name} | {cells['functional']} | {cells['cognitive']} | {cells['affective']} | {cells['cardiometabolic_chronic']} | {risk_text} |"
        )
    lines.extend(
        [
            "",
            "Footnote: This table should be visually implemented as a compact cohort-domain matrix. If Fig4 is added as a harmonization heatmap, this table can move to the supplement and remain machine-readable.",
            "",
        ]
    )
    (OUT / "phase33_revised_main_table_shells.md").write_text("\n".join(lines), encoding="utf-8")


def manuscript_section_map() -> dict[str, int]:
    text = MANUSCRIPT.read_text(encoding="utf-8")
    return {
        "word_count_approx": len(text.split()),
        "section_count": text.count("\\section{"),
        "subsection_count": text.count("\\subsection"),
        "table_count": text.count("\\begin{table}"),
        "figure_count": text.count("\\begin{figure}"),
        "has_limitations_section": int("\\section{Limitations}" in text or "Limitations" in text),
        "uses_endotype_in_title": int("endotype" in text.split("\\maketitle")[0].lower()),
    }


def write_audit(family: pd.DataFrame, main_tables: pd.DataFrame, supp_tables: pd.DataFrame, figures: pd.DataFrame) -> None:
    sec = manuscript_section_map()
    cohort = read_csv("phase32_cohort_tier_lock.csv")
    validation = read_csv("phase32_decoupled_validation_comparison.csv")
    stability = read_csv("phase32_gmm_stability_summary.csv")
    total_source = int(cohort["baseline_women_age50plus_n"].sum())
    total_profile = int(cohort["selected_endotype_n"].sum())
    strict_val = cohort.loc[cohort["analysis_tier"].eq("strict_primary"), "functional_deterioration_ge_0_5sd_available_n"].sum()
    strict_events = cohort.loc[cohort["analysis_tier"].eq("strict_primary"), "functional_deterioration_ge_0_5sd_event_n"].sum()
    strict_better = validation.loc[
        validation["analysis_tier"].eq("strict_primary")
        & validation["phase32b_evidence_status"].str.contains("three_domain_scores", na=False)
    ].shape[0]
    all_near_singular = int(stability["any_near_singular_covariance"].fillna(0).astype(int).sum())

    lines: list[str] = []
    lines.extend(
        [
            "# Phase 33 Skill-Based Manuscript Logic, Table, and Figure Audit",
            "",
            "Date: 2026-06-02",
            "",
            "Applied skills/assets:",
            "",
            "| Rank | Score | Recommendation | Skill or asset | Path | Best use | Limits |",
            "|---:|---:|---|---|---|---|---|",
            "| 1 | 94 | Primary | biomed-figure-redraw / PERSIST protocols | E:/Reserch/Skills/02_callable_skills/figure_publishing/biomed-figure-redraw/SKILL.md | Decide which additional manuscript figures are scientifically needed and how to source-code-first redraw them | This audit does not render new Fig4/Supp figures yet |",
            "| 2 | 86 | Supporting | Documents review workflow | C:/Users/luff9/.codex/plugins/cache/openai-primary-runtime/documents/26.601.10930/skills/documents | Full-text logic and layout/reading-flow review | Current manuscript is LaTeX/PDF, not DOCX |",
            "| 3 | 84 | Supporting | Spreadsheets scientific-research guidance | C:/Users/luff9/.codex/plugins/cache/openai-primary-runtime/spreadsheets/26.601.10930/skills/spreadsheets | Table architecture, machine-readable supplementary tables and reproducible table shells | Final journal LaTeX table styling still needs TeX implementation |",
            "",
            "## Executive Verdict",
            "",
            "The current BMC rescue manuscript is scientifically safer than the prior endotype draft, but it is too skeletal for a reviewer-ready clinical paper. The central statistical caution is now honest, but the paper has not yet rebuilt a positive clinical storyline around that caution.",
            "",
            f"Current source facts: {total_source:,} source-screen women 50+, {total_profile:,} selected profile assignments, {strict_val:,.0f} strict-primary validation rows with {strict_events:,.0f} strict-primary events. Continuous three-domain scores fit functional deterioration better than profile classes in {strict_better} strict validation cohorts. All seven selected cohort solutions have near-singular covariance downgrade flags ({all_near_singular}/7).",
            "",
            "The manuscript should therefore be framed as: a transparent, women-only, seven-cohort map of multidomain burden profiles plus a validation/stability guardrail showing why the profiles are descriptive clinical strata rather than stable latent endotypes or prediction tools.",
            "",
            "## Full-Text Logic Audit",
            "",
            "| Manuscript part | Current issue | Required revision | Priority |",
            "|---|---|---|---|",
            "| Title | The title is now conservative and no longer says endotype, which is correct. It still reads as a purely descriptive mapping paper and does not tell readers that the paper contains a major guardrail/comparator result. | Consider adding 'with validation and stability guardrails' only if title length permits; otherwise keep title and make abstract conclusion stronger. | Medium |",
            "| Abstract | It reports the negative comparator result, but the positive clinical contribution is weak: what the profiles reveal clinically is not summarized. | Add one sentence naming the recurrent clinical patterns, e.g. cardiometabolic/chronic-high function-spared profiles and functional-dominant high-burden profiles, while preserving the no-superiority conclusion. | High |",
            "| Background | The women-only rationale is thin. It says older women may have domain-specific burden, but does not explain why women-only cross-cohort mapping is clinically or epidemiologically justified. | Add a paragraph on sex-specific aging burden, longevity/disability burden, affective symptoms, multimorbidity, and why pooled-sex profiles could hide women-specific heterogeneity. | High |",
            "| Final introduction paragraph | Aim is appropriately modest but not operational enough. | State three aims: profile construction; harmonization audit; validation/stability guardrails against overclaiming. | High |",
            "| Methods: cohorts | Missing exact selected wave logic and follow-up interval details in the main text. | Add a compact methods table or paragraph with cohort wave, baseline year/wave, follow-up endpoint window if available, and why LASI lacks validation. | High |",
            "| Methods: domain construction | Current text gives domain names but not enough reproducibility in main text. | Add score construction details: item aggregation, missingness rule, z-standardization, orientation, and handling of cohort-specific global cognitive scores. | High |",
            "| Methods: GMM | Model-selection rule is present, but selected class counts and candidate 2-5 class diagnostics are hidden. | Keep concise main methods but ensure Supplementary Table S2 is cited. Add why GMM is descriptive, not discovery of latent diseases. | High |",
            "| Methods: validation | Decoupled validation is scientifically crucial but still hard to understand. | Add a short schematic sentence: four-domain profiles describe baseline; leave-functional-domain-out profiles test whether non-functional domains predict later function; continuous three-domain scores are the comparator. | High |",
            "| Results order | Harmonization appears before showing the clinical profile families. This makes the paper feel like an audit report before the reader sees the clinical object. | Reorder Results: denominators -> clinical profile families/Fig2 -> harmonization risks -> validation/stability guardrails. | High |",
            "| Results: profile interpretation | There is no main table translating Fig2 rows into clinical families. | Add new Table 2 from phase33_profile_family_summary.csv and cite it before Fig2. | Critical |",
            "| Results: validation | Table 3 and Fig3 now align, but table status text is too long and not visually clinical. | Redesign Table 3 around grouped performance/stability/claim columns with short claim labels. | Critical |",
            "| Discussion | Discussion correctly avoids overclaiming, but reads mostly negative. | First paragraph should say what descriptive mapping adds despite no prediction superiority: interpretable heterogeneity map, harmonization audit, and transparent non-superiority. | High |",
            "| Limitations | No dedicated limitations section; limitations are embedded in discussion. | Add a separate 'Strengths and limitations' or 'Limitations' paragraph/section with endpoint coupling, harmonization non-equivalence, complete-case selection, within-cohort validation, GMM degeneracy, no clinical actionability. | Critical |",
            "| Declarations | Placeholders are acceptable now, but final submission needs author completion. | Leave placeholders until author data are available; do not fabricate. | Submission gate |",
            "",
            f"Current structure audit: approx {sec['word_count_approx']:,} TeX tokens/words, {sec['table_count']} main tables, {sec['figure_count']} main figures, no dedicated limitations section flag = {sec['has_limitations_section']}.",
            "",
            "## Main Table Upgrade Plan",
            "",
        ]
    )
    for _, row in main_tables.iterrows():
        lines.extend(
            [
                f"### {row['table']}: {row['title']}",
                "",
                f"- Placement/action: {row['recommended_placement']}; {row['action']}.",
                f"- Reader question: {row['reader_question']}",
                f"- Core columns: {row['core_columns']}",
                f"- Data source: `{row['data_source']}`",
                f"- Design upgrade: {row['design_upgrade']}",
                f"- Status: `{row['status']}`",
                "",
            ]
        )

    lines.extend(
        [
            "## New Clinical Profile Family Table Evidence",
            "",
            "The following rows are generated from selected GMM classes only. They should drive the new main Table 2, with the full 28-class dictionary placed in the supplement.",
            "",
            "| Clinical family | Group | Classes | Cohorts | Participants | Participant % | Class % range | Mean F/Cog/Aff/CM z |",
            "|---|---|---:|---|---:|---:|---|---|",
        ]
    )
    for _, r in family.iterrows():
        lines.append(
            f"| {r['clinical_family']} | {r['main_table_group']} | {int(r['selected_classes'])} | {r['represented_cohorts']} | {int(r['participants']):,} | {r['participant_pct_of_selected_profiles']:.2f} | {r['min_class_pct']:.2f}-{r['max_class_pct']:.2f} | {r['mean_functional_z']:.2f}/{r['mean_cognitive_z']:.2f}/{r['mean_affective_z']:.2f}/{r['mean_cardiometabolic_chronic_z']:.2f} |"
        )

    lines.extend(
        [
            "",
            "Table 2 should not overinterpret these families as diagnoses or actionable treatment groups. The safest wording is 'clinical burden-profile families' or 'descriptive profile families'.",
            "",
            "## Supplementary Table Upgrade Plan",
            "",
            "| Table | Title | Minimum fields | Data source | Purpose |",
            "|---|---|---|---|---|",
        ]
    )
    for _, row in supp_tables.iterrows():
        lines.append(
            f"| {row['table']} | {row['title']} | {row['minimum_fields']} | `{row['data_source']}` | {row['purpose']} |"
        )

    lines.extend(
        [
            "",
            "## Table Visual Design Rules",
            "",
            "- Do not use `\\tiny` in main tables unless absolutely unavoidable; use `\\small`/`\\scriptsize`, `tabularx`, `adjustbox`, or split tables instead.",
            "- Use grouped column headers: `Construction`, `Validation`, `Model stability`, `Allowed claim`.",
            "- Use numbers as numbers: right-align N, events, percentages, AIC/AUC/ARI; keep text columns left-aligned.",
            "- Replace machine labels such as `three_domain_scores_fit_better_than_profiles` with short reader labels such as `continuous favored`.",
            "- Use `NA/not available` for LASI validation rather than `0 events`.",
            "- Move raw variable strings out of main table body when they create line wrapping; retain source tier and cite the full crosswalk.",
            "- Give every table a one-line interpretation footnote, not just definitions.",
            "- Keep color optional and print-safe. If color is used in PDFs, it must be redundant with text/tier codes.",
            "",
            "## Figure Upgrade Plan",
            "",
            "| Figure | Placement | Action | Title | Panels | Data source | Why it strengthens the manuscript | Priority |",
            "|---|---|---|---|---|---|---|---|",
        ]
    )
    for _, row in figures.iterrows():
        lines.append(
            f"| {row['figure']} | {row['recommended_placement']} | {row['action']} | {row['title']} | {row['panels']} | `{row['data_source']}` | {row['reader_question']} {row['design_note']} | {row['priority']} |"
        )

    lines.extend(
        [
            "",
            "## Should Additional Figures Be Added?",
            "",
            "Yes. The most important added figure is a cohort-domain harmonization risk matrix. The current manuscript says harmonization is a key limitation, but the main visual sequence does not show the measurement non-equivalence that justifies the conservative conclusion. If page budget allows, add it as main Figure 4; otherwise make it Supplementary Figure S4 and cite it prominently in Methods and Results.",
            "",
            "A GMM model-selection/stability diagnostic figure should be supplementary. Fig3 already exposes the main stability guardrail; the supplement should show the underlying 2-5 class BIC/min-class/entropy/covariance evidence.",
            "",
            "An endpoint leakage/coupling figure should be supplementary unless the manuscript is reframed as a primarily methodological warning. It is valuable because the endpoint-coupling issue was the prior fatal flaw.",
            "",
            "## Recommended Revised Main-Text Reading Order",
            "",
            "1. Background: clinical need for women-only multidomain burden mapping and risk of overinterpreting profiles.",
            "2. Methods: seven-cohort construction; four domains; GMM descriptive profile construction; harmonization audit; decoupled validation guardrail.",
            "3. Results 1: denominator and role lock (Table 1, Fig1).",
            "4. Results 2: what profiles look like clinically (new Table 2, Fig2).",
            "5. Results 3: harmonization risks that constrain interpretation (Table 4 or Fig4).",
            "6. Results 4: validation/comparator and stability guardrails (revised Table 3, Fig3).",
            "7. Discussion: descriptive value first, then why profiles are not prediction-superior or stable latent endotypes.",
            "",
            "## Pass/Fail Gates Before Manuscript Rewrite",
            "",
            "- Main Table 2 must exist, or the paper has no clinical interpretation anchor.",
            "- Table 1 must not show LASI as 0 validation events; it must show validation unavailable.",
            "- Table 3 must include delta AUC and delta AIC/1,000 plus ARI p10, not only median ARI.",
            "- A harmonization risk matrix must appear either as main Table 4/main Fig4 or as a prominently cited supplementary figure/table.",
            "- A limitations section must explicitly state endpoint coupling, harmonization non-equivalence, complete-case selection, within-cohort validation, and GMM degeneracy.",
            "- The abstract must name at least one concrete clinical pattern; otherwise the manuscript reads like only a negative methods audit.",
            "",
            "## Immediate Implementation Recommendation",
            "",
            "Do not add every proposed figure to the main paper. For BMC Geriatrics, the strongest package is four main tables and four main figures if page budget allows: Table 1 denominator lock, Table 2 clinical profile families, Table 3 validation/stability guardrails, Table 4 harmonization risk matrix; Fig1 denominator architecture, Fig2 profile heatmap, Fig3 validation/stability, Fig4 harmonization risk matrix. If this feels heavy, keep Table 4 in supplement and keep Fig4 as main because harmonization is easier to understand visually.",
            "",
        ]
    )
    (OUT / "phase33_logic_table_figure_skill_audit.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    family = build_profile_family_summary()
    main_tables, supp_tables = build_table_blueprints()
    figures = build_figure_blueprint()
    build_main_table_shells(family)
    write_audit(family, main_tables, supp_tables, figures)
    print(OUT / "phase33_logic_table_figure_skill_audit.md")
    print(OUT / "phase33_profile_family_summary.csv")
    print(OUT / "phase33_selected_class_dictionary.csv")
    print(OUT / "phase33_main_table_upgrade_blueprint.csv")
    print(OUT / "phase33_supplement_table_upgrade_blueprint.csv")
    print(OUT / "phase33_figure_upgrade_blueprint.csv")
    print(OUT / "phase33_revised_main_table_shells.md")


if __name__ == "__main__":
    main()
