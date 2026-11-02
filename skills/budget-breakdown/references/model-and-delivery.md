# Budget model and output rules

Use this contract for `scripts/check_budget.py`. It is a small interchange/control model, not a substitute for the complete scene ledger or output workbook.

## Numeric model

```json
{
  "currency": "INR",
  "as_of": "2026-11-02",
  "contingency_rate": 0.1,
  "lines": [
    {"id": "CAM01", "category": "Equipment", "item": "Main body", "quantity": 1, "units": 4, "rate": 100, "status": "included", "basis": "kit-days; fictional example"},
    {"id": "LOC01", "category": "Locations", "item": "Campus hire", "quantity": null, "units": null, "rate": null, "status": "tbd", "basis": "access requirements tracked separately"}
  ],
  "expected": {"direct": 400, "contingency": 40, "total": 440}
}
```

- Mandatory metadata: ISO estimate date and currency. Monetary inputs can be JSON numbers or decimal strings. Quantities/units/rates and contingency are finite, nonnegative numbers; contingency is a fraction from 0 through 1.
- `status` is `included`, `excluded` or `tbd`. Included rows require all three factors. An included zero is a real waiver; do not use zero for an unknown rate. A `tbd` row must have at least one missing factor. A known waived location may be included at a genuine zero if instructed.
- The checker sums exact decimal products within each category, rounds category subtotals to two decimal places, and sums those rounded subtotals into direct cost. It computes contingency on that direct cost and rounds contingency to two decimal places using half-up rounding. Use the same convention in the output model, or document and implement a different required rounding policy consistently.
- `expected` is optional and supplies independent controls, with optional `categories` mapping. A mismatched control exits unsuccessfully. Keep independent checks downstream from business calculations.
- Unknown/excluded costs remain visible in the checker's separate lists. A valid priced subtotal does not mean these costs have been funded.

## Workbook calculations

Category sheets: `ID | Item | Quantity | Paid days/units | Rate | Amount | Scope/basis`. Keep raw inputs numeric; use currency number formats, not currency text. Use direct quantity × units × rate formulas. Guard required blanks without converting them to zero. If an included line is incomplete, expose the issue in its subtotal and the summary. Keep editable percentage controls in one authoritative place.

Use `SUM` over detail amounts for subtotals and link the summary to them. Apply a single labelled contingency base. Quote worksheet names in cross-sheet formulas. A project fee is not a per-day fee. Cast rehearsals are separate paid calls from shooting unless the agreement explicitly bundles them.

Changing schedule text does not automatically change independent budget-day inputs. Either link matching rows to a shared schedule/control or explicitly instruct the user to update both. Never imply propagation that was not implemented and checked. Inserted rows must preserve amount formulas and subtotal coverage; explain the supported extension method.

Location schedule: location cluster, component scenes, access days, extra dress/prelight/rehearsal/strike access, amount/status, quote conditions. Do not add overlapping location days into a shoot-day total. Optional later quotations may calculate separately while remaining excluded from the requested main total.

## PDF/workbook reconciliation

Check names/revision, scene coverage, call counts, direct cost, contingency base, rounding, exclusions and exact total in both formats. Review all worksheet layouts and PDF tables, including final rows. Check a normal input edit, a missing required value and a deliberate zero, then restore the published scenario. Avoid moving a failed calculation into a healthy-looking zero summary.

## Useful intake examples

- Complete feature screenplay, Hyderabad, optional deck: dated INR estimate using researched local anchors and explicit assumptions.
- Complete short script, no deck: proceed; choose scale from the script and label the inferred treatment.
- Only a pitch deck or an incomplete season: request the complete scoped script before presenting a full budget.
- Updated vendor quote or changed shoot days: update the affected drivers and reconcile existing outputs without rewriting unrelated script material.
