---
name: voicebox-skill
description: Use Voicebox (jamiepine/voicebox), the local open-source ElevenLabs alternative, to clone voices, generate voiceovers to audio files, speak aloud, or transcribe audio via its local API/MCP at 127.0.0.1:17493.
---

# Voicebox — local voice cloning, TTS and transcription

Voicebox (https://github.com/jamiepine/voicebox, docs https://docs.voicebox.sh) is a desktop app
that runs a local server at `http://127.0.0.1:17493`. It only listens while the app is open.
No API keys, no cloud. Use it whenever the user wants a voiceover, narration, a cloned voice,
spoken notifications, or a transcript — instead of ElevenLabs.

## 0. Check it's running

```bash
curl -s -m 3 http://127.0.0.1:17493/health
```

- No response → ask the user to open the Voicebox app (download: https://voicebox.sh or
  https://github.com/jamiepine/voicebox/releases; macOS Intel uses the x64 build, Apple Silicon the arm64/MLX build).
- The calls must run on the user's own computer (a cloud sandbox can't reach their localhost).
- First generation with an engine downloads its model — check `GET /models/status`; trigger with
  `POST /models/download`. A `model_not_downloaded` error means: download it in Voicebox → Models.

## 1. Pick a voice

```bash
curl -s http://127.0.0.1:17493/profiles   # → [{id, name, language, voice_type, ...}]
```

Profiles are addressed by **name (case-insensitive) or id**. If the user names a voice that
doesn't exist, list profiles and ask — never silently substitute.

## 2. Generate a voiceover to a file (most common)

Use the OpenAI-compatible endpoint — returns finished audio in one response:

```bash
curl -s -X POST http://127.0.0.1:17493/v1/audio/speech \
  -H 'Content-Type: application/json' \
  -d '{"model":"tts-1","voice":"Morgan","input":"Every great film starts with one line.","response_format":"mp3","speed":1.0}' \
  --output voiceover.mp3
```

- `voice`: profile name/id. `model`: `tts-1` = the profile's configured engine, or an engine
  (`qwen`, `qwen_custom_voice`, `luxtts`, `chatterbox`, `chatterbox_turbo`, `tada`, `kokoro`).
- `response_format`: `wav` (default), `mp3`, `flac`, `opus`, `pcm`, `aac` (needs ffmpeg).
- `speed` 0.25–4.0 (pitch-preserving). `instructions`: delivery direction ("warm, slow, cinematic") — Qwen only.
- Max 10,000 characters per call; split longer scripts by paragraph and concatenate with ffmpeg.
- Not saved to Voicebox history. Save output next to the user's project files with a clear name.
- Errors come back as `{"error":{"code":...}}`: `voice_not_found`, `model_not_downloaded`,
  `engine_not_compatible`, `unsupported_format`.

For tracked generations (show in the app's history, seeds, effects): `POST /generate` with
`{"profile_id","text","language","seed","instruct","engine"}` → returns an id; poll
`GET /generate/<id>/status` until `completed`, then download `GET /audio/<id>`.

## 3. Speak aloud (notify the user)

```bash
curl -s -X POST http://127.0.0.1:17493/speak \
  -H 'Content-Type: application/json' -H 'X-Voicebox-Client-Id: claude' \
  -d '{"text":"Render finished.","profile":"Morgan"}'
```

Plays on the user's speakers with an on-screen pill. Only do this when the user asked for spoken output.
With the MCP server connected, use the `voicebox_speak` tool instead (same fields: `text`, `profile`,
`engine`, `personality`, `language`).

## 4. Clone a new voice

Only clone a voice the user owns or has explicit consent to use. Never clone a celebrity or
another real person without consent.

```bash
# create the profile
curl -s -X POST http://127.0.0.1:17493/profiles -H 'Content-Type: application/json' \
  -d '{"name":"Vamshi","language":"en","voice_type":"cloned"}'
# add a clean 5–30 s sample + its exact transcript (wav/mp3/m4a/flac/ogg)
curl -s -X POST http://127.0.0.1:17493/profiles/<profile_id>/samples \
  -F "file=@sample.wav" -F "reference_text=Exact words spoken in the sample."
```

Tips: one speaker, no music/reverb, consistent mic. Several samples improve quality.
If no transcript is known, transcribe the sample first (step 5) and have the user confirm it.
Optional `personality` (free-text persona) lets `personality: true` rewrite text in character via the local LLM.

## 5. Transcribe audio

```bash
curl -s -X POST http://127.0.0.1:17493/transcribe -F "audio=@recording.wav" -F "model=whisper-turbo"
```

MCP: `voicebox_transcribe({audio_path: "/absolute/path.wav", model: "turbo"})`.

## Languages

Supported codes: zh en ja ko de fr ru pt es it he ar da el fi hi ms nl no pl sv sw tr.
**Telugu (te) and Tamil are not in the list** — for Telugu lines, tell the user up front; options are
Hindi/English voiceover, or romanized Telugu through an English voice (expect an accent), and
test a short line before generating a whole script.

## MCP setup (optional, for the voicebox_* tools)

Claude Code:
```
claude mcp add voicebox --transport http --url http://127.0.0.1:17493/mcp --header "X-Voicebox-Client-Id: claude-code"
```
Project `.mcp.json`:
```json
{"mcpServers":{"voicebox":{"type":"http","url":"http://127.0.0.1:17493/mcp","headers":{"X-Voicebox-Client-Id":"claude-code"}}}}
```
Stdio-only clients (Claude Desktop): command `/Applications/Voicebox.app/Contents/MacOS/voicebox-mcp`,
env `VOICEBOX_CLIENT_ID=claude-desktop`. Pin a default voice per client in Voicebox → Settings → MCP.
Tools: `voicebox_speak`, `voicebox_transcribe`, `voicebox_list_captures`, `voicebox_list_profiles`.
