# DaVinci Resolve hand-off (optional final grade)

The engine already does a light correction and one of the reference looks, so most reels need no extra
grading. When you want to finish in Resolve:

```bash
python pulse.py render work/timeline.json --grade none --prores --out renders/reel_flat.mov  # styled edit, no correction/look
python pulse.py luts --out luts                                                             # pulse_moody/airy/overcast/natural.cube
```

**In Resolve (Free or Studio)**
1. New project, timeline **1080×1920, 30 fps** (Project Settings → Master Settings → custom resolution 1080×1920).
2. Import `reel_flat.mov` (the effects, colour pop and titles are already in it).
3. Copy the `.cube` files into Resolve's LUT folder, then *Project Settings → Color Management → Update Lists*:
   - macOS: `/Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT/`
   - Windows: `C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\LUT\`
4. Color page: on node 1 do exposure/balance, on node 2 *right-click → LUT → pulse_moody* (and so on per
   section: blade the clip at the look markers: the drop and ~82 %). Lower the node's Key Output Gain to
   taste. The same LUTs give the same look as the engine.
5. Deliver: H.264 or H.265, 1080×1920, 15–25 Mbps, audio AAC 320 kbps.

**If a DaVinci Resolve MCP / scripting connection is available to the agent:** do the same steps through it:
create the project and timeline, import the flat render, add markers at each `grade.sections[].start`,
apply the LUT per section on the Color page, then render with a 1080×1920 H.264 preset. Resolve's scripting
API needs Resolve running (Studio for external scripting) and *Preferences → System → General → External
scripting using: Local*.

Order of operations: **finalise the edit first** (engine or FilmCraft), then grade. The colour pop and blur
pulse are baked into the flat render, so a heavy grade on top should keep reds recognisable.
