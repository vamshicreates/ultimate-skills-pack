#!/usr/bin/env python3
"""
Blender Knowledge Distiller.
Takes harvested transcripts, chapters, and keyframes and distills them into
actionable, structured markdown Recipe Cards in references/ for image-to-blender.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List

SKILL_ROOT = Path(__file__).resolve().parent.parent
REFERENCES_DIR = SKILL_ROOT / "references"


def extract_key_terms(text: str) -> Dict[str, List[str]]:
    """Scan transcript text for Blender tools, modifiers, and shortcuts."""
    modifiers = [
        "Subdivision Surface", "Subsurf", "Bevel", "Boolean", "Mirror",
        "Solidify", "Array", "Curve", "Screw", "Skin", "Displace", "Remesh",
        "Decimate", "Lattice", "Shrinkwrap", "Weld", "Weighted Normal"
    ]
    shortcuts = [
        "Ctrl + R", "Ctrl+R", "Ctrl + B", "Ctrl+B", "Alt + E", "Alt+E",
        "Shift + D", "Shift+D", "Shift + A", "Shift+A", "E to extrude", "I to inset",
        "G to move", "S to scale", "R to rotate", "G G", "Ctrl + J", "Ctrl + P"
    ]
    nodes = [
        "Principled BSDF", "Color Ramp", "ColorRamp", "Voronoi", "Noise Texture",
        "Musgrave", "Bump", "Normal Map", "Mix Shader", "Mix Color", "Emission",
        "Displacement", "Texture Coordinate", "Mapping", "Fresnel"
    ]
    
    found_mods = set()
    found_cuts = set()
    found_nodes = set()
    
    for mod in modifiers:
        if re.search(rf"\b{re.escape(mod)}\b", text, re.IGNORECASE):
            found_mods.add(mod)
    for sc in shortcuts:
        if re.search(rf"\b{re.escape(sc)}\b", text, re.IGNORECASE):
            found_cuts.add(sc)
    for nd in nodes:
        if re.search(rf"\b{re.escape(nd)}\b", text, re.IGNORECASE):
            found_nodes.add(nd)
            
    return {
        "modifiers": sorted(list(found_mods)),
        "shortcuts": sorted(list(found_cuts)),
        "nodes": sorted(list(found_nodes))
    }


def distill_recipe(metadata_file: Path) -> Path:
    """Create a structured Recipe Card from a harvested metadata.json."""
    if not metadata_file.exists():
        raise FileNotFoundError(f"Metadata file not found: {metadata_file}")
        
    data = json.loads(metadata_file.read_text(encoding="utf-8"))
    title = data.get("title", "Blender Technique")
    url = data.get("url", "")
    channel = data.get("channel", "YouTube")
    category = data.get("category", "recipes")
    chapters = data.get("chapters", [])
    keyframes = data.get("keyframes", [])
    
    transcript_path = data.get("clean_transcript_path")
    transcript_text = ""
    if transcript_path and Path(transcript_path).exists():
        transcript_text = Path(transcript_path).read_text(encoding="utf-8")
        
    detected = extract_key_terms(transcript_text)
    
    safe_slug = re.sub(r"[^\w\-]", "_", title.lower()).strip("_")[:40]
    out_dir = REFERENCES_DIR / category
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{safe_slug}.md"
    
    content = f"""# {title}

**Source:** [{channel}]({url})  
**Category:** `{category}`  
**Analyzed Elements:**
- **Key Modifiers:** {', '.join(f'`{m}`' for m in detected['modifiers']) if detected['modifiers'] else 'None detected'}
- **Shader Nodes:** {', '.join(f'`{n}`' for n in detected['nodes']) if detected['nodes'] else 'Standard Shading'}
- **Core Shortcuts:** {', '.join(f'`{s}`' for s in detected['shortcuts']) if detected['shortcuts'] else 'Standard Operators'}

---

## 1. Overview & Core Philosophy
This recipe was synthesized from *{title}* by {channel}.
It details practical 3D production workflows, topology conventions, and execution rules to replicate high-quality 3D results in Blender.

---

## 2. Chapter Breakdown & Workflow Steps
"""
    if chapters:
        for ch in chapters:
            start = int(ch.get("start_time", 0))
            m, s = divmod(start, 60)
            content += f"### [{m:02d}:{s:02d}] {ch.get('title')}\n"
    else:
        content += "*(Continuous walkthrough without explicit chapter markers)*\n"

    content += f"""
---

## 3. Python (`bpy`) Execution Blueprint
When executing scenes requiring this style, follow these programmatic rules:

```python
import bpy

# Key modifiers identified in this workflow:
"""
    for mod in detected["modifiers"][:4]:
        mod_type = mod.upper().replace(" ", "_")
        content += f"# bpy.context.object.modifiers.new(name='{mod}', type='{mod_type}')\n"

    content += f"""```

---

## 4. Visual Keyframes Captured
"""
    if keyframes:
        for kf in keyframes:
            kf_name = Path(kf).name
            content += f"- `{kf_name}` (Visual reference stored in `{kf}`)\n"
    else:
        content += "*(No visual keyframes captured)*\n"

    out_file.write_text(content, encoding="utf-8")
    print(f"[+] Distilled recipe written to: {out_file}")
    return out_file


def main():
    parser = argparse.ArgumentParser(description="Distill harvested YouTube data into Recipe Cards.")
    parser.add_argument("--metadata", "-m", required=True, help="Path to metadata.json in data/harvested_raw/<dir>/")
    args = parser.parse_args()
    distill_recipe(Path(args.metadata))


if __name__ == "__main__":
    main()
