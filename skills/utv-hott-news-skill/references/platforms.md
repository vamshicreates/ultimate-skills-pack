# Install and Canva access

The same skill folder works on macOS and Windows. The generator uses Python 3.11+ standard library only. It does not depend on shell scripts, hard-coded home directories, or local Canva credentials.

| Agent | Skill location or import | Canva requirement |
| --- | --- | --- |
| Codex | Copy this folder to `~/.codex/skills/utv-hott-news-carousel/` or an available project skill directory. | Canva connector with design-file import. |
| ChatGPT | On eligible plans, open **Plugins → Skills → Create → Upload from your computer** and upload the skill folder or ZIP. | A Canva app/connector that can create a design from generated files; otherwise use the ZIP output manually. |
| Claude Code | Copy this folder to `<project>/.claude/skills/utv-hott-news-carousel/` or `~/.claude/skills/utv-hott-news-carousel/`. Claude.ai can upload a custom skill where available. | Canva MCP/integration or a user-assisted import. |
| Google Antigravity | Copy this folder to `<project>/.agents/skills/utv-hott-news-carousel/` or `~/.gemini/config/skills/utv-hott-news-carousel/`. | Canva MCP/integration or a user-assisted import. |

Windows equivalents use the user profile directory, such as `%USERPROFILE%\.codex\skills\` and `%USERPROFILE%\.claude\skills\`. For an article photo, run `py -3 scripts\build_carousel.py --story story.json --image article.jpg --output output-name` on Windows or `python3 scripts/build_carousel.py --story story.json --image article.jpg --output output-name` on macOS. For a screenshot story without a usable photo, use `--screenshot screenshot.png` instead of `--image article.jpg` and omit `source_url` from the story JSON.

The skill handles source reading, bilingual editorial decisions, and deterministic design packaging. Creating a Canva link requires account access in the platform where it runs. Do not put Canva tokens or GitHub credentials into the skill or story JSON.
