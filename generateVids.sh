#!/bin/bash

# Generate centers video
for vid_no in {1..6}; do
    ffmpeg -framerate 24 -i ./raw/centers/${vid_no}_%d.png -vf "scale=iw:ih-mod(ih\,2)" -c:v libx264 -pix_fmt yuv420p ./raw/centers_${vid_no}.mp4 -y
done

