---
name: automation-antigravity
description: Builds recurring website and editorial jobs with an explicit timezone, repeat-safe processing, source provenance, and visible failures. Use for scheduled ingestion, content review queues, and maintenance jobs.
license: MIT
---

# Website automations

This is an independently authored portable workflow for this bundle. It does not require a Codex service or a specific Antigravity sidecar implementation.

## Establish the job

Reuse the user's stated schedule, timezone, sources, destination, and publication rules. Ask only for missing choices that materially affect the result. Write a self-contained job description with inputs, outputs, credentials needed, and what counts as success. Keep secrets in the scheduler's secret store or environment, never in source files.

## Choose where it runs

Use the project's existing scheduler when practical. GitHub Actions is suitable for repository-backed content jobs; a hosted scheduler and persistent database suit frequent runtime updates. For an Antigravity-native background job, inspect the installed version's scheduler tools and documentation before configuring it. Do not invent sidecar schema or command names.

State whether execution needs the user's machine online. Distinguish a configured schedule from a verified successful run. GitHub scheduled workflows must exist on the repository's default branch and can check out another explicit branch. GitHub schedules use UTC and may start late during load; do not promise exact-to-the-minute execution. Confirm plan limits before choosing a hosting-provider cron.

Example: 09:00 and 21:00 Asia/Kolkata correspond to GitHub cron `30 3,15 * * *`. For timezones with daylight saving, use a timezone-aware scheduler or account for clock changes explicitly.

## Build the processing pipeline

1. Read allowed feeds, APIs, or public pages with bounded timeouts and a source-specific item limit. Respect source access restrictions; do not bypass a login or blocking mechanism.
2. Normalize records and deduplicate by canonical URL or stable source ID. Preserve source name, original URL, publication time when known, and discovery time.
3. Keep retries bounded and prevent overlapping runs. An unchanged source should not produce duplicate content. Preserve manual edits, verification notes, and publication states during later imports.
4. Keep editorial discovery separate from publication. Newly discovered claims enter review unless the user explicitly authorized a defined auto-publication policy. Original writing still requires factual checking and attribution.
5. Treat an image URL as a candidate, not a reuse license. Prefer official embeds for public social posts; downloading and storing media requires appropriate reuse rights. Do not rehost publisher images merely because they are publicly visible.
6. Persist results with atomic writes or transactions. Do not mix a runtime database and Git commits without defining the source of truth and how updates are reconciled.
7. Record added, updated, duplicate, and failed counts. Fail the job on complete source failure; report partial failures accurately. Notify only according to the user's preference.

## Handoff

Document the job's timezone, scheduler, branch, persistence, required secrets, manual trigger, disable procedure, and last verified run. If a deployment or account permission remains missing, name the exact unfinished step without claiming the automation is operational.
