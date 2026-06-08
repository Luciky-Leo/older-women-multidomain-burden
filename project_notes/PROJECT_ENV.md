# Project Environment

## Project Root

`E:\Reserch\Older women`

WSL path:

`/mnt/e/Reserch/Older women`

## Data Root

`E:\Database\七大老年健康数据库数据\csv 版本 清洗后`

WSL path:

`/mnt/e/Database/七大老年健康数据库数据/csv 版本 清洗后`

## Intended Runtime

Follow `E:\Reserch\AGENTS.md`.

- Python data-audit scripts: `research-py312`
- R trajectory modeling later: `research-r45`
- Do not install packages into Windows global Python/R for this project.

## Smoke Check

From PowerShell:

```powershell
wsl.exe -d Ubuntu -- bash -lc "cd '/mnt/e/Reserch/Older women' && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python scripts/build_variable_inventory.py --data-root '/mnt/e/Database/七大老年健康数据库数据/csv 版本 清洗后' --output-dir outputs"
```

## Current Phase

Phase 23 BMC declarations completion package complete:

- sex coding confirmed as `ragender == 0` for women and `ragender == 1` for men;
- women aged 50+ baseline and wave-level feasibility generated;
- four-domain harmonization candidates expanded and confirmed;
- analytic domain-score tables and QC generated under `outputs/`;
- first-pass Gaussian mixture endotype models generated under `outputs/`;
- severity-tertile comparator profiles generated under `outputs/`;
- follow-up outcome availability and event screens generated under `outputs/`;
- first-pass logistic outcome validation models generated under `outputs/`;
- severity-score, matched-domain, four-domain, and endotype-plus-domain comparator models generated under `outputs/`;
- mortality variables `radyear`, `radmonth`, and `iwstat` confirmed from Working_data DTA labels and cleaned CSV headers;
- participant-level mortality screen and Cox mortality models generated under `outputs/`;
- class-level outcome review table and manuscript triage figures generated under `outputs/`;
- lightweight Schoenfeld-residual PH diagnostic outputs generated under `outputs/`;
- early/late mortality HR stability outputs generated under `outputs/`;
- English and Chinese class-label candidates generated under `outputs/`;
- manuscript-facing Table 1-3 drafts and combined Figure 1 draft generated under `outputs/`;
- Results skeleton, claims table, and label review queue generated under `outputs/` and `manuscript/`;
- baseline covariate coverage inventory, participant-level covariate screen, and label/display policy generated under `outputs/`;
- covariate sensitivity plan generated under `manuscript/`;
- functional deterioration and mortality covariate-sensitivity model outputs generated under `outputs/`;
- covariate sensitivity results draft generated under `manuscript/`;
- integrated Results skeleton generated under `outputs/` and `manuscript/`;
- supplementary table shell generated under `outputs/` and `manuscript/`;
- Phase 15 label-lock queue generated under `outputs/`;
- KLoSA/SHARE/LASI display policy recommendation generated under `outputs/`;
- novelty refresh source log and report generated under `outputs/`;
- Phase 16 locked-for-draft label dictionary generated under `outputs/`;
- Phase 16 Table 2 label backfill generated under `outputs/`;
- Phase 16 Figure 1 label map and main/sensitivity figure candidates generated under `outputs/figures/`;
- Phase 16 Results draft generated under `outputs/` and `manuscript/`;
- Phase 17 label-review packet generated under `outputs/`;
- Phase 17 Introduction and Discussion drafts generated under `outputs/` and `manuscript/`;
- Phase 17 Table 1-3 and Supplement S1-S3 drafts generated under `outputs/` and `manuscript/`;
- Phase 17 claim-to-evidence guardrail map generated under `outputs/`;
- Phase 17 manuscript assembly draft generated under `outputs/` and `manuscript/`;
- Phase 18 conservative auto-v0 label decisions generated under `outputs/`;
- Phase 18 final label dictionary, Table 2 label table, and Figure 1 label map generated under `outputs/`;
- Phase 18 main-validation and seven-cohort sensitivity Figure 1 v0 candidates generated under `outputs/figures/`;
- Phase 18 journal-style manuscript draft and submission-readiness checklist generated under `outputs/` and `manuscript/`;
- Phase 19 clean target-neutral manuscript generated under `outputs/` and `manuscript/`;
- Phase 19 verified reference queue and reference-correction memo generated under `outputs/`;
- Phase 19 label signoff sheet generated under `outputs/`;
- Phase 19 target-journal decision matrix, title page draft, cover letter skeleton, and package index generated under `outputs/` and `manuscript/`;
- Phase 20 human label-signoff decision template and review packet generated under `outputs/`;
- Phase 20 official target-journal guideline snapshot generated under `outputs/`;
- Phase 20 current clean-draft format gap check generated under `outputs/`;
- Phase 20 working target memo generated under `outputs/` and `manuscript/`;
- Phase 21 BMC Geriatrics LaTeX package generated under `manuscript/bmc_geriatrics_submission/`;
- Phase 21 BMC Geriatrics zip package generated as `manuscript/bmc_geriatrics_submission_package.zip`;
- Phase 21 package manifest, summary, report, and LaTeX compile check generated under `outputs/`;
- Phase 22 conservative label-signoff proposal generated under `outputs/`;
- Phase 22 cleaned BMC class profile additional file generated under `outputs/` and the review-ready package;
- Phase 22 BMC review-ready LaTeX package generated under `manuscript/bmc_geriatrics_submission_review_ready/`;
- Phase 22 BMC review-ready zip package generated as `manuscript/bmc_geriatrics_review_ready_package.zip`;
- Phase 22 review-ready source sanity check generated under `outputs/`;
- Phase 23 BMC declarations-ready package generated under `manuscript/bmc_geriatrics_submission_declarations_ready/`;
- Phase 23 BMC declarations-ready zip package generated as `manuscript/bmc_geriatrics_declarations_ready_package.zip`;
- Phase 23 declaration completion template, cohort data-availability template, author metadata template, AI-disclosure decision note, and precheck generated under `outputs/`;
- current positioning is heterogeneity mapping plus endpoint-specific outcome relevance, not universal endotype prediction superiority;
- next phase is replacing the remaining author-input placeholders, deciding AI-disclosure wording, and compiling or uploading the source package.

