from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch


ROOT = Path(__file__).resolve().parents[1]
STYLE_MODULE_DIR = ROOT / "scripts"
if str(STYLE_MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(STYLE_MODULE_DIR))

from manuscript_figure_style import apply_manuscript_figure_style, save_manuscript_figure  # noqa: E402

OUT = ROOT / "outputs"
PKG = ROOT / "manuscript" / "bmc_geriatrics_submission_burden_profiles_rescue"
TEX = PKG / "bmc_geriatrics_main.tex"
FIG4_ROOT = ROOT / "figure_redraw" / "fig4_harmonization_risk_matrix"


COHORT_ORDER = ["CHARLS", "ELSA", "HRS", "KLoSA", "LASI", "MHAS", "SHARE"]
DOMAIN_ORDER = [
    ("functional", "Functional"),
    ("cognitive", "Cognitive"),
    ("affective", "Affective"),
    ("cardiometabolic_chronic", "Cardiometabolic/\nchronic"),
]


def read_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(OUT / name)


def tex_escape(value: object) -> str:
    if pd.isna(value):
        return "NA"
    text = str(value)
    repl = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(repl.get(ch, ch) for ch in text)


def fmt_int(x: object) -> str:
    if pd.isna(x):
        return "NA"
    return f"{int(round(float(x))):,}"


def fmt_pct(n: object, d: object) -> str:
    if pd.isna(n) or pd.isna(d) or float(d) == 0:
        return "NA"
    return f"{float(n) / float(d) * 100:.1f}%"


def selected_class_counts() -> pd.DataFrame:
    selected = read_csv("phase28_gmm_selection_table.csv")
    return selected.loc[selected["selected_model"].eq(1), ["cohort", "n_classes"]]


def clean_tier(tier: str, role: str) -> str:
    if role == "baseline_profile_only":
        return "Baseline only"
    if tier == "bridge_sensitivity":
        return "Bridge sensitivity"
    return "Strict construction"


def table1_tex() -> str:
    cohort = read_csv("phase32_cohort_tier_lock.csv").merge(selected_class_counts(), on="cohort", how="left")
    cohort = cohort.set_index("cohort").loc[COHORT_ORDER].reset_index()
    lines = [
        r"\begin{table}[htbp]",
        r"\caption{Cohort roles, denominator locks and validation availability}\label{tab:tier-lock}",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{2pt}",
        r"\begin{tabular}{@{}>{\raggedright\arraybackslash}p{0.11\textwidth}>{\raggedright\arraybackslash}p{0.12\textwidth}>{\raggedright\arraybackslash}p{0.24\textwidth}>{\raggedright\arraybackslash}p{0.18\textwidth}>{\raggedright\arraybackslash}p{0.31\textwidth}@{}}",
        r"\toprule",
        r"Cohort & Role/tier & Construction denominator & Validation denominator/events & Claim status\\",
        r"\midrule",
    ]
    for _, r in cohort.iterrows():
        source = r["baseline_women_age50plus_n"]
        complete = r["complete_four_domain_n"]
        profile = r["selected_endotype_n"]
        val = r["functional_deterioration_ge_0_5sd_available_n"]
        events = r["functional_deterioration_ge_0_5sd_event_n"]
        role = "baseline_profile_only" if r["cohort"] == "LASI" else r["analysis_tier"]
        if val == 0:
            validation = "NA; no follow-up validation"
        else:
            validation = f"{fmt_int(val)}; events {fmt_int(events)} ({fmt_pct(events, val)})"
        if r["cohort"] == "LASI":
            claim = "Baseline profile construction only; excluded from validation denominator."
        elif r["cohort"] == "KLoSA":
            claim = "Bridge-sensitivity construction only; not pooled as strict primary evidence."
        elif r["cohort"] == "SHARE":
            claim = "Descriptive construction allowed; functional validation downgraded."
        else:
            claim = "Descriptive construction and within-cohort gradients only; no prediction-superiority claim."
        lines.append(
            " & ".join(
                [
                    tex_escape(r["cohort"]),
                    tex_escape(clean_tier(str(r["analysis_tier"]), role)),
                    tex_escape(
                        f"source {fmt_int(source)}; complete {fmt_int(complete)} "
                        f"({float(complete) / float(source) * 100:.1f}%); "
                        f"profile {fmt_int(profile)}, {int(r['n_classes'])} classes"
                    ),
                    tex_escape(validation),
                    tex_escape(claim),
                ]
            )
            + r"\\"
        )
    lines += [
        r"\botrule",
        r"\end{tabular}",
        r"\footnotetext{Source-screen, complete-domain, profile-construction and validation denominators are intentionally separated. LASI had no follow-up validation denominator in the current cleaned-data pass and is not counted as zero events.}",
        r"\end{table}",
    ]
    return "\n".join(lines)


