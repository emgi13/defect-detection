#!/bin/bash
for video in ./source/src_*.mp4; do
    base_name=$(basename "$video" .mp4)
    ffmpeg -i "$video" "./raw/frames/${base_name}_%04d.png"
done
