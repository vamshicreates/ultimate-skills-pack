---
name: song-to-video-studio
description: Research reference YouTube songs and produce rights-cleared original or authorized revised songs with finished lyric or music videos. Use for a repeatable song-to-video production batch, including SelfStudio releases.
---

# Song to video studio

Turn a list of reference songs into a tracked batch of research, original or authorized lyrics, finished audio, visuals, and deliverable videos. For the current SelfStudio batch, the videos are references for learning and the user has a Google AI Pro plan for Google Flow Music. A YouTube link is a research reference, not a license to reuse its lyrics, melody, master recording, or footage.

## Intake and batch record

For each URL, record the video ID, title, channel, duration, observed date, output target (full lyric video, motion music video, short cut, or a combination), aspect ratio, language, and status. Keep one batch record with these fields plus: source rights, exact lyric source, music provider and plan, asset licenses, estimated and actual time, cost or credits, output paths, and outstanding decisions. Use one song as the pilot, then reuse its style and export settings where they fit the others.

Resolve two creative modes before writing or generating:

- **Authorized revision:** The user owns or has permission covering the composition and lyrics. If they want every original lyric retained, preserve every line verbatim, in order, in a locked lyric sheet. Improve the song through section order, added lines, melody, harmony, arrangement, vocal direction, or production within the granted rights. If using the original recording, verify separate permission for the master.
- **Original response (default for this batch):** Use the reference's broad topic, audience need, emotional arc, and genre as research. Write distinct lyrics and melody. Do not upload the reference recording or lyrics to a generator, request a close imitation, clone the singer, or call the result a remix or cover.

Record the user's intended commercial uses (SelfStudio app, YouTube monetization, streaming, advertising, client use) before choosing a provider. If ownership is unresolved, complete research and an original-response creative brief while requesting the specific missing rights information. Do not label a generated asset commercially cleared until its creation plan and terms have been checked.

## 1. Research each reference

Read the watch page and, where accessible, its public metadata: title, description, visible hashtags, date, duration, views, likes, comment count, and representative comment themes. Capture the observation date. Use captions as a navigation aid; for an exact lyric sheet, verify against user-provided words or permitted source audio because singing transcription is error-prone. In this workspace, `../youtube-transcript/SKILL.md` provides a caption path, but it may fail when captions or network access are unavailable.

Build a keyword map from title, description, visible search suggestions, and relevant search results. Label actual ranking observations with the query, region, date, and position. Explain likely relevance and engagement drivers as hypotheses, never as known algorithmic causes. Public counts cannot reveal retention, click-through rate, search terms that brought viewers, or revenue; use the user's YouTube Studio analytics if they control the channel.

Deliver a one-page research brief per song: audience promise, keyword cluster, likely search intent, engagement themes, musical tone and structure, visual conventions, and a specific opportunity to improve originality, clarity, or production. Separate observed facts from interpretation.

## 2. Write the song brief

Listen to authorized audio when available. Describe tempo and groove, energy arc, voice, instrumentation, language, hook placement, repeated phrases, and the listener state the song aims to create. Draft a section map and lyric sheet. For authorized revisions, compare the locked source lyric sheet line by line against the new version and identify additions explicitly. For original responses, check that the hook, line wording, melody direction, and arrangement are independently conceived.

For the current SelfStudio batch, write **affirmation songs**. Make the title a direct, first-person affirmation and sing that exact affirmation as the first line. Keep short, declarative affirmations at the center of every verse and chorus; repeat the title phrase prominently in the chorus and outro. Use plain present-tense language that a listener can say along with the song. Do not replace the affirmations with a narrative, metaphor-heavy lyric, or a delayed poetic setup. Distinguish songs by the affirmation target (money identity, receiving income, financial freedom, confidence, health, love, luck, calm) and by the arrangement. Treat the reference videos as theme and format cues, not as lyric sources. Review the complete lyric sheet with the user before music generation when they request lyric approval.

Set a practical target duration before production. A reference's full running time is not automatically the best new-song length. Use the research to propose the duration and a repeat or extended version only if it serves the listener.

## 3. Generate and finish the audio

Read [music provider and rights checks](references/music-providers.md) when choosing a generator. For this batch, start with the user's Google AI Pro benefit in Google Flow Music, once the account is connected. Check the live plan, terms, territory, download allowance, and commercial-use scope for the account that will actually generate the song. Save the provider, plan, generation date, prompt, asset ID, and a copy or link to the applicable terms in the batch record. A free trial is not evidence of commercial rights.

Generate a small set of candidates within the user's authorized credit or spend limit. Judge each by hook, lyric fidelity, pronunciation, vocal artifacts, musical structure, ending, and resemblance to the reference. Revise or regenerate only the failed sections where the tool supports it. Export the chosen stereo master and, if available, stems. Inspect the audio with `ffprobe`/`ffmpeg`, listen through, and fix clipping, abrupt cuts, or level jumps. Keep the unprocessed generation and final master.

If no rights-cleared music provider is connected, deliver the lyric sheet, musical direction, generation prompt, and visual plan as a production-ready handoff, with audio generation marked pending rather than presenting a video without a finished song as complete.

## 4. Build the visuals and edit

Storyboard the actual chosen audio by section and lyric timing. Generate a consistent image set first; create moving clips where motion adds meaning. Keep visual prompts focused on the new song's imagery and SelfStudio's brand, not on recreating frames from the reference video. Add lyric text as editable overlays so spelling and timing can be corrected. Retain source files and generation records for the assets used.

Choose an editor based on the job: the workspace's music-to-video/HyperFrames route for repeatable beat-synced typography, DaVinci Resolve for detailed timeline work, and FFmpeg for deterministic media processing and export. Generated video clips are optional and may consume credits. Edit to musical phrases or a trustworthy beat grid; confirm lyric lines against the final audio. Produce a draft, inspect opening, chorus, transitions, text safe areas, audio peaks, and ending, then render the final version.

## 5. Quality check and deliver

Verify the exported file exists, plays, has the intended aspect ratio and duration, contains the final master audio, and has legible and correctly timed lyrics. For authorized revisions, repeat the line-by-line lyric preservation check on the displayed text. Keep a separate record of licenses for music, images, video clips, fonts, and any third-party material. Do not promise that a provider license prevents every Content ID claim.

Per song, hand over: final MP4, audio master, exact lyric sheet, thumbnail or cover when requested, title/description/keyword suggestions, editable project or edit specification, and the rights/provenance record. Report what was observed, what was inferred, and any licensing or quality limitation. Update actual time from the pilot before forecasting the rest of the batch.
