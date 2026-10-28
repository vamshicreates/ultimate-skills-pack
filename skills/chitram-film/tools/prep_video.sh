#!/usr/bin/env bash
# Convert footage for the film engine (headless Chromium can't be trusted with H.264).
#   tools/prep_video.sh in.mp4 assets/clip        -> assets/clip/00001.jpg ... (image sequence, most robust)
#   tools/prep_video.sh in.mp4 assets/clip.webm   -> VP9 webm (smaller; use <video data-at>)
# Optional env: FPS=30  WIDTH=1920  START=0  DUR=  (trim)
set -euo pipefail
in="$1"; out="$2"; fps="${FPS:-30}"; w="${WIDTH:-1920}"
trim=(); [ -n "${START:-}" ] && trim+=(-ss "$START"); [ -n "${DUR:-}" ] && trim+=(-t "$DUR")
if [[ "$out" == *.webm ]]; then
  ffmpeg -v error -y "${trim[@]}" -i "$in" -an -vf "fps=$fps,scale=$w:-2" -c:v libvpx-vp9 -b:v 0 -crf 30 -row-mt 1 -deadline good "$out"
  echo "webm: $out   ->  <video src=\"$out\" data-at=\"START\" muted playsinline></video>"
else
  mkdir -p "$out"
  ffmpeg -v error -y "${trim[@]}" -i "$in" -an -vf "fps=$fps,scale=$w:-2" -q:v 2 "$out/%05d.jpg"
  n=$(ls "$out" | wc -l)
  echo "sequence: $out ($n frames) ->  <img data-seq=\"$out/%05d.jpg\" data-count=\"$n\" data-seq-fps=\"$fps\" data-at=\"START\">"
fi
