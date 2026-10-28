---
name: vamsi-creates-carousel
description: Turn supplied information into a concise, editable Canva carousel in the Vamsi Creates visual style. Use for new carousels or revisions when the user asks for Vamsi Creates branding.
---

# Vamsi Creates Carousel Skill

Create a clean, high-value carousel from the user's text. Default to an editable Canva design in 4:5 format and apply the palette, typography, and hierarchy in [references/design-system.md](references/design-system.md). The user's instructions about topic, slide count, CTA, audience, or format take priority over these defaults.

## Turn information into slides

1. Extract the central promise, the distinct points, any evidence or examples, and the intended CTA from the user's material. Preserve the user's facts and meaning. Check claims that may have changed before presenting them as current.
2. Make the cover a direct, readable statement aimed at the named audience. Put one main idea on each following slide. Use short titles, a useful visual or evidence block, and only the explanation needed to make the point clear. Split dense material across more slides instead of shrinking type.
3. Use a closing CTA only when the user supplies one or the goal clearly calls for it. Adapt its exact wording and keyword to the request; the earlier “Comment SOLO” example is not a default.
4. Do not print raw URLs on slides unless the user asks. If links are useful, put them in accompanying notes or a separate link list, since image exports are not clickable.

## Build in Canva

- Prefer the available Canva tools and skills. For a new carousel, make a new design or copy a suitable existing design; preserve the source. For a requested edit, update that specific design.
- Keep headlines, labels, and body copy as separate editable text elements. Keep screenshots/photos as replaceable media. Do not flatten the whole slide into one image.
- Use authentic screenshots or user-provided media when the slide discusses a real profile, product, or result. Use generated imagery only for conceptual illustration or when the user asks for it; never present generated UI as an authentic screenshot.
- Apply **Poppins to every text element**, including cover, labels, body, and CTA. Canva's editing API may not change font family, so use the Canva editor's font control when necessary. If converting from another font, use its “Change all” option across all pages and verify a cover, a content slide, and the CTA.
- Review every page at carousel viewing size. Check contrast, line wraps, spelling, screenshot crop, image frame, divider placement, and the final CTA. Fix visible inconsistencies before sharing the editable Canva link.

## Visual decisions

Use the established visual language: a thin blue top rule, white content pages, dark navy closing page, dark text, vivid blue emphasis, generous whitespace, and a clear top-to-bottom reading path. Match the reference layout for profile or product slides; adapt the central visual block for lists, comparisons, data, or stories while retaining the same type scale and restraint. See [references/design-system.md](references/design-system.md) for measured colors and layout proportions.

Deliver the Canva edit link and a brief note on the slide count and any material source limitations. Show a representative preview when one is available.
