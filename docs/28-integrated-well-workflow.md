# Integrated measured-well research workflow

Status: implemented local demonstration, October 6, 2026 (Pacific). This extends the independently evaluated mathematical core to a strict request/response workflow. It does not establish prospective laboratory performance or complete the competition submission.

## Run

From the repository root with the pinned environment installed:

```sh
.venv/bin/python scripts/plan_wells.py examples/farin_wells_request.json --output artifacts/well_workflow_v1/cli-response.json
.venv/bin/python scripts/serve_demo.py
```

Open http://127.0.0.1:8765/ in a browser. The server binds only to loopback, computes locally, and does not persist submitted requests. Stop it with Ctrl-C. It is a local research demonstration, not a deployed multi-user service. The page displays the actual saved confirmation results, including the small incremental improvement over greedy selection.

## Scientific contract

The workflow accepts one single-agent organoid context with a supplied single-plate interpretation. Raw signals must be positive and finite. The reference vehicle control and the minimum and maximum designed treatment doses must already be measured. The model parameters are fixed at amplitude 1, length 0.5, noise standard deviation 0.3 and mean slope 2; these are the parameters selected on the development cohort and frozen before confirmation.

The output selects an exact requested number of additional wells, assuming every supplied unmeasured well is feasible and costs one well. Vehicle controls count toward the budget. It minimizes equally weighted posterior latent log-response variance across the supplied distinct positive doses. The optimizer validates exchangeability in the complete conditional Gaussian law before collapsing equivalent subsets. Exactness applies to this finite, fixed Gaussian model and numerical symmetry tolerance; it is not a guarantee about biological utility.

The workflow reports current conditional means, latent variances, and expected variances after the proposed batch. Future measurements and updated means are unknown. The displayed 90% intervals concern a fresh treatment log signal minus the mean of a specified number of fresh control log signals. They assume independent, equal-variance raw log errors. Confirmation coverage was conservative (98.05% at 90% nominal); the intervals are neither distribution-free nor clinically validated.

## Request and output

The example JSON is the complete schema: version, research context, experiment and plate identifiers, concentration unit (`nM` or `uM`), measured reference ID, future control count, additional budget and well records. Every well contains exactly an ID, role, drug concentration and measured positive signal or `null`. There must be at least four distinct positive treatment doses. Zero drug concentration denotes a vehicle control, not zero solvent concentration.

The implementation rejects unknown fields, duplicate JSON keys or well IDs, nonfinite numbers, nonpositive signals, unsupported contexts, booleans used as numbers, missing measured anchors, inconsistent roles and excessive budgets. Inputs are bounded to one MiB, 64 wells and 10,000 subset representatives. Designs exceeding the enumeration bound are explicitly rejected rather than silently approximated. All cardinalities are enumerated, so even a small requested budget can exceed that bound for a large design.

Responses include selected source IDs, measured/additional cost counts, fixed parameters, request SHA-256, objective, uncertainty meaning, numerical enumeration assurance and limitations. JSON export is available through the CLI, a browser download button and a selectable/copyable JSON field. Browser automation did not observe a download event within ten seconds; the copy field and CLI export were verified. Browser download portability remains unverified.

## Actual-data example

The example is the first lexicographically complete Farin curve, `O01:Coculture:F01:Gef`, not a curve chosen for favorable performance. The provenance JSON records the source DOI, file SHA-256, original row IDs, transformations and CC BY 4.0 attribution. Only three initial measurements are populated; all remaining candidate signals are withheld from the request.

Farin does not provide a verified plate ID. The supplied identifier `unreported-source-plate` is an explicit within-curve simulation assumption. This demonstration must not be represented as a validated physical plate plan. The independent Kryeziu confirmation has stronger plate metadata; see documents 26–27.

For three additional wells, the verified output selects `farin:170` (vehicle control), `farin:178` (0.1 uM), and `farin:184` (1.1 uM). It evaluates 1,944 representatives covering 8,192 subsets. The mean latent variance reduction is 0.1997883585855267. This is a model objective in squared log-response units, not an observed biological improvement. At budget one, the selected well is `farin:181` (0.4 uM).

## Validation and limits

The complete suite passes 127 tests with warnings treated as errors. Workflow tests check budgets, conditional variance identities, unit/signal scaling, missing measurements, extreme finite concentration ratios, oversized integers, enumeration bounds and malformed inputs. HTTP tests exercise actual local requests, budget override, duplicate keys, unsupported media, outside origins/hosts and path traversal.

Browser checks confirmed budget-three and budget-one outputs, clearing stale results on edits, duplicate-key rejection, reset/recovery and the exact selected IDs in the copyable output. A full-page screenshot at a 625-pixel viewport was saved. No browser console errors or warnings were observed during those checks. Semantic labels, keyboard focus styles, status/error regions and a numeric alternative to the chart are present; this is not a full accessibility certification or cross-browser audit.

The frozen confirmation code and protocol are unchanged. The demonstration adds input/output handling and a stricter interactive enumeration bound; it does not retrospectively retune or replace the scientific results. There is no claim of prospective assay savings, clinical decisions, new GP theory, general optimal stopping, or guaranteed competition placement.

## Files

- `src/zenithsync/well_workflow.py`: strict scientific workflow.
- `scripts/plan_wells.py`: CLI and strict JSON parsing.
- `scripts/serve_demo.py`, `demo/`: local API and browser interface.
- `examples/farin_wells_request.json`, `examples/farin_wells_provenance.json`: actual source example and attribution.
- `artifacts/well_workflow_v1/`: response, screenshot and UI verification record.
- `tests/test_well_workflow.py`, `tests/test_demo_api.py`: contracts and local HTTP checks.

Remaining delivery gates include final contribution assessment, full report/video/writeup, expanded clean-environment reproduction, external review and competition-specific release/eligibility facts. No new manual intervention is required to run this local demonstration.
