#!/usr/bin/env bash
# Add family photos to the site. Optimizes (resize + strip metadata) any images
# from a source folder into static/photos/. Re-run anytime you have new photos;
# the next build picks them up automatically (the build scans static/photos/).
#
# Usage:  bash scripts/add-photos.sh <folder-with-photos>
#   e.g.  bash scripts/add-photos.sh ~/Downloads/new-family-photos
set -euo pipefail
cd "$(dirname "$0")/.."
SRC="${1:?给我一个照片文件夹路径，比如 ~/Downloads/photos}"
mkdir -p static/photos
# continue numbering after the highest existing fam-NN
last=$(ls static/photos/fam-*.jpg 2>/dev/null | sed -E 's/.*fam-0*([0-9]+)\.jpg/\1/' | sort -n | tail -1)
i=$(( ${last:-0} + 1 ))
n=0
shopt -s nullglob nocaseglob
for f in "$SRC"/*.jpg "$SRC"/*.jpeg "$SRC"/*.png "$SRC"/*.heic; do
  [ -e "$f" ] || continue
  out=$(printf "static/photos/fam-%02d.jpg" "$i")
  sips -Z 1200 -s format jpeg -s formatOptions 72 "$f" --out "$out" >/dev/null 2>&1 || continue
  i=$((i+1)); n=$((n+1))
done
echo "加了 $n 张，现在共 $(ls static/photos/*.jpg 2>/dev/null | wc -l | tr -d ' ') 张。跑 build 就会生效。"
