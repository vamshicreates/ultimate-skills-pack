# Source mapping

Reviewed 26 October 2026:

- https://github.com/vamshicreates/job-hunter — `SKILL.md` and `scripts/inspect_ats_form.py`: resume-first intake, requested role priority, multi-platform discovery, compact descriptions, location precision, active-link inspection. The original's five-result limit and resume/application stages are superseded by JobGod's ten-link discovery-only brief.
- https://github.com/ai-job-search-dev/ai-job-search — `.claude/skills/job-scraper/SKILL.md`, `.claude/skills/job-application-assistant/04-job-evaluation.md`, and `.claude/agents/posting-scorer.md`: provenance, posting integrity, deduplication, skills/function evaluation, explicit logistics constraints, and uncertainty. Danish-specific portals are not made the default for a global product. Culture, personality, nationality, and work rights are not inferred.

This is a new, scoped implementation of the combined workflow, not a claim that the two original agent runtimes are embedded in a browser. Their MIT license notices are preserved in the project's `licenses/` folder.

Provider documentation:

- https://himalayas.app/docs/remote-jobs-api — targeted searches and per-job availability; preserve applicationLink unchanged and show visible source credit.
- https://developers.smartrecruiters.com/docs/endpoints — selected public employer career boards and active posting details. Industrial searches additionally use the public Dr. Reddy’s, Eurofins, and AbbVie boards, alongside the general employer set; coverage is still limited to declared employers.

- https://www.arbeitnow.com/job-board-api
- https://github.com/remotive-com/remote-jobs-api
- https://jobicy.com/jobs-rss-feed
- https://developer.adzuna.com/docs/search

Feed sources must be credited and their supplied posting URLs preserved. Public feeds have geographic/role coverage limits; Adzuna adds broader local search when configured. Provider failures must be visible in the response.
