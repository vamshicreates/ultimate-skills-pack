#!/usr/bin/env node
/**
 * Fetch a YouTube video's captions and save them as a markdown file named
 * after the video title.
 *
 * Zero dependencies — uses Node 18+ global fetch and a small regex XML reader,
 * so it runs from any directory without an npm install.
 *
 * Usage:
 *   node youtube-captions.js <url-or-video-id> [options]
 *
 * Options:
 *   --out <dir>       Directory to write into (default: current directory)
 *   --lang <code>     Preferred caption language (default: en)
 *   --name <file>     Override the output filename
 *   --timestamps      Write one [MM:SS] line per caption cue instead of prose
 *   --stdout          Print the transcript instead of writing a file
 *   --list-langs      List available caption tracks and exit
 */

const fs = require("fs").promises;
const path = require("path");

// Public Innertube key. It is a client identifier, not a secret — YouTube ships
// it in every watch page. Hardcoding avoids an extra HTML fetch that regularly
// breaks on consent/bot-check interstitials.
const INNERTUBE_KEY = "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8";

// Mobile app clients are the ones that still return captionTracks. WEB returns
// UNPLAYABLE without a PO token, so it is not worth trying.
const CLIENTS = [
  {
    name: "ANDROID",
    context: { clientName: "ANDROID", clientVersion: "20.10.38", androidSdkVersion: 34, hl: "en" },
    userAgent: "com.google.android.youtube/20.10.38 (Linux; U; Android 14) gzip",
  },
  {
    name: "IOS",
    context: { clientName: "IOS", clientVersion: "20.10.4", deviceModel: "iPhone16,2", hl: "en" },
    userAgent: "com.google.ios.youtube/20.10.4 (iPhone16,2; U; CPU iOS 18_1 like Mac OS X)",
  },
];

/**
 * Pull the 11-character video ID out of any YouTube URL shape, or accept a
 * bare ID. Returns null when nothing looks like an ID.
 */
function extractVideoId(input) {
  if (!input) return null;
  const raw = input.trim().replace(/^["']|["']$/g, "");

  if (/^[\w-]{11}$/.test(raw)) return raw;

  const patterns = [
    /[?&]v=([\w-]{11})/,           // watch?v=ID
    /youtu\.be\/([\w-]{11})/,      // youtu.be/ID
    /\/(?:embed|v|shorts|live)\/([\w-]{11})/, // /embed/ /shorts/ /live/
  ];
  for (const pattern of patterns) {
    const match = raw.match(pattern);
    if (match) return match[1];
  }
  return null;
}

/** Ask Innertube for player data, trying each client until one returns captions. */
async function fetchPlayerData(videoId) {
  const failures = [];

  for (const client of CLIENTS) {
    let data;
    try {
      const response = await fetch(`https://www.youtube.com/youtubei/v1/player?key=${INNERTUBE_KEY}`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "User-Agent": client.userAgent },
        body: JSON.stringify({
          context: { client: client.context },
          videoId,
          contentCheckOk: true,
          racyCheckOk: true,
        }),
      });
      data = await response.json();
    } catch (error) {
      failures.push(`${client.name}: ${error.message}`);
      continue;
    }

    const status = data?.playabilityStatus?.status;
    if (status && status !== "OK") {
      const reason = data?.playabilityStatus?.reason || status;
      failures.push(`${client.name}: ${reason}`);
      continue;
    }
    if (!data?.captions?.playerCaptionsTracklistRenderer?.captionTracks?.length) {
      failures.push(`${client.name}: no caption tracks in response`);
      continue;
    }
    return data;
  }

  throw new Error(
    `Could not get captions for ${videoId}. Tried ${failures.length} client(s):\n  ` +
      failures.join("\n  ") +
      "\nThe video may be private, age-restricted, region-locked, or have captions disabled."
  );
}

/**
 * Choose a caption track. Language match matters most (exact, then a regional
 * variant like en-GB for "en"), and within the same language a human-authored
 * track beats auto-captions because ASR misspells names and jargon. Always
 * returns something — a wrong-language transcript is more useful than an error.
 */
function selectTrack(tracks, language) {
  const lang = language.toLowerCase();
  const code = (track) => (track.languageCode || "").toLowerCase();

  const langScore = (track) => {
    if (code(track) === lang) return 2;
    if (code(track).startsWith(`${lang}-`) || lang.startsWith(`${code(track)}-`)) return 1;
    return 0;
  };

  return [...tracks].sort(
    (a, b) => langScore(b) - langScore(a) || (a.kind === "asr" ? 1 : 0) - (b.kind === "asr" ? 1 : 0)
  )[0];
}

