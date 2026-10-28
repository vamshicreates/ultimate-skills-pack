# Video to Screenplay_Laya

An experimental Codex skill that adds [Laya](https://github.com/NandhaKishorM/laya) transcript triage to [Video to Screenplay](https://github.com/vamshicreates/video-to-screenplay). It keeps the base skill's visual and audio review. The screenplay includes dialogue, brief video song montages with locations and visible actions, and Tinglish beneath Telugu dialogue. Laya labels are review hints; they do not remove source material automatically.

## Install

Install the [base skill](https://github.com/vamshicreates/video-to-screenplay) and its requirements first. Clone this repository into `~/.codex/skills/video-to-screenplay-laya` (on Windows, `$HOME\.codex\skills\video-to-screenplay-laya`). Then create this skill's separate `.venv-laya` with the base installer's `uv`. Windows x64 and Apple Silicon macOS can use Python 3.12 and `laya`; Intel macOS needs Python 3.11 plus the NumPy/PyTorch/Transformers pins in [SKILL.md](SKILL.md). The first Laya run downloads a model.

Use `$video-to-screenplay-laya` in Codex to invoke this variant. Run `scripts/triage_laya.py captions.srt --output triage.json --dry-run` with `.venv-laya`'s Python to check caption timing before running Laya.

This variant has not yet been benchmarked on a film, so its speed, token, and quality effects remain unmeasured.
