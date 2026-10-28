# Cloud Sheets publishing

Use this reference when a run should write to Google Sheets.

1. Discover the Google Sheets or Google Drive connector/tool available in the current environment. The user's instruction to create or update the actor database authorizes writing to their connected account. Use the authenticated connector; do not require a pasted token, embed credentials, or assume an account connected on another machine.
2. If the user supplies a Sheet URL, inspect its metadata and exact tab names before editing. Edit that Sheet only when they asked to update it. Otherwise create a new native spreadsheet with a descriptive film title.
3. Create or populate **Actors** and **Film evidence** with the headers in `SKILL.md`. Keep the primary tab at six columns. Preserve real blank cells for unverified age, Instagram, and character data. Freeze headers and add filters when supported. Write full URLs as clickable links.
4. Batch writes in bounded ranges. Verify the returned spreadsheet ID, tab IDs, actor count, evidence count, sample cells, and at least one source link. Return the provider's actual URL.
5. If creation or editing fails, retry only after identifying a concrete recoverable cause such as an expired connection, wrong Sheet ID, or malformed range. Do not repeatedly retry access denied. If no authenticated writer is available, build a local workbook from the template, state that cloud output is pending connection, and give the user the exact connection step.

The connection is account-specific. The repository contains neither OAuth secrets nor a service-account key; installation alone cannot grant Google access. Do not change Sheet sharing permissions unless the user asks.
