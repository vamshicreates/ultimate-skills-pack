#!/usr/bin/env python3
"""
Multi-Style Art Generator - Sri Priyatham Engine
Transforms input images into 4 signature art styles:
1. Digital Illustration & Concept Art
2. Pencil Sketches & Anatomical Studies
3. Caricatures & Expressive Portraits
4. Inktober & Fine Ink Work
"""

import os
import sys
import json
from pathlib import Path

STYLE_PROMPTS = {
    "digital_illustration": {
        "title": "Digital Illustration & Concept Art",
        "prompt_template": (
            "A masterful cinematic digital illustration and concept art of {subject}, "
            "in the signature art style of Sri Priyatham. Painterly textured digital oil and gouache brushstrokes, "
            "dramatic cinematic key lighting with warm amber golden hour glow and contrasting cool teal rim light, "
            "expressive facial depth, authentic textured canvas tooth, rich atmospheric mood, ArtStation 8k masterpiece."
        ),
        "aspect_ratio": "16:9",
        "palette": "Warm amber key light, teal/slate shadows, rich earth tones"
    },
    "pencil_sketch": {
        "title": "Pencil Sketches & Anatomical Studies",
        "prompt_template": (
            "Masterful graphite pencil sketch and anatomical study of {subject}, in the style of Sri Priyatham. "
            "Authentic toned sketchbook page, visible construction scaffolding and Asaro planar head breakdown, "
            "directional cross-hatching, loose energetic gesture lines with finely rendered focal features, authentic paper grain."
        ),
        "aspect_ratio": "16:9",
        "palette": "Monochrome graphite (2H to 6B), warm sepia/cream toned paper"
    },
    "caricature": {
        "title": "Caricatures & Expressive Portraits",
        "prompt_template": (
            "Character-driven expressive caricature portrait of {subject}, in the style of Sri Priyatham. "
            "Exaggerated iconic facial features capturing perfect recognizable likeness and intense cinematic charisma, "
            "dynamic micro-expression, bold silhouette contours, rich planar shading, vibrant stylized illustrative rendering."
        ),
        "aspect_ratio": "16:9",
        "palette": "Vibrant saturated skin tones, rich dark beard contours, high contrast"
    },
    "inktober": {
        "title": "Inktober & Fine Ink Work",
        "prompt_template": (
            "Exquisite pen and ink illustration of {subject}, Inktober style by Sri Priyatham. "
            "Crisp black micron and dip pen nib linework on textured off-white paper, intricate cross-hatching, "
            "delicate stippling, dramatic chiaroscuro contrast, bold silhouette strokes, master ink craftsmanship."
        ),
        "aspect_ratio": "16:9",
        "palette": "India ink black, delicate grey washes, high-contrast ivory paper"
    }
}

def generate_prompts_for_subject(subject_description):
    results = {}
    for style_key, config in STYLE_PROMPTS.items():
        results[style_key] = {
            "title": config["title"],
            "prompt": config["prompt_template"].format(subject=subject_description),
            "aspect_ratio": config["aspect_ratio"],
            "palette": config["palette"]
        }
    return results

if __name__ == "__main__":
    subject = "Allu Arjun as Pushpa Raj, rugged man with thick black beard, red tilak on forehead, intense piercing eyes, hand with rings brushing his beard, wearing collared shirt"
    prompts = generate_prompts_for_subject(subject)
    print(json.dumps(prompts, indent=2))