def table2_tex() -> str:
    fam = read_csv("phase33_profile_family_summary.csv")
    recurrent = fam[fam["main_table_group"].eq("recurrent family")]
    specific = fam[fam["main_table_group"].eq("cohort-specific family")]
    if not specific.empty:
        row = {
            "clinical_family": "Cohort-specific high-burden variants",
            "main_table_group": "cohort-specific variants",
            "selected_classes": int(specific["selected_classes"].sum()),
            "represented_cohorts": ", ".join(sorted(set(", ".join(specific["represented_cohorts"]).split(", ")))),
            "participants": int(specific["participants"].sum()),
            "participant_pct_of_selected_profiles": specific["participants"].sum() / fam["participants"].sum() * 100,
            "min_class_pct": specific["min_class_pct"].min(),
            "max_class_pct": specific["max_class_pct"].max(),
            "mean_functional_z": specific["mean_functional_z"].mean(),
            "mean_cognitive_z": specific["mean_cognitive_z"].mean(),
            "mean_affective_z": specific["mean_affective_z"].mean(),
            "mean_cardiometabolic_chronic_z": specific["mean_cardiometabolic_chronic_z"].mean(),
        }
        display = pd.concat([recurrent, pd.DataFrame([row])], ignore_index=True)
    else:
        display = recurrent.copy()

    def reading(label: str) -> str:
        if "functional dominant" in label:
            return "Functional limitation is the main signal."
        if "severity aligned" in label:
            return "Domains move together as a severity gradient."
        if "cardiometabolic/chronic high" in label:
            return "Chronic disease burden dominates while function is relatively preserved."
        if "cardiometabolic/chronic spared" in label:
            return "Cardiometabolic/chronic burden is relatively low despite intermediate burden."
        return "Heterogeneous cohort-specific pattern; inspect full dictionary."

    def family_label(label: str) -> str:
        mapping = {
            "Intermediate burden, cardiometabolic/chronic spared": "Intermediate, CM spared",
            "Intermediate burden, severity aligned": "Intermediate, severity aligned",
            "Intermediate burden, cardiometabolic/chronic high with function spared": "Intermediate, CM high/function spared",
            "Intermediate burden, cardiometabolic/chronic high": "Intermediate, CM high",
            "High burden, functional dominant with cardiometabolic/chronic spared": "High burden, functional dominant/CM spared",
            "High burden, functional dominant with cognition relatively spared": "High burden, functional dominant/cognition spared",
            "Cohort-specific high-burden variants": "Cohort-specific high-burden variants",
        }
        return mapping.get(label, label)

    lines = [
        r"\begin{table}[htbp]",
        r"\caption{Clinical burden-profile families among selected Gaussian mixture classes}\label{tab:profile-families}",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{2pt}",
        r"\begin{tabular}{@{}>{\raggedright\arraybackslash}p{0.20\textwidth}>{\raggedright\arraybackslash}p{0.25\textwidth}>{\raggedright\arraybackslash}p{0.12\textwidth}>{\raggedright\arraybackslash}p{0.37\textwidth}@{}}",
        r"\toprule",
        r"Clinical family & Cross-cohort evidence & N (\%) & Conservative clinical interpretation\\",
        r"\midrule",
    ]
    for _, r in display.iterrows():
        participant = f"{int(r['participants']):,} ({float(r['participant_pct_of_selected_profiles']):.1f}%)"
        signature = (
            f"{float(r['mean_functional_z']):.2f}/"
            f"{float(r['mean_cognitive_z']):.2f}/"
            f"{float(r['mean_affective_z']):.2f}/"
            f"{float(r['mean_cardiometabolic_chronic_z']):.2f}"
        )
        lines.append(
            " & ".join(
                [
                    tex_escape(family_label(str(r["clinical_family"]))),
                    tex_escape(f"{int(r['selected_classes'])} classes; {r['represented_cohorts']}"),
                    tex_escape(participant),
                    tex_escape(f"{reading(str(r['clinical_family']))} Mean z F/Cog/Aff/CM = {signature}."),
                ]
            )
            + r"\\"
        )
    lines += [
        r"\botrule",
        r"\end{tabular}",
        r"\footnotetext{Higher z-scores indicate worse burden. F = functional, Cog = cognitive, Aff = affective symptoms and CM = cardiometabolic/chronic disease burden. Families summarize selected cohort-specific classes and should be interpreted as descriptive clinical strata, not diagnoses or treatment-assignment groups. Full class-level details are provided in Additional file 7.}",
        r"\end{table}",
    ]
    return "\n".join(lines)


def table3_tex() -> str:
    val = read_csv("phase32_decoupled_validation_comparison.csv")
    stab = read_csv("phase32_gmm_stability_summary.csv")
    merged = val.merge(
        stab[["cohort", "median_ari_vs_reference", "p10_ari_vs_reference", "any_near_singular_covariance"]],
        on="cohort",
        how="left",
    )
    merged = merged.set_index("cohort").loc[["CHARLS", "ELSA", "HRS", "MHAS", "SHARE", "KLoSA"]].reset_index()
    lines = [
        r"\begin{table}[htbp]",
        r"\caption{Decoupled validation performance and model-stability guardrails}\label{tab:guardrails}",
        r"\tiny",
        r"\begin{tabular}{@{}llrccccr@{}}",
        r"\toprule",
        r"Cohort & Tier & N/event & AUC P/3D & $\Delta$ AUC & $\Delta$ AIC/1k & ARI 50/10 & Claim\\",
        r"\midrule",
    ]
    for _, r in merged.iterrows():
        valn = float(r["validation_n"])
        events = float(r["validation_events"])
        delta_aic_1k = float(r["delta_aic_three_domain_scores_minus_lfo_profile"]) / valn * 1000
        tier = "Bridge" if r["analysis_tier"] == "bridge_sensitivity" else "Strict"
        interp = "Bridge only" if tier == "Bridge" else "Continuous favored"
        if r["cohort"] == "SHARE":
            interp = "Validation downgraded; continuous favored"
        if tier == "Bridge":
            cov_claim = "cov+bridge"
        elif r["cohort"] == "SHARE":
            cov_claim = "cov+val down"
        else:
            cov_claim = "cov+cont fav"
        lines.append(
            " & ".join(
                [
                    tex_escape(r["cohort"]),
                    tex_escape(tier),
                    tex_escape(f"{fmt_int(valn)} / {fmt_int(events)}"),
                    tex_escape(f"{float(r['auc_lfo_profile_age']):.3f}/{float(r['auc_three_domain_scores_age']):.3f}"),
                    f"{float(r['delta_auc_lfo_profile_minus_three_domain_scores']):.3f}",
                    f"{delta_aic_1k:.1f}",
                    tex_escape(f"{float(r['median_ari_vs_reference']):.2f}/{float(r['p10_ari_vs_reference']):.2f}"),
                    tex_escape(cov_claim),
                ]
            )
            + r"\\"
        )
    lines += [
        r"\botrule",
        r"\end{tabular}",
        r"\footnotetext{Validation profiles were rebuilt after leaving the functional domain out. P/3D = profile-class model/continuous three-domain score model. $\Delta$ AIC is the 3D model minus the profile model, scaled per 1,000 validation participants; negative values favor continuous scores. ARI is adjusted Rand index from bootstrap refits. All selected Gaussian mixture models triggered near-singular covariance downgrade diagnostics.}",
        r"\end{table}",
    ]
    return "\n".join(lines)


