# Matching contract

Hard constraints run before scoring: resume-derived role/function, workplace, employment type, and location eligibility. Unknown employment/location data does not pass an explicit restriction. Country-scoped remote jobs must include the supplied country or a verified compatible region. Relocation broadens geography but does not establish work rights.

Score out of 100: role/function alignment 45, resume skill overlap 35, explicit experience alignment 15, posting freshness 5. Unknown skill or experience information receives a conservative contribution and an explanatory note. A known seniority mismatch lowers rank and may exclude a role; missing resume years are not guessed from age or graduation.

Deduplicate by normalized HTTPS URL with tracking parameters removed and by normalized company/title/location. Verify promising pages before returning them: reachable, not explicitly closed, no expired structured deadline, and a posting-specific title/body with an application signal. Verification records `checkedAt` and its actual scope. It does not claim an application was submitted or prove future availability.

Every result includes `title`, `company`, `url`, `location`, `workplace`, `employment`, `source`, `score`, `reasons`, `cautions`, `postedAt`, and `verification`. The response also includes `coverage`, `profile`, and the actual `count`; return fewer than ten rather than weaken strict preferences silently.
