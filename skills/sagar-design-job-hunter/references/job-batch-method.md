# Job batch method

This workflow adapts the useful discovery and safety ideas from <https://github.com/vamshicreates/job-hunter>: multi-source discovery, seen-job deduplication, strict location/seniority filters, live-page verification, caution notes, and an approval boundary. It adds portfolio-first role selection and persistent accept/reject learning.

## Hard gates

A job is eligible only when all applicable gates pass:

1. The page represents a specific open role and is still accepting applications.
2. The work location is Hyderabad or Secunderabad, or the user explicitly allowed remote India.
3. The role is substantially industrial, furniture, physical-product, CMF, prototyping, or product-visualization work.
4. Its seniority is credible for the candidate profile; no hard requirement above five years by default.
5. The application URL resolves to the employer or a recognizable job platform.
6. The URL has not been seen or rejected in prior batches.

## Fit score

Score each passing role from 0 to 100:

- 0–35: responsibility-to-portfolio alignment
- 0–20: industry/project overlap
- 0–15: explicit tool and process overlap
- 0–15: seniority and experience fit
- 0–10: Hyderabad/location fit
- 0–5: listing freshness and application quality

Subtract rather than hide material gaps. Typical deductions:

- −10 to −25 for a hard required tool not evidenced
- −10 to −20 for a stretch experience band
- −10 for an indirect or uncertain application route
- −5 to −15 for a weakly related industry with otherwise transferable work

Interpretation:

- 85–100: unusually strong evidence-backed fit
- 70–84: good fit with limited gaps
- 55–69: plausible stretch role
- Below 55: do not shortlist unless the user asks for exploratory options

The score is a transparent heuristic, not a prediction of interview or offer probability.

## Verification record

Each saved job must contain:

```json
{
  "company": "Example Company",
  "role": "Industrial Designer",
  "location": "Hyderabad — on-site",
  "salary": "Not disclosed",
  "why_fit": "Furniture range development and Blender visualization align with the Nuqta and Saga work.",
  "match_score": 82,
  "apply_url": "https://company.example/jobs/123",
  "source_url": "https://company.example/jobs/123",
  "verified_at": "2026-10-08T12:00:00+05:30",
  "cautions": ["SolidWorks is required but not evidenced in the Behance profile."],
  "evidence": ["Nuqta Collection", "Saga Collection", "Blender 3D"]
}
```

The batch JSON is either an array of jobs or an object containing `jobs` and optional `batch_id`. Store no phone number, email address, home address, or other private contact data.

## Search query families

Combine synonyms instead of using one broad query:

- `("industrial designer" OR "product designer") Hyderabad furniture`
- `("furniture designer" OR "product development designer") Hyderabad`
- `("CMF designer" OR "industrial design") Hyderabad`
- `("3D product visualizer" OR "furniture visualizer") Hyderabad Blender`
- `site:boards.greenhouse.io (industrial OR furniture) designer India`
- `site:jobs.lever.co (industrial OR furniture) designer India`
- `site:jobs.ashbyhq.com (industrial OR furniture) designer India`
- company-career searches for furniture, consumer-product, home-retail, appliance, lighting, mobility, medtech, and design consultancies with Hyderabad operations

Avoid treating software `Product Designer` results as physical-product roles. Inspect the responsibilities before scoring.

## Feedback semantics

- Bare `Approve` accepts the current batch as a whole for preference learning and permits the next discovery batch.
- Numbered approvals and rejections apply only to those jobs.
- A rejection reason such as `too much interior design`, `salary too low`, or `requires SolidWorks` may become a negative signal. Preserve the user's wording.
- Unexplained rejection should suppress that URL but should not automatically suppress its entire industry or role family.
- Acceptance or approval is not permission to submit an application.