def summarize_cell(row: pd.Series) -> tuple[str, str, int]:
    source = str(row["source_tier"])
    flags = str(row.get("flags", ""))
    variables = row.get("variables", "")
    if pd.isna(variables) or str(variables).strip() == "":
        variables = "source variable not listed"
    variables = str(variables)
    pct = float(row["nonmissing_pct"])

    if "bridge" in flags or source == "bridge":
        risk = "Bridge"
        score = 3
    elif "partial_functional" in flags:
        risk = "Partial"
        score = 2
    elif "non_cesd" in flags:
        risk = "Alternate instrument"
        score = 2
    elif "partial_cognitive" in flags or "cohort_specific_global" in flags:
        risk = "Cohort-specific"
        score = 1
    else:
        risk = "Primary"
        score = 0

    short_vars = {
        "functional": "ADL/IADL",
        "cognitive": "cognitive score",
        "affective": "CES-D family",
        "cardiometabolic_chronic": "chronic count",
    }.get(str(row["domain"]), "domain score")
    if "iadl_only" in flags:
        short_vars = "IADL only"
    elif "adl_only" in flags:
        short_vars = "ADL only"
    if score == 3:
        short_vars = "grip/falls proxy"
    if "eurod" in variables.lower():
        short_vars = "EURO-D"

    label = f"{risk}\n{pct:.1f}%\n{short_vars}"
    return label, risk, score


def build_harmonization_matrix() -> pd.DataFrame:
    dictionary = read_csv("phase28_domain_harmonization_dictionary.csv")
    cross = read_csv("phase32_item_level_harmonization_crosswalk.csv")
    risk = (
        cross.groupby(["cohort", "domain"])
        .agg(
            flags=("comparability_flag", lambda x: "; ".join(sorted(set(map(str, x))))),
            notes=("comparability_note", lambda x: " | ".join(sorted(set(map(str, x)))[:2])),
        )
        .reset_index()
    )
    merged = dictionary.merge(risk, on=["cohort", "domain"], how="left")
    rows = []
    for cohort in COHORT_ORDER:
        for domain, display in DOMAIN_ORDER:
            row = merged[(merged["cohort"] == cohort) & (merged["domain"] == domain)]
            if row.empty:
                rows.append(
                    {
                        "cohort": cohort,
                        "domain": domain,
                        "domain_display": display,
                        "cell_label": "Unavailable",
                        "risk": "Unavailable",
                        "risk_score": 4,
                        "nonmissing_pct": np.nan,
                        "variables": "",
                        "flags": "",
                        "notes": "",
                    }
                )
            else:
                rr = row.iloc[0]
                label, risk_label, score = summarize_cell(rr)
                rows.append(
                    {
                        "cohort": cohort,
                        "domain": domain,
                        "domain_display": display,
                        "cell_label": label,
                        "risk": risk_label,
                        "risk_score": score,
                        "nonmissing_pct": rr["nonmissing_pct"],
                        "variables": rr["variables"],
                        "flags": rr.get("flags", ""),
                        "notes": rr.get("notes", ""),
                    }
                )
    df = pd.DataFrame(rows)
    out_dir = FIG4_ROOT / "intermediate_tables"
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_dir / "fig4_harmonization_matrix_input.tsv", sep="\t", index=False)
    df.to_csv(OUT / "phase34_harmonization_risk_matrix.csv", index=False)
    return df


def render_fig4() -> None:
    apply_manuscript_figure_style()
    df = build_harmonization_matrix()
    matrix = np.zeros((len(COHORT_ORDER), len(DOMAIN_ORDER)))
    labels = [["" for _ in DOMAIN_ORDER] for _ in COHORT_ORDER]
    for i, cohort in enumerate(COHORT_ORDER):
        for j, (domain, _) in enumerate(DOMAIN_ORDER):
            row = df[(df["cohort"] == cohort) & (df["domain"] == domain)].iloc[0]
            matrix[i, j] = int(row["risk_score"])
            labels[i][j] = str(row["cell_label"])

    colors = ["#DDEFE7", "#F7E7B1", "#F3C788", "#D88C73", "#D9D9D9"]
    cmap = ListedColormap(colors)
    fig, ax = plt.subplots(figsize=(9.6, 5.3))
    ax.imshow(matrix, cmap=cmap, vmin=0, vmax=4, aspect="auto")
    ax.set_xticks(range(len(DOMAIN_ORDER)))
    ax.set_xticklabels([d[1] for d in DOMAIN_ORDER], fontsize=10, fontweight="bold")
    ax.set_yticks(range(len(COHORT_ORDER)))
    ax.set_yticklabels(COHORT_ORDER, fontsize=10, fontweight="bold")
    ax.tick_params(length=0)

    for i in range(len(COHORT_ORDER) + 1):
        ax.axhline(i - 0.5, color="#F8FAFC", lw=2)
    for j in range(len(DOMAIN_ORDER) + 1):
        ax.axvline(j - 0.5, color="#F8FAFC", lw=2)

    for i in range(len(COHORT_ORDER)):
        for j in range(len(DOMAIN_ORDER)):
            color = "#2B2B2B"
            ax.text(j, i, labels[i][j], ha="center", va="center", fontsize=8.2, color=color, linespacing=1.25)

    legend = [
        Patch(facecolor=colors[0], edgecolor="none", label="Primary source"),
        Patch(facecolor=colors[1], edgecolor="none", label="Cohort-specific / partial cognition"),
        Patch(facecolor=colors[2], edgecolor="none", label="Partial or alternate instrument"),
        Patch(facecolor=colors[3], edgecolor="none", label="Bridge proxy"),
    ]
    ax.legend(handles=legend, loc="lower center", bbox_to_anchor=(0.5, -0.18), ncol=4, frameon=False, fontsize=8.5)
    fig.subplots_adjust(left=0.12, right=0.98, top=0.95, bottom=0.20)

    out_dir = FIG4_ROOT / "outputs" / "fig4"
    out_dir.mkdir(parents=True, exist_ok=True)
    save_manuscript_figure(
        fig,
        out_dir / "fig4_harmonization_risk_matrix.png",
        out_dir / "fig4_harmonization_risk_matrix.pdf",
        out_dir / "fig4_harmonization_risk_matrix.svg",
        preview_dpi=300,
    )
    plt.close(fig)

    # Copy to manuscript package.
    for ext in ["png", "pdf", "svg"]:
        src = out_dir / f"fig4_harmonization_risk_matrix.{ext}"
        dst = PKG / f"figure4_harmonization_risk_matrix.{ext}"
        dst.write_bytes(src.read_bytes())


