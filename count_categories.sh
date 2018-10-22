#!/bin/bash

DIR=$PWD
. $DIR/models.sh
[[ $# -ge 1 ]] && CORPORA=("$@")

for d in ${CORPORA[@]}; do
  echo $d
  grep -PhRo '(?<=type=")[A-Z](?=")' ${DATA[$d]} | sort | uniq -c | awk '{print $2,$1}' | jq -R . | jq -sr 'map(./" ") | transpose | map(join("\t"))[]'
done
