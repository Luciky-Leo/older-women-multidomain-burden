from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


RUN_DATE = "2026-06-01"
TITLE = "Multidomain Aging Endotypes Among Older Women Across Seven International Aging Cohorts"
SHORT_TITLE = "Aging Endotypes Among Older Women"


VERIFIED_REFERENCE_ROWS = [
    {
        "queue_id": "R1",
        "phase15_source_id": "N1",
        "verification_status": "verified_core_adjacent",
        "use_in_clean_manuscript": "yes",
        "manuscript_role": "adjacent multidimensional aging trajectory evidence",
        "title": "Multidimensional trajectories of multimorbidity, functional status, cognitive performance, and depressive symptoms among diverse groups of older adults.",
        "authors_short": "Quinones AR; Nagel CL; Botoseneanu A; Newsom JT; Dorr DA; Kaye J; et al.",
        "journal": "Journal of Multimorbidity and Comorbidity",
        "year": "2022",
        "volume": "12",
        "issue": "",
        "pages_or_article": "26335565221143012",
        "doi": "10.1177/26335565221143012",
        "pmid": "36479143",
        "pmcid": "PMC9720836",
        "url": "https://pubmed.ncbi.nlm.nih.gov/36479143/",
        "notes": "Phase 15 N1 was confirmed and can be cited as adjacent work, not as a direct women-only seven-cohort endotype collision.",
    },
    {
        "queue_id": "R2",
        "phase15_source_id": "N4_corrected",
        "verification_status": "verified_replacement_for_phase15_N4",
        "use_in_clean_manuscript": "yes",
        "manuscript_role": "adjacent symptom-cluster and disability cohort evidence",
        "title": "Longitudinal associations between multimodal symptom clusters and functional disability in older adults: a comparative cohort analysis using SHARE, ELSA, and KLoSA.",
        "authors_short": "Zhang Q; Liu P; Xu X; Liao H; Yang Y; Xiong Y; et al.",
        "journal": "Scientific Reports",
        "year": "2025",
        "volume": "15",
        "issue": "1",
        "pages_or_article": "40802",
        "doi": "10.1038/s41598-025-24623-2",
        "pmid": "41258422",
        "pmcid": "PMC12630969",
        "url": "https://pubmed.ncbi.nlm.nih.gov/41258422/",
        "notes": "Use this verified article instead of the old Phase 15 N4 PMCID/URL.",
    },
    {
        "queue_id": "N4_old_hold",
        "phase15_source_id": "N4",
        "verification_status": "old_phase15_url_replaced_do_not_cite",
        "use_in_clean_manuscript": "no",
        "manuscript_role": "replaced by R2",
        "title": "Symptom clusters, disability and health-related quality of life in community-dwelling older adults",
        "authors_short": "",
        "journal": "",
        "year": "",
        "volume": "",
        "issue": "",
        "pages_or_article": "",
        "doi": "",
        "pmid": "",
        "pmcid": "PMC12434884",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC12434884/",
        "notes": "The old Phase 15 N4 PMCID/URL should not be cited. Use R2 after final author approval.",
    },
    {
        "queue_id": "R3",
        "phase15_source_id": "N5_corrected",
        "verification_status": "verified_replacement_for_phase15_N5",
        "use_in_clean_manuscript": "yes",
        "manuscript_role": "adjacent predeath memory, depression, and mobility trajectory evidence",
        "title": "Long-term trajectories of memory, depression, and mobility independence before death: a multi-cohort study.",
        "authors_short": "Jiao J; Guo J; Shen J; Liu S; Zhang L; Sun D; et al.",
        "journal": "Translational Psychiatry",
        "year": "2026",
        "volume": "16",
        "issue": "1",
        "pages_or_article": "",
        "doi": "10.1038/s41398-026-03997-5",
        "pmid": "41916958",
        "pmcid": "PMC13039425",
        "url": "https://pubmed.ncbi.nlm.nih.gov/41916958/",
        "notes": "Use this verified article instead of the old Phase 15 N5 PMCID/URL.",
    },
    {
        "queue_id": "N5_old_hold",
        "phase15_source_id": "N5",
        "verification_status": "old_phase15_url_replaced_do_not_cite",
        "use_in_clean_manuscript": "no",
        "manuscript_role": "replaced by R3",
        "title": "Trajectories of Depressive Symptoms, Memory Function, and Mobility Before Death",
        "authors_short": "",
        "journal": "",
        "year": "",
        "volume": "",
        "issue": "",
        "pages_or_article": "",
        "doi": "",
        "pmid": "",
        "pmcid": "PMC11356518",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC11356518/",
        "notes": "The old Phase 15 N5 PMCID/URL resolved to an unrelated article during Phase 19 checking. Use R3 after final author approval.",
    },
    {
        "queue_id": "N2_hold",
        "phase15_source_id": "N2",
        "verification_status": "old_phase15_url_unrelated_do_not_cite",
        "use_in_clean_manuscript": "no",
        "manuscript_role": "removed pending replacement",
        "title": "Sex Differences in Intrinsic Capacity Domains and Their Associations With Adverse Health Outcomes Across Four Aging Cohorts",
        "authors_short": "",
        "journal": "",
        "year": "",
        "volume": "",
        "issue": "",
        "pages_or_article": "",
        "doi": "",
        "pmid": "",
        "pmcid": "PMC12317657",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC12317657/",
        "notes": "The PMCID checked during Phase 19 resolved to an unrelated article. Replace before citing.",
    },
    {
        "queue_id": "N3_hold",
        "phase15_source_id": "N3",
        "verification_status": "old_phase15_url_unrelated_do_not_cite",
        "use_in_clean_manuscript": "no",
        "manuscript_role": "removed pending replacement",
        "title": "Trajectories of intrinsic capacity and their associations with adverse outcomes",
        "authors_short": "",
        "journal": "",
        "year": "",
        "volume": "",
        "issue": "",
        "pages_or_article": "",
        "doi": "",
        "pmid": "",
        "pmcid": "PMC11625515",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC11625515/",
        "notes": "The PMCID checked during Phase 19 resolved to an unrelated article. Replace before citing.",
    },
    {
        "queue_id": "N6_hold",
        "phase15_source_id": "N6",
        "verification_status": "old_phase15_url_unrelated_do_not_cite",
        "use_in_clean_manuscript": "no",
        "manuscript_role": "removed pending replacement",
        "title": "Measurement of Healthy Ageing",
        "authors_short": "",
        "journal": "",
        "year": "",
        "volume": "",
        "issue": "",
        "pages_or_article": "",
        "doi": "",
        "pmid": "",
        "pmcid": "PMC11298082",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC11298082/",
        "notes": "The PMCID checked during Phase 19 resolved to an unrelated article. Replace before citing.",
    },
    {
        "queue_id": "N7_optional",
        "phase15_source_id": "N7",
        "verification_status": "preprint_optional_not_core",
        "use_in_clean_manuscript": "no",
        "manuscript_role": "optional background only after target-journal policy check",
        "title": "Lifecourse systemic inflammation and healthy ageing: a five-cohort study",
        "authors_short": "",
        "journal": "medRxiv",
        "year": "2025",
        "volume": "",
        "issue": "",
        "pages_or_article": "",
        "doi": "10.1101/2025.10.22.25338202",
        "pmid": "",
        "pmcid": "",
        "url": "https://www.medrxiv.org/content/10.1101/2025.10.22.25338202v1",
        "notes": "Do not use as a core novelty comparator unless the target journal permits preprint citations and the record is rechecked.",
    },
]


