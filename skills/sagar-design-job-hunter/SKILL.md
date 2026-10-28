---
name: sagar-design-job-hunter
description: Find, verify, rank, and learn from batches of up to five Hyderabad-area industrial, product, and furniture design jobs for Sagar Dabherao using his Behance portfolio evidence. Use when the user asks for Sagar's next job batch, evaluates or rejects numbered jobs, or wants portfolio-fit job-search criteria; do not use for generic graphic/UI job searches.
---

# Sagar Design Job Hunter

Find high-fit roles from live sources, present no more than five at a time, and use the user's feedback to improve later batches.

## Runtime setup

This skill has no third-party Python packages. It needs Python 3.9 or newer only for the local batch-history helper; live job discovery uses the agent's web/browser capabilities.

- On Windows, use `py -3` when available, otherwise `python`.
- On macOS/Linux, use `python3`.
- Treat `<python>` in commands below as the selected launcher.
- After a new Windows installation or when diagnosing a machine, read [references/windows-setup.md](references/windows-setup.md) and run:

  ```text
  <python> <skill-dir>\scripts\doctor.py --network
  ```

Run state commands from the user's job-search workspace, not from the installed skill directory, so `.job-hunter` state stays with the user's work.

## Load the working context

1. Read [references/candidate-profile.md](references/candidate-profile.md). Treat its **confirmed evidence**, **inferences**, and **unknowns** differently.
2. Read [references/job-batch-method.md](references/job-batch-method.md) before discovery or ranking.
3. If `.job-hunter/sagar-design-job-hunter/state.json` exists, run:

   ```bash
   <python> <skill-dir>/scripts/batch_state.py show
   ```

   Use the returned seen URLs and feedback signals. Do not turn one unexplained rejection into a permanent universal rule.

## Discovery

- Search the live web for every new batch; job status, location, salary, and application URLs are time-sensitive.
- Search role families supported by the portfolio: industrial design, physical product design, furniture design, furniture/product development, CMF, consumer product design, lighting/home-product design, prototyping, and 3D product visualization.
- Enforce Hyderabad or Secunderabad. Include a remote-India role only when the user asks for remote work; never silently substitute Bangalore because the profile currently lists Bangalore.
- Prefer original company career pages and direct ATS listings. Use LinkedIn, Behance Jobs, Wellfound, YC Work at a Startup, Naukri, Instahyre, and similar boards for discovery, then follow through to the original listing when possible.
- Build a pool larger than five. Remove duplicate URLs, previously seen roles, expired listings, staffing reposts without a named client, and roles whose daily work is primarily graphic design, UI/UX, architecture, or mechanical engineering without an industrial-design component.
- Verify each finalist on the actual job page: company, exact title, location/work mode, posting status, experience requirement, required tools, application destination, and any disclosed salary.
- Do not invent salary. Write `Not disclosed` unless the listing or a clearly labeled salary source states a range.
- Do not pad a weak batch. Return exactly five when five verified, high-fit roles exist; otherwise return the smaller verified set and explain the shortfall.

## Rank for actual fit

Apply the gates and scoring rubric in the method reference. Match evidence to responsibilities, not title keywords alone.

Important defaults:

- Treat Sagar as early-career to midlevel until a resume or dates establish exact years of experience.
- Exclude senior/lead/head roles and hard requirements above five years unless the user explicitly expands seniority.
- Give strongest weight to furniture/home retail, consumer products, lighting, physical product development, CMF, prototyping, and visualization.
- Count Blender 3D, Procreate, Miro, 3D printing, and prototyping only where the portfolio explicitly supports them. Do not claim SolidWorks, Rhino, KeyShot, AutoCAD, Adobe tools, or manufacturing ownership without new evidence.
- A match percentage is a reasoned comparison, not a measured hiring probability. Keep scores calibrated; do not cluster every role above 90%.

## Present one batch

Use this table, with one concise evidence-based fit statement per row:

| # | Company | Role | Location / mode | Salary | Why Sagar fits | Match | Apply |
|---|---|---|---|---|---|---:|---|

After the table, add only material cautions: hard tool gaps, experience mismatch, portfolio/resume requirements, on-site mandate, old/uncertain posting, or indirect application route. Link the direct job page and cite live sources near the claims they support.

Write the batch as JSON following [references/job-batch-method.md](references/job-batch-method.md), then record it:

```bash
<python> <skill-dir>/scripts/batch_state.py record-batch --batch <batch.json>
```

Use `--allow-partial` only when fewer than five qualified live roles exist. Do not place private contact details in batch JSON.

End with: `Reply Approve, Reject 2 and 4, or tell me what to change for the next batch.`

## Learn from feedback

- `Approve` means the batch is accepted as a preference signal and the workflow may proceed to the next batch. It does **not** authorize a job application.
- `Reject 2 and 4` records those jobs as rejected. If the user gives a reason, preserve it as a preference signal; otherwise record only the rejection.
- A request to apply must explicitly say to apply and identify the job numbers. Even then, preserve a final user-controlled submission step.

Record feedback with:

```bash
<python> <skill-dir>/scripts/batch_state.py feedback --batch-id <id> --approved all
<python> <skill-dir>/scripts/batch_state.py feedback --batch-id <id> --rejected 2,4 --reason "<user's reason>"
```

Never resurface rejected or already-seen URLs unless the user asks to reconsider them.
