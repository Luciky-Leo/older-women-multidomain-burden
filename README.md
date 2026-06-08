# Code and aggregate materials for multidomain burden among older women across seven international ageing cohorts

This repository contains the public, non-identifying reproducibility materials
for the manuscript:

> Multidomain burden among older women across seven international ageing cohorts: a harmonized descriptive audit and cautionary profile-stability analysis

## Scope

Included materials:

- analysis and manuscript-generation scripts;
- aggregate non-identifying outputs used for tables, figures, and guardrail
  summaries;
- supplementary workbooks submitted with the manuscript;
- figure-generation code, final figure assets, and selected intermediate
  aggregate plotting tables;
- a manuscript submission snapshot.

Excluded materials:

- source cohort participant-level data;
- locally cleaned participant-level datasets;
- derived participant-level score, assignment, screen, or longitudinal files;
- raw Stata/SAS/SPSS/R data objects and any source-cohort restricted files.

The source cohorts require official portal access, registration/application, and
data-use agreement compliance. The authors downloaded approved de-identified
cohort files and cleaned/harmonized the analysis files locally. Restricted
participant-level source or derived files cannot be redistributed in this public
package.

## Reproducibility Boundary

The scripts document the complete analytic workflow used by the authors, but
running participant-level reconstruction requires authorized access to the
respective CHARLS, ELSA, HRS, KLoSA, LASI, MHAS, and SHARE source datasets.
Without those restricted inputs, users can reproduce manuscript tables and
figures from the included aggregate outputs and supplementary workbooks.

## Environment

The project was run on Windows with WSL Ubuntu and micromamba environments.
Primary Python execution used:

```bash
/mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python <script>
```

R-based plotting/model summaries used the local `research-r45` environment
where needed. See `project_notes/PROJECT_ENV.md` for the project environment
notes.

## Main Directories

- `scripts/`: analysis, table, manuscript, QC, and figure-support scripts.
- `outputs_aggregate/`: public-safe aggregate outputs.
- `manuscript_submission_snapshot/`: TeX, BibTeX, PDF, figure PDFs, and
  submitted additional workbooks.
- `figure_generation/`: figure redraw code and final figure assets.
- `metadata/file_manifest.csv`: files included in this release with SHA256.
- `metadata/excluded_files_manifest.csv`: restricted or internal files that
  were intentionally not included.

## Suggested Citation

Lu F, Chen J, Shen J, Guan R, Li L. Code and aggregate materials for
multidomain burden among older women across seven international ageing cohorts.
Zenodo. v1.0.0-submission. DOI to be added after deposit.

## License and Data-Use Notice

Code in this release is provided under the MIT License. Aggregate outputs and
manuscript-support materials are provided for scholarly review and
reproducibility. This package does not grant access to or redistribute source
cohort participant-level data; users must obtain those data from the official
cohort portals under the applicable terms.
