# Phase 32 Next-Step Decision

Date: 2026-06-02

## Decision

Continue with the BMC Geriatrics rescue route, but do not preserve the current functional-validation claim as a primary independent validation result.

The reviewer-risk audit now supports this hierarchy:

1. Seven-cohort baseline burden-profile construction remains possible.
2. LASI contributes to baseline profile construction only, not follow-up validation.
3. KLoSA remains bridge-sensitivity unless strict ADL/IADL evidence is extracted.
4. CHARLS, ELSA, HRS and MHAS can currently support only coupled within-cohort functional association.
5. SHARE functional validation must be excluded or rebuilt because the current endpoint/model shows separation-like behavior.

Phase 32B has now tested the preferred leave-functional-domain-out design. The result does not rescue profile prediction superiority: in every strict validation cohort with follow-up, continuous three-domain scores fit better than the leave-functional-domain-out profile model.

## Required Phase 32B Design

Use the following hierarchy when rewriting the manuscript:

### Preferred Design A: Leave-Functional-Domain-Out Profiles

- Rebuild profiles using cardiometabolic, cognition and affective domains only.
- Validate against follow-up functional deterioration.
- This directly removes functional-domain leakage from profile construction.
- Report whether the three-domain profiles preserve clinically interpretable strata.
- Phase 32B completed this design and found no strict cohort where profile models beat continuous three-domain scores.

### Remaining Design B: Non-Circular Raw Functional Endpoint

- Keep four-domain baseline profiles.
- Rebuild the outcome using a functional endpoint not mathematically constructed from the same baseline functional score.
- Examples: incident ADL/IADL difficulty among baseline-unimpaired participants, clinically meaningful raw-item worsening, or persistent/new functional limitation when raw follow-up items support it.

### Sensitivity Design C: Current Coupled Change Endpoint

- Keep the current follow-up minus baseline functional score endpoint only as sensitivity.
- Label it as coupled within-cohort association, not independent prediction or validation.

## Manuscript Consequence

The next manuscript version should use "burden profiles" or "multidomain phenotypic profiles" instead of "endotypes" unless the final analysis adds evidence of mechanism, transportability or clinical decision utility.

The current best route is a descriptive/cautionary BMC Geriatrics paper:

- Primary contribution: cross-cohort mapping of interpretable multidomain burden profiles among older women.
- Validation language: within-cohort outcome gradients and comparator diagnostics.
- Explicit negative result: continuous domain scores fit functional deterioration better than profile-only models after leakage-control sensitivity.
- GMM caveat: selected four-domain GMM solutions show near-singular covariance diagnostics, so profiles should be called descriptive burden-profile strata, not stable latent endotypes.
- Cohort tiers: use `phase32_cohort_tier_lock.csv`; do not let older drafts describe KLoSA, LASI or SHARE as equivalent validation cohorts.