## Current Clean Package Check

From PowerShell:

```powershell
wsl.exe -d Ubuntu -- bash -lc "cd '/mnt/e/Reserch/Older women' && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python -m py_compile scripts/build_phase19_clean_submission_package.py && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python scripts/build_phase19_clean_submission_package.py --output-dir outputs --manuscript-dir manuscript"
```

Phase 20:

```powershell
wsl.exe -d Ubuntu -- bash -lc "cd '/mnt/e/Reserch/Older women' && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python -m py_compile scripts/build_phase20_target_and_signoff_assets.py && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python scripts/build_phase20_target_and_signoff_assets.py --output-dir outputs --manuscript-dir manuscript"
```

Phase 21:

```powershell
wsl.exe -d Ubuntu -- bash -lc "cd '/mnt/e/Reserch/Older women' && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python -m py_compile scripts/build_phase21_bmc_geriatrics_template_package.py && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python scripts/build_phase21_bmc_geriatrics_template_package.py --template-dir '/mnt/e/Reserch/Temp/_tmp_springer_nature_template_inspect_20260524' --output-dir outputs --manuscript-dir manuscript"
```

Phase 22:

```powershell
wsl.exe -d Ubuntu -- bash -lc "cd '/mnt/e/Reserch/Older women' && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python -m py_compile scripts/build_phase22_bmc_review_ready_package.py && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python scripts/build_phase22_bmc_review_ready_package.py --output-dir outputs --manuscript-dir manuscript"
```

Phase 23:

```powershell
wsl.exe -d Ubuntu -- bash -lc "cd '/mnt/e/Reserch/Older women' && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python -m py_compile scripts/build_phase23_bmc_declarations_completion_pack.py && /mnt/e/WSL/micromamba/bin/micromamba run -n research-py312 python scripts/build_phase23_bmc_declarations_completion_pack.py --output-dir outputs --manuscript-dir manuscript"
```