TARGET_JOURNAL_ROWS = [
    {
        "target_journal": "Journal of Gerontology: Medical Sciences",
        "fit": "high",
        "likely_article_type": "Original research",
        "why_fit": "Geriatric epidemiology, aging phenotypes, functional and mortality outcomes, and cross-cohort methods all fit the journal scope.",
        "main_risk": "The manuscript needs tight clinical interpretation and should not read as a purely methodological clustering paper.",
        "action_before_submission": "After choosing this target, live-check word limits, abstract format, table/figure limits, and data-sharing language.",
    },
    {
        "target_journal": "Age and Ageing",
        "fit": "high",
        "likely_article_type": "Research paper",
        "why_fit": "Clinically interpretable older-adult heterogeneity and functional deterioration are central to the paper.",
        "main_risk": "Negative or mixed prediction-superiority findings must be framed as clinically useful heterogeneity mapping.",
        "action_before_submission": "Shorten discussion, sharpen clinical implications, and live-check target-specific reporting requirements.",
    },
    {
        "target_journal": "BMC Geriatrics",
        "fit": "moderate_high",
        "likely_article_type": "Research article",
        "why_fit": "The journal is suitable for observational geriatric cohort analyses with transparent harmonization and sensitivity work.",
        "main_risk": "Novelty may be challenged unless the women-only and seven-cohort positioning is explicit.",
        "action_before_submission": "Prepare STROBE-style reporting, detailed supplement tables, and live-check current editorial policies.",
    },
    {
        "target_journal": "Journal of the American Geriatrics Society",
        "fit": "moderate",
        "likely_article_type": "Original investigation",
        "why_fit": "The topic is clinically relevant for aging heterogeneity, function, and mortality among older women.",
        "main_risk": "The current draft may be too method-heavy and international-cohort-harmonization-heavy for the clinical readership.",
        "action_before_submission": "Rework the framing around geriatric assessment and care implications before checking current author instructions.",
    },
    {
        "target_journal": "Journals of Gerontology: Series B",
        "fit": "conditional",
        "likely_article_type": "Research article",
        "why_fit": "Cognitive, affective, and social-behavioral aging framing could fit if the paper is shifted away from medical endpoints.",
        "main_risk": "The cardiometabolic and mortality emphasis may fit less well than in medical gerontology journals.",
        "action_before_submission": "Use only if the final story emphasizes cognitive-affective heterogeneity; live-check scope and format first.",
    },
]


