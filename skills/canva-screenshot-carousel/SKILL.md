---
name: canva-screenshot-carousel
description: Create a photo-only Canva carousel from a local folder of screenshots or stills. Use when the user selects Canva and a screenshot folder and wants varied, cropped images arranged three per 4:5 slide, with one link to the finished multi-page design.
---

# Canva screenshot carousel

Turn a screenshot folder into one Canva design whose pages are 1080 × 1350 px. Default to three edge-to-edge horizontal image panels per page, with no visible text, borders, or black screenshot bars. Preserve the user's requested layout or slide count if different.

## Select and plan

1. Resolve the folder the user identified; inspect filenames, image dimensions, and a contact sheet. Use `scripts/carousel.py contact --folder FOLDER --output CONTACT.jpg` if useful. Read the preview visually.
2. Choose only strong, distinct frames. Avoid near-duplicates from adjacent timestamps and give the sequence a visual progression. Use each source at most once. Prefer complete groups of three; if the folder lacks enough good images, ask before repeating or padding.
3. The panels are each 1080 × 450 px, so the target panel aspect ratio is 12:5. Check that the intended cover crop removes black bars and screenshot UI without losing important faces or action. Use a per-image `focus_y` adjustment where necessary. If a screenshot cannot be cleanly framed, choose another.
4. Create a JSON manifest with a `slides` array. Each slide contains exactly three folder-relative filenames or objects with `file`, optional `focus_x`, and optional `focus_y` percentages (0–100). Example:

   ```json
   {"slides":[["frame-a.png",{"file":"frame-b.png","focus_y":55},"frame-c.png"]]}
   ```

## Build and import

1. Run `scripts/carousel.py build --folder FOLDER --manifest MANIFEST.json --output-dir NEW_DIR`. The output directory must not already exist. Use the bundled Python from `load_workspace_dependencies` if ordinary Python lacks Pillow. The builder makes a compact HTML-and-assets ZIP. It retains separate image panels and includes `data-document-role="page"` on each page for Canva import.
2. Preview the built `index.html` or the generated panel contact sheet. Fix any visible black bars, clipping, blank panels, or repetitive selections before import. Adjust the manifest and build in a new output directory if needed.
3. Use the Canva plugin's `import_design_from_url` with `design_file` set to the generated `carousel-import.zip`, `intended_design_type="instagram_post"`, and a clear title. This is a generated artifact, so use the direct file parameter; never publish the user's local screenshots to a public file host to obtain a URL. If the importer rejects size, reduce output image dimensions/quality and rebuild; keep the ZIP below 10 MB.
4. Verify the imported design has the expected number of 1080 × 1350 pages. Visually inspect the first, a middle, and the last page after full-resolution images load. Correct a failed import or bad crop before presenting the design. Share the Canva edit link for the single multi-page carousel.

Do not silently create additional Canva designs or folders. If a revised import is needed, explain which design is the deliverable; leave earlier imports alone unless the user authorizes removal. Only attempt logo or watermark removal when requested. If the user specifically asks for Canva Magic Eraser, use that editor feature and verify every edited image; do not claim all marks are gone after partial success or switch to another removal method without their approval.
