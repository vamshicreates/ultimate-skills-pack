---
name: indian-film-crew-options
description: Read the user's live Indian film technician Google Sheet and propose two costed crew options for a film budget or brief. Use for technician selection and crew package planning, not actor casting or equipment budgets.
---

# Indian film crew options

Use the live [Indian Film Technician Database](https://docs.google.com/spreadsheets/d/10ELbYgTfEF1uBl-RWI6J9_9Z21jQe5UpATI86zRc90M/edit) as the source for every run. It has one tab per role, plus `Start Here` and `Role Catalog`. Do not use a remembered copy, an XLSX template, or prior results as current data. Read with the Google Drive / Google Sheets connector; resolve the spreadsheet ID and current role tabs from metadata before reading rows. If the sheet is inaccessible, explain the access problem and request a working connection rather than inventing candidates.

The repository includes an [Excel template](assets/Indian_Film_Technician_Template.xlsx) with the same 114 roles and six entry columns. It is a blank, portable starting point for Windows and Mac; it is not a live mirror of the Google Sheet. Excel shortens the `Additional Screenplay / Script Consultant` tab to `Addl Screenplay Consultant` to meet its tab-name limit. Use the template when the user asks to start or share an offline database. For crew recommendations, always read the live Sheet unless the user explicitly chooses a populated workbook as the source. Resolve files relative to this skill folder, never through a machine-specific absolute path, symlink, shell, or operating-system assumption.

## Gather the film brief

Use the user's current request for budget, language, genre, format, intended crew scope, and any priorities or exclusions. If the budget is missing, ask for it. If the user gives a total film budget without a technician allocation, compare crew costs against that total and show the remaining amount clearly; state that other production expenses are outside this comparison. Ask about a missing detail only when it materially changes the selection. Do not assume that every role in `Role Catalog` is needed on every film.

## Read the live candidates

- Read the relevant role tabs each time the skill is invoked. Include the core HOD roles appropriate to the brief, then supporting or specialist roles the user requests or the film concept clearly requires. Inspect `Role Catalog` when checking coverage or locating a renamed role tab.
- A candidate is a filled technician name on a role tab. Read the six columns together: technician name, previous work, rating (0–10), base price (₹ lakh), quoted price (₹ lakh), and comments. Use bounded reads and continue through all populated rows in each relevant tab; do not stop after the first page or treat blank template rows as people.
- Treat the quoted price as the current project fee when present. Use the base price only as an estimate when the quote is blank, and label it as such. Keep amounts numeric in ₹ lakh. Never replace a missing price with zero. Ratings are the user's assessments; a blank rating is unknown, not poor performance. Comments and previous work can inform fit, but do not claim language, genre skill, availability, or verified credits unless the row says so or the user supplies evidence.
- Keep the sheet read-only unless the user separately asks to update it. Link important named recommendations to their source tab and row when possible.

## Build two options

Produce **exactly two** distinct, practical crew packages. Use the same required roles in both so their costs are comparable. First prioritize fit for the film and the available budget. Then use ratings, previous work, and comments as evidence. A strong default is:

1. **Best overall:** strongest balance of suitability, rating, and total quoted cost.
2. **Best alternative:** a meaningfully different mix that gives higher priority to the user's stated creative focus; if none is stated, favor stronger creative heads while staying within budget.

Do not repeat almost the same package with a token swap. Avoid choosing the same person for two simultaneous roles unless the sheet or user explicitly supports it. Sum one fee per person and role, show which fees are quotes and which are base-price estimates, and show the total and remaining budget. Do not present an estimated or incomplete total as a confirmed quote. If a role has no priced candidate, list it as an unfilled gap outside the total and say the package cannot yet be confirmed as within budget.

If the sheet has too few usable records to form two complete options, still return two clearly labeled **provisional plans** using only real rows. Show the missing roles and the specific data needed to turn each into a priced package. Never invent names, credits, ratings, or fees to make an option look complete.

## Response

Give a compact film-brief recap, then a comparison table with each option's role, technician, rating, fee, and a short fit reason. Follow with each option's crew total, remaining budget, major tradeoff, and any unfilled or unverified items. End with a one-sentence recommendation grounded in the data. Cite the live sheet and identify when it was checked. Keep the scope to Indian film personnel; do not fold equipment, locations, transport, catering, or other production costs into crew totals.