def read_csv(output_dir: Path, name: str) -> pd.DataFrame:
    path = output_dir / name
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path, low_memory=False)


def fmt_int(value: object) -> str:
    if pd.isna(value):
        return "0"
    return f"{int(round(float(value))):,}"


def fmt_pct(value: object) -> str:
    if pd.isna(value):
        return "NA"
    return f"{float(value):.1f}%"


def fmt_num(value: object, digits: int = 1) -> str:
    if pd.isna(value):
        return "NA"
    return f"{float(value):.{digits}f}"


def clean_cell(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).replace("\n", " ").replace("|", "/").strip()


def markdown_table(frame: pd.DataFrame, columns: list[str]) -> str:
    if frame.empty:
        return "_No rows._"
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for _, row in frame.iterrows():
        lines.append("| " + " | ".join(clean_cell(row.get(column, "")) for column in columns) + " |")
    return "\n".join(lines)


def numeric_sum(frame: pd.DataFrame, column: str) -> int:
    if column not in frame:
        return 0
    return int(pd.to_numeric(frame[column], errors="coerce").fillna(0).sum())


def endpoint_totals(validation: pd.DataFrame, endpoint_contains: str) -> tuple[int, int, int]:
    mask = validation["endpoint"].astype(str).str.contains(endpoint_contains, case=False, regex=False, na=False)
    subset = validation[mask]
    return len(subset), numeric_sum(subset, "n_endotype"), numeric_sum(subset, "events_endotype")


def build_reference_queue(phase15_sources: pd.DataFrame) -> pd.DataFrame:
    verified = pd.DataFrame(VERIFIED_REFERENCE_ROWS)
    if phase15_sources.empty:
        return verified
    source_lookup = phase15_sources[["source_id", "title", "url"]].rename(
        columns={
            "source_id": "phase15_source_id",
            "title": "phase15_original_title",
            "url": "phase15_original_url",
        }
    )
    queue = verified.merge(source_lookup, on="phase15_source_id", how="left")
    queue["phase19_action"] = queue.apply(reference_action, axis=1)
    return queue


def reference_action(row: pd.Series) -> str:
    status = str(row.get("verification_status", ""))
    if status.startswith("verified"):
        return "Allowed in clean manuscript reference list."
    if "preprint" in status:
        return "Hold out of clean manuscript unless target journal permits and authors decide it is needed."
    return "Do not cite until a correct PMID/DOI/PMCID is verified."


def formatted_references(reference_queue: pd.DataFrame) -> list[str]:
    refs = []
    use = reference_queue[reference_queue["use_in_clean_manuscript"].eq("yes")].copy()
    for i, row in enumerate(use.to_dict("records"), start=1):
        issue = f"({row['issue']})" if row.get("issue") else ""
        article = f":{row['pages_or_article']}" if row.get("pages_or_article") else ""
        doi = f" doi:{row['doi']}." if row.get("doi") else ""
        refs.append(
            f"{i}. {row['authors_short']} {row['title']} {row['journal']}. "
            f"{row['year']};{row['volume']}{issue}{article}.{doi}"
        )
    return refs


def label_action(row: pd.Series) -> str:
    marker = str(row.get("phase18_marker", ""))
    decision = str(row.get("phase18_decision_v0", ""))
    if marker == "signoff":
        return "Approve conservative label or replace with reviewer-preferred domain wording."
    if marker == "caveat":
        return "Approve caveat wording and confirm the label is not interpreted as a mortality-driven phenotype."
    if marker == "hold" or "baseline_only" in decision:
        return "Confirm baseline-only display and exclude from follow-up validation claims."
    return "No required action unless the clinical reviewer edits wording."


def build_label_signoff_sheet(decisions: pd.DataFrame) -> pd.DataFrame:
    sheet = decisions.copy()
    sheet["recommended_signoff_action"] = sheet.apply(label_action, axis=1)
    sheet["signoff_decision"] = ""
    sheet["reviewer"] = ""
    sheet["review_date"] = ""
    sheet["notes"] = ""
    keep = [
        "cohort",
        "class_id",
        "class",
        "phase18_label_en_v0",
        "phase18_decision_v0",
        "phase18_marker",
        "human_signoff_required",
        "phase18_rationale",
        "phase15_review_reason",
        "phase14_stability_flag_count",
        "phase14_flag_reasons",
        "recommended_signoff_action",
        "signoff_decision",
        "reviewer",
        "review_date",
        "notes",
    ]
    return sheet[keep].sort_values(["human_signoff_required", "cohort", "class_id"], ascending=[False, True, True])


