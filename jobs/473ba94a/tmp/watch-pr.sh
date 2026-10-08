#!/bin/bash
REPO=trackstarhq/pokedex
PR=5468
last=$(date -u +%Y-%m-%dT%H:%M:%SZ)
while true; do
  sleep 60
  now=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  gh api "repos/$REPO/issues/$PR/comments?since=$last" --jq '.[] | "[comment] \(.user.login): \(.body | gsub("\n";" ") | .[0:500])"' 2>/dev/null || true
  gh api "repos/$REPO/pulls/$PR/comments?since=$last" --jq '.[] | "[inline \(.path):\(.line // .original_line)] \(.user.login): \(.body | gsub("\n";" ") | .[0:500])"' 2>/dev/null || true
  gh api "repos/$REPO/pulls/$PR/reviews" 2>/dev/null | jq -r --arg s "$last" '.[] | select(.submitted_at > $s) | "[review \(.state)] \(.user.login): \((.body // "") | gsub("\n";" ") | .[0:500])"' || true
  last=$now
done
