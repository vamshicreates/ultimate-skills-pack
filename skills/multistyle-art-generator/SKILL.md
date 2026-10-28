---
name: multistyle-art-generator
description: |
  Automatically transforms any attached reference image (photo of a person, character, object, animal, or scene) into a complete multi-style artistic portfolio. Generates 4 distinct, high-fidelity artistic interpretations inspired by Sri Priyatham's master art styles:
  1) Digital Illustration & Concept Art (cinematic lighting, painterly textured brushwork, rich color harmony)
  2) Pencil Sketches & Anatomical Studies (graphite construction lines, planar shading, raw sketchbook feel)
  3) Caricatures & Expressive Portraits (exaggerated facial anatomy, likeness preservation, micro-expressions)
  4) Inktober & Fine Ink Work (crisp micron/pen & ink linework, meticulous cross-hatching, stippling)
  Analyzes the input image's anatomy, lighting, likeness, and focal features, and automatically executes image generation for all styles.
trigger-words:
  - "convert to art styles"
  - "generate art styles"
  - "convert image"
  - "artistic rendition"
  - "sripriyatham style"
  - "digital illustration"
  - "pencil sketch"
  - "caricature"
  - "inktober style"
  - "multi-style art"
---

# Multi-Style Art Generator (Sri Priyatham Edition)

This Skill activates whenever the user provides or attaches an image and requests multi-style artistic conversions, or asks for digital illustrations, pencil sketches, anatomical studies, caricatures, or ink art based on an input reference.

---

## The 4 Signature Art Styles

### Style 1: Digital Illustration & Concept Art
- **Aesthetic**: Painterly digital oils/gouache in Procreate/Photoshop.
- **Lighting & Color**: Cinematic key light, strong rim lighting, rich atmospheric complementary palette (e.g., warm amber against deep navy/teal shadows).
- **Brushwork**: Visible textured brushwork, textured canvas tooth, blending sharp edge definition with soft ambient falloff.

### Style 2: Pencil Sketches & Anatomical Studies
- **Aesthetic**: Authentic graphite on textured, warm-toned sketchbook paper.
- **Linework**: Visible construction scaffolding, Asaro planar breakdown, dynamic gesture lines, and anatomical landmarks.
- **Shading**: Directional cross-hatching, layered graphite tones from 2H guidelines to 6B velvety darks.

### Style 3: Caricatures & Expressive Portraits
- **Aesthetic**: Character-driven caricature celebrating the subject's unique identity.
- **Likeness & Anatomy**: Exaggerates distinctive features (jawline, nose shape, brow ridge, eye spacing, smile curves) without distortion into grotesque territory.
- **Emotion**: Vibrant, energetic facial micro-expressions with dynamic planar lighting.

### Style 4: Inktober & Fine Ink Work
- **Aesthetic**: Traditional pen & ink, Micron fineliner, dip pen nib linework.
- **Technique**: High-contrast black & white (or warm sepia/duotone), intricate crosshatching, stippling, contour hatching, and bold silhouettes.

---

## Workflow: When an Image is Attached

When the user provides an image:

### Step 1: Ingest and Analyze Key Features
Inspect the input image and extract:
1. **Subject Identity & Silhouette**: Face structure, hair silhouette, pose, gesture, props, wardrobe.
2. **Key Landmarks**: Eyes, nose bridge, jawline, expression, focal lighting direction.
3. **Color & Tonal Values**: Dominant hues, shadow accents, key highlights.

### Step 2: Formulate Optimized Generation Prompts for Each Style
Construct tailored prompts incorporating the analyzed likeness and the Style DNA:

1. **Digital Concept Art Prompt**:
   `"Masterful digital illustration and concept art of [Subject Description], inspired by Sri Priyatham. Painterly textured brushstrokes, cinematic key lighting with warm amber glow and cool teal rim light, atmospheric color palette, subtle canvas texture, rich storytelling mood, 8k resolution, trending on ArtStation."`

2. **Pencil Sketch & Anatomy Prompt**:
   `"Masterful graphite pencil sketch and anatomical study of [Subject Description], in the style of Sri Priyatham. Raw sketchbook page, visible construction lines, directional cross-hatching, planar facial analysis, loose gesture drawing with tight focal rendering, authentic paper grain texture."`

3. **Caricature & Expressive Portrait Prompt**:
   `"Expressive stylized caricature portrait of [Subject Description], Sri Priyatham style. Exaggerated iconic facial features capturing perfect likeness and warm humor, dynamic micro-expression, bold silhouette contours, rich planar shading, vibrant illustrative rendering."`

4. **Inktober & Ink Work Prompt**:
   `"Exquisite pen and ink illustration of [Subject Description], Inktober style by Sri Priyatham. Crisp black micron linework on off-white paper, intricate cross-hatching, delicate stippling, dramatic chiaroscuro contrast, clean outlines, master ink craftsmanship."`

### Step 3: Execute Image Generation
Use the `generate_image` tool (or connected image generation backend) for each of the 4 styles:
- Pass the input image reference path where supported (`ImagePaths`).
- Generate high-quality outputs for all 4 styles.

### Step 4: Present Output to User
- Display the generated artwork artifacts.
- Provide a concise breakdown of how the subject was translated into each style.
- Offer options to refine specific styles, change aspect ratios, or export full-resolution assets.
