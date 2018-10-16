#!/bin/bash
grep -PhRo '(?<=type=")[A-Z](?=")' $*|sort|uniq -c| awk '{print $2,$1}' | jq -R . | jq -sr 'map(./" ")|transpose|map(join("\t"))[]'