def build_reference_corrections(reference_queue: pd.DataFrame) -> str:
    hold = reference_queue[reference_queue["use_in_clean_manuscript"].ne("yes")].copy()
    corrected = reference_queue[reference_queue["use_in_clean_manuscript"].eq("yes")].copy()
    lines = [
        "# Phase 19 Reference Corrections",
        "",
        f"Generated: {RUN_DATE}.",
        "",
        "Phase 15 used a novelty-refresh source log, not a formal reference list. Phase 19 checked the source identifiers before building the clean manuscript package and found that several Phase 15 PMCID rows were wrong or unsuitable for direct citation.",
        "",
        "## Verified References Allowed In Clean Draft",
        "",
        markdown_table(
            corrected[
                [
                    "queue_id",
                    "phase15_source_id",
                    "title",
                    "journal",
                    "year",
                    "doi",
                    "pmid",
                    "pmcid",
                    "url",
                ]
            ],
            ["queue_id", "phase15_source_id", "title", "journal", "year", "doi", "pmid", "pmcid", "url"],
        ),
        "",
        "## Rows Held Out Of The Clean Draft",
        "",
        markdown_table(
            hold[["queue_id", "phase15_source_id", "verification_status", "url", "phase19_action", "notes"]],
            ["queue_id", "phase15_source_id", "verification_status", "url", "phase19_action", "notes"],
        ),
        "",
        "## Practical Rule",
        "",
        "Do not copy the Phase 15 `References To Format` list into a submission draft. Use `manuscript/references_verified_v0.md` and `outputs/phase19_verified_reference_queue.csv` until a fresh target-journal reference check is completed.",
    ]
    return "\n".join(lines) + "\n"


def build_references_markdown(reference_queue: pd.DataFrame) -> str:
    lines = [
        "# Verified References v0",
        "",
        f"Generated: {RUN_DATE}.",
        "",
        "These references were retained for the clean target-neutral draft. Rows marked as hold or optional are kept in `outputs/phase19_verified_reference_queue.csv` but not cited here.",
        "",
    ]
    lines.extend(formatted_references(reference_queue))
    lines.append("")
    return "\n".join(lines)


def summarize_counts(table1: pd.DataFrame, validation: pd.DataFrame, decisions: pd.DataFrame) -> dict[str, object]:
    strict = table1[table1["analysis_tier"].astype(str).str.contains("strict", case=False, na=False)]
    bridge = table1[table1["analysis_tier"].astype(str).str.contains("bridge", case=False, na=False)]
    baseline_profile = table1[table1["manuscript_role"].astype(str).str.contains("baseline", case=False, na=False)]
    functional_rows, functional_n, functional_events = endpoint_totals(validation, "Functional deterioration")
    mortality_rows, mortality_n, mortality_events = endpoint_totals(validation, "mortality")
    chronic_rows, chronic_n, chronic_events = endpoint_totals(validation, "Chronic progression")
    return {
        "baseline_n": numeric_sum(table1, "baseline_women_age50plus_n"),
        "strict_selected_n": numeric_sum(strict, "selected_endotype_n"),
        "bridge_selected_n": numeric_sum(bridge, "selected_endotype_n"),
        "baseline_profile_selected_n": numeric_sum(baseline_profile, "selected_endotype_n"),
        "selected_endotype_n": numeric_sum(table1, "selected_endotype_n"),
        "n_classes": len(decisions),
        "human_signoff_n": int(pd.to_numeric(decisions["human_signoff_required"], errors="coerce").fillna(0).sum()),
        "accepted_n": int(decisions["phase18_decision_v0"].eq("accepted_from_phase16").sum()),
        "caveat_n": int(decisions["phase18_decision_v0"].eq("locked_with_caveat_auto_v0").sum()),
        "renamed_n": int(decisions["phase18_decision_v0"].eq("auto_renamed_conservative").sum()),
        "hold_n": int(decisions["phase18_decision_v0"].eq("baseline_only_hold").sum()),
        "functional_rows": functional_rows,
        "functional_n": functional_n,
        "functional_events": functional_events,
        "mortality_rows": mortality_rows,
        "mortality_n": mortality_n,
        "mortality_events": mortality_events,
        "chronic_rows": chronic_rows,
        "chronic_n": chronic_n,
        "chronic_events": chronic_events,
    }


