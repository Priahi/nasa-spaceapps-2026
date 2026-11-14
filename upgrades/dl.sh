#!/bin/bash
# download one file (resume, retries) into its folder
k=$1; u=$2; f=$k/$(basename "$u")
[ -f "$f.ok" ] && exit 0
for i in 1 2 3 4 5 6; do curl -sS -L -n -c ~/.urs_cookies -b ~/.urs_cookies -C - --max-time 600 -o "$f" "$u" 2>>dl.err && touch "$f.ok" && exit 0; sleep 2; done
echo "FAIL $u" >> dl.err
