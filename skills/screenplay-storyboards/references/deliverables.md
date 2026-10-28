# Deliverable format

Organize outputs under one project folder:

```
storyboards.pdf
production_plan.json
shot_list.md
continuity_bible.md
scene_ledger.csv
storyboard_manifest.json
references/character-name.png
triptychs/S001-B01.png
boards/S001-B01.png
```

`storyboards.pdf` is the primary deliverable. It contains the continuity bible, final character reference images, complete shot list, and every three-panel storyboard sheet as a separate 16:9 PDF page, in script order. The other files let the user revise individual sheets. Generate the PDF with `scripts/build_pdf.py <project-folder>` after all sheets are verified.

`production_plan.json` records the preflight count and time estimate, the user's confirmation, the approved maximum image calls, and completed calls by batch. Update it when a batch finishes or the estimate changes. Count every image-generation attempt, including failed calls and revisions. Never infer confirmation from silence. Use these fields at minimum:

```json
{
  "scene_count": 3,
  "shot_count": 54,
  "reference_image_count": 5,
  "board_count": 18,
  "correction_call_allowance": 4,
  "approved_max_calls": 27,
  "actual_calls": 0,
  "estimated_time_range": "5–9 hours, including review and PDF QA",
  "confirmed": false
}
```

Set `confirmed` to true only after an explicit user reply accepting the specific plan. The numbers above illustrate the format only.

In `shot_list.md`, use one heading per source scene with slugline, source page/line span, scene purpose, and numbered shot entries. A shot entry has: shot ID; source anchor and covered action/dialogue; visual description; shot size; angle/height; movement; blocking and screen direction; lighting/lens intent if useful; and editorial reason. Preserve exact dialogue only when needed to identify a beat. Distinguish script facts from proposed staging.

In `scene_ledger.csv`, record `scene_id,printed_number,slugline,source_start,source_end,shot_count,board_count,status,notes`. Use `status` values such as `indexed`, `planned`, `rendered`, `verified`, and `blocked`. The final audit checks that no scene remains merely `indexed` or `planned` when full delivery was requested.

`storyboard_manifest.json` is the source of truth linking shot panels, generated triptych images, and finished sheets. Its `boards` array contains entries like:

```json
{
  "characters": [
    {
      "id": "C001",
      "name": "Mara",
      "reference_image": "references/mara.png"
    }
  ],
  "boards": [
    {
      "scene_id": "S001",
      "board_id": "S001-B01",
      "image": "triptychs/S001-B01.png",
      "prompt_file": "prompts/S001-B01.txt",
      "references": ["references/mara.png"],
      "panels": [
        {
          "shot_id": "S001-SH001",
          "camera": "Wide, eye level, slow dolly in",
          "caption": "Mara enters the empty station.",
          "source": "page 1, lines 8–11"
        },
        {
          "shot_id": "S001-SH002",
          "camera": "Medium, profile, static",
          "caption": "She sees the open ticket window.",
          "source": "page 1, lines 12–13"
        },
        {
          "shot_id": "S001-SH003",
          "camera": "Close, eye level, static",
          "caption": "Her hand stops at the counter.",
          "source": "page 1, lines 14–15"
        }
      ]
    }
  ]
}
```

Give each storyboard panel a unique shot ID and source anchor. Each generated triptych should contain up to three ordered panels from one scene; one image-generation call creates that triptych. For three panels, the visual order is top wide, bottom-left, bottom-right. For a finished sheet, pass its single-board JSON (or the complete manifest with `--board-id`) to `scripts/compose_board.py`. Check that the artwork actually has the requested panel count and consistent character appearance. The composer fits it into a 16:9 white sheet without cropping story content, adds numbered labels below, and produces a 3840×2160 output in the manifest's color or monochrome style. The output canvas size does not increase the source image's real detail.

When all scenes are ready, run `scripts/validate_project.py <project-folder> --final` to check scene/shot counts, unique IDs, required captions, image and board files, and board dimensions. This is a bookkeeping check; manually verify source coverage and visual continuity.

Before image generation, give the user a preflight summary in this shape:

```
Scenes in this group: 3
Planned storyboard panels / shots: 54
New character reference images: 5
Three-panel 16:9 sheets: 18
Baseline image-generation calls: 23 (18 triptychs + 5 references)
Allowed correction calls: up to 4
Maximum calls requiring approval: 27
Estimated time: [range, with assumptions for analysis, generation, review, PDF]
Final file: storyboards.pdf with shot list and all 18 sheets
Proceed with this plan and call ceiling?
```

The numbers above illustrate the format only; derive actual counts from the user's script. For each two- or three-scene group, about 15–20 sheets is a loose target when the script supports 45–60 visual panels. If a scene needs fewer or more panels, say so in the plan. If a scene has no visual shots, explain why before excluding it. Do not start generation until the user confirms the specific plan and call ceiling.
