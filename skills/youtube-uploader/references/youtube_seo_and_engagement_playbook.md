# YouTube SEO & View-Generation Playbook (`youtube_seo_and_engagement_playbook.md`)

Use these proven strategies to maximize **Search Ranking**, **Suggested Video Impressions**, **Click-Through Rate (CTR)**, **Average View Duration (AVD)**, and **Comment/Like Velocity** for every video uploaded by `youtube-uploader`.

---

## 1. Pre-Upload Local File SEO (Filename + MP4 Container Atoms)

Before a video file is ever selected in YouTube Studio, optimize its raw file properties using `scripts/prepare_video_package.py`:

1. **SEO Filename Slug**:
   - Never upload a file named `final.mp4` or `export_v1.mp4`.
   - Rename/copy the file to `<Primary-Keyword-Song-Title-Official-Lyric-Video-4K>.mp4` (e.g., `Sri-Siddhi-Vinayaka-Telugu-Devotional-Song-Lyrics-Official-Lyric-Video.mp4`).
2. **Embedded MP4 Container Meta Tags (`moov`/`udta` Atoms via `ffmpeg`)**:
   - Write standard MP4 metadata keys losslessly (`-c copy -movflags +faststart`):
     - `title`: Full YouTube SEO title
     - `artist` / `author`: Channel / Creator name
     - `album`: Song title & collection
     - `genre`: Genre (e.g., `Devotional / Indian Classical / Music`)
     - `comment` / `description`: First 250 chars of SEO description + core keywords
     - `date`: Release year (`YYYY`)
     - `language`: ISO 639-2 code (e.g., `tel`, `hin`, `eng`, `tam`, `san`)
   - Stream-order optimization (`-movflags +faststart`) ensures YouTube's ingestion transcoders begin processing HD/4K streams immediately without waiting for the end of the file.

---

## 2. High-CTR + High-Search-Intent Title Formula (`<= 100` chars, Ideal `55–75` chars)

A great YouTube title must serve two audiences simultaneously: **Search** (exact phrases people type) and **Browse/Suggested** (emotional intrigue that makes viewers click).

### Formula for Lyric & Music Videos:
```text
[Native Script Hook / Song Title] ([English Transliteration]) | [Genre/Deity/Mood Keyword] | Official Lyric Video
```
- **Example (Devotional / Regional)**:
  `శ్రీ సిద్ధి వినాయకా (Sri Siddhi Vinayaka) | Powerful Ganesh Bhajan & Telugu Devotional Song | Lyrics` (99 chars)
- **Example (Indie / Pop / Romantic)**:
  `Midnight Rain (Official Lyric Video) | Emotional Indie Acoustic Song with Lyrics [4K]` (85 chars)

### Title Rules:
- Put the **#1 searchable song title or hook phrase in the first 40 characters** so it is never cut off on mobile screens.
- Include bilingual hooks (`Native Script + English Transliteration`) whenever the lyrics are in Telugu, Hindi, Tamil, Kannada, Malayalam, or Sanskrit — this captures both native-script searchers and English-keyboard searchers!
- Always include at least one format qualifier (`Lyrics`, `Official Lyric Video`, `Full Song with Lyrics`).

---

## 3. LLM-Optimized Description Architecture (`<= 5,000` chars)

YouTube's discovery engine uses Large Language Models (LLMs) that index your video's **first 2 lines**, **timestamp chapters**, and **full lyrics** to match viewer queries. Structure every description into 6 blocks:

1. **Block 1 — Above-the-Fold Search Snippet (Lines 1–2, `<= 150` chars)**:
   - Appears directly in YouTube & Google search results before the user clicks `"…more"`.
   - Must state the exact song title, English + native script name, emotional/spiritual benefit, and a hook.
2. **Block 2 — Rich Semantic Overview & Story ("About This Song")**:
   - 1–2 natural paragraphs describing what the song is about, the meaning of the lyrics, the mood/visual aesthetic, and when to listen to it (e.g., morning prayer, Vinayaka Chavithi, meditation, late-night reflection).
3. **Block 3 — Interactive Timestamp Chapters (`00:00` Format)**:
   - Derived automatically from `storyboard.json` sections (`పల్లవి`, `అనుపల్లవి`, `చరణం 1`, `చరణం 2`, `మంగళం`) or `master.srt` cues.
   - **Hard YouTube Rules for Chapters**:
     - First timestamp MUST be `00:00`.
     - At least **3 timestamps** in ascending order.
     - Minimum chapter length is **10 seconds** (merge adjacent slides into musical sections so every chapter is `>= 10s`).