def build_clean_manuscript(
    table1: pd.DataFrame,
    validation: pd.DataFrame,
    decisions: pd.DataFrame,
    reference_queue: pd.DataFrame,
) -> str:
    counts = summarize_counts(table1, validation, decisions)
    refs = formatted_references(reference_queue)
    ref_intro = " ".join(["[1]", "[2]", "[3]"])
    lines = [
        f"# {TITLE}",
        "",
        "## Abstract",
        "",
        "### Background",
        "",
        "Aging phenotypes among older women are often represented by single severity or frailty scales, although functional, cognitive, affective, and cardiometabolic burdens may combine in clinically distinct patterns. We evaluated whether multidomain endotype profiles can summarize this heterogeneity across international aging cohort systems.",
        "",
        "### Methods",
        "",
        "We analyzed cleaned data from seven aging cohorts: CHARLS, ELSA, HRS, KLoSA, LASI, MHAS, and SHARE. Women aged 50 years or older were screened at cohort-specific baseline. Four domain scores were constructed for functional, cognitive, affective, and cardiometabolic/chronic disease burden, with higher scores indicating worse burden. Cohort-specific Gaussian mixture models were used to derive multidomain endotype profiles. Functional deterioration was treated as the primary validation endpoint. Mortality was analyzed as a secondary endpoint because proportional-hazards and time-stability diagnostics flagged selected class terms. Endotype models were compared with severity-tertile and continuous four-domain score comparators.",
        "",
        "### Results",
        "",
        f"The baseline screen included {fmt_int(counts['baseline_n'])} women aged 50 years or older. The selected endotype construction contributed {fmt_int(counts['strict_selected_n'])} strict-primary assignments and {fmt_int(counts['bridge_selected_n'])} bridge-sensitivity assignments. The final Phase 18 auto-v0 dictionary contained {fmt_int(counts['n_classes'])} cohort-specific classes. Functional deterioration validation included {fmt_int(counts['functional_rows'])} cohort rows, {fmt_int(counts['functional_n'])} participants, and {fmt_int(counts['functional_events'])} events. Mortality validation included {fmt_int(counts['mortality_rows'])} cohort rows, {fmt_int(counts['mortality_n'])} participants, and {fmt_int(counts['mortality_events'])} deaths. Endotype profiles showed interpretable multidomain heterogeneity, but continuous four-domain score models generally outperformed endotype-only models.",
        "",
        "### Conclusions",
        "",
        "Women-only multidomain endotypes can summarize clinically interpretable aging heterogeneity across international cohorts. The current evidence supports an interpretability and heterogeneity-mapping contribution rather than a universal prediction-superiority claim.",
        "",
        "## Introduction",
        "",
        "Frailty indices, intrinsic-capacity frameworks, and single-domain functional transitions are useful for studying aging, but they can compress heterogeneous aging processes into a single severity continuum. This compression is a particular limitation when studying older women, for whom functional, cognitive, affective, and cardiometabolic burdens may cluster in clinically different ways even when overall burden appears similar.",
        "",
        f"Recent studies have examined multidimensional aging trajectories, multimodal symptom clusters, and predeath trajectories in older-adult cohorts {ref_intro}. These studies reduce the room for broad novelty claims about multidomain aging analysis in general. The present study therefore uses a narrower claim: a women-focused, seven-cohort analysis of multidomain aging endotypes with explicit comparator and sensitivity guardrails.",
        "",
        "## Methods",
        "",
        "### Study Design And Cohorts",
        "",
        "We used cleaned cohort CSV files from CHARLS, ELSA, HRS, KLoSA, LASI, MHAS, and SHARE. The primary population was women aged 50 years or older at the cohort-specific baseline or selected analysis wave. Source data were treated as read-only, and all derived artifacts were written to the project `outputs/` and `manuscript/` directories.",
        "",
        "### Domain Construction",
        "",
        "Four domain scores were constructed: functional burden, cognitive burden, affective burden, and cardiometabolic/chronic disease burden. Scores were oriented so that higher values represented worse burden. Domain construction used the cleaned harmonized variables available in each cohort, with bridge rules retained for KLoSA and SHARE where the strict functional-domain definition was not fully available. LASI contributed baseline endotype profiles but remains excluded from follow-up validation in the current cleaned CSV pass.",
        "",
        "### Endotype Modeling",
        "",
        "Cohort-specific Gaussian mixture models were fit to the multidomain scores. Model selection used convergence, Bayesian information criterion, minimum class-size rules, and clinical interpretability. The selected classes were labeled using conservative domain-profile language. Labels with mortality drift, covariate-sensitivity flags, or baseline-only status retained explicit caveat or hold markers until human signoff.",
        "",
        "### Outcome Validation",
        "",
        "Functional deterioration was the primary validation endpoint. Chronic disease progression and all-cause mortality were secondary validation endpoints. Mortality estimates were interpreted cautiously because proportional-hazards diagnostics and early/late piecewise sensitivity flagged selected cohort-class terms. Comparator models included severity tertiles, continuous severity scores, outcome-matched domain scores, continuous four-domain score models, and diagnostic endotype-plus-domain models.",
        "",
        "## Results",
        "",
        "### Cohort Readiness",
        "",
        f"Across the seven cleaned cohorts, the women aged 50 years or older baseline screen included {fmt_int(counts['baseline_n'])} participants. Strict-primary endotype construction contributed {fmt_int(counts['strict_selected_n'])} selected assignments. KLoSA and SHARE contributed {fmt_int(counts['bridge_selected_n'])} bridge-sensitivity assignments. LASI remained baseline-profile only for follow-up validation in this cleaned CSV pass.",
        "",
        "### Endotype Profile Structure",
        "",
        f"The selected models produced {fmt_int(counts['n_classes'])} cohort-specific classes. Phase 18 auto-v0 labeling accepted {fmt_int(counts['accepted_n'])} labels from the Phase 16 dictionary, retained {fmt_int(counts['caveat_n'])} labels with explicit sensitivity caveats, conservatively renamed {fmt_int(counts['renamed_n'])} generic severity-aligned labels, and kept {fmt_int(counts['hold_n'])} LASI labels as baseline-only profiles. These labels are appropriate for collaborator review but not for submission without final signoff.",
        "",
        "### Functional Deterioration",
        "",
        f"Functional deterioration validation included {fmt_int(counts['functional_rows'])} cohort rows, {fmt_int(counts['functional_n'])} participants, and {fmt_int(counts['functional_events'])} events. The endotype-versus-severity pattern was mixed across cohorts. Continuous four-domain score models generally fit better than endotype-only models for functional deterioration, supporting a heterogeneity-mapping interpretation rather than a prediction-superiority claim.",
        "",
        "### Mortality",
        "",
        f"Mortality validation included {fmt_int(counts['mortality_rows'])} cohort rows, {fmt_int(counts['mortality_n'])} participants, and {fmt_int(counts['mortality_events'])} deaths. Mortality remained secondary because selected class terms showed proportional-hazards, piecewise, or covariate-sensitivity concerns. Mortality-related labels should therefore remain baseline domain-profile labels rather than outcome-driven phenotype names.",
        "",
        "### Comparator Guardrail",
        "",
        "Across tested endpoint-cohort rows, endotype-only models did not consistently outperform continuous four-domain score models. The defensible manuscript claim is that multidomain endotypes provide an interpretable clinical summary of aging heterogeneity among older women, with endpoint-specific outcome relevance, not that class membership is universally stronger than continuous domain scores.",
        "",
        "## Discussion",
        "",
        "This women-only analysis identified interpretable multidomain aging profiles across several international cohort systems. Several profiles were not reducible to a single low-to-high severity gradient and instead showed functional, cardiometabolic, affective, cognitive, or spared-domain structure. This supports a descriptive and interpretive contribution: multidomain endotypes can summarize clinically meaningful heterogeneity among older women.",
        "",
        "The results should be interpreted with an explicit comparator guardrail. Continuous four-domain score models generally outperformed endotype-only models, indicating that endotype membership should be viewed as a compact clinical summary rather than a universally stronger risk model. This distinction should remain central in the abstract, results, and discussion.",
        "",
        "The study has several limitations. First, this analysis used cleaned CSV variables rather than a full raw-file harmonization pass. Second, cohort differences in measurement may influence the shape and interpretation of domain scores. Third, KLoSA and SHARE used bridge definitions for selected domains. Fourth, LASI lacks follow-up validation in the current cleaned CSV pass. Fifth, expanded-core covariate coverage remains incomplete in several cohorts. Finally, selected mortality class terms showed time-drift or proportional-hazards concerns, so mortality should remain secondary unless additional sensitivity analyses support stronger claims.",
        "",
        "## Pre-Submission Blockers",
        "",
        f"This clean draft remains blocked by {fmt_int(counts['human_signoff_n'])} label signoffs. The target journal has not been selected, so author guidelines, abstract format, word limits, reporting checklist requirements, and reference style still require live checking. The Figure 1 display decision also remains open: main validation only versus seven-cohort sensitivity display. The LASI display decision must remain baseline-profile only unless follow-up data are added.",
        "",
        "## References",
        "",
    ]
    lines.extend(refs)
    lines.append("")
    return "\n".join(lines)


