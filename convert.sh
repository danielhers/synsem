#!/usr/bin/env bash
#SBATCH --mem=10G
#SBATCH --time=0-3
#SBATCH --array=0-4

DIR=$PWD
. $DIR/models.sh
echo SLURM_ARRAY_TASK_ID=$SLURM_ARRAY_TASK_ID
[[ -n "$SLURM_ARRAY_TASK_ID" ]] && CORPORA=(${CORPORA[$SLURM_ARRAY_TASK_ID]})

UD_UCCA_LABEL_MAP=$DIR/../semstr/semstr/util/resources/ud_ucca_label_map.csv
UCCA_UD_LABEL_MAP=$DIR/../semstr/semstr/util/resources/ucca_ud_label_map.csv

for d in ${CORPORA[@]}; do
  for MODEL in ${UDPIPE_MODEL[$d]} ${UD_MODEL[$d]}; do  # Parsed UD to UCCA
    python -m semstr.convert $PARSED/conllu/$MODEL/$d.conllu -o $PARSED/xml/$MODEL/$d --extra-normalization --label-map=$UD_UCCA_LABEL_MAP $*
  done
  if [[ -n "${UD_DATA[$d]}" ]]; then  # Convert gold UD to UCCA and gold UCCA to UD
    python -m semstr.convert ${UD_DATA[$d]} -o $PARSED/xml/ud/$d --extra-normalization --label-map=$UD_UCCA_LABEL_MAP $*
    rm -f $PARSED/conllu/ucca/$d.conllu
    python -m semstr.convert "${DATA[$d]}/*.xml" -o $PARSED/conllu/ucca -j $d -f conllu --label-map=$UCCA_UD_LABEL_MAP $*
    for MODEL in ${UCCA_UD_MODEL[$d]} ${UCCA_MODEL[$d]}; do  # Parsed UCCA to UD
      rm -f $PARSED/conllu/$MODEL/$d.conllu
      python -m semstr.convert "$PARSED/xml/$MODEL/$d/*.xml" -o $PARSED/conllu/$MODEL -j $d -f conllu --label-map=$UCCA_UD_LABEL_MAP $*
    done
  fi
done

