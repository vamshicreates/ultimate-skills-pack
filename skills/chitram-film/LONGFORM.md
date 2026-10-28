# LONGFORM — YouTube long-form editing: script assembly, multi-cam, screencasts, briefs, finish (add-on)

Use this for **long-form YouTube** (5–30 min tutorials, explainers, AI-tool walkthroughs, interviews,
case studies): a presenter on 1–3 cameras, screen recordings, B-roll and generated clips, cut to a
script. SHORTFORM.md is for 20–60 s vertical clips; this file is for the long horizontal video, the
edit that lives in an NLE (DaVinci Resolve / Premiere) for days and passes through several hands.

**Origin.** The rules come from a professional YouTube editor's working process ("Max's" skill, Sept
2026: the Blender #2 and Passport Rush episodes of a Higgsfield tutorial channel, with the author's
own corrections studied clip by clip), translated and generalised, plus 2026 retention research. The
*observations* from those episodes are in §14 as examples, not as quotas.

Chitram-film has no NLE of its own. For long-form it **prepares, decides, builds and verifies**:
transcripts and take maps (`sf.py ingest`), sync (`tools/timeline/sync.py`), the assembly as a
portable `timeline.json` exported to OTIO / FCP7 XML / EDL (`tools/timeline/timeline.py`), motion
inserts rendered by the engine (MP4, or ProRes 4444 with alpha via `render.mjs --alpha`), briefs as
NLE markers, and the sound pass (SOUND.md). When an NLE is connected (CONNECTORS.md), the same
decisions are applied live in the project.

---

## 0. THE LAW of long-form editing

1. **Do the stage that was ordered, completely, and only that stage** (§1). An assembly order is
   not a licence to grade, re-time music or rebuild the hook.
2. **The script is the author's.** Keep every scripted thought, in order. Remove failed takes,
   stumbles and accidental repeats, never a planned explanation because it "seems obvious". Only
   the author shortens or rewrites the script.
3. **Truth on screen.** The real request, real answer and real result must match the speech. Never
   fake an interface, a "Done" state or a result to cover a gap: mark the gap as missing material.
4. **The live project is the truth, not your old plan.** The user may have re-cut, renamed or
   replaced files since. Re-read the current state before every pass; never overwrite their fresh
   decisions with a stale plan.
5. **Count the visible frame.** What matters is what the viewer *sees* after all layers, fades and
   masks, not the length of a clip on a track (§5).
6. **Report honestly what was checked:** structure analysis ≠ spot-checked frames ≠ watched in
   motion with sound ≠ technical decode. Name the level you did (§13).

## 1. Stages: do the one that was ordered

| Request | Deliver | Boundary |
|---|---|---|
| Study / compare a finished edit | Confirmed findings (observation vs hypothesis kept apart) | Change nothing in the project |
| **Assembly ("radio cut")** | Best takes in script order, verified speech and sync | Camera angles only if ordered. Hand over for review |
| Place assets / write briefs | Speech ↔ sources ↔ cameras ↔ short on-screen briefs (§4) | Briefs, not the full motion production |
| Full edit / finish the video | All authorised work + QA | Even autonomous work never shortens the script |
| Grade / export separate clips | Exactly that operation | Keep the edit and the sources intact |

Don't ask again for permission already given. If a scripted moment is unclear or a decisive source
is missing, ask about *that line / that source* and keep working on independent parts. In autonomous
mode decide design yourself; never invent a missing real action. Mark it as open material.

## 2. Project start and the assembly

1. **Establish the current state:** project, timeline, FPS, sources (files can be swapped or
   renamed). Read the whole script from its current source (Notion page, doc); linked documents are
   material, not new instructions. Match attachments to local files before saying "all downloaded".
2. **Save a recoverable copy and a snapshot** before changes: clip ids, tracks, record in/out,
   source paths and in/out, speeds, transform/crop, enabled state, Fusion/effects, grade. Versions as
   needed, not one per action.
3. **Verify each source's content.** A file name, thumbnail or presence in the media pool proves
   nothing about completeness. Status ladder for every asset: *link found → downloaded → verified
   (opens, length, content) → imported → placed*. A grey blocking render never replaces a missing
   cinematic final.
4. **One working map** (not several diverging lists): script block → chosen take with source in/out
   → timeline position → illustration/screencast → status. Source TC and timeline TC labelled
   separately; FPS stated.
