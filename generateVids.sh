#!/bin/bash

framerate=24

# Generate centers video
for vid_no in {1..6}; do
    ffmpeg -framerate $framerate -i ./raw/centers/${vid_no}_%d.png -vf "scale=iw-mod(iw\,2):ih-mod(ih\,2)" -c:v libx264 -pix_fmt yuv420p ./raw/centers_${vid_no}.mp4 -y
done

# Generate delaunay video
for vid_no in {1..6}; do
    ffmpeg -framerate $framerate -i ./raw/delaunay/${vid_no}_%d.png -vf "scale=iw-mod(iw\,2):ih-mod(ih\,2)" -c:v libx264 -pix_fmt yuv420p ./raw/delaunay_${vid_no}.mp4 -y
done

# Generate bond_order video
for vid_no in {1..6}; do
    ffmpeg -framerate $framerate -i ./raw/bond_order/${vid_no}_%d.png -vf "scale=iw-mod(iw\,2):ih-mod(ih\,2)" -c:v libx264 -pix_fmt yuv420p ./raw/bond_order_${vid_no}.mp4 -y
done

# Generate voronoi video
for vid_no in {1..6}; do
    ffmpeg -framerate $framerate -i ./raw/voronoi/${vid_no}_%d.png -vf "scale=iw-mod(iw\,2):ih-mod(ih\,2)" -c:v libx264 -pix_fmt yuv420p ./raw/voronoi_${vid_no}.mp4 -y
done

# Generate voronoi_interp video
for vid_no in {1..6}; do
    ffmpeg -framerate $framerate -i ./raw/voronoi_interp/${vid_no}_%d.png -vf "scale=iw-mod(iw\,2):ih-mod(ih\,2)" -c:v libx264 -pix_fmt yuv420p ./raw/voronoi_interp_${vid_no}.mp4 -y
done

