#!/bin/bash

DIR=$PWD
. models.sh
[[ $# -ge 1 ]] && CORPORA=("$@")

for d in ${CORPORA[@]}; do
  echo $d
  CONLLU_FILE=$PARSED/conllu/${UDPIPE_MODEL[$d]}/$d.conllu
  [[ -n "${UD_DATA[$d]}" ]] && CONLLU_FILE=${UD_DATA[$d]}
  echo $CONLLU_FILE
  awk '{if(/^[0-9]*\t/){sub(/:.*|_/,"",$8);if($8)print $8}}' $CONLLU_FILE | sort | uniq -c | grep -wf included_rels.txt | awk '{print $2,$1}' | jq -R . | jq -sr 'map(./" ") | transpose | map(join("\t"))[]'
done