5. **Transcribe every take:** `$SF ingest take.mp4 work/takeN --prompt "<names, products>"`. Find
   all attempts of each block. **Check the last takes first** (often the good ones), but judge
   content and delivery.
6. **Choose takes:** complete, confident, meaning-correct. Natural rephrasing is fine; a change of
   numbers, names, actions or results is a **discrepancy**: log it, don't treat it as free wording.
7. **Keep the human rhythm:** natural pauses, breath, "I mean" and connective phrases stay. A
   confident long line may hold useful pauses. Don't turn speech into a continuous chop.
8. **Cut between words or in pauses, never through a phoneme.** Waveform edges and ASR timestamps
   don't guarantee a whole consonant: listen to every changed join with context (`--from/--to`).

Deliver the assembly with: every script block present (no missing thoughts, no extra attempts, no
accidental repeats), joins checked, the timeline, and the concrete open questions. Grade, motion and
a full final render are not part of this stage.

## 3. Multi-cam: roles, sync, protected tracks

**Sync first:** `python $SKILL/tools/timeline/sync.py master_audio.wav camA.mp4 camB.mp4 camC.mp4`.
It reports each offset and checks **drift** between the start and the end of long sources (> 20
ms/min: split the clip or retime the audio). Confidence < 1.5 = check by eye on a clap or a hard
consonant.

