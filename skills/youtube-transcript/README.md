# youtube-transcript

A [Claude Code](https://claude.com/claude-code) skill that pulls a YouTube video's
captions and saves them as a markdown file named after the video title.

Paste a link, get `Video Title.md` in your working folder. No API key, no npm
install, no `yt-dlp`.

## Install

Clone it straight into your skills directory.

**For one project:**

```bash
git clone https://github.com/shyamwl/youtube-transcript-skill.git \
  .claude/skills/youtube-transcript
```

**For every project (personal skills):**

```bash
git clone https://github.com/shyamwl/youtube-transcript-skill.git \
  ~/.claude/skills/youtube-transcript
```

The directory name matters — Claude Code looks for `<skills-dir>/<name>/SKILL.md`,
so keep it as `youtube-transcript`.

Requires Node 18+ (for global `fetch`). Nothing else.

## Use

Just paste a link into Claude Code:

> get me the transcript of https://www.youtube.com/watch?v=dQw4w9WgXcQ

Claude picks up the skill on its own — for transcripts, and also as a first step
whenever a task means summarising, analysing, or repurposing what's said in a
video.

## Run it directly

The skill is one zero-dependency script, so it works fine outside Claude Code:

```bash
node scripts/youtube-captions.js "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

Quote the URL — YouTube links contain `?` and `&`, which the shell will
otherwise split.

| Flag | Effect |
|---|---|
| `--out <dir>` | Write somewhere other than the current directory |
| `--lang <code>` | Preferred caption language (default `en`) |
| `--name <file>` | Override the output filename |
| `--timestamps` | One `**[MM:SS]** text` line per cue instead of flowing prose |
| `--stdout` | Print the transcript instead of writing a file |
| `--list-langs` | Show which caption tracks the video actually has |

Accepts a full URL (`watch`, `youtu.be`, `/shorts`, `/live`, `/embed`) or a bare
11-character video ID.

## How it works

It asks YouTube's Innertube `player` endpoint for the video's caption tracks
using the mobile app clients (`ANDROID`, then `IOS`), which still return
`captionTracks` without a PO token, then fetches and flattens the timed-text XML.
The Innertube key in the source is YouTube's public client identifier, not a
secret.

## Limits

- **No captions, no transcript.** If the uploader disabled captions and YouTube
  auto-generated none, there is nothing to fetch. Transcribing the audio is a
  different, much bigger job.
- **Private, age-restricted, or region-locked videos** aren't reachable
  anonymously.
- YouTube's internal API is unofficial and can change without notice.

## License

MIT — see [LICENSE](LICENSE).
