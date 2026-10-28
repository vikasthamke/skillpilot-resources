#!/usr/bin/env bash
# Rebuilds the reel: audio mix -> 870 animation frames -> final 1080x1920 MP4.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build
python3 audio.py
node capture.js video build/video.mp4
ffmpeg -hide_banner -loglevel error -y -i build/video.mp4 -i build/mix.wav \
  -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -ar 48000 -shortest -movflags +faststart \
  the-shortlist-code-reel.mp4
echo "done: $(pwd)/the-shortlist-code-reel.mp4"