Establish the real roles from the footage (file names don't prove framing). Typical:

| Angle | Use | Switch when |
|---|---|---|
| **A**, frontal main | addressing the viewer, conclusions, a compact accent, up to 2 small visuals in verified empty zones; also the small presenter window over a big screencast | a phrase/gesture completes |
| **B**, close-up | reactions, short links, "let me show you", a change of case, hiding a mismatched pose. **No graphics on visible B.** Use it meaningfully; don't drop it, don't make it the main angle | the end of a self-contained line, before a demo |
| **C**, side wide | big cards, images, videos and diagrams in the free side of the frame. Choose the side by where the presenter actually is | hold while the explanation develops; switch when it's done |
| Screen big + small A | real work in an interface | after the action and a readable result |

- In pure talk with no visuals, a switch roughly every **~4 s** is a guide, adjusted to phrase and
  gesture, never a timer. A developing visual may need a long A/C hold. Never rotate A-B-C
  mechanically: dynamics come from a change of *meaning* (action → detail → result → comparison).
- A mismatched pose at a speech join → cut to another synced angle at a safe point between words.
- **Protected structure:** original synced angles stay on V1–V3; the camera edit is copies on V4.
  When an inserted standalone piece (e.g. a finished clip shown without speech) shifts program time,
  move the lower angles and their audio together with it. Don't silently rebuild an agreed structure.
- Plan the visual's interval *with* the camera: an 8 s card on C needs the whole 8 s of C with
  natural edges. If a card appears on a cut, its first visible frame is that cut.

## 4. Short on-screen briefs (for the motion designer, or for you later)

Formula: **what to show (final text/object) → where / which angle → on which words it appears and
changes → when it leaves.**

> C, left above the chair. DIRECTION → BLOCKING → FINAL VIDEO. Add one at a time on their words.
> Soft entrance, slight perspective. Remove on "We'll work".

- Give the **final on-screen text** in the right language, a concrete action and the source (file +
  source in/out) when it must be found. Never "make it nice", "highlight the prompt", "by the speech":
  name the line, the trigger words, the result.
- One brief = one editable text layer / marker on its interval. Project-wide rules, history and the
  missing-files registry live **outside** the frame. Update briefs when material is found; a stale
  "file missing" over a found clip is an error. Briefs are off in the clean export, kept in the project.
- In chitram-film, briefs are markers: `timeline.py add-markers tl.json briefs.json` →
  exported in OTIO/XML, as a Resolve marker EDL (`--markers-edl`) and as CSV.

Executable examples:
- **Real interface:** "Chat big. Zoom the paragraph from 'write the lyrics…' to '…move by move', dim
  the rest. Hold the highlight on this line; take the text from the recording."
- **Split with process:** "Chat left, tool right; two rounded cards on a dark background. Speed up
  the waiting, show the room being built by 'right side'. Let the result be read before exit."
- **Linked frames:** "C, left, three frames: room → hose → container. Appear on the enumeration,
  joined by arrows. On 'camera pulls back' show the exit to the product shot. Remove before the next topic."
- **Missing recording:** "NEED SCREENCAST: installing the plugin. Show Plugins → Blender → download →
  install. Interval = this line. Keep this brief until the recording exists." Replace a gap with a
  diagram only by agreement: a diagram explains a sequence, it doesn't prove it happened.

Check before handing over: from one note, is it clear what appears, where, from what material, and
when it leaves? Is there room on that angle? Is the text final and readable in time? Does it
contradict the real screencast?

## 5. Visual continuity: no "blinks"

A long camera clip on a lower track can show for only a few frames between two upper inserts: that
is the same accidental short shot as a stray trim. **Count the visible frame.**

- Join related screencasts, top shots and full-screen visuals without a stray presenter between
  them. A change of track doesn't justify a break.
- Matching clip edges don't guarantee continuity: a fade-out, a transparent first frame, a mask or
  a background leaving early can reveal the lower camera. Check the whole composite at entry and exit.
- Fix by **extending the current visual or starting the next one earlier** (using real handle
  material). `screencast → 9 frames of C → A on a line` becomes `screencast → A`, keeping A in sync.
- A pose jump left on the same camera after an insert: cover the join with a fitting visual or cut
  to another synced angle, and check the *exit* of the cover too (a short cover just moves the jump).
- Never shorten speech or shift the whole edit to close a visual gap; change the coverage over the
  current audio. Never fill missing process with a freeze, a loop or empty continuation.
- Visible fragments under ~1 s are **candidates to review**, not auto-deletes: a deliberate reaction
  or a fast results montage may be short. Return to the presenter for a reason the viewer can read.
- Adjacent clips from one source with continuous source time are one shot, not a jump cut.

`timeline.py check` flags overlaps and flash-gaps (< 1 s gaps where a lower layer shows through).

## 6. Screencasts, inserts and composition

- **Explaining an idea:** presenter big, illustration beside (big visual in C's free side, compact or
  paired on A). **Showing work:** the interface big, a small A in a free corner if it doesn't cover
  buttons, messages, viewport or result. **A standalone finished result:** full screen, original
  sound by context; as proof, the matching blocking can sit small in a free corner of the result.
- Watch the whole source in motion; find request, send, real work, checks, result. Note source
  in/out against the lines. A contact sheet helps navigation; it doesn't prove what happened between frames.
- **Speed up waiting and long work** so the essential actions and the result show, with time to read
  them. Don't spend the interval on "Thinking…". Choose the END of the useful action first, then the
  speed for the window. Don't end an insert mid-typing or before the important result. Use the NLE's
  native retime with handles, never a short pre-exported piece that can't be extended.
- **Split:** conversation left, the tool/result right; crop the chat to the conversation, crop the
  tool to the action. Solo chat: show the whole interface; a zoom on an exact paragraph is a separate,
  deliberate accent. **Cards on C:** in the free space with air from the edge and the presenter;
  slight perspective, rounded corners, soft shadow; the caption belongs to its card. Keep important
  references whole (face, full figure, shoes, sets of views).
- **Never stretch** an image. Aspect mismatch: an agreed crop or a designed composition (rounded
  cards on a textured background). Accidental black bars are errors; designed margins are composition.
- Alternate a top shot of hands and the screencast of the same process by action and stage: gesture
  on the tablet → readable detail in the interface → finished result. Never show the finished result
  and then silently go back to an earlier unfinished version (except as an explicit comparison).
- **Truth:** separate chat and tool recordings illustrate one process but don't prove click-by-click
  sync. A discrepancy (57 figures on screen vs "66" in speech; 13–14 cm vs 10 cm) is logged concretely;
  "keep the video and note it in the brief" doesn't mean it's fixed. A new illustrative chat only when
  ordered, built from a verified real screenshot, never a generic messenger mock. Agreed cleanup of a
  service banner is separate from changing facts: keep the original and the cleaned version.

## 7. Motion and typography for long-form

- Reveal words, lines or cards by **units of meaning**, synced to the speech; never the whole list at
  once. Letter animation only for short phrases, if it doesn't delay reading. After appearing, hold a
  readable state. No general pulsing, endless drift or everything-moves.
- Entrance: gentle ease, small move or scale, blur if needed. Motion blur only along real movement,
  never on text that should be read. Exits finish before the context changes, with no residual opacity.
- A zoom is justified by a change of attention, and something must develop after it.
- **Between different cases the default is a clean cut.** A wipe/mask only for related pairs
  (blocking → generation). No random slide-left, dissolve or zoom transitions as a universal answer.
- Prototype several *different* tasks on real frames (sequential text, a card, a split, a prompt
  highlight) and check readability, scale, timing and smoothness before multiplying one layout.
- Chitram builds these inserts in the engine (ENGINE kit) and delivers them as editable projects +
  renders: full-frame MP4, or **ProRes 4444 with alpha** (`render.mjs --alpha`, background layers
  marked `data-alpha-hide`) to drop over footage in the NLE.

## 8. The hook and retention (long-form)

- Study the reference hook *in motion*: shot lengths, beats, how readable each case is, entry/exit
  motion, how neighbours connect. Don't copy only a transition's name.
- Build a chain of **recognisable cases with cause and effect** (blocking → its result). Dynamics
  come from content, musical accents and variety, never from 0.2 s unreadable flashes.
- Plain cuts between independent shots; a soft wipe only for linked pairs. A zoom *inside* a shot is
  a change of focus, not a zoom transition. If titles were removed by the user, don't bring them back
  "for richness". If a speed change is forbidden, sync with music, selection and cuts instead.
- Music ends as speech starts when so specified; the user chooses where the hook is built (NLE or
  engine): follow the latest choice and keep it editable when asked.
- **Retention research (2026):** the first big drop-off zone is ≈ 25–35 s, so place the first
  deliberate pattern interrupt there; afterwards change something meaningful every ~10–15 s in talk
  (angle, zoom, insert, on-screen text) and add a stronger interrupt every ~60–90 s (a chapter card,
  a demo, a reveal). Use J-cuts (next audio first) and L-cuts (audio continues over the next picture)
  to carry the viewer across sections. A pattern interrupt must carry *new information*; change for
  its own sake reads as noise.

## 9. Colour: soft and natural

Keep the accepted grade. When grading is ordered: match A/B/C (a shared/remote grade), check the
LUT and colour management of *this* project, never apply a LUT twice, and don't put the camera look on
screencasts and generations. Soft must keep volume and separation: living skin, detail in shadows and
highlights, cool background vs warm wood. Don't lift all shadows or desaturate "to be soft". Same
version names don't prove same parameters: check the node tree and the image. Compare the export with
the accepted look, not only the settings.

## 10. Sound for long-form

Separate stems: speech, music, the original sound of shown results, SFX (SOUND.md). No random loud
promo sound under the voice; a standalone result keeps its own sound. Check the mixer and routing when
a single master appears: an enabled track doesn't prove doubling, a WAV on the timeline doesn't prove
a correct mix. Listen to transitions, sync and the whole programme; measure with the right meter.
Sample peak, RMS, true peak and LUFS are different numbers. Deliver −14 LUFS / −1 dBTP for YouTube.

## 11. Export separate clips with speed kept, transform/crop removed

1. Work on a copy of the named timeline; list **every use** of each clip (repeats with different
   speed or range are separate items).
2. Keep the time map (speed-ups, slow-downs, reverse, ramps) and chosen ranges; bake speed into
   *this* export.
3. Reset spatial changes: zoom 1, position/rotation/anchor/pitch/yaw 0, flip off, crop 0, dynamic
   zoom off; remove their keyframes. Check Fusion/colour sizing too. Don't blindly delete all effects.
4. Export each file to its own folder at the source's full image and aspect ratio.
5. Verify retime in the chosen render mode on one sped-up and one complex clip first.
6. Check durations, start/middle/end frames, no crop/zoom. Deliver a map: file name → source →
   timeline interval. Repeats must not overwrite each other.

## 12. NLE realities (learned in DaVinci Resolve Studio 21; verify on the installed version)

- Read the current project/timeline, record in/out, source path/FPS, speed, properties, versions
  and enabled state; snapshot before edits; **after every operation read the real state back**, not
  only the returned "success". `SetInput`-style calls may return None on success: read the value.
- Don't confuse source frames with timeline frames, or inclusive with exclusive ends. Test
  `AppendToTimeline`, XML and offset conventions on a short known source first.
- A retimed clip's left offset is not necessarily the raw source frame. Copying grade, properties
  and Fusion doesn't carry native retime: compare start/middle/end content before replacing a clip.
- Import paths: FCPXML time maps can arrive as compound clips; FCP7 XML `timeremap` was the working
  fallback. After any import check: direct link to the original media item, range, FPS, speed and
  ramp points, frame length and handles, no hidden compound or baked short export.
- Fusion: keep MediaIn and the retime chain (no silent baked Loader); use `PolylineMask`; check tool
  ids and connections after `.comp` import; Fusion time on retimed clips can differ from Edit time;
  check the last frames for residual alpha; draw arrows as geometry if Unicode glyphs render as boxes.
- Never change the timeline during a render; never close the user's unsaved work. If parallel user
  edits appear, re-read and limit your changes to your own current area.
- Cleanup when ordered: archive the full version, group active layers by purpose, label tracks. A
  disabled clip may be an agreed comparison variant: learn its role before removing anything.
- FCPXML exports may be bundles (`Info.fcpxml` inside), not single files.
Connected-tool specifics (Resolve's native MCP, scripting, Premiere) are in CONNECTORS.md.

## 13. QA by stage, and the report

- **Assembly:** every scripted thought present, in order; only failed attempts and accidental
  repeats removed; rephrasings keep meaning (numbers, names, causality checked); no clipped words;
  natural pauses and "I mean" kept; changed joins listened to; A/B/C and audio in sync.
- **Cameras and assets:** the agreed track holds the camera edit; protected sources follow the
  current time; visible angle fits the visual and line; no graphics on visible B; no presenter blinks
  at entries/exits or between related visuals (visible intervals with all layers); each fixed join
  watched in motion with context and its first/last frames checked; every source exists and shows the
  right process; typing finished and results readable before an insert leaves; native retime with
  handles; no freezes or loops for process; margins designed or absent; nothing important cropped;
  blocking and generation really match in action, angle and time.
- **Briefs and motion:** each brief has object, angle/position, speech triggers and exit; text final;
  no stale "missing"; a short native render of each new animation type checked (first frame, entry,
  readable state, change, exit, last frames); smoothness judged in motion; service briefs off in the
  clean export.
- **Colour, sound, whole file:** A/B/C match, no double LUT; speech, music, SFX and original sound
  listened through; routing checked; final export probed (resolution, FPS, duration, end frame, audio,
  decodes to the end). **Watch the whole programme in motion with sound.** If the tools can't play
  it fully, say so and don't claim a full check.
- **Report:** what changed, which timeline/file is delivered, what was checked and at which level
  (structural comparison · frame review · motion review · full playback with audio · technical file
  check), and the real remaining limits. ETA from remaining operations and render; explain changes.
  Send files only to the destination the user named for *this* job.

## 14. Carrying learnings (and the source examples)

Keep the user's words, your observations and your hypotheses apart. A confirmed correction refines
the process; one unusual frame doesn't create a universal rule. Distinguish a permanent rule from a
one-video decision.

Observed in the author's final of Blender #2 (approximate times; examples, not quotas):

| Where | What the author changed | Reusable lesson |
|---|---|---|
| 00:20–00:25 | flat list → sequential DIRECTION / BLOCKING / FINAL VIDEO with perspective on C | reveal by meaning words, fit into free space |
| 01:27–01:32 | generic diagram → the real BLOCKING scene model | show the concrete thing for a concrete object |
| 01:41–02:07 | install/connect diagrams → real interface recordings | a real instruction needs the real screen actions |
| 02:20–02:30 | split → two rounded horizontal cards on a dark warm background | compose the whole frame; designed margins ≠ black bars |
| 02:39–02:52 | presenter A small over the demo | the interface leads during work; the presenter stays present |
| 03:57–04:00 | the key prompt bigger, surroundings dimmed | one precise readable object of attention |
| 04:16–04:28 | flat big insert → compact card with perspective/shadow + linked caption | scale, margins and caption-to-image link matter |
| 04:59–05:30 | big final + matching blocking in a free corner | prove input→result visually; corner adapts to the frame |
| 06:24–06:32 | schematic → real frames with arrows | explain a sequence of shots with a storyboard of real frames |
| 07:33–07:45 | stages reveal in short groups, then BLOCKING → SEEDANCE 2.5 → FINISHED SHOT | never show the whole list at once; sync to speech |
| 07:51–08:06 | product demo goes full screen | an important action isn't always a small side insert |
| 14:48–14:54 | abstract diagram → two short messages about changing the final angle | a concrete mini-example beats a generic label |

Camera holds in that final (median, base camera track; upper layers may cover it): A 5.1 s, B 3.6 s,
C 7.0 s. Statistics, not targets. The author's style (white + lime text, warm dark backgrounds, soft
perspective) belongs to that channel, not to every brand. Passport Rush taught the continuity rules
of §5: presenter blinks hidden by long lower clips, 9 stray frames of C after a screencast, recordings
leaving before typing finished, and the need to re-read the live timeline after the author's edits.
