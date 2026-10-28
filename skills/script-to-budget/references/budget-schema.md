# Budget input schema

`scripts/render_budget.py` reads JSON with these fields:

```json
{
  "project": {"title": "Title", "source_file": "/absolute/path.pdf", "source_sha256": "hex", "revision": "date or label", "report_date": "YYYY-MM-DD", "currency": "INR", "region": "Hyderabad and Goa (assumption)"},
  "scope": {"summary": "What the estimate covers", "schedule": "Shoot-day and travel assumptions", "quality": "Extraction limits", "inclusions": ["..."], "exclusions": ["..."]},
  "inventory": [{"label": "Numbered scenes", "value": "130", "definition": "Scene headings including inserted numbers"}],
  "evidence": [{"id": "E01", "pages": "4, 111", "scenes": "1, 113", "finding": "Two scripted vehicle crashes", "cost_effect": "Controlled action days, stunt team, vehicle and safety"}],
  "line_items": [{"department": "Principal photography", "item": "Core crew", "quantity": 30, "unit": "shoot day", "rate": 250000, "low_factor": 0.8, "high_factor": 1.3, "basis": "Planning allowance; obtain crew quote", "evidence": "Schedule assumption"}],
  "contingency_rate": 0.12,
  "opportunities": [{"idea": "Group club scenes", "basis": "Scenes 2-6, 122", "effect": "Potentially fewer location days and moves", "saving_low": 100000, "saving_high": 300000, "condition": "Requires script/schedule approval"}],
  "risks": ["..."],
  "sources": [{"label": "Official source", "url": "https://...", "note": "What it supports"}]
}
```

All money amounts are numeric currency units. `quantity × rate` is the base amount. `low_factor` and `high_factor` apply to the base line item, not to contingency; defaults are 0.8 and 1.25. Contingency is applied separately to each case's direct subtotal. No proposed savings are deducted from totals. The renderer rejects negative quantities, rates, factors, duplicate evidence IDs, missing required project identity, or a missing source file/hash mismatch. It checks a report against the exact screenplay revision used.

Use `basis` for every rate, especially when it is an allowance rather than a quote. `evidence` may reference scene numbers, evidence IDs, or an explicit schedule assumption. Inventory values may be numbers or cautious ranges when the classification is uncertain. The PDF renderer does not infer screenplay facts; the analyst must review and populate the JSON.
