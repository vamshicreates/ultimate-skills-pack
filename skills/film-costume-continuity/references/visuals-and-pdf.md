# Visual direction and PDF review

## Character identity board

Use a consistent face, age range, body proportions, hair, and grooming from supplied references or the fictional design proposal. Include readable face and full-body views on an uncluttered background. Keep actor identity separate from character traits. Never treat the sample planning-table screenshot as an actor photo.

## Costume look board

Show the same character in the complete outfit. Include front and back views and details needed to make or source it: layering, textile, pattern scale, fastenings, footwear, accessories. Add a side view when silhouette requires it. Use an appropriate number of views; do not force nine story panels onto a costume reference sheet.

Prompt scaffolding:

```text
Asset: costume reference board, [look ID], [character ID].
Identity reference: [saved character board; its role is identity].
Approved/script facts: [facts that must stay].
Proposed costume: [pieces, fit, textile, pattern, colours].
Views: [front, back, relevant detail].
Lighting: neutral reference lighting so materials remain readable.
Constraints: preserve identity, proportions, garment construction, accessories;
no new story action, no dense labels or invented logos.
```

Use deterministic PDF text and swatches for IDs, labels, colour names, and HEX values. Artwork does not need to carry legible text. Save the prompt beside the chosen asset.

## Continuity state references

Edit the accepted look reference for each significant changed state. Name the retained features and the exact change. A stain reference needs garment location, front/back, wearer-left/right, extent and approximate shape. Keep a comparable viewpoint; do not let a dramatic new pose obscure the match. Show the clean and changed reference together in the continuity register.

Repeat an accepted image for exact matches. The PDF should say “Same look/state as Scene 1” and link to that earlier appearance. Do not regenerate the same outfit differently in Scene 4. Same clothing with a different jacket, rolled sleeves, or jewellery may be a state/accessory change if it remains the same look; document the decision.

## Colour coordination

Show named swatches and readable labels outside images. Explain the palette in character and scene context, including group/background costume treatment. Keep proposed set palette assumptions visible. Avoid claiming that a chosen HEX value guarantees a textile dye, print result, or graded camera image. Call for a physical swatch or camera test only where it is an actual production decision.

## PDF composition and checks

The bundled builder produces a portable HTML book with a copied local assets folder. Repeated references share an asset file, so a long film does not duplicate image files per scene. Its order is cover/status, linked index, film palette, characters, looks/states, scene plans, continuity register, master assignment table, and questions. It keeps art uncropped and uses wrapping tables with repeated headers. The browser renderer preserves complex-script shaping using installed system fonts and waits for fonts/images before PDF export.

Inspect a PDF render, not just HTML. At minimum inspect the cover, one identity page, one costume page, a changed state, a dense scene, a continuity comparison, the master table, multilingual text when used, and the final page. Check long field values and long garment lists for overflow. Fix the actual layout issue rather than shrinking all text. A missing image, unreadable caption, cut-off garment, tofu glyphs, broken continuity destination, or unexplained draft badge needs correction before delivery.

For an entire movie, keep scene cards compact and refer to the full look board by stable ID. Repeated scene thumbnails can be smaller, but reference details must be large enough on the look/state pages to inspect. If a page grows long, allow natural pagination and retain the scene ID in the content. Do not reduce scope to a pilot to keep the PDF short.