4. **Block 4 — Full Formatted Lyrics (Massive Long-Tail SEO Engine)**:
   - Include the **complete lyrics** inside the description! Millions of viewers search YouTube by typing a single line of lyrics they remember — having the full text in the description + uploaded `.srt` captions guarantees your video ranks for every single line of the song.
5. **Block 5 — Engagement Call-to-Action & Transparency Credits**:
   - Remind viewers to **Like, Subscribe, Share, and reply to the Pinned Comment**.
   - Include clean production credits and AI-assisted visual illustration disclosure.
6. **Block 6 — Targeted Hashtags (`3 to 5` hashtags at the very bottom)**:
   - Example: `#SriSiddhiVinayaka #GaneshSongs #TeluguDevotionalSongs #BhaktiSongs #LyricVideo`
   - Never exceed 15 hashtags.

---

## 4. Strategic Backend Tags (`<= 500` Characters Total)

Even though YouTube prioritizes titles, descriptions, and captions, backend **Tags** remain essential for:
- **Spelling variations & transliterations** (e.g., `siddhi vinayaka`, `sidhi vinayaka`, `sri siddhi vinayaka song`, `ganapati songs telugu`, `vinayaka bhakti patalu`).
- **Hook lyric searches** (first line of Pallavi / Chorus in both native script and English transliteration).
- **Category & intent anchors** (`telugu devotional songs with lyrics`, `lord ganesha songs`, `morning bhakti songs`).

**Hard Constraint**: The comma-separated string must be strictly `<= 500` characters total.

---

## 5. High-CTR Custom Thumbnail Strategy (`1280x720` or `1920x1080`, `< 2MB`)

CTR in the first 24 hours is the single strongest predictor of whether YouTube pushes a video to Browse/Home feeds:
1. **Pick the Best Visual Hero Frame**:
   - Select the most emotionally luminous, close-up or majestic slide from `projects/<song_slug>/images/` (typically `slide_01` or `slide_02` where the central subject/deity/character has strong eye contact and vibrant contrast).
2. **Add Bold, Readable Title Overlay (2–4 Words Max)**:
   - Do not repeat the entire title. Put a 2–4 word high-contrast hook (e.g., `"శ్రీ సిద్ధి వినాయకా"` + `"DIVINE LYRIC VIDEO"`) in large bold typography with a dark gradient vignette and gold/white glow.
3. **Avoid the Bottom-Right Corner**:
   - Never place text in the bottom-right 15% of the thumbnail — YouTube's duration badge (`01:28`) covers that corner on every device!

---

## 6. Post-Publish View Velocity & Pinned Comment Psychology

When a video goes live, YouTube tests it with an initial seed audience. Videos that earn a high **Comment-to-View** and **Like-to-View** ratio during this seed window get promoted to much larger recommendation pools.

### Why Pinning Your Own Comment Works:
- While the video plays, viewers scroll down to read comments. Seeing an inviting, emotional **Pinned Comment** from the creator right at the top triggers immediate replies.
- While a viewer is typing a reply in the comment box, the video **continues playing in the background**, pushing Average Percentage Viewed (APV) above 80–100%!

### High-Converting Pinned Comment Templates:
1. **Devotional / Spiritual Songs (Blessing + Favorite Line Hook)**:
   > 🙏 **"ఓం శ్రీ సిద్ధి వినాయకాయ నమః | Om Gam Ganapataye Namaha!"** 🌺
   > May Lord Siddhi Vinayaka remove every obstacle from your path and bless your family with peace, wisdom, and prosperity today! ✨
   > 💬 **Which line from this bhajan touched your heart the most? Drop `"Jai Ganesha 🙏"` in the comments below to receive His blessings and don't forget to LIKE 👍 & SHARE this song with your loved ones!**
2. **Emotional / Indie / Melodic Lyric Videos (Timestamp + Personal Resonance Hook)**:
   > ✨ **Thank you for listening!** Every line of this song was crafted to capture that unforgettable feeling.
   > 💬 **Which lyric line hit you the hardest, and at what timestamp (`MM:SS`)? Let us know in the replies below — I'm reading and hearting every comment! ❤️ Don't forget to hit LIKE & SUBSCRIBE for more lyric videos!**
