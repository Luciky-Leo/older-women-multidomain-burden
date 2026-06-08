# Phase 20 Label Signoff Review Packet

Generated: 2026-06-01.

This packet does not perform human signoff. It narrows the review to the labels that still require explicit author or clinical-reviewer decisions.

## Signoff Counts

| marker | n |
| --- | --- |
| caveat | 7 |
| hold | 3 |
| signoff | 3 |

## Conservative Rename Signoff

| cohort | class_id | phase18_label_en_v0 | phase20_required_decision | default_conservative_option | phase18_rationale |
| --- | --- | --- | --- | --- | --- |
| CHARLS | CHARLS_C1 | broad intermediate-burden profile | Approve conservative burden-profile label or replace with a domain-specific clinical label. | broad intermediate-burden profile | Generic severity-aligned label replaced with domain-neutral burden-profile label. |
| CHARLS | CHARLS_C2 | broad elevated-burden profile | Approve conservative burden-profile label or replace with a domain-specific clinical label. | broad elevated-burden profile | Generic severity-aligned label replaced with domain-neutral burden-profile label. |
| ELSA | ELSA_C3 | broad elevated-burden profile | Approve conservative burden-profile label or replace with a domain-specific clinical label. | broad elevated-burden profile | Generic severity-aligned label replaced with domain-neutral burden-profile label. |

## Caveat Approval

| cohort | class_id | phase18_label_en_v0 | phase20_required_decision | default_conservative_option | phase18_rationale |
| --- | --- | --- | --- | --- | --- |
| ELSA | ELSA_C5 | functional-dominant high-burden | Approve label with explicit sensitivity caveat; do not convert mortality signal into the class name. | functional-dominant high-burden [keep caveat in table note, not in final class name] | Keep baseline domain-profile name; avoid mortality-driven interpretation and report sensitivity caveat. |
| HRS | HRS_C3 | elevated-burden severity-aligned | Approve label with explicit sensitivity caveat; do not convert mortality signal into the class name. | elevated-burden severity-aligned [keep caveat in table note, not in final class name] | Keep baseline domain-profile name; avoid mortality-driven interpretation and report sensitivity caveat. |
| HRS | HRS_C4 | affective-dominant elevated-burden | Approve label with explicit sensitivity caveat; do not convert mortality signal into the class name. | affective-dominant elevated-burden [keep caveat in table note, not in final class name] | Keep baseline domain-profile name; avoid mortality-driven interpretation and report sensitivity caveat. |
| HRS | HRS_C5 | functional-dominant high-burden | Approve label with explicit sensitivity caveat; do not convert mortality signal into the class name. | functional-dominant high-burden [keep caveat in table note, not in final class name] | Keep baseline domain-profile name; avoid mortality-driven interpretation and report sensitivity caveat. |
| KLoSA | KLoSA_C2 | cardiometabolic-dominant intermediate-burden | Approve label with explicit sensitivity caveat; do not convert mortality signal into the class name. | cardiometabolic-dominant intermediate-burden [keep caveat in table note, not in final class name] | Keep baseline domain-profile name; avoid mortality-driven interpretation and report sensitivity caveat. |
| SHARE | SHARE_C4 | elevated-burden with spared functional | Approve label with explicit sensitivity caveat; do not convert mortality signal into the class name. | elevated-burden with spared functional [keep caveat in table note, not in final class name] | Keep baseline domain-profile name; avoid mortality-driven interpretation and report sensitivity caveat. |
| SHARE | SHARE_C5 | functional/cognitive-dominant high-burden | Approve label with explicit sensitivity caveat; do not convert mortality signal into the class name. | functional/cognitive-dominant high-burden [keep caveat in table note, not in final class name] | Keep baseline domain-profile name; avoid mortality-driven interpretation and report sensitivity caveat. |

## Baseline-Only Hold Approval

| cohort | class_id | phase18_label_en_v0 | phase20_required_decision | default_conservative_option | phase18_rationale |
| --- | --- | --- | --- | --- | --- |
| LASI | LASI_C1 | intermediate-burden with spared cardiometabolic | Approve baseline-only display and exclude from outcome-validation claims. | intermediate-burden with spared cardiometabolic [baseline-profile only] | LASI lacks follow-up validation in the current cleaned CSV pass. |
| LASI | LASI_C2 | cardiometabolic-dominant intermediate-burden | Approve baseline-only display and exclude from outcome-validation claims. | cardiometabolic-dominant intermediate-burden [baseline-profile only] | LASI lacks follow-up validation in the current cleaned CSV pass. |
| LASI | LASI_C3 | cardiometabolic-dominant elevated-burden | Approve baseline-only display and exclude from outcome-validation claims. | cardiometabolic-dominant elevated-burden [baseline-profile only] | LASI lacks follow-up validation in the current cleaned CSV pass. |

## How To Complete

Fill `outputs/phase20_label_signoff_decision_template.csv`. Use `approve_as_written = yes` only when the reviewer accepts the Phase 18 label and marker. Use `final_label_override` only when the reviewer wants a different class name. Do not clear caveat or baseline-only markers unless the corresponding analysis limitation has been resolved.
