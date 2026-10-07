# Focused accessibility and release audit

This continuation completed additional local release checks. It does not change the frozen scientific method, result, or claim. The previous delivery was concrete progress; the full goal remains unproven because team facts, external review, material rule/rights decisions and authorized release remain outstanding.

## Keyboard and display repairs

Browser testing reproduced a focus loss after calculation: temporarily disabling the initiating form control moved focus to the document body. The form now restores focus to the initiating element when focus remains on the body, after both success and error. It does not steal focus from another element the user reached while the calculation ran.

The skip link now targets a programmatically focusable planner section. Enter focuses that section; Tab then reaches the budget input. The disclosure opens by keyboard. Successful calculation, invalid-budget rejection and reset/recovery were exercised in the in-app browser. The final public example still selects farin:170, farin:178 and farin:184 at budget three. No browser console warnings or errors were observed.

Focus and input outlines were darkened. Selected actual foreground/background pairs were numerically checked using relative luminance; body text, secondary text and primary-button text exceed 4.5:1, while the tested focus outlines, input borders and chart interval strokes exceed 3:1. The [W3C non-text contrast guidance](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html) and [bypass-blocks guidance](https://www.w3.org/WAI/WCAG22/Understanding/bypass-blocks.html) informed this focused check. It is not a complete conformance certification.

The largest supported request can contain one control and 63 distinct treatment doses. Rendering a label at every dose would crowd the axis. The chart now shows at most eight dose labels including the endpoints while retaining every plotted value and every numeric row. A clearly labeled synthetic 64-well, fully observed request successfully returned 63 plotted points, eight dose labels and all 63 numeric rows. This is UI boundary evidence, not biological validation. The full-page screenshot was visually inspected and the public example restored afterward.

Evidence: `artifacts/release_audit_v1/accessibility.json`, `artifacts/well_workflow_v1/keyboard-focus.jpg`, and `artifacts/well_workflow_v1/dense-dose-ui.jpg`. The checks cover the in-app browser at its default 625-pixel width. Assistive-technology and cross-browser certification are not claimed. The report and review video remain valid descriptions of the scientific result; their earlier captured UI is labeled as a capture.

## Dependency inventory

`scripts/inventory_dependencies.py` verifies the installed version of every package in `requirements-lock.txt`. The saved inventory covers 20 pinned packages and hashes 35 license/notice files. It retains the metadata's exact license field, SPDX expression where present, classifiers and file paths within each distribution. It does not infer compatibility from a short label or select a license for the team's work.

The environment and third-party package binaries are excluded from the local checkpoint. The report/video builders additionally rely on the bundled artifact runtime, system fonts, macOS speech and FFmpeg; they are not represented as members of the numerical lock file. Media publication and project-license decisions remain for release review.

## Data attribution and redistribution boundaries

- **Farin v1:** Henner Farin, “Colorectal cancer organoid-stroma biobank allows subtype-specific assessment of individualized therapy responses,” [doi:10.17632/fypp6xhkjy.1](https://doi.org/10.17632/fypp6xhkjy.1). Recorded file license: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). This project filters/restructures source rows, forms log contrasts, computes models/results and selects three observations for the demo. Those are project transformations, not unchanged author outputs.
- **Kryeziu v3:** Kushtrim Kryeziu, Anita Sveen and Ragnhild A. Lothe, the public patient-derived colorectal organoid dataset, [doi:10.17632/hr94h42xdc.3](https://doi.org/10.17632/hr94h42xdc.3). The live provider page confirms these contributors, version 3 and CC BY 4.0. This project projects design/identity fields, pairs plates, excludes invalid contexts, computes log contrasts and derives predictions/statistics. The associated article has separate terms; no article figures are reproduced.
- **Earlier Ewart supplements:** acquisition and source attribution remain in `data/source_manifest.json` and document 12. The recorded article license is CC BY 4.0 with third-party exceptions; final artifact-level redistribution review is still open.
- **Earlier Yakavets source:** `data/yakavets_repository_manifest.json` pins the author repository revision and license file. Its root license is GPL-3.0; file-specific data reuse and redistribution were not resolved by that fact alone. The local checkpoint's derived historical artifacts must not be assumed cleared for public redistribution.

This is an attribution and evidence inventory, not legal clearance. No project license, team ownership claim or public permission was invented. Public access does not itself settle all reuse rights. The complete local archive remains a review artifact until these explicit release decisions are resolved.

## Integrity and completion decision

All 27 artifacts from the clean confirmation reproduction still match their recorded hashes. Every file covered by the scientific protocol freeze and implementation preflight also matches. Only browser presentation/interaction code changed in this continuation; no outcome was retuned or reclassified.

The focused local accessibility checks are complete within the stated scope. This is meaningful progress on M10, but M10 as a whole remains incomplete. Existing requests for team attribution, registration/eligibility status and category remain pending. External scientific review, organizer clarification and publication/submission authorization cannot be replaced with an internal status assertion. A judging rank cannot be guaranteed by any of these checks.
