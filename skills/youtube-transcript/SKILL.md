---
name: youtube-transcript
description: Fetches the captions/transcript of a YouTube video and saves it as a markdown file named after the video title. Use this whenever the user pastes a YouTube link (youtube.com/watch, youtu.be, /shorts, /live) or a video ID and asks for the transcript, captions, subtitles, script, "what does this video say", or wants the video's content pulled into the project as text — and also as the first step whenever a task requires reading, summarising, analysing, or repurposing what is said inside a YouTube video.
---

# YouTube transcript

Pull a video's captions and drop them into the working folder as `<Video Title>.md`.

## How to run it

One command does the whole job — it resolves the video ID, fetches the title and
captions, and writes the file:

```bash
node .agents/skills/youtube-transcript/scripts/youtube-captions.js "<youtube-url-or-id>"
```

If the skill is installed globally rather than in the project, the script
lives at `~/.gemini/config/skills/youtube-transcript/scripts/youtube-captions.js`
(or `.claude/skills/youtube-transcript/scripts/youtube-captions.js`)
instead — use whichever path exists.

Run it from the project root (or pass `--out`), because the script writes to the
current working directory by default — that's what makes the transcript land
"in the same folder" the user is working in.

Quote the URL. YouTube links contain `?` and `&`, which the shell will otherwise
split or glob, and the script will see a truncated argument.

The script takes a full URL or a bare 11-character ID, so paste whatever the
user gave you without pre-processing it.

### Options

| Flag | Effect |
|---|---|
| `--out <dir>` | Write somewhere other than the current directory |
| `--lang <code>` | Preferred caption language (default `en`) |
| `--name <file>` | Override the output filename |
| `--timestamps` | One `**[MM:SS]** text` line per cue instead of flowing prose |
| `--stdout` | Print the transcript instead of writing a file |
| `--list-langs` | Show which caption tracks the video actually has |

Default to prose. It reads better and is what downstream summarising or
rewriting work needs. Reach for `--timestamps` when the user wants to cite
moments, cut clips, or navigate to a point in the video.

Use `--stdout` when the user only wants an answer *about* the video and never
asked for a file — piping it into your context beats writing a file they didn't
request. If they asked for the transcript to be saved, write the file.

## Reporting back

Print-worthy facts come from the script's own output. Tell the user the saved
filename and give a one-line sense of what the video covers, so they know the
right video was fetched without opening the file. Don't paste the whole
transcript back into the conversation — these run to thousands of words.

## Multiple videos

For several links, run the command once per video. They're independent, so a
failure on one shouldn't stop the rest — collect the results and report which
ones worked at the end.

## When something goes wrong

The script prints the reason it failed; the fix depends on which reason:

- **"no caption tracks" / "captions disabled"** — the uploader never enabled
  captions and YouTube hasn't auto-generated any. There is no transcript to
  fetch. Say so plainly rather than retrying; the alternative is downloading
  audio and transcribing it, which is a much bigger job worth asking about first.
- **Private, age-restricted, or region-locked** — the video isn't reachable
  anonymously. Nothing in this skill can work around that.
- **`No "en" captions; using "xx" instead`** (a warning, not an error) — the
  transcript still saved, just in another language. Mention it, and offer
  `--list-langs` if they wanted a specific one.
- **Network or transient HTTP errors** — one retry is reasonable. If it fails
  twice, report it instead of looping.

The script has no npm dependencies and needs no API key, so a failure is about
the video or the network, never a missing install. It needs Node 18+ for global
`fetch`.

## Fallback

If the script is genuinely broken (not just a caption-less video) and the
`mcp__youtube__getTranscripts` tool is available in the session, use it to get
the text, then write the same markdown file yourself: an `# Title` heading, the
video URL / ID / channel metadata lines, a `---` rule, then the transcript body.
Keeping the file shape identical matters because other work in this project
reads these files.
