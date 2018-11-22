#!/bin/bash

DIR=$PWD
. models.sh
[[ $# -ge 1 ]] && CORPORA=("$@")

for d in ${CORPORA[@]}; do
  echo $d
  DATA_DIR=$PARSED/xml/${UCCA_MODEL[$d]}/$d
  [[ -n "${DATA[$d]}" ]] && DATA_DIR=${DATA[$d]}
  grep -PhRo '(?<=type=")[A-Z](?=")' $DATA_DIR | sort | uniq -c | awk '{print $2,$1}' | jq -R . | jq -sr 'map(./" ") | transpose | map(join("\t"))[]'
done