def build_title_page(table1: pd.DataFrame, decisions: pd.DataFrame) -> str:
    baseline_n = numeric_sum(table1, "baseline_women_age50plus_n")
    return "\n".join(
        [
            f"# {TITLE}",
            "",
            f"Running title: {SHORT_TITLE}",
            "",
            "Authors: [Author 1], [Author 2], [Author 3], [Consortium/Group if applicable]",
            "",
            "Affiliations: [Institutional affiliations to be completed]",
            "",
            "Corresponding author: [Name, postal address, email]",
            "",
            "Word count: [To be calculated after target-journal formatting]",
            "",
            "Tables and figures: Table 1-3 draft, Figure 1 main-validation candidate, Figure 1 seven-cohort sensitivity candidate.",
            "",
            f"Study population: {fmt_int(baseline_n)} women aged 50 years or older screened across CHARLS, ELSA, HRS, KLoSA, LASI, MHAS, and SHARE.",
            "",
            f"Label status: {fmt_int(len(decisions))} Phase 18 auto-v0 labels, with {fmt_int(pd.to_numeric(decisions['human_signoff_required'], errors='coerce').fillna(0).sum())} labels requiring human signoff before submission.",
            "",
            "Data availability statement: The analysis used cleaned files derived from CHARLS, ELSA, HRS, KLoSA, LASI, MHAS, and SHARE. Final wording must follow each cohort data-use agreement and the selected journal policy.",
            "",
            "Funding: [To be completed]",
            "",
            "Conflicts of interest: [To be completed]",
            "",
            "Ethics approval: [To be completed according to each source cohort and local institutional requirements]",
            "",
            "Author contributions: [CRediT roles to be completed]",
            "",
        ]
    )


