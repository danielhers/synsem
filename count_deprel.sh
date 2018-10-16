#!/bin/bash
if [ -d $1 ]; then
  f="$1/*.conllu"
else
  f=$1
fi
awk '{if(/^[0-9]/){sub(/:.*|_/,"",$8);if($8)print $8}}' $f | sort | uniq -c | awk '{print $2,$1}' | jq -R . | jq -sr 'map(./" ")|transpose|map(join("\t"))[]'
