---
name: feature-film-storyboard-calculator
description: Build and maintain an interactive pricing calculator that estimates credits and user spend for storyboarding a feature-film screenplay, including one, two, or three image generations per scene and optional screenplay formatting.
---

# Feature Film Storyboard Cost Calculator

## Purpose
Build a transparent, interactive demo that helps filmmakers estimate the credits and money required to storyboard an entire feature film using the product's current subscription and credit pricing.

The calculator is a demo/estimator, not a checkout flow. It must show assumptions and avoid implying that an estimate guarantees final spend.

## Product context
- Target audience: screenwriters, directors, independent filmmakers, production teams.
- Main job to be done: “How much will it cost me to storyboard every scene in my film, including retries?”
- Tone: clear, transparent, filmmaker-friendly; avoid jargon.
- Visual direction: premium dark UI, subtle borders, rounded cards, high-contrast typography, red accent for primary actions or important values.
- Responsive layout: mobile-first, usable on desktop and mobile.
- The main control should feel like a simple set of sliders/toggles, not a complicated finance dashboard.

## Locked baseline assumptions
- Example feature film: 170 minutes.
- Planning estimate: 170 screenplay pages.
- Planning estimate: 34,000 words total, including action/description/dialogue.
- Typical commercial feature-film planning range: roughly 70–120 scenes; use 80 scenes as the default demo.
- These are estimates, not fixed screenplay standards. Real scripts vary by format, dialogue density, pacing, and scene length.
- Storyboard image generation: 15 credits per image.
- Text request: 1 credit per up to 250 words; each additional 250 words costs +1 credit.
- For a single screenplay-formatting pass, estimate `ceil(wordCount / 250)` credits. For 34,000 words, that is 136 credits.
- User chooses 1, 2, or 3 storyboard generations per scene. Treat these as total attempts per scene, not retries in addition to the first image.
- Storyboard credits = `sceneCount * attemptsPerScene * 15`.
- Total estimated credits = storyboard credits + optional formatter credits.
- Plan credits are consumed before purchased top-up credits.
- Purchased top-ups do not expire, according to the supplied product screenshots.

## Pricing data from supplied screenshots
Keep pricing centralized in a config/constants object so it can be updated without rewriting the calculator:
- Base plan: ₹499 first month, then ₹599/month; 500 plan credits.
- Pro plan: ₹899 first month, then ₹999/month; 1,000 plan credits.
- Credit top-up: ₹1,500 for 500 credits; top-up credits do not expire.
- Storyboard image: 15 credits.
- Text request: 1 credit per 250 words.
- Base limits shown in screenshot: 5 projects, 5 scripts, 50 saved versions per script, 50 drafts per scene, 20 storyboard shots per scene.
- Pro limits shown in screenshot: 100 projects, 100 scripts, 200 saved versions per script, 200 drafts per scene, 50 storyboard shots per scene.
- These product limits are not used in the credit-cost calculation unless the product logic changes.

## Calculation logic
1. Accept scene count (default 80; demo range 10–180).
2. Accept attempts per scene: 1, 2, or 3.
3. Accept whether the user wants to include screenplay formatting.
4. Accept screenplay word count (default 34,000; adjustable if desired).
5. Accept billing view: first-month promo or renewal pricing.
6. Compute:
   - `storyboardImages = sceneCount * attemptsPerScene`
   - `storyboardCredits = storyboardImages * 15`
   - `formattingCredits = includeFormatting ? ceil(wordCount / 250) : 0`
   - `totalCredits = storyboardCredits + formattingCredits`
7. Compare at least these two ways to cover usage:
   - Base + enough 500-credit top-ups
   - Pro + enough 500-credit top-ups
8. For each plan option:
   - `topUps = ceil(max(0, totalCredits - planCredits) / 500)`
   - `totalSpend = subscriptionPriceForSelectedBillingPeriod + topUps * 1500`
   - `availableCredits = planCredits + topUps * 500`
   - `remainingCredits = availableCredits - totalCredits`
9. Recommend the cheaper of Base + top-ups or Pro + top-ups. If equal, prefer Pro only if product team wants to emphasize its larger non-credit limits; otherwise state that the prices tie.
10. Display a clear breakdown: scene count, attempts per scene, total storyboard images, storyboard credits, formatter credits, total credits, plan credits, top-up count, estimated spend, and remaining credits.
11. Add a copy-estimate action if practical.

## Important pricing/UX caveats
- Do not claim that Pro is always cheaper. Compare total cost using the actual configured price values.
- Do not compare only subscription prices; include the top-ups required.
- Clearly distinguish first-month promotional pricing from renewal pricing.
- Do not convert USD and INR unless using an explicit exchange-rate assumption.
- Explain that taxes, payment fees, and future pricing changes are excluded unless explicitly modeled.
- Explain that the formatter calculation assumes one pass through the screenplay. If users run multiple text requests or rewrite sections repeatedly, actual text-credit use can be higher.
- The screenshots show a 20-shot-per-scene Base limit and 50-shot-per-scene Pro limit. This demo's 1–3 generation selector models one storyboard image per attempt, not all possible shots within a scene. Make this distinction clear so users do not confuse “attempts per scene” with the plan's maximum storyboard shots per scene.
- Use accessible labels, keyboard-operable controls, visible focus states, and sufficient contrast.
- Use `Intl.NumberFormat('en-IN')` or equivalent for Indian number formatting.
- Keep business rules in pure functions separate from UI rendering so developers can unit-test them.

## Suggested implementation
- Preferred demo: a single static `index.html` with vanilla HTML, CSS, and JavaScript so it can be deployed quickly on GitHub Pages or Vercel.
- If integrated into the product later, port the calculation module to the app's framework and reuse the constants and unit tests.
- No backend, account connection, or real checkout is required for the demo.
- Do not collect or send user inputs to a server.

## Acceptance criteria
- Default state shows 80 scenes, 2 attempts per scene, formatting enabled, 34,000 words, and first-month pricing.
- Changing any input updates all calculations immediately.
- Attempts selector only allows 1, 2, or 3.
- Formatter on/off changes credits and recommendation correctly.
- Base and Pro cost comparisons include top-ups and renewal price mode.
- Estimated cost, top-up count, total credits, and leftover credits are visible.
- Copy estimate works.
- The UI explains the estimate assumptions and pricing caveats.
- Layout works on mobile and desktop.
- All prices and credit costs are editable in one configuration section.