def build_cover_letter() -> str:
    return "\n".join(
        [
            "# Cover Letter Skeleton",
            "",
            "Dear Editor,",
            "",
            f"We are pleased to submit the manuscript entitled \"{TITLE}\" for consideration as a [article type] in [target journal].",
            "",
            "This manuscript analyzes multidomain aging endotypes among women aged 50 years or older across seven international aging cohorts: CHARLS, ELSA, HRS, KLoSA, LASI, MHAS, and SHARE. The study focuses on clinically interpretable heterogeneity across functional, cognitive, affective, and cardiometabolic/chronic disease domains, and evaluates associations with functional deterioration and all-cause mortality using explicit comparator and sensitivity guardrails.",
            "",
            "The main contribution is not a new generic frailty index or a claim that latent classes universally outperform continuous risk scores. Instead, the manuscript provides a women-focused cross-cohort endotype map and shows where these profiles have endpoint-specific validation while preserving a conservative interpretation when four-domain continuous-score models perform better.",
            "",
            "We believe the manuscript will be of interest to readers of [target journal] because it addresses aging heterogeneity, functional decline, and risk stratification in older women using multiple international cohort systems.",
            "",
            "The manuscript is original, is not under consideration elsewhere, and all authors have approved the submission. Data-use, ethics, funding, conflict-of-interest, and author-contribution statements will be finalized according to the selected journal requirements.",
            "",
            "Sincerely,",
            "",
            "[Corresponding author name]",
            "[Affiliation]",
            "[Email]",
            "",
            "Internal pre-submission note: remove this line before submission after label signoff, target-journal guideline checks, and data-use statement finalization.",
            "",
        ]
    )


def build_package_index(output_dir: Path, manuscript_dir: Path, counts: dict[str, object]) -> str:
    rows = [
        {
            "artifact": "Clean target-neutral manuscript",
            "path": str(manuscript_dir / "clean_manuscript_target_neutral.md"),
            "use": "Main collaborator-review manuscript draft",
        },
        {
            "artifact": "Verified references",
            "path": str(manuscript_dir / "references_verified_v0.md"),
            "use": "Reference list allowed in the clean draft",
        },
        {
            "artifact": "Reference correction memo",
            "path": str(output_dir / "phase19_reference_corrections.md"),
            "use": "Documents Phase 15 source rows held out or corrected",
        },
        {
            "artifact": "Label signoff sheet",
            "path": str(output_dir / "phase19_label_signoff_sheet.csv"),
            "use": "Human signoff workflow for labels and caveats",
        },
        {
            "artifact": "Target journal decision matrix",
            "path": str(output_dir / "phase19_target_journal_decision_matrix.csv"),
            "use": "Target-neutral journal triage; requires live author-guideline check after target selection",
        },
        {
            "artifact": "Title page draft",
            "path": str(manuscript_dir / "title_page_draft.md"),
            "use": "Submission metadata skeleton",
        },
        {
            "artifact": "Cover letter skeleton",
            "path": str(manuscript_dir / "cover_letter_skeleton.md"),
            "use": "Target-journal cover letter starting point",
        },
    ]
    lines = [
        "# Phase 19 Clean Submission Package Index",
        "",
        f"Generated: {RUN_DATE}.",
        "",
        f"Current blocking label signoffs: {fmt_int(counts['human_signoff_n'])}.",
        "",
        markdown_table(pd.DataFrame(rows), ["artifact", "path", "use"]),
        "",
        "## Remaining Decisions",
        "",
        "1. Complete human signoff for labels marked signoff, caveat, or baseline-only hold.",
        "2. Select a target journal and live-check current author guidelines before formatting.",
        "3. Decide whether Figure 1 should use main-validation cohorts only or include the seven-cohort sensitivity panel.",
        "4. Keep LASI baseline-profile only unless cleaned follow-up data are added.",
        "5. Replace or remove all held Phase 15 novelty references before any final submission.",
        "",
    ]
    return "\n".join(lines)