def write_fig4_metadata() -> None:
    FIG4_ROOT.mkdir(parents=True, exist_ok=True)
    for sub in ["scripts", "intermediate_tables", "outputs", "composite", "references"]:
        (FIG4_ROOT / sub).mkdir(exist_ok=True)

    (FIG4_ROOT / "panel_inventory.tsv").write_text(
        "\t".join(
            [
                "Panel",
                "Existing figure",
                "Current visual type",
                "One-sentence conclusion",
                "Data type",
                "Cognitive task",
                "Raw data file",
                "Required columns/statistics",
                "Manuscript role",
                "Reader question answered",
                "Guardrail or annotation needed",
                "Recommended analysis runtime",
                "Recommended render runtime",
                "Native or PERSIST candidate",
                "Reason",
            ]
        )
        + "\n"
        + "\t".join(
            [
                "Fig4",
                "new",
                "cohort-domain risk matrix",
                "Domain harmonization is largely primary but has cohort-specific, partial, alternate-instrument and bridge risks that constrain interpretation.",
                "cohort by domain matrix",
                "matrix",
                "outputs/phase28_domain_harmonization_dictionary.csv; outputs/phase32_item_level_harmonization_crosswalk.csv",
                "cohort, domain, source_tier, nonmissing_pct, variables, comparability_flag",
                "Main manuscript harmonization guardrail",
                "How comparable are the four domains across cohorts?",
                "tier/risk labels and non-missing percentages",
                "Python",
                "Python",
                "native_render",
                "PERSIST search returned SHAP/confusion/correlation candidates that do not match a clinical harmonization audit matrix; native table-heatmap is the truthful grammar.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    (FIG4_ROOT / "panel_template_candidates.tsv").write_text(
        "Panel\tOption\tCandidate ID\tCandidate source\tCandidate kind\tTask fit score\tData fit score\tVisual grammar score\tSource-code readiness score\tReadability score\tTotal score\tRender decision\tRuntime\tEnv\tCapsule path\tReference visual\tSource script\tWhy it fits\tRisk\n"
        "Fig4\tF4N1\tnative_harmonization_matrix\tproject_native\tnative_render\t30\t25\t20\t15\t10\t100\trender_recommended\tPython\tresearch-py312\tNA\tNA\tscripts/build_phase34_apply_table_fig4_upgrade.py\tBest truthful representation for cohort-domain harmonization tiers and reviewer guardrails.\tNot a PERSIST high-fidelity capsule.\n"
        "Fig4\tF4P1\tcorrelation_heatmap_template\tPERSIST_TEMPLATE_CATALOG\tPERSIST_template\t18\t15\t12\t12\t8\t65\treject\tPython\tresearch-py312\tE:/Python/PERSIST/_portable_patterns/templates/correlation_omics/correlation_heatmap_template.py\tNA\tNA\tHeatmap grammar partly fits matrix but implies numeric correlation/statistical association.\tWrong statistic and likely reviewer confusion.\n",
        encoding="utf-8",
    )

    (FIG4_ROOT / "panel_render_variants.tsv").write_text(
        "Panel\tOption\tRenderer\tRuntime\tEnv\tInput\tOutput\tDecision\n"
        "Fig4\tF4N1\tnative_harmonization_matrix\tPython\tresearch-py312\toutputs/phase28_domain_harmonization_dictionary.csv; outputs/phase32_item_level_harmonization_crosswalk.csv\toutputs/fig4/fig4_harmonization_risk_matrix.png; outputs/fig4/fig4_harmonization_risk_matrix.pdf; outputs/fig4/fig4_harmonization_risk_matrix.svg\tselected\n",
        encoding="utf-8",
    )

    (FIG4_ROOT / "panel_visual_mapping.md").write_text(
        "| Panel | Runtime | Env | Selected option | Template/capsule | Capsule path | Reference visual | Source script | Source code snapshot | Raw data | Variable mapping | Intermediate file | Ported script | Visual match notes | Validation report | Output | Reason |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n"
        "| Fig4 | Python | research-py312 | F4N1 | native_harmonization_matrix | NA | NA | scripts/build_phase34_apply_table_fig4_upgrade.py | NA | outputs/phase28_domain_harmonization_dictionary.csv; outputs/phase32_item_level_harmonization_crosswalk.csv | cohort, domain, source_tier, nonmissing_pct, variables, comparability_flag | intermediate_tables/fig4_harmonization_matrix_input.tsv | scripts/build_phase34_apply_table_fig4_upgrade.py | visual_match_notes.md | persist_source_code_first_validation.md | outputs/fig4/fig4_harmonization_risk_matrix.png; outputs/fig4/fig4_harmonization_risk_matrix.pdf; outputs/fig4/fig4_harmonization_risk_matrix.svg | Native render chosen because PERSIST candidates implied SHAP/confusion/correlation rather than harmonization audit. |\n",
        encoding="utf-8",
    )

    (FIG4_ROOT / "project_palette_recommendation.md").write_text(
        "# Fig4 Palette\n\n"
        "Palette role: ordered reviewer-risk categories, not biological groups.\n\n"
        "- Primary source: `#DDEFE7`\n"
        "- Cohort-specific/partial cognition: `#F7E7B1`\n"
        "- Partial/alternate instrument: `#F3C788`\n"
        "- Bridge proxy: `#D88C73`\n"
        "- Unavailable: `#D9D9D9`\n\n"
        "This restrained green-to-orange risk palette keeps the figure clinical and print-safe while making KLoSA bridge and SHARE EURO-D visible.\n",
        encoding="utf-8",
    )

    (FIG4_ROOT / "visual_match_notes.md").write_text(
        "# Fig4 Visual Match Notes\n\n"
        "Fig4 is a native PRISM-Figure render rather than a high-fidelity PERSIST capsule. A PERSIST candidate search was performed, but top candidates were SHAP/confusion/correlation heatmaps and would imply the wrong statistic. The final figure uses a table-heatmap grammar because the reader task is an audit of cohort-domain comparability, not correlation or model performance.\n",
        encoding="utf-8",
    )
    (FIG4_ROOT / "redraw_log.md").write_text(
        "# Fig4 Redraw Log\n\n"
        "- Generated from real project harmonization tables.\n"
        "- Render runtime: Python, `research-py312`.\n"
        "- Output copied into the BMC rescue package as Figure 4.\n",
        encoding="utf-8",
    )
    (FIG4_ROOT / "panel_final_selection.md").write_text(
        "# Fig4 Final Selection\n\n"
        "Selected: F4N1 native harmonization risk matrix.\n\n"
        "Rationale: best matches the manuscript role, exposes cohort-domain measurement risk, and avoids implying unsupported statistical relationships.\n",
        encoding="utf-8",
    )
    (FIG4_ROOT / "panel_variant_gallery.md").write_text(
        "# Fig4 Variant Gallery\n\n"
        "Only F4N1 was rendered because PERSIST candidates were rejected for data/statistic mismatch.\n\n"
        "- `outputs/fig4/fig4_harmonization_risk_matrix.png`\n"
        "- `outputs/fig4/fig4_harmonization_risk_matrix.pdf`\n"
        "- `outputs/fig4/fig4_harmonization_risk_matrix.svg`\n",
        encoding="utf-8",
    )
    (FIG4_ROOT / "persist_source_code_first_validation.md").write_text(
        "# Fig4 Validation\n\n"
        "Status: NATIVE_RENDER_NOT_PERSIST\n\n"
        "This panel is intentionally recorded as a native PRISM-Figure render rather than a PERSIST high-fidelity capsule. Real project data, intermediate table, runnable script, PNG/PDF/SVG outputs and manuscript package copies were generated.\n",
        encoding="utf-8",
    )


def write_skills_search_report() -> None:
    report = """# Phase 34 Clinical/Epidemiology Skill Search

Date: 2026-06-02

Search scope:

- `E:/Reserch/Skills/00_registry/skills_catalog.csv`
- `E:/Reserch/Skills/00_registry/skills_catalog.sqlite`
- `E:/Reserch/Skills/02_callable_skills`
- available Codex skill list in the current session

Query terms:

`clinical`, `epidemiology`, `cohort`, `survival`, `causal`, `observational`, `STROBE`, `trial`, `validation`, `prediction`, `geriatric`, `public health`, `biostat`, `risk`.

## Local E-drive Skill Findings

The local registry currently has no dedicated clinical epidemiology or observational-study manuscript skill. The registry search returned zero direct clinical/epidemiology hits in `skills_catalog.csv`; the closest useful local skills are supporting assets.

| Rank | Score | Recommendation | Skill or asset | Path | Suggested runtime | Best use in this project | Limits |
|---:|---:|---|---|---|---|---|---|
| 1 | 82 | Supporting | biomed-figure-redraw / PRISM-Figure | `E:/Reserch/Skills/02_callable_skills/figure_publishing/biomed-figure-redraw` | Python or panel-specific R/Python | Manuscript figures, Fig4 harmonization matrix, future GMM/endpoint diagnostic supplementary figures | Figure workflow only; not a clinical-study reporting checklist |
| 2 | 58 | Optional | science-adz2742-tls-figures | `E:/Reserch/Skills/02_callable_skills/figure_publishing/science-adz2742-tls-figures` | R/Python | Clinical cohort overview, survival or composition figure grammar if a future mortality/survival figure is revived | Cancer/TLS-specific style; not a direct fit for aging epidemiology |
| 3 | 45 | Not recommended for main task | cns-bioinfo-methods | `E:/Reserch/Skills/02_callable_skills/bioinfo_methods/cns-bioinfo-methods` | bioinfo-py311-r45 | Method novelty lookup for computational biology methods | This is not a clinical epidemiology skill and should not drive this manuscript |
| 4 | 35 | Not recommended | ovarian-adc-visual-bioinfo | `E:/Reserch/Skills/02_callable_skills/bioinfo_visualization/ovarian-adc-visual-bioinfo` | bioinfo-py311-r45 | None for this project | Ovarian ADC bioinformatics adapter, unrelated to seven-cohort aging epidemiology |

## Session-Available Skills That Can Help

| Rank | Score | Recommendation | Skill | Best use in this project | Limits |
|---:|---:|---|---|---|---|
| 1 | 86 | Supporting | `documents:documents` | Manuscript logic audit, table layout QA, DOCX/Word-ready supplement packaging if needed | Does not perform epidemiologic analysis |
| 2 | 84 | Supporting | `spreadsheets:Spreadsheets` | Polished CSV/XLSX supplement tables, machine-readable table QA, future data dictionary workbook | Not a stats-method skill |
| 3 | 80 | Supporting | `zotero:Zotero` | Build literature support for women-only aging, intrinsic capacity, frailty, GMM/LPA and observational reporting | Requires local Zotero library availability |
| 4 | 76 | Optional | `life-science-research:research-router-skill` | Route literature/evidence lookups across PubMed-style sources and clinical evidence resources | Broad router, not project-specific |
| 5 | 70 | Optional | `life-science-research:ncbi-entrez-skill` | PubMed citation lookup for STROBE, TRIPOD, PROBAST, frailty/intrinsic-capacity benchmarks | Needs targeted citation tasks |
| 6 | 64 | Optional | `life-science-research:clinicaltrials-skill` | Not central; useful only if comparing clinical trial endpoints or intervention relevance | This paper is observational cohort research, not a trial |

## Application Recommendation

For this project, the immediately useful skill stack is:

1. `biomed-figure-redraw / PRISM-Figure` for Fig4 and future diagnostic figures.
2. `documents` plus `spreadsheets` for table/supplement design and render QA.
3. `Zotero` or `NCBI Entrez` for a targeted reporting-guideline/literature pass.

There is a real gap: no local dedicated skill exists for clinical epidemiology observational-manuscript auditing. If this project continues, create a new local skill:

`clinical-epidemiology-observational-manuscript`

Recommended contents:

- STROBE checklist audit.
- TRIPOD/PROBAST-style prediction-claim guardrails.
- Cohort denominator and missingness audit.
- Confounding/covariate sufficiency checklist.
- Endpoint validity and leakage audit.
- Table/Figure shells for observational cohort papers.
- Journal claim-language guardrails for BMC Geriatrics, JAMA Network Open, Lancet Healthy Longevity and Nature Aging/Nature Communications-level review.
"""
    (OUT / "phase34_clinical_epidemiology_skill_search.md").write_text(report, encoding="utf-8")


def write_additional_files() -> None:
    # New additional files driven by current outputs.
    mapping = {
        "additional_file_7_selected_class_dictionary.csv": OUT / "phase33_selected_class_dictionary.csv",
        "additional_file_8_profile_family_summary.csv": OUT / "phase33_profile_family_summary.csv",
        "additional_file_9_harmonization_risk_matrix.csv": OUT / "phase34_harmonization_risk_matrix.csv",
        "additional_file_10_clinical_epidemiology_skill_search.csv": None,
    }
    for name, src in mapping.items():
        dst = PKG / name
        if src is None:
            pd.DataFrame(
                [
                    {
                        "skill_or_asset": "clinical-epidemiology-observational-manuscript",
                        "status": "gap_recommended_for_creation",
                        "application": "STROBE/TRIPOD/PROBAST-style audit for this observational cohort manuscript",
                    }
                ]
            ).to_csv(dst, index=False)
        else:
            dst.write_bytes(src.read_bytes())


def replace_results_block(text: str) -> str:
    start = text.index(r"\section{Results}")
    end = text.index(r"\section{Discussion}")
    new = r"""\section{Results}\label{sec:results}

\subsection{Cohort roles and denominators}

The source screen included 79,938 women aged 50 years or older, with 76,293 complete four-domain profile assignments. These denominators are not interchangeable. Six cohorts had functional follow-up rows for the decoupled validation guardrail, whereas LASI contributed baseline profile construction only. KLoSA remained bridge-sensitivity evidence. Table~\ref{tab:tier-lock} and Figure~\ref{fig:tier-lock} show the locked cohort roles, construction denominators, validation denominators and allowed claims.

""" + table1_tex() + r"""

\subsection{Clinical burden-profile families}

Across the selected cohort-specific Gaussian mixture solutions, 28 classes were summarized into recurrent or cohort-specific clinical burden-profile families (Table~\ref{tab:profile-families}; Figure~\ref{fig:profile-heatmap}). The largest recurrent family was an intermediate-burden pattern with relatively spared cardiometabolic/chronic disease burden, represented in six cohorts and 33,498 participants. A second recurrent pattern showed cardiometabolic/chronic disease burden with relative functional sparing. Smaller recurrent high-burden patterns were dominated by functional limitation. These families are descriptive clinical strata rather than diagnoses or risk tools.

""" + table2_tex() + r"""

\subsection{Validation and model guardrails}

In the leakage-control leave-functional-domain-out analysis, continuous three-domain scores fit functional deterioration better than profile classes in every strict cohort with follow-up (Table~\ref{tab:guardrails}; Figure~\ref{fig:guardrails}). All selected four-domain GMM solutions triggered near-singular covariance diagnostics. SHARE also had poor bootstrap stability. These results support descriptive profile mapping, not prediction superiority or stable latent endotype discovery.

""" + table3_tex() + r"""

\subsection{Harmonization and comparability guardrails}

The item-level crosswalk included 97 rows and exposed the main comparability risks (Table~\ref{tab:harmonization-risk}; Figure~\ref{fig:harmonization-risk}). Functional-domain strictness differed across cohorts: CHARLS used IADL-only information, HRS used ADL-only information, KLoSA used a bridge proxy based on grip and falls, and SHARE used ADL/IADL variables but remained validation-downgraded. Cognitive batteries were not item-identical, SHARE used EURO-D for affective symptoms, and lipid/cholesterol indicators were not available in all cardiometabolic/chronic disease counts.

""" + table4_tex() + r"""

\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth,height=0.72\textheight,keepaspectratio]{figure1_cohort_tier_lock.png}
\caption{Cohort denominators and locked manuscript roles. Source-screen, complete-domain profile construction and functional follow-up validation denominators are shown separately.}
\label{fig:tier-lock}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth,height=0.86\textheight,keepaspectratio]{figure2_descriptive_profile_heatmap.png}
\caption{Clinically annotated multidomain burden profiles. The left panel shows within-cohort class size, the central matrix shows four-domain z-scored burden profiles, and the right panel shows the clinical family, functional deterioration event percentage where available, and the locked construction or validation tier. Higher z-scores indicate worse burden. Rows marked as bridge, baseline-only, or validation-downgraded are retained for profile construction or descriptive comparison but are not interpreted as equivalent primary validation strata.}
\label{fig:profile-heatmap}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth,height=0.76\textheight,keepaspectratio]{figure3_validation_and_stability_guardrails.png}
\caption{Validation and model-stability guardrails. The left panel compares leave-functional-domain-out profile classes with continuous three-domain scores using delta AIC per 1,000 validation participants; negative values favor continuous scores. The middle panel shows bootstrap median and 10th percentile adjusted Rand index values with stability thresholds. The right table reports validation denominators, raw delta AIC/delta AUC, ARI p50/p10 and the locked claim status. Tier codes are S = strict validation-gradient evidence, D = validation downgraded, B = bridge sensitivity and N = no follow-up validation. All selected Gaussian mixture models triggered near-singular covariance downgrade diagnostics.}
\label{fig:guardrails}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth,height=0.78\textheight,keepaspectratio]{figure4_harmonization_risk_matrix.png}
\caption{Cohort-domain harmonization risk matrix. Cells show source tier, non-missing percentage and the principal construct used for each burden domain. The matrix makes the main measurement guardrails visible: KLoSA contributes a bridge functional proxy, CHARLS and HRS use partial functional information, SHARE uses EURO-D for affective symptoms, and cognitive batteries are cohort-specific or partial across several cohorts.}
\label{fig:harmonization-risk}
\end{figure}

"""
    return text[:start] + new + text[end:]


def table4_tex() -> str:
    matrix = build_harmonization_matrix()
    lookup = {(r["cohort"], r["domain"]): r for _, r in matrix.iterrows()}

    def main_cell(cohort: str, domain: str) -> str:
        row = lookup[(cohort, domain)]
        risk = str(row["risk"])
        label = str(row["cell_label"])
        if domain == "functional":
            if "Bridge" in risk:
                return "Bridge proxy"
            if "IADL only" in label:
                return "Partial: IADL only"
            if "ADL only" in label:
                return "Partial: ADL only"
            return "Primary ADL/IADL"
        if domain == "cognitive":
            return "Cohort-specific"
        if domain == "affective":
            if "EURO-D" in label:
                return "Alternate EURO-D"
            return "Primary CES-D"
        return "Primary"

    lines = [
        r"\begin{table}[htbp]",
        r"\caption{Domain harmonization and comparability risk matrix}\label{tab:harmonization-risk}",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{3pt}",
        r"\begin{tabular}{@{}>{\raggedright\arraybackslash}p{0.11\textwidth}>{\raggedright\arraybackslash}p{0.23\textwidth}>{\raggedright\arraybackslash}p{0.20\textwidth}>{\raggedright\arraybackslash}p{0.20\textwidth}>{\raggedright\arraybackslash}p{0.16\textwidth}@{}}",
        r"\toprule",
        r"Cohort & Functional & Cognitive & Affective & CM/chronic\\",
        r"\midrule",
    ]
    for cohort in COHORT_ORDER:
        cells = []
        for domain, _ in DOMAIN_ORDER:
            r = lookup[(cohort, domain)]
            cells.append(tex_escape(main_cell(cohort, domain)))
        lines.append(" & ".join([tex_escape(cohort), *cells]) + r"\\")
    lines += [
        r"\botrule",
        r"\end{tabular}",
        r"\footnotetext{CM/chronic = cardiometabolic/chronic disease burden. Primary, cohort-specific, partial, alternate-instrument and bridge labels describe measurement comparability, not data quality. Figure~\ref{fig:harmonization-risk} displays non-missing percentages and construct labels; full item-level details are provided in Additional file 1 and matrix data in Additional file 9.}",
        r"\end{table}",
    ]
    return "\n".join(lines)


def replace_discussion_block(text: str) -> str:
    start = text.index(r"\section{Discussion}")
    end = text.index(r"\section{Conclusions}")
    new = r"""\section{Discussion}\label{sec:discussion}

This analysis supports a descriptive burden-profile paper, not a mechanistic endotype or prediction-superiority paper. Its contribution is a transparent cross-cohort map of how functional, cognitive, affective and cardiometabolic/chronic burdens combine among older women, together with explicit measurement, validation and model-stability guardrails. The profile families provide a compact clinical vocabulary for heterogeneity that a single severity score can hide, especially for patterns in which cardiometabolic/chronic disease burden and functional limitation do not move together.

The negative and cautionary findings are equally important. The original functional endpoint was coupled to the functional domain used in profile construction. After removing the functional domain from profile construction, continuous three-domain scores fit functional deterioration better than profile classes in all strict cohorts with follow-up. In addition, selected GMM covariance matrices were near-singular, so high posterior separation should not be mistaken for robust latent subtype discovery.

These findings define the proper clinical interpretation. Burden-profile labels may be useful for communication, subgroup description and hypothesis generation. They should not be used as diagnoses, treatment assignments, transportable risk tools or evidence that categorical profiles outperform continuous domain measures. Mortality should remain secondary and guarded because previous proportional-hazards and piecewise diagnostics raised time-stability concerns.

\section{Strengths and limitations}\label{sec:limitations}

Strengths include the women-only focus across seven international aging cohorts, explicit denominator locking, item-level harmonization review, decoupled validation sensitivity and model-stability diagnostics. The main limitations are also central to interpretation. First, baseline and follow-up functional information can be coupled when functional scores are used both for profile construction and outcome definition; the leave-functional-domain-out analysis was therefore treated as the main validation guardrail. Second, domain measures were harmonized by orientation and within-cohort standardization but were not instrument-identical across cohorts. Third, validation remained within-cohort association rather than transport validation, and LASI lacked a follow-up validation denominator in the current cleaned-data pass. Fourth, complete four-domain profiles may represent selected participants with sufficient data. Fifth, all selected GMM solutions triggered near-singular covariance diagnostics, so the classes should be interpreted as descriptive strata rather than stable latent disease entities.

"""
    return text[:start] + new + text[end:]


def update_front_matter(text: str) -> str:
    old_abs_start = text.index(r"\abstract{")
    old_abs_end = text.index(r"\keywords{")
    new_abs = r"""\abstract{\textbf{Background:} Multidomain geriatric assessment can reveal clinically different patterns of functional, cognitive, affective and cardiometabolic burden, but profile labels can be overinterpreted if harmonization, model stability and comparator performance are not shown. \textbf{Methods:} We analyzed women aged 50 years or older in seven international aging cohorts. Four cohort-specific burden domains were oriented so that higher scores indicated worse health. Gaussian mixture models were used as descriptive profile-construction tools, followed by item-level harmonization review, covariance and bootstrap stability diagnostics, and a leave-functional-domain-out validation guardrail. \textbf{Results:} The source screen included 79,938 women and 76,293 complete four-domain profile assignments. Recurrent profile families included intermediate-burden cardiometabolic/chronic-spared patterns, cardiometabolic/chronic-high function-spared patterns and smaller functional-dominant high-burden patterns. KLoSA was locked as bridge-sensitivity evidence, LASI as baseline-profile construction only, and SHARE as strict construction with downgraded validation. In all 5 strict cohorts with functional follow-up, continuous three-domain scores fit functional deterioration better than leave-functional-domain-out profile classes. All selected four-domain Gaussian mixture models triggered near-singular covariance diagnostics. \textbf{Conclusions:} The defensible contribution is descriptive cross-cohort mapping of multidomain burden profiles among older women with explicit harmonization, validation and stability guardrails. The current evidence does not support claims of stable latent endotypes or prediction superiority over continuous domain scores.}

"""
    text = text[:old_abs_start] + new_abs + text[old_abs_end:]

    old_bg = (
        "Functional ability, intrinsic capacity and multimorbidity are central to geriatric assessment "
        "\\cite{who2015worldreport,who2017icope,cesari2018evidence}. Frailty phenotypes and "
        "deficit-accumulation indices are useful because they summarize vulnerability "
        "\\cite{fried2001frailty,rockwood2007frailty}, but they can also compress distinct clinical "
        "patterns into a single severity continuum. In older women, a similar overall burden may arise "
        "from disability, cognitive or affective symptoms, chronic disease burden, or combinations of these domains.\n\n"
        "The aim of this revised analysis was therefore deliberately modest. We asked whether seven "
        "international aging cohorts could support clinically interpretable multidomain burden-profile "
        "mapping among older women, while making harmonization differences, validation coupling, comparator "
        "performance and Gaussian mixture model stability visible. We do not frame these profiles as "
        "mechanistic endotypes or as replacements for continuous domain scores."
    )
    new_bg = (
        "Functional ability, intrinsic capacity and multimorbidity are central to geriatric assessment "
        "\\cite{who2015worldreport,who2017icope,cesari2018evidence}. Frailty phenotypes and "
        "deficit-accumulation indices are useful because they summarize vulnerability "
        "\\cite{fried2001frailty,rockwood2007frailty}, but they can also compress distinct clinical "
        "patterns into a single severity continuum. In older women, a similar overall burden may arise "
        "from disability, cognitive or affective symptoms, chronic disease burden, or combinations of these domains.\n\n"
        "A women-only cross-cohort analysis is clinically relevant because women experience longer survival, "
        "greater late-life disability burden and distinct patterns of affective symptoms, multimorbidity and "
        "care needs. Pooling sex groups can obscure whether multidomain burden is dominated by functional "
        "limitations, cognitive or affective symptoms, chronic disease burden, or combinations of these domains.\n\n"
        "The aim of this revised analysis was therefore deliberately modest and operational: first, to construct "
        "clinically interpretable multidomain burden-profile families among older women; second, to make "
        "cohort-domain harmonization differences visible; and third, to test validation and model-stability "
        "guardrails that prevent overinterpretation. We do not frame these profiles as mechanistic endotypes "
        "or as replacements for continuous domain scores."
    )
    return text.replace(old_bg, new_bg)


def update_additional_files(text: str) -> str:
    old = r"""Additional file 1: Item-level harmonization crosswalk.\\
Additional file 2: Cohort tier lock.\\
Additional file 3: Decoupled validation comparison.\\
Additional file 4: GMM stability summary.\\
Additional file 5: GMM covariance diagnostics.\\
Additional file 6: Functional endpoint leakage audit.\\
Supplementary Figure S1: Cohort validation dashboard.\\
Supplementary Figure S2: Compact profile heatmap backup.\\
Supplementary Figure S3: Compact validation and stability guardrail backup."""
    new = r"""Additional file 1: Item-level harmonization crosswalk.\\
Additional file 2: Cohort tier lock.\\
Additional file 3: Decoupled validation comparison.\\
Additional file 4: GMM stability summary.\\
Additional file 5: GMM covariance diagnostics.\\
Additional file 6: Functional endpoint leakage audit.\\
Additional file 7: Full selected class dictionary.\\
Additional file 8: Clinical burden-profile family summary.\\
Additional file 9: Harmonization risk matrix data.\\
Additional file 10: Clinical and epidemiology skill-search report.\\
Supplementary Figure S1: Cohort validation dashboard.\\
Supplementary Figure S2: Compact profile heatmap backup.\\
Supplementary Figure S3: Compact validation and stability guardrail backup."""
    return text.replace(old, new)


def update_readme() -> None:
    readme = PKG / "README_BMC_Geriatrics_burden_profiles_rescue.md"
    text = readme.read_text(encoding="utf-8")
    if "Main Figure 4" not in text:
        text = text.replace(
            "- Supplementary Figure S3: PERSIST G2 compact validation/stability guardrail backup.\n",
            "- Supplementary Figure S3: PERSIST G2 compact validation/stability guardrail backup.\n"
            "- Main Figure 4: native PRISM harmonization risk matrix.\n",
        )
    if "Additional files 7-10" not in text:
        text += "\nAdditional files 7-10 add the full selected class dictionary, profile family summary, harmonization matrix data, and clinical/epidemiology skill-search report.\n"
    readme.write_text(text, encoding="utf-8")


def update_tex() -> None:
    text = TEX.read_text(encoding="utf-8")
    text = update_front_matter(text)
    text = replace_results_block(text)
    text = replace_discussion_block(text)
    text = update_additional_files(text)
    TEX.write_text(text, encoding="utf-8")


def copy_self_script() -> None:
    dst = FIG4_ROOT / "scripts" / "build_phase34_apply_table_fig4_upgrade.py"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(Path(__file__).read_text(encoding="utf-8"), encoding="utf-8")


def main() -> None:
    render_fig4()
    write_fig4_metadata()
    write_skills_search_report()
    write_additional_files()
    update_tex()
    update_readme()
    copy_self_script()
    print(PKG / "figure4_harmonization_risk_matrix.png")
    print(OUT / "phase34_clinical_epidemiology_skill_search.md")
    print(TEX)


if __name__ == "__main__":
    main()
