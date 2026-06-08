import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { Workbook, SpreadsheetFile } from "@oai/artifact-tool";

const __filename = fileURLToPath(import.meta.url);
const projectRoot = path.resolve(path.dirname(__filename), "..");
const packageDir = path.join(projectRoot, "manuscript", "bmc_geriatrics_submission_burden_profiles_rescue");
const outDir = path.join(packageDir, "submission_workbooks");

const workbooks = [
  {
    fileName: "additional_file_1_harmonization_and_cohort_construction.xlsx",
    title: "Cohort construction, harmonization and baseline covariate metadata",
    purpose: "Item-level harmonization, cohort denominator/tier lock, harmonization risk and baseline covariate availability.",
    sheets: [
      ["item_crosswalk", "additional_file_1_item_level_harmonization_crosswalk.csv"],
      ["cohort_tier_lock", "additional_file_2_cohort_tier_lock.csv"],
      ["harmonization_risk_matrix", "additional_file_9_harmonization_risk_matrix.csv"],
      ["baseline_covariates", "additional_file_12_baseline_clinical_design_covariate_availability.csv"],
    ],
  },
  {
    fileName: "additional_file_2_profile_stability_and_descriptive_profiles.xlsx",
    title: "Descriptive profile and model-stability guardrails",
    purpose: "GMM selection/stability outputs, covariance diagnostics, descriptive class dictionaries and sensitivity-cohort profile support.",
    sheets: [
      ["gmm_stability_summary", "additional_file_4_gmm_stability_summary.csv"],
      ["gmm_covariance", "additional_file_5_gmm_covariance_diagnostics.csv"],
      ["class_dictionary", "additional_file_7_selected_class_dictionary.csv"],
      ["profile_summary", "additional_file_8_profile_family_summary.csv"],
      ["profile_guardrails", "additional_file_13_profile_stability_guardrails.csv"],
      ["algorithm_robustness", "additional_file_17_gmm_algorithm_robustness.csv"],
      ["sensitivity_profiles", "additional_file_25_sensitivity_cohort_profile_support.csv"],
    ],
  },
  {
    fileName: "additional_file_3_lfo_functional_change_associations.xlsx",
    title: "Leave-functional-domain-out functional-change association outputs",
    purpose: "Decoupled LFO functional-change models, leakage audit, class risks, AUC intervals and functional-change heterogeneity summaries.",
    sheets: [
      ["decoupled_comparison", "additional_file_3_decoupled_validation_comparison.csv"],
      ["leakage_audit", "additional_file_6_functional_endpoint_leakage_audit.csv"],
      ["strict_core_lfo", "additional_file_14_strict_core_lfo_functional_change_association.csv"],
      ["lfo_sensitivity", "additional_file_15_lfo_sensitivity_rows_removed_from_main.csv"],
      ["class_risks", "additional_file_16_functional_association_class_risks.csv"],
      ["auc_bootstrap", "additional_file_18_auc_bootstrap_intervals.csv"],
      ["heterogeneity", "additional_file_32_cross_cohort_heterogeneity_summary.csv"],
    ],
  },
  {
    fileName: "additional_file_4_secondary_endpoints_and_prediction_guardrails.xlsx",
    title: "Secondary endpoint and prediction guardrail outputs",
    purpose: "Formal mortality guardrails, hospitalization candidate analyses, calibration metrics, decision-curve summaries and prediction guardrails.",
    sheets: [
      ["mortality_guardrail", "additional_file_23_mortality_secondary_guardrail_table.csv"],
      ["mortality_formal", "additional_file_26_phase41_mortality_secondary_formal_model_table.csv"],
      ["hospitalization_models", "additional_file_27_phase41_hospitalization_candidate_model_comparison.csv"],
      ["hospitalization_status", "additional_file_27b_phase41_hospitalization_candidate_status.csv"],
      ["calibration", "additional_file_30_phase41_calibration_metrics.csv"],
      ["decision_curve", "additional_file_30b_phase41_decision_curve_summary.csv"],
      ["prediction_guardrails", "additional_file_31_phase41_secondary_endpoint_prediction_guardrail_summary.csv"],
      ["heterogeneity", "additional_file_32_cross_cohort_heterogeneity_summary.csv"],
    ],
  },
  {
    fileName: "additional_file_5_survey_design_and_sex_comparator_audits.xlsx",
    title: "Survey-design and sex-comparator audits",
    purpose: "Survey-design variable/codebook audits, survey triplet status, baseline male-comparator summaries and all-sex LFO interaction terms.",
    sheets: [
      ["survey_variable_audit", "additional_file_19_survey_design_variable_audit.csv"],
      ["survey_raw_codebook", "additional_file_28_phase41_survey_design_raw_codebook_audit.csv"],
      ["survey_triplet_status", "additional_file_28b_phase41_survey_design_triplet_status.csv"],
      ["male_summary", "additional_file_20_baseline_male_comparator_domain_summary.csv"],
      ["male_contrasts", "additional_file_21_baseline_male_comparator_domain_contrasts.csv"],
      ["sex_interaction_summary", "additional_file_29_phase41_all_sex_lfo_sex_interaction_summary.csv"],
      ["sex_interaction_terms", "additional_file_29b_phase41_all_sex_lfo_sex_interaction_terms.csv"],
    ],
  },
];

async function readCsv(fileName) {
  const fullPath = path.join(packageDir, fileName);
  return fs.readFile(fullPath, "utf8");
}

async function addReadme(workbook, spec) {
  const sheet = workbook.worksheets.add("README");
  const rows = [
    ["Field", "Value"],
    ["Workbook title", spec.title],
    ["Purpose", spec.purpose],
    ["Source note", "Generated from project CSV outputs produced from approved downloaded cohort files cleaned by the authors."],
    ["Generated by", "scripts/build_bmc_submission_workbooks.mjs"],
    ["Generated on", new Date().toISOString()],
    ["Included sheets", spec.sheets.map(([sheetName]) => sheetName).join("; ")],
  ];
  sheet.getRange(`A1:B${rows.length}`).values = rows;
  sheet.getRange(`A1:B1`).format.font.bold = true;
  sheet.getRange(`A:B`).format.autofitColumns();
}

async function buildWorkbook(spec) {
  const workbook = Workbook.create();
  await addReadme(workbook, spec);

  for (const [sheetName, fileName] of spec.sheets) {
    const csv = await readCsv(fileName);
    await workbook.fromCSV(csv, { sheetName });
    const sheet = workbook.worksheets.getItem(sheetName);
    if (sheet) {
      const usedRange = sheet.getUsedRange();
      if (usedRange) {
        usedRange.format.autofitColumns();
      }
    }
  }

  const outPath = path.join(outDir, spec.fileName);
  const blob = await SpreadsheetFile.exportXlsx(workbook);
  await blob.save(outPath);
  return outPath;
}

await fs.mkdir(outDir, { recursive: true });
for (const spec of workbooks) {
  const outPath = await buildWorkbook(spec);
  console.log(outPath);
}
