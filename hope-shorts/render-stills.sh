#!/usr/bin/env bash
# Renders the look-dev frames. SCALE=2 gives 2160x3840 PNGs.
SCALE=${SCALE:-1}
mkdir -p out/look
for id in Sheet Cut1 Cut2 Cut3 Cut4 Cut5 Cut6; do
  npx remotion still src/index.ts "$id" "out/look/$id.png" --scale="$SCALE" || exit 1
done