/** Decode the HTML/XML entities YouTube leaves in caption text. */
function decodeEntities(text) {
  const named = { amp: "&", lt: "<", gt: ">", quot: '"', apos: "'", nbsp: " " };
  return text.replace(/&(#x?[0-9a-fA-F]+|\w+);/g, (match, body) => {
    if (body[0] === "#") {
      const codePoint = body[1] === "x" || body[1] === "X"
        ? parseInt(body.slice(2), 16)
        : parseInt(body.slice(1), 10);
      return Number.isFinite(codePoint) ? String.fromCodePoint(codePoint) : match;
    }
    return named[body.toLowerCase()] ?? match;
  });
}

/**
 * YouTube double-encodes caption text (&amp;#39; for an apostrophe), so a
 * single decode pass leaves visible entity codes in the output.
 */
function decodeCaptionText(text) {
  return decodeEntities(decodeEntities(text));
}

/** Parse the legacy timedtext XML. It is compact and ASR-friendly (no duplicate cues). */
function parseTimedTextXml(xml) {
  const cues = [];
  const cueRegex = /<text\s+([^>]*)>([\s\S]*?)<\/text>/g;
  let match;

  while ((match = cueRegex.exec(xml)) !== null) {
    const attrs = match[1];
    const start = parseFloat((attrs.match(/\bstart="([^"]*)"/) || [])[1]);
    const duration = parseFloat((attrs.match(/\bdur="([^"]*)"/) || [])[1]) || 0;
    const caption = decodeCaptionText(match[2].replace(/<[^>]+>/g, "")).replace(/\s+/g, " ").trim();
    if (!caption) continue;
    cues.push({ caption, startTime: Number.isFinite(start) ? start : 0, endTime: (Number.isFinite(start) ? start : 0) + duration });
  }
  return cues;
}

/**
 * Parse the json3 format. Rolling auto-captions repeat text across events, so
 * drop the append-only ones to avoid a transcript that stutters.
 */
function parseTimedTextJson3(body) {
  const data = JSON.parse(body);
  const cues = [];

  for (const event of data.events || []) {
    if (event.aAppend) continue;
    const caption = (event.segs || [])
      .map((seg) => seg.utf8 || "")
      .join("")
      .replace(/\s+/g, " ")
      .trim();
    if (!caption) continue;
    const start = (event.tStartMs || 0) / 1000;
    cues.push({ caption: decodeCaptionText(caption), startTime: start, endTime: start + (event.dDurationMs || 0) / 1000 });
  }
  return cues;
}

/** Download a caption track, preferring XML and falling back to json3. */
async function fetchCues(track) {
  const baseUrl = track.baseUrl.replace(/&fmt=\w+/g, "");
  const attempts = [
    { url: baseUrl, parse: parseTimedTextXml },
    { url: `${baseUrl}&fmt=json3`, parse: parseTimedTextJson3 },
  ];

  const errors = [];
  for (const attempt of attempts) {
    try {
      const response = await fetch(attempt.url, { headers: { "User-Agent": "Mozilla/5.0" } });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const body = await response.text();
      const cues = attempt.parse(body);
      if (cues.length) return cues;
      errors.push("empty track");
    } catch (error) {
      errors.push(error.message);
    }
  }
  throw new Error(`Caption track downloaded but contained no usable text (${errors.join("; ")})`);
}

/** Turn a video title into a filesystem-safe basename. */
function sanitizeFilename(title) {
  const cleaned = title
    .replace(/[\/\\:*?"<>|]/g, " ")      // illegal on macOS/Windows
    // eslint-disable-next-line no-control-regex
    .replace(/[\x00-\x1f\x7f]/g, " ")
    .replace(/\s+/g, " ")
    .replace(/^[.\s]+|[.\s]+$/g, "")     // no leading dot (hidden file) or trailing dot/space
    .trim();
  const safe = cleaned.slice(0, 120).trim().replace(/[.\s]+$/, "");
  return safe || "youtube-transcript";
}

function formatTimestamp(seconds) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);
  const pad = (n) => String(n).padStart(2, "0");
  return hours > 0 ? `${pad(hours)}:${pad(minutes)}:${pad(secs)}` : `${pad(minutes)}:${pad(secs)}`;
}

/** Build the markdown document: a header block plus the transcript body. */
function buildMarkdown({ cues, details, track, withTimestamps }) {
  const videoUrl = `https://www.youtube.com/watch?v=${details.videoId}`;
  const kind = track.kind === "asr" ? "auto-generated" : "manual";
  const trackName = track.name?.simpleText || track.name?.runs?.[0]?.text || track.languageCode;
  // YouTube's own track name often already says "(auto-generated)" — don't say it twice.
  const captionLabel = trackName.toLowerCase().includes(kind)
    ? `${trackName} (${track.languageCode})`
    : `${trackName} (${track.languageCode}, ${kind})`;

  let markdown = `# ${details.title}\n\n`;
  markdown += `**Video URL:** [${videoUrl}](${videoUrl})\n`;
  markdown += `**Video ID:** ${details.videoId}\n`;
  if (details.author) markdown += `**Channel:** ${details.author}\n`;
  if (details.lengthSeconds) markdown += `**Duration:** ${formatTimestamp(Number(details.lengthSeconds))}\n`;
  markdown += `**Captions:** ${captionLabel}\n`;
  markdown += `**Fetched:** ${new Date().toISOString()}\n\n`;
  markdown += `---\n\n`;

  if (withTimestamps) {
    markdown += cues.map((cue) => `**[${formatTimestamp(cue.startTime)}]** ${cue.caption}`).join("\n\n");
    markdown += `\n`;
  } else {
    markdown += `${cues.map((c) => c.caption).join(" ").replace(/\s+/g, " ").trim()}\n`;
  }
  return markdown;
}

function parseArgs(argv) {
  const options = { lang: "en", out: process.cwd(), timestamps: false, stdout: false, listLangs: false, name: null, target: null };

  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    switch (arg) {
      case "--lang": case "-l": options.lang = argv[++i]; break;
      case "--out": case "-o": options.out = argv[++i]; break;
      case "--name": case "-n": options.name = argv[++i]; break;
      case "--timestamps": case "-t": options.timestamps = true; break;
      case "--stdout": options.stdout = true; break;
      case "--list-langs": options.listLangs = true; break;
      default:
        if (arg.startsWith("-")) throw new Error(`Unknown option: ${arg}`);
        if (!options.target) options.target = arg;
    }
  }
  return options;
}

async function main() {
  const argv = process.argv.slice(2);
  if (argv.length === 0) {
    console.error(`Usage: node youtube-captions.js <url-or-video-id> [options]

Options:
  --out <dir>      Directory to write into (default: current directory)
  --lang <code>    Preferred caption language (default: en)
  --name <file>    Override the output filename
  --timestamps     One [MM:SS] line per cue instead of flowing prose
  --stdout         Print the transcript instead of writing a file
  --list-langs     Show available caption tracks and exit

Examples:
  node youtube-captions.js "https://www.youtube.com/watch?v=mOak_imYmqU"
  node youtube-captions.js mOak_imYmqU --out ~/Documents/Projects/foo --timestamps`);
    process.exit(1);
  }

  const options = parseArgs(argv);
  const videoId = extractVideoId(options.target);
  if (!videoId) {
    console.error(`❌ Could not find a YouTube video ID in: ${options.target}`);
    process.exit(1);
  }

  const playerData = await fetchPlayerData(videoId);
  const details = playerData.videoDetails || { videoId };
  details.videoId = details.videoId || videoId;
  details.title = details.title || videoId;

  const tracks = playerData.captions.playerCaptionsTracklistRenderer.captionTracks;

  if (options.listLangs) {
    console.log(`${details.title}\nAvailable caption tracks:`);
    for (const track of tracks) {
      const name = track.name?.simpleText || track.name?.runs?.[0]?.text || "";
      console.log(`  ${track.languageCode.padEnd(8)} ${track.kind === "asr" ? "auto-generated" : "manual"}  ${name}`);
    }
    return;
  }

  const track = selectTrack(tracks, options.lang);
  if (track.languageCode.toLowerCase() !== options.lang.toLowerCase()) {
    console.warn(`⚠️  No "${options.lang}" captions; using "${track.languageCode}" instead.`);
  }

  const cues = await fetchCues(track);
  const markdown = buildMarkdown({ cues, details, track, withTimestamps: options.timestamps });

  if (options.stdout) {
    process.stdout.write(markdown);
    return;
  }

  const filename = options.name || `${sanitizeFilename(details.title)}.md`;
  const outPath = path.resolve(options.out, filename);
  await fs.mkdir(path.dirname(outPath), { recursive: true });
  await fs.writeFile(outPath, markdown, "utf8");

  const words = markdown.split(/\s+/).length;
  console.log(`✅ Saved: ${outPath}`);
  console.log(`   Title: ${details.title}`);
  console.log(`   Cues: ${cues.length} | ~${words} words | language: ${track.languageCode}${track.kind === "asr" ? " (auto-generated)" : ""}`);
}

if (require.main === module) {
  main().catch((error) => {
    console.error(`❌ ${error.message}`);
    process.exit(1);
  });
}

module.exports = { extractVideoId, fetchPlayerData, selectTrack, fetchCues, buildMarkdown, sanitizeFilename };