def build_report(counts: dict[str, object], reference_queue: pd.DataFrame, signoff_sheet: pd.DataFrame) -> str:
    status_counts = reference_queue["verification_status"].value_counts().rename_axis("verification_status").reset_index(name="n")
    signoff_counts = signoff_sheet["phase18_marker"].fillna("").replace("", "none").value_counts().rename_axis("marker").reset_index(name="n")
    lines = [
        "# Phase 19 Clean Submission Package Report",
        "",
        f"Generated: {RUN_DATE}.",
        "",
        "## Key Counts",
        "",
        f"- Baseline women aged 50+ screen: {fmt_int(counts['baseline_n'])}.",
        f"- Strict-primary selected assignments: {fmt_int(counts['strict_selected_n'])}.",
        f"- Bridge-sensitivity selected assignments: {fmt_int(counts['bridge_selected_n'])}.",
        f"- Phase 18 auto-v0 class labels: {fmt_int(counts['n_classes'])}.",
        f"- Labels requiring signoff: {fmt_int(counts['human_signoff_n'])}.",
        f"- Functional deterioration validation: {fmt_int(counts['functional_rows'])} cohort rows, {fmt_int(counts['functional_n'])} participants, {fmt_int(counts['functional_events'])} events.",
        f"- Mortality validation: {fmt_int(counts['mortality_rows'])} cohort rows, {fmt_int(counts['mortality_n'])} participants, {fmt_int(counts['mortality_events'])} deaths.",
        "",
        "## Reference Verification Status",
        "",
        markdown_table(status_counts, ["verification_status", "n"]),
        "",
        "## Label Signoff Markers",
        "",
        markdown_table(signoff_counts, ["marker", "n"]),
        "",
        "## Interpretation",
        "",
        "Phase 19 produces a collaborator-review submission package, not a final journal submission. The clean manuscript cites only verified references and keeps label signoff, target-journal formatting, and figure display decisions as explicit blockers.",
        "",
    ]
    return "\n".join(lines)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def build_package(output_dir: Path, manuscript_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    manuscript_dir.mkdir(parents=True, exist_ok=True)

    table1 = read_csv(output_dir, "phase11_table1_cohort_readiness.csv")
    validation = read_csv(output_dir, "phase11_table3_outcome_validation_summary.csv")
    decisions = read_csv(output_dir, "phase18_label_decisions_auto_v0.csv")
    _dictionary = read_csv(output_dir, "phase18_final_label_dictionary_v0.csv")
    _table2 = read_csv(output_dir, "phase18_table2_final_labels_v0.csv")
    phase15_sources = read_csv(output_dir, "phase15_novelty_refresh_sources.csv")

    reference_queue = build_reference_queue(phase15_sources)
    signoff_sheet = build_label_signoff_sheet(decisions)
    counts = summarize_counts(table1, validation, decisions)

    target_matrix = pd.DataFrame(TARGET_JOURNAL_ROWS)

    reference_queue.to_csv(output_dir / "phase19_verified_reference_queue.csv", index=False, encoding="utf-8-sig")
    signoff_sheet.to_csv(output_dir / "phase19_label_signoff_sheet.csv", index=False, encoding="utf-8-sig")
    target_matrix.to_csv(output_dir / "phase19_target_journal_decision_matrix.csv", index=False, encoding="utf-8-sig")

    clean_manuscript = build_clean_manuscript(table1, validation, decisions, reference_queue)
    reference_corrections = build_reference_corrections(reference_queue)
    references_md = build_references_markdown(reference_queue)
    title_page = build_title_page(table1, decisions)
    cover_letter = build_cover_letter()
    package_index = build_package_index(output_dir, manuscript_dir, counts)
    report = build_report(counts, reference_queue, signoff_sheet)

    write_text(output_dir / "phase19_clean_manuscript_target_neutral.md", clean_manuscript)
    write_text(manuscript_dir / "clean_manuscript_target_neutral.md", clean_manuscript)
    write_text(output_dir / "phase19_reference_corrections.md", reference_corrections)
    write_text(manuscript_dir / "references_verified_v0.md", references_md)
    write_text(manuscript_dir / "title_page_draft.md", title_page)
    write_text(manuscript_dir / "cover_letter_skeleton.md", cover_letter)
    write_text(output_dir / "phase19_submission_package_index.md", package_index)
    write_text(output_dir / "phase19_clean_submission_package_report.md", report)

    print("Phase 19 clean submission package complete.")
    print(f"Reference queue rows: {len(reference_queue)}")
    print(f"Label signoff rows: {len(signoff_sheet)}")
    print(f"Human signoff required: {counts['human_signoff_n']}")
    print(f"Clean manuscript: {manuscript_dir / 'clean_manuscript_target_neutral.md'}")
    print(f"Package index: {output_dir / 'phase19_submission_package_index.md'}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Phase 19 clean target-neutral submission package.")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    parser.add_argument("--manuscript-dir", type=Path, default=Path("manuscript"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    build_package(args.output_dir, args.manuscript_dir)


if __name__ == "__main__":
    main()
