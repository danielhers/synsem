#!/usr/bin/env bash
#SBATCH --mem=10G
#SBATCH --time=0-0:10
#SBATCH --array=0-13

DIR=$PWD
. models.sh
echo SLURM_ARRAY_TASK_ID=$SLURM_ARRAY_TASK_ID
[[ -n "$SLURM_ARRAY_TASK_ID" ]] && CORPORA=(${CORPORA[$SLURM_ARRAY_TASK_ID]})

UD_UCCA_LABEL_MAP=$DIR/../semstr/semstr/util/resources/ud_ucca_label_map.csv
UCCA_UD_LABEL_MAP=$DIR/../semstr/semstr/util/resources/ucca_ud_label_map.csv

for d in ${CORPORA[@]}; do
  for MODEL in ${UDPIPE_MODEL[$d]} ${UD_MODEL[$d]}; do  # Parsed UD to UCCA
    run python -m semstr.convert $PARSED/conllu/$MODEL/$d.conllu -o $PARSED/xml/$MODEL/$d --no-enhanced $*
    #run python -m semstr.convert $PARSED/conllu/$MODEL/$d.conllu -o $PARSED/xml/$MODEL/$d --extra-normalization --label-map=$UD_UCCA_LABEL_MAP $*
  done
  if [[ -z "${UD_DATA[$d]}" ]]; then  # Convert gold UD to UCCA
    echo No UD data for $d, skipping conversion to UCCA
  else
    echo ${UD_DATA[$d]}
    run python -m semstr.convert ${UD_DATA[$d]} -o $PARSED/xml/ud/$d --no-enhanced $*
    #run python -m semstr.convert ${UD_DATA[$d]} -o $PARSED/xml/ud/$d --extra-normalization --label-map=$UD_UCCA_LABEL_MAP $*
  fi
  if [[ -z "${DATA[$d]}" ]]; then  # Convert gold UCCA to UD
    echo No UCCA data for $d, skipping conversion to UD
  else
    rm -fv $PARSED/conllu/ucca/$d.conllu
    echo ${DATA[$d]}
    run python -m semstr.convert "${DATA[$d]}/*.*" -o $PARSED/conllu/ucca -j $d -f conllu --label-map=$UCCA_UD_LABEL_MAP $*
    for MODEL in ${UCCA_UD_MODEL[$d]} ${UCCA_MODEL[$d]}; do  # Parsed UCCA to UD
      rm -fv $PARSED/conllu/$MODEL/$d.conllu
      run python -m semstr.convert "$PARSED/xml/$MODEL/$d/*.xml" -o $PARSED/conllu/$MODEL -j $d -f conllu --label-map=$UCCA_UD_LABEL_MAP $*
    done
  fi
done

