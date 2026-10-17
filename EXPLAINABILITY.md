# Explainability and Decision Record

## Purpose
Attribute supplied cloud cost records using explicit tags and create an auditable summary.

## Inputs
Required: `record_id`, `resource_id`, `service`, `cost`, `currency`, `tags`. JSON tags must be an object; CSV tags must be JSON text. No external source is queried.

## Decision
Validate each row. Use configured tag keys literally. Missing or blank tags become `unallocated`. Never infer ownership. Sum costs separately by currency and retain validation findings.

## Severity and Prioritization
- `high`: malformed records that prevent reliable reconciliation.
- `medium`: missing tags, duplicate IDs, or unresolved ownership.
- `low`: records fully attributed from supplied tags.
- `review`: human confirmation is required.

## Outputs and Evidence
The report contains record-level decisions, IDs, tag evidence, validation findings, per-currency totals, and limitations.

## Tool: validate-cost-data
### Inputs and Data Sources
Reads supplied JSON or CSV records only.
### Decision and Reasoning
Checks required fields, tag shape, identifiers, currency, and finite non-negative costs.
### Outputs and Evidence
Returns validation issues by record index and field.
### Limits and Constraints
Cannot confirm invoice accuracy or real-world ownership.
### Failure Handling
Malformed files and invalid rows produce explicit findings.
### Human Review
Verify source data and billing period.

## Tool: attribute-cloud-costs
### Inputs and Data Sources
Uses valid supplied records and configured tag keys.
### Decision and Reasoning
Maps each dimension to its tag. Missing values become `unallocated`; no inference or currency conversion occurs.
### Outputs and Evidence
Returns record-level attribution, tag evidence, and per-currency totals.
### Limits and Constraints
Does not call provider APIs or apply chargeback.
### Failure Handling
Invalid rows remain visible and are excluded from totals.
### Human Review
Resolve unallocated costs and confirm tag governance.

## Tool: generate-attribution-report
### Inputs and Data Sources
Uses local validation and attribution results.
### Decision and Reasoning
Formats decisions, currency-separated summaries, and findings as JSON.
### Outputs and Evidence
Produces a report with totals, decisions, issues, and limitations.
### Limits and Constraints
Not an official invoice or accounting entry.
### Failure Handling
File errors are surfaced; unresolved rows remain visible.
### Human Review
Review before showback, chargeback, or accounting.

## Human Review and Safety
Reviewers must confirm tag ownership, export completeness, currency, billing period, and organizational rules. The agent does not access accounts or modify resources.

## Auditability
Identical inputs produce identical decisions. Each attribution traces to its record ID and tag key/value.

## Global Limits
No external services, credentials, currency conversion, financial posting, resource modification, or chargeback execution. Supplied data may be incomplete or inaccurate.
## Decision Traceability

Each processed record should be traceable through its supplied record identifier, resource identifier, configured tag keys, original tag values, validation findings, and final attribution. Missing or blank ownership tags are represented as `unallocated`; the agent does not substitute inferred team, project, or environment values. Reviewers should compare the report with the original input record to verify each decision.

## Determinism and Reproducibility

The attribution engine uses explicit configuration and supplied input data. It does not use probabilistic ownership inference, external lookups, or currency conversion. Re-running the same input with the same configuration should produce equivalent attribution decisions and currency-separated totals.

## Validation and Exclusion Rules

Records that fail validation must remain visible in the report with their associated findings. Invalid records are excluded from valid cost totals so that malformed data does not silently affect reconciliation. Duplicate identifiers, missing required fields, invalid currency values, malformed tags, and negative or non-finite costs require review according to the implemented validation rules.

## Confidence and Uncertainty

The agent does not assign a probabilistic confidence score to ownership. An attribution based on an explicit tag indicates what the supplied data states, not independent proof that the ownership information is correct. Missing, ambiguous, or potentially outdated tag information requires human verification.

## Review Checklist

Before using a report for financial or operational decisions, a reviewer should:
1. Confirm the input export covers the intended billing period.
2. Verify that the supplied records are complete and that costs and currencies match the source export.
3. Confirm that configured tag keys match the organization's tagging policy.
4. Investigate unallocated records, duplicate identifiers, and validation findings.
5. Verify that record-level decisions reconcile with totals for each currency.
6. Approve any downstream showback or chargeback process separately.

## Non-Goals

This agent performs attribution and reporting only. It does not establish legal ownership, certify invoice accuracy, forecast spending, recommend resource deletion, modify cloud resources, or execute financial postings. Its output is decision-support evidence and is not a substitute for billing-system reconciliation or human approval.
