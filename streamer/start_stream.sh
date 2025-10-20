#!/usr/bin/env bash
RTSP_URL="$1"
OUT_DIR="$2"
mkdir -p "$OUT_DIR"
ffmpeg -rtsp_transport tcp -i "$RTSP_URL" -c:v copy -c:a aac \
  -f hls -hls_time 4 -hls_list_size 5 -hls_flags delete_segments \
  "$OUT_DIR/stream.m3u8"
