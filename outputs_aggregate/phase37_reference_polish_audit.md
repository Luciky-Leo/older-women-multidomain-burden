# Phase 37 reference and language polish audit

Date: 2026-06-02

## Skills used

- `life-science-research:research-router-skill` for clinical/literature evidence routing.
- `life-science-research:ncbi-entrez-skill` for PubMed E-Utilities verification.
- `latex:latex-compile` for final manuscript compilation.

## PubMed records verified through Entrez

General clinical and epidemiology rationale:

- Barnett et al. 2012, Lancet, multimorbidity epidemiology, PMID 22579043, DOI 10.1016/S0140-6736(12)60240-2.
- Crimmins et al. 2011, Eur J Public Health, gender differences in SHARE/ELSA/HRS, PMID 20237171, DOI 10.1093/eurpub/ckq022.
- Clegg et al. 2013, Lancet, frailty in elderly people, PMID 23395245, DOI 10.1016/S0140-6736(12)62167-9.
- von Elm et al. 2007, Lancet, STROBE statement, PMID 18064739, DOI 10.1016/S0140-6736(07)61602-X.

Harmonization and domain measurement:

- Doiron et al. 2013, Emerging Themes in Epidemiology, BioSHaRE harmonization, PMID 24257327, DOI 10.1186/1742-7622-10-12.
- Fortier et al. 2017, Int J Epidemiol, Maelstrom harmonization guidelines, PMID 27272186, DOI 10.1093/ije/dyw075.
- Katz et al. 1963, JAMA, ADL index, PMID 14044222, DOI 10.1001/jama.1963.03060120024016.
- Lawton and Brody 1969, The Gerontologist, IADL, PMID 5349366.
- Prince et al. 1999, Br J Psychiatry, EURO-D, PMID 10533553, DOI 10.1192/bjp.174.4.339.

Cohort sources:

- Zhao et al. 2014, CHARLS cohort profile, PMID 23243115, DOI 10.1093/ije/dys203.
- Steptoe et al. 2013, ELSA cohort profile, PMID 23143611, DOI 10.1093/ije/dys168.
- Sonnega et al. 2014, HRS cohort profile, PMID 24671021, DOI 10.1093/ije/dyu067.
- Borsch-Supan et al. 2013, SHARE data resource profile, PMID 23778574, DOI 10.1093/ije/dyt088.
- Perianayagam et al. 2022, LASI cohort profile, PMID 35021187, DOI 10.1093/ije/dyab266.
- Wong et al. 2017, MHAS cohort profile, PMID 25626437, DOI 10.1093/ije/dyu263.

## Non-PubMed records verified by web/DOI

- Korea Employment Information Service official KLoSA study-design and user-guide page: https://survey.keis.or.kr/eng/klosa/index.jsp.
- McLachlan and Peel, Finite Mixture Models, Wiley, 2000, DOI 10.1002/0471721182.
- Nylund et al. 2007, Structural Equation Modeling, DOI 10.1080/10705510701575396.
- Hennig 2015, Pattern Recognition Letters, DOI 10.1016/j.patrec.2015.04.009.

## Manuscript changes

- Added cohort-profile/data-resource citations in Methods.
- Added ADL/IADL, EURO-D, harmonization, STROBE, GMM and cluster-interpretation citations.
- Added recent multidomain trajectory/symptom-cluster literature to Background.
- Polished Background, Methods, Discussion and Limitations to keep claims descriptive and guardrail-focused.

## Verification

- Citation-key audit: 27 unique citation keys in the manuscript; 27 keys present in `bmc_geriatrics_refs.bib`; 0 missing keys.
- PDF compiled successfully with bundled Tectonic.
